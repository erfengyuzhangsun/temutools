package service

import (
	"fmt"
	"log/slog"

	"github.com/erfengyuzhangsun/temutools/internal/temu"
)

type LogisticsCompany struct {
	ID   string `json:"id"`
	Name string `json:"name"`
}

type ShipmentResult struct {
	ShipmentID string `json:"shipment_id"`
	OrderSn    string `json:"order_sn"`
	Status     string `json:"status"`
	TrackingNo string `json:"tracking_no"`
}

type DocumentResult struct {
	ShipmentID  string `json:"shipment_id"`
	LabelURL    string `json:"label_url"`
	LabelBase64 string `json:"label_base64,omitempty"`
}

type ShipmentStatusResult struct {
	ShipmentID  string `json:"shipment_id"`
	Status      string `json:"status"`
	TrackingNo  string `json:"tracking_no"`
	LogisticsID string `json:"logistics_id"`
}

type Warehouse struct {
	WarehouseID string `json:"warehouse_id"`
	Name        string `json:"name"`
	Region      string `json:"region"`
}

type ShippingService struct {
	LogisticsID string `json:"logistics_id"`
	Name        string `json:"name"`
	ServiceType string `json:"service_type"`
}

type LogisticsService struct {
	UserID int
}

func NewLogisticsService(userID int) *LogisticsService {
	return &LogisticsService{UserID: userID}
}

func (s *LogisticsService) GetCompanies(client temu.ApiClient) ([]LogisticsCompany, error) {
	slog.Info("fetching logistics companies", "user_id", s.UserID)

	resp, err := client.GetLogisticsCompanies()
	if err != nil {
		return nil, fmt.Errorf("获取物流公司列表失败: %w", err)
	}
	if !resp.Success {
		return nil, nil
	}

	var companies []LogisticsCompany
	for _, c := range extractList(resp, "companies") {
		if id, ok := c["id"].(string); ok {
			name, _ := c["name"].(string)
			companies = append(companies, LogisticsCompany{ID: id, Name: name})
		}
	}
	if companies == nil {
		companies = []LogisticsCompany{}
	}
	return companies, nil
}

func (s *LogisticsService) CreateShipment(client temu.ApiClient, orderSn, logisticsID, trackingNo string) (*ShipmentResult, error) {
	slog.Info("creating shipment", "user_id", s.UserID, "order_sn", orderSn)

	resp, err := client.CreateLogisticsShipment(orderSn, logisticsID, trackingNo)
	if err != nil {
		return nil, fmt.Errorf("创建发货失败: %w", err)
	}
	if !resp.Success {
		return nil, fmt.Errorf("创建发货失败: %s", resp.Error)
	}

	result := &ShipmentResult{
		OrderSn:    orderSn,
		TrackingNo: trackingNo,
	}
	for _, item := range extractList(resp, "") {
		if id, ok := item["shipmentId"].(string); ok {
			result.ShipmentID = id
		}
		if status, ok := item["status"].(string); ok {
			result.Status = status
		}
	}

	return result, nil
}

func (s *LogisticsService) ConfirmShipment(client temu.ApiClient, shipmentID string) error {
	slog.Info("confirming shipment", "user_id", s.UserID, "shipment_id", shipmentID)

	resp, err := client.ConfirmLogisticsShipment(shipmentID)
	if err != nil {
		return fmt.Errorf("确认发货失败: %w", err)
	}
	if !resp.Success {
		return fmt.Errorf("确认发货失败: %s", resp.Error)
	}

	return nil
}

func (s *LogisticsService) GetDocument(client temu.ApiClient, shipmentID string) (*DocumentResult, error) {
	slog.Info("getting shipment document", "user_id", s.UserID, "shipment_id", shipmentID)

	resp, err := client.GetLogisticsShipmentDocument(shipmentID)
	if err != nil {
		return nil, fmt.Errorf("获取面单失败: %w", err)
	}
	if !resp.Success {
		return nil, fmt.Errorf("获取面单失败: %s", resp.Error)
	}

	result := &DocumentResult{ShipmentID: shipmentID}
	for _, item := range extractList(resp, "") {
		if url, ok := item["labelUrl"].(string); ok {
			result.LabelURL = url
		}
		if b64, ok := item["labelBase64"].(string); ok {
			result.LabelBase64 = b64
		}
	}
	return result, nil
}

func (s *LogisticsService) GetShipmentResult(client temu.ApiClient, shipmentID string) (*ShipmentStatusResult, error) {
	slog.Info("checking shipment result", "user_id", s.UserID, "shipment_id", shipmentID)

	resp, err := client.GetLogisticsShipmentResult(shipmentID)
	if err != nil {
		return nil, fmt.Errorf("查询发货结果失败: %w", err)
	}
	if !resp.Success {
		return nil, fmt.Errorf("查询发货结果失败: %s", resp.Error)
	}

	result := &ShipmentStatusResult{ShipmentID: shipmentID}
	for _, item := range extractList(resp, "") {
		if status, ok := item["status"].(string); ok {
			result.Status = status
		}
		if trackingNo, ok := item["trackingNo"].(string); ok {
			result.TrackingNo = trackingNo
		}
		if logisticsID, ok := item["logisticsId"].(string); ok {
			result.LogisticsID = logisticsID
		}
	}
	return result, nil
}

func (s *LogisticsService) GetWarehouses(client temu.ApiClient) ([]Warehouse, error) {
	slog.Info("fetching warehouses", "user_id", s.UserID)

	resp, err := client.GetLogisticsWarehouses()
	if err != nil {
		return nil, fmt.Errorf("获取仓库列表失败: %w", err)
	}
	if !resp.Success {
		return nil, nil
	}

	warehouses := make([]Warehouse, 0)
	for _, w := range extractList(resp, "warehouses") {
		wh := Warehouse{}
		if id, ok := w["warehouseId"].(string); ok {
			wh.WarehouseID = id
		}
		if name, ok := w["name"].(string); ok {
			wh.Name = name
		}
		if region, ok := w["region"].(string); ok {
			wh.Region = region
		}
		warehouses = append(warehouses, wh)
	}
	return warehouses, nil
}

func (s *LogisticsService) GetShippingServices(client temu.ApiClient, warehouseID string) ([]ShippingService, error) {
	slog.Info("fetching shipping services", "user_id", s.UserID, "warehouse_id", warehouseID)

	resp, err := client.GetLogisticsShippingServices(warehouseID)
	if err != nil {
		return nil, fmt.Errorf("获取物流服务列表失败: %w", err)
	}
	if !resp.Success {
		return nil, nil
	}

	services := make([]ShippingService, 0)
	for _, svc := range extractList(resp, "services") {
		s := ShippingService{}
		if id, ok := svc["logisticsId"].(string); ok {
			s.LogisticsID = id
		}
		if name, ok := svc["name"].(string); ok {
			s.Name = name
		}
		if st, ok := svc["serviceType"].(string); ok {
			s.ServiceType = st
		}
		services = append(services, s)
	}
	return services, nil
}

func extractList(resp *temu.ApiResponse, key string) []map[string]interface{} {
	data := resp.Data
	if len(data) == 0 {
		data = resp.Result
	}
	if len(data) == 0 {
		return nil
	}

	var root map[string]interface{}
	if err := parseJSON(data, &root); err != nil {
		return nil
	}

	if key != "" {
		if list, ok := root[key].([]interface{}); ok {
			result := make([]map[string]interface{}, 0)
			for _, item := range list {
				if m, ok := item.(map[string]interface{}); ok {
					result = append(result, m)
				}
			}
			return result
		}
	}

	for _, v := range root {
		if list, ok := v.([]interface{}); ok {
			result := make([]map[string]interface{}, 0)
			for _, item := range list {
				if m, ok := item.(map[string]interface{}); ok {
					result = append(result, m)
				}
			}
			return result
		}
	}

	return nil
}
