package repository

import (
	"fmt"
	"log/slog"

	"github.com/erfengyuzhangsun/temutools/internal/crypto"
	"github.com/erfengyuzhangsun/temutools/internal/models"
)

func encryptOrderPII(order *models.Order) {
	encName, _ := crypto.EncryptPII(order.ContactName)
	encPhone, _ := crypto.EncryptPII(order.Phone)
	encWechat, _ := crypto.EncryptPII(order.Wechat)
	order.ContactName = encName
	order.Phone = encPhone
	order.Wechat = encWechat
}

func decryptOrderPII(order *models.Order) {
	if name, err := crypto.DecryptPII(order.ContactName); err == nil {
		order.ContactName = name
	} else {
		slog.Debug("order contact_name not encrypted, using raw", "order_id", order.OrderID)
	}
	if phone, err := crypto.DecryptPII(order.Phone); err == nil {
		order.Phone = phone
	} else {
		slog.Debug("order phone not encrypted, using raw", "order_id", order.OrderID)
	}
	if wechat, err := crypto.DecryptPII(order.Wechat); err == nil {
		order.Wechat = wechat
	} else {
		slog.Debug("order wechat not encrypted, using raw", "order_id", order.OrderID)
	}
}

func CreateOrder(order *models.Order) error {
	db := GetDB()
	if db == nil {
		return fmt.Errorf("database not initialized")
	}
	encryptOrderPII(order)
	if err := db.Create(order).Error; err != nil {
		return fmt.Errorf("create order: %w", err)
	}
	decryptOrderPII(order)
	return nil
}

func ListOrders() ([]models.Order, error) {
	db := GetDB()
	if db == nil {
		return nil, fmt.Errorf("database not initialized")
	}
	var orders []models.Order
	result := db.Order("created_at DESC").Find(&orders)
	if result.Error != nil {
		return nil, fmt.Errorf("list orders: %w", result.Error)
	}
	for i := range orders {
		decryptOrderPII(&orders[i])
	}
	return orders, nil
}

func MarkOrderCompleted(orderID int) error {
	db := GetDB()
	if db == nil {
		return fmt.Errorf("database not initialized")
	}
	result := db.Model(&models.Order{}).Where("order_id = ?", orderID).
		Update("status", "completed")
	if result.Error != nil {
		return fmt.Errorf("mark order completed: %w", result.Error)
	}
	if result.RowsAffected == 0 {
		return fmt.Errorf("order not found")
	}
	return nil
}

func DeleteOrder(orderID int) error {
	db := GetDB()
	if db == nil {
		return fmt.Errorf("database not initialized")
	}
	result := db.Delete(&models.Order{}, orderID)
	if result.Error != nil {
		return fmt.Errorf("delete order: %w", result.Error)
	}
	if result.RowsAffected == 0 {
		return fmt.Errorf("order not found")
	}
	return nil
}
