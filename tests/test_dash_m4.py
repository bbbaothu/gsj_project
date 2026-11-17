"""
TDD Kiểm thử Phân hệ 04 trên Plotly Dash: Gợi ý nhập hàng, Cân đối ngân sách & Gom đơn PO.
"""
import sqlite3
import unittest
from pathlib import Path
from dash import html

from src.services.replenishment_service import ReplenishmentService

DB_PATH = str(Path(__file__).resolve().parent.parent / "data" / "retail_dienmay.db")


def _collect_ids(component, found=None):
    if found is None:
        found = set()
    if hasattr(component, "id") and component.id is not None:
        if isinstance(component.id, str):
            found.add(component.id)
    children = getattr(component, "children", None)
    if isinstance(children, (list, tuple)):
        for c in children:
            _collect_ids(c, found)
    elif children is not None and hasattr(children, "to_plotly_json"):
        _collect_ids(children, found)
    return found


def _collect_text(component, chunks=None):
    if chunks is None:
        chunks = []
    if isinstance(component, str):
        chunks.append(component)
        return chunks
    children = getattr(component, "children", None)
    if isinstance(children, (list, tuple)):
        for c in children:
            _collect_text(c, chunks)
    elif children is not None:
        _collect_text(children, chunks)
    return chunks


class TestDashM4Replenishment(unittest.TestCase):
    """Kiểm tra bố cục, cân đối ngân sách, gom PO theo hãng và RBAC cho Module 04."""

    def test_m4_landmark_ids_match_prototype(self):
        """Kiểm tra Panel M4, Drawers và Modals (PO Preview, Approve, Lifecycle) đủ ID chuẩn Prototype."""
        from src.dash_app.pages.m4_replenishment import build_m4_panel

        panel = build_m4_panel(is_active=True)
        ids = _collect_ids(panel)
        for req_id in [
            "panel-m4",
            "m4HeaderOrderBadge",
            "m4Cycle14Btn",
            "m4Cycle30Btn",
            "m4HeaderBudgetText",
            "m4AutoBalanceBtn",
            "m4KpiSkuCount",
            "m4KpiTotalUnits",
            "m4KpiTotalCost",
            "m4KpiBudgetBar",
            "m4ReplenishTableBody",
            "m4SupplierCardsContainer",
            "m4SupplierDrawer",
            "m4ApproveModal",
            "m4PoLifecycleModal",
            "poPreviewModal",
        ]:
            self.assertIn(req_id, ids, f"Thiếu landmark ID M4: {req_id}")

    def test_m4_cycle_switch_budget_balance_and_rbac_masking(self):
        """Kiểm tra chuyển chu kỳ 14d->30d, cân đối ngân sách <= B_cap, chỉnh SL & RBAC ROLE_SALES."""
        from src.dash_app.callbacks.m4_callbacks import (
            render_m4_workspace,
            compute_m4_items_state,
        )

        svc = ReplenishmentService(DB_PATH)
        state_14 = compute_m4_items_state(svc, cycle_days=14, budget_cap=200_000_000.0, role="ROLE_OWNER")
        state_30 = compute_m4_items_state(svc, cycle_days=30, budget_cap=200_000_000.0, role="ROLE_OWNER")
        self.assertGreaterEqual(state_30["total_units"], state_14["total_units"])
        self.assertGreater(len(state_14["items"]), 0)

        # Kiểm tra tự động cân đối ngân sách đưa tổng tiền <= 80 triệu
        tight_cap = 80_000_000.0
        balanced = compute_m4_items_state(
            svc,
            cycle_days=14,
            budget_cap=tight_cap,
            auto_balance=True,
            role="ROLE_OWNER",
        )
        self.assertLessEqual(balanced["total_cost"], tight_cap)

        # Kiểm tra chỉnh số lượng 1 SKU bằng qty_overrides cập nhật tổng đơn & modal preview
        first_code = state_14["items"][0]["product_code"]
        custom = render_m4_workspace(
            svc,
            cycle_days=14,
            budget_cap=250_000_000.0,
            qty_overrides={first_code: 9},
            role="ROLE_OWNER",
        )
        text_owner = " ".join(_collect_text(html.Div(custom["approve_modal_body"])))
        self.assertIn("PO", text_owner)

        # Kiểm tra RBAC ROLE_SALES ẩn toàn bộ giá vốn / thành tiền
        sales_view = render_m4_workspace(
            svc,
            cycle_days=14,
            budget_cap=250_000_000.0,
            role="ROLE_SALES",
        )
        sales_text = " ".join(_collect_text(html.Div(sales_view["kpi_total_cost"])))
        self.assertIn("******", sales_text)
        self.assertTrue(sales_view["approve_disabled"])

    def test_m4_create_po_rbac_and_csv_export(self):
        """Kiểm tra chặn ROLE_SALES tạo PO, xuất CSV UTF-8 BOM và ghi/rollback PO_ITEMS cho ROLE_OWNER."""
        from src.dash_app.callbacks.m4_callbacks import (
            compute_m4_items_state,
            submit_m4_purchase_orders,
            generate_m4_po_csv,
        )

        svc = ReplenishmentService(DB_PATH)
        state = compute_m4_items_state(svc, cycle_days=14, budget_cap=250_000_000.0, role="ROLE_OWNER")
        items = state["items"]

        # Export CSV
        csv_bytes = generate_m4_po_csv(svc, items)
        csv_str = csv_bytes.decode("utf-8-sig")
        self.assertIn("Ma_SKU", csv_str)
        self.assertIn("Nha_Cung_Cap", csv_str)

        # ROLE_SALES bi chan
        res_sales = submit_m4_purchase_orders(svc, items, role="ROLE_SALES")
        self.assertFalse(res_sales["success"])
        self.assertEqual(res_sales["error_code"], "ERR_UNAUTHORIZED")

        # ROLE_OWNER tao PO va don sach DB
        res_owner = submit_m4_purchase_orders(svc, items, role="ROLE_OWNER")
        self.assertTrue(res_owner["success"])
        created_codes = res_owner["created_po_codes"]
        self.assertGreater(len(created_codes), 0)

        conn = sqlite3.connect(DB_PATH)
        try:
            for code in created_codes:
                row = conn.execute(
                    "SELECT purchase_code FROM PURCHASE_ORDERS WHERE purchase_code = ?",
                    (code,),
                ).fetchone()
                self.assertIsNotNone(row)
                conn.execute("DELETE FROM PO_ITEMS WHERE purchase_code = ?", (code,))
                conn.execute("DELETE FROM PURCHASE_ORDERS WHERE purchase_code = ?", (code,))
            conn.commit()
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
