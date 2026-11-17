"""
TDD Kiểm thử mở rộng Tầng Service cho Nâng cấp V2 (M1 Order Detail + Overdue Capital, M4 Multi-SKU, M5 Revenue Pie Periods, M6 Dynamic Commission Policy).
"""
import os
import unittest

from src.services.crm_service import CrmService
from src.services.order_service import OrderService
from src.services.performance_service import PerformanceService
from src.services.replenishment_service import ReplenishmentService

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "retail_dienmay.db"))


class TestServiceV2Enhancements(unittest.TestCase):
    """Kiểm thử API mới ở tầng Services và dữ liệu mở rộng phục vụ Dash Parity V2."""

    def test_m1_order_overdue_capital_and_detail_modal_data(self):
        """OrderService trả vốn kẹt đơn quá hạn 48h & chi tiết đơn giữ chỗ kèm che ROLE_SALES."""
        svc = OrderService(DB_PATH)
        kpis_owner = svc.get_order_flow_kpis(role="ROLE_OWNER")
        self.assertIn("expired_capital", kpis_owner)
        self.assertGreater(kpis_owner["expired_capital"], 0)
        self.assertGreater(kpis_owner["reserved_capital"], kpis_owner["expired_capital"])

        kpis_sales = svc.get_order_flow_kpis(role="ROLE_SALES")
        self.assertIsNone(kpis_sales["expired_capital"])
        self.assertEqual(kpis_sales["display_expired_capital"], "****** đ")

        detail = svc.get_order_detail("DH00030", role="ROLE_OWNER")
        self.assertEqual(detail["order_code"], "DH00030")
        self.assertTrue(detail["is_expired"])
        self.assertTrue(detail["customer_name"])
        self.assertTrue(detail["phone"])
        self.assertGreater(len(detail["items"]), 0)
        self.assertGreater(detail["total_amount"], 0)

    def test_m4_multi_vendor_replenishment_depth(self):
        """ReplenishmentService chu kỳ 14 ngày đề xuất ít nhất 4 mã hàng thuộc >= 3 hãng."""
        svc = ReplenishmentService(DB_PATH)
        plan14 = svc.get_replenishment_recommendations(cycle_days=14, budget_cap=250_000_000, role="ROLE_OWNER")
        plan30 = svc.get_replenishment_recommendations(cycle_days=30, budget_cap=250_000_000, role="ROLE_OWNER")
        need_items = [x for x in plan14["items"] if x["suggested_qty"] > 0]
        brands = {x["brand"] for x in need_items}

        self.assertGreaterEqual(len(need_items), 4, f"Cần >= 4 mã đề xuất nhập ở M4, hiện có: {len(need_items)}")
        self.assertGreaterEqual(len(brands), 3, f"Cần >= 3 hãng ở M4, hiện có: {brands}")
        self.assertGreater(plan30["total_suggested_units"], plan14["total_suggested_units"])

    def test_m5_service_revenue_breakdown_by_period(self):
        """CrmService thống kê doanh thu & số đơn 5 dịch vụ CSKH biến thiên theo 14 / 30 / 90 ngày."""
        svc = CrmService(DB_PATH)
        r14 = svc.get_service_revenue_breakdown(period_days=14, ref_date="2026-11-12")
        r30 = svc.get_service_revenue_breakdown(period_days=30, ref_date="2026-11-12")
        r90 = svc.get_service_revenue_breakdown(period_days=90, ref_date="2026-11-12")

        self.assertGreaterEqual(len(r90), 5)
        tot14 = sum(x["total_revenue"] for x in r14)
        tot30 = sum(x["total_revenue"] for x in r30)
        tot90 = sum(x["total_revenue"] for x in r90)
        self.assertGreater(tot14, 0)
        self.assertGreater(tot30, tot14)
        self.assertGreater(tot90, tot30)
        self.assertAlmostEqual(sum(x["share_pct"] for x in r90), 100.0, delta=0.5)
        self.assertTrue(all(x["order_count"] > 0 for x in r90))

    def test_m6_dynamic_commission_policy_and_ranking(self):
        """PerformanceService cho phép đổi % PK, % DV, thưởng nóng và tiêu chí xếp hạng."""
        svc = PerformanceService(DB_PATH)
        base = svc.calculate_dynamic_commission_ranking(
            acc_rate_pct=15.0, srv_rate_pct=20.0, hot_bonus_per_case=50_000.0, sort_by="commission", role="ROLE_OWNER"
        )
        boosted = svc.calculate_dynamic_commission_ranking(
            acc_rate_pct=22.0, srv_rate_pct=28.0, hot_bonus_per_case=120_000.0, sort_by="attached_sales", role="ROLE_OWNER"
        )
        self.assertGreater(boosted["total_fund"], base["total_fund"])
        self.assertEqual(len(boosted["staff"]), 3)
        sales_vals = [s["attached_sales"] for s in boosted["staff"]]
        self.assertEqual(sales_vals, sorted(sales_vals, reverse=True))

        masked = svc.calculate_dynamic_commission_ranking(role="ROLE_SALES")
        self.assertIsNone(masked["total_fund"])
        self.assertTrue(all(s["dynamic_commission"] is None for s in masked["staff"]))


if __name__ == "__main__":
    unittest.main()
