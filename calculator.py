import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from config import (
    CATEGORY_COMMISSION_RATES,
    PERFORMANCE_FEES,
    PAYMENT_PROCESSING_RATE,
    PAYMENT_PROCESSING_FIXED,
    RETURN_RESIDUAL_VALUE,
    SHIPPING_PENALTY_RATE,
    CSV_FIELD_MAPPING,
    DEFAULT_STORE_SCORE,
    PROFIT_WARNING_THRESHOLD
)

@dataclass
class OrderResult:
    order_id: str
    sku: str
    product_name: str
    category: str
    buyer_payment: float
    platform_shipping: float
    settlement_price: float
    cost_price: float
    store_score: float
    ship_time: Optional[str]
    confirm_time: Optional[str]
    return_status: str
    
    commission: float = 0.0
    payment_fee: float = 0.0
    performance_fee: float = 0.0
    return_loss: float = 0.0
    shipping_penalty: float = 0.0
    total_deduction: float = 0.0
    net_amount: float = 0.0
    profit: float = 0.0
    profit_rate: float = 0.0
    is_warning: bool = False
    warning_msg: str = ""

class ProfitCalculator:
    def __init__(self):
        self.orders: List[OrderResult] = []
        self.sku_return_rates: Dict[str, float] = {}
    
    def detect_csv_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        mapping = {}
        df_columns_lower = [col.lower().strip() for col in df.columns]
        
        for standard_name, possible_names in CSV_FIELD_MAPPING.items():
            for name in possible_names:
                if name.lower() in df_columns_lower or name in df.columns:
                    actual_col = None
                    for col in df.columns:
                        if col.lower().strip() == name.lower() or col == name:
                            actual_col = col
                            break
                        elif name.lower() in col.lower():
                            actual_col = col
                            break
                    
                    if actual_col:
                        mapping[standard_name] = actual_col
                        break
        
        return mapping
    
    def get_commission_rate(self, category: str) -> float:
        for key, rate in CATEGORY_COMMISSION_RATES.items():
            if key in category or category in key:
                return rate
        return 0.08
    
    def get_performance_rate(self, store_score: float) -> float:
        for level in ["excellent", "good", "average", "poor"]:
            if store_score >= PERFORMANCE_FEES[level]["min_score"]:
                return PERFORMANCE_FEES[level]["rate"]
        return PERFORMANCE_FEES["poor"]["rate"]
    
    def calculate_sku_return_rate(self, sku: str, all_orders: List[OrderResult]) -> float:
        sku_orders = [o for o in all_orders if o.sku == sku]
        
        if not sku_orders:
            return 0.10
        
        returned_count = sum(1 for o in sku_orders if o.return_status in ['已退货', '退货', 'returned', '是', '1', 'yes', True])
        
        return returned_count / len(sku_orders)
    
    def calculate_single_order(
        self,
        order_id: str,
        sku: str,
        product_name: str,
        category: str,
        buyer_payment: float,
        platform_shipping: float,
        settlement_price: float,
        cost_price: float,
        store_score: float = DEFAULT_STORE_SCORE,
        ship_time: Optional[str] = None,
        confirm_time: Optional[str] = None,
        return_status: str = ""
    ) -> OrderResult:
        
        result = OrderResult(
            order_id=str(order_id),
            sku=str(sku),
            product_name=str(product_name),
            category=str(category),
            buyer_payment=float(buyer_payment),
            platform_shipping=float(platform_shipping),
            settlement_price=float(settlement_price),
            cost_price=float(cost_price),
            store_score=float(store_score),
            ship_time=ship_time,
            confirm_time=confirm_time,
            return_status=str(return_status)
        )
        
        taxable_amount = max(0, result.buyer_payment - result.platform_shipping)
        
        result.commission = taxable_amount * self.get_commission_rate(result.category)
        
        result.payment_fee = result.buyer_payment * PAYMENT_PROCESSING_RATE + PAYMENT_PROCESSING_FIXED
        
        result.performance_fee = taxable_amount * self.get_performance_rate(result.store_score)
        
        sku_return_rate = self.calculate_sku_return_rate(result.sku, self.orders + [result])
        result.return_loss = sku_return_rate * result.buyer_payment * (1 - RETURN_RESIDUAL_VALUE)
        
        result.shipping_penalty = max(0, (result.platform_shipping - result.settlement_price) * SHIPPING_PENALTY_RATE)
        
        result.total_deduction = (
            result.commission +
            result.payment_fee +
            result.performance_fee +
            result.return_loss +
            result.shipping_penalty
        )
        
        result.net_amount = max(0, result.buyer_payment - result.platform_shipping - result.total_deduction)
        
        result.profit = result.net_amount - result.cost_price
        
        if result.cost_price > 0:
            result.profit_rate = (result.profit / result.cost_price) * 100
        else:
            result.profit_rate = 0.0
        
        if result.profit_rate < PROFIT_WARNING_THRESHOLD:
            result.is_warning = True
            if result.profit_rate < 0:
                result.warning_msg = f"🔴 亏损！该订单亏损 ¥{abs(result.profit):.2f}，建议立即下架或调整价格"
            else:
                result.warning_msg = f"⚠️ 利润率仅 {result.profit_rate:.1f}%，低于安全线，建议降价促销或下架"
        else:
            result.is_warning = False
            result.warning_msg = ""
        
        self.orders.append(result)
        return result
    
    def process_csv(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        column_mapping = self.detect_csv_columns(df)
        
        required_fields = ['买家支付金额', '平台运费', '结算价']
        missing_fields = [f for f in required_fields if f not in column_mapping]
        
        if missing_fields:
            raise ValueError(f"CSV 文件缺少必要字段: {', '.join(missing_fields)}")
        
        results = []
        
        for idx, row in df.iterrows():
            try:
                order_id = row.get(column_mapping.get('订单号', ''), f'ORD{idx+1}')
                sku = row.get(column_mapping.get('SKU', ''), f'SKU{idx+1}')
                product_name = row.get(column_mapping.get('商品名称', ''), f'商品{idx+1}')
                category = str(row.get(column_mapping.get('类目', '家居百货'), '家居百货'))
                
                buyer_payment = float(row[column_mapping['买家支付金额']])
                platform_shipping = float(row.get(column_mapping['平台运费'], 0))
                settlement_price = float(row[column_mapping['结算价']])
                cost_price = float(row.get(column_mapping.get('成本价', ''), settlement_price * 0.7))
                
                store_score = float(row.get(column_mapping.get('店铺评分', ''), DEFAULT_STORE_SCORE))
                
                ship_time = str(row.get(column_mapping.get('发货时间', ''), ''))
                confirm_time = str(row.get(column_mapping.get('确认收货时间', ''), ''))
                return_status = str(row.get(column_mapping.get('退货状态', ''), ''))
                
                result = self.calculate_single_order(
                    order_id=order_id,
                    sku=sku,
                    product_name=product_name,
                    category=category,
                    buyer_payment=buyer_payment,
                    platform_shipping=platform_shipping,
                    settlement_price=settlement_price,
                    cost_price=cost_price,
                    store_score=store_score,
                    ship_time=ship_time if ship_time else None,
                    confirm_time=confirm_time if confirm_time else None,
                    return_status=return_status
                )
                
                results.append({
                    '订单号': result.order_id,
                    'SKU': result.sku,
                    '商品名称': result.product_name[:20] + '...' if len(str(result.product_name)) > 20 else result.product_name,
                    '类目': result.category,
                    '买家支付': round(result.buyer_payment, 2),
                    '平台运费': round(result.platform_shipping, 2),
                    '结算价': round(result.settlement_price, 2),
                    '成本价': round(result.cost_price, 2),
                    '基础佣金': round(result.commission, 2),
                    '支付处理费': round(result.payment_fee, 2),
                    '绩效附加费': round(result.performance_fee, 2),
                    '退货损耗': round(result.return_loss, 2),
                    '运费罚款': round(result.shipping_penalty, 2),
                    '总扣费': round(result.total_deduction, 2),
                    '实际到账': round(result.net_amount, 2),
                    '利润': round(result.profit, 2),
                    '利润率%': round(result.profit_rate, 2),
                    '是否预警': '🔴 预警' if result.is_warning else '✅ 正常',
                    '预警信息': result.warning_msg
                })
                
            except Exception as e:
                print(f"处理第 {idx+1} 行数据时出错: {e}")
                continue
        
        results_df = pd.DataFrame(results)
        
        summary = self.generate_summary(results_df)
        
        return results_df, summary
    
    def generate_summary(self, df: pd.DataFrame) -> Dict:
        if df.empty:
            return {'total_orders': 0}
        
        total_orders = len(df)
        total_revenue = df['买家支付'].sum()
        total_cost = df['成本价'].sum()
        total_profit = df['利润'].sum()
        total_deduction = df['总扣费'].sum()
        avg_profit_rate = (total_profit / total_cost * 100) if total_cost > 0 else 0
        
        warning_orders = len(df[df['是否预警'] == '🔴 预警'])
        loss_orders = len(df[df['利润'] < 0])
        
        summary = {
            'total_orders': total_orders,
            'total_revenue': round(total_revenue, 2),
            'total_cost': round(total_cost, 2),
            'total_profit': round(total_profit, 2),
            'avg_profit_rate': round(avg_profit_rate, 2),
            'total_deduction': round(total_deduction, 2),
            'deduction_rate': round((total_deduction / total_revenue * 100), 2) if total_revenue > 0 else 0,
            'warning_orders': warning_orders,
            'loss_orders': loss_orders,
            'net_margin': round((total_profit / total_revenue * 100), 2) if total_revenue > 0 else 0
        }
        
        return summary
    
    def get_sku_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame()
        
        sku_summary = df.groupby(['SKU', '商品名称', '类目']).agg({
            '订单号': 'count',
            '买家支付': 'sum',
            '成本价': 'sum',
            '利润': 'sum',
            '总扣费': 'sum',
            '利润率%': 'mean'
        }).reset_index()
        
        sku_summary.columns = ['SKU', '商品名称', '类目', '销量', '销售额', '总成本', '总利润', '总扣费', '平均利润率']
        
        sku_summary['利润率'] = (sku_summary['总利润'] / sku_summary['总成本'] * 100).round(2)
        
        sku_summary = sku_summary.sort_values('总利润', ascending=False)
        
        sku_summary['状态'] = sku_summary['利润率'].apply(
            lambda x: '🔴 危险' if x < PROFIT_WARNING_THRESHOLD else ('⚠️ 关注' if x < 10 else '✅ 良好')
        )
        
        return sku_summary
    
    def get_category_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame()
        
        cat_summary = df.groupby('类目').agg({
            '订单号': 'count',
            '买家支付': 'sum',
            '利润': 'sum',
            '总扣费': 'sum'
        }).reset_index()
        
        cat_summary.columns = ['类目', '订单数', '销售额', '总利润', '总扣费']
        cat_summary['利润率'] = (cat_summary['总利润'] / cat_summary['销售额'] * 100).round(2)
        cat_summary = cat_summary.sort_values('总利润', ascending=False)
        
        return cat_summary
    
    def filter_data(self, df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
        filtered_df = df.copy()
        
        if filters.get('sku') and filters['sku'] != '全部':
            filtered_df = filtered_df[filtered_df['SKU'] == filters['sku']]
        
        if filters.get('category') and filters['category'] != '全部':
            filtered_df = filtered_df[filtered_df['类目'] == filters['category']]
        
        if filters.get('status') == '预警':
            filtered_df = filtered_df[filtered_df['是否预警'] == '🔴 预警']
        elif filters.get('status') == '正常':
            filtered_df = filtered_df[filtered_df['是否预警'] == '✅ 正常']
        
        if filters.get('profit_min') is not None:
            filtered_df = filtered_df[filtered_df['利润'] >= filters['profit_min']]
        
        if filters.get('profit_max') is not None:
            filtered_df = filtered_df[filtered_df['利润'] <= filters['profit_max']]
        
        return filtered_df.reset_index(drop=True)
    
    def predict_90day_revenue(self, daily_orders: int = 10, avg_order_value: float = 50) -> List[Dict]:
        predictions = []
        cumulative = 0
        
        if self.orders:
            total_profit = sum(o.profit for o in self.orders)
            total_revenue = sum(o.buyer_payment for o in self.orders)
            avg_profit_rate = (total_profit / total_revenue) if total_revenue > 0 else 0.15
        else:
            avg_profit_rate = 0.15
        
        for day in range(1, 91):
            daily_revenue = daily_orders * avg_order_value
            daily_profit = daily_revenue * avg_profit_rate
            cumulative += daily_profit
            
            predictions.append({
                '天数': day,
                '预计收入': round(daily_revenue, 2),
                '预计利润': round(daily_profit, 2),
                '累计利润': round(cumulative, 2)
            })
        
        return predictions
