"""
Test Suite tích hợp toàn diện cho Dashboard Tổng quan kho (Module 01).
Kiểm tra tính nhất quán giữa InventoryService và OrderService và các chỉ số KPI theo DoD.
"""
import os
import unittest

from src.services.inventory_service import InventoryService
from src.services.order_service import OrderService

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "retail_dienmay.db"))

class TestDashboardIntegration(unittest.TestCase):
    def setUp(self):
        self.inv_service = InventoryService(db_path=DB_PATH)
        self.order_service = OrderService(db_path=DB_PATH)

    def test_cross_service_soh_consistency(self):
        """
        DoD-DATA-01: Kiểm tra tính nhất quán về tồn kho SOH giữa Tab 1 và Tab 2.
        Tổng SOH trên InventoryService phải bằng đúng SUM(SOH) trên OrderService flow matrix.
        """
        inv_kpis = self.inv_service.get_kpis(role="ROLE_OWNER")
        flow_df = self.order_service.get_inventory_flow_matrix()
        
        self.assertEqual(inv_kpis["total_soh"], flow_df["soh"].sum())

    def test_overstock_capital_percentage_reflection(self):
        """
        DoD-UX-01: Kiểm tra 74.9% vốn kẹt ở nhóm Tồn quá cao phản ánh mâu thuẫn cốt lõi.
        """
        inv_kpis = self.inv_service.get_kpis(role="ROLE_OWNER")
        overstock_cap = inv_kpis["overstock_capital"]
        total_cap = inv_kpis["total_capital"]
        
        pct = (overstock_cap / total_cap) * 100
        self.assertGreaterEqual(pct, 70.0, f"Tỷ lệ vốn đọng quá cao phải >= 70%, thực tế: {pct:.1f}%")

    def test_in_transit_replenishes_stockouts(self):
        """
        DoD-DATA-01: Kiểm tra hàng đang về (INC) bổ sung đúng các mặt hàng SOH <= 0.
        """
        flow_df = self.order_service.get_inventory_flow_matrix()
        stockouts = flow_df[flow_df["soh"] == 0]
        
        # Tất cả các mặt hàng SOH == 0 đều phải có INC > 0
        self.assertTrue(all(stockouts["inc"] > 0), "Hàng cháy (SOH=0) bắt buộc phải có đơn nhập INC đang về")

    def test_dash_requirements_tracked_and_complete(self):
        """
        Kiểm tra file requirements.txt tồn tại ở thư mục gốc, chứa đủ thư viện cho Plotly Dash
        (dash, pandas, numpy, plotly) và đã được Git theo dõi.
        """
        import subprocess

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        req_path = os.path.join(project_root, "requirements.txt")
        self.assertTrue(os.path.isfile(req_path), "Thiếu file requirements.txt ở thư mục gốc dự án")

        with open(req_path, "r", encoding="utf-8") as f:
            content = f.read().lower()

        for pkg in ("streamlit", "dash", "pandas", "numpy", "plotly"):
            self.assertIn(pkg, content, f"Thiếu thư viện bắt buộc '{pkg}' trong requirements.txt")

        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "requirements.txt"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            tracked.returncode,
            0,
            "requirements.txt chưa được git track",
        )

if __name__ == '__main__':
    unittest.main()
