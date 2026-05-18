# Temu 合作伙伴平台完整文档参考 + 系统合规对照

> **用途**：一次性抓取 Partner Platform 所有公开文档的结构和关键内容，供后续开发直接参考，不用再重复翻网页。
> 
> **数据来源**：https://partner.temu.com/documentation 全站抓取（2026-05-18）
> - Partner Guide · Developer Guide · API Reference · 4 份 Policy 文档

---

## 一、站点结构速览

Temu Partner Platform 有 4 个独立站点，对应不同的卖家群体：

| 站点 | 域名 | 服务对象 |
|:----|:-----|:---------|
| **US** | `https://partner-us.temu.com` | 美国本地卖家 + 跨境卖家 |
| **EU** | `https://partner-eu.temu.com` | 欧洲本地卖家 + 跨境卖家 |
| **GLOBAL** | `https://partner.temu.com` | 其他区域（不含中国/美国/欧洲） |
| **中国** | `https://partner.kuajingmaihuo.com` | 中国大陆跨境卖家 + 全托管卖家 |

你当前注册的是 **US 站点**（`partner-us.temu.com`），创建的应用"鲸云策"将服务 US 区域的卖家。

---

## 二、合作伙伴类型（Partner Guide）

> 来源：https://partner.temu.com/documentation?menu_code=52ef88bdef1d4527b15f6d303b173e48

### 2.1 两种合作类型

| 类型 | 说明 | 注册方式 |
|:----|:-----|:---------|
| **Developer（开发者）** | 提供系统集成服务（ERP/OMS/WMS/电商连接器） | ✅ 线上注册 |
| **Service Provider（服务商）** | 提供运营服务（代运营/产品优化/广告服务） | ❌ 线下对接（发意向到 partner@temu.com） |

> **你的定位**：Developer。你是独立软件开发商（ISV），为 Temu 卖家提供自动化运营工具。

### 2.2 平台流程（4 步上架）

```
Step 1: 注册 → Step 2: 创建应用 → Step 3: 合规与安全评估 → Step 4: 发布应用
   ↓             ↓                    ↓                        ↓
 你已完成      鲸云策已提交         等待审核中             审核通过后可上架
```

> 官方说明：**每个阶段最快 1 个工作日**，具体取决于实际情况。

---

## 三、开发者指南完整结构（Developer Guide）

> 来源：https://partner.temu.com/documentation?menu_code=38e79b35d2cb463d85619c1c786dd303

### 3.1 Seller Authorization Guide（卖家授权指南）

#### 3.1.1 卖家类型与授权方式

| 卖家类型 | 站点区域 | 授权类型 | 授权地址 |
|:--------|:---------|:---------|:---------|
| 跨境卖家 | US | 手动授权 | `https://agentseller.temu.com/open-platform/system-manage/client-manage` |
| 跨境卖家 | EU | 手动授权 | `https://agentseller-eu.temu.com/open-platform/system-manage/client-manage` |
| 本地卖家 | US | 手动授权 + 回调授权 | `https://seller.temu.com/open-platform/client-manage` |
| 本地卖家 | EU | 手动授权 + 回调授权 | `https://seller-eu.temu.com/open-platform/client-manage` |

#### 3.1.2 三种授权类型

| 类型 | 流程 | 推荐度 |
|:----|:-----|:-------|
| **Manual Authorization** | 卖家中心授权 → 展示 access_token → 卖家复制 → 你粘贴到系统保存 | 可用 |
| **Callback Authorization** | 卖家中心授权 → 回调 `redirect_url` 收到 code → 后端调用 `bg.open.accesstoken.create` 换 token → 自动保存 | ⭐ **推荐** |
| **In-app Authorization**（即将上线） | 在你的系统内触发 Temu 授权页面，不跳转到卖家中心 | 未来 |

#### 3.1.3 回调授权 URL 格式

```
https://seller.temu.com/open-platform/client-manage/authorization?appKey=XXX&redirect_uri=XXX&state=XXX
```

回调后收到的参数：
- `app_key` — 你的应用 key
- `callback_host` — 回调主机
- `code` — 授权码（用于换 token）
- `state` — 你传入的自定义参数

> **注意**：你目前申请的是跨境卖家（Crossborder seller）模式，仅支持**手动授权**。你之前实现的回调端点是为本地卖家准备的。

---

## 四、API Reference 完整结构

> 来源：https://partner.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a

### 4.1 左侧菜单分类

```
┌─────────────────────────────────────┐
│ Authorization                       │
│  ├─ Authorize and Authorization Call│
│  ├─ bg.open.accesstoken.create      │
│  ├─ bg.open.accesstoken.info.get    │
│  └─ temu.local.mall.tags.get        │
├─────────────────────────────────────┤
│ Product                             │
│  ├─ How to release product?         │
│  ├─ Special Category Requirements   │
│  ├─ Add Products                    │
│  └─ Manage Products                 │
├─────────────────────────────────────┤
│ Price                               │
├─────────────────────────────────────┤
│ Order                               │
├─────────────────────────────────────┤
│ Order Cancellation                  │
├─────────────────────────────────────┤
│ Fulfillment                         │
├─────────────────────────────────────┤
│ Return and Refund                   │
├─────────────────────────────────────┤
│ Promotion                           │
├─────────────────────────────────────┤
│ Webhook                             │
├─────────────────────────────────────┤
│ Ads                                 │
└─────────────────────────────────────┘
```

### 4.2 当前系统已对接的 API（从 scope list 提取，共 53 个）

| 分类 | API 方法 | 系统状态 |
|:----|:---------|:---------|
| **商品 (Product)** | `bg.local.goods.list.query`, `bg.local.goods.sku.list.query`, `bg.local.goods.sku.list.price.query`, `bg.local.goods.sale.status.set`, `bg.local.goods.stock.edit`, `bg.local.goods.priceorder.query/accept/change.sku.price/negotiate` 等 22 个 | ✅ 已实现常用 API |
| **订单 (Order)** | `bg.order.list.get`, `bg.order.detail.get`, `bg.order.amount.query`, `bg.order.shippinginfo.get`, `bg.order.combinedshipment.list.get` | ✅ 已实现 |
| **售后 (After-sales)** | `bg.aftersales.aftersales.list.get`, `bg.aftersales.parentaftersales.list.get` | ✅ 已实现 |
| **物流 (Logistics)** | `bg.logistics.companies.get`, `bg.logistics.shipment.*` 等 | ⏳ 未对接 |
| **授权 (Auth)** | `bg.open.accesstoken.create`, `bg.open.accesstoken.info.get` | ✅ 已实现 |
| **Webhook 订阅** | `bg.tmc.message.update` | ⏳ 未对接 |
| **合规** | `bg.local.compliance.goods.list.query` | ✅ 已实现 |
| **运费模板** | `bg.freight.template.list.query` | ✅ 已实现 |

### 4.3 API 调用基础规范（从文档提取，供未来参考）

| 规范 | 值 |
|:----|:----|
| 请求 URL | `POST https://openapi-b-{region}.temu.com/openapi/router` |
| Content-Type | `application/json` |
| 公共参数 | `type`, `app_key`, `access_token`, `sign`, `timestamp`, `data_type` (6 个) |
| 签名算法 | MD5(secret + key1value1key2value2... + secret) → 大写 hex |
| 时间戳 | Unix 秒级，10 位 |
| 限流 | 默认 20 qps / app_key |
| data_type | 固定传 `"JSON"` |

---

## 五、Policy 文档完整体系

Partner Platform 底部有 4 份法律文档：

| 文档 | 链接 | 关键内容 |
|:----|:-----|:---------|
| **Temu Partner Platform Terms** | [PDF](https://partner.temu.com/protocol/temu_partner_platform_terms_20250523.pdf) | 合作协议 · 权利义务 · 数据保护 · 终止条款 |
| **Temu Partner Platform Privacy Policy** | [页面](https://partner.temu.com/documentation?menu_code=d8425dcd25b04658843e622e178a3b42&sub_menu_code=2b5a53673c5f4b2284cb30c77d40ae98) | 个人信息收集/使用/共享 · 跨境传输 · 用户权利 |
| **Data Security Policy for Service Providers** | [页面](https://partner.temu.com/documentation?menu_code=d8425dcd25b04658843e622e178a3b42&sub_menu_code=9cc3edb526494a059c477fd99953fa3e) | 数据安全要求 · 事件报告 · 合规违规处理 |
| **Partner Platform Cookie Policy** | [PDF](https://partner.temu.com/protocol/temu_partner_platform_cookie_policy_20240731.pdf) | Cookie 使用说明 |

---

## 六、系统合规完整对照清单

### 6.1 审核流程相关

| 要求 | 当前状态 | 说明 |
|:----|:---------|:-----|
| 开发者账号注册 | ✅ 已完成 | 484478363@qq.com 已注册 |
| 创建自研应用 | ✅ 已提交"鲸云策" | US 区，等待审核 |
| 合规与安全评估 | ⏳ 审核中 | 已提交问卷和文件 |
| 应用上架 | ⏳ 审核通过后才可操作 |
| 设置应用类型 (Public/Private) | ⏳ 审核通过后决定 | 如果服务其他卖家需设为 Public |

### 6.2 授权流程相关

| 要求 | 当前状态 | 说明 |
|:----|:---------|:-----|
| 回调端点 `redirect_url` | ✅ 已实现 | `GET /temu/callback` → code 换 token → 自动绑定 |
| 回调地址在平台配置 | ⏳ 审核通过后配置 | 在 APP Management → 编辑应用 → `redirect_url` 字段 |
| 手动授权支持 | ✅ 已实现 | 绑定店铺弹窗 → 手动输入 Access Token |
| In-app Authorization | ⏳ 未实现（待 Temu 上线） | 未来版本 |

### 6.3 Terms（合作协议）合规

| 条款 | 要求 | 当前状态 |
|:-----|:-----|:---------|
| §3.2 | 服务其他卖家必须在 Partner Platform 上架应用 | ⏳ 审核通过后上架 |
| §3.3 | 与 Subscriber 签署书面协议，符合适用法律 | ⚠️ 建议起草客户协议 |
| §3.3 | 数据处理严格按 Subscriber 指示 | ✅ 系统设计已遵循 |
| §3.3 | 违反条款须立即通知 Temu | ✅ 系统有日志可追溯 |
| §3.4 | 你拥有应用的完整权利 | ✅ 你是开发者 |
| §9 | Temu 有权审查源代码 | ✅ 代码可审查 |
| §4.3 | 遵守所有适用法律 | ⚠️ 需要注意数据出境法 |

### 6.4 数据安全政策合规

| 要求 | 当前状态 |
|:-----|:---------|
| Access Token 加密存储 | ✅ AES-256 加密 |
| 数据安全事件报告流程 | ⚠️ 建议建立文档 |
| 数据按 Subscriber 指示使用 | ✅ 系统设计已遵循 |
| 安全措施充分 | ✅ HTTPS + 加密存储 + JWT |

### 6.5 隐私政策合规

| 要求 | 当前状态 |
|:-----|:---------|
| 隐私政策公开 | ✅ 已发布（Privacy.jsx） |
| 说明数据存储位置 | ✅ DigitalOcean 新加坡 |
| 说明数据用途 | ✅ 运营管理工具 |
| 用户同意流程 | ✅ 注册时勾选同意 |

### 6.6 API 对接合规

| 要求 | 当前状态 |
|:-----|:---------|
| 公共参数正确的 6 个 | ✅ 已对齐 |
| 签名算法 MD5 | ✅ 已实现 |
| 请求格式 JSON | ✅ `Content-Type: application/json` |
| 限流 20 qps | ✅ 未超限 |
| access_token 必传 | ✅ 每请求携带 |

---

## 七、后续待办清单（按优先级）

| 优先级 | 事项 | 时机 |
|:------:|:-----|:-----|
| 🔴 P0 | US 应用审核通过 | 等待 Temu |
| 🔴 P0 | 审核后在 Partner Platform 配置 `redirect_url` | 审核通过后立即 |
| 🔴 P0 | 服务器 `.env` 配 TEMU_APP_KEY/SECRET/REGION | 审核通过后立即 |
| 🔴 P0 | 用自己的 LINGLINGhuang 店铺测试连通性 | 配置密钥后 |
| 🟡 P1 | 设置应用类型（Public/Private） | 审核通过后 |
| 🟡 P1 | 起草客户服务协议 | 开始服务前 |
| 🟡 P2 | 建立数据安全事件处理文档 | 有余力时 |
| 🟢 P3 | 对接 Webhook（订单状态变更回调） | 未来迭代 |
| 🟢 P3 | 对接物流 API（发货/面单） | 未来迭代 |

---

## 八、网站地图索引（方便 AI 后续直接引用）

以下索引可在后续开发中直接引用，无需重复翻页：

```
https://partner.temu.com/
├─ /documentation?menu_code=52ef88bdef1d4527b15f6d303b173e48       # Partner Guide
├─ /documentation?menu_code=38e79b35d2cb463d85619c1c786dd303       # Developer Guide
│  └─ sub_menu_code=1                                               #   Seller Authorization Guide
├─ /documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a       # API Reference
│  ├─ Authorization
│  │  ├─ sub_menu_code=d8425dcd25b04658843e622e178a3b42            #     Authorize Callback
│  │  ├─ bg.open.accesstoken.create
│  │  ├─ bg.open.accesstoken.info.get
│  │  └─ temu.local.mall.tags.get
│  ├─ Product                                                      # 商品上架管理类
│  ├─ Price                                                         # 核价 API 类
│  ├─ Order                                                         # 订单 API 类
│  ├─ Order Cancellation                                            # 取消订单 API
│  ├─ Fulfillment                                                   # 物流发货 API
│  ├─ Return and Refund                                             # 售后退款 API
│  ├─ Promotion                                                     # 活动报名 API
│  ├─ Webhook                                                       # 回调事件订阅
│  ├─ Ads                                                           # 广告 API
│  └─ Compliance                                                    # 合规 API
├─ Policy
│  ├─ /protocol/temu_partner_platform_terms_20250523.pdf            # Terms PDF
│  ├─ /documentation?...sub_menu_code=2b5a53673c5f4b2284cb30c77d40ae98  # Privacy Policy
│  ├─ /documentation?...sub_menu_code=9cc3edb526494a059c477fd99953fa3e  # Data Security Policy
│  └─ /protocol/temu_partner_platform_cookie_policy_20240731.pdf    # Cookie Policy
└─ /app/app-mgmt                                                    # APP 管理后台（需登录）
   └─ /detail/edit?app_key=XXX                                      #   编辑应用（配 redirect_url）
```

---

> **免责声明**：本文档仅为基于公开信息的整理摘要，不构成法律意见。具体合规问题请咨询专业律师。
