"""
Lớp dịch vụ xử lý nghiệp vụ Phân hệ 06: Hiệu quả kinh doanh & Thác nước lợi nhuận (US-6.1).
Bao gồm tính Vốn gốc thu hồi, Động cơ Attach-Rate (ERR_PRF_002), Thác nước lợi nhuận (ERR_PRF_003) và Hoa hồng bán kèm.
"""
import io
from typing import Any, Dict, List
import pandas as pd

from src.services.base_service import BaseService


class PerformanceService(BaseService):
    """Business Performance & Capital Recovery service implementing SRS_06 (FR-PRF-01..05)."""

    def get_profit_waterfall_data(self, role: str = "ROLE_OWNER") -> Dict[str, Any]:
        """
        FR-PRF-03 & ERR_PRF_003: Phân rã Lợi nhuận gộp dạng Thác nước dựa trên cost_price lịch sử tại hóa đơn.
        """
        conn = self._get_connection()
        line_rows = conn.execute(
            """
            SELECT
                p.product_type, p.category_path,
                l.quantity, l.cost_price, l.line_total
            FROM FACT_INVOICES_LINES l
            JOIN DIM_PRODUCTS p ON l.product_code = p.product_code;
            """
        ).fetchall()
        disc_row = conn.execute(
            "SELECT COALESCE(SUM(invoice_discount_amount), 0) AS total_disc FROM FACT_INVOICES;"
        ).fetchone()
        conn.close()

        core_rev = acc_rev = srv_rev = 0.0
        core_profit = acc_profit = srv_profit = 0.0

        for r in line_rows:
            grp = self.classify_product_group(r["product_type"], r["category_path"])
            rev = float(r["line_total"])
            cost = float(r["quantity"]) * float(r["cost_price"])
            prof = rev - cost
            if grp in self.CORE_CATEGORIES:
                core_rev += rev
                core_profit += prof
            elif grp == "Phụ kiện":
                acc_rev += rev
                acc_profit += prof
            elif grp == "Dịch vụ":
                srv_rev += rev
                srv_profit += prof

        promo_discount = float(disc_row["total_disc"] or 0.0)
        net_gross_profit = core_profit + acc_profit + srv_profit - promo_discount
        attached_profit = acc_profit + srv_profit
        attached_share_pct = round((attached_profit / (core_profit + attached_profit)) * 100, 1) if (core_profit + attached_profit) > 0 else 0.0

        if role == "ROLE_SALES":
            return {
                "core_revenue": round(core_rev, 0),
                "accessory_revenue": round(acc_rev, 0),
                "service_revenue": round(srv_rev, 0),
                "core_profit": None,
                "accessory_profit": None,
                "service_profit": None,
                "promo_discount_cost": None,
                "net_gross_profit": None,
                "attached_profit_share_pct": None,
            }

        return {
            "core_revenue": round(core_rev, 0),
            "accessory_revenue": round(acc_rev, 0),
            "service_revenue": round(srv_rev, 0),
            "core_profit": round(core_profit, 0),
            "accessory_profit": round(acc_profit, 0),
            "service_profit": round(srv_profit, 0),
            "promo_discount_cost": round(promo_discount, 0),
            "net_gross_profit": round(net_gross_profit, 0),
            "attached_profit_share_pct": attached_share_pct,
        }

    def get_category_attach_rate_dataframe(self, role: str = "ROLE_OWNER") -> pd.DataFrame:
        """
        FR-PRF-02 & ERR_PRF_002: Tính Attach-Rate % cho 4 ngành hàng chính,
        loại trừ các hóa đơn chỉ mua lẻ phụ kiện khỏi mẫu số N_core.
        """
        conn = self._get_connection()
        rows = conn.execute(
            """
            SELECT
                l.invoice_code, p.product_type, p.category_path,
                l.quantity, l.cost_price, l.line_total
            FROM FACT_INVOICES_LINES l
            JOIN DIM_PRODUCTS p ON l.product_code = p.product_code;
            """
        ).fetchall()
        conn.close()

        invoices: Dict[str, Dict[str, Any]] = {}
        for r in rows:
            inv_code = r["invoice_code"]
            inv = invoices.setdefault(
                inv_code,
                {"core_cats": set(), "core_units": {}, "has_attached": False, "att_rev": 0.0, "att_profit": 0.0},
            )
            grp = self.classify_product_group(r["product_type"], r["category_path"])
            rev = float(r["line_total"])
            prof = rev - (float(r["quantity"]) * float(r["cost_price"]))
            if grp in self.CORE_CATEGORIES:
                inv["core_cats"].add(grp)
                inv["core_units"][grp] = inv["core_units"].get(grp, 0) + int(r["quantity"])
            elif grp in ("Phụ kiện", "Dịch vụ"):
                inv["has_attached"] = True
                inv["att_rev"] += rev
                inv["att_profit"] += prof

        stats: Dict[str, Dict[str, Any]] = {
            cat: {"core_units": 0, "core_orders": 0, "attached_orders": 0, "attached_sales": 0.0, "attached_profit": 0.0}
            for cat in self.CORE_CATEGORIES
        }

        for inv in invoices.values():
            # ERR_PRF_002: Đơn không có máy chính -> không cộng vào N_core
            if not inv["core_cats"]:
                continue
            share_div = len(inv["core_cats"])
            for cat in inv["core_cats"]:
                stats[cat]["core_orders"] += 1
                stats[cat]["core_units"] += inv["core_units"].get(cat, 0)
                if inv["has_attached"]:
                    stats[cat]["attached_orders"] += 1
                    stats[cat]["attached_sales"] += inv["att_rev"] / share_div
                    stats[cat]["attached_profit"] += inv["att_profit"] / share_div

        records: List[Dict[str, Any]] = []
        for cat in self.CORE_CATEGORIES:
            s = stats[cat]
            ar = round((s["attached_orders"] / s["core_orders"]) * 100, 1) if s["core_orders"] > 0 else 0.0
            if ar >= 70.0:
                badge = "🌟 Xuất sắc"
            elif ar >= 60.0:
                badge = "✅ Đạt chuẩn"
            elif ar >= 50.0:
                badge = "⚠️ Cần đẩy"
            else:
                badge = "⛔ Kém"

            records.append(
                {
                    "category": cat,
                    "core_units": s["core_units"],
                    "core_orders": s["core_orders"],
                    "attached_orders": s["attached_orders"],
                    "attach_rate_pct": ar,
                    "attached_sales": round(s["attached_sales"], 0),
                    "attached_profit": round(s["attached_profit"], 0),
                    "rating_badge": badge,
                }
            )

        df = pd.DataFrame(records).sort_values(by="attach_rate_pct", ascending=False).reset_index(drop=True)
        if role == "ROLE_SALES":
            df = df.drop(columns=["attached_profit"])
        return df

    def get_performance_kpis(self, role: str = "ROLE_OWNER") -> Dict[str, Any]:
        """FR-PRF-01: Tổng hợp 4 Thẻ KPI Tài chính & Thu hồi vốn kèm che giấu ROLE_SALES."""
        conn = self._get_connection()
        inv_row = conn.execute(
            """
            SELECT
                COUNT(*) AS invoice_count,
                COALESCE(SUM(amount_due), 0) AS total_revenue
            FROM FACT_INVOICES;
            """
        ).fetchone()
        cap_row = conn.execute(
            "SELECT COALESCE(SUM(quantity * cost_price), 0) AS total_cogs FROM FACT_INVOICES_LINES;"
        ).fetchone()
        conn.close()

        wf = self.get_profit_waterfall_data(role="ROLE_OWNER")
        df_cat = self.get_category_attach_rate_dataframe(role="ROLE_OWNER")

        total_core_orders = int(df_cat["core_orders"].sum())
        total_att_orders = int(df_cat["attached_orders"].sum())
        overall_ar = round((total_att_orders / total_core_orders) * 100, 1) if total_core_orders > 0 else 0.0

        total_rev = float(inv_row["total_revenue"] or 0.0)
        recovered_cap = float(cap_row["total_cogs"] or 0.0)
        net_profit = float(wf["net_gross_profit"])
        att_sales = float(wf["accessory_revenue"]) + float(wf["service_revenue"])
        margin_pct = round((net_profit / total_rev) * 100, 1) if total_rev > 0 else 0.0

        return {
            "invoice_count": int(inv_row["invoice_count"] or 0),
            "total_revenue": round(total_rev, 0),
            "recovered_capital": None if role == "ROLE_SALES" else round(recovered_cap, 0),
            "display_recovered_capital": self.mask_currency(recovered_cap, role),
            "net_gross_profit": None if role == "ROLE_SALES" else round(net_profit, 0),
            "display_net_gross_profit": self.mask_currency(net_profit, role),
            "gross_margin_pct": None if role == "ROLE_SALES" else margin_pct,
            "attached_sales": round(att_sales, 0),
            "overall_attach_rate_pct": overall_ar,
            "attached_profit_share_pct": None if role == "ROLE_SALES" else wf["attached_profit_share_pct"],
        }

    def get_staff_commission_list(self, role: str = "ROLE_OWNER") -> List[Dict[str, Any]]:
        """FR-PRF-04: Truy vấn bảng xếp hạng hiệu suất bán kèm & hoa hồng (15% PK + 20% DV)."""
        conn = self._get_connection()
        rows = conn.execute(
            """
            SELECT
                l.employee_code, e.employee_name, e.title,
                l.period_label, l.accessory_sales, l.accessory_profit,
                l.service_sales, l.service_profit, l.commission_amount, l.status
            FROM FACT_COMMISSION_LEDGER l
            JOIN DIM_EMPLOYEES e ON l.employee_code = e.employee_code
            ORDER BY l.commission_amount DESC;
            """
        ).fetchall()
        conn.close()

        result = []
        for r in rows:
            d = dict(r)
            if role == "ROLE_SALES":
                d["accessory_profit"] = None
                d["service_profit"] = None
            result.append(d)
        return result

    def approve_commission(self, employee_code: str, role: str = "ROLE_OWNER") -> Dict[str, Any]:
        """FR-PRF-04: Phê duyệt chi hoa hồng bán kèm cho nhân sự (chỉ ROLE_OWNER)."""
        if role != "ROLE_OWNER":
            return {
                "success": False,
                "error_code": "ERR_UNAUTHORIZED",
                "error": "Chỉ Chủ cửa hàng (ROLE_OWNER) mới có quyền phê duyệt chi hoa hồng.",
            }
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE FACT_COMMISSION_LEDGER
                SET status = 'APPROVED', approved_at = DATETIME('now', 'localtime'), approved_by = 'NV0001'
                WHERE employee_code = ?;
                """,
                (employee_code,),
            )
            if cur.rowcount == 0:
                return {"success": False, "error_code": "ERR_NOT_FOUND", "error": f"Không tìm thấy sổ hoa hồng cho {employee_code}."}
            conn.commit()
        finally:
            conn.close()

        return {"success": True, "employee_code": employee_code, "message": f"Đã duyệt chi hoa hồng cho nhân sự {employee_code}!"}

    def export_financial_summary_csv(self) -> bytes:
        """FR-PRF-05: Xuất báo cáo tổng hợp Hiệu quả kinh doanh & Attach-Rate định dạng CSV UTF-8 BOM."""
        df_cat = self.get_category_attach_rate_dataframe(role="ROLE_OWNER").rename(
            columns={
                "category": "Nganh_Hang",
                "core_units": "So_May_Ban",
                "core_orders": "Tong_Don_Chinh",
                "attached_orders": "Don_Co_Ban_Kem",
                "attach_rate_pct": "Attach_Rate_Pct",
                "attached_sales": "Doanh_So_PK_DV",
                "attached_profit": "Lai_Gop_PK_DV",
                "rating_badge": "Danh_Gia",
            }
        )
        buf = io.BytesIO()
        buf.write(df_cat.to_csv(index=False).encode("utf-8-sig"))
        return buf.getvalue()
