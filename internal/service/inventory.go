package service

import (
	"fmt"
	"log/slog"
	"time"

	"github.com/erfengyuzhangsun/temutools/internal/repository"
	"github.com/erfengyuzhangsun/temutools/internal/temu"
)

type InventoryItem struct {
	ShopID       int     `json:"shop_id"`
	ShopName     string  `json:"shop_name"`
	SkuCode      string  `json:"sku_code"`
	SkuName      string  `json:"sku_name"`
	Category     string  `json:"category"`
	CostPrice    float64 `json:"cost_price"`
	TotalSales   int     `json:"total_sales"`
	TotalRevenue float64 `json:"total_revenue"`
	TotalProfit  float64 `json:"total_profit"`
	ProfitRate   float64 `json:"profit_rate"`
	IsLowStock   bool    `json:"is_low_stock"`
	IsLoss       bool    `json:"is_loss"`
	LastSyncAt   string  `json:"last_sync_at,omitempty"`
}

type ShopInventorySummary struct {
	ShopID        int              `json:"shop_id"`
	ShopName      string           `json:"shop_name"`
	SkuCount      int              `json:"sku_count"`
	LowStockCount int              `json:"low_stock_count"`
	Items         []InventoryItem  `json:"items,omitempty"`
}

type InventoryService struct {
	UserID int
}

func NewInventoryService(userID int) *InventoryService {
	return &InventoryService{UserID: userID}
}

func (s *InventoryService) GetInventoryList() ([]ShopInventorySummary, error) {
	slog.Info("getting inventory list", "user_id", s.UserID)

	shops, err := repository.GetUserShops(s.UserID)
	if err != nil {
		slog.Warn("failed to get user shops", "error", err)
		return nil, fmt.Errorf("获取店铺列表失败: %w", err)
	}

	summaries := make([]ShopInventorySummary, 0, len(shops))
	for _, shop := range shops {
		skus, err := repository.GetShopSKUs(s.UserID, shop.ShopID)
		if err != nil {
			slog.Warn("failed to get shop skus", "shop_id", shop.ShopID, "error", err)
			skus = nil
		}

		items := make([]InventoryItem, 0, len(skus))
		lowStockCount := 0
		for _, sku := range skus {
			isLow := sku.TotalSales > 0 && sku.TotalSales < 10
			if isLow {
				lowStockCount++
			}
			items = append(items, InventoryItem{
				ShopID:       shop.ShopID,
				ShopName:     shop.ShopName,
				SkuCode:      sku.SkuCode,
				SkuName:      sku.SkuName,
				Category:     sku.Category,
				CostPrice:    sku.CostPrice,
				TotalSales:   sku.TotalSales,
				TotalRevenue: sku.TotalRevenue,
				TotalProfit:  sku.TotalProfit,
				ProfitRate:   sku.ProfitRate,
				IsLowStock:   isLow,
				IsLoss:       sku.IsLoss,
			})
		}

		summaries = append(summaries, ShopInventorySummary{
			ShopID:        shop.ShopID,
			ShopName:      shop.ShopName,
			SkuCount:      len(skus),
			LowStockCount: lowStockCount,
			Items:         items,
		})
	}

	return summaries, nil
}

func (s *InventoryService) SyncInventory(shopID int, client temu.ApiClient) (int, error) {
	slog.Info("syncing inventory", "user_id", s.UserID, "shop_id", shopID)

	skus, err := repository.GetShopSKUs(s.UserID, shopID)
	if err != nil {
		return 0, fmt.Errorf("获取SKU列表失败: %w", err)
	}

	if len(skus) == 0 {
		return 0, nil
	}

	skuCodes := make([]string, len(skus))
	for i, sku := range skus {
		skuCodes[i] = sku.SkuCode
	}

	resp, err := client.GetInventory(skuCodes)
	if err != nil {
		return 0, fmt.Errorf("同步库存失败: %w", err)
	}
	if !resp.Success {
		return 0, fmt.Errorf("API返回错误: %s", resp.Error)
	}

	repository.SaveSyncRecord(s.UserID, shopID, "inventory", len(skuCodes), len(skuCodes), 2*time.Second)

	return len(skuCodes), nil
}

type InventoryAlertConfig struct {
	LowStockThreshold int    `json:"low_stock_threshold"`
	Enabled           bool   `json:"enabled"`
	Message           string `json:"message,omitempty"`
}

func (s *InventoryService) SetAlertConfig(cfg InventoryAlertConfig) *InventoryAlertConfig {
	slog.Info("set inventory alert config", "user_id", s.UserID, "threshold", cfg.LowStockThreshold)
	if cfg.LowStockThreshold <= 0 {
		cfg.LowStockThreshold = 10
	}
	cfg.Message = fmt.Sprintf("低库存告警阈值已设为 %d", cfg.LowStockThreshold)
	return &cfg
}
