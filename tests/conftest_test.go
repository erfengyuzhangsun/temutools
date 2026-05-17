package tests

import (
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
	"strconv"
	"strings"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"golang.org/x/crypto/bcrypt"

	"github.com/erfengyuzhangsun/temutools/internal/api"
	"github.com/erfengyuzhangsun/temutools/internal/auth"
	"github.com/erfengyuzhangsun/temutools/internal/config"
	"github.com/erfengyuzhangsun/temutools/internal/models"
	"github.com/erfengyuzhangsun/temutools/internal/repository"
)

var (
	testRouter       *gin.Engine
	testAuthService  *auth.AuthService
	testUserID       int
	testUserToken    string
	proToken         string
	enterpriseToken  string
	lifetimeToken    string
	testDBReady      bool
)

func TestMain(m *testing.M) {
	gin.SetMode(gin.TestMode)

	testAuthService = auth.NewAuthService("test-jwt-secret-for-integration-tests", 24)

	testRouter = api.SetupRouter(testAuthService)

	dbConfig := config.DatabaseConfig{
		Host:     getEnv("DB_HOST", "localhost"),
		Port:     getEnvInt("DB_PORT", 3306),
		User:     getEnv("DB_USER", "root"),
		Password: os.Getenv("DB_PASSWORD"),
		DBName:   getEnv("DB_NAME", "temu_tools"),
	}

	_, err := repository.InitDB(dbConfig)
	if err != nil {
		fmt.Printf("SKIP DB-dependent tests: database unavailable (%v)\n", err)
		testDBReady = false
		code := m.Run()
		os.Exit(code)
	}

	sqlDB, err := repository.GetDB().DB()
	if err != nil || sqlDB.Ping() != nil {
		fmt.Printf("SKIP integration tests: database ping failed\n")
		testDBReady = false
		code := m.Run()
		os.Exit(code)
	}

	if err := repository.AutoMigrate(); err != nil {
		fmt.Printf("SKIP integration tests: auto migrate failed (%v)\n", err)
		testDBReady = false
		code := m.Run()
		os.Exit(code)
	}

	testDBReady = true

	err = seedTestData()
	if err != nil {
		fmt.Printf("SKIP integration tests: seed failed (%v)\n", err)
		testDBReady = false
		code := m.Run()
		os.Exit(code)
	}

	code := m.Run()
	cleanupTestData()
	repository.Close()
	os.Exit(code)
}

func seedTestData() error {
	if err := repository.GetDB().Exec("DELETE FROM temu_users WHERE email = 'integ-test@example.com'").Error; err != nil {
		return fmt.Errorf("delete existing user: %w", err)
	}

	hashedBytes, err := bcrypt.GenerateFromPassword([]byte("test-pass-123"), bcrypt.MinCost)
	if err != nil {
		return fmt.Errorf("hash password: %w", err)
	}

	startDate := parseDate("2026-01-01")
	expireDate := parseDate("2027-01-01")
	user := models.User{
		Email:        "integ-test@example.com",
		PasswordHash: string(hashedBytes),
		WechatNickname: "integration-test-user",
		PlanType:       "basic",
		StartDate:      &startDate,
		ExpireDate:     &expireDate,
		IsActive:       true,
	}
	if err := repository.GetDB().Create(&user).Error; err != nil {
		return fmt.Errorf("create test user: %w", err)
	}
	testUserID = user.UserID

	testUserToken, err = testAuthService.GenerateToken(testUserID, "basic")
	if err != nil {
		return fmt.Errorf("generate basic token: %w", err)
	}
	proToken, err = testAuthService.GenerateToken(testUserID, "pro")
	if err != nil {
		return fmt.Errorf("generate pro token: %w", err)
	}
	enterpriseToken, err = testAuthService.GenerateToken(testUserID, "enterprise")
	if err != nil {
		return fmt.Errorf("generate enterprise token: %w", err)
	}
	lifetimeToken, err = testAuthService.GenerateToken(testUserID, "lifetime")
	if err != nil {
		return fmt.Errorf("generate lifetime token: %w", err)
	}

	return nil
}

func cleanupTestData() {
	if repository.GetDB() != nil {
		repository.GetDB().Exec("DELETE FROM temu_users WHERE email = 'integ-test@example.com'")
		repository.GetDB().Exec("DELETE FROM temu_users WHERE email LIKE 'test-reg-%'")
		repository.GetDB().Exec("DELETE FROM temu_shops WHERE shop_name LIKE 'test-int-shop-%'")
	}
}

func executeRequest(req *http.Request) *httptest.ResponseRecorder {
	w := httptest.NewRecorder()
	testRouter.ServeHTTP(w, req)
	return w
}

func makeJSONRequest(method, path, body string) *http.Request {
	req := httptest.NewRequest(method, path, strings.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	return req
}

func makeAuthRequest(method, path, token, body string) *http.Request {
	req := makeJSONRequest(method, path, body)
	req.Header.Set("Authorization", "Bearer "+token)
	return req
}

func getEnv(key, defaultVal string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return defaultVal
}

func getEnvInt(key string, defaultVal int) int {
	if v := os.Getenv(key); v != "" {
		if i, err := strconv.Atoi(v); err == nil {
			return i
		}
	}
	return defaultVal
}

func parseDate(s string) time.Time {
	t, err := time.Parse("2006-01-02", s)
	if err != nil {
		panic(err)
	}
	return t
}
