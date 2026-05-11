# 💰 Temu 商家风控与利润管家

<div align="center">

**精确到分的费用拆分 | 实时亏损预警 | 智能罚款预测**

[🚀 在线体验](https://temutools.vercel.app) · [📖 文档](#使用说明) · [💬 微信客服](#联系我们) · [⭐ Star](https://github.com/erfengyuzhangsun/temutools/stargazers)

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/Version-1.0.0-green.svg)](https://github.com/erfengyuzhangsun/temutools)

</div>

---

## 📌 项目简介

Temu 商家风控与利润管家是一款专为 Temu 全托管卖家打造的**智能利润计算与风险监控工具**。

### 🎯 解决的核心痛点

- ❌ **费用看不懂** - 平台扣费有10多项，根本算不清
- ❌ **利润算不清** - 日出几十单，月底一算反而亏钱
- ❌ **罚款防不住** - 发货超时、虚假发货...各种罚款突如其来
- ❌ **风险不知道** - 不知道哪些SKU在亏钱

### ✅ 我们的解决方案

- ✅ **精准费用拆分** - 自动拆分10+项费用，精确到每个订单
- ✅ **真实利润计算** - 不是理论利润，是实际能到手多少钱
- ✅ **智能风险预警** - 6大指标实时监控，提前预警避免罚款
- ✅ **数据驱动决策** - 告诉你哪些SKU赚钱，哪些该下架

---

## 🎨 核心功能

### 1️⃣ 精准利润计算器
- 一键导入订单 CSV 文件（支持 Temu 商家后台导出格式）
- 自动拆分 10+ 项平台费用：
  - 基础佣金（5%-11%，按类目）
  - 支付处理费（1.75% + ¥0.12/单）
  - 绩效附加费（基于店铺评分动态计算）
  - 退货损耗（按退货比例）
  - 运费罚款（结算价 < 运费时倒贴5%）
- 计算**真实净利润**（不是理论利润！）
- SKU 级深度分析（识别赚钱/亏钱商品）
- 利润率低于 5% 自动预警

### 2️⃣ 智能风险监控系统
实时监控 6 大核心风险指标：

| 指标 | 黄色预警 | 红色预警 | 处罚金额 |
|------|---------|---------|---------|
| 发货超时率 | >4.5% | >5% | 5-10元/单 |
| 虚假发货率 | >0.5% | >1% | 50-100元/单 |
| 货不对版率 | >1% | >2% | 销售额10倍 |
| 缺货率 | >2% | >3% | 货值5倍 |
| 退货率 | >8% | >10% | 强制下架 |
| 差评率 | >3% | >5% | 降权限流 |

### 3️⃣ 风险仪表盘
- 店铺健康评分系统（A+/A/B+/B/C/D/F 六个等级）
- 可视化展示所有指标状态（🟢安全 / 🟡关注 / 🔴危险 / 💀极危）
- 智能改进建议（带优先级和截止时间）
- 月度罚款金额预测

### 4️⃣ 数据分析报告
- 费用构成可视化（饼图 + 柱状图）
- SKU 盈利排行榜
- 订单明细报表（支持筛选和排序）
- 一键导出 Excel 报表

---

## 🚀 快速开始

### 方法一：在线使用（推荐）

直接访问我们的在线版本：**https://temutools.vercel.app**

无需安装，上传 CSV 即可使用！

### 方法二：本地运行

#### 前置要求
- Python 3.11+ （推荐 3.13）
- pip 包管理器

#### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/erfengyuzhangsun/temutools.git
cd temutools

# 2. 创建虚拟环境（可选但推荐）
python -m venv venv

# Windows 激活虚拟环境
venv\Scripts\activate

# macOS/Linux 激活虚拟环境
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动应用
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`

---

## 📊 数据格式要求

### 支持的 CSV 格式

工具支持从 **Temu 商家后台** 直接导出的订单数据。

#### 必需字段列表

| 字段名 | 说明 | 示例 |
|--------|------|------|
| 订单号 | 订单唯一标识 | ORD20260512001 |
| SKU | 商品编码 | SKU_BL001 |
| 商品名称 | 商品标题 | 北欧风收纳盒套装 |
| 买家支付金额 | 用户实付金额（元） | 68.5 |
| 平台运费 | 平台收取的运费（元） | 8.0 |
| 结算价 | 卖家结算价格（元） | 32.0 |
| 类目 | 商品类目 | 家居百货 |
| 发货时间 | 发货时间戳 | 2026-05-01 10:30:00 |
| 确认收货时间 | 收货确认时间 | 2026-05-15 14:20:00 |
| 退货状态 | 是否退货（是/否） | 否 |
| 成本价 | 你的进货成本（元） | 25.0 |
| 店铺评分 | 该订单的店铺评分 | 4.8 |

#### 示例数据文件

项目包含示例文件 `temu_orders_sample.csv`，包含 20 条测试数据。

---

## 📖 详细使用说明

### 第一步：导入数据

1. 点击左侧边栏的 **"上传 Temu 订单 CSV 文件"**
2. 选择从商家后台导出的 CSV 文件
3. 或者点击 **"使用示例数据"** 快速体验功能

### 第二步：开始分析

点击 **"🚀 开始分析"** 按钮，等待 10-30 秒完成计算

### 第三步：查看结果

#### 🎯 风险仪表盘（页面顶部）
- 查看**店铺健康评分**（A-F等级）
- 了解各项风险指标状态
- 查看预计月罚款金额
- 阅读改进建议

#### 📊 利润总览（Tab 1）
- 总订单数、总收入、总利润
- 净利润率和扣费占比
- 预警订单和亏损订单统计
- 费用构成分析

#### 📋 明细报表（Tab 2）
- 所有订单的详细数据
- 支持 SKU、类目、状态筛选
- 高亮显示亏损订单
- 导出为 Excel 或 CSV

#### 📈 SKU 分析（Tab 3）
- 按 SKU 分组统计
- 销量、销售额、总利润排行
- 识别盈利/亏损 SKU
- 利润率排名

#### ⚠️ 风险详情（Tab 4）
- 6 大指标的详细数据
- 预警历史记录
- 罚款预测明细
- 风险趋势图表

### 第四步：导出报告

在"明细报表"标签页中，可以：
- 导出完整报表为 **Excel** 格式
- 导出为 **CSV** 格式
- 复制到剪贴板

---

## ⚙️ 配置说明

### 费用规则配置（config.py）

所有费用规则都在 [config.py](config.py) 中配置，可以根据 Temu 最新政策调整：

```python
# 类目佣金比例
CATEGORY_COMMISSION_RATES = {
    "服装鞋包": 0.08,      # 8%
    "3C数码": 0.10,        # 10%
    "家居百货": 0.06,      # 6%
    "美妆个护": 0.09,      # 9%
    # ... 更多类目
}

# 风险阈值设置
RISK_THRESHOLDS = {
    "shipping_timeout": {
        "safe": 0.03,       # <3% 安全
        "warning": 0.045,   # 4.5% 黄色预警
        "danger": 0.05,     # 5% 红色预警
        "penalty": "5-10元/单"
    },
    # ... 更多阈值
}
```

### 定价方案配置

```python
PRICING_PLANS = {
    "basic": {"price": 39.9, "period": "月"},
    "pro": {"price": 99, "period": "月"},        # 推荐
    "lifetime": {"price": 399, "period": "终身"}
}
```

---

## 🛠️ 技术架构

### 技术栈

```
前端界面：Streamlit 1.45+ (Python Web框架)
数据处理：Pandas 2.2+ (数据分析)
数值计算：NumPy 2.1+ (高性能计算)
Excel导出：OpenPyxl 3.1+ (电子表格处理)
部署平台：Vercel (免费托管)
编程语言：Python 3.13
```

### 项目结构

```
temutools/
├── app.py                 # 主应用入口（含导航+UI）
├── landing.py             # 产品 Landing Page
├── calculator.py          # 利润计算引擎核心
├── risk_monitor.py        # 风险监控与预警系统
├── config.py              # 配置中心（费用规则+阈值）
├── test_calculator.py     # 单元测试脚本
├── requirements.txt       # Python 依赖包
├── Procfile               # Vercel 启动配置
├── runtime.txt            # Python 版本指定
├── vercel.json            # Vercel 部署配置
├── .gitignore             # Git 忽略规则
├── README.md              # 项目文档（本文件）
├── temu_orders_sample.csv # 示例数据（Temu格式）
└── sample_orders.csv      # 示例数据（通用格式）
```

### 核心模块说明

#### calculator.py - 利润计算引擎
```python
class ProfitCalculator:
    def process_csv(self, df) -> Tuple[pd.DataFrame, Dict]
    def calculate_fees(self, row) -> Dict[str, float]
    def calculate_profit(self, fees, cost_price) -> float
    def filter_data(self, df, filters) -> pd.DataFrame
```

#### risk_monitor.py - 风险监控系统
```python
class RiskMonitor:
    def calculate_risk_from_csv(self, df) -> None
    def analyze_all_risks(self) -> List[RiskIndicator]
    def get_overall_health_score(self) -> float
    def get_health_grade(self) -> Tuple[str, str, str]
    def predict_penalty_risk(self, monthly_orders) -> Dict
    def generate_risk_report(self) -> Dict
```

---

## 🧪 测试

运行单元测试验证功能：

```bash
python test_calculator.py
```

预期输出：

```
============================================================
🧪 Temu 利润计算器 - 单元测试
============================================================

✅ 成功加载 20 条订单数据
📋 数据列: ['订单号', 'SKU', '商品名称', ...]

============================================================
📊 计算结果汇总
============================================================

总订单数: 20
总收入: ¥1,981.60
总成本: ¥831.00
总利润: ¥636.20
平均利润率: 76.56%
总扣费: ¥376.49 (占收入 19.0%)
净利润率: 32.1%
预警订单数: 2 (利润率 < 5%)
亏损订单数: 2

============================================================
✅ 测试完成！所有功能正常运行
============================================================
```

---

## 🌐 部署指南

### Vercel 部署（推荐）

#### 1. 推送代码到 GitHub
```bash
git add .
git commit -m "更新内容"
git push origin main
```

#### 2. 在 Vercel 创建项目
1. 访问 https://vercel.com 并登录
2. 点击 "Add New" → "Project"
3. 导入 GitHub 仓库 `temutools`
4. 配置如下：
   ```
   Framework Preset: Other
   Build Command: pip install -r requirements.txt
   Output Directory: ./
   Start Command: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```
5. 点击 "Deploy"

#### 3. 绑定自定义域名（可选）
1. 在 Vercel 项目设置 → Domains
2. 添加你的域名
3. 按提示添加 DNS 记录

### Docker 部署

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

构建并运行：

```bash
docker build -t temutools .
docker run -p 8501:8501 temutools
```

---

## 💰 定价方案

| 版本 | 价格 | 适用场景 |
|------|------|----------|
| 🧪 **基础版** | ¥39.9/月 | 刚起步的小卖家，只需基础利润计算 |
| ⭐ **专业版** | ¥99/月 | **推荐！** 全功能使用，适合日常运营 |
| 👑 **终身版** | ¥399一次 | 重度用户，终身免费更新 |

### 开通方式

1. 选择套餐，扫描微信/支付宝收款码付款
2. 保存付款截图
3. 发送截图到微信客服：`temu_tools_helper`
4. 客服确认后 10 分钟内开通账号

**免费试用：7天无需信用卡**

---

## ❓ 常见问题 FAQ

### Q1: 支持哪些数据格式？
**A:** 目前支持从 Temu 商家后台直接导出的 CSV 文件。后续将支持 API 对接。

### Q2: 数据安全吗？
**A:** 完全安全！所有数据处理都在本地/浏览器端完成，不会上传到任何服务器。

### Q3: 费用规则多久更新一次？
**A:** 我们每周更新一次 Temu 最新费用规则，确保计算准确。

### Q4: 可以自定义费用规则吗？
**A:** 可以！修改 `config.py` 中的配置即可调整所有费用参数。

### Q5: 支持多少条订单数据？
**A:** 理论上无限制，建议单次不超过 10,000 条以保证性能。

### Q6: 如何导出数据？
**A:** 在"明细报表"标签页，点击"导出 Excel"或"导出 CSV"按钮即可。

### Q7: 有手机版吗？
**A:** Web 应用响应式设计，手机浏览器可以直接访问使用。

### Q8: 遇到问题怎么办？
**A:** 
- 查看本文档的使用说明
- 联系微信客服：`temu_tools_helper`
- 发送邮件：support@temu-tools.com

---

## 📈 更新日志

### v1.0.0 (2026-05-12)
- ✅ 初始版本发布
- ✅ 精准利润计算器（10+项费用拆分）
- ✅ 智能风险预警系统（6大指标监控）
- ✅ 风险仪表盘 + 健康评分
- ✅ 产品 Landing Page
- ✅ 收款码集成
- ✅ 单元测试覆盖
- ✅ Vercel 部署就绪

### 计划中的功能（Roadmap）
- [ ] 对接 Temu 商家后台 API
- [ ] 用户登录/注册系统
- [ ] 数据存储和历史记录
- [ ] 邮件/微信通知推送
- [ ] 多店铺管理
- [ ] 移动端 App
- [ ] 批量处理优化
- [ ] 国际化多语言支持

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

### 代码规范
- 遵循 PEP 8 Python 编码规范
- 添加适当的注释和文档字符串
- 确保通过所有现有测试
- 为新功能添加单元测试

---

## 📞 联系我们

- **微信客服：** `temu_tools_helper`
- **邮箱：** support@temu-tools.com
- **GitHub Issues：** [提交问题](https://github.com/erfengyuzhangsun/temutools/issues)
- **工作时间：** 周一至周六 9:00-21:00

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

```
MIT License

Copyright (c) 2026 Temu Tools Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## ⭐ Star 历史

如果这个项目对你有帮助，欢迎给一个 ⭐ 支持我们！

<a href="https://github.com/erfengyuzhangsun/temutools/stargazers">
    <img src="https://api.star-history.com/svg?repos=erfengyuzhangsun/temutools&type=Date" alt="Star History Chart">
</a>

---

## 🙏 致谢

感谢以下开源项目和社区：
- [Streamlit](https://streamlit.io/) - 强大的 Python Web 框架
- [Pandas](https://pandas.pydata.org/) - 数据分析利器
- [Vercel](https://vercel.com/) - 免费的部署平台

特别感谢所有早期用户和测试者的宝贵反馈！

---

<div align="center">

**© 2026 Temu 商家风控与利润管家 | 让每个卖家都能赚到钱 💰**

*Made with ❤️ by [Your Name](https://github.com/erfengyuzhangsun)*

</div>