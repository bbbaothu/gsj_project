"""
Callbacks Module 01: Tổng quan kho, Lọc nâng cao, Scatter Tên ngắn & Quản lý Đơn giữ chỗ.
"""
from typing import Any, Dict, List, Optional
import dash
from dash import ALL, Input, Output, State, html
import plotly.graph_objects as go

from src.dash_app.components.charts import apply_stock_sense_layout, empty_figure
from src.dash_app.components.layout_shell import (
    format_vnd_compact,
    format_vnd_full,
    get_brand_badge_class,
    get_short_product_name,
)

KPI_BASE = "kpi-card cursor-pointer bg-white rounded-2xl p-4 xl:p-5 shadow-xs flex flex-col justify-between relative group"
KPI_ACTIVE_BORDER = f"{KPI_BASE} border-2 border-slate-900"
KPI_IDLE_BORDER = f"{KPI_BASE} border border-slate-200/90 hover:border-slate-300"

PILL_ACTIVE = (
    "filter-pill px-2.5 xl:px-3 py-1.5 rounded-lg text-xs font-semibold transition-all "
    "bg-slate-900 text-white flex items-center gap-1.5 cursor-pointer shadow-xs whitespace-nowrap"
)
PILL_IDLE = (
    "filter-pill px-2.5 xl:px-3 py-1.5 rounded-lg text-xs font-medium transition-all "
    "bg-slate-100/80 hover:bg-slate-200/70 text-slate-700 flex items-center gap-1.5 cursor-pointer whitespace-nowrap"
)

ORDER_TAB_ACTIVE = "px-3 py-1.5 rounded-lg font-semibold bg-white text-slate-900 shadow-2xs transition cursor-pointer"
ORDER_TAB_IDLE = "px-3 py-1.5 rounded-lg font-medium text-slate-600 hover:text-slate-900 transition cursor-pointer"


def _derive_category_and_shelf(category_path: str) -> tuple:
    cat = category_path or ""
    if "Tivi" in cat:
        return "Tivi", "Kệ A1"
    if "Điều hòa" in cat:
        return "Điều hòa", "Kệ B1"
    if "Tủ lạnh" in cat:
        return "Tủ lạnh", "Sảnh C1"
    if "Máy giặt" in cat:
        return "Máy giặt", "Kho D1"
    return "Khác", "Kho chung"


def _build_m1_kpi_cards(
    inv_kpis: Dict[str, Any],
    ord_kpis: Dict[str, Any],
    matrix_rows: List[Dict[str, Any]],
    active_filter: str,
    role: str,
) -> List[html.Div]:
    total_cap = inv_kpis.get("total_capital")
    overstock_cap = inv_kpis.get("overstock_capital")
    held_cap_est = sum(float(r["res"]) * float(r["cost_price"]) for r in matrix_rows)

    over_pct = round((overstock_cap / total_cap) * 100, 1) if total_cap else 74.0
    held_pct = round((held_cap_est / total_cap) * 100, 1) if total_cap else 11.3
    good_pct = max(0.0, round(100.0 - over_pct - held_pct, 1))

    urgent_low_no_po = sum(1 for r in matrix_rows if r["soh"] <= r["min_stock"] and r["inc"] == 0)
    incoming_cnt = sum(1 for r in matrix_rows if r["inc"] > 0)
    stagnant_cnt = sum(1 for r in matrix_rows if r["soh"] > r["max_stock"])
    exp_cap_badge = f"Kẹt {ord_kpis.get('display_expired_capital', '****** đ')}"

    return [
        # Card 1: Tổng vốn kho + Progress bar 3 phân đoạn
        html.Div(
            id="kpi-all",
            n_clicks=0,
            className=KPI_ACTIVE_BORDER if active_filter == "all" else KPI_IDLE_BORDER,
            children=[
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span("TỔNG VỐN KHO", className="whitespace-nowrap"),
                                html.Span(
                                    f"12 mặt hàng chính · {inv_kpis['total_soh']} máy",
                                    className="bg-slate-100 text-slate-600 font-medium px-2 py-0.5 rounded-md normal-case tracking-normal whitespace-nowrap",
                                ),
                            ],
                            className="flex items-center justify-between gap-1 text-[11px] xl:text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2",
                        ),
                        html.Div(
                            [
                                html.Span(format_vnd_compact(total_cap, role), className="text-2xl xl:text-3xl font-bold tracking-tight text-slate-900 cost-val"),
                                html.Span(
                                    f"{good_pct:.0f}% luân chuyển tốt",
                                    className="text-[11px] xl:text-xs font-medium text-emerald-700 bg-emerald-50 border border-emerald-200/60 px-2 py-0.5 rounded-md",
                                ),
                            ],
                            className="flex items-baseline gap-2 my-1 whitespace-nowrap",
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span("Cơ cấu sức khỏe vốn"),
                                html.Span(f"{over_pct + held_pct:.0f}% đang kẹt & giữ", className="text-rose-600 font-semibold"),
                            ],
                            className="flex justify-between text-[11px] text-slate-500 font-medium mb-1.5",
                        ),
                        html.Div(
                            [
                                html.Div(style={"width": f"{over_pct}%"}, className="bg-rose-500 h-full rounded-l-full transition-all"),
                                html.Div(style={"width": f"{held_pct}%"}, className="bg-amber-400 h-full transition-all"),
                                html.Div(style={"width": f"{good_pct}%"}, className="bg-emerald-500 h-full rounded-r-full transition-all"),
                            ],
                            className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden flex gap-0.5 p-0.5",
                        ),
                        html.Div(
                            [
                                html.Span([html.Span(className="w-2 h-2 rounded-full bg-rose-500"), f"Đọng {over_pct:.0f}%"], className="flex items-center gap-1"),
                                html.Span([html.Span(className="w-2 h-2 rounded-full bg-amber-400"), f"Giữ {held_pct:.0f}%"], className="flex items-center gap-1"),
                                html.Span([html.Span(className="w-2 h-2 rounded-full bg-emerald-500"), f"Tốt {good_pct:.0f}%"], className="flex items-center gap-1"),
                            ],
                            className="flex items-center justify-between text-[11px] text-slate-500 mt-2",
                        ),
                    ],
                    className="mt-4 pt-3 border-t border-slate-100",
                ),
            ],
        ),
        # Card 2: Vốn chôn vượt trần
        html.Div(
            id="kpi-stagnant",
            n_clicks=0,
            className=KPI_ACTIVE_BORDER if active_filter == "stagnant" else KPI_IDLE_BORDER,
            children=[
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span([html.Span(className="w-2 h-2 rounded-full bg-rose-500 shrink-0"), "VỐN CHÔN VƯỢT TRẦN"], className="flex items-center gap-1.5 whitespace-nowrap"),
                                html.Span(f"{stagnant_cnt} mã vượt trần", className="text-slate-500 font-medium normal-case tracking-normal whitespace-nowrap"),
                            ],
                            className="flex items-center justify-between gap-1 text-[11px] xl:text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2",
                        ),
                        html.Div(
                            [
                                html.Span(format_vnd_compact(overstock_cap, role), className="text-2xl xl:text-3xl font-bold tracking-tight text-rose-600 cost-val"),
                                html.Span(f"Chiếm {over_pct:.1f}% vốn", className="text-[11px] xl:text-xs font-semibold text-rose-700 bg-rose-50 border border-rose-200/60 px-2 py-0.5 rounded-md"),
                            ],
                            className="flex items-baseline gap-2 my-1 whitespace-nowrap",
                        ),
                        html.P("Tiền nằm im vượt định mức, cần giải phóng", className="text-xs text-slate-500 mt-1"),
                    ]
                ),
                html.Div(
                    [
                        html.Span(f"Bấm để lọc {stagnant_cnt} mã", className="text-xs text-slate-400"),
                        html.Span(["Xả thu vốn ", html.I(className="ph-bold ph-arrow-right")], className="text-xs font-semibold text-rose-600 flex items-center gap-1"),
                    ],
                    className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between",
                ),
            ],
        ),
        # Card 3: Đơn giữ quá hạn -> Mác lượng vốn đang kẹt + Link xuống tab Gấp
        html.Div(
            id="kpi-held",
            n_clicks=0,
            className=KPI_ACTIVE_BORDER if active_filter == "held" else KPI_IDLE_BORDER,
            children=[
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span([html.Span(className="w-2 h-2 rounded-full bg-amber-500 shrink-0"), "ĐƠN GIỮ QUÁ HẠN"], className="flex items-center gap-1.5 whitespace-nowrap"),
                                html.Span(f"Khóa {ord_kpis['reserved_units_count']} máy", className="text-slate-500 font-medium normal-case tracking-normal whitespace-nowrap"),
                            ],
                            className="flex items-center justify-between gap-1 text-[11px] xl:text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2",
                        ),
                        html.Div(
                            [
                                html.Span(f"{ord_kpis['expired_orders_count']} đơn", className="text-2xl xl:text-3xl font-bold tracking-tight text-amber-600"),
                                html.Span(exp_cap_badge, className="text-[11px] xl:text-xs font-semibold text-amber-800 bg-amber-50 border border-amber-200/70 px-2 py-0.5 rounded-md cost-val"),
                            ],
                            className="flex items-baseline flex-wrap gap-2 my-1",
                        ),
                        html.P(
                            f"Trong {ord_kpis['reserved_orders_count']} đơn giữ ({ord_kpis['installment_orders_count']} đơn trả góp)",
                            className="text-xs text-slate-500 mt-1",
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Span("Quá 48h giữ hàng", className="text-xs text-slate-400"),
                        html.Button(
                            [f"Xử lý {ord_kpis['expired_orders_count']} đơn ", html.I(className="ph-bold ph-arrow-right")],
                            id="btn-kpi-held-goto-expired",
                            n_clicks=0,
                            className="text-xs font-semibold text-amber-600 hover:text-amber-800 flex items-center gap-1 cursor-pointer bg-transparent border-0 p-0",
                        ),
                    ],
                    className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between",
                ),
            ],
        ),
        # Card 4: Sắp hết & Đang về
        html.Div(
            id="kpi-low",
            n_clicks=0,
            className=KPI_ACTIVE_BORDER if active_filter == "low" else KPI_IDLE_BORDER,
            children=[
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span([html.Span(className="w-2 h-2 rounded-full bg-blue-600 shrink-0"), "SẮP HẾT · CẦN NHẬP"], className="flex items-center gap-1.5 whitespace-nowrap"),
                                html.Span(f"{inv_kpis['stockout_count']} mã chạm đáy", className="text-rose-600 bg-rose-50 font-semibold px-1.5 py-0.5 rounded-md normal-case tracking-normal whitespace-nowrap text-[11px]"),
                            ],
                            className="flex items-center justify-between gap-1 text-[11px] xl:text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2",
                        ),
                        html.Div(
                            [
                                html.Span(f"{urgent_low_no_po} mã chưa đặt", className="text-2xl xl:text-3xl font-bold tracking-tight text-slate-900"),
                                html.Span(f"+{incoming_cnt} mã đang về", className="text-[11px] xl:text-xs font-semibold text-blue-700 bg-blue-50 border border-blue-200/60 px-2 py-0.5 rounded-md whitespace-nowrap"),
                            ],
                            className="flex items-baseline flex-wrap gap-x-2 gap-y-1 my-1",
                        ),
                        html.P(f"Đang vận chuyển +{ord_kpis['in_transit_units']} thiết bị từ Hãng", className="text-xs text-slate-500 mt-1"),
                    ]
                ),
                html.Div(
                    [
                        html.Span("Xem các mã chạm đáy", className="text-xs text-slate-400"),
                        html.Span(["Nhập bù gấp ", html.I(className="ph-bold ph-arrow-right")], className="text-xs font-semibold text-blue-600 flex items-center gap-1"),
                    ],
                    className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between",
                ),
            ],
        ),
    ]


def _build_m1_scatter_figure(merged_df: Any, role: str) -> go.Figure:
    """Biểu đồ Scatter Full-width với tên ngắn tiếng Việt chống đè chữ & Tooltip chi tiết 4 trường."""
    if merged_df.empty:
        return empty_figure("Không có dữ liệu biểu đồ", height=340)

    df = merged_df.sort_values(by=["soh", "sale_price"], ascending=[True, True]).reset_index(drop=True)
    status_palette = {
        "Cảnh báo: Tồn kho quá cao": ("Vượt trần (Chôn vốn)", "#E11D48"),
        "Cảnh báo: Cần nhập gấp": ("Sắp hết / Cần nhập", "#D97706"),
        "Tồn kho an toàn": ("An toàn", "#059669"),
    }
    pos_cycle = ["top center", "bottom center", "top right", "bottom left", "top left", "bottom right"]

    fig = go.Figure()
    for raw_status, (vn_label, hex_color) in status_palette.items():
        sub = df[df["inventory_status"] == raw_status]
        if sub.empty:
            continue
        texts: List[str] = []
        positions: List[str] = []
        customs: List[List[Any]] = []
        sizes: List[float] = []
        for idx, row in sub.iterrows():
            short_lbl = get_short_product_name(row["product_name"], row["product_code"])
            texts.append(short_lbl)
            positions.append(pos_cycle[int(idx) % len(pos_cycle)])
            sizes.append(max(16.0, min(44.0, float(row["soh"]) * 1.6 + 12.0)))
            price_txt = f"{float(row['sale_price']):,.0f} đ"
            customs.append([
                row["product_name"],
                row["product_code"],
                price_txt,
                int(row["soh"]),
                int(row["avl"]),
            ])

        fig.add_trace(
            go.Scatter(
                x=sub["soh"].tolist(),
                y=sub["sale_price"].tolist(),
                mode="markers+text",
                name=vn_label,
                text=texts,
                textposition=positions,
                textfont=dict(size=10, color="#1E293B", family="Inter, sans-serif"),
                marker=dict(size=sizes, color=hex_color, opacity=0.84, line=dict(width=1.5, color="#FFFFFF")),
                customdata=customs,
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Mã sản phẩm: <b>%{customdata[1]}</b><br>"
                    "Giá niêm yết: %{customdata[2]}<br>"
                    "Số lượng tồn thực tế: <b>%{customdata[3]} máy</b> (Bán ngay: %{customdata[4]})"
                    "<extra></extra>"
                ),
            )
        )

    max_soh = max(24.0, float(df["soh"].max()) * 1.15)
    max_price = max(30_000_000.0, float(df["sale_price"].max()) * 1.16)
    fig.update_xaxes(title_text="Số lượng tồn kho thực tế (máy)", range=[-1.8, max_soh])
    fig.update_yaxes(title_text="Giá bán niêm yết (VNĐ)", range=[-1_000_000, max_price])
    fig.update_layout(legend=dict(title_text="", orientation="h", yanchor="bottom", y=1.03, xanchor="left", x=0))
    return apply_stock_sense_layout(fig, height=340, margin=dict(l=54, r=24, t=42, b=38))


def render_m1_kpis_and_table(
    services: Dict[str, Any],
    filter_key: str = "all",
    search: str = "",
    brand_filter: str = "ALL",
    category_filter: str = "ALL",
    shelf_filter: str = "ALL",
    order_filter: str = "all",
    role: str = "ROLE_OWNER",
) -> Dict[str, Any]:
    """Tính toán toàn bộ KPI Cards, Bảng, Ma trận full-width và Quản lý đơn giữ chỗ từ SQLite."""
    inv_svc = services["inventory"]
    ord_svc = services["order"]

    inv_kpis = inv_svc.get_kpis(role=role)
    ord_kpis = ord_svc.get_order_flow_kpis(role=role)
    df_flow = ord_svc.get_inventory_flow_matrix()
    df_prods = inv_svc.get_products_dataframe(role="ROLE_OWNER")[["product_code", "min_stock", "max_stock", "capital_tied"]]
    merged = df_flow.merge(df_prods, on="product_code", how="left")
    matrix_rows = merged.to_dict(orient="records")

    brand_options = sorted({r["brand"] for r in matrix_rows if r.get("brand")})

    counts = {
        "all": len(matrix_rows),
        "stagnant": sum(1 for r in matrix_rows if r["soh"] > r["max_stock"]),
        "low": sum(1 for r in matrix_rows if r["soh"] <= r["min_stock"] or r["avl"] <= r["min_stock"]),
        "held": sum(1 for r in matrix_rows if r["res"] > 0),
        "incoming": sum(1 for r in matrix_rows if r["inc"] > 0),
        "healthy": sum(1 for r in matrix_rows if r["min_stock"] < r["soh"] <= r["max_stock"]),
    }

    kw = (search or "").strip().lower()
    filtered_rows = []
    for r in matrix_rows:
        cat_short, shelf_lbl = _derive_category_and_shelf(r.get("category_path", ""))
        r["cat_short"] = cat_short
        r["shelf_lbl"] = shelf_lbl

        if filter_key == "stagnant" and not (r["soh"] > r["max_stock"]):
            continue
        if filter_key == "low" and not (r["soh"] <= r["min_stock"] or r["avl"] <= r["min_stock"]):
            continue
        if filter_key == "held" and not (r["res"] > 0):
            continue
        if filter_key == "incoming" and not (r["inc"] > 0):
            continue
        if filter_key == "healthy" and not (r["min_stock"] < r["soh"] <= r["max_stock"]):
            continue
        if brand_filter and brand_filter != "ALL" and r.get("brand") != brand_filter:
            continue
        if category_filter and category_filter != "ALL" and cat_short != category_filter:
            continue
        if shelf_filter and shelf_filter != "ALL" and shelf_lbl != shelf_filter:
            continue
        if kw and (
            kw not in r["product_code"].lower()
            and kw not in r["product_name"].lower()
            and kw not in (r.get("brand") or "").lower()
            and kw not in shelf_lbl.lower()
        ):
            continue
        filtered_rows.append(r)

    table_rows: List[html.Tr] = []
    for r in filtered_rows:
        soh, res, avl, inc = int(r["soh"]), int(r["res"]), int(r["avl"]), int(r["inc"])
        min_st, max_st = int(r["min_stock"]), max(1, int(r["max_stock"]))
        fill_pct = min(100, round((soh / max_st) * 100))

        if soh > max_st:
            badge = html.Span("🔴 Vượt trần vốn", className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200/70 whitespace-nowrap")
            bar_cls = "h-1.5 rounded-full bg-rose-500"
            evidence_txt = f"Tồn {soh} / trần {max_st} máy (vượt +{soh - max_st})"
            cta_btn = html.Button(
                "Xả tồn →",
                id={"type": "m1-goto-action", "sku": r["product_code"], "target": "m3"},
                n_clicks=0,
                className="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 cursor-pointer whitespace-nowrap",
            )
        elif inc > 0 and soh <= min_st:
            badge = html.Span(f"🔵 Xe đang về (+{inc})", className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200/70 whitespace-nowrap")
            bar_cls = "h-1.5 rounded-full bg-blue-500"
            evidence_txt = f"Đang về +{inc} máy · bù đủ hàng bán"
            cta_btn = html.Button(
                "Theo dõi nhập",
                id={"type": "m1-goto-action", "sku": r["product_code"], "target": "m4"},
                n_clicks=0,
                className="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 cursor-pointer whitespace-nowrap",
            )
        elif soh <= min_st or avl <= min_st:
            badge = html.Span("⚡ Sắp hết hàng", className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold bg-amber-50 text-amber-800 border border-amber-200/70 whitespace-nowrap")
            bar_cls = "h-1.5 rounded-full bg-amber-500"
            evidence_txt = f"Bán ngay {avl} / tối thiểu {min_st} máy"
            cta_btn = html.Button(
                "Nhập gấp →",
                id={"type": "m1-goto-action", "sku": r["product_code"], "target": "m4"},
                n_clicks=0,
                className="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-slate-900 hover:bg-slate-800 text-white cursor-pointer whitespace-nowrap",
            )
        else:
            badge = html.Span("🟢 An toàn", className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/70 whitespace-nowrap")
            bar_cls = "h-1.5 rounded-full bg-emerald-500"
            evidence_txt = f"Tồn {soh} / định mức {min_st}–{max_st} máy"
            cta_btn = html.Button(
                "Chi tiết",
                id={"type": "m1-open-drawer", "sku": r["product_code"], "slot": "cta"},
                n_clicks=0,
                className="px-2.5 py-1 rounded-lg text-[11px] font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 cursor-pointer whitespace-nowrap",
            )

        cap_str = format_vnd_compact(r["capital_tied"], role)
        avl_cls = "text-rose-600 font-bold" if avl <= 0 else ("text-amber-600 font-bold" if avl <= min_st else "text-emerald-700 font-bold")
        brand_cls = get_brand_badge_class(r.get("brand"))

        table_rows.append(
            html.Tr(
                className="hover:bg-slate-50/90 transition-colors group",
                children=[
                    html.Td(
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span(r["product_code"], className="font-code text-xs font-bold text-slate-900 mr-2"),
                                        html.Span(r["brand"] or "", className=f"text-[10px] px-1.5 py-0.2 rounded font-semibold mr-1.5 {brand_cls}"),
                                        html.Span(r["shelf_lbl"], className="text-[10px] text-slate-400 font-medium"),
                                    ],
                                    className="flex items-center flex-wrap gap-y-0.5",
                                ),
                                html.Div(r["product_name"], className="text-xs text-slate-700 font-medium mt-0.5"),
                            ]
                        ),
                        className="py-3 pl-5 pr-3",
                    ),
                    html.Td(f"{soh}", className="py-3 px-2.5 text-right font-code text-xs font-semibold text-slate-900 tabular-nums"),
                    html.Td(f"{res}", className="py-3 px-2.5 text-right font-code text-xs text-amber-700 font-medium tabular-nums"),
                    html.Td(f"{avl}", className=f"py-3 px-3 text-right font-code text-xs tabular-nums {avl_cls}"),
                    html.Td(f"+{inc}" if inc > 0 else "0", className="py-3 px-2.5 text-right font-code text-xs text-blue-700 font-semibold tabular-nums"),
                    html.Td(
                        html.Div(
                            [
                                badge,
                                html.Div(
                                    html.Div(style={"width": f"{fill_pct}%"}, className=bar_cls),
                                    className="w-36 h-1.5 bg-slate-100 rounded-full overflow-hidden mt-1.5",
                                ),
                                html.Div(evidence_txt, className="text-[11px] text-slate-500 mt-1"),
                            ]
                        ),
                        className="py-3 px-3.5",
                    ),
                    html.Td(cap_str, className="py-3 px-3.5 text-right font-code text-xs font-bold text-slate-900 tabular-nums whitespace-nowrap cost-val"),
                    html.Td(
                        html.Div(
                            [
                                html.Button(
                                    html.I(className="ph-bold ph-qr-code text-sm"),
                                    id={"type": "m1-open-drawer", "sku": r["product_code"], "slot": "qr"},
                                    n_clicks=0,
                                    title="Xem danh sách Số máy / IMEI",
                                    className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 cursor-pointer",
                                ),
                                cta_btn,
                            ],
                            className="flex items-center justify-end gap-1.5",
                        ),
                        className="py-3 pl-3 pr-5 text-right",
                    ),
                ],
            )
        )

    if not table_rows:
        table_rows.append(
            html.Tr(html.Td("Không có mặt hàng nào khớp bộ lọc hiện tại.", colSpan=8, className="py-8 text-center text-xs text-slate-400"))
        )

    fig_sc = _build_m1_scatter_figure(merged, role=role)

    # Reserved orders section rows (group by order_code for clean display)
    df_orders = ord_svc.get_orders_dataframe()
    held_df = df_orders[df_orders["order_status"].isin(["Chờ xử lý", "Đã xác nhận"])]
    if order_filter == "expired":
        held_df = held_df[held_df["is_expired"] == True]

    reserved_order_rows: List[html.Tr] = []
    if not held_df.empty:
        grouped_orders = held_df.groupby("order_code", sort=False)
        for order_code, grp in grouped_orders:
            first = grp.iloc[0]
            is_exp = bool(first["is_expired"])
            prod_summary = ", ".join(f"{row['product_name']}" for _, row in grp.iterrows())
            total_qty = int(grp["quantity"].sum())
            total_val = float(first["total_amount"] or 0)
            paid_val = float(first["amount_paid"] or 0)
            status_badge = (
                html.Span("🚨 Quá hạn 48h giữ chỗ", className="px-2 py-0.5 rounded bg-rose-100 text-rose-700 border border-rose-200 font-bold text-[11px] whitespace-nowrap")
                if is_exp
                else html.Span(f"{first['order_status']} · {first['payment_type']}", className="px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200 font-semibold text-[11px] whitespace-nowrap")
            )
            reserved_order_rows.append(
                html.Tr(
                    className="hover:bg-slate-50/80 transition",
                    children=[
                        html.Td(
                            [
                                html.Span(order_code, className="font-code font-bold text-slate-900 mr-2"),
                                html.Span(first["customer_name"], className="font-semibold text-slate-800"),
                                html.Div(f"Đặt lúc: {str(first['order_time'])[:16]} · SĐT: {first['customer_phone']}", className="text-[11px] text-slate-400 mt-0.5"),
                            ],
                            className="py-2.5 pl-5 pr-3",
                        ),
                        html.Td(prod_summary, className="py-2.5 px-3 text-slate-700 font-medium max-w-[260px]"),
                        html.Td(f"{total_qty} máy", className="py-2.5 px-3 text-right font-code font-semibold text-slate-900"),
                        html.Td(
                            [
                                html.Div(format_vnd_full(total_val, "ROLE_OWNER"), className="font-code font-bold text-slate-900"),
                                html.Div(f"Đã thu/cọc: {format_vnd_compact(paid_val, 'ROLE_OWNER')}", className="text-[11px] text-slate-500"),
                            ],
                            className="py-2.5 px-3 text-right",
                        ),
                        html.Td(status_badge, className="py-2.5 px-3"),
                        html.Td(
                            html.Button(
                                "Xử lý →",
                                id={"type": "m1-open-order-modal", "order": order_code},
                                n_clicks=0,
                                className=(
                                    "px-3 py-1 rounded-lg text-[11px] font-bold bg-rose-600 hover:bg-rose-700 text-white cursor-pointer whitespace-nowrap"
                                    if is_exp
                                    else "px-3 py-1 rounded-lg text-[11px] font-semibold bg-slate-900 hover:bg-slate-800 text-white cursor-pointer whitespace-nowrap"
                                ),
                            ),
                            className="py-2.5 pl-3 pr-5 text-right",
                        ),
                    ],
                )
            )
    if not reserved_order_rows:
        reserved_order_rows.append(
            html.Tr(html.Td("Không còn đơn giữ chỗ nào cần xử lý.", colSpan=6, className="py-6 text-center text-slate-400"))
        )

    pill_classes = {k: (PILL_ACTIVE if k == filter_key else PILL_IDLE) for k in counts}
    footer_summary = html.Span(
        [
            "Đang hiển thị ",
            html.Strong(f"{len(filtered_rows)} / {counts['all']} mặt hàng chính", className="text-slate-800"),
            " · Tổng tồn thực tế: ",
            html.Strong(f"{inv_kpis['total_soh']} máy", className="text-slate-800"),
        ]
    )

    total_held_orders = len(df_orders[df_orders["order_status"].isin(["Chờ xử lý", "Đã xác nhận"])]["order_code"].unique())

    return {
        "kpi_cards": _build_m1_kpi_cards(inv_kpis, ord_kpis, matrix_rows, filter_key, role),
        "table_rows": table_rows,
        "scatter_fig": fig_sc,
        "reserved_order_rows": reserved_order_rows,
        "orders_count_badge": f"{total_held_orders} đơn đang giữ",
        "order_tab_all_cls": ORDER_TAB_ACTIVE if order_filter != "expired" else ORDER_TAB_IDLE,
        "order_tab_exp_cls": ORDER_TAB_ACTIVE if order_filter == "expired" else ORDER_TAB_IDLE,
        "counts": counts,
        "pill_classes": pill_classes,
        "footer_summary": footer_summary,
        "brand_options": brand_options,
    }


def build_m1_order_modal_body(order_code: str, services: Dict[str, Any], role: str = "ROLE_OWNER") -> Dict[str, Any]:
    """Chuẩn bị thông tin chi tiết khách hàng, liên hệ & mặt hàng cho Modal xử lý đơn giữ chỗ."""
    det = services["order"].get_order_detail(order_code, role=role)
    if "error" in det:
        return {
            "order_code": order_code,
            "phone": "",
            "body": html.P(det["error"], className="text-rose-600 font-semibold"),
        }

    exp_banner = (
        html.Div(
            "🚨 Đơn giữ hàng đã quá hạn 48 giờ nhưng khách chưa chốt giao. Nên liên hệ xác nhận lại hoặc Hủy đơn để nhả tồn kho bán cho khách khác.",
            className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 font-medium",
        )
        if det["is_expired"]
        else html.Div(
            f"Trạng thái hiện tại: {det['status']} ({det['payment_type']}).",
            className="p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 font-medium",
        )
    )

    item_rows = [
        html.Tr(
            [
                html.Td(
                    [
                        html.Div(it["product_name"], className="font-semibold text-slate-900"),
                        html.Div(it["product_code"], className="font-code text-[11px] text-slate-500"),
                    ],
                    className="py-2 px-3",
                ),
                html.Td(f"{int(it['quantity'])} máy", className="py-2 px-3 text-right font-code"),
                html.Td(format_vnd_full(it["line_total"], "ROLE_OWNER"), className="py-2 px-3 text-right font-code font-bold text-slate-900"),
            ]
        )
        for it in det["items"]
    ]

    body = html.Div(
        [
            exp_banner,
            html.Div(
                [
                    html.Div([html.Span("Khách hàng:", className="text-slate-500 block"), html.Strong(det["customer_name"], className="text-slate-900 text-sm")]),
                    html.Div([html.Span("Số điện thoại:", className="text-slate-500 block"), html.Strong(det["phone"], className="text-blue-700 font-code text-sm")]),
                    html.Div([html.Span("Thời gian đặt:", className="text-slate-500 block"), html.Strong(str(det["order_time"])[:16], className="text-slate-800")]),
                    html.Div([html.Span("Địa chỉ:", className="text-slate-500 block"), html.Strong(det["address"] or "Tại cửa hàng", className="text-slate-800")]),
                ],
                className="grid grid-cols-2 gap-3 p-3.5 rounded-xl bg-slate-50 border border-slate-200",
            ),
            html.Table(
                [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("Mặt hàng", className="py-2 px-3"),
                                html.Th("Số lượng", className="py-2 px-3 text-right"),
                                html.Th("Thành tiền", className="py-2 px-3 text-right"),
                            ],
                            className="bg-slate-100 text-[11px] text-slate-600 uppercase",
                        )
                    ),
                    html.Tbody(item_rows, className="divide-y divide-slate-100"),
                ],
                className="w-full border border-slate-200 rounded-xl overflow-hidden text-left",
            ),
            html.Div(
                [
                    html.Span(f"Tổng đơn: {format_vnd_full(det['total_amount'], 'ROLE_OWNER')} · Đã thu/cọc: {format_vnd_full(det['amount_paid'], 'ROLE_OWNER')}"),
                    html.Strong(f"Còn phải thu: {format_vnd_full(max(0.0, det['amount_due'] - det['amount_paid']), 'ROLE_OWNER')}", className="text-rose-700"),
                ],
                className="flex flex-wrap items-center justify-between gap-2 pt-2 text-xs text-slate-600",
            ),
        ],
        className="space-y-3",
    )
    return {"order_code": det["order_code"], "phone": det["phone"], "customer_name": det["customer_name"], "body": body}


def build_m1_drawer_body(sku: str, services: Dict[str, Any], role: str = "ROLE_OWNER") -> Dict[str, Any]:
    """Chuẩn bị dữ liệu cho Slide-over Serial Drawer (Detail Drawer)."""
    drill = services["inventory"].get_serial_drilldown(sku)
    if "error" in drill:
        return {
            "sku_badge": sku,
            "product_name": drill["error"],
            "total_capital_text": "****** đ",
            "unit_cost_text": "Giá vốn: ****** đ",
            "stock_ratio_text": "0 / 0 máy",
            "held_info_text": "Đang giữ: 0 máy",
            "velocity_text": "N/A",
            "recommendation": "Không tìm thấy thông tin mặt hàng.",
            "serial_rows": [],
            "target_tab": "m2",
            "cta_label": "Xem Cảnh báo",
        }

    df_flow = services["order"].get_inventory_flow_matrix()
    flow_row = df_flow[df_flow["product_code"] == sku].iloc[0].to_dict()
    df_prod = services["inventory"].get_products_dataframe(search=sku, role="ROLE_OWNER")
    prod_row = df_prod[df_prod["product_code"] == sku].iloc[0].to_dict()

    soh = int(flow_row["soh"])
    res = int(flow_row["res"])
    avl = int(flow_row["avl"])
    cost_price = float(prod_row["cost_price"])
    total_cap = soh * cost_price

    if soh > prod_row["max_stock"]:
        rec_text = (
            f"Mặt hàng này đang vượt trần tồn kho ({soh} máy so với định mức tối đa {int(prod_row['max_stock'])} máy). "
            "Khuyến nghị chuyển sang phân hệ Gợi ý Xả hàng để áp dụng Combo thu hồi vốn nhanh."
        )
        target_tab = "m3"
        cta_label = "Chuyển sang Gợi ý xả hàng"
    elif avl <= prod_row["min_stock"]:
        rec_text = (
            f"Hàng bán ngay chạm ngưỡng tối thiểu (Còn {avl} <= Tối thiểu {int(prod_row['min_stock'])}). "
            "Khuyến nghị mở phân hệ Gợi ý nhập hàng để bổ sung tồn kho kịp thời."
        )
        target_tab = "m4"
        cta_label = "Chuyển sang Gợi ý nhập hàng"
    else:
        rec_text = "Sức khỏe tồn kho đang ở vùng an toàn. Duy trì theo dõi tốc độ ra hàng định kỳ."
        target_tab = "m2"
        cta_label = "Kiểm tra Cần xử lý hôm nay"

    serial_rows = []
    for s in drill["serials"]:
        serial_rows.append(
            html.Tr(
                [
                    html.Td(s["serial_number"], className="py-2 px-3 font-code font-semibold text-slate-900"),
                    html.Td(s["branch_code"], className="py-2 px-3 text-slate-600"),
                    html.Td(str(s["import_date"])[:10], className="py-2 px-3 text-slate-500"),
                    html.Td(
                        html.Span("Còn trong kho", className="px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 font-semibold text-[10px]"),
                        className="py-2 px-3 text-right",
                    ),
                ]
            )
        )
    if not serial_rows:
        serial_rows.append(
            html.Tr(html.Td("Hiện không còn Số máy trong kho (Tồn thực tế = 0).", colSpan=4, className="py-4 text-center text-slate-400"))
        )

    return {
        "sku_badge": sku,
        "product_name": drill["product_name"],
        "total_capital_text": format_vnd_compact(total_cap, role),
        "unit_cost_text": f"Giá vốn: {format_vnd_compact(cost_price, role)}/c",
        "stock_ratio_text": f"{avl} / {soh} máy",
        "held_info_text": f"Đang giữ: {res} máy",
        "velocity_text": f"Δ = {drill['delta']}",
        "recommendation": rec_text,
        "serial_rows": serial_rows,
        "target_tab": target_tab,
        "cta_label": cta_label,
    }


def register_m1_callbacks(app: dash.Dash, services: Dict[str, Any]) -> None:
    """Đăng ký tập trung các Callbacks cho Module 01."""

    @app.callback(
        Output("store-m1-extra-open", "data"),
        Output("m1ExtraFilterPanel", "style"),
        Input("btn-m1-extra-filter", "n_clicks"),
        State("store-m1-extra-open", "data"),
        prevent_initial_call=True,
    )
    def on_toggle_extra_filter(_n, is_open):
        nxt = not bool(is_open)
        return nxt, ({"display": "flex"} if nxt else {"display": "none"})

    @app.callback(
        Output("m1BrandSelect", "value"),
        Output("m1CategorySelect", "value"),
        Output("m1ShelfSelect", "value"),
        Input("btn-m1-reset-extra-filter", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_reset_extra_filter(_n):
        return "ALL", "ALL", "ALL"

    @app.callback(
        Output("store-m1-filter", "data"),
        Input("kpi-all", "n_clicks"),
        Input("kpi-stagnant", "n_clicks"),
        Input("kpi-held", "n_clicks"),
        Input("kpi-low", "n_clicks"),
        Input("m1-pill-all", "n_clicks"),
        Input("m1-pill-stagnant", "n_clicks"),
        Input("m1-pill-low", "n_clicks"),
        Input("m1-pill-held", "n_clicks"),
        Input("m1-pill-incoming", "n_clicks"),
        Input("m1-pill-healthy", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_m1_filter_select(*_args):
        trig = dash.ctx.triggered_id or ""
        for k in ("all", "stagnant", "held", "low", "incoming", "healthy"):
            if trig.endswith(f"-{k}"):
                return k
        return "all"

    @app.callback(
        Output("store-m1-order-filter", "data"),
        Output("store-toast", "data", allow_duplicate=True),
        Input("m1OrderTabAll", "n_clicks"),
        Input("m1OrderTabExpired", "n_clicks"),
        Input("btn-kpi-held-goto-expired", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_m1_order_tab_switch(_all, _exp, _kpi_exp):
        trig = dash.ctx.triggered_id or ""
        if trig in ("m1OrderTabExpired", "btn-kpi-held-goto-expired"):
            toast_val = (
                {"open": True, "message": "Đã chuyển tới danh sách Đơn giữ chỗ quá hạn 48h cần xử lý gấp!", "kind": "success"}
                if trig == "btn-kpi-held-goto-expired"
                else dash.no_update
            )
            return "expired", toast_val
        return "all", dash.no_update

    @app.callback(
        Output("m1-kpi-section", "children"),
        Output("inventoryTableBody", "children"),
        Output("m1-scatter-chart", "figure"),
        Output("m1ReservedOrdersTableBody", "children"),
        Output("m1OrdersCountBadge", "children"),
        Output("m1OrderTabAll", "className"),
        Output("m1OrderTabExpired", "className"),
        Output("tableFooterSummary", "children"),
        Output("m1-pill-all", "className"),
        Output("m1-pill-stagnant", "className"),
        Output("m1-pill-low", "className"),
        Output("m1-pill-held", "className"),
        Output("m1-pill-incoming", "className"),
        Output("m1-pill-healthy", "className"),
        Input("store-m1-filter", "data"),
        Input("searchInput", "value"),
        Input("m1BrandSelect", "value"),
        Input("m1CategorySelect", "value"),
        Input("m1ShelfSelect", "value"),
        Input("store-m1-order-filter", "data"),
        Input("store-role", "data"),
        Input("store-refresh-tick", "data"),
        prevent_initial_call=True,
    )
    def on_m1_refresh(filter_key, search, brand_f, cat_f, shelf_f, order_f, role, _tick):
        res = render_m1_kpis_and_table(
            services,
            filter_key=filter_key or "all",
            search=search or "",
            brand_filter=brand_f or "ALL",
            category_filter=cat_f or "ALL",
            shelf_filter=shelf_f or "ALL",
            order_filter=order_f or "all",
            role=role or "ROLE_OWNER",
        )
        pc = res["pill_classes"]
        return (
            res["kpi_cards"],
            res["table_rows"],
            res["scatter_fig"],
            res["reserved_order_rows"],
            res["orders_count_badge"],
            res["order_tab_all_cls"],
            res["order_tab_exp_cls"],
            res["footer_summary"],
            pc["all"],
            pc["stagnant"],
            pc["low"],
            pc["held"],
            pc["incoming"],
            pc["healthy"],
        )

    @app.callback(
        Output("m1OrderDetailModal", "style"),
        Output("store-m1-active-order", "data"),
        Output("m1OrderModalTitle", "children"),
        Output("m1OrderModalBody", "children"),
        Output("store-refresh-tick", "data", allow_duplicate=True),
        Output("store-toast", "data", allow_duplicate=True),
        Input({"type": "m1-open-order-modal", "order": ALL}, "n_clicks"),
        Input("btn-close-m1-order-modal", "n_clicks"),
        Input("btn-cancel-m1-order-modal", "n_clicks"),
        Input("btn-m1-contact-customer", "n_clicks"),
        Input("btn-m1-cancel-order", "n_clicks"),
        State("store-m1-active-order", "data"),
        State("store-role", "data"),
        State("store-refresh-tick", "data"),
        prevent_initial_call=True,
    )
    def on_m1_order_modal_action(_open, _c1, _c2, _contact, _cancel, active_order, role, tick):
        trig = dash.ctx.triggered_id
        if trig in ("btn-close-m1-order-modal", "btn-cancel-m1-order-modal"):
            return {"display": "none"}, None, dash.no_update, dash.no_update, dash.no_update, dash.no_update

        if isinstance(trig, dict) and trig.get("type") == "m1-open-order-modal":
            val = dash.ctx.triggered[0]["value"] if dash.ctx.triggered else 0
            if not val:
                return tuple([dash.no_update] * 6)
            ord_code = trig["order"]
            info = build_m1_order_modal_body(ord_code, services, role=role or "ROLE_OWNER")
            return {"display": "flex"}, ord_code, f"Đơn hàng #{ord_code}", info["body"], dash.no_update, dash.no_update

        if trig == "btn-m1-contact-customer" and active_order:
            det = services["order"].get_order_detail(active_order, role="ROLE_OWNER")
            phone = det.get("phone", "")
            cname = det.get("customer_name", "")
            return (
                dash.no_update,
                active_order,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                {"open": True, "message": f"Đã ghi nhận nhắc lịch nhận hàng cho {cname} ({phone})!", "kind": "success"},
            )

        if trig == "btn-m1-cancel-order" and active_order:
            res = services["order"].cancel_order(active_order, reason="Quá hạn 48h giữ hàng · Giải phóng tồn kho")
            if res.get("success"):
                return (
                    {"display": "none"},
                    None,
                    dash.no_update,
                    dash.no_update,
                    int(tick or 0) + 1,
                    {"open": True, "message": res["message"], "kind": "success"},
                )
            return (
                dash.no_update,
                active_order,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                {"open": True, "message": res.get("error", "Không thể hủy đơn hàng"), "kind": "error"},
            )

        return tuple([dash.no_update] * 6)

    @app.callback(
        Output("detailDrawer", "className"),
        Output("drawerBackdrop", "style"),
        Output("store-m1-drawer-sku", "data"),
        Output("store-m1-drawer-target-tab", "data"),
        Output("drawerSkuBadge", "children"),
        Output("drawerProductName", "children"),
        Output("drawerTotalCapital", "children"),
        Output("drawerUnitCost", "children"),
        Output("drawerStockRatio", "children"),
        Output("drawerHeldInfo", "children"),
        Output("drawerVelocity", "children"),
        Output("drawerRecommendationText", "children"),
        Output("drawerSerialList", "children"),
        Output("drawerPrimaryCtaLabel", "children"),
        Input({"type": "m1-open-drawer", "sku": ALL, "slot": ALL}, "n_clicks"),
        Input("store-quick-action", "data"),
        Input("btn-close-m1-drawer", "n_clicks"),
        Input("btn-close-m1-drawer-footer", "n_clicks"),
        Input("drawerBackdrop", "n_clicks"),
        Input("store-role", "data"),
        State("store-m1-drawer-sku", "data"),
        prevent_initial_call=True,
    )
    def on_m1_drawer_toggle(_open_clicks, quick_action, _c1, _c2, _c3, role, current_sku):
        trig = dash.ctx.triggered_id
        drawer_closed_cls = "fixed top-0 right-0 h-full w-full max-w-lg bg-white shadow-2xl border-l border-slate-200 z-50 translate-x-full transition-transform duration-300 flex flex-col"
        drawer_open_cls = "fixed top-0 right-0 h-full w-full max-w-lg bg-white shadow-2xl border-l border-slate-200 z-50 translate-x-0 transition-transform duration-300 flex flex-col"

        if trig in ("btn-close-m1-drawer", "btn-close-m1-drawer-footer", "drawerBackdrop"):
            return (drawer_closed_cls, {"display": "none"}, None, dash.no_update, *[dash.no_update] * 10)

        target_sku = None
        if isinstance(trig, dict) and trig.get("type") == "m1-open-drawer":
            triggered_val = dash.ctx.triggered[0]["value"] if dash.ctx.triggered else 0
            if not triggered_val:
                return tuple([dash.no_update] * 14)
            target_sku = trig["sku"]
        elif trig == "store-quick-action" and quick_action == "OPEN_M1_SERIAL_DRAWER":
            target_sku = "TV-LG-55C3"
        elif trig == "store-role" and current_sku:
            target_sku = current_sku
        else:
            return tuple([dash.no_update] * 14)

        body = build_m1_drawer_body(target_sku, services, role=role or "ROLE_OWNER")
        return (
            drawer_open_cls,
            {"display": "block"},
            target_sku,
            body["target_tab"],
            body["sku_badge"],
            body["product_name"],
            body["total_capital_text"],
            body["unit_cost_text"],
            body["stock_ratio_text"],
            body["held_info_text"],
            body["velocity_text"],
            body["recommendation"],
            body["serial_rows"],
            body["cta_label"],
        )

    @app.callback(
        Output("store-active-tab", "data", allow_duplicate=True),
        Output("store-selected-sku", "data", allow_duplicate=True),
        Input({"type": "m1-goto-action", "sku": ALL, "target": ALL}, "n_clicks"),
        Input("btn-m1-drawer-cta", "n_clicks"),
        State("store-m1-drawer-sku", "data"),
        State("store-m1-drawer-target-tab", "data"),
        prevent_initial_call=True,
    )
    def on_m1_cross_navigate(_row_clicks, _cta_click, drawer_sku, drawer_target):
        trig = dash.ctx.triggered_id
        if isinstance(trig, dict) and trig.get("type") == "m1-goto-action":
            if not (dash.ctx.triggered and dash.ctx.triggered[0]["value"]):
                return dash.no_update, dash.no_update
            return trig["target"], trig["sku"]
        if trig == "btn-m1-drawer-cta" and drawer_sku:
            return drawer_target or "m3", drawer_sku
        return dash.no_update, dash.no_update
