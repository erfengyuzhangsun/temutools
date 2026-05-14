import logging;from datetime import datetime;from modules.message.schemas import ServiceResult;logger=logging.getLogger(__name__)
class MessageService:
    def __init__(self,user_id:int):self.user_id=user_id
    async def sync_messages(self,shop_id:int)->ServiceResult:
        from common.temu_client import TemuApiClient, TemuApiError
        client=TemuApiClient(shop_id=shop_id)
        try:
            if not client.api_key or not client.api_secret:
                return ServiceResult(False,"该店铺未绑定 API 凭证，请先在「API数据同步→店铺管理」中配置 API Key 和 Secret")
            resp=await client.get_messages()
            if not resp.success:return ServiceResult(False,"同步失败")
            msgs=(resp.data or {}).get("messages",[])or[]
            for m in msgs:
                priority="high" if any(k in str(m.get("topic","")) for k in["处罚","投诉","侵权","罚款"]) else "normal"
                self._save_msg(shop_id,m.get("topic",""),m.get("content",""),priority,m.get("category","general"))
            return ServiceResult(True,data={"synced":len(msgs)})
        except TemuApiError as e:
            return ServiceResult(False,f"消息同步失败: {e.message}")
        finally:await client.close()
    def _save_msg(self,shop_id:int,topic:str,content:str,priority:str,category:str):
        from db import execute_query
        execute_query("INSERT INTO temu_messages(user_id,shop_id,topic,content,priority,category)VALUES(?,?,?,?,?,?)",(self.user_id,shop_id,topic,content,priority,category))
    def get_templates(self,category:str="")->list:
        from db import execute_query
        if category:return execute_query("SELECT*FROM temu_reply_templates WHERE user_id=? AND category=?",(self.user_id,category),fetch=True)or[]
        return execute_query("SELECT*FROM temu_reply_templates WHERE user_id=?",(self.user_id,),fetch=True)or[]
