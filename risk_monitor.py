import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from config import RISK_THRESHOLDS

@dataclass
class RiskIndicator:
    metric_key: str
    name: str
    current_value: float
    safe_threshold: float
    warning_threshold: float
    danger_threshold: float
    status: str
    level: str
    penalty: str
    suggestion: str
    urgency: str

class RiskMonitor:
    def __init__(self):
        self.risk_indicators: Dict[str, float] = {}
        self.alerts: List[Dict] = []
        self.order_data: Optional[pd.DataFrame] = None
    
    def calculate_risk_from_csv(self, df: pd.DataFrame) -> None:
        self.order_data = df.copy()
        
        total_orders = len(df)
        
        if total_orders == 0:
            return
        
        ship_timeout_count = 0
        fake_shipping_count = 0
        product_mismatch_count = 0
        stockout_count = 0
        return_count = 0
        negative_review_count = 0
        
        for idx, row in df.iterrows():
            try:
                ship_time_str = str(row.get('发货时间', ''))
                confirm_time_str = str(row.get('确认收货时间', ''))
                return_status = str(row.get('退货状态', ''))
                
                if ship_time_str and confirm_time_str and ship_time_str != 'nan' and confirm_time_str != 'nan':
                    try:
                        ship_time = datetime.strptime(ship_time_str.split(' ')[0], '%Y-%m-%d')
                        confirm_time = datetime.strptime(confirm_time_str.split(' ')[0], '%Y-%m-%d')
                        days_diff = (confirm_time - ship_time).days
                        
                        if days_diff > 7:
                            ship_timeout_count += 1
                    except:
                        pass
                
                if return_status in ['是', '已退货', 'returned', '1', 'yes', True]:
                    return_count += 1
                
                buyer_payment = float(row.get('买家支付金额', 0))
                
                if buyer_payment > 0:
                    platform_shipping = float(row.get('平台运费', 0))
                    settlement_price = float(row.get('结算价', 0))
                    
                    if settlement_price <= 0:
                        stockout_count += 1
                    
                    if settlement_price > 0 and platform_shipping > 0:
                        cost_price = float(row.get('成本价', 0))
                        
                        expected_price_range = (settlement_price * 0.8, settlement_price * 1.5)
                        
                        if cost_price < expected_price_range[0] or cost_price > expected_price_range[1]:
                            fake_shipping_count += 1
                        
                        if abs(cost_price - settlement_price) / settlement_price > 0.3:
                            product_mismatch_count += 1
                
                store_score = row.get('店铺评分', 4.8)
                if isinstance(store_score, (int, float)) and store_score < 4.0:
                    negative_review_count += 1
                    
            except Exception as e:
                continue
        
        shipping_timeout_rate = ship_timeout_count / total_orders
        fake_shipping_rate = fake_shipping_count / total_orders
        product_mismatch_rate = product_mismatch_count / total_orders
        stockout_rate = stockout_count / total_orders
        return_rate = return_count / total_orders
        negative_review_rate = negative_review_count / total_orders
        
        self.risk_indicators = {
            "shipping_timeout": shipping_timeout_rate,
            "fake_shipping": fake_shipping_rate,
            "product_mismatch": product_mismatch_rate,
            "stockout_rate": stockout_rate,
            "return_rate": return_rate,
            "negative_review_rate": negative_review_rate
        }
    
    def update_indicator(self, metric_key: str, value: float):
        self.risk_indicators[metric_key] = value
    
    def check_risk_level(self, metric_key: str, value: float) -> Tuple[str, str]:
        if metric_key not in RISK_THRESHOLDS:
            return ("unknown", "未知")
        
        threshold = RISK_THRESHOLDS[metric_key]
        
        if value < threshold['safe']:
            return ("safe", "正常")
        elif value < threshold['warning']:
            return ("warning", "关注")
        elif value < threshold['danger']:
            return ("danger", "危险")
        else:
            return ("critical", "极危")
    
    def get_risk_level_info(self, status: str) -> Dict:
        level_info = {
            "safe": {
                "emoji": "🟢",
                "color": "#28a745",
                "bg_color": "#d4edda",
                "text_color": "#155724",
                "label": "安全",
                "urgency": "低"
            },
            "warning": {
                "emoji": "🟡",
                "color": "#ffc107",
                "bg_color": "#fff3cd",
                "text_color": "#856404",
                "label": "关注",
                "urgency": "中"
            },
            "danger": {
                "emoji": "🔴",
                "color": "#dc3545",
                "bg_color": "#f8d7da",
                "text_color": "#721c24",
                "label": "危险",
                "urgency": "高"
            },
            "critical": {
                "emoji": "💀",
                "color": "#6c757d",
                "bg_color": "#e2e3e5",
                "text_color": "#383d41",
                "label": "极危",
                "urgency": "紧急"
            }
        }
        return level_info.get(status, level_info["safe"])
    
    def generate_suggestion(self, metric_key: str, value: float, status: str) -> str:
        suggestions_base = {
            "shipping_timeout": {
                "warning": f"⚠️ 发货超时率已达 {value*100:.1f}%，接近预警线！建议加快发货速度，优先处理即将超时的订单",
                "danger": f"🔴 发货超时率已达 {value*100:.1f}%，即将被罚款！每单罚 5-10 元！请立即处理所有待发货订单",
                "critical": f"💀 发货超时率严重超标 ({value*100:.1f}%)！可能面临严重处罚！建议暂停接单，集中处理积压订单"
            },
            "fake_shipping": {
                "warning": f"⚠️ 虚假发货率 {value*100:.2f}%，请检查物流信息是否真实有效",
                "danger": f"🔴 虚假发货率 {value*100:.2f}%！每单罚 50-100 元！立即核实所有物流单号",
                "critical": f"💀 虚假发货率严重超标！可能面临封店风险！"
            },
            "product_mismatch": {
                "warning": f"⚠️ 货不对版率 {value*100:.2f}%，请核对产品描述与实物是否一致",
                "danger": f"🔴 货不对版率 {value*100:.2f}%！罚销售额 10 倍！立即更新商品详情页",
                "critical": f"💀 货不对版率极高！可能面临巨额罚款和下架处理！"
            },
            "stockout_rate": {
                "warning": f"⚠️ 缺货率 {value*100:.1f}%，建议及时补货，设置库存预警线",
                "danger": f"🔴 缺货率 {value*100:.1f}%！罚货值 5 倍！立即补货或下架缺货商品",
                "critical": f"💀 缺货率严重！严重影响店铺权重！"
            },
            "return_rate": {
                "warning": f"⚠️ 退货率 {value*100:.1f}% 已接近阈值，分析退货原因并优化产品质量",
                "danger": f"🔴 退货率 {value*100:.1f}%！将被强制下架！检查产品质量和描述准确性",
                "critical": f"💀 退货率极高！面临商品强制下架风险！"
            },
            "negative_review_rate": {
                "warning": f"⚠️ 差评率 {value*100:.2f}%，及时回复差评，改进服务质量",
                "danger": f"🔴 差评率 {value*100:.2f}%！将降权限流！主动联系买家解决问题",
                "critical": f"💀 差评率极高！店铺权重严重下降！"
            }
        }
        
        if status == "safe":
            return f"✅ {RISK_THRESHOLDS[metric_key]['name']}处于安全范围 ({value*100:.2f}%)，继续保持"
        
        return suggestions_base.get(metric_key, {}).get(status, "请关注该指标变化")
    
    def analyze_all_risks(self) -> List[RiskIndicator]:
        results = []
        
        for metric_key, thresholds in RISK_THRESHOLDS.items():
            current_value = self.risk_indicators.get(metric_key, 0)
            
            status, level = self.check_risk_level(metric_key, current_value)
            
            suggestion = self.generate_suggestion(metric_key, current_value, status)
            
            urgency = self.get_risk_level_info(status)['urgency']
            
            result = RiskIndicator(
                metric_key=metric_key,
                name=thresholds['name'],
                current_value=current_value,
                safe_threshold=thresholds['safe'],
                warning_threshold=thresholds['warning'],
                danger_threshold=thresholds['danger'],
                status=status,
                level=level,
                penalty=thresholds['penalty'],
                suggestion=suggestion,
                urgency=urgency
            )
            
            results.append(result)
            
            if status in ["warning", "danger", "critical"]:
                level_info = self.get_risk_level_info(status)
                self.alerts.append({
                    '指标': thresholds['name'],
                    '当前值': f"{current_value*100:.2f}%",
                    '状态': f"{level_info['emoji']} {level}",
                    '紧急程度': urgency,
                    '时间': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    '建议': suggestion,
                    '可能处罚': thresholds['penalty']
                })
        
        results.sort(key=lambda x: ['critical', 'danger', 'warning', 'safe'].index(x.status))
        
        return results
    
    def get_overall_health_score(self) -> float:
        if not self.risk_indicators:
            return 100.0
        
        total_score = 0
        weight_sum = 0
        
        weights = {
            "shipping_timeout": 0.20,
            "fake_shipping": 0.25,
            "product_mismatch": 0.25,
            "stockout_rate": 0.15,
            "return_rate": 0.10,
            "negative_review_rate": 0.05
        }
        
        score_map = {
            "safe": 100,
            "warning": 70,
            "danger": 40,
            "critical": 0
        }
        
        for metric_key, value in self.risk_indicators.items():
            status, _ = self.check_risk_level(metric_key, value)
            weight = weights.get(metric_key, 0.1)
            
            total_score += score_map.get(status, 50) * weight
            weight_sum += weight
        
        return total_score / weight_sum if weight_sum > 0 else 100
    
    def get_health_grade(self) -> Tuple[str, str, str]:
        score = self.get_overall_health_score()
        
        if score >= 90:
            return ("A+", "优秀", "#28a745")
        elif score >= 80:
            return ("A", "良好", "#5cb85c")
        elif score >= 70:
            return ("B+", "较好", "#8bc34a")
        elif score >= 60:
            return ("B", "一般", "#ffc107")
        elif score >= 50:
            return ("C", "需关注", "#ff9800")
        elif score >= 40:
            return ("D", "危险", "#ff5722")
        else:
            return ("F", "极危", "#f44336")
    
    def predict_penalty_risk(self, monthly_orders: int = 300) -> Dict[str, Dict]:
        predictions = {}
        
        for metric_key, value in self.risk_indicators.items():
            status, _ = self.check_risk_level(metric_key, value)
            
            if status not in ["danger", "critical"]:
                continue
            
            if metric_key == "shipping_timeout":
                penalty_per_order = 10 if status == "critical" else 7.5
                monthly_penalty = monthly_orders * value * penalty_per_order
                predictions["发货超时罚款"] = {
                    'amount': round(monthly_penalty, 2),
                    'reason': f"发货超时率 {value*100:.1f}% > 阈值",
                    'severity': status
                }
            
            elif metric_key == "fake_shipping":
                penalty_per_order = 100 if status == "critical" else 75
                monthly_penalty = monthly_orders * value * penalty_per_order
                predictions["虚假发货罚款"] = {
                    'amount': round(monthly_penalty, 2),
                    'reason': f"虚假发货率 {value*100:.2f}% > 阈值",
                    'severity': status
                }
            
            elif metric_key == "product_mismatch":
                avg_order_value = 50
                multiplier = 10
                monthly_penalty = monthly_orders * value * avg_order_value * multiplier
                predictions["货不对版罚款"] = {
                    'amount': round(monthly_penalty, 2),
                    'reason': f"货不对版率 {value*100:.2f}%，罚销售额 {multiplier}倍",
                    'severity': status
                }
            
            elif metric_key == "stockout_rate":
                avg_product_value = 30
                multiplier = 5
                monthly_penalty = monthly_orders * value * avg_product_value * multiplier
                predictions["缺货罚款"] = {
                    'amount': round(monthly_penalty, 2),
                    'reason': f"缺货率 {value*100:.1f}%，罚货值 {multiplier}倍",
                    'severity': status
                }
        
        return predictions
    
    def generate_risk_report(self) -> Dict:
        risk_analysis = self.analyze_all_risks()
        health_score = self.get_overall_health_score()
        grade, grade_label, grade_color = self.get_health_grade()
        penalty_predictions = self.predict_penalty_risk()
        
        critical_count = sum(1 for r in risk_analysis if r.status == "critical")
        danger_count = sum(1 for r in risk_analysis if r.status == "danger")
        warning_count = sum(1 for r in risk_analysis if r.status == "warning")
        safe_count = sum(1 for r in risk_analysis if r.status == "safe")
        
        total_predicted_penalty = sum(p['amount'] for p in penalty_predictions.values())
        
        improvement_suggestions = []
        for risk in risk_analysis:
            if risk.status in ["warning", "danger", "critical"]:
                improvement_suggestions.append({
                    'priority': '高' if risk.status in ['danger', 'critical'] else '中',
                    'indicator': risk.name,
                    'current_value': f"{risk.current_value*100:.2f}%",
                    'target_value': f"<{risk.safe_threshold*100:.1f}%",
                    'action': risk.suggestion,
                    'deadline': '24小时内' if risk.status == 'critical' else ('3天内' if risk.status == 'danger' else '7天内')
                })
        
        improvement_suggestions.sort(key=lambda x: {'高': 0, '中': 1}.get(x['priority'], 2))
        
        report = {
            '生成时间': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            '健康评分': health_score,
            '等级': grade,
            '等级标签': grade_label,
            '等级颜色': grade_color,
            '指标统计': {
                '总指标数': len(risk_analysis),
                '安全': safe_count,
                '关注': warning_count,
                '危险': danger_count,
                '极危': critical_count
            },
            '详细指标': [],
            '预计月罚款': total_predicted_penalty,
            '罚款明细': penalty_predictions,
            '预警记录': self.alerts[-10:] if self.alerts else [],
            '改进建议': improvement_suggestions[:5],
            '总结': self._generate_summary(grade, critical_count, danger_count, warning_count, total_predicted_penalty)
        }
        
        for risk in risk_analysis:
            level_info = self.get_risk_level_info(risk.status)
            report['详细指标'].append({
                '指标名称': risk.name,
                '当前值': f"{risk.current_value*100:.2f}%",
                '安全阈值': f"<{risk.safe_threshold*100:.1f}%",
                '预警阈值': f"<{risk.warning_threshold*100:.1f}%",
                '危险阈值': f">{risk.danger_threshold*100:.1f}%",
                '状态': f"{level_info['emoji']} {risk.level}",
                '状态颜色': level_info['color'],
                '背景颜色': level_info['bg_color'],
                '紧急程度': risk.urgency,
                '可能处罚': risk.penalty,
                '建议': risk.suggestion
            })
        
        return report
    
    def _generate_summary(self, grade: str, critical: int, danger: int, warning: int, total_penalty: float) -> str:
        if grade in ["A+", "A"]:
            return "🎉 恭喜！您的店铺运营状况优秀，各项指标均在安全范围内。继续保持良好的运营习惯！"
        elif grade in ["B+", "B"]:
            issues = []
            if warning > 0:
                issues.append(f"{warning}项指标需要关注")
            summary = f"⚡ 您的店铺整体状况良好，但{'、'.join(issues)}。建议优化这些指标以提升评分。"
            return summary
        elif grade == "C":
            issues = [f"{danger}项危险指标", f"{warning}项预警指标"]
            return f"⚠️ 店铺存在明显风险：{'、'.join(issues)}。需要立即采取行动避免罚款！"
        else:
            issues = [f"{critical}项极危指标", f"{danger}项危险指标"]
            penalty_text = f"，预计月罚款 ¥{total_penalty:,.0f}" if total_penalty > 0 else ""
            return f"🚨 店铺处于高风险状态：{'、'.join(issues)}{penalty_text}！请立即处理！"
    
    def get_dashboard_data(self) -> Dict:
        return self.generate_risk_report()
