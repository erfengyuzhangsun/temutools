package service

import (
	"log/slog"

	"github.com/erfengyuzhangsun/temutools/internal/repository"
)

type RiskReport struct {
	UserID      int            `json:"user_id"`
	ShopCount   int            `json:"shop_count"`
	OverallScore int           `json:"overall_score"`
	RiskLevel   string         `json:"risk_level"`
	Alerts      []RiskAlert    `json:"alerts"`
	CheckedAt   string         `json:"checked_at"`
}

type RiskAlert struct {
	ShopID   int    `json:"shop_id"`
	ShopName string `json:"shop_name"`
	Type     string `json:"type"`
	Message  string `json:"message"`
	Severity string `json:"severity"`
}

type RiskCheckResult struct {
	RiskScore int         `json:"risk_score"`
	Alerts    []RiskAlert `json:"alerts"`
	Passed    bool        `json:"passed"`
}

type RiskService struct {
	UserID int
}

func NewRiskService(userID int) *RiskService {
	return &RiskService{UserID: userID}
}

func (s *RiskService) GetReport() *RiskReport {
	slog.Info("getting risk report", "user_id", s.UserID)

	shops, err := repository.GetUserShops(s.UserID)
	if err != nil {
		shops = nil
	}

	alerts := make([]RiskAlert, 0)
	alertCount := 0

	for _, shop := range shops {
		pp, _ := repository.GetPricingPendingCount(s.UserID, shop.ShopID)
		if pp > 0 {
			alertCount += pp
			alerts = append(alerts, RiskAlert{
				ShopID:   shop.ShopID,
				ShopName: shop.ShopName,
				Type:     "核价待处理",
				Message:  "有待处理的核价通知",
				Severity: "medium",
			})
		}

		ia, _ := repository.GetInventoryAlertCount(s.UserID, shop.ShopID)
		if ia > 0 {
			alertCount += ia
			alerts = append(alerts, RiskAlert{
				ShopID:   shop.ShopID,
				ShopName: shop.ShopName,
				Type:     "库存告警",
				Message:  "存在库存异常",
				Severity: "low",
			})
		}
	}

	overallScore := 100 - alertCount*10
	if overallScore < 0 {
		overallScore = 0
	}

	riskLevel := "low"
	if overallScore < 60 {
		riskLevel = "high"
	} else if overallScore < 80 {
		riskLevel = "medium"
	}

	return &RiskReport{
		UserID:       s.UserID,
		ShopCount:    len(shops),
		OverallScore: overallScore,
		RiskLevel:    riskLevel,
		Alerts:       alerts,
		CheckedAt:    "now",
	}
}

func (s *RiskService) RunCheck(shopID int) *RiskCheckResult {
	slog.Info("running risk check", "user_id", s.UserID, "shop_id", shopID)

	pp, _ := repository.GetPricingPendingCount(s.UserID, shopID)

	alerts := make([]RiskAlert, 0)
	if pp > 0 {
		alerts = append(alerts, RiskAlert{
			ShopID:   shopID,
			Type:     "核价待处理",
			Message:  "有核价通知待处理",
			Severity: "medium",
		})
	}

	score := 100 - len(alerts)*15
	if score < 0 {
		score = 0
	}

	return &RiskCheckResult{
		RiskScore: score,
		Alerts:    alerts,
		Passed:    len(alerts) == 0,
	}
}
