"""
Giao diện Dash cho Phân hệ 06: Hiệu quả kinh doanh, Thác nước Lợi nhuận, Attach-Rate & Hoa hồng (Prototype L2097–L2584).
"""
from dash import dcc, html


def build_m6_panel(is_active: bool = False) -> html.Main:
    """Xây dựng Panel M6 (Header kỳ đánh giá, 4 KPI Cards, Waterfall 6:6, Attach-Rate & Hoa hồng)."""
    return html.Main(
        id="panel-m6",
        style={"display": "flex" if is_active else "none"},
        className="tab-panel flex-1 min-w-0 bg-[#F8FAFC] overflow-y-auto custom-scrollbar px-5 py-4 flex-col gap-4",
        children=[
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
                                        className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-200/80 text-slate-700",
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
                                                {"label": "Tháng 10–11/2026 (Thực tế SQLite)", "value": "T10_11"},
                                                {"label": "Kỳ so sánh Tháng 09/2026", "value": "T09"},
                                            ],
                                            className="w-56 text-xs font-semibold",
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
                                    html.Div(html.Span("0 đ", id="m6KpiRev", className="text-2xl font-bold tracking-tight text-slate-900 tabular-nums"), className="my-1"),
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
                                    html.Div(html.Span("0 đ", id="m6KpiProfit", className="text-2xl font-bold tracking-tight text-emerald-600 tabular-nums cost-val"), className="my-1"),
                                    html.Div("Biên lãi gộp tổng: ...", id="m6KpiProfitSub", className="text-xs text-slate-500 pt-2 mt-1 border-t border-slate-100 leading-snug tabular-nums"),
                                ],
                            ),
                            html.Div(
                                className="kpi-card bg-white rounded-xl p-4 min-h-[138px] border border-slate-200/90 shadow-2xs flex flex-col justify-between min-w-0",
                                children=[
                                    html.Div(
                                        [
                                            html.Span([html.Span(className="w-2 h-2 rounded-full bg-amber-500 shrink-0"), html.Span("DOANH SỐ BÁN KÈM (PK + DỊCH VỤ)")], className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500"),
                                            html.Span("Động lực tạo lãi", className="shrink-0 px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-50 text-amber-800 border border-amber-200/70"),
                                        ],
                                        className="flex items-start justify-between gap-2 mb-1.5",
                                    ),
                                    html.Div(html.Span("0 đ", id="m6KpiAttachRev", className="text-2xl font-bold tracking-tight text-slate-900 tabular-nums"), className="my-1"),
                                    html.Div("Đóng góp lợi nhuận từ PK + DV", id="m6KpiAttachSub", className="text-xs text-slate-500 pt-2 mt-1 border-t border-slate-100 leading-snug tabular-nums"),
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
                                            html.Span("0%", id="m6KpiAttachRate", className="text-2xl font-bold tracking-tight text-blue-600 tabular-nums"),
                                            html.Span("(0 / 0 hóa đơn)", id="m6KpiAttachOrders", className="text-xs text-slate-400"),
                                        ],
                                        className="flex items-baseline flex-wrap gap-x-2 gap-y-0.5 my-1",
                                    ),
                                    html.Div("Loại trừ đơn mua lẻ phụ kiện (ERR_PRF_002)", className="text-xs text-slate-500 pt-2 mt-1 border-t border-slate-100 leading-snug"),
                                ],
                            ),
                        ],
                    ),
                    # 3. TẦNG GIỮA (6 : 6): WATERFALL LỢI NHUẬN + ATTACH RATE & CHI TIẾT NGÀNH HÀNG
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
                            # RIGHT 6: ATTACH-RATE CHART & CATEGORY TABLE
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
                                                            html.P("So sánh Attach-Rate với Chuẩn ngành (60%) và Mục tiêu Q4 (70%)", className="text-xs text-slate-500 mt-0.5"),
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
                                                                        html.Th("TỶ LỆ GẮN KÈM", className="py-2 px-2"),
                                                                        html.Th("DOANH SỐ PK+DV", className="py-2 px-2 text-right"),
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
                    # 4. TẦNG DƯỚI: XẾP HẠNG HIỆU SUẤT & HOA HỒNG BÁN KÈM
                    html.Section(
                        className="bg-white rounded-xl border border-slate-200/90 shadow-2xs p-5",
                        children=[
                            html.Div(
                                className="flex flex-wrap items-center justify-between gap-3 mb-4",
                                children=[
                                    html.Div(
                                        [
                                            html.H2("Xếp hạng Hiệu suất & Hoa hồng Bán kèm", className="text-sm font-bold text-slate-900"),
                                            html.P("Chính sách thưởng minh bạch: PK 15% + DV Lắp đặt 20% · Duyệt chi chỉ dành cho Quản lý", className="text-xs text-slate-500 mt-0.5"),
                                        ]
                                    ),
                                    html.Div(
                                        className="flex flex-wrap items-center gap-2.5",
                                        children=[
                                            html.Span("QUỸ CHI: 0 đ", id="m6StaffFundBadge", className="px-3 py-1.5 rounded-lg text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200/80 tabular-nums"),
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
                            html.Div(id="m6StaffCommissionCards", className="grid grid-cols-1 lg:grid-cols-3 gap-4 text-xs"),
                        ],
                    ),
        ],
    )
