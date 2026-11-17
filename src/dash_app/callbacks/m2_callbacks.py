"""
Callbacks Module 02: Cần xử lý hôm nay — Lọc 2 chiều KPI/Pills, Biểu đồ, Decision Drawer & Snooze Modal.
"""
import io
from typing import Any, Dict, List, Optional
import dash
from dash import ALL, Input, Output, State, dcc, html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.dash_app.components.charts import apply_stock_sense_layout, empty_figure
from src.dash_app.components.layout_shell import format_vnd_compact

M2_KPI_BASE = "kpi-card cursor-pointer bg-white rounded-xl p-4 shadow-2xs select-none"
M2_KPI_ACT = f"{M2_KPI_BASE} border-2 border-slate-900"
M2_KPI_IDLE = f"{M2_KPI_BASE} border border-slate-200/90 hover:border-slate-300"

M2_PILL_ACT = "px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-slate-900 text-white transition flex items-center gap-1 cursor-pointer whitespace-nowrap"
M2_PILL_IDLE = "px-2.5 py-1 rounded-lg text-[11px] font-medium text-slate-600 hover:bg-slate-100 border border-slate-200/80 transition flex items-center gap-1 cursor-pointer whitespace-nowrap"


def render_m2_workspace(
    services: Dict[str, Any],
    filter_key: str = "all",
    search: str = "",
    lead_time_override: Optional[int] = None,
    role: str = "ROLE_OWNER",
) -> Dict[str, Any]:
    """Chuẩn bị toàn bộ dữ liệu KPI, Bảng 7 cột hợp nhất và 2 Biểu đồ Plotly cho Module 02."""
    alert_svc = services["alert"]
    kpis = alert_svc.get_alert_kpis(role=role)
    df_slow = alert_svc.get_slow_moving_alerts(role=role, include_snoozed=False)
    df_stockout = alert_svc.get_stockout_alerts()

    slow_rows = df_slow.to_dict(orient="records") if not df_slow.empty else []
    stockout_rows = df_stockout.to_dict(orient="records") if not df_stockout.empty else []

    counts = {
        "all": len(slow_rows) + len(stockout_rows),
        "stagnant": len(slow_rows),
        "dead": sum(1 for r in slow_rows if r["risk_group"] == "Tồn chết / Vượt trần"),
        "seasonal": sum(1 for r in slow_rows if r["risk_group"] == "Sắp hết mùa"),
        "stockout": len(stockout_rows),
    }

    dead_cap = sum(float(r["stagnant_capital"]) for r in slow_rows if r["risk_group"] == "Tồn chết / Vượt trần") if role != "ROLE_SALES" else None
    seasonal_cap = sum(float(r["stagnant_capital"]) for r in slow_rows if r["risk_group"] == "Sắp hết mùa") if role != "ROLE_SALES" else None

    kpi_cards = [
        html.Div(
            id="m2-kpi-stagnant",
            n_clicks=0,
            className=M2_KPI_ACT if filter_key == "stagnant" else M2_KPI_IDLE,
            children=[
                html.Div(
                    [
                        html.Span([html.Span(className="w-2 h-2 rounded-full bg-amber-500"), "TỔNG VỐN KẸT CẦN XẢ"], className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500"),
                        html.Span(f"{counts['stagnant']} SKU", className="px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-50 text-amber-800 border border-amber-200/60"),
                    ],
                    className="flex items-center justify-between gap-2 mb-2 whitespace-nowrap",
                ),
                html.Div(
                    [
                        html.Span(format_vnd_compact(kpis["stagnant_capital"], role), className="text-2xl font-bold tracking-tight text-slate-900 tabular-nums cost-val"),
                        html.Span(f"{sum(r['soh'] for r in slow_rows)} máy", className="text-xs font-medium text-slate-400"),
                    ],
                    className="flex items-baseline gap-2 mb-2.5 whitespace-nowrap",
                ),
                html.Div(
                    [html.Span("Giải phóng vốn lưu động"), html.Span("Lọc nhóm chậm →", className="font-semibold text-slate-700")],
                    className="flex items-center justify-between text-xs pt-2 border-t border-slate-100 whitespace-nowrap text-slate-500",
                ),
            ],
        ),
        html.Div(
            id="m2-kpi-dead",
            n_clicks=0,
            className=M2_KPI_ACT if filter_key == "dead" else M2_KPI_IDLE,
            children=[
                html.Div(
                    [
                        html.Span([html.Span(className="w-2 h-2 rounded-full bg-slate-600"), "TỒN CHẾT & VƯỢT TRẦN"], className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500"),
                        html.Span("DSI > 60d", className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-700 border border-slate-200"),
                    ],
                    className="flex items-center justify-between gap-2 mb-2 whitespace-nowrap",
                ),
                html.Div(
                    [
                        html.Span(format_vnd_compact(dead_cap, role), className="text-2xl font-bold tracking-tight text-slate-900 tabular-nums cost-val"),
                        html.Span(f"{counts['dead']} mã", className="text-xs font-medium text-slate-400"),
                    ],
                    className="flex items-baseline gap-2 mb-2.5 whitespace-nowrap",
                ),
                html.Div(
                    [html.Span("Nguy cơ trôi bảo hành"), html.Span("Xả thu vốn →", className="font-semibold text-slate-700")],
                    className="flex items-center justify-between text-xs pt-2 border-t border-slate-100 whitespace-nowrap text-slate-500",
                ),
            ],
        ),
        html.Div(
            id="m2-kpi-seasonal",
            n_clicks=0,
            className=M2_KPI_ACT if filter_key == "seasonal" else M2_KPI_IDLE,
            children=[
                html.Div(
                    [
                        html.Span([html.Span(className="w-2 h-2 rounded-full bg-amber-500"), "TRÁI MÙA & SẮP HẾT MÙA"], className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500"),
                        html.Span("Đẩy trước vụ", className="px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-50 text-amber-800 border border-amber-200/60"),
                    ],
                    className="flex items-center justify-between gap-2 mb-2 whitespace-nowrap",
                ),
                html.Div(
                    [
                        html.Span(format_vnd_compact(seasonal_cap, role), className="text-2xl font-bold tracking-tight text-amber-600 tabular-nums cost-val"),
                        html.Span(f"{counts['seasonal']} mã ĐH", className="text-xs font-medium text-slate-400"),
                    ],
                    className="flex items-baseline gap-2 mb-2.5 whitespace-nowrap",
                ),
                html.Div(
                    [html.Span("Điều hòa cuối vụ hè"), html.Span("Xả mùa vụ →", className="font-semibold text-amber-700")],
                    className="flex items-center justify-between text-xs pt-2 border-t border-slate-100 whitespace-nowrap text-slate-500",
                ),
            ],
        ),
        html.Div(
            id="m2-kpi-stockout",
            n_clicks=0,
            className=M2_KPI_ACT if filter_key == "stockout" else M2_KPI_IDLE,
            children=[
                html.Div(
                    [
                        html.Span([html.Span(className="w-2 h-2 rounded-full bg-rose-600"), "SẮP CHÁY KHO (DOS)"], className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500"),
                        html.Span(f"{kpis['stockout_risk_skus']} mã trống PO", className="px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200/60"),
                    ],
                    className="flex items-center justify-between gap-2 mb-2 whitespace-nowrap",
                ),
                html.Div(
                    [
                        html.Span(f"-{format_vnd_compact(kpis['daily_lost_revenue'], 'ROLE_OWNER')}/ngày", className="text-2xl font-bold tracking-tight text-rose-600 tabular-nums"),
                        html.Span(f"+{kpis['in_transit_skus']} xe đang về", className="text-xs font-medium text-blue-600"),
                    ],
                    className="flex items-baseline gap-2 mb-2.5 whitespace-nowrap",
                ),
                html.Div(
                    [html.Span("Khử báo động giả INC > 0"), html.Span("Nhập bù gấp →", className="font-semibold text-rose-600")],
                    className="flex items-center justify-between text-xs pt-2 border-t border-slate-100 whitespace-nowrap text-slate-500",
                ),
            ],
        ),
    ]

    # Combine filtered rows into 7-column unified alert table
    kw = (search or "").strip().lower()
    table_rows: List[html.Tr] = []

    if filter_key in ("all", "stagnant", "dead", "seasonal"):
        for r in slow_rows:
            if filter_key == "dead" and r["risk_group"] != "Tồn chết / Vượt trần":
                continue
            if filter_key == "seasonal" and r["risk_group"] != "Sắp hết mùa":
                continue
            if kw and kw not in r["product_code"].lower() and kw not in r["product_name"].lower():
                continue
            cap_str = format_vnd_compact(r.get("stagnant_capital"), role)
            table_rows.append(
                html.Tr(
                    className="hover:bg-slate-50/90 transition-colors",
                    children=[
                        html.Td(
                            [html.Span(r["product_code"], className="font-mono font-bold text-slate-900 mr-2"), html.Span(r["product_name"], className="text-slate-700")],
                            className="py-2.5 px-4",
                        ),
                        html.Td(html.Span(r["risk_badge"], className="px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200 font-semibold text-[11px] whitespace-nowrap"), className="py-2.5 px-3"),
                        html.Td(f"SOH: {r['soh']}", className="py-2.5 px-3 text-right font-mono font-semibold text-slate-800"),
                        html.Td("0", className="py-2.5 px-3 text-right font-mono text-slate-400"),
                        html.Td(f"DSI: {r['dsi_days']:.0f}d", className="py-2.5 px-3 text-right font-mono font-semibold text-rose-600"),
                        html.Td(cap_str, className="py-2.5 px-3 text-right font-mono font-bold text-slate-900 cost-val whitespace-nowrap"),
                        html.Td(
                            html.Div(
                                [
                                    html.Button("Chi tiết", id={"type": "m2-open-drawer", "sku": r["product_code"], "kind": "slow"}, n_clicks=0, className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium cursor-pointer"),
                                    html.Button("Xả hàng →", id={"type": "m2-goto-m3", "sku": r["product_code"]}, n_clicks=0, className="px-2.5 py-1 rounded-lg bg-amber-500 hover:bg-amber-600 text-white font-semibold cursor-pointer whitespace-nowrap"),
                                ],
                                className="flex items-center justify-end gap-1.5",
                            ),
                            className="py-2.5 px-4 text-right",
                        ),
                    ],
                )
            )

    if filter_key in ("all", "stockout"):
        for r in stockout_rows:
            if kw and kw not in r["product_code"].lower() and kw not in r["product_name"].lower():
                continue
            lost_txt = "0 đ (Có PO về)" if r["inc"] > 0 else f"-{format_vnd_compact(r['daily_lost_revenue'], 'ROLE_OWNER')}/ng"
            badge_cls = (
                "px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 font-semibold text-[11px] whitespace-nowrap"
                if r["inc"] > 0
                else "px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200 font-semibold text-[11px] whitespace-nowrap"
            )
            table_rows.append(
                html.Tr(
                    className="hover:bg-slate-50/90 transition-colors",
                    children=[
                        html.Td(
                            [html.Span(r["product_code"], className="font-mono font-bold text-slate-900 mr-2"), html.Span(r["product_name"], className="text-slate-700")],
                            className="py-2.5 px-4",
                        ),
                        html.Td(html.Span(r["severity"], className=badge_cls), className="py-2.5 px-3"),
                        html.Td(f"AVL: {r['avl']}", className="py-2.5 px-3 text-right font-mono font-bold text-rose-600"),
                        html.Td(f"+{r['inc']}" if r["inc"] > 0 else "0", className="py-2.5 px-3 text-right font-mono font-semibold text-blue-700"),
                        html.Td(f"DOS: {r['dos_days']:.1f}d", className="py-2.5 px-3 text-right font-mono font-semibold text-slate-900"),
                        html.Td(lost_txt, className="py-2.5 px-3 text-right font-mono text-rose-600 font-semibold whitespace-nowrap"),
                        html.Td(
                            html.Div(
                                [
                                    html.Button("Chi tiết", id={"type": "m2-open-drawer", "sku": r["product_code"], "kind": "stockout"}, n_clicks=0, className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium cursor-pointer"),
                                    html.Button("Nhập gấp →", id={"type": "m2-goto-m4", "sku": r["product_code"]}, n_clicks=0, className="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-semibold cursor-pointer whitespace-nowrap"),
                                ],
                                className="flex items-center justify-end gap-1.5",
                            ),
                            className="py-2.5 px-4 text-right",
                        ),
                    ],
                )
            )

    if not table_rows:
        table_rows.append(html.Tr(html.Td("Không có cảnh báo phù hợp bộ lọc.", colSpan=7, className="py-8 text-center text-slate-400")))

    # Charts
    if role == "ROLE_SALES":
        cap_fig = empty_figure("🔒 Đã bảo mật biểu đồ Vốn kẹt theo Role Sales", height=250)
    elif not df_slow.empty:
        cap_fig = px.bar(
            df_slow.head(6),
            x="stagnant_capital",
            y="product_code",
            orientation="h",
            color="risk_group",
            color_discrete_map={"Tồn chết / Vượt trần": "#DC2626", "Sắp hết mùa": "#EA580C", "Hãng EOL": "#D97706"},
        )
        cap_fig.update_yaxes(autorange="reversed")
        cap_fig.update_layout(showlegend=False, xaxis_title="Vốn kẹt (VNĐ)", yaxis_title="")
        apply_stock_sense_layout(cap_fig, height=250)
    else:
        cap_fig = empty_figure("Không còn SKU kẹt vốn", height=250)

    lt_line = int(lead_time_override or 4)
    if not df_stockout.empty:
        colors = ["#2563EB" if inc > 0 else ("#DC2626" if dos <= lt else "#D97706") for inc, dos, lt in zip(df_stockout["inc"], df_stockout["dos_days"], df_stockout["lead_time_days"])]
        runway_fig = go.Figure(
            go.Bar(
                x=df_stockout["product_code"],
                y=df_stockout["dos_days"],
                marker_color=colors,
                text=[f"{d:.1f}d" for d in df_stockout["dos_days"]],
                textposition="outside",
            )
        )
        runway_fig.add_hline(y=lt_line, line_dash="dash", line_color="#DC2626", annotation_text=f"Lead Time {lt_line}d")
        runway_fig.update_layout(xaxis_title="Mã SKU", yaxis_title="Số ngày bán còn lại (DOS)")
        apply_stock_sense_layout(runway_fig, height=250)
    else:
        runway_fig = empty_figure("Toàn bộ SKU đều đủ bán an toàn", height=250)

    pill_classes = {k: (M2_PILL_ACT if k == filter_key else M2_PILL_IDLE) for k in counts}

    return {
        "kpi_cards": kpi_cards,
        "table_rows": table_rows,
        "capital_fig": cap_fig,
        "runway_fig": runway_fig,
        "counts": counts,
        "pill_classes": pill_classes,
    }


def build_m2_drawer_body(sku: str, services: Dict[str, Any], role: str = "ROLE_OWNER") -> Dict[str, Any]:
    """Lấy chi tiết cảnh báo của 1 SKU cho Slide-over Decision Drawer M2."""
    alert_svc = services["alert"]
    df_slow = alert_svc.get_slow_moving_alerts(role=role, include_snoozed=True)
    df_st = alert_svc.get_stockout_alerts()

    if not df_slow.empty and sku in df_slow["product_code"].values:
        r = df_slow[df_slow["product_code"] == sku].iloc[0].to_dict()
        cap_txt = format_vnd_compact(r.get("stagnant_capital"), role)
        return {
            "sku": sku,
            "badge": r["risk_badge"],
            "name": r["product_name"],
            "meta": f"{sku} · Tồn SOH: {r['soh']} máy · Chưa bán: {r['days_since_last_sale']} ngày",
            "body": html.Div(
                [
                    html.Div([html.Strong("Vốn đang kẹt: "), html.Span(cap_txt, className="cost-val font-bold text-rose-600")], className="p-3 rounded-lg bg-slate-50 border border-slate-200"),
                    html.Div([html.Strong("Chỉ số DSI ước tính: "), f"{r['dsi_days']} ngày (vượt ngưỡng an toàn 60 ngày)."], className="p-3 rounded-lg bg-amber-50 border border-amber-200"),
                    html.Div([html.Strong("Đề xuất hành động: "), f"Chuyển {r['suggested_clearance_qty']} máy sang Module 03 để chạy kịch bản Combo phụ kiện thu hồi vốn nhanh."], className="p-3 rounded-lg bg-blue-50 border border-blue-200"),
                ],
                className="space-y-2.5",
            ),
            "target_module": "m3",
            "cta_label": "Chuyển sang M3: Gợi ý Xả hàng →",
        }

    if not df_st.empty and sku in df_st["product_code"].values:
        r = df_st[df_st["product_code"] == sku].iloc[0].to_dict()
        return {
            "sku": sku,
            "badge": r["severity"],
            "name": r["product_name"],
            "meta": f"{sku} · AVL: {r['avl']} · INC: {r['inc']} · Lead Time: {r['lead_time_days']} ngày",
            "body": html.Div(
                [
                    html.Div([html.Strong("Trạng thái đường ống: "), r["po_info"]], className="p-3 rounded-lg bg-blue-50 border border-blue-200"),
                    html.Div([html.Strong("Đề xuất nhập bù: "), f"{r['po_draft_qty']} máy (theo tốc độ bán {r['rr_7']} máy/ngày)."], className="p-3 rounded-lg bg-amber-50 border border-amber-200"),
                ],
                className="space-y-2.5",
            ),
            "target_module": "m4",
            "cta_label": "Chuyển sang M4: Tạo đơn PO →",
        }

    return {
        "sku": sku,
        "badge": "Bình thường",
        "name": sku,
        "meta": "",
        "body": html.P("Không có cảnh báo đang hoạt động cho SKU này."),
        "target_module": "m1",
        "cta_label": "Quay về M1",
    }


def submit_m2_snooze(
    sku: str, snooze_days: int, reason: str, services: Dict[str, Any], role: str = "ROLE_OWNER"
) -> Dict[str, Any]:
    """Gọi AlertService.snooze_alert kiểm tra ERR_ACT_003 và lưu DB."""
    return services["alert"].snooze_alert(
        product_code=sku,
        snooze_days=int(snooze_days or 14),
        reason=reason or "",
        role=role,
    )


def register_m2_callbacks(app: dash.Dash, services: Dict[str, Any]) -> None:
    """Đăng ký các Callbacks cho Module 02."""

    @app.callback(
        Output("store-m2-filter", "data"),
        Input("m2-kpi-stagnant", "n_clicks"),
        Input("m2-kpi-dead", "n_clicks"),
        Input("m2-kpi-seasonal", "n_clicks"),
        Input("m2-kpi-stockout", "n_clicks"),
        Input("m2-pill-all", "n_clicks"),
        Input("m2-pill-stagnant", "n_clicks"),
        Input("m2-pill-dead", "n_clicks"),
        Input("m2-pill-seasonal", "n_clicks"),
        Input("m2-pill-stockout", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_m2_filter_select(*_args):
        trig = dash.ctx.triggered_id or ""
        for k in ("all", "stagnant", "dead", "seasonal", "stockout"):
            if trig.endswith(f"-{k}"):
                return k
        return "all"

    @app.callback(
        Output("m2-kpi-section", "children"),
        Output("m2-alerts-table-body", "children"),
        Output("m2-capital-chart", "figure"),
        Output("m2-runway-chart", "figure"),
        Output("m2-pill-all", "className"),
        Output("m2-pill-stagnant", "className"),
        Output("m2-pill-dead", "className"),
        Output("m2-pill-seasonal", "className"),
        Output("m2-pill-stockout", "className"),
        Output("m2HeaderAlertCountBadge", "children"),
        Input("store-m2-filter", "data"),
        Input("m2-search-input", "value"),
        Input("store-m2-lead-time", "data"),
        Input("store-role", "data"),
        Input("store-refresh-tick", "data"),
        prevent_initial_call=True,
    )
    def on_m2_refresh(filter_key, search, lt_val, role, _tick):
        ws = render_m2_workspace(
            services,
            filter_key=filter_key or "all",
            search=search or "",
            lead_time_override=lt_val,
            role=role or "ROLE_OWNER",
        )
        pc = ws["pill_classes"]
        return (
            ws["kpi_cards"],
            ws["table_rows"],
            ws["capital_fig"],
            ws["runway_fig"],
            pc["all"],
            pc["stagnant"],
            pc["dead"],
            pc["seasonal"],
            pc["stockout"],
            f"{ws['counts']['all']} CẢNH BÁO",
        )

    @app.callback(
        Output("m2DecisionDrawer", "className"),
        Output("m2DrawerBackdrop", "style"),
        Output("store-m2-drawer-sku", "data"),
        Output("store-m2-drawer-target", "data"),
        Output("m2DrawerTypeBadge", "children"),
        Output("m2DrawerProductName", "children"),
        Output("m2DrawerMeta", "children"),
        Output("m2DrawerBodyContent", "children"),
        Output("btn-m2-drawer-primary", "children"),
        Input({"type": "m2-open-drawer", "sku": ALL, "kind": ALL}, "n_clicks"),
        Input("btn-close-m2-drawer", "n_clicks"),
        Input("m2DrawerBackdrop", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_m2_drawer(_clicks, _close_btn, _backdrop):
        trig = dash.ctx.triggered_id
        closed_cls = "fixed top-0 right-0 h-full w-[460px] max-w-full bg-white shadow-2xl border-l border-slate-200 z-50 transform translate-x-full transition-transform duration-200 flex flex-col justify-between"
        open_cls = "fixed top-0 right-0 h-full w-[460px] max-w-full bg-white shadow-2xl border-l border-slate-200 z-50 transform translate-x-0 transition-transform duration-200 flex flex-col justify-between"

        if trig in ("btn-close-m2-drawer", "m2DrawerBackdrop"):
            return closed_cls, {"display": "none"}, None, dash.no_update, *[dash.no_update] * 5

        if isinstance(trig, dict) and trig.get("type") == "m2-open-drawer":
            if not (dash.ctx.triggered and dash.ctx.triggered[0]["value"]):
                return tuple([dash.no_update] * 9)
            sku = trig["sku"]
            info = build_m2_drawer_body(sku, services, role="ROLE_OWNER")
            return open_cls, {"display": "block"}, sku, info["target_module"], info["badge"], info["name"], info["meta"], info["body"], info["cta_label"]

        return tuple([dash.no_update] * 9)

    @app.callback(
        Output("snoozeModal", "style"),
        Output("store-m2-snooze-sku", "data"),
        Output("snoozeTargetTitle", "children"),
        Output("m2-snooze-error", "children"),
        Output("store-refresh-tick", "data", allow_duplicate=True),
        Output("store-toast", "data", allow_duplicate=True),
        Input("btn-m2-drawer-snooze", "n_clicks"),
        Input("btn-close-snooze-modal", "n_clicks"),
        Input("btn-cancel-snooze-modal", "n_clicks"),
        Input("btn-confirm-m2-snooze", "n_clicks"),
        State("store-m2-drawer-sku", "data"),
        State("store-m2-snooze-sku", "data"),
        State("m2-snooze-days", "value"),
        State("m2-snooze-reason", "value"),
        State("store-role", "data"),
        State("store-refresh-tick", "data"),
        prevent_initial_call=True,
    )
    def on_m2_snooze_modal(_open, _c1, _c2, _confirm, drawer_sku, snooze_sku, days, reason, role, tick):
        trig = dash.ctx.triggered_id
        if trig == "btn-m2-drawer-snooze":
            target_sku = drawer_sku or "TV-LG-55C3"
            return {"display": "flex"}, target_sku, f"SKU: {target_sku}", "", dash.no_update, dash.no_update
        if trig in ("btn-close-snooze-modal", "btn-cancel-snooze-modal"):
            return {"display": "none"}, None, dash.no_update, "", dash.no_update, dash.no_update
        if trig == "btn-confirm-m2-snooze":
            res = submit_m2_snooze(snooze_sku or drawer_sku or "TV-LG-55C3", days, reason, services, role=role or "ROLE_OWNER")
            if not res["success"]:
                return {"display": "flex"}, snooze_sku, dash.no_update, f"[{res.get('error_code')}] {res['error']}", dash.no_update, dash.no_update
            return (
                {"display": "none"},
                None,
                dash.no_update,
                "",
                int(tick or 0) + 1,
                {"open": True, "message": res["message"], "kind": "success"},
            )
        return tuple([dash.no_update] * 6)

    @app.callback(
        Output("m2ThresholdModal", "style"),
        Output("store-m2-lead-time", "data"),
        Output("m2LeadTimeDisplay", "children"),
        Input("btn-open-m2-threshold", "n_clicks"),
        Input("btn-close-m2-threshold", "n_clicks"),
        Input("btn-cancel-m2-threshold", "n_clicks"),
        Input("btn-save-m2-threshold", "n_clicks"),
        Input("store-quick-action", "data"),
        State("m2LeadTimeInput", "value"),
        prevent_initial_call=True,
    )
    def on_m2_threshold_modal(_open, _c1, _c2, _save, quick_action, lt_input):
        trig = dash.ctx.triggered_id
        if trig == "btn-open-m2-threshold" or (trig == "store-quick-action" and quick_action == "OPEN_M2_THRESHOLD_MODAL"):
            return {"display": "flex"}, dash.no_update, dash.no_update
        if trig in ("btn-close-m2-threshold", "btn-cancel-m2-threshold"):
            return {"display": "none"}, dash.no_update, dash.no_update
        if trig == "btn-save-m2-threshold":
            lt = max(1, int(lt_input or 4))
            return {"display": "none"}, lt, f"{lt} ngày"
        return dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        Output("store-active-tab", "data", allow_duplicate=True),
        Output("store-selected-sku", "data", allow_duplicate=True),
        Input({"type": "m2-goto-m3", "sku": ALL}, "n_clicks"),
        Input({"type": "m2-goto-m4", "sku": ALL}, "n_clicks"),
        Input("btn-m2-drawer-primary", "n_clicks"),
        State("store-m2-drawer-sku", "data"),
        State("store-m2-drawer-target", "data"),
        prevent_initial_call=True,
    )
    def on_m2_cross_navigate(_m3, _m4, _drawer_cta, drawer_sku, drawer_target):
        trig = dash.ctx.triggered_id
        if isinstance(trig, dict):
            if not (dash.ctx.triggered and dash.ctx.triggered[0]["value"]):
                return dash.no_update, dash.no_update
            if trig.get("type") == "m2-goto-m3":
                return "m3", trig["sku"]
            if trig.get("type") == "m2-goto-m4":
                return "m4", trig["sku"]
        if trig == "btn-m2-drawer-primary" and drawer_sku:
            return drawer_target or "m3", drawer_sku
        return dash.no_update, dash.no_update

    @app.callback(
        Output("m2-download-csv", "data"),
        Input("btn-m2-export-csv", "n_clicks"),
        State("store-role", "data"),
        prevent_initial_call=True,
    )
    def on_m2_export_csv(_n, role):
        df = services["alert"].get_slow_moving_alerts(role=role or "ROLE_OWNER", include_snoozed=False)
        return dcc.send_data_frame(df.to_csv, "stock_sense_can_xu_ly_hom_nay.csv", index=False, encoding="utf-8-sig")

    @app.callback(
        Output("store-refresh-tick", "data", allow_duplicate=True),
        Output("store-toast", "data", allow_duplicate=True),
        Input("btn-m2-restore-snoozed", "n_clicks"),
        State("store-refresh-tick", "data"),
        prevent_initial_call=True,
    )
    def on_m2_restore_snoozed(_n, tick):
        conn = services["alert"]._get_connection()
        conn.execute("UPDATE SYS_ALERT_SNOOZE_LOG SET is_active = 0;")
        conn.commit()
        conn.close()
        return int(tick or 0) + 1, {"open": True, "message": "Đã khôi phục toàn bộ cảnh báo đang tạm hoãn!", "kind": "success"}
