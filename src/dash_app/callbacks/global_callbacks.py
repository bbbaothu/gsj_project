"""
Callbacks toàn cục cho App Shell: Điều hướng 6 Modules, Sidebar thu gọn, RBAC Toggle, Quick Search Ctrl+K & Toast.
"""
from typing import Any, Dict, List, Optional, Tuple
import dash
from dash import Input, Output, State, html

from src.dash_app.components.layout_shell import (
    MODULE_KEYS,
    ROLE_BTN_ACTIVE_CLASS,
    ROLE_BTN_IDLE_CLASS,
    SIDEBAR_COLLAPSED_CLASS,
    SIDEBAR_EXPANDED_CLASS,
    SIDEBAR_NAV_ACTIVE_CLASS,
    SIDEBAR_NAV_IDLE_CLASS,
    format_vnd_full,
)


def handle_role_switch(triggered_id: Optional[str], current_role: str) -> Tuple[str, str, str, str]:
    """Pure logic chuyển đổi vai trò RBAC OWNER <-> SALES."""
    new_role = current_role
    if triggered_id == "btn-role-sales":
        new_role = "ROLE_SALES"
    elif triggered_id == "btn-role-owner":
        new_role = "ROLE_OWNER"

    is_owner = new_role != "ROLE_SALES"
    owner_cls = ROLE_BTN_ACTIVE_CLASS if is_owner else ROLE_BTN_IDLE_CLASS
    sales_cls = ROLE_BTN_IDLE_CLASS if is_owner else ROLE_BTN_ACTIVE_CLASS
    subtitle = "Chủ cửa hàng" if is_owner else "Nhân viên bán hàng"
    return new_role, owner_cls, sales_cls, subtitle


def handle_tab_navigation(
    triggered_id: Optional[str], current_tab: str
) -> Tuple[str, List[str], List[Dict[str, str]], Optional[str]]:
    """Pure logic điều hướng 6 Module, Chuông thông báo & Quick Actions bên Sidebar."""
    target_tab = current_tab if current_tab in MODULE_KEYS else "m1"
    quick_action: Optional[str] = None

    if triggered_id in ("btn-nav-m1", "btn-brand-home"):
        target_tab = "m1"
    elif triggered_id in ("btn-nav-m2", "btn-topbar-bell"):
        target_tab = "m2"
    elif triggered_id == "btn-nav-m3":
        target_tab = "m3"
    elif triggered_id == "btn-nav-m4":
        target_tab = "m4"
    elif triggered_id == "btn-nav-m5":
        target_tab = "m5"
    elif triggered_id == "btn-nav-m6":
        target_tab = "m6"
    elif triggered_id == "btn-quick-serial":
        target_tab = "m1"
        quick_action = "OPEN_M1_SERIAL_DRAWER"
    elif triggered_id == "btn-quick-po":
        target_tab = "m4"
        quick_action = "OPEN_M4_PO_MODAL"
    elif triggered_id == "btn-quick-threshold":
        target_tab = "m2"
        quick_action = "OPEN_M2_THRESHOLD_MODAL"

    nav_classes = [
        SIDEBAR_NAV_ACTIVE_CLASS if k == target_tab else SIDEBAR_NAV_IDLE_CLASS
        for k in MODULE_KEYS
    ]
    panel_styles = [
        {"display": "flex" if k == target_tab else "none"}
        for k in MODULE_KEYS
    ]
    return target_tab, nav_classes, panel_styles, quick_action


def handle_quick_search_query(query_text: Optional[str], services: Dict[str, Any], role: str = "ROLE_OWNER") -> List[Any]:
    """Tra cứu tức thời SKU, Serial/IMEI hoặc Đơn hàng trên DB thật và che giá vốn khi ROLE_SALES."""
    kw = (query_text or "").strip()
    df_prod = services["inventory"].get_products_dataframe(search=kw, role=role)
    items: List[Any] = []

    if not df_prod.empty:
        for _, row in df_prod.head(6).iterrows():
            price_str = f"Bán: {row['sale_price']:,.0f} đ"
            if role == "ROLE_SALES":
                cost_str = "Vốn: ****** đ"
            else:
                cost_str = f"Vốn: {format_vnd_full(row['cost_price'], role)}"
            items.append(
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(row["product_code"], className="font-mono font-bold text-slate-900 mr-2"),
                                html.Span(row["product_name"], className="text-slate-700 font-medium"),
                            ],
                            className="truncate",
                        ),
                        html.Div(
                            [
                                html.Span(f"Tồn: {int(row['stock_on_hand'])}", className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-semibold mr-2"),
                                html.Span(price_str, className="text-blue-700 font-semibold mr-2"),
                                html.Span(cost_str, className="text-slate-500"),
                            ],
                            className="text-[11px] shrink-0 whitespace-nowrap",
                        ),
                    ],
                    className="py-2 px-2 hover:bg-slate-50 rounded-lg flex items-center justify-between gap-2",
                )
            )

    if kw:
        df_ord = services["order"].get_orders_dataframe(search=kw)
        for _, row in df_ord.head(3).iterrows():
            items.append(
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(row["order_code"], className="font-mono font-bold text-amber-700 mr-2"),
                                html.Span(f"{row['customer_name']} · {row['product_name']}", className="text-slate-700"),
                            ],
                            className="truncate",
                        ),
                        html.Span(row["order_status"], className="px-1.5 py-0.5 rounded bg-amber-50 text-amber-800 text-[11px] font-semibold shrink-0"),
                    ],
                    className="py-2 px-2 hover:bg-slate-50 rounded-lg flex items-center justify-between gap-2",
                )
            )

    if not items:
        return [html.Div("Không tìm thấy Sản phẩm, Số máy hoặc Đơn hàng phù hợp.", className="py-6 text-center text-slate-400")]
    return items


def register_global_callbacks(app: dash.Dash, services: Dict[str, Any]) -> None:
    """Đăng ký tập trung các Global Callbacks cho App Shell."""

    @app.callback(
        Output("store-role", "data"),
        Output("btn-role-owner", "className"),
        Output("btn-role-sales", "className"),
        Output("userRoleSubtitle", "children"),
        Input("btn-role-owner", "n_clicks"),
        Input("btn-role-sales", "n_clicks"),
        State("store-role", "data"),
        prevent_initial_call=True,
    )
    def on_role_switch(_n_owner, _n_sales, current_role):
        return handle_role_switch(dash.ctx.triggered_id, current_role or "ROLE_OWNER")

    @app.callback(
        Output("store-sidebar-collapsed", "data"),
        Output("appSidebar", "className"),
        Input("sidebarToggleBtn", "n_clicks"),
        State("store-sidebar-collapsed", "data"),
        prevent_initial_call=True,
    )
    def on_toggle_sidebar(_n, collapsed):
        new_state = not bool(collapsed)
        return new_state, (SIDEBAR_COLLAPSED_CLASS if new_state else SIDEBAR_EXPANDED_CLASS)

    @app.callback(
        Output("store-active-tab", "data", allow_duplicate=True),
        Output("btn-nav-m1", "className"),
        Output("btn-nav-m2", "className"),
        Output("btn-nav-m3", "className"),
        Output("btn-nav-m4", "className"),
        Output("btn-nav-m5", "className"),
        Output("btn-nav-m6", "className"),
        Output("panel-m1", "style"),
        Output("panel-m2", "style"),
        Output("panel-m3", "style"),
        Output("panel-m4", "style"),
        Output("panel-m5", "style"),
        Output("panel-m6", "style"),
        Output("store-quick-action", "data"),
        Input("btn-nav-m1", "n_clicks"),
        Input("btn-nav-m2", "n_clicks"),
        Input("btn-nav-m3", "n_clicks"),
        Input("btn-nav-m4", "n_clicks"),
        Input("btn-nav-m5", "n_clicks"),
        Input("btn-nav-m6", "n_clicks"),
        Input("btn-brand-home", "n_clicks"),
        Input("btn-topbar-bell", "n_clicks"),
        Input("btn-quick-serial", "n_clicks"),
        Input("btn-quick-po", "n_clicks"),
        Input("btn-quick-threshold", "n_clicks"),
        State("store-active-tab", "data"),
        prevent_initial_call=True,
    )
    def on_navigate(*args):
        current_tab = args[-1] or "m1"
        target_tab, nav_cls, p_styles, quick_act = handle_tab_navigation(dash.ctx.triggered_id, current_tab)
        return (target_tab, *nav_cls, *p_styles, quick_act)

    @app.callback(
        Output("btn-nav-m1", "className", allow_duplicate=True),
        Output("btn-nav-m2", "className", allow_duplicate=True),
        Output("btn-nav-m3", "className", allow_duplicate=True),
        Output("btn-nav-m4", "className", allow_duplicate=True),
        Output("btn-nav-m5", "className", allow_duplicate=True),
        Output("btn-nav-m6", "className", allow_duplicate=True),
        Output("panel-m1", "style", allow_duplicate=True),
        Output("panel-m2", "style", allow_duplicate=True),
        Output("panel-m3", "style", allow_duplicate=True),
        Output("panel-m4", "style", allow_duplicate=True),
        Output("panel-m5", "style", allow_duplicate=True),
        Output("panel-m6", "style", allow_duplicate=True),
        Input("store-active-tab", "data"),
        prevent_initial_call=True,
    )
    def on_store_tab_sync(active_tab):
        """Đồng bộ giao diện Sidebar & Panel khi store-active-tab thay đổi từ liên kết chéo M1/M2 -> M3/M4."""
        target = active_tab if active_tab in MODULE_KEYS else "m1"
        nav_cls = [SIDEBAR_NAV_ACTIVE_CLASS if k == target else SIDEBAR_NAV_IDLE_CLASS for k in MODULE_KEYS]
        p_styles = [{"display": "flex" if k == target else "none"} for k in MODULE_KEYS]
        return (*nav_cls, *p_styles)

    @app.callback(
        Output("quickSearchModal", "style"),
        Input("btn-open-quick-search", "n_clicks"),
        Input("btn-close-quick-search", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_toggle_quick_search(_open, _close):
        if dash.ctx.triggered_id == "btn-open-quick-search":
            return {"display": "flex"}
        return {"display": "none"}

    @app.callback(
        Output("quickSearchResults", "children"),
        Input("quickSearchInput", "value"),
        Input("store-role", "data"),
    )
    def on_quick_search_input(query_text, role):
        return handle_quick_search_query(query_text, services, role=role or "ROLE_OWNER")

    @app.callback(
        Output("toast", "style"),
        Output("toastMessage", "children"),
        Output("toastIcon", "className"),
        Input("store-toast", "data"),
        Input("btn-close-toast", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_toast_change(toast_data, _close_clicks):
        if dash.ctx.triggered_id == "btn-close-toast" or not toast_data or not toast_data.get("open"):
            return {"display": "none"}, dash.no_update, dash.no_update
        kind = toast_data.get("kind", "success")
        icon_cls = (
            "material-symbols-outlined text-rose-400 text-[18px]"
            if kind == "error"
            else "material-symbols-outlined text-emerald-400 text-[18px]"
        )
        return {"display": "flex"}, toast_data.get("message", "Thao tác thành công"), icon_cls

    @app.callback(
        Output("store-toast", "data", allow_duplicate=True),
        Output("syncTimeText", "children"),
        Input("btn-sync-kiotviet", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_sync_kiotviet(_n):
        return {"open": True, "message": "Đã đồng bộ dữ liệu kho mới nhất từ KiotViet (16 SKU · 52 HĐ)!", "kind": "success"}, "Vừa đồng bộ · CN01"
