"""
TDD Test Suite cho Phân hệ 02: Cần xử lý hôm nay (US-2.1 & US-2.2).
Kiểm thử lớp nghiệp vụ AlertService.
"""
import os
import unittest

from src.services.alert_service import AlertService

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "retail_dienmay.db"))


class TestAlertService(unittest.TestCase):
    def setUp(self):
        self.service = AlertService(db_path=DB_PATH)

    def test_alert_kpis_owner_vs_sales_masking(self):
        """
        FR-ACT-01: Kiểm tra 4 chỉ số tác chiến đầu ngày và cơ chế che giấu vốn kẹt cho ROLE_SALES.
        """
        owner_kpis = self.service.get_alert_kpis(role="ROLE_OWNER")
        self.assertIsNotNone(owner_kpis["stagnant_capital"])
        self.assertGreater(owner_kpis["stagnant_capital"], 400_000_000)
        self.assertGreaterEqual(owner_kpis["dead_or_overstock_skus"], 3)
        self.assertGreaterEqual(owner_kpis["seasonal_risk_skus"], 1)
        self.assertGreaterEqual(owner_kpis["stockout_risk_skus"], 1)

        sales_kpis = self.service.get_alert_kpis(role="ROLE_SALES")
        self.assertIsNone(sales_kpis["stagnant_capital"])
        self.assertEqual(sales_kpis["display_stagnant_capital"], "****** đ")

    def test_slow_moving_detection_and_sorting(self):
        """
        FR-ACT-02: Phát hiện SKU bán chậm/vượt trần/hết mùa và sắp xếp theo Vốn kẹt giảm dần.
        """
        df = self.service.get_slow_moving_alerts(role="ROLE_OWNER")
        self.assertGreaterEqual(len(df), 3)
        skus = df["product_code"].tolist()
        for expected_sku in ("TV-LG-55C3", "ML-PN-XPU12", "TL-SS-647L"):
            self.assertIn(expected_sku, skus)

        capitals = df["stagnant_capital"].tolist()
        self.assertEqual(capitals, sorted(capitals, reverse=True))

        # Kiểm tra ROLE_SALES không thấy cột cost_price / stagnant_capital
        df_sales = self.service.get_slow_moving_alerts(role="ROLE_SALES")
        self.assertNotIn("cost_price", df_sales.columns)
        self.assertNotIn("stagnant_capital", df_sales.columns)

    def test_stockout_dos_and_in_transit_reconciliation(self):
        """
        FR-ACT-05, FR-ACT-06, FR-ACT-07: Kiểm tra DOS, khử báo động giả khi INC > 0 và tính PO Draft Qty.
        """
        df = self.service.get_stockout_alerts()
        self.assertFalse(df.empty)

        # Các SKU có INC > 0 phải được khử báo động giả (daily_lost_revenue = 0.0)
        in_transit_rows = df[df["inc"] > 0]
        self.assertGreaterEqual(len(in_transit_rows), 4)
        for _, row in in_transit_rows.iterrows():
            self.assertIn("Đang trên đường về", row["alert_badge"])
            self.assertEqual(row["daily_lost_revenue"], 0.0)

        # SKU sắp đứt hàng chưa có PO (ML-DK-FTKB25) phải nằm trong cảnh báo & có PO Draft Qty > 0
        daikin = df[df["product_code"] == "ML-DK-FTKB25"]
        self.assertEqual(len(daikin), 1)
        self.assertGreater(daikin.iloc[0]["po_draft_qty"], 0)

    def test_snooze_alert_validation_and_persistence(self):
        """
        FR-ACT-04 & ERR_ACT_003: Chặn lý do < 10 ký tự, chặn ROLE_SALES, lưu và lọc đúng bản ghi đã Snooze.
        """
        bad_res = self.service.snooze_alert("TV-LG-55C3", 14, "Ngắn", role="ROLE_OWNER")
        self.assertFalse(bad_res["success"])
        self.assertEqual(bad_res["error_code"], "ERR_ACT_003")

        unauth_res = self.service.snooze_alert(
            "TV-LG-55C3", 14, "Giữ hàng trưng bày sự kiện cuối năm tại showroom", role="ROLE_SALES"
        )
        self.assertFalse(unauth_res["success"])
        self.assertEqual(unauth_res["error_code"], "ERR_UNAUTHORIZED")

        try:
            ok_res = self.service.snooze_alert(
                "TV-LG-55C3", 14, "Giữ hàng trưng bày sự kiện Black Friday tại cửa hàng", role="ROLE_OWNER"
            )
            self.assertTrue(ok_res["success"])
            df_active = self.service.get_slow_moving_alerts(role="ROLE_OWNER", include_snoozed=False)
            self.assertNotIn("TV-LG-55C3", df_active["product_code"].tolist())
        finally:
            conn = self.service._get_connection()
            conn.execute("DELETE FROM SYS_ALERT_SNOOZE_LOG WHERE product_code = 'TV-LG-55C3';")
            conn.commit()
            conn.close()


if __name__ == "__main__":
    unittest.main()
