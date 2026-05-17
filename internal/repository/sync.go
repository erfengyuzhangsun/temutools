package repository

import (
	"log/slog"
	"time"

	"github.com/erfengyuzhangsun/temutools/internal/models"
)

func GetExistingOrderIDs(shopID int) map[string]struct{} {
	db := GetDB()
	if db == nil {
		return make(map[string]struct{})
	}

	if !db.Migrator().HasTable("temu_sync_orders") {
		return make(map[string]struct{})
	}

	var orderIDs []string
	err := db.Table("temu_sync_orders").
		Select("DISTINCT order_id").
		Where("shop_id = ?", shopID).
		Pluck("order_id", &orderIDs).Error
	if err != nil {
		slog.Warn("failed to query existing order IDs", "error", err)
		return make(map[string]struct{})
	}

	result := make(map[string]struct{}, len(orderIDs))
	for _, id := range orderIDs {
		result[id] = struct{}{}
	}
	return result
}

func SaveSyncRecord(userID, shopID int, syncType string, syncedCount, totalCount int, duration time.Duration) {
	db := GetDB()
	if db == nil {
		return
	}

	record := models.SyncRecord{
		UserID:      userID,
		ShopID:      shopID,
		SyncType:    syncType,
		Status:      "success",
		SyncedCount: syncedCount,
		TotalCount:  totalCount,
		DurationMs:  int(duration.Milliseconds()),
		StartedAt:   time.Now().Add(-duration),
	}

	if err := db.Create(&record).Error; err != nil {
		slog.Warn("failed to save sync record", "error", err)
	}
}

type SyncRecordBrief struct {
	SyncID          int
	ShopID          int
	SyncType        string
	Status          string
	SyncedCount     int
	DurationMs      int
	StartedAt       time.Time
	CreatedAt       time.Time
}

func QuerySyncRecords(userID, shopID int, limit int) ([]SyncRecordBrief, error) {
	db := GetDB()
	if db == nil {
		return nil, nil
	}

	var records []models.SyncRecord
	result := db.Where("user_id = ? AND shop_id = ?", userID, shopID).
		Order("created_at DESC").
		Limit(limit).
		Find(&records)
	if result.Error != nil {
		return nil, result.Error
	}

	briefs := make([]SyncRecordBrief, len(records))
	for i, r := range records {
		briefs[i] = SyncRecordBrief{
			SyncID:      r.SyncID,
			ShopID:      r.ShopID,
			SyncType:    r.SyncType,
			Status:      r.Status,
			SyncedCount: r.SyncedCount,
			DurationMs:  r.DurationMs,
			StartedAt:   r.StartedAt,
			CreatedAt:   r.CreatedAt,
		}
	}
	return briefs, nil
}
