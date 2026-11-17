"""
TDD Kiểm thử Phân hệ 06 (Parity V2):
Tùy chỉnh Chính sách Thưởng (% Phụ kiện, % Dịch vụ, Thưởng nóng/ca, Tiêu chí xếp hạng #1-#3),
Biểu đồ Thác nước Lợi nhuận, Tỷ lệ bán kèm 60%/70%, RBAC ROLE_SALES khóa chỉnh policy & Hoa hồng.
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
    """Kiểm tra Panel chỉnh Chính sách Thưởng M6 V2, Waterfall, Tỷ lệ bán kèm & RBAC."""

    def test_m6_landmark_ids_and_policy_config_panel(self):
        """Kiểm tra Panel M6 đủ các landmark ID V2 (bao gồm m6PolicyConfigPanel) & sạch Attach-Rate."""
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
            "m6PolicyConfigPanel",
            "m6PolicyAccRateInput",
            "m6PolicySrvRateInput",
            "m6PolicyHotBonusInput",
            "m6PolicySortSelect",
            "btn-m6-apply-policy",
            "btn-m6-reset-policy",
            "m6TotalBonusFundDisplay",
            "m6StaffCommissionCards",
            "m6ApproveAllBonusBtn",
        ]:
            self.assertIn(req_id, ids, f"Thiếu landmark ID M6 V2: {req_id}")

        txt = " ".join(_collect_text(panel))
        self.assertNotIn("Attach-Rate", txt)
        self.assertNotIn("Attach Rate", txt)

    def test_m6_dynamic_bonus_policy_ranking_and_rbac_lock(self):
        """Kiểm tra chỉnh % Phụ kiện, % Dịch vụ, Thưởng nóng, Tiêu chí xếp hạng tính lại thưởng & khóa với ROLE_SALES."""
        from src.dash_app.callbacks.m6_callbacks import render_m6_workspace

        svc = PerformanceService(DB_PATH)
        ws_default = render_m6_workspace(svc, role="ROLE_OWNER")
        ws_boosted = render_m6_workspace(
            svc,
            acc_rate_pct=25.0,
            srv_rate_pct=30.0,
            hot_bonus_per_case=100_000.0,
            sort_by="attached_sales",
            role="ROLE_OWNER",
        )
        self.assertGreater(ws_boosted["total_fund_value"], ws_default["total_fund_value"], "Tăng % thưởng phải tăng Quỹ chi")
        self.assertIn("25", ws_boosted["policy_summary_text"])
        self.assertIn("30", ws_boosted["policy_summary_text"])
        self.assertFalse(ws_default["policy_controls_disabled"])

        ws_sales = render_m6_workspace(svc, role="ROLE_SALES")
        self.assertTrue(ws_sales["policy_controls_disabled"], "ROLE_SALES phải bị khóa không được sửa chính sách thưởng")
        self.assertIn("******", ws_sales["total_bonus_fund_display"])
        self.assertIn("******", ws_sales["kpi_profit"])
        self.assertEqual(len(ws_sales["fig_waterfall"].data), 0)
        self.assertTrue(ws_sales["approve_disabled"])

    def test_m6_waterfall_and_category_attach_chart(self):
        """Kiểm tra Waterfall khớp net_gross_profit, đường chuẩn 60%/70% & danh sách nhân sự."""
        from src.dash_app.callbacks.m6_callbacks import render_m6_workspace

        svc = PerformanceService(DB_PATH)
        owner_ws = render_m6_workspace(svc, role="ROLE_OWNER")
        wf_data = svc.get_profit_waterfall_data(role="ROLE_OWNER")

        self.assertGreater(len(owner_ws["fig_waterfall"].data), 0)
        wf_trace = owner_ws["fig_waterfall"].data[0]
        self.assertEqual(wf_trace.type, "waterfall")
        self.assertAlmostEqual(sum(wf_trace.y[:-1]), wf_data["net_gross_profit"], delta=5.0)

        self.assertGreater(len(owner_ws["fig_attach"].data), 0)
        shapes = owner_ws["fig_attach"].layout.shapes
        xs = {s.x0 for s in shapes if hasattr(s, "x0")}
        self.assertIn(60, xs)
        self.assertIn(70, xs)

        staff_txt = " ".join(_collect_text(html.Div(owner_ws["staff_cards"])))
        self.assertIn("Nguyễn", staff_txt)

    def test_m6_commission_approval_and_csv_export(self):
        """Kiểm tra xuất CSV, chặn ROLE_SALES duyệt chi & duyệt thật cho ROLE_OWNER kèm rollback."""
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

        res_sales = submit_m6_approve_commission(svc, employee_code=target_emp, role="ROLE_SALES")
        self.assertFalse(res_sales["success"])
        self.assertEqual(res_sales["error_code"], "ERR_UNAUTHORIZED")

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
