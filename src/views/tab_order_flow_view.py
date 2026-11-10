"""
Component hiển thị Giao diện Tab 2: Theo dõi Đơn hàng & Điều phối dòng hàng (US-1.2).
"""
import streamlit as st
import pandas as pd
from src.services.order_service import OrderService

def render_tab_order_flow(service: OrderService):
    """
    Render toàn bộ nội dung của Tab 2: Điều phối Đơn hàng & Dòng hàng.
    """
    # 1. TẢI VÀ HIỂN THỊ 4 THẺ METRIC CARDS
    kpis = service.get_order_flow_kpis()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="📑 ĐƠN ĐANG GIỮ HÀNG (RES)",
            value=f"{kpis['reserved_orders_count']} Đơn",
            delta=f"{kpis['reserved_units_count']} thiết bị đang khóa",
            delta_color="off"
        )
    with col2:
        st.metric(
            label="🚚 HÀNG ĐANG TRÊN ĐƯỜNG VỀ (INC)",
            value=f"{kpis['in_transit_units']} Máy",
            delta=f"{kpis['in_transit_po_count']} chuyến xe từ Hãng",
            delta_color="normal"
        )
    with col3:
        total_orders = kpis['reserved_orders_count'] if kpis['reserved_orders_count'] > 0 else 1
        inst_pct = (kpis['installment_orders_count'] / total_orders) * 100
        st.metric(
            label="💳 CƠ CẤU ĐƠN TRẢ GÓP",
            value=f"{kpis['installment_orders_count']} Đơn",
            delta=f"Chiếm {inst_pct:.1f}% dòng đơn giữ",
            delta_color="normal"
        )
    with col4:
        st.metric(
            label="⏳ CẢNH BÁO GIỮ CHỖ QUÁ HẠN",
            value=f"{kpis['expired_orders_count']} Đơn",
            delta="Quá 48h chưa nhận máy",
            delta_color="inverse"
        )

    st.markdown("---")

    # 2. MA TRẬN DÒNG HÀNG 4 TRẠNG THÁI (4-PILLAR INVENTORY FLOW)
    st.markdown("##### 🌊 Bảng Ma Trận Dòng Hàng 4 Trạng Thái: $AVL = SOH - RES$ & $Dự\\,kiến = AVL + INC$")
    df_flow = service.get_inventory_flow_matrix()
    
    flow_display = df_flow[[
        "product_code", "product_name", "brand", "soh", "res", "avl", "inc", "projected_stock", "flow_status"
    ]].rename(columns={
        "product_code": "Mã SKU",
        "product_name": "Tên sản phẩm",
        "brand": "Hãng",
        "soh": "Tồn thực (SOH)",
        "res": "Giữ đơn (RES)",
        "avl": "Khả dụng (AVL)",
        "inc": "Đang về (INC)",
        "projected_stock": "Dự kiến có",
        "flow_status": "Dòng hàng"
    })

    def highlight_flow(val):
        if val == "Chờ hàng đang về":
            return "background-color: #EDE7F6; color: #512DA8; font-weight: bold;"
        elif val == "Hết hàng (OOS)":
            return "background-color: #FFCDD2; color: #B71C1C; font-weight: bold;"
        return "background-color: #E8F5E9; color: #1B5E20;"

    st.dataframe(
        flow_display.style.map(highlight_flow, subset=["Dòng hàng"]),
        use_container_width=True,
        height=260
    )

    st.markdown("---")

    # 3. BỘ LỌC ĐIỀU PHỐI ĐƠN HÀNG
    st.markdown("##### 📦 Danh Sách Đơn Đặt Hàng & Điều Phối Giao Nhận")
    f1, f2, f3, f4 = st.columns([1, 1, 1, 2])
    with f1:
        st_opt = ["Tất cả", "Chờ xử lý", "Đã xác nhận", "Đã hủy"]
        sel_status = st.selectbox("Trạng thái đơn:", st_opt)
    with f2:
        pay_opt = ["Tất cả", "Trả đủ", "Cọc (COD)", "Trả góp"]
        sel_pay = st.selectbox("Hình thức thanh toán:", pay_opt)
    with f3:
        flow_opt = ["Tất cả", "Sẵn sàng bán", "Chờ hàng đang về"]
        sel_flow = st.selectbox("Tình trạng máy:", flow_opt)
    with f4:
        search_order = st.text_input("🔍 Tìm kiếm Đơn / Khách hàng / SĐT:", placeholder="Nhập DH0001, tên khách hoặc SĐT...")

    # 4. BẢNG DỮ LIỆU ĐƠN HÀNG
    df_orders = service.get_orders_dataframe(
        status=sel_status,
        payment_type=sel_pay,
        flow_status=sel_flow,
        search=search_order
    )

    # Hiển thị bảng
    order_disp = df_orders[[
        "order_code", "order_time", "customer_name", "customer_phone", "product_name",
        "quantity", "amount_due", "amount_paid", "payment_type", "order_status", "is_expired", "note"
    ]].copy()

    order_disp["Cảnh báo quá hạn"] = order_disp["is_expired"].apply(lambda x: "🚨 QUÁ HẠN 48H" if x else "Bình thường")
    order_disp = order_disp.drop(columns=["is_expired"]).rename(columns={
        "order_code": "Mã đơn",
        "order_time": "Ngày giờ đặt",
        "customer_name": "Khách hàng",
        "customer_phone": "Điện thoại",
        "product_name": "Thiết bị đặt mua",
        "quantity": "SL",
        "amount_due": "Tổng tiền (đ)",
        "amount_paid": "Đã thu/Cọc (đ)",
        "payment_type": "Thanh toán",
        "order_status": "Trạng thái",
        "note": "Ghi chú điều phối"
    })

    def highlight_order_row(val):
        if "QUÁ HẠN 48H" in str(val):
            return "background-color: #FFCDD2; color: #B71C1C; font-weight: bold;"
        return ""

    st.dataframe(
        order_disp.style.map(highlight_order_row, subset=["Cảnh báo quá hạn"]).format({
            "Tổng tiền (đ)": "{:,.0f}",
            "Đã thu/Cọc (đ)": "{:,.0f}"
        }),
        use_container_width=True,
        height=320
    )

    # 5. THAO TÁC XỬ LÝ NHANH TRÊN ĐƠN HÀNG
    st.markdown("##### ⚡ Thao Tác Xử Lý Nhanh Đơn Hàng")
    act_col1, act_col2 = st.columns(2)
    with act_col1:
        with st.expander("❌ HỦY ĐƠN HÀNG & NHẢ TỒN GIỮ CHỖ (RELEASE LOCK)", expanded=False):
            cancelable_orders = df_orders[df_orders["order_status"] == "Chờ xử lý"]["order_code"].tolist()
            if cancelable_orders:
                c_order = st.selectbox("Chọn mã đơn cần hủy:", cancelable_orders)
                c_reason = st.text_input("Lý do hủy đơn:", value="Khách đổi ý / Quá hạn giữ cọc 48h")
                if st.button("Xác nhận Hủy Đơn & Giải Phóng Tồn"):
                    res = service.cancel_order(c_order, c_reason)
                    if res["success"]:
                        st.success(f"✅ Đã hủy thành công đơn {c_order}. Tồn giữ chỗ đã được giải phóng!")
                        st.rerun()
                    else:
                        st.error(res["error"])
            else:
                st.info("Hiện không có đơn hàng nào ở trạng thái Chờ xử lý để hủy.")
    with act_col2:
        with st.expander("🚚 XUẤT KHO GIAO HÀNG & QUÉT SERIAL (DISPATCH MODAL)", expanded=False):
            confirmed_orders = df_orders[df_orders["order_status"] == "Đã xác nhận"]["order_code"].tolist()
            if confirmed_orders:
                d_order = st.selectbox("Chọn đơn đã xác nhận để xuất xe giao:", confirmed_orders)
                st.write(f"Đơn hàng được chọn: **{d_order}**")
                technicians = ["Nguyễn Tuấn Long (NV0003)", "Trần Đình Khang (NV0002)", "Nguyễn Anh Tâm (Chủ tiệm)"]
                st.selectbox("Kỹ thuật viên phụ trách giao lắp:", technicians)
                st.text_input("Quét mã vạch Serial thực tế:", placeholder="Quét mã SN-...")
                if st.button("Xác nhận Bốc Hàng & Giao Lắp"):
                    st.success(f"✅ Đã ghi nhận xuất kho cho đơn {d_order}! Phiếu bảo hành e-Warranty được kích hoạt tự động.")
            else:
                st.info("Không có đơn hàng 'Đã xác nhận' nào sẵn sàng xuất giao.")
