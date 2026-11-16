#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STOCK SENSE ERP - MASTER DASHBOARD (6 MODULES)
Cửa hàng Điện máy Anh Tâm (108 Cầu Giấy, Quan Hoa, Cầu Giấy, Hà Nội - CN01)
Điều hướng 6 phân hệ qua Sidebar trái, đồng bộ kiến trúc từ docs/SRS_01..06 và prototypes/stock_sense_dashboard.html.
"""
import os
import sys
import streamlit as st

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.services.alert_service import AlertService
from src.services.clearance_service import ClearanceService
from src.services.crm_service import CrmService
from src.services.inventory_service import InventoryService
from src.services.order_service import OrderService
from src.services.performance_service import PerformanceService
from src.services.replenishment_service import ReplenishmentService
from src.views.styles import inject_stock_sense_styles, render_module_header
from src.views.tab_alerts_view import render_tab_alerts
from src.views.tab_clearance_view import render_tab_clearance
from src.views.tab_crm_view import render_tab_crm
from src.views.tab_inventory_view import render_tab_inventory
from src.views.tab_order_flow_view import render_tab_order_flow
from src.views.tab_performance_view import render_tab_performance
from src.views.tab_replenishment_view import render_tab_replenishment

st.set_page_config(
    page_title="Stock Sense ERP - Điện Máy Anh Tâm",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_stock_sense_styles()

DB_PATH = os.path.join(PROJECT_ROOT, "data", "retail_dienmay.db")

MODULES = [
    "1. Tổng quan kho",
    "2. Cần xử lý hôm nay",
    "3. Gợi ý xả hàng",
    "4. Gợi ý nhập hàng",
    "5. Khách cần chăm sóc",
    "6. Hiệu quả kinh doanh",
]

MODULE_LABELS = {
    "1. Tổng quan kho": "📦 1. Tổng quan kho (US-1.1 & 1.2)",
    "2. Cần xử lý hôm nay": "🔔 2. Cần xử lý hôm nay (US-2.1 & 2.2)",
    "3. Gợi ý xả hàng": "🏷️ 3. Gợi ý xả hàng (US-3.1 & 3.2)",
    "4. Gợi ý nhập hàng": "🛒 4. Gợi ý nhập hàng (US-4.1)",
    "5. Khách cần chăm sóc": "🎧 5. Khách cần chăm sóc (US-5.1)",
    "6. Hiệu quả kinh doanh": "📊 6. Hiệu quả kinh doanh (US-6.1)",
}


@st.cache_resource
def get_all_services():
    return {
        "inventory": InventoryService(DB_PATH),
        "order": OrderService(DB_PATH),
        "alert": AlertService(DB_PATH),
        "clearance": ClearanceService(DB_PATH),
        "replenishment": ReplenishmentService(DB_PATH),
        "crm": CrmService(DB_PATH),
        "performance": PerformanceService(DB_PATH),
    }


services = get_all_services()

# -----------------------------------------------------------------------------
# SIDEBAR TRÁI: THƯƠNG HIỆU, ĐIỀU HƯỚNG 6 MODULES & RBAC TOÀN CỤC
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🏪 Stock Sense ERP")
    st.caption("**Điện Máy Anh Tâm** · 108 Cầu Giấy, Hà Nội (`CN01`)")
    st.markdown("---")

    st.markdown("**🔐 Phân Quyền Truy Cập (RBAC)**")
    role_options = {
        "👑 Chủ tiệm (Xem đầy đủ Giá vốn)": "ROLE_OWNER",
        "👤 Bán hàng (Ẩn trường Giá vốn)": "ROLE_SALES",
    }
    selected_role_label = st.selectbox("Vai trò vận hành:", list(role_options.keys()), index=0, label_visibility="collapsed")
    current_role = role_options[selected_role_label]

    st.markdown("---")
    st.markdown("**🧭 Menu Điều Hành (6 Modules)**")

    if "active_module" not in st.session_state or st.session_state["active_module"] not in MODULES:
        st.session_state["active_module"] = MODULES[0]

    current_idx = MODULES.index(st.session_state["active_module"])
    chosen_module = st.radio(
        "Chọn phân hệ:",
        options=MODULES,
        index=current_idx,
        format_func=lambda m: MODULE_LABELS[m],
        label_visibility="collapsed",
    )
    if chosen_module != st.session_state["active_module"]:
        st.session_state["active_module"] = chosen_module
        st.rerun()

    st.markdown("---")
    st.caption("Chủ hộ: **Nguyễn Anh Tâm (`NV0001`)**  \nCSDL: `data/retail_dienmay.db` (KiotViet x SQLite)")


# -----------------------------------------------------------------------------
# NỘI DUNG CHÍNH THEO MODULE ĐANG CHỌN (LAZY MODULE RENDERING)
# -----------------------------------------------------------------------------
active = st.session_state["active_module"]

if active == "1. Tổng quan kho":
    render_module_header(
        "Hệ thống Quản trị Kho › Module 01: Tổng quan kho & Điều phối dòng hàng",
        "Tổng quan Kho & Dòng hàng 4 Trạng thái (SOH · RES · AVL · INC)",
        "Giám sát sức khỏe tồn kho thiết bị điện máy theo thời gian thực, kiểm đếm Serial/IMEI và điều phối đơn cọc/trả góp.",
    )
    sub1, sub2 = st.tabs([
        "📦 Danh mục & Tồn kho Thiết bị (US-1.1)",
        "🚚 Điều phối Đơn hàng & Dòng hàng (US-1.2)",
    ])
    with sub1:
        render_tab_inventory(services["inventory"], role=current_role)
    with sub2:
        render_tab_order_flow(services["order"])

elif active == "2. Cần xử lý hôm nay":
    render_module_header(
        "Hệ thống Quản trị Kho › Module 02: Cần xử lý hôm nay",
        "Trung tâm Radar Cảnh báo Tác chiến Đầu ngày",
        "Phát hiện tức thời SKU bán chậm/vượt trần chôn vốn (DSI > 60) và nguy cơ cháy hàng (DOS <= Lead Time), tự động khử báo động giả qua INC.",
    )
    render_tab_alerts(services["alert"], role=current_role)

elif active == "3. Gợi ý xả hàng":
    render_module_header(
        "Hệ thống Quản trị Kho › Module 03: Gợi ý xả hàng & Định giá cạnh tranh",
        "Chiến lược Thanh lý Tồn kho & Radar Giá Thị Trường",
        "Sinh 4 kịch bản khuyến mại thông minh (Giảm thẳng, Combo phụ kiện, Bảo dưỡng 24T, Trả góp 0%) kèm mô phỏng dòng tiền và làm tròn giá tâm lý.",
    )
    render_tab_clearance(services["clearance"], role=current_role)

elif active == "4. Gợi ý nhập hàng":
    render_module_header(
        "Hệ thống Quản trị Kho › Module 04: Gợi ý nhập hàng & Tự động hóa PO",
        "Đề xuất Nhập Bổ sung Thích ứng & Gom Đơn PO Theo Hãng",
        "Dự báo nhu cầu RR14/RR30 kết hợp hệ số mùa vụ, tồn an toàn thích ứng, kiểm soát trần ngân sách và tự động gom PO gửi Nhà phân phối.",
    )
    render_tab_replenishment(services["replenishment"], role=current_role)

elif active == "5. Khách cần chăm sóc":
    render_module_header(
        "Hệ thống Quản trị Kho › Module 05: Khách hàng cần chăm sóc & Smart CRM",
        "Trung tâm CSKH 5 Điểm chạm Vàng & Xếp lịch Kỹ thuật viên",
        "Tự động quét hạn bảo dưỡng điều hòa, bán chéo phụ kiện và bảo hành; sinh kịch bản thoại AI, chặn spam 30 ngày và đặt lịch thợ tận nhà.",
    )
    render_tab_crm(services["crm"], role=current_role)

elif active == "6. Hiệu quả kinh doanh":
    render_module_header(
        "Hệ thống Quản trị Kho › Module 06: Hiệu quả kinh doanh & Thác nước lợi nhuận",
        "Phân rã Lợi nhuận Thác nước (Waterfall) & Tỷ lệ Bán kèm (Attach-Rate)",
        "Đo lường vốn gốc thu hồi, chứng minh đòn bẩy lợi nhuận từ Phụ kiện/Dịch vụ, đánh giá Attach-Rate theo chuẩn 60%/70% và duyệt hoa hồng nhân sự.",
    )
    render_tab_performance(services["performance"], role=current_role)

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#64748B; font-size:12px;'>"
    "Stock Sense ERP v2.0 · Cửa hàng Điện máy Anh Tâm (108 Cầu Giấy, Hà Nội) · Dữ liệu SQLite Data Warehouse"
    "</div>",
    unsafe_allow_html=True,
)
