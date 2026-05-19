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

type PriceAdjustmentItem struct {
	Sku              string  `json:"sku"`
	SkuName          string  `json:"sku_name"`
	CurrentPrice     float64 `json:"current_price"`
	CostPrice        float64 `json:"cost_price"`
	CurrentMargin    float64 `json:"current_margin"`
	TargetMargin     float64 `json:"target_margin"`
	TargetPrice      float64 `json:"target_price"`
	SuggestedAction  string  `json:"suggested_action"`
	RiskCheckPassed  bool    `json:"risk_check_passed"`
	RiskCheckMessage string  `json:"risk_check_message,omitempty"`
	Executed         bool    `json:"executed"`
	ExecutedMessage  string  `json:"executed_message,omitempty"`
}

type PriceAdjustmentResult struct {
	TotalChecked    int                    `json:"total_checked"`
	NeedsAdjustment int                   `json:"needs_adjustment"`
	Executed        int                   `json:"executed"`
	Items           []PriceAdjustmentItem `json:"items"`
}

func (s *PricingService) AutoAdjustPrices(shopID int, client temu.ApiClient, targetMargin float64) (*PriceAdjustmentResult, error) {
	slog.Info("starting auto price adjustment", "user_id", s.UserID, "shop_id", shopID, "target_margin", targetMargin)
	if targetMargin <= 0 {
		targetMargin = 20.0
	}

	skus, err := repository.GetShopSKUs(s.UserID, shopID)
	if err != nil {
		return nil, fmt.Errorf("获取SKU列表失败: %w", err)
	}
	if len(skus) == 0 {
		return &PriceAdjustmentResult{}, nil
	}

	skuCodes := make([]string, len(skus))
	for i, sku := range skus {
		skuCodes[i] = sku.SkuCode
	}

	resp, err := client.GetSkuPriceList(skuCodes)
	if err != nil {
		return nil, fmt.Errorf("获取SKU价格失败: %w", err)
	}

	var pricePayload struct {
		Prices []struct {
			Sku          string  `json:"sku"`
			CurrentPrice float64 `json:"currentPrice"`
		} `json:"prices"`
	}
	if resp.Success {
		parseJSON(resp.Result, &pricePayload)
		parseJSON(resp.Data, &pricePayload)
	}

	priceMap := make(map[string]float64)
	for _, p := range pricePayload.Prices {
		priceMap[p.Sku] = p.CurrentPrice
	}

	items := make([]PriceAdjustmentItem, 0)
	needsAdj := 0
	executed := 0

	for _, sku := range skus {
		currentPrice, hasPrice := priceMap[sku.SkuCode]
		if !hasPrice || sku.CostPrice <= 0 {
			continue
		}

		currentMargin := ((currentPrice - sku.CostPrice) / sku.CostPrice) * 100
		targetPrice := sku.CostPrice * (1 + targetMargin/100)

		item := PriceAdjustmentItem{
			Sku:           sku.SkuCode,
			SkuName:       sku.SkuName,
			CurrentPrice:  currentPrice,
			CostPrice:     sku.CostPrice,
			CurrentMargin: round2(currentMargin),
			TargetMargin:  targetMargin,
			TargetPrice:   round2(targetPrice),
		}

		diff := targetPrice - currentPrice
		changePercent := (diff / currentPrice) * 100

		if changePercent < 1 && changePercent > -1 {
			item.SuggestedAction = "skip"
			item.RiskCheckPassed = true
			item.RiskCheckMessage = "当前价格已在目标区间内"
			items = append(items, item)
			continue
		}

		needsAdj++

		if changePercent < -5 {
			item.SuggestedAction = "warn"
			item.RiskCheckPassed = false
			item.RiskCheckMessage = fmt.Sprintf("降价幅度%.1f%%超过安全阈值5%%，需人工审核", changePercent)
			items = append(items, item)
			continue
		}

		item.SuggestedAction = "adjust"
		item.RiskCheckPassed = true
		item.RiskCheckMessage = fmt.Sprintf("建议调价%.1f%% (%.2f→%.2f)", changePercent, currentPrice, targetPrice)

		negoResp, negoErr := client.NegotiatePricing("", fmt.Sprintf("%.2f", targetPrice))
		if negoErr != nil {
			item.Executed = false
			item.ExecutedMessage = fmt.Sprintf("调价失败: %s", negoErr.Error())
		} else if negoResp != nil && negoResp.Success {
			item.Executed = true
			executed++
			item.ExecutedMessage = fmt.Sprintf("已发起调价: %.2f→%.2f (目标毛利率%.0f%%)", currentPrice, targetPrice, targetMargin)
			repository.SavePricingLog(s.UserID, shopID, "", sku.SkuCode,
				"adjust", targetPrice, sku.CostPrice, round2(targetMargin), item.ExecutedMessage, false)
		} else {
			item.Executed = false
			errMsg := "调价被平台拒绝"
			if negoResp != nil {
				errMsg = negoResp.Error
			}
			item.ExecutedMessage = fmt.Sprintf("调价失败: %s", errMsg)
		}

		items = append(items, item)
	}

	return &PriceAdjustmentResult{
		TotalChecked:    len(items),
		NeedsAdjustment: needsAdj,
		Executed:        executed,
		Items:           items,
	}, nil
}
