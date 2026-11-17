"""
Callbacks Module 02 (Parity V2): Cần xử lý hôm nay —
Pie Chart Vốn kẹt dải Vàng-Cam-Đỏ-Nâu đỏ, Bảng 7 cột Ảnh 1 với .cell-hscroll, Bộ lọc Hãng/Ngành/Xếp, Decision Drawer & Snooze.
"""
from typing import Any, Dict, List, Optional, Tuple
import dash
from dash import ALL, Input, Output, State, dcc, html
import plotly.graph_objects as go

from src.dash_app.components.charts import apply_stock_sense_layout, empty_figure
from src.dash_app.components.layout_shell import (
    format_vnd_compact,
    get_brand_badge_class,
    get_short_product_name,
)

M2_KPI_BASE = "kpi-card cursor-pointer bg-white rounded-xl p-4 shadow-2xs select-none transition"
M2_KPI_ACT = f"{M2_KPI_BASE} border-2 border-slate-900"
M2_KPI_IDLE = f"{M2_KPI_BASE} border border-slate-200/90 hover:border-slate-300"

M2_PILL_ACT = "px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-slate-900 text-white transition flex items-center gap-1.5 cursor-pointer whitespace-nowrap"
M2_PILL_IDLE = "px-2.5 py-1 rounded-lg text-[11px] font-medium text-slate-600 hover:bg-slate-100 border border-slate-200/80 transition flex items-center gap-1.5 cursor-pointer whitespace-nowrap"

URGENT_PIE_COLORS = ["#7F1D1D", "#B91C1C", "#DC2626", "#EA580C", "#D97706", "#F59E0B"]


_SHELF_MAP = {
    "Tivi": "Kệ A1",
    "Điều hòa": "Kệ B1",
    "Tủ lạnh": "Sảnh C1",
    "Máy giặt": "Kho Tầng 2",
    "Máy sấy": "Kệ D1",
}


def _load_product_meta_map(alert_svc) -> Tuple[Dict[str, Dict[str, Any]], List[str], List[str]]:
    """Nạp nhanh vị trí kệ, đơn vị tính (uom), ngành hàng, giữ cọc và tốc độ bán từ SQLite."""
    conn = alert_svc._get_connection()
    try:
        rows = conn.execute(
            """
            SELECT
                v.product_code,
                p.uom,
                p.category_path,
                p.brand,
                v.soh,
                v.res,
                v.avl,
                v.inc,
                p.min_stock,
                p.max_stock,
                p.cost_price,
                p.sale_price,
                p.seasonality,
                p.lifecycle_status
            FROM VW_INVENTORY_FLOW_OVERVIEW v
            JOIN DIM_PRODUCTS p ON v.product_code = p.product_code
            WHERE p.has_serial = 1 AND p.is_active = 1;
            """
        ).fetchall()
    finally:
        conn.close()

    meta_map: Dict[str, Dict[str, Any]] = {}
    brands = set()
    categories = set()
    for r in rows:
        d = dict(r)
        parts = [seg.strip() for seg in (d.get("category_path") or "").split(">") if seg.strip()]
        cat_short = parts[-1] if parts else "Điện máy"
        d["category_short"] = cat_short
        d["unit"] = (d.get("uom") or "cái").lower()
        shelf = "Kho chính"
        for k, sh in _SHELF_MAP.items():
            if k.lower() in (d.get("category_path") or "").lower():
                shelf = sh
                break
        d["shelf_location"] = shelf
        meta_map[d["product_code"]] = d
        if d.get("brand"):
            brands.add(d["brand"])
        if cat_short:
            categories.add(cat_short)
    return meta_map, sorted(brands), sorted(categories)


def _format_money_compact_vi(val: Optional[float], role: str) -> str:
    if role == "ROLE_SALES" or val is None:
        return "****** đ"
    return format_vnd_compact(val, role)


def render_m2_workspace(
    services: Dict[str, Any],
    filter_key: str = "all",
    search: str = "",
    brand_filter: str = "ALL",
    category_filter: str = "ALL",
    sort_by: str = "urgent",
    pareto_only: bool = False,
    lead_time_override: Optional[int] = None,
    role: str = "ROLE_OWNER",
) -> Dict[str, Any]:
    """Chuẩn bị KPI thuần Việt, Pie Chart Vốn kẹt 4-thông-tin Hover và Bảng 7 cột chuẩn Ảnh 1 (.cell-hscroll)."""
    alert_svc = services["alert"]
    kpis = alert_svc.get_alert_kpis(role=role)
    df_slow = alert_svc.get_slow_moving_alerts(role=role, include_snoozed=False)
    df_stockout = alert_svc.get_stockout_alerts()
    meta_map, brands_list, categories_list = _load_product_meta_map(alert_svc)

    slow_rows = df_slow.to_dict(orient="records") if not df_slow.empty else []
    stockout_rows_all = df_stockout.to_dict(orient="records") if not df_stockout.empty else []

    # Nối thông tin bổ sung từ DB cho từng dòng
    for r in slow_rows:
        m = meta_map.get(r["product_code"], {})
        r.update(
            {
                "shelf_location": m.get("shelf_location") or "Kho chính",
                "unit": m.get("unit") or "máy",
                "category_short": m.get("category_short") or (r.get("category_path", "").split(" > ")[0] or "Điện máy"),
                "res": int(m.get("res") or 0),
                "avl": int(m.get("avl") or r["soh"]),
                "min_stock": int(m.get("min_stock") or 2),
                "lifecycle_status": m.get("lifecycle_status") or "",
                "seasonality": m.get("seasonality") or "",
            }
        )
    for r in stockout_rows_all:
        m = meta_map.get(r["product_code"], {})
        r.update(
            {
                "shelf_location": m.get("shelf_location") or "Kệ chính",
                "unit": m.get("unit") or "cái",
                "category_short": m.get("category_short") or "Điện máy",
                "soh": int(m.get("soh") or max(0, r["avl"])),
                "res": int(m.get("res") or 0),
                "max_stock": int(m.get("max_stock") or 10),
                "cost_price": float(m.get("cost_price") or 0.0),
                "sale_price": float(m.get("sale_price") or 0.0),
            }
        )

    urgent_stockout_rows = [r for r in stockout_rows_all if int(r.get("inc", 0)) == 0]
    incoming_rows = [r for r in stockout_rows_all if int(r.get("inc", 0)) > 0]

    counts = {
        "all": len(slow_rows) + len(stockout_rows_all),
        "stagnant": len(slow_rows),
        "dead": sum(1 for r in slow_rows if r["risk_group"] in ("Tồn chết / Vượt trần", "Hãng EOL")),
        "seasonal": sum(1 for r in slow_rows if r["risk_group"] == "Sắp hết mùa"),
        "stockout": len(urgent_stockout_rows),
        "incoming": len(incoming_rows),
    }

    dead_cap = (
        sum(float(r.get("stagnant_capital", 0)) for r in slow_rows if r["risk_group"] in ("Tồn chết / Vượt trần", "Hãng EOL"))
        if role != "ROLE_SALES"
        else None
    )
    seasonal_cap = (
        sum(float(r.get("stagnant_capital", 0)) for r in slow_rows if r["risk_group"] == "Sắp hết mùa")
        if role != "ROLE_SALES"
        else None
    )
    total_slow_capital = sum(float(r.get("stagnant_capital", 0)) for r in slow_rows) if role != "ROLE_SALES" else 0.0

    # Tính Pareto 80/20 trên 2 mã đầu bán chậm
    top2_slow = sorted(slow_rows, key=lambda x: float(x.get("stagnant_capital") or 0), reverse=True)[:2]
    top2_codes = {r["product_code"] for r in top2_slow}
    top2_cap = sum(float(r.get("stagnant_capital") or 0) for r in top2_slow)
    top2_pct = round((top2_cap / total_slow_capital) * 100, 1) if total_slow_capital > 0 else 0.0
    top2_brands = " & ".join(dict.fromkeys(r["brand"] for r in top2_slow)) if top2_slow else "Top 2"

    # 4 Thẻ KPI chuẩn thuần Việt
    kpi_cards = [
        html.Div(
            id="m2-kpi-stagnant",
            n_clicks=0,
            className=M2_KPI_ACT if filter_key == "stagnant" else M2_KPI_IDLE,
            children=[
                html.Div(
                    [
                        html.Span(
                            [html.Span(className="w-2 h-2 rounded-full bg-amber-500"), "TỔNG VỐN KẸT CẦN XẢ"],
                            className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500",
                        ),
                        html.Span(
                            f"{counts['stagnant']} mặt hàng",
                            className="px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-50 text-amber-800 border border-amber-200/60",
                        ),
                    ],
                    className="flex items-center justify-between gap-2 mb-2 whitespace-nowrap",
                ),
                html.Div(
                    [
                        html.Span(
                            format_vnd_compact(kpis["stagnant_capital"], role),
                            className="text-2xl font-bold tracking-tight text-slate-900 tabular-nums cost-val font-mono",
                        ),
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
                        html.Span(
                            [html.Span(className="w-2 h-2 rounded-full bg-slate-700"), "TỒN CHẾT & VƯỢT TRẦN"],
                            className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500",
                        ),
                        html.Span(
                            "Tồn > 60 ngày",
                            className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-700 border border-slate-200",
                        ),
                    ],
                    className="flex items-center justify-between gap-2 mb-2 whitespace-nowrap",
                ),
                html.Div(
                    [
                        html.Span(
                            format_vnd_compact(dead_cap, role),
                            className="text-2xl font-bold tracking-tight text-slate-900 tabular-nums cost-val font-mono",
                        ),
                        html.Span(f"{counts['dead']} mặt hàng", className="text-xs font-medium text-slate-400"),
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
                        html.Span(
                            [html.Span(className="w-2 h-2 rounded-full bg-amber-500"), "TRÁI MÙA & SẮP HẾT MÙA"],
                            className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500",
                        ),
                        html.Span(
                            "Đẩy trước vụ",
                            className="px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-50 text-amber-800 border border-amber-200/60",
                        ),
                    ],
                    className="flex items-center justify-between gap-2 mb-2 whitespace-nowrap",
                ),
                html.Div(
                    [
                        html.Span(
                            format_vnd_compact(seasonal_cap, role),
                            className="text-2xl font-bold tracking-tight text-amber-600 tabular-nums cost-val font-mono",
                        ),
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
                        html.Span(
                            [html.Span(className="w-2 h-2 rounded-full bg-rose-600"), "SẮP CHÁY KHO"],
                            className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500",
                        ),
                        html.Span(
                            f"{kpis['stockout_risk_skus']} mã chưa đặt nhập",
                            className="px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200/60",
                        ),
                    ],
                    className="flex items-center justify-between gap-2 mb-2 whitespace-nowrap",
                ),
                html.Div(
                    [
                        html.Span(
                            f"-{format_vnd_compact(kpis['daily_lost_revenue'], 'ROLE_OWNER')}/ngày",
                            className="text-2xl font-bold tracking-tight text-rose-600 tabular-nums font-mono",
                        ),
                        html.Span(f"+{kpis['in_transit_skus']} xe đang về", className="text-xs font-medium text-blue-600"),
                    ],
                    className="flex items-baseline gap-2 mb-2.5 whitespace-nowrap",
                ),
                html.Div(
                    [html.Span("Đã trừ hàng sắp về kho"), html.Span("Nhập bù gấp →", className="font-semibold text-rose-600")],
                    className="flex items-center justify-between text-xs pt-2 border-t border-slate-100 whitespace-nowrap text-slate-500",
                ),
            ],
        ),
    ]

    # Hợp nhất danh sách để lọc theo Pills, Hãng, Ngành, Search, Pareto & Sắp xếp
    kw = (search or "").strip().lower()
    lt_default = int(lead_time_override or 4)
    merged_records: List[Dict[str, Any]] = []

    def _matches_common(item: Dict[str, Any]) -> bool:
        if brand_filter and brand_filter != "ALL" and item.get("brand") != brand_filter:
            return False
        if category_filter and category_filter != "ALL" and item.get("category_short") != category_filter:
            return False
        if kw and kw not in item["product_code"].lower() and kw not in item["product_name"].lower():
            return False
        return True

    if filter_key in ("all", "stagnant", "dead", "seasonal") and not (pareto_only and filter_key not in ("all", "stagnant", "dead")):
        for r in slow_rows:
            if filter_key == "dead" and r["risk_group"] not in ("Tồn chết / Vượt trần", "Hãng EOL"):
                continue
            if filter_key == "seasonal" and r["risk_group"] != "Sắp hết mùa":
                continue
            if pareto_only and r["product_code"] not in top2_codes:
                continue
            if not _matches_common(r):
                continue

            cap_val = float(r.get("stagnant_capital") or 0)
            cap_share = round((cap_val / total_slow_capital) * 100, 1) if total_slow_capital > 0 else 0.0
            soh = int(r["soh"])
            max_stk = max(1, int(r["max_stock"]))
            ratio_ceil = round(soh / max_stk, 1)
            days_idle = int(r["days_since_last_sale"])
            dsi_days = float(r["dsi_days"])

            # Nhãn & hành động thuần Việt chuẩn Ảnh 1
            if r["risk_group"] == "Hãng EOL":
                runway_left = f"❄ {days_idle} ngày 0 đơn"
                runway_right = "Đóng băng"
                bar_cls = "frozen-striped-bar h-full w-full"
                cause_badge = html.Div(
                    [
                        html.Span("• Tồn chết lâu nhất", className="px-2 py-0.5 rounded bg-slate-100 text-slate-800 border border-slate-200 font-semibold text-[11px]"),
                        html.Span("Hãng ngừng SX", className="px-1.5 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200 font-semibold text-[10px]"),
                    ],
                    className="inline-flex items-center gap-1.5 whitespace-nowrap",
                )
                cause_desc = f"Model ngừng SX · Cất khuất {r['shelf_location']}"
                cta_label = "Xả Thu Vốn →"
                urgency_rank = 3
            elif r["risk_group"] == "Sắp hết mùa":
                runway_left = f"Chậm {days_idle} ngày"
                runway_right = "Cầu giảm mùa vụ"
                bar_cls = "bg-amber-500 h-full w-4/5"
                cause_badge = html.Span(f"• Hết mùa hè · Vượt {ratio_ceil:.1f}x trần", className="px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200 font-semibold text-[11px] whitespace-nowrap")
                cause_desc = f"Ôm hàng qua mùa · Kệ {r['shelf_location']}"
                cta_label = "Xả Mùa Vụ →"
                urgency_rank = 2
            else:
                runway_left = f"❄ {days_idle} ngày 0 đơn" if days_idle >= 30 else f"Chậm {days_idle} ngày"
                runway_right = f"Đóng băng (~{int(min(dsi_days, 180))} ngày)"
                bar_cls = "frozen-striped-bar h-full w-full" if days_idle >= 30 else "bg-amber-500 h-full w-2/3"
                cause_badge = html.Span(f"• Chôn {cap_share:.1f}% vốn kẹt", className="px-2 py-0.5 rounded bg-slate-100 text-slate-800 border border-slate-200 font-semibold text-[11px] whitespace-nowrap")
                cause_desc = "Tồn lâu chiếm chỗ kệ & nguy cơ trôi bảo hành"
                cta_label = "Xả Combo →" if r["brand"] == "LG" else "Xả Trả Góp 0% →"
                urgency_rank = 1

            merged_records.append(
                {
                    "kind": "slow",
                    "urgency_rank": urgency_rank,
                    "capital_val": cap_val,
                    "dos_val": float(r["dsi_days"]),
                    "row_data": r,
                    "ratio_badge": (f"{ratio_ceil:.1f}x trần" if ratio_ceil > 1 else "Bán chậm"),
                    "ratio_badge_cls": "bg-amber-50 text-amber-800 border-amber-200",
                    "stock_subline": f"Bán ngay: {r['avl']} · Giữ cọc: {r['res']} {r['unit']}",
                    "runway_left": runway_left,
                    "runway_right": runway_right,
                    "bar_cls": bar_cls,
                    "risk_top": _format_money_compact_vi(cap_val, role),
                    "risk_top_cls": "text-slate-900 cost-val",
                    "risk_sub": f"Giá vốn: {_format_money_compact_vi(r.get('cost_price'), role)}/{r['unit']}",
                    "cause_badge": cause_badge,
                    "cause_desc": cause_desc,
                    "cta_label": cta_label,
                    "cta_cls": "px-2.5 py-1.5 rounded-lg bg-amber-50 text-amber-800 border border-amber-300 hover:bg-amber-100 font-semibold cursor-pointer whitespace-nowrap",
                    "hot_badge": False,
                }
            )

    if filter_key in ("all", "stockout", "incoming") and not pareto_only:
        for r in stockout_rows_all:
            inc = int(r.get("inc") or 0)
            if filter_key == "stockout" and inc > 0:
                continue
            if filter_key == "incoming" and inc == 0:
                continue
            if not _matches_common(r):
                continue

            avl = int(r["avl"])
            min_stk = int(r["min_stock"])
            lt = max(lt_default, int(r["lead_time_days"]))
            dos = float(r["dos_days"])
            lost_daily = float(r["daily_lost_revenue"])
            po_qty = int(r["po_draft_qty"])

            if inc > 0:
                ratio_badge = f"+{inc} đang về"
                ratio_badge_cls = "bg-blue-50 text-blue-700 border-blue-200"
                stock_subline = r.get("po_info") or f"Có thể bán: {avl} · Đang giao về +{inc}"
                runway_left = "Xe về sau ít ngày"
                runway_right = "Đã khóa giá nhập"
                bar_cls = "bg-blue-600 h-full w-3/4"
                risk_top = _format_money_compact_vi(r["soh"] * r["cost_price"], role) if role != "ROLE_SALES" else "****** đ"
                risk_top_cls = "text-slate-900 cost-val"
                risk_sub = f"Giá vốn: {_format_money_compact_vi(r['cost_price'], role)}/{r['unit']}"
                cause_badge = html.Span("• Đã có xe hàng đang giao", className="px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 font-semibold text-[11px] whitespace-nowrap")
                cause_desc = f"Chuẩn bị chỗ tại {r['shelf_location']} nhận {inc} {r['unit']}"
                cta_label = "Xem chuyến xe →"
                cta_cls = "px-2.5 py-1.5 rounded-lg bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 font-semibold cursor-pointer whitespace-nowrap"
                urgency_rank = 4
            elif avl <= 0:
                ratio_badge = "Đứt kho"
                ratio_badge_cls = "bg-rose-50 text-rose-700 border-rose-200"
                stock_subline = f"Có thể bán: {avl} · Cầu {r['rr_7']:.1f} {r['unit']}/ngày"
                runway_left = "Cạn kho (0 ngày)"
                runway_right = f"Giao: {lt} ngày"
                bar_cls = "bg-rose-600 h-full w-1/12"
                risk_top = f"Mất ~{format_vnd_compact(lost_daily, 'ROLE_OWNER')}/ngày"
                risk_top_cls = "text-rose-600"
                risk_sub = f"Giá vốn: {_format_money_compact_vi(r['cost_price'], role)} · Hết hàng"
                cause_badge = html.Span("• Cấp 1 · Hết sạch hàng", className="px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200 font-semibold text-[11px] whitespace-nowrap")
                cause_desc = f"Cầu {r['rr_7']:.1f} {r['unit']}/ngày · Chưa đặt đơn nhập"
                cta_label = f"⚡ Nhập gấp +{po_qty} {r['unit']}"
                cta_cls = "px-2.5 py-1.5 rounded-lg bg-rose-50 text-rose-700 border border-rose-300 hover:bg-rose-100 font-semibold cursor-pointer whitespace-nowrap"
                urgency_rank = 0
            else:
                ratio_badge = "Dưới tối thiểu"
                ratio_badge_cls = "bg-rose-50 text-rose-700 border-rose-200"
                stock_subline = f"Có thể bán: {avl} · Cầu {r['rr_7']:.1f} {r['unit']}/ngày"
                runway_left = f"Đủ bán {dos:.1f} ngày"
                runway_right = f"Giao: {lt} ngày"
                pct_w = max(10, min(90, int((dos / max(1, lt)) * 45)))
                bar_cls = "bg-rose-600 h-full" if dos <= lt else "bg-amber-500 h-full"
                risk_top = f"Mất ~{format_vnd_compact(lost_daily, 'ROLE_OWNER')}/ngày"
                risk_top_cls = "text-rose-600"
                risk_sub = f"Giá vốn: {_format_money_compact_vi(r['cost_price'], role)}/{r['unit']}"
                lvl = "Cấp 2 · Đứt hàng trước khi xe về" if dos <= lt else "Cấp 3 · Cần lên kế hoạch nhập"
                cause_badge = html.Span(f"• {lvl}", className="px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200 font-semibold text-[11px] whitespace-nowrap")
                gap_days = max(0.5, round(lt - dos, 1)) if dos <= lt else 0
                cause_desc = f"Thiếu {gap_days:.1f} ngày bán · Chưa đặt nhập" if gap_days > 0 else "Sắp chạm ngưỡng thời gian hãng giao"
                cta_label = f"⚡ Nhập bù +{po_qty} {r['unit']}"
                cta_cls = "px-2.5 py-1.5 rounded-lg bg-rose-50 text-rose-700 border border-rose-200 hover:bg-rose-100 font-semibold cursor-pointer whitespace-nowrap"
                urgency_rank = 1 if dos <= lt else 2

            merged_records.append(
                {
                    "kind": "stockout",
                    "urgency_rank": urgency_rank,
                    "capital_val": float(lost_daily),
                    "dos_val": dos,
                    "row_data": r,
                    "ratio_badge": ratio_badge,
                    "ratio_badge_cls": ratio_badge_cls,
                    "stock_subline": stock_subline,
                    "runway_left": runway_left,
                    "runway_right": runway_right,
                    "bar_cls": bar_cls,
                    "risk_top": risk_top,
                    "risk_top_cls": risk_top_cls,
                    "risk_sub": risk_sub,
                    "cause_badge": cause_badge,
                    "cause_desc": cause_desc,
                    "cta_label": cta_label,
                    "cta_cls": cta_cls,
                    "hot_badge": inc == 0,
                    "bar_pct": pct_w if inc == 0 and avl > 0 else None,
                }
            )

    if sort_by == "capital":
        merged_records.sort(key=lambda x: (-x["capital_val"], x["urgency_rank"]))
    elif sort_by == "runway":
        merged_records.sort(key=lambda x: (x["dos_val"], x["urgency_rank"]))
    else:
        merged_records.sort(key=lambda x: (x["urgency_rank"], -x["capital_val"]))

    table_rows: List[html.Tr] = []
    for rec in merged_records:
        r = rec["row_data"]
        row_kind = rec["kind"]
        code = r["product_code"]
        brand = r.get("brand") or ""
        brand_cls = get_brand_badge_class(brand)
        norm_val = r["max_stock"] if row_kind == "slow" else r["min_stock"]
        soh_display = r["soh"] if row_kind == "slow" else max(0, r["avl"])

        bar_style = {"width": f"{rec['bar_pct']}%"} if rec.get("bar_pct") is not None else {}

        sub_children: List[Any] = [
            html.Span(code, className="font-code font-semibold text-slate-600"),
            html.Span(" · "),
            html.Span(r.get("category_short") or "Điện máy"),
            html.Span(" · "),
            html.Span(r.get("shelf_location") or "Kho chính"),
        ]
        if brand:
            sub_children.append(html.Span(brand, className=f"ml-1.5 px-1.5 py-0.2 rounded text-[10px] font-semibold border {brand_cls}"))
        if rec["hot_badge"]:
            sub_children.append(html.Span("BÁN CHẠY", className="ml-1 px-1.5 py-0.2 rounded text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200"))

        action_btn_id = (
            {"type": "m2-goto-m3", "sku": code, "kind": row_kind}
            if row_kind == "slow"
            else {"type": "m2-goto-m4", "sku": code, "kind": row_kind}
        )

        table_rows.append(
            html.Tr(
                className="hover:bg-slate-50/90 transition-colors",
                children=[
                    # Cột 1: Checkbox trực quan
                    html.Td(
                        html.Span("", className="inline-block w-3.5 h-3.5 rounded border border-slate-300 bg-white align-middle"),
                        className="py-3 pl-3.5 pr-1.5 text-center align-middle",
                    ),
                    # Cột 2: Sản phẩm & Vị trí kệ (.cell-hscroll)
                    html.Td(
                        html.Div(
                            [
                                html.Button(
                                    r["product_name"],
                                    id={"type": "m2-open-drawer", "sku": code, "kind": row_kind},
                                    n_clicks=0,
                                    className="font-semibold text-slate-900 hover:text-blue-700 text-left cursor-pointer",
                                ),
                                html.Div(sub_children, className="text-[11px] text-slate-500 mt-0.5 flex items-center"),
                            ],
                            className="cell-hscroll",
                        ),
                        className="py-3 px-3 max-w-[260px]",
                    ),
                    # Cột 3: Tồn thực / Định mức
                    html.Td(
                        [
                            html.Div(
                                [
                                    html.Span(f"{soh_display} / {norm_val} {r['unit']}", className="font-bold text-slate-900 font-code"),
                                    html.Span(rec["ratio_badge"], className=f"px-1.5 py-0.5 rounded border text-[10px] font-semibold whitespace-nowrap {rec['ratio_badge_cls']}"),
                                ],
                                className="flex items-center gap-1.5 whitespace-nowrap",
                            ),
                            html.Div(rec["stock_subline"], className="text-[11px] text-slate-500 mt-0.5 whitespace-nowrap"),
                        ],
                        className="py-3 px-3",
                    ),
                    # Cột 4: Đường băng & Tốc độ bán (.cell-hscroll)
                    html.Td(
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span(rec["runway_left"], className="font-semibold text-slate-800 mr-3"),
                                        html.Span(rec["runway_right"], className="text-slate-500"),
                                    ],
                                    className="flex items-center justify-between text-[11px] mb-1.5",
                                ),
                                html.Div(
                                    html.Div(className=rec["bar_cls"], style=bar_style),
                                    className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden",
                                ),
                            ],
                            className="cell-hscroll",
                        ),
                        className="py-3 px-3 max-w-[225px]",
                    ),
                    # Cột 5: Vốn đọng / Rủi ro
                    html.Td(
                        [
                            html.Div(rec["risk_top"], className=f"font-bold text-[12px] font-code whitespace-nowrap {rec['risk_top_cls']}"),
                            html.Div(rec["risk_sub"], className="text-[11px] text-slate-400 mt-0.5 cost-val whitespace-nowrap"),
                        ],
                        className="py-3 px-3",
                    ),
                    # Cột 6: Nguyên nhân cốt lõi (.cell-hscroll)
                    html.Td(
                        html.Div(
                            [
                                html.Div(rec["cause_badge"], className="mb-1"),
                                html.Div(rec["cause_desc"], className="text-[11px] text-slate-500"),
                            ],
                            className="cell-hscroll",
                        ),
                        className="py-3 px-3 max-w-[235px]",
                    ),
                    # Cột 7: Hành động quyết định + Nút Tạm hoãn
                    html.Td(
                        html.Div(
                            [
                                html.Button(rec["cta_label"], id=action_btn_id, n_clicks=0, className=rec["cta_cls"]),
                                html.Button(
                                    html.I(className="ph-bold ph-clock text-sm"),
                                    id={"type": "m2-row-snooze", "sku": code, "kind": row_kind},
                                    n_clicks=0,
                                    title="Tạm hoãn cảnh báo",
                                    className="p-1.5 rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-100 hover:text-slate-800 cursor-pointer",
                                ),
                            ],
                            className="flex items-center justify-end gap-1.5",
                        ),
                        className="py-3 px-3 text-right whitespace-nowrap",
                    ),
                ],
            )
        )

    if not table_rows:
        table_rows.append(
            html.Tr(html.Td("Không có cảnh báo phù hợp bộ lọc hiện tại.", colSpan=7, className="py-8 text-center text-slate-400"))
        )

    # Biểu đồ Pie Chart Vốn kẹt dải màu Vàng - Cam - Đỏ - Nâu đỏ + Tooltip 4 thông tin
    if role == "ROLE_SALES":
        cap_fig = empty_figure("🔒 Đã bảo mật biểu đồ Vốn kẹt theo phân quyền Bán hàng", height=270)
    elif not df_slow.empty:
        pie_rows = sorted(slow_rows, key=lambda x: float(x.get("stagnant_capital") or 0), reverse=True)[:6]
        labels = [get_short_product_name(r["product_name"], r["product_code"]) for r in pie_rows]
        values = [float(r["stagnant_capital"]) for r in pie_rows]
        customdata = [
            [
                r["product_name"],
                r["product_code"],
                format_vnd_compact(r["stagnant_capital"], "ROLE_OWNER"),
                f"{r['soh']} {r['unit']}",
            ]
            for r in pie_rows
        ]
        slice_colors = URGENT_PIE_COLORS[: len(pie_rows)]
        cap_fig = go.Figure(
            go.Pie(
                labels=labels,
                values=values,
                customdata=customdata,
                hole=0.22,
                pull=[0.04 if idx == 0 else 0 for idx in range(len(pie_rows))],
                marker=dict(colors=slice_colors, line=dict(color="#FFFFFF", width=2)),
                textinfo="percent+label",
                textposition="inside",
                insidetextfont=dict(color="#FFFFFF", size=11),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Mã sản phẩm: <code>%{customdata[1]}</code><br>"
                    "Vốn đang kẹt: <b>%{customdata[2]}</b> (%{percent})<br>"
                    "Số lượng tồn kho: <b>%{customdata[3]}</b>"
                    "<extra></extra>"
                ),
            )
        )
        cap_fig.update_layout(
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, font=dict(size=11)),
            margin=dict(l=12, r=135, t=12, b=12),
        )
        apply_stock_sense_layout(cap_fig, height=270)
    else:
        cap_fig = empty_figure("Không còn mặt hàng kẹt vốn cần xử lý", height=270)

    pareto_summary = {
        "brands": top2_brands,
        "pct": top2_pct,
        "capital_str": _format_money_compact_vi(top2_cap, role),
        "active": pareto_only,
    }

    pill_classes = {k: (M2_PILL_ACT if k == filter_key else M2_PILL_IDLE) for k in counts}

    return {
        "kpi_cards": kpi_cards,
        "table_rows": table_rows,
        "capital_fig": cap_fig,
        "counts": counts,
        "pill_classes": pill_classes,
        "brands_list": brands_list,
        "categories_list": categories_list,
        "pareto": pareto_summary,
    }


def build_m2_drawer_body(sku: str, services: Dict[str, Any], role: str = "ROLE_OWNER") -> Dict[str, Any]:
    """Lấy chi tiết cảnh báo thuần Việt của 1 mặt hàng cho Slide-over Decision Drawer M2."""
    alert_svc = services["alert"]
    df_slow = alert_svc.get_slow_moving_alerts(role=role, include_snoozed=True)
    df_st = alert_svc.get_stockout_alerts()
    meta_map, _, _ = _load_product_meta_map(alert_svc)
    unit = (meta_map.get(sku) or {}).get("unit") or "máy"

    if not df_slow.empty and sku in df_slow["product_code"].values:
        r = df_slow[df_slow["product_code"] == sku].iloc[0].to_dict()
        cap_txt = format_vnd_compact(r.get("stagnant_capital"), role)
        return {
            "sku": sku,
            "badge": r["risk_badge"],
            "name": r["product_name"],
            "meta": f"{sku} · Tồn thực tế: {r['soh']} {unit} · Chưa bán: {r['days_since_last_sale']} ngày",
            "body": html.Div(
                [
                    html.Div([html.Strong("Vốn đang kẹt: "), html.Span(cap_txt, className="cost-val font-bold text-rose-600")], className="p-3 rounded-lg bg-slate-50 border border-slate-200"),
                    html.Div([html.Strong("Số ngày tồn kho ước tính: "), f"{r['dsi_days']:.0f} ngày (vượt ngưỡng an toàn 60 ngày)."], className="p-3 rounded-lg bg-amber-50 border border-amber-200"),
                    html.Div([html.Strong("Đề xuất hành động: "), f"Chuyển {r['suggested_clearance_qty']} {unit} sang phân hệ Gợi ý xả hàng để chạy kịch bản bán kèm phụ kiện thu hồi vốn nhanh."], className="p-3 rounded-lg bg-blue-50 border border-blue-200"),
                ],
                className="space-y-2.5",
            ),
            "target_module": "m3",
            "cta_label": "Chuyển sang Gợi ý xả hàng →",
        }

    if not df_st.empty and sku in df_st["product_code"].values:
        r = df_st[df_st["product_code"] == sku].iloc[0].to_dict()
        return {
            "sku": sku,
            "badge": r["severity"],
            "name": r["product_name"],
            "meta": f"{sku} · Có thể bán: {r['avl']} · Hàng đang về: {r['inc']} · Thời gian hãng giao: {r['lead_time_days']} ngày",
            "body": html.Div(
                [
                    html.Div([html.Strong("Trạng thái đơn đang về: "), r["po_info"]], className="p-3 rounded-lg bg-blue-50 border border-blue-200"),
                    html.Div([html.Strong("Đề xuất nhập bù: "), f"{r['po_draft_qty']} {unit} (theo tốc độ bán {r['rr_7']} {unit}/ngày)."], className="p-3 rounded-lg bg-amber-50 border border-amber-200"),
                ],
                className="space-y-2.5",
            ),
            "target_module": "m4",
            "cta_label": "Chuyển sang Gợi ý nhập hàng →",
        }

    return {
        "sku": sku,
        "badge": "Bình thường",
        "name": sku,
        "meta": "",
        "body": html.P("Không có cảnh báo đang hoạt động cho mặt hàng này."),
        "target_module": "m1",
        "cta_label": "Quay về Tổng quan kho",
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
        Input("m2-pill-incoming", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_m2_filter_select(*_args):
        trig = dash.ctx.triggered_id or ""
        for k in ("all", "stagnant", "dead", "seasonal", "stockout", "incoming"):
            if trig.endswith(f"-{k}"):
                return k
        return "all"

    @app.callback(
        Output("store-m2-pareto", "data"),
        Input("btn-m2-pareto-filter", "n_clicks"),
        Input("btn-m2-pareto-card", "n_clicks"),
        State("store-m2-pareto", "data"),
        prevent_initial_call=True,
    )
    def on_m2_pareto_toggle(_b1, _b2, current):
        return not bool(current)

    @app.callback(
        Output("m2-kpi-section", "children"),
        Output("m2-alerts-table-body", "children"),
        Output("m2-capital-chart", "figure"),
        Output("m2-pill-all", "className"),
        Output("m2-pill-stagnant", "className"),
        Output("m2-pill-dead", "className"),
        Output("m2-pill-seasonal", "className"),
        Output("m2-pill-stockout", "className"),
        Output("m2-pill-incoming", "className"),
        Output("m2HeaderAlertCountBadge", "children"),
        Output("btn-m2-pareto-filter", "children"),
        Input("store-m2-filter", "data"),
        Input("m2-search-input", "value"),
        Input("m2BrandSelect", "value"),
        Input("m2CategorySelect", "value"),
        Input("m2SortSelect", "value"),
        Input("store-m2-pareto", "data"),
        Input("store-m2-lead-time", "data"),
        Input("store-role", "data"),
        Input("store-refresh-tick", "data"),
        prevent_initial_call=True,
    )
    def on_m2_refresh(filter_key, search, brand_val, cat_val, sort_val, pareto_only, lt_val, role, _tick):
        ws = render_m2_workspace(
            services,
            filter_key=filter_key or "all",
            search=search or "",
            brand_filter=brand_val or "ALL",
            category_filter=cat_val or "ALL",
            sort_by=sort_val or "urgent",
            pareto_only=bool(pareto_only),
            lead_time_override=lt_val,
            role=role or "ROLE_OWNER",
        )
        pc = ws["pill_classes"]
        p = ws["pareto"]
        pareto_txt = "Bỏ lọc Top 2 →" if p["active"] else "Lọc ngay"
        return (
            ws["kpi_cards"],
            ws["table_rows"],
            ws["capital_fig"],
            pc["all"],
            pc["stagnant"],
            pc["dead"],
            pc["seasonal"],
            pc["stockout"],
            pc["incoming"],
            f"{ws['counts']['all']} CẢNH BÁO",
            pareto_txt,
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
        State("store-role", "data"),
        prevent_initial_call=True,
    )
    def on_m2_drawer(_clicks, _close_btn, _backdrop, role):
        trig = dash.ctx.triggered_id
        closed_cls = "fixed top-0 right-0 h-full w-[460px] max-w-full bg-white shadow-2xl border-l border-slate-200 z-50 transform translate-x-full transition-transform duration-200 flex flex-col justify-between"
        open_cls = "fixed top-0 right-0 h-full w-[460px] max-w-full bg-white shadow-2xl border-l border-slate-200 z-50 transform translate-x-0 transition-transform duration-200 flex flex-col justify-between"

        if trig in ("btn-close-m2-drawer", "m2DrawerBackdrop"):
            return closed_cls, {"display": "none"}, None, dash.no_update, *[dash.no_update] * 5

        if isinstance(trig, dict) and trig.get("type") == "m2-open-drawer":
            if not (dash.ctx.triggered and dash.ctx.triggered[0]["value"]):
                return tuple([dash.no_update] * 9)
            sku = trig["sku"]
            info = build_m2_drawer_body(sku, services, role=role or "ROLE_OWNER")
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
        Input({"type": "m2-row-snooze", "sku": ALL, "kind": ALL}, "n_clicks"),
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
    def on_m2_snooze_modal(_open, _row_clicks, _c1, _c2, _confirm, drawer_sku, snooze_sku, days, reason, role, tick):
        trig = dash.ctx.triggered_id
        if trig == "btn-m2-drawer-snooze":
            target_sku = drawer_sku or "TV-LG-55C3"
            return {"display": "flex"}, target_sku, f"Mã sản phẩm: {target_sku}", "", dash.no_update, dash.no_update
        if isinstance(trig, dict) and trig.get("type") == "m2-row-snooze":
            if not (dash.ctx.triggered and dash.ctx.triggered[0]["value"]):
                return tuple([dash.no_update] * 6)
            target_sku = trig["sku"]
            return {"display": "flex"}, target_sku, f"Mã sản phẩm: {target_sku}", "", dash.no_update, dash.no_update
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
        Input({"type": "m2-goto-m3", "sku": ALL, "kind": ALL}, "n_clicks"),
        Input({"type": "m2-goto-m4", "sku": ALL, "kind": ALL}, "n_clicks"),
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
