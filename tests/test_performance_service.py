"""
TDD Test Suite cho Phân hệ 06: Hiệu quả kinh doanh & Thác nước lợi nhuận (US-6.1).
Kiểm thử lớp nghiệp vụ PerformanceService.
"""
import os
import unittest

from src.services.performance_service import PerformanceService

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "retail_dienmay.db"))


class TestPerformanceService(unittest.TestCase):
    def setUp(self):
        self.service = PerformanceService(db_path=DB_PATH)

    def test_performance_kpis_and_rbac_masking(self):
        """
        FR-PRF-01: Kiểm tra 4 KPI Hiệu quả kinh doanh và che giấu vốn/lãi đối với ROLE_SALES.
        """
        owner_kpis = self.service.get_performance_kpis(role="ROLE_OWNER")
        self.assertGreater(owner_kpis["total_revenue"], 700_000_000)
        self.assertIsNotNone(owner_kpis["recovered_capital"])
        self.assertIsNotNone(owner_kpis["net_gross_profit"])
        self.assertGreater(owner_kpis["overall_attach_rate_pct"], 50.0)

        sales_kpis = self.service.get_performance_kpis(role="ROLE_SALES")
        self.assertIsNone(sales_kpis["recovered_capital"])
        self.assertIsNone(sales_kpis["net_gross_profit"])
        self.assertEqual(sales_kpis["display_recovered_capital"], "****** đ")
        self.assertEqual(sales_kpis["display_net_gross_profit"], "****** đ")

    def test_waterfall_profit_reconciliation(self):
        """
        FR-PRF-03 & ERR_PRF_003: Khớp nối Thác nước Lợi nhuận dựa trên cost_price lịch sử tại dòng hóa đơn.
        """
        wf = self.service.get_profit_waterfall_data(role="ROLE_OWNER")
        expected_net = (
            wf["core_profit"]
            + wf["accessory_profit"]
            + wf["service_profit"]
            - wf["promo_discount_cost"]
        )
        self.assertAlmostEqual(wf["net_gross_profit"], expected_net, places=0)
        self.assertGreater(wf["core_profit"], 0)
        self.assertGreater(wf["accessory_profit"] + wf["service_profit"], 0)

        wf_sales = self.service.get_profit_waterfall_data(role="ROLE_SALES")
        self.assertIsNone(wf_sales["net_gross_profit"])

    def test_attach_rate_excludes_accessory_only_orders_err_prf_002(self):
        """
        FR-PRF-02 & ERR_PRF_002: Hóa đơn chỉ mua lẻ phụ kiện không được tính vào mẫu số N_core của Attach-Rate.
        """
        df_before = self.service.get_category_attach_rate_dataframe(role="ROLE_OWNER")
        self.assertEqual(len(df_before), 4)
        core_orders_before = int(df_before["core_orders"].sum())

        wf_before = self.service.get_profit_waterfall_data(role="ROLE_OWNER")

        # Chèn 1 hóa đơn chỉ mua lẻ phụ kiện PK-GIATREO-55 (không có máy chính)
        conn = self.service._get_connection()
        cust_code = conn.execute("SELECT customer_code FROM DIM_CUSTOMERS LIMIT 1;").fetchone()[0]
        try:
            conn.execute(
                """
                INSERT INTO FACT_INVOICES (
                    invoice_code, invoice_time, seller_code, branch_code, customer_code,
                    total_amount, invoice_discount_amount, amount_due, pay_cash, note
                ) VALUES ('HDTEST0001', '2026-10-12 10:00:00', 'NV0001', 'CN01', ?, 390000, 0, 390000, 390000, 'Test accessory only');
                """,
                (cust_code,),
            )
            conn.execute(
                """
                INSERT INTO FACT_INVOICES_LINES (
                    invoice_code, product_code, quantity, unit_price, cost_price, line_total, warranty_months
                ) VALUES ('HDTEST0001', 'PK-GIATREO-55', 1, 390000, 190000, 390000, 12);
                """
            )
            conn.commit()
            conn.close()

            df_after = self.service.get_category_attach_rate_dataframe(role="ROLE_OWNER")
            wf_after = self.service.get_profit_waterfall_data(role="ROLE_OWNER")

            # Mẫu số N_core không đổi, nhưng lãi phụ kiện tăng thêm +200.000 đ
            self.assertEqual(int(df_after["core_orders"].sum()), core_orders_before)
            self.assertAlmostEqual(wf_after["accessory_profit"] - wf_before["accessory_profit"], 200_000.0, places=0)
        finally:
            cleanup = self.service._get_connection()
            cleanup.execute("DELETE FROM FACT_INVOICES WHERE invoice_code = 'HDTEST0001';")
            cleanup.commit()
            cleanup.close()

    def test_staff_commission_formula_and_approval(self):
        """
        FR-PRF-04: Tính hoa hồng bán kèm 15% PK + 20% DV và kiểm soát duyệt chi theo Role.
        """
        staff = self.service.get_staff_commission_list(role="ROLE_OWNER")
        self.assertEqual(len(staff), 3)
        for s in staff:
            expected_comm = round(s["accessory_profit"] * 0.15 + s["service_profit"] * 0.20, 0)
            self.assertAlmostEqual(s["commission_amount"], expected_comm, delta=1.0)

        unauth = self.service.approve_commission("NV0003", role="ROLE_SALES")
        self.assertFalse(unauth["success"])

        try:
            ok = self.service.approve_commission("NV0003", role="ROLE_OWNER")
            self.assertTrue(ok["success"])
        finally:
            conn = self.service._get_connection()
            conn.execute(
                "UPDATE FACT_COMMISSION_LEDGER SET status = 'PENDING', approved_at = NULL, approved_by = NULL WHERE employee_code = 'NV0003';"
            )
            conn.commit()
            conn.close()

    def test_export_financial_summary_csv(self):
        """FR-PRF-05: Kết xuất dữ liệu báo cáo tài chính CSV."""
        csv_bytes = self.service.export_financial_summary_csv()
        text = csv_bytes.decode("utf-8-sig")
        self.assertIn("Attach_Rate_Pct", text)


if __name__ == "__main__":
    unittest.main()
