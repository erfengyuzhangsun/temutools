#!/usr/bin/env python3
"""
Temu开放平台 API 连通性测试工具
独立脚本，不依赖项目其他代码，拿真实凭证一键测试

用法:
    set TEMU_APP_KEY=你的app_key
    set TEMU_APP_SECRET=你的app_secret
    python test_temu_api.py

或直接修改下面两个变量
"""

import json
import hashlib
import hmac
import os
import sys
from datetime import datetime
from urllib.parse import urlencode

# ============================================================
# 配置区 —— 从环境变量读取，或直接修改这里
# ============================================================
APP_KEY = os.environ.get("TEMU_APP_KEY", "请填入你的app_key")
APP_SECRET = os.environ.get("TEMU_APP_SECRET", "请填入你的app_secret")

# Temu API 基础域名（待验证）
API_BASE_URL = os.environ.get("TEMU_API_BASE", "https://open-api.temu.com")

# ============================================================
# 颜色输出
# ============================================================
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def section(title):
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}{BOLD}  {title}{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")

def ok(msg):
    print(f"  {GREEN}✅ {msg}{RESET}")

def fail(msg):
    print(f"  {RED}❌ {msg}{RESET}")

def info(msg):
    print(f"  {YELLOW}ℹ️  {msg}{RESET}")

# ============================================================
# 多种签名算法实现（挨个试，看哪个能通）
# ============================================================

def sign_md5_sort(params: dict, secret: str) -> str:
    signed = dict(params)
    sign_str = secret + json.dumps(signed, sort_keys=True, ensure_ascii=False) + secret
    return hashlib.md5(sign_str.encode()).hexdigest().upper()

def sign_md5_join(params: dict, secret: str) -> str:
    sorted_keys = sorted(params.keys())
    pairs = [f"{k}{params[k]}" for k in sorted_keys]
    sign_str = secret + "".join(pairs) + secret
    return hashlib.md5(sign_str.encode()).hexdigest().upper()

def sign_sha256_sort(params: dict, secret: str) -> str:
    signed = dict(params)
    sign_str = secret + json.dumps(signed, sort_keys=True, ensure_ascii=False) + secret
    return hashlib.sha256(sign_str.encode()).hexdigest().upper()

def sign_hmac_sha256(params: dict, secret: str) -> str:
    sorted_keys = sorted(params.keys())
    sign_str = "&".join([f"{k}={params[k]}" for k in sorted_keys])
    return hmac.new(secret.encode(), sign_str.encode(), hashlib.sha256).hexdigest().upper()

def sign_hmac_md5(params: dict, secret: str) -> str:
    sorted_keys = sorted(params.keys())
    sign_str = "&".join([f"{k}={params[k]}" for k in sorted_keys])
    return hmac.new(secret.encode(), sign_str.encode(), hashlib.md5).hexdigest().upper()

SIGN_METHODS = [
    ("MD5 + json.dumps(sort_keys=True)", sign_md5_sort),
    ("MD5 + k+v拼接", sign_md5_join),
    ("SHA256 + json.dumps(sort_keys=True)", sign_sha256_sort),
    ("HMAC-SHA256 + URL参数拼接", sign_hmac_sha256),
    ("HMAC-MD5 + URL参数拼接", sign_hmac_md5),
]

def get_timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

# ============================================================
# 测试接口列表
# ============================================================
TEST_ENDPOINTS = [
    {
        "name": "📦 订单列表",
        "endpoint": "/api/open/order/list",
        "method": "POST",
        "params": {"method": "temu.order.list.get", "page": 1, "page_size": 10},
    },
    {
        "name": "🏪 店铺指标",
        "endpoint": "/api/open/shop/metrics",
        "method": "POST",
        "params": {
            "method": "temu.shop.metrics.get",
            "date_from": "2026-05-01",
            "date_to": "2026-05-15",
        },
    },
    {
        "name": "📋 核价通知列表",
        "endpoint": "/api/open/pricing/notice/list",
        "method": "POST",
        "params": {"method": "temu.pricing.notice.list", "page": 1, "page_size": 10},
    },
    {
        "name": "💰 结算列表",
        "endpoint": "/api/open/settlement/list",
        "method": "POST",
        "params": {
            "method": "temu.settlement.list.get",
            "date_from": "2026-05-01",
            "date_to": "2026-05-15",
            "page": 1,
        },
    },
    {
        "name": "📦 库存查询",
        "endpoint": "/api/open/inventory/get",
        "method": "POST",
        "params": {"method": "temu.inventory.get", "sku_codes": "[]"},
    },
    {
        "name": "🎯 活动列表",
        "endpoint": "/api/open/activity/list",
        "method": "POST",
        "params": {"method": "temu.activity.list.get", "page": 1},
    },
    {
        "name": "💬 消息列表",
        "endpoint": "/api/open/message/list",
        "method": "POST",
        "params": {"method": "temu.message.list.get", "page": 1, "page_size": 10},
    },
    # === 备选路径（有些平台的路径可能是 /api/rest/ 格式）===
    {
        "name": "📦 订单列表(备选路径1)",
        "endpoint": "/api/rest/order/list",
        "method": "POST",
        "params": {"method": "temu.order.list.get", "page": 1, "page_size": 10},
    },
    {
        "name": "📦 订单列表(备选路径2)",
        "endpoint": "/api/open/order/list/get",
        "method": "POST",
        "params": {"method": "temu.order.list.get", "page": 1, "page_size": 10},
    },
]

# ============================================================
# HTTP 请求
# ============================================================
def try_request(url: str, payload: dict, method: str = "POST") -> dict:
    """用 urllib 尝试发送请求，不依赖第三方库"""
    import urllib.request
    import urllib.error

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data if method == "POST" else None,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            return {
                "status": resp.status,
                "headers": dict(resp.headers),
                "body_text": body[:3000],
                "body_json": _try_parse_json(body),
                "error": None,
            }
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {
            "status": e.code,
            "headers": dict(e.headers),
            "body_text": body[:3000],
            "body_json": _try_parse_json(body),
            "error": f"HTTP {e.code}: {e.reason}",
        }
    except urllib.error.URLError as e:
        return {
            "status": 0,
            "headers": {},
            "body_text": "",
            "body_json": None,
            "error": f"网络错误: {e.reason}",
        }
    except Exception as e:
        return {
            "status": 0,
            "headers": {},
            "body_text": "",
            "body_json": None,
            "error": f"请求异常: {e}",
        }


def _try_parse_json(text: str):
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None


# ============================================================
# 主测试流程
# ============================================================
def main():
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  Temu 开放平台 API 连通性测试{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"\n  APP_KEY:    {APP_KEY[:8]}...{APP_KEY[-4:] if len(APP_KEY) > 12 else ''}")
    print(f"  API基础地址: {API_BASE_URL}")
    print(f"  测试时间:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if APP_KEY.startswith("请填入") or APP_SECRET.startswith("请填入"):
        print(f"\n{RED}{BOLD}  ⚠️  请先设置 API 凭证！{RESET}")
        print(f"\n  方法一（推荐）：设置环境变量")
        print(f"    set TEMU_APP_KEY=你的app_key")
        print(f"    set TEMU_APP_SECRET=你的app_secret")
        print(f"    python test_temu_api.py")
        print(f"\n  方法二：直接修改本文件顶部 APP_KEY / APP_SECRET 变量")
        sys.exit(1)

    # === 第1步：网络连通性 ===
    section("第1步：网络连通性检查")
    import socket
    hostname = API_BASE_URL.replace("https://", "").replace("http://", "").split("/")[0]
    try:
        ip = socket.gethostbyname(hostname)
        ok(f"DNS 解析成功: {hostname} → {ip}")
    except socket.gaierror as e:
        fail(f"DNS 解析失败: {e}")
        info("请检查服务器能否访问外网，或需要配置代理")
        sys.exit(1)

    # === 第2步：接口探测（用最简单的方法试基础连通性）===
    section("第2步：接口基础探测")

    base_params = {
        "app_key": APP_KEY,
        "timestamp": get_timestamp(),
    }

    first_endpoint = TEST_ENDPOINTS[0]
    url = f"{API_BASE_URL}{first_endpoint['endpoint']}"
    info(f"测试接口: {url}")

    test_results = []

    for sign_name, sign_func in SIGN_METHODS:
        params = {**base_params, **first_endpoint["params"]}
        sign = sign_func(params, APP_SECRET)
        params["sign"] = sign
        result = try_request(url, params, first_endpoint["method"])

        status = result["status"]
        body_json = result["body_json"]
        body_text = result["body_text"]

        if status == 200 and body_json and body_json.get("success"):
            ok(f"[{sign_name}] 签名通过! 返回: {json.dumps(body_json, ensure_ascii=False)[:200]}")
            test_results.append(("pass", sign_name, result))
        elif status == 200:
            info(f"[{sign_name}] 请求成功但返回异常: {body_text[:150]}")
            test_results.append(("unknown", sign_name, result))
        elif status == 403 or status == 401:
            info(f"[{sign_name}] 认证失败(status={status}) — 可能是签名算法不对")
            test_results.append(("auth_fail", sign_name, result))
        elif status == 404:
            info(f"[{sign_name}] 路径不存在(status=404) — 接口地址可能不对")
            test_results.append(("not_found", sign_name, result))
        else:
            info(f"[{sign_name}] status={status}: {result['error'] or body_text[:100]}")
            test_results.append(("error", sign_name, result))

    # === 第3步：如果找到了签名算法，用它对所有接口做批量测试 ===
    best_method = None
    for status, name, result in test_results:
        if status == "pass":
            best_method = name
            break

    if best_method:
        section(f"第3步：用「{best_method}」批量测试所有接口")

        base_params = {
            "app_key": APP_KEY,
            "timestamp": get_timestamp(),
        }
        _, sign_func = next((n, f) for n, f in SIGN_METHODS if n == best_method)

        success_count = 0
        fail_count = 0

        for ep in TEST_ENDPOINTS:
            url = f"{API_BASE_URL}{ep['endpoint']}"
            params = {**base_params, **ep["params"]}
            sign = sign_func(params, APP_SECRET)
            params["sign"] = sign

            result = try_request(url, params, ep["method"])
            status = result["status"]
            body_json = result["body_json"]

            if status == 200:
                ok(f"{ep['name']} → 200 OK")
                success_count += 1
            else:
                fail(f"{ep['name']} → {result['error'] or 'status='+str(status)}")
                fail_count += 1

            if body_json:
                print(f"           响应首部: {json.dumps(body_json, ensure_ascii=False)[:300]}")

        print(f"\n  结果: {GREEN}{success_count}个通过{RESET}, {RED}{fail_count}个失败{RESET}")

    # === 第4步：打印原始响应示例 ===
    section("第4步：原始响应示例")

    if test_results:
        for status, name, result in test_results[:2]:
            print(f"\n{YELLOW}--- 签名方式: {name} ---{RESET}")
            print(f"  HTTP状态码: {result['status']}")
            if result["error"]:
                print(f"  错误: {result['error']}")
            if result["body_json"]:
                print(f"  JSON响应（格式化）:")
                print(json.dumps(result["body_json"], indent=2, ensure_ascii=False)[:2000])
            elif result["body_text"]:
                print(f"  原始响应（截取）:")
                print(f"  {result['body_text'][:1000]}")

    # === 总结 ===
    section("测试总结")

    has_any_200 = any(r["status"] == 200 for _, _, r in test_results)
    has_any_pass = any(s == "pass" for s, _, _ in test_results)

    if has_any_pass:
        print(f"  {GREEN}{BOLD}🎉 连通成功！{RESET}")
        print(f"  {GREEN}可用签名算法: {best_method}{RESET}")
        info("现在可以可信地继续开发了。建议:")
        info("1. 将找到的签名算法更新到 common/temu_client.py")
        info("2. 根据实际返回的 JSON 结构调整数据库字段")
        info("3. 逐个验证所有需要的接口")
    elif has_any_200:
        print(f"  {YELLOW}{BOLD}⚠️  部分接口能通，但签名算法需要调整{RESET}")
        info("检查返回体中是否有错误码和说明")
    else:
        print(f"  {RED}{BOLD}❌ 所有尝试均未成功{RESET}")
        info("可能的原因：")
        info("1. API 基础域名不对（当前: {})".format(API_BASE_URL))
        info("2. 接口路径格式不对（当前: {})".format(first_endpoint['endpoint']))
        info("3. 签名算法完全不同（如 RSA、国密等）")
        info("4. 凭证无效或已过期")
        info("5. 需要 IP 白名单或额外鉴权头")
        print(f"\n  建议拿到 Temu 开放平台的官方文档后，核对:")
        print(f"    - 基础域名")
        print(f"    - 签名算法")
        print(f"    - 参数格式（JSON body vs URL encoded vs form-data）")


if __name__ == "__main__":
    main()
