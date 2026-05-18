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
		Error(c, http.StatusBadRequest, ErrValidation, "系统未配置 TEMU_APP_KEY，请联系管理员")
		return
	}

	region := cfg.Temu.Region
	baseURL := temu.GetRegionBaseURL(region)

	state := authState{
		UserID:   userID,
		ShopName: shopName,
	}
	stateData, _ := json.Marshal(state)
	stateEncoded := base64.URLEncoding.EncodeToString(stateData)

	redirectURL := fmt.Sprintf("https://www.jinpuhuang.com/api/v1/temu/callback")

	authURL := fmt.Sprintf("%s/openapi/oauth?app_key=%s&redirect_url=%s&state=%s",
		baseURL, appKey, url.QueryEscape(redirectURL), url.QueryEscape(stateEncoded))

	Success(c, gin.H{
		"auth_url":    authURL,
		"description": "将此链接发给Temu卖家，卖家点击后在卖家中心授权即可自动绑定店铺",
	})
}

func HandleTemuCallback(c *gin.Context) {
	code := c.Query("code")
	stateEncoded := c.Query("state")

	if code == "" || stateEncoded == "" {
		Error(c, http.StatusBadRequest, ErrValidation, "缺少 code 或 state 参数")
		return
	}

	stateData, err := base64.URLEncoding.DecodeString(stateEncoded)
	if err != nil {
		slog.Error("failed to decode state", "error", err)
		Error(c, http.StatusBadRequest, ErrValidation, "无效的 state 参数")
		return
	}

	var state authState
	if err := json.Unmarshal(stateData, &state); err != nil {
		slog.Error("failed to unmarshal state", "error", err)
		Error(c, http.StatusBadRequest, ErrValidation, "无效的 state 数据")
		return
	}

	slog.Info("temu oauth callback received", "user_id", state.UserID, "shop_name", state.ShopName)

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
		AccessToken string `json:"access_token"`
		ExpiresIn   int    `json:"expires_in"`
		ShopName    string `json:"shop_name,omitempty"`
	}
	if resp.Data != nil {
		json.Unmarshal(resp.Data, &tokenData)
	}
	if tokenData.AccessToken == "" {
		slog.Error("access token is empty in response", "resp", string(resp.Data))
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
