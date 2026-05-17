package repository

import (
	"fmt"
	"os"
	"strconv"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"golang.org/x/crypto/bcrypt"
	"gorm.io/gorm"

	"github.com/erfengyuzhangsun/temutools/internal/config"
	"github.com/erfengyuzhangsun/temutools/internal/models"
)

var testDB *gorm.DB

func TestMain(m *testing.M) {
	dbConfig := config.DatabaseConfig{
		Host:     getEnvOrDefault("DB_HOST", "localhost"),
		Port:     getEnvIntOrDefault("DB_PORT", 3306),
		User:     getEnvOrDefault("DB_USER", "root"),
		Password: os.Getenv("DB_PASSWORD"),
		DBName:   getEnvOrDefault("DB_NAME", "temu_tools"),
	}

	var err error
	testDB, err = InitDB(dbConfig)
	if err != nil {
		fmt.Printf("SKIP repository tests: database unavailable (%v)\n", err)
		os.Exit(0)
	}

	sqlDB, err := testDB.DB()
	if err != nil {
		fmt.Printf("SKIP repository tests: sql.DB unavailable (%v)\n", err)
		os.Exit(0)
	}
	if err := sqlDB.Ping(); err != nil {
		fmt.Printf("SKIP repository tests: database ping failed (%v)\n", err)
		os.Exit(0)
	}

	if err := AutoMigrate(); err != nil {
		fmt.Printf("SKIP repository tests: auto migrate failed (%v)\n", err)
		os.Exit(0)
	}

	fmt.Println("repository tests: database connected, running tests...")
	code := m.Run()

	cleanupTestData()
	_ = Close()
	os.Exit(code)
}

func cleanupTestData() {
	if db := GetDB(); db != nil {
		db.Exec("DELETE FROM temu_pricing_logs WHERE sku LIKE 'test-sku-%'")
		db.Exec("DELETE FROM temu_sync_records WHERE sync_type = 'test'")
		db.Exec("DELETE FROM temu_scheduler_tasks WHERE task_id LIKE 'test-task-%'")
		db.Exec("DELETE FROM temu_scheduler_logs WHERE task_id LIKE 'test-task-%'")
		db.Exec("DELETE FROM temu_sku_profit WHERE sku_code LIKE 'test-sku-%'")
		db.Exec("DELETE FROM temu_shops WHERE shop_name LIKE 'test-shop-%'")
		db.Exec("DELETE FROM temu_users WHERE email LIKE 'user-%@test.com'")
		db.Exec("DELETE FROM temu_profit_stats WHERE stat_id > 999000")
	}
}

func getEnvOrDefault(key, defaultVal string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return defaultVal
}

func getEnvIntOrDefault(key string, defaultVal int) int {
	if v := os.Getenv(key); v != "" {
		if i, err := strconv.Atoi(v); err == nil {
			return i
		}
	}
	return defaultVal
}

func createTestUser(t *testing.T, suffix string) *models.User {
	t.Helper()
	startDate := parseDate("2026-01-01")
	expireDate := parseDate("2027-01-01")
	hashed, err := bcryptHash(fmt.Sprintf("pass_%s", suffix))
	require.NoError(t, err)
	user := models.User{
		Email:          fmt.Sprintf("user-%s@test.com", suffix),
		PasswordHash:   hashed,
		WechatNickname: fmt.Sprintf("test-user-%s", suffix),
		PlanType:       "basic",
		StartDate:      &startDate,
		ExpireDate:     &expireDate,
		IsActive:       true,
	}
	err = GetDB().Create(&user).Error
	require.NoError(t, err)
	t.Cleanup(func() {
		GetDB().Unscoped().Delete(&models.User{}, user.UserID)
	})
	return &user
}

func bcryptHash(password string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.MinCost)
	if err != nil {
		return "", err
	}
	return string(bytes), nil
}

func parseDate(s string) time.Time {
	t, err := time.Parse("2006-01-02", s)
	if err != nil {
		panic(err)
	}
	return t
}

func createTestShop(t *testing.T, userID int, suffix string) *models.Shop {
	t.Helper()
	shop := models.Shop{
		UserID:   userID,
		ShopName: fmt.Sprintf("test-shop-%s", suffix),
	}
	err := GetDB().Create(&shop).Error
	require.NoError(t, err)
	t.Cleanup(func() {
		GetDB().Unscoped().Delete(&models.Shop{}, shop.ShopID)
	})
	return &shop
}

func createTestSkuProfit(t *testing.T, userID, shopID int, suffix string) *models.SkuProfit {
	t.Helper()
	sku := models.SkuProfit{
		UserID:     userID,
		ShopID:     shopID,
		SkuCode:    fmt.Sprintf("test-sku-%s", suffix),
		SkuName:    fmt.Sprintf("Test SKU %s", suffix),
		Category:   "test",
		CostPrice:  50.00,
		TotalSales: 10,
	}
	err := GetDB().Create(&sku).Error
	require.NoError(t, err)
	t.Cleanup(func() {
		GetDB().Unscoped().Delete(&models.SkuProfit{}, sku.SkuID)
	})
	return &sku
}

func cleanupPricingLogs(t *testing.T, userID, shopID int) {
	t.Helper()
	GetDB().Where("user_id = ? AND shop_id = ?", userID, shopID).Delete(&models.PricingLog{})
}

// ====== User Repository Tests ======

func TestFindByEmail_Valid(t *testing.T) {
	user := createTestUser(t, "find-email")
	found, err := FindByEmail(user.Email)
	require.NoError(t, err)
	require.NotNil(t, found)
	assert.Equal(t, user.UserID, found.UserID)
	assert.Equal(t, user.Email, found.Email)
	assert.Equal(t, user.WechatNickname, found.WechatNickname)
}

func TestFindByEmail_NotFound(t *testing.T) {
	found, err := FindByEmail("nonexistent@test.com")
	require.NoError(t, err)
	assert.Nil(t, found)
}

func TestFindByEmail_Inactive(t *testing.T) {
	email := "inactive-user@test.com"
	hashed, err := bcryptHash("somepassword")
	require.NoError(t, err)
	err = GetDB().Exec(
		"INSERT INTO temu_users (email, password_hash, wechat_nickname, plan_type, start_date, expire_date, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)",
		email, hashed, "inactive-user", "basic", "2026-01-01", "2027-01-01", false,
	).Error
	require.NoError(t, err)
	t.Cleanup(func() {
		GetDB().Exec("DELETE FROM temu_users WHERE email = ?", email)
	})

	found, err := FindByEmail(email)
	require.NoError(t, err)
	assert.Nil(t, found)
}

func TestCreateUser_Success(t *testing.T) {
	email := "test-create-user@test.com"
	t.Cleanup(func() {
		GetDB().Unscoped().Delete(&models.User{}, "email = ?", email)
	})

	user, err := CreateUser(email, "securePass123", "basic")
	require.NoError(t, err)
	require.NotNil(t, user)
	assert.Equal(t, email, user.Email)
	assert.Equal(t, "basic", user.PlanType)
	assert.True(t, user.IsActive)
	assert.Greater(t, user.UserID, 0)
	assert.NotEmpty(t, user.PasswordHash)
	assert.True(t, CheckPassword("securePass123", user.PasswordHash))
}

func TestCreateUser_DuplicateEmail(t *testing.T) {
	existing := createTestUser(t, "dup-email")

	user, err := CreateUser(existing.Email, "anotherPass123", "pro")
	assert.Error(t, err)
	assert.Nil(t, user)
}

func TestCheckPassword_Valid(t *testing.T) {
	hashed, err := bcryptHash("myTestPassword")
	require.NoError(t, err)
	assert.True(t, CheckPassword("myTestPassword", hashed))
}

func TestCheckPassword_Invalid(t *testing.T) {
	hashed, err := bcryptHash("correctPassword")
	require.NoError(t, err)
	assert.False(t, CheckPassword("wrongPassword", hashed))
}

func TestCheckPassword_EmptyHash(t *testing.T) {
	assert.False(t, CheckPassword("anyPassword", ""))
}

func TestIsUserExpired_NoExpireDate(t *testing.T) {
	user := &models.User{ExpireDate: nil}
	assert.False(t, IsUserExpired(user))
}

func TestIsUserExpired_NotExpired(t *testing.T) {
	futureDate := time.Now().AddDate(0, 1, 0)
	user := &models.User{ExpireDate: &futureDate}
	assert.False(t, IsUserExpired(user))
}

func TestIsUserExpired_Expired(t *testing.T) {
	pastDate := time.Now().AddDate(0, -1, 0)
	user := &models.User{ExpireDate: &pastDate}
	assert.True(t, IsUserExpired(user))
}

// ====== SeedAdmin Tests ======

func TestSeedAdmin_CreatesNewUser(t *testing.T) {
	email := "test-seed-admin-new@test.com"
	t.Cleanup(func() {
		GetDB().Unscoped().Delete(&models.User{}, "email = ?", email)
	})

	SeedAdmin(email, "adminPass123")

	user, err := FindByEmail(email)
	require.NoError(t, err)
	require.NotNil(t, user, "SeedAdmin should create the user")
	assert.Equal(t, "lifetime", user.PlanType, "admin should have lifetime plan")
	assert.True(t, CheckPassword("adminPass123", user.PasswordHash), "admin should be able to login with env password")
}

func TestSeedAdmin_UpgradesExistingPlan(t *testing.T) {
	email := "test-seed-admin-upgrade@test.com"
	t.Cleanup(func() {
		GetDB().Unscoped().Delete(&models.User{}, "email = ?", email)
	})

	user, err := CreateUser(email, "userPassword123", "basic")
	require.NoError(t, err)
	assert.Equal(t, "basic", user.PlanType, "should start as basic")

	SeedAdmin(email, "userPassword123")

	updated, err := FindByEmail(email)
	require.NoError(t, err)
	require.NotNil(t, updated)
	assert.Equal(t, "lifetime", updated.PlanType, "SeedAdmin should upgrade plan to lifetime")
}

func TestSeedAdmin_DoesNotOverwriteUserPassword(t *testing.T) {
	email := "test-seed-admin-pw@test.com"
	t.Cleanup(func() {
		GetDB().Unscoped().Delete(&models.User{}, "email = ?", email)
	})

	_, err := CreateUser(email, "myRealPassword", "basic")
	require.NoError(t, err)

	SeedAdmin(email, "adminEnvPassword")

	user, err := FindByEmail(email)
	require.NoError(t, err)
	require.NotNil(t, user)
	assert.Equal(t, "lifetime", user.PlanType, "plan should be upgraded to lifetime")
	assert.True(t, CheckPassword("myRealPassword", user.PasswordHash),
		"user's original password should NOT be overwritten by SeedAdmin")
	assert.False(t, CheckPassword("adminEnvPassword", user.PasswordHash),
		"SeedAdmin's env password should NOT work after overwriting")
}

// ====== Shop Repository Tests ======

func TestCreateAndGetUserShops(t *testing.T) {
	user := createTestUser(t, "shops-1")
	shop1 := createTestShop(t, user.UserID, "list-1")
	shop2 := createTestShop(t, user.UserID, "list-2")

	shops, err := GetUserShops(user.UserID)
	require.NoError(t, err)

	found1, found2 := false, false
	for _, s := range shops {
		if s.ShopID == shop1.ShopID {
			found1 = true
		}
		if s.ShopID == shop2.ShopID {
			found2 = true
		}
	}
	assert.True(t, found1, "shop1 should be in results")
	assert.True(t, found2, "shop2 should be in results")
}

func TestGetUserShops_OtherUserNotVisible(t *testing.T) {
	user1 := createTestUser(t, "shops-vis-1")
	user2 := createTestUser(t, "shops-vis-2")
	shop := createTestShop(t, user1.UserID, "visibility")

	shops, err := GetUserShops(user2.UserID)
	require.NoError(t, err)

	for _, s := range shops {
		assert.NotEqual(t, shop.ShopID, s.ShopID, "user2 should not see user1's shop")
	}
}

func TestCreateShop_AssignsID(t *testing.T) {
	user := createTestUser(t, "shops-create-id")
	shopID, err := CreateShop(user.UserID, "test-shop-create-id-assert")
	require.NoError(t, err)
	assert.Greater(t, shopID, 0)
	t.Cleanup(func() { GetDB().Unscoped().Delete(&models.Shop{}, shopID) })
}

func TestDeleteShop(t *testing.T) {
	user := createTestUser(t, "shops-delete")
	shopID, err := CreateShop(user.UserID, "test-shop-delete-me")
	require.NoError(t, err)
	assert.Greater(t, shopID, 0)

	err = DeleteShop(shopID)
	require.NoError(t, err)

	var count int64
	GetDB().Model(&models.Shop{}).Where("shop_id = ?", shopID).Count(&count)
	assert.Equal(t, int64(0), count)
}

func TestGetShopProfit_WithData(t *testing.T) {
	user := createTestUser(t, "profit-1")
	shop := createTestShop(t, user.UserID, "profit")

	stat := models.ProfitStat{
		UserID:      user.UserID,
		ShopID:      shop.ShopID,
		StatDate:    "2026-05-01",
		TotalProfit: 1500.00,
		TotalRevenue: 10000.00,
	}
	err := GetDB().Create(&stat).Error
	require.NoError(t, err)
	t.Cleanup(func() { GetDB().Unscoped().Delete(&models.ProfitStat{}, stat.StatID) })

	profit, err := GetShopProfit(user.UserID, shop.ShopID)
	require.NoError(t, err)
	assert.Equal(t, 1500.00, profit)
}

func TestGetShopProfit_NoData(t *testing.T) {
	user := createTestUser(t, "profit-2")
	shop := createTestShop(t, user.UserID, "profit-empty")

	profit, err := GetShopProfit(user.UserID, shop.ShopID)
	require.NoError(t, err)
	assert.Equal(t, 0.0, profit)
}

func TestGetShopRevenue_WithData(t *testing.T) {
	user := createTestUser(t, "rev-1")
	shop := createTestShop(t, user.UserID, "revenue")

	stat := models.ProfitStat{
		UserID:      user.UserID,
		ShopID:      shop.ShopID,
		StatDate:    "2026-05-01",
		TotalProfit: 500.00,
		TotalRevenue: 8000.00,
	}
	err := GetDB().Create(&stat).Error
	require.NoError(t, err)
	t.Cleanup(func() { GetDB().Unscoped().Delete(&models.ProfitStat{}, stat.StatID) })

	revenue, err := GetShopRevenue(user.UserID, shop.ShopID)
	require.NoError(t, err)
	assert.Equal(t, 8000.00, revenue)
}

func TestGetShopRevenue_NoData(t *testing.T) {
	user := createTestUser(t, "rev-2")
	shop := createTestShop(t, user.UserID, "rev-empty")

	revenue, err := GetShopRevenue(user.UserID, shop.ShopID)
	require.NoError(t, err)
	assert.Equal(t, 0.0, revenue)
}

func TestGetPricingPendingCount(t *testing.T) {
	user := createTestUser(t, "pp-1")
	shop := createTestShop(t, user.UserID, "pending")
	t.Cleanup(func() { cleanupPricingLogs(t, user.UserID, shop.ShopID) })

	_ = GetDB().Create(&models.PricingLog{
		UserID:    user.UserID,
		ShopID:    shop.ShopID,
		Sku:       "test-sku-pending-1",
		Action:    "skip",
		HandledAt: time.Now(),
	}).Error
	_ = GetDB().Create(&models.PricingLog{
		UserID:    user.UserID,
		ShopID:    shop.ShopID,
		Sku:       "test-sku-pending-2",
		Action:    "skip",
		HandledAt: time.Now(),
	}).Error

	count, err := GetPricingPendingCount(user.UserID, shop.ShopID)
	require.NoError(t, err)
	assert.Equal(t, 2, count)
}

func TestGetPricingPendingCount_NoData(t *testing.T) {
	user := createTestUser(t, "pp-2")
	shop := createTestShop(t, user.UserID, "pending-zero")

	count, err := GetPricingPendingCount(user.UserID, shop.ShopID)
	require.NoError(t, err)
	assert.Equal(t, 0, count)
}

func TestGetPricingExpiring(t *testing.T) {
	user := createTestUser(t, "expiring")
	shop := createTestShop(t, user.UserID, "expiring")

	result := GetPricingExpiring(user.UserID, shop.ShopID)
	assert.Nil(t, result)
}

// ====== Pricing Repository Tests ======

func TestSavePricingLog(t *testing.T) {
	user := createTestUser(t, "pl-1")
	shop := createTestShop(t, user.UserID, "pricing-log")
	t.Cleanup(func() { cleanupPricingLogs(t, user.UserID, shop.ShopID) })

	SavePricingLog(user.UserID, shop.ShopID, "notice-1", "test-sku-pl-1",
		"accept", 100.00, 50.00, 50.00, "毛利率达标", false)

	var count int64
	GetDB().Model(&models.PricingLog{}).
		Where("user_id = ? AND shop_id = ?", user.UserID, shop.ShopID).
		Count(&count)
	assert.Equal(t, int64(1), count)
}

func TestQueryPricingLogs(t *testing.T) {
	user := createTestUser(t, "pl-2")
	shop := createTestShop(t, user.UserID, "pricing-query")
	t.Cleanup(func() { cleanupPricingLogs(t, user.UserID, shop.ShopID) })

	SavePricingLog(user.UserID, shop.ShopID, "notice-2", "test-sku-pl-2",
		"accept", 120.00, 60.00, 50.00, "自动接受", false)
	SavePricingLog(user.UserID, shop.ShopID, "notice-3", "test-sku-pl-3",
		"reject", 80.00, 60.00, 25.00, "毛利率不足", true)

	logs, err := QueryPricingLogs(user.UserID, shop.ShopID, 10)
	require.NoError(t, err)
	assert.Len(t, logs, 2)

	if len(logs) == 2 {
		assert.Equal(t, "test-sku-pl-3", logs[0].Sku)
		assert.Equal(t, "test-sku-pl-2", logs[1].Sku)
	}
}

func TestQueryPricingLogs_NoData(t *testing.T) {
	user := createTestUser(t, "pl-3")
	shop := createTestShop(t, user.UserID, "pricing-empty")

	logs, err := QueryPricingLogs(user.UserID, shop.ShopID, 10)
	require.NoError(t, err)
	assert.Empty(t, logs)
}

func TestGetSkuCostPrice(t *testing.T) {
	user := createTestUser(t, "scp-1")
	shop := createTestShop(t, user.UserID, "cost")
	sku := createTestSkuProfit(t, user.UserID, shop.ShopID, "cost-1")

	price, err := GetSkuCostPrice(user.UserID, shop.ShopID, sku.SkuCode)
	require.NoError(t, err)
	assert.Equal(t, 50.00, price)
}

func TestGetSkuCostPrice_NotFound(t *testing.T) {
	user := createTestUser(t, "scp-2")
	shop := createTestShop(t, user.UserID, "cost-na")

	price, err := GetSkuCostPrice(user.UserID, shop.ShopID, "test-sku-nonexistent")
	require.NoError(t, err)
	assert.Equal(t, 0.0, price)
}

// ====== Sync Repository Tests ======

func TestSaveSyncRecord(t *testing.T) {
	user := createTestUser(t, "sr-1")
	shop := createTestShop(t, user.UserID, "sync-save")
	t.Cleanup(func() {
		GetDB().Where("user_id = ? AND shop_id = ?", user.UserID, shop.ShopID).Delete(&models.SyncRecord{})
	})

	SaveSyncRecord(user.UserID, shop.ShopID, "orders", 15, 100, 2*time.Second)

	var records []models.SyncRecord
	GetDB().Where("user_id = ? AND shop_id = ?", user.UserID, shop.ShopID).Find(&records)
	require.Len(t, records, 1)
	assert.Equal(t, "orders", records[0].SyncType)
	assert.Equal(t, 15, records[0].SyncedCount)
	assert.Equal(t, 100, records[0].TotalCount)
	assert.Equal(t, "success", records[0].Status)
}

func TestQuerySyncRecords(t *testing.T) {
	user := createTestUser(t, "sr-2")
	shop := createTestShop(t, user.UserID, "sync-query")
	t.Cleanup(func() {
		GetDB().Where("user_id = ? AND shop_id = ?", user.UserID, shop.ShopID).Delete(&models.SyncRecord{})
	})

	SaveSyncRecord(user.UserID, shop.ShopID, "orders", 10, 50, 1*time.Second)
	SaveSyncRecord(user.UserID, shop.ShopID, "pricing", 5, 20, 500*time.Millisecond)

	records, err := QuerySyncRecords(user.UserID, shop.ShopID, 10)
	require.NoError(t, err)
	assert.Len(t, records, 2)
	assert.Equal(t, "pricing", records[0].SyncType)
	assert.Greater(t, records[0].DurationMs, 0)
}

func TestQuerySyncRecords_NoData(t *testing.T) {
	user := createTestUser(t, "sr-3")
	shop := createTestShop(t, user.UserID, "sync-empty")

	records, err := QuerySyncRecords(user.UserID, shop.ShopID, 10)
	require.NoError(t, err)
	assert.Empty(t, records)
}

func TestGetExistingOrderIDs(t *testing.T) {
	user := createTestUser(t, "eo-1")
	shop := createTestShop(t, user.UserID, "existing-orders")

	ids := GetExistingOrderIDs(shop.ShopID)
	assert.Empty(t, ids)
}

// ====== Scheduler Repository Tests ======

func TestSaveAndQuerySchedulerTasks(t *testing.T) {
	suffix := fmt.Sprintf("task-%d", time.Now().Nanosecond())
	taskID := fmt.Sprintf("test-task-%s", suffix)
	t.Cleanup(func() {
		GetDB().Where("task_id LIKE ?", "test-task-%").Delete(&models.SchedulerTask{})
	})

	SaveSchedulerTask(taskID, "测试任务", "0 */5 * * * *",
		300, 3, true, "每5分钟执行的测试任务")

	tasks, err := QuerySchedulerTasks()
	require.NoError(t, err)

	var found bool
	for _, task := range tasks {
		if task.TaskID == taskID {
			found = true
			assert.Equal(t, "测试任务", task.Name)
			assert.Equal(t, "0 */5 * * * *", task.CronExpression)
			assert.True(t, task.Enabled)
			break
		}
	}
	assert.True(t, found, "saved task should be in query results")
}

func TestSaveAndQuerySchedulerLogs(t *testing.T) {
	taskID := "test-task-log-main"
	t.Cleanup(func() {
		GetDB().Where("task_id = ?", taskID).Delete(&models.SchedulerLog{})
	})

	now := time.Now()
	SaveSchedulerLog(taskID, "completed", now, 1.5, "", 0)

	logs, err := QuerySchedulerLogs(taskID, 10)
	require.NoError(t, err)
	require.Len(t, logs, 1)
	assert.Equal(t, "completed", logs[0].Status)
	assert.Equal(t, 1.5, logs[0].DurationSeconds)
	assert.Equal(t, taskID, logs[0].TaskID)
}

func TestQuerySchedulerLogs_AllTasks(t *testing.T) {
	t.Cleanup(func() {
		GetDB().Where("task_id LIKE 'test-task-log-all%'").Delete(&models.SchedulerLog{})
	})

	SaveSchedulerLog("test-task-log-all-1", "completed", time.Now(), 0.5, "", 0)
	SaveSchedulerLog("test-task-log-all-2", "failed", time.Now(), 2.0, "timeout", 1)

	logs, err := QuerySchedulerLogs("", 10)
	require.NoError(t, err)
	assert.GreaterOrEqual(t, len(logs), 2)
}

func TestQuerySchedulerLogs_NoData(t *testing.T) {
	logs, err := QuerySchedulerLogs("test-task-nonexistent-xxxx", 10)
	require.NoError(t, err)
	assert.Empty(t, logs)
}

func TestSaveSchedulerTask_UpdateExisting(t *testing.T) {
	taskID := "test-task-update"
	t.Cleanup(func() {
		GetDB().Where("task_id = ?", taskID).Delete(&models.SchedulerTask{})
	})

	SaveSchedulerTask(taskID, "初始任务", "0 0 * * * *", 300, 3, true, "初始描述")
	SaveSchedulerTask(taskID, "更新任务", "0 */10 * * * *", 600, 5, false, "更新描述")

	tasks, err := QuerySchedulerTasks()
	require.NoError(t, err)

	for _, task := range tasks {
		if task.TaskID == taskID {
			assert.Equal(t, "更新任务", task.Name)
			assert.Equal(t, 600, task.TimeoutSeconds)
			assert.Equal(t, 5, task.MaxRetries)
			return
		}
	}
	t.Error("updated task not found")
}

// ====== Inventory Alert Tests ======

func TestGetInventoryAlertCount_NoTable(t *testing.T) {
	user := createTestUser(t, "ia-1")
	shop := createTestShop(t, user.UserID, "inv-alert")

	count, err := GetInventoryAlertCount(user.UserID, shop.ShopID)
	require.NoError(t, err)
	assert.Equal(t, 0, count)
}

func TestGetInventoryAlerts_NoTable(t *testing.T) {
	user := createTestUser(t, "ia-2")
	shop := createTestShop(t, user.UserID, "inv-alerts")

	alerts := GetInventoryAlerts(user.UserID, shop.ShopID)
	assert.Nil(t, alerts)
}

func TestGetRiskWarningCount_NoTable(t *testing.T) {
	user := createTestUser(t, "rw-1")
	shop := createTestShop(t, user.UserID, "risk-warn")

	count, err := GetRiskWarningCount(user.UserID, shop.ShopID)
	require.NoError(t, err)
	assert.Equal(t, 0, count)
}

func TestGetUserShops_NoShops(t *testing.T) {
	user := createTestUser(t, "no-shops")

	shops, err := GetUserShops(user.UserID)
	require.NoError(t, err)
	assert.Empty(t, shops)
}

func TestGetShopProfit_MultipleStatsAggregation(t *testing.T) {
	user := createTestUser(t, "profit-multi")
	shop := createTestShop(t, user.UserID, "profit-agg")

	for _, day := range []string{"2026-05-01", "2026-05-02", "2026-05-03"} {
		stat := models.ProfitStat{
			UserID:      user.UserID,
			ShopID:      shop.ShopID,
			StatDate:    day,
			TotalProfit: 1000.00,
			TotalRevenue: 5000.00,
		}
		GetDB().Create(&stat)
		t.Cleanup(func() { GetDB().Unscoped().Delete(&models.ProfitStat{}, stat.StatID) })
	}

	profit, err := GetShopProfit(user.UserID, shop.ShopID)
	require.NoError(t, err)
	assert.Equal(t, 3000.00, profit)

	revenue, err := GetShopRevenue(user.UserID, shop.ShopID)
	require.NoError(t, err)
	assert.Equal(t, 15000.00, revenue)
}

func TestListUsers_WithSearch(t *testing.T) {
	user := createTestUser(t, "list-search")
	users, total, err := ListUsers("list-search", 1, 20)
	require.NoError(t, err)
	assert.GreaterOrEqual(t, total, int64(1))
	found := false
	for _, u := range users {
		if u.Email == user.Email {
			found = true
			assert.Equal(t, user.PlanType, u.Plan)
			assert.True(t, u.IsActive)
			break
		}
	}
	assert.True(t, found, "created user should be found by email search")
}

func TestListUsers_Pagination(t *testing.T) {
	for i := 0; i < 3; i++ {
		createTestUser(t, fmt.Sprintf("list-pg-%d", i))
	}

	page1, total, err := ListUsers("list-pg-", 1, 2)
	require.NoError(t, err)
	assert.GreaterOrEqual(t, total, int64(3))
	assert.Len(t, page1, 2)

	page2, total2, err := ListUsers("list-pg-", 2, 2)
	require.NoError(t, err)
	assert.Equal(t, total, total2)
	assert.Len(t, page2, 1)
}

func TestListUsers_EmptySearch(t *testing.T) {
	users, total, err := ListUsers("", 1, 20)
	require.NoError(t, err)
	assert.Greater(t, total, int64(0))
	assert.NotEmpty(t, users)
}

func TestListUsers_NoMatch(t *testing.T) {
	users, total, err := ListUsers("zzzz-nonexistent-email-xxxx", 1, 20)
	require.NoError(t, err)
	assert.Equal(t, int64(0), total)
	assert.Empty(t, users)
}
