package api

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"
	"net/url"

	"github.com/gin-gonic/gin"

	"github.com/erfengyuzhangsun/temutools/internal/api/middleware"
	"github.com/erfengyuzhangsun/temutools/internal/config"
	"github.com/erfengyuzhangsun/temutools/internal/repository"
	"github.com/erfengyuzhangsun/temutools/internal/service"
	"github.com/erfengyuzhangsun/temutools/internal/temu"
)

type authState struct {
	UserID   int    `json:"uid"`
	ShopName string `json:"shop"`
}

func HandleGetAuthURL(c *gin.Context) {
	userID := middleware.GetUserID(c)
	shopName := c.DefaultQuery("shop_name", "我的店铺")

	cfg := config.Cfg
	appKey := cfg.Temu.AppKey
	if appKey == "" {
		Error(c, http.StatusBadRequest, ErrBadRequest, "系统未配置 App Key")
		return
	}

	state := base64.StdEncoding.EncodeToString([]byte(
		fmt.Sprintf(`{"uid":%d,"shop":"%s"}`, userID, shopName),
	))

	redirectURL := fmt.Sprintf("%s?appKey=%s&state=%s&redirectUrl=%s",
		"https://partner.temu.com/auth/authorize",
		appKey,
		url.QueryEscape(state),
		url.QueryEscape("https://www.jinpuhuang.com/api/v1/temu/callback"),
	)

	Success(c, gin.H{"auth_url": redirectURL})
}

func HandleTemuCallback(c *gin.Context) {
	code := c.DefaultQuery("code", "")
	stateEncoded := c.DefaultQuery("state", "")

	if code == "" || stateEncoded == "" {
		c.Redirect(http.StatusFound, fmt.Sprintf("/?error=%s", url.QueryEscape("缺少授权code或state参数")))
		return
	}

	stateBytes, err := base64.StdEncoding.DecodeString(stateEncoded)
	if err != nil {
		c.Redirect(http.StatusFound, fmt.Sprintf("/?error=%s", url.QueryEscape("state参数无效")))
		return
	}

	var state authState
	if err := json.Unmarshal(stateBytes, &state); err != nil {
		c.Redirect(http.StatusFound, fmt.Sprintf("/?error=%s", url.QueryEscape("state参数解析失败")))
		return
	}

	cfg := config.Cfg
	appKey := cfg.Temu.AppKey
	appSecret := cfg.Temu.AppSecret
	region := cfg.Temu.Region

	if appKey == "" || appSecret == "" {
		slog.Error("TEMU_APP_KEY or TEMU_APP_SECRET not configured")
		c.Redirect(http.StatusFound, fmt.Sprintf("/?error=%s", url.QueryEscape("系统未配置Temu API凭证，请联系管理员")))
		return
	}

	client := temu.NewClient(0, appKey, appSecret, "", region, cfg.Temu.Proxy)
	resp, err := client.GetAccessToken(code)
	if err != nil || resp == nil || !resp.Success {
		slog.Error("failed to get access token from Temu", "error", err, "resp", resp)
		c.Redirect(http.StatusFound, fmt.Sprintf("/?error=%s", url.QueryEscape("Access Token获取失败，请重试")))
		return
	}

	var tokenData struct {
		AccessToken string `json:"accessToken"`
		ExpiresIn   int    `json:"expires_in"`
		ShopName    string `json:"shop_name,omitempty"`
	}
	if resp.Data != nil {
		json.Unmarshal(resp.Data, &tokenData)
	}
	if tokenData.AccessToken == "" && resp.Result != nil {
		var resultToken struct {
			AccessToken string `json:"accessToken"`
			ExpiresIn   int    `json:"expires_in"`
			MallID      int    `json:"mallId"`
		}
		json.Unmarshal(resp.Result, &resultToken)
		if resultToken.AccessToken != "" {
			tokenData.AccessToken = resultToken.AccessToken
		}
	}
	if tokenData.AccessToken == "" && resp.Data != nil {
		var altToken struct {
			AccessToken string `json:"access_token"`
		}
		json.Unmarshal(resp.Data, &altToken)
		tokenData.AccessToken = altToken.AccessToken
	}
	if tokenData.AccessToken == "" {
		slog.Error("access token is empty in response", "data", string(resp.Data), "result", string(resp.Result))
		c.Redirect(http.StatusFound, fmt.Sprintf("/?error=%s", url.QueryEscape("返回的Access Token为空")))
		return
	}

	shopName := state.ShopName
	if tokenData.ShopName != "" {
		shopName = tokenData.ShopName
	}

	shopID, err := repository.CreateShop(state.UserID, shopName)
	if err != nil {
		slog.Error("failed to create shop", "error", err)
		c.Redirect(http.StatusFound, fmt.Sprintf("/?error=%s", url.QueryEscape("店铺创建失败")))
		return
	}

	if err := repository.SaveShopCredentials(shopID, tokenData.AccessToken, region, "", ""); err != nil {
		slog.Error("failed to save credentials", "error", err)
		c.Redirect(http.StatusFound, fmt.Sprintf("/?error=%s", url.QueryEscape("保存凭证失败")))
		return
	}

	slog.Info("shop bound via oauth", "user_id", state.UserID, "shop_id", shopID, "shop_name", shopName, "region", region)

	c.Redirect(http.StatusFound, fmt.Sprintf("/?success=%s", url.QueryEscape(fmt.Sprintf("店铺「%s」绑定成功！", shopName))))
}

func HandleTemuWebhook(c *gin.Context) {
	var request struct {
		MessageID   string          `json:"message_id"`
		MessageType string          `json:"message_type"`
		ShopID      int             `json:"shop_id"`
		Timestamp   int64           `json:"timestamp"`
		Data        json.RawMessage `json:"data"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		slog.Warn("webhook: invalid request body", "error", err)
		Success(c, gin.H{"code": 0, "message": "ok"})
		return
	}

	if request.MessageID == "" || request.MessageType == "" {
		slog.Warn("webhook: missing message_id or message_type")
		Success(c, gin.H{"code": 0, "message": "ok"})
		return
	}

	svc := service.NewWebhookService(0)
	msg := &service.WebhookMessage{
		MessageID:   request.MessageID,
		MessageType: request.MessageType,
		ShopID:      request.ShopID,
		Timestamp:   request.Timestamp,
		Data:        request.Data,
	}

	result := svc.ProcessWebhook(msg)
	slog.Info("webhook processed", "message_id", result.MessageID,
		"type", result.MessageType, "action", result.Action)

	Success(c, gin.H{"code": 0, "message": "ok"})
}
