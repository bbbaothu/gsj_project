"""
Callbacks Module 04 (Parity V2): Dự báo nhập hàng 14/30 ngày, Cân đối ngân sách, Chỉnh SL +/-, Drawer Hãng & Xuất CSV.
"""
from typing import Any, Dict, List, Optional
import dash
from dash import ALL, Input, Output, State, dcc, html, no_update

from src.dash_app.components.layout_shell import (
    format_vnd_compact,
    format_vnd_full,
    get_brand_badge_class,
)

BRAND_COLORS = ["#0F172A", "#059669", "#F59E0B", "#2563EB", "#6366F1", "#EC4899"]


def compute_m4_items_state(
    replenish_svc: Any,
    cycle_days: int = 14,
    budget_cap: float = 250_000_000.0,
    brand_filter: str = "ALL",
    show_adequate: bool = False,
    search_text: str = "",
    qty_overrides: Optional[Dict[str, int]] = None,
    auto_balance: bool = False,
    role: str = "ROLE_OWNER",
) -> Dict[str, Any]:
    """Tính toán toàn bộ danh sách đề xuất nhập, áp dụng override +/- và cân đối ngân sách."""
    raw = replenish_svc.get_replenishment_recommendations(
        cycle_days=int(cycle_days or 14),
        budget_cap=float(budget_cap or 250_000_000.0),
        vendor_filter="Tất cả",
        role="ROLE_OWNER",
    )
    overrides = qty_overrides or {}
    items: List[Dict[str, Any]] = []
    for it in raw["items"]:
        cloned = dict(it)
        code = cloned["product_code"]
        if code in overrides:
            cloned["suggested_qty"] = max(0, int(overrides[code]))
            cloned["line_total"] = round(cloned["suggested_qty"] * float(cloned["cost_price"] or 0.0), 0)
        items.append(cloned)

    if auto_balance:
        items = replenish_svc.optimize_within_budget(items, float(budget_cap or 250_000_000.0))

    total_units = sum(i["suggested_qty"] for i in items)
    total_cost = sum(float(i["suggested_qty"]) * float(i["cost_price"] or 0.0) for i in items)
    skus_need = sum(1 for i in items if i["suggested_qty"] > 0)
    groups = replenish_svc.preview_po_grouping(items)

    # Filter view items for table
    q_search = (search_text or "").strip().lower()
    visible_items: List[Dict[str, Any]] = []
    for it in items:
        if not show_adequate and it["suggested_qty"] <= 0:
            continue
        if brand_filter and brand_filter != "ALL" and it["brand"] != brand_filter:
            continue
        if q_search and q_search not in it["product_code"].lower() and q_search not in it["product_name"].lower():
            continue
        visible_items.append(it)

    if role == "ROLE_SALES":
        for it in items:
            it["cost_price"] = None
            it["line_total"] = None

    return {
        "cycle_days": int(cycle_days or 14),
        "budget_cap": float(budget_cap or 250_000_000.0),
        "items": items,
        "visible_items": visible_items,
        "groups": groups,
        "skus_need": skus_need,
        "total_units": total_units,
        "total_cost": round(total_cost, 0),
        "over_budget": total_cost > float(budget_cap or 250_000_000.0),
        "avg_confidence": raw.get("avg_confidence_score", 92.0),
    }


def _load_recent_pos(replenish_svc: Any) -> List[Dict[str, Any]]:
    """Đọc các đơn PO gần nhất từ bảng PURCHASE_ORDERS."""
    conn = replenish_svc._get_connection()
    try:
        rows = conn.execute(
            """
            SELECT purchase_code, order_time, vendor_code, vendor_name, total_amount, expected_delivery_date, status
            FROM PURCHASE_ORDERS
            ORDER BY order_time DESC, purchase_code DESC
            LIMIT 10;
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def render_m4_workspace(
    services_or_svc: Any,
    cycle_days: int = 14,
    budget_cap: float = 250_000_000.0,
    brand_filter: str = "ALL",
    show_adequate: bool = False,
    search_text: str = "",
    qty_overrides: Optional[Dict[str, int]] = None,
    auto_balance: bool = False,
    role: str = "ROLE_OWNER",
) -> Dict[str, Any]:
    """Dựng toàn bộ bảng, KPIs, Cards PO theo hãng, biểu đồ & modal preview cho Module 04."""
    replenish_svc = services_or_svc["replenishment"] if isinstance(services_or_svc, dict) else services_or_svc
    state = compute_m4_items_state(
        replenish_svc,
        cycle_days=cycle_days,
        budget_cap=budget_cap,
        brand_filter=brand_filter,
        show_adequate=show_adequate,
        search_text=search_text,
        qty_overrides=qty_overrides,
        auto_balance=auto_balance,
        role=role,
    )
    groups = state["groups"]
    total_cost = state["total_cost"]
    cap = state["budget_cap"]
    pct = round((total_cost / cap) * 100.0, 1) if cap > 0 else 0.0
    remain = cap - total_cost
    freeship_count = sum(1 for g in groups if g["total_amount"] >= 10_000_000)

    # Brand filter pills
    brand_counts: Dict[str, int] = {}
    for it in state["items"]:
        if it["suggested_qty"] > 0 or show_adequate:
            brand_counts[it["brand"]] = brand_counts.get(it["brand"], 0) + 1
    pills: List[Any] = [
        html.Span("Nhà phân phối:", className="text-xs font-semibold text-slate-400 mr-1"),
        html.Button(
            [html.Span("Tất cả "), html.Span(str(sum(brand_counts.values())), className="px-1.5 py-0.2 rounded bg-white/20 text-[11px]")],
            id={"type": "m4-brand-pill", "brand": "ALL"},
            n_clicks=0,
            className=(
                "px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 text-white transition flex items-center gap-1.5 cursor-pointer"
                if brand_filter == "ALL"
                else "px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:bg-slate-100 border border-slate-200/80 transition flex items-center gap-1.5 cursor-pointer"
            ),
        ),
    ]
    for idx, (b_name, b_cnt) in enumerate(sorted(brand_counts.items())):
        is_sel = brand_filter == b_name
        dot_color = BRAND_COLORS[idx % len(BRAND_COLORS)]
        pills.append(
            html.Button(
                [
                    html.Span(className="w-2 h-2 rounded-full", style={"backgroundColor": dot_color}),
                    html.Span(f" {b_name} "),
                    html.Span(f"({b_cnt})", className="text-slate-400 text-[11px]"),
                ],
                id={"type": "m4-brand-pill", "brand": b_name},
                n_clicks=0,
                className=(
                    "px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 text-white transition flex items-center gap-1.5 cursor-pointer"
                    if is_sel
                    else "px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:bg-slate-100 border border-slate-200/80 transition flex items-center gap-1.5 cursor-pointer"
                ),
            )
        )

    # Replenishment Table Rows
    table_rows: List[Any] = []
    for it in state["visible_items"]:
        code = it["product_code"]
        avl = int(it["avl"])
        inc = int(it["inc"])
        demand_total = max(1.0, float(it["forecast_demand"]) + float(it["safety_stock"]))
        avl_pos = max(0, avl)
        # Lượng hàng đang về ròng còn lại sau khi bù đơn đã giữ cọc nếu avl < 0
        inc_effective = max(0, avl + inc - avl_pos)
        gap = max(0.0, demand_total - (avl + inc))
        bar_denom = max(1.0, float(avl_pos + inc_effective) + gap, demand_total)
        pct_avl = min(100.0, round((avl_pos / bar_denom) * 100.0, 1))
        pct_inc = min(100.0 - pct_avl, round((inc_effective / bar_denom) * 100.0, 1))
        pct_gap = max(0.0, round(100.0 - pct_avl - pct_inc, 1)) if gap > 0 else 0.0

        brand_cls = get_brand_badge_class(it.get("brand"))
        unit_price_txt = "****** đ" if role == "ROLE_SALES" else format_vnd_full(it["cost_price"], role)
        line_total_txt = "****** đ" if role == "ROLE_SALES" else format_vnd_compact(it["line_total"] or 0, role)

        table_rows.append(
            html.Tr(
                className="hover:bg-slate-50/80 transition-colors",
                children=[
                    html.Td(
                        className="pl-4 pr-2 py-3 align-top",
                        children=[
                            html.Div(
                                [
                                    html.Span(it["product_name"], className="font-semibold text-slate-900 leading-snug"),
                                    html.Span(it["brand"], className=f"px-1.5 py-0.5 rounded border text-[10px] font-bold {brand_cls}"),
                                ],
                                className="flex flex-wrap items-center gap-1.5",
                            ),
                            html.Div(
                                [
                                    html.Span(code, className="font-code font-semibold text-slate-500"),
                                    html.Span(f" · Đặt tối thiểu {it['moq']} · Quy cách {it['pack_size']} · Độ tin cậy {it['confidence_score']:.0f}%"),
                                ],
                                className="text-[11px] text-slate-400 mt-0.5",
                            ),
                        ],
                    ),
                    html.Td(
                        className="px-2.5 py-3 align-top tabular-nums",
                        children=[
                            html.Div(
                                [
                                    html.Span(f"Có thể bán: {avl}", className=f"font-bold font-code {'text-rose-600' if avl <= 2 else 'text-slate-800'}"),
                                    html.Span(f" · Đang về: +{inc}", className="text-blue-600 font-semibold font-code"),
                                ],
                                className="text-xs",
                            ),
                            html.Div(f"Định mức an toàn: {it['safety_stock']} chiếc", className="text-[11px] text-slate-400 mt-0.5"),
                        ],
                    ),
                    html.Td(
                        className="px-2.5 py-3 align-top",
                        children=[
                            html.Div(
                                [
                                    html.Span(f"Nhu cầu {state['cycle_days']} ngày: {it['forecast_demand']:.1f}", className="font-medium text-slate-700"),
                                    html.Span(f"Thiếu {gap:.0f}" if gap > 0 else "Đủ tồn", className=f"font-bold {'text-rose-600' if gap > 0 else 'text-emerald-600'}"),
                                ],
                                className="flex items-center justify-between text-[11px] mb-1 tabular-nums",
                            ),
                            html.Div(
                                [
                                    html.Div(style={"width": f"{pct_avl}%"}, className="h-full bg-emerald-500"),
                                    html.Div(style={"width": f"{pct_inc}%"}, className="h-full bg-blue-600"),
                                    html.Div(style={"width": f"{pct_gap}%"}, className="h-full gap-pattern"),
                                ],
                                className="w-full h-2 bg-slate-100 rounded-full overflow-hidden flex",
                            ),
                        ],
                    ),
                    html.Td(
                        className="px-2.5 py-3 align-top text-center",
                        children=[
                            html.Div(
                                [
                                    html.Button("−", id={"type": "m4-qty-minus", "sku": code}, n_clicks=0, className="w-7 h-7 rounded-md border border-slate-300 bg-white hover:bg-slate-100 font-bold text-slate-700 cursor-pointer"),
                                    html.Span(str(it["suggested_qty"]), className="w-9 text-center font-code font-bold text-sm text-slate-900 tabular-nums"),
                                    html.Button("+", id={"type": "m4-qty-plus", "sku": code}, n_clicks=0, className="w-7 h-7 rounded-md border border-slate-300 bg-white hover:bg-slate-100 font-bold text-slate-700 cursor-pointer"),
                                ],
                                className="inline-flex items-center justify-center gap-1",
                            ),
                            html.Div(it["status_label"], className="text-[10px] text-slate-400 mt-1"),
                        ],
                    ),
                    html.Td(
                        className="pl-2.5 pr-4 py-3 align-top text-right tabular-nums",
                        children=[
                            html.Div(line_total_txt, className="font-code font-bold text-slate-900 cost-val"),
                            html.Div(f"{unit_price_txt}/máy", className="text-[11px] text-slate-400 mt-0.5 cost-val"),
                        ],
                    ),
                ],
            )
        )

    if not table_rows:
        table_rows = [
            html.Tr(
                html.Td(
                    "Không có mặt hàng cần nhập theo bộ lọc hiện tại. Thử bật 'Hiện cả mã đã đủ tồn'.",
                    colSpan=5,
                    className="py-8 text-center text-xs text-slate-400",
                )
            )
        ]

    # Supplier Cards (Gom đơn theo Hãng)
    supplier_cards: List[Any] = []
    stacked_bars: List[Any] = []
    for idx, g in enumerate(groups):
        amt = g["total_amount"]
        share_pct = round(amt / max(1.0, total_cost) * 100.0, 1) if total_cost > 0 else 0.0
        color = BRAND_COLORS[idx % len(BRAND_COLORS)]
        stacked_bars.append(html.Div(style={"width": f"{share_pct}%", "backgroundColor": color}, className="h-full"))
        freeship = amt >= 10_000_000
        amt_txt = "****** đ" if role == "ROLE_SALES" else format_vnd_compact(amt, role)
        supplier_cards.append(
            html.Div(
                className="p-3 rounded-xl border border-slate-200 bg-white hover:border-blue-300 hover:shadow-xs transition",
                children=[
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(className="w-2.5 h-2.5 rounded-full inline-block mr-1.5", style={"backgroundColor": color}),
                                    html.Strong(g["brand"], className="text-xs font-bold text-slate-900"),
                                ],
                                className="flex items-center",
                            ),
                            html.Span(
                                "✓ Freeship" if freeship else "Cần ghép thêm",
                                className=f"px-2 py-0.5 rounded text-[10px] font-bold {'bg-emerald-50 text-emerald-700 border border-emerald-200' if freeship else 'bg-amber-50 text-amber-700 border border-amber-200'}",
                            ),
                        ],
                        className="flex items-center justify-between gap-2",
                    ),
                    html.Div(g["vendor_name"], className="text-[11px] text-slate-500 truncate mt-0.5"),
                    html.Div(
                        [
                            html.Span(f"{len(g['items'])} mặt hàng · {g['total_units']} thiết bị", className="text-[11px] font-medium text-slate-600"),
                            html.Span(amt_txt, className="font-code font-bold text-xs text-slate-900 cost-val"),
                        ],
                        className="flex items-center justify-between mt-2 pt-2 border-t border-slate-100",
                    ),
                    html.Button(
                        "Xem chi tiết phiếu Hãng →",
                        id={"type": "m4-open-vendor-drawer", "vendor": g["brand"]},
                        n_clicks=0,
                        className="mt-2 w-full py-1.5 rounded-lg text-[11px] font-semibold bg-slate-50 hover:bg-blue-50 text-blue-700 border border-slate-200 cursor-pointer",
                    ),
                ],
            )
        )

    if not supplier_cards:
        supplier_cards = [
            html.Div("Chưa có mặt hàng nào có số lượng > 0 để gom đơn nhập.", className="p-4 text-center text-xs text-slate-400 border border-dashed border-slate-200 rounded-xl")
        ]

    # Approve Modal body
    approve_body: List[Any] = []
    for idx, g in enumerate(groups, start=1):
        amt_txt = "****** đ" if role == "ROLE_SALES" else format_vnd_full(g["total_amount"], role)
        skus_txt = ", ".join(f"{x['product_code']} ({x['quantity']} chiếc)" for x in g["items"])
        approve_body.append(
            html.Div(
                className="p-3 border border-slate-200 rounded-xl bg-slate-50 flex justify-between items-center gap-3",
                children=[
                    html.Div(
                        [
                            html.Strong(f"{idx}. Đơn nhập {g['brand'].upper()} · {g['vendor_name']}", className="text-slate-900"),
                            html.Div(skus_txt, className="text-slate-500 mt-0.5 font-code text-[11px]"),
                        ]
                    ),
                    html.Span(amt_txt, className="font-code font-bold text-slate-900 cost-val shrink-0"),
                ],
            )
        )
    approve_body.append(
        html.Div(
            className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl flex justify-between items-center font-bold text-emerald-900",
            children=[
                html.Span(f"TỔNG DỰ TOÁN ({len(groups)} đơn nhập · Đạt Freeship {freeship_count}/{len(groups)} hãng)"),
                html.Span("****** đ" if role == "ROLE_SALES" else format_vnd_full(total_cost, role), className="font-code text-sm cost-val"),
            ],
        )
    )

    # Recent PO strip & lifecycle list
    recent_pos = _load_recent_pos(replenish_svc)
    po_strip_cards = []
    po_lifecycle_rows = []
    for p in recent_pos[:2]:
        po_amt = "****** đ" if role == "ROLE_SALES" else format_vnd_compact(p["total_amount"], role)
        po_strip_cards.append(
            html.Div(
                className="p-2.5 rounded-lg bg-white border border-slate-200 flex items-center justify-between gap-2 text-xs",
                children=[
                    html.Div(
                        [
                            html.Div(f"{p['purchase_code']} · {p['vendor_name']}", className="font-bold text-slate-800 truncate"),
                            html.Div(f"ETA: {p['expected_delivery_date'] or 'Đang cập nhật'}", className="text-[11px] text-slate-400"),
                        ],
                        className="min-w-0",
                    ),
                    html.Div(
                        [
                            html.Div(po_amt, className="font-mono font-bold text-slate-900 cost-val"),
                            html.Span(p["status"] or "Đang vận chuyển", className="px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 text-[10px] font-semibold"),
                        ],
                        className="text-right shrink-0",
                    ),
                ],
            )
        )
    for p in recent_pos:
        po_amt = "****** đ" if role == "ROLE_SALES" else format_vnd_full(p["total_amount"], role)
        po_lifecycle_rows.append(
            html.Div(
                className="p-3 rounded-xl border border-slate-200 bg-slate-50/70 flex items-center justify-between gap-3",
                children=[
                    html.Div(
                        [
                            html.Strong(f"{p['purchase_code']} · {p['vendor_name']}", className="text-slate-900"),
                            html.Div(f"Ngày đặt: {p['order_time']} · Dự kiến về: {p['expected_delivery_date'] or 'N/A'}", className="text-slate-500 mt-0.5"),
                        ]
                    ),
                    html.Div(
                        [
                            html.Div(po_amt, className="font-mono font-bold text-slate-900 cost-val"),
                            html.Span(p["status"] or "Đang vận chuyển", className="inline-block mt-1 px-2 py-0.5 rounded bg-blue-100 text-blue-800 text-[10px] font-bold"),
                        ],
                        className="text-right shrink-0",
                    ),
                ],
            )
        )

    # Strings for KPIs
    budget_text_short = "****** đ" if role == "ROLE_SALES" else format_vnd_compact(cap, role)
    total_cost_txt = "****** đ" if role == "ROLE_SALES" else format_vnd_compact(total_cost, role)
    cap_label_txt = "/ Trần ******" if role == "ROLE_SALES" else f"/ Trần {format_vnd_compact(cap, role)}"
    pct_txt = "Ẩn theo quyền" if role == "ROLE_SALES" else f"{pct:.1f}% ngân sách"
    remain_txt = (
        "****** đ"
        if role == "ROLE_SALES"
        else (f"Còn dư: +{format_vnd_compact(remain, role)}" if remain >= 0 else f"Vượt trần: {format_vnd_compact(abs(remain), role)}")
    )
    savings_txt = "****** đ" if role == "ROLE_SALES" else f"+{format_vnd_compact(total_cost * 0.015, role)}"
    approve_btn_label = (
        f"Chỉ Quản lý được duyệt {len(groups)} Đơn"
        if role == "ROLE_SALES"
        else f"Duyệt & Xuất {len(groups)} Đơn Nhập ({format_vnd_compact(total_cost, role)})"
    )

    return {
        "state": state,
        "header_order_badge": f"{len(groups)} ĐƠN NHẬP ĐỀ XUẤT",
        "header_budget_text": budget_text_short,
        "issued_po_count": str(len(recent_pos)),
        "kpi_sku_count": f"{state['skus_need']} mã trọng yếu",
        "kpi_brand_span": f"trên {len(groups)} hãng",
        "kpi_cycle_note": f"Thiếu hàng trong {state['cycle_days']} ngày tới nếu chưa đặt",
        "kpi_toggle_adequate_text": "Ẩn mã đã đủ tồn" if show_adequate else "+ Hiện mã đã đủ tồn",
        "kpi_total_units": f"{state['total_units']} thiết bị",
        "kpi_order_count_text": f"{len(groups)} đơn đặt nhập",
        "kpi_budget_badge": pct_txt,
        "kpi_total_cost": total_cost_txt,
        "kpi_cap_label": cap_label_txt,
        "kpi_budget_bar_style": {"width": f"{min(100.0, pct if role != 'ROLE_SALES' else 0):.1f}%"},
        "kpi_budget_bar_cls": (
            "h-full bg-rose-500 rounded-full transition-all duration-200"
            if state["over_budget"] and role != "ROLE_SALES"
            else "h-full bg-emerald-500 rounded-full transition-all duration-200"
        ),
        "kpi_budget_remain": remain_txt,
        "kpi_freeship_badge": f"{freeship_count}/{len(groups)} đơn Freeship" if groups else "0 đơn",
        "kpi_savings_val": savings_txt,
        "kpi_conf_val": f"{state['avg_confidence']:.1f}%",
        "brand_pills": pills,
        "table_rows": table_rows,
        "supplier_cards": supplier_cards,
        "stacked_bars": stacked_bars,
        "right_summary_badge": "Vượt trần!" if (state["over_budget"] and role != "ROLE_SALES") else "Trong trần ngân sách",
        "right_allocation_text": "****** đ" if role == "ROLE_SALES" else f"{format_vnd_compact(total_cost, role)} / {format_vnd_compact(cap, role)} ({pct:.1f}%)",
        "shipping_benefit_title": f"Đạt Miễn phí vận chuyển cho {freeship_count}/{len(groups)} đơn (>10 tr/đơn)",
        "shipping_benefit_sub": f"Ước tính chiết khấu thanh toán sớm 1,5%: {savings_txt}",
        "approve_btn_text": approve_btn_label,
        "approve_disabled": role == "ROLE_SALES" or len(groups) == 0,
        "recent_po_strip": po_strip_cards,
        "po_lifecycle_list": po_lifecycle_rows,
        "approve_modal_body": approve_body,
    }


def generate_m4_po_csv(replenish_svc: Any, items: List[Dict[str, Any]]) -> bytes:
    """Xuất CSV bảng gom nhóm PO theo nhà phân phối."""
    clean_items = [dict(i) for i in items]
    # Bảo đảm cost_price có số hợp lệ khi tạo CSV nội bộ
    if any(i.get("cost_price") is None for i in clean_items):
        ref = {x["product_code"]: x for x in replenish_svc.get_replenishment_recommendations(role="ROLE_OWNER")["items"]}
        for i in clean_items:
            if i.get("cost_price") is None and i["product_code"] in ref:
                i["cost_price"] = ref[i["product_code"]]["cost_price"]
    groups = replenish_svc.preview_po_grouping(clean_items)
    return replenish_svc.export_po_groups_csv(groups)


def submit_m4_purchase_orders(
    replenish_svc: Any,
    items: List[Dict[str, Any]],
    role: str = "ROLE_OWNER",
) -> Dict[str, Any]:
    """Ghi đơn PO vào SQLite thông qua ReplenishmentService (kiểm tra RBAC)."""
    return replenish_svc.create_grouped_purchase_orders(items, role=role)


def register_m4_callbacks(app: Any, services: Dict[str, Any]) -> None:
    """Đăng ký toàn bộ callbacks tương tác cho Module 04."""
    replenish_svc = services["replenishment"]

    @app.callback(
        Output("m4BudgetDropdown", "className"),
        Input("m4BudgetToggleBtn", "n_clicks"),
        Input("m4Budget150Btn", "n_clicks"),
        Input("m4Budget200Btn", "n_clicks"),
        Input("m4Budget250Btn", "n_clicks"),
        Input("m4Budget350Btn", "n_clicks"),
        Input("m4ApplyCustomBudgetBtn", "n_clicks"),
        State("m4BudgetDropdown", "className"),
        prevent_initial_call=True,
    )
    def toggle_budget_dropdown(t1, b1, b2, b3, b4, b_apply, current_cls):
        ctx = dash.callback_context
        tid = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else ""
        base = "absolute left-0 top-full mt-1.5 w-60 bg-white rounded-xl shadow-xl border border-slate-200 p-2.5 z-30"
        if tid == "m4BudgetToggleBtn":
            is_hidden = "hidden" in (current_cls or "hidden")
            return base if is_hidden else f"hidden {base}"
        return f"hidden {base}"

    @app.callback(
        Output("store-m4-cycle", "data"),
        Output("m4Cycle14Btn", "className"),
        Output("m4Cycle30Btn", "className"),
        Input("m4Cycle14Btn", "n_clicks"),
        Input("m4Cycle30Btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def switch_cycle(n14, n30):
        ctx = dash.callback_context
        tid = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else ""
        active = "px-2.5 py-1 rounded-md font-semibold bg-white text-slate-900 shadow-sm transition cursor-pointer"
        idle = "px-2.5 py-1 rounded-md font-medium text-slate-600 hover:text-slate-900 transition cursor-pointer"
        if tid == "m4Cycle30Btn":
            return 30, idle, active
        return 14, active, idle

    @app.callback(
        Output("store-m4-budget", "data"),
        Input("m4Budget150Btn", "n_clicks"),
        Input("m4Budget200Btn", "n_clicks"),
        Input("m4Budget250Btn", "n_clicks"),
        Input("m4Budget350Btn", "n_clicks"),
        Input("m4ApplyCustomBudgetBtn", "n_clicks"),
        State("m4CustomBudgetInput", "value"),
        prevent_initial_call=True,
    )
    def update_budget_cap(b150, b200, b250, b350, b_apply, custom_val):
        ctx = dash.callback_context
        tid = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else ""
        mapping = {
            "m4Budget150Btn": 150_000_000.0,
            "m4Budget200Btn": 200_000_000.0,
            "m4Budget250Btn": 250_000_000.0,
            "m4Budget350Btn": 350_000_000.0,
        }
        if tid in mapping:
            return mapping[tid]
        try:
            mil = max(50.0, min(1000.0, float(custom_val or 250)))
            return mil * 1_000_000.0
        except Exception:
            return 250_000_000.0

    @app.callback(
        Output("store-m4-brand", "data"),
        Input({"type": "m4-brand-pill", "brand": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def select_brand_pill(n_clicks):
        ctx = dash.callback_context
        if not ctx.triggered or not any(n_clicks):
            return no_update
        tid = ctx.triggered_id
        return tid["brand"] if isinstance(tid, dict) else "ALL"

    @app.callback(
        Output("store-m4-show-adequate", "data"),
        Input("m4ToggleAdequateBtn", "n_clicks"),
        Input("m4KpiCard1Btn", "n_clicks"),
        State("store-m4-show-adequate", "data"),
        prevent_initial_call=True,
    )
    def toggle_show_adequate(n1, n2, cur):
        return not bool(cur)

    @app.callback(
        Output("store-m4-qty-overrides", "data"),
        Output("store-m4-autobalance", "data"),
        Input({"type": "m4-qty-minus", "sku": ALL}, "n_clicks"),
        Input({"type": "m4-qty-plus", "sku": ALL}, "n_clicks"),
        Input("m4ResetQtyBtn", "n_clicks"),
        Input("m4FooterResetBtn", "n_clicks"),
        Input("m4AutoBalanceBtn", "n_clicks"),
        State("store-m4-cycle", "data"),
        State("store-m4-budget", "data"),
        State("store-m4-qty-overrides", "data"),
        prevent_initial_call=True,
    )
    def update_qty_or_balance(m_clicks, p_clicks, r1, r2, auto_btn, cycle, budget, overrides):
        ctx = dash.callback_context
        if not ctx.triggered:
            return no_update, no_update
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if prop_id in ("m4ResetQtyBtn", "m4FooterResetBtn"):
            return {}, False
        if prop_id == "m4AutoBalanceBtn":
            return {}, True
        tid = ctx.triggered_id
        if isinstance(tid, dict) and tid.get("type") in ("m4-qty-minus", "m4-qty-plus"):
            # Guard against initial dynamic mount trigger with n_clicks=0
            if not any(m_clicks or []) and not any(p_clicks or []):
                return no_update, no_update
            sku = tid["sku"]
            state = compute_m4_items_state(
                replenish_svc,
                cycle_days=cycle or 14,
                budget_cap=budget or 250_000_000.0,
                qty_overrides=overrides,
                role="ROLE_OWNER",
            )
            cur_item = next((x for x in state["items"] if x["product_code"] == sku), None)
            if not cur_item:
                return no_update, no_update
            step = max(1, int(cur_item.get("pack_size", 1)))
            cur_qty = int(cur_item["suggested_qty"])
            new_qty = max(0, cur_qty - step) if tid["type"] == "m4-qty-minus" else cur_qty + step
            next_overrides = dict(overrides or {})
            next_overrides[sku] = new_qty
            return next_overrides, False
        return no_update, no_update

    @app.callback(
        Output("m4HeaderOrderBadge", "children"),
        Output("m4HeaderBudgetText", "children"),
        Output("m4IssuedPoCountBadge", "children"),
        Output("m4KpiSkuCount", "children"),
        Output("m4KpiBrandSpan", "children"),
        Output("m4KpiCycleNote", "children"),
        Output("m4KpiToggleAquaText", "children"),
        Output("m4KpiTotalUnits", "children"),
        Output("m4KpiOrderCountText", "children"),
        Output("m4KpiBudgetBadge", "children"),
        Output("m4KpiTotalCost", "children"),
        Output("m4KpiCapLabel", "children"),
        Output("m4KpiBudgetBar", "style"),
        Output("m4KpiBudgetBar", "className"),
        Output("m4KpiBudgetRemain", "children"),
        Output("m4KpiFreeshipBadge", "children"),
        Output("m4KpiSavingsVal", "children"),
        Output("m4KpiConfVal", "children"),
        Output("m4BrandFilterContainer", "children"),
        Output("m4ReplenishTableBody", "children"),
        Output("m4SupplierCardsContainer", "children"),
        Output("m4SupplierStackedBar", "children"),
        Output("m4RightSummaryBadge", "children"),
        Output("m4RightAllocationText", "children"),
        Output("m4ShippingBenefitTitle", "children"),
        Output("m4ShippingBenefitSub", "children"),
        Output("m4ApproveBtnText", "children"),
        Output("m4RecentPoStrip", "children"),
        Output("m4PoLifecycleList", "children"),
        Output("m4ApproveModalBody", "children"),
        Input("store-m4-cycle", "data"),
        Input("store-m4-budget", "data"),
        Input("store-m4-brand", "data"),
        Input("store-m4-show-adequate", "data"),
        Input("m4SearchInput", "value"),
        Input("store-m4-qty-overrides", "data"),
        Input("store-m4-autobalance", "data"),
        Input("store-m4-po-refresh", "data"),
        Input("store-role", "data"),
    )
    def sync_m4_workspace(cycle, budget, brand, show_adq, search_txt, overrides, auto_bal, _po_ref, role):
        res = render_m4_workspace(
            replenish_svc,
            cycle_days=cycle or 14,
            budget_cap=budget or 250_000_000.0,
            brand_filter=brand or "ALL",
            show_adequate=bool(show_adq),
            search_text=search_txt or "",
            qty_overrides=overrides,
            auto_balance=bool(auto_bal),
            role=role or "ROLE_OWNER",
        )
        return (
            res["header_order_badge"],
            res["header_budget_text"],
            res["issued_po_count"],
            res["kpi_sku_count"],
            res["kpi_brand_span"],
            res["kpi_cycle_note"],
            res["kpi_toggle_adequate_text"],
            res["kpi_total_units"],
            res["kpi_order_count_text"],
            res["kpi_budget_badge"],
            res["kpi_total_cost"],
            res["kpi_cap_label"],
            res["kpi_budget_bar_style"],
            res["kpi_budget_bar_cls"],
            res["kpi_budget_remain"],
            res["kpi_freeship_badge"],
            res["kpi_savings_val"],
            res["kpi_conf_val"],
            res["brand_pills"],
            res["table_rows"],
            res["supplier_cards"],
            res["stacked_bars"],
            res["right_summary_badge"],
            res["right_allocation_text"],
            res["shipping_benefit_title"],
            res["shipping_benefit_sub"],
            res["approve_btn_text"],
            res["recent_po_strip"],
            res["po_lifecycle_list"],
            res["approve_modal_body"],
        )

    @app.callback(
        Output("m4DrawerBackdrop", "className"),
        Output("m4SupplierDrawer", "className"),
        Output("m4DrawerSupplierTitle", "children"),
        Output("m4DrawerSupplierMeta", "children"),
        Output("m4DrawerSupplierBody", "children"),
        Input({"type": "m4-open-vendor-drawer", "vendor": ALL}, "n_clicks"),
        Input("m4CloseDrawerBtn", "n_clicks"),
        Input("m4CloseDrawerFooterBtn", "n_clicks"),
        Input("m4DrawerApproveSingleBtn", "n_clicks"),
        State("store-m4-cycle", "data"),
        State("store-m4-budget", "data"),
        State("store-m4-qty-overrides", "data"),
        State("store-m4-autobalance", "data"),
        State("store-role", "data"),
        prevent_initial_call=True,
    )
    def toggle_supplier_drawer(open_clicks, c1, c2, go_approve, cycle, budget, overrides, auto_bal, role):
        ctx = dash.callback_context
        base_drawer = "fixed top-0 right-0 h-full w-[480px] max-w-full bg-white shadow-2xl border-l border-slate-200 z-50 transform transition-transform duration-200 flex flex-col justify-between"
        closed = ("fixed inset-0 bg-slate-900/30 backdrop-blur-[1px] z-40 hidden", f"{base_drawer} translate-x-full", "", "", [])
        if not ctx.triggered:
            return closed
        tid = ctx.triggered_id
        if isinstance(tid, dict) and tid.get("type") == "m4-open-vendor-drawer" and any(open_clicks or []):
            vendor = tid["vendor"]
            state = compute_m4_items_state(
                replenish_svc,
                cycle_days=cycle or 14,
                budget_cap=budget or 250_000_000.0,
                qty_overrides=overrides,
                auto_balance=bool(auto_bal),
                role="ROLE_OWNER",
            )
            grp = next((g for g in state["groups"] if g["brand"] == vendor), None)
            if not grp:
                return closed
            body = [
                html.Div(
                    [
                        html.Div(f"{line['product_name']} ({line['product_code']})", className="font-semibold text-slate-900"),
                        html.Div(
                            f"Số lượng: {line['quantity']} chiếc · Thành tiền: {'****** đ' if role == 'ROLE_SALES' else format_vnd_full(line['line_total'], role)}",
                            className="text-slate-600 mt-0.5 cost-val",
                        ),
                    ],
                    className="p-3 rounded-lg border border-slate-200 bg-slate-50",
                )
                for line in grp["items"]
            ]
            meta = f"{grp['vendor_code']} · {grp['total_units']} thiết bị · Tổng {'****** đ' if role == 'ROLE_SALES' else format_vnd_full(grp['total_amount'], role)}"
            return (
                "fixed inset-0 bg-slate-900/30 backdrop-blur-[1px] z-40",
                f"{base_drawer} translate-x-0",
                grp["vendor_name"],
                meta,
                body,
            )
        return closed

    @app.callback(
        Output("m4ApproveModal", "className"),
        Input("m4ApproveAllOrdersBtn", "n_clicks"),
        Input("m4DrawerApproveSingleBtn", "n_clicks"),
        Input("m4CloseApproveModalBtn", "n_clicks"),
        Input("m4CancelApproveModalBtn", "n_clicks"),
        Input("m4ConfirmApproveBtn", "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_approve_modal(o1, o2, c1, c2, c3):
        ctx = dash.callback_context
        tid = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else ""
        if tid in ("m4ApproveAllOrdersBtn", "m4DrawerApproveSingleBtn"):
            return "fixed inset-0 bg-slate-900/40 z-50 flex items-center justify-center p-4"
        return "fixed inset-0 bg-slate-900/40 z-50 hidden items-center justify-center p-4"

    @app.callback(
        Output("m4PoLifecycleModal", "className"),
        Input("m4OpenPoLifecycleBtn", "n_clicks"),
        Input("m4ManageAllPoBtn", "n_clicks"),
        Input("m4CloseLifecycleModalBtn", "n_clicks"),
        Input("m4CloseLifecycleFooterBtn", "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_lifecycle_modal(o1, o2, c1, c2):
        ctx = dash.callback_context
        tid = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else ""
        if tid in ("m4OpenPoLifecycleBtn", "m4ManageAllPoBtn"):
            return "fixed inset-0 bg-slate-900/40 z-50 flex items-center justify-center p-4"
        return "fixed inset-0 bg-slate-900/40 z-50 hidden items-center justify-center p-4"

    @app.callback(
        Output("store-m4-po-refresh", "data"),
        Output("store-toast", "data", allow_duplicate=True),
        Input("m4ConfirmApproveBtn", "n_clicks"),
        State("store-m4-cycle", "data"),
        State("store-m4-budget", "data"),
        State("store-m4-qty-overrides", "data"),
        State("store-m4-autobalance", "data"),
        State("store-role", "data"),
        State("store-m4-po-refresh", "data"),
        prevent_initial_call=True,
    )
    def approve_and_create_po(n_clicks, cycle, budget, overrides, auto_bal, role, cur_ref):
        if not n_clicks:
            return no_update, no_update
        state = compute_m4_items_state(
            replenish_svc,
            cycle_days=cycle or 14,
            budget_cap=budget or 250_000_000.0,
            qty_overrides=overrides,
            auto_balance=bool(auto_bal),
            role="ROLE_OWNER",
        )
        res = submit_m4_purchase_orders(replenish_svc, state["items"], role=role or "ROLE_OWNER")
        if res.get("success"):
            return (cur_ref or 0) + 1, {"open": True, "message": res["message"], "kind": "success"}
        return no_update, {"open": True, "message": res.get("error", "Không thể phát hành đơn PO"), "kind": "error"}

    @app.callback(
        Output("m4-download-csv", "data"),
        Input("m4QuickCsvBtn", "n_clicks"),
        Input("m4DrawerExportCsvBtn", "n_clicks"),
        Input("m4ApproveExportCsvBtn", "n_clicks"),
        Input("m4LifecycleExportCsvBtn", "n_clicks"),
        State("store-m4-cycle", "data"),
        State("store-m4-budget", "data"),
        State("store-m4-qty-overrides", "data"),
        State("store-m4-autobalance", "data"),
        prevent_initial_call=True,
    )
    def download_m4_csv(b1, b2, b3, b4, cycle, budget, overrides, auto_bal):
        state = compute_m4_items_state(
            replenish_svc,
            cycle_days=cycle or 14,
            budget_cap=budget or 250_000_000.0,
            qty_overrides=overrides,
            auto_balance=bool(auto_bal),
            role="ROLE_OWNER",
        )
        csv_bytes = generate_m4_po_csv(replenish_svc, state["items"])
        return dcc.send_bytes(csv_bytes, "stock_sense_po_grouped.csv")
