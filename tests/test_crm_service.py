"""
TDD Test Suite cho Phân hệ 05: Khách hàng cần chăm sóc & Smart CRM (US-5.1).
Kiểm thử lớp nghiệp vụ CrmService.
"""
import os
import unittest

from src.services.crm_service import CrmService

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "retail_dienmay.db"))


class TestCrmService(unittest.TestCase):
    def setUp(self):
        self.service = CrmService(db_path=DB_PATH)

    def test_crm_kpis_and_care_queue_priority_sorting(self):
        """
        FR-CRM-01, FR-CRM-02, FR-CRM-04: Quét điểm chạm chăm sóc, sắp xếp theo Priority Score giảm dần và lọc Cooldown 30 ngày.
        """
        kpis = self.service.get_crm_kpis()
        self.assertGreater(kpis["due_today_count"], 0)
        self.assertGreaterEqual(kpis["cooldown_blocked_count"], 1)

        df = self.service.get_care_queue_dataframe(include_cooldown=False)
        self.assertFalse(df.empty)
        scores = df["priority_score"].tolist()
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertTrue(all(df["in_cooldown"] == 0))

        # Khi bật include_cooldown=True, tổng danh sách phải >= danh sách đã lọc
        df_all = self.service.get_care_queue_dataframe(include_cooldown=True)
        self.assertGreater(len(df_all), len(df))

    def test_personalized_call_script_and_zalo_generation(self):
        """
        FR-CRM-03: Sinh kịch bản thoại AI và tin nhắn Zalo ZNS cá nhân hóa cho Điện Máy Anh Tâm.
        """
        df = self.service.get_care_queue_dataframe()
        row = df.iloc[0]
        script = self.service.generate_personalized_script(
            customer_code=row["customer_code"],
            product_code=row["product_code"],
            trigger_type=row["trigger_type"],
        )
        self.assertIn("Điện Máy Anh Tâm", script["call_script"])
        self.assertIn(row["customer_name"], script["call_script"])
        self.assertIn("Điện Máy Anh Tâm", script["zalo_zns"])
        self.assertGreater(len(script["call_script"]), 40)

    def test_cooldown_blocking_and_technician_double_booking_conflict(self):
        """
        ERR_CRM_001 & ERR_CRM_002: Chặn spam khách hàng trong Cooldown 30d và chặn trùng lịch Kỹ thuật viên.
        """
        df = self.service.get_care_queue_dataframe(include_cooldown=False)
        r1 = df.iloc[0]
        r2 = df.iloc[1]

        created_appts = []
        created_logs = []
        try:
            # 1. Chốt lịch hẹn lần 1 cho NV0003
            res1 = self.service.record_interaction_and_book_service(
                customer_code=r1["customer_code"],
                product_code=r1["product_code"],
                serial_number=r1["serial_number"],
                trigger_type=r1["trigger_type"],
                outcome="CONVERTED_BOOKING",
                appointment_date="2026-12-01",
                time_slot="15:30 (Chiều)",
                technician_code="NV0003",
                note="Test booking 1",
            )
            self.assertTrue(res1["success"])
            created_appts.append(res1["appointment_id"])
            created_logs.append(res1["interaction_id"])

            # 2. Đặt tiếp khách hàng thứ 2 vào đúng khung giờ + ngày của cùng kỹ thuật viên NV0003 -> PHẢI CHẶN ERR_CRM_002
            res_conflict = self.service.record_interaction_and_book_service(
                customer_code=r2["customer_code"],
                product_code=r2["product_code"],
                serial_number=r2["serial_number"],
                trigger_type=r2["trigger_type"],
                outcome="CONVERTED_BOOKING",
                appointment_date="2026-12-01",
                time_slot="15:30 (Chiều)",
                technician_code="NV0003",
                note="Test booking conflict",
            )
            self.assertFalse(res_conflict["success"])
            self.assertEqual(res_conflict["error_code"], "ERR_CRM_002")

            # 3. Gọi lại chính khách hàng r1 ngay hôm nay (vừa mới liên hệ -> đang Cooldown) -> PHẢI CHẶN ERR_CRM_001
            res_spam = self.service.record_interaction_and_book_service(
                customer_code=r1["customer_code"],
                product_code=r1["product_code"],
                serial_number=r1["serial_number"],
                trigger_type=r1["trigger_type"],
                outcome="SNOOZED",
            )
            self.assertFalse(res_spam["success"])
            self.assertEqual(res_spam["error_code"], "ERR_CRM_001")
        finally:
            conn = self.service._get_connection()
            for aid in created_appts:
                if aid is not None:
                    conn.execute("DELETE FROM FACT_SERVICE_APPOINTMENTS WHERE appointment_id = ?;", (aid,))
            for iid in created_logs:
                if iid is not None:
                    conn.execute("DELETE FROM SYS_CRM_INTERACTION_LOG WHERE interaction_id = ?;", (iid,))
            conn.commit()
            conn.close()


if __name__ == "__main__":
    unittest.main()
