# 🚀 Temu 利润管家 - 部署指南

## ⚠️ Vercel 部署问题说明

### ❌ 当前问题
Vercel 无法直接部署 Streamlit 应用，因为：
- Streamlit 不是标准的 WSGI/ASGI 框架
- Vercel 默认寻找 `app`、`application` 或 `handler` 对象
- Streamlit 使用自己的运行机制

### ✅ 推荐解决方案：Streamlit Cloud（官方平台）

**为什么选择 Streamlit Cloud？**
- ✅ 100% 原生支持 Streamlit
- ✅ 完全免费（个人项目）
- ✅ 2分钟快速部署
- ✅ 自动 HTTPS
- ✅ 无需修改代码

---

## 📋 方案一：Streamlit Cloud 部署（推荐⭐⭐⭐⭐⭐）

### 步骤 1：准备 GitHub 仓库 ✅ 已完成

你的代码已经在 GitHub 上：
```
https://github.com/erfengyuzhangsun/temutools.git
```

### 步骤 2：注册 Streamlit Cloud 账号

1. 访问 **https://share.streamlit.io**
2. 点击 **"Sign up"**（注册）
3. 选择 **"Sign up with GitHub"**（使用 GitHub 登录）
4. 授权 Streamlit 访问你的 GitHub 仓库

### 步骤 3：创建新应用

1. 登录后，点击 **"+ New app"** 按钮
2. 在部署页面填写信息：

   **Deploy an app:**
   
   | 字段 | 填写内容 |
   |------|----------|
   | Repository | `erfengyuzhangsun/temutools` |
   | Branch | `main` |
   | Main file path | `app.py` |

3. 点击 **"Deploy"** 按钮

### 步骤 4：等待部署完成

- ⏱️ 首次部署约需 **2-5 分钟**
- 📊 你会看到实时构建日志
- ✅ 成功后会显示：**"Your app is live!"**

### 步骤 5：访问你的应用

部署成功后，你会得到一个 URL：
```
https://temutools-xxx.streamlit.app
```

**示例：**
```
https://temu-profit-manager.streamlit.app
```

---

## 🔧 高级配置（可选）

### 自定义子域名

1. 在 Streamlit Cloud Dashboard 中点击你的应用
2. 进入 **Settings** → **Domain**
3. 输入你想要的子域名，例如：`temu-tools`
4. 最终地址变为：`https://temu-tools.streamlit.app`

### 设置环境变量（如果需要）

1. 进入 **Settings** → **Secrets**
2. 添加环境变量（如果未来需要 API Key 等）

---

## 📱 方案二：Vercel 部署（备选方案）

> ⚠️ **警告：此方案较复杂，需要额外代码适配**
> 
> 如果你一定要使用 Vercel，请按照以下步骤操作：

### 方法 A：使用 Streamlit + FastAPI 包装器

#### 1. 安装额外依赖

在 `requirements.txt` 中添加：
```txt
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
openpyxl>=3.1.0
fastapi>=0.104.0
uvicorn>=0.24.0
```

#### 2. 创建 API 服务器

创建文件 `api/server.py`：

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import subprocess
import threading
import time
import requests

app = FastAPI()

# 启动 Streamlit 进程
def start_streamlit():
    cmd = [
        "streamlit", "run", "app.py",
        "--server.port", "8501",
        "--server.address", "127.0.0.1"
    ]
    subprocess.Popen(cmd)

# 在后台启动 Streamlit
threading.Thread(target=start_streamlit, daemon=True).start()

# 等待 Streamlit 启动
time.sleep(5)

@app.get("/")
async def root():
    try:
        response = requests.get("http://127.0.0.1:8501")
        return HTMLResponse(content=response.text)
    except:
        return HTMLResponse(content="<h1>Starting...</h1>")
```

#### 3. 更新 vercel.json

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/server.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/server.py"
    }
  ]
}
```

#### 4. 部署到 Vercel

```bash
git add .
git commit -m "Add Vercel deployment support"
git push origin main
```

> ⚠️ **注意：此方法可能存在性能问题，不推荐用于生产环境**

---

## 🎯 快速决策指南

| 你的需求 | 推荐方案 | 理由 |
|----------|----------|------|
| 快速上线（今天） | **Streamlit Cloud** | 2分钟搞定 |
| 完全免费 | **Streamlit Cloud** | 无限流量免费 |
| 自定义域名 | **Vercel** | 支持绑定域名 |
| 企业级需求 | **Vercel/AWS** | 更多控制权 |
| 个人项目/SaaS | **Streamlit Cloud** | 够用且简单 |

---

## ✅ 部署检查清单

### Streamlit Cloud 部署前确认：

- [x] GitHub 仓库已创建并推送代码
- [x] 主文件名为 `app.py`
- [x] `requirements.txt` 存在且正确
- [x] `.streamlit/config.toml` 配置文件已添加
- [x] 所有依赖项都在 requirements.txt 中列出

### 部署后验证：

- [ ] 访问应用 URL 能正常打开
- [ ] 上传 CSV 文件功能正常
- [ ] 利润计算结果准确
- [ ] 收款码图片显示正常
- [ ] 导出功能可用
- [ ] 移动端显示正常

---

## 🆘 故障排除

### 问题 1：部署失败 - ModuleNotFoundError

**原因：** 缺少依赖包

**解决：**
```bash
# 检查 requirements.txt 是否包含所有包
pip install -r requirements.txt
# 如果缺少包，添加到 requirements.txt 并重新提交
```

### 问题 2：图片无法显示

**原因：** 收款码图片路径错误

**解决：**
确保图片文件已提交到 GitHub：
```bash
git add WeChat_20260512015412.png paypal_20260512015446.jpg
git commit -m "Add payment QR codes"
git push origin main
```

### 问题 3：页面加载缓慢

**原因：** 首次加载需要安装依赖

**解决：**
- 耐心等待 2-5 分钟
- 后续访问会快很多（有缓存）

### 问题 4：中文乱码

**原因：** 编码问题

**解决：**
已在代码中使用 UTF-8 BOM 编码导出，应该不会有此问题。

---

## 📞 技术支持

如果遇到其他问题：

1. **查看日志：** Streamlit Cloud Dashboard → 你的应用 → Logs
2. **官方文档：** https://docs.streamlit.io/streamlit-cloud
3. **社区论坛：** https://discuss.streamlit.io
4. **微信客服：** temu_tools_helper

---

## 🎉 下一步

部署成功后：

1. ✅ 测试所有功能
2. ✅ 分享链接给朋友测试
3. ✅ 开始推广营销
4. ✅ 收集用户反馈

**祝你部署顺利！🚀**

---

<div align="center">

**推荐立即行动：👉 访问 https://share.streamlit.io 开始部署！**

*预计耗时：5分钟 | 难度：⭐ 极简*

</div>