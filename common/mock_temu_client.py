import json
import logging
import random
import time
from datetime import datetime, timedelta
from typing import Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

API_REGION_MAP = {
    "cn": "https://openapi.kuajingmaihuo.com",
    "pa": "https://openapi-b-partner.temu.com",
    "global": "https://openapi-b-global.temu.com",
    "us": "https://openapi-b-us.temu.com",
    "eu": "https://openapi-b-eu.temu.com",
}


@dataclass
class MockApiResponse:
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    status_code: int = 200


class MockTemuApiClient:
    _instance = None
    _mock_data_generated = False

    MOCK_SKUS = [
        "SKU_BL001", "SKU_3C001", "SKU_CZ001", "SKU_MZ001", "SKU_WJ001",
        "SKU_BL002", "SKU_3C002", "SKU_CZ002", "SKU_SP001", "SKU_WJ002",
        "SKU_BL003", "SKU_3C003", "SKU_MZ002", "SKU_CZ003", "SKU_WJ003",
    ]

    MOCK_PRODUCT_NAMES = [
        "北欧风简约收纳盒套装", "无线蓝牙耳机Pro版", "夏季轻薄透气运动T恤",
        "玻尿酸保湿精华液30ml", "儿童益智积木玩具100片", "多功能厨房置物架",
        "智能手表运动版", "韩版宽松休闲卫衣", "有机坚果礼盒500g", "婴儿早教布书套装",
        "ins风桌面收纳架", "Type-C快充数据线3条装", "烟酰胺美白面膜10片",
        "复古高腰牛仔裤女", "乐高式拼装汽车模型",
    ]

    MOCK_CATEGORIES = [
        "家居百货", "3C数码", "服装鞋包", "美妆个护", "玩具母婴",
    ]

    def __init__(self, shop_id: int, api_key: str = "", api_secret: str = ""):
        self.shop_id = shop_id
        self.api_key = api_key or "MOCK_APP_KEY"
        self.api_secret = api_secret or "MOCK_APP_SECRET"
        self.access_token = "MOCK_ACCESS_TOKEN"
        import os
        region = os.environ.get("TEMU_API_REGION", "global")
        self.base_url = API_REGION_MAP.get(region, API_REGION_MAP["global"])
        self._generate_mock_data()

    @classmethod
    def _generate_mock_data(cls):
        if cls._mock_data_generated:
            return
        cls._mock_data_generated = True

    def __hash__(self):
        return hash(("MockTemuApiClient", self.shop_id))

    def __eq__(self, other):
        if isinstance(other, MockTemuApiClient):
            return self.shop_id == other.shop_id
        return NotImplemented

    async def close(self):
        pass

    def _make_success(self, data: Any) -> MockApiResponse:
        return MockApiResponse(success=True, data=data, status_code=200)

    def _mock_orders_page(self, page: int, page_size: int) -> list:
        orders = []
        base_time = datetime.now() - timedelta(days=30)
        for i in range(page_size):
            idx = (page - 1) * page_size + i
            if idx >= 150:
                break
            sku_idx = idx % len(self.MOCK_SKUS)
            unit_price = round(random.uniform(15.0, 300.0), 2)
            quantity = random.randint(1, 5)
            orders.append({
                "parentOrderSn": f"PO-211-{800000000 + idx:012d}",
                "subOrderSn": f"SO-211-{900000000 + idx:012d}",
                "sku": self.MOCK_SKUS[sku_idx],
                "goodsName": self.MOCK_PRODUCT_NAMES[sku_idx],
                "quantity": quantity,
                "unitPrice": unit_price,
                "totalPrice": round(unit_price * quantity, 2),
                "settlementPrice": round(unit_price * 0.55, 2),
                "orderStatus": random.choice(["SHIPPED", "DELIVERED", "CONFIRMED"]),
                "orderTime": (base_time + timedelta(hours=idx)).isoformat(),
                "shippingTime": (base_time + timedelta(hours=idx + 24)).isoformat(),
                "categoryName": self.MOCK_CATEGORIES[sku_idx % 5],
            })
        return orders

    async def get_orders(self, page: int = 1, page_size: int = 100, **kwargs) -> MockApiResponse:
        return self._make_success({
            "success": True,
            "result": {
                "list": self._mock_orders_page(page, page_size),
                "total": 150,
                "pageNumber": page,
                "pageSize": page_size,
            },
        })

    async def get_order_detail(self, parent_order_sn: str) -> MockApiResponse:
        sku_idx = random.randint(0, len(self.MOCK_SKUS) - 1)
        return self._make_success({
            "success": True,
            "result": {
                "parentOrderSn": parent_order_sn,
                "subOrderList": [{
                    "subOrderSn": f"SO-{parent_order_sn}",
                    "sku": self.MOCK_SKUS[sku_idx],
                    "goodsName": self.MOCK_PRODUCT_NAMES[sku_idx],
                    "quantity": random.randint(1, 3),
                    "unitPrice": round(random.uniform(20.0, 200.0), 2),
                    "orderStatus": "CONFIRMED",
                }],
                "shippingAddress": {
                    "name": "Test User",
                    "phone": "138****8888",
                    "country": "US",
                    "state": "California",
                    "city": "Los Angeles",
                    "streetAddress": "123 Main St",
                    "zipCode": "90001",
                },
            },
        })

    async def get_inventory(self, sku_codes: list = None) -> MockApiResponse:
        if not sku_codes:
            sku_codes = self.MOCK_SKUS
        items = []
        for sku in sku_codes:
            items.append({
                "skuCode": sku,
                "skuId": f"SKUID_{sku}",
                "quantity": random.randint(50, 5000),
                "reservedQuantity": random.randint(0, 200),
                "availableQuantity": random.randint(30, 4800),
                "warehouseCode": "WH-US-EAST",
            })
        return self._make_success({
            "success": True,
            "result": {
                "skuList": items,
                "total": len(items),
            },
        })

    async def get_pricing_notices(self, page: int = 1, page_size: int = 50) -> MockApiResponse:
        notices = []
        now = datetime.now()
        for i in range(min(page_size, 12)):
            sku_idx = (page * 10 + i) % len(self.MOCK_SKUS)
            supply_price = round(random.uniform(18.0, 160.0), 2)
            notices.append({
                "notice_id": f"PN{now.strftime('%Y%m%d')}{1000 + i:04d}",
                "sku": self.MOCK_SKUS[sku_idx],
                "goodsName": self.MOCK_PRODUCT_NAMES[sku_idx],
                "supply_price": supply_price,
                "original_price": round(supply_price * random.uniform(0.85, 1.15), 2),
                "expire_at": (now + timedelta(days=random.randint(1, 5))).isoformat(),
                "is_activity": random.random() < 0.2,
                "status": random.choice(["pending", "pending", "pending", "accepted", "rejected"]),
                "category_name": self.MOCK_CATEGORIES[sku_idx % 5],
            })
        return self._make_success({
            "success": True,
            "result": {
                "notices": notices,
                "total": 36,
                "page": page,
                "pageSize": page_size,
            },
        })

    async def accept_pricing(self, price_order_id: str) -> MockApiResponse:
        return self._make_success({
            "success": True,
            "result": {"priceOrderId": price_order_id, "status": "accepted"},
        })

    async def reject_pricing(self, price_order_id: str, reason: str = "") -> MockApiResponse:
        return self._make_success({
            "success": True,
            "result": {"priceOrderId": price_order_id, "status": "rejected", "reason": reason},
        })

    async def get_settlements(self, date_from: str, date_to: str, page: int = 1) -> MockApiResponse:
        items = []
        base_date = datetime.strptime(date_from, "%Y-%m-%d")
        for i in range(10):
            day = base_date + timedelta(days=i)
            items.append({
                "settlementId": f"SETTLE{day.strftime('%Y%m%d')}_{page}",
                "periodStart": day.isoformat(),
                "periodEnd": (day + timedelta(days=1)).isoformat(),
                "totalSales": round(random.uniform(500.0, 5000.0), 2),
                "totalCommission": round(random.uniform(50.0, 500.0), 2),
                "totalShipping": round(random.uniform(30.0, 200.0), 2),
                "netAmount": round(random.uniform(400.0, 4500.0), 2),
                "currency": "USD",
                "status": random.choice(["SETTLED", "PENDING"]),
            })
        return self._make_success({
            "success": True,
            "result": {
                "list": items,
                "total": 30,
                "pageNumber": page,
                "pageSize": 10,
            },
        })

    async def get_shop_metrics(self, date_from: str, date_to: str) -> MockApiResponse:
        return self._make_success({
            "success": True,
            "result": {
                "totalSales": round(random.uniform(10000.0, 50000.0), 2),
                "totalOrders": random.randint(100, 500),
                "avgOrderValue": round(random.uniform(25.0, 100.0), 2),
                "totalProducts": random.randint(50, 200),
                "activeProducts": random.randint(30, 150),
                "conversionRate": round(random.uniform(1.5, 5.0), 2),
                "returnRate": round(random.uniform(1.0, 8.0), 2),
                "rating": round(random.uniform(4.0, 5.0), 1),
            },
        })

    async def get_messages(self, page: int = 1, page_size: int = 50) -> MockApiResponse:
        msg_types = ["SYSTEM", "PRICING", "ORDER", "ACTIVITY", "RISK"]
        messages = []
        now = datetime.now()
        for i in range(min(page_size, 15)):
            msg_type = random.choice(msg_types)
            templates = {
                "SYSTEM": ["系统维护通知", "平台规则更新", "资质审核通过通知"],
                "PRICING": ["核价通知：{sku} 供货价调整", "活动商品核价提醒", "批量核价处理结果"],
                "ORDER": [f"新订单({now.strftime('%m%d')}-{1000+i})待处理", f"订单 PO-211-{800000000 + i:012d} 已发货"],
                "ACTIVITY": ["新品推广活动邀请", "限时促销报名通知", "秒杀活动审核结果"],
                "RISK": ["商品合规风险提醒", "店铺评分波动预警", "退货率异常通知"],
            }
            titles = templates[msg_type]
            title = random.choice(titles)
            if "{sku}" in title:
                title = title.replace("{sku}", self.MOCK_SKUS[i % len(self.MOCK_SKUS)])

            messages.append({
                "message_id": f"MSG{now.strftime('%Y%m%d')}{1000 + i:04d}",
                "type": msg_type,
                "title": title,
                "content": f"这是{title}的详细内容，请及时处理。",
                "is_read": random.random() < 0.3,
                "created_at": (now - timedelta(hours=random.randint(1, 72))).isoformat(),
                "priority": random.choice(["high", "medium", "low"]),
            })
        return self._make_success({
            "success": True,
            "result": {
                "messages": messages,
                "total": 45,
                "page": page,
                "pageSize": page_size,
                "unread_count": sum(1 for m in messages if not m["is_read"]),
            },
        })

    async def get_activities(self, page: int = 1) -> MockApiResponse:
        now = datetime.now()
        activities = []
        for i in range(5):
            activities.append({
                "activity_id": f"ACT{now.strftime('%Y%m%d')}{100 + i:03d}",
                "name": random.choice([
                    "618年中大促", "夏季清凉节", "新品首发扶持",
                    "限时秒杀", "满减优惠活动", "会员专享折扣",
                ]),
                "type": random.choice(["sale", "flash", "coupon", "new_product"]),
                "status": random.choice(["ongoing", "upcoming", "ended"]),
                "start_time": now.isoformat(),
                "end_time": (now + timedelta(days=7)).isoformat(),
                "description": "活动描述详情",
            })
        return self._make_success({
            "success": True,
            "result": {
                "activities": activities,
                "total": len(activities),
                "page": page,
                "pageSize": 20,
            },
        })

    async def get_access_token(self, code: str) -> MockApiResponse:
        return self._make_success({
            "success": True,
            "result": {
                "access_token": "MOCK_ACCESS_TOKEN_" + code[:8],
                "expires_in": 7776000,
                "scope": "all",
                "shop_id": str(self.shop_id),
            },
        })

    async def check_access_token(self) -> MockApiResponse:
        return self._make_success({
            "success": True,
            "result": {
                "access_token": self.access_token,
                "status": "valid",
                "expires_at": (datetime.now() + timedelta(days=89)).isoformat(),
                "scope": "all",
                "shop_id": str(self.shop_id),
            },
        })

    async def get_goods_list(self, page: int = 1, page_size: int = 10) -> MockApiResponse:
        goods = []
        for i in range(page_size):
            idx = (page - 1) * page_size + i
            if idx >= len(self.MOCK_SKUS):
                break
            goods.append({
                "goodsId": f"G{600000000 + idx:09d}",
                "goodsName": self.MOCK_PRODUCT_NAMES[idx],
                "skuCode": self.MOCK_SKUS[idx],
                "categoryName": self.MOCK_CATEGORIES[idx % 5],
                "supplyPrice": round(random.uniform(15.0, 160.0), 2),
                "salePrice": round(random.uniform(25.0, 300.0), 2),
                "stockQuantity": random.randint(100, 5000),
                "salesCount": random.randint(10, 2000),
                "onlineStatus": random.choice(["ONLINE", "OFFLINE"]),
                "imageUrl": f"https://img.example.com/goods/{idx}.jpg",
            })
        return self._make_success({
            "success": True,
            "result": {
                "goodsList": goods,
                "total": len(self.MOCK_SKUS),
                "page": page,
                "pageSize": page_size,
            },
        })

    async def get_order_shipping_info(self, parent_order_sn: str) -> MockApiResponse:
        return self._make_success({
            "success": True,
            "result": {
                "parentOrderSn": parent_order_sn,
                "receiptName": "Test User",
                "mobile": "138****8888",
                "regionName1": "California",
                "regionName2": "Los Angeles",
                "addressLine1": "123 Main St",
                "postCode": "90001",
                "country": "US",
            },
        })

    async def get_order_amount(self, parent_order_sn: str) -> MockApiResponse:
        return self._make_success({
            "success": True,
            "result": {
                "parentOrderSn": parent_order_sn,
                "totalAmount": round(random.uniform(50.0, 500.0), 2),
                "supplyPriceAmount": round(random.uniform(30.0, 300.0), 2),
                "shippingFee": round(random.uniform(5.0, 30.0), 2),
                "currency": "USD",
            },
        })

    async def get_combined_shipment_list(self, page: int = 1, page_size: int = 10) -> MockApiResponse:
        groups = []
        for i in range(min(page_size, 5)):
            groups.append({
                "combineGroupId": f"CG{datetime.now().strftime('%Y%m%d')}{100 + i:03d}",
                "parentOrderSnList": [f"PO-211-{800000000 + i:012d}"],
                "createTime": datetime.now().isoformat(),
            })
        return self._make_success({
            "success": True,
            "result": {
                "combineGroupList": groups,
                "total": len(groups),
                "pageNumber": page,
                "pageSize": page_size,
            },
        })

    async def get_sku_price_list(self, sku_codes: list = None) -> MockApiResponse:
        if not sku_codes:
            sku_codes = self.MOCK_SKUS
        items = []
        for sku in sku_codes:
            items.append({
                "skuCode": sku,
                "supplyPrice": round(random.uniform(15.0, 160.0), 2),
                "salePrice": round(random.uniform(25.0, 300.0), 2),
                "currency": "USD",
            })
        return self._make_success({
            "success": True,
            "result": {
                "skuPriceList": items,
                "total": len(items),
            },
        })

    async def update_stock(self, goods_id: str, sku_stock_list: list) -> MockApiResponse:
        return self._make_success({
            "success": True,
            "result": {
                "goodsId": goods_id,
                "operateResult": True,
                "skuStockEditStatusInfoList": [
                    {"stockEditStatus": True, "skuId": item.get("skuId", "")}
                    for item in sku_stock_list
                ],
            },
        })

    async def negotiate_pricing(self, price_order_id: str, price: float, reason: str = "") -> MockApiResponse:
        return self._make_success({
            "success": True,
            "result": {
                "priceOrderId": price_order_id,
                "price": price,
                "status": "negotiated",
                "reason": reason,
            },
        })

    async def set_sale_status(self, goods_id: str, status: str) -> MockApiResponse:
        return self._make_success({
            "success": True,
            "result": {
                "goodsId": goods_id,
                "status": status,
                "result": True,
            },
        })

    async def get_freight_templates(self) -> MockApiResponse:
        return self._make_success({
            "success": True,
            "result": {
                "templateList": [
                    {"templateId": "FT001", "name": "标准运费模板", "type": "standard"},
                    {"templateId": "FT002", "name": "免运费模板", "type": "free"},
                ],
                "total": 2,
            },
        })

    async def get_compliance_goods_list(self, page: int = 1, page_size: int = 10) -> MockApiResponse:
        items = []
        for i in range(min(page_size, 5)):
            idx = (page - 1) * page_size + i
            items.append({
                "goodsId": f"G{600000000 + idx:09d}",
                "goodsName": self.MOCK_PRODUCT_NAMES[idx % len(self.MOCK_PRODUCT_NAMES)],
                "complianceStatus": "passed",
                "complianceType": "CE",
            })
        return self._make_success({
            "success": True,
            "result": {
                "goodsList": items,
                "total": 15,
                "page": page,
                "pageSize": page_size,
            },
        })

    async def get_aftersales_list(self, page: int = 1, page_size: int = 10) -> MockApiResponse:
        items = []
        for i in range(min(page_size, 5)):
            items.append({
                "afterSaleId": f"AS{datetime.now().strftime('%Y%m%d')}{100 + i:03d}",
                "parentOrderSn": f"PO-211-{800000000 + i:012d}",
                "status": random.choice(["pending", "approved", "completed"]),
                "type": random.choice(["return", "refund"]),
                "amount": round(random.uniform(10.0, 100.0), 2),
                "createdAt": datetime.now().isoformat(),
            })
        return self._make_success({
            "success": True,
            "result": {
                "list": items,
                "total": 15,
                "page": page,
                "pageSize": page_size,
            },
        })
