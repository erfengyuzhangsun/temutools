#!/usr/bin/env python3
"""
Temu开放平台 API 连通性测试工具（v2 — 基于真实API规范）
独立脚本，不依赖项目其他代码，拿真实凭证一键测试

用法:
    set TEMU_APP_KEY=你的app_key
    set TEMU_APP_SECRET=你的app_secret
    set TEMU_ACCESS_TOKEN=卖家的access_token
    python test_temu_api.py
"""

import hashlib
import json
import os
import sys
import time
import urllib.request
import urllib.error
import socket
from datetime import datetime

APP_KEY = os.environ.get("TEMU_APP_KEY", "请填入你的app_key")
APP_SECRET = os.environ.get("TEMU_APP_SECRET", "请填入你的app_secret")
ACCESS_TOKEN = os.environ.get("TEMU_ACCESS_TOKEN", "请填入你的access_token")
API_BASE_URL = os.environ.get("TEMU_API_BASE", "https://openapi-b-global.temu.com")

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


def sign(params: dict, secret: str) -> str:
    sorted_params = dict(sorted(params.items()))
    sign_str = secret
    for key, value in sorted_params.items():
        if value is not None:
            sign_str += f"{key}{value}"
    sign_str += secret
    return hashlib.md5(sign_str.encode("utf-8")).hexdigest().upper()


TEST_ENDPOINTS = [
    {"name": "📦 订单列表", "type": "bg.order.list.get",
     "params": {"pageSize": 10, "pageNumber": 1}},
    {"name": "🎯 活动列表", "type": "bg.promotion.activity.query",
     "params": {"pageSize": 10, "pageNumber": 1}},
    {"name": "💰 结算列表", "type": "bg.settlement.list.get",
     "params": {"dateFrom": "2026-05-01", "dateTo": "2026-05-15", "page": 1}},
    {"name": "📋 核价通知", "type": "bg.pricing.notice.list",
     "params": {"pageSize": 10, "page": 1}},
    {"name": "📦 订单详情", "type": "bg.order.detail.get",
     "params": {"parentOrderSn": "test"}},
]


def make_request(api_type: str, extra_params: dict = None) -> dict:
    body = {
        "type": api_type,
        "app_key": APP_KEY,
        "access_token": ACCESS_TOKEN,
        "timestamp": round(time.time()),
        "data_type": "JSON",
    }
    if extra_params:
        body.update(extra_params)
    body["sign"] = sign(body, APP_SECRET)
    url = f"{API_BASE_URL}/openapi/router"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json;charset=UTF-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body_text = resp.read().decode("utf-8")
            return {
                "status": resp.status,
                "body_text": body_text[:3000],
                "body_json": _try_parse(body_text),
                "error": None,
            }
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        return {"status": e.code, "body_text": body_text[:2000], "body_json": _try_parse(body_text), "error": f"HTTP {e.code}"}
    except urllib.error.URLError as e:
        return {"status": 0, "body_text": "", "body_json": None, "error": f"网络错误: {e.reason}"}
    except Exception as e:
        return {"status": 0, "body_text": "", "body_json": None, "error": f"异常: {e}"}


def _try_parse(text: str):
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None


def main():
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  Temu 开放平台 API 连通性测试 v2{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"\n  APP_KEY:     {APP_KEY[:8]}...{APP_KEY[-4:] if len(APP_KEY) > 12 else ''}")
    print(f"  API地址:     {API_BASE_URL}")
    print(f"  测试时间:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if "请填入" in APP_KEY or "请填入" in APP_SECRET or "请填入" in ACCESS_TOKEN:
        print(f"\n{RED}{BOLD}  ⚠️  请先设置 API 凭证！{RESET}")
        print(f"\n  设置环境变量：")
        print(f"    set TEMU_APP_KEY=你的app_key")
        print(f"    set TEMU_APP_SECRET=你的app_secret")
        print(f"    set TEMU_ACCESS_TOKEN=卖家的access_token")
        print(f"    python test_temu_api.py")
        sys.exit(1)

    section("第1步：DNS解析检查")
    hostname = API_BASE_URL.replace("https://", "").replace("http://", "").split("/")[0]
    try:
        ip = socket.gethostbyname(hostname)
        ok(f"DNS 解析成功: {hostname} → {ip}")
    except socket.gaierror as e:
        fail(f"DNS 解析失败: {e}")
        sys.exit(1)

    section("第2步：签名算法验证")
    test_body = {
        "type": "bg.open.accesstoken.info.get",
        "app_key": APP_KEY,
        "access_token": ACCESS_TOKEN,
        "timestamp": round(time.time()),
        "data_type": "JSON",
    }
    test_body["sign"] = sign(test_body, APP_SECRET)
    result = make_request("bg.open.accesstoken.info.get")
    if result["status"] == 200 and result["body_json"]:
        api_success = result["body_json"].get("success", False)
        error_code = result["body_json"].get("errorCode", 0)
        if api_success or error_code == 1000000:
            ok("签名算法正确！MD5 + k/v拼接")
        else:
            info(f"请求成功但返回业务错误: {result['body_json'].get('errorMsg', '')}")
    else:
        result_text = result["body_text"][:300]
        fail(f"请求失败 (status={result['status']}): {result_text}")

    section("第3步：批量测试接口")
    success_count = 0
    fail_count = 0
    for ep in TEST_ENDPOINTS:
        result = make_request(ep["type"], ep["params"])
        j = result["body_json"]
        if result["status"] == 200 and j:
            api_ok = j.get("success", False) or j.get("errorCode") == 1000000
            if api_ok:
                ok(f"{ep['name']} → {ep['type']}")
                success_count += 1
            else:
                info(f"{ep['name']} → 业务错误: {j.get('errorMsg', '')}")
                fail_count += 1
        else:
            fail(f"{ep['name']} → {result['error'] or 'status='+str(result['status'])}")
            fail_count += 1

    print(f"\n  结果: {GREEN}{success_count}个通过{RESET}, {RED}{fail_count}个失败{RESET}")

    section("第4步：原始响应示例")
    last_ok = None
    for ep in TEST_ENDPOINTS:
        result = make_request(ep["type"], ep["params"])
        if result["body_json"]:
            last_ok = result["body_json"]
            break
    if last_ok:
        print(json.dumps(last_ok, indent=2, ensure_ascii=False)[:2000])

    section("测试总结")
    if success_count > 0:
        print(f"  {GREEN}{BOLD}🎉 连通成功！{RESET}")
        print(f"  {GREEN}正确签名: MD5 + k/v拼接{RESET}")
        info("API对接已验证通过，可以继续开发。")
    else:
        print(f"  {RED}{BOLD}❌ 所有接口均未通过{RESET}")
        info("可能原因：")
        info(f"1. 基础域名不对（当前: {API_BASE_URL}），试试 --global/--us/--eu")
        info("2. app_key / app_secret / access_token 无效")
        info("3. 签名算法不同（试试HMAC-SHA256等）")
        info("4. 需要IP白名单")


if __name__ == "__main__":
    main()
