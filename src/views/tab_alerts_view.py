"""
Component hiển thị Giao diện Module 02: Cần xử lý hôm nay (US-2.1 & US-2.2).
"""
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.services.alert_service import AlertService


def render_tab_alerts(service: AlertService, role: str = "ROLE_OWNER"):
    """Render màn hình Radar Cảnh báo tác chiến đầu ngày (Module 02)."""
    kpis = service.get_alert_kpis(role=role)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            label="🧊 VỐN KẸT Ở HÀNG CHẬM",
            value=kpis["display_stagnant_capital"],
            delta=f"{kpis['total_slow_skus']} SKU cần giải phóng" if role != "ROLE_SALES" else "Đã ẩn theo Role Sales",
            delta_color="inverse" if role != "ROLE_SALES" else "off",
        )
    with c2:
        st.metric(
            label="🔴 SKU TỒN CHẾT / VƯỢT TRẦN",
            value=f"{kpis['dead_or_overstock_skus']} Sản phẩm",
            delta="DSI > 60 ngày hoặc vượt Max",
            delta_color="inverse",
        )
    with c3:
        st.metric(
            label="🟠 SKU SẮP HẾT MÙA VỤ",
            value=f"{kpis['seasonal_risk_skus']} Sản phẩm",
            delta="Điều hòa sắp qua cao điểm",
            delta_color="off",
        )
    with c4:
        lost_txt = f"Mất ~{kpis['daily_lost_revenue']:,.0f} đ/ngày" if kpis["daily_lost_revenue"] > 0 else "Đã phủ PO đang về"
        st.metric(
            label="⚡ NGUY CƠ CHÁY HÀNG (CẦN NHẬP)",
            value=f"{kpis['stockout_risk_skus']} SKU Gấp",
            delta=f"{lost_txt} ({kpis['in_transit_skus']} SKU có PO về)",
            delta_color="inverse",
        )

    st.markdown("---")

    df_slow_all = service.get_slow_moving_alerts(role=role, include_snoozed=False)
    df_stockout_all = service.get_stockout_alerts()

    # Hàng 2 Biểu đồ trực quan theo Prototype M2
    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown("##### 📊 Phân bổ Vốn kẹt theo Mặt hàng bán chậm")
        if role == "ROLE_SALES":
            st.info("🔒 Chế độ Bán hàng (`ROLE_SALES`): Biểu đồ giá trị vốn kẹt được bảo mật.")
        elif not df_slow_all.empty:
            fig_cap = px.bar(
                df_slow_all.head(6),
                x="stagnant_capital",
                y="product_code",
                orientation="h",
                color="risk_group",
                text="stagnant_capital",
                labels={
                    "stagnant_capital": "Vốn đang chôn (VNĐ)",
                    "product_code": "Mã SKU",
                    "risk_group": "Nhóm rủi ro",
                },
                color_discrete_map={
                    "Tồn chết / Vượt trần": "#DC2626",
                    "Sắp hết mùa": "#EA580C",
                    "Hãng EOL": "#D97706",
                },
                height=310,
            )
            fig_cap.update_traces(texttemplate="%{text:,.0f} đ", textposition="outside")
            fig_cap.update_layout(yaxis=dict(autorange="reversed"), margin=dict(l=10, r=40, t=20, b=20))
            st.plotly_chart(fig_cap, use_container_width=True)
        else:
            st.success("Không còn SKU nào bị kẹt vốn cần xử lý.")

    with ch2:
        st.markdown("##### ⏱️ Đường băng Tồn kho Khả dụng (DOS) vs Lead Time Hãng")
        if not df_stockout_all.empty:
            fig_dos = go.Figure()
            colors = [
                "#2563EB" if inc > 0 else ("#DC2626" if dos <= lt else "#D97706")
                for inc, dos, lt in zip(
                    df_stockout_all["inc"], df_stockout_all["dos_days"], df_stockout_all["lead_time_days"]
                )
            ]
            fig_dos.add_trace(
                go.Bar(
                    x=df_stockout_all["product_code"],
                    y=df_stockout_all["dos_days"],
                    marker_color=colors,
                    text=[f"{d:.1f}d" for d in df_stockout_all["dos_days"]],
                    textposition="outside",
                    name="Số ngày còn lại (DOS)",
                )
            )
            fig_dos.add_hline(
                y=3,
                line_dash="dash",
                line_color="#DC2626",
                annotation_text="Ngưỡng Lead Time chuẩn (3 ngày)",
                annotation_position="top right",
            )
            fig_dos.update_layout(
                xaxis_title="Mã SKU",
                yaxis_title="Số ngày bán còn lại (DOS)",
                margin=dict(l=10, r=20, t=30, b=20),
                height=310,
            )
            st.plotly_chart(fig_dos, use_container_width=True)
        else:
            st.info("Toàn bộ SKU đều có mức tồn khả dụng an toàn.")

    st.markdown("---")

    sub_t1, sub_t2 = st.tabs([
        f"🔴 Tab 1: Hàng bán chậm, Vượt trần & Hết mùa ({len(df_slow_all)})",
        f"⚡ Tab 2: Cảnh báo Sắp cháy hàng & Đang về ({len(df_stockout_all)})",
    ])

    with sub_t1:
        f1, f2, f3, f4 = st.columns([2, 1, 1, 1])
        with f1:
            kw_slow = st.text_input("🔍 Tìm SKU hoặc Tên thiết bị:", key="m2_slow_kw", placeholder="TV-LG-55C3, Panasonic...")
        with f2:
            risk_opt = st.selectbox("Nhóm rủi ro:", ["Tất cả", "Tồn chết / Vượt trần", "Sắp hết mùa", "Hãng EOL"], key="m2_risk_sel")
        with f3:
            brand_list = ["Tất cả"] + sorted(df_slow_all["brand"].dropna().unique().tolist()) if not df_slow_all.empty else ["Tất cả"]
            brand_opt = st.selectbox("Thương hiệu:", brand_list, key="m2_brand_sel")
        with f4:
            show_snoozed = st.checkbox("Hiện cả mục đã Hoãn", value=False, key="m2_show_snoozed")

        df_slow = service.get_slow_moving_alerts(
            risk_filter=risk_opt,
            brand=brand_opt,
            search=kw_slow,
            role=role,
            include_snoozed=show_snoozed,
        )

        if not df_slow.empty:
            cols_order = [
                c
                for c in [
                    "product_code", "product_name", "brand", "soh", "stagnant_capital",
                    "days_since_last_sale", "dsi_days", "risk_badge", "suggested_clearance_qty",
                ]
                if c in df_slow.columns
            ]
            rename_map = {
                "product_code": "Mã SKU",
                "product_name": "Tên thiết bị",
                "brand": "Hãng",
                "soh": "Tồn (SOH)",
                "stagnant_capital": "Vốn kẹt (đ)",
                "days_since_last_sale": "Chưa bán (ngày)",
                "dsi_days": "DSI (ngày)",
                "risk_badge": "Phân loại rủi ro",
                "suggested_clearance_qty": "Đề xuất xả",
            }
            disp_df = df_slow[cols_order].rename(columns=rename_map)
            fmt = {"DSI (ngày)": "{:.1f}"}
            if "Vốn kẹt (đ)" in disp_df.columns:
                fmt["Vốn kẹt (đ)"] = "{:,.0f}"
            st.dataframe(disp_df.style.format(fmt), use_container_width=True, height=250)

            st.markdown("##### ⚡ Hành động Tác chiến 1 Chạm (Liên thông Module 03 & Tạm hoãn)")
            act_l, act_r = st.columns(2)
            sku_choices = df_slow["product_code"].tolist()
            with act_l:
                target_sku = st.selectbox("Chọn SKU cần đẩy sang Chiến lược Xả hàng:", sku_choices, key="m2_push_sku")
                if st.button("👉 Đẩy sang Module 03: Gợi ý Xả hàng", type="primary", use_container_width=True):
                    st.session_state["selected_clearance_sku"] = target_sku
                    st.session_state["active_module"] = "3. Gợi ý xả hàng"
                    st.rerun()

            with act_r:
                with st.expander("⏰ Tạm hoãn cảnh báo (Snooze Alert - MDL-ALERT-SNOOZE)", expanded=False):
                    sn_sku = st.selectbox("SKU tạm hoãn:", sku_choices, key="m2_sn_sku")
                    sn_days = st.radio("Thời hạn nhắc lại:", [7, 14, 30], index=1, horizontal=True, format_func=lambda d: f"{d} Ngày")
                    sn_reason = st.text_area(
                        "Lý do tạm hoãn bắt buộc (tối thiểu 10 ký tự):",
                        placeholder="Ví dụ: Đang giữ máy mẫu trưng bày phục vụ chương trình cuối tuần...",
                        key="m2_sn_reason",
                    )
                    if st.button("Xác nhận Tạm hoãn Cảnh báo", key="m2_sn_submit"):
                        res = service.snooze_alert(sn_sku, sn_days, sn_reason, role=role)
                        if res["success"]:
                            st.success(res["message"])
                            st.rerun()
                        else:
                            st.error(f"[{res.get('error_code')}] {res['error']}")
        else:
            st.info("Không tìm thấy mặt hàng bán chậm phù hợp điều kiện lọc.")

    with sub_t2:
        sf1, sf2 = st.columns([1, 2])
        with sf1:
            sev_opt = st.selectbox(
                "Mức độ nguy cơ:",
                ["Tất cả", "Đã hết hàng (OOS)", "Nguy cơ đứt hàng tức thì", "Cần lên kế hoạch nhập", "Đang trên đường về"],
                key="m2_sev_sel",
            )
        with sf2:
            kw_st = st.text_input("🔍 Tìm SKU hoặc Tên thiết bị sắp thiếu:", key="m2_st_kw")

        df_st = service.get_stockout_alerts(severity_filter=sev_opt, search=kw_st)
        if not df_st.empty:
            st_disp = df_st[
                [
                    "product_code", "product_name", "brand", "avl", "inc",
                    "lead_time_days", "dos_days", "alert_badge", "daily_lost_revenue", "po_draft_qty",
                ]
            ].rename(
                columns={
                    "product_code": "Mã SKU",
                    "product_name": "Tên thiết bị",
                    "brand": "Hãng",
                    "avl": "Khả dụng (AVL)",
                    "inc": "Đang về (INC)",
                    "lead_time_days": "Lead Time (ng)",
                    "dos_days": "DOS (ng)",
                    "alert_badge": "Trạng thái cảnh báo / PO",
                    "daily_lost_revenue": "DT mất/ngày (đ)",
                    "po_draft_qty": "Gợi ý nhập gấp",
                }
            )
            st.dataframe(
                st_disp.style.format({"DOS (ng)": "{:.1f}", "DT mất/ngày (đ)": "{:,.0f}"}),
                use_container_width=True,
                height=260,
            )

            need_po = df_st[df_st["po_draft_qty"] > 0]["product_code"].tolist()
            if need_po:
                col_po1, col_po2 = st.columns([2, 1])
                with col_po1:
                    po_sku = st.selectbox("Chọn SKU cần tạo đơn nhập bổ sung gấp:", need_po, key="m2_po_sku")
                with col_po2:
                    st.write("")
                    st.write("")
                    if st.button("➕ Nhập hàng gấp (Mở Module 04)", type="primary", use_container_width=True):
                        st.session_state["selected_replenish_sku"] = po_sku
                        st.session_state["active_module"] = "4. Gợi ý nhập hàng"
                        st.rerun()
        else:
            st.success("Không có mặt hàng nào đang thiếu hụt theo bộ lọc.")
