"""
TDD Test Suite cho Phân hệ 04: Gợi ý nhập hàng & Tự động hóa đặt hàng (US-4.1).
Kiểm thử lớp nghiệp vụ ReplenishmentService.
"""
import os
import unittest

from src.services.replenishment_service import ReplenishmentService

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "retail_dienmay.db"))


class TestReplenishmentService(unittest.TestCase):
    def setUp(self):
        self.service = ReplenishmentService(db_path=DB_PATH)

    def test_moq_and_pack_rounding_rules(self):
        """
        FR-REP-05: Kiểm tra quy tắc làm tròn theo MOQ và quy cách đóng gói (pack_size).
        """
        self.assertEqual(self.service.apply_moq_and_pack_rounding(0, moq=5, pack_size=2), 0)
        self.assertEqual(self.service.apply_moq_and_pack_rounding(3, moq=5, pack_size=1), 5)
        self.assertEqual(self.service.apply_moq_and_pack_rounding(7, moq=4, pack_size=4), 8)

    def test_replenishment_recommendations_14_vs_30_days_and_masking(self):
        """
        FR-REP-01..04: Kiểm tra dự báo chu kỳ 14 ngày vs 30 ngày, điểm tin cậy CV và che giá vốn ROLE_SALES.
        """
        plan_14 = self.service.get_replenishment_recommendations(cycle_days=14, budget_cap=200_000_000, role="ROLE_OWNER")
        plan_30 = self.service.get_replenishment_recommendations(cycle_days=30, budget_cap=200_000_000, role="ROLE_OWNER")

        self.assertGreater(plan_14["total_suggested_units"], 0)
        self.assertGreater(plan_30["total_suggested_units"], plan_14["total_suggested_units"])
        for item in plan_14["items"]:
            self.assertGreaterEqual(item["confidence_score"], 50.0)
            self.assertLessEqual(item["confidence_score"], 99.0)

        plan_sales = self.service.get_replenishment_recommendations(cycle_days=14, budget_cap=200_000_000, role="ROLE_SALES")
        self.assertIsNone(plan_sales["estimated_capital"])
        self.assertEqual(plan_sales["display_estimated_capital"], "****** đ")
        self.assertIsNone(plan_sales["items"][0]["cost_price"])

    def test_budget_cap_optimization(self):
        """
        FR-REP-05: Tự động cân đối số lượng nhập không vượt quá Trần ngân sách B_cap.
        """
        plan = self.service.get_replenishment_recommendations(cycle_days=30, budget_cap=80_000_000, role="ROLE_OWNER")
        optimized = self.service.optimize_within_budget(plan["items"], budget_cap=80_000_000)
        total_cost = sum(i["suggested_qty"] * i["cost_price"] for i in optimized)
        self.assertLessEqual(total_cost, 80_000_000)

    def test_po_auto_grouping_by_vendor_and_creation(self):
        """
        FR-REP-06: Gom đơn PO tự động theo Hãng, chặn ROLE_SALES ký duyệt, và lưu DB an toàn cho ROLE_OWNER.
        """
        sample_items = [
            {"product_code": "ML-CS-TC09", "product_name": "ĐH Casper 1HP", "brand": "Casper", "suggested_qty": 10, "cost_price": 5_100_000},
            {"product_code": "TV-CS-43FG6", "product_name": "Tivi Casper 43", "brand": "Casper", "suggested_qty": 8, "cost_price": 4_600_000},
            {"product_code": "TL-AQ-180L", "product_name": "Tủ lạnh Aqua 180L", "brand": "Aqua", "suggested_qty": 6, "cost_price": 3_800_000},
        ]
        grouped = self.service.preview_po_grouping(sample_items)
        self.assertEqual(len(grouped), 2)

        unauth = self.service.create_grouped_purchase_orders(sample_items, role="ROLE_SALES")
        self.assertFalse(unauth["success"])

        created_codes = []
        try:
            res = self.service.create_grouped_purchase_orders(sample_items, role="ROLE_OWNER")
            self.assertTrue(res["success"])
            created_codes = res["created_po_codes"]
            self.assertEqual(len(created_codes), 2)
        finally:
            if created_codes:
                conn = self.service._get_connection()
                for code in created_codes:
                    conn.execute("DELETE FROM PURCHASE_ORDERS WHERE purchase_code = ?;", (code,))
                conn.commit()
                conn.close()


if __name__ == "__main__":
    unittest.main()
