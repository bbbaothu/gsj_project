"""
Component hiển thị Giao diện Module 06: Hiệu quả kinh doanh & Thác nước lợi nhuận (US-6.1).
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.services.performance_service import PerformanceService


def render_tab_performance(service: PerformanceService, role: str = "ROLE_OWNER"):
    """Render màn hình Hiệu quả Kinh doanh, Thác nước Lợi nhuận & Attach-Rate (Module 06)."""
    kpis = service.get_performance_kpis(role=role)

    # 1. HÀNG 4 THẺ KPI & NÚT XUẤT BÁO CÁO
    hdr_l, hdr_r = st.columns([4, 1.2])
    with hdr_r:
        if role == "ROLE_OWNER":
            st.download_button(
                label="📥 Xuất Báo cáo (.CSV)",
                data=service.export_financial_summary_csv(),
                file_name="stock_sense_financial_report.csv",
                mime="text/csv",
                use_container_width=True,
            )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "💰 TỔNG DOANH THU THỰC",
        f"{kpis['total_revenue']:,.0f} đ",
        delta=f"Vốn gốc thu hồi: {kpis['display_recovered_capital']} ({kpis['invoice_count']} HĐ)",
    )
    c2.metric(
        "📈 LỢI NHUẬN GỘP HỢP NHẤT",
        kpis["display_net_gross_profit"],
        delta=f"Biên lãi gộp: {kpis['gross_margin_pct']}%" if kpis["gross_margin_pct"] is not None else "Đã bảo mật theo Role",
    )
    c3.metric(
        "🔌 DOANH SỐ BÁN KÈM (PK+DV)",
        f"{kpis['attached_sales']:,.0f} đ",
        delta=(
            f"Đóng góp {kpis['attached_profit_share_pct']}% tổng lãi gộp"
            if kpis["attached_profit_share_pct"] is not None
            else "Động lực tăng biên lãi"
        ),
    )
    c4.metric(
        "🎯 TỶ LỆ GẮN KÈM (ATTACH-RATE)",
        f"{kpis['overall_attach_rate_pct']}%",
        delta="Vượt chuẩn ngành 60%" if kpis["overall_attach_rate_pct"] >= 60.0 else "Cần đẩy mạnh bán kèm",
    )

    st.markdown("---")

    # 2. HÀNG 2 BIỂU ĐỒ: THÁC NƯỚC LỢI NHUẬN (7 COLS) | ATTACH-RATE VS CHUẨN 60%/70% (5 COLS)
    ch_l, ch_r = st.columns([7, 5])
    wf = service.get_profit_waterfall_data(role=role)
    df_cat = service.get_category_attach_rate_dataframe(role=role)

    with ch_l:
        st.markdown("##### 🌊 Biểu đồ Thác nước Phân rã Nguồn Lợi nhuận Gộp")
        if role == "ROLE_SALES":
            st.info("🔒 Chế độ Bán hàng (`ROLE_SALES`): Biểu đồ chi tiết lãi gộp và chiết khấu được bảo mật.")
        else:
            fig_wf = go.Figure(
                go.Waterfall(
                    orientation="v",
                    measure=["relative", "relative", "relative", "relative", "total"],
                    x=[
                        "Lãi Máy Chính",
                        "Lãi Phụ Kiện",
                        "Công Dịch Vụ",
                        "Chiết Khấu / KM",
                        "TỔNG LÃI GỘP",
                    ],
                    textposition="outside",
                    text=[
                        f"+{wf['core_profit']/1e6:.1f}tr",
                        f"+{wf['accessory_profit']/1e6:.1f}tr",
                        f"+{wf['service_profit']/1e6:.1f}tr",
                        f"-{wf['promo_discount_cost']/1e6:.1f}tr",
                        f"{wf['net_gross_profit']/1e6:.1f}tr",
                    ],
                    y=[
                        wf["core_profit"],
                        wf["accessory_profit"],
                        wf["service_profit"],
                        -wf["promo_discount_cost"],
                        0,
                    ],
                    increasing={"marker": {"color": "#059669"}},
                    decreasing={"marker": {"color": "#DC2626"}},
                    totals={"marker": {"color": "#0F172A"}},
                )
            )
            fig_wf.update_layout(yaxis_title="Lợi nhuận (VNĐ)", height=340, margin=dict(l=10, r=10, t=25, b=20))
            st.plotly_chart(fig_wf, use_container_width=True)
            st.success(
                f"💡 **Insight:** Phụ kiện & Công thợ đang đóng góp **{wf['attached_profit_share_pct']}%** tổng lợi nhuận gộp trước chiết khấu!"
            )

    with ch_r:
        st.markdown("##### 🎯 Tỷ lệ Bán kèm (Attach-Rate %) vs Chuẩn 60% / Mục tiêu 70%")
        if not df_cat.empty:
            colors = [
                "#059669" if ar >= 70 else ("#2563EB" if ar >= 60 else ("#D97706" if ar >= 50 else "#DC2626"))
                for ar in df_cat["attach_rate_pct"]
            ]
            fig_ar = go.Figure(
                go.Bar(
                    x=df_cat["attach_rate_pct"],
                    y=df_cat["category"],
                    orientation="h",
                    marker_color=colors,
                    text=[f"{ar:.1f}% ({att}/{core})" for ar, att, core in zip(df_cat["attach_rate_pct"], df_cat["attached_orders"], df_cat["core_orders"])],
                    textposition="outside",
                )
            )
            fig_ar.add_vline(x=60, line_dash="dash", line_color="#DC2626", annotation_text="Chuẩn 60%", annotation_position="top left")
            fig_ar.add_vline(x=70, line_dash="dot", line_color="#059669", annotation_text="Mục tiêu 70%", annotation_position="top right")
            fig_ar.update_layout(
                xaxis=dict(range=[0, 115], title="Attach-Rate (%)"),
                yaxis=dict(autorange="reversed"),
                height=340,
                margin=dict(l=10, r=30, t=30, b=20),
            )
            st.plotly_chart(fig_ar, use_container_width=True)

    st.markdown("---")

    # 3. HÀNG BẢNG ĐÔI: BẢNG NGÀNH HÀNG (7 COLS) | BẢNG XẾP HẠNG & DUYỆT HOA HỒNG (5 COLS)
    b_l, b_r = st.columns([7, 5])
    with b_l:
        st.markdown("##### 📋 Chi tiết Hiệu quả Bán kèm theo Ngành hàng")
        cols_keep = [
            c
            for c in ["category", "core_units", "core_orders", "attached_orders", "attach_rate_pct", "attached_sales", "attached_profit", "rating_badge"]
            if c in df_cat.columns
        ]
        cat_disp = df_cat[cols_keep].rename(
            columns={
                "category": "Ngành hàng",
                "core_units": "Số máy",
                "core_orders": "Đơn chính",
                "attached_orders": "Đơn kèm",
                "attach_rate_pct": "Attach %",
                "attached_sales": "DS PK+DV (đ)",
                "attached_profit": "Lãi PK+DV (đ)",
                "rating_badge": "Đánh giá",
            }
        )
        fmt = {"Attach %": "{:.1f}%", "DS PK+DV (đ)": "{:,.0f}"}
        if "Lãi PK+DV (đ)" in cat_disp.columns:
            fmt["Lãi PK+DV (đ)"] = "{:,.0f}"
        st.dataframe(cat_disp.style.format(fmt), use_container_width=True, hide_index=True, height=220)

    with b_r:
        st.markdown("##### 🏆 Xếp hạng & Duyệt chi Hoa hồng (15% PK + 20% DV)")
        staff_list = service.get_staff_commission_list(role=role)
        for s in staff_list:
            sc1, sc2 = st.columns([3, 1.4])
            with sc1:
                st.markdown(
                    f"**{s['employee_name']}** (`{s['employee_code']}`)  \n"
                    f"DS bán kèm: **{(s['accessory_sales'] + s['service_sales']):,.0f} đ** · Hoa hồng: **{s['commission_amount']:,.0f} đ**"
                )
            with sc2:
                if s["status"] == "APPROVED":
                    st.success("✅ Đã duyệt")
                else:
                    if st.button("✓ Duyệt chi", key=f"m6_comm_{s['employee_code']}", disabled=(role != "ROLE_OWNER"), use_container_width=True):
                        res = service.approve_commission(s["employee_code"], role=role)
                        if res["success"]:
                            st.success(res["message"])
                            st.rerun()
                        else:
                            st.error(res["error"])
