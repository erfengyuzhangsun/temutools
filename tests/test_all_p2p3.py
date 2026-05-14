import os,sys,tempfile
_db=tempfile.NamedTemporaryFile(suffix=".db",delete=False);_dp=_db.name;_db.close()
os.environ["DB_MODE"]="sqlite";os.environ["SQLITE_PATH"]=_dp
from cryptography.fernet import Fernet;os.environ["ENCRYPTION_KEY"]=Fernet.generate_key().decode()
os.environ["SEED_ADMIN_PASSWORD"]="test-seed-pwd"
from db import initialize_database;initialize_database()
from common.models_p2p3 import initialize_tables;initialize_tables()
from unittest.mock import AsyncMock, patch, MagicMock
import pytest;pytestmark=pytest.mark.asyncio

@pytest.fixture(autouse=True)
def mock_db():
    with patch("db.execute_query") as m:
        m.return_value=[]
        yield m

class TestMessage:
    @patch("common.temu_client.TemuApiClient")
    async def test_sync(self,mc,mock_db):
        from modules.message.service import MessageService;from common.temu_client import TemuApiResponse
        m=AsyncMock();mc.return_value=m;m.get_messages.return_value=TemuApiResponse(True,{"messages":[{"topic":"处罚","content":"违规","category":"penalty"}]})
        r=await MessageService(1).sync_messages(1);assert r.data["synced"]==1

class TestShipping:
    async def test_labels(self,mock_db):
        mock_db.return_value=[{"sku":"SKU1","product_name":"Test","settlement_price":100.0}]
        from common.services_p2p3 import ShippingService
        r=await ShippingService(1).generate_labels(1,["SKU1"]);assert r.success;assert r.data["count"]==1
    async def test_manifest(self,mock_db):
        from common.services_p2p3 import ShippingService
        r=await ShippingService(1).generate_manifest(1,["ORD1"]);assert r.success

class TestActivity:
    @patch("common.temu_client.TemuApiClient")
    async def test_fetch(self,mc,mock_db):
        from common.services_p2p3 import ActivityService;from common.temu_client import TemuApiResponse
        m=AsyncMock();mc.return_value=m;m.get_activities.return_value=TemuApiResponse(True,{"activities":[{"activity_id":"ACT001","name":"家居大促","category":"家居百货"}]})
        mock_db.return_value=[{"sku":"SKU1","category":"家居百货"}]
        r=await ActivityService(1).fetch_and_match(1);assert r.success

class TestRiskInspection:
    async def test_inspect(self,mock_db):
        mock_db.side_effect=[ [{"sku":"SKU1","product_name":"纯金项链","category":"珠宝"}], [{"word":"纯金"}], None ]
        from common.services_p2p3 import RiskInspectionService
        r=await RiskInspectionService(1).inspect_all_skus(1);assert r.success

class TestBatchOps:
    async def test_batch_offline(self,mock_db):
        from common.services_p2p3 import BatchOpsService
        r=await BatchOpsService(1).batch_offline(1,["SKU1","SKU2"]);assert r.success

class TestReviewMonitor:
    async def test_sync(self,mock_db):
        mock_db.return_value=[{"sku":"SKU1","t":10,"b":3}]
        from common.services_p2p3 import ReviewMonitorService
        r=await ReviewMonitorService(1).sync_new_reviews(1);assert r.success
    async def test_analyze(self,mock_db):
        mock_db.return_value=[{"content":"质量差","keywords":"质量","category":"quality"}]
        from common.services_p2p3 import ReviewMonitorService
        r=await ReviewMonitorService(1).analyze_reviews(1);assert r.success

class TestProductResearch:
    async def test_collect(self,mock_db):
        from common.services_p2p3 import ProductResearchService
        r=await ProductResearchService(1).collect_1688("家居",3);assert r.success
    async def test_profit(self):
        from common.services_p2p3 import ProductResearchService
        r=await ProductResearchService(1).estimate_profit({"price":30,"suggested_price":80},1);assert r.success
    def test_infringement(self):
        from common.services_p2p3 import ProductResearchService
        r=ProductResearchService(1).check_infringement("Nike鞋");assert r.data["risk"]=="high"

class TestSupplier:
    def test_add(self,mock_db):
        from common.services_p2p3 import SupplierService
        r=SupplierService(1).add_supplier("XX工厂","张三","13800","家居");assert r.success
    def test_compare(self,mock_db):
        mock_db.return_value=[{"supplier_name":"工厂A","price":30,"product_name":"商品"},{"supplier_name":"工厂B","price":28,"product_name":"商品"}]
        from common.services_p2p3 import SupplierService
        r=SupplierService(1).compare_prices("SKU1");assert r.success

def teardown_module(module):
    try:os.unlink(_dp)
    except:pass
