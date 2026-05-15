import psutil
import httpx
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "cpu_threshold": 80.0,
    "cpu_critical_threshold": 95.0,
    "memory_threshold": 85.0,
    "memory_critical_mb": 200,
    "disk_threshold": 90.0,
    "disk_critical_threshold": 98.0,
    "critical_processes": [],
    "check_interval": 30,
    "alert_cooldown_seconds": 300,
    "alert_ttl_seconds": 3600,
    "notification_webhook": None,
    "enable_multi_platform_notifications": True,
    "health_score_weights": {
        "cpu": 0.3,
        "memory": 0.3,
        "disk": 0.2,
        "processes": 0.2
    }
}


class ServerMonitor:
    def __init__(self, config: Optional[Dict] = None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.alerts: List[Dict] = []
        self._last_alert_times: Dict[str, datetime] = {}
        
        if self.config.get("enable_multi_platform_notifications", True):
            try:
                from modules.server_monitor.notifications import NotificationManager
                self.notification_manager = NotificationManager()
            except Exception as e:
                logger.warning(f"无法初始化通知管理器: {e}")
                self.notification_manager = None
        else:
            self.notification_manager = None

    async def check_cpu(self) -> Dict[str, Any]:
        usage = psutil.cpu_percent(interval=1)
        threshold = self.config["cpu_threshold"]
        critical_threshold = self.config.get("cpu_critical_threshold", 95.0)

        if usage >= critical_threshold:
            status = "critical"
            alert_triggered = True
            message = f"CPU使用率严重超标: {usage}% (临界值:{critical_threshold}%)"
        elif usage >= threshold:
            status = "warning"
            alert_triggered = True
            message = f"CPU使用率偏高: {usage}% (阈值:{threshold}%)"
        else:
            status = "normal"
            alert_triggered = False
            message = f"CPU使用率正常: {usage}%"

        if alert_triggered:
            self.create_alert("cpu", status, message, usage, threshold)

        return {
            "status": status,
            "usage": usage,
            "alert_triggered": alert_triggered,
            "message": message,
            "timestamp": datetime.now()
        }

    async def check_memory(self) -> Dict[str, Any]:
        memory = psutil.virtual_memory()
        usage_percent = memory.percent
        threshold = self.config["memory_threshold"]
        critical_mb = self.config.get("memory_critical_mb", 200)
        available_mb = memory.available / (1024 * 1024)

        if available_mb <= critical_mb:
            status = "critical"
            alert_triggered = True
            message = f"内存严重不足: 可用 {available_mb:.1f}MB < {critical_mb}MB"
        elif usage_percent >= threshold:
            status = "warning"
            alert_triggered = True
            message = f"内存使用率偏高: {usage_percent:.1f}% (阈值:{threshold}%)"
        else:
            status = "normal"
            alert_triggered = False
            message = f"内存使用率正常: {usage_percent:.1f}%"

        if alert_triggered:
            self.create_alert("memory", status, message, usage_percent, threshold)

        return {
            "status": status,
            "usage_percent": usage_percent,
            "available_mb": available_mb,
            "total_mb": memory.total / (1024 * 1024),
            "alert_triggered": alert_triggered,
            "message": message,
            "timestamp": datetime.now()
        }

    async def check_disk(self, path: str = "/") -> Dict[str, Any]:
        disk = psutil.disk_usage(path)
        usage_percent = disk.percent
        threshold = self.config["disk_threshold"]
        critical_threshold = self.config.get("disk_critical_threshold", 98.0)
        free_gb = disk.free / (1024 ** 3)
        total_gb = disk.total / (1024 ** 3)

        if usage_percent >= critical_threshold:
            status = "critical"
            alert_triggered = True
            message = f"磁盘空间严重不足: {usage_percent:.1f}% (临界值:{critical_threshold}%)"
        elif usage_percent >= threshold:
            status = "warning"
            alert_triggered = True
            message = f"磁盘使用率偏高: {usage_percent:.1f}% (阈值:{threshold}%)"
        else:
            status = "normal"
            alert_triggered = False
            message = f"磁盘使用率正常: {usage_percent:.1f}%"

        if alert_triggered:
            self.create_alert("disk", status, message, usage_percent, threshold)

        return {
            "status": status,
            "usage_percent": usage_percent,
            "free_gb": free_gb,
            "total_gb": total_gb,
            "path": path,
            "alert_triggered": alert_triggered,
            "message": message,
            "timestamp": datetime.now()
        }

    async def check_processes(self) -> Dict[str, Dict]:
        critical_processes = self.config.get("critical_processes", [])
        results = {}

        running_processes = set()
        try:
            for proc in psutil.process_iter(['name']):
                try:
                    running_processes.add(proc.info['name'].lower())
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.error(f"获取进程列表失败: {e}")

        for proc_name in critical_processes:
            is_running = proc_name.lower() in running_processes
            if is_running:
                results[proc_name] = {
                    "status": "running",
                    "alert_triggered": False,
                    "message": f"{proc_name} 运行正常"
                }
            else:
                results[proc_name] = {
                    "status": "missing",
                    "alert_triggered": True,
                    "message": f"关键进程 {proc_name} 未运行!"
                }
                self.create_alert("process", "critical", results[proc_name]["message"], 0, 1)

        return results

    async def check_network(self) -> Dict[str, Any]:
        """检查网络连接状态和流量使用情况"""
        network_info = {}

        try:
            # 获取网络IO统计
            net_io = psutil.net_io_counters()
            network_info["bytes_sent"] = net_io.bytes_sent
            network_info["bytes_recv"] = net_io.bytes_recv
            network_info["packets_sent"] = net_io.packets_sent
            network_info["packets_recv"] = net_io.packets_recv
            network_info["errors_in"] = net_io.errin
            network_info["errors_out"] = net_io.errout
            network_info["drops_in"] = net_io.dropin
            network_info["drops_out"] = net_io.dropout

            # 获取网络接口信息
            net_connections = psutil.net_if_addrs()
            interfaces = []
            for interface_name, addrs in net_connections.items():
                iface_info = {"name": interface_name, "addresses": []}
                for addr in addrs:
                    iface_info["addresses"].append({
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast if hasattr(addr, 'broadcast') else None
                    })
                interfaces.append(iface_info)
            network_info["interfaces"] = interfaces

            # 获取网络连接数
            connections = psutil.net_connections(kind='inet')
            network_info["active_connections"] = len([c for c in connections if c.status == 'ESTABLISHED'])
            network_info["listening_ports"] = len([c for c in connections if c.status == 'LISTEN'])
            network_info["total_connections"] = len(connections)

            # 检查关键端口是否在监听
            critical_ports = self.config.get("critical_ports", [80, 443, 3306, 8501])
            listening = {c.laddr.port for c in connections if c.status == 'LISTEN' and c.laddr}
            missing_ports = [p for p in critical_ports if p not in listening]

            if missing_ports:
                status = "warning"
                alert_triggered = True
                message = f"关键端口未监听: {missing_ports}"
                self.create_alert("network", "warning", message, len(missing_ports), 0)
            else:
                status = "normal"
                alert_triggered = False
                message = "所有关键端口正常监听"

            # 网络错误率检查
            total_packets = net_io.packets_sent + net_io.packets_recv
            if total_packets > 0:
                error_rate = (net_io.errin + net_io.errout) / total_packets * 100
                network_info["error_rate"] = round(error_rate, 4)

                error_threshold = self.config.get("network_error_threshold", 1.0)
                if error_rate > error_threshold:
                    status = "warning"
                    alert_triggered = True
                    message = f"网络错误率偏高: {error_rate:.2f}% (阈值: {error_threshold}%)"
                    self.create_alert("network", "warning", message, error_rate, error_threshold)

            network_info.update({
                "status": status,
                "alert_triggered": alert_triggered,
                "message": message,
                "timestamp": datetime.now(),
                "critical_ports": critical_ports,
                "missing_ports": missing_ports if missing_ports else []
            })

        except Exception as e:
            logger.error(f"网络检查失败: {e}")
            network_info = {
                "status": "error",
                "alert_triggered": True,
                "message": f"网络检查异常: {str(e)}",
                "timestamp": datetime.now(),
                "error": str(e)
            }
            self.create_alert("network", "critical", network_info["message"], 0, 0)

        return network_info

    async def check_dns_resolution(self, hostname: str = "www.baidu.com") -> Dict[str, Any]:
        """检查DNS解析是否正常"""
        import socket

        try:
            start_time = datetime.now()
            ip_address = socket.gethostbyname(hostname)
            resolve_time = (datetime.now() - start_time).total_seconds() * 1000

            dns_threshold_ms = self.config.get("dns_resolve_threshold_ms", 1000)

            if resolve_time > dns_threshold_ms:
                status = "warning"
                alert_triggered = True
                message = f"DNS解析缓慢: {resolve_time:.0f}ms > {dns_threshold_ms}ms"
                self.create_alert("dns", "warning", message, resolve_time, dns_threshold_ms)
            else:
                status = "normal"
                alert_triggered = False
                message = f"DNS解析正常: {resolve_time:.0f}ms"

            return {
                "hostname": hostname,
                "ip_address": ip_address,
                "resolve_time_ms": round(resolve_time, 2),
                "status": status,
                "alert_triggered": alert_triggered,
                "message": message,
                "timestamp": datetime.now()
            }

        except socket.gaierror as e:
            error_msg = f"DNS解析失败: {hostname} - {str(e)}"
            logger.error(error_msg)
            self.create_alert("dns", "critical", error_msg, 0, 0)
            return {
                "hostname": hostname,
                "ip_address": None,
                "resolve_time_ms": None,
                "status": "critical",
                "alert_triggered": True,
                "message": error_msg,
                "timestamp": datetime.now(),
                "error": str(e)
            }
        except Exception as e:
            error_msg = f"DNS检查异常: {str(e)}"
            logger.error(error_msg)
            return {
                "hostname": hostname,
                "ip_address": None,
                "resolve_time_ms": None,
                "status": "error",
                "alert_triggered": True,
                "message": error_msg,
                "timestamp": datetime.now(),
                "error": str(e)
            }

    def create_alert(
        self,
        alert_type: str,
        level: str,
        message: str,
        metric_value: float,
        threshold: float
    ) -> Optional[Dict]:
        alert_key = f"{alert_type}_{level}"

        cooldown = self.config.get("alert_cooldown_seconds", 300)
        if alert_key in self._last_alert_times:
            last_time = self._last_alert_times[alert_key]
            if datetime.now() - last_time < timedelta(seconds=cooldown):
                return None

        alert = {
            "type": alert_type,
            "level": level,
            "message": message,
            "metric_value": metric_value,
            "threshold": threshold,
            "timestamp": datetime.now(),
            "acknowledged": False
        }

        self.alerts.append(alert)
        self._last_alert_times[alert_key] = datetime.now()

        logger.warning(f"[{level.upper()}] {message}")
        return alert

    def get_active_alerts(self) -> List[Dict]:
        ttl = self.config.get("alert_ttl_seconds", 3600)
        cutoff = datetime.now() - timedelta(seconds=ttl)
        active = [a for a in self.alerts if a["timestamp"] > cutoff and not a["acknowledged"]]
        return sorted(active, key=lambda x: {"critical": 0, "warning": 1, "info": 2}.get(x["level"], 3))

    def clear_expired_alerts(self) -> int:
        ttl = self.config.get("alert_ttl_seconds", 3600)
        cutoff = datetime.now() - timedelta(seconds=ttl)
        before_count = len(self.alerts)
        self.alerts = [a for a in self.alerts if a["timestamp"] > cutoff]
        return before_count - len(self.alerts)

    def format_notification(self, alert: Dict) -> Dict:
        level_emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}
        emoji = level_emoji.get(alert["level"], "⚪")

        title = f"[{alert['level'].upper()}] {emoji} 服务器告警 - {alert['type'].upper()}"
        content = (
            f"**告警类型**: {alert['type']}\n"
            f"**级别**: {alert['level']}\n"
            f"**消息**: {alert['message']}\n"
            f"**当前值**: {alert['metric_value']}\n"
            f"**阈值**: {alert['threshold']}\n"
            f"**时间**: {alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"
        )

        priority = "high" if alert["level"] == "critical" else "medium"

        return {
            "title": title,
            "content": content,
            "priority": priority,
            "alert": alert
        }

    async def send_notification(self, alert: Dict) -> Dict:
        if self.notification_manager and self.config.get("enable_multi_platform_notifications", True):
            try:
                results = await self.notification_manager.send_alert(alert)
                success_count = sum(1 for r in results.values() if r.get("success"))
                total_count = len(results)
                
                if success_count > 0:
                    logger.info(f"告警已发送到 {success_count}/{total_count} 个平台")
                    return {
                        "success": True,
                        "message": f"成功发送到 {success_count}/{total_count} 个平台",
                        "details": results
                    }
                else:
                    logger.error(f"所有平台发送失败: {results}")
                    return {
                        "success": False,
                        "error": "所有平台发送失败",
                        "details": results
                    }
            except Exception as e:
                logger.error(f"多平台通知失败，回退到单 Webhook: {e}")
        
        webhook_url = self.config.get("notification_webhook")
        if not webhook_url:
            return {"success": False, "error": "未配置通知 Webhook"}

        notification = self.format_notification(alert)

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    webhook_url,
                    json={
                        "title": notification["title"],
                        "content": notification["content"],
                        "priority": notification["priority"]
                    }
                )

                if response.status_code == 200:
                    logger.info(f"告警通知发送成功: {notification['title']}")
                    return {"success": True, "response": "通知已发送"}
                else:
                    logger.error(f"告警通知发送失败: HTTP {response.status_code}")
                    return {"success": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"发送告警通知异常: {e}")
            return {"success": False, "error": str(e)}

    async def calculate_health_score(self) -> float:
        weights = self.config.get("health_score_weights", {})
        scores = []

        cpu_result = await self.check_cpu()
        cpu_score = 100 if cpu_result["status"] == "normal" else (50 if cpu_result["status"] == "warning" else 0)
        scores.append(("cpu", cpu_score, weights.get("cpu", 0.25)))

        mem_result = await self.check_memory()
        mem_score = 100 if mem_result["status"] == "normal" else (50 if mem_result["status"] == "warning" else 0)
        scores.append(("memory", mem_score, weights.get("memory", 0.25)))

        disk_result = await self.check_disk()
        disk_score = 100 if disk_result["status"] == "normal" else (50 if disk_result["status"] == "warning" else 0)
        scores.append(("disk", disk_score, weights.get("disk", 0.25)))

        proc_results = await self.check_processes()
        if proc_results:
            proc_running = sum(1 for p in proc_results.values() if p["status"] == "running")
            proc_score = (proc_running / len(proc_results)) * 100
        else:
            proc_score = 100
        scores.append(("processes", proc_score, weights.get("processes", 0.25)))

        total_weighted_score = sum(score * weight for _, score, weight in scores)
        total_weight = sum(weight for _, _, weight in scores)

        return total_weighted_score / total_weight if total_weight > 0 else 100.0

    async def run_full_check(self) -> Dict:
        logger.info("开始执行完整服务器健康检查...")

        cpu_result = await self.check_cpu()
        memory_result = await self.check_memory()
        disk_result = await self.check_disk("/")
        process_results = await self.check_processes()
        network_result = await self.check_network()
        dns_result = await self.check_dns_resolution()

        health_score = await self.calculate_health_score()

        if health_score >= 90:
            overall_status = "healthy"
        elif health_score >= 70:
            overall_status = "degraded"
        elif health_score >= 50:
            overall_status = "warning"
        else:
            overall_status = "critical"

        active_alerts = self.get_active_alerts()

        report = {
            "timestamp": datetime.now().isoformat(),
            "status": overall_status,
            "health_score": round(health_score, 2),
            "metrics": {
                "cpu": cpu_result,
                "memory": memory_result,
                "disk": disk_result,
                "processes": process_results,
                "network": network_result,
                "dns": dns_result
            },
            "alerts": active_alerts,
            "alert_count": len(active_alerts),
            "config_summary": {
                "cpu_threshold": self.config["cpu_threshold"],
                "memory_threshold": self.config["memory_threshold"],
                "disk_threshold": self.config["disk_threshold"]
            }
        }

        logger.info(f"检查完成 | 状态: {overall_status} | 评分: {health_score:.1f} | 告警数: {len(active_alerts)}")

        return report
