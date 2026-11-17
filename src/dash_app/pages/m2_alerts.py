"""
Giao diện Module 02 (Parity V2): Cần xử lý hôm nay —
Pie Chart Vốn kẹt dải Vàng-Cam-Đỏ-Nâu đỏ, Bảng 7 cột Ảnh 1 với .cell-hscroll và Thuật ngữ thuần Việt.
"""
from typing import Any, Dict, List
from dash import dcc, html

from src.dash_app.components.charts import empty_figure


def build_m2_modals_and_drawer() -> html.Div:
    """Dựng Slide-over Decision Drawer, Snooze Modal và Threshold Modal của Module 02."""
    return html.Div(
        [
            dcc.Store(id="store-m2-drawer-sku", data=None),
            dcc.Store(id="store-m2-drawer-target", data="m3"),
            dcc.Store(id="store-m2-snooze-sku", data=None),
            # Slide-over Decision Drawer
            html.Div(
                id="m2DrawerBackdrop",
                n_clicks=0,
                style={"display": "none"},
                className="fixed inset-0 bg-slate-900/30 backdrop-blur-[1px] z-40",
            ),
            html.Aside(
                id="m2DecisionDrawer",
                className=(
                    "fixed top-0 right-0 h-full w-[460px] max-w-full bg-white shadow-2xl border-l border-slate-200 "
                    "z-50 transform translate-x-full transition-transform duration-200 flex flex-col justify-between"
                ),
                children=[
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span("", id="m2DrawerTypeBadge", className="inline-block px-2 py-0.5 rounded text-[11px] font-bold mb-1"),
                                            html.H3("", id="m2DrawerProductName", className="text-base font-bold text-slate-900"),
                                            html.P("", id="m2DrawerMeta", className="text-xs text-slate-500 mt-0.5 font-code"),
                                        ]
                                    ),
                                    html.Button("✕", id="btn-close-m2-drawer", n_clicks=0, className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 cursor-pointer"),
                                ],
                                className="flex items-start justify-between gap-3 pb-3 border-b border-slate-100",
                            ),
                            html.Div(id="m2DrawerBodyContent", className="space-y-4 text-xs mt-4"),
                        ],
                        className="p-5 overflow-y-auto flex-1",
                    ),
                    html.Div(
                        [
                            html.Button(
                                "🕒 Tạm hoãn cảnh báo",
                                id="btn-m2-drawer-snooze",
                                n_clicks=0,
                                className="px-3 py-2 rounded-lg text-xs font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-100 cursor-pointer",
                            ),
                            html.Button(
                                "Chuyển xử lý →",
                                id="btn-m2-drawer-primary",
                                n_clicks=0,
                                className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-slate-900 hover:bg-slate-800 shadow-sm transition cursor-pointer",
                            ),
                        ],
                        className="p-4 border-t border-slate-200 bg-slate-50 flex items-center justify-between gap-2",
                    ),
                ],
            ),
            # Snooze Modal
            html.Div(
                id="snoozeModal",
                style={"display": "none"},
                className="fixed inset-0 bg-slate-900/60 z-50 items-center justify-center p-4 flex",
                children=html.Div(
                    className="bg-white rounded-2xl max-w-md w-full p-5 shadow-2xl border border-slate-200 space-y-4",
                    children=[
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H3("⏰ Tạm hoãn cảnh báo tồn kho", className="text-sm font-bold text-slate-900"),
                                        html.P("TV-LG-55C3", id="snoozeTargetTitle", className="text-xs font-semibold text-blue-700 mt-0.5 font-code"),
                                    ]
                                ),
                                html.Button("✕", id="btn-close-snooze-modal", n_clicks=0, className="text-slate-400 hover:text-slate-700 cursor-pointer"),
                            ],
                            className="flex items-start justify-between border-b border-slate-100 pb-3",
                        ),
                        html.Div(
                            [
                                html.Label("Thời hạn tạm hoãn:", className="block text-xs font-semibold text-slate-700 mb-1.5"),
                                dcc.RadioItems(
                                    id="m2-snooze-days",
                                    options=[
                                        {"label": " 7 ngày", "value": 7},
                                        {"label": " 14 ngày (Khuyên dùng)", "value": 14},
                                        {"label": " 30 ngày", "value": 30},
                                    ],
                                    value=14,
                                    inline=True,
                                    className="flex gap-4 text-xs text-slate-800",
                                ),
                                html.Label("Lý do tạm hoãn bắt buộc (tối thiểu 10 ký tự):", className="block text-xs font-semibold text-slate-700 mt-3 mb-1.5"),
                                dcc.Textarea(
                                    id="m2-snooze-reason",
                                    placeholder="Ví dụ: Đang giữ máy mẫu trưng bày phục vụ sự kiện cuối tuần...",
                                    value="",
                                    className="w-full h-20 p-2.5 text-xs rounded-xl border border-slate-300 focus:outline-none focus:border-slate-900",
                                ),
                                html.Div(id="m2-snooze-error", className="text-xs font-semibold text-rose-600 mt-1"),
                            ]
                        ),
                        html.Div(
                            [
                                html.Button("Hủy bỏ", id="btn-cancel-snooze-modal", n_clicks=0, className="px-3.5 py-1.5 rounded-lg border border-slate-200 text-xs font-medium text-slate-600 hover:bg-slate-50 cursor-pointer"),
                                html.Button("Xác nhận Tạm hoãn", id="btn-confirm-m2-snooze", n_clicks=0, className="px-4 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold cursor-pointer"),
                            ],
                            className="flex justify-end gap-2 pt-2 border-t border-slate-100",
                        ),
                    ],
                ),
            ),
            # Threshold Modal
            html.Div(
                id="m2ThresholdModal",
                style={"display": "none"},
                className="fixed inset-0 bg-slate-900/40 z-50 items-center justify-center p-4 flex",
                children=html.Div(
                    className="bg-white rounded-2xl max-w-md w-full p-5 shadow-xl border border-slate-200 space-y-4",
                    children=[
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H3("Cấu hình Ngưỡng cảnh báo kho", className="text-sm font-bold text-slate-900"),
                                        html.P("Áp dụng cho hệ thống phát hiện sắp hết hàng & tồn lâu", className="text-xs text-slate-500"),
                                    ]
                                ),
                                html.Button("✕", id="btn-close-m2-threshold", n_clicks=0, className="text-slate-400 hover:text-slate-600 cursor-pointer"),
                            ],
                            className="flex items-center justify-between border-b border-slate-100 pb-3",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span("Thời gian hãng giao mặc định:", className="font-medium text-slate-700"),
                                        dcc.Input(
                                            id="m2LeadTimeInput",
                                            type="number",
                                            value=4,
                                            min=1,
                                            max=15,
                                            className="w-20 px-2.5 py-1 rounded border border-slate-300 text-right font-semibold font-code",
                                        ),
                                    ],
                                    className="flex items-center justify-between py-1.5",
                                ),
                                html.Div(
                                    [
                                        html.Span("Đệm an toàn cảnh báo sớm Cấp 3:", className="font-medium text-slate-700"),
                                        html.Span("+3 ngày (Mặc định)", className="px-2.5 py-1 rounded bg-slate-100 font-semibold text-slate-800"),
                                    ],
                                    className="flex items-center justify-between py-1.5",
                                ),
                                html.Div(
                                    [
                                        html.Strong("Quy tắc hàng mới nhập: "),
                                        "Sản phẩm mới nhập dưới 7 ngày chưa đủ lịch sử bán dùng tốc độ bán trung bình ngành và gắn nhãn Dự báo theo ngành.",
                                    ],
                                    className="p-3 rounded-lg bg-blue-50 text-blue-900 border border-blue-200/80 leading-relaxed",
                                ),
                            ],
                            className="space-y-3 text-xs",
                        ),
                        html.Div(
                            [
                                html.Button("Đóng", id="btn-cancel-m2-threshold", n_clicks=0, className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:bg-slate-100 cursor-pointer"),
                                html.Button("Lưu cấu hình", id="btn-save-m2-threshold", n_clicks=0, className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 text-white hover:bg-slate-800 cursor-pointer"),
                            ],
                            className="flex justify-end gap-2 pt-2 border-t border-slate-100",
                        ),
                    ],
                ),
            ),
        ]
    )


def build_m2_panel(services: Dict[str, Any], active: bool = False, role: str = "ROLE_OWNER") -> html.Main:
    """Dựng màn hình chính Module 02 (Parity V2)."""
    from src.dash_app.callbacks.m2_callbacks import render_m2_workspace

    init_ws = render_m2_workspace(services, filter_key="all", search="", role=role)

    pills_spec = [
        ("all", "Tất cả", None, init_ws["counts"]["all"]),
        ("stagnant", "Tổng vốn kẹt", "bg-amber-500", init_ws["counts"]["stagnant"]),
        ("dead", "Tồn chết 0 đơn", "bg-slate-600", init_ws["counts"]["dead"]),
        ("seasonal", "Trái mùa & Vượt trần", "bg-amber-500", init_ws["counts"]["seasonal"]),
        ("stockout", "Cần nhập gấp", "bg-rose-600", init_ws["counts"]["stockout"]),
        ("incoming", "Hàng đang về", "bg-blue-600", init_ws["counts"]["incoming"]),
    ]

    pill_btns: List[Any] = []
    for k, lbl, dot, cnt in pills_spec:
        ch: List[Any] = []
        if dot:
            ch.append(html.Span(className=f"w-1.5 h-1.5 rounded-full {dot}"))
        ch.extend([lbl, html.Span(str(cnt), id=f"m2-pill-cnt-{k}", className="px-1 rounded bg-slate-200 text-slate-700 font-semibold text-[10px] tabular-nums ml-0.5 font-code")])
        pill_btns.append(html.Button(ch, id=f"m2-pill-{k}", n_clicks=0, className=init_ws["pill_classes"][k]))

    brand_options = [{"label": "Hãng: Tất cả", "value": "ALL"}] + [{"label": b, "value": b} for b in init_ws["brands_list"]]
    cat_options = [{"label": "Ngành: Tất cả", "value": "ALL"}] + [{"label": c, "value": c} for c in init_ws["categories_list"]]
    pareto = init_ws["pareto"]

    return html.Main(
        id="panel-m2",
        style={"display": "flex" if active else "none"},
        className="tab-panel flex-1 min-w-0 bg-[#F8FAFC] overflow-y-auto custom-scrollbar px-5 py-4 flex-col gap-4",
        children=[
            dcc.Store(id="store-m2-filter", data="all"),
            dcc.Store(id="store-m2-lead-time", data=4),
            dcc.Store(id="store-m2-pareto", data=False),
            dcc.Download(id="m2-download-csv"),
            # 1. Header 1 dòng gọn gàng
            html.Header(
                [
                    html.Div(
                        [
                            html.Span(className="w-2.5 h-2.5 rounded-full bg-rose-600 pulse-red-dot"),
                            html.H1("Cần xử lý hôm nay", className="text-xl font-bold tracking-tight text-slate-900"),
                            html.Span(f"{init_ws['counts']['all']} CẢNH BÁO", id="m2HeaderAlertCountBadge", className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-600 text-white tracking-wide"),
                            html.Span("Mốc đối soát 04/11/2026", className="px-2.5 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200/80"),
                            html.Span(
                                ["Thời gian hãng giao: ", html.Strong("4 ngày", id="m2LeadTimeDisplay", className="font-semibold text-slate-900")],
                                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200/80",
                            ),
                        ],
                        className="flex items-center gap-2.5",
                    ),
                    html.Div(
                        [
                            html.Button(
                                [html.I(className="ph-bold ph-download-simple text-slate-500"), "Xuất CSV"],
                                id="btn-m2-export-csv",
                                n_clicks=0,
                                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 shadow-2xs transition cursor-pointer",
                            ),
                            html.Button(
                                [html.I(className="ph-bold ph-sliders text-slate-500"), "Ngưỡng cảnh báo"],
                                id="btn-open-m2-threshold",
                                n_clicks=0,
                                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 shadow-2xs transition cursor-pointer",
                            ),
                        ],
                        className="flex items-center gap-2",
                    ),
                ],
                className="flex flex-wrap items-center justify-between gap-4 whitespace-nowrap shrink-0",
            ),
            # 2. 4 Thẻ KPI tối giản thuần Việt
            html.Section(init_ws["kpi_cards"], id="m2-kpi-section", className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3.5 shrink-0"),
            # 3. Pie Chart Phân bổ Vốn kẹt dải Vàng-Cam-Đỏ-Nâu đỏ + Khối Tóm tắt Pareto 80/20 (Đã bỏ Runway Chart)
            html.Section(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H2("Phân bổ vốn kẹt theo mặt hàng bán chậm", className="text-xs font-bold uppercase tracking-wider text-slate-700"),
                                            html.P("Di chuột lên từng lát cắt để xem tên hàng, mã sản phẩm, lượng vốn kẹt và số lượng tồn", className="text-[11px] text-slate-500 mt-0.5"),
                                        ]
                                    ),
                                    html.Span("Dải cảnh báo khẩn cấp", className="px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200 text-[10px] font-bold whitespace-nowrap"),
                                ],
                                className="flex items-start justify-between gap-2 px-4 pt-3.5 pb-1",
                            ),
                            dcc.Graph(id="m2-capital-chart", figure=init_ws.get("capital_fig", empty_figure()), config={"displayModeBar": False}, className="px-2 pb-2"),
                        ],
                        className="xl:col-span-8 bg-white rounded-xl border border-slate-200/90 shadow-2xs overflow-hidden",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("TRỌNG TÂM THU HỒI VỐN 80/20", className="text-[11px] font-bold uppercase tracking-wider text-amber-800"),
                                    html.P(
                                        [
                                            f"2 mặt hàng bán chậm đứng đầu ({pareto['brands']}) đang chiếm ",
                                            html.Strong(f"{pareto['pct']:.1f}%", className="text-rose-700 font-code"),
                                            f" tổng vốn kẹt ({pareto['capital_str']}).",
                                        ],
                                        className="text-xs text-slate-700 mt-1.5 leading-relaxed",
                                    ),
                                ],
                                className="p-3.5 rounded-xl bg-amber-50/70 border border-amber-200/80",
                            ),
                            html.Div(
                                [
                                    html.Div("Ý nghĩa dải màu khẩn cấp:", className="text-[11px] font-bold text-slate-700 mb-2"),
                                    html.Div([html.Span(className="w-2.5 h-2.5 rounded-sm bg-[#7F1D1D] shrink-0"), html.Span("Nâu đỏ / Đỏ đậm: Đọng vốn lớn nhất hoặc tồn > 60 ngày 0 đơn")], className="flex items-center gap-2 text-[11px] text-slate-600 mb-1"),
                                    html.Div([html.Span(className="w-2.5 h-2.5 rounded-sm bg-[#EA580C] shrink-0"), html.Span("Cam đậm: Vượt trần kệ hoặc sắp hết mùa vụ")], className="flex items-center gap-2 text-[11px] text-slate-600 mb-1"),
                                    html.Div([html.Span(className="w-2.5 h-2.5 rounded-sm bg-[#F59E0B] shrink-0"), html.Span("Vàng hổ phách: Nhóm chậm nhẹ cần theo dõi thêm")], className="flex items-center gap-2 text-[11px] text-slate-600"),
                                ],
                                className="p-3 rounded-xl bg-slate-50 border border-slate-200/70",
                            ),
                            html.Button(
                                f"⚡ Lọc nhanh 2 mã kẹt vốn lớn nhất ({pareto['pct']:.1f}%)",
                                id="btn-m2-pareto-card",
                                n_clicks=0,
                                className="w-full py-2 px-3 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold transition cursor-pointer",
                            ),
                        ],
                        className="xl:col-span-4 bg-white rounded-xl border border-slate-200/90 shadow-2xs p-4 flex flex-col justify-between gap-3",
                    ),
                ],
                className="grid grid-cols-1 xl:grid-cols-12 gap-4 shrink-0",
            ),
            # 4. Thanh Bộ lọc 1 dòng chuẩn Ảnh 1 + Bảng 7 cột có trượt ngang trong ô (.cell-hscroll)
            html.Section(
                [
                    html.Div(
                        [
                            html.Div(pill_btns, className="flex items-center gap-1.5 flex-wrap"),
                            html.Div(
                                [
                                    dcc.Input(
                                        id="m2-search-input",
                                        type="text",
                                        debounce=True,
                                        value="",
                                        placeholder="Tìm tên, mã hàng...",
                                        className="px-3 py-1 rounded-lg border border-slate-200 bg-slate-50 text-xs w-40 focus:outline-none focus:bg-white",
                                    ),
                                    dcc.Dropdown(
                                        id="m2BrandSelect",
                                        options=brand_options,
                                        value="ALL",
                                        clearable=False,
                                        searchable=False,
                                        className="text-xs w-32",
                                    ),
                                    dcc.Dropdown(
                                        id="m2CategorySelect",
                                        options=cat_options,
                                        value="ALL",
                                        clearable=False,
                                        searchable=False,
                                        className="text-xs w-36",
                                    ),
                                    dcc.Dropdown(
                                        id="m2SortSelect",
                                        options=[
                                            {"label": "Xếp: Khẩn cấp", "value": "urgent"},
                                            {"label": "Xếp: Vốn kẹt lớn", "value": "capital"},
                                            {"label": "Xếp: Đường băng ngắn", "value": "runway"},
                                        ],
                                        value="urgent",
                                        clearable=False,
                                        searchable=False,
                                        className="text-xs w-40",
                                    ),
                                    html.Button(
                                        "Khôi phục mục đã hoãn",
                                        id="btn-m2-restore-snoozed",
                                        n_clicks=0,
                                        className="px-2.5 py-1 rounded-lg border border-slate-200 text-[11px] font-medium text-slate-600 hover:bg-slate-100 cursor-pointer whitespace-nowrap",
                                    ),
                                ],
                                className="flex items-center gap-2 flex-wrap shrink-0",
                            ),
                        ],
                        className="border-b border-slate-200/80 px-3.5 py-2.5 flex flex-wrap items-center justify-between gap-2",
                    ),
                    html.Div(
                        html.Table(
                            [
                                html.Thead(
                                    html.Tr(
                                        [
                                            html.Th("☐", className="py-2.5 pl-3.5 pr-1.5 text-center text-slate-400 w-9"),
                                            html.Th("SẢN PHẨM & VỊ TRÍ KỆ", className="py-2.5 px-3 min-w-[230px]"),
                                            html.Th("TỒN THỰC / ĐỊNH MỨC", className="py-2.5 px-3 min-w-[165px]"),
                                            html.Th("ĐƯỜNG BĂNG & TỐC ĐỘ BÁN", className="py-2.5 px-3 min-w-[205px]"),
                                            html.Th("VỐN ĐỌNG / RỦI RO", className="py-2.5 px-3 min-w-[140px]"),
                                            html.Th("NGUYÊN NHÂN CỐT LÕI", className="py-2.5 px-3 min-w-[215px]"),
                                            html.Th("HÀNH ĐỘNG QUYẾT ĐỊNH", className="py-2.5 px-3 text-right min-w-[175px]"),
                                        ],
                                        className="bg-slate-50/80 border-b border-slate-200 text-[11px] font-semibold uppercase tracking-wider text-slate-500",
                                    )
                                ),
                                html.Tbody(init_ws["table_rows"], id="m2-alerts-table-body", className="divide-y divide-slate-200/60 text-xs"),
                            ],
                            className="w-full text-left border-collapse",
                        ),
                        className="overflow-x-auto",
                    ),
                    # Footer legend & 80/20 pill chuẩn Ảnh 1
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("Đường băng:", className="font-semibold text-slate-600"),
                                    html.Span([html.Span(className="w-2 h-2 rounded-xs bg-rose-600 inline-block mr-1"), "Đứt / Sắp cháy"], className="inline-flex items-center"),
                                    html.Span([html.Span(className="w-2 h-2 rounded-xs bg-slate-700 inline-block mr-1"), "Đóng băng (0 đơn)"], className="inline-flex items-center"),
                                    html.Span([html.Span(className="w-2 h-2 rounded-xs bg-amber-500 inline-block mr-1"), "Chậm / Trái mùa"], className="inline-flex items-center"),
                                    html.Span([html.Span(className="w-2 h-2 rounded-xs bg-blue-600 inline-block mr-1"), "Xe đang về"], className="inline-flex items-center"),
                                ],
                                className="flex items-center flex-wrap gap-3.5 text-[11px] text-slate-500",
                            ),
                            html.Div(
                                [
                                    html.Span(f"💡 80/20: 2 mã đầu ({pareto['brands']}) chiếm {pareto['pct']:.1f}% vốn kẹt ({pareto['capital_str']})", className="text-[11px] font-medium text-amber-900"),
                                    html.Span(" — "),
                                    html.Button("Lọc ngay", id="btn-m2-pareto-filter", n_clicks=0, className="text-[11px] font-bold text-amber-900 underline hover:text-amber-700 cursor-pointer"),
                                ],
                                className="px-3 py-1 rounded-full bg-amber-50 border border-amber-200/80 whitespace-nowrap",
                            ),
                        ],
                        className="px-4 py-2.5 bg-slate-50/70 border-t border-slate-200/60 flex flex-wrap items-center justify-between gap-2",
                    ),
                ],
                className="bg-white border border-slate-200/90 rounded-xl shadow-2xs overflow-hidden shrink-0 flex flex-col",
            ),
        ],
    )
