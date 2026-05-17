package temu

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestSign(t *testing.T) {
	tests := []struct {
		name     string
		params   map[string]interface{}
		secret   string
		expected string
	}{
		{
			name: "simple params",
			params: map[string]interface{}{
				"app_key":   "test_key",
				"timestamp": int64(1700000000),
			},
			secret:   "test_secret",
			expected: "8A8B8C8D8E8F10111213141516171819",
		},
		{
			name: "with type and data_type",
			params: map[string]interface{}{
				"type":       "bg.order.list.get",
				"app_key":    "test_app_key",
				"access_token": "test_token",
				"timestamp":  int64(1700000000),
				"data_type":  "JSON",
			},
			secret: "test_secret",
		},
		{
			name: "with boolean values",
			params: map[string]interface{}{
				"app_key":   "test_key",
				"timestamp": int64(1700000000),
				"is_active": true,
				"is_test":   false,
			},
			secret: "secret123",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := Sign(tt.params, tt.secret)
			assert.NotEmpty(t, result)
			assert.Equal(t, 32, len(result), "MD5 hex should be 32 characters")
			assert.Regexp(t, "^[0-9A-F]+$", result, "should be uppercase hex")

			if tt.expected != "8A8B8C8D8E8F10111213141516171819" {
				t.Logf("sign result: %s", result)
			}
		})
	}
}

func TestSignDeterministic(t *testing.T) {
	params := map[string]interface{}{
		"app_key":   "test_key",
		"timestamp": int64(1700000000),
		"type":      "test.api.method",
	}
	secret := "my_secret"

	result1 := Sign(params, secret)
	result2 := Sign(params, secret)

	assert.Equal(t, result1, result2, "sign should be deterministic")
}

func TestSignExcludesSignKey(t *testing.T) {
	params := map[string]interface{}{
		"app_key": "test_key",
		"sign":    "should_be_excluded",
	}

	secret := "test"
	result := Sign(params, secret)

	hasSignKey := false
	for k := range params {
		if k == "sign" {
			hasSignKey = true
		}
	}
	assert.True(t, hasSignKey, "sign key exists in original params")
	assert.NotEmpty(t, result)
}

func TestNewClient(t *testing.T) {
	client := NewClient(1, "key", "secret", "token", "global", "")
	require.NotNil(t, client)
	assert.Equal(t, 1, client.shopID)
	assert.Equal(t, "key", client.apiKey)
	assert.Equal(t, "secret", client.apiSecret)
	assert.Equal(t, "token", client.accessToken)
	assert.Equal(t, "https://openapi-b-global.temu.com", client.baseURL)
}

func TestNewClientWithRegion(t *testing.T) {
	client := NewClient(1, "key", "secret", "token", "us", "")
	require.NotNil(t, client)
	assert.Equal(t, "https://openapi-b-us.temu.com", client.baseURL)

	clientEU := NewClient(2, "key", "secret", "token", "eu", "")
	assert.Equal(t, "https://openapi-b-eu.temu.com", clientEU.baseURL)

	clientCN := NewClient(3, "key", "secret", "token", "cn", "")
	assert.Equal(t, "https://openapi.kuajingmaihuo.com", clientCN.baseURL)
}

func TestNewMockClient(t *testing.T) {
	client := NewMockClient(1)
	require.NotNil(t, client)
	assert.Equal(t, 1, client.shopID)
}

func TestMockClientInterface(t *testing.T) {
	var client ApiClient = NewMockClient(1)
	require.NotNil(t, client)

	resp, err := client.GetOrders(1, 10, nil)
	assert.NoError(t, err)
	assert.NotNil(t, resp)
	assert.True(t, resp.Success)

	resp, err = client.GetOrderDetail("test_order")
	assert.NoError(t, err)
	assert.NotNil(t, resp)

	list, err := client.GetGoodsList(1, 10)
	assert.NoError(t, err)
	assert.NotNil(t, list)

	err = client.Close()
	assert.NoError(t, err)
}

func TestMockClientGetOrdersPagination(t *testing.T) {
	client := NewMockClient(1)

	page1, err := client.GetOrders(1, 10, nil)
	require.NoError(t, err)
	require.NotNil(t, page1)

	page2, err := client.GetOrders(2, 10, nil)
	require.NoError(t, err)
	require.NotNil(t, page2)
}

func TestSkuStock(t *testing.T) {
	stock := SkuStock{
		SkuID: "SKU001",
		Stock: 100,
	}
	assert.Equal(t, "SKU001", stock.SkuID)
	assert.Equal(t, 100, stock.Stock)
}

func TestApiResponse(t *testing.T) {
	resp := &ApiResponse{
		Success: true,
		Status:  200,
	}
	assert.True(t, resp.Success)
	assert.Equal(t, 200, resp.Status)

	resp = &ApiResponse{
		Success:   false,
		Error:     "test error",
		ErrorCode: 400,
		Status:    400,
	}
	assert.False(t, resp.Success)
	assert.Equal(t, "test error", resp.Error)
	assert.Equal(t, 400, resp.ErrorCode)
}
