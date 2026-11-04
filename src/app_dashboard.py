#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DASHBOARD KINH DOANH CỬA HÀNG ĐIỆN MÁY TUẤN HƯNG (SOLE TRADER)
Mô hình Hộ kinh doanh cá thể: 1 Chi nhánh duy nhất, 1 Người vận hành, Nhập hàng theo Cảm tính
"""

import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Điện Máy Tuấn Hưng - Sole Trader Dashboard",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = "data/retail_dienmay.db"

@st.cache_data(ttl=30)
def load_data():
    con = sqlite3.connect(DB_PATH)
    
    # 1. Hóa đơn bán hàng
    query_invoices = """
        SELECT 
            i.invoice_code,
            i.invoice_time,
            DATE(i.invoice_time) AS sale_date,
            i.sales_channel,
            i.total_amount,
            i.invoice_discount_amount,
            i.amount_due,
            i.pay_cash,
            i.pay_card,
            i.pay_transfer,
            i.pay_installment,
            i.delivery_status,
            b.branch_name,
            e.employee_name AS seller_name,
            c.customer_code,
            c.customer_name,
            c.customer_type,
            c.phone AS customer_phone,
            l.product_code,
            l.quantity,
            l.unit_price,
            l.cost_price,
            l.line_total,
            (l.line_total - (l.quantity * l.cost_price)) AS line_profit,
            p.product_name,
            p.category_path,
            p.brand,
            p.has_serial
        FROM FACT_INVOICES i
        JOIN FACT_INVOICES_LINES l ON i.invoice_code = l.invoice_code
        JOIN DIM_PRODUCTS p ON l.product_code = p.product_code
        JOIN DIM_CUSTOMERS c ON i.customer_code = c.customer_code
        JOIN DIM_EMPLOYEES e ON i.seller_code = e.employee_code
        JOIN DIM_BRANCHES b ON i.branch_code = b.branch_code;
    """
    df_sales = pd.read_sql_query(query_invoices, con)
    df_sales['sale_date'] = pd.to_datetime(df_sales['sale_date'])

    # 2. Danh mục sản phẩm & tồn kho cảm tính
    df_products = pd.read_sql_query("SELECT * FROM VW_PRODUCT_PERFORMANCE;", con)

    # 3. RFM khách hàng
    df_rfm = pd.read_sql_query("SELECT * FROM VW_CUSTOMER_RFM_METRICS;", con)

    # 4. Bảo hành thiết bị
    query_warranty = """
        SELECT 
            w.warranty_id,
            w.serial_number,
            w.product_code,
            p.product_name,
            p.brand,
            w.customer_code,
            c.customer_name,
            c.phone,
            w.warranty_start_date,
            w.warranty_end_date,
            w.status,
            w.claim_count
        FROM FACT_WARRANTIES w
        JOIN DIM_PRODUCTS p ON w.product_code = p.product_code
        JOIN DIM_CUSTOMERS c ON w.customer_code = c.customer_code;
    """
    df_warranties = pd.read_sql_query(query_warranty, con)

    con.close()
    return df_sales, df_products, df_rfm, df_warranties

df_sales, df_products, df_rfm, df_warranties = load_data()

# -----------------------------------------------------------------------------
# SIDEBAR: THÔNG TIN HỘ KINH DOANH CÁ THỂ
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/color/96/small-business.png", width=64)
st.sidebar.title("🏪 Điện Máy Tuấn Hưng")
st.sidebar.markdown("**Mô hình:** Hộ kinh doanh cá thể *(Sole Trader)*")
st.sidebar.markdown("""
* **Chủ hộ kinh doanh:** Nguyễn Tuấn Hưng
* **Vai trò:** Chủ tiệm kiêm Bán hàng, Thu ngân, Giao hàng & Lắp ráp kỹ thuật
* **Địa điểm:** 108 Cầu Giấy, Quan Hoa, Cầu Giấy, Hà Nội
* **Chi nhánh:** Duy nhất 1 cửa hàng
""")
st.sidebar.markdown("---")

# Bộ lọc ngày
min_date = df_sales['sale_date'].min().date()
max_date = df_sales['sale_date'].max().date()
date_range = st.sidebar.date_input("Khoảng thời gian bán hàng:", value=(min_date, max_date), min_value=min_date, max_value=max_date)

# Bộ lọc Thương hiệu
brands_list = ['Tất cả'] + sorted([b for b in df_sales['brand'].dropna().unique() if b != 'Tuấn Hưng'])
selected_brand = st.sidebar.selectbox("Lọc theo Thương hiệu:", brands_list)

filtered_sales = df_sales.copy()
if len(date_range) == 2:
    start_d, end_d = date_range
    filtered_sales = filtered_sales[(filtered_sales['sale_date'].dt.date >= start_d) & (filtered_sales['sale_date'].dt.date <= end_d)]

if selected_brand != 'Tất cả':
    filtered_sales = filtered_sales[filtered_sales['brand'] == selected_brand]

st.sidebar.markdown("---")
st.sidebar.caption(f"⚡ Đã ghi nhận **{filtered_sales['invoice_code'].nunique()}** hóa đơn bán lẻ")

# -----------------------------------------------------------------------------
# HEADER
# -----------------------------------------------------------------------------
st.title("🏪 BÁO CÁO HOẠT ĐỘNG KINH DOANH - ĐIỆN MÁY TUẤN HƯNG")
st.markdown("""
> **Đặc tả mô hình Sole Trader:** Cửa hàng vận hành độc lập bởi **1 chủ tiệm duy nhất** (Nguyễn Tuấn Hưng), 
> **1 chi nhánh duy nhất**, và **lượng nhập hàng chịu ảnh hưởng nặng từ cảm tính chủ quan** (Gut-feeling inventory bias).
""")

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Tổng quan Vận hành Cửa hàng",
    "⚠️ Phân tích Tồn kho Cảm tính (Gut-Feeling)",
    "👥 Khách hàng Quen & RFM",
    "🛡️ Bảo hành & Trách nhiệm Hậu mãi"
])

# =============================================================================
# TAB 1: TỔNG QUAN VẬN HÀNH
# =============================================================================
with tab1:
    st.subheader("1. Chỉ Số Vận Hành Của Hộ Kinh Doanh Cá Thể")

    total_rev = filtered_sales.groupby('invoice_code')['amount_due'].first().sum()
    total_profit = (filtered_sales['line_total'] - (filtered_sales['quantity'] * filtered_sales['cost_price'])).sum()
    profit_margin = (total_profit / total_rev * 100) if total_rev > 0 else 0.0
    total_orders = filtered_sales['invoice_code'].nunique()
    aov = (total_rev / total_orders) if total_orders > 0 else 0.0
    total_units = filtered_sales[filtered_sales['has_serial'] == 1]['quantity'].sum()

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Tổng Doanh Thu", f"{total_rev:,.0f} đ", delta="Doanh số thực thu")
    kpi2.metric("Lợi Nhuận Gộp", f"{total_profit:,.0f} đ", delta=f"Biên LN: {profit_margin:.1f}%")
    kpi3.metric("Số Đơn Đã Bán", f"{total_orders} đơn", delta="1 người trực tiếp phục vụ")
    kpi4.metric("Giá Trị Đơn (AOV)", f"{aov:,.0f} đ", delta="Trung bình mỗi giao dịch")
    kpi5.metric("Thiết Bị Điện Máy Bán Ra", f"{total_units} máy", delta="Tivi, Điều hòa, Tủ lạnh...")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("##### 📅 Diễn biến Doanh thu & Lợi nhuận hàng ngày")
        daily_perf = filtered_sales.groupby('sale_date').agg(
            revenue=('amount_due', lambda x: x.drop_duplicates().sum()),
            profit=('line_profit', 'sum')
        ).reset_index()

        fig_daily = go.Figure()
        fig_daily.add_trace(go.Bar(
            x=daily_perf['sale_date'], y=daily_perf['revenue'],
            name='Doanh thu (VNĐ)', marker_color='#1976D2'
        ))
        fig_daily.add_trace(go.Scatter(
            x=daily_perf['sale_date'], y=daily_perf['profit'],
            name='Lợi nhuận gộp (VNĐ)', mode='lines+markers', line=dict(color='#388E3C', width=3)
        ))
        fig_daily.update_layout(
            hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=30, b=20), height=350
        )
        st.plotly_chart(fig_daily, use_container_width=True)

    with col2:
        st.markdown("##### 💵 Thói quen Thanh toán tại Cửa hàng")
        inv_headers = filtered_sales.drop_duplicates(subset=['invoice_code'])
        pay_summary = pd.DataFrame({
            'Phương thức': ['Chuyển khoản VietQR', 'Tiền mặt tại quầy'],
            'Số tiền': [inv_headers['pay_transfer'].sum(), inv_headers['pay_cash'].sum()]
        })
        fig_pay = px.pie(
            pay_summary, names='Phương thức', values='Số tiền',
            hole=0.45, color_discrete_sequence=['#00897B', '#FB8C00']
        )
        fig_pay.update_traces(textposition='inside', textinfo='percent+label')
        fig_pay.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=350, showlegend=False)
        st.plotly_chart(fig_pay, use_container_width=True)

# =============================================================================
# TAB 2: PHÂN TÍCH TỒN KHO CẢM TÍNH (GUT-FEELING INVENTORY ANALYSIS)
# =============================================================================
with tab2:
    st.subheader("2. Phân Tích Hiện Tượng Nhập Hàng Theo Cảm Tính (Gut-Feeling Inventory Bias)")
    st.markdown("""
    > 🧠 **Góc nhìn Data Analyst:** Ở mô hình Hộ kinh doanh cá thể, chủ tiệm thường nhập hàng dựa trên **sở thích cá nhân** 
    > hoặc **lời chào mời chiết khấu của đại lý** thay vì phân tích nhu cầu thực tế. Điều này dẫn đến sự phân kỳ nghiêm trọng:
    > * **Cụm 1 - Ứ đọng vốn (Dead Stock / Overstock):** Hàng giá cao kén khách nhưng nhập quá nhiều $\rightarrow$ Kẹt vốn hàng trăm triệu.
    > * **Cụm 2 - Đứt gãy nguồn cung (Stockout / OOS):** Hàng bình dân nhu cầu cao nhưng nhập quá ít $\rightarrow$ Hết hàng, mất doanh thu.
    """)

    # Tính toán vốn tồn kho
    df_prod_serial = df_products[df_products['has_serial'] == 1].copy()
    df_prod_serial['capital_tied'] = df_prod_serial['stock_on_hand'] * df_prod_serial['cost_price']
    total_capital_tied = df_prod_serial['capital_tied'].sum()
    dead_stock_capital = df_prod_serial[df_prod_serial['inventory_status'] == 'Cảnh báo: Tồn kho quá cao']['capital_tied'].sum()
    oos_count = len(df_prod_serial[df_prod_serial['stock_on_hand'] == 0])

    stock_kpi1, stock_kpi2, stock_kpi3 = st.columns(3)
    stock_kpi1.metric("Tổng Vốn Tồn Kho Đang Đọng", f"{total_capital_tied:,.0f} đ", delta="Vốn nằm trong kho")
    stock_kpi2.metric("Vốn Kẹt Ở Hàng Tồn Quá Cao", f"{dead_stock_capital:,.0f} đ", delta=f"Chiếm {(dead_stock_capital/total_capital_tied)*100:.1f}% tổng vốn", delta_color="inverse")
    stock_kpi3.metric("Số Mặt Hàng Cháy Hàng (OOS)", f"{oos_count} sản phẩm", delta="Hết sạch hàng để bán", delta_color="inverse")

    st.markdown("---")

    # Ma trận phân tán Tồn kho vs. Tốc độ bán (Scatter Plot)
    st.markdown("##### 🎯 Ma trận Phân tán: Tồn kho Thực tế vs. Tốc độ Đã bán")
    fig_scatter = px.scatter(
        df_prod_serial,
        x='total_units_sold',
        y='stock_on_hand',
        size='capital_tied',
        color='inventory_status',
        hover_name='product_name',
        text='product_name',
        labels={
            'total_units_sold': 'Số lượng đã bán (Nhu cầu thực tế)',
            'stock_on_hand': 'Số lượng tồn kho (Quyết định nhập hàng)',
            'inventory_status': 'Trạng thái'
        },
        color_discrete_map={
            'Cảnh báo: Tồn kho quá cao': '#E53935',
            'Cảnh báo: Cần nhập gấp': '#FF9800',
            'Tồn kho an toàn': '#43A047'
        },
        size_max=45
    )
    fig_scatter.update_traces(textposition='top center', textfont_size=10)
    fig_scatter.add_hline(y=10, line_dash="dash", line_color="gray", annotation_text="Ngưỡng tồn trần an toàn (10 máy)")
    fig_scatter.update_layout(height=450, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("##### 📋 Bảng Chi Tiết Tồn Kho & Đánh Giá Rủi Ro")
    display_cols = ['product_name', 'brand', 'sale_price', 'cost_price', 'stock_on_hand', 'total_units_sold', 'capital_tied', 'inventory_status']
    stock_table = df_prod_serial[display_cols].copy()
    stock_table.columns = ['Tên thiết bị', 'Hãng', 'Giá bán (đ)', 'Giá vốn (đ)', 'Tồn kho', 'Đã bán', 'Vốn đọng (đ)', 'Trạng thái tồn kho']

    def highlight_status(val):
        if 'Tồn kho quá cao' in str(val):
            return 'background-color: #FFCDD2; color: #B71C1C; font-weight: bold;'
        elif 'Cần nhập gấp' in str(val):
            return 'background-color: #FFE0B2; color: #E65100; font-weight: bold;'
        return 'background-color: #C8E6C9; color: #1B5E20;'

    st.dataframe(
        stock_table.sort_values(by='Vốn đọng (đ)', ascending=False)
                   .style.map(highlight_status, subset=['Trạng thái tồn kho'])
                   .format({'Giá bán (đ)': '{:,.0f}', 'Giá vốn (đ)': '{:,.0f}', 'Vốn đọng (đ)': '{:,.0f}'}),
        use_container_width=True, height=350
    )

# =============================================================================
# TAB 3: KHÁCH HÀNG & PHÂN KHÚC RFM
# =============================================================================
with tab3:
    st.subheader("3. Khách Hàng Quen Thuộc & Phân Khúc RFM")
    st.caption("Cửa hàng cá thể chủ yếu phục vụ cư dân và hộ gia đình bán kính 3-5km xung quanh khu vực Cầu Giấy")

    def assign_rfm(row):
        f = row['frequency']
        m = row['monetary']
        r = row['recency_days']
        if pd.isna(m) or m == 0:
            return 'Chưa mua hàng'
        if f >= 3 and m >= 30000000:
            return '1. Khách VIP / Hộ kinh doanh lớn'
        elif f >= 2:
            return '2. Khách quen thân thiết'
        elif r <= 30:
            return '3. Khách mới mua gần đây'
        else:
            return '4. Khách vãng lai / Lâu chưa quay lại'

    df_rfm_calc = df_rfm.copy()
    df_rfm_calc['segment'] = df_rfm_calc.apply(assign_rfm, axis=1)

    r_col1, r_col2 = st.columns([2, 1])
    with r_col1:
        st.markdown("##### 👥 Cơ cấu nhóm khách hàng của cửa hàng")
        seg_summary = df_rfm_calc.groupby('segment').agg(
            customers=('customer_code', 'count'),
            total_spent=('monetary', 'sum')
        ).reset_index()

        fig_rfm = px.bar(
            seg_summary, x='segment', y='customers', text='customers',
            color='segment', color_discrete_sequence=['#1565C0', '#2E7D32', '#F9A825', '#C62828']
        )
        fig_rfm.update_traces(textposition='outside')
        fig_rfm.update_layout(xaxis_title="Nhóm khách", yaxis_title="Số khách", showlegend=False, height=320)
        st.plotly_chart(fig_rfm, use_container_width=True)

    with r_col2:
        st.markdown("##### 💰 Doanh thu mang lại theo nhóm")
        fig_rfm_pie = px.pie(
            seg_summary[seg_summary['total_spent'] > 0], names='segment', values='total_spent', hole=0.45,
            color_discrete_sequence=['#1565C0', '#2E7D32', '#F9A825', '#C62828']
        )
        fig_rfm_pie.update_traces(textinfo='percent+label')
        fig_rfm_pie.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=320, showlegend=False)
        st.plotly_chart(fig_rfm_pie, use_container_width=True)

    st.markdown("##### 📞 Sổ Danh Bạ Khách Hàng (Dành cho Anh Tuấn Hưng chăm sóc định kỳ)")
    st.dataframe(
        df_rfm_calc[['customer_code', 'customer_name', 'phone', 'recency_days', 'frequency', 'monetary', 'segment']]
            .sort_values(by='monetary', ascending=False)
            .rename(columns={
                'customer_code': 'Mã KH', 'customer_name': 'Họ tên', 'phone': 'Số điện thoại',
                'recency_days': 'Số ngày từ lần mua cuối', 'frequency': 'Số lần mua',
                'monetary': 'Tổng tiền mua (đ)', 'segment': 'Phân loại'
            })
            .style.format({'Tổng tiền mua (đ)': '{:,.0f}', 'Số ngày từ lần mua cuối': '{:.0f}'}),
        use_container_width=True, height=260
    )

# =============================================================================
# TAB 4: BẢO HÀNH & TRÁCH NHIỆM HẬU MÃI
# =============================================================================
with tab4:
    st.subheader("4. Quản Lý Bảo Hành & Hỗ Trợ Kỹ Thuật Tận Nhà")
    st.caption("Ưu thế cạnh tranh của Sole Trader: Chủ tiệm trực tiếp hỗ trợ bảo hành và sửa chữa tận nhà cho bà con trong khu vực")

    w_col1, w_col2, w_col3 = st.columns(3)
    total_w = len(df_warranties)
    active_w = len(df_warranties[df_warranties['status'] == 'Hiệu lực'])
    claimed_w = len(df_warranties[df_warranties['claim_count'] > 0])

    w_col1.metric("Tổng Phiếu Bảo Hành e-Warranty", f"{total_w} phiếu", delta="Đã kích hoạt cho khách")
    w_col2.metric("Còn Hạn Bảo Hành", f"{active_w} máy", delta="Trong thời gian cam kết")
    w_col3.metric("Đang Xử Lý Sửa Chữa / Hỗ Trợ", f"{claimed_w} ca", delta="Anh Hưng đang xử lý tận nhà")

    st.markdown("---")
    st.markdown("##### 🛠️ Danh sách Khách hàng đang cần hỗ trợ Bảo hành / Sửa chữa")
    claims = df_warranties[df_warranties['claim_count'] > 0][[
        'serial_number', 'product_name', 'brand', 'customer_name', 'phone', 'warranty_end_date', 'status'
    ]].copy()
    claims.columns = ['Số Serial/IMEI', 'Tên thiết bị', 'Hãng', 'Tên khách hàng', 'SĐT khách', 'Hạn bảo hành', 'Tình trạng']

    st.dataframe(claims, use_container_width=True, height=200)

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Cửa hàng Điện máy Tuấn Hưng | 108 Cầu Giấy, Hà Nội | Hệ thống PoS KiotViet x SQLite Data Warehouse</div>", unsafe_allow_html=True)
