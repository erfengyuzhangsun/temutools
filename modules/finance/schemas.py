from dataclasses import dataclass; from datetime import datetime; from typing import Optional,Any,List
@dataclass
class ServiceResult: success:bool;message:str="";data:Any=None;error_code:str=""
@dataclass
class Settlement: settlement_id:int;period_start:str;period_end:str;total_revenue:float;total_deductions:float;net_payout:float;status:str
@dataclass
class MonthlySummary: month:str;total_revenue:float;total_cost:float;total_profit:float;profit_rate:float;platform_fees:float;shop_details:list
