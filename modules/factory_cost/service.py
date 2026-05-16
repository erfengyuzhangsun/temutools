import json
import logging
import os
import base64
from datetime import datetime
from typing import List, Optional
from modules.factory_cost.schemas import ProductInfo, PricingAdvice, ExportData
from modules.factory_cost.config import MODULE_CONFIG

logger = logging.getLogger(__name__)


class FactoryCostService:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self._ensure_tables()

    @staticmethod
    def _ensure_tables():
        try:
            from db import get_connection, DB_MODE
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS temu_factory_products (
                    product_id INTEGER AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    product_name VARCHAR(255) NOT NULL,
                    sku_code VARCHAR(100) NOT NULL,
                    category_name VARCHAR(100) DEFAULT '',
                    material_cost DECIMAL(10,2) DEFAULT 0.00,
                    labor_cost DECIMAL(10,2) DEFAULT 0.00,
                    packaging_cost DECIMAL(10,2) DEFAULT 0.00,
                    shipping_cost DECIMAL(10,2) DEFAULT 0.00,
                    other_cost DECIMAL(10,2) DEFAULT 0.00,
                    total_cost DECIMAL(10,2) DEFAULT 0.00,
                    expected_profit_margin DECIMAL(5,2) DEFAULT 20.00,
                    suggested_supply_price DECIMAL(10,2) DEFAULT 0.00,
                    product_images TEXT DEFAULT '',
                    product_description TEXT DEFAULT '',
                    is_full_commission TINYINT(1) DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY uk_user_sku (user_id, sku_code)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.close()
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"确保工厂成本表存在时出错: {e}")

    def save_product(self, product: ProductInfo) -> int:
        from db import execute_query
        total_cost = round(
            product.material_cost + product.labor_cost
            + product.packaging_cost + product.shipping_cost
            + product.other_cost, 2
        )
        suggested_price = round(
            total_cost * (1 + product.expected_profit_margin / 100), 2
        )
        existing = execute_query(
            "SELECT product_id FROM temu_factory_products WHERE user_id=? AND sku_code=?",
            (self.user_id, product.sku_code), fetch=True,
        )
        if existing:
            execute_query("""
                UPDATE temu_factory_products SET
                 product_name=?, category_name=?, material_cost=?, labor_cost=?,
                 packaging_cost=?, shipping_cost=?, other_cost=?, total_cost=?,
                 expected_profit_margin=?, suggested_supply_price=?,
                 product_images=?, product_description=?, is_full_commission=?
                WHERE product_id=?
            """, (
                product.product_name, product.category_name,
                product.material_cost, product.labor_cost,
                product.packaging_cost, product.shipping_cost, product.other_cost,
                total_cost, product.expected_profit_margin, suggested_price,
                product.product_images, product.product_description,
                1 if product.is_full_commission else 0,
                existing[0]["product_id"],
            ))
            return existing[0]["product_id"]
        else:
            execute_query("""
                INSERT INTO temu_factory_products
                (user_id, product_name, sku_code, category_name,
                 material_cost, labor_cost, packaging_cost, shipping_cost, other_cost,
                 total_cost, expected_profit_margin, suggested_supply_price,
                 product_images, product_description, is_full_commission)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.user_id, product.product_name, product.sku_code,
                product.category_name, product.material_cost, product.labor_cost,
                product.packaging_cost, product.shipping_cost, product.other_cost,
                total_cost, product.expected_profit_margin, suggested_price,
                product.product_images, product.product_description,
                1 if product.is_full_commission else 0,
            ))
            rows = execute_query(
                "SELECT product_id FROM temu_factory_products WHERE user_id=? AND sku_code=?",
                (self.user_id, product.sku_code), fetch=True,
            )
            return rows[0]["product_id"] if rows else 0

    def get_products(self) -> List[ProductInfo]:
        from db import execute_query
        rows = execute_query(
            "SELECT * FROM temu_factory_products WHERE user_id=? ORDER BY updated_at DESC",
            (self.user_id,), fetch=True,
        ) or []
        return [self._row_to_product(r) for r in rows]

    def get_product(self, product_id: int) -> Optional[ProductInfo]:
        from db import execute_query
        rows = execute_query(
            "SELECT * FROM temu_factory_products WHERE product_id=? AND user_id=?",
            (product_id, self.user_id), fetch=True,
        )
        if not rows:
            return None
        return self._row_to_product(rows[0])

    def get_product_by_sku(self, sku_code: str) -> Optional[ProductInfo]:
        from db import execute_query
        rows = execute_query(
            "SELECT * FROM temu_factory_products WHERE sku_code=? AND user_id=?",
            (sku_code, self.user_id), fetch=True,
        )
        if not rows:
            return None
        return self._row_to_product(rows[0])

    def delete_product(self, product_id: int) -> bool:
        from db import execute_query
        execute_query(
            "DELETE FROM temu_factory_products WHERE product_id=? AND user_id=?",
            (product_id, self.user_id),
        )
        return True

    def _row_to_product(self, row: dict) -> ProductInfo:
        return ProductInfo(
            product_id=row.get("product_id", 0),
            user_id=row.get("user_id", self.user_id),
            product_name=row.get("product_name", ""),
            sku_code=row.get("sku_code", ""),
            category_name=row.get("category_name", ""),
            material_cost=float(row.get("material_cost", 0)),
            labor_cost=float(row.get("labor_cost", 0)),
            packaging_cost=float(row.get("packaging_cost", 0)),
            shipping_cost=float(row.get("shipping_cost", 0)),
            other_cost=float(row.get("other_cost", 0)),
            total_cost=float(row.get("total_cost", 0)),
            expected_profit_margin=float(row.get("expected_profit_margin", 20)),
            suggested_supply_price=float(row.get("suggested_supply_price", 0)),
            product_images=row.get("product_images", ""),
            product_description=row.get("product_description", ""),
            is_full_commission=bool(row.get("is_full_commission", True)),
            created_at=str(row.get("created_at", "")),
            updated_at=str(row.get("updated_at", "")),
        )

    def calculate_pricing_advice(self, product: ProductInfo) -> PricingAdvice:
        total_cost = round(
            product.material_cost + product.labor_cost
            + product.packaging_cost + product.shipping_cost
            + product.other_cost, 2
        )
        min_margin_setting = (
            MODULE_CONFIG["full_commission_min_margin"]["default"]
            if product.is_full_commission
            else MODULE_CONFIG["half_commission_min_margin"]["default"]
        )
        min_margin = max(min_margin_setting, product.expected_profit_margin * 0.7)
        safe_floor_ratio = MODULE_CONFIG["safe_price_floor_ratio"]["default"]
        safe_ceil_ratio = MODULE_CONFIG["safe_price_ceiling_ratio"]["default"]

        suggested_price = round(total_cost * (1 + product.expected_profit_margin / 100), 2)
        min_safe_price = round(suggested_price * safe_floor_ratio, 2)
        max_safe_price = round(suggested_price * safe_ceil_ratio, 2)
        actual_margin = round(
            ((suggested_price - total_cost) / total_cost) * 100 if total_cost > 0 else 0, 1
        )

        platform_low = round(suggested_price * 0.9, 2)
        platform_high = round(suggested_price * 1.2, 2)

        risk_parts = []
        if actual_margin < min_margin:
            risk_parts.append(f"毛利率{actual_margin}%低于安全线{min_margin}%，易触发二次核价")
        if suggested_price < total_cost * 1.05:
            risk_parts.append(f"供货价过低，利润空间不足")
        if actual_margin > 50:
            risk_parts.append(f"毛利率过高({actual_margin}%)，可能触发平台调价机制")

        if not risk_parts:
            risk_level = "safe"
            advice = f"建议供货价 ¥{suggested_price}，安全范围 ¥{min_safe_price}~¥{max_safe_price}，预计毛利率{actual_margin}%"
        else:
            risk_level = "risky"
            advice = f"建议供货价 ¥{suggested_price}，风险提示：{'；'.join(risk_parts)}"

        return PricingAdvice(
            product_id=product.product_id,
            sku_code=product.sku_code,
            product_name=product.product_name,
            total_cost=total_cost,
            min_safe_price=min_safe_price,
            max_safe_price=max_safe_price,
            suggested_price=suggested_price,
            profit_margin=actual_margin,
            platform_price_range_low=platform_low,
            platform_price_range_high=platform_high,
            risk_level=risk_level,
            advice_detail=advice,
        )

    def batch_calculate_pricing(self) -> List[PricingAdvice]:
        products = self.get_products()
        return [self.calculate_pricing_advice(p) for p in products]

    def export_pricing_data(self) -> List[ExportData]:
        advices = self.batch_calculate_pricing()
        result = []
        for adv in advices:
            product = self.get_product(adv.product_id)
            result.append(ExportData(
                sku_code=adv.sku_code,
                product_name=adv.product_name,
                cost_price=product.total_cost if product else 0,
                suggested_supply_price=adv.suggested_price,
                min_safe_price=adv.min_safe_price,
                max_safe_price=adv.max_safe_price,
                expected_margin=product.expected_profit_margin if product else 0,
                risk_level=adv.risk_level,
            ))
        return result

    def save_image(self, product_id: int, image_data: str, index: int) -> str:
        upload_dir = f"uploads/factory_cost/user_{self.user_id}"
        os.makedirs(upload_dir, exist_ok=True)
        ext = "jpg"
        filename = f"{product_id}_{index}.{ext}"
        filepath = os.path.join(upload_dir, filename)
        try:
            if "," in image_data:
                image_data = image_data.split(",")[1]
            img_bytes = base64.b64decode(image_data)
            with open(filepath, "wb") as f:
                f.write(img_bytes)
            return filepath
        except Exception as e:
            logger.error(f"保存图片失败: {e}")
            return ""
