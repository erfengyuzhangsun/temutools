import os
from typing import Dict, Optional, List
from dataclasses import dataclass
import json

@dataclass
class WebhookConfig:
    url: str
    secret: Optional[str] = None
    headers: Optional[Dict] = None
    enabled: bool = True

class NotificationManager:
    SUPPORTED_PLATFORMS = {
        "dingtalk": {
            "name": "钉钉机器人",
            "template": {
                "msgtype": "markdown",
                "markdown": {
                    "title": "{title}",
                    "text": "{content}"
                }
            }
        },
        "wechat_work": {
            "name": "企业微信",
            "template": {
                "msgtype": "markdown",
                "markdown": {
                    "content": "{content}"
                }
            }
        },
        "feishu": {
            "name": "飞书",
            "template": {
                "msg_type": "interactive",
                "card": {
                    "header": {
                        "title": {"tag": "plain_text", "content": "{title}"},
                        "template": "{color}"
                    },
                    "elements": [
                        {"tag": "markdown", "content": "{content}"}
                    ]
                }
            }
        },
        "generic": {
            "name": "通用Webhook",
            "template": {
                "title": "{title}",
                "content": "{content}",
                "priority": "{priority}",
                "timestamp": "{timestamp}"
            }
        }
    }

    def __init__(self):
        self.webhooks: Dict[str, WebhookConfig] = {}
        self._load_from_env()

    def _load_from_env(self):
        dingtalk_webhook = os.getenv("DINGTALK_WEBHOOK_URL")
        if dingtalk_webhook:
            self.add_webhook("dingtalk", dingtalk_webhook)

        wechat_webhook = os.getenv("WECHAT_WORK_WEBHOOK_URL")
        if wechat_webhook:
            self.add_webhook("wechat_work", wechat_webhook)

        feishu_webhook = os.getenv("FEISHU_WEBHOOK_URL")
        if feishu_webhook:
            self.add_webhook("feishu", feishu_webhook)

        generic_webhook = os.getenv("GENERIC_WEBHOOK_URL")
        if generic_webhook:
            self.add_webhook("generic", generic_webhook)

    def add_webhook(self, platform: str, url: str, secret: Optional[str] = None):
        if platform not in self.SUPPORTED_PLATFORMS:
            raise ValueError(f"不支持的平台: {platform}. 支持: {list(self.SUPPORTED_PLATFORMS.keys())}")

        self.webhooks[platform] = WebhookConfig(
            url=url,
            secret=secret,
            enabled=True
        )

    def remove_webhook(self, platform: str):
        if platform in self.webhooks:
            del self.webhooks[platform]

    def enable_webhook(self, platform: str):
        if platform in self.webhooks:
            self.webhooks[platform].enabled = True

    def disable_webhook(self, platform: str):
        if platform in self.webhooks:
            self.webhooks[platform].enabled = False

    def get_active_webhooks(self) -> Dict[str, WebhookConfig]:
        return {k: v for k, v in self.webhooks.items() if v.enabled}

    def format_alert_for_platform(self, alert: Dict, platform: str) -> Dict:
        if platform not in self.SUPPORTED_PLATFORMS:
            raise ValueError(f"不支持的平台: {platform}")

        platform_config = self.SUPPORTED_PLATFORMS[platform]
        template = platform_config["template"]

        level_emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}
        emoji = level_emoji.get(alert.get("level", "info"), "⚪")

        title = f"[{alert.get('level', 'INFO').upper()}] {emoji} 服务器告警 - {alert.get('type', 'UNKNOWN').upper()}"
        
        content = (
            f"## {title}\n\n"
            f"**告警类型**: {alert.get('type', 'N/A')}\n"
            f"**级别**: {alert.get('level', 'N/A')}\n"
            f"**消息**: {alert.get('message', 'N/A')}\n"
            f"**当前值**: {alert.get('metric_value', 'N/A')}\n"
            f"**阈值**: {alert.get('threshold', 'N/A')}\n"
            f"**时间**: {alert.get('timestamp', 'N/A')}\n\n"
            f"---\n"
            f"*来自 Temu 运营平台云主机监控系统*"
        )

        color_map = {
            "critical": "#FF0000",
            "warning": "#FFA500",
            "info": "#1890FF"
        }

        formatted = {}
        for key, value in template.items():
            if isinstance(value, str):
                formatted[key] = value.format(
                    title=title,
                    content=content,
                    priority=alert.get('level', 'info'),
                    timestamp=str(alert.get('timestamp', '')),
                    color=color_map.get(alert.get('level', 'info'), '#1890FF')
                )
            elif isinstance(value, dict):
                formatted[key] = self._format_dict(value, title, content, alert)

        return formatted

    def _format_dict(self, template_dict: Dict, title: str, content: str, alert: Dict) -> Dict:
        result = {}
        for key, value in template_dict.items():
            if isinstance(value, str):
                result[key] = value.format(
                    title=title,
                    content=content,
                    priority=alert.get('level', 'info'),
                    timestamp=str(alert.get('timestamp', ''))
                )
            elif isinstance(value, dict):
                result[key] = self._format_dict(value, title, content, alert)
            elif isinstance(value, list):
                result[key] = [self._format_dict(item, title, content, alert) if isinstance(item, dict) else item for item in value]
            else:
                result[key] = value
        return result

    async def send_alert(self, alert: Dict) -> Dict[str, Dict]:
        import httpx
        results = {}

        active_webhooks = self.get_active_webhooks()
        if not active_webhooks:
            return {"error": "没有配置活跃的 Webhook"}

        for platform, config in active_webhooks.items():
            try:
                payload = self.format_alert_for_platform(alert, platform)
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                    if platform == "dingtalk" and config.secret:
                        import time
                        import hmac
                        import hashlib
                        import base64

                        timestamp = str(round(time.time() * 1000))
                        string_to_sign = f'{timestamp}\n{config.secret}'
                        hmac_code = hmac.new(
                            config.secret.encode('utf-8'),
                            string_to_sign.encode('utf-8'),
                            digestmod=hashlib.sha256
                        ).digest()
                        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
                        
                        response = await client.post(
                            config.url,
                            json=payload,
                            params={"timestamp": timestamp, "sign": sign}
                        )
                    else:
                        response = await client.post(config.url, json=payload)

                    if response.status_code == 200:
                        results[platform] = {
                            "success": True,
                            "message": f"{self.SUPPORTED_PLATFORMS[platform]['name']} 通知发送成功"
                        }
                    else:
                        results[platform] = {
                            "success": False,
                            "message": f"HTTP {response.status_code}: {response.text}"
                        }

            except Exception as e:
                results[platform] = {
                    "success": False,
                    "message": str(e)
                }

        return results

    def get_platform_info(self) -> Dict[str, Dict]:
        info = {}
        for platform, config in self.SUPPORTED_PLATFORMS.items():
            is_configured = platform in self.webhooks
            is_enabled = is_configured and self.webhooks[platform].enabled
            
            info[platform] = {
                "name": config["name"],
                "configured": is_configured,
                "enabled": is_enabled,
                "url": self.webhooks[platform].url if is_configured else None
            }
        return info

    def test_connection(self, platform: str) -> Dict:
        if platform not in self.webhooks:
            return {"success": False, "error": f"平台 {platform} 未配置"}

        config = self.webhooks[platform]
        test_alert = {
            "type": "test",
            "level": "info",
            "message": "这是一条测试消息，用于验证 Webhook 连接是否正常",
            "metric_value": 0,
            "threshold": 0,
            "timestamp": "测试时间"
        }

        return {"platform": platform, "config": config, "test_alert": test_alert}
