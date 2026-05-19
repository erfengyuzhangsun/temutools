package service

import (
	"encoding/json"
	"fmt"
	"log/slog"
	"time"

	"github.com/erfengyuzhangsun/temutools/internal/repository"
)

type WebhookMessage struct {
	MessageID   string          `json:"message_id"`
	MessageType string          `json:"message_type"`
	ShopID      int             `json:"shop_id"`
	Timestamp   int64           `json:"timestamp"`
	Data        json.RawMessage `json:"data"`
}

type WebhookProcessResult struct {
	MessageID   string `json:"message_id"`
	MessageType string `json:"message_type"`
	Processed   bool   `json:"processed"`
	Action      string `json:"action,omitempty"`
	Error       string `json:"error,omitempty"`
}

type WebhookService struct {
	UserID int
}

func NewWebhookService(userID int) *WebhookService {
	return &WebhookService{UserID: userID}
}

func (s *WebhookService) ProcessWebhook(msg *WebhookMessage) *WebhookProcessResult {
	slog.Info("processing webhook message", "message_id", msg.MessageID, "type", msg.MessageType)

	start := time.Now()
	result := &WebhookProcessResult{
		MessageID:   msg.MessageID,
		MessageType: msg.MessageType,
	}

	switch msg.MessageType {
	case "order_update":
		result = s.handleOrderUpdate(msg)
	case "order_shipped":
		result = s.handleOrderShipped(msg)
	case "inventory_change":
		result = s.handleInventoryChange(msg)
	case "pricing_update":
		result = s.handlePricingUpdate(msg)
	case "aftersale_update":
		result = s.handleAftersaleUpdate(msg)
	default:
		result.Processed = true
		result.Action = "ignored"
	}

	duration := time.Since(start).Seconds()
	_ = duration
	slog.Info("webhook processed", "message_id", msg.MessageID, "type", msg.MessageType,
		"processed", result.Processed, "action", result.Action)

	return result
}

func (s *WebhookService) handleOrderUpdate(msg *WebhookMessage) *WebhookProcessResult {
	var payload struct {
		OrderSn    string `json:"order_sn"`
		OldStatus  int    `json:"old_status"`
		NewStatus  int    `json:"new_status"`
		UpdateTime string `json:"update_time"`
	}
	if err := json.Unmarshal(msg.Data, &payload); err != nil {
		return &WebhookProcessResult{
			MessageID: msg.MessageID, MessageType: msg.MessageType,
			Processed: false, Error: fmt.Sprintf("解析订单更新消息失败: %s", err.Error()),
		}
	}

	slog.Info("order status changed", "order_sn", payload.OrderSn,
		"old_status", payload.OldStatus, "new_status", payload.NewStatus)

	return &WebhookProcessResult{
		MessageID: msg.MessageID, MessageType: msg.MessageType,
		Processed: true, Action: fmt.Sprintf("订单%s状态更新: %d→%d", payload.OrderSn, payload.OldStatus, payload.NewStatus),
	}
}

func (s *WebhookService) handleOrderShipped(msg *WebhookMessage) *WebhookProcessResult {
	var payload struct {
		OrderSn      string `json:"order_sn"`
		TrackingNo   string `json:"tracking_no"`
		LogisticsID  string `json:"logistics_id"`
		ShippedTime  string `json:"shipped_time"`
	}
	if err := json.Unmarshal(msg.Data, &payload); err != nil {
		return &WebhookProcessResult{
			MessageID: msg.MessageID, MessageType: msg.MessageType,
			Processed: false, Error: fmt.Sprintf("解析发货消息失败: %s", err.Error()),
		}
	}

	slog.Info("order shipped", "order_sn", payload.OrderSn,
		"tracking", payload.TrackingNo, "logistics", payload.LogisticsID)

	return &WebhookProcessResult{
		MessageID: msg.MessageID, MessageType: msg.MessageType,
		Processed: true, Action: fmt.Sprintf("订单%s已发货, 运单号%s", payload.OrderSn, payload.TrackingNo),
	}
}

func (s *WebhookService) handleInventoryChange(msg *WebhookMessage) *WebhookProcessResult {
	var payload struct {
		GoodsID   string `json:"goods_id"`
		SkuID     string `json:"sku_id"`
		OldStock  int    `json:"old_stock"`
		NewStock  int    `json:"new_stock"`
		ChangedAt string `json:"changed_at"`
	}
	if err := json.Unmarshal(msg.Data, &payload); err != nil {
		return &WebhookProcessResult{
			MessageID: msg.MessageID, MessageType: msg.MessageType,
			Processed: false, Error: fmt.Sprintf("解析库存变更消息失败: %s", err.Error()),
		}
	}

	slog.Info("inventory changed", "goods_id", payload.GoodsID, "sku_id", payload.SkuID,
		"old_stock", payload.OldStock, "new_stock", payload.NewStock)

	return &WebhookProcessResult{
		MessageID: msg.MessageID, MessageType: msg.MessageType,
		Processed: true, Action: fmt.Sprintf("库存变更: %s→%s (%d→%d)", payload.GoodsID, payload.SkuID, payload.OldStock, payload.NewStock),
	}
}

func (s *WebhookService) handlePricingUpdate(msg *WebhookMessage) *WebhookProcessResult {
	var payload struct {
		SkuID       string  `json:"sku_id"`
		OldPrice    float64 `json:"old_price"`
		NewPrice    float64 `json:"new_price"`
		UpdatedAt   string  `json:"updated_at"`
	}
	if err := json.Unmarshal(msg.Data, &payload); err != nil {
		return &WebhookProcessResult{
			MessageID: msg.MessageID, MessageType: msg.MessageType,
			Processed: false, Error: fmt.Sprintf("解析核价消息失败: %s", err.Error()),
		}
	}

	slog.Info("pricing updated", "sku_id", payload.SkuID,
		"old_price", payload.OldPrice, "new_price", payload.NewPrice)

	return &WebhookProcessResult{
		MessageID: msg.MessageID, MessageType: msg.MessageType,
		Processed: true, Action: fmt.Sprintf("核价更新SKU %s: %.2f→%.2f", payload.SkuID, payload.OldPrice, payload.NewPrice),
	}
}

func (s *WebhookService) handleAftersaleUpdate(msg *WebhookMessage) *WebhookProcessResult {
	var payload struct {
		AftersaleID  string `json:"aftersale_id"`
		OrderSn      string `json:"order_sn"`
		OldStatus    int    `json:"old_status"`
		NewStatus    int    `json:"new_status"`
		UpdatedAt    string `json:"updated_at"`
	}
	if err := json.Unmarshal(msg.Data, &payload); err != nil {
		return &WebhookProcessResult{
			MessageID: msg.MessageID, MessageType: msg.MessageType,
			Processed: false, Error: fmt.Sprintf("解析售后消息失败: %s", err.Error()),
		}
	}

	slog.Info("aftersale updated", "aftersale_id", payload.AftersaleID, "order_sn", payload.OrderSn,
		"old_status", payload.OldStatus, "new_status", payload.NewStatus)

	repository.SaveSyncRecord(s.UserID, msg.ShopID, "aftersale", 0, 0, 2*time.Second)

	return &WebhookProcessResult{
		MessageID: msg.MessageID, MessageType: msg.MessageType,
		Processed: true, Action: fmt.Sprintf("售后%s状态更新: %d→%d", payload.AftersaleID, payload.OldStatus, payload.NewStatus),
	}
}
