"""
Callbacks Module 06: Biểu đồ Thác nước Lợi nhuận, Attach-Rate 60%/70%, Duyệt chi hoa hồng & Xuất CSV.
"""
from typing import Any, Dict, List
import dash
from dash import ALL, Input, Output, State, dcc, html, no_update
import plotly.graph_objects as go

from src.dash_app.components.charts import apply_stock_sense_layout, empty_figure
from src.dash_app.components.layout_shell import format_vnd_compact, format_vnd_full


def render_m6_workspace(
    services_or_svc: Any,
    period: str = "T10_11",
    role: str = "ROLE_OWNER",
) -> Dict[str, Any]:
    """Dựng 4 KPI Cards, Waterfall Plotly, Attach-Rate Chart, Bảng ngành hàng & Bảng Hoa hồng nhân sự."""
    perf_svc = services_or_svc["performance"] if isinstance(services_or_svc, dict) else services_or_svc
    kpis = perf_svc.get_performance_kpis(role=role)
    wf = perf_svc.get_profit_waterfall_data(role=role)
    df_cat = perf_svc.get_category_attach_rate_dataframe(role=role)
    staff_list = perf_svc.get_staff_commission_list(role=role)

    # 1. Waterfall Chart
    if role == "ROLE_SALES":
        fig_waterfall = empty_figure("🔒 Đã ẩn dữ liệu Vốn gốc & Lãi gộp theo quyền Nhân viên bán hàng", height=280)
    else:
        y_vals = [
            float(wf["core_profit"] or 0.0),
            float(wf["accessory_profit"] or 0.0),
            float(wf["service_profit"] or 0.0),
            -abs(float(wf["promo_discount_cost"] or 0.0)),
            float(wf["net_gross_profit"] or 0.0),
        ]
        fig_waterfall = go.Figure(
            go.Waterfall(
                name="Lãi gộp",
                orientation="v",
                measure=["relative", "relative", "relative", "relative", "total"],
                x=["Lãi Máy Chính", "Lãi Phụ Kiện", "Công Dịch Vụ", "Khuyến Mại", "TỔNG LÃI THỰC"],
                y=y_vals,
                text=[
                    f"+{y_vals[0]/1_000_000:.1f}tr",
                    f"+{y_vals[1]/1_000_000:.1f}tr",
                    f"+{y_vals[2]/1_000_000:.1f}tr",
                    f"{y_vals[3]/1_000_000:.1f}tr",
                    f"{y_vals[4]/1_000_000:.1f}tr",
                ],
                textposition="outside",
                increasing={"marker": {"color": "#059669"}},
                decreasing={"marker": {"color": "#E11D48"}},
                totals={"marker": {"color": "#0F172A"}},
                connector={"line": {"color": "#94A3B8", "dash": "dot", "width": 1.2}},
            )
        )
        fig_waterfall.update_yaxes(title_text="VNĐ")
        apply_stock_sense_layout(fig_waterfall, height=280, margin=dict(l=46, r=16, t=28, b=36))

    # 2. Attach-Rate Horizontal Bar Chart (with vertical lines at 60% and 70%)
    if df_cat.empty:
        fig_attach = empty_figure("Chưa có dữ liệu tỷ lệ bán kèm", height=190)
    else:
        cats = df_cat["category"].tolist()
        rates = [float(r) for r in df_cat["attach_rate_pct"].tolist()]
        colors = ["#2563EB" if r >= 70 else ("#F59E0B" if r >= 60 else "#E11D48") for r in rates]
        fig_attach = go.Figure()
        fig_attach.add_bar(
            y=cats,
            x=rates,
            orientation="h",
            marker_color=colors,
            text=[f"{r:.1f}%" for r in rates],
            textposition="outside",
        )
        fig_attach.add_vline(x=60, line_dash="dash", line_color="#E11D48", line_width=1.5)
        fig_attach.add_vline(x=70, line_dash="solid", line_color="#0F172A", line_width=1.5)
        fig_attach.update_xaxes(range=[0, 105], ticksuffix="%")
        fig_attach.update_yaxes(autorange="reversed")
        apply_stock_sense_layout(fig_attach, height=190, margin=dict(l=140, r=36, t=12, b=24))

    # 3. Category Attach Table Rows
    cat_rows: List[Any] = []
    for _, row in df_cat.iterrows():
        rate = float(row["attach_rate_pct"])
        bar_color = "bg-blue-600" if rate >= 70 else ("bg-amber-500" if rate >= 60 else "bg-rose-600")
        sales_txt = format_vnd_compact(row["attached_sales"], "ROLE_OWNER")
        prof_txt = "****** đ" if role == "ROLE_SALES" else f"Lãi: {format_vnd_compact(row['attached_profit'], role)}"
        cat_rows.append(
            html.Tr(
                className="hover:bg-slate-50/80 transition",
                children=[
                    html.Td(
                        [
                            html.Div(row["category"], className="font-semibold text-slate-900"),
                            html.Div(f"{int(row['attached_orders'])} / {int(row['core_orders'])} đơn kèm", className="text-[11px] text-slate-400 mt-0.5"),
                        ],
                        className="py-2.5 pr-2",
                    ),
                    html.Td(
                        [
                            html.Div(
                                [
                                    html.Span(f"{rate:.1f}%", className="font-bold text-slate-800"),
                                    html.Span("Đạt mục tiêu" if rate >= 70 else "Dưới 70%", className="text-[11px] text-slate-500"),
                                ],
                                className="flex items-center justify-between text-[11px] mb-1",
                            ),
                            html.Div(
                                html.Div(className=f"h-full {bar_color} rounded-full", style={"width": f"{min(100.0, rate):.1f}%"}),
                                className="w-full h-2 bg-slate-100 rounded-full overflow-hidden",
                            ),
                        ],
                        className="py-2.5 px-2",
                    ),
                    html.Td(
                        [
                            html.Div(sales_txt, className="font-bold text-slate-900"),
                            html.Div(prof_txt, className="text-[11px] text-emerald-600 cost-val"),
                        ],
                        className="py-2.5 px-2 text-right",
                    ),
                    html.Td(
                        html.Span(row["rating_badge"], className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-700 border border-slate-200 whitespace-nowrap"),
                        className="py-2.5 pl-2 text-right",
                    ),
                ],
            )
        )

    # 4. Staff Commission Cards
    total_fund = sum(float(s["commission_amount"]) for s in staff_list)
    staff_cards: List[Any] = []
    for idx, s in enumerate(staff_list, start=1):
        is_approved = s["status"] == "APPROVED"
        comm_txt = "****** đ" if role == "ROLE_SALES" else format_vnd_full(s["commission_amount"], role)
        card_cls = (
            "p-4 rounded-xl border-2 border-amber-300/80 bg-amber-50/20 flex flex-col justify-between gap-3"
            if idx == 1
            else "p-4 rounded-xl border border-slate-200 bg-white flex flex-col justify-between gap-3"
        )
        staff_cards.append(
            html.Div(
                className=card_cls,
                children=[
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(f"#{idx}", className="px-2 py-0.5 rounded-full bg-slate-900 text-white text-[10px] font-bold mr-2"),
                                    html.Strong(s["employee_name"], className="text-sm text-slate-900"),
                                ],
                                className="flex items-center",
                            ),
                            html.Span(
                                "✓ Đã duyệt" if is_approved else "Chờ duyệt",
                                className=f"px-2 py-0.5 rounded text-[10px] font-bold {'bg-emerald-100 text-emerald-800' if is_approved else 'bg-amber-100 text-amber-800'}",
                            ),
                        ],
                        className="flex items-center justify-between gap-2",
                    ),
                    html.Div(
                        [
                            html.Div(s["title"], className="text-slate-500"),
                            html.Div(f"PK: {format_vnd_compact(s['accessory_sales'], 'ROLE_OWNER')} · DV: {format_vnd_compact(s['service_sales'], 'ROLE_OWNER')}", className="text-[11px] text-slate-600 mt-1 tabular-nums"),
                        ]
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("Hoa hồng:", className="text-slate-400 mr-1"),
                                    html.Strong(comm_txt, className="font-mono text-sm text-emerald-700 cost-val"),
                                ]
                            ),
                            html.Button(
                                "Đã chi ✓" if is_approved else ("🔒 Quản lý" if role == "ROLE_SALES" else "✓ Duyệt chi"),
                                id={"type": "m6-approve-emp", "emp": s["employee_code"]},
                                n_clicks=0,
                                disabled=is_approved or role == "ROLE_SALES",
                                className=(
                                    "px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-slate-100 text-slate-400 cursor-not-allowed"
                                    if (is_approved or role == "ROLE_SALES")
                                    else "px-2.5 py-1 rounded-lg text-[11px] font-bold bg-slate-900 hover:bg-slate-800 text-white cursor-pointer"
                                ),
                            ),
                        ],
                        className="pt-2.5 border-t border-slate-100 flex items-center justify-between gap-2",
                    ),
                ],
            )
        )

    profit_str = "****** đ" if role == "ROLE_SALES" else f"+{format_vnd_full(kpis['net_gross_profit'], role)}"
    cap_str = "****** đ" if role == "ROLE_SALES" else format_vnd_full(kpis["recovered_capital"], role)
    margin_str = "**%" if role == "ROLE_SALES" else f"{kpis['gross_margin_pct']:.1f}%"
    share_str = "**%" if role == "ROLE_SALES" else f"{kpis['attached_profit_share_pct']:.1f}%"
    fund_str = "QUỸ CHI: ****** đ" if role == "ROLE_SALES" else f"QUỸ CHI: {format_vnd_full(total_fund, role)}"

    total_core = int(df_cat["core_orders"].sum()) if not df_cat.empty else 0
    total_att = int(df_cat["attached_orders"].sum()) if not df_cat.empty else 0

    return {
        "header_badge": f"{kpis['invoice_count']} hóa đơn thực tế",
        "kpi_rev": format_vnd_full(kpis["total_revenue"], "ROLE_OWNER"),
        "kpi_rev_sub": f"Vốn gốc quay về két: {cap_str} ({kpis['invoice_count']} HĐ)",
        "kpi_profit": profit_str,
        "kpi_profit_sub": f"Biên lãi gộp tổng: {margin_str} · Lãi ròng thực tế",
        "kpi_attach_rev": format_vnd_full(kpis["attached_sales"], "ROLE_OWNER"),
        "kpi_attach_sub": f"Đóng góp {share_str} tổng lợi nhuận gộp từ PK & Công thợ",
        "kpi_attach_rate": f"{kpis['overall_attach_rate_pct']:.1f}%",
        "kpi_attach_orders": f"({total_att} / {total_core} hóa đơn)",
        "kpi_target_badge": "Vượt chuẩn 60%" if kpis["overall_attach_rate_pct"] >= 60 else "Dưới chuẩn 60%",
        "insight_text": (
            f"Insight đắt giá: Phụ kiện & Công thợ đóng góp tới {share_str} LỢI NHUẬN GỘP toàn cửa hàng! Đẩy mạnh bán kèm nhóm Tủ lạnh & Máy giặt."
        ),
        "fig_waterfall": fig_waterfall,
        "fig_attach": fig_attach,
        "category_rows": cat_rows,
        "staff_fund_badge": fund_str,
        "staff_cards": staff_cards,
        "approve_disabled": role == "ROLE_SALES",
    }


def generate_m6_csv(perf_svc: Any) -> bytes:
    """Xuất CSV báo cáo tổng hợp Hiệu quả kinh doanh & Attach-Rate."""
    return perf_svc.export_financial_summary_csv()


def submit_m6_approve_commission(
    perf_svc: Any,
    employee_code: str,
    role: str = "ROLE_OWNER",
) -> Dict[str, Any]:
    """Phê duyệt chi hoa hồng nhân sự qua PerformanceService."""
    return perf_svc.approve_commission(employee_code=employee_code, role=role)


def register_m6_callbacks(app: Any, services: Dict[str, Any]) -> None:
    """Đăng ký callbacks tương tác cho Module 06 Hiệu quả kinh doanh."""
    perf_svc = services["performance"]

    @app.callback(
        Output("m6HeaderInvoiceBadge", "children"),
        Output("m6KpiRev", "children"),
        Output("m6KpiRevSub", "children"),
        Output("m6KpiProfit", "children"),
        Output("m6KpiProfitSub", "children"),
        Output("m6KpiAttachRev", "children"),
        Output("m6KpiAttachSub", "children"),
        Output("m6KpiAttachRate", "children"),
        Output("m6KpiAttachOrders", "children"),
        Output("m6KpiTargetBadge", "children"),
        Output("m6InsightText", "children"),
        Output("m6WaterfallChart", "figure"),
        Output("m6AttachRateChart", "figure"),
        Output("m6CategoryTableBody", "children"),
        Output("m6StaffFundBadge", "children"),
        Output("m6StaffCommissionCards", "children"),
        Output("m6ApproveAllBonusBtn", "disabled"),
        Input("m6PeriodSelect", "value"),
        Input("store-m6-refresh", "data"),
        Input("store-rbac-role", "data"),
    )
    def sync_m6_workspace(period, _ref, role):
        res = render_m6_workspace(perf_svc, period=period or "T10_11", role=role or "ROLE_OWNER")
        return (
            res["header_badge"],
            res["kpi_rev"],
            res["kpi_rev_sub"],
            res["kpi_profit"],
            res["kpi_profit_sub"],
            res["kpi_attach_rev"],
            res["kpi_attach_sub"],
            res["kpi_attach_rate"],
            res["kpi_attach_orders"],
            res["kpi_target_badge"],
            res["insight_text"],
            res["fig_waterfall"],
            res["fig_attach"],
            res["category_rows"],
            res["staff_fund_badge"],
            res["staff_cards"],
            res["approve_disabled"],
        )

    @app.callback(
        Output("store-m6-refresh", "data"),
        Output("store-toast-msg", "data", allow_duplicate=True),
        Input({"type": "m6-approve-emp", "emp": ALL}, "n_clicks"),
        Input("m6ApproveAllBonusBtn", "n_clicks"),
        State("store-rbac-role", "data"),
        State("store-m6-refresh", "data"),
        prevent_initial_call=True,
    )
    def approve_commission_cb(emp_clicks, all_clicks, role, cur_ref):
        ctx = dash.callback_context
        if not ctx.triggered:
            return no_update, no_update
        tid = ctx.triggered_id
        prop = ctx.triggered[0]["prop_id"].split(".")[0]
        eff_role = role or "ROLE_OWNER"

        if prop == "m6ApproveAllBonusBtn":
            staff_list = perf_svc.get_staff_commission_list(role="ROLE_OWNER")
            pending = [s for s in staff_list if s["status"] != "APPROVED"]
            if not pending:
                return no_update, "Tất cả nhân sự đã được duyệt chi hoa hồng."
            for s in pending:
                res = submit_m6_approve_commission(perf_svc, s["employee_code"], role=eff_role)
                if not res.get("success"):
                    return no_update, res.get("error", "Không đủ quyền duyệt hoa hồng")
            return (cur_ref or 0) + 1, f"Đã duyệt chi hoa hồng cho {len(pending)} nhân sự!"

        if isinstance(tid, dict) and tid.get("type") == "m6-approve-emp" and any(emp_clicks or []):
            res = submit_m6_approve_commission(perf_svc, tid["emp"], role=eff_role)
            if res.get("success"):
                return (cur_ref or 0) + 1, res["message"]
            return no_update, res.get("error", "Không thể duyệt chi hoa hồng")
        return no_update, no_update

    @app.callback(
        Output("m6-download-csv", "data"),
        Input("m6ExportCsvBtn", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_m6_csv(n_clicks):
        if not n_clicks:
            return no_update
        csv_bytes = generate_m6_csv(perf_svc)
        return dcc.send_bytes(csv_bytes, "stock_sense_performance_summary.csv")
