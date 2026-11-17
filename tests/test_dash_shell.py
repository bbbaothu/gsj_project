"""
TDD Test Suite cho Giai đoạn 1 (Task 2): App Shell, Sidebar, Topbar, RBAC Toggle & Global Quick Search (Plotly Dash).
"""
import os
import unittest

from src.services.inventory_service import InventoryService
from src.services.order_service import OrderService
from src.services.alert_service import AlertService
from src.services.clearance_service import ClearanceService
from src.services.replenishment_service import ReplenishmentService
from src.services.crm_service import CrmService
from src.services.performance_service import PerformanceService
from src.dash_app.components.layout_shell import build_app_shell
from src.dash_app.callbacks.global_callbacks import (
    handle_quick_search_query,
    handle_role_switch,
    handle_tab_navigation,
)

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "retail_dienmay.db"))


def _build_services():
    return {
        "inventory": InventoryService(DB_PATH),
        "order": OrderService(DB_PATH),
        "alert": AlertService(DB_PATH),
        "clearance": ClearanceService(DB_PATH),
        "replenishment": ReplenishmentService(DB_PATH),
        "crm": CrmService(DB_PATH),
        "performance": PerformanceService(DB_PATH),
    }


def _collect_ids(component) -> set:
    ids = set()
    if component is None:
        return ids
    if hasattr(component, "id") and getattr(component, "id", None) is not None:
        ids.add(component.id)
    children = getattr(component, "children", None)
    if isinstance(children, (list, tuple)):
        for c in children:
            ids.update(_collect_ids(c))
    elif children is not None and not isinstance(children, (str, int, float, bool)):
        ids.update(_collect_ids(children))
    return ids


class TestDashShell(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.services = _build_services()

    def test_app_shell_contains_prototype_landmark_ids(self):
        """Kiểm tra DOM App Shell có đủ Sidebar 6 Modules, Topbar, RBAC Switcher, Quick Search & Toast."""
        shell = build_app_shell(self.services)
        ids = _collect_ids(shell)
        expected_ids = {
            "store-active-tab",
            "store-role",
            "store-selected-sku",
            "store-sidebar-collapsed",
            "appSidebar",
            "sidebarToggleBtn",
            "btn-nav-m1",
            "btn-nav-m2",
            "btn-nav-m3",
            "btn-nav-m4",
            "btn-nav-m5",
            "btn-nav-m6",
            "btn-quick-serial",
            "btn-quick-po",
            "btn-quick-threshold",
            "btn-role-owner",
            "btn-role-sales",
            "btn-topbar-bell",
            "userRoleSubtitle",
            "quickSearchModal",
            "quickSearchInput",
            "quickSearchResults",
            "toast",
        }
        missing = expected_ids - ids
        self.assertFalse(missing, f"Thiếu các thành phần ID chuẩn Prototype: {missing}")

    def test_role_switch_updates_rbac_styles_and_subtitle(self):
        """Kiểm tra chuyển đổi RBAC OWNER <-> SALES đồng bộ class active & nhãn vai trò."""
        role, owner_cls, sales_cls, subtitle = handle_role_switch("btn-role-sales", "ROLE_OWNER")
        self.assertEqual(role, "ROLE_SALES")
        self.assertIn("bg-white text-slate-900", sales_cls)
        self.assertNotIn("bg-white text-slate-900", owner_cls)
        self.assertEqual(subtitle, "Nhân viên bán hàng")

        role2, owner_cls2, sales_cls2, subtitle2 = handle_role_switch("btn-role-owner", role)
        self.assertEqual(role2, "ROLE_OWNER")
        self.assertIn("bg-white text-slate-900", owner_cls2)
        self.assertEqual(subtitle2, "Chủ cửa hàng")

    def test_tab_navigation_and_quick_action_targets(self):
        """Kiểm tra chuyển đổi 6 Module và nút truy cập nhanh Sidebar / Chuông thông báo."""
        tab, nav_classes, panel_styles, quick_target = handle_tab_navigation("btn-nav-m3", "m1")
        self.assertEqual(tab, "m3")
        self.assertIn("border-blue-600", nav_classes[2])
        self.assertEqual(panel_styles[2]["display"], "flex")
        self.assertEqual(panel_styles[0]["display"], "none")
        self.assertIsNone(quick_target)

        # Nút Chuông thông báo mở Module 2
        tab_bell, nav_bell, _, _ = handle_tab_navigation("btn-topbar-bell", "m1")
        self.assertEqual(tab_bell, "m2")
        self.assertIn("border-blue-600", nav_bell[1])

        # Nút Quản lý nghiệp vụ "Đối soát Serial" chuyển sang M1 + tín hiệu mở Drawer
        tab_s, _, _, action_s = handle_tab_navigation("btn-quick-serial", "m4")
        self.assertEqual(tab_s, "m1")
        self.assertEqual(action_s, "OPEN_M1_SERIAL_DRAWER")

    def test_quick_search_returns_real_sku_and_respects_rbac(self):
        """Kiểm tra Quick Search Ctrl+K tìm đúng SKU từ SQLite và che giá vốn khi ROLE_SALES."""
        res_owner = handle_quick_search_query("TV-LG-55C3", self.services, role="ROLE_OWNER")
        text_owner = str(res_owner)
        self.assertIn("TV-LG-55C3", text_owner)
        self.assertIn("22,500,000", text_owner)

        res_sales = handle_quick_search_query("TV-LG-55C3", self.services, role="ROLE_SALES")
        text_sales = str(res_sales)
        self.assertIn("TV-LG-55C3", text_sales)
        self.assertNotIn("22,500,000", text_sales)
        self.assertIn("******", text_sales)

    def test_v2_typography_css_brand_badges_and_plain_vietnamese(self):
        """Kiểm tra CSS tiện ích V2, helper màu riêng từng Hãng, tên sản phẩm ngắn & tiếng Việt thuần."""
        from src.dash_app.components.layout_shell import get_brand_badge_class, get_short_product_name

        css_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "assets", "stock_sense.css"))
        with open(css_path, "r", encoding="utf-8") as f:
            css_text = f.read()
        for cls_name in (".gap-pattern", ".frozen-striped-bar", ".cell-hscroll", ".font-code"):
            self.assertIn(cls_name, css_text, f"Thiếu lớp CSS '{cls_name}' trong stock_sense.css")

        brands = ["Daikin", "Sony", "Casper", "Toshiba", "LG", "Samsung", "Panasonic"]
        badge_classes = [get_brand_badge_class(b) for b in brands]
        self.assertEqual(len(set(badge_classes)), len(brands), "Mỗi hãng phải có 1 lớp màu badge riêng biệt")
        for b_cls in badge_classes:
            self.assertIn("bg-", b_cls)
            self.assertIn("text-", b_cls)
            self.assertIn("border-", b_cls)

        short_oled = get_short_product_name("Smart Tivi OLED LG 4K 55 inch 55C3PSA", "TV-LG-55C3")
        self.assertLessEqual(len(short_oled), 22)
        self.assertIn("LG", short_oled)

        shell_str = str(build_app_shell(self.services))
        self.assertNotIn("Mã SKU", shell_str)
        self.assertIn("Mã sản phẩm", shell_str)


if __name__ == "__main__":
    unittest.main()
