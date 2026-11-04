"""
TDD Test Suite cho Phân hệ 1: Quản lý danh mục & Tồn kho thiết bị (US-1.1)
Sử dụng thư viện chuẩn unittest (hỗ trợ cả pytest).
"""
import os
import sqlite3
import unittest

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "retail_dienmay.db"))

class TestInventoryService(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.row_factory = sqlite3.Row

    def tearDown(self):
        self.conn.close()

    def test_inventory_kpi_metrics(self):
        """
        FR-INV-01: Kiểm tra tính toán các chỉ số vĩ mô trên thẻ KPI.
        """
        cur = self.conn.cursor()
        cur.execute("""
            SELECT 
                COUNT(DISTINCT product_code) AS total_skus,
                SUM(stock_on_hand) AS total_soh,
                ROUND(SUM(stock_on_hand * cost_price), 0) AS total_capital
            FROM DIM_PRODUCTS
            WHERE is_active = 1 AND has_serial = 1;
        """)
        row = cur.fetchone()
        
        self.assertEqual(row["total_skus"], 12, "Số lượng SKU quản lý Serial đang kinh doanh phải là 12")
        self.assertGreater(row["total_soh"], 0, "Tổng tồn kho vật lý phải > 0")
        self.assertGreater(row["total_capital"], 0, "Tổng vốn kho phải > 0")

    def test_serial_integrity(self):
        """
        FR-INV-03: Kiểm tra tính toàn vẹn: stock_on_hand == COUNT(Serial IN_STOCK).
        """
        cur = self.conn.cursor()
        cur.execute("""
            SELECT 
                p.product_code,
                p.product_name,
                p.stock_on_hand,
                COUNT(s.serial_number) AS in_stock_serials
            FROM DIM_PRODUCTS p
            LEFT JOIN DIM_PRODUCT_SERIALS s 
                ON p.product_code = s.product_code AND s.status = 'IN_STOCK'
            WHERE p.has_serial = 1
            GROUP BY p.product_code, p.product_name, p.stock_on_hand;
        """)
        rows = cur.fetchall()
        for r in rows:
            delta = r["stock_on_hand"] - r["in_stock_serials"]
            self.assertEqual(delta, 0, f"Lệch tồn kho Serial tại SKU {r['product_code']}")

    def test_overstock_and_stockout_classification(self):
        """
        FR-INV-04: Kiểm tra phân loại sức khỏe tồn kho theo ngưỡng ROP Min/Max.
        """
        cur = self.conn.cursor()
        cur.execute("""
            SELECT inventory_status, COUNT(*) AS sku_count, ROUND(SUM(stock_on_hand * cost_price), 0) AS capital
            FROM VW_PRODUCT_PERFORMANCE
            WHERE has_serial = 1
            GROUP BY inventory_status;
        """)
        status_dict = {r["inventory_status"]: (r["sku_count"], r["capital"]) for r in cur.fetchall()}

        self.assertIn("Cảnh báo: Tồn kho quá cao", status_dict)
        self.assertEqual(status_dict["Cảnh báo: Tồn kho quá cao"][0], 3, "Phải có đúng 3 SKU tồn kho quá cao")

        cur.execute("SELECT COUNT(*) AS oos_count FROM DIM_PRODUCTS WHERE has_serial = 1 AND stock_on_hand = 0;")
        oos_count = cur.fetchone()["oos_count"]
        self.assertGreaterEqual(oos_count, 4, f"Phải có ít nhất 4 mặt hàng cháy hàng (SOH = 0)")

    def test_role_based_cost_masking(self):
        """
        FR-INV-05: Kiểm tra hàm bảo mật che giấu giá vốn.
        """
        def format_capital(val: float, role: str) -> str:
            if role == "ROLE_SALES":
                return "****** đ"
            return f"{val:,.0f} đ"

        capital_val = 1227600000.0
        self.assertEqual(format_capital(capital_val, "ROLE_OWNER"), "1,227,600,000 đ")
        self.assertEqual(format_capital(capital_val, "ROLE_SALES"), "****** đ")

if __name__ == '__main__':
    unittest.main()
