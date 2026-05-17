package repository

import (
	"time"

	"github.com/erfengyuzhangsun/temutools/internal/models"
)

type PricingLogRow struct {
	LogID       int
	NoticeID    string
	Sku         string
	Action      string
	SupplyPrice float64
	CostPrice   float64
	GrossMargin float64
	Reason      string
	IsActivity  bool
	HandledAt   time.Time
}

func GetSkuCostPrice(userID, shopID int, sku string) (float64, error) {
	db := GetDB()
	if db == nil {
		return 0, nil
	}

	var result struct {
		CostPrice float64
	}
	err := db.Model(&models.SkuProfit{}).
		Select("cost_price").
		Where("user_id = ? AND shop_id = ? AND sku_code = ?", userID, shopID, sku).
		Scan(&result).Error
	if err != nil {
		return 0, err
	}
	return result.CostPrice, nil
}

func SavePricingLog(userID, shopID int, noticeID, sku, action string, supplyPrice, costPrice, grossMargin float64, reason string, isActivity bool) {
	db := GetDB()
	if db == nil {
		return
	}

	log := models.PricingLog{
		UserID:      userID,
		ShopID:      shopID,
		NoticeID:    noticeID,
		Sku:         sku,
		Action:      action,
		SupplyPrice: supplyPrice,
		CostPrice:   costPrice,
		GrossMargin: grossMargin,
		Reason:      reason,
		IsActivity:  isActivity,
		HandledAt:   time.Now(),
	}

	if err := db.Create(&log).Error; err != nil {
		return
	}
}

func QueryPricingLogs(userID, shopID int, limit int) ([]PricingLogRow, error) {
	db := GetDB()
	if db == nil {
		return nil, nil
	}

	var logs []models.PricingLog
	result := db.Where("user_id = ? AND shop_id = ?", userID, shopID).
		Order("handled_at DESC").
		Limit(limit).
		Find(&logs)
	if result.Error != nil {
		return nil, result.Error
	}

	rows := make([]PricingLogRow, len(logs))
	for i, l := range logs {
		rows[i] = PricingLogRow{
			LogID:       l.LogID,
			NoticeID:    l.NoticeID,
			Sku:         l.Sku,
			Action:      l.Action,
			SupplyPrice: l.SupplyPrice,
			CostPrice:   l.CostPrice,
			GrossMargin: l.GrossMargin,
			Reason:      l.Reason,
			IsActivity:  l.IsActivity,
			HandledAt:   l.HandledAt,
		}
	}
	return rows, nil
}
