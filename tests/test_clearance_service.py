"""
TDD Test Suite cho Phân hệ 03: Gợi ý xả hàng & Định giá cạnh tranh (US-3.1 & US-3.2).
Kiểm thử lớp nghiệp vụ ClearanceService.
"""
import os
import unittest

from src.services.clearance_service import ClearanceService

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "retail_dienmay.db"))


class TestClearanceService(unittest.TestCase):
    def setUp(self):
        self.service = ClearanceService(db_path=DB_PATH)

    def test_psychological_price_rounding(self):
        """
        FR-CLR-06: Kiểm tra quy tắc làm tròn giá tâm lý bán lẻ đuôi ..50.000 hoặc ..90.000 đ.
        """
        self.assertEqual(self.service.round_psychological_price(17_532_000), 17_550_000)
        self.assertEqual(self.service.round_psychological_price(8_981_000), 8_990_000)
        self.assertIn(self.service.round_psychological_price(25_740_000) % 100_000, (50_000, 90_000))

    def test_clearance_kpis_and_candidates_masking(self):
        """
        FR-CLR-01: Kiểm tra KPI xả hàng và che giấu giá vốn/lợi nhuận đối với ROLE_SALES.
        """
        owner_kpis = self.service.get_clearance_kpis(role="ROLE_OWNER")
        self.assertGreater(owner_kpis["expected_recovery_capital"], 400_000_000)
        self.assertGreater(owner_kpis["total_target_qty"], 20)

        sales_kpis = self.service.get_clearance_kpis(role="ROLE_SALES")
        self.assertIsNone(sales_kpis["expected_recovery_capital"])
        self.assertIsNone(sales_kpis["expected_gross_profit"])
        self.assertEqual(sales_kpis["display_recovery_capital"], "****** đ")

        candidates_sales = self.service.get_clearance_candidates(role="ROLE_SALES")
        self.assertGreaterEqual(len(candidates_sales), 4)
        self.assertIsNone(candidates_sales[0]["cost_price"])

    def test_generate_4_tactics_and_simulator(self):
        """
        FR-CLR-02 & FR-CLR-03: Sinh đủ 4 phương án khuyến mại và mô phỏng tài chính tức thời.
        """
        tactics = self.service.generate_4_tactics("TV-LG-55C3", target_qty=10)
        self.assertEqual(len(tactics), 4)
        self.assertEqual([t["tactic_code"] for t in tactics], ["PA1", "PA2", "PA3", "PA4"])
        recommended = [t for t in tactics if t["is_recommended"]]
        self.assertEqual(len(recommended), 1)

        sim = self.service.simulate_financials("TV-LG-55C3", "PA2", target_qty=10, extra_discount_pct=0.0, role="ROLE_OWNER")
        self.assertEqual(sim["recovered_capital"], 10 * 22_500_000)
        self.assertGreater(sim["net_gross_profit"], 0)
        self.assertGreater(sim["roi_pct"], 10.0)
        self.assertFalse(sim["is_loss"])

        # Kiểm tra cảnh báo cắt lỗ khi giảm sâu 25%
        sim_loss = self.service.simulate_financials("TV-LG-55C3", "PA1", target_qty=10, extra_discount_pct=25.0, role="ROLE_OWNER")
        self.assertTrue(sim_loss["is_loss"])
        self.assertLess(sim_loss["net_gross_profit"], 0)

    def test_market_price_radar_and_pai(self):
        """
        FR-CLR-05 & FR-CLR-06: Đối chiếu giá ĐMX/MediaMart/Online Min, tính PAI và làm tròn giá gợi ý.
        """
        radar = self.service.get_market_price_radar("TV-LG-55C3", role="ROLE_OWNER")
        self.assertEqual(len(radar["competitors"]), 3)
        self.assertIn(radar["suggested_price"] % 100_000, (50_000, 90_000))
        self.assertGreater(radar["pai_pct"], 0.0)
        self.assertIsNotNone(radar["cost_price"])

    def test_approve_campaign_blocks_sales_role_on_loss_and_persists_owner(self):
        """
        FR-CLR-04 & ERR_CLR_001: Chặn ROLE_SALES duyệt bán dưới giá vốn; cho phép ROLE_OWNER lưu chiến dịch.
        """
        bad_res = self.service.approve_clearance_campaign(
            product_code="TV-LG-55C3",
            tactic_code="PA1",
            target_qty=10,
            clearance_price=21_000_000,
            role="ROLE_SALES",
        )
        self.assertFalse(bad_res["success"])
        self.assertEqual(bad_res["error_code"], "ERR_CLR_001")

        # Lưu thử và dọn dẹp để test bất biến
        conn = self.service._get_connection()
        orig_price = conn.execute("SELECT sale_price FROM DIM_PRODUCTS WHERE product_code='TV-LG-55C3';").fetchone()[0]
        conn.close()
        created_id = None
        try:
            ok_res = self.service.approve_clearance_campaign(
                product_code="TV-LG-55C3",
                tactic_code="PA2",
                target_qty=10,
                clearance_price=26_990_000,
                role="ROLE_OWNER",
            )
            self.assertTrue(ok_res["success"])
            created_id = ok_res["campaign_id"]
        finally:
            conn = self.service._get_connection()
            if created_id is not None:
                conn.execute("DELETE FROM FACT_CLEARANCE_CAMPAIGNS WHERE campaign_id = ?;", (created_id,))
            conn.execute("UPDATE DIM_PRODUCTS SET sale_price = ? WHERE product_code='TV-LG-55C3';", (orig_price,))
            conn.commit()
            conn.close()


if __name__ == "__main__":
    unittest.main()
