from dataclasses import dataclass; from datetime import datetime; from typing import Optional,Any,List
@dataclass
class ServiceResult: success:bool;message:str="";data:Any=None;error_code:str=""
@dataclass
class PriceAdjustment: adjustment_id:int;sku:str;old_price:float;new_price:float;reason:str;adjustment_type:str;created_at:datetime;operator:str="system"
@dataclass
class CompetitorPrice: sku:str;price:float;source:str;collected_at:str
