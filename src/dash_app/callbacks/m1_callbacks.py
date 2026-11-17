"""
Callbacks Module 01: Tổng quan kho, lọc 2 chiều KPI/Pills, Biểu đồ Scatter & Serial Drawer.
"""
from typing import Any, Dict, List, Optional
import dash
from dash import ALL, Input, Output, State, html
import plotly.express as px

from src.dash_app.components.charts import apply_stock_sense_layout, empty_figure
from src.dash_app.components.layout_shell import format_vnd_compact, format_vnd_full

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


def _classify_m1_row(row: Dict[str, Any]) -> str:
    if row["soh"] > row["max_stock"] or (row["inventory_status"] == "Cảnh báo: Tồn kho quá cao"):
        return "stagnant"
    if row["avl"] <= row["min_stock"] or row["soh"] <= row["min_stock"]:
        if row["inc"] > 0 and row["soh"] == 0:
            return "low"
        return "low"
    return "healthy"


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
    healthy_cap_est = max(0.0, (total_cap or 0.0) - (overstock_cap or 0.0) - held_cap_est) if total_cap else 0.0

    over_pct = round((overstock_cap / total_cap) * 100, 1) if total_cap else 71.7
    held_pct = round((held_cap_est / total_cap) * 100, 1) if total_cap else 11.3
    good_pct = max(0.0, round(100.0 - over_pct - held_pct, 1))

    urgent_low_no_po = sum(1 for r in matrix_rows if r["soh"] <= r["min_stock"] and r["inc"] == 0)
    incoming_cnt = sum(1 for r in matrix_rows if r["inc"] > 0)
    stagnant_cnt = sum(1 for r in matrix_rows if r["soh"] > r["max_stock"])

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
                                    f"12 máy chính · {inv_kpis['total_soh']} máy",
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
        # Card 2: Vốn chôn > 60 ngày
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
                                html.Span(f"{stagnant_cnt} mã vượt Max", className="text-slate-500 font-medium normal-case tracking-normal whitespace-nowrap"),
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
        # Card 3: Đơn giữ quá hạn
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
                                html.Span("Quá 48h giữ chỗ", className="text-[11px] xl:text-xs font-semibold text-amber-800 bg-amber-50 border border-amber-200/70 px-2 py-0.5 rounded-md"),
                            ],
                            className="flex items-baseline gap-2 my-1 whitespace-nowrap",
                        ),
                        html.P(
                            f"Trong {ord_kpis['reserved_orders_count']} đơn giữ ({ord_kpis['installment_orders_count']} đơn trả góp)",
                            className="text-xs text-slate-500 mt-1 whitespace-nowrap",
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Span("Bấm lọc mã có đơn giữ", className="text-xs text-slate-400"),
                        html.Span([f"Xử lý {ord_kpis['expired_orders_count']} đơn ", html.I(className="ph-bold ph-arrow-right")], className="text-xs font-semibold text-amber-600 flex items-center gap-1"),
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
                                html.Span(f"{urgent_low_no_po} mã trống PO", className="text-2xl xl:text-3xl font-bold tracking-tight text-slate-900"),
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


def render_m1_kpis_and_table(
    services: Dict[str, Any],
    filter_key: str = "all",
    search: str = "",
    role: str = "ROLE_OWNER",
) -> Dict[str, Any]:
    """Tính toán toàn bộ KPI Cards, Bảng 9 cột, Biểu đồ Scatter và Danh sách đơn giữ chỗ từ SQLite."""
    inv_svc = services["inventory"]
    ord_svc = services["order"]

    inv_kpis = inv_svc.get_kpis(role=role)
    ord_kpis = ord_svc.get_order_flow_kpis()
    df_flow = ord_svc.get_inventory_flow_matrix()
    df_prods = inv_svc.get_products_dataframe(role="ROLE_OWNER")[["product_code", "min_stock", "max_stock", "capital_tied"]]
    merged = df_flow.merge(df_prods, on="product_code", how="left")
    matrix_rows = merged.to_dict(orient="records")

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
        if kw and kw not in r["product_code"].lower() and kw not in r["product_name"].lower() and kw not in (r["brand"] or "").lower():
            continue
        filtered_rows.append(r)

    table_rows: List[html.Tr] = []
    for r in filtered_rows:
        soh, res, avl, inc = int(r["soh"]), int(r["res"]), int(r["avl"]), int(r["inc"])
        max_st = max(1, int(r["max_stock"]))
        fill_pct = min(100, round((soh / max_st) * 100))

        if soh > r["max_stock"]:
            badge = html.Span("🔴 Vượt trần vốn", className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200/70 whitespace-nowrap")
            bar_cls = "h-1.5 rounded-full bg-rose-500"
            cta_btn = html.Button(
                "Xả tồn →",
                id={"type": "m1-goto-action", "sku": r["product_code"], "target": "m3"},
                n_clicks=0,
                className="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 cursor-pointer whitespace-nowrap",
            )
        elif inc > 0 and soh <= r["min_stock"]:
            badge = html.Span(f"🔵 Xe đang về (+{inc})", className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200/70 whitespace-nowrap")
            bar_cls = "h-1.5 rounded-full bg-blue-500"
            cta_btn = html.Button(
                "Theo dõi PO",
                id={"type": "m1-goto-action", "sku": r["product_code"], "target": "m4"},
                n_clicks=0,
                className="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 cursor-pointer whitespace-nowrap",
            )
        elif soh <= r["min_stock"] or avl <= r["min_stock"]:
            badge = html.Span("⚡ Sắp hết hàng", className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold bg-amber-50 text-amber-800 border border-amber-200/70 whitespace-nowrap")
            bar_cls = "h-1.5 rounded-full bg-amber-500"
            cta_btn = html.Button(
                "Nhập gấp →",
                id={"type": "m1-goto-action", "sku": r["product_code"], "target": "m4"},
                n_clicks=0,
                className="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-slate-900 hover:bg-slate-800 text-white cursor-pointer whitespace-nowrap",
            )
        else:
            badge = html.Span("🟢 An toàn", className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/70 whitespace-nowrap")
            bar_cls = "h-1.5 rounded-full bg-emerald-500"
            cta_btn = html.Button(
                "Chi tiết",
                id={"type": "m1-open-drawer", "sku": r["product_code"], "slot": "cta"},
                n_clicks=0,
                className="px-2.5 py-1 rounded-lg text-[11px] font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 cursor-pointer whitespace-nowrap",
            )

        cap_str = format_vnd_compact(r["capital_tied"], role)
        avl_cls = "text-rose-600 font-bold" if avl <= 0 else ("text-amber-600 font-bold" if avl <= r["min_stock"] else "text-emerald-700 font-bold")

        table_rows.append(
            html.Tr(
                className="hover:bg-slate-50/90 transition-colors group",
                children=[
                    html.Td(
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span(r["product_code"], className="font-mono text-xs font-bold text-slate-900 mr-2"),
                                        html.Span(r["brand"] or "", className="text-[11px] px-1.5 py-0.2 rounded bg-slate-100 text-slate-600 font-medium"),
                                    ]
                                ),
                                html.Div(r["product_name"], className="text-xs text-slate-700 font-medium mt-0.5"),
                            ]
                        ),
                        className="py-3 pl-5 pr-3",
                    ),
                    html.Td(f"{soh}", className="py-3 px-2.5 text-right font-mono text-xs font-semibold text-slate-900 tabular-nums"),
                    html.Td(f"{res}", className="py-3 px-2.5 text-right font-mono text-xs text-amber-700 font-medium tabular-nums"),
                    html.Td(f"{avl}", className=f"py-3 px-3 text-right font-mono text-xs tabular-nums {avl_cls}"),
                    html.Td(f"+{inc}" if inc > 0 else "0", className="py-3 px-2.5 text-right font-mono text-xs text-blue-700 font-semibold tabular-nums"),
                    html.Td(
                        html.Div(
                            [
                                badge,
                                html.Div(
                                    html.Div(style={"width": f"{fill_pct}%"}, className=bar_cls),
                                    className="w-28 h-1.5 bg-slate-100 rounded-full overflow-hidden mt-1.5",
                                ),
                            ]
                        ),
                        className="py-3 px-3.5",
                    ),
                    html.Td(cap_str, className="py-3 px-3.5 text-right font-mono text-xs font-bold text-slate-900 tabular-nums whitespace-nowrap cost-val"),
                    html.Td(
                        html.Div(
                            [
                                html.Button(
                                    html.I(className="ph-bold ph-qr-code text-sm"),
                                    id={"type": "m1-open-drawer", "sku": r["product_code"], "slot": "qr"},
                                    n_clicks=0,
                                    title="Mở Serial Drawer",
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
            html.Tr(html.Td("Không có mặt hàng nào khớp bộ lọc.", colSpan=8, className="py-8 text-center text-xs text-slate-400"))
        )

    # Scatter chart
    if not merged.empty:
        fig_sc = px.scatter(
            merged,
            x="soh",
            y="sale_price",
            size=merged["soh"].clip(lower=2),
            color="inventory_status",
            hover_name="product_name",
            text="product_code",
            labels={"soh": "Tồn kho thực tế (SOH)", "sale_price": "Giá bán niêm yết (VNĐ)", "inventory_status": "Sức khỏe"},
            color_discrete_map={
                "Cảnh báo: Tồn kho quá cao": "#E11D48",
                "Cảnh báo: Cần nhập gấp": "#D97706",
                "Tồn kho an toàn": "#059669",
            },
            size_max=34,
        )
        fig_sc.update_traces(textposition="top center", textfont_size=10)
        fig_sc.update_layout(legend=dict(title_text="", orientation="h", yanchor="bottom", y=1.04, xanchor="left", x=0))
        apply_stock_sense_layout(fig_sc, height=320, margin=dict(l=44, r=16, t=44, b=36))
    else:
        fig_sc = empty_figure("Không có dữ liệu biểu đồ", height=320)

    # Held/expired orders preview
    df_orders = ord_svc.get_orders_dataframe()
    held_orders = df_orders[df_orders["order_status"].isin(["Chờ xử lý", "Đã xác nhận"])].head(8)
    orders_preview = []
    for _, orow in held_orders.iterrows():
        is_exp = bool(orow["is_expired"])
        orders_preview.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(orow["order_code"], className="font-mono font-bold text-slate-900 mr-2"),
                            html.Span(orow["customer_name"], className="font-semibold text-slate-800"),
                            html.Div(f"{orow['product_name']} (SL: {orow['quantity']})", className="text-[11px] text-slate-500 mt-0.5"),
                        ]
                    ),
                    html.Div(
                        [
                            html.Span(
                                "🚨 Quá hạn 48h" if is_exp else orow["payment_type"],
                                className=(
                                    "px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-700"
                                    if is_exp
                                    else "px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-50 text-amber-800"
                                ),
                            ),
                            html.Div(f"{orow['order_status']}", className="text-[10px] text-slate-400 text-right mt-0.5"),
                        ],
                        className="text-right shrink-0",
                    ),
                ],
                className="p-2.5 rounded-xl border border-slate-200/80 bg-slate-50/70 flex items-center justify-between gap-2",
            )
        )

    pill_classes = {k: (PILL_ACTIVE if k == filter_key else PILL_IDLE) for k in counts}
    footer_summary = html.Span(
        [
            "Đang hiển thị ",
            html.Strong(f"{len(filtered_rows)} / {counts['all']} thiết bị chính", className="text-slate-800"),
            " · Tổng SOH: ",
            html.Strong(f"{inv_kpis['total_soh']} máy", className="text-slate-800"),
        ]
    )

    return {
        "kpi_cards": _build_m1_kpi_cards(inv_kpis, ord_kpis, matrix_rows, filter_key, role),
        "table_rows": table_rows,
        "scatter_fig": fig_sc,
        "orders_preview": orders_preview,
        "counts": counts,
        "pill_classes": pill_classes,
        "footer_summary": footer_summary,
    }


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
            "recommendation": "Không tìm thấy thông tin SKU.",
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
            f"SKU này đang vượt trần tồn kho ({soh} máy so với định mức tối đa {int(prod_row['max_stock'])} máy). "
            "Khuyến nghị chuyển sang Phân hệ Gợi ý Xả hàng (Module 03) để áp dụng Combo Phụ kiện thu hồi vốn nhanh."
        )
        target_tab = "m3"
        cta_label = "Chuyển sang M3: Xả hàng"
    elif avl <= prod_row["min_stock"]:
        rec_text = (
            f"Tồn khả dụng chạm ngưỡng nguy hiểm (AVL={avl} <= Min {int(prod_row['min_stock'])}). "
            "Khuyến nghị mở Module 04 để tạo đơn đặt hàng PO bổ sung ngay."
        )
        target_tab = "m4"
        cta_label = "Chuyển sang M4: Nhập hàng"
    else:
        rec_text = "Sức khỏe tồn kho đang ở vùng an toàn. Duy trì theo dõi tốc độ ra hàng định kỳ."
        target_tab = "m2"
        cta_label = "Kiểm tra Radar M2"

    serial_rows = []
    for s in drill["serials"]:
        serial_rows.append(
            html.Tr(
                [
                    html.Td(s["serial_number"], className="py-2 px-3 font-mono font-semibold text-slate-900"),
                    html.Td(s["branch_code"], className="py-2 px-3 text-slate-600"),
                    html.Td(str(s["import_date"])[:10], className="py-2 px-3 text-slate-500"),
                    html.Td(
                        html.Span("IN_STOCK", className="px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 font-semibold text-[10px]"),
                        className="py-2 px-3 text-right",
                    ),
                ]
            )
        )
    if not serial_rows:
        serial_rows.append(
            html.Tr(html.Td("Hiện không còn Serial IN_STOCK (SOH = 0).", colSpan=4, className="py-4 text-center text-slate-400"))
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
        Output("m1-kpi-section", "children"),
        Output("inventoryTableBody", "children"),
        Output("m1-scatter-chart", "figure"),
        Output("m1-orders-preview", "children"),
        Output("tableFooterSummary", "children"),
        Output("m1-pill-all", "className"),
        Output("m1-pill-stagnant", "className"),
        Output("m1-pill-low", "className"),
        Output("m1-pill-held", "className"),
        Output("m1-pill-incoming", "className"),
        Output("m1-pill-healthy", "className"),
        Input("store-m1-filter", "data"),
        Input("searchInput", "value"),
        Input("store-role", "data"),
        Input("store-refresh-tick", "data"),
        prevent_initial_call=True,
    )
    def on_m1_refresh(filter_key, search, role, _tick):
        res = render_m1_kpis_and_table(services, filter_key=filter_key or "all", search=search or "", role=role or "ROLE_OWNER")
        pc = res["pill_classes"]
        return (
            res["kpi_cards"],
            res["table_rows"],
            res["scatter_fig"],
            res["orders_preview"],
            res["footer_summary"],
            pc["all"],
            pc["stagnant"],
            pc["low"],
            pc["held"],
            pc["incoming"],
            pc["healthy"],
        )

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
            # Only open if button was actually clicked
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
