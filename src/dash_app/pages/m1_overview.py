"""
Giao diện Module 01: Tổng quan kho & Serial Drill-down (Plotly Dash - Khớp 1:1 Prototype L435-L668 & L2679-L2763).
"""
from typing import Any, Dict, List
from dash import dcc, html

from src.dash_app.components.charts import empty_figure


def build_m1_detail_drawer() -> html.Div:
    """Dựng Slide-over Drawer tra cứu Serial/IMEI chi tiết khớp Prototype L2679-L2763."""
    return html.Div(
        [
            html.Div(
                id="drawerBackdrop",
                n_clicks=0,
                style={"display": "none"},
                className="fixed inset-0 bg-slate-900/30 backdrop-blur-[1px] z-40",
            ),
            html.Aside(
                id="detailDrawer",
                className=(
                    "fixed top-0 right-0 h-full w-full max-w-lg bg-white shadow-2xl border-l border-slate-200 "
                    "z-50 translate-x-full transition-transform duration-300 flex flex-col"
                ),
                children=[
                    dcc.Store(id="store-m1-drawer-sku", data=None),
                    dcc.Store(id="store-m1-drawer-target-tab", data="m3"),
                    # Header
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span("TV-LG-55C3", id="drawerSkuBadge", className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-slate-200/80 text-slate-700"),
                                            html.Span("· Kho CN01", id="drawerShelfBadge", className="text-xs font-medium text-slate-500"),
                                        ],
                                        className="flex items-center gap-2 mb-1",
                                    ),
                                    html.H3("Chi tiết thiết bị", id="drawerProductName", className="text-base font-bold text-slate-900 leading-snug"),
                                ]
                            ),
                            html.Button(
                                html.I(className="ph-bold ph-x text-lg"),
                                id="btn-close-m1-drawer",
                                n_clicks=0,
                                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors cursor-pointer",
                            ),
                        ],
                        className="px-6 py-4 border-b border-slate-200 flex items-start justify-between gap-4 bg-slate-50/70",
                    ),
                    # Body
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span("Vốn đang kẹt", className="text-[11px] font-medium text-slate-500 uppercase"),
                                            html.Div("0 đ", id="drawerTotalCapital", className="text-lg font-bold text-slate-900 mt-0.5 cost-val"),
                                            html.Span("Giá vốn: 0 đ", id="drawerUnitCost", className="text-[11px] text-slate-400 cost-val"),
                                        ],
                                        className="bg-slate-50 p-3.5 rounded-xl border border-slate-200/70",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("Bán ngay / Tồn", className="text-[11px] font-medium text-slate-500 uppercase"),
                                            html.Div("0 / 0 máy", id="drawerStockRatio", className="text-lg font-bold text-slate-900 mt-0.5"),
                                            html.Span("Đang giữ: 0 máy", id="drawerHeldInfo", className="text-[11px] text-amber-600 font-medium"),
                                        ],
                                        className="bg-slate-50 p-3.5 rounded-xl border border-slate-200/70",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("Toàn vẹn Serial", className="text-[11px] font-medium text-slate-500 uppercase"),
                                            html.Div("Δ = 0", id="drawerVelocity", className="text-lg font-bold text-emerald-700 mt-0.5"),
                                            html.Span("Khớp SOH vật lý", id="drawerIntegrityMeta", className="text-[11px] text-slate-400"),
                                        ],
                                        className="bg-slate-50 p-3.5 rounded-xl border border-slate-200/70",
                                    ),
                                ],
                                className="grid grid-cols-3 gap-3",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                [html.I(className="ph-fill ph-warning-circle text-amber-600 text-base"), "Đề xuất cho Chủ cửa hàng"],
                                                id="drawerStatusTitle",
                                                className="text-xs font-bold uppercase tracking-wider text-amber-900 flex items-center gap-1.5",
                                            ),
                                            html.Span("Xả tồn thu vốn", id="drawerActionTag", className="text-xs font-semibold px-2 py-0.5 rounded bg-amber-200/70 text-amber-900"),
                                        ],
                                        className="flex items-center justify-between",
                                    ),
                                    html.P("", id="drawerRecommendationText", className="text-xs text-slate-700 leading-relaxed"),
                                ],
                                id="drawerDecisionBox",
                                className="p-4 rounded-xl border bg-amber-50/70 border-amber-200/90 space-y-2",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H4("Danh sách Serial theo tuổi tồn kho (FIFO)", className="text-xs font-bold uppercase tracking-wider text-slate-500"),
                                            html.Span("Trạng thái IN_STOCK", className="text-xs text-slate-400"),
                                        ],
                                        className="flex items-center justify-between mb-3",
                                    ),
                                    html.Div(
                                        html.Table(
                                            [
                                                html.Thead(
                                                    html.Tr(
                                                        [
                                                            html.Th("Số Serial (IMEI/SN)", className="py-2.5 px-3"),
                                                            html.Th("Kho", className="py-2.5 px-3"),
                                                            html.Th("Ngày nhập", className="py-2.5 px-3"),
                                                            html.Th("Trạng thái", className="py-2.5 px-3 text-right"),
                                                        ],
                                                        className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold",
                                                    )
                                                ),
                                                html.Tbody(id="drawerSerialList", className="divide-y divide-slate-200/70"),
                                            ],
                                            className="w-full text-left border-collapse text-xs",
                                        ),
                                        className="border border-slate-200 rounded-xl overflow-hidden max-h-64 overflow-y-auto",
                                    ),
                                ]
                            ),
                        ],
                        className="p-6 overflow-y-auto flex-1 space-y-6",
                    ),
                    # Footer CTA
                    html.Div(
                        [
                            html.Button(
                                "Đóng",
                                id="btn-close-m1-drawer-footer",
                                n_clicks=0,
                                className="px-4 py-2 rounded-xl border border-slate-300 bg-white hover:bg-slate-50 text-xs font-semibold text-slate-700 cursor-pointer",
                            ),
                            html.Button(
                                [html.I(className="ph-bold ph-lightning"), html.Span("Thực thi ngay", id="drawerPrimaryCtaLabel")],
                                id="btn-m1-drawer-cta",
                                n_clicks=0,
                                className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold flex items-center gap-1.5 shadow-sm cursor-pointer",
                            ),
                        ],
                        className="p-4 border-t border-slate-200 bg-slate-50 flex items-center justify-end gap-2.5",
                    ),
                ],
            ),
        ]
    )


def build_m1_panel(services: Dict[str, Any], active: bool = True, role: str = "ROLE_OWNER") -> html.Main:
    """Dựng toàn bộ vùng nội dung chính Module 01 khớp Prototype L435-L668."""
    from src.dash_app.callbacks.m1_callbacks import render_m1_kpis_and_table

    init_data = render_m1_kpis_and_table(services, filter_key="all", search="", role=role)

    pills = [
        ("all", "Tất cả", None, init_data["counts"]["all"]),
        ("stagnant", "Đọng vốn & Vượt trần", "bg-rose-500", init_data["counts"]["stagnant"]),
        ("low", "Sắp hết", "bg-blue-600", init_data["counts"]["low"]),
        ("held", "Có đơn giữ", "bg-amber-500", init_data["counts"]["held"]),
        ("incoming", "Xe đang về", None, init_data["counts"]["incoming"]),
        ("healthy", "Bán nhanh & An toàn", "bg-emerald-500", init_data["counts"]["healthy"]),
    ]

    pill_btns: List[Any] = []
    for key, label, dot_cls, cnt in pills:
        btn_children: List[Any] = []
        if dot_cls:
            btn_children.append(html.Span(className=f"w-1.5 h-1.5 rounded-full {dot_cls}"))
        btn_children.append(html.Span(label))
        badge_cls = "px-1.5 py-0.2 rounded bg-slate-700 text-slate-100 text-[11px]" if key == "all" else "px-1.5 py-0.2 rounded bg-slate-200 text-slate-700 font-semibold text-[11px]"
        btn_children.append(html.Span(str(cnt), id=f"m1-pill-cnt-{key}", className=badge_cls))
        pill_btns.append(
            html.Button(
                btn_children,
                id=f"m1-pill-{key}",
                n_clicks=0,
                className=init_data["pill_classes"][key],
            )
        )

    return html.Main(
        id="panel-m1",
        style={"display": "flex" if active else "none"},
        className="tab-panel flex-1 flex-col min-w-0 bg-[#F8FAFC] overflow-y-auto custom-scrollbar px-4 sm:px-6 py-5 gap-5",
        children=[
            dcc.Store(id="store-m1-filter", data="all"),
            # 1. 4 KPI Cards Row
            html.Section(
                init_data["kpi_cards"],
                id="m1-kpi-section",
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3.5 relative shrink-0",
            ),
            # 2. Filter Pills + Search Bar + 9-Column Table Container
            html.Section(
                [
                    html.Div(
                        [
                            html.Div(pill_btns, id="filter-pills-container", className="flex items-center gap-1.5 flex-wrap"),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.I(className="ph ph-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm"),
                                            dcc.Input(
                                                id="searchInput",
                                                type="text",
                                                debounce=True,
                                                value="",
                                                placeholder="Tìm tên, model, SKU, hãng...",
                                                className="w-full pl-9 pr-3 py-1.5 bg-slate-50 border border-slate-200/90 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:bg-white focus:border-slate-400 transition-all",
                                            ),
                                        ],
                                        className="relative flex-1 sm:w-56 xl:w-64",
                                    ),
                                    html.Button(
                                        [html.I(className="ph-bold ph-chart-scatter"), html.Span("Biểu đồ & Đơn giữ")],
                                        id="btn-m1-toggle-analytics",
                                        n_clicks=0,
                                        className="px-3 py-1.5 rounded-xl bg-white hover:bg-slate-50 border border-slate-200/90 text-xs font-medium text-slate-700 flex items-center gap-1.5 shrink-0 cursor-pointer",
                                    ),
                                ],
                                className="flex items-center gap-2 shrink-0",
                            ),
                        ],
                        className="p-3.5 sm:px-5 border-b border-slate-200/80 flex flex-col lg:flex-row lg:items-center justify-between gap-2.5",
                    ),
                    # 9-Column Data Table
                    html.Div(
                        html.Table(
                            [
                                html.Thead(
                                    html.Tr(
                                        [
                                            html.Th("SẢN PHẨM & PHÂN LOẠI", className="py-3 pl-5 pr-3 min-w-[290px]"),
                                            html.Th("TỒN", className="py-3 px-2.5 text-right w-16"),
                                            html.Th("GIỮ", className="py-3 px-2.5 text-right w-16"),
                                            html.Th("BÁN NGAY", className="py-3 px-3 text-right w-24 text-slate-800 whitespace-nowrap"),
                                            html.Th("ĐANG VỀ", className="py-3 px-2.5 text-right w-20 whitespace-nowrap"),
                                            html.Th("SỨC KHỎE TỒN KHO", className="py-3 px-3.5 min-w-[200px]"),
                                            html.Th("VỐN TỒN", className="py-3 px-3.5 text-right min-w-[110px] whitespace-nowrap"),
                                            html.Th("HÀNH ĐỘNG", className="py-3 pl-3 pr-5 text-right min-w-[155px]"),
                                        ],
                                        className="border-b border-slate-200/80 bg-slate-50/70 text-[11px] font-semibold uppercase tracking-wider text-slate-500",
                                    )
                                ),
                                html.Tbody(init_data["table_rows"], id="inventoryTableBody", className="divide-y divide-slate-200/60 text-sm"),
                            ],
                            className="w-full text-left border-collapse",
                        ),
                        className="overflow-x-auto relative",
                    ),
                    # Table Footer
                    html.Div(
                        [
                            html.Div(init_data["footer_summary"], id="tableFooterSummary"),
                            html.Div(
                                [
                                    html.I(className="ph-bold ph-qr-code text-slate-700"),
                                    html.Span("Bấm biểu tượng Serial/QR ở cuối dòng để đối soát tuổi tồn từng máy"),
                                ],
                                className="flex items-center gap-1.5 text-slate-500",
                            ),
                        ],
                        className="px-5 py-3.5 bg-slate-50/60 border-t border-slate-200/80 rounded-b-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-slate-500",
                    ),
                ],
                className="bg-white rounded-2xl border border-slate-200/90 shadow-xs flex flex-col relative shrink-0",
            ),
            # 3. Visual Analytics Section (Plotly Scatter 4 Quadrants + Held Orders Summary)
            html.Section(
                id="m1-analytics-section",
                className="grid grid-cols-1 xl:grid-cols-12 gap-4 shrink-0",
                children=[
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H3("Ma trận Sức khỏe Tồn kho: Tồn thực (SOH) vs Giá trị bán", className="text-sm font-bold text-slate-900"),
                                    html.Span("Phát hiện trực quan 4 góc phần tư (Tồn cao chôn vốn vs Hàng cháy)", className="text-xs text-slate-500"),
                                ],
                                className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between",
                            ),
                            html.Div(
                                dcc.Graph(
                                    id="m1-scatter-chart",
                                    figure=init_data["scatter_fig"] if init_data.get("scatter_fig") else empty_figure(),
                                    config={"displayModeBar": False},
                                ),
                                className="p-3",
                            ),
                        ],
                        className="xl:col-span-7 bg-white rounded-2xl border border-slate-200/90 shadow-xs overflow-hidden",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H3("Đơn giữ chỗ & Chờ xử lý quá hạn 48h", className="text-sm font-bold text-slate-900"),
                                    html.Span("US-1.2 Điều phối cọc & Trả góp", className="text-xs text-amber-700 font-semibold"),
                                ],
                                className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between",
                            ),
                            html.Div(init_data["orders_preview"], id="m1-orders-preview", className="p-4 space-y-2.5 text-xs max-h-[340px] overflow-y-auto"),
                        ],
                        className="xl:col-span-5 bg-white rounded-2xl border border-slate-200/90 shadow-xs overflow-hidden",
                    ),
                ],
            ),
        ],
    )
