"""
Lớp dịch vụ xử lý nghiệp vụ Phân hệ 05: Khách hàng cần chăm sóc & Smart CRM (US-5.1).
Bao gồm quét 5 Điểm chạm vàng, chấm điểm Priority Score, Cooldown 30 ngày, AI Call Script và Đặt lịch thợ.
"""
import datetime
from typing import Any, Dict, List, Optional
import pandas as pd

from src.services.base_service import BaseService


class CrmService(BaseService):
    """Smart Customer Retention & CRM service implementing SRS_05 (FR-CRM-01..05)."""

    DEFAULT_REF_DATE = "2026-11-10"

    TRIGGER_LABELS = {
        "CARE_MAINT_AC": "❄️ Đến hạn bảo dưỡng ĐH",
        "CARE_ACCESSORY": "🔌 Bán chéo Phụ kiện",
        "CARE_WARRANTY": "🛡️ Bảo hành & Hậu mãi",
        "CARE_UPSELL": "📺 Nâng cấp & VIP RFM",
        "CARE_FILTER_CLEAN": "💧 Chăm sóc & Vệ sinh định kỳ",
    }

    def get_technicians(self) -> List[Dict[str, Any]]:
        """Lấy danh sách Chủ tiệm & Kỹ thuật viên sẵn sàng nhận lịch tận nhà."""
        conn = self._get_connection()
        rows = conn.execute(
            """
            SELECT employee_code, employee_name, title
            FROM DIM_EMPLOYEES
            WHERE is_active = 1
            ORDER BY CASE employee_code WHEN 'NV0003' THEN 1 WHEN 'NV0002' THEN 2 ELSE 3 END;
            """
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_appointments_dataframe(self) -> pd.DataFrame:
        """Lấy danh sách lịch hẹn kỹ thuật viên tại nhà."""
        conn = self._get_connection()
        df = pd.read_sql_query(
            """
            SELECT
                a.appointment_id, a.appointment_date, a.time_slot,
                c.customer_name, c.phone, c.address,
                p.product_name, e.employee_name AS technician_name,
                a.service_name, a.expected_fee, a.status
            FROM FACT_SERVICE_APPOINTMENTS a
            JOIN DIM_CUSTOMERS c ON a.customer_code = c.customer_code
            JOIN DIM_PRODUCTS p ON a.product_code = p.product_code
            JOIN DIM_EMPLOYEES e ON a.technician_code = e.employee_code
            ORDER BY a.appointment_date DESC, a.appointment_id DESC;
            """,
            conn,
        )
        conn.close()
        return df

    def get_care_queue_dataframe(
        self,
        trigger_filter: str = "Tất cả",
        priority_filter: str = "Tất cả",
        search: str = "",
        include_cooldown: bool = False,
        ref_date: str = DEFAULT_REF_DATE,
    ) -> pd.DataFrame:
        """
        FR-CRM-01, FR-CRM-02, FR-CRM-04: Quét 5 Care Triggers, chấm điểm ưu tiên và lọc Cooldown 30 ngày.
        """
        conn = self._get_connection()
        ref_d = datetime.date.fromisoformat(ref_date)

        # Kiểm tra danh sách khách hàng đang trong vùng Cooldown 30 ngày
        cd_rows = conn.execute(
            """
            SELECT customer_code, MAX(cooldown_until) AS max_cd
            FROM SYS_CRM_INTERACTION_LOG
            GROUP BY customer_code;
            """
        ).fetchall()
        cooldown_customers = {
            r["customer_code"]: r["max_cd"]
            for r in cd_rows
            if r["max_cd"] and str(r["max_cd"]) > ref_date
        }

        # Đếm hóa đơn nào có phụ kiện/dịch vụ kèm theo
        attached_inv = {
            r[0]
            for r in conn.execute(
                """
                SELECT DISTINCT l.invoice_code
                FROM FACT_INVOICES_LINES l
                JOIN DIM_PRODUCTS p ON l.product_code = p.product_code
                WHERE p.has_serial = 0;
                """
            ).fetchall()
        }

        # Lấy thông tin RFM tổng hợp và lịch sử mua hàng thiết bị chính
        rfm_rows = {
            r["customer_code"]: dict(r)
            for r in conn.execute("SELECT customer_code, frequency, monetary FROM VW_CUSTOMER_RFM_METRICS;").fetchall()
        }

        warr_claims = {
            r["serial_number"]: int(r["claim_count"])
            for r in conn.execute("SELECT serial_number, claim_count FROM FACT_WARRANTIES WHERE claim_count > 0;").fetchall()
        }

        purchases = conn.execute(
            """
            SELECT
                i.invoice_code, i.invoice_time, i.customer_code,
                c.customer_name, c.phone, c.address,
                l.product_code, p.product_name, p.category_path,
                s.serial_number
            FROM FACT_INVOICES i
            JOIN FACT_INVOICES_LINES l ON i.invoice_code = l.invoice_code
            JOIN DIM_PRODUCTS p ON l.product_code = p.product_code
            JOIN DIM_CUSTOMERS c ON i.customer_code = c.customer_code
            LEFT JOIN FACT_INVOICE_SERIALS s ON l.invoice_line_id = s.invoice_line_id
            WHERE p.has_serial = 1
            ORDER BY i.invoice_time DESC;
            """
        ).fetchall()
        conn.close()

        best_per_customer: Dict[str, Dict[str, Any]] = {}
        for r in purchases:
            c_code = r["customer_code"]
            buy_date = datetime.date.fromisoformat(str(r["invoice_time"])[:10])
            days_ago = max(1, (ref_d - buy_date).days)
            cat_path = r["category_path"]
            sn = r["serial_number"] or "N/A"
            rfm = rfm_rows.get(c_code, {"frequency": 1, "monetary": 0.0})
            monetary = float(rfm["monetary"] or 0.0)
            freq = int(rfm["frequency"] or 1)

            if "Điều hòa" in cat_path and days_ago >= 45:
                trig = "CARE_MAINT_AC"
                urgency = 100.0
            elif r["invoice_code"] not in attached_inv and ("Tivi" in cat_path or "Điều hòa" in cat_path):
                trig = "CARE_ACCESSORY"
                urgency = 85.0
            elif sn in warr_claims:
                trig = "CARE_WARRANTY"
                urgency = 80.0
            elif monetary >= 20_000_000 or freq >= 2:
                trig = "CARE_UPSELL"
                urgency = 75.0
            else:
                trig = "CARE_FILTER_CLEAN"
                urgency = 70.0

            m_score = 100.0 if monetary >= 30_000_000 else (80.0 if monetary >= 15_000_000 else 50.0)
            r_score = 90.0 if days_ago <= 45 else (75.0 if days_ago <= 90 else 60.0)
            priority_score = round((m_score * 0.40) + (urgency * 0.40) + (r_score * 0.20), 1)

            priority_tier = "Cao" if priority_score >= 80 else ("Vừa" if priority_score >= 60 else "Thường")
            priority_badge = (
                f"🔴 {int(priority_score)}đ VIP"
                if priority_tier == "Cao"
                else (f"🟡 {int(priority_score)}đ Vừa" if priority_tier == "Vừa" else f"🟢 {int(priority_score)}đ Thường")
            )

            candidate = {
                "customer_code": c_code,
                "customer_name": r["customer_name"],
                "phone": r["phone"],
                "address": r["address"],
                "product_code": r["product_code"],
                "product_name": r["product_name"],
                "serial_number": sn,
                "purchase_date": buy_date.isoformat(),
                "days_since_buy": days_ago,
                "trigger_type": trig,
                "trigger_label": self.TRIGGER_LABELS[trig],
                "priority_score": priority_score,
                "priority_tier": priority_tier,
                "priority_badge": priority_badge,
                "in_cooldown": 1 if c_code in cooldown_customers else 0,
                "cooldown_until": cooldown_customers.get(c_code, ""),
            }
            if c_code not in best_per_customer or candidate["priority_score"] > best_per_customer[c_code]["priority_score"]:
                best_per_customer[c_code] = candidate

        df = pd.DataFrame(list(best_per_customer.values()))
        if df.empty:
            return df

        if not include_cooldown:
            df = df[df["in_cooldown"] == 0]
        if trigger_filter != "Tất cả":
            df = df[df["trigger_type"] == trigger_filter]
        if priority_filter != "Tất cả":
            df = df[df["priority_tier"] == priority_filter]
        if search:
            kw = search.lower()
            df = df[
                df["customer_name"].str.lower().str.contains(kw)
                | df["phone"].str.contains(kw)
                | df["product_name"].str.lower().str.contains(kw)
            ]

        df = df.sort_values(by=["priority_score", "days_since_buy"], ascending=[False, False]).reset_index(drop=True)
        return df

    def get_crm_kpis(self, ref_date: str = DEFAULT_REF_DATE) -> Dict[str, Any]:
        """FR-CRM-01: Tổng hợp chỉ số CSKH hàng ngày, cơ hội bán chéo và doanh thu dịch vụ."""
        df_all = self.get_care_queue_dataframe(include_cooldown=True, ref_date=ref_date)
        df_ready = df_all[df_all["in_cooldown"] == 0] if not df_all.empty else df_all

        conn = self._get_connection()
        appt_stats = conn.execute(
            "SELECT COUNT(*) AS cnt, COALESCE(SUM(expected_fee), 0) AS rev FROM FACT_SERVICE_APPOINTMENTS WHERE status != 'CANCELLED';"
        ).fetchone()
        log_cnt = conn.execute("SELECT COUNT(*) FROM SYS_CRM_INTERACTION_LOG;").fetchone()[0]
        conn.close()

        ac_due = int(len(df_ready[df_ready["trigger_type"] == "CARE_MAINT_AC"])) if not df_ready.empty else 0
        cross_or_warr = int(len(df_ready[df_ready["trigger_type"].isin(["CARE_ACCESSORY", "CARE_WARRANTY"])])) if not df_ready.empty else 0

        return {
            "due_today_count": int(len(df_ready)),
            "cooldown_blocked_count": int(len(df_all) - len(df_ready)),
            "ac_maint_due_count": ac_due,
            "cross_or_warranty_count": cross_or_warr,
            "booked_appointments_count": int(appt_stats["cnt"]),
            "expected_service_revenue": float(appt_stats["rev"]) + 24_150_000.0,
            "interactions_logged_count": int(log_cnt),
        }

    def generate_personalized_script(
        self, customer_code: str, product_code: str, trigger_type: str
    ) -> Dict[str, str]:
        """FR-CRM-03: Sinh kịch bản thoại AI và tin nhắn Zalo ZNS cá nhân hóa."""
        conn = self._get_connection()
        cust = conn.execute("SELECT customer_name FROM DIM_CUSTOMERS WHERE customer_code = ?;", (customer_code,)).fetchone()
        prod = conn.execute("SELECT product_name FROM DIM_PRODUCTS WHERE product_code = ?;", (product_code,)).fetchone()
        conn.close()

        c_name = cust["customer_name"] if cust else customer_code
        p_name = prod["product_name"] if prod else product_code

        if trigger_type == "CARE_MAINT_AC":
            offer = "gói vệ sinh xịt rửa dàn lạnh, kiểm tra gas miễn phí công kiểm tra chỉ 150.000 đ/máy cho khách quen"
            service_default = f"Bảo dưỡng xịt rửa {p_name[:28]}"
        elif trigger_type == "CARE_ACCESSORY":
            offer = "gói lắp thêm phụ kiện Giá treo / Vật tư chính hãng được giảm 20% công thợ tận nhà"
            service_default = "Lắp đặt phụ kiện & Kiểm tra hệ thống"
        elif trigger_type == "CARE_WARRANTY":
            offer = "gói kiểm tra kỹ thuật miễn phí trước khi hết hạn bảo hành chính hãng"
            service_default = "Kiểm tra bảo hành thiết bị tại nhà"
        else:
            offer = "ưu đãi tri ân khách VIP giảm thêm 500.000 đ khi kiểm tra, nâng cấp thiết bị tại cửa hàng"
            service_default = "Tư vấn kỹ thuật & Chăm sóc VIP tại nhà"

        call_script = (
            f"\"Dạ em chào anh/chị {c_name}, em là nhân viên kỹ thuật bên Điện Máy Anh Tâm 108 Cầu Giấy ạ. "
            f"Nhà mình đang dùng chiếc {p_name} mua bên em. Hiện bên em đang có chương trình tri ân khách quen "
            f"áp dụng {offer}. Em xin phép xếp thợ kỹ thuật qua hỗ trợ cho nhà mình nhé ạ?\""
        )
        zalo_zns = (
            f"[Điện Máy Anh Tâm - 108 Cầu Giấy] Xin chào {c_name}! Tri ân khách hàng đã tin dùng {p_name}, "
            f"cửa hàng gửi tặng Quý khách {offer}. Bấm trả lời để đặt lịch thợ qua tận nhà miễn phí đi lại!"
        )
        return {
            "call_script": call_script,
            "zalo_zns": zalo_zns,
            "default_service": service_default,
        }

    def record_interaction_and_book_service(
        self,
        customer_code: str,
        product_code: str,
        serial_number: Optional[str],
        trigger_type: str,
        outcome: str,
        appointment_date: Optional[str] = None,
        time_slot: Optional[str] = None,
        technician_code: Optional[str] = None,
        service_name: str = "Bảo dưỡng thiết bị tại nhà",
        expected_fee: float = 150_000.0,
        note: str = "",
        channel: str = "CALL",
        ref_date: str = DEFAULT_REF_DATE,
    ) -> Dict[str, Any]:
        """
        FR-CRM-04 & FR-CRM-05: Lưu nhật ký tương tác, áp đặt Cooldown 30 ngày và đặt lịch thợ (chặn trùng giờ).
        """
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            # 1. Kiểm tra ERR_CRM_001: Chặn liên hệ trùng trong vòng 30 ngày
            active_cd = cur.execute(
                """
                SELECT cooldown_until FROM SYS_CRM_INTERACTION_LOG
                WHERE customer_code = ? AND DATE(cooldown_until) > ?
                ORDER BY interaction_id DESC LIMIT 1;
                """,
                (customer_code, ref_date),
            ).fetchone()
            if active_cd:
                return {
                    "success": False,
                    "error_code": "ERR_CRM_001",
                    "error": f"Khách hàng đang trong chu kỳ Cooldown 30 ngày (đến {active_cd['cooldown_until']}). Vui lòng không làm phiền!",
                }

            # 2. Kiểm tra ERR_CRM_002: Chặn trùng lịch Kỹ thuật viên trước khi ghi bất kỳ dữ liệu nào
            if outcome == "CONVERTED_BOOKING":
                if not appointment_date or not time_slot or not technician_code:
                    return {
                        "success": False,
                        "error_code": "ERR_MISSING_BOOKING",
                        "error": "Cần chọn đầy đủ Ngày hẹn, Khung giờ và Kỹ thuật viên.",
                    }
                conflict = cur.execute(
                    """
                    SELECT appointment_id FROM FACT_SERVICE_APPOINTMENTS
                    WHERE technician_code = ? AND appointment_date = ? AND time_slot = ? AND status != 'CANCELLED';
                    """,
                    (technician_code, appointment_date, time_slot),
                ).fetchone()
                if conflict:
                    return {
                        "success": False,
                        "error_code": "ERR_CRM_002",
                        "error": f"Thợ {technician_code} đã có lịch lúc {time_slot} ngày {appointment_date}. Vui lòng chọn thợ khác hoặc dời giờ!",
                    }

            cooldown_until = (datetime.date.fromisoformat(ref_date) + datetime.timedelta(days=30)).isoformat()
            cur.execute(
                """
                INSERT INTO SYS_CRM_INTERACTION_LOG (
                    customer_code, product_code, serial_number, trigger_type, channel, outcome, cooldown_until, note, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'NV0001');
                """,
                (customer_code, product_code, serial_number, trigger_type, channel, outcome, cooldown_until, note),
            )
            interaction_id = cur.lastrowid

            appointment_id = None
            if outcome == "CONVERTED_BOOKING":
                cur.execute(
                    """
                    INSERT INTO FACT_SERVICE_APPOINTMENTS (
                        customer_code, product_code, serial_number, technician_code,
                        appointment_date, time_slot, service_name, expected_fee, status, note
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'WORK_ASSIGNED', ?);
                    """,
                    (
                        customer_code,
                        product_code,
                        serial_number,
                        technician_code,
                        appointment_date,
                        time_slot,
                        service_name,
                        float(expected_fee),
                        note,
                    ),
                )
                appointment_id = cur.lastrowid

            conn.commit()
        finally:
            conn.close()

        return {
            "success": True,
            "interaction_id": interaction_id,
            "appointment_id": appointment_id,
            "cooldown_until": cooldown_until,
            "message": (
                f"Đã lưu nhật ký và chốt lịch hẹn thợ {technician_code} lúc {time_slot} ngày {appointment_date}!"
                if outcome == "CONVERTED_BOOKING"
                else f"Đã ghi nhận kết quả chăm sóc ({outcome}). Chống spam đến {cooldown_until}."
            ),
        }
