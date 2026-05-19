package service

import (
	"log/slog"

	"github.com/erfengyuzhangsun/temutools/internal/temu"
)

type AftersaleItem struct {
	AftersaleID string  `json:"aftersale_id"`
	OrderSn     string  `json:"order_sn"`
	Sku         string  `json:"sku"`
	GoodsName   string  `json:"goods_name"`
	Status      string  `json:"status"`
	Reason      string  `json:"reason"`
	Amount      float64 `json:"amount"`
	Quantity    int     `json:"quantity"`
	CreatedAt   string  `json:"created_at"`
}

type ParentAftersaleItem struct {
	ParentAfterSalesSn     string `json:"parent_after_sales_sn"`
	ParentOrderSn          string `json:"parent_order_sn"`
	AfterSalesStatusGroup  int    `json:"after_sales_status_group"`
	ParentAfterSalesStatus int    `json:"parent_after_sales_status"`
	AfterSalesType         int    `json:"after_sales_type"`
	CreateAt               int64  `json:"create_at"`
	UpdateAt               int64  `json:"update_at"`
}

type ParentReturnOrderItem struct {
	ParentAfterSalesSn string  `json:"parent_after_sales_sn"`
	ReturnReason       string  `json:"return_reason"`
	ReturnQuantity     int     `json:"return_quantity"`
	ReturnAmount       float64 `json:"return_amount"`
	ReturnStatus       string  `json:"return_status"`
	ReturnType         int     `json:"return_type"`
	CreateAt           int64   `json:"create_at"`
	UpdateAt           int64   `json:"update_at"`
}

type AftersaleService struct {
	UserID int
}

func NewAftersaleService(userID int) *AftersaleService {
	return &AftersaleService{UserID: userID}
}

func (s *AftersaleService) ListAftersales(client temu.ApiClient, page, pageSize int) ([]AftersaleItem, error) {
	slog.Info("listing aftersales", "user_id", s.UserID, "page", page)

	resp, err := client.GetAftersalesList(page, pageSize)
	if err != nil {
		slog.Warn("get aftersales list failed (maybe mock)", "error", err)
		return []AftersaleItem{}, nil
	}
	if !resp.Success {
		return []AftersaleItem{}, nil
	}

	items := make([]AftersaleItem, 0)
	for _, a := range extractList(resp, "aftersales") {
		item := AftersaleItem{}
		if id, ok := a["aftersaleId"].(string); ok {
			item.AftersaleID = id
		}
		if orderSn, ok := a["orderSn"].(string); ok {
			item.OrderSn = orderSn
		}
		if sku, ok := a["sku"].(string); ok {
			item.Sku = sku
		}
		if name, ok := a["goodsName"].(string); ok {
			item.GoodsName = name
		}
		if status, ok := a["status"].(string); ok {
			item.Status = status
		}
		if reason, ok := a["reason"].(string); ok {
			item.Reason = reason
		}
		if amount, ok := a["amount"].(float64); ok {
			item.Amount = amount
		}
		if qty, ok := a["quantity"].(float64); ok {
			item.Quantity = int(qty)
		}
		if t, ok := a["createdAt"].(string); ok {
			item.CreatedAt = t
		}
		items = append(items, item)
	}
	return items, nil
}

func (s *AftersaleService) ListParentAftersales(client temu.ApiClient, page, pageSize int, statusGroup int, updateAtStart, updateAtEnd int64) ([]ParentAftersaleItem, error) {
	slog.Info("listing parent aftersales", "user_id", s.UserID, "page", page)

	resp, err := client.GetParentAftersalesList(page, pageSize, statusGroup, updateAtStart, updateAtEnd)
	if err != nil {
		slog.Warn("get parent aftersales list failed", "error", err)
		return []ParentAftersaleItem{}, nil
	}
	if !resp.Success {
		return []ParentAftersaleItem{}, nil
	}

	items := make([]ParentAftersaleItem, 0)
	for _, a := range extractList(resp, "data") {
		item := ParentAftersaleItem{}
		if sn, ok := a["parentAfterSalesSn"].(string); ok {
			item.ParentAfterSalesSn = sn
		}
		if sn, ok := a["parentOrderSn"].(string); ok {
			item.ParentOrderSn = sn
		}
		if g, ok := a["afterSalesStatusGroup"].(float64); ok {
			item.AfterSalesStatusGroup = int(g)
		}
		if s, ok := a["parentAfterSalesStatus"].(float64); ok {
			item.ParentAfterSalesStatus = int(s)
		}
		if t, ok := a["afterSalesType"].(float64); ok {
			item.AfterSalesType = int(t)
		}
		if t, ok := a["createAt"].(float64); ok {
			item.CreateAt = int64(t)
		}
		if t, ok := a["updateAt"].(float64); ok {
			item.UpdateAt = int64(t)
		}
		items = append(items, item)
	}
	return items, nil
}

func (s *AftersaleService) GetParentReturnOrder(client temu.ApiClient, parentAfterSalesSn string) (*ParentReturnOrderItem, error) {
	slog.Info("getting parent return order", "parent_after_sales_sn", parentAfterSalesSn)

	resp, err := client.GetParentReturnOrder(parentAfterSalesSn)
	if err != nil {
		return nil, err
	}
	if !resp.Success {
		return nil, nil
	}

	items := extractList(resp, "data")
	if len(items) == 0 {
		items = extractList(resp, "result")
	}
	if len(items) == 0 {
		return nil, nil
	}

	a := items[0]
	item := &ParentReturnOrderItem{}
	if sn, ok := a["parentAfterSalesSn"].(string); ok {
		item.ParentAfterSalesSn = sn
	}
	if reason, ok := a["returnReason"].(string); ok {
		item.ReturnReason = reason
	}
	if qty, ok := a["returnQuantity"].(float64); ok {
		item.ReturnQuantity = int(qty)
	}
	if amount, ok := a["returnAmount"].(float64); ok {
		item.ReturnAmount = amount
	}
	if status, ok := a["returnStatus"].(string); ok {
		item.ReturnStatus = status
	}
	if t, ok := a["returnType"].(float64); ok {
		item.ReturnType = int(t)
	}
	if t, ok := a["createAt"].(float64); ok {
		item.CreateAt = int64(t)
	}
	if t, ok := a["updateAt"].(float64); ok {
		item.UpdateAt = int64(t)
	}
	return item, nil
}

func (s *AftersaleService) CountByStatus(client temu.ApiClient) (map[string]int, error) {
	slog.Info("counting aftersales by status", "user_id", s.UserID)

	items, err := s.ListAftersales(client, 1, 100)
	if err != nil {
		return nil, err
	}

	counts := map[string]int{"pending": 0, "approved": 0, "rejected": 0, "completed": 0}
	for _, item := range items {
		status := item.Status
		if status == "" {
			status = "pending"
		}
		statusLower := status
		switch {
		case statusLower == "PENDING":
			counts["pending"]++
		case statusLower == "APPROVED":
			counts["approved"]++
		case statusLower == "REJECTED":
			counts["rejected"]++
		case statusLower == "COMPLETED":
			counts["completed"]++
		default:
			counts["pending"]++
		}
	}

	return counts, nil
}

func init() {
	slog.Info("Aftersale service initialized")
}
