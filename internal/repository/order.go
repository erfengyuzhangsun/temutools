package repository

import (
	"fmt"

	"github.com/erfengyuzhangsun/temutools/internal/models"
)

func CreateOrder(order *models.Order) error {
	db := GetDB()
	if db == nil {
		return fmt.Errorf("database not initialized")
	}
	if err := db.Create(order).Error; err != nil {
		return fmt.Errorf("create order: %w", err)
	}
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
