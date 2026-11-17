"""
Giao diện Dash cho Phân hệ 04: Gợi ý nhập hàng & Cân đối ngân sách PO (Prototype L1296–L1709).
"""
from dash import dcc, html


def build_m4_panel(is_active: bool = False) -> html.Main:
    """Xây dựng Panel M4 (Gợi ý nhập hàng, Bảng điều phối +/-, Gom PO theo Hãng & Modals)."""
    return html.Main(
        id="panel-m4",
        style={"display": "flex" if is_active else "none"},
        className="tab-panel flex-1 min-w-0 bg-[#F8FAFC] overflow-y-auto custom-scrollbar px-5 py-4 flex-col gap-4",
        children=[
            dcc.Store(id="store-m4-cycle", data=14),
            dcc.Store(id="store-m4-budget", data=250_000_000.0),
            dcc.Store(id="store-m4-brand", data="ALL"),
            dcc.Store(id="store-m4-show-adequate", data=False),
            dcc.Store(id="store-m4-qty-overrides", data={}),
            dcc.Store(id="store-m4-autobalance", data=False),
            dcc.Store(id="store-m4-active-vendor", data=None),
            dcc.Store(id="store-m4-po-refresh", data=0),
            dcc.Download(id="m4-download-csv"),
            # 1. COMPACT HEADER BAR
            html.Header(
                        className="flex flex-wrap items-center justify-between gap-3",
                        children=[
                            html.Div(
                                className="flex flex-wrap items-center gap-2.5",
                                children=[
                                    html.Span(className="w-2.5 h-2.5 rounded-full bg-blue-600 animate-pulse shrink-0"),
                                    html.H1(
                                        "Gợi ý nhập hàng & Cân đối ngân sách",
                                        className="text-lg xl:text-xl font-bold tracking-tight text-slate-900",
                                    ),
                                    html.Span(
                                        "4 ĐƠN NHẬP ĐỀ XUẤT",
                                        id="m4HeaderOrderBadge",
                                        className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-600 text-white tracking-wide",
                                    ),
                                    html.Div(
                                        className="inline-flex items-center bg-slate-200/75 p-0.5 rounded-lg border border-slate-300/60 text-xs",
                                        children=[
                                            html.Button(
                                                "14 ngày tới",
                                                id="m4Cycle14Btn",
                                                n_clicks=0,
                                                className="px-2.5 py-1 rounded-md font-semibold bg-white text-slate-900 shadow-sm transition cursor-pointer",
                                            ),
                                            html.Button(
                                                "30 ngày tới",
                                                id="m4Cycle30Btn",
                                                n_clicks=0,
                                                className="px-2.5 py-1 rounded-md font-medium text-slate-600 hover:text-slate-900 transition cursor-pointer",
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="relative inline-flex items-center",
                                        children=[
                                            html.Button(
                                                id="m4BudgetToggleBtn",
                                                n_clicks=0,
                                                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium bg-white text-slate-700 border border-slate-200 hover:border-slate-300 shadow-2xs transition cursor-pointer",
                                                children=[
                                                    html.Span("Trần ngân sách:"),
                                                    html.Strong("250,0 tr", id="m4HeaderBudgetText", className="font-bold text-slate-900 tabular-nums"),
                                                    html.Span("✎", className="text-blue-600 font-semibold"),
                                                ],
                                            ),
                                            html.Div(
                                                id="m4BudgetDropdown",
                                                className="hidden absolute left-0 top-full mt-1.5 w-60 bg-white rounded-xl shadow-xl border border-slate-200 p-2.5 z-30",
                                                children=[
                                                    html.Div("Chọn nhanh hạn mức giải ngân", className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2 px-1"),
                                                    html.Div(
                                                        className="grid grid-cols-2 gap-1.5 text-xs mb-2",
                                                        children=[
                                                            html.Button("150,0 tr (Hẹp)", id="m4Budget150Btn", n_clicks=0, className="px-2.5 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 font-semibold text-slate-700 text-left cursor-pointer"),
                                                            html.Button("200,0 tr (Vừa)", id="m4Budget200Btn", n_clicks=0, className="px-2.5 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 font-semibold text-slate-700 text-left cursor-pointer"),
                                                            html.Button("250,0 tr (Chuẩn)", id="m4Budget250Btn", n_clicks=0, className="px-2.5 py-1.5 rounded-lg border border-blue-200 bg-blue-50/60 font-bold text-blue-700 text-left cursor-pointer"),
                                                            html.Button("350,0 tr (Rộng)", id="m4Budget350Btn", n_clicks=0, className="px-2.5 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 font-semibold text-slate-700 text-left cursor-pointer"),
                                                        ],
                                                    ),
                                                    html.Div(
                                                        className="flex items-center gap-1.5 pt-2 border-t border-slate-100",
                                                        children=[
                                                            dcc.Input(
                                                                id="m4CustomBudgetInput",
                                                                type="number",
                                                                value=250,
                                                                min=50,
                                                                max=1000,
                                                                step=10,
                                                                className="w-full px-2 py-1 text-xs rounded border border-slate-200 font-semibold tabular-nums",
                                                            ),
                                                            html.Button("Lưu", id="m4ApplyCustomBudgetBtn", n_clicks=0, className="px-2.5 py-1 rounded bg-slate-900 text-white text-xs font-semibold cursor-pointer"),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.Div(
                                className="flex flex-wrap items-center gap-2",
                                children=[
                                    html.Button(
                                        id="m4OpenPoLifecycleBtn",
                                        n_clicks=0,
                                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 transition cursor-pointer",
                                        children=[
                                            html.Span("📋"),
                                            html.Span(["PO đã phát hành (", html.Strong("2", id="m4IssuedPoCountBadge"), ")"]),
                                        ],
                                    ),
                                    html.Button(
                                        "↺ Khôi phục đề xuất",
                                        id="m4ResetQtyBtn",
                                        n_clicks=0,
                                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 shadow-2xs transition cursor-pointer",
                                    ),
                                    html.Button(
                                        [html.Span("⚖️"), html.Span(" Tự động cân đối ngân sách")],
                                        id="m4AutoBalanceBtn",
                                        n_clicks=0,
                                        className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 text-white hover:bg-slate-800 shadow-2xs transition cursor-pointer",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # 2. 4 KPI CARDS
                    html.Section(
                        className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3.5",
                        children=[
                            html.Div(
                                id="m4KpiCard1Btn",
                                n_clicks=0,
                                className="kpi-card cursor-pointer bg-white rounded-xl p-4 min-h-[148px] border border-slate-200/90 shadow-2xs select-none flex flex-col justify-between gap-2",
                                children=[
                                    html.Div(
                                        [
                                            html.Span(
                                                [html.Span(className="w-2 h-2 rounded-full bg-rose-600 shrink-0"), html.Span("MẶT HÀNG CẦN NHẬP BÙ")],
                                                className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500 leading-snug",
                                            ),
                                            html.Span("Nguy cơ thiếu hàng", className="px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200/60 shrink-0"),
                                        ],
                                        className="flex items-start justify-between gap-2",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("4 mã trọng yếu", id="m4KpiSkuCount", className="text-2xl font-bold tracking-tight text-slate-900 tabular-nums"),
                                            html.Span("", id="m4KpiBrandSpan", className="text-xs font-medium text-slate-400"),
                                        ],
                                        className="flex items-baseline flex-wrap gap-x-2 gap-y-0.5 my-0.5",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("Thiếu hàng trong 14 ngày tới nếu chưa đặt", id="m4KpiCycleNote", className="text-slate-400"),
                                            html.Span("+ Hiện mã đủ tồn", id="m4KpiToggleAquaText", className="font-semibold text-blue-600 hover:underline"),
                                        ],
                                        className="pt-2 border-t border-slate-100 flex flex-col gap-0.5 text-xs",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="kpi-card bg-white rounded-xl p-4 min-h-[148px] border border-slate-200/90 shadow-2xs select-none flex flex-col justify-between gap-2",
                                children=[
                                    html.Div(
                                        [
                                            html.Span(
                                                [html.Span(className="w-2 h-2 rounded-full bg-blue-600 shrink-0"), html.Span("TỔNG LƯỢNG NHẬP ĐỀ XUẤT")],
                                                className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500 leading-snug",
                                            ),
                                            html.Span("Đã làm tròn kiện", className="px-2 py-0.5 rounded text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200/60 shrink-0"),
                                        ],
                                        className="flex items-start justify-between gap-2",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("0 thiết bị", id="m4KpiTotalUnits", className="text-2xl font-bold tracking-tight text-slate-900 tabular-nums"),
                                            html.Span("", id="m4KpiOrderCountText", className="text-xs font-medium text-slate-400"),
                                        ],
                                        className="flex items-baseline flex-wrap gap-x-2 gap-y-0.5 my-0.5",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("Tự động quy chuẩn theo bộ đôi & lô hãng", className="text-slate-400"),
                                            html.Span("Chẵn lô 100%", className="font-semibold text-slate-700"),
                                        ],
                                        className="pt-2 border-t border-slate-100 flex flex-col gap-0.5 text-xs",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="kpi-card bg-white rounded-xl p-4 min-h-[148px] border border-slate-200/90 shadow-2xs select-none flex flex-col justify-between gap-1.5",
                                children=[
                                    html.Div(
                                        [
                                            html.Span(
                                                [html.Span(id="m4KpiBudgetDot", className="w-2 h-2 rounded-full bg-emerald-500 shrink-0"), html.Span("DỰ TOÁN VỐN NHẬP HÀNG")],
                                                className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500 leading-snug",
                                            ),
                                            html.Span("0% ngân sách", id="m4KpiBudgetBadge", className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/60 tabular-nums shrink-0"),
                                        ],
                                        className="flex items-start justify-between gap-2",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("0 đ", id="m4KpiTotalCost", className="text-2xl font-bold tracking-tight text-blue-600 tabular-nums cost-val"),
                                            html.Span("/ Trần 250,0 tr", id="m4KpiCapLabel", className="text-xs font-medium text-slate-400 tabular-nums"),
                                        ],
                                        className="flex items-baseline flex-wrap justify-between gap-x-2 gap-y-0.5",
                                    ),
                                    html.Div(
                                        html.Div(id="m4KpiBudgetBar", className="h-full bg-emerald-500 rounded-full transition-all duration-200", style={"width": "0%"}),
                                        className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("Còn dư: ...", id="m4KpiBudgetRemain", className="text-emerald-700 font-medium tabular-nums"),
                                            html.Span("Điều chỉnh trần ngân sách ở góc trên →", className="text-left font-semibold text-slate-600"),
                                        ],
                                        className="pt-1.5 border-t border-slate-100 flex flex-col gap-0.5 text-xs",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="kpi-card bg-white rounded-xl p-4 min-h-[148px] border border-slate-200/90 shadow-2xs select-none flex flex-col justify-between gap-2",
                                children=[
                                    html.Div(
                                        [
                                            html.Span(
                                                [html.Span(className="w-2 h-2 rounded-full bg-emerald-500 shrink-0"), html.Span("ƯU ĐÃI & TIẾT KIỆM TỪ HÃNG")],
                                                className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500 leading-snug",
                                            ),
                                            html.Span("Freeship", id="m4KpiFreeshipBadge", className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/60 shrink-0"),
                                        ],
                                        className="flex items-start justify-between gap-2",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("+0 đ", id="m4KpiSavingsVal", className="text-2xl font-bold tracking-tight text-emerald-600 tabular-nums cost-val"),
                                            html.Span("Chiết khấu trả sớm 1,5%", className="text-xs font-medium text-slate-400"),
                                        ],
                                        className="flex items-baseline flex-wrap gap-x-2 gap-y-0.5 my-0.5",
                                    ),
                                    html.Div(
                                        [
                                            html.Span(["Độ tin cậy dự báo trung bình: ", html.Strong("90%", id="m4KpiConfVal", className="text-slate-600 font-semibold")], className="text-slate-400"),
                                            html.Span("Miễn phí vận chuyển (>10 tr/đơn)", className="font-semibold text-emerald-700"),
                                        ],
                                        className="pt-2 border-t border-slate-100 flex flex-col gap-0.5 text-xs",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # 3. FILTER BAR
                    html.Section(
                        className="bg-white rounded-xl border border-slate-200/90 px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 shadow-2xs",
                        children=[
                            html.Div(id="m4BrandFilterContainer", className="flex flex-wrap items-center gap-1.5"),
                            html.Div(
                                className="flex flex-wrap items-center gap-2.5",
                                children=[
                                    html.Button(
                                        "Hiện cả mã đã đủ tồn",
                                        id="m4ToggleAdequateBtn",
                                        n_clicks=0,
                                        className="px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:bg-slate-100 border border-dashed border-slate-300 transition cursor-pointer",
                                    ),
                                    dcc.Input(
                                        id="m4SearchInput",
                                        type="text",
                                        value="",
                                        debounce=True,
                                        placeholder="Tìm tên máy, mã SKU...",
                                        className="px-3 py-1.5 w-52 rounded-lg text-xs bg-slate-50 border border-slate-200 focus:bg-white focus:outline-none",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # 4. CHARTS STRIP (2 BIỂU ĐỒ TRỰC QUAN DỰ BÁO NHU CẦU & NGÂN SÁCH THEO HÃNG)
                    html.Section(
                        className="grid grid-cols-1 lg:grid-cols-2 gap-4",
                        children=[
                            html.Div(
                                className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-2xs",
                                children=[
                                    html.Div("Nhu cầu an toàn vs Tồn khả dụng & Đang về", className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2"),
                                    dcc.Graph(id="m4DemandChart", config={"displayModeBar": False}, style={"height": "230px"}),
                                ],
                            ),
                            html.Div(
                                className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-2xs",
                                children=[
                                    html.Div("Phân bổ vốn đặt hàng theo Nhà phân phối", className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2"),
                                    dcc.Graph(id="m4BudgetChart", config={"displayModeBar": False}, style={"height": "230px"}),
                                ],
                            ),
                        ],
                    ),
                    # 5. MAIN 8:4 INTERACTIVE WORKSPACE
                    html.Section(
                        className="grid grid-cols-1 xl:grid-cols-12 gap-4 items-stretch",
                        children=[
                            # LEFT 8 COLS: REPLENISHMENT TABLE + PO STRIP
                            html.Div(
                                className="xl:col-span-8 bg-white border border-slate-200/90 rounded-xl shadow-2xs overflow-hidden flex flex-col justify-between",
                                children=[
                                    html.Div(
                                        [
                                            html.Div(
                                                className="px-4 py-3 border-b border-slate-200/80 flex flex-wrap items-center justify-between gap-2 bg-slate-50/50",
                                                children=[
                                                    html.Div(
                                                        [
                                                            html.H2("Bảng điều phối lượng nhập theo mặt hàng", className="text-sm font-bold text-slate-900"),
                                                            html.Span("Bấm [−] / [+] để chỉnh trực tiếp số lượng", className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-600 border border-slate-200"),
                                                        ],
                                                        className="flex flex-wrap items-center gap-2",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Span([html.Span(className="w-2.5 h-2 rounded-sm bg-emerald-500"), html.Span(" Khả dụng")], className="inline-flex items-center gap-1"),
                                                            html.Span([html.Span(className="w-2.5 h-2 rounded-sm bg-blue-600"), html.Span(" Đang về")], className="inline-flex items-center gap-1"),
                                                            html.Span([html.Span(className="w-2.5 h-2 rounded-sm bg-rose-300 border border-rose-400"), html.Span(" Khoảng thiếu")], className="inline-flex items-center gap-1"),
                                                        ],
                                                        className="flex flex-wrap items-center gap-3 text-[11px] text-slate-500",
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                className="overflow-x-auto",
                                                children=[
                                                    html.Table(
                                                        className="w-full border-collapse text-left",
                                                        children=[
                                                            html.Thead(
                                                                html.Tr(
                                                                    [
                                                                        html.Th("SẢN PHẨM & NHÀ PHÂN PHỐI", className="w-[30%] pl-4 pr-2 py-3"),
                                                                        html.Th("KHẢ DỤNG & ĐANG VỀ", className="w-[19%] px-2.5 py-3"),
                                                                        html.Th("NHU CẦU & KHOẢNG THIẾU", className="w-[21%] px-2.5 py-3"),
                                                                        html.Th("LƯỢNG NHẬP ĐỀ XUẤT", className="w-[16%] px-2.5 py-3 text-center"),
                                                                        html.Th("ĐƠN GIÁ & THÀNH TIỀN", className="w-[14%] pl-2.5 pr-4 py-3 text-right"),
                                                                    ],
                                                                    className="bg-slate-50/90 border-b border-slate-200 text-[11px] font-bold uppercase tracking-wider text-slate-400",
                                                                )
                                                            ),
                                                            html.Tbody(id="m4ReplenishTableBody", className="divide-y divide-slate-100 text-xs"),
                                                        ],
                                                    )
                                                ],
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        className="mt-auto",
                                        children=[
                                            html.Div(
                                                className="px-4 py-3 border-t border-slate-200/80 bg-slate-50/40",
                                                children=[
                                                    html.Div(
                                                        [
                                                            html.Span("Tiến độ đơn PO đã phát hành (Cập nhật hàng đang về INC)", className="text-[11px] font-bold uppercase tracking-wider text-slate-500"),
                                                            html.Button("Quản lý tất cả PO →", id="m4ManageAllPoBtn", n_clicks=0, className="text-xs font-semibold text-blue-600 hover:text-blue-800 cursor-pointer"),
                                                        ],
                                                        className="flex items-center justify-between gap-2 mb-2",
                                                    ),
                                                    html.Div(id="m4RecentPoStrip", className="grid grid-cols-1 md:grid-cols-2 gap-2.5"),
                                                ],
                                            ),
                                            html.Div(
                                                className="bg-slate-50/80 border-t border-slate-200/80 px-4 py-2.5 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500",
                                                children=[
                                                    html.Div(
                                                        [
                                                            html.Span(className="w-2 h-2 rounded-full bg-emerald-500 shrink-0"),
                                                            html.Span(["Tất cả mặt hàng điều hòa đã được làm tròn theo ", html.Strong("bộ đôi (Dàn nóng + Dàn lạnh)"), " và quy cách kiện hãng."]),
                                                        ],
                                                        className="flex items-center gap-2",
                                                    ),
                                                    html.Button("Đặt lại số lượng tối ưu ban đầu", id="m4FooterResetBtn", n_clicks=0, className="font-semibold text-blue-600 hover:underline cursor-pointer shrink-0"),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            # RIGHT 4 COLS: GROUPED PO BY SUPPLIER
                            html.Div(
                                className="xl:col-span-4 bg-white border border-slate-200/90 rounded-xl shadow-2xs overflow-hidden flex flex-col justify-between",
                                children=[
                                    html.Div(
                                        [
                                            html.Div(
                                                className="px-4 py-3 border-b border-slate-200/80 flex items-start justify-between gap-2 bg-slate-50/50",
                                                children=[
                                                    html.Div(
                                                        [
                                                            html.H2("Gom đơn nhập theo Hãng", className="text-sm font-bold text-slate-900"),
                                                            html.P("Tự động tách phiếu nhập & kiểm tra Freeship (>10 tr)", className="text-[11px] text-slate-500 mt-0.5 leading-snug"),
                                                        ],
                                                        className="min-w-0",
                                                    ),
                                                    html.Span("Trong trần ngân sách", id="m4RightSummaryBadge", className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 shrink-0"),
                                                ],
                                            ),
                                            html.Div(
                                                className="px-4 py-3 border-b border-slate-100 bg-slate-50/30",
                                                children=[
                                                    html.Div(
                                                        [
                                                            html.Span("Phân bổ ngân sách theo Hãng:", className="font-medium text-slate-600"),
                                                            html.Span("0 tr / 250 tr", id="m4RightAllocationText", className="font-bold text-slate-900 tabular-nums"),
                                                        ],
                                                        className="flex items-center justify-between gap-2 text-xs mb-1.5",
                                                    ),
                                                    html.Div(id="m4SupplierStackedBar", className="w-full h-2 bg-slate-100 rounded-full overflow-hidden flex gap-0.5"),
                                                ],
                                            ),
                                            html.Div(id="m4SupplierCardsContainer", className="p-3.5 space-y-2.5"),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                className="px-3.5 pb-3",
                                                children=[
                                                    html.Div(
                                                        id="m4ShippingBenefitBox",
                                                        className="p-3 rounded-xl bg-blue-50/70 border border-blue-200/80 text-xs text-blue-950 flex items-start gap-2.5",
                                                        children=[
                                                            html.Span("🚚", className="text-base leading-none mt-0.5"),
                                                            html.Div(
                                                                [
                                                                    html.Strong("Đang kiểm tra điều kiện Freeship...", id="m4ShippingBenefitTitle", className="font-semibold"),
                                                                    html.Div("Ưu đãi chiết khấu 1,5% thanh toán sớm.", id="m4ShippingBenefitSub", className="text-[11px] text-blue-800 mt-0.5"),
                                                                ],
                                                                className="leading-relaxed",
                                                            ),
                                                        ],
                                                    )
                                                ],
                                            ),
                                            html.Div(
                                                className="p-3.5 bg-slate-50 border-t border-slate-200/90 flex items-center justify-between gap-2",
                                                children=[
                                                    html.Button("📥 Xuất CSV", id="m4QuickCsvBtn", n_clicks=0, className="px-3 py-2 rounded-lg text-xs font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-100 transition cursor-pointer shrink-0"),
                                                    html.Button(
                                                        [html.Span("🚀 "), html.Span("Duyệt & Xuất Đơn Nhập", id="m4ApproveBtnText")],
                                                        id="m4ApproveAllOrdersBtn",
                                                        n_clicks=0,
                                                        className="w-full px-3.5 py-2 rounded-lg text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 shadow-2xs transition cursor-pointer flex items-center justify-center gap-1.5",
                                                    ),
                                                ],
                                            ),
                                        ]
                                    ),
                                ],
                            ),
                        ],
                    ),
            # SUPPLIER DRAWER (m4SupplierDrawer)
            html.Div(id="m4DrawerBackdrop", className="fixed inset-0 bg-slate-900/30 backdrop-blur-[1px] z-40 hidden"),
            html.Aside(
                id="m4SupplierDrawer",
                className="fixed top-0 right-0 h-full w-[480px] max-w-full bg-white shadow-2xl border-l border-slate-200 z-50 transform translate-x-full transition-transform duration-200 flex flex-col justify-between",
                children=[
                    html.Div(
                        className="p-5 overflow-y-auto space-y-4",
                        children=[
                            html.Div(
                                className="flex items-start justify-between gap-3 pb-3 border-b border-slate-100",
                                children=[
                                    html.Div(
                                        [
                                            html.Span("PHIẾU ĐẶT NHẬP HÀNG HÃNG", className="inline-block px-2 py-0.5 rounded text-[11px] font-bold mb-1 bg-blue-50 text-blue-700 border border-blue-200"),
                                            html.H3("", id="m4DrawerSupplierTitle", className="text-base font-bold text-slate-900"),
                                            html.P("", id="m4DrawerSupplierMeta", className="text-xs text-slate-500 mt-0.5"),
                                        ]
                                    ),
                                    html.Button("✕", id="m4CloseDrawerBtn", n_clicks=0, className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 cursor-pointer"),
                                ],
                            ),
                            html.Div(id="m4DrawerSupplierBody", className="space-y-4 text-xs"),
                        ],
                    ),
                    html.Div(
                        className="p-4 border-t border-slate-200 bg-slate-50 flex items-center justify-between gap-2",
                        children=[
                            html.Button("Đóng", id="m4CloseDrawerFooterBtn", n_clicks=0, className="px-3 py-2 rounded-lg text-xs font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-100 cursor-pointer"),
                            html.Div(
                                [
                                    html.Button("📥 Xuất Excel", id="m4DrawerExportCsvBtn", n_clicks=0, className="px-3 py-2 rounded-lg text-xs font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-100 cursor-pointer"),
                                    html.Button("Mở bảng duyệt tổng →", id="m4DrawerApproveSingleBtn", n_clicks=0, className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 shadow-sm transition cursor-pointer"),
                                ],
                                className="flex items-center gap-2",
                            ),
                        ],
                    ),
                ],
            ),
            # APPROVE MODAL (m4ApproveModal + poPreviewModal landmark)
            html.Div(
                id="m4ApproveModal",
                className="fixed inset-0 bg-slate-900/40 z-50 hidden items-center justify-center p-4",
                children=[
                    html.Div(
                        id="poPreviewModal",
                        className="bg-white rounded-2xl max-w-lg w-full p-5 shadow-xl border border-slate-200 space-y-4",
                        children=[
                            html.Div(
                                className="flex items-center justify-between border-b border-slate-100 pb-3",
                                children=[
                                    html.Div(
                                        [
                                            html.H3("Xác nhận Phê duyệt & Phát hành Đơn nhập hàng (PO)", className="text-base font-bold text-slate-900"),
                                            html.P("Hệ thống sẽ sinh mã PO-xxxx riêng cho từng Nhà phân phối", className="text-xs text-slate-500 mt-0.5"),
                                        ]
                                    ),
                                    html.Button("✕", id="m4CloseApproveModalBtn", n_clicks=0, className="text-slate-400 hover:text-slate-600 cursor-pointer"),
                                ],
                            ),
                            html.Div(id="m4ApproveModalBody", className="space-y-3 text-xs max-h-[55vh] overflow-y-auto"),
                            html.Div(
                                className="flex flex-wrap items-center justify-between gap-2 pt-3 border-t border-slate-100",
                                children=[
                                    html.Button("📥 Xuất file Excel PO", id="m4ApproveExportCsvBtn", n_clicks=0, className="px-3 py-2 rounded-lg text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 cursor-pointer"),
                                    html.Div(
                                        [
                                            html.Button("Xem lại", id="m4CancelApproveModalBtn", n_clicks=0, className="px-3.5 py-2 rounded-lg text-xs font-medium text-slate-600 hover:bg-slate-100 cursor-pointer"),
                                            html.Button("✓ Ký duyệt & Phát hành PO", id="m4ConfirmApproveBtn", n_clicks=0, className="px-4 py-2 rounded-lg text-xs font-bold bg-emerald-600 text-white hover:bg-emerald-700 shadow-sm cursor-pointer"),
                                        ],
                                        className="flex items-center gap-2",
                                    ),
                                ],
                            ),
                        ],
                    )
                ],
            ),
            # PO LIFECYCLE MODAL (m4PoLifecycleModal)
            html.Div(
                id="m4PoLifecycleModal",
                className="fixed inset-0 bg-slate-900/40 z-50 hidden items-center justify-center p-4",
                children=[
                    html.Div(
                        className="bg-white rounded-2xl max-w-2xl w-full p-5 shadow-xl border border-slate-200 space-y-4",
                        children=[
                            html.Div(
                                className="flex items-center justify-between border-b border-slate-100 pb-3",
                                children=[
                                    html.Div(
                                        [
                                            html.H3("Theo dõi Tiến độ Đơn Mua Hàng (PO Lifecycle)", className="text-base font-bold text-slate-900"),
                                            html.P("Danh sách đơn nhập từ SQLite PURCHASE_ORDERS & hàng đang về (INC)", className="text-xs text-slate-500 mt-0.5"),
                                        ]
                                    ),
                                    html.Button("✕", id="m4CloseLifecycleModalBtn", n_clicks=0, className="text-slate-400 hover:text-slate-600 cursor-pointer"),
                                ],
                            ),
                            html.Div(id="m4PoLifecycleList", className="space-y-2.5 max-h-[60vh] overflow-y-auto text-xs"),
                            html.Div(
                                className="flex items-center justify-between pt-3 border-t border-slate-100",
                                children=[
                                    html.Button("📥 Xuất danh sách PO (Excel)", id="m4LifecycleExportCsvBtn", n_clicks=0, className="px-3 py-2 rounded-lg text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 cursor-pointer"),
                                    html.Button("Đóng", id="m4CloseLifecycleFooterBtn", n_clicks=0, className="px-4 py-2 rounded-lg text-xs font-bold bg-slate-900 text-white hover:bg-slate-800 cursor-pointer"),
                                ],
                            ),
                        ],
                    )
                ],
            ),
        ],
    )
