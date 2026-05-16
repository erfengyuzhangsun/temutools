import logging;from datetime import datetime;from typing import Any;logger=logging.getLogger(__name__)
class ServiceResult:
    def __init__(self,success,message="",data=None,error_code=""):
        self.success=success;self.message=message;self.data=data;self.error_code=error_code
def R(success,message="",data=None,error_code=""):
    return ServiceResult(success,message,data,error_code)

class ShippingService:
    def __init__(self,uid:int):self.uid=uid
    async def generate_labels(self,shop_id:int,sku_list:list)->Any:
        from db import execute_query
        labels=[]
        skipped=[]
        for sku in sku_list:
            sku=sku.strip()
            if not sku:
                continue
            rows=execute_query("SELECT sku,product_name,settlement_price FROM temu_sync_orders WHERE user_id=? AND shop_id=? AND sku=? LIMIT 1",(self.uid,shop_id,sku),fetch=True)
            if not rows:
                logger.warning(f"SKU {sku} 数据不完整，已跳过")
                skipped.append(sku)
                continue
            r=rows[0]
            label={"sku":r["sku"],"name":r.get("product_name",""),"price":float(r.get("settlement_price",0)),"barcode":f"TEMU_{r['sku']}","status":"generated"}
            execute_query("INSERT INTO temu_shipping_labels(user_id,shop_id,sku,label_data,status)VALUES(?,?,?,?,?)",(self.uid,shop_id,sku,"{}","ready"))
            labels.append(label)
        msg=f"生成{len(labels)}张标签"
        if skipped:
            msg+=f"，{len(skipped)}个SKU未找到"
        return R(True,msg,{"labels":labels,"count":len(labels),"skipped":skipped})
    async def generate_manifest(self,shop_id:int,order_ids:list)->Any:
        from db import execute_query
        manifest={"order_ids":order_ids,"generated_at":datetime.now().isoformat(),"total_orders":len(order_ids)}
        execute_query("INSERT INTO temu_shipping_manifests(user_id,shop_id,order_ids,manifest_data,status)VALUES(?,?,?,?,?)",(self.uid,shop_id,",".join(str(x)for x in order_ids),"{}","ready"))
        return R(True,"发货单生成成功",{"manifest":manifest})

class ActivityService:
    def __init__(self,uid:int):self.uid=uid
    async def fetch_and_match(self,shop_id:int)->Any:
        from common.temu_client import TemuApiClient
        c=None
        try:
            c=TemuApiClient(shop_id)
            r=await c.get_activities()
            if not r.success:return R(False,"获取活动失败")
            acts=(r.data or {}).get("activities",[])or[]
            from db import execute_query
            skus=execute_query("SELECT DISTINCT category,sku FROM temu_sync_orders WHERE user_id=? AND shop_id=?",(self.uid,shop_id),fetch=True)or[]
            matched=[]
            for act in acts:
                cat=act.get("category","");matched_skus=[s["sku"] for s in skus if cat and cat in str(s.get("category",""))]
                if matched_skus:
                    activity_id=act.get("activity_id");name=act.get("name","")
                    matched.append({"activity_id":activity_id,"name":name,"matched_skus":matched_skus,"count":len(matched_skus)})
                    try:
                        execute_query("INSERT OR REPLACE INTO temu_activities(user_id,shop_id,activity_id,name,status,applied_skus)VALUES(?,?,?,?,?,?)",(self.uid,shop_id,activity_id,name,"pending",""))
                    except Exception:
                        pass
            return R(True,data={"activities":matched,"count":len(matched)})
        except Exception:
            return R(False,"获取活动异常")
        finally:
            if c is not None:
                await c.close()
    async def batch_apply(self,shop_id:int,activity_id:str,sku_list:list)->Any:
        from db import execute_query
        execute_query("INSERT OR REPLACE INTO temu_activities(user_id,shop_id,activity_id,status,applied_skus)VALUES(?,?,?,?,?)",(self.uid,shop_id,activity_id,"applied",",".join(sku_list)))
        return R(True,"报名成功",{"activity_id":activity_id,"sku_count":len(sku_list)})

class RiskInspectionService:
    def __init__(self,uid:int):self.uid=uid
    async def inspect_all_skus(self,shop_id:int)->Any:
        from db import execute_query
        skus=execute_query("SELECT sku,MAX(product_name)as product_name,MAX(category)as category FROM temu_sync_orders WHERE user_id=? AND shop_id=? GROUP BY sku",(self.uid,shop_id),fetch=True)or[]
        words=execute_query("SELECT word FROM temu_sensitive_words WHERE user_id=?",(self.uid,),fetch=True)or[]
        sensitive=[w["word"] for w in words]
        violations=[]
        for s in skus:
            for field in["product_name","sku","category"]:
                val=str(s.get(field,""))
                for wd in sensitive:
                    if wd in val:
                        violations.append({"sku":s["sku"],"field":field,"content":val,"word":wd,"level":"high","suggestion":f"移除'{wd}'"})
                        execute_query("INSERT INTO temu_inspection_records(user_id,shop_id,sku,field,content,risk_level,suggestion)VALUES(?,?,?,?,?,?,?)",(self.uid,shop_id,s["sku"],field,val,"high",f"移除敏感词'{wd}'"))
        return R(True,data={"violations":violations,"count":len(violations),"total_skus":len(skus)})
    async def generate_report(self,shop_id:int)->Any:
        from db import execute_query
        rows=execute_query("SELECT COUNT(*)as t,(SELECT COUNT(*)FROM temu_inspection_records WHERE user_id=? AND shop_id=?)as v FROM temu_sync_orders WHERE user_id=? AND shop_id=?",(self.uid,shop_id,self.uid,shop_id),fetch=True)or[]
        t=rows[0]["t"]if rows else 0;v=rows[0]["v"]if rows else 0
        return R(True,data={"report":{"total_skus":t,"violations":v,"compliance_score":round(100*(1-v/max(t,1)),1)}})

class BatchOpsService:
    def __init__(self,uid:int):self.uid=uid
    async def batch_offline(self,shop_id:int,sku_list:list)->Any:
        from db import execute_query
        success,fail=[],0
        for sku in sku_list:
            try:
                execute_query("UPDATE temu_sync_orders SET status='offline' WHERE user_id=? AND shop_id=? AND sku=?",(self.uid,shop_id,sku))
                success.append(sku)
            except:fail+=1
        return R(True,data={"success":len(success),"failed":fail,"results":success,"total":len(sku_list)})

class ReviewMonitorService:
    def __init__(self,uid:int):self.uid=uid
    async def sync_new_reviews(self,shop_id:int)->Any:
        from db import execute_query
        threshold_r=15
        rows=execute_query("SELECT sku,COUNT(*)as t,SUM(CASE WHEN rating<=2 THEN 1 ELSE 0 END)as b FROM temu_reviews WHERE user_id=? AND shop_id=? GROUP BY sku",(self.uid,shop_id),fetch=True)or[]
        alerts=[]
        for r in rows:
            rate=r["b"]/r["t"]*100 if r["t"]>0 else 0
            if rate>threshold_r:
                alerts.append({"sku":r["sku"],"bad_rate":round(rate,1),"total":r["t"],"bad":r["b"]})
        return R(True,data={"new_reviews_synced":len(rows),"high_risk_skus":alerts,"alert_count":len(alerts)})
    async def analyze_reviews(self,shop_id:int)->Any:
        from db import execute_query
        rows=execute_query("SELECT content,keywords,category FROM temu_reviews WHERE user_id=? AND shop_id=? AND rating<=2",(self.uid,shop_id),fetch=True)or[]
        from collections import Counter
        kw=Counter()
        for r in rows:
            if r.get("keywords"):
                for k in str(r["keywords"]).split(","):
                    if k.strip():kw[k.strip()]+=1
        return R(True,data={"total_bad_reviews":len(rows),"keyword_stats":dict(kw.most_common(10))})

class SupplierService:
    def __init__(self,uid:int):self.uid=uid
    def add_supplier(self,name:str,contact:str="",phone:str="",category:str="")->Any:
        from db import execute_query
        sid=execute_query("INSERT INTO temu_suppliers(user_id,name,contact,phone,main_category)VALUES(?,?,?,?,?)",(self.uid,name,contact,phone,category))
        return R(True,"供应商添加成功",{"supplier_id":sid})
    async def check_price_changes(self,supplier_id:int)->Any:
        from db import execute_query
        rows=execute_query("SELECT sku,product_name,price,last_price FROM temu_supplier_products WHERE supplier_id=?",(supplier_id,),fetch=True)or[]
        changes=[]
        for r in rows:
            if r.get("last_price")and r["price"]!=r["last_price"]:
                changes.append({"sku":r["sku"],"product":r.get("product_name",""),"old_price":float(r["last_price"]),"new_price":float(r["price"]),"change_pct":round((r["price"]-r["last_price"])/r["last_price"]*100,1)})
        return R(True,data={"changes":changes,"count":len(changes)})
    def compare_prices(self,sku:str)->Any:
        from db import execute_query
        rows=execute_query("SELECT s.name as supplier_name,sp.price,sp.product_name FROM temu_supplier_products sp JOIN temu_suppliers s ON sp.supplier_id=s.supplier_id WHERE sp.sku=?",(sku,),fetch=True)or[]
        if rows:
            best=min(rows,key=lambda x:x["price"])
            return R(True,data={"sku":sku,"suppliers":rows,"best_supplier":best["supplier_name"],"best_price":float(best["price"])})
        return R(True,"暂无数据",{"suppliers":[]})

class ProductResearchService:
    def __init__(self,uid:int):self.uid=uid
    async def collect_1688(self,keywords:str,limit:int=10)->Any:
        from db import execute_query
        items=[]
        for i in range(min(limit,5)):
            item={"title":f"测试商品{i+1}","price":30+i*5,"sales":1000-i*100,"source":"1688"}
            execute_query("INSERT INTO temu_product_research(user_id,source,title,price,sales_count,category)VALUES(?,?,?,?,?,?)",(self.uid,"1688",item["title"],item["price"],item["sales"],keywords))
            items.append(item)
        return R(True,data={"items":items,"count":len(items)})
    async def estimate_profit(self,product_data:dict,shop_id:int)->Any:
        cost=float(product_data.get("price",30))
        shipping=15.0
        suggested_price=float(product_data.get("suggested_price",cost*2.5))
        platform_fee=suggested_price*0.15
        profit=suggested_price-cost-shipping-platform_fee
        margin=profit/cost*100 if cost>0 else 0
        return R(True,data={"estimated_profit":round(profit,2),"estimated_margin":round(margin,1),"cost":cost,"shipping":shipping,"platform_fee":round(platform_fee,2),"suggested_price":suggested_price})
    def check_infringement(self,title:str)->Any:
        brands=["nike","adidas","gucci","lv","chanel","apple","samsung",
                "耐克","阿迪达斯","古驰","路易威登","香奈儿","苹果","三星"]
        found=[b for b in brands if b.lower() in title.lower()]
        if found:
            return R(True,data={"risk":"high","infringing_brands":found,"suggestion":f"移除品牌词:{','.join(found)}"})
        return R(True,data={"risk":"low","infringing_brands":[]})
