"""
Cấu hình Design System CSS đồng bộ với Stock Sense Prototype (Industrial Utilitarian).
"""
import streamlit as st


def inject_stock_sense_styles() -> None:
    """Nhúng CSS Design Tokens cho toàn bộ Dashboard 6 Module Stock Sense."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700&family=Space+Grotesk:wght@600;700&display=swap');

            html, body, [class*="css"] {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            }
            h1, h2, h3, h4, h5 {
                font-family: 'Space Grotesk', 'Inter', sans-serif !important;
                color: #0F172A;
                letter-spacing: -0.015em;
            }
            /* Thẻ KPI chuẩn mật độ cao */
            div[data-testid="stMetric"] {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 12px 14px;
                box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
            }
            div[data-testid="stMetricLabel"] {
                font-size: 11px !important;
                font-weight: 700 !important;
                color: #475569 !important;
                text-transform: uppercase;
                letter-spacing: 0.04em;
            }
            div[data-testid="stMetricValue"] {
                font-family: 'JetBrains Mono', monospace !important;
                font-size: 22px !important;
                font-weight: 700 !important;
                color: #0F172A !important;
            }
            /* Sidebar Industrial Slate */
            section[data-testid="stSidebar"] {
                background-color: #F8FAFC;
                border-right: 1px solid #E2E8F0;
            }
            section[data-testid="stSidebar"] div[role="radiogroup"] label {
                padding: 6px 10px;
                border-radius: 6px;
                margin-bottom: 2px;
                font-weight: 500;
                transition: background-color 0.15s ease;
            }
            section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
                background-color: #EFF6FF;
            }
            /* Banner tiêu đề phân hệ */
            .ss-header-banner {
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-left: 4px solid #0F172A;
                border-radius: 8px;
                padding: 12px 16px;
                margin-bottom: 12px;
            }
            .ss-breadcrumb {
                font-size: 11px;
                color: #64748B;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.04em;
            }
            .ss-title {
                font-size: 20px;
                font-weight: 700;
                color: #0F172A;
                margin: 2px 0;
            }
            .ss-subtitle {
                font-size: 12.5px;
                color: #475569;
                margin: 0;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_module_header(breadcrumb: str, title: str, subtitle: str) -> None:
    """Hiển thị tiêu đề chuẩn của từng phân hệ."""
    st.markdown(
        f"""
        <div class="ss-header-banner">
            <div class="ss-breadcrumb">{breadcrumb}</div>
            <div class="ss-title">{title}</div>
            <p class="ss-subtitle">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
