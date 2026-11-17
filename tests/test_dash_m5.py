"""
TDD Kiểm thử Phân hệ 05 trên Plotly Dash: Khách hàng cần chăm sóc, Cooldown 30d, AI Call Script & Đặt lịch thợ.
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
    """Kiểm tra bố cục 7:5, AI Call Script, Cooldown ERR_CRM_001 & Trùng lịch thợ ERR_CRM_002."""

    def test_m5_landmark_ids_match_prototype(self):
        """Kiểm tra Panel M5 đủ các ID KPI, bảng hàng đợi, hồ sơ tác chiến & m5CycleModal."""
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
            "m5CustomerTableBody",
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
            self.assertIn(req_id, ids, f"Thiếu landmark ID M5: {req_id}")

    def test_m5_workspace_script_and_charts(self):
        """Kiểm tra render danh sách khách hàng ưu tiên, AI Call Script Điện Máy Anh Tâm & biểu đồ 5 Điểm chạm."""
        from src.dash_app.callbacks.m5_callbacks import render_m5_workspace

        svc = CrmService(DB_PATH)
        ws = render_m5_workspace(svc, role="ROLE_OWNER")
        self.assertGreater(len(ws["queue_records"]), 0)
        self.assertIn("Điện Máy Anh Tâm", ws["call_script"])
        self.assertIn("Điện Máy Anh Tâm", ws["zalo_zns"])
        self.assertGreater(len(ws["fig_triggers"].data), 0)

    def test_m5_cooldown_conflict_and_booking_persistence(self):
        """Kiểm tra lưu chốt lịch thợ, chặn trùng giờ KTV (ERR_CRM_002) & chặn gọi trùng (ERR_CRM_001)."""
        from src.dash_app.callbacks.m5_callbacks import submit_m5_outcome, render_m5_workspace

        svc = CrmService(DB_PATH)
        ws = render_m5_workspace(svc, include_cooldown=False)
        records = [r for r in ws["queue_records"] if not r["in_cooldown"]]
        self.assertGreaterEqual(len(records), 2, "Cần ít nhất 2 khách hàng ngoài vùng Cooldown để test")

        cust1 = records[0]
        cust2 = records[1]
        techs = svc.get_technicians()
        tech_code = techs[0]["employee_code"]
        test_date = "2026-12-25"
        test_slot = "09:00 - 10:30"

        created_interaction_ids = []
        created_appt_ids = []
        try:
            # 1. Đặt lịch hợp lệ cho khách 1
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

            # 2. Đặt trùng lịch KTV cùng ngày/giờ cho khách 2 -> ERR_CRM_002
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

            # 3. Gọi lại khách 1 trong vùng Cooldown 30 ngày -> ERR_CRM_001
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
