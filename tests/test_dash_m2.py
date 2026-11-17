"""
TDD Test Suite cho Module 02 (Parity V2): Pie Chart Vốn kẹt dải Vàng-Cam-Đỏ-Nâu đỏ,
Bỏ Runway Chart, Bảng 7 cột thuần Việt chuẩn Ảnh 1 với trượt ngang trong ô (.cell-hscroll).
"""
import os
import unittest

from src.services.alert_service import AlertService
from src.dash_app.pages.m2_alerts import build_m2_modals_and_drawer, build_m2_panel
from src.dash_app.callbacks.m2_callbacks import (
    build_m2_drawer_body,
    render_m2_workspace,
    submit_m2_snooze,
)

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "retail_dienmay.db"))


def _build_m2_services():
    return {"alert": AlertService(DB_PATH)}


def _collect_ids(component) -> set:
    ids = set()
    if component is None:
        return ids
    if hasattr(component, "id") and getattr(component, "id", None) is not None:
        ids.add(str(component.id))
    children = getattr(component, "children", None)
    if isinstance(children, (list, tuple)):
        for c in children:
            ids.update(_collect_ids(c))
    elif children is not None and not isinstance(children, (str, int, float, bool)):
        ids.update(_collect_ids(children))
    return ids


def _collect_text(component) -> str:
    if component is None:
        return ""
    if isinstance(component, (str, int, float, bool)):
        return str(component)
    children = getattr(component, "children", None)
    if isinstance(children, (list, tuple)):
        return " ".join(_collect_text(c) for c in children)
    return _collect_text(children)


class TestDashM2Alerts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.services = _build_m2_services()

    def test_m2_landmark_ids_and_removed_runway_chart(self):
        """Kiểm tra Panel M2 đủ ID chuẩn Ảnh 1, đã loại bỏ m2-runway-chart và sạch viết tắt Anh ngữ."""
        panel = build_m2_panel(self.services, active=False)
        overlays = build_m2_modals_and_drawer()
        ids = _collect_ids(panel) | _collect_ids(overlays)
        for req_id in (
            "panel-m2",
            "m2-kpi-stagnant",
            "m2-kpi-dead",
            "m2-kpi-seasonal",
            "m2-kpi-stockout",
            "m2-pill-all",
            "m2-pill-stagnant",
            "m2-pill-dead",
            "m2-pill-seasonal",
            "m2-pill-stockout",
            "m2-pill-incoming",
            "m2-search-input",
            "m2BrandSelect",
            "m2CategorySelect",
            "m2SortSelect",
            "m2-alerts-table-body",
            "m2-capital-chart",
            "btn-m2-pareto-filter",
            "m2DecisionDrawer",
            "snoozeModal",
            "m2ThresholdModal",
            "m2-download-csv",
        ):
            self.assertIn(req_id, ids, f"Thiếu ID '{req_id}' trong Module 2 Dash")

        self.assertNotIn("m2-runway-chart", ids, "Phải loại bỏ biểu đồ Đường băng tồn kho (m2-runway-chart)")

        txt = _collect_text(panel)
        for col_header in (
            "SẢN PHẨM & VỊ TRÍ KỆ",
            "TỒN THỰC / ĐỊNH MỨC",
            "ĐƯỜNG BĂNG & TỐC ĐỘ BÁN",
            "VỐN ĐỌNG / RỦI RO",
            "NGUYÊN NHÂN CỐT LÕI",
            "HÀNH ĐỘNG QUYẾT ĐỊNH",
        ):
            self.assertIn(col_header, txt)

        for banned in ("MÃ SKU", "DSI", "DOS", "INC", "SOH:", "AVL:", "trống PO"):
            self.assertNotIn(banned, txt, f"Không để thuật ngữ viết tắt '{banned}' trên UI M2")

    def test_m2_capital_pie_chart_urgent_palette_and_hover(self):
        """Kiểm tra biểu đồ Phân bổ vốn kẹt là Pie chart dải màu Vàng-Cam-Đỏ-Nâu đỏ & Tooltip 4 thông tin."""
        res_owner = render_m2_workspace(self.services, filter_key="all", role="ROLE_OWNER")
        fig = res_owner["capital_fig"]
        self.assertEqual(fig.data[0].type, "pie")

        urgent_colors = {"#7F1D1D", "#B91C1C", "#DC2626", "#EA580C", "#D97706", "#F59E0B"}
        slice_colors = set(fig.data[0].marker.colors or [])
        self.assertTrue(slice_colors, "Pie chart phải thiết lập dải màu rõ ràng")
        self.assertTrue(slice_colors.issubset(urgent_colors), f"Màu lát cắt {slice_colors} phải nằm trong dải Vàng-Cam-Đỏ-Nâu đỏ")

        cd = fig.data[0].customdata
        self.assertIsNotNone(cd)
        self.assertEqual(len(cd[0]), 4, "Hover customdata Pie chart phải gồm 4 trường (Tên, Mã SP, Vốn kẹt, Tồn)")
        hover_tpl = fig.data[0].hovertemplate or ""
        self.assertIn("customdata[0]", hover_tpl)
        self.assertIn("customdata[1]", hover_tpl)
        self.assertIn("customdata[2]", hover_tpl)
        self.assertIn("customdata[3]", hover_tpl)

        res_sales = render_m2_workspace(self.services, filter_key="all", role="ROLE_SALES")
        self.assertEqual(len(res_sales["capital_fig"].data), 0, "ROLE_SALES không được thấy số liệu vốn kẹt trong Pie chart")

    def test_m2_workspace_hscroll_cells_brand_sort_and_rbac_masking(self):
        """Kiểm tra lớp trượt ngang .cell-hscroll, bộ lọc Hãng/Ngành/Hàng đang về và bảo mật ROLE_SALES."""
        res_owner = render_m2_workspace(self.services, filter_key="all", role="ROLE_OWNER")
        rows_str = str(res_owner["table_rows"])
        self.assertIn("cell-hscroll", rows_str, "Các ô dài trong bảng M2 phải dùng .cell-hscroll để trượt ngang")
        self.assertIn("TV-LG-55C3", rows_str)
        self.assertIn("ML-DK-FTKB25", rows_str)

        res_sales = render_m2_workspace(self.services, filter_key="all", role="ROLE_SALES")
        self.assertIn("****** đ", str(res_sales["kpi_cards"]))
        self.assertIn("****** đ", str(res_sales["table_rows"]))

        res_incoming = render_m2_workspace(self.services, filter_key="incoming", role="ROLE_OWNER")
        inc_str = str(res_incoming["table_rows"])
        self.assertIn("đang về", inc_str.lower())
        self.assertNotIn("TV-LG-55C3", inc_str)

        res_brand = render_m2_workspace(self.services, filter_key="all", brand_filter="LG", role="ROLE_OWNER")
        self.assertIn("TV-LG-55C3", str(res_brand["table_rows"]))
        self.assertNotIn("ML-DK-FTKB25", str(res_brand["table_rows"]))

    def test_m2_drawer_and_snooze_modal_validation_and_persistence(self):
        """Kiểm tra Decision Drawer thuần Việt và validation ERR_ACT_003 khi bấm Tạm hoãn trong Modal."""
        drawer = build_m2_drawer_body("TV-LG-55C3", self.services, role="ROLE_OWNER")
        self.assertEqual(drawer["sku"], "TV-LG-55C3")
        self.assertEqual(drawer["target_module"], "m3")
        self.assertNotIn("SOH", drawer["meta"])
        self.assertNotIn("DSI", str(drawer["body"]))

        bad = submit_m2_snooze("TV-LG-55C3", 14, "ngan", self.services, role="ROLE_OWNER")
        self.assertFalse(bad["success"])
        self.assertEqual(bad["error_code"], "ERR_ACT_003")

        try:
            ok = submit_m2_snooze("TV-LG-55C3", 14, "Giữ máy trưng bày chương trình cuối tháng", self.services, role="ROLE_OWNER")
            self.assertTrue(ok["success"])
        finally:
            conn = self.services["alert"]._get_connection()
            conn.execute("DELETE FROM SYS_ALERT_SNOOZE_LOG WHERE product_code = 'TV-LG-55C3';")
            conn.commit()
            conn.close()


if __name__ == "__main__":
    unittest.main()
