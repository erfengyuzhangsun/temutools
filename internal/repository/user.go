package repository

import (
	"fmt"
	"log/slog"
	"time"

	"golang.org/x/crypto/bcrypt"
	"gorm.io/gorm"

	"github.com/erfengyuzhangsun/temutools/internal/models"
)

func FindByEmail(email string) (*models.User, error) {
	db := GetDB()
	if db == nil {
		return nil, nil
	}

	var user models.User
	result := db.Where("email = ? AND is_active = ?", email, true).First(&user)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, nil
		}
		return nil, result.Error
	}

	return &user, nil
}

func CreateUser(email, password, planType string, policyVersion string, termsAgreed, privacyAgreed bool) (*models.User, error) {
	db := GetDB()
	if db == nil {
		return nil, fmt.Errorf("database not initialized")
	}

	existing, err := FindByEmail(email)
	if err != nil {
		return nil, fmt.Errorf("check existing user: %w", err)
	}
	if existing != nil {
		return nil, fmt.Errorf("email already registered")
	}

	hashedBytes, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return nil, fmt.Errorf("hash password: %w", err)
	}

	now := time.Now()
	user := models.User{
		Email:         email,
		PasswordHash:  string(hashedBytes),
		PlanType:      planType,
		IsActive:      true,
		StartDate:     &now,
		ExpireDate:    nil,
		PolicyVersion: policyVersion,
	}
	if termsAgreed {
		user.TermsAgreedAt = &now
	}
	if privacyAgreed {
		user.PrivacyAgreedAt = &now
	}

	if planType != "lifetime" {
		expire := now.AddDate(0, 0, 30)
		user.ExpireDate = &expire
	}

	if err := db.Create(&user).Error; err != nil {
		return nil, fmt.Errorf("create user: %w", err)
	}

	return &user, nil
}

func CheckPassword(password, hash string) bool {
	if hash == "" {
		return false
	}
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
	return err == nil
}

func IsUserExpired(user *models.User) bool {
	if user.ExpireDate == nil {
		return false
	}
	return time.Now().After(*user.ExpireDate)
}

func UpdateUserPlan(email, planType string) error {
	db := GetDB()
	if db == nil {
		return fmt.Errorf("database not initialized")
	}
	result := db.Model(&models.User{}).Where("email = ?", email).Update("plan_type", planType)
	if result.Error != nil {
		return fmt.Errorf("update plan: %w", result.Error)
	}
	if result.RowsAffected == 0 {
		return fmt.Errorf("user not found")
	}
	return nil
}

func UpdateUserPassword(email, password string) error {
	db := GetDB()
	if db == nil {
		return fmt.Errorf("database not initialized")
	}
	hashedBytes, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return fmt.Errorf("hash password: %w", err)
	}
	result := db.Model(&models.User{}).Where("email = ?", email).Update("password_hash", string(hashedBytes))
	if result.Error != nil {
		return fmt.Errorf("update password: %w", result.Error)
	}
	if result.RowsAffected == 0 {
		return fmt.Errorf("user not found")
	}
	slog.Info("admin password synced from env", "email", email)
	return nil
}

type UserListItem struct {
	UserID         int        `json:"user_id"`
	Email          string     `json:"email"`
	WechatNickname string     `json:"nickname"`
	PlanType       string     `json:"plan"`
	StartDate      *time.Time `json:"start_date"`
	ExpireDate     *time.Time `json:"expire_date"`
	IsActive       bool       `json:"is_active"`
	CreatedAt      time.Time  `json:"created_at"`
}

func ListUsers(search string, page, pageSize int) ([]UserListItem, int64, error) {
	db := GetDB()
	if db == nil {
		return nil, 0, fmt.Errorf("database not initialized")
	}

	query := db.Model(&models.User{})
	if search != "" {
		query = query.Where("email LIKE ?", "%"+search+"%")
	}

	var total int64
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, fmt.Errorf("count users: %w", err)
	}

	var users []UserListItem
	result := query.Select("user_id, email, wechat_nickname, plan_type, start_date, expire_date, is_active, created_at").
		Order("user_id DESC").
		Offset((page - 1) * pageSize).
		Limit(pageSize).
		Find(&users)
	if result.Error != nil {
		return nil, 0, fmt.Errorf("list users: %w", result.Error)
	}

	return users, total, nil
}

func SeedAdmin(email, password string) {
	if email == "" || password == "" {
		slog.Warn("admin seed skipped: ADMIN_EMAIL or ADMIN_PASSWORD not set")
		return
	}
	existing, _ := FindByEmail(email)
	if existing != nil {
		_ = UpdateUserPassword(email, password)
		if existing.PlanType != "lifetime" {
			_ = UpdateUserPlan(email, "lifetime")
		}
		return
	}
	user, err := CreateUser(email, password, "lifetime", "", true, true)
	if err != nil {
		slog.Error("failed to seed admin account", "error", err)
		return
	}
	slog.Info("admin account seeded successfully", "user_id", user.UserID, "email", email)
}

func UpdateUserExpiry(email string, extraDays int) error {
	db := GetDB()
	if db == nil {
		return fmt.Errorf("database not initialized")
	}
	result := db.Model(&models.User{}).Where("email = ?", email).
		Update("expire_date", gorm.Expr("DATE_ADD(expire_date, INTERVAL ? DAY)", extraDays))
	if result.Error != nil {
		return fmt.Errorf("update expiry: %w", result.Error)
	}
	if result.RowsAffected == 0 {
		return fmt.Errorf("user not found")
	}
	return nil
}

func ToggleUserActive(email string, active bool) error {
	db := GetDB()
	if db == nil {
		return fmt.Errorf("database not initialized")
	}
	result := db.Model(&models.User{}).Where("email = ?", email).
		Update("is_active", active)
	if result.Error != nil {
		return fmt.Errorf("toggle active: %w", result.Error)
	}
	if result.RowsAffected == 0 {
		return fmt.Errorf("user not found")
	}
	return nil
}

func FindByUserID(userID int) (*models.User, error) {
	db := GetDB()
	if db == nil {
		return nil, fmt.Errorf("database not initialized")
	}

	var user models.User
	result := db.First(&user, userID)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, nil
		}
		return nil, result.Error
	}
	return &user, nil
}

func DeleteUser(userID int) error {
	db := GetDB()
	if db == nil {
		return fmt.Errorf("database not initialized")
	}

	user, err := FindByUserID(userID)
	if err != nil {
		return fmt.Errorf("find user: %w", err)
	}
	if user == nil {
		return fmt.Errorf("user not found")
	}

	shops, err := GetUserShops(userID)
	if err != nil {
		return fmt.Errorf("get user shops: %w", err)
	}

	for _, shop := range shops {
		db.Delete(&models.ShopCredential{}, "shop_id = ?", shop.ShopID)
		db.Delete(&models.PricingLog{}, "shop_id = ?", shop.ShopID)
		db.Delete(&models.SyncRecord{}, "shop_id = ?", shop.ShopID)
		db.Delete(&models.SkuProfit{}, "shop_id = ?", shop.ShopID)
		db.Delete(&models.ProfitStat{}, "shop_id = ?", shop.ShopID)
		db.Delete(&models.Shop{}, shop.ShopID)
	}

	result := db.Delete(&models.User{}, userID)
	if result.Error != nil {
		return fmt.Errorf("delete user: %w", result.Error)
	}
	if result.RowsAffected == 0 {
		return fmt.Errorf("user not found")
	}

	slog.Info("user deleted", "user_id", userID, "email", user.Email, "shop_count", len(shops))
	return nil
}
