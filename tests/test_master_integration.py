"""
Test Suite Tích hợp Toàn diện Toàn Hệ thống (End-to-End 6 Modules - Master Integration).
Kiểm tra tính nhất quán dữ liệu, bảo mật RBAC toàn cục và luồng liên thông nghiệp vụ M1 -> M6.
"""
import os
import unittest

from src.services.alert_service import AlertService
from src.services.clearance_service import ClearanceService
from src.services.crm_service import CrmService
from src.services.inventory_service import InventoryService
from src.services.order_service import OrderService
from src.services.performance_service import PerformanceService
from src.services.replenishment_service import ReplenishmentService

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "retail_dienmay.db"))


class TestMasterIntegration(unittest.TestCase):
    def setUp(self):
        self.inv = InventoryService(DB_PATH)
        self.ord = OrderService(DB_PATH)
        self.alert = AlertService(DB_PATH)
        self.clear = ClearanceService(DB_PATH)
        self.rep = ReplenishmentService(DB_PATH)
        self.crm = CrmService(DB_PATH)
        self.perf = PerformanceService(DB_PATH)

    def test_global_rbac_cost_masking_across_all_6_modules(self):
        """
        DoD-SEC-01: Khi truy cập với ROLE_SALES, toàn bộ 6 Module đều phải che tuyệt đối
        giá vốn, tổng tài sản kho, vốn kẹt, vốn thu hồi và lợi nhuận gộp.
        """
        self.assertIsNone(self.inv.get_kpis(role="ROLE_SALES")["total_capital"])
        self.assertIsNone(self.alert.get_alert_kpis(role="ROLE_SALES")["stagnant_capital"])
        self.assertIsNone(self.clear.get_clearance_kpis(role="ROLE_SALES")["expected_recovery_capital"])
        self.assertIsNone(self.rep.get_replenishment_recommendations(role="ROLE_SALES")["estimated_capital"])
        self.assertIsNone(self.perf.get_performance_kpis(role="ROLE_SALES")["net_gross_profit"])
        self.assertIsNone(self.perf.get_profit_waterfall_data(role="ROLE_SALES")["net_gross_profit"])

    def test_cross_module_m1_m2_m3_clearance_pipeline(self):
        """
        Kiểm tra liên thông M1 (SOH > max_stock) -> M2 (Cảnh báo hàng chậm) -> M3 (4 kịch bản xả hàng).
        """
        inv_over = self.inv.get_products_dataframe(status="Cảnh báo: Tồn kho quá cao", role="ROLE_OWNER")
        slow_alerts = self.alert.get_slow_moving_alerts(role="ROLE_OWNER")
        slow_skus = set(slow_alerts["product_code"].tolist())

        # Toàn bộ hàng vượt trần ở M1 phải xuất hiện trong danh sách cảnh báo M2
        for sku in inv_over["product_code"].tolist():
            self.assertIn(sku, slow_skus, f"SKU vượt trần {sku} chưa được M2 phát hiện")

        # Kiểm tra SKU đầu bảng M2 đẩy sang M3 sinh đủ 4 chiến thuật xả hàng có lãi
        top_sku = slow_alerts.iloc[0]["product_code"]
        tactics = self.clear.generate_4_tactics(top_sku)
        self.assertEqual(len(tactics), 4)
        self.assertTrue(any(t["is_recommended"] and t["total_profit"] > 0 for t in tactics))

    def test_cross_module_m2_m4_replenishment_and_po_pipeline(self):
        """
        Kiểm tra liên thông M2 (Cảnh báo sắp cháy hàng) -> M4 (Dự báo & Gom đơn PO).
        """
        stockout_df = self.alert.get_stockout_alerts()
        urgent = stockout_df[stockout_df["inc"] == 0]
        self.assertFalse(urgent.empty)

        rep_plan = self.rep.get_replenishment_recommendations(cycle_days=14, budget_cap=200_000_000, role="ROLE_OWNER")
        rep_map = {item["product_code"]: item for item in rep_plan["items"]}

        # SKU sắp đứt hàng chưa có PO (ML-DK-FTKB25) phải có đề xuất nhập > 0 ở M4
        self.assertGreater(rep_map["ML-DK-FTKB25"]["suggested_qty"], 0)
        groups = self.rep.preview_po_grouping(rep_plan["items"])
        self.assertGreaterEqual(len(groups), 1)

    def test_cross_module_m5_crm_and_m6_financial_reconciliation(self):
        """
        Kiểm tra M5 (CRM & Lịch thợ) hoạt động trên dữ liệu hóa đơn thực và M6 khớp 100% doanh thu & lãi gộp.
        """
        crm_kpis = self.crm.get_crm_kpis()
        self.assertGreater(crm_kpis["due_today_count"], 0)

        perf_kpis = self.perf.get_performance_kpis(role="ROLE_OWNER")
        wf = self.perf.get_profit_waterfall_data(role="ROLE_OWNER")
        self.assertEqual(perf_kpis["net_gross_profit"], wf["net_gross_profit"])
        self.assertGreater(perf_kpis["invoice_count"], 50)


if __name__ == "__main__":
    unittest.main()
