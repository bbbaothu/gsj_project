"""
Callbacks Module 03: Chọn SKU Card, Chọn Kịch bản PA1-PA4, Simulator, Price Radar & Approve PoS.
"""
from typing import Any, Dict, List
import dash
from dash import ALL, Input, Output, State, html
import plotly.graph_objects as go

from src.dash_app.components.charts import apply_stock_sense_layout, empty_figure
from src.dash_app.components.layout_shell import format_vnd_compact, format_vnd_full


def render_m3_workspace(
    services: Dict[str, Any],
    sku: str = "TV-LG-55C3",
    tactic_code: str = "PA2",
    target_qty: int = 10,
    extra_disc: float = 0.0,
    role: str = "ROLE_OWNER",
) -> Dict[str, Any]:
    """Chuẩn bị toàn bộ trạng thái 4 SKU cards, 4 Kịch bản, Simulator, Chart và Price Radar."""
    clr_svc = services["clearance"]
    kpis = clr_svc.get_clearance_kpis(role=role)
    candidates = clr_svc.get_clearance_candidates(role="ROLE_OWNER")[:4]
    cand_skus = [c["product_code"] for c in candidates]
    active_sku = sku if sku in cand_skus else (cand_skus[0] if cand_skus else "TV-LG-55C3")
    active_cand = next((c for c in candidates if c["product_code"] == active_sku), candidates[0])

    effective_qty = max(1, min(int(target_qty or active_cand["target_qty"]), active_cand["soh"]))
    tactics = clr_svc.generate_4_tactics(active_sku, target_qty=effective_qty)
    sim = clr_svc.simulate_financials(active_sku, tactic_code, target_qty=effective_qty, extra_discount_pct=float(extra_disc or 0.0), role=role)
    radar = clr_svc.get_market_price_radar(active_sku, role=role)

    # 4 SKU Cards
    sku_cards: List[Any] = []
    for c in candidates:
        is_sel = c["product_code"] == active_sku
        cls = (
            "p-3 rounded-xl border-2 border-indigo-600 bg-indigo-50/40 shadow-sm cursor-pointer transition-all text-left w-full"
            if is_sel
            else "p-3 rounded-xl border border-slate-200 bg-white hover:border-slate-300 cursor-pointer transition-all text-left w-full"
        )
        sku_cards.append(
            html.Button(
                id={"type": "m3-select-sku", "sku": c["product_code"]},
                n_clicks=0,
                className=cls,
                children=[
                    html.Div(
                        [
                            html.Span(c["category_group"], className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-bold text-[10px]"),
                            html.Span("ĐANG CHỌN" if is_sel else f"Tồn: {c['soh']}", className=f"text-[10px] font-bold {'text-indigo-700' if is_sel else 'text-slate-400'}"),
                        ],
                        className="flex items-center justify-between mb-1.5",
                    ),
                    html.Div(c["product_code"], className="font-mono text-[11px] text-slate-500"),
                    html.Div(c["product_name"], className="text-xs font-bold text-slate-900 truncate mt-0.5"),
                    html.Div(
                        [
                            html.Span(f"Đề xuất xả: {c['target_qty']} máy", className="text-rose-600 font-semibold"),
                            html.Span(f"Vốn: {format_vnd_compact(c['cost_price'], role)}", className="text-slate-600 cost-val"),
                        ],
                        className="flex items-center justify-between text-[11px] mt-2 pt-2 border-t border-slate-100",
                    ),
                ],
            )
        )

    # 4 Tactic Radio Cards
    tactic_cards: List[Any] = []
    for t in tactics:
        is_t_sel = t["tactic_code"] == tactic_code
        border_cls = "border-2 border-emerald-600 bg-emerald-50/40" if is_t_sel else "border border-slate-200 bg-white hover:border-slate-300"
        badges = []
        if t["is_recommended"]:
            badges.append(html.Span("⭐ TỐI ƯU", className="px-1.5 py-0.5 rounded bg-emerald-600 text-white text-[10px] font-bold"))
        if t["map_violation"]:
            badges.append(html.Span("Dưới MAP", className="px-1.5 py-0.5 rounded bg-rose-100 text-rose-700 text-[10px] font-bold"))
        profit_txt = "****** đ" if role == "ROLE_SALES" else f"Lãi {effective_qty} máy: {format_vnd_compact(t['total_profit'], role)}"
        tactic_cards.append(
            html.Button(
                id={"type": "m3-select-tactic", "code": t["tactic_code"]},
                n_clicks=0,
                className=f"w-full text-left p-3 rounded-xl transition-all cursor-pointer {border_cls}",
                children=[
                    html.Div(
                        [
                            html.Div([html.Span(t["title"], className="text-xs font-bold text-slate-900 mr-2"), *badges], className="flex items-center flex-wrap gap-1"),
                            html.Span(f"Giá xả: {t['clearance_price']:,.0f} đ", className="font-mono text-xs font-bold text-indigo-700 whitespace-nowrap"),
                        ],
                        className="flex items-center justify-between gap-2",
                    ),
                    html.Div(
                        [html.Span(t["note"], className="text-[11px] text-slate-500"), html.Span(profit_txt, className="font-semibold text-emerald-700 text-[11px] whitespace-nowrap cost-val")],
                        className="flex items-center justify-between gap-2 mt-1",
                    ),
                ],
            )
        )

    # Chart
    if role == "ROLE_SALES":
        tactic_fig = empty_figure("🔒 Đã bảo mật biểu đồ Vốn thu hồi & Lợi nhuận cho Role Sales", height=230)
    else:
        cap_val = float(active_cand["cost_price"]) * effective_qty
        t_names = [t["tactic_code"] for t in tactics]
        t_profs = [t["total_profit"] for t in tactics]
        tactic_fig = go.Figure()
        tactic_fig.add_trace(go.Bar(name="Vốn hoàn két", y=t_names, x=[cap_val] * 4, orientation="h", marker_color="#1E293B", text=[f"{cap_val/1e6:.0f}tr"] * 4, textposition="inside"))
        tactic_fig.add_trace(go.Bar(name="Lãi gộp ròng", y=t_names, x=t_profs, orientation="h", marker_color="#059669", text=[f"+{p/1e6:.1f}tr" for p in t_profs], textposition="outside"))
        max_x = max([cap_val + max(0.0, float(p)) for p in t_profs] or [cap_val])
        tactic_fig.update_layout(barmode="stack", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        tactic_fig.update_xaxes(range=[0, max_x * 1.24])
        apply_stock_sense_layout(tactic_fig, height=230, margin=dict(l=36, r=42, t=28, b=24))

    # Competitor Radar rows
    comp_rows = []
    for c in radar["competitors"]:
        diff = float(c["competitor_price"]) - float(radar["suggested_price"])
        comp_rows.append(
            html.Div(
                [
                    html.Div([html.Div(c["competitor_name"], className="font-semibold text-slate-800"), html.Div(c["promo_note"] or "", className="text-[11px] text-slate-400")]),
                    html.Div(
                        [html.Div(f"{c['competitor_price']:,.0f} đ", className="font-mono font-bold text-slate-900"), html.Div(f"Cao hơn {diff:,.0f} đ" if diff >= 0 else f"Thấp hơn {abs(diff):,.0f} đ", className="text-[11px] text-emerald-700 font-medium")],
                        className="text-right shrink-0",
                    ),
                ],
                className="p-2.5 rounded-lg bg-slate-50 border border-slate-200/70 flex items-center justify-between text-xs",
            )
        )

    is_sales = role == "ROLE_SALES"
    is_loss = bool(sim["is_loss"])

    return {
        "active_sku": active_sku,
        "sku_cards": sku_cards,
        "tactic_cards": tactic_cards,
        "tactic_fig": tactic_fig,
        "competitor_rows": comp_rows,
        "kpi_recovery": format_vnd_compact(kpis["expected_recovery_capital"], role),
        "kpi_qty_sub": f"{kpis['total_target_qty']} máy · {kpis['candidate_skus_count']} mã",
        "kpi_profit": format_vnd_compact(kpis["expected_gross_profit"], role),
        "kpi_roi_badge": "Bảo mật" if is_sales else f"ROI {kpis['roi_pct']}%",
        "kpi_pai_text": f"Rẻ hơn {radar['pai_pct']}%",
        "kpi_active_camp": f"{kpis['active_campaigns_count']} Đang chạy",
        "kpi_pending_camp": f"· {kpis['pending_campaigns_count']} Chờ duyệt",
        "sim_revenue": format_vnd_compact(sim["expected_revenue"], "ROLE_OWNER"),
        "sim_capital": format_vnd_compact(sim["recovered_capital"], role),
        "sim_promo_cost": format_vnd_compact(sim["total_promo_cost"], role),
        "sim_net_profit": "****** đ" if is_sales else f"{format_vnd_compact(sim['net_gross_profit'], role)} ({sim['roi_pct']}%)",
        "effective_price": sim["effective_unit_price"],
        "suggested_price_text": f"{radar['suggested_price']:,.0f} đ",
        "pai_summary_text": f"Rẻ hơn TB {radar['pai_pct']}% · Lãi máy: {format_vnd_compact(radar['unit_margin_vnd'], role)}",
        "sales_lock_style": {"display": "flex" if is_sales else "none"},
        "cap_protect_style": {"display": "flex" if (is_loss and not is_sales) else "none"},
        "tag_product_name": active_cand["product_name"],
        "tag_old_price": f"{active_cand['sale_price']:,.0f} đ",
        "tag_new_price": f"{sim['effective_unit_price']:,.0f} đ",
    }


def submit_m3_approve_campaign(
    sku: str, tactic_code: str, target_qty: int, effective_price: float, services: Dict[str, Any], role: str = "ROLE_OWNER"
) -> Dict[str, Any]:
    """Lưu chiến dịch xả hàng thông qua ClearanceService."""
    return services["clearance"].approve_clearance_campaign(
        product_code=sku,
        tactic_code=tactic_code,
        target_qty=int(target_qty or 1),
        clearance_price=float(effective_price),
        role=role,
    )


def register_m3_callbacks(app: dash.Dash, services: Dict[str, Any]) -> None:
    """Đăng ký tập trung các Callbacks cho Module 03."""

    @app.callback(
        Output("store-m3-sku", "data"),
        Input({"type": "m3-select-sku", "sku": ALL}, "n_clicks"),
        Input("store-selected-sku", "data"),
        prevent_initial_call=True,
    )
    def on_m3_select_sku(_card_clicks, global_sku):
        trig = dash.ctx.triggered_id
        if isinstance(trig, dict) and trig.get("type") == "m3-select-sku":
            if not (dash.ctx.triggered and dash.ctx.triggered[0]["value"]):
                return dash.no_update
            return trig["sku"]
        if trig == "store-selected-sku" and global_sku:
            return global_sku
        return dash.no_update

    @app.callback(
        Output("store-m3-tactic", "data"),
        Input({"type": "m3-select-tactic", "code": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def on_m3_select_tactic(_clicks):
        trig = dash.ctx.triggered_id
        if isinstance(trig, dict) and trig.get("type") == "m3-select-tactic":
            if not (dash.ctx.triggered and dash.ctx.triggered[0]["value"]):
                return dash.no_update
            return trig["code"]
        return dash.no_update

    @app.callback(
        Output("m3SkuSelectorGrid", "children"),
        Output("m3TacticsContainer", "children"),
        Output("m3-tactic-chart", "figure"),
        Output("m3CompetitorListContainer", "children"),
        Output("m3KpiTotalRecovery", "children"),
        Output("m3KpiTotalProfit", "children"),
        Output("m3KpiMarginPill", "children"),
        Output("m3KpiPaiHero", "children"),
        Output("m3KpiActiveCampaigns", "children"),
        Output("m3KpiPendingCampaigns", "children"),
        Output("m3SelectedSkuHeaderBadge", "children"),
        Output("m3SimBoxRevenue", "children"),
        Output("m3SimBoxCapital", "children"),
        Output("m3SimBoxPromoCost", "children"),
        Output("m3SimBoxNetProfit", "children"),
        Output("m3SuggestedPriceHero", "children"),
        Output("m3SuggestedUnitProfitText", "children"),
        Output("m3SalesLockBanner", "style"),
        Output("m3CapitalProtectionBanner", "style"),
        Output("store-m3-effective-price", "data"),
        Output("m3TagSkuCode", "children"),
        Output("m3TagProductName", "children"),
        Output("m3TagOldPrice", "children"),
        Output("m3TagNewPrice", "children"),
        Input("store-m3-sku", "data"),
        Input("store-m3-tactic", "data"),
        Input("m3-discount-slider", "value"),
        Input("m3-qty-input", "value"),
        Input("store-role", "data"),
        Input("store-refresh-tick", "data"),
        prevent_initial_call=True,
    )
    def on_m3_refresh(sku, tactic, disc, qty, role, _tick):
        ws = render_m3_workspace(
            services,
            sku=sku or "TV-LG-55C3",
            tactic_code=tactic or "PA2",
            target_qty=int(qty or 10),
            extra_disc=float(disc or 0.0),
            role=role or "ROLE_OWNER",
        )
        return (
            ws["sku_cards"],
            ws["tactic_cards"],
            ws["tactic_fig"],
            ws["competitor_rows"],
            ws["kpi_recovery"],
            ws["kpi_profit"],
            ws["kpi_roi_badge"],
            ws["kpi_pai_text"],
            ws["kpi_active_camp"],
            ws["kpi_pending_camp"],
            ws["active_sku"],
            ws["sim_revenue"],
            ws["sim_capital"],
            ws["sim_promo_cost"],
            ws["sim_net_profit"],
            ws["suggested_price_text"],
            ws["pai_summary_text"],
            ws["sales_lock_style"],
            ws["cap_protect_style"],
            ws["effective_price"],
            ws["active_sku"],
            ws["tag_product_name"],
            ws["tag_old_price"],
            ws["tag_new_price"],
        )

    @app.callback(
        Output("store-toast", "data", allow_duplicate=True),
        Output("store-refresh-tick", "data", allow_duplicate=True),
        Input("btn-m3-approve-pos", "n_clicks"),
        State("store-m3-sku", "data"),
        State("store-m3-tactic", "data"),
        State("m3-qty-input", "value"),
        State("store-m3-effective-price", "data"),
        State("store-role", "data"),
        State("store-refresh-tick", "data"),
        prevent_initial_call=True,
    )
    def on_m3_approve(_n, sku, tactic, qty, price, role, tick):
        res = submit_m3_approve_campaign(sku, tactic, qty, price, services, role=role or "ROLE_OWNER")
        if res["success"]:
            return {"open": True, "message": res["message"], "kind": "success"}, int(tick or 0) + 1
        return {"open": True, "message": f"[{res.get('error_code')}] {res['error']}", "kind": "error"}, dash.no_update

    @app.callback(
        Output("m3SaleTagModal", "style"),
        Input("btn-m3-open-tag-modal", "n_clicks"),
        Input("btn-close-m3-tag-modal", "n_clicks"),
        Input("btn-cancel-m3-tag-modal", "n_clicks"),
        Input("btn-confirm-m3-print-tag", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_m3_tag_modal(*_args):
        if dash.ctx.triggered_id == "btn-m3-open-tag-modal":
            return {"display": "flex"}
        return {"display": "none"}

    @app.callback(
        Output("m3CampaignModal", "style"),
        Output("m3CampaignModalBody", "children"),
        Input("btn-m3-open-campaign-modal", "n_clicks"),
        Input("btn-close-m3-campaign-modal", "n_clicks"),
        Input("btn-cancel-m3-campaign-modal", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_m3_campaign_modal(_open, _c1, _c2):
        if dash.ctx.triggered_id != "btn-m3-open-campaign-modal":
            return {"display": "none"}, dash.no_update
        conn = services["clearance"]._get_connection()
        rows = conn.execute(
            "SELECT product_code, tactic_code, target_qty, clearance_price, expected_profit, status FROM FACT_CLEARANCE_CAMPAIGNS ORDER BY campaign_id DESC;"
        ).fetchall()
        conn.close()
        cards = [
            html.Div(
                [
                    html.Div([html.Span(r["product_code"], className="font-mono font-bold mr-2"), html.Span(r["tactic_code"], className="px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 font-semibold")]),
                    html.Div([html.Span(f"SL: {r['target_qty']} · Giá: {r['clearance_price']:,.0f} đ · "), html.Strong(r["status"], className="text-emerald-700")]),
                ],
                className="p-2.5 rounded-lg border border-slate-200 flex items-center justify-between",
            )
            for r in rows
        ]
        return {"display": "flex"}, cards
