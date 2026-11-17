"""
Giao diện Dash cho Phân hệ 06 (Parity V2): Hiệu quả kinh doanh, Thác nước Lợi nhuận,
Tỷ lệ bán kèm & Tùy chỉnh Chính sách Thưởng nhân viên trực tiếp.
"""
from dash import dcc, html


def build_m6_panel(is_active: bool = False) -> html.Main:
    """Xây dựng Panel M6 V2 (Header, 4 KPI Cards, Waterfall 6:6, Bảng ngành & Chính sách thưởng)."""
    return html.Main(
        id="panel-m6",
        style={"display": "flex" if is_active else "none"},
        className="tab-panel flex-1 min-w-0 bg-[#F8FAFC] overflow-y-auto custom-scrollbar px-5 py-4 flex-col gap-4",
        children=[
            dcc.Store(
                id="store-m6-policy",
                data={"acc_rate_pct": 15.0, "srv_rate_pct": 20.0, "hot_bonus_per_case": 50_000.0, "sort_by": "commission"},
            ),
            dcc.Store(id="store-m6-refresh", data=0),
            dcc.Download(id="m6-download-csv"),
            # 1. HEADER BAR
            html.Header(
                className="flex flex-wrap items-center justify-between gap-3",
                children=[
                    html.Div(
                        className="flex flex-wrap items-center gap-2.5",
                        children=[
                            html.Span(className="w-2.5 h-2.5 rounded-full bg-emerald-600 shrink-0"),
                            html.H1("Hiệu quả kinh doanh & Thác nước Lợi nhuận", className="text-lg xl:text-xl font-bold tracking-tight text-slate-900"),
                            html.Span(
                                "0 hóa đơn thực tế",
                                id="m6HeaderInvoiceBadge",
                                className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-200/80 text-slate-700 font-code",
                            ),
                        ],
                    ),
                    html.Div(
                        className="flex flex-wrap items-center gap-2",
                        children=[
                            html.Div(
                                dcc.Dropdown(
                                    id="m6PeriodSelect",
                                    clearable=False,
                                    value="T10_11",
                                    options=[
                                        {"label": "Tháng 10–11/2026 (Dữ liệu thực tế)", "value": "T10_11"},
                                        {"label": "Kỳ so sánh Tháng 09/2026", "value": "T09"},
                                    ],
                                    className="w-60 text-xs font-semibold",
                                )
                            ),
                            html.Span("Kho 108 Cầu Giấy", className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200/80"),
                            html.Button(
                                "📥 Xuất Excel (.CSV)",
                                id="m6ExportCsvBtn",
                                n_clicks=0,
                                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 shadow-2xs transition cursor-pointer",
                            ),
                        ],
                    ),
                ],
            ),
            # 2. 4 KPI CARDS CHUẨN 3 DÒNG
            html.Section(
                className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3.5",
                children=[
                    html.Div(
                        className="kpi-card bg-white rounded-xl p-4 min-h-[138px] border border-slate-200/90 shadow-2xs flex flex-col justify-between min-w-0",
                        children=[
                            html.Div(
                                [
                                    html.Span([html.Span(className="w-2 h-2 rounded-full bg-slate-700 shrink-0"), html.Span("TỔNG DOANH THU & THU HỒI VỐN")], className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500"),
                                    html.Span("Bảo toàn dòng tiền", className="shrink-0 px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-700 border border-slate-200"),
                                ],
                                className="flex items-start justify-between gap-2 mb-1.5",
                            ),
                            html.Div(html.Span("0 đ", id="m6KpiRev", className="text-2xl font-bold tracking-tight text-slate-900 font-code"), className="my-1"),
                            html.Div("Vốn gốc quay về két: ...", id="m6KpiRevSub", className="text-xs text-slate-500 pt-2 mt-1 border-t border-slate-100 leading-snug tabular-nums"),
                        ],
                    ),
                    html.Div(
                        className="kpi-card bg-white rounded-xl p-4 min-h-[138px] border border-slate-200/90 shadow-2xs flex flex-col justify-between min-w-0",
                        children=[
                            html.Div(
                                [
                                    html.Span([html.Span(className="w-2 h-2 rounded-full bg-emerald-600 shrink-0"), html.Span("LỢI NHUẬN GỘP HỢP NHẤT")], className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500"),
                                    html.Span("Lãi ròng tối ưu", className="shrink-0 px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/70"),
                                ],
                                className="flex items-start justify-between gap-2 mb-1.5",
                            ),
                            html.Div(html.Span("0 đ", id="m6KpiProfit", className="text-2xl font-bold tracking-tight text-emerald-600 font-code cost-val"), className="my-1"),
                            html.Div("Biên lãi gộp tổng: ...", id="m6KpiProfitSub", className="text-xs text-slate-500 pt-2 mt-1 border-t border-slate-100 leading-snug tabular-nums"),
                        ],
                    ),
                    html.Div(
                        className="kpi-card bg-white rounded-xl p-4 min-h-[138px] border border-slate-200/90 shadow-2xs flex flex-col justify-between min-w-0",
                        children=[
                            html.Div(
                                [
                                    html.Span([html.Span(className="w-2 h-2 rounded-full bg-amber-500 shrink-0"), html.Span("DOANH SỐ PHỤ KIỆN & DỊCH VỤ")], className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500"),
                                    html.Span("Động lực tạo lãi", className="shrink-0 px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-50 text-amber-800 border border-amber-200/70"),
                                ],
                                className="flex items-start justify-between gap-2 mb-1.5",
                            ),
                            html.Div(html.Span("0 đ", id="m6KpiAttachRev", className="text-2xl font-bold tracking-tight text-slate-900 font-code"), className="my-1"),
                            html.Div("Đóng góp lợi nhuận từ Phụ kiện & Dịch vụ", id="m6KpiAttachSub", className="text-xs text-slate-500 pt-2 mt-1 border-t border-slate-100 leading-snug tabular-nums"),
                        ],
                    ),
                    html.Div(
                        className="kpi-card bg-white rounded-xl p-4 min-h-[138px] border border-slate-200/90 shadow-2xs flex flex-col justify-between min-w-0",
                        children=[
                            html.Div(
                                [
                                    html.Span([html.Span(className="w-2 h-2 rounded-full bg-blue-600 shrink-0"), html.Span("TỶ LỆ BÁN KÈM TRUNG BÌNH")], className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500"),
                                    html.Span("Chuẩn 60%", id="m6KpiTargetBadge", className="shrink-0 px-2 py-0.5 rounded text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200/70"),
                                ],
                                className="flex items-start justify-between gap-2 mb-1.5",
                            ),
                            html.Div(
                                [
                                    html.Span("0%", id="m6KpiAttachRate", className="text-2xl font-bold tracking-tight text-blue-600 font-code"),
                                    html.Span("(0 / 0 hóa đơn)", id="m6KpiAttachOrders", className="text-xs text-slate-400"),
                                ],
                                className="flex items-baseline flex-wrap gap-x-2 gap-y-0.5 my-1",
                            ),
                            html.Div("Chỉ tính trên hóa đơn bán máy chính (loại trừ mua lẻ phụ kiện)", className="text-xs text-slate-500 pt-2 mt-1 border-t border-slate-100 leading-snug"),
                        ],
                    ),
                ],
            ),
            # 3. TẦNG GIỮA (6 : 6): WATERFALL LỢI NHUẬN + TỶ LỆ BÁN KÈM & CHI TIẾT NGÀNH HÀNG
            html.Section(
                className="grid grid-cols-1 xl:grid-cols-12 gap-4 items-stretch",
                children=[
                    # LEFT 6: WATERFALL
                    html.Div(
                        className="xl:col-span-6 bg-white rounded-xl border border-slate-200/90 shadow-2xs p-5 flex flex-col justify-between",
                        children=[
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.H2("Biểu đồ Thác nước Phân rã Nguồn Lợi nhuận Gộp", className="text-sm font-bold text-slate-900"),
                                                    html.P("Phân rã đóng góp lãi gộp từ Thiết bị chính, Phụ kiện, Công lắp đặt và Khuyến mại", className="text-xs text-slate-500 mt-0.5"),
                                                ]
                                            ),
                                            html.Span("Đơn vị: Triệu đồng (tr đ)", className="px-2.5 py-1 rounded-md text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200/70 shrink-0"),
                                        ],
                                        className="flex flex-wrap items-start justify-between gap-2 mb-3",
                                    ),
                                    dcc.Graph(id="m6WaterfallChart", config={"displayModeBar": False}, style={"height": "280px"}),
                                ]
                            ),
                            html.Div(
                                id="m6WaterfallInsight",
                                className="mt-4 p-3.5 rounded-xl bg-emerald-50/80 border border-emerald-200/80 flex items-start gap-2.5 text-xs text-emerald-950",
                                children=[
                                    html.Span("💡", className="text-base leading-none mt-0.5"),
                                    html.P("Phụ kiện & Dịch vụ lắp đặt đang đóng góp tỷ trọng lớn vào tổng lợi nhuận gộp.", id="m6InsightText", className="leading-relaxed"),
                                ],
                            ),
                        ],
                    ),
                    # RIGHT 6: TỶ LỆ BÁN KÈM THEO NGÀNH HÀNG
                    html.Div(
                        className="xl:col-span-6 bg-white rounded-xl border border-slate-200/90 shadow-2xs p-5 flex flex-col justify-between",
                        children=[
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.H2("Tỷ lệ & Chi tiết Hiệu quả Bán kèm theo Ngành hàng", className="text-sm font-bold text-slate-900"),
                                                    html.P("So sánh tỷ lệ bán kèm thực tế với Chuẩn ngành (60%) và Mục tiêu quý (70%)", className="text-xs text-slate-500 mt-0.5"),
                                                ]
                                            ),
                                            html.Div(
                                                [
                                                    html.Span("Chuẩn: 60%", className="px-2 py-0.5 rounded bg-rose-50 text-rose-700 font-semibold"),
                                                    html.Span("Mục tiêu: 70%", className="px-2 py-0.5 rounded bg-slate-100 text-slate-800 font-semibold"),
                                                ],
                                                className="flex items-center gap-2 text-[11px] shrink-0",
                                            ),
                                        ],
                                        className="flex flex-wrap items-start justify-between gap-2 mb-3",
                                    ),
                                    dcc.Graph(id="m6AttachRateChart", config={"displayModeBar": False}, style={"height": "190px"}),
                                    html.Div(
                                        className="overflow-x-auto mt-3",
                                        children=[
                                            html.Table(
                                                className="w-full border-collapse text-left text-xs",
                                                children=[
                                                    html.Thead(
                                                        html.Tr(
                                                            [
                                                                html.Th("NGÀNH HÀNG", className="py-2 pr-2"),
                                                                html.Th("TỶ LỆ BÁN KÈM", className="py-2 px-2"),
                                                                html.Th("DOANH SỐ BÁN KÈM", className="py-2 px-2 text-right"),
                                                                html.Th("ĐÁNH GIÁ", className="py-2 pl-2 text-right"),
                                                            ],
                                                            className="border-b border-slate-200 text-[11px] font-bold uppercase tracking-wider text-slate-400",
                                                        )
                                                    ),
                                                    html.Tbody(id="m6CategoryTableBody", className="divide-y divide-slate-100 tabular-nums"),
                                                ],
                                            )
                                        ],
                                    ),
                                ]
                            ),
                        ],
                    ),
                ],
            ),
            # 4. TẦNG DƯỚI: TÙY CHỈNH CHÍNH SÁCH THƯỞNG & XẾP HẠNG HIỆU SUẤT NHÂN VIÊN
            html.Section(
                className="bg-white rounded-xl border border-slate-200/90 shadow-2xs p-5 space-y-4",
                children=[
                    html.Div(
                        className="flex flex-wrap items-center justify-between gap-3",
                        children=[
                            html.Div(
                                [
                                    html.H2("Xếp hạng Hiệu suất & Hoa hồng Bán kèm", className="text-sm font-bold text-slate-900"),
                                    html.P(
                                        "Chính sách hiện hành: Phụ kiện 15% + Dịch vụ 20% + Thưởng nóng 50k/ca · Duyệt chi chỉ dành cho Chủ cửa hàng",
                                        id="m6PolicySummaryText",
                                        className="text-xs text-slate-500 mt-0.5",
                                    ),
                                ]
                            ),
                            html.Div(
                                className="flex flex-wrap items-center gap-2.5",
                                children=[
                                    html.Span("QUỸ CHI: 0 đ", id="m6StaffFundBadge", className="px-3 py-1.5 rounded-lg text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200/80 font-code"),
                                    html.Button(
                                        "✓ Duyệt chi tất cả chờ duyệt",
                                        id="m6ApproveAllBonusBtn",
                                        n_clicks=0,
                                        className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-white shadow-2xs transition cursor-pointer",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Panel Điều chỉnh Chính sách Thưởng & Tiêu chí Xếp hạng trực tiếp
                    html.Div(
                        id="m6PolicyConfigPanel",
                        className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-3",
                        children=[
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.I(className="ph-bold ph-sliders-horizontal text-blue-600"),
                                            html.Span("ĐIỀU CHỈNH CHÍNH SÁCH THƯỞNG & XẾP HẠNG TRỰC TIẾP", className="text-[11px] font-bold uppercase tracking-wider text-slate-700"),
                                        ],
                                        className="flex items-center gap-1.5",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("Tổng quỹ dự kiến chi: ", className="text-xs text-slate-500"),
                                            html.Strong("0 đ", id="m6TotalBonusFundDisplay", className="text-sm font-extrabold text-blue-700 font-code cost-val"),
                                        ],
                                        className="flex items-center gap-1.5",
                                    ),
                                ],
                                className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-slate-200/80",
                            ),
                            html.Div(
                                className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-6 gap-2.5 items-end text-xs",
                                children=[
                                    html.Div(
                                        [
                                            html.Label("% Hoa hồng Phụ kiện (5–30%)", className="block text-[11px] font-semibold text-slate-600 mb-1"),
                                            dcc.Input(
                                                id="m6PolicyAccRateInput",
                                                type="number",
                                                min=5,
                                                max=30,
                                                step=1,
                                                value=15,
                                                className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white font-bold font-code text-slate-900",
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Label("% Hoa hồng Dịch vụ (5–35%)", className="block text-[11px] font-semibold text-slate-600 mb-1"),
                                            dcc.Input(
                                                id="m6PolicySrvRateInput",
                                                type="number",
                                                min=5,
                                                max=35,
                                                step=1,
                                                value=20,
                                                className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white font-bold font-code text-slate-900",
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Label("Thưởng nóng / ca chốt (đ)", className="block text-[11px] font-semibold text-slate-600 mb-1"),
                                            dcc.Input(
                                                id="m6PolicyHotBonusInput",
                                                type="number",
                                                min=0,
                                                max=200000,
                                                step=10000,
                                                value=50000,
                                                className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white font-bold font-code text-slate-900",
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        className="xl:col-span-2",
                                        children=[
                                            html.Label("Tiêu chí xếp hạng (#1–#3)", className="block text-[11px] font-semibold text-slate-600 mb-1"),
                                            dcc.Dropdown(
                                                id="m6PolicySortSelect",
                                                clearable=False,
                                                value="commission",
                                                options=[
                                                    {"label": "Theo tổng tiền thưởng", "value": "commission"},
                                                    {"label": "Theo doanh số bán kèm", "value": "attached_sales"},
                                                    {"label": "Theo lợi nhuận mang lại", "value": "attached_profit"},
                                                ],
                                                className="text-xs font-semibold",
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="flex items-center gap-1.5",
                                        children=[
                                            html.Button(
                                                "Áp dụng",
                                                id="btn-m6-apply-policy",
                                                n_clicks=0,
                                                className="flex-1 py-1.5 px-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold cursor-pointer whitespace-nowrap",
                                            ),
                                            html.Button(
                                                "Mặc định",
                                                id="btn-m6-reset-policy",
                                                n_clicks=0,
                                                className="py-1.5 px-2.5 rounded-lg bg-white hover:bg-slate-100 border border-slate-300 text-slate-700 text-xs font-semibold cursor-pointer whitespace-nowrap",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.Div(
                                "🔒 Chế độ Nhân viên bán hàng: Chỉ Chủ cửa hàng được chỉnh chính sách thưởng & xem tổng quỹ chi.",
                                id="m6PolicySalesLockNote",
                                style={"display": "none"},
                                className="text-[11px] font-semibold text-amber-800 bg-amber-50 border border-amber-200 rounded-lg px-3 py-1.5",
                            ),
                        ],
                    ),
                    html.Div(id="m6StaffCommissionCards", className="grid grid-cols-1 lg:grid-cols-3 gap-4 text-xs"),
                ],
            ),
        ],
    )
