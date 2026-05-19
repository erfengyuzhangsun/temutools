package repository

import (
	"log/slog"
	"time"

	"github.com/erfengyuzhangsun/temutools/internal/models"
)

type SettlementRow struct {
	SettlementID     int     `json:"settlement_id"`
	ShopID           int     `json:"shop_id"`
	OrderSn          string  `json:"order_sn"`
	TotalAmount      float64 `json:"total_amount"`
	PlatformFee      float64 `json:"platform_fee"`
	SettlementAmount float64 `json:"settlement_amount"`
	CostPrice        float64 `json:"cost_price"`
	Profit           float64 `json:"profit"`
	StatDate         string  `json:"stat_date"`
	CreatedAt        time.Time `json:"created_at"`
}

type ProfitStatRow struct {
	StatID       int     `json:"stat_id"`
	ShopID       int     `json:"shop_id"`
	StatDate     string  `json:"stat_date"`
	TotalOrders  int     `json:"total_orders"`
	TotalRevenue float64 `json:"total_revenue"`
	TotalCost    float64 `json:"total_cost"`
	TotalProfit  float64 `json:"total_profit"`
	NetProfitRate float64 `json:"net_profit_rate"`
}

func SaveSettlementRecord(record *models.SettlementRecord) error {
	db := GetDB()
	if db == nil {
		return nil
	}

	var existing models.SettlementRecord
	result := db.Where("shop_id = ? AND order_sn = ?", record.ShopID, record.OrderSn).First(&existing)
	if result.Error == nil {
		record.SettlementID = existing.SettlementID
		return db.Model(&existing).Updates(map[string]interface{}{
			"total_amount":      record.TotalAmount,
			"platform_fee":      record.PlatformFee,
			"settlement_amount": record.SettlementAmount,
			"cost_price":        record.CostPrice,
			"profit":            record.Profit,
			"stat_date":         record.StatDate,
		}).Error
	}

	return db.Create(record).Error
}

func GetSettledOrderIDs(shopID int) (map[string]struct{}, error) {
	db := GetDB()
	if db == nil {
		return make(map[string]struct{}), nil
	}

	if !db.Migrator().HasTable("temu_settlement_records") {
		return make(map[string]struct{}), nil
	}

	var orderSns []string
	err := db.Model(&models.SettlementRecord{}).
		Where("shop_id = ?", shopID).
		Pluck("order_sn", &orderSns).Error
	if err != nil {
		slog.Warn("failed to query settled order IDs", "error", err)
		return make(map[string]struct{}), nil
	}

	result := make(map[string]struct{}, len(orderSns))
	for _, sn := range orderSns {
		result[sn] = struct{}{}
	}
	return result, nil
}

func QuerySettlementRecords(userID, shopID int, limit int) ([]SettlementRow, error) {
	db := GetDB()
	if db == nil {
		return nil, nil
	}

	if !db.Migrator().HasTable("temu_settlement_records") {
		return nil, nil
	}

	var records []models.SettlementRecord
	query := db.Where("user_id = ?", userID)
	if shopID > 0 {
		query = query.Where("shop_id = ?", shopID)
	}
	result := query.Order("created_at DESC").Limit(limit).Find(&records)
	if result.Error != nil {
		return nil, result.Error
	}

	rows := make([]SettlementRow, len(records))
	for i, r := range records {
		rows[i] = SettlementRow{
			SettlementID:     r.SettlementID,
			ShopID:           r.ShopID,
			OrderSn:          r.OrderSn,
			TotalAmount:      r.TotalAmount,
			PlatformFee:      r.PlatformFee,
			SettlementAmount: r.SettlementAmount,
			CostPrice:        r.CostPrice,
			Profit:           r.Profit,
			StatDate:         r.StatDate,
			CreatedAt:        r.CreatedAt,
		}
	}
	return rows, nil
}

func SaveProfitStat(stat *models.ProfitStat) error {
	db := GetDB()
	if db == nil {
		return nil
	}

	var existing models.ProfitStat
	result := db.Where("user_id = ? AND shop_id = ? AND stat_date = ?", stat.UserID, stat.ShopID, stat.StatDate).First(&existing)
	if result.Error == nil {
		stat.StatID = existing.StatID
		return db.Model(&existing).Updates(map[string]interface{}{
			"total_orders":         stat.TotalOrders,
			"total_revenue":        stat.TotalRevenue,
			"total_cost":           stat.TotalCost,
			"total_commission":     stat.TotalCommission,
			"total_payment_fee":    stat.TotalPaymentFee,
			"total_profit":         stat.TotalProfit,
			"net_profit_rate":      stat.NetProfitRate,
		}).Error
	}

	return db.Create(stat).Error
}

func QueryProfitStats(userID, shopID int, startDate, endDate string) ([]ProfitStatRow, error) {
	db := GetDB()
	if db == nil {
		return nil, nil
	}

	if !db.Migrator().HasTable("temu_profit_stats") {
		return nil, nil
	}

	var stats []models.ProfitStat
	query := db.Where("user_id = ?", userID)
	if shopID > 0 {
		query = query.Where("shop_id = ?", shopID)
	}
	if startDate != "" {
		query = query.Where("stat_date >= ?", startDate)
	}
	if endDate != "" {
		query = query.Where("stat_date <= ?", endDate)
	}
	result := query.Order("stat_date DESC").Find(&stats)
	if result.Error != nil {
		return nil, result.Error
	}

	rows := make([]ProfitStatRow, len(stats))
	for i, s := range stats {
		rows[i] = ProfitStatRow{
			StatID:       s.StatID,
			ShopID:       s.ShopID,
			StatDate:     s.StatDate,
			TotalOrders:  s.TotalOrders,
			TotalRevenue: s.TotalRevenue,
			TotalCost:    s.TotalCost,
			TotalProfit:  s.TotalProfit,
			NetProfitRate: s.NetProfitRate,
		}
	}
	return rows, nil
}
