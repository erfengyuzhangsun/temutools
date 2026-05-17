package service

import (
	"log/slog"

	"github.com/erfengyuzhangsun/temutools/internal/repository"
)

type ShopOverview struct {
	ShopID          int     `json:"shop_id"`
	ShopName        string  `json:"shop_name"`
	Profit          float64 `json:"profit"`
	Revenue         float64 `json:"revenue"`
	PricingPending  int     `json:"pricing_pending"`
	InventoryAlerts int     `json:"inventory_alerts"`
	RiskWarnings    int     `json:"risk_warnings"`
	ReviewAlerts    int     `json:"review_alerts"`
}

type DashboardOverview struct {
	TotalProfit     float64         `json:"total_profit"`
	TotalRevenue    float64         `json:"total_revenue"`
	TotalAlerts     int             `json:"total_alerts"`
	PricingPending  int             `json:"pricing_pending"`
	InventoryAlerts int             `json:"inventory_alerts"`
	RiskWarnings    int             `json:"risk_warnings"`
	ReviewAlerts    int             `json:"review_alerts"`
	ShopCount       int             `json:"shop_count"`
	ShopDetails     []ShopOverview  `json:"shop_details"`
}

type AlertItem struct {
	Shop      string `json:"shop"`
	ShopID    int    `json:"shop_id"`
	Type      string `json:"type"`
	Message   string `json:"msg"`
	Severity  string `json:"severity"`
}

type DashboardService struct {
	UserID int
}

func NewDashboardService(userID int) *DashboardService {
	return &DashboardService{UserID: userID}
}

func (s *DashboardService) GetOverview() *DashboardOverview {
	slog.Info("getting dashboard overview", "user_id", s.UserID)

	shops, err := repository.GetUserShops(s.UserID)
	if err != nil {
		slog.Warn("failed to get user shops", "error", err)
		shops = nil
	}

	var totalProfit, totalRevenue float64
	var pricingPending, inventoryAlerts, riskWarnings, reviewAlerts int
	shopCards := make([]ShopOverview, 0)

	for _, shop := range shops {
		profit, _ := repository.GetShopProfit(s.UserID, shop.ShopID)
		revenue, _ := repository.GetShopRevenue(s.UserID, shop.ShopID)
		pp, _ := repository.GetPricingPendingCount(s.UserID, shop.ShopID)
		ia, _ := repository.GetInventoryAlertCount(s.UserID, shop.ShopID)
		rw, _ := repository.GetRiskWarningCount(s.UserID, shop.ShopID)
		ra := 0

		totalProfit += profit
		totalRevenue += revenue
		pricingPending += pp
		inventoryAlerts += ia
		riskWarnings += rw
		reviewAlerts += ra

		shopCards = append(shopCards, ShopOverview{
			ShopID:          shop.ShopID,
			ShopName:        shop.ShopName,
			Profit:          round2(profit),
			Revenue:         round2(revenue),
			PricingPending:  pp,
			InventoryAlerts: ia,
			RiskWarnings:    rw,
			ReviewAlerts:    ra,
		})
	}

	totalAlerts := pricingPending + inventoryAlerts + riskWarnings + reviewAlerts

	return &DashboardOverview{
		TotalProfit:     round2(totalProfit),
		TotalRevenue:    round2(totalRevenue),
		TotalAlerts:     totalAlerts,
		PricingPending:  pricingPending,
		InventoryAlerts: inventoryAlerts,
		RiskWarnings:    riskWarnings,
		ReviewAlerts:    reviewAlerts,
		ShopCount:       len(shops),
		ShopDetails:     shopCards,
	}
}

func (s *DashboardService) GetAllAlerts() ([]AlertItem, int) {
	slog.Info("getting all alerts", "user_id", s.UserID)

	shops, err := repository.GetUserShops(s.UserID)
	if err != nil {
		slog.Warn("failed to get user shops", "error", err)
		return nil, 0
	}

	alerts := make([]AlertItem, 0)

	for _, shop := range shops {
		expiring := repository.GetPricingExpiring(s.UserID, shop.ShopID)
		for _, a := range expiring {
			alerts = append(alerts, AlertItem{
				Shop:     shop.ShopName,
				ShopID:   shop.ShopID,
				Type:     "核价超时",
				Message:  a,
				Severity: "high",
			})
		}

		inventoryAlerts := repository.GetInventoryAlerts(s.UserID, shop.ShopID)
		for _, a := range inventoryAlerts {
			alerts = append(alerts, AlertItem{
				Shop:     shop.ShopName,
				ShopID:   shop.ShopID,
				Type:     a.AlertType,
				Message:  a.Message,
				Severity: "medium",
			})
		}
	}

	severityOrder := map[string]int{"high": 0, "medium": 1, "low": 2}
	for i := 0; i < len(alerts); i++ {
		for j := i + 1; j < len(alerts); j++ {
			if severityOrder[alerts[i].Severity] > severityOrder[alerts[j].Severity] {
				alerts[i], alerts[j] = alerts[j], alerts[i]
			}
		}
	}

	return alerts, len(alerts)
}

func round2(val float64) float64 {
	return float64(int(val*100)) / 100
}
