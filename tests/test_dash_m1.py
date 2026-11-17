"""
TDD Test Suite cho Giai đoạn 2: Module 01 Tổng quan kho & Serial Drill-down trên Plotly Dash.
"""
import os
import unittest

from src.services.inventory_service import InventoryService
from src.services.order_service import OrderService
from src.dash_app.pages.m1_overview import build_m1_panel, build_m1_detail_drawer
from src.dash_app.callbacks.m1_callbacks import (
    build_m1_drawer_body,
    render_m1_kpis_and_table,
)

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "retail_dienmay.db"))


def _build_m1_services():
    return {
        "inventory": InventoryService(DB_PATH),
        "order": OrderService(DB_PATH),
    }


def _collect_ids(component) -> set:
    ids = set()
    if component is None:
        return ids
    if hasattr(component, "id") and getattr(component, "id", None) is not None:
        ids.add(str(component.id))
    children = getattr(component, "children", None)
    if isinstance(children, (list, tuple)):
        for c in children:
            ids.update(_collect_ids(c))
    elif children is not None and not isinstance(children, (str, int, float, bool)):
        ids.update(_collect_ids(children))
    return ids


class TestDashM1Overview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.services = _build_m1_services()

    def test_m1_panel_and_drawer_landmark_ids(self):
        """Kiểm tra Panel M1 và Detail Drawer chứa đủ ID chuẩn Prototype."""
        panel = build_m1_panel(self.services, active=True)
        drawer = build_m1_detail_drawer()
        ids = _collect_ids(panel) | _collect_ids(drawer)
        for req_id in (
            "panel-m1",
            "kpi-all",
            "kpi-stagnant",
            "kpi-held",
            "kpi-low",
            "m1-pill-all",
            "m1-pill-stagnant",
            "m1-pill-low",
            "m1-pill-held",
            "m1-pill-incoming",
            "m1-pill-healthy",
            "searchInput",
            "inventoryTableBody",
            "m1-scatter-chart",
            "detailDrawer",
            "drawerSerialList",
        ):
            self.assertIn(req_id, ids, f"Thiếu ID '{req_id}' trong Module 1 Dash")

    def test_m1_kpis_and_table_rbac_masking_and_filtering(self):
        """Kiểm tra che giấu giá vốn cho ROLE_SALES và lọc chính xác theo Pill / Search."""
        res_owner = render_m1_kpis_and_table(self.services, filter_key="all", search="", role="ROLE_OWNER")
        owner_kpis_txt = str(res_owner["kpi_cards"])
        self.assertIn("1,27 tỷ", owner_kpis_txt)
        self.assertIn("941,4 tr", owner_kpis_txt)

        res_sales = render_m1_kpis_and_table(self.services, filter_key="all", search="", role="ROLE_SALES")
        sales_txt = str(res_sales["kpi_cards"]) + str(res_sales["table_rows"])
        self.assertNotIn("1,27 tỷ", sales_txt)
        self.assertNotIn("941,4 tr", sales_txt)
        self.assertIn("****** đ", sales_txt)

        # Lọc theo nhóm đọng vốn vượt trần
        res_stag = render_m1_kpis_and_table(self.services, filter_key="stagnant", search="", role="ROLE_OWNER")
        stag_txt = str(res_stag["table_rows"])
        self.assertIn("TV-LG-55C3", stag_txt)
        self.assertNotIn("ML-DK-FTKB25", stag_txt)

        # Tìm kiếm theo từ khóa Sony
        res_sony = render_m1_kpis_and_table(self.services, filter_key="all", search="Sony", role="ROLE_OWNER")
        sony_txt = str(res_sony["table_rows"])
        self.assertIn("TV-SN-55X80K", sony_txt)
        self.assertNotIn("TV-LG-55C3", sony_txt)

    def test_m1_serial_drawer_loads_real_serials_and_masks_cost(self):
        """Kiểm tra Slide-over Detail Drawer tra cứu Serial thực tế và bảo mật giá vốn."""
        drawer_owner = build_m1_drawer_body("TV-SN-55X80K", self.services, role="ROLE_OWNER")
        self.assertEqual(drawer_owner["sku_badge"], "TV-SN-55X80K")
        self.assertIn("13,2 tr", drawer_owner["unit_cost_text"])
        self.assertEqual(len(drawer_owner["serial_rows"]), 5)

        drawer_sales = build_m1_drawer_body("TV-SN-55X80K", self.services, role="ROLE_SALES")
        self.assertEqual(drawer_sales["total_capital_text"], "****** đ")
        self.assertIn("****** đ", drawer_sales["unit_cost_text"])


if __name__ == "__main__":
    unittest.main()
