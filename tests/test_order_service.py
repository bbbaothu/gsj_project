"""
TDD Test Suite cho Phân hệ 2: Theo dõi Đơn hàng & Điều phối dòng hàng (US-1.2)
Kiểm thử lớp nghiệp vụ OrderService.
"""
import os
import unittest

from src.services.order_service import OrderService

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "retail_dienmay.db"))

class TestOrderService(unittest.TestCase):
    def setUp(self):
        self.service = OrderService(db_path=DB_PATH)

    def test_get_order_flow_kpis(self):
        """
        FR-ORD-01 & FR-ORD-05: Kiểm tra 4 thẻ chỉ số dòng hàng và đơn hàng.
        """
        kpis = self.service.get_order_flow_kpis()
        
        self.assertGreaterEqual(kpis["reserved_orders_count"], 20, "Phải có >= 20 đơn đang giữ hàng")
        self.assertGreaterEqual(kpis["in_transit_units"], 40, "Phải có >= 40 máy đang trên đường về kho")
        self.assertGreaterEqual(kpis["installment_orders_count"], 6, "Phải có >= 6 đơn mua trả góp")
        self.assertGreaterEqual(kpis["expired_orders_count"], 4, "Phải phát hiện >= 4 đơn quá hạn 48h")

    def test_inventory_flow_matrix_equations(self):
        """
        FR-ORD-01 & FR-ORD-04: Kiểm tra ma trận dòng hàng 4 trạng thái và công thức toán học:
        Available = SOH - RES
        Projected = Available + INC
        """
        df = self.service.get_inventory_flow_matrix()
        self.assertEqual(len(df), 12, "Ma trận phải có 12 SKU điện máy có Serial")
        
        for _, row in df.iterrows():
            expected_avl = row["soh"] - row["res"]
            expected_proj = expected_avl + row["inc"]
            self.assertEqual(row["avl"], expected_avl, f"Sai lệch AVL tại {row['product_code']}")
            self.assertEqual(row["projected_stock"], expected_proj, f"Sai lệch Projected tại {row['product_code']}")

    def test_get_orders_dataframe_with_expiration_flag(self):
        """
        FR-ORD-03: Kiểm tra cờ cảnh báo quá hạn 48 giờ trên danh sách đơn hàng.
        """
        df_orders = self.service.get_orders_dataframe()
        self.assertGreaterEqual(len(df_orders), 30)
        self.assertIn("is_expired", df_orders.columns)
        self.assertIn("payment_type", df_orders.columns)
        
        expired_orders = df_orders[df_orders["is_expired"] == True]
        self.assertGreaterEqual(len(expired_orders), 4, "Phải có ít nhất 4 đơn có cờ is_expired = True")

    def test_cancel_order_and_release_stock(self):
        """
        FR-ORD-03: Kiểm tra thao tác hủy đơn và nhả tồn giữ hàng.
        """
        # Lấy 1 đơn Chờ xử lý đang quá hạn
        df_orders = self.service.get_orders_dataframe(status="Chờ xử lý")
        order_code = df_orders.iloc[0]["order_code"]
        
        try:
            res = self.service.cancel_order(order_code, reason="Khách đổi ý hủy mua")
            self.assertTrue(res["success"])
            self.assertEqual(res["order_status"], "Đã hủy")
        finally:
            # Khôi phục trạng thái ban đầu để test mang tính bất biến (idempotent)
            conn = self.service._get_connection()
            conn.execute("UPDATE FACT_ORDERS SET status = 'Chờ xử lý', note = NULL WHERE order_code = ?", (order_code,))
            conn.commit()
            conn.close()

if __name__ == '__main__':
    unittest.main()

