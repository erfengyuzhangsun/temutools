import streamlit as st
import asyncio
import pandas as pd
from datetime import datetime
from modules.scheduler.service import SchedulerService
from common.async_runner import run as run_async
from modules.scheduler.schemas import TaskDefinition, TaskStatus
from modules.scheduler.task_templates import (
    TASK_TEMPLATES, is_template_task, is_task_due,
)

_AUTO_EXECUTED_KEY = "_scheduler_auto_executed"


def _auto_register_templates(service: SchedulerService, user_id: int):
    for template in TASK_TEMPLATES:
        existing = service.get_task_status(template.task_id)
        if existing is not None:
            continue
        callback = template.callback_factory(user_id)
        definition = TaskDefinition(
            task_id=template.task_id,
            name=template.name,
            cron_expression=template.default_cron,
            callback=callback,
            timeout_seconds=300,
            max_retries=2,
            enabled=True,
            description=template.description,
        )
        service.register_task(definition)


def _auto_execute_due_tasks(service: SchedulerService):
    if st.session_state.get(_AUTO_EXECUTED_KEY, False):
        return
    st.session_state[_AUTO_EXECUTED_KEY] = True

    tasks = service.get_all_task_statuses()
    due_tasks = []
    for t in tasks:
        if not t.enabled:
            continue
        if not is_template_task(t.task_id):
            continue
        if is_task_due(t.cron_expression, t.last_run):
            due_tasks.append(t)

    if due_tasks:
        for t in due_tasks:
            with st.spinner(f"🔄 自动执行 [{t.name}]..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(service._execute_task(t.task_id))
                    if result.success:
                        st.toast(f"✅ {t.name} 自动执行成功 ({result.duration_seconds:.1f}s)", icon="✅")
                    else:
                        st.toast(f"❌ {t.name} 自动执行失败: {result.message}", icon="❌")
                finally:
                    loop.close()


def show_page():
    user_id = st.session_state.get("user_id", 1)

    st.markdown('<p class="main-header">⏰ 定时任务调度中心</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">预设自动任务 · 一键执行 · 定时调度</p>', unsafe_allow_html=True)

    if "scheduler_service" not in st.session_state:
        st.session_state["scheduler_service"] = SchedulerService()

    service: SchedulerService = st.session_state["scheduler_service"]

    _auto_register_templates(service, user_id)
    _auto_execute_due_tasks(service)

    tab1, tab2, tab3 = st.tabs(["📋 任务列表", "➕ 注册自定义任务", "📜 执行日志"])

    with tab1:
        st.markdown("#### 定时任务列表")

        tasks = service.get_all_task_statuses()

        if tasks:
            task_data = []
            for t in tasks:
                status_map = {
                    TaskStatus.REGISTERED: "📋 待执行",
                    TaskStatus.RUNNING: "🔄 运行中",
                    TaskStatus.STOPPED: "⏹️ 已暂停",
                    TaskStatus.COMPLETED: "✅ 已完成",
                    TaskStatus.FAILED: "❌ 失败",
                    TaskStatus.TIMEOUT: "⏰ 超时",
                }
                is_template = is_template_task(t.task_id)
                task_data.append({
                    "类型": "📦 预设" if is_template else "⚙️ 自定义",
                    "任务名称": t.name,
                    "状态": status_map.get(t.status, t.status.value),
                    "Cron": t.cron_expression,
                    "执行次数": t.run_count,
                    "失败": t.fail_count,
                    "上次运行": t.last_run.strftime("%m-%d %H:%M") if t.last_run else "-",
                    "启用": "✅" if t.enabled else "❌",
                })

            df = pd.DataFrame(task_data)
            st.dataframe(df, width='stretch', hide_index=True)

            st.markdown("#### 任务控制")
            col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)

            task_ids = [t.task_id for t in tasks]
            task_names = {t.task_id: t.name for t in tasks}
            selected_task = st.selectbox("选择任务", task_ids,
                                         format_func=lambda x: task_names.get(x, x))

            with col_ctrl1:
                if st.button("▶️ 启动任务", use_container_width=True):
                    if service.start_task(selected_task):
                        st.success(f"任务已启动")
                        st.rerun()
                    else:
                        st.error("启动失败")

                if st.button("⏹️ 暂停任务", use_container_width=True):
                    if service.stop_task(selected_task):
                        st.success(f"任务已暂停")
                        st.rerun()
                    else:
                        st.error("暂停失败")

            with col_ctrl2:
                if st.button("🚀 立即执行一次", use_container_width=True, type="primary"):
                    with st.spinner(f"正在执行 [{selected_task}]..."):
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            result = loop.run_until_complete(service._execute_task(selected_task))
                            if result.success:
                                st.success(f"✅ 执行成功！耗时 {result.duration_seconds:.1f}s")
                            else:
                                st.error(f"❌ 执行失败: {result.message}")
                        finally:
                            loop.close()
                    st.rerun()

            with col_ctrl3:
                if st.button("🗑️ 注销任务", use_container_width=True):
                    if is_template_task(selected_task):
                        st.warning("预设任务不可注销，如需禁用请在启用开关中关闭")
                    elif service.unregister_task(selected_task):
                        st.success(f"任务已注销")
                        st.rerun()
                    else:
                        st.error("注销失败")

            with st.expander("⚙️ 修改任务配置"):
                selected_status = next((t for t in tasks if t.task_id == selected_task), None)
                new_cron = st.text_input("Cron 表达式",
                                         value=selected_status.cron_expression if selected_status else "0 */6 * * *")
                new_timeout = st.number_input("超时时间(秒)", min_value=30, value=300, step=30)
                new_retries = st.number_input("重试次数", min_value=0, max_value=10, value=2)

                if st.button("更新配置"):
                    if service.update_task_config(
                        selected_task, cron_expression=new_cron,
                        timeout_seconds=new_timeout, max_retries=new_retries,
                    ):
                        st.success("配置已更新")
                        st.rerun()
                    else:
                        st.error("更新失败")

            st.markdown("---")
            st.markdown("#### 预设任务说明")
            for tpl in TASK_TEMPLATES:
                with st.container():
                    st.markdown(f"""
                    **📦 {tpl.name}** `{tpl.default_cron}`
                    > {tpl.description}
                    """)
        else:
            st.info("暂无已注册的任务，请在「注册自定义任务」中创建")

    with tab2:
        st.markdown("#### 注册自定义任务")
        st.info("💡 预设任务已自动注册（见「任务列表」标签），覆盖了大部分常见自动化场景。如需额外的自定义任务，请在此添加。注意：自定义任务仅记录执行日志，不会自动执行业务逻辑。")

        with st.form("register_task_form"):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                task_id = st.text_input("任务ID", placeholder="例如: my_custom_task_001")
                task_name = st.text_input("任务名称", placeholder="例如: 我的自定义任务")
                cron_expr = st.text_input("Cron 表达式", value="0 */6 * * *",
                    help="格式: 分 时 日 月 周 (例如 0 */6 * * * 表示每6小时)")
            with col_f2:
                timeout = st.number_input("超时时间(秒)", min_value=30, value=300, step=30)
                max_retries = st.number_input("最大重试次数", min_value=0, max_value=10, value=3)
                enabled = st.checkbox("启用", value=True)
                description = st.text_area("任务描述", placeholder="描述这个任务的用途")

            submitted = st.form_submit_button("📋 注册自定义任务", type="primary", use_container_width=True)

            if submitted:
                if not task_id or not task_name or not cron_expr:
                    st.error("请填写必要信息（任务ID、名称、Cron表达式）")
                else:
                    async def noop_callback():
                        logger = logging.getLogger(__name__)
                        logger.info(f"自定义任务 {task_id} 执行记录 | 无业务逻辑关联")

                    import logging
                    definition = TaskDefinition(
                        task_id=task_id, name=task_name,
                        cron_expression=cron_expr, callback=noop_callback,
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
            task_names = {t.task_id: t.name for t in tasks}
            selected = st.selectbox("选择任务查看日志", task_ids,
                                    format_func=lambda x: task_names.get(x, x))

            limit = st.slider("显示条数", min_value=5, max_value=50, value=20)

            if st.button("📋 查询日志", use_container_width=True):
                logs = run_async(service.get_task_logs(selected, limit=limit))

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
                    st.dataframe(pd.DataFrame(records), width='stretch', hide_index=True)
                else:
                    st.info("暂无执行日志")
        else:
            st.info("暂无任务数据")

    st.markdown("---")
    st.caption("定时任务调度中心 | 预设任务包含真实业务逻辑，支持超时重试、异常隔离、自动到期执行")
