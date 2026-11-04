"""
TDD Test Suite cho Phân hệ 1: Quản lý danh mục & Tồn kho thiết bị (US-1.1)
Kiểm thử lớp nghiệp vụ InventoryService.
"""
import os
import unittest

from src.services.inventory_service import InventoryService

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "retail_dienmay.db"))

class TestInventoryService(unittest.TestCase):
    def setUp(self):
        self.service = InventoryService(db_path=DB_PATH)

    def test_get_kpis_as_owner(self):
        """
        FR-INV-01: Kiểm tra tính toán các chỉ số vĩ mô cho Chủ cửa hàng (ROLE_OWNER).
        Giá vốn phải được hiển thị chính xác.
        """
        kpis = self.service.get_kpis(role="ROLE_OWNER")
        
        self.assertEqual(kpis["total_skus"], 12)
        self.assertGreater(kpis["total_soh"], 0)
        self.assertGreater(kpis["total_capital"], 0)
        self.assertIn("1,", kpis["display_capital"])
        self.assertEqual(kpis["overstock_count"], 3)
        self.assertGreaterEqual(kpis["stockout_count"], 4)

    def test_get_kpis_as_sales_masked(self):
        """
        FR-INV-05: Kiểm tra cơ chế che giấu giá vốn đối với ROLE_SALES.
        """
        kpis = self.service.get_kpis(role="ROLE_SALES")
        
        self.assertEqual(kpis["total_skus"], 12)
        self.assertGreater(kpis["total_soh"], 0)
        self.assertIsNone(kpis["total_capital"], "ROLE_SALES không được nhận giá trị vốn số thực")
        self.assertEqual(kpis["display_capital"], "****** đ", "Giá vốn hiển thị phải bị che giấu")

    def test_get_products_dataframe_filtering(self):
        """
        FR-INV-02: Kiểm tra lọc danh mục sản phẩm theo thương hiệu và tìm kiếm.
        """
        df_all = self.service.get_products_dataframe(role="ROLE_OWNER")
        self.assertEqual(len(df_all), 16)
        self.assertIn("cost_price", df_all.columns)

        # Lọc theo hãng Sony
        df_sony = self.service.get_products_dataframe(brand="Sony", role="ROLE_OWNER")
        self.assertTrue(all(df_sony["brand"] == "Sony"))

        # Kiểm tra role SALES bị ẩn cột giá vốn
        df_sales = self.service.get_products_dataframe(role="ROLE_SALES")
        self.assertNotIn("cost_price", df_sales.columns)
        self.assertNotIn("capital_tied", df_sales.columns)

    def test_serial_drilldown_integrity(self):
        """
        FR-INV-03: Kiểm tra drill-down danh sách Serial và tính toàn vẹn Delta = SOH - COUNT(Serial).
        """
        drilldown = self.service.get_serial_drilldown("TV-SN-55X80K")
        self.assertEqual(drilldown["product_code"], "TV-SN-55X80K")
        self.assertTrue(drilldown["is_integrity_ok"])
        self.assertEqual(len(drilldown["serials"]), drilldown["stock_on_hand"])

if __name__ == '__main__':
    unittest.main()
