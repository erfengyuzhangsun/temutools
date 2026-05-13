# Temu全托管卖家运营平台 - 项目统一开发规范文档

> 版本：v1.0  
> 生效范围：所有16大功能模块的前后端、数据库、接口、配置、日志、测试开发  
> 强制标准：后续所有编码严格遵循，不得私自偏离

---

## 目录

1. [目录结构规范](#1-目录结构规范)
2. [文件命名规范](#2-文件命名规范)
3. [接口设计规范](#3-接口设计规范)
4. [数据库表设计规范](#4-数据库表设计规范)
5. [日志分级规范](#5-日志分级规范)
6. [全局异常处理规范](#6-全局异常处理规范)
7. [定时任务开发规范](#7-定时任务开发规范)
8. [前端页面组件规范](#8-前端页面组件规范)
9. [版本迭代规范](#9-版本迭代规范)
10. [模块依赖约束规范](#10-模块依赖约束规范)
11. [安全编码规范](#11-安全编码规范)
12. [测试开发规范](#12-测试开发规范)
13. [配置管理规范](#13-配置管理规范)

---

## 1. 目录结构规范

### 1.1 顶层目录

```
temu_tools/
├── app.py                  # [已有] 主应用入口（Streamlit）- 严禁修改
├── calculator.py           # [已有] 利润核算引擎 - 严禁修改
├── risk_monitor.py         # [已有] 风控监控 - 严禁修改
├── config.py               # [已有] 全局配置 - 严禁修改
├── db.py                   # [已有] 数据库操作 - 严禁修改
├── auth.py                 # [已有] 认证模块 - 严禁修改
├── admin.py                # [已有] 管理后台 - 严禁修改
├── logger.py               # [已有] 日志模块 - 严禁修改
├── landing.py              # [已有] 落地页 - 严禁修改
├── api/
│   └── index.py            # [已有] FastAPI代理 - 严禁修改
├── docs/                   # [新增] 文档目录
│   ├── TEST_CASES_COMPLETE.md
│   └── DEVELOPMENT_STANDARDS.md
│
├── modules/                # [新增] 所有新功能模块的根目录
│   ├── __init__.py
│   │
│   ├── api_sync/           # 模块1：API对接与数据同步
│   │   ├── __init__.py
│   │   ├── service.py      # 业务逻辑层
│   │   ├── models.py       # 数据模型
│   │   ├── schemas.py      # 请求/响应数据结构
│   │   ├── temu_client.py  # Temu API客户端封装
│   │   ├── config.py       # 模块专属配置
│   │   └── tests/
│   │       ├── __init__.py
│   │       └── test_api_sync.py
│   │
│   ├── pricing/            # 模块2：核价自动化
│   │   ├── __init__.py
│   │   ├── service.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── rules_engine.py # 核价规则引擎
│   │   └── tests/
│   │
│   ├── scheduler/          # 模块3：全局定时任务调度中心
│   │   ├── __init__.py
│   │   ├── service.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── core.py         # 调度核心
│   │   └── tests/
│   │
│   ├── inventory/          # 模块4：库存管理系统
│   │   ├── __init__.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── tests/
│   │
│   ├── analysis/           # 模块5：数据分析与预警
│   │   ├── __init__.py
│   │   ├── service.py
│   │   ├── models.py
│   │   ├── alert_engine.py # 告警引擎
│   │   └── tests/
│   │
│   ├── pricing_adj/        # 模块6：智能定价调价
│   │   ├── __init__.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── tests/
│   │
│   ├── finance/            # 模块7：财务结算对账
│   │   ├── __init__.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── tests/
│   │
│   ├── dashboard/          # 模块8：多店铺总控大屏
│   │   ├── __init__.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── tests/
│   │
│   ├── message/            # 模块9：消息与售后
│   │   ├── __init__.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── tests/
│   │
│   ├── shipping/           # 模块10：标签与发货
│   │   ├── __init__.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── tests/
│   │
│   ├── activity/           # 模块11：活动报名
│   │   ├── __init__.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── tests/
│   │
│   ├── risk_inspection/    # 模块12：风控体检
│   │   ├── __init__.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── tests/
│   │
│   ├── batch_ops/          # 模块13：批量运营
│   │   ├── __init__.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── tests/
│   │
│   ├── review_monitor/     # 模块14：差评监控
│   │   ├── __init__.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── tests/
│   │
│   ├── product_research/   # 模块15：选品辅助
│   │   ├── __init__.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── tests/
│   │
│   └── supplier/           # 模块16：供应商管理
│       ├── __init__.py
│       ├── service.py
│       ├── models.py
│       └── tests/
│
├── common/                 # [新增] 公共基础设施层
│   ├── __init__.py
│   ├── temu_client.py      # Temu API统一客户端（合并所有API调用）
│   ├── crypto.py           # 加解密工具
│   ├── pagination.py       # 分页工具
│   ├── retry.py            # 重试机制
│   └── excel.py            # Excel导出工具
│
├── tests/                  # [新增] 全局集成测试
│   ├── __init__.py
│   ├── conftest.py         # pytest共享fixture
│   └── test_global_integration.py
│
└── scripts/                # [已有] 脚本
```

### 1.2 目录规范要点

- 所有新模块位于 `modules/` 下，各自独立目录
- 公共基础设施位于 `common/`，供所有模块复用
- 每个模块目录内包含 `__init__.py`（可为空）
- 每个模块自包含 `tests/` 子目录存放该模块测试用例
- 严禁在已有文件（app.py, calculator.py等）中添加新功能代码

---

## 2. 文件命名规范

### 2.1 Python文件

| 文件类型 | 命名规则 | 示例 |
|---------|---------|------|
| 业务服务层 | `service.py` | `modules/api_sync/service.py` |
| 数据模型 | `models.py` | `modules/api_sync/models.py` |
| 数据结构定义 | `schemas.py` | `modules/api_sync/schemas.py` |
| 模块配置 | `config.py` | `modules/api_sync/config.py` |
| 测试文件 | `test_<模块名>.py` | `test_api_sync.py` |
| 工具类/客户端 | 小写下划线 | `temu_client.py`, `rules_engine.py` |

### 2.2 命名约定

- **类名**：PascalCase（大驼峰），如 `TemuApiClient`, `PricingRulesEngine`
- **函数/方法名**：snake_case（小写下划线），如 `sync_orders()`, `get_pricing_logs()`
- **变量名**：snake_case，如 `shop_id`, `sync_status`
- **常量名**：UPPER_SNAKE_CASE（大写+下划线），如 `MAX_RETRY_COUNT`
- **私有成员**：以单下划线 `_` 开头，如 `_calculate_profit_rate()`
- **模块名**：简短小写，无下划线或简短下划线，如 `pricing_adj`, `api_sync`

---

## 3. 接口设计规范

### 3.1 Service层接口规范

所有模块的 `service.py` 中，Service类必须遵循以下规范：

```python
class XxxService:
    """Xxx业务服务 - 单一职责，只处理Xxx相关业务"""
    
    def __init__(self, user_id: int):
        """必须接收user_id用于数据隔离"""
        self.user_id = user_id
    
    # 所有公开方法必须包含完整的类型注解
    def sync_orders(self, shop_id: int) -> SyncResult:
        ...
    
    # 统一的返回结构
    @dataclass
    class SyncResult:
        success: bool
        message: str
        data: Optional[Any] = None
        error_code: Optional[str] = None
```

### 3.2 接口设计约束

1. **所有接口统一返回 `ServiceResult`** 结构：
   ```python
   @dataclass
   class ServiceResult:
       success: bool
       message: str
       data: Any = None
       error_code: str = ""
   ```

2. **所有方法必须包含完整类型注解**（参数类型 + 返回值类型）

3. **所有业务方法必须包含docstring**（至少一行描述）

4. **禁止Service直接操作数据库**，必须通过Model层操作

5. **禁止Service直接调用外部API**，必须通过Client层封装

### 3.3 Temu API统一客户端规范

`common/temu_client.py` 提供所有模块共用的Temu API调用封装：

```python
class TemuApiClient:
    """Temu开放平台API统一客户端"""
    
    def __init__(self, shop_id: int):
        self.shop_id = shop_id
        self.api_key = self._load_api_key(shop_id)
        self.base_url = "https://open-api.temu.com"
    
    async def request(self, endpoint: str, method: str, params: dict = None) -> dict:
        """统一请求封装：鉴权 + 加密 + 签名 + 重试"""
    
    # 各业务接口
    async def get_orders(self, page: int, page_size: int) -> dict: ...
    async def get_inventory(self, sku_codes: list) -> dict: ...
    async def get_pricing_notices(self) -> dict: ...
    async def get_settlements(self, date_from: str, date_to: str) -> dict: ...
```

---

## 4. 数据库表设计规范

### 4.1 命名规范

| 元素 | 格式 | 示例 |
|------|------|------|
| 表名 | `temu_<模块缩写>_<业务含义>` | `temu_sync_orders`, `temu_pricing_logs` |
| 主键 | `<表名缩写>_id` | `sync_id`, `pricing_id` |
| 外键 | `user_id`, `shop_id` | 统一命名 |
| 时间戳 | `created_at`, `updated_at` | 所有表必须包含 |
| 状态字段 | `status` | VARCHAR(20)，有明确枚举值 |
| 逻辑删除 | `is_deleted` | TINYINT(1) DEFAULT 0 |

### 4.2 新建表通用结构标准

```sql
CREATE TABLE IF NOT EXISTS temu_xxx_yyy (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    shop_id INT NOT NULL COMMENT '店铺ID',
    ...业务字段...,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted TINYINT(1) DEFAULT 0 COMMENT '逻辑删除',
    FOREIGN KEY (user_id) REFERENCES temu_users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (shop_id) REFERENCES temu_shops(shop_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='业务说明';
```

### 4.3 约束规则

1. **所有新表必须同时支持SQLite/MySQL双模式**（参考db.py的adapt_query_for_sqlite机制）
2. **所有表必须有 `user_id` 字段** 用于数据隔离
3. **所有表必须有 `shop_id` 字段** 用于店铺隔离
4. **所有表必须有 `created_at`/`updated_at` 时间戳**
5. **避免使用外键约束级联删除**（应用层处理数据清理）
6. **状态字段使用 VARCHAR 而非 ENUM**（兼容SQLite）
7. **金额字段使用 DECIMAL(10,2)**（MySQL）或 **REAL**（SQLite）
8. **索引原则**：user_id+shop_id联合索引；高频查询字段单独索引

### 4.4 新建表清单（全部16个模块）

各模块对应的数据库表在模块开发阶段按需创建，详见各模块 `models.py`。

---

## 5. 日志分级规范

### 5.1 日志级别定义

| 级别 | 数值 | 使用场景 | 示例 |
|------|------|---------|------|
| DEBUG | 10 | 开发调试细节，生产关闭 | "请求参数: {...}" |
| INFO | 20 | 正常业务流程记录 | "订单同步成功，共50条" |
| WARNING | 30 | 异常但可自动恢复 | "API响应缓慢(3.2s)" |
| ERROR | 40 | 功能异常但系统可用 | "订单同步失败(超时)" |
| CRITICAL | 50 | 系统级严重故障 | "数据库连接池耗尽" |

### 5.2 日志记录规范

```python
# 正确示例
logger.info(f"订单同步完成 | shop_id={shop_id} | count={count} |耗时={cost_time:.2f}s")
logger.error(f"API请求失败 | endpoint={endpoint} | error={str(e)} | retry={retry_count}")

# 禁止行为
logger.info("订单同步完成")  # 缺少关键上下文信息
logger.error(f"API密钥: {api_key}")  # 禁止记录敏感信息
```

### 5.3 日志存储

- 每个模块使用独立的 logger 实例：`logger = logging.getLogger(__name__)`
- 日志文件统一存储在 `logs/<模块名>/` 目录
- 日志保留周期：至少90天
- 操作日志（谁在什么时间做了什么）统一写入 `temu_operation_logs` 表

### 5.4 操作日志表结构

```sql
CREATE TABLE IF NOT EXISTS temu_operation_logs (
    log_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    shop_id INT DEFAULT NULL,
    module VARCHAR(50) NOT NULL COMMENT '模块名',
    action VARCHAR(100) NOT NULL COMMENT '操作动作',
    detail TEXT COMMENT '操作详情',
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. 全局异常处理规范

### 6.1 自定义异常体系

```python
class TemuBaseException(Exception):
    """所有自定义异常的基类"""
    def __init__(self, message: str, error_code: str = ""):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ApiAuthException(TemuBaseException):
    """API认证异常"""

class ApiTimeoutException(TemuBaseException):
    """API超时异常"""

class DataSyncException(TemuBaseException):
    """数据同步异常"""

class ConfigException(TemuBaseException):
    """配置异常"""

class BusinessRuleException(TemuBaseException):
    """业务规则异常"""
```

### 6.2 异常处理规范

```python
try:
    result = await temu_client.request(endpoint, params)
except ApiAuthException as e:
    logger.error(f"API认证失败 | shop_id={shop_id} | error={e.message}")
    return ServiceResult(success=False, message="API认证失败，请检查密钥", error_code="AUTH_FAILED")
except ApiTimeoutException as e:
    logger.warning(f"API超时 | endpoint={endpoint} | retry={retry_count}")
    # 自动重试逻辑
    return _retry_request(endpoint, params)
except Exception as e:
    logger.critical(f"未知错误 | {str(e)}")
    return ServiceResult(success=False, message="系统内部错误", error_code="INTERNAL_ERROR")
```

### 6.3 强制约束

1. **所有API调用必须包裹 try-except**，禁止未捕获的异常传递到上层
2. **所有定时任务执行体必须包裹 try-except**，防止单任务崩溃影响调度器
3. **前端回调必须捕获异常**，不能出现白屏/崩溃
4. **禁止使用裸 `except:`**，必须指定具体的异常类型

---

## 7. 定时任务开发规范

### 7.1 任务定义接口

所有定时任务必须实现统一的 `TaskInterface`：

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class TaskResult:
    success: bool
    message: str
    execution_time: float
    records_affected: int = 0

class BaseTask(ABC):
    """所有定时任务的基类"""
    
    def __init__(self, task_id: str, user_id: int, shop_id: int):
        self.task_id = task_id
        self.user_id = user_id
        self.shop_id = shop_id
        self.logger = logging.getLogger(f"task.{task_id}")
    
    @abstractmethod
    async def execute(self) -> TaskResult:
        """任务执行体 - 子类必须实现"""
        pass
    
    @abstractmethod
    def get_config_schema(self) -> dict:
        """返回任务的可配置参数schema"""
        pass
```

### 7.2 任务注册规范

```python
# modules/scheduler/service.py

class SchedulerService:
    def register_task(self, task: BaseTask):
        """注册任务到调度中心"""
    
    def unregister_task(self, task_id: str):
        """移除任务"""
    
    def start_task(self, task_id: str):
        """启动指定任务"""
    
    def stop_task(self, task_id: str):
        """停止指定任务"""
```

### 7.3 约束规则

1. 所有自动化功能必须通过调度中心统一管理，禁止独立cron/threading
2. 任务默认不阻塞主进程（异步后台执行）
3. 任务失败自动重试（默认3次，间隔递增）
4. 任务执行超时自动终止（默认300s，可配置）
5. 任务日志强制记录执行时间、状态、结果数量

---

## 8. 前端页面组件规范

### 8.1 页面路由规范

所有新页面统一通过 Streamlit 的 `st.query_params` 实现路由：

```python
query_params = st.query_params
page = query_params.get("page", ["app"])[0]

if page == "api_sync":
    show_api_sync_page()
elif page == "pricing":
    show_pricing_page()
```

### 8.2 UI组件风格统一

1. 使用现有CSS主题色（渐变紫 #667eea → #764ba2）
2. 卡片式布局，统一 `border-radius: 12px` + `box-shadow` 效果
3. 警告/错误使用彩色横幅（红/黄/绿）
4. 表格数据统一使用 `st.dataframe` 带分页
5. 图表统一使用 `st.line_chart` / `st.bar_chart`

### 8.3 页面组件复用

每个模块的页面组件统一放在 `modules/<模块名>/ui.py` 中：

```python
# modules/api_sync/ui.py
def show_api_sync_page():
    """API同步配置与管理页面"""
    st.title("API对接与数据同步")
    
    # 店铺选择器
    shop_id = _shop_selector()
    
    # 同步状态卡片
    _show_sync_status_card(shop_id)
    
    # 操作按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("立即同步", use_container_width=True):
            _trigger_sync(shop_id)
```

### 8.4 导航集成

所有新模块页面统一在主应用的侧边栏导航接入：

```python
# 在 app.py 中只添加路由跳转和侧边栏入口
# 严禁在 app.py 中添加业务逻辑代码
```

---

## 9. 版本迭代规范

### 9.1 版本号规则

主版本号.次版本号.修订号（如 v1.2.0）

- **主版本**：重大架构变更或不兼容升级
- **次版本**：新功能模块增加
- **修订号**：BUG修复、性能优化

### 9.2 迭代流程

1. `docs/CHANGELOG.md` 记录每次迭代的变更
2. 每次迭代结束更新 `docs/VERIFICATION_REPORT.md`
3. 迭代产出包含：测试报告 + 代码 + 配置变更说明

### 9.3 发版检查清单

- [ ] 全量测试用例通过率100%
- [ ] 原有功能不受影响（回归测试通过）
- [ ] 新模块测试覆盖所有正常/异常/边界场景
- [ ] 所有配置项可视化可用
- [ ] 日志记录完整可追溯
- [ ] 无硬编码业务参数

---

## 10. 模块依赖约束规范

### 10.1 依赖方向

```
common/  ←────────────────  modules/* (所有模块可依赖公共层)
    │
    ├── temu_client.py      ← 所有模块复用
    ├── crypto.py           ← 所有模块复用
    └── retry.py            ← 所有模块复用

modules/*   ←──────────────  禁止模块间互相依赖
    │
    ├── api_sync/           ← 独立，不依赖其他模块
    ├── pricing/            ← 独立，依赖api_sync的数据
    ├── inventory/          ← 独立，依赖api_sync的数据
    └── ...                 ← 所有模块平级独立
```

### 10.2 约束规则

1. **模块间禁止直接 import**，如需调用其他模块功能，通过 `SchedulerService` 或事件机制
2. **所有模块只允许依赖 `common/` 和系统内置库**
3. **如必须跨模块调用，通过统一的事件总线**（在`common/event_bus.py`中实现）
4. **禁止循环依赖**——A模块import B + B模块import A 绝对禁止

---

## 11. 安全编码规范

### 11.1 数据加密

1. **API密钥加密**：使用 Fernet（对称加密）存储，密钥由环境变量 `ENCRYPTION_KEY` 提供
2. **传输加密**：所有Temu API调用使用 HTTPS
3. **敏感数据脱敏**：日志、异常信息中禁止打印完整API密钥（只显示前4位+后4位）

### 11.2 数据隔离

1. 所有数据查询必须带 `user_id` 条件，禁止全表扫描
2. 所有数据接口必须验证当前用户对该数据的访问权限
3. 跨店铺操作必须显式声明店铺ID，禁止默认使用"所有店铺"

### 11.3 输入校验

1. 所有用户输入必须做类型校验和范围校验
2. SKU编码、金额等字段必须做格式校验
3. 禁止在SQL查询中拼接用户输入（使用参数化查询）

### 11.4 加密工具规范

```python
# common/crypto.py
from cryptography.fernet import Fernet
import os

class CryptoUtils:
    def __init__(self):
        key = os.environ.get("ENCRYPTION_KEY")
        if not key:
            key = Fernet.generate_key()
            os.environ["ENCRYPTION_KEY"] = key.decode()
        self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
    
    def encrypt(self, plain_text: str) -> str:
        return self.cipher.encrypt(plain_text.encode()).decode()
    
    def decrypt(self, cipher_text: str) -> str:
        return self.cipher.decrypt(cipher_text.encode()).decode()
```

---

## 12. 测试开发规范

### 12.1 测试框架

- 使用 **pytest** 作为统一测试框架
- 测试文件命名：`test_<module_name>.py`
- 测试类命名：`Test<ModuleName>`
- 测试方法命名：`test_<场景>_<预期行为>`

### 12.2 AAA测试模式

所有测试用例必须遵循 Arrange-Act-Assert 模式：

```python
class TestApiSyncService:
    
    def test_sync_orders_success(self):
        # Arrange - 准备测试数据
        shop_id = 1
        mock_api_data = [{"order_id": "ORD001", ...}]
        with patch.object(TemuApiClient, 'get_orders', return_value=mock_api_data):
            service = ApiSyncService(user_id=1)
            
            # Act - 执行测试
            result = service.sync_orders(shop_id=shop_id)
            
            # Assert - 断言结果
            assert result.success is True
            assert result.data["synced_count"] == 1
            assert len(result.data["orders"]) == 1
```

### 12.3 测试覆盖要求

| 测试类型 | 覆盖率要求 | 说明 |
|---------|-----------|------|
| 正常流程 | 100% | 所有核心业务路径 |
| 异常流程 | 100% | 所有可预见的异常分支 |
| 边界值 | >=80% | 数值边界、空数据、大数据量 |
| 安全测试 | 100% | 密钥加密、数据隔离 |

### 12.4 Mock规范

1. 外部API调用必须Mock（不依赖Temu平台真实可用）
2. 数据库操作使用内存SQLite（`:memory:`）
3. 时间相关使用 `freezegun` 冻结时间
4. 测试之间必须隔离（独立的数据库、独立的Mock）

### 12.5 测试文件结构

每个模块的测试文件 `tests/test_<module>.py` 结构：

```python
"""模块名 - 单元测试"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestNormalFlow:
    """正常流程测试"""
    
    def test_basic_operation_success(self):
        ...
    
    def test_with_multiple_records(self):
        ...


class TestExceptionFlow:
    """异常场景测试"""
    
    def test_api_timeout(self):
        ...
    
    def test_invalid_input(self):
        ...


class TestBoundaryValue:
    """边界值测试"""
    
    def test_empty_data(self):
        ...
    
    def test_large_data_set(self):
        ...
```

---

## 13. 配置管理规范

### 13.1 配置层级

```
系统级（环境变量） → 模块级（config.py） → 用户级（数据库配置表）
```

| 层级 | 存储方式 | 示例 |
|------|---------|------|
| 系统级 | `.env` / 环境变量 | `DB_MODE=mysql`, `ENCRYPTION_KEY=xxx` |
| 模块级 | `modules/<模块>/config.py` | 默认值、参数范围 |
| 用户级 | `temu_configs` 表 | 毛利率阈值、安全库存天数 |

### 13.2 用户配置表结构

```sql
CREATE TABLE IF NOT EXISTS temu_configs (
    config_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    shop_id INT DEFAULT NULL,
    config_key VARCHAR(100) NOT NULL COMMENT '配置键',
    config_value TEXT NOT NULL COMMENT '配置值（JSON格式）',
    module VARCHAR(50) NOT NULL COMMENT '所属模块',
    description VARCHAR(255) COMMENT '配置说明',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_config (user_id, shop_id, config_key),
    FOREIGN KEY (user_id) REFERENCES temu_users(user_id) ON DELETE CASCADE
);
```

### 13.3 配置规范

```python
# modules/api_sync/config.py
"""模块1：API同步 - 模块级默认配置"""

MODULE_CONFIG = {
    "sync_interval_minutes": {
        "default": 60,          # 默认值
        "min": 5,               # 最小值
        "max": 1440,            # 最大值（24小时）
        "type": "int",
        "description": "自动同步间隔（分钟）"
    },
    "max_retry_count": {
        "default": 3,
        "min": 0,
        "max": 10,
        "type": "int",
        "description": "最大重试次数"
    },
    "retry_interval_seconds": {
        "default": 30,
        "min": 5,
        "max": 600,
        "type": "int",
        "description": "重试间隔（秒）"
    }
}
```

### 13.4 强制约束

1. **严禁任何业务参数硬编码在Python代码中**
2. **所有阈值、开关、周期、比率必须后台可视化配置**
3. **配置修改即时生效**，无需重启服务
4. **配置数据按用户隔离**，用户A的配置不影响用户B

---

## 附录A：代码风格检查清单

- [ ] 类名PascalCase + 函数/变量snake_case
- [ ] 所有方法包含完整类型注解
- [ ] 所有方法包含docstring
- [ ] 无硬编码业务参数
- [ ] 无裸except
- [ ] 密码/密钥不硬编码
- [ ] 数据库查询参数化（无字符串拼接）
- [ ] 导入语句分组（标准库 → 第三方 → 本地）
- [ ] 行长度不超过120字符
- [ ] 测试覆盖正常/异常/边界场景

## 附录B：代码审查标准

1. **架构合规**：是否符合高内聚低耦合、模块化设计
2. **开闭原则**：是否做到了只新增不修改
3. **测试覆盖**：是否满足AAA模式 + 全场景覆盖
4. **安全审查**：是否有敏感信息泄露、数据隔离漏洞
5. **性能审查**：是否有N+1查询、未使用异步导致阻塞
6. **配置审查**：是否有硬编码的魔法数值
