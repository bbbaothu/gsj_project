"""
Thư viện dựng biểu đồ Plotly chuẩn Design System Stock Sense (Industrial Slate / Blue / Emerald / Rose / Amber).
"""
import plotly.graph_objects as go


def apply_stock_sense_layout(fig: go.Figure, height: int = 300, margin=None) -> go.Figure:
    """Áp dụng chuẩn màu sắc, lưới và typography Inter / JetBrains Mono cho biểu đồ Plotly."""
    if margin is None:
        margin = dict(l=16, r=20, t=24, b=24)
    fig.update_layout(
        height=height,
        margin=margin,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=11, color="#475569"),
        hoverlabel=dict(bgcolor="#0F172A", font_color="#FFFFFF", font_size=11),
    )
    fig.update_xaxes(showgrid=False, linecolor="#E2E8F0", tickfont=dict(size=11, color="#64748B"))
    fig.update_yaxes(gridcolor="#F1F5F9", zerolinecolor="#CBD5E1", tickfont=dict(size=11, color="#64748B"))
    return fig


def empty_figure(message: str = "Chưa có dữ liệu hiển thị", height: int = 260) -> go.Figure:
    """Biểu đồ rỗng an toàn khi bộ lọc không có bản ghi hoặc ROLE_SALES bị ẩn dữ liệu vốn."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=12, color="#64748B", family="Inter, sans-serif"),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return apply_stock_sense_layout(fig, height=height)
