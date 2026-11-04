"""
Component hiển thị Giao diện Tab 1: Danh mục sản phẩm & Tồn kho thiết bị (US-1.1).
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from src.services.inventory_service import InventoryService

def render_tab_inventory(service: InventoryService, role: str = "ROLE_OWNER"):
    """
    Render toàn bộ nội dung của Tab 1: Danh mục sản phẩm & Tồn kho.
    """
    # 1. TẢI VÀ HIỂN THỊ 4 THẺ METRIC CARDS
    kpis = service.get_kpis(role=role)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="📦 TỔNG SỐ LƯỢNG SKU",
            value=f"{kpis['total_skus']} SKU",
            delta="Mặt hàng kinh doanh"
        )
    with col2:
        st.metric(
            label="🏢 TỔNG TỒN THỰC TẾ (SOH)",
            value=f"{kpis['total_soh']} Máy",
            delta="Hiện diện vật lý tại kho"
        )
    with col3:
        st.metric(
            label="💰 TỔNG GIÁ VỐN TỒN KHO",
            value=kpis["display_capital"],
            delta="Tài sản vốn lưu động" if role != "ROLE_SALES" else "Đã bảo mật theo Role",
            delta_color="normal" if role != "ROLE_SALES" else "off"
        )
    with col4:
        alert_text = f"⚠️ {kpis['stockout_count']} Cần nhập | 🛑 {kpis['overstock_count']} Tồn cao"
        delta_val = f"Vốn kẹt: {kpis['display_overstock_capital']}" if role != "ROLE_SALES" else "Cảnh báo mất cân đối"
        st.metric(
            label="🚨 CẢNH BÁO TỒN KHO",
            value=alert_text,
            delta=delta_val,
            delta_color="inverse"
        )

    st.markdown("---")

    # 2. BỘ LỌC ĐA CHIỀU
    f_col1, f_col2, f_col3, f_col4 = st.columns([2, 1, 1, 1])
    with f_col1:
        search_kw = st.text_input("🔍 Tìm kiếm theo Mã SKU hoặc Tên sản phẩm:", placeholder="Nhập Sony, Daikin, TV-SN...")
    with f_col2:
        category_options = ["Tất cả", "Tivi", "Điều hòa", "Tủ lạnh", "Máy giặt", "Dịch vụ", "Phụ kiện"]
        selected_category = st.selectbox("Nhóm hàng:", category_options)
    with f_col3:
        brand_options = ["Tất cả", "Sony", "Samsung", "LG", "Daikin", "Panasonic", "Casper", "Aqua", "Toshiba"]
        selected_brand = st.selectbox("Thương hiệu:", brand_options)
    with f_col4:
        status_options = ["Tất cả", "Tồn kho an toàn", "Cảnh báo: Cần nhập gấp", "Cảnh báo: Tồn kho quá cao"]
        selected_status = st.selectbox("Trạng thái:", status_options)

    # 3. LẤY DỮ LIỆU BẢNG ĐÃ QUA LỌC
    df_products = service.get_products_dataframe(
        category=selected_category,
        brand=selected_brand,
        status=selected_status,
        search=search_kw,
        role=role
    )

    # 4. MA TRẬN PHÂN TÁN (PLOTLY SCATTER PLOT) - Phân tích Cảm tính vs Thực tế
    st.markdown("##### 🎯 Ma trận Phân tích Tồn kho Thực tế vs. Nhu cầu")
    df_serial_only = df_products[df_products["has_serial"] == 1].copy()
    if not df_serial_only.empty:
        # Giả lập số lượng đã bán để hiển thị trực quan nếu chưa join invoice
        fig = px.scatter(
            df_serial_only,
            x="stock_on_hand",
            y="sale_price",
            size="stock_on_hand",
            color="inventory_status",
            hover_name="product_name",
            text="product_code",
            labels={
                "stock_on_hand": "Số lượng Tồn kho vật lý (SOH)",
                "sale_price": "Giá bán niêm yết (VNĐ)",
                "inventory_status": "Trạng thái sức khỏe"
            },
            color_discrete_map={
                "Cảnh báo: Tồn kho quá cao": "#E53935",
                "Cảnh báo: Cần nhập gấp": "#FB8C00",
                "Tồn kho an toàn": "#43A047"
            },
            size_max=35,
            height=360
        )
        fig.update_traces(textposition="top center", textfont_size=10)
        fig.update_layout(margin=dict(l=20, r=20, t=25, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # 5. BẢNG DANH MỤC SẢN PHẨM & TỒN KHO CHI TIẾT
    st.markdown(f"##### 📋 Danh sách Mặt hàng ({len(df_products)} SKU)")
    
    # Định dạng cột hiển thị
    display_df = df_products.copy()
    rename_cols = {
        "product_code": "Mã SKU",
        "product_name": "Tên sản phẩm",
        "brand": "Hãng",
        "sale_price": "Giá bán (đ)",
        "stock_on_hand": "Tồn kho (SOH)",
        "min_stock": "Định mức Min",
        "max_stock": "Trần Max",
        "inventory_status": "Trạng thái sức khỏe"
    }
    if "cost_price" in display_df.columns:
        rename_cols["cost_price"] = "Giá vốn (đ)"
    if "capital_tied" in display_df.columns:
        rename_cols["capital_tied"] = "Vốn đọng (đ)"

    cols_order = [c for c in ["product_code", "product_name", "brand", "cost_price", "sale_price", "stock_on_hand", "capital_tied", "inventory_status"] if c in display_df.columns]
    
    st_df = display_df[cols_order].rename(columns=rename_cols)

    def highlight_status(val):
        if "Tồn kho quá cao" in str(val):
            return "background-color: #FFCDD2; color: #B71C1C; font-weight: bold;"
        elif "Cần nhập gấp" in str(val):
            return "background-color: #FFE0B2; color: #E65100; font-weight: bold;"
        return "background-color: #C8E6C9; color: #1B5E20;"

    style_format = {"Giá bán (đ)": "{:,.0f}"}
    if "Giá vốn (đ)" in st_df.columns:
        style_format["Giá vốn (đ)"] = "{:,.0f}"
    if "Vốn đọng (đ)" in st_df.columns:
        style_format["Vốn đọng (đ)"] = "{:,.0f}"

    st.dataframe(
        st_df.style.map(highlight_status, subset=["Trạng thái sức khỏe"]).format(style_format),
        use_container_width=True,
        height=320
    )

    # 6. TRA CỨU CHI TIẾT SERIAL/IMEI THỰC TẾ
    st.markdown("##### 🔍 Tra cứu Chi tiết Serial / IMEI Thiết bị trong Kho")
    serial_skus = df_products[df_products["has_serial"] == 1]["product_code"].tolist()
    if serial_skus:
        selected_sku = st.selectbox("Chọn Mã SKU cần kiểm đếm Serial:", serial_skus)
        drilldown = service.get_serial_drilldown(selected_sku)

        s_col1, s_col2 = st.columns([1, 2])
        with s_col1:
            st.info(f"**Tên thiết bị:** {drilldown['product_name']}\n\n"
                    f"**Tồn kho vật lý (SOH):** {drilldown['stock_on_hand']} máy\n\n"
                    f"**Serial tồn kho thực tế:** {len(drilldown['serials'])} mã\n\n"
                    f"**Kiểm kê toàn vẹn:** {'✅ KHỚP TUYỆT ĐỐI' if drilldown['is_integrity_ok'] else '❌ CẢNH BÁO LỆCH'}")
        with s_col2:
            if drilldown["serials"]:
                df_ser = pd.DataFrame(drilldown["serials"]).rename(columns={
                    "serial_number": "Số Serial / IMEI",
                    "branch_code": "Kho lưu trữ",
                    "status": "Trạng thái",
                    "import_date": "Ngày giờ nhập kho"
                })
                st.dataframe(df_ser, use_container_width=True, height=200)
            else:
                st.warning("Mặt hàng này hiện không có Serial nào trong kho (Đã bán hết hoặc SOH = 0).")
