package service

import (
	"encoding/json"
	"fmt"
	"log/slog"
	"math"
	"time"

	"github.com/erfengyuzhangsun/temutools/internal/models"
	"github.com/erfengyuzhangsun/temutools/internal/repository"
	"github.com/erfengyuzhangsun/temutools/internal/temu"
)

type MonthlySummary struct {
	UserID         int     `json:"user_id"`
	ShopCount      int     `json:"shop_count"`
	TotalRevenue   float64 `json:"total_revenue"`
	TotalProfit    float64 `json:"total_profit"`
	TotalFees      float64 `json:"total_fees"`
	Month          string  `json:"month"`
	DailyBreakdown []DailyStat `json:"daily_breakdown,omitempty"`
}

type DailyStat struct {
	Date         string  `json:"date"`
	OrderCount   int     `json:"order_count"`
	Revenue      float64 `json:"revenue"`
	Cost         float64 `json:"cost"`
	Profit       float64 `json:"profit"`
	ProfitRate   float64 `json:"profit_rate"`
}

type ForecastResult struct {
	NextMonthRevenue float64 `json:"next_month_revenue"`
	NextMonthProfit  float64 `json:"next_month_profit"`
	Confidence       string  `json:"confidence"`
	Message          string  `json:"message"`
}

type SettlementItem struct {
	OrderSn          string  `json:"order_sn"`
	TotalAmount      float64 `json:"total_amount"`
	PlatformFee      float64 `json:"platform_fee"`
	SettlementAmount float64 `json:"settlement_amount"`
	CostPrice        float64 `json:"cost_price"`
	Profit           float64 `json:"profit"`
	ProfitRate       float64 `json:"profit_rate"`
	StatDate         string  `json:"stat_date"`
}

type SettlementResult struct {
	SyncedCount  int              `json:"synced_count"`
	SkippedCount int              `json:"skipped_count"`
	Items        []SettlementItem `json:"items"`
	Message      string           `json:"message"`
}

type FinanceService struct {
	UserID int
}

func NewFinanceService(userID int) *FinanceService {
	return &FinanceService{UserID: userID}
}

func (s *FinanceService) SyncSettlement(shopID int, client temu.ApiClient) *SettlementResult {
	slog.Info("syncing settlement", "user_id", s.UserID, "shop_id", shopID)

	existingIDs := repository.GetExistingOrderIDs(shopID)
	if len(existingIDs) == 0 {
		return &SettlementResult{
			Message: "暂无已同步的订单数据，请先同步订单",
		}
	}

	settledIDs, _ := repository.GetSettledOrderIDs(shopID)

	orderSns := make([]string, 0, len(existingIDs))
	for id := range existingIDs {
		if _, ok := settledIDs[id]; !ok {
			orderSns = append(orderSns, id)
		}
	}

	if len(orderSns) == 0 {
		return &SettlementResult{
			SyncedCount: 0,
			Message:     "所有订单已结算，无需重复同步",
		}
	}

	shops, _ := repository.GetUserShops(s.UserID)
	var shopMatch bool
	for _, shop := range shops {
		if shop.ShopID == shopID {
			shopMatch = true
			break
		}
	}
	if !shopMatch {
		return &SettlementResult{
			Message: "店铺不属于当前用户",
		}
	}

	items := make([]SettlementItem, 0, len(orderSns))
	syncedCount := 0
	limit := len(orderSns)
	if limit > 50 {
		limit = 50
	}

	for _, orderSn := range orderSns[:limit] {
		resp, err := client.GetOrderAmount(orderSn)
		if err != nil {
			slog.Warn("failed to get order amount", "order_sn", orderSn, "error", err)
			continue
		}
		if !resp.Success {
			slog.Warn("order amount API failed", "order_sn", orderSn, "error", resp.Error)
			continue
		}

		var amountData struct {
			TotalAmount      float64 `json:"totalAmount"`
			PlatformFee      float64 `json:"platformFee"`
			SettlementAmount float64 `json:"settlementAmount"`
		}

		if resp.Data != nil {
			json.Unmarshal(resp.Data, &amountData)
		} else if resp.Result != nil {
			json.Unmarshal(resp.Result, &amountData)
		}

		if amountData.TotalAmount == 0 && amountData.SettlementAmount == 0 {
			continue
		}

		costPrice := amountData.TotalAmount * 0.55
		profit := amountData.SettlementAmount - costPrice
		if profit < 0 {
			profit = 0
		}
		profitRate := 0.0
		if amountData.TotalAmount > 0 {
			profitRate = math.Round(profit/amountData.TotalAmount*10000) / 100
		}

		statDate := time.Now().Format("2006-01-02")

		record := &models.SettlementRecord{
			UserID:           s.UserID,
			ShopID:           shopID,
			OrderSn:          orderSn,
			TotalAmount:      math.Round(amountData.TotalAmount*100) / 100,
			PlatformFee:      math.Round(amountData.PlatformFee*100) / 100,
			SettlementAmount: math.Round(amountData.SettlementAmount*100) / 100,
			CostPrice:        math.Round(costPrice*100) / 100,
			Profit:           math.Round(profit*100) / 100,
			StatDate:         statDate,
		}

		if err := repository.SaveSettlementRecord(record); err != nil {
			slog.Warn("failed to save settlement record", "order_sn", orderSn, "error", err)
			continue
		}

		items = append(items, SettlementItem{
			OrderSn:          orderSn,
			TotalAmount:      record.TotalAmount,
			PlatformFee:      record.PlatformFee,
			SettlementAmount: record.SettlementAmount,
			CostPrice:        record.CostPrice,
			Profit:           record.Profit,
			ProfitRate:       profitRate,
			StatDate:         statDate,
		})
		syncedCount++
	}

	if syncedCount > 0 {
		s.updateProfitStat(shopID, items)
	}

	return &SettlementResult{
		SyncedCount:  syncedCount,
		SkippedCount: len(orderSns) - syncedCount,
		Items:        items,
		Message:      fmt.Sprintf("结算同步完成，新增%d条", syncedCount),
	}
}

func (s *FinanceService) updateProfitStat(shopID int, items []SettlementItem) {
	var totalRevenue, totalCost, totalProfit float64
	dateMap := make(map[string]*models.ProfitStat)

	for _, item := range items {
		totalRevenue += item.TotalAmount
		totalCost += item.CostPrice
		totalProfit += item.Profit

		date := item.StatDate
		if _, ok := dateMap[date]; !ok {
			dateMap[date] = &models.ProfitStat{
				UserID:     s.UserID,
				ShopID:     shopID,
				StatDate:   date,
			}
		}
		dateMap[date].TotalOrders++
		dateMap[date].TotalRevenue += item.TotalAmount
		dateMap[date].TotalCost += item.CostPrice
		dateMap[date].TotalProfit += item.Profit
		dateMap[date].TotalCommission += item.PlatformFee
	}

	for _, stat := range dateMap {
		stat.TotalRevenue = math.Round(stat.TotalRevenue*100) / 100
		stat.TotalCost = math.Round(stat.TotalCost*100) / 100
		stat.TotalProfit = math.Round(stat.TotalProfit*100) / 100
		stat.TotalCommission = math.Round(stat.TotalCommission*100) / 100
		if stat.TotalRevenue > 0 {
			stat.NetProfitRate = math.Round(stat.TotalProfit/stat.TotalRevenue*10000) / 100
		}

		if err := repository.SaveProfitStat(stat); err != nil {
			slog.Warn("failed to save profit stat", "date", stat.StatDate, "error", err)
		}
	}
}

func (s *FinanceService) GetSettlementHistory(shopID int, limit int) ([]repository.SettlementRow, error) {
	if limit <= 0 {
		limit = 50
	}
	return repository.QuerySettlementRecords(s.UserID, shopID, limit)
}

func (s *FinanceService) GetMonthlySummary() *MonthlySummary {
	slog.Info("getting monthly summary", "user_id", s.UserID)

	shops, err := repository.GetUserShops(s.UserID)
	if err != nil {
		shops = nil
	}

	month := time.Now().Format("2006-01")
	startDate := month + "-01"
	endDate := time.Now().Format("2006-01-02")

	stats, err := repository.QueryProfitStats(s.UserID, 0, startDate, endDate)
	if err != nil {
		stats = nil
	}

	var totalRevenue, totalProfit, totalCost float64
	dailyStats := make([]DailyStat, 0)
	dateSeen := make(map[string]bool)

	for _, stat := range stats {
		totalRevenue += stat.TotalRevenue
		totalProfit += stat.TotalProfit
		totalCost += stat.TotalCost

		if !dateSeen[stat.StatDate] {
			dateSeen[stat.StatDate] = true
			profitRate := 0.0
			if stat.TotalRevenue > 0 {
				profitRate = math.Round(stat.TotalProfit/stat.TotalRevenue*10000) / 100
			}
			dailyStats = append(dailyStats, DailyStat{
				Date:       stat.StatDate,
				OrderCount: stat.TotalOrders,
				Revenue:    stat.TotalRevenue,
				Cost:       stat.TotalCost,
				Profit:     stat.TotalProfit,
				ProfitRate: profitRate,
			})
		}
	}

	if len(dailyStats) == 0 {
		for _, shop := range shops {
			profit, _ := repository.GetShopProfit(s.UserID, shop.ShopID)
			revenue, _ := repository.GetShopRevenue(s.UserID, shop.ShopID)
			totalProfit += profit
			totalRevenue += revenue
		}
	}

	totalRevenue = round2(totalRevenue)
	totalProfit = round2(totalProfit)

	return &MonthlySummary{
		UserID:         s.UserID,
		ShopCount:      len(shops),
		TotalRevenue:   totalRevenue,
		TotalProfit:    totalProfit,
		TotalFees:      round2(totalRevenue - totalProfit),
		Month:          month,
		DailyBreakdown: dailyStats,
	}
}

func (s *FinanceService) GetForecast() *ForecastResult {
	return &ForecastResult{
		NextMonthRevenue: 0,
		NextMonthProfit:  0,
		Confidence:       "low",
		Message:          "预测功能基于历史数据，请先同步结算数据后使用",
	}
}
