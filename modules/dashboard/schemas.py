from dataclasses import dataclass; from typing import Optional,Any,List
@dataclass
class ServiceResult: success:bool;message:str="";data:Any=None;error_code:str=""
@dataclass
class DashboardOverview: total_profit:float;total_revenue:float;total_alerts:int;pricing_pending:int;inventory_alerts:int;risk_warnings:int;review_alerts:int;shop_count:int;shop_details:list
