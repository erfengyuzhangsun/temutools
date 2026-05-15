import streamlit as st
from modules.server_monitor.service import ServerMonitor
from modules.server_monitor.config import MODULE_CONFIG
import asyncio

def render_server_monitor():
    st.header("🖥️ 云主机监控告警")
    st.caption("实时监控服务器 CPU、内存、磁盘和关键进程状态")

    with st.expander("⚙️ 监控配置", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            cpu_thresh = st.slider(
                "CPU告警阈值(%)",
                float(MODULE_CONFIG["cpu_threshold"]["min"]),
                float(MODULE_CONFIG["cpu_threshold"]["max"]),
                float(MODULE_CONFIG["cpu_threshold"]["default"])
            )
        with col2:
            mem_thresh = st.slider(
                "内存告警阈值(%)",
                float(MODULE_CONFIG["memory_threshold"]["min"]),
                float(MODULE_CONFIG["memory_threshold"]["max"]),
                float(MODULE_CONFIG["memory_threshold"]["default"])
            )
        with col3:
            disk_thresh = st.slider(
                "磁盘告警阈值(%)",
                float(MODULE_CONFIG["disk_threshold"]["min"]),
                float(MODULE_CONFIG["disk_threshold"]["max"]),
                float(MODULE_CONFIG["disk_threshold"]["default"])
            )

    if st.button("🔍 立即检查", type="primary"):
        with st.spinner("正在执行健康检查..."):
            config = {
                "cpu_threshold": cpu_thresh,
                "memory_threshold": mem_thresh,
                "disk_threshold": disk_thresh
            }
            monitor = ServerMonitor(config=config)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                report = loop.run_until_complete(monitor.run_full_check())
                _display_report(report, monitor)
            finally:
                loop.close()

def _display_report(report: dict, monitor: ServerMonitor):
    score = report["health_score"]
    status = report["status"]

    status_colors = {
        "healthy": ("#28a745", "🟢 健康"),
        "degraded": ("#ffc107", "🟡 降级"),
        "warning": ("#fd7e14", "🟠 警告"),
        "critical": ("#dc3545", "🔴 危险")
    }
    color, label = status_colors.get(status, ("#6c757d", "❓ 未知"))

    st.markdown(f"### 整体状态: {label}")
    st.progress(score / 100.0)
    st.metric("健康评分", f"{score:.1f}/100")

    col1, col2, col3, col4 = st.columns(4)
    metrics = report["metrics"]

    with col1:
        cpu = metrics["cpu"]
        cpu_color = "#dc3545" if cpu["status"] != "normal" else "#28a745"
        st.metric(
            "📊 CPU使用率",
            f"{cpu['usage']:.1f}%",
            delta=None,
            delta_color="inverse"
        )
        st.markdown(f"<div style='text-align:center;color:{cpu_color}'>{cpu['status'].upper()}</div>",
                   unsafe_allow_html=True)

    with col2:
        mem = metrics["memory"]
        mem_color = "#dc3545" if mem["status"] != "normal" else "#28a745"
        st.metric(
            "💾 内存使用率",
            f"{mem['usage_percent']:.1f}%",
            delta=f"{mem['available_mb']:.0f}MB 可用"
        )
        st.markdown(f"<div style='text-align:center;color:{mem_color}'>{mem['status'].upper()}</div>",
                   unsafe_allow_html=True)

    with col3:
        disk = metrics["disk"]
        disk_color = "#dc3545" if disk["status"] != "normal" else "#28a745"
        st.metric(
            "💿 磁盘使用率",
            f"{disk['usage_percent']:.1f}%",
            delta=f"{disk['free_gb']:.1f}GB 可用"
        )
        st.markdown(f"<div style='text-align:center;color:{disk_color}'>{disk['status'].upper()}</div>",
                   unsafe_allow_html=True)

    with col4:
        proc_count = len(metrics["processes"])
        running = sum(1 for p in metrics["processes"].values() if p["status"] == "running")
        st.metric(
            "⚙️ 进程监控",
            f"{running}/{proc_count}",
            delta=None
        )

    if report["alerts"]:
        st.subheader("🔔 活跃告警")
        for alert in report["alerts"][:10]:
            severity_icon = {"critical": "🔴", "warning": "🟡", "info": "🔵"}
            icon = severity_icon.get(alert["level"], "⚪")
            with st.container():
                st.markdown(f"""
                **{icon} [{alert['level'].upper()}]** {alert['type']}
                - {alert['message']}
                - *{alert['timestamp'].strftime('%H:%M:%S')}*
                """)
                st.divider()
    else:
        st.success("✅ 无活跃告警，系统运行正常")

    with st.expander("📋 详细报告"):
        st.json(report)
