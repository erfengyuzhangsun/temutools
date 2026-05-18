package temu

import (
	"crypto/md5"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"sort"
	"strings"
	"sync"
	"time"
)

var regionMap = map[string]string{
	"cn":     "https://openapi.kuajingmaihuo.com",
	"pa":     "https://openapi-b-partner.temu.com",
	"global": "https://openapi-b-global.temu.com",
	"us":     "https://openapi-b-us.temu.com",
	"eu":     "https://openapi-b-eu.temu.com",
}

type ApiResponse struct {
	Success   bool            `json:"success"`
	Data      json.RawMessage `json:"data,omitempty"`
	Error     string          `json:"error,omitempty"`
	ErrorCode int             `json:"errorCode,omitempty"`
	ErrorMsg  string          `json:"errorMsg,omitempty"`
	Result    json.RawMessage `json:"result,omitempty"`
	Status    int             `json:"-"`
}

type ApiClient interface {
	GetOrders(page, pageSize int, params map[string]string) (*ApiResponse, error)
	GetOrderDetail(orderSn string) (*ApiResponse, error)
	GetInventory(skuCodes []string) (*ApiResponse, error)
	GetPricingNotices(page, pageSize int) (*ApiResponse, error)
	AcceptPricing(priceOrderID string) (*ApiResponse, error)
	RejectPricing(priceOrderID, reason string) (*ApiResponse, error)
	GetSettlements(dateFrom, dateTo string, page int) (*ApiResponse, error)
	GetShopMetrics(dateFrom, dateTo string) (*ApiResponse, error)
	GetMessages(page, pageSize int) (*ApiResponse, error)
	GetActivities(page int) (*ApiResponse, error)
	GetAccessToken(code string) (*ApiResponse, error)
	CheckAccessToken() (*ApiResponse, error)
	GetGoodsList(page, pageSize int) (*ApiResponse, error)
	GetOrderShippingInfo(orderSn string) (*ApiResponse, error)
	GetOrderAmount(orderSn string) (*ApiResponse, error)
	GetCombinedShipmentList() (*ApiResponse, error)
	GetSkuPriceList(skuCodes []string) (*ApiResponse, error)
	UpdateStock(goodsID string, skuStockList []SkuStock) (*ApiResponse, error)
	NegotiatePricing(priceOrderID, newPrice string) (*ApiResponse, error)
	SetSaleStatus(goodsID string, status int) (*ApiResponse, error)
	GetFreightTemplates() (*ApiResponse, error)
	GetComplianceGoodsList(page, pageSize int) (*ApiResponse, error)
	GetAftersalesList(page, pageSize int) (*ApiResponse, error)
	Close() error
}

type SkuStock struct {
	SkuID    string `json:"skuId"`
	Stock    int    `json:"stockTarget"`
}

type RealClient struct {
	shopID      int
	apiKey      string
	apiSecret   string
	accessToken string
	baseURL     string
	proxy       string
	httpClient  *http.Client
	mu          sync.RWMutex
}

func NewClient(shopID int, apiKey, apiSecret, accessToken, region, proxy string) *RealClient {
	baseURL := regionMap["global"]
	if u, ok := regionMap[region]; ok {
		baseURL = u
	}

	transport := &http.Transport{
		MaxIdleConns:        100,
		MaxIdleConnsPerHost: 20,
		IdleConnTimeout:     90 * time.Second,
		DisableCompression:  false,
	}

	client := &RealClient{
		shopID:      shopID,
		apiKey:      apiKey,
		apiSecret:   apiSecret,
		accessToken: accessToken,
		baseURL:     baseURL,
		proxy:       proxy,
		httpClient: &http.Client{
			Transport: transport,
			Timeout:   60 * time.Second,
		},
	}

	return client
}

func (c *RealClient) request(apiType string, params map[string]interface{}) (*ApiResponse, error) {
	c.mu.RLock()
	apiKey := c.apiKey
	apiSecret := c.apiSecret
	accessToken := c.accessToken
	client := c.httpClient
	c.mu.RUnlock()

	if client == nil {
		c.mu.Lock()
		if c.httpClient == nil {
			c.httpClient = &http.Client{
				Transport: &http.Transport{
					MaxIdleConns:        100,
					MaxIdleConnsPerHost: 20,
					IdleConnTimeout:     90 * time.Second,
				},
				Timeout: 60 * time.Second,
			}
		}
		client = c.httpClient
		c.mu.Unlock()
	}

	body := map[string]interface{}{
		"type":         apiType,
		"app_key":      apiKey,
		"access_token": accessToken,
		"timestamp":    time.Now().Unix(),
		"data_type":    "JSON",
	}

	for k, v := range params {
		if v != nil {
			body[k] = v
		}
	}

	body["sign"] = Sign(body, apiSecret)

	jsonBody, err := json.Marshal(body)
	if err != nil {
		return nil, fmt.Errorf("json marshal error: %w", err)
	}

	url := fmt.Sprintf("%s/openapi/router?app_secret=%s", c.baseURL, apiSecret)
	req, err := http.NewRequest("POST", url, strings.NewReader(string(jsonBody)))
	if err != nil {
		return nil, fmt.Errorf("request create error: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("request error: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("read response error: %w", err)
	}

	var apiResp ApiResponse
	if err := json.Unmarshal(respBody, &apiResp); err != nil {
		apiResp.Success = false
		apiResp.Error = fmt.Sprintf("invalid json response: %s", string(respBody))
		apiResp.Status = resp.StatusCode
		return &apiResp, nil
	}
	apiResp.Status = resp.StatusCode

	if resp.StatusCode == 401 {
		apiResp.Success = false
		apiResp.Error = "API认证失败(401)，请检查 app_key 或 access_token"
		return &apiResp, nil
	}
	if resp.StatusCode == 403 {
		apiResp.Success = false
		apiResp.Error = "API权限不足(403)，请检查 access_token 权限范围"
		return &apiResp, nil
	}
	if resp.StatusCode >= 500 {
		apiResp.Success = false
		apiResp.Error = fmt.Sprintf("Temu服务器错误(%d)", resp.StatusCode)
		return &apiResp, nil
	}

	if apiResp.ErrorCode == 1000000 {
		apiResp.Success = true
	}

	return &apiResp, nil
}

func Sign(params map[string]interface{}, secret string) string {
	keys := make([]string, 0, len(params))
	for k := range params {
		if k == "sign" {
			continue
		}
		keys = append(keys, k)
	}
	sort.Strings(keys)

	var signStr strings.Builder
	signStr.WriteString(secret)
	for _, k := range keys {
		v := params[k]
		if v == nil {
			continue
		}
		switch val := v.(type) {
		case bool:
			signStr.WriteString(fmt.Sprintf("%s%t", k, val))
		case float64:
			signStr.WriteString(fmt.Sprintf("%s%v", k, val))
		case string:
			signStr.WriteString(fmt.Sprintf("%s%s", k, val))
		default:
			b, _ := json.Marshal(val)
			signStr.WriteString(fmt.Sprintf("%s%s", k, string(b)))
		}
	}
	signStr.WriteString(secret)

	hash := md5.Sum([]byte(signStr.String()))
	return strings.ToUpper(hex.EncodeToString(hash[:]))
}

func (c *RealClient) GetOrders(page, pageSize int, params map[string]string) (*ApiResponse, error) {
	p := map[string]interface{}{
		"pageSize":   pageSize,
		"pageNumber": page,
	}
	for k, v := range params {
		p[k] = v
	}
	return c.request("bg.order.list.get", p)
}

func (c *RealClient) GetOrderDetail(orderSn string) (*ApiResponse, error) {
	return c.request("bg.order.detail.get", map[string]interface{}{
		"parentOrderSn": orderSn,
	})
}

func (c *RealClient) GetInventory(skuCodes []string) (*ApiResponse, error) {
	return c.request("bg.local.goods.sku.list.query", map[string]interface{}{
		"skuIdList": skuCodes,
	})
}

func (c *RealClient) GetPricingNotices(page, pageSize int) (*ApiResponse, error) {
	return c.request("bg.local.goods.priceorder.query", map[string]interface{}{
		"page":     page,
		"pageSize": pageSize,
	})
}

func (c *RealClient) AcceptPricing(priceOrderID string) (*ApiResponse, error) {
	return c.request("bg.local.goods.priceorder.accept", map[string]interface{}{
		"priceOrderId": priceOrderID,
	})
}

func (c *RealClient) RejectPricing(priceOrderID, reason string) (*ApiResponse, error) {
	return c.request("bg.local.goods.priceorder.change.sku.price", map[string]interface{}{
		"priceOrderId": priceOrderID,
		"reason":       reason,
	})
}

func (c *RealClient) GetSettlements(dateFrom, dateTo string, page int) (*ApiResponse, error) {
	return nil, fmt.Errorf("结算查询API未在Temu开放平台公开接口中提供")
}

func (c *RealClient) GetShopMetrics(dateFrom, dateTo string) (*ApiResponse, error) {
	return nil, fmt.Errorf("店铺指标API未在Temu开放平台公开接口中提供")
}

func (c *RealClient) GetMessages(page, pageSize int) (*ApiResponse, error) {
	return nil, fmt.Errorf("消息列表API未在Temu开放平台公开接口中提供")
}

func (c *RealClient) GetActivities(page int) (*ApiResponse, error) {
	return c.request("bg.promotion.activity.query", map[string]interface{}{
		"pageNumber": page,
		"pageSize":   20,
	})
}

func (c *RealClient) GetAccessToken(code string) (*ApiResponse, error) {
	return c.request("bg.open.accesstoken.create", map[string]interface{}{
		"code": code,
	})
}

func (c *RealClient) CheckAccessToken() (*ApiResponse, error) {
	return c.request("bg.open.accesstoken.info.get", nil)
}

func (c *RealClient) GetGoodsList(page, pageSize int) (*ApiResponse, error) {
	return c.request("bg.local.goods.list.query", map[string]interface{}{
		"page":     page,
		"pageSize": pageSize,
	})
}

func (c *RealClient) GetOrderShippingInfo(orderSn string) (*ApiResponse, error) {
	return c.request("bg.order.shippinginfo.get", map[string]interface{}{
		"parentOrderSn": orderSn,
	})
}

func (c *RealClient) GetOrderAmount(orderSn string) (*ApiResponse, error) {
	return c.request("bg.order.amount.query", map[string]interface{}{
		"parentOrderSn": orderSn,
	})
}

func (c *RealClient) GetCombinedShipmentList() (*ApiResponse, error) {
	return c.request("bg.order.combinedshipment.list.get", nil)
}

func (c *RealClient) GetSkuPriceList(skuCodes []string) (*ApiResponse, error) {
	return c.request("bg.local.goods.sku.list.price.query", map[string]interface{}{
		"skuIdList": skuCodes,
	})
}

func (c *RealClient) UpdateStock(goodsID string, skuStockList []SkuStock) (*ApiResponse, error) {
	return c.request("bg.local.goods.stock.edit", map[string]interface{}{
		"goodsId":          goodsID,
		"skuStockTargetList": skuStockList,
	})
}

func (c *RealClient) NegotiatePricing(priceOrderID, newPrice string) (*ApiResponse, error) {
	return c.request("bg.local.goods.priceorder.negotiate", map[string]interface{}{
		"priceOrderId": priceOrderID,
		"suggestPrice": newPrice,
	})
}

func (c *RealClient) SetSaleStatus(goodsID string, status int) (*ApiResponse, error) {
	return c.request("bg.local.goods.sale.status.set", map[string]interface{}{
		"goodsId":    goodsID,
		"saleStatus": status,
	})
}

func (c *RealClient) GetFreightTemplates() (*ApiResponse, error) {
	return c.request("bg.freight.template.list.query", nil)
}

func (c *RealClient) GetComplianceGoodsList(page, pageSize int) (*ApiResponse, error) {
	return c.request("bg.local.compliance.goods.list.query", map[string]interface{}{
		"page":     page,
		"pageSize": pageSize,
	})
}

func (c *RealClient) GetAftersalesList(page, pageSize int) (*ApiResponse, error) {
	return c.request("bg.aftersales.aftersales.list.get", map[string]interface{}{
		"pageNo":   page,
		"pageSize": pageSize,
	})
}

func (c *RealClient) Close() error {
	c.httpClient.CloseIdleConnections()
	return nil
}

func (c *RealClient) UpdateCredentials(apiKey, apiSecret, accessToken string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	if apiKey != "" {
		c.apiKey = apiKey
	}
	if apiSecret != "" {
		c.apiSecret = apiSecret
	}
	if accessToken != "" {
		c.accessToken = accessToken
	}
}

func init() {
	slog.Info("Temu API client initialized", "region_count", len(regionMap))
}

func GetRegionBaseURL(region string) string {
	if u, ok := regionMap[region]; ok {
		return u
	}
	return regionMap["global"]
}
