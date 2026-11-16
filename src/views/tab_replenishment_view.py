"""
Component hiển thị Giao diện Module 04: Gợi ý nhập hàng & Tự động tạo PO (US-4.1).
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.services.replenishment_service import ReplenishmentService


def render_tab_replenishment(service: ReplenishmentService, role: str = "ROLE_OWNER"):
    """Render màn hình Gợi ý nhập hàng thông minh & Gom đơn PO theo Hãng (Module 04)."""
    if role == "ROLE_SALES":
        st.warning("🔒 Tài khoản Nhân viên bán hàng (`ROLE_SALES`) chỉ xem được số lượng gợi ý nhập và ngày hàng về; thông tin giá vốn, hạn mức ngân sách và chức năng ký duyệt PO bị ẩn.")

    # 1. THANH ĐIỀU KHIỂN THAM SỐ DỰ BÁO
    ctrl1, ctrl2, ctrl3 = st.columns([1.2, 1.3, 1.2])
    with ctrl1:
        cycle_label = st.radio("Chu kỳ lập kế hoạch nhập:", ["14 Ngày tới", "30 Ngày tới"], horizontal=True, key="m4_cycle")
        cycle_days = 14 if "14" in cycle_label else 30
    with ctrl2:
        budget_cap_millions = st.number_input(
            "Trần ngân sách vốn đợt này (Triệu VNĐ):",
            min_value=30,
            max_value=1000,
            value=200,
            step=10,
            disabled=(role == "ROLE_SALES"),
            key="m4_budget_m",
        )
        budget_cap = float(budget_cap_millions) * 1_000_000.0
    with ctrl3:
        vendor_filter = st.selectbox(
            "Lọc Nhà cung cấp / Hãng:",
            ["Tất cả", "Casper", "Daikin", "Aqua", "Toshiba", "Sony", "Panasonic", "LG", "Samsung"],
            key="m4_vendor",
        )

    plan = service.get_replenishment_recommendations(
        cycle_days=cycle_days,
        budget_cap=budget_cap,
        vendor_filter=vendor_filter,
        role=role,
    )
    items = plan["items"]

    # 2. 4 THẺ KPI VĨ MÔ & THANH TIẾN ĐỘ NGÂN SÁCH
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📦 SKU CẦN NHẬP BỔ SUNG", f"{plan['skus_to_replenish']} Mặt hàng", delta=f"Chu kỳ {cycle_days} ngày")
    k2.metric("🚚 TỔNG SỐ LƯỢNG ĐỀ XUẤT", f"{plan['total_suggested_units']} Thiết bị", delta="Đã làm tròn theo MOQ/Thùng")
    k3.metric(
        "💰 TỔNG VỐN DỰ TOÁN",
        plan["display_estimated_capital"],
        delta=f"Trần: {budget_cap_millions} triệu đ" if role != "ROLE_SALES" else "Protected",
    )
    k4.metric("🎯 ĐỘ TIN CẬY DỰ BÁO TB", f"{plan['avg_confidence_score']}%", delta="Dựa trên CV 30 ngày")

    if role != "ROLE_SALES" and plan["estimated_capital"] is not None:
        ratio = min(1.0, plan["estimated_capital"] / budget_cap) if budget_cap > 0 else 0.0
        st.progress(ratio, text=f"Tiến độ giải ngân ngân sách: {plan['estimated_capital']/1e6:.1f}tr / {budget_cap_millions}tr ({ratio*100:.1f}%)")
        if plan["over_budget"]:
            st.error(f"⚠️ `ERR_REP_001`: Dự toán vượt trần ngân sách {plan['estimated_capital'] - budget_cap:,.0f} đ. Bấm 'Cân đối ngân sách' bên dưới hoặc tăng hạn mức.")

    st.markdown("---")

    # 3. 2 BIỂU ĐỒ TRỰC QUAN
    df_items = pd.DataFrame(items)
    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown(f"##### 📈 Dự báo Nhu cầu ({cycle_days} ngày) + An toàn vs Hiện có")
        df_focus = df_items[df_items["suggested_qty"] > 0].head(6)
        if df_focus.empty:
            df_focus = df_items.head(6)
        if not df_focus.empty:
            fig_dem = go.Figure()
            fig_dem.add_trace(
                go.Bar(
                    name="Nhu cầu + Tồn an toàn",
                    x=df_focus["product_code"],
                    y=df_focus["forecast_demand"] + df_focus["safety_stock"],
                    marker_color="#2563EB",
                )
            )
            fig_dem.add_trace(
                go.Bar(
                    name="Tồn khả dụng + Đang về (AVL+INC)",
                    x=df_focus["product_code"],
                    y=(df_focus["avl"] + df_focus["inc"]).clip(lower=0),
                    marker_color="#059669",
                )
            )
            fig_dem.update_layout(barmode="group", height=300, margin=dict(l=10, r=10, t=20, b=20))
            st.plotly_chart(fig_dem, use_container_width=True)

    with ch2:
        st.markdown("##### 🏭 Phân bổ Vốn nhập & Số lượng theo Hãng (PO Grouping)")
        df_pos = df_items[df_items["suggested_qty"] > 0]
        if role == "ROLE_SALES":
            st.info("🔒 Biểu đồ giá trị vốn phân bổ theo Nhà cung cấp được ẩn cho `ROLE_SALES`.")
        elif not df_pos.empty:
            grp_brand = df_pos.groupby("brand", as_index=False)["line_total"].sum()
            fig_b = px.bar(
                grp_brand,
                x="brand",
                y="line_total",
                text="line_total",
                color="brand",
                labels={"brand": "Hãng / Nhà cung cấp", "line_total": "Vốn nhập dự kiến (VNĐ)"},
                height=300,
            )
            fig_b.update_traces(texttemplate="%{text:,.0f} đ", textposition="outside")
            fig_b.update_layout(showlegend=False, margin=dict(l=10, r=10, t=20, b=20))
            st.plotly_chart(fig_b, use_container_width=True)
        else:
            st.success("Tất cả SKU theo bộ lọc hiện tại đều đang đủ hàng kinh doanh.")

    st.markdown("---")

    # 4. BẢNG ĐỀ XUẤT ĐẶT HÀNG TƯƠNG TÁC & GOM ĐƠN PO
    st.markdown("##### 🧾 Bảng Đề xuất Đặt hàng 4 Trụ cột & Điều chỉnh Số lượng (Chỉnh trực tiếp cột `SL Đặt`)")
    if "selected_replenish_sku" in st.session_state:
        st.info(f"📌 Đang chú trọng SKU chuyển từ Module 02: **{st.session_state['selected_replenish_sku']}**")

    edit_df = df_items.copy()
    edit_df["Chon"] = edit_df["suggested_qty"] > 0
    display_cols = ["Chon", "product_code", "product_name", "brand", "forecast_demand", "avl", "inc", "safety_stock", "suggested_qty", "confidence_score"]
    if role != "ROLE_SALES":
        display_cols.extend(["cost_price", "line_total"])

    col_cfg = {
        "Chon": st.column_config.CheckboxColumn("Chọn", default=True),
        "product_code": st.column_config.TextColumn("Mã SKU", disabled=True),
        "product_name": st.column_config.TextColumn("Tên thiết bị", disabled=True),
        "brand": st.column_config.TextColumn("Hãng", disabled=True),
        "forecast_demand": st.column_config.NumberColumn("Nhu cầu", format="%.1f", disabled=True),
        "avl": st.column_config.NumberColumn("Khả dụng", disabled=True),
        "inc": st.column_config.NumberColumn("Đang về", disabled=True),
        "safety_stock": st.column_config.NumberColumn("Tồn an toàn", disabled=True),
        "suggested_qty": st.column_config.NumberColumn("SL Đặt", min_value=0, step=1),
        "confidence_score": st.column_config.NumberColumn("Tin cậy (%)", format="%.1f%%", disabled=True),
    }
    if role != "ROLE_SALES":
        col_cfg["cost_price"] = st.column_config.NumberColumn("Đơn giá vốn (đ)", format="%,.0f", disabled=True)
        col_cfg["line_total"] = st.column_config.NumberColumn("Thành tiền (đ)", format="%,.0f", disabled=True)

    edited = st.data_editor(
        edit_df[display_cols],
        column_config=col_cfg,
        use_container_width=True,
        hide_index=True,
        height=320,
        key=f"m4_editor_{cycle_days}_{vendor_filter}",
    )

    selected_rows = []
    for _, r in edited.iterrows():
        if r["Chon"] and int(r["suggested_qty"]) > 0:
            orig = next((x for x in items if x["product_code"] == r["product_code"]), {})
            row_dict = dict(orig)
            row_dict["suggested_qty"] = int(r["suggested_qty"])
            if role != "ROLE_SALES":
                row_dict["line_total"] = float(r["suggested_qty"]) * float(orig.get("cost_price") or 0.0)
            selected_rows.append(row_dict)

    if role != "ROLE_SALES":
        btn1, btn2, btn3 = st.columns([1.2, 1.3, 1.2])
        with btn1:
            if st.button("⚖️ Tự động Cân đối theo Ngân sách", use_container_width=True):
                opt = service.optimize_within_budget(selected_rows, budget_cap)
                opt_total = sum(o["suggested_qty"] * (o["cost_price"] or 0.0) for o in opt)
                st.success(f"Đã tối ưu phương án vừa khít ngân sách: {opt_total:,.0f} đ / {budget_cap:,.0f} đ!")

        po_groups = service.preview_po_grouping(selected_rows)
        with st.expander(f"📑 Xem trước Gom Đơn PO theo Nhà phân phối ({len(po_groups)} Đơn PO)", expanded=bool(po_groups)):
            if po_groups:
                for idx, g in enumerate(po_groups, start=1):
                    st.markdown(f"**Đơn PO {idx} — {g['vendor_name']}**: `{g['total_units']} thiết bị` | Tổng tiền: **{g['total_amount']:,.0f} đ**")
                    st.dataframe(pd.DataFrame(g["items"]), use_container_width=True, hide_index=True)
            else:
                st.info("Chưa có SKU nào có SL Đặt > 0 để gom đơn PO.")

        with btn2:
            if st.button("🚀 KÝ DUYỆT & TẠO ĐƠN PO VÀO KHO", type="primary", use_container_width=True):
                res = service.create_grouped_purchase_orders(selected_rows, role=role)
                if res["success"]:
                    st.success(res["message"])
                else:
                    st.error(res["error"])
        with btn3:
            if po_groups:
                csv_bytes = service.export_po_groups_csv(po_groups)
                st.download_button(
                    label="📥 Xuất Excel/CSV Đơn PO",
                    data=csv_bytes,
                    file_name=f"stock_sense_po_cycle{cycle_days}d.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
