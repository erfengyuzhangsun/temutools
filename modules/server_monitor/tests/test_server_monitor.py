import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import time

pytestmark = pytest.mark.asyncio


class TestServerMonitorInit:
    """测试服务器监控初始化"""

    def test_default_config(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor()
        assert monitor.config["cpu_threshold"] == 80.0
        assert monitor.config["memory_threshold"] == 85.0
        assert monitor.config["disk_threshold"] == 90.0
        assert len(monitor.alerts) == 0

    def test_custom_config(self):
        from modules.server_monitor.service import ServerMonitor
        custom_config = {
            "cpu_threshold": 70.0,
            "memory_threshold": 75.0,
            "disk_threshold": 80.0,
            "check_interval": 30
        }
        monitor = ServerMonitor(config=custom_config)
        assert monitor.config["cpu_threshold"] == 70.0
        assert monitor.config["check_interval"] == 30


class TestCPUMonitoring:
    """测试 CPU 监控功能"""

    async def test_cpu_normal(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor()
        with patch('psutil.cpu_percent', return_value=45.0):
            result = await monitor.check_cpu()
            assert result["status"] == "normal"
            assert result["usage"] == 45.0
            assert result["alert_triggered"] is False

    async def test_cpu_warning(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor(config={"cpu_threshold": 80.0})
        with patch('psutil.cpu_percent', return_value=82.0):
            result = await monitor.check_cpu()
            assert result["status"] == "warning"
            assert result["alert_triggered"] is True
            assert "CPU使用率" in result["message"]

    async def test_cpu_critical(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor(config={"cpu_threshold": 80.0, "cpu_critical_threshold": 95.0})
        with patch('psutil.cpu_percent', return_value=97.0):
            result = await monitor.check_cpu()
            assert result["status"] == "critical"
            assert result["alert_triggered"] is True


class TestMemoryMonitoring:
    """测试内存监控功能"""

    async def test_memory_normal(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor()
        mock_memory = Mock()
        mock_memory.percent = 60.0
        mock_memory.available = 3435973836
        mock_memory.total = 8589934592
        with patch('psutil.virtual_memory', return_value=mock_memory):
            result = await monitor.check_memory()
            assert result["status"] == "normal"
            assert result["usage_percent"] == 60.0
            assert result["alert_triggered"] is False

    async def test_memory_warning(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor(config={"memory_threshold": 85.0})
        mock_memory = Mock()
        mock_memory.percent = 88.0
        mock_memory.available = 1073741824
        mock_memory.total = 8589934592
        with patch('psutil.virtual_memory', return_value=mock_memory):
            result = await monitor.check_memory()
            assert result["status"] == "warning"
            assert result["alert_triggered"] is True

    async def test_memory_critical_low_available(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor(config={"memory_threshold": 85.0, "memory_critical_mb": 200})
        mock_memory = Mock()
        mock_memory.percent = 95.0
        mock_memory.available = 104857600
        mock_memory.total = 8589934592
        with patch('psutil.virtual_memory', return_value=mock_memory):
            result = await monitor.check_memory()
            assert result["status"] == "critical"


class TestDiskMonitoring:
    """测试磁盘监控功能"""

    async def test_disk_normal(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor()
        mock_disk = Mock()
        mock_disk.percent = 70.0
        mock_disk.free = 10737418240
        mock_disk.total = 107374182400
        with patch('psutil.disk_usage', return_value=mock_disk):
            result = await monitor.check_disk("/")
            assert result["status"] == "normal"
            assert result["usage_percent"] == 70.0
            assert result["alert_triggered"] is False

    async def test_disk_warning(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor(config={"disk_threshold": 90.0})
        mock_disk = Mock()
        mock_disk.percent = 92.0
        mock_disk.free = 8589934592
        mock_disk.total = 107374182400
        with patch('psutil.disk_usage', return_value=mock_disk):
            result = await monitor.check_disk("/")
            assert result["status"] == "warning"
            assert result["alert_triggered"] is True

    async def test_disk_critical(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor(config={"disk_threshold": 90.0, "disk_critical_threshold": 98.0})
        mock_disk = Mock()
        mock_disk.percent = 99.0
        mock_disk.free = 107374182
        mock_disk.total = 107374182400
        with patch('psutil.disk_usage', return_value=mock_disk):
            result = await monitor.check_disk("/")
            assert result["status"] == "critical"


class TestProcessMonitoring:
    """测试进程监控功能"""

    async def test_critical_process_running(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor(config={"critical_processes": ["nginx", "mysql"]})
        mock_proc = Mock()
        mock_proc.info = {'name': 'nginx'}
        with patch('psutil.process_iter', return_value=[mock_proc]):
            result = await monitor.check_processes()
            assert result["nginx"]["status"] == "running"
            assert result["mysql"]["status"] == "missing"

    async def test_all_processes_running(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor(config={"critical_processes": ["nginx"]})
        mock_proc = Mock()
        mock_proc.info = {'name': 'nginx'}
        with patch('psutil.process_iter', return_value=[mock_proc]):
            result = await monitor.check_processes()
            assert result["nginx"]["status"] == "running"
            assert result["nginx"]["alert_triggered"] is False

    async def test_critical_process_down_alert(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor(config={"critical_processes": ["redis"]})
        with patch('psutil.process_iter', return_value=[]):
            result = await monitor.check_processes()
            assert result["redis"]["status"] == "missing"
            assert result["redis"]["alert_triggered"] is True


class TestAlertManagement:
    """测试告警管理功能"""

    async def test_alert_creation(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor()
        alert = monitor.create_alert(
            alert_type="cpu",
            level="warning",
            message="CPU使用率达到85%",
            metric_value=85.0,
            threshold=80.0
        )
        assert alert["type"] == "cpu"
        assert alert["level"] == "warning"
        assert alert["message"] == "CPU使用率达到85%"
        assert "timestamp" in alert
        assert len(monitor.alerts) == 1

    async def test_alert_deduplication(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor(config={"alert_cooldown_seconds": 60})
        monitor.create_alert("cpu", "warning", "CPU高", 85.0, 80.0)
        alert2 = monitor.create_alert("cpu", "warning", "CPU高", 87.0, 80.0)
        assert alert2 is None
        assert len(monitor.alerts) == 1

    async def test_alert_after_cooldown(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor(config={"alert_cooldown_seconds": 0})
        monitor.create_alert("cpu", "warning", "CPU高", 85.0, 80.0)
        alert2 = monitor.create_alert("cpu", "warning", "CPU更高", 90.0, 80.0)
        assert alert2 is not None
        assert len(monitor.alerts) == 2

    async def test_get_active_alerts(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor()
        monitor.create_alert("cpu", "critical", "CPU极高", 98.0, 80.0)
        monitor.create_alert("memory", "warning", "内存高", 88.0, 85.0)
        active = monitor.get_active_alerts()
        assert len(active) == 2
        assert active[0]["level"] == "critical"

    async def test_clear_expired_alerts(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor(config={"alert_ttl_seconds": 3600})
        monitor.create_alert("cpu", "warning", "测试", 85.0, 80.0)
        with patch('modules.server_monitor.service.datetime') as mock_dt:
            mock_dt.now.return_value = datetime.now() + timedelta(hours=2)
            monitor.clear_expired_alerts()
            assert len(monitor.alerts) == 0


class TestNotificationSystem:
    """测试通知系统"""

    async def test_notification_format(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor()
        alert = {
            "type": "cpu",
            "level": "critical",
            "message": "CPU使用率98%",
            "metric_value": 98.0,
            "threshold": 80.0,
            "timestamp": datetime.now()
        }
        notification = monitor.format_notification(alert)
        assert "[CRITICAL]" in notification["title"]
        assert "CPU" in notification["title"]
        assert "98%" in notification["content"]
        assert notification["priority"] == "high"

    async def test_webhook_notification(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor(config={
            "notification_webhook": "https://example.com/webhook"
        })
        alert = monitor.create_alert("disk", "critical", "磁盘满", 99.0, 90.0)
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            result = await monitor.send_notification(alert)
            assert result["success"] is True
            mock_post.assert_called_once()

    async def test_notification_failure_handling(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor(config={
            "notification_webhook": "https://example.com/webhook"
        })
        alert = monitor.create_alert("cpu", "warning", "CPU高", 85.0, 80.0)
        with patch('httpx.AsyncClient.post', side_effect=Exception("Network error")):
            result = await monitor.send_notification(alert)
            assert result["success"] is False
            assert "error" in result


class TestHealthScore:
    """测试健康评分系统"""

    async def test_perfect_health_score(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor()
        with patch.object(monitor, 'check_cpu', return_value={"status": "normal"}), \
             patch.object(monitor, 'check_memory', return_value={"status": "normal"}), \
             patch.object(monitor, 'check_disk', return_value={"status": "normal"}), \
             patch.object(monitor, 'check_processes', return_value={}):
            score = await monitor.calculate_health_score()
            assert score >= 90

    async def test_degraded_health_score(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor()
        with patch.object(monitor, 'check_cpu', return_value={"status": "warning"}), \
             patch.object(monitor, 'check_memory', return_value={"status": "normal"}), \
             patch.object(monitor, 'check_disk', return_value={"status": "normal"}):
            score = await monitor.calculate_health_score()
            assert 60 <= score < 90

    async def test_critical_health_score(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor()
        with patch.object(monitor, 'check_cpu', return_value={"status": "critical"}), \
             patch.object(monitor, 'check_memory', return_value={"status": "critical"}), \
             patch.object(monitor, 'check_disk', return_value={"status": "critical"}), \
             patch.object(monitor, 'check_processes', return_value={}):
            score = await monitor.calculate_health_score()
            assert score < 60


class TestIntegrationFullCheck:
    """集成测试：完整检查流程"""

    async def test_full_check_with_multiple_alerts(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor(config={
            "cpu_threshold": 80.0,
            "memory_threshold": 85.0,
            "disk_threshold": 90.0
        })
        mock_memory = Mock()
        mock_memory.percent = 88.0
        mock_memory.available = 1073741824
        mock_memory.total = 8589934592
        mock_disk = Mock()
        mock_disk.percent = 95.0
        mock_disk.free = 5368709120
        mock_disk.total = 107374182400
        
        with patch('psutil.cpu_percent', return_value=85.0), \
             patch('psutil.virtual_memory', return_value=mock_memory), \
             patch('psutil.disk_usage', return_value=mock_disk):
            report = await monitor.run_full_check()
            assert report["health_score"] < 80
            assert len(report["alerts"]) >= 2
            assert report["status"] != "healthy"

    async def test_full_check_healthy_system(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor(config={
            "cpu_threshold": 80.0,
            "memory_threshold": 85.0,
            "disk_threshold": 90.0,
            "critical_ports": []
        })
        mock_memory = Mock()
        mock_memory.percent = 45.0
        mock_memory.available = 4724464025
        mock_memory.total = 8589934592
        mock_disk = Mock()
        mock_disk.percent = 50.0
        mock_disk.free = 53687091200
        mock_disk.total = 107374182400

        with patch('psutil.cpu_percent', return_value=30.0), \
             patch('psutil.virtual_memory', return_value=mock_memory), \
             patch('psutil.disk_usage', return_value=mock_disk), \
             patch('psutil.process_iter', return_value=[]), \
             patch('modules.server_monitor.service.psutil.net_io_counters', return_value=Mock(bytes_sent=1000, bytes_recv=2000, packets_sent=10, packets_recv=20, errin=0, errout=0, dropin=0, dropout=0)), \
             patch('modules.server_monitor.service.psutil.net_if_addrs', return_value={}), \
             patch('modules.server_monitor.service.psutil.net_connections', return_value=[]), \
             patch('socket.gethostbyname', return_value='1.2.3.4'):
            report = await monitor.run_full_check()
            assert report["health_score"] >= 90
            assert report["status"] == "healthy"
            assert len(report["alerts"]) == 0


class TestNetworkMonitoring:
    """测试网络监控功能"""

    async def test_network_normal(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor(config={"critical_ports": []})
        mock_net_io = Mock(
            bytes_sent=1073741824,
            bytes_recv=2147483648,
            packets_sent=10000,
            packets_recv=20000,
            errin=0,
            errout=0,
            dropin=0,
            dropout=0
        )
        with patch('modules.server_monitor.service.psutil.net_io_counters', return_value=mock_net_io), \
             patch('modules.server_monitor.service.psutil.net_if_addrs', return_value={}), \
             patch('modules.server_monitor.service.psutil.net_connections', return_value=[]):
            result = await monitor.check_network()
            assert result["status"] == "normal"
            assert result["alert_triggered"] is False

    async def test_network_missing_critical_ports(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor(config={"critical_ports": [80, 443]})
        mock_connection = Mock()
        mock_connection.status = 'LISTEN'
        mock_connection.laddr = Mock(port=80)

        mock_net_io = Mock(
            bytes_sent=1000, bytes_recv=2000, packets_sent=10, packets_recv=20,
            errin=0, errout=0, dropin=0, dropout=0
        )
        with patch('modules.server_monitor.service.psutil.net_io_counters', return_value=mock_net_io), \
             patch('modules.server_monitor.service.psutil.net_if_addrs', return_value={}), \
             patch('modules.server_monitor.service.psutil.net_connections', return_value=[mock_connection]):
            result = await monitor.check_network()
            assert result["status"] == "warning"
            assert 443 in result["missing_ports"]
            assert result["alert_triggered"] is True

    async def test_network_high_error_rate(self):
        from modules.server_monitor.service import ServerMonitor
        monitor = ServerMonitor(config={"network_error_threshold": 1.0})
        mock_net_io = Mock(
            bytes_sent=1000,
            bytes_recv=2000,
            packets_sent=50,
            packets_recv=50,
            errin=2,
            errout=1,
            dropin=0,
            dropout=0
        )
        with patch('modules.server_monitor.service.psutil.net_io_counters', return_value=mock_net_io), \
             patch('modules.server_monitor.service.psutil.net_if_addrs', return_value={}), \
             patch('modules.server_monitor.service.psutil.net_connections', return_value=[]):
            result = await monitor.check_network()
            assert result["error_rate"] > 1.0
            assert result["status"] == "warning"


class TestDNSMonitoring:
    """测试DNS监控功能"""

    async def test_dns_resolution_normal(self):
        from modules.server_monitor.service import ServerMonitor
        import socket
        monitor = ServerMonitor()

        with patch('socket.gethostbyname', return_value='93.184.216.34'):
            result = await monitor.check_dns_resolution("example.com")
            assert result["status"] == "normal"
            assert result["ip_address"] == '93.184.216.34'
            assert result["resolve_time_ms"] >= 0

    async def test_dns_resolution_slow(self):
        from modules.server_monitor.service import ServerMonitor
        import socket

        monitor = ServerMonitor(config={"dns_resolve_threshold_ms": 100})

        from datetime import datetime, timedelta
        base_time = datetime(2026, 1, 1, 12, 0, 0)
        slow_resolve_time = base_time + timedelta(milliseconds=150)

        call_count = [0]
        def mock_datetime_now(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return base_time
            elif call_count[0] == 2:
                return slow_resolve_time
            else:
                return datetime.now()

        with patch('socket.gethostbyname', return_value='93.184.216.34'), \
             patch('modules.server_monitor.service.datetime') as mock_dt:
            mock_dt.now = mock_datetime_now
            mock_dt.side_effect = None
            result = await monitor.check_dns_resolution("example.com")
            assert result["status"] == "warning"
            assert result["alert_triggered"] is True
            assert result["resolve_time_ms"] > 100

    async def test_dns_resolution_failure(self):
        from modules.server_monitor.service import ServerMonitor
        import socket
        monitor = ServerMonitor()

        with patch('socket.gethostbyname', side_effect=socket.gaierror("Name or service not known")):
            result = await monitor.check_dns_resolution("nonexistent.domain.test")
            assert result["status"] == "critical"
            assert result["ip_address"] is None
            assert result["alert_triggered"] is True
