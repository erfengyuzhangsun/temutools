package repository

import (
	"fmt"
	"log/slog"

	"github.com/erfengyuzhangsun/temutools/internal/models"
)

type ShopBrief struct {
	ShopID   int
	ShopName string
}

type InventoryAlertItem struct {
	AlertType string
	Message   string
}

func GetUserShops(userID int) ([]models.Shop, error) {
	db := GetDB()
	if db == nil {
		return nil, nil
	}

	var shops []models.Shop
	result := db.Where("user_id = ?", userID).Find(&shops)
	return shops, result.Error
}

func GetShopProfit(userID, shopID int) (float64, error) {
	db := GetDB()
	if db == nil {
		return 0, nil
	}

	var result struct {
		Total float64
	}
	err := db.Model(&models.ProfitStat{}).
		Select("COALESCE(SUM(total_profit), 0) as total").
		Where("user_id = ? AND shop_id = ?", userID, shopID).
		Scan(&result).Error
	if err != nil {
		return 0, err
	}
	return result.Total, nil
}

func GetShopRevenue(userID, shopID int) (float64, error) {
	db := GetDB()
	if db == nil {
		return 0, nil
	}

	var result struct {
		Total float64
	}
	err := db.Model(&models.ProfitStat{}).
		Select("COALESCE(SUM(total_revenue), 0) as total").
		Where("user_id = ? AND shop_id = ?", userID, shopID).
		Scan(&result).Error
	if err != nil {
		return 0, err
	}
	return result.Total, nil
}

func GetPricingPendingCount(userID, shopID int) (int, error) {
	db := GetDB()
	if db == nil {
		return 0, nil
	}

	var count int64
	err := db.Model(&models.PricingLog{}).
		Where("user_id = ? AND shop_id = ? AND action = ?", userID, shopID, "skip").
		Count(&count).Error
	if err != nil {
		return 0, err
	}
	return int(count), nil
}

func GetInventoryAlertCount(userID, shopID int) (int, error) {
	db := GetDB()
	if db == nil {
		return 0, nil
	}

	if !db.Migrator().HasTable("temu_inventory_alerts") {
		return 0, nil
	}

	var count int64
	err := db.Table("temu_inventory_alerts").
		Where("user_id = ? AND shop_id = ? AND is_read = ?", userID, shopID, 0).
		Count(&count).Error
	if err != nil {
		return 0, err
	}
	return int(count), nil
}

func GetRiskWarningCount(userID, shopID int) (int, error) {
	db := GetDB()
	if db == nil {
		return 0, nil
	}

	if !db.Migrator().HasTable("temu_risk_metrics") {
		return 0, nil
	}

	var count int64
	err := db.Table("temu_risk_metrics").
		Where("user_id = ? AND shop_id = ? AND comprehensive_score < ?", userID, shopID, 80).
		Count(&count).Error
	if err != nil {
		slog.Warn("failed to query risk warning count", "error", err)
		return 0, nil
	}
	return int(count), nil
}

func GetPricingExpiring(userID, shopID int) []string {
	return nil
}

func GetInventoryAlerts(userID, shopID int) []InventoryAlertItem {
	db := GetDB()
	if db == nil {
		return nil
	}

	if !db.Migrator().HasTable("temu_inventory_alerts") {
		return nil
	}

	type alertRow struct {
		AlertType string `gorm:"column:alert_type"`
		Message   string `gorm:"column:message"`
	}

	var rows []alertRow
	err := db.Table("temu_inventory_alerts").
		Select("alert_type, message").
		Where("user_id = ? AND shop_id = ? AND is_read = ?", userID, shopID, 0).
		Find(&rows).Error
	if err != nil {
		slog.Warn("failed to query inventory alerts", "error", err)
		return nil
	}

	alerts := make([]InventoryAlertItem, len(rows))
	for i, r := range rows {
		alerts[i] = InventoryAlertItem{
			AlertType: r.AlertType,
			Message:   r.Message,
		}
	}
	return alerts
}

func GetShopSKUs(userID, shopID int) ([]models.SkuProfit, error) {
	db := GetDB()
	if db == nil {
		return nil, nil
	}

	var skus []models.SkuProfit
	result := db.Where("user_id = ? AND shop_id = ?", userID, shopID).Find(&skus)
	return skus, result.Error
}

func GetShopSKUsByCodes(userID, shopID int, skuCodes []string) ([]models.SkuProfit, error) {
	db := GetDB()
	if db == nil {
		return nil, nil
	}

	var skus []models.SkuProfit
	result := db.Where("user_id = ? AND shop_id = ? AND sku_code IN ?", userID, shopID, skuCodes).Find(&skus)
	return skus, result.Error
}

func CreateShop(userID int, shopName string) (int, error) {
	db := GetDB()
	if db == nil {
		return 0, nil
	}

	shop := models.Shop{
		UserID:   userID,
		ShopName: shopName,
	}
	if err := db.Create(&shop).Error; err != nil {
		return 0, err
	}
	return shop.ShopID, nil
}

func DeleteShop(shopID int) error {
	db := GetDB()
	if db == nil {
		return nil
	}
	db.Delete(&models.ShopCredential{}, "shop_id = ?", shopID)
	return db.Delete(&models.Shop{}, shopID).Error
}

func SaveShopCredentials(shopID int, accessToken string) error {
	db := GetDB()
	if db == nil {
		return fmt.Errorf("database not initialized")
	}

	var cred models.ShopCredential
	result := db.Where("shop_id = ?", shopID).First(&cred)
	if result.Error == nil {
		return db.Model(&cred).Update("encrypted_access_token", accessToken).Error
	}

	cred = models.ShopCredential{
		ShopID:               shopID,
		EncryptedAccessToken: accessToken,
	}
	return db.Create(&cred).Error
}

func GetShopAccessToken(shopID int) (string, error) {
	db := GetDB()
	if db == nil {
		return "", fmt.Errorf("database not initialized")
	}

	var cred models.ShopCredential
	result := db.Where("shop_id = ?", shopID).First(&cred)
	if result.Error != nil {
		return "", result.Error
	}
	return cred.EncryptedAccessToken, nil
}

func GetFactoryProducts(userID int) ([]models.FactoryProduct, error) {
	db := GetDB()
	if db == nil {
		return nil, nil
	}
	if !db.Migrator().HasTable("temu_factory_products") {
		return nil, nil
	}
	var products []models.FactoryProduct
	result := db.Where("user_id = ?", userID).Order("updated_at DESC").Find(&products)
	return products, result.Error
}

func CreateFactoryProduct(userID int, p models.FactoryProduct) (*models.FactoryProduct, error) {
	db := GetDB()
	if db == nil {
		return nil, nil
	}
	p.UserID = userID
	if err := db.Create(&p).Error; err != nil {
		return nil, err
	}
	return &p, nil
}

func GetSuppliers(userID int) ([]models.Supplier, error) {
	db := GetDB()
	if db == nil {
		return nil, nil
	}
	if !db.Migrator().HasTable("temu_suppliers") {
		return nil, nil
	}
	var suppliers []models.Supplier
	result := db.Where("user_id = ?", userID).Order("created_at DESC").Find(&suppliers)
	return suppliers, result.Error
}

func CreateSupplier(supplier models.Supplier) (*models.Supplier, error) {
	db := GetDB()
	if db == nil {
		return nil, nil
	}
	if err := db.Create(&supplier).Error; err != nil {
		return nil, err
	}
	return &supplier, nil
}
