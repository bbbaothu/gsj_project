"""
Component hiển thị Giao diện Module 05: Khách hàng cần chăm sóc & Smart CRM (US-5.1).
"""
import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

from src.services.crm_service import CrmService


def render_tab_crm(service: CrmService, role: str = "ROLE_OWNER"):
    """Render màn hình Trung tâm CSKH 5 Điểm chạm Vàng & Đặt lịch thợ (Module 05)."""
    kpis = service.get_crm_kpis()

    # 1. 4 THẺ KPI VĨ MÔ
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "📞 CẦN LIÊN HỆ HÔM NAY",
        f"{kpis['due_today_count']} Khách hàng",
        delta=f"Đang chặn spam 30d: {kpis['cooldown_blocked_count']} KH",
    )
    c2.metric("❄️ HẠN BẢO DƯỠNG ĐIỀU HÒA", f"{kpis['ac_maint_due_count']} Hộ gia đình", delta="Ưu tiên gọi sáng nay")
    c3.metric("🔌 BÁN CHÉO PK & BẢO HÀNH", f"{kpis['cross_or_warranty_count']} Cơ hội", delta="Giá treo TV, Ống đồng, Gia hạn BH")
    c4.metric(
        "💵 DOANH THU CSKH THÁNG NÀY",
        f"{kpis['expected_service_revenue']:,.0f} đ",
        delta=f"{kpis['booked_appointments_count']} lịch hẹn thợ đã xếp",
    )

    st.markdown("---")

    df_all = service.get_care_queue_dataframe(include_cooldown=True)
    df_ready = df_all[df_all["in_cooldown"] == 0] if not df_all.empty else df_all

    # 2. HÀNG 2 BIỂU ĐỒ TRỰC QUAN
    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown("##### 🎯 Phễu 5 Điểm chạm Vàng CSKH (Care Triggers Breakdown)")
        if not df_ready.empty:
            trig_summary = df_ready.groupby("trigger_label", as_index=False).size().rename(columns={"size": "Số khách"})
            fig_trig = px.bar(
                trig_summary.sort_values("Số khách", ascending=True),
                x="Số khách",
                y="trigger_label",
                orientation="h",
                text="Số khách",
                color="trigger_label",
                height=290,
            )
            fig_trig.update_traces(textposition="outside")
            fig_trig.update_layout(showlegend=False, yaxis_title="", margin=dict(l=10, r=30, t=15, b=15))
            st.plotly_chart(fig_trig, use_container_width=True)
        else:
            st.info("Hiện chưa có khách hàng cần liên hệ ngoài chu kỳ Cooldown 30 ngày.")

    with ch2:
        st.markdown("##### 📈 Cơ cấu Mức độ Ưu tiên & Tiến độ Xếp lịch Thợ")
        if not df_ready.empty:
            prio_summary = df_ready.groupby("priority_tier", as_index=False).size().rename(columns={"size": "Số khách"})
            fig_p = px.pie(
                prio_summary,
                names="priority_tier",
                values="Số khách",
                hole=0.45,
                color="priority_tier",
                color_discrete_map={"Cao": "#DC2626", "Vừa": "#D97706", "Thường": "#059669"},
                height=290,
            )
            fig_p.update_traces(textinfo="percent+label+value")
            fig_p.update_layout(showlegend=False, margin=dict(l=10, r=10, t=15, b=15))
            st.plotly_chart(fig_p, use_container_width=True)

    st.markdown("---")

    # 3. MASTER-DETAIL CRM WORKSPACE (7 COLS TABLE | 5 COLS CALL SCRIPT & SCHEDULER)
    left_col, right_col = st.columns([7, 5])

    with left_col:
        st.markdown("##### 📋 Danh sách Khách hàng Theo Điểm chạm Chăm sóc")
        fc1, fc2, fc3, fc4 = st.columns([1.3, 1.1, 1.4, 1.0])
        with fc1:
            trig_options = {"Tất cả": "Tất cả", **service.TRIGGER_LABELS}
            sel_trig = st.selectbox("Lọc Trigger:", list(trig_options.keys()), format_func=lambda k: trig_options[k], key="m5_trig")
        with fc2:
            sel_prio = st.selectbox("Ưu tiên:", ["Tất cả", "Cao", "Vừa", "Thường"], key="m5_prio")
        with fc3:
            kw = st.text_input("🔍 Tìm Tên / SĐT / Máy:", key="m5_kw")
        with fc4:
            inc_cd = st.checkbox("Hiện Cooldown 30d", value=False, key="m5_cd")

        df_queue = service.get_care_queue_dataframe(
            trigger_filter=sel_trig,
            priority_filter=sel_prio,
            search=kw,
            include_cooldown=inc_cd,
        )

        if not df_queue.empty:
            disp = df_queue[
                ["customer_name", "phone", "product_name", "purchase_date", "trigger_label", "priority_badge"]
            ].rename(
                columns={
                    "customer_name": "Khách hàng",
                    "phone": "SĐT",
                    "product_name": "Thiết bị đã mua",
                    "purchase_date": "Ngày mua",
                    "trigger_label": "Điểm chạm chăm sóc",
                    "priority_badge": "Điểm RFM",
                }
            )
            st.dataframe(disp, use_container_width=True, height=340)
        else:
            st.info("Không tìm thấy khách hàng phù hợp điều kiện lọc.")

    with right_col:
        st.markdown("##### 🎧 Khung Tác chiến Cuộc gọi & Đặt lịch Kỹ thuật viên")
        if df_queue.empty:
            st.info("Chọn bộ lọc có khách hàng để hiển thị kịch bản tư vấn.")
        else:
            cust_options = {
                f"{r['customer_code']} | {r['product_code']}": f"{r['customer_name']} ({r['phone']}) — {r['trigger_label']}"
                for _, r in df_queue.iterrows()
            }
            selected_key = st.selectbox(
                "Chọn khách hàng đang tác chiến:",
                options=list(cust_options.keys()),
                format_func=lambda k: cust_options[k],
                key="m5_sel_cust",
            )
            c_code, p_code = selected_key.split(" | ")
            sel_row = df_queue[(df_queue["customer_code"] == c_code) & (df_queue["product_code"] == p_code)].iloc[0]

            if sel_row["in_cooldown"] == 1:
                st.warning(f"⏳ Khách hàng đang trong chu kỳ chống spam đến **{sel_row['cooldown_until']}**.")

            scripts = service.generate_personalized_script(c_code, p_code, sel_row["trigger_type"])
            st.info(f"**💬 AI Call Script cá nhân hóa:**\n\n{scripts['call_script']}")

            outcome_map = {
                "CONVERTED_BOOKING": "✅ Khách đồng ý chốt lịch thợ tận nhà",
                "SNOOZED": "🕒 Khách bận, hẹn gọi lại sau (Đẩy vào Cooldown)",
                "FAILED_CONTACT": "📵 Không nghe máy / Thuê bao",
                "CLOSED_DECLINED": "❌ Khách từ chối (Chưa có nhu cầu)",
            }
            outcome = st.radio("Ghi nhận kết quả cuộc gọi:", list(outcome_map.keys()), format_func=lambda k: outcome_map[k], key="m5_outcome")

            techs = service.get_technicians()
            tech_labels = {t["employee_code"]: f"{t['employee_name']} ({t['employee_code']} - {t['title']})" for t in techs}

            appt_date = None
            time_slot = None
            tech_code = None
            expected_fee = 150_000.0
            if outcome == "CONVERTED_BOOKING":
                d1, d2 = st.columns(2)
                with d1:
                    appt_date_obj = st.date_input("Ngày hẹn thợ:", value=datetime.date(2026, 11, 11), key="m5_appt_date")
                    appt_date = appt_date_obj.isoformat()
                with d2:
                    time_slot = st.selectbox("Khung giờ:", ["09:00 (Sáng)", "14:00 (Chiều)", "15:30 (Chiều)", "17:00 (Chiều)"], index=2, key="m5_slot")
                tech_code = st.selectbox("Phân công Kỹ thuật viên:", list(tech_labels.keys()), format_func=lambda k: tech_labels[k], key="m5_tech")
                expected_fee = float(st.number_input("Phí dịch vụ / vật tư dự kiến (đ):", min_value=0, max_value=5_000_000, value=150_000, step=50_000, key="m5_fee"))

            note_txt = st.text_input("Ghi chú tương tác:", placeholder="Nhập phản hồi hoặc yêu cầu thêm của khách...", key="m5_note")

            b1, b2 = st.columns(2)
            with b1:
                if st.button("💾 LƯU NHẬT KÝ & LÊN LỊCH THỢ", type="primary", use_container_width=True):
                    res = service.record_interaction_and_book_service(
                        customer_code=c_code,
                        product_code=p_code,
                        serial_number=sel_row["serial_number"],
                        trigger_type=sel_row["trigger_type"],
                        outcome=outcome,
                        appointment_date=appt_date,
                        time_slot=time_slot,
                        technician_code=tech_code,
                        service_name=scripts["default_service"],
                        expected_fee=expected_fee,
                        note=note_txt,
                    )
                    if res["success"]:
                        st.success(res["message"])
                    else:
                        st.error(f"[{res.get('error_code')}] {res['error']}")
            with b2:
                if st.button("📲 Gửi tin nhắn Zalo ZNS (Mock OA)", use_container_width=True):
                    st.toast("Đã gửi tin nhắn Zalo ZNS thành công qua Điện Máy Anh Tâm OA!", icon="✅")
                    st.caption(f"Nội dung đã gửi: {scripts['zalo_zns']}")

    with st.expander("🗓️ Xem Lịch Hẹn Kỹ Thuật Viên Tận Nhà Đã Xếp", expanded=False):
        df_appts = service.get_appointments_dataframe()
        if not df_appts.empty:
            st.dataframe(df_appts, use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có lịch hẹn nào.")
