"""
Giao diện Dash cho Phân hệ 05: Chăm sóc khách hàng & Smart CRM 5 Điểm chạm (Prototype L1712–L2094).
"""
from dash import dcc, html


def build_m5_panel(is_active: bool = False) -> html.Main:
    """Xây dựng Panel M5 (KPIs lọc nhanh, Phễu 5 điểm chạm, Master-Detail 7:5 & Modal chu kỳ)."""
    return html.Main(
        id="panel-m5",
        style={"display": "flex" if is_active else "none"},
        className="tab-panel flex-1 min-w-0 bg-[#F8FAFC] overflow-y-auto custom-scrollbar px-5 py-4 flex-col gap-4",
        children=[
            dcc.Store(id="store-m5-trigger", data="Tất cả"),
            dcc.Store(id="store-m5-include-cooldown", data=False),
            dcc.Store(id="store-m5-selected-customer", data=None),
            dcc.Store(id="store-m5-outcome", data="booked"),
            dcc.Store(id="store-m5-refresh", data=0),
            # 1. HEADER BAR
            html.Header(
                        className="flex flex-wrap items-center justify-between gap-3",
                        children=[
                            html.Div(
                                className="flex flex-wrap items-center gap-2.5",
                                children=[
                                    html.Span(className="w-2.5 h-2.5 rounded-full bg-rose-600 animate-pulse shrink-0"),
                                    html.H1("Chăm sóc khách hàng & Đặt lịch bảo dưỡng", className="text-lg xl:text-xl font-bold tracking-tight text-slate-900"),
                                    html.Span(
                                        "0 KHÁCH CẦN GỌI HÔM NAY",
                                        id="m5HeaderPendingBadge",
                                        className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-600 text-white tracking-wide tabular-nums",
                                    ),
                                    html.Span(
                                        "🛡️ Chống gọi trùng 30 ngày",
                                        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200/80",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="flex flex-wrap items-center gap-2",
                                children=[
                                    html.Button(
                                        "↻ Quét dữ liệu mới",
                                        id="m5ScanTriggersBtn",
                                        n_clicks=0,
                                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 shadow-2xs transition cursor-pointer",
                                    ),
                                    html.Button(
                                        "⚙ Cài đặt chu kỳ",
                                        id="m5OpenCycleModalBtn",
                                        n_clicks=0,
                                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 shadow-2xs transition cursor-pointer",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # 2. 4 KPI CARDS (BẤM LỌC NHANH)
                    html.Section(
                        className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3.5",
                        children=[
                            html.Div(
                                id="m5Kpi-pending",
                                n_clicks=0,
                                className="kpi-card cursor-pointer bg-white rounded-xl p-4 min-h-[136px] border border-slate-200/90 shadow-2xs flex flex-col justify-between select-none",
                                children=[
                                    html.Div(
                                        [
                                            html.Span([html.Span(className="w-2 h-2 rounded-full bg-rose-600 shrink-0"), html.Span("CẦN LIÊN HỆ HÔM NAY")], className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500"),
                                            html.Span("Ưu tiên gọi", className="shrink-0 px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200/70"),
                                        ],
                                        className="flex items-start justify-between gap-2 mb-1.5",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("0 khách hàng", id="m5KpiPendingVal", className="text-2xl font-bold tracking-tight text-slate-900 tabular-nums"),
                                            html.Span("trong danh sách", className="text-xs text-slate-400"),
                                        ],
                                        className="flex items-baseline flex-wrap gap-x-2 gap-y-0.5 my-0.5",
                                    ),
                                    html.Div(id="m5KpiPendingFoot", className="text-xs text-slate-500 pt-2 mt-1.5 border-t border-slate-100 tabular-nums"),
                                ],
                            ),
                            html.Div(
                                id="m5Kpi-maintenance",
                                n_clicks=0,
                                className="kpi-card cursor-pointer bg-white rounded-xl p-4 min-h-[136px] border border-slate-200/90 shadow-2xs flex flex-col justify-between select-none",
                                children=[
                                    html.Div(
                                        [
                                            html.Span([html.Span(className="w-2 h-2 rounded-full bg-blue-600 shrink-0"), html.Span("BẢO DƯỠNG & THAY LÕI ĐỊNH KỲ")], className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500"),
                                            html.Span("Chu kỳ ĐH", className="shrink-0 px-2 py-0.5 rounded text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200/70"),
                                        ],
                                        className="flex items-start justify-between gap-2 mb-1.5",
                                    ),
                                    html.Div(html.Span("0 hộ gia đình", id="m5KpiMaintVal", className="text-2xl font-bold tracking-tight text-blue-600 tabular-nums"), className="flex items-baseline gap-2 my-0.5"),
                                    html.Div("Đến chu kỳ bảo dưỡng · bấm để lọc riêng", className="text-xs text-slate-500 pt-2 mt-1.5 border-t border-slate-100"),
                                ],
                            ),
                            html.Div(
                                id="m5Kpi-crosssell",
                                n_clicks=0,
                                className="kpi-card cursor-pointer bg-white rounded-xl p-4 min-h-[136px] border border-slate-200/90 shadow-2xs flex flex-col justify-between select-none",
                                children=[
                                    html.Div(
                                        [
                                            html.Span([html.Span(className="w-2 h-2 rounded-full bg-amber-500 shrink-0"), html.Span("BÁN CHÉO PK & GIA HẠN BH")], className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500"),
                                            html.Span("Cơ hội vàng", className="shrink-0 px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-50 text-amber-800 border border-amber-200/70"),
                                        ],
                                        className="flex items-start justify-between gap-2 mb-1.5",
                                    ),
                                    html.Div(html.Span("0 cơ hội bán", id="m5KpiCrossVal", className="text-2xl font-bold tracking-tight text-amber-600 tabular-nums"), className="flex items-baseline gap-2 my-0.5"),
                                    html.Div("Máy chưa giá treo & Khách sắp hết bảo hành", className="text-xs text-slate-500 pt-2 mt-1.5 border-t border-slate-100"),
                                ],
                            ),
                            html.Div(
                                id="m5Kpi-done",
                                n_clicks=0,
                                className="kpi-card cursor-pointer bg-white rounded-xl p-4 min-h-[136px] border border-slate-200/90 shadow-2xs flex flex-col justify-between select-none",
                                children=[
                                    html.Div(
                                        [
                                            html.Span([html.Span(className="w-2 h-2 rounded-full bg-emerald-600 shrink-0"), html.Span("DOANH THU DỊCH VỤ & HẸN THỢ")], className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500"),
                                            html.Span("Đã chốt lịch", id="m5KpiDoneBadge", className="shrink-0 px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/70 tabular-nums"),
                                        ],
                                        className="flex items-start justify-between gap-2 mb-1.5",
                                    ),
                                    html.Div(html.Span("0 đ", id="m5KpiRevenueMain", className="text-2xl font-bold tracking-tight text-slate-900 tabular-nums"), className="flex items-baseline gap-2 my-0.5"),
                                    html.Div(id="m5KpiDoneFoot", className="text-xs text-slate-500 pt-2 mt-1.5 border-t border-slate-100 tabular-nums"),
                                ],
                            ),
                        ],
                    ),
                    # 3. 2 BIỂU ĐỒ PHỄU 5 ĐIỂM CHẠM & LỊCH HẸN THỢ
                    html.Section(
                        className="grid grid-cols-1 lg:grid-cols-2 gap-4",
                        children=[
                            html.Div(
                                className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-2xs",
                                children=[
                                    html.Div("Phân bổ 5 Điểm chạm Vàng CSKH (Care Triggers)", className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2"),
                                    dcc.Graph(id="m5TriggersChart", config={"displayModeBar": False}, style={"height": "220px"}),
                                ],
                            ),
                            html.Div(
                                className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-2xs",
                                children=[
                                    html.Div("Cơ cấu mức độ Ưu tiên & Hàng đợi Cooldown 30 ngày", className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2"),
                                    dcc.Graph(id="m5PriorityChart", config={"displayModeBar": False}, style={"height": "220px"}),
                                ],
                            ),
                        ],
                    ),
                    # 4. BỐ CỤC LÀM VIỆC MASTER-DETAIL (7 : 5)
                    html.Div(
                        className="grid grid-cols-1 xl:grid-cols-12 gap-4 items-stretch",
                        children=[
                            # LEFT 7 COLS: CUSTOMER QUEUE
                            html.Section(
                                className="xl:col-span-7 bg-white rounded-xl border border-slate-200/90 shadow-2xs flex flex-col justify-between overflow-hidden",
                                children=[
                                    html.Div(
                                        [
                                            html.Div(
                                                className="px-4 py-3 border-b border-slate-200/80 flex flex-wrap items-center justify-between gap-2.5 bg-slate-50/60",
                                                children=[
                                                    html.Div(id="m5TriggerPillsContainer", className="flex flex-wrap items-center gap-1.5"),
                                                    html.Div(
                                                        className="flex flex-wrap items-center gap-2",
                                                        children=[
                                                            html.Button(
                                                                "Hiện cả Cooldown",
                                                                id="m5ToggleCooldownBtn",
                                                                n_clicks=0,
                                                                className="px-2.5 py-1.5 rounded-lg text-[11px] font-semibold bg-white border border-slate-200 text-slate-600 hover:bg-slate-100 cursor-pointer",
                                                            ),
                                                            dcc.Input(
                                                                id="m5SearchInput",
                                                                type="text",
                                                                value="",
                                                                debounce=True,
                                                                placeholder="Tìm tên, SĐT, mã máy...",
                                                                className="px-3 py-1.5 w-44 rounded-lg text-xs bg-white border border-slate-200 focus:outline-none",
                                                            ),
                                                        ],
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
                                                                        html.Th("KHÁCH HÀNG & ƯU TIÊN", className="w-[33%] pl-4 pr-2.5 py-3"),
                                                                        html.Th("THIẾT BỊ ĐÃ MUA", className="w-[26%] px-2.5 py-3"),
                                                                        html.Th("LÝ DO CHĂM SÓC", className="w-[25%] px-2.5 py-3"),
                                                                        html.Th("TÁC VỤ NHANH", className="w-[16%] pl-2.5 pr-4 py-3 text-right"),
                                                                    ],
                                                                    className="bg-slate-50/90 border-b border-slate-200 text-[11px] font-bold uppercase tracking-wider text-slate-400",
                                                                )
                                                            ),
                                                            html.Tbody(id="m5CustomerTableBody", className="divide-y divide-slate-100 text-xs"),
                                                        ],
                                                    )
                                                ],
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Span("Hiển thị nhóm ưu tiên gọi hôm nay", id="m5TableFooterInfo"),
                                            html.Span("Bấm vào dòng khách hàng để mở kịch bản gọi bên phải →", className="text-slate-400"),
                                        ],
                                        className="px-4 py-3 bg-slate-50/80 border-t border-slate-200/80 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500",
                                    ),
                                ],
                            ),
                            # RIGHT 5 COLS: CALL SCRIPT, ZALO ZNS & BOOKING PANEL
                            html.Aside(
                                className="xl:col-span-5 bg-white rounded-xl border border-slate-200/90 shadow-2xs flex flex-col justify-between overflow-hidden",
                                children=[
                                    html.Div(
                                        className="p-4 space-y-3.5 overflow-y-auto",
                                        children=[
                                            html.Div(
                                                className="pb-3 border-b border-slate-100",
                                                children=[
                                                    html.Div(
                                                        [
                                                            html.Span("HỒ SƠ TÁC CHIẾN CUỘC GỌI", className="text-[11px] font-bold uppercase tracking-wider text-slate-400"),
                                                            html.Span("✓ Hợp lệ (Chưa gọi trong 30 ngày)", id="m5PanelValidBadge", className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/80"),
                                                        ],
                                                        className="flex flex-wrap items-center justify-between gap-2 mb-1.5",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Div(
                                                                [
                                                                    html.H2("Chưa chọn khách", id="m5PanelCustomerName", className="text-base font-bold text-slate-900"),
                                                                    html.Span("Ưu tiên", id="m5PanelPriorityBadge", className="shrink-0 px-2 py-0.5 rounded text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-200/80 tabular-nums"),
                                                                ],
                                                                className="flex flex-wrap items-center gap-1.5 min-w-0",
                                                            ),
                                                            html.Span("09xx", id="m5PanelPhoneLink", className="text-sm font-bold text-blue-600 tabular-nums shrink-0"),
                                                        ],
                                                        className="flex items-baseline justify-between gap-2",
                                                    ),
                                                    html.Div("", id="m5PanelAddressDevice", className="text-xs text-slate-500 mt-1 leading-snug"),
                                                ],
                                            ),
                                            html.Div(
                                                id="m5CooldownWarningBanner",
                                                className="hidden p-2.5 rounded-xl bg-amber-50 border border-amber-300 text-amber-900 text-xs flex items-start gap-2",
                                                children=[
                                                    html.Span("🛡️", className="text-base leading-none shrink-0 mt-0.5"),
                                                    html.Div(
                                                        [
                                                            html.Div("Chặn chống làm phiền 30 ngày (ERR_CRM_001)", className="font-bold"),
                                                            html.P("", id="m5CooldownWarningDesc", className="text-[11px] text-amber-800 mt-0.5"),
                                                        ],
                                                        className="flex-1 leading-snug",
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                className="p-3.5 rounded-xl bg-amber-50/75 border border-amber-200/80 space-y-2",
                                                children=[
                                                    html.Div(
                                                        [
                                                            html.Span([html.Span("💬 "), html.Span("AI Call Script (Điện Máy Anh Tâm)")], className="inline-flex items-center gap-1.5 text-xs font-bold text-amber-950"),
                                                            html.Span("Cá nhân hóa theo máy", className="px-1.5 py-0.5 rounded bg-amber-200/60 text-amber-900 text-[10px] font-semibold"),
                                                        ],
                                                        className="flex flex-wrap items-center justify-between gap-2",
                                                    ),
                                                    html.P("", id="m5PanelCallScript", className="text-xs text-slate-800 leading-relaxed italic"),
                                                    html.Div(id="m5PanelZaloPreview", className="text-[11px] text-blue-900 bg-blue-50/70 border border-blue-200/60 rounded-lg p-2"),
                                                ],
                                            ),
                                            html.Div(
                                                className="space-y-2",
                                                children=[
                                                    html.Div("GHI NHẬN KẾT QUẢ CUỘC GỌI", className="text-[11px] font-bold uppercase tracking-wider text-slate-400"),
                                                    html.Div(
                                                        id="m5OutcomeCard-booked",
                                                        n_clicks=0,
                                                        className="rounded-xl border-2 border-blue-600 bg-blue-50/25 p-3 cursor-pointer transition",
                                                        children=[
                                                            html.Div(
                                                                [
                                                                    html.Span("✓ Khách đồng ý chốt lịch thợ tận nhà", className="text-xs font-bold text-slate-900"),
                                                                    html.Span("150.000 đ", id="m5BookedFeePill", className="text-xs font-bold text-blue-600 tabular-nums shrink-0"),
                                                                ],
                                                                className="flex items-center justify-between gap-2",
                                                            ),
                                                            html.Div(
                                                                className="mt-3 pt-3 border-t border-blue-200/60 space-y-2.5",
                                                                children=[
                                                                    html.Div(
                                                                        className="grid grid-cols-2 gap-2.5",
                                                                        children=[
                                                                            html.Div(
                                                                                [
                                                                                    html.Label("Ngày hẹn kỹ thuật", className="block text-[11px] font-medium text-slate-500 mb-1"),
                                                                                    dcc.Input(
                                                                                        id="m5AppointmentDate",
                                                                                        type="text",
                                                                                        value="2026-11-18",
                                                                                        className="w-full px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-white border border-slate-200 text-slate-800",
                                                                                    ),
                                                                                ]
                                                                            ),
                                                                            html.Div(
                                                                                [
                                                                                    html.Label("Khung giờ phục vụ", className="block text-[11px] font-medium text-slate-500 mb-1"),
                                                                                    dcc.Dropdown(
                                                                                        id="m5AppointmentSlot",
                                                                                        clearable=False,
                                                                                        value="14:00 - 15:30",
                                                                                        options=[
                                                                                            {"label": "09:00 - 10:30 (Sáng)", "value": "09:00 - 10:30"},
                                                                                            {"label": "14:00 - 15:30 (Chiều)", "value": "14:00 - 15:30"},
                                                                                            {"label": "15:30 - 17:00 (Chiều)", "value": "15:30 - 17:00"},
                                                                                            {"label": "18:30 - 20:00 (Ngoài giờ)", "value": "18:30 - 20:00"},
                                                                                        ],
                                                                                        className="text-xs font-semibold",
                                                                                    ),
                                                                                ]
                                                                            ),
                                                                        ],
                                                                    ),
                                                                    html.Div(
                                                                        className="grid grid-cols-12 gap-2.5 items-end",
                                                                        children=[
                                                                            html.Div(
                                                                                [
                                                                                    html.Label("Phân công kỹ thuật viên", className="block text-[11px] font-medium text-slate-500 mb-1"),
                                                                                    dcc.Dropdown(id="m5TechnicianSelect", clearable=False, className="text-xs font-semibold"),
                                                                                ],
                                                                                className="col-span-7",
                                                                            ),
                                                                            html.Div(
                                                                                [
                                                                                    html.Label("Gói dịch vụ", className="block text-[11px] font-medium text-slate-500 mb-1"),
                                                                                    dcc.Input(
                                                                                        id="m5ServicePackageInput",
                                                                                        type="text",
                                                                                        value="Bảo dưỡng xịt rửa ĐH",
                                                                                        className="w-full px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-100/80 border border-slate-200 text-slate-700",
                                                                                    ),
                                                                                ],
                                                                                className="col-span-5",
                                                                            ),
                                                                        ],
                                                                    ),
                                                                    html.Div(
                                                                        id="m5TechConflictBanner",
                                                                        className="hidden p-2.5 rounded-lg bg-rose-50 border border-rose-300 text-rose-900 text-[11px] flex items-start gap-2",
                                                                        children=[
                                                                            html.Span("⚠️", className="text-sm leading-none shrink-0 mt-0.5"),
                                                                            html.Div("", id="m5TechConflictDesc", className="leading-snug font-medium"),
                                                                        ],
                                                                    ),
                                                                ],
                                                            ),
                                                        ],
                                                    ),
                                                    html.Div(
                                                        id="m5OutcomeCard-callback",
                                                        n_clicks=0,
                                                        className="rounded-xl border border-slate-200 hover:border-slate-300 bg-white px-3 py-2.5 cursor-pointer transition flex items-center justify-between gap-2",
                                                        children=[
                                                            html.Span("Khách bận, hẹn gọi lại sau", className="text-xs font-medium text-slate-700"),
                                                            html.Span("Đặt lịch nhắc gọi lại", className="text-[11px] text-slate-400"),
                                                        ],
                                                    ),
                                                    html.Div(
                                                        id="m5OutcomeCard-noanswer",
                                                        n_clicks=0,
                                                        className="rounded-xl border border-slate-200 hover:border-slate-300 bg-white px-3 py-2.5 cursor-pointer transition flex items-center justify-between gap-2",
                                                        children=[
                                                            html.Span("Không nghe máy", className="text-xs font-medium text-slate-700"),
                                                            html.Span("Tự động nhắc lại sau 4 giờ", className="text-[11px] text-slate-400"),
                                                        ],
                                                    ),
                                                    html.Div(
                                                        id="m5OutcomeCard-declined",
                                                        n_clicks=0,
                                                        className="rounded-xl border border-slate-200 hover:border-slate-300 bg-white px-3 py-2.5 cursor-pointer transition flex items-center justify-between gap-2",
                                                        children=[
                                                            html.Span("Khách từ chối", className="text-xs font-medium text-slate-700"),
                                                            html.Span("Dời chu kỳ sang 30 ngày sau", className="text-[11px] text-slate-400"),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="p-4 bg-slate-50 border-t border-slate-200/90 grid grid-cols-12 gap-2.5",
                                        children=[
                                            html.Button(
                                                "💬 Gửi Zalo ZNS",
                                                id="m5SecondaryActionBtn",
                                                n_clicks=0,
                                                className="col-span-5 py-2.5 px-3 rounded-xl text-xs font-semibold bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 transition cursor-pointer flex items-center justify-center gap-1.5",
                                            ),
                                            html.Button(
                                                "✓ Lưu nhật ký & Chốt lịch thợ",
                                                id="m5PrimarySaveBtn",
                                                n_clicks=0,
                                                className="col-span-7 py-2.5 px-4 rounded-xl text-xs font-bold bg-slate-900 hover:bg-slate-800 text-white shadow-2xs transition cursor-pointer flex items-center justify-center gap-1.5",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # CYCLE SETTINGS MODAL (m5CycleModal)
                    html.Div(
                        id="m5CycleModal",
                        className="fixed inset-0 bg-slate-900/40 z-50 hidden items-center justify-center p-4",
                        children=[
                            html.Div(
                                className="bg-white rounded-2xl max-w-md w-full p-5 shadow-xl border border-slate-200 space-y-4",
                                children=[
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.H3("Cài đặt Chu kỳ Chăm sóc & Chống Spam", className="text-sm font-bold text-slate-900"),
                                                    html.P("Tự động quét danh sách khách hàng lúc 06:00 sáng hàng ngày", className="text-xs text-slate-500 mt-0.5"),
                                                ]
                                            ),
                                            html.Button("✕", id="m5CloseCycleModalBtn", n_clicks=0, className="text-slate-400 hover:text-slate-600 cursor-pointer"),
                                        ],
                                        className="flex items-center justify-between border-b border-slate-100 pb-3",
                                    ),
                                    html.Div(
                                        className="space-y-3 text-xs",
                                        children=[
                                            html.Div([html.Span("Chu kỳ nhắc bảo dưỡng Điều hòa:", className="font-medium text-slate-700"), html.Span("6 tháng sau lắp đặt", className="px-2.5 py-1 rounded bg-blue-50 text-blue-700 font-semibold")], className="flex items-center justify-between py-1"),
                                            html.Div([html.Span("Chu kỳ nhắc thay lõi Máy lọc nước RO:", className="font-medium text-slate-700"), html.Span("6 tháng (Lõi 1, 2, 3)", className="px-2.5 py-1 rounded bg-blue-50 text-blue-700 font-semibold")], className="flex items-center justify-between py-1"),
                                            html.Div([html.Span("Cảnh báo gia hạn Bảo hành hãng:", className="font-medium text-slate-700"), html.Span("Trước khi hết hạn 30 ngày", className="px-2.5 py-1 rounded bg-amber-50 text-amber-800 font-semibold")], className="flex items-center justify-between py-1"),
                                            html.Div([html.Span("Chặn gọi trùng chống làm phiền (Spam):", className="font-medium text-slate-700"), html.Span("Tối thiểu 30 ngày / khách", className="px-2.5 py-1 rounded bg-emerald-50 text-emerald-700 font-semibold")], className="flex items-center justify-between py-1"),
                                        ],
                                    ),
                                    html.Div(
                                        [
                                            html.Button("Đóng", id="m5CancelCycleModalBtn", n_clicks=0, className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:bg-slate-100 cursor-pointer"),
                                            html.Button("Lưu cài đặt", id="m5SaveCycleModalBtn", n_clicks=0, className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 text-white hover:bg-slate-800 cursor-pointer"),
                                        ],
                                        className="flex justify-end gap-2 pt-3 border-t border-slate-100",
                                    ),
                                ],
                            )
                        ],
                    ),
        ],
    )
