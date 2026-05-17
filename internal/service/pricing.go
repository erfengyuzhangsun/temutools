package service

import (
	"fmt"
	"log/slog"
	"time"

	"github.com/erfengyuzhangsun/temutools/internal/repository"
	"github.com/erfengyuzhangsun/temutools/internal/temu"
)

type PricingResult struct {
	NoticeID    string  `json:"notice_id"`
	Sku         string  `json:"sku"`
	SupplyPrice float64 `json:"supply_price"`
	CostPrice   float64 `json:"cost_price"`
	GrossMargin float64 `json:"gross_margin"`
	Action      string  `json:"action"`
	Reason      string  `json:"reason"`
}

type PricingLogItem struct {
	LogID       int       `json:"log_id"`
	NoticeID    string    `json:"notice_id"`
	Sku         string    `json:"sku"`
	Action      string    `json:"action"`
	SupplyPrice float64   `json:"supply_price"`
	CostPrice   float64   `json:"cost_price"`
	GrossMargin float64   `json:"gross_margin"`
	Reason      string    `json:"reason"`
	IsActivity  bool      `json:"is_activity"`
	HandledAt   time.Time `json:"handled_at"`
}

type AutoPricingResult struct {
	HandledCount int             `json:"handled_count"`
	Results      []PricingResult `json:"results"`
	ExpiringSoon []ExpiringItem  `json:"expiring_soon,omitempty"`
}

type ExpiringItem struct {
	NoticeID string `json:"notice_id"`
	Sku      string `json:"sku"`
	ExpireAt string `json:"expire_at"`
}

type PricingService struct {
	UserID int
}

func NewPricingService(userID int) *PricingService {
	return &PricingService{UserID: userID}
}

func (s *PricingService) AutoHandlePricing(shopID int, client temu.ApiClient) (*AutoPricingResult, error) {
	slog.Info("starting auto pricing", "user_id", s.UserID, "shop_id", shopID)

	resp, err := client.GetPricingNotices(1, 50)
	if err != nil {
		return nil, fmt.Errorf("fetch pricing notices failed: %w", err)
	}
	if !resp.Success {
		return nil, fmt.Errorf("fetch pricing notices failed: %s", resp.Error)
	}

	var noticesPayload struct {
		Notices []struct {
			NoticeID    string  `json:"notice_id"`
			Sku         string  `json:"sku"`
			SupplyPrice float64 `json:"supply_price"`
			IsActivity  bool    `json:"is_activity"`
			ExpireAt    string  `json:"expire_at"`
		} `json:"notices"`
	}
	if err := parseJSON(resp.Result, &noticesPayload); err != nil {
		if err := parseJSON(resp.Data, &noticesPayload); err != nil {
			return nil, fmt.Errorf("parse notices response failed: %w", err)
		}
	}

	notices := noticesPayload.Notices
	if len(notices) == 0 {
		return &AutoPricingResult{
			HandledCount: 0,
			Results:      []PricingResult{},
		}, nil
	}

	profitThreshold := 20.0
	activityThreshold := 10.0
	now := time.Now()
	results := make([]PricingResult, 0)
	expiringSoon := make([]ExpiringItem, 0)

	for _, notice := range notices {
		costPrice, err := repository.GetSkuCostPrice(s.UserID, shopID, notice.Sku)
		if err != nil || costPrice <= 0 {
			results = append(results, PricingResult{
				NoticeID:    notice.NoticeID,
				Sku:         notice.Sku,
				SupplyPrice: notice.SupplyPrice,
				CostPrice:   0,
				GrossMargin: 0,
				Action:      "skip",
				Reason:      "成本价缺失，待人工处理",
			})
			repository.SavePricingLog(s.UserID, shopID, notice.NoticeID, notice.Sku,
				"skip", notice.SupplyPrice, 0, 0, "成本价缺失，待人工处理", notice.IsActivity)
			continue
		}

		grossMargin := ((notice.SupplyPrice - costPrice) / costPrice) * 100
		threshold := profitThreshold
		if notice.IsActivity {
			threshold = activityThreshold
		}

		var action, reason string
		if grossMargin >= threshold {
			action = "accept"
			reason = "毛利率达标，自动接受"
			client.AcceptPricing(notice.NoticeID)
		} else {
			action = "reject"
			reason = fmt.Sprintf("毛利率%.1f%%低于阈值%.0f%%，自动拒绝", grossMargin, threshold)
			client.RejectPricing(notice.NoticeID, reason)
		}

		results = append(results, PricingResult{
			NoticeID:    notice.NoticeID,
			Sku:         notice.Sku,
			SupplyPrice: notice.SupplyPrice,
			CostPrice:   costPrice,
			GrossMargin: round2(grossMargin),
			Action:      action,
			Reason:      reason,
		})

		repository.SavePricingLog(s.UserID, shopID, notice.NoticeID, notice.Sku,
			action, notice.SupplyPrice, costPrice, round2(grossMargin), reason, notice.IsActivity)

		if notice.ExpireAt != "" {
			expireDt, err := time.Parse(time.RFC3339, notice.ExpireAt)
			if err == nil {
				remaining := expireDt.Sub(now)
				if remaining > 0 && remaining < 24*time.Hour {
					expiringSoon = append(expiringSoon, ExpiringItem{
						NoticeID: notice.NoticeID,
						Sku:      notice.Sku,
						ExpireAt: notice.ExpireAt,
					})
				}
			}
		}
	}

	return &AutoPricingResult{
		HandledCount: len(results),
		Results:      results,
		ExpiringSoon: expiringSoon,
	}, nil
}

func (s *PricingService) GetPricingLogs(shopID int, limit int) ([]PricingLogItem, error) {
	if limit <= 0 {
		limit = 50
	}

	rows, err := repository.QueryPricingLogs(s.UserID, shopID, limit)
	if err != nil {
		return nil, err
	}

	items := make([]PricingLogItem, len(rows))
	for i, r := range rows {
		items[i] = PricingLogItem{
			LogID:       r.LogID,
			NoticeID:    r.NoticeID,
			Sku:         r.Sku,
			Action:      r.Action,
			SupplyPrice: r.SupplyPrice,
			CostPrice:   r.CostPrice,
			GrossMargin: r.GrossMargin,
			Reason:      r.Reason,
			IsActivity:  r.IsActivity,
			HandledAt:   r.HandledAt,
		}
	}
	return items, nil
}
