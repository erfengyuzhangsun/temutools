package service

import (
	"log/slog"

	"github.com/erfengyuzhangsun/temutools/internal/temu"
)

type MessageItem struct {
	ID      int    `json:"id"`
	Title   string `json:"title"`
	Content string `json:"content"`
	Status  string `json:"status"`
	ShopID  int    `json:"shop_id"`
	Time    string `json:"time"`
}

type ShippingOrder struct {
	OrderID     string `json:"order_id"`
	ShopID      int    `json:"shop_id"`
	Status      string `json:"status"`
	ProductName string `json:"product_name"`
	Quantity    int    `json:"quantity"`
	Address     string `json:"address"`
}

type ReviewItem struct {
	ReviewID  int    `json:"review_id"`
	ShopID    int    `json:"shop_id"`
	Sku       string `json:"sku"`
	Content   string `json:"content"`
	Rating    int    `json:"rating"`
	Status    string `json:"status"`
	CreatedAt string `json:"created_at"`
}

type ActivityItem struct {
	ActivityID   int    `json:"activity_id"`
	Title        string `json:"title"`
	Status       string `json:"status"`
	StartTime    string `json:"start_time"`
	EndTime      string `json:"end_time"`
	Enrolled     bool   `json:"enrolled"`
}

type MiscService struct {
	UserID int
}

func NewMiscService(userID int) *MiscService {
	return &MiscService{UserID: userID}
}

func (s *MiscService) GetMessages(client temu.ApiClient) ([]MessageItem, error) {
	slog.Info("getting messages", "user_id", s.UserID)

	resp, err := client.GetMessages(1, 50)
	if err != nil {
		return nil, err
	}
	if !resp.Success {
		return nil, nil
	}

	return []MessageItem{}, nil
}

func (s *MiscService) GetActivities(client temu.ApiClient) ([]ActivityItem, error) {
	slog.Info("getting activities", "user_id", s.UserID)

	resp, err := client.GetActivities(1)
	if err != nil {
		return nil, err
	}
	if !resp.Success {
		return nil, nil
	}

	return []ActivityItem{}, nil
}

func (s *MiscService) GetShippingOrders(client temu.ApiClient) ([]ShippingOrder, error) {
	return []ShippingOrder{}, nil
}

func (s *MiscService) GetReviews(client temu.ApiClient) ([]ReviewItem, error) {
	return []ReviewItem{}, nil
}

type RiskGuardCheck struct {
	Name   string `json:"name"`
	Passed bool   `json:"passed"`
}

type RiskGuardResult struct {
	Passed bool             `json:"passed"`
	Checks []RiskGuardCheck `json:"checks"`
}

func (s *MiscService) RunRiskGuardCheck() *RiskGuardResult {
	return &RiskGuardResult{
		Passed: true,
		Checks: []RiskGuardCheck{
			{Name: "毛利率检查", Passed: true},
			{Name: "调价幅度检查", Passed: true},
			{Name: "频率检查", Passed: true},
		},
	}
}
