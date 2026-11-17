"""
Giao diện Module 01: Tổng quan kho, Ma trận Sức khỏe toàn màn hình & Quản lý Đơn giữ chỗ (Plotly Dash).
"""
from typing import Any, Dict, List
from dash import dcc, html

from src.dash_app.components.charts import empty_figure


def build_m1_detail_drawer() -> html.Div:
    """Dựng Slide-over Drawer tra cứu Số máy/IMEI và Modal Xử lý Đơn giữ chỗ."""
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
                                            html.Span("· Kho Cầu Giấy", id="drawerShelfBadge", className="text-xs font-medium text-slate-500"),
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
                                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition cursor-pointer",
                            ),
                        ],
                        className="p-5 border-b border-slate-200/80 flex items-start justify-between gap-4 bg-slate-50/70",
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
                                            html.Span("Toàn vẹn Số máy", className="text-[11px] font-medium text-slate-500 uppercase"),
                                            html.Div("Δ = 0", id="drawerVelocity", className="text-lg font-bold text-emerald-700 mt-0.5"),
                                            html.Span("Khớp tồn kho thực tế", id="drawerIntegrityMeta", className="text-[11px] text-slate-400"),
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
                                            html.H4("Danh sách Số máy theo tuổi tồn kho (Nhập trước xuất trước)", className="text-xs font-bold uppercase tracking-wider text-slate-500"),
                                            html.Span("Đang nằm trong kho", className="text-xs text-slate-400"),
                                        ],
                                        className="flex items-center justify-between mb-3",
                                    ),
                                    html.Div(
                                        html.Table(
                                            [
                                                html.Thead(
                                                    html.Tr(
                                                        [
                                                            html.Th("Số máy (IMEI/Serial)", className="py-2.5 px-3"),
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
            # MODAL CHI TIẾT ĐƠN GIỮ CHỖ & HỦY ĐƠN / LIÊN HỆ KHÁCH HÀNG
            dcc.Store(id="store-m1-active-order", data=None),
            html.Div(
                id="m1OrderDetailModal",
                style={"display": "none"},
                className="fixed inset-0 bg-slate-900/50 backdrop-blur-[1px] z-50 items-center justify-center p-4 flex",
                children=html.Div(
                    className="bg-white rounded-2xl max-w-xl w-full border border-slate-200 shadow-2xl overflow-hidden",
                    children=[
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span("CHI TIẾT ĐƠN GIỮ CHỖ", className="text-[10px] font-bold uppercase tracking-wider text-amber-300 block"),
                                        html.H3("Đơn hàng #DH00000", id="m1OrderModalTitle", className="text-base font-bold text-white mt-0.5 font-code"),
                                    ]
                                ),
                                html.Button("✕", id="btn-close-m1-order-modal", n_clicks=0, className="text-slate-300 hover:text-white cursor-pointer text-base p-1"),
                            ],
                            className="px-5 py-3.5 bg-slate-900 flex items-center justify-between",
                        ),
                        html.Div(id="m1OrderModalBody", className="p-5 space-y-3 text-xs max-h-[65vh] overflow-y-auto"),
                        html.Div(
                            [
                                html.Button(
                                    "Đóng",
                                    id="btn-cancel-m1-order-modal",
                                    n_clicks=0,
                                    className="px-3.5 py-2 rounded-xl border border-slate-300 bg-white hover:bg-slate-50 text-xs font-semibold text-slate-700 cursor-pointer",
                                ),
                                html.Div(
                                    [
                                        html.Button(
                                            "📞 Liên hệ khách hàng",
                                            id="btn-m1-contact-customer",
                                            n_clicks=0,
                                            className="px-3.5 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold cursor-pointer",
                                        ),
                                        html.Button(
                                            "✕ Hủy đơn & Nhả giữ chỗ",
                                            id="btn-m1-cancel-order",
                                            n_clicks=0,
                                            className="px-3.5 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold cursor-pointer",
                                        ),
                                    ],
                                    className="flex items-center gap-2",
                                ),
                            ],
                            className="px-5 py-3.5 bg-slate-50 border-t border-slate-200 flex flex-wrap items-center justify-between gap-2",
                        ),
                    ],
                ),
            ),
        ]
    )


def build_m1_panel(services: Dict[str, Any], active: bool = True, role: str = "ROLE_OWNER") -> html.Main:
    """Dựng toàn bộ vùng nội dung chính Module 01: 4 KPI, Bảng, Ma trận full-width & Quản lý đơn giữ chỗ."""
    from src.dash_app.callbacks.m1_callbacks import render_m1_kpis_and_table

    init_data = render_m1_kpis_and_table(services, filter_key="all", search="", role=role)

    pills = [
        ("all", "Tất cả", None, init_data["counts"]["all"]),
        ("stagnant", "Đọng vốn & Vượt trần", "bg-rose-500", init_data["counts"]["stagnant"]),
        ("low", "Sắp hết hàng", "bg-blue-600", init_data["counts"]["low"]),
        ("held", "Có đơn giữ chỗ", "bg-amber-500", init_data["counts"]["held"]),
        ("incoming", "Hàng đang về", None, init_data["counts"]["incoming"]),
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
            dcc.Store(id="store-m1-order-filter", data="all"),
            dcc.Store(id="store-m1-extra-open", data=False),
            # 1. 4 KPI Cards Row
            html.Section(
                init_data["kpi_cards"],
                id="m1-kpi-section",
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3.5 relative shrink-0",
            ),
            # 2. Filter Pills + Search + "Lọc thêm" + Data Table
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
                                                placeholder="Tìm tên máy, mã hàng, kệ kho...",
                                                className="w-full pl-9 pr-3 py-1.5 bg-slate-50 border border-slate-200/90 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:bg-white focus:border-slate-400 transition-all",
                                            ),
                                        ],
                                        className="relative flex-1 sm:w-56 xl:w-64",
                                    ),
                                    html.Button(
                                        [html.I(className="ph-bold ph-sliders-horizontal"), html.Span("Lọc thêm")],
                                        id="btn-m1-extra-filter",
                                        n_clicks=0,
                                        className="px-3 py-1.5 rounded-xl bg-white hover:bg-slate-50 border border-slate-200/90 text-xs font-medium text-slate-700 flex items-center gap-1.5 shrink-0 cursor-pointer",
                                    ),
                                ],
                                className="flex items-center gap-2 shrink-0",
                            ),
                        ],
                        className="p-3.5 sm:px-5 border-b border-slate-200/80 flex flex-col lg:flex-row lg:items-center justify-between gap-2.5",
                    ),
                    # Collapsible Extra Filters (Thương hiệu, Ngành hàng, Kệ kho)
                    html.Div(
                        id="m1ExtraFilterPanel",
                        style={"display": "none"},
                        className="px-5 py-3 bg-slate-50/90 border-b border-slate-200/80 flex-wrap items-center gap-3 text-xs",
                        children=[
                            html.Span("Bộ lọc nâng cao:", className="font-semibold text-slate-500"),
                            html.Div(
                                dcc.Dropdown(
                                    id="m1BrandSelect",
                                    value="ALL",
                                    clearable=False,
                                    options=[{"label": "Thương hiệu: Tất cả", "value": "ALL"}]
                                    + [{"label": b, "value": b} for b in init_data["brand_options"]],
                                    className="w-44 text-xs",
                                )
                            ),
                            html.Div(
                                dcc.Dropdown(
                                    id="m1CategorySelect",
                                    value="ALL",
                                    clearable=False,
                                    options=[
                                        {"label": "Ngành hàng: Tất cả", "value": "ALL"},
                                        {"label": "Tivi", "value": "Tivi"},
                                        {"label": "Điều hòa", "value": "Điều hòa"},
                                        {"label": "Tủ lạnh", "value": "Tủ lạnh"},
                                        {"label": "Máy giặt", "value": "Máy giặt"},
                                    ],
                                    className="w-44 text-xs",
                                )
                            ),
                            html.Div(
                                dcc.Dropdown(
                                    id="m1ShelfSelect",
                                    value="ALL",
                                    clearable=False,
                                    options=[
                                        {"label": "Kệ kho: Tất cả", "value": "ALL"},
                                        {"label": "Kệ A1 (Khu Tivi)", "value": "Kệ A1"},
                                        {"label": "Kệ B1 (Khu Điều hòa)", "value": "Kệ B1"},
                                        {"label": "Sảnh C1 (Khu Tủ lạnh)", "value": "Sảnh C1"},
                                        {"label": "Kho D1 (Khu Máy giặt)", "value": "Kho D1"},
                                    ],
                                    className="w-48 text-xs",
                                )
                            ),
                            html.Button(
                                "↺ Đặt lại",
                                id="btn-m1-reset-extra-filter",
                                n_clicks=0,
                                className="px-2.5 py-1.5 rounded-lg bg-white border border-slate-200 hover:bg-slate-100 text-xs font-medium text-slate-600 cursor-pointer",
                            ),
                        ],
                    ),
                    # Data Table
                    html.Div(
                        html.Table(
                            [
                                html.Thead(
                                    html.Tr(
                                        [
                                            html.Th("SẢN PHẨM & VỊ TRÍ KỆ", className="py-3 pl-5 pr-3 min-w-[290px]"),
                                            html.Th("TỒN THỰC", className="py-3 px-2.5 text-right w-20"),
                                            html.Th("ĐANG GIỮ", className="py-3 px-2.5 text-right w-20"),
                                            html.Th("BÁN NGAY", className="py-3 px-3 text-right w-24 text-slate-800 whitespace-nowrap"),
                                            html.Th("ĐANG VỀ", className="py-3 px-2.5 text-right w-20 whitespace-nowrap"),
                                            html.Th("SỨC KHỎE TỒN KHO", className="py-3 px-3.5 min-w-[235px]"),
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
                                    html.Span("Bấm biểu tượng mã số ở cuối dòng để đối soát tuổi tồn từng máy"),
                                ],
                                className="flex items-center gap-1.5 text-slate-500",
                            ),
                        ],
                        className="px-5 py-3.5 bg-slate-50/60 border-t border-slate-200/80 rounded-b-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-slate-500",
                    ),
                ],
                className="bg-white rounded-2xl border border-slate-200/90 shadow-xs flex flex-col relative shrink-0",
            ),
            # 3. Full-Width Visual Matrix Section (Ma trận Sức khỏe Tồn kho & Giá trị bán)
            html.Section(
                id="m1-analytics-section",
                className="bg-white rounded-2xl border border-slate-200/90 shadow-xs overflow-hidden shrink-0",
                children=[
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H3("Ma trận Sức khỏe Tồn kho & Giá trị bán", className="text-sm font-bold text-slate-900"),
                                    html.Span("Phát hiện trực quan nhóm hàng chôn vốn quá nhiều vs hàng sắp đứt kho · Di chuột vào bong bóng để xem chi tiết", className="text-xs text-slate-500"),
                                ]
                            ),
                            html.Span("Toàn cảnh 12 mặt hàng chính", className="px-2.5 py-1 rounded-lg bg-slate-100 text-slate-600 text-[11px] font-semibold shrink-0"),
                        ],
                        className="px-5 py-3.5 border-b border-slate-100 flex flex-wrap items-center justify-between gap-2",
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
            ),
            # 4. Quản lý những đơn giữ chỗ (Dưới Ma trận)
            html.Section(
                id="m1ReservedOrdersSection",
                className="bg-white rounded-2xl border border-slate-200/90 shadow-xs overflow-hidden shrink-0",
                children=[
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(className="w-2.5 h-2.5 rounded-full bg-amber-500 shrink-0"),
                                            html.H3("Quản lý những đơn giữ chỗ", className="text-sm font-bold text-slate-900"),
                                            html.Span(init_data["orders_count_badge"], id="m1OrdersCountBadge", className="px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 text-[11px] font-bold"),
                                        ],
                                        className="flex items-center gap-2",
                                    ),
                                    html.P("Theo dõi đơn khách cọc/trả góp giữ máy và xử lý giải phóng tồn khi quá hạn 48 giờ", className="text-xs text-slate-500 mt-0.5"),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Button(
                                        "Tất cả đơn giữ",
                                        id="m1OrderTabAll",
                                        n_clicks=0,
                                        className=init_data["order_tab_all_cls"],
                                    ),
                                    html.Button(
                                        "🚨 Cần xử lý gấp (Quá hạn 48h)",
                                        id="m1OrderTabExpired",
                                        n_clicks=0,
                                        className=init_data["order_tab_exp_cls"],
                                    ),
                                ],
                                className="inline-flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200/80 text-xs gap-1",
                            ),
                        ],
                        className="px-5 py-3.5 border-b border-slate-200/80 flex flex-wrap items-center justify-between gap-3 bg-slate-50/50",
                    ),
                    html.Div(
                        html.Table(
                            [
                                html.Thead(
                                    html.Tr(
                                        [
                                            html.Th("MÃ ĐƠN & KHÁCH HÀNG", className="py-2.5 pl-5 pr-3"),
                                            html.Th("SẢN PHẨM TRONG ĐƠN", className="py-2.5 px-3"),
                                            html.Th("SỐ LƯỢNG", className="py-2.5 px-3 text-right"),
                                            html.Th("TỔNG GIÁ TRỊ & ĐÃ CỌC", className="py-2.5 px-3 text-right"),
                                            html.Th("TRẠNG THÁI GIỮ CHỖ", className="py-2.5 px-3"),
                                            html.Th("XỬ LÝ ĐƠN", className="py-2.5 pl-3 pr-5 text-right"),
                                        ],
                                        className="bg-slate-50/80 border-b border-slate-200 text-[11px] font-bold uppercase tracking-wider text-slate-500",
                                    )
                                ),
                                html.Tbody(init_data["reserved_order_rows"], id="m1ReservedOrdersTableBody", className="divide-y divide-slate-100 text-xs"),
                            ],
                            className="w-full text-left border-collapse",
                        ),
                        className="overflow-x-auto max-h-[380px] overflow-y-auto custom-scrollbar",
                    ),
                ],
            ),
        ],
    )
