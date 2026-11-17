"""
Giao diện Module 03 (Parity V2): Gợi ý xả hàng & Định giá cạnh tranh —
Khớp 100% Ảnh 2: Inline Cashflow Bar trên PA1-PA4, Mô phỏng Presets & Sliders,
Radar đối chiếu giá + Thang định vị giá & Sàn vốn + Nhận định chiến lược từ Hệ thống.
"""
from typing import Any, Dict
from dash import dcc, html


def build_m3_modals() -> html.Div:
    """Dựng 2 Modals: Mẫu In Tem Giá Xả Đỏ (Khổ A6) & Danh sách Chiến dịch Xả kho."""
    return html.Div(
        [
            # Modal In Tem Giá Xả Đỏ
            html.Div(
                id="m3SaleTagModal",
                style={"display": "none"},
                className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-50 items-center justify-center p-4 flex",
                children=html.Div(
                    className="bg-white rounded-2xl max-w-md w-full border border-slate-200 shadow-2xl overflow-hidden",
                    children=[
                        html.Div(
                            [
                                html.Div(
                                    [html.I(className="ph-bold ph-printer text-rose-400 text-lg"), html.H3("Mẫu In Tem Giá Xả Đỏ Dán Kệ (Khổ A6)", className="font-bold text-sm")],
                                    className="flex items-center gap-2",
                                ),
                                html.Button(html.I(className="ph-bold ph-x text-base"), id="btn-close-m3-tag-modal", n_clicks=0, className="text-slate-400 hover:text-white cursor-pointer"),
                            ],
                            className="px-5 py-3.5 bg-slate-900 text-white flex items-center justify-between",
                        ),
                        html.Div(
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span([html.I(className="ph-fill ph-lightning"), " XẢ KHO THU HỒI VỐN"], className="font-extrabold text-xs tracking-wider uppercase flex items-center gap-1"),
                                            html.Span("TV-LG-55C3", id="m3TagSkuCode", className="text-[11px] font-code bg-rose-800/80 px-2 py-0.5 rounded"),
                                        ],
                                        className="bg-rose-600 text-white px-4 py-2 flex items-center justify-between",
                                    ),
                                    html.Div(
                                        [
                                            html.Div("Smart Tivi OLED LG 4K 55 inch 55C3PSA", id="m3TagProductName", className="font-bold text-sm text-slate-900 leading-snug"),
                                            html.Div(
                                                [
                                                    html.Div([html.Div("Giá niêm yết cũ:", className="text-[11px] text-slate-400"), html.Div("27.990.000 đ", id="m3TagOldPrice", className="text-sm font-semibold text-slate-400 line-through font-code")]),
                                                    html.Div([html.Div("GIÁ XẢ ĐẶC BIỆT", className="text-[10px] font-bold uppercase text-rose-600"), html.Div("26.990.000 đ", id="m3TagNewPrice", className="text-2xl font-extrabold text-rose-600 font-code")], className="text-right"),
                                                ],
                                                className="flex items-baseline justify-between border-y border-dashed border-slate-200 py-2.5 tabular-nums whitespace-nowrap",
                                            ),
                                            html.Div(
                                                [html.I(className="ph-fill ph-gift text-amber-600 text-base shrink-0"), html.Span("Combo Tivi + Giá treo + Công lắp đặt", id="m3TagPromoNote", className="font-semibold")],
                                                className="bg-amber-50 border border-amber-200/80 rounded-lg p-2.5 text-xs text-amber-900 flex items-center gap-2",
                                            ),
                                            html.Div(
                                                [html.Span("Điện Máy Anh Tâm · 108 Cầu Giấy"), html.Span([html.I(className="ph-bold ph-qr-code text-sm"), " Quét tra số máy"], className="font-semibold text-slate-700 flex items-center gap-1")],
                                                className="flex items-center justify-between pt-1 text-[11px] text-slate-500",
                                            ),
                                        ],
                                        className="p-4 space-y-3",
                                    ),
                                ],
                                className="w-full bg-white rounded-xl border-2 border-rose-600 shadow-md overflow-hidden",
                            ),
                            className="p-6 bg-slate-100 flex justify-center",
                        ),
                        html.Div(
                            [
                                html.Span("Số lượng tem in: 2 bản (Kệ & Sảnh)", className="text-xs text-slate-500"),
                                html.Div(
                                    [
                                        html.Button("Đóng", id="btn-cancel-m3-tag-modal", n_clicks=0, className="px-3.5 py-1.5 rounded-xl border border-slate-300 text-xs font-semibold text-slate-700 cursor-pointer"),
                                        html.Button([html.I(className="ph-bold ph-printer mr-1"), "In ngay ra máy in nhiệt"], id="btn-confirm-m3-print-tag", n_clicks=0, className="px-4 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold flex items-center cursor-pointer"),
                                    ],
                                    className="flex items-center gap-2",
                                ),
                            ],
                            className="px-5 py-3.5 bg-white border-t border-slate-200 flex items-center justify-between",
                        ),
                    ],
                ),
            ),
            # Modal Chiến dịch xả hàng
            html.Div(
                id="m3CampaignModal",
                style={"display": "none"},
                className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-50 items-center justify-center p-4 flex",
                children=html.Div(
                    className="bg-white rounded-2xl max-w-lg w-full border border-slate-200 shadow-2xl overflow-hidden",
                    children=[
                        html.Div(
                            [
                                html.Div([html.I(className="ph-bold ph-megaphone text-emerald-400 text-lg"), html.H3("Danh sách Chiến dịch Xả kho đang theo dõi", className="font-bold text-sm")], className="flex items-center gap-2"),
                                html.Button(html.I(className="ph-bold ph-x text-base"), id="btn-close-m3-campaign-modal", n_clicks=0, className="text-slate-400 hover:text-white cursor-pointer"),
                            ],
                            className="px-5 py-3.5 bg-slate-900 text-white flex items-center justify-between",
                        ),
                        html.Div(id="m3CampaignModalBody", className="p-5 space-y-2.5 max-h-96 overflow-y-auto text-xs"),
                        html.Div(
                            [
                                html.Span("Chủ cửa hàng có quyền theo dõi & phê duyệt chiến dịch", className="text-[11px] text-slate-500"),
                                html.Button("Đóng", id="btn-cancel-m3-campaign-modal", n_clicks=0, className="px-4 py-1.5 rounded-xl bg-slate-900 text-white text-xs font-semibold cursor-pointer"),
                            ],
                            className="px-5 py-3 bg-slate-50 border-t border-slate-200 flex justify-between items-center",
                        ),
                    ],
                ),
            ),
        ]
    )


def build_m3_panel(services: Dict[str, Any], active: bool = False, role: str = "ROLE_OWNER") -> html.Main:
    """Dựng màn hình chính Module 03 (Parity V2 khớp 100% Ảnh 2)."""
    from src.dash_app.callbacks.m3_callbacks import render_m3_workspace

    init_ws = render_m3_workspace(services, sku="TV-LG-55C3", tactic_code="PA2", target_qty=10, extra_disc=0.0, role=role)

    return html.Main(
        id="panel-m3",
        style={"display": "flex" if active else "none"},
        className="tab-panel flex-1 min-w-0 bg-[#F8FAFC] overflow-y-auto custom-scrollbar px-5 py-4 flex-col gap-4",
        children=[
            dcc.Store(id="store-m3-sku", data="TV-LG-55C3"),
            dcc.Store(id="store-m3-tactic", data="PA2"),
            dcc.Store(id="store-m3-effective-price", data=init_ws["effective_price"]),
            dcc.Store(id="store-m3-price-override", data=None),
            dcc.Store(id="store-m3-offline", data=False),
            # 1. Clean Header
            html.Header(
                [
                    html.Div(
                        [
                            html.Div([html.Span(className="w-2.5 h-2.5 rounded-full bg-emerald-600 pulse-red-dot"), html.H1("Gợi ý xả hàng & Định giá cạnh tranh", className="text-xl font-bold tracking-tight text-slate-900")], className="flex items-center gap-2"),
                            html.Span("4 MÃ ĐỀ XUẤT XẢ", className="bg-amber-100 text-amber-800 border border-amber-200/80 text-xs px-2.5 py-0.5 rounded-md font-bold"),
                            html.Span([html.I(className="ph-bold ph-map-pin text-rose-500"), "Khu vực đối chiếu: ", html.Strong("Cầu Giấy, Hà Nội", className="text-slate-800")], className="text-xs text-slate-500 bg-white border border-slate-200/90 px-2.5 py-1 rounded-lg hidden 2xl:flex items-center gap-1.5"),
                        ],
                        className="flex items-center gap-2.5 min-w-0",
                    ),
                    html.Div(
                        [
                            html.Button([html.I(className="ph-bold ph-arrows-clockwise text-indigo-600"), html.Span("Quét giá thị trường")], id="btn-m3-refresh-radar", n_clicks=0, className="px-3 py-1.5 rounded-lg bg-white hover:bg-slate-50 text-slate-700 border border-slate-200/90 shadow-2xs text-xs font-medium flex items-center gap-1.5 cursor-pointer"),
                            html.Button([html.I(className="ph-bold ph-printer text-sm"), html.Span("In tem giá xả đỏ")], id="btn-m3-open-tag-modal", n_clicks=0, className="px-3.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white shadow-2xs text-xs font-semibold flex items-center gap-1.5 cursor-pointer"),
                        ],
                        className="flex items-center gap-2 shrink-0",
                    ),
                ],
                className="flex items-center justify-between gap-3 whitespace-nowrap shrink-0",
            ),
            # 2. 4 KPI Cards
            html.Section(
                [
                    html.Div(
                        [
                            html.Div([html.Span([html.Span(className="w-2 h-2 rounded-full bg-indigo-600 shrink-0"), html.Span("VỐN DỰ KIẾN THU HỒI")], className="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5"), html.Span("Đạt chỉ tiêu xả", className="bg-indigo-50 text-indigo-700 border border-indigo-200/70 text-[11px] font-semibold px-2 py-0.5 rounded shrink-0")], className="flex items-center justify-between gap-2"),
                            html.Div([html.Span(init_ws["kpi_recovery"], id="m3KpiTotalRecovery", className="text-2xl font-bold tracking-tight text-slate-900 cost-val font-code"), html.Span(init_ws["kpi_qty_sub"], id="m3KpiQtySub", className="text-xs font-medium text-slate-400")], className="my-1 flex items-baseline flex-wrap gap-x-2 gap-y-0.5 tabular-nums"),
                            html.Div([html.Span("Tiền mặt gốc quay về két", className="text-slate-400"), html.Span("Giải phóng diện tích kho", className="font-semibold text-indigo-600")], className="pt-2 border-t border-slate-100 flex flex-col gap-0.5 text-xs"),
                        ],
                        className="kpi-card bg-white rounded-xl p-4 min-h-[142px] border border-slate-200/90 shadow-2xs flex flex-col justify-between gap-2",
                    ),
                    html.Div(
                        [
                            html.Div([html.Span([html.Span(className="w-2 h-2 rounded-full bg-emerald-500 shrink-0"), html.Span("LỢI NHUẬN GỘP KỲ VỌNG")], className="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5"), html.Span(init_ws["kpi_roi_badge"], id="m3KpiMarginPill", className="bg-emerald-50 text-emerald-700 border border-emerald-200/70 text-[11px] font-semibold px-2 py-0.5 rounded shrink-0")], className="flex items-center justify-between gap-2"),
                            html.Div([html.Span(init_ws["kpi_profit"], id="m3KpiTotalProfit", className="text-2xl font-bold tracking-tight text-emerald-600 cost-val font-code"), html.Span("Bảo toàn lãi dương", className="text-xs font-medium text-slate-400")], className="my-1 flex items-baseline flex-wrap gap-x-2 gap-y-0.5 tabular-nums"),
                            html.Div([html.Span("Ưu tiên Combo phụ kiện PA2", className="text-slate-400"), html.Span("Không phá giá máy chính", className="font-semibold text-emerald-700")], className="pt-2 border-t border-slate-100 flex flex-col gap-0.5 text-xs"),
                        ],
                        className="kpi-card bg-white rounded-xl p-4 min-h-[142px] border border-slate-200/90 shadow-2xs flex flex-col justify-between gap-2",
                    ),
                    html.Div(
                        [
                            html.Div([html.Span([html.Span(className="w-2 h-2 rounded-full bg-amber-500 shrink-0"), html.Span("LỢI THẾ GIÁ SO VỚI ĐỐI THỦ")], className="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5"), html.Span([html.I(className="ph-fill ph-fire text-amber-600 mr-1"), "Ưu thế"], className="bg-amber-50 text-amber-800 border border-amber-200/70 text-[11px] font-semibold px-2 py-0.5 rounded flex items-center shrink-0")], className="flex items-center justify-between gap-2"),
                            html.Div([html.Span(init_ws["kpi_pai_text"], id="m3KpiPaiHero", className="text-2xl font-bold tracking-tight text-amber-600"), html.Span("so với mặt bằng giá", className="text-xs font-medium text-slate-400")], className="my-1 flex items-baseline flex-wrap gap-x-2 gap-y-0.5 tabular-nums"),
                            html.Div([html.Span("Đối chiếu ĐMX, MediaMart, Shopee", className="text-slate-400"), html.Span("Làm tròn tâm lý ..50k / ..90k", className="text-emerald-700 font-semibold")], className="pt-2 border-t border-slate-100 flex flex-col gap-0.5 text-xs"),
                        ],
                        className="kpi-card bg-white rounded-xl p-4 min-h-[142px] border border-slate-200/90 shadow-2xs flex flex-col justify-between gap-2",
                    ),
                    html.Div(
                        id="btn-m3-open-campaign-modal",
                        n_clicks=0,
                        className="kpi-card cursor-pointer bg-white rounded-xl p-4 min-h-[142px] border border-slate-200/90 hover:border-slate-300 shadow-2xs flex flex-col justify-between gap-2 group",
                        children=[
                            html.Div([html.Span([html.Span(className="w-2 h-2 rounded-full bg-blue-600 shrink-0"), html.Span("CHIẾN DỊCH XẢ ĐANG CHẠY")], className="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5"), html.Span("Đồng bộ máy tính tiền", className="bg-blue-50 text-blue-700 border border-blue-200/70 text-[11px] font-semibold px-2 py-0.5 rounded shrink-0")], className="flex items-center justify-between gap-2"),
                            html.Div([html.Span(init_ws["kpi_active_camp"], id="m3KpiActiveCampaigns", className="text-2xl font-bold tracking-tight text-slate-900"), html.Span(init_ws["kpi_pending_camp"], id="m3KpiPendingCampaigns", className="text-xs font-semibold text-amber-600")], className="my-1 flex items-baseline flex-wrap gap-x-2 gap-y-0.5 tabular-nums"),
                            html.Div([html.Span("Chiến dịch: Đẩy hàng tồn cuối năm", className="text-slate-400"), html.Span(["Xem tiến độ ", html.I(className="ph-bold ph-arrow-right text-[11px]")], className="font-semibold text-blue-700 inline-flex items-center gap-1")], className="pt-2 border-t border-slate-100 flex flex-col gap-0.5 text-xs"),
                        ],
                    ),
                ],
                className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3.5 shrink-0",
            ),
            # 3. 4-SKU Selector Grid
            html.Section(
                [
                    html.Div(
                        [
                            html.Span([html.I(className="ph-bold ph-crosshair text-indigo-600 text-sm mr-1.5"), "CHỌN MẶT HÀNG XẢ TỒN ĐỂ PHÂN TÍCH KỊCH BẢN & ĐỊNH GIÁ (4 MÃ ĐỀ XUẤT)"], className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center"),
                            html.Span("Bấm vào thẻ để chuyển đổi kịch bản & Radar đối chiếu bên dưới", className="text-xs text-slate-400 hidden xl:inline"),
                        ],
                        className="flex items-center justify-between mb-2.5 px-1 whitespace-nowrap",
                    ),
                    html.Div(init_ws["sku_cards"], id="m3SkuSelectorGrid", className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3"),
                ],
                className="bg-white rounded-xl p-3.5 border border-slate-200/90 shadow-2xs shrink-0",
            ),
            # 4. Split Analytical Workspace (7 cols Left + 5 cols Right) khớp 100% Ảnh 2
            html.Section(
                [
                    # CỘT TRÁI 7 PHẦN: 4 Phương án kèm inline bar + Mô phỏng dòng tiền
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.H2("1. CHỌN KỊCH BẢN KHUYẾN MẠI XẢ HÀNG", className="text-sm font-bold uppercase tracking-wider text-slate-800"),
                                                    html.Span("TV-LG-55C3", id="m3SelectedSkuHeaderBadge", className="text-xs font-code font-semibold px-2 py-0.5 rounded bg-slate-200/80 text-slate-800"),
                                                ],
                                                className="flex items-center flex-wrap gap-2",
                                            ),
                                            html.Div(
                                                [
                                                    html.Span([html.Span(className="w-2.5 h-2.5 rounded-xs bg-slate-800 inline-block mr-1.5"), "Vốn thu hồi"], className="inline-flex items-center text-[11px] font-medium text-slate-600"),
                                                    html.Span([html.Span(className="w-2.5 h-2.5 rounded-xs bg-emerald-500 inline-block mr-1.5"), "Lãi gộp ròng"], className="inline-flex items-center text-[11px] font-medium text-slate-600"),
                                                ],
                                                className="flex items-center gap-3 shrink-0",
                                            ),
                                        ],
                                        className="flex items-center justify-between gap-2",
                                    ),
                                    html.P(init_ws["tactic_header_sub"], id="m3TacticHeaderSub", className="text-xs text-slate-500 mt-1"),
                                ],
                                className="px-4 py-3 border-b border-slate-200/80 bg-slate-50/60",
                            ),
                            html.Div(init_ws["tactic_cards"], id="m3TacticsContainer", className="p-3.5 space-y-2.5"),
                            # Banners bảo mật & cắt lỗ
                            html.Div(
                                [html.I(className="ph-fill ph-lock text-amber-600 text-base"), html.Span("Chế độ Nhân viên bán hàng: Giá vốn, vốn thu hồi và lãi gộp bị ẩn; không được phê duyệt giá cắt lỗ.")],
                                id="m3SalesLockBanner",
                                style=init_ws["sales_lock_style"],
                                className="mx-3.5 mb-2 p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-900 items-center gap-2",
                            ),
                            html.Div(
                                [html.I(className="ph-fill ph-warning-octagon text-rose-600 text-base"), html.Span("CẢNH BÁO CẮT LỖ: Kịch bản đang mô phỏng có lợi nhuận gộp ròng âm! Yêu cầu Chủ cửa hàng phê duyệt.")],
                                id="m3CapitalProtectionBanner",
                                style=init_ws["cap_protect_style"],
                                className="mx-3.5 mb-2 p-2.5 rounded-lg bg-rose-50 border border-rose-300 text-xs font-semibold text-rose-800 items-center gap-2",
                            ),
                            # Khối Mô phỏng dòng tiền khớp 100% Ảnh 2
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.I(className="ph-bold ph-sliders-horizontal text-indigo-600"),
                                                    html.Span("MÔ PHỎNG DÒNG TIỀN", className="text-xs font-bold uppercase tracking-wider text-slate-800"),
                                                    html.Span(init_ws["sim_tactic_badge"], id="m3SimTacticBadge", className="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200/70 text-[10px] font-semibold"),
                                                ],
                                                className="flex items-center gap-2",
                                            ),
                                            html.Div(
                                                [
                                                    html.Button("Mặc định", id="btn-m3-preset-default", n_clicks=0, className="px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-[11px] font-medium text-slate-700 hover:bg-slate-100 cursor-pointer"),
                                                    html.Button("⚡ Khớp giá đối thủ", id="btn-m3-preset-match-comp", n_clicks=0, className="px-2.5 py-1 rounded-lg bg-amber-50 border border-amber-200 text-[11px] font-semibold text-amber-800 hover:bg-amber-100 cursor-pointer"),
                                                    html.Button("Cắt lỗ (-5% vốn)", id="btn-m3-preset-cut-loss", n_clicks=0, className="px-2.5 py-1 rounded-lg bg-rose-50 border border-rose-200 text-[11px] font-semibold text-rose-700 hover:bg-rose-100 cursor-pointer"),
                                                ],
                                                className="flex items-center flex-wrap gap-1.5",
                                            ),
                                        ],
                                        className="flex flex-wrap items-center justify-between gap-2 pb-3 mb-3 border-b border-slate-200/80",
                                    ),
                                    # Hai thanh trượt Giá bán xả & SL xả mục tiêu
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Span("Giá bán xả:", className="text-xs font-semibold text-slate-700"),
                                                            html.Div(
                                                                [
                                                                    html.Strong(init_ws["sim_unit_price_str"], id="m3SimUnitPriceDisplay", className="text-sm font-bold text-slate-900 font-code mr-1.5"),
                                                                    html.Span(init_ws["sim_disc_badge"], id="m3SimDiscountBadge", className="px-1.5 py-0.5 rounded bg-slate-200/80 text-slate-700 text-[10px] font-semibold"),
                                                                ],
                                                                className="flex items-center",
                                                            ),
                                                        ],
                                                        className="flex items-center justify-between mb-2",
                                                    ),
                                                    dcc.Slider(id="m3-discount-slider", min=0, max=30, step=0.5, value=0, marks=None),
                                                    html.Div(
                                                        [
                                                            html.Span(["Cắt lỗ: ", html.Span(init_ws["sim_markers_cutloss"], id="m3SimMarkerCutLoss", className="font-code")]),
                                                            html.Span(["Vốn: ", html.Span(init_ws["sim_markers_cost"], id="m3SimMarkerCost", className="font-code font-bold text-rose-600")]),
                                                            html.Span(["Sàn hãng: ", html.Span(init_ws["sim_markers_floor"], id="m3SimMarkerFloor", className="font-code")]),
                                                            html.Span(["NY: ", html.Span(init_ws["sim_markers_ny"], id="m3SimMarkerNy", className="font-code")]),
                                                        ],
                                                        className="flex items-center justify-between text-[10px] text-slate-500 mt-1",
                                                    ),
                                                ],
                                                className="p-2.5 bg-white rounded-xl border border-slate-200/70",
                                            ),
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Span("SL xả mục tiêu:", className="text-xs font-semibold text-slate-700"),
                                                            html.Span(init_ws["sim_qty_ratio"], id="m3SimQtyRatioBadge", className="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200 text-[11px] font-bold font-code"),
                                                        ],
                                                        className="flex items-center justify-between mb-2",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Button("−", id="btn-m3-qty-dec", n_clicks=0, className="w-7 h-7 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-sm flex items-center justify-center shrink-0 cursor-pointer"),
                                                            html.Div(dcc.Slider(id="m3-qty-input", min=1, max=max(2, init_ws["active_soh"]), step=1, value=init_ws["active_target_qty"], marks=None), className="flex-1"),
                                                            html.Button("+", id="btn-m3-qty-inc", n_clicks=0, className="w-7 h-7 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-sm flex items-center justify-center shrink-0 cursor-pointer"),
                                                        ],
                                                        className="flex items-center gap-2",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Span(init_ws["sim_qty_clear_lbl"], id="m3SimQtyClearLabel", className="font-semibold text-slate-700"),
                                                            html.Span(init_ws["sim_qty_keep_lbl"], id="m3SimQtyKeepLabel", className="text-slate-500"),
                                                        ],
                                                        className="flex items-center justify-between text-[11px] mt-1",
                                                    ),
                                                ],
                                                className="p-2.5 bg-white rounded-xl border border-slate-200/70",
                                            ),
                                        ],
                                        className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3",
                                    ),
                                    # 4 Thẻ Kết quả Dòng tiền mô phỏng
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Span("DOANH THU DỰ KIẾN", className="text-[10px] font-bold uppercase text-slate-500 block"),
                                                    html.Strong(init_ws["sim_revenue"], id="m3SimBoxRevenue", className="text-base font-extrabold text-slate-900 font-code block mt-1"),
                                                    html.Span(init_ws["sim_rev_sub"], id="m3SimBoxRevSub", className="text-[11px] text-slate-500 mt-0.5 block"),
                                                ],
                                                className="p-3 bg-white rounded-xl border border-slate-200",
                                            ),
                                            html.Div(
                                                [
                                                    html.Span("VỐN GỐC THU HỒI", className="text-[10px] font-bold uppercase text-slate-500 block"),
                                                    html.Strong(init_ws["sim_capital"], id="m3SimBoxCapital", className="text-base font-extrabold text-slate-900 cost-val font-code block mt-1"),
                                                    html.Span(init_ws["sim_cap_sub"], id="m3SimBoxCapSub", className="text-[11px] text-slate-500 mt-0.5 block"),
                                                ],
                                                className="p-3 bg-white rounded-xl border border-slate-200",
                                            ),
                                            html.Div(
                                                [
                                                    html.Span("CHI PHÍ QUÀ TẶNG", className="text-[10px] font-bold uppercase text-slate-500 block"),
                                                    html.Strong(init_ws["sim_promo_cost"], id="m3SimBoxPromoCost", className="text-base font-extrabold text-rose-600 cost-val font-code block mt-1"),
                                                    html.Span(init_ws["sim_promo_sub"], id="m3SimBoxPromoSub", className="text-[11px] text-slate-500 mt-0.5 block"),
                                                ],
                                                className="p-3 bg-white rounded-xl border border-slate-200",
                                            ),
                                            html.Div(
                                                [
                                                    html.Span("LỢI NHUẬN GỘP", className="text-[10px] font-bold uppercase text-emerald-700 block"),
                                                    html.Strong(init_ws["sim_net_profit"], id="m3SimBoxNetProfit", className="text-base font-extrabold text-emerald-700 cost-val font-code block mt-1"),
                                                    html.Span(init_ws["sim_profit_sub"], id="m3SimBoxProfitSub", className="text-[11px] text-emerald-700/80 mt-0.5 block"),
                                                ],
                                                className="p-3 bg-emerald-50/70 rounded-xl border border-emerald-200",
                                            ),
                                        ],
                                        className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 mb-3 tabular-nums",
                                    ),
                                    # Footer Phê duyệt & Đẩy lên quầy
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.I(className="ph-fill ph-check-circle text-emerald-600 text-base"),
                                                    html.Span(init_ws["sim_autostop_label"], id="m3AutoStopLabel", className="text-xs font-medium text-slate-700"),
                                                ],
                                                className="inline-flex items-center gap-1.5",
                                            ),
                                            html.Button(
                                                [html.I(className="ph-bold ph-rocket-launch mr-1.5"), "Phê duyệt & Áp dụng lên quầy bán hàng"],
                                                id="btn-m3-approve-pos",
                                                n_clicks=0,
                                                className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold flex items-center justify-center shadow-sm cursor-pointer",
                                            ),
                                        ],
                                        className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-200/80",
                                    ),
                                ],
                                className="mx-3.5 mb-3.5 p-3.5 bg-slate-50 border border-slate-200/80 rounded-xl",
                            ),
                        ],
                        className="xl:col-span-7 bg-white rounded-xl border border-slate-200/90 shadow-2xs flex flex-col overflow-hidden",
                    ),
                    # CỘT PHẢI 5 PHẦN: Radar Giá Thị Trường + Thang định vị + Hero ..90k + Nhận định chiến lược
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.H2("2. RADAR GIÁ THỊ TRƯỜNG", className="text-sm font-bold uppercase tracking-wider text-slate-800"),
                                                    html.Div("ĐMX, MediaMart & Đại lý Online", className="text-[11px] text-slate-500 mt-0.5"),
                                                ]
                                            ),
                                            html.Div(
                                                [
                                                    html.Button("Giả lập mất mạng", id="btn-m3-toggle-offline", n_clicks=0, className=init_ws["offline_btn_cls"]),
                                                    html.Span([html.I(className="ph-bold ph-clock mr-1"), "10 phút trước"], className="px-2 py-1 rounded-lg bg-slate-100 text-slate-600 text-[11px] font-medium inline-flex items-center"),
                                                ],
                                                className="flex items-center gap-1.5 shrink-0",
                                            ),
                                        ],
                                        className="px-4 py-3 border-b border-slate-100 flex items-start justify-between gap-2",
                                    ),
                                    # Banner mất mạng tham chiếu nội bộ
                                    html.Div(
                                        [
                                            html.I(className="ph-fill ph-wifi-slash text-rose-600 text-base shrink-0"),
                                            html.Span("Mất kết nối đối chiếu giá thị trường — Đang sử dụng dữ liệu tham chiếu nội bộ gần nhất."),
                                        ],
                                        id="m3Err003Banner",
                                        style=init_ws["err003_style"],
                                        className="mx-3.5 mt-3 p-2.5 rounded-lg bg-rose-50 border border-rose-200 text-xs font-medium text-rose-800 items-center gap-2",
                                    ),
                                    html.Div(init_ws["competitor_rows"], id="m3CompetitorListContainer", className="p-3.5 space-y-2"),
                                    # Thang định vị giá & Sàn vốn
                                    html.Div(init_ws["price_ruler"], id="m3PricePositionRuler", className="px-4 py-3 border-t border-slate-100 bg-slate-50/50"),
                                    # Khối Đề xuất Giá Xả Tối Ưu viền đỏ chuẩn Ảnh 2
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Span("GIÁ XẢ GỢI Ý TỐI ƯU", className="text-[11px] font-bold uppercase tracking-wider text-rose-700 mr-1.5"),
                                                            html.Span(init_ws["tail_badge"], id="m3SuggestedTailBadge", className="px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200 text-[10px] font-bold font-code"),
                                                        ],
                                                        className="flex items-center flex-wrap gap-1",
                                                    ),
                                                    html.Span(init_ws["suggested_price_text"], id="m3SuggestedPriceHero", className="text-2xl font-extrabold text-rose-600 font-code tabular-nums"),
                                                ],
                                                className="flex items-baseline justify-between gap-2",
                                            ),
                                            html.Div(
                                                [
                                                    html.Span(init_ws["radar_pai_badge"], id="m3RadarPaiBadge", className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 text-[11px] font-semibold"),
                                                    html.Span(init_ws["pai_summary_text"], id="m3SuggestedUnitProfitText", className="text-xs font-bold text-emerald-700 cost-val"),
                                                ],
                                                className="flex items-center justify-between gap-2 mt-1.5",
                                            ),
                                            html.Div(
                                                [
                                                    html.Div(["So ĐMX: ", html.Strong(init_ws["radar_dmx_diff"], id="m3RadarDmxDiff", className="text-slate-900")], className="text-center py-1.5 border-r border-slate-200"),
                                                    html.Div(["So Online: ", html.Strong(init_ws["radar_online_diff"], id="m3RadarOnlineDiff", className="text-slate-900")], className="text-center py-1.5"),
                                                ],
                                                className="grid grid-cols-2 bg-slate-50 rounded-lg border border-slate-200/70 text-[11px] text-slate-600 my-2.5",
                                            ),
                                            html.Div(
                                                [
                                                    html.Button(init_ws["sync_btn_label"], id="m3SyncRadarPriceBtn", n_clicks=0, className="flex-1 py-2 px-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold cursor-pointer transition"),
                                                    html.Button([html.I(className="ph-bold ph-tag mr-1"), "Tem giá"], id="btn-m3-open-price-tag", n_clicks=0, className="px-3 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold cursor-pointer inline-flex items-center"),
                                                ],
                                                className="flex items-center gap-2",
                                            ),
                                        ],
                                        className="mx-3.5 mb-3.5 p-3.5 rounded-xl bg-white border-2 border-rose-400 shadow-xs",
                                    ),
                                ],
                                className="bg-white rounded-xl border border-slate-200/90 shadow-2xs overflow-hidden",
                            ),
                            # Khối Nhận định chiến lược từ Hệ thống
                            html.Div(
                                init_ws["strategic_insight"],
                                id="m3StrategicInsightBox",
                                className="bg-white rounded-xl border border-slate-200/90 shadow-2xs p-4",
                            ),
                        ],
                        className="xl:col-span-5 space-y-4",
                    ),
                ],
                className="grid grid-cols-1 xl:grid-cols-12 gap-4 items-start shrink-0",
            ),
        ],
    )
