"""
Khung giao diện App Shell chuẩn Prototype HTML (Sidebar 216px/68px, Topbar 56px, Quick Search Modal & Toast).
"""
from typing import Any, Dict, List, Optional
from dash import dcc, html

MODULE_KEYS = ("m1", "m2", "m3", "m4", "m5", "m6")

SIDEBAR_NAV_ACTIVE_CLASS = (
    "nav-tab-btn w-full flex items-center justify-between gap-2 px-2.5 py-2 rounded-lg "
    "font-semibold bg-blue-50/90 text-blue-700 border-l-[3px] border-blue-600 transition cursor-pointer"
)
SIDEBAR_NAV_IDLE_CLASS = (
    "nav-tab-btn w-full flex items-center justify-between gap-2 px-2.5 py-2 rounded-lg "
    "font-medium text-slate-600 hover:bg-slate-100/80 hover:text-slate-900 transition cursor-pointer"
)

SIDEBAR_EXPANDED_CLASS = (
    "w-[216px] shrink-0 bg-white border-r border-slate-200/90 flex flex-col "
    "justify-between h-full select-none z-30 overflow-hidden"
)
SIDEBAR_COLLAPSED_CLASS = f"{SIDEBAR_EXPANDED_CLASS} sidebar-collapsed"

ROLE_BTN_ACTIVE_CLASS = (
    "px-2.5 py-1 rounded-md font-semibold bg-white text-slate-900 shadow-2xs transition cursor-pointer whitespace-nowrap"
)
ROLE_BTN_IDLE_CLASS = (
    "px-2.5 py-1 rounded-md font-medium text-slate-500 hover:text-slate-900 transition cursor-pointer whitespace-nowrap"
)


def format_vnd_compact(value: Optional[float], role: str = "ROLE_OWNER") -> str:
    """Định dạng tiền tệ rút gọn chuẩn Prototype (1,30 tỷ / 929,6 tr) kèm bảo mật ROLE_SALES."""
    if role == "ROLE_SALES" or value is None:
        return "****** đ"
    sign = "-" if value < 0 else ""
    abs_val = abs(float(value))
    if abs_val >= 1_000_000_000:
        return f"{sign}{abs_val / 1_000_000_000:.2f}".replace(".", ",") + " tỷ"
    if abs_val >= 1_000_000:
        return f"{sign}{abs_val / 1_000_000:.1f}".replace(".", ",") + " tr"
    return f"{sign}{abs_val:,.0f} đ"


def format_vnd_full(value: Optional[float], role: str = "ROLE_OWNER") -> str:
    """Định dạng tiền tệ đầy đủ VNĐ kèm bảo mật ROLE_SALES."""
    if role == "ROLE_SALES" or value is None:
        return "****** đ"
    return f"{value:,.0f} đ"


def _compute_sidebar_counts(services: Dict[str, Any]) -> Dict[str, Any]:
    """Lấy số đếm badge thực tế từ DB cho Sidebar."""
    try:
        alert_kpis = services["alert"].get_alert_kpis(role="ROLE_OWNER")
        m2_cnt = alert_kpis.get("total_slow_skus", 0) + alert_kpis.get("stockout_risk_skus", 0)
        clear_cnt = len(services["clearance"].get_clearance_candidates(role="ROLE_OWNER")[:4])
        rep_plan = services["replenishment"].get_replenishment_recommendations(role="ROLE_OWNER")
        m4_cnt = len(services["replenishment"].preview_po_grouping(rep_plan["items"]))
        crm_kpis = services["crm"].get_crm_kpis()
        m5_cnt = crm_kpis.get("due_today_count", 0)
        return {"m2": m2_cnt, "m3": clear_cnt, "m4": max(1, m4_cnt), "m5": m5_cnt}
    except Exception:
        return {"m2": 8, "m3": 4, "m4": 3, "m5": 18}


def build_sidebar(services: Dict[str, Any], active_tab: str = "m1") -> html.Aside:
    """Dựng Sidebar trái 216px thu gọn được thành 68px khớp Prototype L224-L369."""
    counts = _compute_sidebar_counts(services)

    nav_specs = [
        ("m1", "Tổng quan kho", "ph-squares-four", None, None),
        ("m2", "Cần xử lý hôm nay", "ph-warning", f"{counts['m2']}", "px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-600 text-white tabular-nums shrink-0"),
        ("m3", "Gợi ý xả hàng", "ph-trend-down", f"{counts['m3']} mã", "px-1.5 py-0.5 rounded text-[10px] font-semibold bg-amber-100 text-amber-800 tabular-nums shrink-0"),
        ("m4", "Gợi ý nhập hàng", "ph-shopping-cart", f"{counts['m4']} đơn", "px-1.5 py-0.5 rounded text-[10px] font-semibold bg-blue-100 text-blue-700 tabular-nums shrink-0"),
        ("m5", "Chăm sóc khách hàng", "ph-users-three", f"{counts['m5']}", "px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-100 text-emerald-700 tabular-nums shrink-0"),
        ("m6", "Hiệu quả kinh doanh", "ph-chart-bar", None, None),
    ]

    nav_items = []
    for key, label, icon_cls, badge_txt, badge_cls in nav_specs:
        is_act = key == active_tab
        left_part = html.Span(
            [
                html.I(className=f"ph-bold {icon_cls} text-base shrink-0 {'text-blue-600' if is_act else 'text-slate-400'}"),
                html.Span(label, className="sidebar-label truncate"),
            ],
            className="flex items-center gap-2.5 min-w-0",
        )
        btn_children: List[Any] = [left_part]
        if badge_txt:
            btn_children.append(html.Span(badge_txt, className=f"sidebar-badge {badge_cls}"))
            dot_color = "bg-rose-600" if key == "m2" else ("bg-amber-500" if key == "m3" else ("bg-blue-600" if key == "m4" else "bg-emerald-500"))
            btn_children.append(html.Span(className=f"sidebar-mini-dot hidden absolute top-1.5 right-3 w-2 h-2 rounded-full {dot_color}"))

        nav_items.append(
            html.Li(
                html.Button(
                    btn_children,
                    id=f"btn-nav-{key}",
                    n_clicks=0,
                    title=label,
                    className=SIDEBAR_NAV_ACTIVE_CLASS if is_act else SIDEBAR_NAV_IDLE_CLASS,
                )
            )
        )

    quick_items = [
        ("btn-quick-serial", "Đối soát Serial / IMEI", "ph-qr-code"),
        ("btn-quick-po", "Đơn nhập & Giữ cọc", "ph-file-text"),
        ("btn-quick-threshold", "Thiết lập định mức", "ph-sliders"),
    ]
    quick_lis = [
        html.Li(
            html.Button(
                [
                    html.I(className=f"ph-bold {q_icon} text-base shrink-0 text-slate-400"),
                    html.Span(q_label, className="sidebar-label truncate"),
                ],
                id=q_id,
                n_clicks=0,
                title=q_label,
                className="sidebar-quick-btn w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg font-medium text-slate-600 hover:bg-slate-100/80 hover:text-slate-900 transition cursor-pointer",
            )
        )
        for q_id, q_label, q_icon in quick_items
    ]

    return html.Aside(
        id="appSidebar",
        className=SIDEBAR_EXPANDED_CLASS,
        children=[
            html.Div(
                [
                    # Brand Header + Collapse toggle
                    html.Div(
                        [
                            html.Button(
                                [
                                    html.Div(
                                        html.I(className="ph-bold ph-cube text-base"),
                                        className="w-8 h-8 rounded-lg bg-slate-900 text-white flex items-center justify-center shrink-0 shadow-sm",
                                    ),
                                    html.Div(
                                        [
                                            html.Div("Stock Sense", className="text-[14px] font-bold tracking-tight text-slate-900 leading-none text-left"),
                                            html.Div("Quản lý kho điện máy", className="text-[11px] text-slate-400 font-medium mt-1 truncate"),
                                        ],
                                        className="sidebar-label min-w-0",
                                    ),
                                ],
                                id="btn-brand-home",
                                n_clicks=0,
                                className="flex items-center gap-2.5 min-w-0 cursor-pointer bg-transparent border-0 p-0",
                            ),
                            html.Button(
                                html.I(id="collapseIcon", className="ph-bold ph-caret-double-left text-sm"),
                                id="sidebarToggleBtn",
                                n_clicks=0,
                                title="Thu gọn / Mở rộng thanh điều hướng (Ctrl+B)",
                                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition shrink-0 cursor-pointer",
                            ),
                        ],
                        className="h-14 px-3.5 border-b border-slate-100 flex items-center justify-between gap-2",
                    ),
                    # Navigation Groups
                    html.Nav(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        "Vận hành kho & Dòng tiền",
                                        className="sidebar-section-header px-2.5 mb-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-400",
                                    ),
                                    html.Ul(nav_items, id="masterSidebarNav", className="space-y-1 text-[13px]"),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        "Quản lý nghiệp vụ",
                                        className="sidebar-section-header px-2.5 mb-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-400",
                                    ),
                                    html.Ul(quick_lis, className="space-y-1 text-[13px]"),
                                ],
                                className="pt-3 border-t border-slate-100",
                            ),
                        ],
                        className="p-2.5 space-y-5 overflow-y-auto no-scrollbar",
                    ),
                ]
            ),
            # Bottom KiotViet Sync Card
            html.Div(
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(className="w-2 h-2 rounded-full bg-emerald-500 shrink-0"),
                                html.Div(
                                    [
                                        html.Div("Đồng bộ KiotViet", className="text-[11px] font-semibold text-slate-800 truncate"),
                                        html.Div("Vừa xong · CN01", id="syncTimeText", className="text-[10px] text-slate-500 truncate"),
                                    ],
                                    className="sidebar-label min-w-0",
                                ),
                            ],
                            className="sidebar-sync-info flex items-center gap-2 min-w-0",
                        ),
                        html.Button(
                            html.I(className="ph-bold ph-arrows-clockwise text-xs"),
                            id="btn-sync-kiotviet",
                            n_clicks=0,
                            title="Đồng bộ dữ liệu KiotViet ngay",
                            className="p-1.5 rounded-lg bg-white hover:bg-slate-50 text-slate-600 border border-slate-200/90 shadow-2xs transition shrink-0 cursor-pointer",
                        ),
                    ],
                    className="sidebar-sync-card p-2.5 rounded-xl bg-slate-100/80 border border-slate-200/70 flex items-center justify-between gap-2",
                ),
                className="p-2.5 border-t border-slate-100",
            ),
        ],
    )


def build_topbar(role: str = "ROLE_OWNER") -> html.Header:
    """Dựng Topbar 56px khớp Prototype L377-L432."""
    is_owner = role != "ROLE_SALES"
    return html.Header(
        [
            # Left: Store & Branch Selector
            html.Div(
                html.Div(
                    [
                        html.Span(className="w-2 h-2 rounded-full bg-emerald-500 shrink-0"),
                        html.Span("Điện Máy Anh Tâm", className="font-bold text-slate-900 whitespace-nowrap"),
                        html.Span("·", className="text-slate-400"),
                        dcc.Dropdown(
                            id="branchSelect",
                            options=[
                                {"label": "Kho 108 Cầu Giấy (CN01)", "value": "CN01"},
                            ],
                            value="CN01",
                            clearable=False,
                            className="text-xs min-w-[175px] font-medium text-slate-600",
                        ),
                    ],
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-50 border border-slate-200/80 text-xs",
                ),
                className="flex items-center gap-2 shrink-0",
            ),
            # Center: Ctrl+K Quick Search Button
            html.Button(
                [
                    html.Span(
                        [
                            html.I(className="ph ph-magnifying-glass text-slate-400 text-sm shrink-0"),
                            html.Span("Tra cứu nhanh Serial, Hóa đơn...", className="truncate"),
                        ],
                        className="inline-flex items-center gap-2 min-w-0",
                    ),
                    html.Kbd("Ctrl K", className="px-1.5 py-0.5 rounded bg-white border border-slate-200 text-[10px] font-semibold text-slate-500 shrink-0"),
                ],
                id="btn-open-quick-search",
                n_clicks=0,
                className="hidden md:inline-flex items-center justify-between gap-3 px-3 py-1.5 rounded-lg bg-slate-100/80 hover:bg-slate-100 border border-slate-200/80 text-xs text-slate-500 transition flex-1 max-w-[270px] min-w-[180px] cursor-pointer whitespace-nowrap",
            ),
            # Right: RBAC Switcher + Notification Bell + Profile AT
            html.Div(
                [
                    html.Div(
                        [
                            html.Button(
                                "Chủ cửa hàng (Xem vốn)",
                                id="btn-role-owner",
                                n_clicks=0,
                                className=ROLE_BTN_ACTIVE_CLASS if is_owner else ROLE_BTN_IDLE_CLASS,
                            ),
                            html.Button(
                                "Bán hàng (Ẩn vốn)",
                                id="btn-role-sales",
                                n_clicks=0,
                                className=ROLE_BTN_IDLE_CLASS if is_owner else ROLE_BTN_ACTIVE_CLASS,
                            ),
                        ],
                        title="Chuyển chế độ bảo mật giá vốn theo vai trò RBAC",
                        className="inline-flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200/80 text-xs",
                    ),
                    html.Button(
                        [
                            html.I(className="ph-bold ph-bell text-base"),
                            html.Span(className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-600 ring-2 ring-white"),
                        ],
                        id="btn-topbar-bell",
                        n_clicks=0,
                        title="Cảnh báo tồn kho & đứt hàng hôm nay",
                        className="relative p-2 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition cursor-pointer",
                    ),
                    html.Span(className="h-5 w-px bg-slate-200"),
                    html.Div(
                        [
                            html.Div(
                                "AT",
                                className="w-8 h-8 rounded-full bg-slate-900 text-white text-xs font-bold flex items-center justify-center shrink-0",
                            ),
                            html.Div(
                                [
                                    html.Div("Nguyễn Anh Tâm", className="text-xs font-bold text-slate-900"),
                                    html.Div(
                                        "Chủ cửa hàng" if is_owner else "Nhân viên bán hàng",
                                        id="userRoleSubtitle",
                                        className="text-[11px] text-slate-500",
                                    ),
                                ],
                                className="hidden xl:block leading-tight",
                            ),
                        ],
                        className="flex items-center gap-2.5",
                    ),
                ],
                className="flex items-center gap-3 shrink-0",
            ),
        ],
        className="h-14 bg-white border-b border-slate-200/90 px-4 flex items-center justify-between gap-3 shrink-0 z-20",
    )


def build_quick_search_modal() -> html.Div:
    """Modal tra cứu nhanh toàn cục (Ctrl+K) khớp Prototype L2585-L2599."""
    return html.Div(
        id="quickSearchModal",
        style={"display": "none"},
        className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-50 items-start justify-center pt-20 p-4 flex",
        children=html.Div(
            className="bg-white rounded-2xl max-w-lg w-full border border-slate-200 shadow-2xl overflow-hidden",
            children=[
                html.Div(
                    [
                        html.Span("search", className="material-symbols-outlined text-slate-400 text-[18px]"),
                        dcc.Input(
                            id="quickSearchInput",
                            type="text",
                            debounce=True,
                            placeholder="Tìm nhanh theo Mã SKU, Serial (SN-...), hoặc Mã đơn (DH...)...",
                            className="w-full text-xs text-slate-900 placeholder-slate-400 focus:outline-none border-0 bg-transparent",
                        ),
                        html.Button(
                            "ESC",
                            id="btn-close-quick-search",
                            n_clicks=0,
                            className="px-1.5 py-0.5 rounded bg-slate-100 hover:bg-slate-200 text-[10px] font-semibold text-slate-500 cursor-pointer",
                        ),
                    ],
                    className="px-4 py-3 border-b border-slate-200 flex items-center gap-2",
                ),
                html.Div(
                    id="quickSearchResults",
                    className="p-3 max-h-80 overflow-y-auto divide-y divide-slate-100 text-xs",
                ),
            ],
        ),
    )


def build_toast() -> html.Div:
    """Thông báo Toast nổi góc dưới phải."""
    return html.Div(
        id="toast",
        style={"display": "none"},
        className="fixed bottom-5 right-5 bg-slate-900 text-white text-xs px-3.5 py-2.5 rounded-xl shadow-xl items-center gap-2 z-[70] border border-slate-700 flex",
        children=[
            html.Span("check_circle", id="toastIcon", className="material-symbols-outlined text-emerald-400 text-[18px]"),
            html.Span("Thao tác thành công", id="toastMessage"),
            html.Button("✕", id="btn-close-toast", n_clicks=0, className="ml-2 text-slate-400 hover:text-white cursor-pointer"),
        ],
    )


def _default_placeholder_panel(tab_key: str, title: str, active: bool) -> html.Main:
    return html.Main(
        html.Div(
            [
                html.H2(title, className="text-lg font-bold text-slate-900"),
                html.P(f"Phân hệ {tab_key.upper()} đang được nạp...", className="text-xs text-slate-500 mt-1"),
            ],
            className="bg-white border border-slate-200 rounded-xl p-6",
        ),
        id=f"panel-{tab_key}",
        style={"display": "flex" if active else "none"},
        className="tab-panel flex-1 flex-col min-w-0 bg-[#F8FAFC] overflow-y-auto custom-scrollbar px-5 py-4 gap-4",
    )


def build_app_shell(
    services: Dict[str, Any],
    active_tab: str = "m1",
    role: str = "ROLE_OWNER",
    page_panels: Optional[Dict[str, Any]] = None,
    extra_overlays: Optional[List[Any]] = None,
) -> html.Div:
    """Lắp ghép hoàn chỉnh Khung Giao diện Stock Sense ERP chuẩn Prototype."""
    panel_titles = {
        "m1": "Tổng quan Kho & Danh mục Thiết bị",
        "m2": "Cần xử lý hôm nay",
        "m3": "Gợi ý xả hàng & Định giá cạnh tranh",
        "m4": "Gợi ý nhập hàng & Cân đối ngân sách",
        "m5": "Chăm sóc khách hàng & Đặt lịch bảo dưỡng",
        "m6": "Hiệu quả kinh doanh & Thác nước Lợi nhuận",
    }
    panels = []
    for key in MODULE_KEYS:
        if page_panels and key in page_panels:
            panels.append(page_panels[key])
        else:
            panels.append(_default_placeholder_panel(key, panel_titles[key], active=(key == active_tab)))

    children: List[Any] = [
        # Global Shared Stores (Single Source of Truth)
        dcc.Store(id="store-active-tab", data=active_tab),
        dcc.Store(id="store-role", data=role),
        dcc.Store(id="store-selected-sku", data="TV-LG-55C3"),
        dcc.Store(id="store-sidebar-collapsed", data=False),
        dcc.Store(id="store-quick-action", data=None),
        dcc.Store(id="store-toast", data={"open": False, "message": "", "kind": "success"}),
        dcc.Store(id="store-refresh-tick", data=0),
        # Left Collapsible Sidebar
        build_sidebar(services, active_tab=active_tab),
        # Right Workspace Stage: Topbar + 6 Module Panels
        html.Div(
            [build_topbar(role=role), *panels],
            className="flex-1 flex flex-col min-w-0 h-full overflow-hidden bg-[#F8FAFC] relative",
        ),
        build_quick_search_modal(),
        build_toast(),
    ]
    if extra_overlays:
        children.extend(extra_overlays)

    return html.Div(
        children,
        className="h-screen overflow-hidden flex bg-slate-50 text-slate-900 font-body-md text-body-md antialiased",
    )
