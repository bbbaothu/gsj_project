"""
Callbacks Module 05: Hàng đợi Smart CRM 5 Điểm chạm, AI Call Script, Zalo ZNS & Đặt lịch thợ tận nhà.
"""
from typing import Any, Dict, List, Optional
import dash
from dash import ALL, Input, Output, State, html, no_update
import plotly.graph_objects as go

from src.dash_app.components.charts import apply_stock_sense_layout, empty_figure
from src.dash_app.components.layout_shell import format_vnd_compact, format_vnd_full

OUTCOME_MAP = {
    "booked": "CONVERTED_BOOKING",
    "callback": "CALLBACK_SCHEDULED",
    "noanswer": "NO_ANSWER",
    "declined": "DECLINED",
}


def render_m5_workspace(
    services_or_svc: Any,
    trigger_filter: str = "Tất cả",
    search_text: str = "",
    include_cooldown: bool = False,
    selected_customer: Optional[str] = None,
    appointment_date: str = "2026-11-18",
    time_slot: str = "14:00 - 15:30",
    technician_code: Optional[str] = None,
    role: str = "ROLE_OWNER",
) -> Dict[str, Any]:
    """Dựng KPIs, 2 Biểu đồ Plotly, Bảng hàng đợi khách hàng và Panel Script/Booking."""
    crm_svc = services_or_svc["crm"] if isinstance(services_or_svc, dict) else services_or_svc
    kpis = crm_svc.get_crm_kpis()
    df_all = crm_svc.get_care_queue_dataframe(trigger_filter="Tất cả", include_cooldown=include_cooldown)
    df_filtered = crm_svc.get_care_queue_dataframe(
        trigger_filter=trigger_filter,
        search=search_text,
        include_cooldown=include_cooldown,
    )
    queue_records = df_filtered.to_dict("records") if not df_filtered.empty else []

    active_row = None
    if selected_customer:
        active_row = next((r for r in queue_records if r["customer_code"] == selected_customer), None)
    if active_row is None and queue_records:
        active_row = queue_records[0]

    if active_row:
        script = crm_svc.generate_personalized_script(
            active_row["customer_code"],
            active_row["product_code"],
            active_row["trigger_type"],
        )
        cust_name = active_row["customer_name"]
        cust_phone = active_row["phone"]
        addr_device = f"{active_row['address'] or 'Hà Nội'} · {active_row['product_name']} ({active_row['serial_number'] or active_row['product_code']})"
        priority_badge = f"{active_row['priority_badge']} · {active_row['priority_score']}đ"
        in_cd = bool(active_row["in_cooldown"])
        cd_until = str(active_row["cooldown_until"] or "")
        valid_badge = (
            f"🛡️ Đang Cooldown đến {cd_until}"
            if in_cd
            else "✓ Hợp lệ (Chưa gọi trong 30 ngày)"
        )
    else:
        script = {
            "call_script": "Chưa có khách hàng phù hợp theo bộ lọc hiện tại.",
            "zalo_zns": "",
            "default_service": "Bảo dưỡng thiết bị tại nhà",
        }
        cust_name = "Chưa có khách"
        cust_phone = "—"
        addr_device = "Thử thay đổi bộ lọc điểm chạm ở bên trái."
        priority_badge = "—"
        in_cd = False
        cd_until = ""
        valid_badge = "—"

    # Trigger pills
    counts_by_trig = df_all["trigger_type"].value_counts().to_dict() if not df_all.empty else {}
    pills: List[Any] = [
        html.Button(
            f"Tất cả ({len(df_all)})",
            id={"type": "m5-trigger-pill", "trig": "Tất cả"},
            n_clicks=0,
            className=(
                "px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 text-white transition cursor-pointer"
                if trigger_filter == "Tất cả"
                else "px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:bg-slate-100 border border-slate-200/80 transition cursor-pointer"
            ),
        )
    ]
    for t_key, t_label in crm_svc.TRIGGER_LABELS.items():
        cnt = int(counts_by_trig.get(t_key, 0))
        is_sel = trigger_filter == t_key
        pills.append(
            html.Button(
                f"{t_label} ({cnt})",
                id={"type": "m5-trigger-pill", "trig": t_key},
                n_clicks=0,
                className=(
                    "px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 text-white transition cursor-pointer"
                    if is_sel
                    else "px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:bg-slate-100 border border-slate-200/80 transition cursor-pointer"
                ),
            )
        )

    # Customer Table rows
    table_rows: List[Any] = []
    for r in queue_records:
        is_sel = active_row and r["customer_code"] == active_row["customer_code"]
        row_cls = (
            "bg-blue-50/70 hover:bg-blue-50 cursor-pointer transition"
            if is_sel
            else "hover:bg-slate-50/80 cursor-pointer transition"
        )
        cd_tag = (
            html.Span("Cooldown 30d", className="ml-1.5 px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 text-[10px] font-bold")
            if r["in_cooldown"]
            else None
        )
        table_rows.append(
            html.Tr(
                className=row_cls,
                children=[
                    html.Td(
                        className="pl-4 pr-2.5 py-3 align-top",
                        children=[
                            html.Div(
                                [
                                    html.Span(r["customer_name"], className="font-semibold text-slate-900"),
                                    cd_tag,
                                ],
                                className="flex flex-wrap items-center",
                            ),
                            html.Div(f"{r['phone']} · {r['priority_badge']} ({r['priority_score']}đ)", className="text-[11px] text-slate-500 mt-0.5 tabular-nums"),
                        ],
                    ),
                    html.Td(
                        className="px-2.5 py-3 align-top",
                        children=[
                            html.Div(r["product_name"], className="font-medium text-slate-800"),
                            html.Div(f"Mua {r['days_since_buy']} ngày trước", className="text-[11px] text-slate-400 mt-0.5"),
                        ],
                    ),
                    html.Td(
                        className="px-2.5 py-3 align-top",
                        children=[
                            html.Span(r["trigger_label"], className="inline-block px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[11px] font-semibold"),
                        ],
                    ),
                    html.Td(
                        className="pl-2.5 pr-4 py-3 align-top text-right",
                        children=[
                            html.Button(
                                "Đang chọn" if is_sel else "Tác chiến →",
                                id={"type": "m5-select-customer", "cust": r["customer_code"]},
                                n_clicks=0,
                                className=(
                                    "px-2.5 py-1 rounded-md text-[11px] font-bold bg-blue-600 text-white cursor-pointer"
                                    if is_sel
                                    else "px-2.5 py-1 rounded-md text-[11px] font-semibold bg-white border border-slate-300 text-slate-700 hover:bg-slate-100 cursor-pointer"
                                ),
                            )
                        ],
                    ),
                ],
            )
        )

    if not table_rows:
        table_rows = [
            html.Tr(
                html.Td(
                    "Không có khách hàng phù hợp theo bộ lọc hiện tại.",
                    colSpan=4,
                    className="py-8 text-center text-xs text-slate-400",
                )
            )
        ]

    # Technicians dropdown & conflict check
    techs = crm_svc.get_technicians()
    tech_options = [{"label": f"{t['employee_name']} ({t['title']})", "value": t["employee_code"]} for t in techs]
    active_tech = technician_code or (techs[0]["employee_code"] if techs else "NV0003")

    conflict_msg = ""
    appts_df = crm_svc.get_appointments_dataframe()
    if not appts_df.empty and active_tech and appointment_date and time_slot:
        tech_name = next((t["employee_name"] for t in techs if t["employee_code"] == active_tech), active_tech)
        hit = appts_df[
            (appts_df["technician_name"] == tech_name)
            & (appts_df["appointment_date"] == appointment_date)
            & (appts_df["time_slot"] == time_slot)
            & (appts_df["status"] != "CANCELLED")
        ]
        if not hit.empty:
            conflict_msg = f"Thợ {tech_name} đã có lịch hẹn lúc {time_slot} ngày {appointment_date} (ERR_CRM_002)!"

    # Charts
    if df_all.empty:
        fig_triggers = empty_figure("Chưa có dữ liệu điểm chạm CSKH", height=220)
        fig_priority = empty_figure("Chưa có dữ liệu ưu tiên", height=220)
    else:
        trig_s = df_all["trigger_label"].value_counts()
        fig_triggers = go.Figure()
        fig_triggers.add_bar(
            y=list(trig_s.index),
            x=[int(v) for v in trig_s.values],
            orientation="h",
            marker_color=["#2563EB", "#059669", "#F59E0B", "#6366F1", "#0EA5E9"][: len(trig_s)],
            text=[int(v) for v in trig_s.values],
            textposition="outside",
        )
        fig_triggers.update_yaxes(autorange="reversed")
        apply_stock_sense_layout(fig_triggers, height=220, margin=dict(l=140, r=24, t=12, b=24))

        prio_counts = df_all["priority_tier"].value_counts().to_dict()
        labels = ["Cao", "Trung bình", "Thấp", "Cooldown 30d"]
        vals = [
            int(prio_counts.get("CAO", 0)),
            int(prio_counts.get("TRUNG_BINH", 0)),
            int(prio_counts.get("THAP", 0)),
            int(kpis["cooldown_blocked_count"]),
        ]
        fig_priority = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=vals,
                    hole=0.58,
                    marker=dict(colors=["#E11D48", "#F59E0B", "#059669", "#94A3B8"]),
                    textinfo="label+value",
                )
            ]
        )
        apply_stock_sense_layout(fig_priority, height=220, margin=dict(l=12, r=12, t=12, b=12))

    return {
        "queue_records": queue_records,
        "active_customer_code": active_row["customer_code"] if active_row else None,
        "call_script": script["call_script"],
        "zalo_zns": script["zalo_zns"],
        "default_service": script["default_service"],
        "header_badge": f"{kpis['due_today_count']} KHÁCH CẦN GỌI HÔM NAY",
        "kpi_pending_val": f"{kpis['due_today_count']} khách hàng",
        "kpi_pending_foot": f"Chặn gọi trùng Cooldown: {kpis['cooldown_blocked_count']} · Đã ghi nhận: {kpis['interactions_logged_count']}",
        "kpi_maint_val": f"{kpis['ac_maint_due_count']} hộ gia đình",
        "kpi_cross_val": f"{kpis['cross_or_warranty_count']} cơ hội bán",
        "kpi_done_badge": f"{kpis['booked_appointments_count']} lịch thợ",
        "kpi_rev_main": format_vnd_compact(kpis["expected_service_revenue"], "ROLE_OWNER"),
        "kpi_done_foot": f"Tổng doanh thu dịch vụ dự kiến từ {kpis['booked_appointments_count']} lịch hẹn",
        "trigger_pills": pills,
        "table_rows": table_rows,
        "table_footer": f"Hiển thị {len(queue_records)} khách hàng trong hàng đợi (tổng quét {len(df_all)} hồ sơ)",
        "panel_valid_badge": valid_badge,
        "panel_cust_name": cust_name,
        "panel_priority_badge": priority_badge,
        "panel_phone": cust_phone,
        "panel_addr_device": addr_device,
        "in_cooldown": in_cd,
        "cd_desc": f"Khách hàng này đang trong vùng bảo vệ 30 ngày đến {cd_until}." if in_cd else "",
        "tech_options": tech_options,
        "active_tech": active_tech,
        "conflict_msg": conflict_msg,
        "fig_triggers": fig_triggers,
        "fig_priority": fig_priority,
    }


def submit_m5_outcome(
    crm_svc: Any,
    customer_code: str,
    product_code: str,
    serial_number: Optional[str],
    trigger_type: str,
    outcome_ui: str = "booked",
    appointment_date: Optional[str] = None,
    time_slot: Optional[str] = None,
    technician_code: Optional[str] = None,
    service_name: str = "Bảo dưỡng thiết bị tại nhà",
    expected_fee: float = 150_000.0,
    channel: str = "CALL",
) -> Dict[str, Any]:
    """Ghi nhận kết quả cuộc gọi & chốt lịch thợ qua CrmService."""
    outcome = OUTCOME_MAP.get(outcome_ui, outcome_ui)
    return crm_svc.record_interaction_and_book_service(
        customer_code=customer_code,
        product_code=product_code,
        serial_number=serial_number,
        trigger_type=trigger_type,
        outcome=outcome,
        appointment_date=appointment_date,
        time_slot=time_slot,
        technician_code=technician_code,
        service_name=service_name,
        expected_fee=expected_fee,
        channel=channel,
    )


def register_m5_callbacks(app: Any, services: Dict[str, Any]) -> None:
    """Đăng ký callbacks tương tác cho Module 05 Smart CRM."""
    crm_svc = services["crm"]

    @app.callback(
        Output("store-m5-trigger", "data"),
        Input({"type": "m5-trigger-pill", "trig": ALL}, "n_clicks"),
        Input("m5Kpi-pending", "n_clicks"),
        Input("m5Kpi-maintenance", "n_clicks"),
        Input("m5Kpi-crosssell", "n_clicks"),
        prevent_initial_call=True,
    )
    def filter_m5_trigger(pill_clicks, k_pend, k_maint, k_cross):
        ctx = dash.callback_context
        if not ctx.triggered:
            return no_update
        tid = ctx.triggered_id
        if isinstance(tid, dict) and tid.get("type") == "m5-trigger-pill" and any(pill_clicks or []):
            return tid["trig"]
        prop = ctx.triggered[0]["prop_id"].split(".")[0]
        if prop == "m5Kpi-pending":
            return "Tất cả"
        if prop == "m5Kpi-maintenance":
            return "CARE_MAINT_AC"
        if prop == "m5Kpi-crosssell":
            return "CARE_ACCESSORY"
        return no_update

    @app.callback(
        Output("store-m5-include-cooldown", "data"),
        Input("m5ToggleCooldownBtn", "n_clicks"),
        State("store-m5-include-cooldown", "data"),
        prevent_initial_call=True,
    )
    def toggle_cooldown(n, cur):
        return not bool(cur)

    @app.callback(
        Output("store-m5-selected-customer", "data"),
        Input({"type": "m5-select-customer", "cust": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def select_customer(n_clicks):
        ctx = dash.callback_context
        if not ctx.triggered or not any(n_clicks or []):
            return no_update
        tid = ctx.triggered_id
        return tid["cust"] if isinstance(tid, dict) else no_update

    @app.callback(
        Output("store-m5-outcome", "data"),
        Output("m5OutcomeCard-booked", "className"),
        Output("m5OutcomeCard-callback", "className"),
        Output("m5OutcomeCard-noanswer", "className"),
        Output("m5OutcomeCard-declined", "className"),
        Input("m5OutcomeCard-booked", "n_clicks"),
        Input("m5OutcomeCard-callback", "n_clicks"),
        Input("m5OutcomeCard-noanswer", "n_clicks"),
        Input("m5OutcomeCard-declined", "n_clicks"),
        prevent_initial_call=True,
    )
    def select_outcome(n1, n2, n3, n4):
        ctx = dash.callback_context
        tid = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else ""
        chosen = tid.replace("m5OutcomeCard-", "") if tid.startswith("m5OutcomeCard-") else "booked"
        sel_booked = "rounded-xl border-2 border-blue-600 bg-blue-50/25 p-3 cursor-pointer transition"
        idle_booked = "rounded-xl border border-slate-200 bg-white p-3 cursor-pointer transition"
        sel_row = "rounded-xl border-2 border-blue-600 bg-blue-50/25 px-3 py-2.5 cursor-pointer transition flex items-center justify-between gap-2"
        idle_row = "rounded-xl border border-slate-200 hover:border-slate-300 bg-white px-3 py-2.5 cursor-pointer transition flex items-center justify-between gap-2"
        return (
            chosen,
            sel_booked if chosen == "booked" else idle_booked,
            sel_row if chosen == "callback" else idle_row,
            sel_row if chosen == "noanswer" else idle_row,
            sel_row if chosen == "declined" else idle_row,
        )

    @app.callback(
        Output("m5HeaderPendingBadge", "children"),
        Output("m5KpiPendingVal", "children"),
        Output("m5KpiPendingFoot", "children"),
        Output("m5KpiMaintVal", "children"),
        Output("m5KpiCrossVal", "children"),
        Output("m5KpiDoneBadge", "children"),
        Output("m5KpiRevenueMain", "children"),
        Output("m5KpiDoneFoot", "children"),
        Output("m5TriggerPillsContainer", "children"),
        Output("m5CustomerTableBody", "children"),
        Output("m5TableFooterInfo", "children"),
        Output("m5PanelValidBadge", "children"),
        Output("m5PanelCustomerName", "children"),
        Output("m5PanelPriorityBadge", "children"),
        Output("m5PanelPhoneLink", "children"),
        Output("m5PanelAddressDevice", "children"),
        Output("m5CooldownWarningBanner", "className"),
        Output("m5CooldownWarningDesc", "children"),
        Output("m5PanelCallScript", "children"),
        Output("m5PanelZaloPreview", "children"),
        Output("m5TechnicianSelect", "options"),
        Output("m5TechnicianSelect", "value"),
        Output("m5ServicePackageInput", "value"),
        Output("m5TechConflictBanner", "className"),
        Output("m5TechConflictDesc", "children"),
        Output("m5TriggersChart", "figure"),
        Output("m5PriorityChart", "figure"),
        Input("store-m5-trigger", "data"),
        Input("store-m5-include-cooldown", "data"),
        Input("m5SearchInput", "value"),
        Input("store-m5-selected-customer", "data"),
        Input("m5AppointmentDate", "value"),
        Input("m5AppointmentSlot", "value"),
        Input("m5TechnicianSelect", "value"),
        Input("store-m5-refresh", "data"),
        Input("m5ScanTriggersBtn", "n_clicks"),
        Input("store-rbac-role", "data"),
    )
    def sync_m5_workspace(
        trig, include_cd, search_txt, sel_cust, appt_date, appt_slot, tech_code, _ref, _scan, role
    ):
        res = render_m5_workspace(
            crm_svc,
            trigger_filter=trig or "Tất cả",
            search_text=search_txt or "",
            include_cooldown=bool(include_cd),
            selected_customer=sel_cust,
            appointment_date=appt_date or "2026-11-18",
            time_slot=appt_slot or "14:00 - 15:30",
            technician_code=tech_code,
            role=role or "ROLE_OWNER",
        )
        cd_cls = (
            "p-2.5 rounded-xl bg-amber-50 border border-amber-300 text-amber-900 text-xs flex items-start gap-2"
            if res["in_cooldown"]
            else "hidden p-2.5 rounded-xl bg-amber-50 border border-amber-300 text-amber-900 text-xs flex items-start gap-2"
        )
        conf_cls = (
            "p-2.5 rounded-lg bg-rose-50 border border-rose-300 text-rose-900 text-[11px] flex items-start gap-2"
            if res["conflict_msg"]
            else "hidden p-2.5 rounded-lg bg-rose-50 border border-rose-300 text-rose-900 text-[11px] flex items-start gap-2"
        )
        return (
            res["header_badge"],
            res["kpi_pending_val"],
            res["kpi_pending_foot"],
            res["kpi_maint_val"],
            res["kpi_cross_val"],
            res["kpi_done_badge"],
            res["kpi_rev_main"],
            res["kpi_done_foot"],
            res["trigger_pills"],
            res["table_rows"],
            res["table_footer"],
            res["panel_valid_badge"],
            res["panel_cust_name"],
            res["panel_priority_badge"],
            res["panel_phone"],
            res["panel_addr_device"],
            cd_cls,
            res["cd_desc"],
            res["call_script"],
            res["zalo_zns"],
            res["tech_options"],
            res["active_tech"],
            res["default_service"],
            conf_cls,
            res["conflict_msg"],
            res["fig_triggers"],
            res["fig_priority"],
        )

    @app.callback(
        Output("store-m5-refresh", "data"),
        Output("store-toast-msg", "data", allow_duplicate=True),
        Input("m5PrimarySaveBtn", "n_clicks"),
        Input("m5SecondaryActionBtn", "n_clicks"),
        State("store-m5-trigger", "data"),
        State("store-m5-include-cooldown", "data"),
        State("m5SearchInput", "value"),
        State("store-m5-selected-customer", "data"),
        State("store-m5-outcome", "data"),
        State("m5AppointmentDate", "value"),
        State("m5AppointmentSlot", "value"),
        State("m5TechnicianSelect", "value"),
        State("m5ServicePackageInput", "value"),
        State("store-m5-refresh", "data"),
        prevent_initial_call=True,
    )
    def save_crm_action(
        n_save, n_zalo, trig, include_cd, search_txt, sel_cust, outcome_ui, appt_date, appt_slot, tech_code, svc_name, cur_ref
    ):
        ctx = dash.callback_context
        tid = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else ""
        ws = render_m5_workspace(
            crm_svc,
            trigger_filter=trig or "Tất cả",
            search_text=search_txt or "",
            include_cooldown=bool(include_cd),
            selected_customer=sel_cust,
        )
        records = ws["queue_records"]
        active = next((r for r in records if r["customer_code"] == ws["active_customer_code"]), None)
        if not active:
            return no_update, "Chưa chọn khách hàng để tác chiến."

        if tid == "m5SecondaryActionBtn":
            res = submit_m5_outcome(
                crm_svc,
                customer_code=active["customer_code"],
                product_code=active["product_code"],
                serial_number=active["serial_number"],
                trigger_type=active["trigger_type"],
                outcome_ui="callback",
                channel="ZALO_ZNS",
            )
            if res.get("success"):
                return (cur_ref or 0) + 1, f"Đã gửi tin Zalo ZNS tới {active['customer_name']} ({active['phone']})!"
            return no_update, res.get("error", "Không thể gửi Zalo ZNS.")

        res = submit_m5_outcome(
            crm_svc,
            customer_code=active["customer_code"],
            product_code=active["product_code"],
            serial_number=active["serial_number"],
            trigger_type=active["trigger_type"],
            outcome_ui=outcome_ui or "booked",
            appointment_date=appt_date,
            time_slot=appt_slot,
            technician_code=tech_code,
            service_name=svc_name or ws["default_service"],
        )
        if res.get("success"):
            return (cur_ref or 0) + 1, res["message"]
        return no_update, res.get("error", "Lỗi lưu nhật ký CRM")

    @app.callback(
        Output("m5CycleModal", "className"),
        Output("store-toast-msg", "data", allow_duplicate=True),
        Input("m5OpenCycleModalBtn", "n_clicks"),
        Input("m5CloseCycleModalBtn", "n_clicks"),
        Input("m5CancelCycleModalBtn", "n_clicks"),
        Input("m5SaveCycleModalBtn", "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_cycle_modal(o1, c1, c2, s1):
        ctx = dash.callback_context
        tid = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else ""
        if tid == "m5OpenCycleModalBtn":
            return "fixed inset-0 bg-slate-900/40 z-50 flex items-center justify-center p-4", no_update
        if tid == "m5SaveCycleModalBtn":
            return "fixed inset-0 bg-slate-900/40 z-50 hidden items-center justify-center p-4", "Đã lưu cấu hình chu kỳ chăm sóc tự động"
        return "fixed inset-0 bg-slate-900/40 z-50 hidden items-center justify-center p-4", no_update
