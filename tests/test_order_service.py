"""
TDD Test Suite cho Phân hệ 2: Theo dõi Đơn hàng & Điều phối dòng hàng (US-1.2)
Sử dụng thư viện chuẩn unittest.
"""
import os
import sqlite3
import unittest

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "retail_dienmay.db"))

class TestOrderService(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.row_factory = sqlite3.Row

    def tearDown(self):
        self.conn.close()

    def test_inventory_flow_equation_balance(self):
        """
        FR-ORD-01: Kiểm tra tính cân bằng phương trình dòng hàng 4 trạng thái:
        Available (AVL) = Stock On Hand (SOH) - Reserved (RES)
        Projected Stock = Available (AVL) + In-Transit (INC)
        """
        cur = self.conn.cursor()
        cur.execute("""
            SELECT product_code, soh, res, avl, inc, projected_stock
            FROM VW_INVENTORY_FLOW_OVERVIEW
            WHERE has_serial = 1;
        """)
        rows = cur.fetchall()
        
        self.assertEqual(len(rows), 12, "Phải có đúng 12 SKU điện máy có Serial")
        for r in rows:
            expected_avl = r["soh"] - r["res"]
            expected_projected = expected_avl + r["inc"]
            self.assertEqual(r["avl"], expected_avl, f"Sai lệch Tồn khả dụng tại SKU {r['product_code']}")
            self.assertEqual(r["projected_stock"], expected_projected, f"Sai lệch Tồn dự kiến tại SKU {r['product_code']}")

    def test_detect_expired_orders_48h(self):
        """
        FR-ORD-03: Kiểm tra quy tắc Hold Time Policy:
        Đơn hàng ở trạng thái 'Chờ xử lý' có thời gian tạo > 48 giờ phải được phát hiện để cảnh báo.
        """
        cur = self.conn.cursor()
        cur.execute("""
            SELECT COUNT(*) AS expired_count
            FROM FACT_ORDERS
            WHERE status = 'Chờ xử lý' AND note LIKE '%48h%';
        """)
        expired_count = cur.fetchone()["expired_count"]
        self.assertGreaterEqual(expired_count, 4, f"Phải có ít nhất 4 đơn quá hạn 48h")

    def test_in_transit_pipeline_tracking(self):
        """
        FR-ORD-04: Kiểm tra khả năng theo dõi hàng đang trên đường về kho từ PURCHASE_ORDERS.
        """
        cur = self.conn.cursor()
        cur.execute("""
            SELECT 
                po.purchase_code, 
                po.vendor_name, 
                po.expected_delivery_date, 
                poi.product_code, 
                poi.quantity
            FROM PURCHASE_ORDERS po
            JOIN PO_ITEMS poi ON po.purchase_code = poi.purchase_code
            WHERE po.status = 'Đang vận chuyển';
        """)
        rows = cur.fetchall()
        self.assertGreaterEqual(len(rows), 4, "Phải có ít nhất 4 dòng chi tiết hàng đang về từ 3 đơn nhập")
        
        in_transit_skus = {r["product_code"] for r in rows}
        self.assertIn("ML-CS-TC09", in_transit_skus, "Phải có Điều hòa Casper trong danh sách hàng đang về")
        self.assertIn("TL-AQ-180L", in_transit_skus, "Phải có Tủ lạnh Aqua trong danh sách hàng đang về")
        self.assertIn("MG-TB-85K", in_transit_skus, "Phải có Máy giặt Toshiba trong danh sách hàng đang về")

    def test_payment_classification_metrics(self):
        """
        FR-ORD-05: Kiểm tra cơ cấu thanh toán đơn hàng (Trả toàn phần vs. Trả góp).
        """
        cur = self.conn.cursor()
        cur.execute("""
            SELECT 
                COUNT(CASE WHEN pay_installment > 0 THEN 1 END) AS installment_orders,
                COUNT(CASE WHEN pay_installment = 0 AND amount_paid < amount_due AND amount_paid > 0 THEN 1 END) AS deposit_cod_orders,
                COUNT(CASE WHEN pay_installment = 0 AND amount_paid >= amount_due THEN 1 END) AS full_payment_orders
            FROM FACT_ORDERS;
        """)
        res = cur.fetchone()
        
        self.assertGreaterEqual(res["installment_orders"], 6, "Phải có ít nhất 6 đơn đăng ký mua trả góp")
        self.assertGreaterEqual(res["deposit_cod_orders"], 5, "Phải có ít nhất 5 đơn đặt cọc COD")
        self.assertGreaterEqual(res["full_payment_orders"], 5, "Phải có ít nhất 5 đơn thanh toán đủ toàn phần")

if __name__ == '__main__':
    unittest.main()
