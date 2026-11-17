"""
Giao diện Module 03: Gợi ý xả hàng & Định giá cạnh tranh (Plotly Dash - Khớp 1:1 Prototype L920-L1295 & L2840-L2916).
"""
from typing import Any, Dict
from dash import dcc, html

from src.dash_app.components.charts import empty_figure


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
                                            html.Span("TV-LG-55C3", id="m3TagSkuCode", className="text-[11px] font-mono bg-rose-800/80 px-2 py-0.5 rounded"),
                                        ],
                                        className="bg-rose-600 text-white px-4 py-2 flex items-center justify-between",
                                    ),
                                    html.Div(
                                        [
                                            html.Div("Smart Tivi OLED LG 4K 55 inch 55C3PSA", id="m3TagProductName", className="font-bold text-sm text-slate-900 leading-snug"),
                                            html.Div(
                                                [
                                                    html.Div([html.Div("Giá niêm yết cũ:", className="text-[11px] text-slate-400"), html.Div("27.990.000 đ", id="m3TagOldPrice", className="text-sm font-semibold text-slate-400 line-through")]),
                                                    html.Div([html.Div("GIÁ XẢ ĐẶC BIỆT", className="text-[10px] font-bold uppercase text-rose-600"), html.Div("26.990.000 đ", id="m3TagNewPrice", className="text-2xl font-extrabold text-rose-600")], className="text-right"),
                                                ],
                                                className="flex items-baseline justify-between border-y border-dashed border-slate-200 py-2.5 tabular-nums whitespace-nowrap",
                                            ),
                                            html.Div(
                                                [html.I(className="ph-fill ph-gift text-amber-600 text-base shrink-0"), html.Span("Combo Tivi + Giá treo + Công lắp đặt", id="m3TagPromoNote", className="font-semibold")],
                                                className="bg-amber-50 border border-amber-200/80 rounded-lg p-2.5 text-xs text-amber-900 flex items-center gap-2",
                                            ),
                                            html.Div(
                                                [html.Span("Điện Máy Anh Tâm · 108 Cầu Giấy"), html.Span([html.I(className="ph-bold ph-qr-code text-sm"), " Quét tra Serial"], className="font-semibold text-slate-700 flex items-center gap-1")],
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
    """Dựng màn hình chính Module 03 khớp Prototype L920-L1295."""
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
                            html.Div([html.Span(init_ws["kpi_recovery"], id="m3KpiTotalRecovery", className="text-2xl font-bold tracking-tight text-slate-900 cost-val"), html.Span(init_ws["kpi_qty_sub"], id="m3KpiQtySub", className="text-xs font-medium text-slate-400")], className="my-1 flex items-baseline flex-wrap gap-x-2 gap-y-0.5 tabular-nums"),
                            html.Div([html.Span("Tiền mặt gốc quay về két", className="text-slate-400"), html.Span("Giải phóng diện tích kho", className="font-semibold text-indigo-600")], className="pt-2 border-t border-slate-100 flex flex-col gap-0.5 text-xs"),
                        ],
                        className="kpi-card bg-white rounded-xl p-4 min-h-[146px] border border-slate-200/90 shadow-2xs flex flex-col justify-between gap-2",
                    ),
                    html.Div(
                        [
                            html.Div([html.Span([html.Span(className="w-2 h-2 rounded-full bg-emerald-500 shrink-0"), html.Span("LỢI NHUẬN GỘP KỲ VỌNG")], className="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5"), html.Span(init_ws["kpi_roi_badge"], id="m3KpiMarginPill", className="bg-emerald-50 text-emerald-700 border border-emerald-200/70 text-[11px] font-semibold px-2 py-0.5 rounded shrink-0")], className="flex items-center justify-between gap-2"),
                            html.Div([html.Span(init_ws["kpi_profit"], id="m3KpiTotalProfit", className="text-2xl font-bold tracking-tight text-emerald-600 cost-val"), html.Span("Bảo toàn lãi dương", className="text-xs font-medium text-slate-400")], className="my-1 flex items-baseline flex-wrap gap-x-2 gap-y-0.5 tabular-nums"),
                            html.Div([html.Span("Ưu tiên Combo phụ kiện PA2", className="text-slate-400"), html.Span("Không phá giá máy chính", className="font-semibold text-emerald-700")], className="pt-2 border-t border-slate-100 flex flex-col gap-0.5 text-xs"),
                        ],
                        className="kpi-card bg-white rounded-xl p-4 min-h-[146px] border border-slate-200/90 shadow-2xs flex flex-col justify-between gap-2",
                    ),
                    html.Div(
                        [
                            html.Div([html.Span([html.Span(className="w-2 h-2 rounded-full bg-amber-500 shrink-0"), html.Span("LỢI THẾ GIÁ SO VỚI ĐỐI THỦ")], className="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5"), html.Span([html.I(className="ph-fill ph-fire text-amber-600 mr-1"), "Ưu thế"], className="bg-amber-50 text-amber-800 border border-amber-200/70 text-[11px] font-semibold px-2 py-0.5 rounded flex items-center shrink-0")], className="flex items-center justify-between gap-2"),
                            html.Div([html.Span(init_ws["kpi_pai_text"], id="m3KpiPaiHero", className="text-2xl font-bold tracking-tight text-amber-600"), html.Span("so với TB thị trường", className="text-xs font-medium text-slate-400")], className="my-1 flex items-baseline flex-wrap gap-x-2 gap-y-0.5 tabular-nums"),
                            html.Div([html.Span("Đối chiếu ĐMX, MediaMart, Shopee", className="text-slate-400"), html.Span("Làm tròn tâm lý ..50k / ..90k", className="text-emerald-700 font-semibold")], className="pt-2 border-t border-slate-100 flex flex-col gap-0.5 text-xs"),
                        ],
                        className="kpi-card bg-white rounded-xl p-4 min-h-[146px] border border-slate-200/90 shadow-2xs flex flex-col justify-between gap-2",
                    ),
                    html.Div(
                        id="btn-m3-open-campaign-modal",
                        n_clicks=0,
                        className="kpi-card cursor-pointer bg-white rounded-xl p-4 min-h-[146px] border border-slate-200/90 hover:border-slate-300 shadow-2xs flex flex-col justify-between gap-2 group",
                        children=[
                            html.Div([html.Span([html.Span(className="w-2 h-2 rounded-full bg-blue-600 shrink-0"), html.Span("CHIẾN DỊCH XẢ ĐANG CHẠY")], className="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5"), html.Span("Đồng bộ PoS", className="bg-blue-50 text-blue-700 border border-blue-200/70 text-[11px] font-semibold px-2 py-0.5 rounded shrink-0")], className="flex items-center justify-between gap-2"),
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
                            html.Span([html.I(className="ph-bold ph-crosshair text-indigo-600 text-sm mr-1.5"), "CHỌN THIẾT BỊ XẢ TỒN ĐỂ PHÂN TÍCH KỊCH BẢN & ĐỊNH GIÁ (4 MÃ ĐỀ XUẤT)"], className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center"),
                            html.Span("Click vào thẻ để chuyển đổi kịch bản & Radar bên dưới", className="text-xs text-slate-400 hidden xl:inline"),
                        ],
                        className="flex items-center justify-between mb-2.5 px-1 whitespace-nowrap",
                    ),
                    html.Div(init_ws["sku_cards"], id="m3SkuSelectorGrid", className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3"),
                ],
                className="bg-white rounded-xl p-3.5 border border-slate-200/90 shadow-2xs shrink-0",
            ),
            # 4. Split Analytical Workspace (7 cols Left + 5 cols Right)
            html.Section(
                [
                    # LEFT COLUMN: 4 Tactics + Cashflow Simulator
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div([html.H2("1. Chọn kịch bản khuyến mại xả hàng", className="text-sm font-bold uppercase tracking-wider text-slate-800"), html.Span("TV-LG-55C3", id="m3SelectedSkuHeaderBadge", className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-slate-200/80 text-slate-800")], className="flex items-center flex-wrap gap-2"),
                                    html.P("Chọn phương án xả tồn tối ưu tốc độ bán hoặc bảo toàn biên lợi nhuận.", className="text-xs text-slate-500 mt-1"),
                                ],
                                className="px-4 py-3 border-b border-slate-200/80 bg-slate-50/60",
                            ),
                            html.Div(init_ws["tactic_cards"], id="m3TacticsContainer", className="p-3.5 space-y-2"),
                            # Banners (Role Sales Lock & Loss Protection)
                            html.Div(
                                [html.I(className="ph-fill ph-lock text-amber-600 text-base"), html.Span("Chế độ Bán hàng (ROLE_SALES): Giá vốn, tổng vốn thu hồi và lãi gộp bị ẩn; không được phê duyệt giá cắt lỗ (ERR_CLR_001).")],
                                id="m3SalesLockBanner",
                                style=init_ws["sales_lock_style"],
                                className="mx-3.5 mb-2 p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-900 items-center gap-2",
                            ),
                            html.Div(
                                [html.I(className="ph-fill ph-warning-octagon text-rose-600 text-base"), html.Span("CẢNH BÁO CẮT LỖ: Kịch bản đang mô phỏng có lợi nhuận gộp ròng âm! Yêu cầu ROLE_OWNER phê duyệt.")],
                                id="m3CapitalProtectionBanner",
                                style=init_ws["cap_protect_style"],
                                className="mx-3.5 mb-2 p-2.5 rounded-lg bg-rose-50 border border-rose-300 text-xs font-semibold text-rose-800 items-center gap-2",
                            ),
                            # Interactive Simulator Box
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div([html.Label("Tỷ lệ giảm giá bổ sung (%):", className="text-[11px] font-semibold text-slate-600"), dcc.Slider(id="m3-discount-slider", min=0, max=30, step=1, value=0, marks={0: "0%", 10: "10%", 20: "20%", 30: "30%"})]),
                                            html.Div([html.Label("Số lượng xả mục tiêu (Máy):", className="text-[11px] font-semibold text-slate-600 block mb-1"), dcc.Input(id="m3-qty-input", type="number", min=1, max=50, step=1, value=10, className="w-full px-3 py-1.5 text-xs font-bold rounded-lg border border-slate-300")]),
                                        ],
                                        className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3",
                                    ),
                                    html.Div(
                                        [
                                            html.Div([html.Span("Doanh thu dự kiến", className="text-[11px] text-slate-500 block"), html.Strong(init_ws["sim_revenue"], id="m3SimBoxRevenue", className="text-sm font-bold text-slate-900")], className="p-2.5 bg-white rounded-lg border border-slate-200"),
                                            html.Div([html.Span("Vốn hoàn về két", className="text-[11px] text-slate-500 block"), html.Strong(init_ws["sim_capital"], id="m3SimBoxCapital", className="text-sm font-bold text-slate-900 cost-val")], className="p-2.5 bg-white rounded-lg border border-slate-200"),
                                            html.Div([html.Span("Chi phí khuyến mại", className="text-[11px] text-slate-500 block"), html.Strong(init_ws["sim_promo_cost"], id="m3SimBoxPromoCost", className="text-sm font-bold text-amber-700 cost-val")], className="p-2.5 bg-white rounded-lg border border-slate-200"),
                                            html.Div([html.Span("Lãi gộp ròng & ROI", className="text-[11px] text-slate-500 block"), html.Strong(init_ws["sim_net_profit"], id="m3SimBoxNetProfit", className="text-sm font-bold text-emerald-700 cost-val")], className="p-2.5 bg-emerald-50/70 rounded-lg border border-emerald-200"),
                                        ],
                                        className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-3 tabular-nums",
                                    ),
                                    html.Button(
                                        [html.I(className="ph-bold ph-rocket-launch mr-1.5"), "PHÊ DUYỆT & ĐẨY LÊN POS ANH TÂM"],
                                        id="btn-m3-approve-pos",
                                        n_clicks=0,
                                        className="w-full py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold flex items-center justify-center shadow-sm cursor-pointer",
                                    ),
                                ],
                                className="mx-3.5 mb-3.5 p-3.5 bg-slate-50 border border-slate-200/80 rounded-xl",
                            ),
                        ],
                        className="xl:col-span-7 bg-white rounded-xl border border-slate-200/90 shadow-2xs flex flex-col overflow-hidden",
                    ),
                    # RIGHT COLUMN: Tactics Comparison Chart + Price Radar
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2("2. So sánh dòng tiền 4 chiến thuật", className="text-sm font-bold uppercase tracking-wider text-slate-800 px-4 pt-3.5"),
                                    dcc.Graph(id="m3-tactic-chart", figure=init_ws["tactic_fig"], config={"displayModeBar": False}, className="px-2 pb-2"),
                                ],
                                className="bg-white rounded-xl border border-slate-200/90 shadow-2xs overflow-hidden",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H2("3. Radar Đối chiếu Giá Thị Trường", className="text-sm font-bold uppercase tracking-wider text-slate-800"),
                                            html.Span("API ĐMX · MediaMart · Shopee", className="text-[11px] text-slate-400"),
                                        ],
                                        className="px-4 py-3 border-b border-slate-100 flex items-center justify-between",
                                    ),
                                    html.Div(init_ws["competitor_rows"], id="m3CompetitorListContainer", className="p-3.5 space-y-2"),
                                    html.Div(
                                        [
                                            html.Div([html.Span("GIÁ XẢ GỢI Ý TỐI ƯU (LÀM TRÒN TÂM LÝ):", className="text-[10px] font-bold uppercase text-indigo-700 block"), html.Span(init_ws["suggested_price_text"], id="m3SuggestedPriceHero", className="text-xl font-extrabold text-slate-900 tabular-nums")]),
                                            html.Div([html.Span(init_ws["pai_summary_text"], id="m3SuggestedUnitProfitText", className="text-xs font-semibold text-emerald-700 block text-right")]),
                                        ],
                                        className="mx-3.5 mb-3.5 p-3 rounded-xl bg-indigo-50/80 border border-indigo-200 flex items-center justify-between gap-2",
                                    ),
                                ],
                                className="bg-white rounded-xl border border-slate-200/90 shadow-2xs overflow-hidden",
                            ),
                        ],
                        className="xl:col-span-5 space-y-4",
                    ),
                ],
                className="grid grid-cols-1 xl:grid-cols-12 gap-4 items-start shrink-0",
            ),
        ],
    )
