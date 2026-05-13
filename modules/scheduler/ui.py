import streamlit as st
import asyncio
import pandas as pd
from datetime import datetime
from modules.scheduler.service import SchedulerService
from modules.scheduler.schemas import TaskDefinition, TaskStatus


def show_page():
    st.markdown('<p class="main-header">⏰ 定时任务调度中心</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">任务注册 · 启停控制 · 超时重试 · 执行日志</p>', unsafe_allow_html=True)

    if "scheduler_service" not in st.session_state:
        st.session_state["scheduler_service"] = SchedulerService()

    service: SchedulerService = st.session_state["scheduler_service"]

    tab1, tab2, tab3 = st.tabs(["📋 任务列表", "➕ 注册任务", "📜 执行日志"])

    with tab1:
        st.markdown("#### 定时任务列表")

        tasks = service.get_all_task_statuses()

        if tasks:
            task_data = []
            for t in tasks:
                status_map = {
                    TaskStatus.REGISTERED: "📋 已注册",
                    TaskStatus.RUNNING: "🔄 运行中",
                    TaskStatus.STOPPED: "⏹️ 已停止",
                    TaskStatus.COMPLETED: "✅ 已完成",
                    TaskStatus.FAILED: "❌ 失败",
                    TaskStatus.TIMEOUT: "⏰ 超时",
                }
                task_data.append({
                    "任务ID": t.task_id,
                    "名称": t.name,
                    "状态": status_map.get(t.status, t.status.value),
                    "Cron": t.cron_expression,
                    "运行次数": t.run_count,
                    "失败次数": t.fail_count,
                    "上次运行": t.last_run.strftime("%m-%d %H:%M") if t.last_run else "-",
                    "启用": "✅" if t.enabled else "❌",
                })

            df = pd.DataFrame(task_data)
            st.dataframe(df, width='stretch')

            st.markdown("#### 任务控制")
            col_ctrl1, col_ctrl2 = st.columns(2)

            task_ids = [t.task_id for t in tasks]
            selected_task = st.selectbox("选择任务", task_ids)

            with col_ctrl1:
                if st.button("▶️ 启动任务", use_container_width=True):
                    if service.start_task(selected_task):
                        st.success(f"任务 {selected_task} 已启动")
                        st.rerun()
                    else:
                        st.error("启动失败")

                if st.button("⏹️ 停止任务", use_container_width=True):
                    if service.stop_task(selected_task):
                        st.success(f"任务 {selected_task} 已停止")
                        st.rerun()
                    else:
                        st.error("停止失败")

            with col_ctrl2:
                if st.button("🗑️ 注销任务", use_container_width=True):
                    if service.unregister_task(selected_task):
                        st.success(f"任务 {selected_task} 已注销")
                        st.rerun()
                    else:
                        st.error("注销失败")

                with st.expander("⚙️ 修改配置"):
                    new_cron = st.text_input("Cron 表达式", value="0 */6 * * *")
                    new_timeout = st.number_input("超时时间(秒)", min_value=30, value=300, step=30)
                    new_retries = st.number_input("重试次数", min_value=0, max_value=10, value=3)

                    if st.button("更新配置"):
                        if service.update_task_config(
                            selected_task, cron_expression=new_cron,
                            timeout_seconds=new_timeout, max_retries=new_retries,
                        ):
                            st.success("配置已更新")
                            st.rerun()
                        else:
                            st.error("更新失败")
        else:
            st.info("暂无已注册的任务，请在「注册任务」中创建")

    with tab2:
        st.markdown("#### 注册新任务")

        with st.form("register_task_form"):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                task_id = st.text_input("任务ID", placeholder="例如: sync_orders_001")
                task_name = st.text_input("任务名称", placeholder="例如: 每日订单同步")
                cron_expr = st.text_input("Cron 表达式", value="0 */6 * * *",
                    help="格式: 分 时 日 月 周 (例如 0 */6 * * * 表示每6小时)")
            with col_f2:
                timeout = st.number_input("超时时间(秒)", min_value=30, value=300, step=30)
                max_retries = st.number_input("最大重试次数", min_value=0, max_value=10, value=3)
                enabled = st.checkbox("启用", value=True)
                description = st.text_area("任务描述", placeholder="描述这个任务的用途")

            submitted = st.form_submit_button("📋 注册任务", type="primary", use_container_width=True)

            if submitted:
                if not task_id or not task_name or not cron_expr:
                    st.error("请填写必要信息（任务ID、名称、Cron表达式）")
                else:
                    async def dummy_callback():
                        import logging
                        logging.getLogger(__name__).info(f"任务 {task_id} 执行中...")

                    definition = TaskDefinition(
                        task_id=task_id, name=task_name,
                        cron_expression=cron_expr, callback=dummy_callback,
                        timeout_seconds=timeout, max_retries=max_retries,
                        enabled=enabled, description=description,
                    )

                    if service.register_task(definition):
                        st.success(f"✅ 任务 {task_name} 注册成功")
                        st.rerun()
                    else:
                        st.error("❌ 注册失败，任务ID可能已存在")

    with tab3:
        st.markdown("#### 任务执行日志")

        tasks = service.get_all_task_statuses()
        if tasks:
            task_ids = [t.task_id for t in tasks]
            selected = st.selectbox("选择任务查看日志", task_ids)

            limit = st.slider("显示条数", min_value=5, max_value=50, value=20)

            if st.button("📋 查询日志", use_container_width=True):
                loop = asyncio.new_event_loop()
                logs = loop.run_until_complete(service.get_task_logs(selected, limit=limit))
                loop.close()

                if logs:
                    records = []
                    for log in logs:
                        status_map = {
                            TaskStatus.COMPLETED: "✅ 成功",
                            TaskStatus.FAILED: "❌ 失败",
                            TaskStatus.TIMEOUT: "⏰ 超时",
                            TaskStatus.RUNNING: "🔄 运行中",
                        }
                        records.append({
                            "ID": log.log_id,
                            "状态": status_map.get(log.status, log.status.value),
                            "开始时间": log.started_at.strftime("%Y-%m-%d %H:%M:%S") if log.started_at else "-",
                            "耗时": f"{log.duration_seconds:.1f}s",
                            "重试次数": log.retry_count,
                            "错误信息": log.error_message or "-",
                        })
                    st.dataframe(pd.DataFrame(records), width='stretch')
                else:
                    st.info("暂无执行日志")
        else:
            st.info("暂无任务数据")

    st.markdown("---")
    st.caption("全局定时任务调度中心 | 支持超时重试、异常隔离、并行执行")
