package service

import (
	"fmt"
	"log/slog"
	"time"

	"github.com/erfengyuzhangsun/temutools/internal/repository"
	"github.com/erfengyuzhangsun/temutools/internal/temu"
)

type SyncResult struct {
	Success         bool   `json:"success"`
	Message         string `json:"message"`
	ErrorCode       string `json:"error_code,omitempty"`
	SyncedCount     int    `json:"synced_count"`
	DuplicateSkipped int   `json:"duplicate_skipped"`
	TotalInAPI      int    `json:"total_in_api"`
	DurationSeconds  float64 `json:"duration_seconds"`
	Warnings        []string `json:"warnings,omitempty"`
	Orders          []interface{} `json:"orders,omitempty"`
}

type SyncHistoryItem struct {
	SyncID          int       `json:"sync_id"`
	ShopID          int       `json:"shop_id"`
	SyncType        string    `json:"sync_type"`
	Status          string    `json:"status"`
	SyncedCount     int       `json:"synced_count"`
	DurationSeconds float64   `json:"duration_seconds"`
	StartedAt       time.Time `json:"started_at"`
	FinishedAt      time.Time `json:"finished_at"`
}

type ApiSyncService struct {
	UserID int
}

func NewApiSyncService(userID int) *ApiSyncService {
	return &ApiSyncService{UserID: userID}
}

func (s *ApiSyncService) SyncOrders(shopID int, client temu.ApiClient) *SyncResult {
	startTime := time.Now()
	slog.Info("starting order sync", "user_id", s.UserID, "shop_id", shopID)

	pageSize := 50
	allOrders := make([]interface{}, 0)
	syncedCount := 0
	duplicateCount := 0
	warnings := make([]string, 0)

	existingIDs := repository.GetExistingOrderIDs(shopID)

	page := 1
	for {
		resp, err := client.GetOrders(page, pageSize, nil)
		if err != nil {
			return &SyncResult{
				Success:   false,
				Message:   fmt.Sprintf("同步失败: %s", err.Error()),
				ErrorCode: "SYNC_ERROR",
				DurationSeconds: time.Since(startTime).Seconds(),
			}
		}
		if !resp.Success {
			return &SyncResult{
				Success:   false,
				Message:   resp.Error,
				ErrorCode: "API_ERROR",
				DurationSeconds: time.Since(startTime).Seconds(),
			}
		}

		var payload struct {
			Orders []interface{} `json:"orders"`
			Total  int           `json:"total"`
		}
		if err := parseJSON(resp.Result, &payload); err != nil {
			if err := parseJSON(resp.Data, &payload); err != nil {
				break
			}
		}

		if len(payload.Orders) == 0 {
			break
		}

		for _, order := range payload.Orders {
			orderMap, ok := order.(map[string]interface{})
			if !ok {
				continue
			}

			orderID, _ := orderMap["parentOrderSn"].(string)
			if orderID == "" {
				orderID, _ = orderMap["order_id"].(string)
			}

			if orderID != "" {
				if _, exists := existingIDs[orderID]; exists {
					duplicateCount++
					continue
				}
				existingIDs[orderID] = struct{}{}
			}

			if _, ok := orderMap["sku"]; !ok {
				warnings = append(warnings, fmt.Sprintf("订单 %s 缺失SKU字段", orderID))
			}
			if _, ok := orderMap["quantity"]; !ok {
				warnings = append(warnings, fmt.Sprintf("订单 %s 缺失数量字段", orderID))
			}

			allOrders = append(allOrders, order)
			syncedCount++
		}

		if len(payload.Orders) < pageSize {
			break
		}
		page++
	}

	if syncedCount > 0 {
		repository.SaveSyncRecord(s.UserID, shopID, "order", syncedCount, len(allOrders), time.Since(startTime))
	}

	return &SyncResult{
		Success:          true,
		Message:          fmt.Sprintf("同步完成，新增%d条", syncedCount),
		SyncedCount:      syncedCount,
		DuplicateSkipped: duplicateCount,
		TotalInAPI:       syncedCount + duplicateCount,
		DurationSeconds:  time.Since(startTime).Seconds(),
		Warnings:         warnings,
		Orders:           allOrders,
	}
}

func (s *ApiSyncService) SyncAllShops(shopIDs []int, clients map[int]temu.ApiClient) map[int]*SyncResult {
	results := make(map[int]*SyncResult)
	for _, shopID := range shopIDs {
		client, ok := clients[shopID]
		if !ok {
			client = temu.NewMockClient(shopID)
		}
		result := s.SyncOrders(shopID, client)
		results[shopID] = result
	}
	return results
}

func (s *ApiSyncService) GetSyncHistory(shopID int, limit int) ([]SyncHistoryItem, error) {
	if limit <= 0 {
		limit = 20
	}

	records, err := repository.QuerySyncRecords(s.UserID, shopID, limit)
	if err != nil {
		return nil, err
	}

	items := make([]SyncHistoryItem, len(records))
	for i, r := range records {
		items[i] = SyncHistoryItem{
			SyncID:          r.SyncID,
			ShopID:          r.ShopID,
			SyncType:        r.SyncType,
			Status:          r.Status,
			SyncedCount:     r.SyncedCount,
			DurationSeconds: float64(r.DurationMs) / 1000,
			StartedAt:       r.StartedAt,
			FinishedAt:      r.CreatedAt,
		}
	}
	return items, nil
}
