"""
TDD Test Suite cho Giai đoạn 4: Module 03 Gợi ý xả hàng & Định giá cạnh tranh trên Plotly Dash.
"""
import os
import unittest

from src.services.clearance_service import ClearanceService
from src.dash_app.pages.m3_clearance import build_m3_modals, build_m3_panel
from src.dash_app.callbacks.m3_callbacks import (
    render_m3_workspace,
    submit_m3_approve_campaign,
)

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "retail_dienmay.db"))


def _build_m3_services():
    return {"clearance": ClearanceService(DB_PATH)}


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


class TestDashM3Clearance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.services = _build_m3_services()

    def test_m3_landmark_ids_match_prototype(self):
        """Kiểm tra Panel M3 và 2 Modals (In tem xả đỏ, Chiến dịch) đủ ID chuẩn Prototype."""
        panel = build_m3_panel(self.services, active=False)
        modals = build_m3_modals()
        ids = _collect_ids(panel) | _collect_ids(modals)
        for req_id in (
            "panel-m3",
            "m3KpiTotalRecovery",
            "m3KpiTotalProfit",
            "m3KpiPaiHero",
            "m3SkuSelectorGrid",
            "m3TacticsContainer",
            "m3SalesLockBanner",
            "m3CapitalProtectionBanner",
            "m3-discount-slider",
            "m3-qty-input",
            "m3SimBoxRevenue",
            "m3SimBoxCapital",
            "m3SimBoxPromoCost",
            "m3SimBoxNetProfit",
            "m3-tactic-chart",
            "m3CompetitorListContainer",
            "m3SuggestedPriceHero",
            "m3SaleTagModal",
            "m3CampaignModal",
            "btn-m3-approve-pos",
        ):
            self.assertIn(req_id, ids, f"Thiếu ID '{req_id}' trong Module 3 Dash")

    def test_m3_simulator_loss_warning_and_rbac_masking(self):
        """Kiểm tra Simulator dòng tiền PA2, cảnh báo cắt lỗ 25% và bảo mật ROLE_SALES."""
        ws_ok = render_m3_workspace(self.services, sku="TV-LG-55C3", tactic_code="PA2", target_qty=10, extra_disc=0.0, role="ROLE_OWNER")
        self.assertIn("225,0 tr", str(ws_ok["sim_capital"]))
        self.assertEqual(ws_ok["cap_protect_style"]["display"], "none")
        self.assertEqual(ws_ok["sales_lock_style"]["display"], "none")

        ws_loss = render_m3_workspace(self.services, sku="TV-LG-55C3", tactic_code="PA1", target_qty=10, extra_disc=25.0, role="ROLE_OWNER")
        self.assertEqual(ws_loss["cap_protect_style"]["display"], "flex")

        ws_sales = render_m3_workspace(self.services, sku="TV-LG-55C3", tactic_code="PA2", target_qty=10, extra_disc=0.0, role="ROLE_SALES")
        self.assertEqual(ws_sales["kpi_recovery"], "****** đ")
        self.assertEqual(ws_sales["sim_capital"], "****** đ")
        self.assertEqual(ws_sales["sales_lock_style"]["display"], "flex")

    def test_m3_approve_campaign_blocks_sales_and_saves_owner(self):
        """Kiểm tra chặn ROLE_SALES duyệt bán dưới giá vốn (ERR_CLR_001) và lưu chiến dịch cho ROLE_OWNER."""
        bad = submit_m3_approve_campaign("TV-LG-55C3", "PA1", 10, 21_000_000, self.services, role="ROLE_SALES")
        self.assertFalse(bad["success"])
        self.assertEqual(bad["error_code"], "ERR_CLR_001")

        conn = self.services["clearance"]._get_connection()
        orig_price = conn.execute("SELECT sale_price FROM DIM_PRODUCTS WHERE product_code='TV-LG-55C3';").fetchone()[0]
        conn.close()
        cid = None
        try:
            ok = submit_m3_approve_campaign("TV-LG-55C3", "PA2", 10, 26_990_000, self.services, role="ROLE_OWNER")
            self.assertTrue(ok["success"])
            cid = ok["campaign_id"]
        finally:
            cleanup = self.services["clearance"]._get_connection()
            if cid is not None:
                cleanup.execute("DELETE FROM FACT_CLEARANCE_CAMPAIGNS WHERE campaign_id = ?;", (cid,))
            cleanup.execute("UPDATE DIM_PRODUCTS SET sale_price = ? WHERE product_code='TV-LG-55C3';", (orig_price,))
            cleanup.commit()
            cleanup.close()


if __name__ == "__main__":
    unittest.main()
