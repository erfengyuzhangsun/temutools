#!/usr/bin/env python3
"""
云主机监控守护进程 - 独立运行版本
用于后台持续监控服务器状态
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.server_monitor.service import ServerMonitor
from modules.server_monitor.notifications import NotificationManager
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def monitor_loop(check_interval: int = 30):
    """持续监控循环"""

    config = {
        "cpu_threshold": float(os.getenv("CPU_THRESHOLD", 80.0)),
        "memory_threshold": float(os.getenv("MEMORY_THRESHOLD", 85.0)),
        "disk_threshold": float(os.getenv("DISK_THRESHOLD", 90.0)),
        "check_interval": check_interval,
        "enable_multi_platform_notifications": True,
        "critical_processes": [
            p.strip() for p in os.getenv("CRITICAL_PROCESSES", "").split(",") if p.strip()
        ]
    }

    monitor = ServerMonitor(config=config)
    logger.info(f"监控服务启动 | 配置: {config}")

    consecutive_errors = 0
    max_consecutive_errors = 5

    while True:
        try:
            report = await monitor.run_full_check()

            # 如果有活跃告警，发送通知
            if report["alerts"]:
                logger.warning(f"发现 {len(report['alerts'])} 个活跃告警")
                for alert in report["alerts"][:3]:  # 最多发送前3个告警
                    await monitor.send_notification(alert)

            # 记录健康状态
            status_emoji = {"healthy": "✅", "degraded": "⚠️", "warning": "🟡", "critical": "🔴"}
            emoji = status_emoji.get(report["status"], "❓")

            logger.info(f"{emoji} 健康检查完成 | 评分: {report['health_score']:.1f} | 状态: {report['status']} | 告警数: {len(report['alerts'])}")

            consecutive_errors = 0

        except Exception as e:
            consecutive_errors += 1
            logger.error(f"监控检查失败 (连续错误: {consecutive_errors}/{max_consecutive_errors}): {e}")

            if consecutive_errors >= max_consecutive_errors:
                logger.critical(f"连续 {max_consecutive_errors} 次错误，发送严重告警")
                critical_alert = {
                    "type": "system",
                    "level": "critical",
                    "message": f"监控系统连续失败 {max_consecutive_errors} 次，请立即检查！",
                    "metric_value": consecutive_errors,
                    "threshold": max_consecutive_errors,
                    "timestamp": datetime.now()
                }
                try:
                    await monitor.send_notification(critical_alert)
                except:
                    pass
                consecutive_errors = 0

        await asyncio.sleep(check_interval)

if __name__ == "__main__":
    interval = int(os.getenv("MONITOR_INTERVAL", 30))
    logger.info(f"=== 云主机监控守护进程启动 === | 检查间隔: {interval}秒")

    try:
        asyncio.run(monitor_loop(interval))
    except KeyboardInterrupt:
        logger.info("监控服务停止 (用户中断)")
    except Exception as e:
        logger.critical(f"监控服务异常退出: {e}")
        sys.exit(1)
