package tests

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/erfengyuzhangsun/temutools/internal/models"
	"github.com/erfengyuzhangsun/temutools/internal/repository"
)

type apiResponse struct {
	Success bool            `json:"success"`
	Data    json.RawMessage `json:"data,omitempty"`
	Error   *struct {
		Code    string `json:"code"`
		Message string `json:"message"`
	} `json:"error,omitempty"`
}

func parseResponse(t *testing.T, body []byte) *apiResponse {
	t.Helper()
	var resp apiResponse
	err := json.Unmarshal(body, &resp)
	require.NoError(t, err, "response should be valid JSON: %s", string(body))
	return &resp
}

func requireSuccess(t *testing.T, body []byte) *apiResponse {
	t.Helper()
	resp := parseResponse(t, body)
	assert.True(t, resp.Success, "response should be successful: %s", string(body))
	return resp
}

func requireError(t *testing.T, body []byte, expectedCode string, expectedStatus int) *apiResponse {
	t.Helper()
	resp := parseResponse(t, body)
	assert.False(t, resp.Success, "response should indicate failure: %s", string(body))
	require.NotNil(t, resp.Error, "response should have error field: %s", string(body))
	assert.Equal(t, expectedCode, resp.Error.Code, "error code mismatch: %s", string(body))
	return resp
}

func skipIfNoDB(t *testing.T) {
	t.Helper()
	if !testDBReady {
		t.Skip("SKIP: database not available")
	}
}

func TestHealthCheck(t *testing.T) {
	req := makeJSONRequest("GET", "/health", "")
	resp := executeRequest(req)

	assert.Equal(t, http.StatusOK, resp.Code)

	var data map[string]interface{}
	err := json.Unmarshal(resp.Body.Bytes(), &data)
	require.NoError(t, err)
	assert.Equal(t, "ok", data["status"])
	assert.Equal(t, "0.1.0", data["version"])
	assert.Equal(t, "temu-tools-go", data["service"])
}

func TestLogin_Success(t *testing.T) {
	skipIfNoDB(t)

	req := makeJSONRequest("POST", "/api/v1/auth/login", `{"email":"integ-test@example.com","password":"test-pass-123"}`)
	resp := executeRequest(req)

	assert.Equal(t, http.StatusOK, resp.Code)
	respData := requireSuccess(t, resp.Body.Bytes())

	var data map[string]interface{}
	err := json.Unmarshal(respData.Data, &data)
	require.NoError(t, err)
	assert.NotEmpty(t, data["token"], "should return a JWT token")

	user, ok := data["user"].(map[string]interface{})
	require.True(t, ok, "should have user object")
	assert.Equal(t, "integ-test@example.com", user["email"])
	assert.Equal(t, "integration-test-user", user["nickname"])
	assert.Equal(t, "basic", user["plan"])
}

func TestLogin_WrongPassword(t *testing.T) {
	skipIfNoDB(t)

	req := makeJSONRequest("POST", "/api/v1/auth/login", `{"email":"integ-test@example.com","password":"wrong-password"}`)
	resp := executeRequest(req)

	assert.Equal(t, http.StatusUnauthorized, resp.Code)
	requireError(t, resp.Body.Bytes(), "UNAUTHORIZED", http.StatusUnauthorized)
}

func TestLogin_EmailNotFound(t *testing.T) {
	req := makeJSONRequest("POST", "/api/v1/auth/login", `{"email":"nonexistent@test.com","password":"somepassword"}`)
	resp := executeRequest(req)

	assert.Equal(t, http.StatusUnauthorized, resp.Code)
	requireError(t, resp.Body.Bytes(), "UNAUTHORIZED", http.StatusUnauthorized)
}

func TestLogin_MissingCredentials(t *testing.T) {
	req := makeJSONRequest("POST", "/api/v1/auth/login", `{}`)
	resp := executeRequest(req)

	assert.Equal(t, http.StatusBadRequest, resp.Code)
}

func TestRegister_Success(t *testing.T) {
	skipIfNoDB(t)

	email := "test-reg-success@example.com"
	t.Cleanup(func() {
		repository.GetDB().Exec("DELETE FROM temu_users WHERE email = ?", email)
	})

	req := makeJSONRequest("POST", "/api/v1/auth/register", `{"email":"test-reg-success@example.com","password":"securePass123","agreed_terms":true,"agreed_privacy":true,"policy_version":"2026-05-18"}`)
	resp := executeRequest(req)

	assert.Equal(t, http.StatusOK, resp.Code)
	respData := requireSuccess(t, resp.Body.Bytes())

	var data map[string]interface{}
	err := json.Unmarshal(respData.Data, &data)
	require.NoError(t, err)
	assert.NotEmpty(t, data["token"], "should return a JWT token")

	user, ok := data["user"].(map[string]interface{})
	require.True(t, ok, "should have user object")
	assert.Equal(t, "test-reg-success@example.com", user["email"])
	assert.Equal(t, "basic", user["plan"])
}

func TestRegister_DuplicateEmail(t *testing.T) {
	skipIfNoDB(t)

	req := makeJSONRequest("POST", "/api/v1/auth/register", `{"email":"integ-test@example.com","password":"anotherPass123","agreed_terms":true,"agreed_privacy":true}`)
	resp := executeRequest(req)

	assert.Equal(t, http.StatusConflict, resp.Code)
	requireError(t, resp.Body.Bytes(), "CONFLICT", http.StatusConflict)
}

func TestRegister_ShortPassword(t *testing.T) {
	req := makeJSONRequest("POST", "/api/v1/auth/register", `{"email":"test-short@example.com","password":"12345","agreed_terms":true,"agreed_privacy":true}`)
	resp := executeRequest(req)

	assert.Equal(t, http.StatusBadRequest, resp.Code)
}

func TestRegister_WithoutConsent(t *testing.T) {
	req := makeJSONRequest("POST", "/api/v1/auth/register", `{"email":"test-no-consent@example.com","password":"securePass123","agreed_terms":false,"agreed_privacy":true}`)
	resp := executeRequest(req)
	assert.Equal(t, http.StatusBadRequest, resp.Code)
}

func TestRegister_BasicExpiresIn30Days(t *testing.T) {
	skipIfNoDB(t)

	email := "test-expire-basic@example.com"
	t.Cleanup(func() {
		repository.GetDB().Exec("DELETE FROM temu_users WHERE email = ?", email)
	})

	req := makeJSONRequest("POST", "/api/v1/auth/register", `{"email":"`+email+`","password":"securePass123","agreed_terms":true,"agreed_privacy":true}`)
	resp := executeRequest(req)
	assert.Equal(t, http.StatusOK, resp.Code)

	user, err := repository.FindByEmail(email)
	require.NoError(t, err)
	require.NotNil(t, user)

	assert.NotNil(t, user.StartDate, "basic user should have start_date set")
	assert.NotNil(t, user.ExpireDate, "basic user should have expire_date set")
	assert.Equal(t, "basic", user.PlanType)

	daysDiff := int(user.ExpireDate.Sub(*user.StartDate).Hours() / 24)
	assert.Equal(t, 30, daysDiff, "basic plan should expire in 30 days from start_date")

	expired := repository.IsUserExpired(user)
	assert.False(t, expired, "newly registered basic user should not be expired")
}

func TestRegister_LifetimeNeverExpires(t *testing.T) {
	skipIfNoDB(t)

	email := "test-expire-lifetime@example.com"
	t.Cleanup(func() {
		repository.GetDB().Exec("DELETE FROM temu_users WHERE email = ?", email)
	})

	user, err := repository.CreateUser(email, "securePass123", "lifetime", "2026-05-18", true, true)
	require.NoError(t, err)
	require.NotNil(t, user)

	assert.Equal(t, "lifetime", user.PlanType)
	assert.NotNil(t, user.StartDate, "lifetime user should have start_date set")
	assert.Nil(t, user.ExpireDate, "lifetime user should have nil expire_date (never expires)")

	expired := repository.IsUserExpired(user)
	assert.False(t, expired, "lifetime user should never expire")
}

func TestLogin_ShowsExpiryInfo(t *testing.T) {
	skipIfNoDB(t)

	req := makeJSONRequest("POST", "/api/v1/auth/login", `{"email":"integ-test@example.com","password":"test-pass-123"}`)
	resp := executeRequest(req)
	assert.Equal(t, http.StatusOK, resp.Code)

	respData := requireSuccess(t, resp.Body.Bytes())
	var data map[string]interface{}
	err := json.Unmarshal(respData.Data, &data)
	require.NoError(t, err)

	expiry, ok := data["expiry"].(map[string]interface{})
	require.True(t, ok, "login response should have expiry field")
	assert.NotNil(t, expiry["expire_date"])
	assert.NotNil(t, expiry["days_remaining"])
	assert.NotNil(t, expiry["is_expiring_soon"])
	assert.Equal(t, false, expiry["is_expired"])
}

func TestAuthMiddleware_NoToken(t *testing.T) {
	req := makeJSONRequest("GET", "/api/v1/auth/me", "")
	resp := executeRequest(req)

	assert.Equal(t, http.StatusUnauthorized, resp.Code)
	requireError(t, resp.Body.Bytes(), "UNAUTHORIZED", http.StatusUnauthorized)
}

func TestAuthMiddleware_InvalidToken(t *testing.T) {
	req := makeAuthRequest("GET", "/api/v1/auth/me", "invalid-token-here", "")
	resp := executeRequest(req)

	assert.Equal(t, http.StatusUnauthorized, resp.Code)
	requireError(t, resp.Body.Bytes(), "UNAUTHORIZED", http.StatusUnauthorized)
}

func TestAuthMiddleware_ValidToken(t *testing.T) {
	skipIfNoDB(t)

	req := makeAuthRequest("GET", "/api/v1/auth/me", testUserToken, "")
	resp := executeRequest(req)

	assert.Equal(t, http.StatusOK, resp.Code)
	respData := requireSuccess(t, resp.Body.Bytes())

	var data map[string]interface{}
	err := json.Unmarshal(respData.Data, &data)
	require.NoError(t, err)
	assert.Equal(t, float64(testUserID), data["user_id"])
	assert.Equal(t, "basic", data["plan_type"])
}

func TestDashboard_RequiresAuth(t *testing.T) {
	req := makeJSONRequest("GET", "/api/v1/dashboard/overview", "")
	resp := executeRequest(req)

	assert.Equal(t, http.StatusUnauthorized, resp.Code)
}

func TestDashboard_WithValidToken(t *testing.T) {
	skipIfNoDB(t)

	req := makeAuthRequest("GET", "/api/v1/dashboard/overview", testUserToken, "")
	resp := executeRequest(req)

	assert.Equal(t, http.StatusOK, resp.Code)
	respData := requireSuccess(t, resp.Body.Bytes())

	var data map[string]interface{}
	err := json.Unmarshal(respData.Data, &data)
	require.NoError(t, err)
	assert.Contains(t, data, "total_profit")
	assert.Contains(t, data, "total_revenue")
	assert.Contains(t, data, "shop_count")
	assert.Contains(t, data, "shop_details")
}

func TestDashboardAlerts_WithValidToken(t *testing.T) {
	skipIfNoDB(t)

	req := makeAuthRequest("GET", "/api/v1/dashboard/alerts", testUserToken, "")
	resp := executeRequest(req)

	assert.Equal(t, http.StatusOK, resp.Code)
	_ = requireSuccess(t, resp.Body.Bytes())
}

func TestPlanGuard_BasicCannotAccessPro(t *testing.T) {
	skipIfNoDB(t)

	endpoints := []struct {
		method string
		path   string
		body   string
	}{
		{"POST", "/api/v1/pricing/auto-handle", `{"shop_id":1}`},
		{"GET", "/api/v1/api-sync/shops", ""},
		{"GET", "/api/v1/scheduler/tasks", ""},
		{"GET", "/api/v1/analysis/report", ""},
	}

	for _, ep := range endpoints {
		t.Run(fmt.Sprintf("%s %s", ep.method, ep.path), func(t *testing.T) {
			req := makeAuthRequest(ep.method, ep.path, testUserToken, ep.body)
			resp := executeRequest(req)

			assert.Equal(t, http.StatusForbidden, resp.Code)
			requireError(t, resp.Body.Bytes(), "PLAN_ACCESS_DENIED", http.StatusForbidden)
		})
	}
}

func TestPlanGuard_ProCanAccessProEndpoints(t *testing.T) {
	skipIfNoDB(t)

	req := makeAuthRequest("GET", "/api/v1/scheduler/tasks", proToken, "")
	resp := executeRequest(req)

	assert.Equal(t, http.StatusOK, resp.Code)
	_ = requireSuccess(t, resp.Body.Bytes())
}

func TestPlanGuard_ProCannotAccessEnterprise(t *testing.T) {
	skipIfNoDB(t)

	req := makeAuthRequest("GET", "/api/v1/supplier/list", proToken, "")
	resp := executeRequest(req)

	assert.Equal(t, http.StatusForbidden, resp.Code)
	requireError(t, resp.Body.Bytes(), "PLAN_ACCESS_DENIED", http.StatusForbidden)
}

func TestPlanGuard_EnterpriseCanAccessAll(t *testing.T) {
	skipIfNoDB(t)

	endpoints := []struct {
		method string
		path   string
		body   string
	}{
		{"GET", "/api/v1/dashboard/overview", ""},
		{"GET", "/api/v1/supplier/list", ""},
	}

	for _, ep := range endpoints {
		t.Run(fmt.Sprintf("%s %s", ep.method, ep.path), func(t *testing.T) {
			req := makeAuthRequest(ep.method, ep.path, enterpriseToken, ep.body)
			resp := executeRequest(req)

			assert.Equal(t, http.StatusOK, resp.Code)
			_ = requireSuccess(t, resp.Body.Bytes())
		})
	}
}

func TestPricingEngine_Calculate(t *testing.T) {
	skipIfNoDB(t)

	req := makeAuthRequest("POST", "/api/v1/pricing-engine/calculate",
		testUserToken, `{"cost_price":50,"expected_margin":20}`)
	resp := executeRequest(req)

	assert.Equal(t, http.StatusOK, resp.Code)
	respData := requireSuccess(t, resp.Body.Bytes())

	var data map[string]interface{}
	err := json.Unmarshal(respData.Data, &data)
	require.NoError(t, err)

	result, ok := data["result"].(map[string]interface{})
	require.True(t, ok)
	assert.Equal(t, float64(50), result["cost_price"])
	assert.Equal(t, float64(20), result["expected_margin"])
	assert.Equal(t, "62.50", result["recommended_price"])
}

func TestBindAndGetShops(t *testing.T) {
	skipIfNoDB(t)

	t.Cleanup(func() {
		repository.GetDB().Exec("DELETE FROM temu_shops WHERE shop_name LIKE 'test-int-shop-%'")
	})

	bindReq := makeAuthRequest("POST", "/api/v1/api-sync/bind-shop",
		proToken, `{"shop_name":"test-int-shop-bind","access_token":"test-token-123"}`)
	bindResp := executeRequest(bindReq)
	assert.Equal(t, http.StatusOK, bindResp.Code)
	_ = requireSuccess(t, bindResp.Body.Bytes())

	getReq := makeAuthRequest("GET", "/api/v1/api-sync/shops", proToken, "")
	getResp := executeRequest(getReq)
	assert.Equal(t, http.StatusOK, getResp.Code)

	getData := requireSuccess(t, getResp.Body.Bytes())
	var data map[string]interface{}
	err := json.Unmarshal(getData.Data, &data)
	require.NoError(t, err)
	shops, ok := data["shops"].([]interface{})
	require.True(t, ok)

	var found bool
	for _, s := range shops {
		shop, ok := s.(map[string]interface{})
		if ok && shop["ShopName"] == "test-int-shop-bind" {
			found = true
			break
		}
	}
	assert.True(t, found, "bound shop should be in shop list")
}

func TestCORSHeaders(t *testing.T) {
	req := makeJSONRequest("OPTIONS", "/api/v1/auth/login", "")
	resp := executeRequest(req)

	assert.Equal(t, http.StatusNoContent, resp.Code)
	assert.Equal(t, "*", resp.Header().Get("Access-Control-Allow-Origin"))
	assert.Contains(t, resp.Header().Get("Access-Control-Allow-Methods"), "POST")
}

func TestGetShops_Unauthenticated(t *testing.T) {
	req := makeJSONRequest("GET", "/api/v1/api-sync/shops", "")
	resp := executeRequest(req)

	assert.Equal(t, http.StatusUnauthorized, resp.Code)
}

func TestGetShops_PlanGuardBasic(t *testing.T) {
	skipIfNoDB(t)

	req := makeAuthRequest("GET", "/api/v1/api-sync/shops", testUserToken, "")
	resp := executeRequest(req)

	assert.Equal(t, http.StatusForbidden, resp.Code)
}

func TestGetShops_PlanGuardPro(t *testing.T) {
	skipIfNoDB(t)

	req := makeAuthRequest("GET", "/api/v1/api-sync/shops", proToken, "")
	resp := executeRequest(req)

	assert.Equal(t, http.StatusOK, resp.Code)
}

func TestFactoryCost_EnterpriseOnly(t *testing.T) {
	skipIfNoDB(t)

	tests := []struct {
		name  string
		token string
		code  int
	}{
		{"basic user denied", testUserToken, http.StatusForbidden},
		{"pro user denied", proToken, http.StatusForbidden},
		{"enterprise allowed", enterpriseToken, http.StatusOK},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := makeAuthRequest("GET", "/api/v1/factory-cost/products", tt.token, "")
			resp := executeRequest(req)
			assert.Equal(t, tt.code, resp.Code)
		})
	}
}

func TestRiskInspection_BasicAccess(t *testing.T) {
	skipIfNoDB(t)

	req := makeAuthRequest("GET", "/api/v1/risk-inspection/report", testUserToken, "")
	resp := executeRequest(req)

	assert.Equal(t, http.StatusOK, resp.Code)
	_ = requireSuccess(t, resp.Body.Bytes())
}

func TestInventory_BasicAccess(t *testing.T) {
	skipIfNoDB(t)

	req := makeAuthRequest("GET", "/api/v1/inventory/list", testUserToken, "")
	resp := executeRequest(req)

	assert.Equal(t, http.StatusOK, resp.Code)
	_ = requireSuccess(t, resp.Body.Bytes())
}

func TestAdminListUsers_LifetimeOnly(t *testing.T) {
	skipIfNoDB(t)

	t.Run("basic user gets 403", func(t *testing.T) {
		req := makeAuthRequest("GET", "/api/v1/admin/users", testUserToken, "")
		resp := executeRequest(req)
		assert.Equal(t, http.StatusForbidden, resp.Code)
		requireError(t, resp.Body.Bytes(), "PLAN_ACCESS_DENIED", http.StatusForbidden)
	})

	t.Run("lifetime user gets 200", func(t *testing.T) {
		req := makeAuthRequest("GET", "/api/v1/admin/users", lifetimeToken, "")
		resp := executeRequest(req)
		assert.Equal(t, http.StatusOK, resp.Code)
		data := requireSuccess(t, resp.Body.Bytes())
		var result map[string]interface{}
		err := json.Unmarshal(data.Data, &result)
		require.NoError(t, err)
		assert.Contains(t, result, "users")
		assert.Contains(t, result, "total")
		assert.Contains(t, result, "page")
	})
}

func TestAdminUpgradePlan_Success(t *testing.T) {
	skipIfNoDB(t)

	email := "test-upgrade@test.com"
	t.Cleanup(func() {
		repository.GetDB().Exec("DELETE FROM temu_users WHERE email = ?", email)
	})

	_, err := repository.CreateUser(email, "testPass123", "basic", "2026-05-18", true, true)
	require.NoError(t, err)

	req := makeAuthRequest("POST", "/api/v1/admin/upgrade-plan",
		lifetimeToken, `{"email":"`+email+`","plan_type":"pro"}`)
	resp := executeRequest(req)
	assert.Equal(t, http.StatusOK, resp.Code)
	data := requireSuccess(t, resp.Body.Bytes())
	var result map[string]interface{}
	err = json.Unmarshal(data.Data, &result)
	require.NoError(t, err)
	assert.Contains(t, result["message"], email)
	assert.Contains(t, result["message"], "pro")
}

func TestAdminUpgradePlan_InvalidPlan(t *testing.T) {
	skipIfNoDB(t)

	req := makeAuthRequest("POST", "/api/v1/admin/upgrade-plan",
		lifetimeToken, `{"email":"test@test.com","plan_type":"vip"}`)
	resp := executeRequest(req)
	assert.Equal(t, http.StatusBadRequest, resp.Code)
}

func TestAdminUpgradePlan_UserNotFound(t *testing.T) {
	skipIfNoDB(t)

	req := makeAuthRequest("POST", "/api/v1/admin/upgrade-plan",
		lifetimeToken, `{"email":"nobody@test.com","plan_type":"pro"}`)
	resp := executeRequest(req)
	assert.Equal(t, http.StatusNotFound, resp.Code)
}

func TestAdminCompleteOrder_Success(t *testing.T) {
	skipIfNoDB(t)

	order := &models.Order{
		ContactName: "test-complete",
		Phone:       "13800138000",
		PlanName:    "pro",
		Amount:      199,
		Status:      "pending",
	}
	err := repository.CreateOrder(order)
	require.NoError(t, err)
	require.Greater(t, order.OrderID, 0)
	t.Cleanup(func() {
		repository.GetDB().Exec("DELETE FROM temu_orders WHERE order_id = ?", order.OrderID)
	})

	req := makeAuthRequest("POST", "/api/v1/admin/orders/complete",
		lifetimeToken, `{"order_id":`+strconv.Itoa(order.OrderID)+`}`)
	resp := executeRequest(req)
	assert.Equal(t, http.StatusOK, resp.Code)
	data := requireSuccess(t, resp.Body.Bytes())
	var result map[string]interface{}
	err = json.Unmarshal(data.Data, &result)
	require.NoError(t, err)
	assert.Contains(t, result["message"], "已标记为已处理")
}

func TestAdminCompleteOrder_NotFound(t *testing.T) {
	skipIfNoDB(t)

	req := makeAuthRequest("POST", "/api/v1/admin/orders/complete",
		lifetimeToken, `{"order_id":999999999}`)
	resp := executeRequest(req)
	assert.Equal(t, http.StatusNotFound, resp.Code)
}

func TestAdminDeleteOrder_Success(t *testing.T) {
	skipIfNoDB(t)

	order := &models.Order{
		ContactName: "test-delete",
		Phone:       "13800138001",
		PlanName:    "basic",
		Amount:      99,
		Status:      "pending",
	}
	err := repository.CreateOrder(order)
	require.NoError(t, err)
	require.Greater(t, order.OrderID, 0)

	req := makeAuthRequest("POST", "/api/v1/admin/orders/delete",
		lifetimeToken, `{"order_id":`+strconv.Itoa(order.OrderID)+`}`)
	resp := executeRequest(req)
	assert.Equal(t, http.StatusOK, resp.Code)
	data := requireSuccess(t, resp.Body.Bytes())
	var result map[string]interface{}
	err = json.Unmarshal(data.Data, &result)
	require.NoError(t, err)
	assert.Contains(t, result["message"], "已删除")
}

func TestAdminDeleteOrder_NotFound(t *testing.T) {
	skipIfNoDB(t)

	req := makeAuthRequest("POST", "/api/v1/admin/orders/delete",
		lifetimeToken, `{"order_id":999999999}`)
	resp := executeRequest(req)
	assert.Equal(t, http.StatusNotFound, resp.Code)
}

func TestAdminListUsers_SearchPagination(t *testing.T) {
	skipIfNoDB(t)

	req := makeAuthRequest("GET", "/api/v1/admin/users?search=integ-test&page=1&page_size=5", lifetimeToken, "")
	resp := executeRequest(req)
	assert.Equal(t, http.StatusOK, resp.Code)
	data := requireSuccess(t, resp.Body.Bytes())
	var result map[string]interface{}
	err := json.Unmarshal(data.Data, &result)
	require.NoError(t, err)
	assert.Contains(t, result, "users")
	assert.Contains(t, result, "total")
	assert.GreaterOrEqual(t, result["total"].(float64), float64(1))
}

func TestAdminRenewUser_NotFound(t *testing.T) {
	skipIfNoDB(t)

	req := makeAuthRequest("POST", "/api/v1/admin/users/renew",
		lifetimeToken, `{"email":"no-such-user@test.com","days":30}`)
	resp := executeRequest(req)
	assert.Equal(t, http.StatusNotFound, resp.Code)
}

func TestAdminToggleUser_NotFound(t *testing.T) {
	skipIfNoDB(t)

	req := makeAuthRequest("POST", "/api/v1/admin/users/toggle",
		lifetimeToken, `{"email":"no-such-user@test.com","active":false}`)
	resp := executeRequest(req)
	assert.Equal(t, http.StatusNotFound, resp.Code)
}

func TestLogin_WithOriginalPasswordAfterSeedAdmin(t *testing.T) {
	skipIfNoDB(t)

	email := "test-seed-login@test.com"
	t.Cleanup(func() {
		repository.GetDB().Exec("DELETE FROM temu_users WHERE email = ?", email)
	})

	_, err := repository.CreateUser(email, "originalPass123", "basic", "2026-05-18", true, true)
	require.NoError(t, err, "user should register first")

	repository.SeedAdmin(email, "adminEnvPass456")

	t.Run("login with original password succeeds", func(t *testing.T) {
		req := makeJSONRequest("POST", "/api/v1/auth/login",
			`{"email":"`+email+`","password":"originalPass123"}`)
		resp := executeRequest(req)
		assert.Equal(t, http.StatusOK, resp.Code)
		data := requireSuccess(t, resp.Body.Bytes())
		var result map[string]interface{}
		err := json.Unmarshal(data.Data, &result)
		require.NoError(t, err)
		assert.Contains(t, result, "token")
		user, ok := result["user"].(map[string]interface{})
		require.True(t, ok)
		assert.Equal(t, "lifetime", user["plan"], "plan should be upgraded to lifetime")
	})

	t.Run("login with admin env password fails", func(t *testing.T) {
		req := makeJSONRequest("POST", "/api/v1/auth/login",
			`{"email":"`+email+`","password":"adminEnvPass456"}`)
		resp := executeRequest(req)
		assert.Equal(t, http.StatusUnauthorized, resp.Code,
			"admin env password should NOT work after SeedAdmin")
	})
}

func TestAdminRenewUser(t *testing.T) {
	skipIfNoDB(t)

	email := "test-renew@test.com"
	t.Cleanup(func() {
		repository.GetDB().Exec("DELETE FROM temu_users WHERE email = ?", email)
	})

	_, err := repository.CreateUser(email, "testPass123", "basic", "2026-05-18", true, true)
	require.NoError(t, err)

	req := makeAuthRequest("POST", "/api/v1/admin/users/renew",
		lifetimeToken, `{"email":"`+email+`","days":30}`)
	resp := executeRequest(req)
	assert.Equal(t, http.StatusOK, resp.Code)

	t.Run("basic user gets 403", func(t *testing.T) {
		req := makeAuthRequest("POST", "/api/v1/admin/users/renew",
			testUserToken, `{"email":"`+email+`","days":30}`)
		resp := executeRequest(req)
		assert.Equal(t, http.StatusForbidden, resp.Code)
	})
}

func TestAdminToggleUser(t *testing.T) {
	skipIfNoDB(t)

	email := "test-toggle@test.com"
	t.Cleanup(func() {
		repository.GetDB().Exec("DELETE FROM temu_users WHERE email = ?", email)
	})

	_, err := repository.CreateUser(email, "testPass123", "basic", "2026-05-18", true, true)
	require.NoError(t, err)

	req := makeAuthRequest("POST", "/api/v1/admin/users/toggle",
		lifetimeToken, `{"email":"`+email+`","active":false}`)
	resp := executeRequest(req)
	assert.Equal(t, http.StatusOK, resp.Code)
}

func TestAdminOrders(t *testing.T) {
	skipIfNoDB(t)

	t.Run("rejects non-lifetime", func(t *testing.T) {
		req := makeAuthRequest("GET", "/api/v1/admin/orders", testUserToken, "")
		resp := executeRequest(req)
		assert.Equal(t, http.StatusForbidden, resp.Code)
	})

	t.Run("lifetime gets 200", func(t *testing.T) {
		req := makeAuthRequest("GET", "/api/v1/admin/orders", lifetimeToken, "")
		resp := executeRequest(req)
		assert.Equal(t, http.StatusOK, resp.Code)
	})
}

func TestAdminMonitor(t *testing.T) {
	skipIfNoDB(t)

	t.Run("rejects non-lifetime", func(t *testing.T) {
		req := makeAuthRequest("GET", "/api/v1/admin/monitor", testUserToken, "")
		resp := executeRequest(req)
		assert.Equal(t, http.StatusForbidden, resp.Code)
	})

	t.Run("lifetime gets 200", func(t *testing.T) {
		req := makeAuthRequest("GET", "/api/v1/admin/monitor", lifetimeToken, "")
		resp := executeRequest(req)
		assert.Equal(t, http.StatusOK, resp.Code)
		var result map[string]interface{}
		data := requireSuccess(t, resp.Body.Bytes())
		err := json.Unmarshal(data.Data, &result)
		require.NoError(t, err)
		assert.Contains(t, result, "cpu")
		assert.Contains(t, result, "memory")
		assert.Contains(t, result, "disk")
	})
}
