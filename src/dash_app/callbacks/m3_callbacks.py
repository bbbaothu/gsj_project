"""
Callbacks Module 03 (Parity V2): Khớp 100% Ảnh 2 —
Inline Cashflow Bar trên PA1-PA4 (bỏ m3-tactic-chart), Simulator Presets, Price Ruler,
Radar Giả lập mất mạng (ERR_CLR_003), Sync Giá Gợi ý & Nhận định chiến lược từ Hệ thống.
"""
from typing import Any, Dict, List, Optional
import dash
from dash import ALL, Input, Output, State, html

from src.dash_app.components.layout_shell import (
    format_vnd_compact,
    get_brand_badge_class,
    get_short_product_name,
)


def _format_tr(val: Optional[float], role: str = "ROLE_OWNER", signed: bool = False) -> str:
    if role == "ROLE_SALES" or val is None:
        return "****** đ"
    n = float(val)
    prefix = "+" if (signed and n > 0) else ("-" if n < 0 else "")
    return f"{prefix}{abs(n) / 1e6:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " tr"


def _build_strategic_insight(cand: Dict[str, Any], best_tactic: Dict[str, Any], role: str) -> html.Div:
    """Sinh nhận định chiến lược từ hệ thống theo đặc thù từng ngành hàng và mặt hàng."""
    cat = (cand.get("category_group") or "").lower()
    p_name = get_short_product_name(cand["product_name"], cand["product_code"])
    roi = 0.0
    if role != "ROLE_SALES" and cand.get("cost_price") and best_tactic.get("clearance_price"):
        rev = float(best_tactic["clearance_price"])
        prof = float(best_tactic["unit_profit"])
        roi = round((prof / rev) * 100, 1) if rev > 0 else 0.0
    prof_txt = "biên lãi dương ổn định" if role == "ROLE_SALES" else f"giữ biên lãi {roi:.1f}% (+{format_vnd_compact(best_tactic['total_profit'], role)})"

    if "tivi" in cat:
        insight_body = [
            f"Khách mua {p_name} rất nhạy cảm với chi phí lắp đặt và phụ kiện treo tường. Chọn ",
            html.Strong("Phương án 2 (Bán Combo Giá treo + Công lắp)", className="text-slate-900"),
            f" giúp {prof_txt} mà không làm giảm uy tín giá của cửa hàng.",
        ]
    elif "điều hòa" in cat:
        insight_body = [
            f"{p_name} bước vào cuối mùa nóng, tốc độ cầu tự nhiên giảm mạnh. Ưu tiên ",
            html.Strong("Phương án 2 (Tặng 1,5m ống đồng + Vật tư)", className="text-slate-900"),
            f" để đẩy tồn nhanh trước mùa lạnh mà vẫn {prof_txt}.",
        ]
    elif "tủ lạnh" in cat:
        insight_body = [
            f"{p_name} dung tích lớn đang chiếm diện tích trưng bày sảnh chính. Có thể kết hợp ",
            html.Strong("Phương án 2 hoặc Trả góp 0%", className="text-slate-900"),
            f" để chốt khách gia đình thu hồi vốn nhanh trong khi {prof_txt}.",
        ]
    else:
        insight_body = [
            f"{p_name} là mặt hàng cần giải phóng sớm khỏi kho để nhường chỗ mẫu mới. Chọn ",
            html.Strong("Phương án 2", className="text-slate-900"),
            f" hoặc khớp sát giá thấp nhất khu vực để {prof_txt}.",
        ]

    return html.Div(
        [
            html.Div(
                html.I(className="ph-fill ph-lightbulb text-indigo-600 text-base"),
                className="w-8 h-8 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-center shrink-0",
            ),
            html.Div(
                [
                    html.Div("Nhận định chiến lược từ Hệ thống", className="text-xs font-bold text-slate-900"),
                    html.P(insight_body, className="text-xs text-slate-600 leading-relaxed mt-1"),
                ],
                className="min-w-0",
            ),
        ],
        className="flex items-start gap-3",
    )


def render_m3_workspace(
    services: Dict[str, Any],
    sku: str = "TV-LG-55C3",
    tactic_code: str = "PA2",
    target_qty: int = 10,
    extra_disc: float = 0.0,
    price_override: Optional[float] = None,
    offline_mode: bool = False,
    role: str = "ROLE_OWNER",
) -> Dict[str, Any]:
    """Chuẩn bị toàn bộ trạng thái 4 SKU cards, 4 Kịch bản kèm inline bar, Simulator, Radar & Price Ruler."""
    clr_svc = services["clearance"]
    kpis = clr_svc.get_clearance_kpis(role=role)
    candidates = clr_svc.get_clearance_candidates(role="ROLE_OWNER")[:4]
    cand_skus = [c["product_code"] for c in candidates]
    active_sku = sku if sku in cand_skus else (cand_skus[0] if cand_skus else "TV-LG-55C3")
    active_cand = next((c for c in candidates if c["product_code"] == active_sku), candidates[0])

    # Lấy max_stock & cost_price thực tế cho ruler/header
    conn = clr_svc._get_connection()
    prod_row = conn.execute(
        "SELECT max_stock, map_price, sale_price, cost_price, stock_on_hand FROM DIM_PRODUCTS WHERE product_code = ?;",
        (active_sku,),
    ).fetchone()
    conn.close()
    max_stock = int(prod_row["max_stock"]) if prod_row else max(1, active_cand["soh"] - active_cand["target_qty"])
    map_price = float(prod_row["map_price"] or 0.0) if prod_row else 0.0
    sale_price = float(active_cand["sale_price"])
    cost_price = float(active_cand["cost_price"])

    effective_qty = max(1, min(int(target_qty or active_cand["target_qty"]), active_cand["soh"]))
    keep_qty = max(0, active_cand["soh"] - effective_qty)
    tactics = clr_svc.generate_4_tactics(active_sku, target_qty=effective_qty)
    chosen_tactic = next((t for t in tactics if t["tactic_code"] == tactic_code), tactics[1])

    if price_override is not None:
        eff_price = float(price_override)
        promo_unit = float(chosen_tactic["promo_cost_per_unit"])
        exp_rev = float(eff_price * effective_qty)
        rec_cap = float(cost_price * effective_qty)
        tot_promo = float(promo_unit * effective_qty)
        net_prof = exp_rev - rec_cap - tot_promo
        roi_pct = round((net_prof / rec_cap) * 100, 1) if rec_cap > 0 else 0.0
        sim = {
            "product_code": active_sku,
            "tactic_code": chosen_tactic["tactic_code"],
            "target_qty": effective_qty,
            "effective_unit_price": eff_price,
            "expected_revenue": exp_rev,
            "recovered_capital": None if role == "ROLE_SALES" else rec_cap,
            "total_promo_cost": None if role == "ROLE_SALES" else tot_promo,
            "net_gross_profit": None if role == "ROLE_SALES" else net_prof,
            "roi_pct": None if role == "ROLE_SALES" else roi_pct,
            "is_loss": net_prof < 0,
        }
    else:
        sim = clr_svc.simulate_financials(
            active_sku,
            tactic_code,
            target_qty=effective_qty,
            extra_discount_pct=float(extra_disc or 0.0),
            role=role,
        )

    radar = clr_svc.get_market_price_radar(active_sku, role=role)
    if offline_mode:
        radar["competitors"] = [
            {
                "competitor_name": "Siêu thị Điện máy chuẩn (Tham chiếu nội bộ)",
                "competitor_price": sale_price,
                "promo_note": "Dữ liệu tham chiếu nội bộ gần nhất (Đang mất mạng)",
                "crawled_at": "Offline",
            }
        ]
        radar["online_min_price"] = sale_price
        radar["avg_market_price"] = sale_price

    # 1. 4 Thẻ sản phẩm ứng viên
    sku_cards: List[Any] = []
    for c in candidates:
        is_sel = c["product_code"] == active_sku
        b_cls = get_brand_badge_class(c.get("brand"))
        cls = (
            "p-3 rounded-xl border-2 border-slate-900 bg-indigo-50/30 shadow-sm cursor-pointer transition-all text-left w-full"
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
                            html.Div(
                                [
                                    html.Span(c["category_group"], className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-bold text-[10px]"),
                                    html.Span(c.get("brand") or "", className=f"px-1.5 py-0.5 rounded border font-semibold text-[10px] {b_cls}"),
                                ],
                                className="flex items-center gap-1",
                            ),
                            html.Span(
                                "ĐANG CHỌN" if is_sel else f"Tồn: {c['soh']} máy",
                                className=f"text-[10px] font-bold {'text-indigo-700' if is_sel else 'text-slate-400'}",
                            ),
                        ],
                        className="flex items-center justify-between mb-1.5",
                    ),
                    html.Div(c["product_code"], className="font-code text-[11px] text-slate-500"),
                    html.Div(c["product_name"], className="text-xs font-bold text-slate-900 truncate mt-0.5"),
                    html.Div(
                        [
                            html.Span(f"Đề xuất xả: {c['target_qty']} máy", className="text-rose-600 font-semibold"),
                            html.Span(f"Vốn: {format_vnd_compact(c['cost_price'], role)}", className="text-slate-600 cost-val font-code"),
                        ],
                        className="flex items-center justify-between text-[11px] mt-2 pt-2 border-t border-slate-100",
                    ),
                ],
            )
        )

    # 2. 4 Thẻ Phương án PA1-PA4 tích hợp Thanh so sánh dòng tiền (Bỏ graph riêng)
    is_sales = role == "ROLE_SALES"
    tactic_cards: List[Any] = []
    for t in tactics:
        is_t_sel = t["tactic_code"] == chosen_tactic["tactic_code"]
        border_cls = "border-2 border-slate-900 bg-white shadow-xs" if is_t_sel else "border border-slate-200 bg-white hover:border-slate-300"

        badges: List[Any] = []
        if t["is_recommended"]:
            badges.append(html.Span("★ TỐI ƯU", className="px-2 py-0.5 rounded bg-emerald-600 text-white text-[10px] font-bold tracking-wide"))
        if t["map_violation"]:
            badges.append(html.Span("Dưới giá sàn", className="px-1.5 py-0.5 rounded bg-rose-100 text-rose-700 text-[10px] font-bold"))

        unit_prof = float(t["unit_profit"])
        tot_prof = float(t["total_profit"])
        tot_rev = max(1.0, float(t["total_revenue"]))
        tot_cap = float(cost_price * effective_qty)
        margin_pct = round((tot_prof / tot_rev) * 100, 1)

        if is_sales:
            cap_w = 82.0
            prof_w = 18.0
            unit_prof_str = "******"
            tot_prof_str = "******"
            prof_cls = "text-slate-500"
        else:
            denom = max(tot_rev, tot_cap + max(0.0, tot_prof))
            cap_w = round(min(94.0, (tot_cap / denom) * 100.0), 1)
            prof_w = round(max(4.0, min(100.0 - cap_w, (max(0.0, tot_prof) / denom) * 100.0)), 1)
            unit_prof_str = f"{_format_tr(unit_prof, role, signed=True)}/máy"
            tot_prof_str = f"{_format_tr(tot_prof, role, signed=True)} ({margin_pct:.1f}%)"
            prof_cls = "text-emerald-700" if tot_prof >= 0 else "text-rose-600"

        km_str = "0 đ/máy" if t["promo_cost_per_unit"] == 0 else f"{int(t['promo_cost_per_unit'] / 1000)}k/máy"
        bar_prof_cls = "bg-emerald-500 h-full" if tot_prof >= 0 else "bg-rose-500 h-full"

        radio_dot = html.Span(
            html.Span(className="w-2 h-2 rounded-full bg-slate-900") if is_t_sel else None,
            className=(
                "w-4 h-4 rounded-full border-2 border-slate-900 flex items-center justify-center shrink-0 mt-0.5"
                if is_t_sel
                else "w-4 h-4 rounded-full border-2 border-slate-300 flex items-center justify-center shrink-0 mt-0.5"
            ),
        )

        tactic_cards.append(
            html.Button(
                id={"type": "m3-select-tactic", "code": t["tactic_code"]},
                n_clicks=0,
                className=f"w-full text-left px-3.5 py-2.5 rounded-xl transition-all cursor-pointer flex items-center justify-between gap-3 {border_cls}",
                children=[
                    # Trái: Radio + Tiêu đề + Mô tả
                    html.Div(
                        [
                            radio_dot,
                            html.Div(
                                [
                                    html.Div([html.Span(t["title"], className="text-xs font-bold text-slate-900 mr-1.5"), *badges], className="flex items-center flex-wrap gap-1"),
                                    html.Div(t["note"], className="text-[11px] text-slate-500 mt-0.5 leading-snug"),
                                ],
                                className="min-w-0",
                            ),
                        ],
                        className="flex items-start gap-2.5 flex-1 min-w-0",
                    ),
                    # Giữa-phải: Giá xả + Chi phí KM
                    html.Div(
                        [
                            html.Div(f"Xả: {_format_tr(t['clearance_price'], 'ROLE_OWNER')}", className="font-code text-xs font-bold text-slate-900 whitespace-nowrap"),
                            html.Div(
                                ["KM: ", html.Span(km_str, className="text-rose-600 font-semibold")],
                                className="text-[11px] text-slate-500 mt-0.5 whitespace-nowrap",
                            ),
                        ],
                        className="text-right shrink-0",
                    ),
                    # Phải: Lãi 1 máy + Tổng lãi + Inline Bar Vốn thu hồi vs Lãi gộp ròng
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("Lãi 1 máy:", className="text-[10px] text-slate-500"),
                                    html.Span(unit_prof_str, className=f"text-[11px] font-bold font-code cost-val {prof_cls}"),
                                ],
                                className="flex items-center justify-between gap-2 whitespace-nowrap",
                            ),
                            html.Div(
                                [
                                    html.Span("Tổng lãi:", className="text-[10px] text-slate-500"),
                                    html.Span(tot_prof_str, className=f"text-[11px] font-bold font-code cost-val {prof_cls}"),
                                ],
                                className="flex items-center justify-between gap-2 whitespace-nowrap mb-1",
                            ),
                            html.Div(
                                [
                                    html.Div(className="bg-slate-800 h-full", style={"width": f"{cap_w}%"}),
                                    html.Div(className=bar_prof_cls, style={"width": f"{prof_w}%"}),
                                ],
                                className="w-full h-1.5 rounded-full bg-slate-100 overflow-hidden flex",
                            ),
                        ],
                        className="w-44 sm:w-48 shrink-0 pl-2 border-l border-slate-100",
                    ),
                ],
            )
        )

    # 3. Các dòng Đối thủ Radar + Thang định vị giá & Sàn vốn + Giá gợi ý Hero
    dot_colors = ["bg-blue-600", "bg-rose-600", "bg-amber-500"]
    comp_rows: List[Any] = []
    sug_price = float(radar["suggested_price"])
    for idx, c in enumerate(radar["competitors"]):
        diff = float(c["competitor_price"]) - sug_price
        dot_cls = dot_colors[idx % len(dot_colors)]
        diff_label = f"Cao hơn mình +{format_vnd_compact(diff, 'ROLE_OWNER')}" if diff >= 0 else f"Thấp hơn mình -{format_vnd_compact(abs(diff), 'ROLE_OWNER')}"
        diff_cls = "text-[11px] font-semibold text-emerald-700" if diff >= 0 else "text-[11px] font-semibold text-rose-600"
        comp_rows.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(className=f"w-2 h-2 rounded-full shrink-0 mt-1.5 {dot_cls}"),
                            html.Div(
                                [
                                    html.Div(c["competitor_name"], className="text-xs font-bold text-slate-900"),
                                    html.Div(c["promo_note"] or "Giá niêm yết thị trường", className="text-[11px] text-slate-500"),
                                ]
                            ),
                        ],
                        className="flex items-start gap-2.5",
                    ),
                    html.Div(
                        [
                            html.Div(f"{c['competitor_price']:,.0f} đ", className="font-code text-xs font-bold text-slate-900"),
                            html.Div(diff_label, className=diff_cls),
                        ],
                        className="text-right shrink-0",
                    ),
                ],
                className="p-2.5 rounded-xl bg-slate-50/70 border border-slate-200/80 flex items-center justify-between gap-2",
            )
        )

    online_min = float(radar["online_min_price"])
    top_comp = max([float(c["competitor_price"]) for c in radar["competitors"]] + [sale_price])
    unit_headroom = round(sug_price - cost_price, 0)
    unit_margin_pct = round((unit_headroom / sug_price) * 100, 1) if sug_price > 0 else 0.0
    min_axis = min(cost_price * 0.94, sug_price * 0.95)
    max_axis = max(top_comp, sug_price * 1.05, cost_price + 1)
    sug_marker_pct = round(max(12.0, min(82.0, ((sug_price - min_axis) / (max_axis - min_axis)) * 100.0)), 1)

    ruler_widget = [
        html.Div(
            [
                html.Span("Thang định vị giá & Sàn vốn", className="text-xs font-semibold text-slate-700"),
                html.Span(
                    "Bảo mật theo phân quyền" if is_sales else f"Dư địa lãi: +{_format_tr(unit_headroom, role)}/máy",
                    className="text-xs font-bold text-emerald-700 cost-val font-code",
                ),
            ],
            className="flex items-center justify-between mb-2",
        ),
        html.Div(
            [
                html.Div(className="bg-rose-200 h-full", style={"width": "32%"}),
                html.Div(className="bg-emerald-200 h-full", style={"width": "43%"}),
                html.Div(className="bg-slate-200 h-full", style={"width": "25%"}),
                html.Div(
                    className="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-emerald-600 border-2 border-white shadow",
                    style={"left": f"{sug_marker_pct}%"},
                ),
            ],
            className="relative w-full h-2 rounded-full overflow-hidden flex bg-slate-100 mb-2",
        ),
        html.Div(
            [
                html.Span(f"Sàn vốn: {_format_tr(cost_price, role)}", className="text-[10px] font-bold text-rose-700 cost-val font-code"),
                html.Span(f"Gợi ý: {_format_tr(sug_price, 'ROLE_OWNER')}", className="text-[10px] font-bold text-emerald-700 font-code"),
                html.Span(f"Online: {_format_tr(online_min, 'ROLE_OWNER')}", className="text-[10px] font-medium text-slate-500 font-code"),
                html.Span(f"ĐMX: {_format_tr(top_comp, 'ROLE_OWNER')}", className="text-[10px] font-medium text-slate-500 font-code"),
            ],
            className="grid grid-cols-4 gap-1 text-center whitespace-nowrap",
        ),
    ]

    tail_tag = "Đuôi ..50k" if int(round(sug_price)) % 100_000 == 50_000 else "Đuôi ..90k"
    dmx_diff = max(0.0, top_comp - sug_price)
    online_diff = max(0.0, online_min - sug_price)

    # Simulator metrics
    eff_unit = float(sim["effective_unit_price"])
    disc_pct_vs_ny = round(((sale_price - eff_unit) / sale_price) * 100.0, 1) if sale_price > 0 else 0.0
    cut_loss_5_price = round(cost_price * 0.95, -4)
    floor_price = map_price if map_price > 0 else round(cost_price * 1.08, -4)
    sim_net_prof = sim["net_gross_profit"]
    sim_margin_pct = round((float(sim_net_prof) / float(sim["expected_revenue"])) * 100, 1) if (not is_sales and sim["expected_revenue"] > 0) else 0.0

    best_rec_tactic = next((t for t in tactics if t["is_recommended"]), tactics[0])
    strategic_insight = _build_strategic_insight(active_cand, best_rec_tactic, role)

    tactic_header_sub = f"Lý do xả: Tồn {active_cand['soh']} máy · Mục tiêu giải phóng {effective_qty} máy đưa tồn về trần an toàn ({max_stock} máy)."
    tactic_label_num = chosen_tactic["tactic_code"].replace("PA", "Phương án ")

    return {
        "active_sku": active_sku,
        "active_soh": active_cand["soh"],
        "active_target_qty": effective_qty,
        "sku_cards": sku_cards,
        "tactic_cards": tactic_cards,
        "tactic_header_sub": tactic_header_sub,
        "sim_tactic_badge": tactic_label_num,
        "legend_label": "Vốn thu hồi · Lãi gộp ròng",
        "competitor_rows": comp_rows,
        "price_ruler": ruler_widget,
        "tail_badge": tail_tag,
        "radar_pai_badge": f"🔥 Rẻ hơn {radar['pai_pct']}% · Rẻ nhất Cầu Giấy",
        "radar_dmx_diff": f"Rẻ hơn {format_vnd_compact(dmx_diff, 'ROLE_OWNER')}",
        "radar_online_diff": f"Rẻ hơn {online_diff:,.0f} đ",
        "sync_btn_label": f"🪄 Áp dụng giá {_format_tr(sug_price, 'ROLE_OWNER')} vào mô phỏng",
        "strategic_insight": strategic_insight,
        "kpi_recovery": format_vnd_compact(kpis["expected_recovery_capital"], role),
        "kpi_qty_sub": f"{kpis['total_target_qty']} máy · {kpis['candidate_skus_count']} mã hàng",
        "kpi_profit": format_vnd_compact(kpis["expected_gross_profit"], role),
        "kpi_roi_badge": "Bảo mật" if is_sales else f"Thu hồi vốn +{kpis['roi_pct']}%",
        "kpi_pai_text": f"Rẻ hơn {radar['pai_pct']}%",
        "kpi_active_camp": f"{kpis['active_campaigns_count']} Đang chạy",
        "kpi_pending_camp": f"· {kpis['pending_campaigns_count']} Chờ duyệt",
        "sim_unit_price_str": f"{_format_tr(eff_price if price_override is not None else eff_unit, 'ROLE_OWNER')}/máy",
        "sim_disc_badge": f"Giảm {max(0.0, disc_pct_vs_ny):.1f}%",
        "sim_markers_cutloss": _format_tr(cut_loss_5_price, role),
        "sim_markers_cost": _format_tr(cost_price, role),
        "sim_markers_floor": _format_tr(floor_price, "ROLE_OWNER"),
        "sim_markers_ny": _format_tr(sale_price, "ROLE_OWNER"),
        "sim_qty_ratio": f"{effective_qty} / {active_cand['soh']} máy",
        "sim_qty_clear_lbl": f"Xả: {effective_qty} máy",
        "sim_qty_keep_lbl": f"Giữ lại: {keep_qty} máy",
        "sim_revenue": _format_tr(sim["expected_revenue"], "ROLE_OWNER"),
        "sim_rev_sub": f"{effective_qty} máy × {_format_tr(eff_unit, 'ROLE_OWNER')}",
        "sim_capital": _format_tr(sim["recovered_capital"], role),
        "sim_cap_sub": "Bảo mật" if is_sales else f"{effective_qty} × {_format_tr(cost_price, role)} vốn",
        "sim_promo_cost": _format_tr(sim["total_promo_cost"], role),
        "sim_promo_sub": "0 đ/máy" if is_sales or chosen_tactic["promo_cost_per_unit"] == 0 else f"{int(chosen_tactic['promo_cost_per_unit']/1000)}k/máy",
        "sim_net_profit": "****** đ" if is_sales else _format_tr(sim_net_prof, role, signed=True),
        "sim_profit_sub": "Bảo mật" if is_sales else f"Biên: {sim_margin_pct:.1f}% · Hiệu suất vốn: {sim['roi_pct']:+.1f}%",
        "sim_autostop_label": f"Tự dừng khi xả đủ {effective_qty} máy",
        "effective_price": eff_unit,
        "suggested_price_text": f"{sug_price:,.0f} đ",
        "pai_summary_text": "Lãi ròng: ****** đ" if is_sales else f"Lãi ròng: +{_format_tr(unit_headroom, role)}/máy ({unit_margin_pct:.1f}%)",
        "sales_lock_style": {"display": "flex" if is_sales else "none"},
        "cap_protect_style": {"display": "flex" if (bool(sim["is_loss"]) and not is_sales) else "none"},
        "err003_style": {"display": "flex" if offline_mode else "none"},
        "offline_btn_cls": (
            "px-2.5 py-1 rounded-lg border border-rose-300 bg-rose-50 text-rose-700 text-[11px] font-semibold cursor-pointer"
            if offline_mode
            else "px-2.5 py-1 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 text-[11px] font-medium cursor-pointer"
        ),
        "tag_product_name": active_cand["product_name"],
        "tag_old_price": f"{sale_price:,.0f} đ",
        "tag_new_price": f"{eff_unit:,.0f} đ",
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
    """Đăng ký tập trung các Callbacks cho Module 03 (Parity V2)."""

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
        Output("store-m3-price-override", "data"),
        Input("btn-m3-preset-default", "n_clicks"),
        Input("btn-m3-preset-match-comp", "n_clicks"),
        Input("btn-m3-preset-cut-loss", "n_clicks"),
        Input("m3SyncRadarPriceBtn", "n_clicks"),
        Input("m3-discount-slider", "value"),
        Input("store-m3-sku", "data"),
        Input("store-m3-tactic", "data"),
        State("store-m3-sku", "data"),
        prevent_initial_call=True,
    )
    def on_m3_price_control(_def, _match, _cut, _sync, _slider, _sku_in, _tac_in, active_sku):
        trig = dash.ctx.triggered_id
        sku = active_sku or "TV-LG-55C3"
        if trig in ("btn-m3-preset-default", "store-m3-sku", "store-m3-tactic", "m3-discount-slider"):
            return None
        clr_svc = services["clearance"]
        if trig in ("btn-m3-preset-match-comp", "m3SyncRadarPriceBtn"):
            radar = clr_svc.get_market_price_radar(sku, role="ROLE_OWNER")
            return float(radar["suggested_price"])
        if trig == "btn-m3-preset-cut-loss":
            cands = clr_svc.get_clearance_candidates(role="ROLE_OWNER")
            cand = next((c for c in cands if c["product_code"] == sku), cands[0])
            return float(round(float(cand["cost_price"]) * 0.95, -4))
        return dash.no_update

    @app.callback(
        Output("m3-qty-input", "value"),
        Output("m3-qty-input", "max"),
        Input("btn-m3-qty-dec", "n_clicks"),
        Input("btn-m3-qty-inc", "n_clicks"),
        Input("store-m3-sku", "data"),
        State("m3-qty-input", "value"),
        State("store-m3-sku", "data"),
        prevent_initial_call=True,
    )
    def on_m3_qty_step(_dec, _inc, sku_in, cur_qty, active_sku):
        trig = dash.ctx.triggered_id
        sku = sku_in if trig == "store-m3-sku" else (active_sku or "TV-LG-55C3")
        cands = services["clearance"].get_clearance_candidates(role="ROLE_OWNER")
        cand = next((c for c in cands if c["product_code"] == sku), cands[0])
        max_soh = max(2, int(cand["soh"]))
        if trig == "store-m3-sku":
            return int(cand["target_qty"]), max_soh
        cur = int(cur_qty or cand["target_qty"])
        if trig == "btn-m3-qty-dec":
            return max(1, cur - 1), dash.no_update
        if trig == "btn-m3-qty-inc":
            return min(max_soh, cur + 1), dash.no_update
        return dash.no_update, dash.no_update

    @app.callback(
        Output("store-m3-offline", "data"),
        Input("btn-m3-toggle-offline", "n_clicks"),
        Input("btn-m3-refresh-radar", "n_clicks"),
        State("store-m3-offline", "data"),
        prevent_initial_call=True,
    )
    def on_m3_toggle_offline(_tog, _ref, current_off):
        if dash.ctx.triggered_id == "btn-m3-refresh-radar":
            return False
        return not bool(current_off)

    @app.callback(
        Output("m3SkuSelectorGrid", "children"),
        Output("m3TacticsContainer", "children"),
        Output("m3TacticHeaderSub", "children"),
        Output("m3SimTacticBadge", "children"),
        Output("m3CompetitorListContainer", "children"),
        Output("m3PricePositionRuler", "children"),
        Output("m3StrategicInsightBox", "children"),
        Output("m3Err003Banner", "style"),
        Output("btn-m3-toggle-offline", "className"),
        Output("m3KpiTotalRecovery", "children"),
        Output("m3KpiTotalProfit", "children"),
        Output("m3KpiMarginPill", "children"),
        Output("m3KpiPaiHero", "children"),
        Output("m3KpiActiveCampaigns", "children"),
        Output("m3KpiPendingCampaigns", "children"),
        Output("m3SelectedSkuHeaderBadge", "children"),
        Output("m3SimUnitPriceDisplay", "children"),
        Output("m3SimDiscountBadge", "children"),
        Output("m3SimMarkerCutLoss", "children"),
        Output("m3SimMarkerCost", "children"),
        Output("m3SimMarkerFloor", "children"),
        Output("m3SimMarkerNy", "children"),
        Output("m3SimQtyRatioBadge", "children"),
        Output("m3SimQtyClearLabel", "children"),
        Output("m3SimQtyKeepLabel", "children"),
        Output("m3SimBoxRevenue", "children"),
        Output("m3SimBoxRevSub", "children"),
        Output("m3SimBoxCapital", "children"),
        Output("m3SimBoxCapSub", "children"),
        Output("m3SimBoxPromoCost", "children"),
        Output("m3SimBoxPromoSub", "children"),
        Output("m3SimBoxNetProfit", "children"),
        Output("m3SimBoxProfitSub", "children"),
        Output("m3SuggestedTailBadge", "children"),
        Output("m3SuggestedPriceHero", "children"),
        Output("m3RadarPaiBadge", "children"),
        Output("m3SuggestedUnitProfitText", "children"),
        Output("m3RadarDmxDiff", "children"),
        Output("m3RadarOnlineDiff", "children"),
        Output("m3SyncRadarPriceBtn", "children"),
        Output("m3AutoStopLabel", "children"),
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
        Input("store-m3-price-override", "data"),
        Input("store-m3-offline", "data"),
        Input("store-role", "data"),
        Input("store-refresh-tick", "data"),
        prevent_initial_call=True,
    )
    def on_m3_refresh(sku, tactic, disc, qty, price_ovr, off_mode, role, _tick):
        ws = render_m3_workspace(
            services,
            sku=sku or "TV-LG-55C3",
            tactic_code=tactic or "PA2",
            target_qty=int(qty or 10),
            extra_disc=float(disc or 0.0),
            price_override=price_ovr,
            offline_mode=bool(off_mode),
            role=role or "ROLE_OWNER",
        )
        return (
            ws["sku_cards"],
            ws["tactic_cards"],
            ws["tactic_header_sub"],
            ws["sim_tactic_badge"],
            ws["competitor_rows"],
            ws["price_ruler"],
            ws["strategic_insight"],
            ws["err003_style"],
            ws["offline_btn_cls"],
            ws["kpi_recovery"],
            ws["kpi_profit"],
            ws["kpi_roi_badge"],
            ws["kpi_pai_text"],
            ws["kpi_active_camp"],
            ws["kpi_pending_camp"],
            ws["active_sku"],
            ws["sim_unit_price_str"],
            ws["sim_disc_badge"],
            ws["sim_markers_cutloss"],
            ws["sim_markers_cost"],
            ws["sim_markers_floor"],
            ws["sim_markers_ny"],
            ws["sim_qty_ratio"],
            ws["sim_qty_clear_lbl"],
            ws["sim_qty_keep_lbl"],
            ws["sim_revenue"],
            ws["sim_rev_sub"],
            ws["sim_capital"],
            ws["sim_cap_sub"],
            ws["sim_promo_cost"],
            ws["sim_promo_sub"],
            ws["sim_net_profit"],
            ws["sim_profit_sub"],
            ws["tail_badge"],
            ws["suggested_price_text"],
            ws["radar_pai_badge"],
            ws["pai_summary_text"],
            ws["radar_dmx_diff"],
            ws["radar_online_diff"],
            ws["sync_btn_label"],
            ws["sim_autostop_label"],
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
        Input("btn-m3-open-price-tag", "n_clicks"),
        Input("btn-close-m3-tag-modal", "n_clicks"),
        Input("btn-cancel-m3-tag-modal", "n_clicks"),
        Input("btn-confirm-m3-print-tag", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_m3_tag_modal(*_args):
        if dash.ctx.triggered_id in ("btn-m3-open-tag-modal", "btn-m3-open-price-tag"):
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
                    html.Div([html.Span(r["product_code"], className="font-code font-bold mr-2"), html.Span(r["tactic_code"], className="px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 font-semibold")]),
                    html.Div([html.Span(f"SL: {r['target_qty']} · Giá: {r['clearance_price']:,.0f} đ · "), html.Strong(r["status"], className="text-emerald-700")]),
                ],
                className="p-2.5 rounded-lg border border-slate-200 flex items-center justify-between",
            )
            for r in rows
        ]
        return {"display": "flex"}, cards
