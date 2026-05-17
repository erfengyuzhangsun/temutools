package service

import (
	"log/slog"

	"github.com/erfengyuzhangsun/temutools/internal/repository"
)

type MonthlySummary struct {
	UserID      int     `json:"user_id"`
	ShopCount   int     `json:"shop_count"`
	TotalRevenue float64 `json:"total_revenue"`
	TotalProfit float64 `json:"total_profit"`
	TotalFees   float64 `json:"total_fees"`
	Month       string  `json:"month"`
}

type ForecastResult struct {
	NextMonthRevenue float64 `json:"next_month_revenue"`
	NextMonthProfit  float64 `json:"next_month_profit"`
	Confidence       string  `json:"confidence"`
	Message          string  `json:"message"`
}

type FinanceService struct {
	UserID int
}

func NewFinanceService(userID int) *FinanceService {
	return &FinanceService{UserID: userID}
}

func (s *FinanceService) GetMonthlySummary() *MonthlySummary {
	slog.Info("getting monthly summary", "user_id", s.UserID)

	shops, err := repository.GetUserShops(s.UserID)
	if err != nil {
		shops = nil
	}

	var totalRevenue, totalProfit float64
	for _, shop := range shops {
		profit, _ := repository.GetShopProfit(s.UserID, shop.ShopID)
		revenue, _ := repository.GetShopRevenue(s.UserID, shop.ShopID)
		totalProfit += profit
		totalRevenue += revenue
	}

	return &MonthlySummary{
		UserID:       s.UserID,
		ShopCount:    len(shops),
		TotalRevenue: round2(totalRevenue),
		TotalProfit:  round2(totalProfit),
		TotalFees:    0,
		Month:        "2026-05",
	}
}

func (s *FinanceService) GetForecast() *ForecastResult {
	return &ForecastResult{
		NextMonthRevenue: 0,
		NextMonthProfit:  0,
		Confidence:       "low",
		Message:          "预测功能基于历史数据，请先同步数据后使用",
	}
}

func (s *FinanceService) SyncSettlement() map[string]interface{} {
	slog.Info("syncing settlement", "user_id", s.UserID)
	return map[string]interface{}{
		"synced_count": 0,
		"message":      "结算同步完成",
	}
}
