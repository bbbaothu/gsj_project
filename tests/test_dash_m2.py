"""
TDD Test Suite cho Giai đoạn 3: Module 02 Cần xử lý hôm nay trên Plotly Dash.
"""
import os
import unittest

from src.services.alert_service import AlertService
from src.dash_app.pages.m2_alerts import build_m2_modals_and_drawer, build_m2_panel
from src.dash_app.callbacks.m2_callbacks import (
    build_m2_drawer_body,
    render_m2_workspace,
    submit_m2_snooze,
)

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "retail_dienmay.db"))


def _build_m2_services():
    return {"alert": AlertService(DB_PATH)}


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


class TestDashM2Alerts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.services = _build_m2_services()

    def test_m2_landmark_ids_match_prototype(self):
        """Kiểm tra Panel M2, Decision Drawer, Snooze Modal và Threshold Modal có đủ ID chuẩn."""
        panel = build_m2_panel(self.services, active=False)
        overlays = build_m2_modals_and_drawer()
        ids = _collect_ids(panel) | _collect_ids(overlays)
        for req_id in (
            "panel-m2",
            "m2-kpi-stagnant",
            "m2-kpi-dead",
            "m2-kpi-seasonal",
            "m2-kpi-stockout",
            "m2-pill-all",
            "m2-pill-stagnant",
            "m2-pill-dead",
            "m2-pill-seasonal",
            "m2-pill-stockout",
            "m2-search-input",
            "m2-alerts-table-body",
            "m2-capital-chart",
            "m2-runway-chart",
            "m2DecisionDrawer",
            "snoozeModal",
            "m2ThresholdModal",
            "m2-download-csv",
        ):
            self.assertIn(req_id, ids, f"Thiếu ID '{req_id}' trong Module 2 Dash")

    def test_m2_workspace_filtering_and_rbac_masking(self):
        """Kiểm tra lọc 2 chiều và bảo mật vốn kẹt cho ROLE_SALES."""
        res_owner = render_m2_workspace(self.services, filter_key="all", role="ROLE_OWNER")
        self.assertIn("TV-LG-55C3", str(res_owner["table_rows"]))
        self.assertIn("ML-DK-FTKB25", str(res_owner["table_rows"]))

        res_sales = render_m2_workspace(self.services, filter_key="all", role="ROLE_SALES")
        self.assertIn("****** đ", str(res_sales["kpi_cards"]))
        self.assertIn("****** đ", str(res_sales["table_rows"]))

        res_stockout = render_m2_workspace(self.services, filter_key="stockout", role="ROLE_OWNER")
        self.assertIn("ML-DK-FTKB25", str(res_stockout["table_rows"]))
        self.assertNotIn("TV-LG-55C3", str(res_stockout["table_rows"]))

    def test_m2_drawer_and_snooze_modal_validation_and_persistence(self):
        """Kiểm tra Decision Drawer và validation ERR_ACT_003 khi bấm Tạm hoãn trong Modal."""
        drawer = build_m2_drawer_body("TV-LG-55C3", self.services, role="ROLE_OWNER")
        self.assertEqual(drawer["sku"], "TV-LG-55C3")
        self.assertEqual(drawer["target_module"], "m3")

        bad = submit_m2_snooze("TV-LG-55C3", 14, "ngan", self.services, role="ROLE_OWNER")
        self.assertFalse(bad["success"])
        self.assertEqual(bad["error_code"], "ERR_ACT_003")

        try:
            ok = submit_m2_snooze("TV-LG-55C3", 14, "Giữ máy trưng bày chương trình cuối tháng", self.services, role="ROLE_OWNER")
            self.assertTrue(ok["success"])
        finally:
            conn = self.services["alert"]._get_connection()
            conn.execute("DELETE FROM SYS_ALERT_SNOOZE_LOG WHERE product_code = 'TV-LG-55C3';")
            conn.commit()
            conn.close()


if __name__ == "__main__":
    unittest.main()
