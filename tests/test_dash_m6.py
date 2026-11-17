"""
TDD Kiểm thử Phân hệ 06 trên Plotly Dash: Hiệu quả kinh doanh, Thác nước Lợi nhuận, Attach-Rate & Hoa hồng.
"""
import sqlite3
import unittest
from pathlib import Path
from dash import html

from src.services.performance_service import PerformanceService

DB_PATH = str(Path(__file__).resolve().parent.parent / "data" / "retail_dienmay.db")


def _collect_ids(component, found=None):
    if found is None:
        found = set()
    if hasattr(component, "id") and component.id is not None:
        if isinstance(component.id, str):
            found.add(component.id)
    children = getattr(component, "children", None)
    if isinstance(children, (list, tuple)):
        for c in children:
            _collect_ids(c, found)
    elif children is not None and hasattr(children, "to_plotly_json"):
        _collect_ids(children, found)
    return found


def _collect_text(component, chunks=None):
    if chunks is None:
        chunks = []
    if isinstance(component, str):
        chunks.append(component)
        return chunks
    children = getattr(component, "children", None)
    if isinstance(children, (list, tuple)):
        for c in children:
            _collect_text(c, chunks)
    elif children is not None:
        _collect_text(children, chunks)
    return chunks


class TestDashM6Performance(unittest.TestCase):
    """Kiểm tra Biểu đồ Waterfall, Attach-Rate 60%/70%, RBAC ROLE_SALES & Duyệt hoa hồng."""

    def test_m6_landmark_ids_match_prototype(self):
        """Kiểm tra Panel M6 đủ các landmark ID chuẩn Prototype (Header, 4 KPI, Charts, Staff Cards)."""
        from src.dash_app.pages.m6_performance import build_m6_panel

        panel = build_m6_panel(is_active=True)
        ids = _collect_ids(panel)
        for req_id in [
            "panel-m6",
            "m6HeaderInvoiceBadge",
            "m6PeriodSelect",
            "m6ExportCsvBtn",
            "m6KpiRev",
            "m6KpiProfit",
            "m6KpiAttachRev",
            "m6KpiAttachRate",
            "m6WaterfallChart",
            "m6AttachRateChart",
            "m6CategoryTableBody",
            "m6StaffCommissionCards",
            "m6ApproveAllBonusBtn",
        ]:
            self.assertIn(req_id, ids, f"Thiếu landmark ID M6: {req_id}")

    def test_m6_waterfall_attach_rate_and_rbac_masking(self):
        """Kiểm tra Waterfall khớp net_gross_profit, đường chuẩn 60%/70% và che vốn/lãi khi ROLE_SALES."""
        from src.dash_app.callbacks.m6_callbacks import render_m6_workspace

        svc = PerformanceService(DB_PATH)
        owner_ws = render_m6_workspace(svc, role="ROLE_OWNER")
        wf_data = svc.get_profit_waterfall_data(role="ROLE_OWNER")

        # Waterfall chart has Waterfall trace with matching total
        self.assertGreater(len(owner_ws["fig_waterfall"].data), 0)
        wf_trace = owner_ws["fig_waterfall"].data[0]
        self.assertEqual(wf_trace.type, "waterfall")
        self.assertAlmostEqual(sum(wf_trace.y[:-1]), wf_data["net_gross_profit"], delta=5.0)

        # Attach-rate chart has data and reference lines at 60 & 70
        self.assertGreater(len(owner_ws["fig_attach"].data), 0)
        shapes = owner_ws["fig_attach"].layout.shapes
        xs = {s.x0 for s in shapes if hasattr(s, "x0")}
        self.assertIn(60, xs)
        self.assertIn(70, xs)

        # Staff cards contain 3 staff names
        staff_txt = " ".join(_collect_text(html.Div(owner_ws["staff_cards"])))
        self.assertIn("Nguyễn", staff_txt)

        # RBAC ROLE_SALES masks net_gross_profit & Waterfall
        sales_ws = render_m6_workspace(svc, role="ROLE_SALES")
        self.assertIn("******", sales_ws["kpi_profit"])
        self.assertEqual(len(sales_ws["fig_waterfall"].data), 0)
        self.assertTrue(sales_ws["approve_disabled"])

    def test_m6_commission_approval_and_csv_export(self):
        """Kiểm tra xuất CSV Attach_Rate_Pct, chặn ROLE_SALES duyệt chi & duyệt thật cho ROLE_OWNER kèm rollback."""
        from src.dash_app.callbacks.m6_callbacks import (
            generate_m6_csv,
            submit_m6_approve_commission,
        )

        svc = PerformanceService(DB_PATH)
        csv_bytes = generate_m6_csv(svc)
        self.assertIn("Attach_Rate_Pct", csv_bytes.decode("utf-8-sig"))

        staff_list = svc.get_staff_commission_list(role="ROLE_OWNER")
        self.assertGreater(len(staff_list), 0)
        target_emp = staff_list[0]["employee_code"]

        # ROLE_SALES bi chan
        res_sales = submit_m6_approve_commission(svc, employee_code=target_emp, role="ROLE_SALES")
        self.assertFalse(res_sales["success"])
        self.assertEqual(res_sales["error_code"], "ERR_UNAUTHORIZED")

        # Luu trang thai goc de rollback
        conn = sqlite3.connect(DB_PATH)
        orig = conn.execute(
            "SELECT status, approved_at, approved_by FROM FACT_COMMISSION_LEDGER WHERE employee_code = ?",
            (target_emp,),
        ).fetchone()
        conn.close()

        try:
            res_owner = submit_m6_approve_commission(svc, employee_code=target_emp, role="ROLE_OWNER")
            self.assertTrue(res_owner["success"])
            conn2 = sqlite3.connect(DB_PATH)
            after = conn2.execute(
                "SELECT status FROM FACT_COMMISSION_LEDGER WHERE employee_code = ?",
                (target_emp,),
            ).fetchone()
            conn2.close()
            self.assertEqual(after[0], "APPROVED")
        finally:
            conn_restore = sqlite3.connect(DB_PATH)
            conn_restore.execute(
                "UPDATE FACT_COMMISSION_LEDGER SET status = ?, approved_at = ?, approved_by = ? WHERE employee_code = ?",
                (orig[0], orig[1], orig[2], target_emp),
            )
            conn_restore.commit()
            conn_restore.close()


if __name__ == "__main__":
    unittest.main()
