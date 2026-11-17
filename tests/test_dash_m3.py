"""
TDD Test Suite cho Module 03 (Parity V2):
Khớp 100% Ảnh 2 — Inline Cashflow Bar trong thẻ PA1-PA4 (bỏ m3-tactic-chart),
Simulator Presets (Khớp giá đối thủ, Cắt lỗ -5% vốn), Thang định vị giá & Sàn vốn,
Radar mất mạng (ERR_CLR_003), nút Áp dụng giá gợi ý và Nhận định chiến lược từ Hệ thống.
"""
import os
import unittest

from src.services.clearance_service import ClearanceService
from src.dash_app.pages.m3_clearance import build_m3_modals, build_m3_panel
from src.dash_app.callbacks.m3_callbacks import (
    render_m3_workspace,
    submit_m3_approve_campaign,
)

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "retail_dienmay.db"))


def _build_m3_services():
    return {"clearance": ClearanceService(DB_PATH)}


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


class TestDashM3Clearance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.services = _build_m3_services()

    def test_m3_landmark_ids_match_image2_and_remove_tactic_chart(self):
        """Kiểm tra Panel M3 khớp Ảnh 2: bỏ m3-tactic-chart, đủ Presets, Price Ruler, Radar nút đồng bộ & Strategic Insight."""
        panel = build_m3_panel(self.services, active=False)
        modals = build_m3_modals()
        ids = _collect_ids(panel) | _collect_ids(modals)
        for req_id in (
            "panel-m3",
            "m3KpiTotalRecovery",
            "m3KpiTotalProfit",
            "m3KpiPaiHero",
            "m3SkuSelectorGrid",
            "m3TacticsContainer",
            "m3SalesLockBanner",
            "m3CapitalProtectionBanner",
            "m3-discount-slider",
            "m3-qty-input",
            "btn-m3-qty-dec",
            "btn-m3-qty-inc",
            "btn-m3-preset-default",
            "btn-m3-preset-match-comp",
            "btn-m3-preset-cut-loss",
            "m3SimBoxRevenue",
            "m3SimBoxCapital",
            "m3SimBoxPromoCost",
            "m3SimBoxNetProfit",
            "btn-m3-toggle-offline",
            "m3Err003Banner",
            "m3CompetitorListContainer",
            "m3PricePositionRuler",
            "m3SuggestedPriceHero",
            "m3SyncRadarPriceBtn",
            "btn-m3-open-price-tag",
            "m3StrategicInsightBox",
            "m3SaleTagModal",
            "m3CampaignModal",
            "btn-m3-approve-pos",
        ):
            self.assertIn(req_id, ids, f"Thiếu ID '{req_id}' trong Module 3 Dash V2")

        self.assertNotIn("m3-tactic-chart", ids, "Phải bỏ biểu đồ m3-tactic-chart riêng vì đã tích hợp vào từng phương án PA1-PA4")

        txt = _collect_text(panel)
        for label in (
            "1. CHỌN KỊCH BẢN KHUYẾN MẠI XẢ HÀNG",
            "2. RADAR GIÁ THỊ TRƯỜNG",
            "Thang định vị giá & Sàn vốn",
            "GIÁ XẢ GỢI Ý TỐI ƯU",
            "Nhận định chiến lược từ Hệ thống",
            "Mặc định",
            "Khớp giá đối thủ",
            "Cắt lỗ (-5% vốn)",
        ):
            self.assertIn(label, txt, f"Thiếu nhãn giao diện Ảnh 2 '{label}'")

        self.assertNotIn("Mã SKU", txt)

    def test_m3_inline_bars_presets_radar_offline_and_rbac_masking(self):
        """Kiểm tra thanh dòng tiền inline trong PA1-PA4, mô phỏng cắt lỗ -5%, giả lập mất mạng và bảo mật ROLE_SALES."""
        ws_ok = render_m3_workspace(self.services, sku="TV-LG-55C3", tactic_code="PA2", target_qty=10, extra_disc=0.0, role="ROLE_OWNER")
        tactics_html = str(ws_ok["tactic_cards"])
        self.assertIn("Vốn thu hồi", str(ws_ok.get("legend_label", "Vốn thu hồi")))
        self.assertIn("bg-emerald-500", tactics_html, "Mỗi thẻ PA1-PA4 phải nhúng trực tiếp thanh Lãi gộp ròng")
        self.assertIn("bg-slate-800", tactics_html, "Mỗi thẻ PA1-PA4 phải nhúng trực tiếp thanh Vốn thu hồi")
        self.assertIn("225,00 tr", str(ws_ok["sim_capital"]))
        self.assertIn("Nhận định chiến lược", str(ws_ok["strategic_insight"]))
        self.assertEqual(ws_ok["cap_protect_style"]["display"], "none")
        self.assertEqual(ws_ok["sales_lock_style"]["display"], "none")

        # Mô phỏng cắt lỗ -5% vốn qua price_override hoặc giảm sâu
        ws_loss = render_m3_workspace(
            self.services,
            sku="TV-LG-55C3",
            tactic_code="PA1",
            target_qty=10,
            extra_disc=25.0,
            role="ROLE_OWNER",
        )
        self.assertEqual(ws_loss["cap_protect_style"]["display"], "flex")

        # Chế độ giả lập mất mạng ERR_CLR_003
        ws_offline = render_m3_workspace(self.services, sku="TV-LG-55C3", offline_mode=True, role="ROLE_OWNER")
        self.assertEqual(ws_offline["err003_style"]["display"], "flex")
        self.assertIn("Dữ liệu tham chiếu nội bộ", str(ws_offline["competitor_rows"]))

        # Bảo mật ROLE_SALES
        ws_sales = render_m3_workspace(self.services, sku="TV-LG-55C3", tactic_code="PA2", target_qty=10, extra_disc=0.0, role="ROLE_SALES")
        self.assertEqual(ws_sales["kpi_recovery"], "****** đ")
        self.assertEqual(ws_sales["sim_capital"], "****** đ")
        self.assertEqual(ws_sales["sales_lock_style"]["display"], "flex")

    def test_m3_approve_campaign_blocks_sales_and_saves_owner(self):
        """Kiểm tra chặn ROLE_SALES duyệt bán dưới giá vốn (ERR_CLR_001) và lưu chiến dịch cho ROLE_OWNER."""
        bad = submit_m3_approve_campaign("TV-LG-55C3", "PA1", 10, 21_000_000, self.services, role="ROLE_SALES")
        self.assertFalse(bad["success"])
        self.assertEqual(bad["error_code"], "ERR_CLR_001")

        conn = self.services["clearance"]._get_connection()
        orig_price = conn.execute("SELECT sale_price FROM DIM_PRODUCTS WHERE product_code='TV-LG-55C3';").fetchone()[0]
        conn.close()
        cid = None
        try:
            ok = submit_m3_approve_campaign("TV-LG-55C3", "PA2", 10, 26_990_000, self.services, role="ROLE_OWNER")
            self.assertTrue(ok["success"])
            cid = ok["campaign_id"]
        finally:
            cleanup = self.services["clearance"]._get_connection()
            if cid is not None:
                cleanup.execute("DELETE FROM FACT_CLEARANCE_CAMPAIGNS WHERE campaign_id = ?;", (cid,))
            cleanup.execute("UPDATE DIM_PRODUCTS SET sale_price = ? WHERE product_code='TV-LG-55C3';", (orig_price,))
            cleanup.commit()
            cleanup.close()


if __name__ == "__main__":
    unittest.main()
