"""
TDD Kiểm thử Phân hệ 05 (Parity V2):
Bỏ Donut ưu tiên (m5PriorityChart) & top chart row, đặt Pie Chart Doanh thu 5 Dịch vụ CSKH (14/30/90 ngày)
trên Hồ sơ cuộc gọi bên cột phải, Cột trái 7:5 có header/filter cố định & vùng cuộn dọc cân đối chiều cao.
"""
import sqlite3
import unittest
from pathlib import Path
from dash import html

from src.services.crm_service import CrmService

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


class TestDashM5Crm(unittest.TestCase):
    """Kiểm tra bố cục 7:5 M5 V2, Pie doanh thu 5 dịch vụ theo kỳ, thuần Việt & Cooldown/Lịch thợ."""

    def test_m5_landmark_ids_pie_revenue_and_balanced_layout(self):
        """Kiểm tra bỏ m5PriorityChart, có m5ServiceRevenuePie + lọc 14/30/90 ngày + cột trái cuộn dọc cân phải."""
        from src.dash_app.pages.m5_crm import build_m5_panel

        panel = build_m5_panel(is_active=True)
        ids = _collect_ids(panel)
        for req_id in [
            "panel-m5",
            "m5HeaderPendingBadge",
            "m5Kpi-pending",
            "m5Kpi-maintenance",
            "m5Kpi-crosssell",
            "m5Kpi-done",
            "m5QueueScrollBox",
            "m5CustomerTableBody",
            "m5ServiceRevenuePie",
            "m5RevPeriod14",
            "m5RevPeriod30",
            "m5RevPeriod90",
            "m5CallOpsCard",
            "m5PanelCustomerName",
            "m5PanelAddressDevice",
            "m5PanelCallScript",
            "m5CooldownWarningBanner",
            "m5TechConflictBanner",
            "m5OutcomeCard-booked",
            "m5OutcomeCard-callback",
            "m5OutcomeCard-noanswer",
            "m5OutcomeCard-declined",
            "m5PrimarySaveBtn",
            "m5CycleModal",
        ]:
            self.assertIn(req_id, ids, f"Thiếu landmark ID M5 V2: {req_id}")

        self.assertNotIn("m5PriorityChart", ids, "Phải loại bỏ biểu đồ Donut ưu tiên (m5PriorityChart)")
        self.assertNotIn("m5TriggersChart", ids, "Phải thay biểu đồ top bằng Pie doanh thu 5 dịch vụ trên cột phải")

        panel_str = str(panel)
        self.assertIn("overflow-y-auto", panel_str)
        txt = " ".join(_collect_text(panel))
        for banned in ("Cooldown", "AI Call Script", "Smart CRM", "Care Triggers"):
            self.assertNotIn(banned, txt, f"Không để từ chuyên ngành tiếng Anh '{banned}' trên UI M5")

    def test_m5_service_revenue_pie_periods_and_order_count_hover(self):
        """Kiểm tra Pie chart Doanh thu 5 dịch vụ theo kỳ 14/30/90 ngày & Hover hiện số lượng đơn hàng."""
        from src.dash_app.callbacks.m5_callbacks import render_m5_workspace

        svc = CrmService(DB_PATH)
        ws14 = render_m5_workspace(svc, rev_period_days=14, role="ROLE_OWNER")
        ws90 = render_m5_workspace(svc, rev_period_days=90, role="ROLE_OWNER")

        self.assertGreater(len(ws90["queue_records"]), 0)
        self.assertIn("Điện Máy Anh Tâm", ws90["call_script"])
        self.assertIn("Điện Máy Anh Tâm", ws90["zalo_zns"])

        fig14 = ws14["fig_service_pie"]
        fig90 = ws90["fig_service_pie"]
        self.assertEqual(fig90.data[0].type, "pie")
        self.assertGreater(sum(fig90.data[0].values), sum(fig14.data[0].values), "Doanh thu 90 ngày phải lớn hơn 14 ngày")
        cd = fig90.data[0].customdata
        self.assertEqual(len(cd[0]), 4, "Customdata Pie M5 phải gồm 4 trường (Nhóm dịch vụ, Số đơn, Doanh thu, %)")
        self.assertIn("Số lượng đơn", fig90.data[0].hovertemplate or "")

    def test_m5_cooldown_conflict_and_booking_persistence(self):
        """Kiểm tra lưu chốt lịch thợ, chặn trùng giờ KTV (ERR_CRM_002) & chặn gọi trùng (ERR_CRM_001)."""
        from src.dash_app.callbacks.m5_callbacks import submit_m5_outcome, render_m5_workspace

        svc = CrmService(DB_PATH)
        ws = render_m5_workspace(svc, include_cooldown=False)
        records = [r for r in ws["queue_records"] if not r["in_cooldown"]]
        self.assertGreaterEqual(len(records), 2, "Cần ít nhất 2 khách hàng ngoài vùng bảo vệ 30 ngày để test")

        cust1 = records[0]
        cust2 = records[1]
        techs = svc.get_technicians()
        tech_code = techs[0]["employee_code"]
        test_date = "2026-12-25"
        test_slot = "09:00 - 10:30"

        created_interaction_ids = []
        created_appt_ids = []
        try:
            res1 = submit_m5_outcome(
                svc,
                customer_code=cust1["customer_code"],
                product_code=cust1["product_code"],
                serial_number=cust1["serial_number"],
                trigger_type=cust1["trigger_type"],
                outcome_ui="booked",
                appointment_date=test_date,
                time_slot=test_slot,
                technician_code=tech_code,
            )
            self.assertTrue(res1["success"])
            created_interaction_ids.append(res1["interaction_id"])
            if res1.get("appointment_id"):
                created_appt_ids.append(res1["appointment_id"])

            res2 = submit_m5_outcome(
                svc,
                customer_code=cust2["customer_code"],
                product_code=cust2["product_code"],
                serial_number=cust2["serial_number"],
                trigger_type=cust2["trigger_type"],
                outcome_ui="booked",
                appointment_date=test_date,
                time_slot=test_slot,
                technician_code=tech_code,
            )
            self.assertFalse(res2["success"])
            self.assertEqual(res2["error_code"], "ERR_CRM_002")

            res3 = submit_m5_outcome(
                svc,
                customer_code=cust1["customer_code"],
                product_code=cust1["product_code"],
                serial_number=cust1["serial_number"],
                trigger_type=cust1["trigger_type"],
                outcome_ui="callback",
            )
            self.assertFalse(res3["success"])
            self.assertEqual(res3["error_code"], "ERR_CRM_001")
        finally:
            conn = sqlite3.connect(DB_PATH)
            for aid in created_appt_ids:
                conn.execute("DELETE FROM FACT_SERVICE_APPOINTMENTS WHERE appointment_id = ?", (aid,))
            for iid in created_interaction_ids:
                conn.execute("DELETE FROM SYS_CRM_INTERACTION_LOG WHERE interaction_id = ?", (iid,))
            conn.commit()
            conn.close()


if __name__ == "__main__":
    unittest.main()
