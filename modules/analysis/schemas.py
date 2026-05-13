from dataclasses import dataclass,field; from datetime import datetime; from typing import Optional,Any,List

@dataclass
class ServiceResult: success:bool;message:str="";data:Any=None;error_code:str=""

@dataclass
class ShopMetrics:
    shop_id:int;date:str;impressions:int=0;clicks:int=0;click_rate:float=0.0;conversion_rate:float=0.0
    return_rate:float=0.0;total_sales:float=0.0;total_orders:int=0;negative_review_rate:float=0.0

@dataclass
class ReportData:
    report_type:str;generated_at:str;shop_id:int;metrics:dict;trends:dict;recommendations:list
