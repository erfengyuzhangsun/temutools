package temu

import (
	"fmt"
	"math/rand"
	"sync"
	"time"
)

type MockClient struct {
	shopID int
	mu     sync.RWMutex
}

var mockSkus = []string{
	"SKU_BL001", "SKU_3C001", "SKU_CZ001", "SKU_MZ001", "SKU_WJ001",
	"SKU_BL002", "SKU_3C002", "SKU_CZ002", "SKU_SP001", "SKU_WJ002",
	"SKU_BL003", "SKU_3C003", "SKU_MZ002", "SKU_CZ003", "SKU_WJ003",
}

var mockProductNames = []string{
	"北欧风简约收纳盒套装", "无线蓝牙耳机Pro版", "夏季轻薄透气运动T恤",
	"玻尿酸保湿精华液30ml", "儿童益智积木玩具100片", "多功能厨房置物架",
	"智能手表运动版", "韩版宽松休闲卫衣", "有机坚果礼盒500g", "婴儿早教布书套装",
	"ins风桌面收纳架", "Type-C快充数据线3条装", "烟酰胺美白面膜10片",
	"复古高腰牛仔裤女", "乐高式拼装汽车模型",
}

var mockCategories = []string{
	"家居百货", "3C数码", "服装鞋包", "美妆个护", "玩具母婴",
}

func NewMockClient(shopID int) *MockClient {
	return &MockClient{
		shopID: shopID,
	}
}

func (m *MockClient) Close() error {
	return nil
}

func (m *MockClient) mockSuccess(data interface{}) *ApiResponse {
	return &ApiResponse{
		Success: true,
		Status:  200,
	}
}

func (m *MockClient) GetOrders(page, pageSize int, params map[string]string) (*ApiResponse, error) {
	orders := make([]map[string]interface{}, 0, pageSize)
	baseTime := time.Now().Add(-30 * 24 * time.Hour)
	for i := 0; i < pageSize; i++ {
		idx := (page-1)*pageSize + i
		if idx >= 150 {
			break
		}
		skuIdx := idx % len(mockSkus)
		unitPrice := 15.0 + rand.Float64()*285.0
		quantity := rand.Intn(5) + 1
		order := map[string]interface{}{
			"parentOrderSn":   fmt.Sprintf("PO-211-%012d", 800000000+idx),
			"subOrderSn":      fmt.Sprintf("SO-211-%012d", 900000000+idx),
			"sku":             mockSkus[skuIdx],
			"goodsName":       mockProductNames[skuIdx],
			"quantity":        quantity,
			"unitPrice":       unitPrice,
			"totalPrice":      unitPrice * float64(quantity),
			"settlementPrice": unitPrice * 0.55,
			"orderStatus":     []string{"SHIPPED", "DELIVERED", "CONFIRMED"}[rand.Intn(3)],
			"orderTime":       baseTime.Add(time.Duration(idx) * time.Hour).Format(time.RFC3339),
		}
		orders = append(orders, order)
	}
	return m.mockSuccess(map[string]interface{}{
		"orders": orders,
		"total":  150,
	}), nil
}

func (m *MockClient) GetOrderDetail(orderSn string) (*ApiResponse, error) {
	return m.mockSuccess(map[string]interface{}{
		"parentOrderSn":  orderSn,
		"orderStatus":    "CONFIRMED",
		"totalAmount":    299.00,
		"shippingStatus": "DELIVERED",
		"items": []map[string]interface{}{
			{"sku": "SKU_BL001", "goodsName": "北欧风简约收纳盒套装", "quantity": 2, "unitPrice": 49.90},
		},
	}), nil
}

func (m *MockClient) GetInventory(skuCodes []string) (*ApiResponse, error) {
	items := make([]map[string]interface{}, 0)
	for _, sku := range skuCodes {
		items = append(items, map[string]interface{}{
			"sku":          sku,
			"currentStock": rand.Intn(500) + 10,
			"warehouseStock": []map[string]interface{}{
				{"warehouse": "CN_WAREHOUSE", "stock": rand.Intn(300) + 5},
			},
			"lastUpdated": time.Now().Format(time.RFC3339),
		})
	}
	return m.mockSuccess(map[string]interface{}{
		"items": items,
	}), nil
}

func (m *MockClient) GetPricingNotices(page, pageSize int) (*ApiResponse, error) {
	notices := make([]map[string]interface{}, 0)
	for i := 0; i < 5; i++ {
		idx := (page-1)*5 + i
		if idx >= len(mockSkus) {
			break
		}
		costPrice := 10.0 + rand.Float64()*90.0
		supplyPrice := costPrice * (1.05 + rand.Float64()*0.25)
		notices = append(notices, map[string]interface{}{
			"notice_id":    fmt.Sprintf("N-%012d", idx+1),
			"sku":          mockSkus[idx],
			"supply_price": supplyPrice,
			"cost_price":   costPrice,
			"is_activity":  idx%3 == 0,
			"expire_at":    time.Now().Add(48 * time.Hour).Format(time.RFC3339),
		})
	}
	return m.mockSuccess(map[string]interface{}{
		"notices": notices,
	}), nil
}

func (m *MockClient) AcceptPricing(priceOrderID string) (*ApiResponse, error) {
	return m.mockSuccess(map[string]interface{}{
		"message": "核价已接受",
	}), nil
}

func (m *MockClient) RejectPricing(priceOrderID, reason string) (*ApiResponse, error) {
	return m.mockSuccess(map[string]interface{}{
		"message": "核价已拒绝",
	}), nil
}

func (m *MockClient) GetMessages(page, pageSize int) (*ApiResponse, error) {
	return nil, fmt.Errorf("消息列表API未在Temu开放平台公开接口中提供")
}

func (m *MockClient) GetActivities(page int) (*ApiResponse, error) {
	activities := make([]map[string]interface{}, 0)
	for i := 1; i <= 5; i++ {
		activities = append(activities, map[string]interface{}{
			"activity_id":   fmt.Sprintf("ACT_%d", i),
			"activity_name": []string{"夏季大促", "会员日特卖", "新品尝鲜", "限时秒杀", "满减活动"}[i-1],
			"start_time":    time.Now().Add(time.Duration(i) * 24 * time.Hour).Format(time.RFC3339),
			"end_time":      time.Now().Add(time.Duration(i+7) * 24 * time.Hour).Format(time.RFC3339),
			"status":        "UPCOMING",
		})
	}
	return m.mockSuccess(map[string]interface{}{
		"activities": activities,
	}), nil
}

func (m *MockClient) GetAccessToken(code string) (*ApiResponse, error) {
	return m.mockSuccess(map[string]interface{}{
		"accessToken": "MOCK_ACCESS_TOKEN_" + code,
		"expires_in":  7776000,
	}), nil
}

func (m *MockClient) CheckAccessToken() (*ApiResponse, error) {
	return m.mockSuccess(map[string]interface{}{
		"valid":   true,
		"scopes":  []string{"bg.order.*", "bg.goods.*"},
		"expires": time.Now().Add(90 * 24 * time.Hour).Unix(),
	}), nil
}

func (m *MockClient) GetGoodsList(page, pageSize int) (*ApiResponse, error) {
	goods := make([]map[string]interface{}, 0)
	for i := 0; i < pageSize; i++ {
		idx := (page-1)*pageSize + i
		if idx >= len(mockSkus) {
			break
		}
		goods = append(goods, map[string]interface{}{
			"goodsId":   fmt.Sprintf("G_%d", idx+1),
			"sku":       mockSkus[idx],
			"goodsName": mockProductNames[idx],
			"category":  mockCategories[idx%len(mockCategories)],
			"price":     29.9 + rand.Float64()*200.0,
			"stock":     rand.Intn(1000),
			"status":    "ONLINE",
		})
	}
	return m.mockSuccess(map[string]interface{}{
		"goods": goods,
		"total": len(mockSkus),
	}), nil
}

func (m *MockClient) GetOrderShippingInfo(orderSn string) (*ApiResponse, error) {
	return m.mockSuccess(map[string]interface{}{
		"shippingAddress": map[string]interface{}{
			"receiverName":  "张三",
			"receiverPhone": "138****1234",
			"province":      "广东省",
			"city":          "深圳市",
			"district":      "南山区",
			"detailAddress": "科技园南区A栋1001",
		},
		"shippingMethod": "STANDARD",
		"trackingNumber": "SF" + fmt.Sprintf("%012d", rand.Intn(999999999999)),
	}), nil
}

func (m *MockClient) GetOrderAmount(orderSn string) (*ApiResponse, error) {
	return m.mockSuccess(map[string]interface{}{
		"totalAmount":      299.00,
		"platformFee":      35.88,
		"settlementAmount": 263.12,
	}), nil
}

func (m *MockClient) GetCombinedShipmentList() (*ApiResponse, error) {
	return m.mockSuccess(map[string]interface{}{
		"combinedShips": []map[string]interface{}{},
	}), nil
}

func (m *MockClient) GetSkuPriceList(skuCodes []string) (*ApiResponse, error) {
	prices := make([]map[string]interface{}, 0)
	for _, sku := range skuCodes {
		prices = append(prices, map[string]interface{}{
			"sku":          sku,
			"currentPrice": 49.9 + rand.Float64()*150.0,
			"costPrice":    20.0 + rand.Float64()*50.0,
			"profitRate":   15.0 + rand.Float64()*30.0,
		})
	}
	return m.mockSuccess(map[string]interface{}{
		"prices": prices,
	}), nil
}

func (m *MockClient) UpdateStock(goodsID string, skuStockList []SkuStock) (*ApiResponse, error) {
	return m.mockSuccess(map[string]interface{}{
		"message": "库存更新成功",
	}), nil
}

func (m *MockClient) NegotiatePricing(priceOrderID, newPrice string) (*ApiResponse, error) {
	return m.mockSuccess(map[string]interface{}{
		"message": "核价协商已提交",
	}), nil
}

func (m *MockClient) SetSaleStatus(goodsID string, status int) (*ApiResponse, error) {
	return m.mockSuccess(map[string]interface{}{
		"message": "销售状态更新成功",
	}), nil
}

func (m *MockClient) GetFreightTemplates() (*ApiResponse, error) {
	return m.mockSuccess(map[string]interface{}{
		"templates": []map[string]interface{}{
			{"id": "FT_001", "name": "标准运费", "baseFee": 5.0, "perUnitFee": 2.0},
			{"id": "FT_002", "name": "免运费", "baseFee": 0, "perUnitFee": 0},
		},
	}), nil
}

func (m *MockClient) GetComplianceGoodsList(page, pageSize int) (*ApiResponse, error) {
	return m.mockSuccess(map[string]interface{}{
		"goods": []map[string]interface{}{},
		"total": 0,
	}), nil
}

func (m *MockClient) GetAftersalesList(page, pageSize int) (*ApiResponse, error) {
	items := make([]map[string]interface{}, 0)
	for i := 0; i < pageSize; i++ {
		idx := (page-1)*pageSize + i
		if idx >= 10 {
			break
		}
		statuses := []string{"PENDING", "APPROVED", "REJECTED", "COMPLETED"}
		items = append(items, map[string]interface{}{
			"aftersaleId": fmt.Sprintf("AS-%012d", 600000000+idx),
			"orderSn":     fmt.Sprintf("PO-%012d", 500000000+idx),
			"sku":         mockSkus[idx%len(mockSkus)],
			"goodsName":   mockProductNames[idx%len(mockProductNames)],
			"status":      statuses[idx%len(statuses)],
			"reason":      "商品与描述不符",
			"amount":      29.9 + float64(idx)*10,
			"createdAt":   time.Now().Add(-time.Duration(idx) * 24 * time.Hour).Format(time.RFC3339),
		})
	}
	return m.mockSuccess(map[string]interface{}{
		"aftersales": items,
		"total":      10,
	}), nil
}

func (m *MockClient) GetParentAftersalesList(page, pageSize int, statusGroup int, updateAtStart, updateAtEnd int64) (*ApiResponse, error) {
	items := make([]map[string]interface{}, 0)
	for i := 0; i < pageSize && i < 5; i++ {
		items = append(items, map[string]interface{}{
			"parentAfterSalesSn":     fmt.Sprintf("PO-076-%012d-D01", 300000000+i),
			"afterSalesStatusGroup":  statusGroup,
			"parentAfterSalesStatus": statusGroup,
			"parentOrderSn":          fmt.Sprintf("PO-076-%012d", 100000000+i),
			"afterSalesType":         2,
			"createAt":               time.Now().Add(-time.Duration(i+1) * 24 * time.Hour).Unix(),
			"updateAt":               time.Now().Add(-time.Duration(i) * 24 * time.Hour).Unix(),
		})
	}
	return m.mockSuccess(map[string]interface{}{
		"data":       items,
		"total":      len(items),
		"pageNumber": page,
	}), nil
}

func (m *MockClient) GetParentReturnOrder(parentAfterSalesSn string) (*ApiResponse, error) {
	return m.mockSuccess(map[string]interface{}{
		"parentAfterSalesSn": parentAfterSalesSn,
		"returnReason":       "商品与描述不符",
		"returnQuantity":     1,
		"returnAmount":       29.90,
		"returnStatus":       "REFUNDED",
		"returnType":         1,
		"createAt":           time.Now().Add(-24 * time.Hour).Unix(),
		"updateAt":           time.Now().Unix(),
	}), nil
}

func (m *MockClient) GetLogisticsCompanies() (*ApiResponse, error) {
	companies := []map[string]interface{}{
		{"id": "SF", "name": "顺丰速运"},
		{"id": "EMS", "name": "EMS"},
		{"id": "YTO", "name": "圆通速递"},
		{"id": "ZTO", "name": "中通快递"},
		{"id": "STO", "name": "申通快递"},
		{"id": "YUNDA", "name": "韵达快递"},
	}
	return m.mockSuccess(map[string]interface{}{
		"companies": companies,
	}), nil
}

func (m *MockClient) CreateLogisticsShipment(orderSn, logisticsID, trackingNo string) (*ApiResponse, error) {
	return m.mockSuccess(map[string]interface{}{
		"shipmentId": fmt.Sprintf("SHIP-%d", time.Now().Unix()),
		"orderSn":    orderSn,
		"status":     "created",
		"trackingNo": trackingNo,
	}), nil
}

func (m *MockClient) ConfirmLogisticsShipment(shipmentID string) (*ApiResponse, error) {
	return m.mockSuccess(map[string]interface{}{
		"shipmentId": shipmentID,
		"status":     "confirmed",
	}), nil
}

func (m *MockClient) GetLogisticsShipmentDocument(shipmentID string) (*ApiResponse, error) {
	return m.mockSuccess(map[string]interface{}{
		"shipmentId":  shipmentID,
		"labelUrl":    "https://example.com/label.pdf",
		"labelBase64": "JVBERi0xLjQK...",
	}), nil
}

func (m *MockClient) GetLogisticsShipmentResult(shipmentID string) (*ApiResponse, error) {
	return m.mockSuccess(map[string]interface{}{
		"shipmentId":  shipmentID,
		"status":      "shipped",
		"trackingNo":  "SF1234567890",
		"logisticsId": "SF",
	}), nil
}

func (m *MockClient) GetLogisticsWarehouses() (*ApiResponse, error) {
	warehouses := []map[string]interface{}{
		{"warehouseId": "WH_CN_001", "name": "中国深圳仓", "region": "CN"},
		{"warehouseId": "WH_US_001", "name": "美国洛杉矶仓", "region": "US"},
	}
	return m.mockSuccess(map[string]interface{}{
		"warehouses": warehouses,
	}), nil
}

func (m *MockClient) GetLogisticsShippingServices(warehouseID string) (*ApiResponse, error) {
	services := []map[string]interface{}{
		{"logisticsId": "SF", "name": "顺丰速运", "serviceType": "STANDARD"},
		{"logisticsId": "EMS", "name": "EMS", "serviceType": "STANDARD"},
	}
	return m.mockSuccess(map[string]interface{}{
		"services": services,
	}), nil
}
