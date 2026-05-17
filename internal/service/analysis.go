package service

import (
	"log/slog"
	"time"

	"github.com/erfengyuzhangsun/temutools/internal/repository"
)

type AnalysisReport struct {
	TotalShops  int              `json:"total_shops"`
	Period      string           `json:"period"`
	Summary     AnalysisSummary  `json:"summary"`
	ShopReports []ShopReport     `json:"shop_reports"`
}

type AnalysisSummary struct {
	TotalProfit  float64 `json:"total_profit"`
	TotalRevenue float64 `json:"total_revenue"`
	TotalOrders  int     `json:"total_orders"`
}

type ShopReport struct {
	ShopID      int     `json:"shop_id"`
	ShopName    string  `json:"shop_name"`
	Profit      float64 `json:"profit"`
	Revenue     float64 `json:"revenue"`
	OrderCount  int     `json:"order_count"`
	ProfitRate  float64 `json:"profit_rate"`
}

type AnalysisService struct {
	UserID int
}

func NewAnalysisService(userID int) *AnalysisService {
	return &AnalysisService{UserID: userID}
}

func (s *AnalysisService) GetReport() *AnalysisReport {
	slog.Info("getting analysis report", "user_id", s.UserID)

	shops, err := repository.GetUserShops(s.UserID)
	if err != nil {
		shops = nil
	}

	var totalProfit, totalRevenue float64
	shopReports := make([]ShopReport, 0, len(shops))

	for _, shop := range shops {
		profit, _ := repository.GetShopProfit(s.UserID, shop.ShopID)
		revenue, _ := repository.GetShopRevenue(s.UserID, shop.ShopID)

		totalProfit += profit
		totalRevenue += revenue

		profitRate := 0.0
		if revenue > 0 {
			profitRate = round2((profit / revenue) * 100)
		}

		shopReports = append(shopReports, ShopReport{
			ShopID:     shop.ShopID,
			ShopName:   shop.ShopName,
			Profit:     round2(profit),
			Revenue:    round2(revenue),
			OrderCount: 0,
			ProfitRate: profitRate,
		})
	}

	return &AnalysisReport{
		TotalShops: len(shops),
		Period:     "最近30天",
		Summary: AnalysisSummary{
			TotalProfit:  round2(totalProfit),
			TotalRevenue: round2(totalRevenue),
			TotalOrders:  0,
		},
		ShopReports: shopReports,
	}
}

func (s *AnalysisService) CollectMetrics() map[string]interface{} {
	slog.Info("collecting metrics", "user_id", s.UserID)
	return map[string]interface{}{
		"status":       "ok",
		"collected_at": time.Now().Format("2006-01-02 15:04:05"),
	}
}
