from dataclasses import dataclass;from typing import Any
@dataclass
class ServiceResult:success:bool;message:str="";data:Any=None;error_code:str=""
