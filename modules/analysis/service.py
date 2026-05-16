import logging; from datetime import datetime, timedelta; from typing import List; from modules.analysis.schemas import ServiceResult, ShopMetrics, ReportData; from modules.analysis.config import MODULE_CONFIG; logger=logging.getLogger(__name__)

class AnalysisService:
    def __init__(self, user_id: int):
        from common.plan_guard import check_plan_access
        check_plan_access("analysis", user_id)
        self.user_id = user_id

    async def collect_metrics(self, shop_id: int) -> ServiceResult:
        logger.info(f"采集指标 | user_id={self.user_id} | shop_id={shop_id}")
        from common.temu_client import TemuApiClient
        client = TemuApiClient(shop_id=shop_id)
        try:
            today = datetime.now().strftime("%Y-%m-%d"); date_from = (datetime.now()-timedelta(days=30)).strftime("%Y-%m-%d")
            resp = await client.get_shop_metrics(date_from, today)
            if not resp.success: return ServiceResult(success=False,message="指标采集失败",error_code="FETCH_FAILED")
            data = (resp.data or {}).get("metrics",{}) or {}
            metrics = ShopMetrics(shop_id=shop_id,date=today,impressions=int(data.get("impressions",0)),clicks=int(data.get("clicks",0)),
                click_rate=float(data.get("click_rate",0)),conversion_rate=float(data.get("conversion_rate",0)),
                return_rate=float(data.get("return_rate",0)),total_sales=float(data.get("total_sales",0)),
                total_orders=int(data.get("total_orders",0)),negative_review_rate=float(data.get("negative_review_rate",0)))
            self._save_metrics(shop_id, metrics)
            return ServiceResult(success=True,data={"metrics":metrics.__dict__})
        except Exception as e: logger.error(f"指标采集异常: {e}"); return ServiceResult(success=False,message="指标采集异常，请检查网络连接及API凭证配置",error_code="INTERNAL_ERROR")
        finally: await client.close()

    async def check_metric_alerts(self, shop_id: int) -> ServiceResult:
        rows = self._get_latest_metrics(shop_id)
        if not rows: return ServiceResult(success=True,data={"alerts":[],"alert_count":0})
        r = rows[0]; alerts = []
        conv_threshold = MODULE_CONFIG["conversion_rate_alert_threshold"]["default"]
        ret_threshold = MODULE_CONFIG["return_rate_alert_threshold"]["default"]
        conv = float(r.get("conversion_rate",100))
        ret = float(r.get("return_rate",0))
        if conv < conv_threshold:
            alerts.append({"type":"conversion_rate","level":"warning","value":conv,"threshold":conv_threshold,
                           "suggestion":"优化主图/调整定价/优化标题关键词"})
        if ret > ret_threshold:
            alerts.append({"type":"return_rate","level":"warning","value":ret,"threshold":ret_threshold,
                           "suggestion":"检查产品质量/优化描述/改进包装"})
        return ServiceResult(success=True,data={"alerts":alerts,"alert_count":len(alerts)})

    async def generate_report(self, shop_id: int, report_type: str = "daily") -> ServiceResult:
        rows = self._get_metrics_range(shop_id, 30)
        trends = {"impressions":[],"conversion_rate":[],"return_rate":[],"dates":[]}
        for r in rows:
            trends["dates"].append(str(r.get("date",""))); trends["impressions"].append(int(r.get("impressions",0)))
            trends["conversion_rate"].append(float(r.get("conversion_rate",0))); trends["return_rate"].append(float(r.get("return_rate",0)))
        latest = rows[0] if rows else {}
        report = ReportData(report_type=report_type,generated_at=datetime.now().isoformat(),shop_id=shop_id,
            metrics={"total_sales":float(latest.get("total_sales",0)),"total_orders":int(latest.get("total_orders",0)),
                     "avg_conversion":float(latest.get("conversion_rate",0)),"avg_return_rate":float(latest.get("return_rate",0))},
            trends=trends,recommendations=[])
        return ServiceResult(success=True,data={"report":report.__dict__})

    def _save_metrics(self, shop_id: int, m: ShopMetrics):
        from db import execute_query
        execute_query("INSERT OR REPLACE INTO temu_shop_metrics (user_id,shop_id,record_date,impressions,clicks,click_rate,conversion_rate,return_rate,total_sales,total_orders,negative_review_rate) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (self.user_id,shop_id,m.date,m.impressions,m.clicks,m.click_rate,m.conversion_rate,m.return_rate,m.total_sales,m.total_orders,m.negative_review_rate))

    def _get_latest_metrics(self, shop_id: int) -> list:
        from db import execute_query
        return execute_query("SELECT * FROM temu_shop_metrics WHERE user_id=? AND shop_id=? ORDER BY record_date DESC LIMIT 1",(self.user_id,shop_id),fetch=True) or []

    def _get_metrics_range(self, shop_id: int, days: int) -> list:
        from db import execute_query
        return execute_query("SELECT * FROM temu_shop_metrics WHERE user_id=? AND shop_id=? ORDER BY record_date DESC LIMIT ?",(self.user_id,shop_id,days),fetch=True) or []
