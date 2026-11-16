"""
Lớp dịch vụ xử lý nghiệp vụ Phân hệ 02: Cần xử lý hôm nay (US-2.1 & US-2.2).
Bao gồm cảnh báo hàng bán chậm/hết mùa, dự báo ngày đứt hàng (DOS), khử báo động giả (In-Transit) và Snooze.
"""
import datetime
import math
from typing import Any, Dict, List, Optional
import pandas as pd

from src.services.base_service import BaseService


class AlertService(BaseService):
    """Actionable Daily Alerts service implementing SRS_02 (FR-ACT-01..07)."""

    DEFAULT_REF_DATE = "2026-11-04"

    def _get_active_snoozed_skus(self, conn, ref_date: str) -> Dict[str, Dict[str, Any]]:
        rows = conn.execute(
            """
            SELECT product_code, snooze_days, snooze_until, reason, created_at
            FROM SYS_ALERT_SNOOZE_LOG
            WHERE is_active = 1 AND DATE(snooze_until) > ?
            ORDER BY snooze_id DESC;
            """,
            (ref_date,),
        ).fetchall()
        result: Dict[str, Dict[str, Any]] = {}
        for r in rows:
            if r["product_code"] not in result:
                result[r["product_code"]] = dict(r)
        return result

    def _get_in_transit_po_map(self, conn) -> Dict[str, str]:
        rows = conn.execute(
            """
            SELECT poi.product_code,
                   GROUP_CONCAT(po.purchase_code || ' (' || poi.quantity || ' máy, về ' || po.expected_delivery_date || ')', '; ') AS po_info
            FROM PO_ITEMS poi
            JOIN PURCHASE_ORDERS po ON poi.purchase_code = po.purchase_code
            WHERE po.status = 'Đang vận chuyển'
            GROUP BY poi.product_code;
            """
        ).fetchall()
        return {r["product_code"]: r["po_info"] for r in rows}

    def get_slow_moving_alerts(
        self,
        risk_filter: str = "Tất cả",
        brand: str = "Tất cả",
        search: str = "",
        role: str = "ROLE_OWNER",
        include_snoozed: bool = False,
        ref_date: str = DEFAULT_REF_DATE,
    ) -> pd.DataFrame:
        """
        FR-ACT-02: Sàng lọc các SKU tồn chết, bán chậm (DSI > 60), vượt trần hoặc sắp hết mùa.
        """
        conn = self._get_connection()
        _, velocity_map = self.load_sales_velocity_map(conn, ref_date)
        snoozed_map = self._get_active_snoozed_skus(conn, ref_date)

        rows = conn.execute(
            """
            SELECT
                product_code, product_name, category_path, brand,
                cost_price, sale_price, stock_on_hand, min_stock, max_stock,
                seasonality, lifecycle_status
            FROM DIM_PRODUCTS
            WHERE is_active = 1 AND has_serial = 1 AND stock_on_hand > 0;
            """
        ).fetchall()
        conn.close()

        records: List[Dict[str, Any]] = []
        for r in rows:
            p_code = r["product_code"]
            if not include_snoozed and p_code in snoozed_map:
                continue

            vel = velocity_map.get(p_code, {})
            rr_30 = vel.get("rr_30", 0.0)
            days_no_sale = int(vel.get("days_since_last_sale", 120))
            soh = int(r["stock_on_hand"])
            dsi = round(soh / rr_30, 1) if rr_30 > 0 else 999.0

            risk_group = None
            risk_badge = None
            if r["lifecycle_status"] == "EOL":
                risk_group = "Hãng EOL"
                risk_badge = "🟡 Hãng EOL"
            elif r["seasonality"] == "SUMMER" and (soh > r["max_stock"] or days_no_sale >= 35):
                risk_group = "Sắp hết mùa"
                risk_badge = "🟠 Sắp hết mùa hè"
            elif soh > r["max_stock"]:
                risk_group = "Tồn chết / Vượt trần"
                risk_badge = "🔴 Tồn đọng vượt trần"
            elif dsi > 60 or days_no_sale >= 45:
                risk_group = "Tồn chết / Vượt trần"
                risk_badge = "🔴 Tồn chết (>60d)"

            if not risk_group:
                continue

            stagnant_capital = round(soh * float(r["cost_price"]), 0)
            suggested_clear = soh if risk_group in ("Hãng EOL", "Sắp hết mùa") and soh <= r["max_stock"] else max(0, soh - int(r["max_stock"]))
            if suggested_clear == 0:
                suggested_clear = max(1, soh // 2)

            records.append(
                {
                    "product_code": p_code,
                    "product_name": r["product_name"],
                    "category_path": r["category_path"],
                    "brand": r["brand"],
                    "soh": soh,
                    "max_stock": int(r["max_stock"]),
                    "cost_price": float(r["cost_price"]),
                    "sale_price": float(r["sale_price"]),
                    "stagnant_capital": stagnant_capital,
                    "days_since_last_sale": days_no_sale,
                    "rr_30": round(rr_30, 3),
                    "dsi_days": dsi,
                    "risk_group": risk_group,
                    "risk_badge": risk_badge,
                    "suggested_clearance_qty": suggested_clear,
                    "is_snoozed": p_code in snoozed_map,
                }
            )

        df = pd.DataFrame(records)
        if df.empty:
            cols = [
                "product_code", "product_name", "category_path", "brand", "soh", "max_stock",
                "sale_price", "days_since_last_sale", "rr_30", "dsi_days",
                "risk_group", "risk_badge", "suggested_clearance_qty", "is_snoozed",
            ]
            if role != "ROLE_SALES":
                cols.extend(["cost_price", "stagnant_capital"])
            return pd.DataFrame(columns=cols)

        df = df.sort_values(by=["stagnant_capital", "dsi_days"], ascending=[False, False]).reset_index(drop=True)

        if risk_filter != "Tất cả":
            df = df[df["risk_group"] == risk_filter]
        if brand != "Tất cả":
            df = df[df["brand"] == brand]
        if search:
            kw = search.lower()
            df = df[
                df["product_code"].str.lower().str.contains(kw)
                | df["product_name"].str.lower().str.contains(kw)
            ]

        if role == "ROLE_SALES":
            df = df.drop(columns=["cost_price", "stagnant_capital"])

        return df.reset_index(drop=True)

    def get_stockout_alerts(
        self,
        severity_filter: str = "Tất cả",
        search: str = "",
        ref_date: str = DEFAULT_REF_DATE,
    ) -> pd.DataFrame:
        """
        FR-ACT-05, FR-ACT-06, FR-ACT-07: Dự báo DOS, khử báo động giả qua INC và tính PO Draft Qty.
        """
        conn = self._get_connection()
        _, velocity_map = self.load_sales_velocity_map(conn, ref_date)
        po_map = self._get_in_transit_po_map(conn)

        rows = conn.execute(
            """
            SELECT
                v.product_code, v.product_name, v.category_path, v.brand,
                v.sale_price, v.soh, v.res, v.avl, v.inc, v.projected_stock,
                v.min_stock, p.lead_time_days
            FROM VW_INVENTORY_FLOW_OVERVIEW v
            JOIN DIM_PRODUCTS p ON v.product_code = p.product_code
            WHERE v.has_serial = 1 AND p.is_active = 1;
            """
        ).fetchall()
        conn.close()

        records: List[Dict[str, Any]] = []
        for r in rows:
            p_code = r["product_code"]
            avl = int(r["avl"])
            inc = int(r["inc"])
            lt = int(r["lead_time_days"])
            min_stock = int(r["min_stock"])

            vel = velocity_map.get(p_code, {})
            rr_7 = vel.get("rr_7", 0.0)
            # Nếu sản phẩm cháy hàng sớm trong quá khứ (RR_7=0), dùng tốc độ bán lịch sử làm chuẩn tốc độ cầu
            effective_rr = rr_7 if rr_7 > 0 else (vel.get("total_hist", 0.0) / 85.0)
            if effective_rr <= 0 and avl <= 0:
                effective_rr = 0.1

            dos = 0.0 if avl <= 0 else (round(avl / effective_rr, 1) if effective_rr > 0 else 999.0)

            severity = None
            alert_badge = None
            if (avl <= 0 or dos <= lt + 3 or avl <= min_stock) and inc > 0:
                severity = "Đang trên đường về"
                alert_badge = f"🔵 Đang trên đường về ({po_map.get(p_code, f'INC={inc}')})"
            elif avl <= 0:
                severity = "Đã hết hàng (OOS)"
                alert_badge = "⛔ Đã hết sạch hàng (OOS)"
            elif dos <= lt:
                severity = "Nguy cơ đứt hàng tức thì"
                alert_badge = "🔴 Nguy cơ đứt hàng tức thì"
            elif dos <= lt + 3 or avl <= min_stock:
                severity = "Cần lên kế hoạch nhập"
                alert_badge = "🟡 Cần lên kế hoạch nhập"

            if not severity:
                continue

            # FR-ACT-06: Không cộng doanh thu mất tiềm năng nếu đã có đơn hàng đang vận chuyển về (INC > 0)
            daily_lost_rev = 0.0 if inc > 0 else round(effective_rr * float(r["sale_price"]), 0)
            po_draft_qty = max(0, math.ceil((effective_rr * (lt + 14)) - avl - inc))
            if avl <= min_stock and inc == 0 and po_draft_qty == 0:
                po_draft_qty = max(1, min_stock * 2 - avl)

            records.append(
                {
                    "product_code": p_code,
                    "product_name": r["product_name"],
                    "brand": r["brand"],
                    "avl": avl,
                    "inc": inc,
                    "min_stock": min_stock,
                    "lead_time_days": lt,
                    "rr_7": round(effective_rr, 2),
                    "dos_days": dos,
                    "severity": severity,
                    "alert_badge": alert_badge,
                    "po_info": po_map.get(p_code, "Chưa có PO"),
                    "daily_lost_revenue": daily_lost_rev,
                    "po_draft_qty": po_draft_qty,
                }
            )

        df = pd.DataFrame(records)
        if df.empty:
            return pd.DataFrame(
                columns=[
                    "product_code", "product_name", "brand", "avl", "inc", "min_stock",
                    "lead_time_days", "rr_7", "dos_days", "severity", "alert_badge",
                    "po_info", "daily_lost_revenue", "po_draft_qty",
                ]
            )

        severity_order = {
            "Đã hết hàng (OOS)": 0,
            "Nguy cơ đứt hàng tức thì": 1,
            "Cần lên kế hoạch nhập": 2,
            "Đang trên đường về": 3,
        }
        df["_rank"] = df["severity"].map(severity_order).fillna(9)
        df = df.sort_values(by=["_rank", "dos_days"]).drop(columns=["_rank"]).reset_index(drop=True)

        if severity_filter != "Tất cả":
            df = df[df["severity"] == severity_filter]
        if search:
            kw = search.lower()
            df = df[
                df["product_code"].str.lower().str.contains(kw)
                | df["product_name"].str.lower().str.contains(kw)
            ]

        return df.reset_index(drop=True)

    def get_alert_kpis(
        self, role: str = "ROLE_OWNER", ref_date: str = DEFAULT_REF_DATE
    ) -> Dict[str, Any]:
        """FR-ACT-01: Kết xuất 4 chỉ số tác chiến đầu ngày kèm che giấu Vốn kẹt theo Role."""
        df_slow = self.get_slow_moving_alerts(role="ROLE_OWNER", include_snoozed=False, ref_date=ref_date)
        df_stockout = self.get_stockout_alerts(ref_date=ref_date)

        stagnant_cap = float(df_slow["stagnant_capital"].sum()) if not df_slow.empty else 0.0
        dead_or_over = int(len(df_slow[df_slow["risk_group"] == "Tồn chết / Vượt trần"])) if not df_slow.empty else 0
        seasonal = int(len(df_slow[df_slow["risk_group"] == "Sắp hết mùa"])) if not df_slow.empty else 0

        urgent_stockouts = df_stockout[df_stockout["inc"] == 0] if not df_stockout.empty else df_stockout
        stockout_skus = int(len(urgent_stockouts))
        in_transit_skus = int(len(df_stockout[df_stockout["inc"] > 0])) if not df_stockout.empty else 0
        daily_lost_rev = float(urgent_stockouts["daily_lost_revenue"].sum()) if not urgent_stockouts.empty else 0.0

        return {
            "stagnant_capital": None if role == "ROLE_SALES" else stagnant_cap,
            "display_stagnant_capital": self.mask_currency(stagnant_cap, role),
            "dead_or_overstock_skus": dead_or_over,
            "seasonal_risk_skus": seasonal,
            "total_slow_skus": int(len(df_slow)),
            "stockout_risk_skus": stockout_skus,
            "in_transit_skus": in_transit_skus,
            "daily_lost_revenue": daily_lost_rev,
        }

    def snooze_alert(
        self,
        product_code: str,
        snooze_days: int,
        reason: str,
        role: str = "ROLE_OWNER",
        ref_date: str = DEFAULT_REF_DATE,
    ) -> Dict[str, Any]:
        """FR-ACT-04 & ERR_ACT_003: Tạm hoãn cảnh báo 7/14/30 ngày và ghi nhật ký DB."""
        if role not in ("ROLE_OWNER", "ROLE_WH_MGR"):
            return {
                "success": False,
                "error_code": "ERR_UNAUTHORIZED",
                "error": "Nhân viên bán hàng không có quyền tạm hoãn cảnh báo kho.",
            }
        clean_reason = (reason or "").strip()
        if len(clean_reason) < 10:
            return {
                "success": False,
                "error_code": "ERR_ACT_003",
                "error": "Vui lòng nhập lý do tạm hoãn tối thiểu 10 ký tự.",
            }
        if snooze_days not in (7, 14, 30):
            return {
                "success": False,
                "error_code": "ERR_INVALID_DAYS",
                "error": "Thời hạn tạm hoãn chỉ hỗ trợ 7, 14 hoặc 30 ngày.",
            }

        snooze_until = (datetime.date.fromisoformat(ref_date) + datetime.timedelta(days=snooze_days)).isoformat()
        conn = self._get_connection()
        try:
            exists = conn.execute("SELECT 1 FROM DIM_PRODUCTS WHERE product_code = ?;", (product_code,)).fetchone()
            if not exists:
                return {"success": False, "error_code": "ERR_NOT_FOUND", "error": f"Không tìm thấy SKU {product_code}"}
            conn.execute("UPDATE SYS_ALERT_SNOOZE_LOG SET is_active = 0 WHERE product_code = ?;", (product_code,))
            conn.execute(
                """
                INSERT INTO SYS_ALERT_SNOOZE_LOG (product_code, snooze_days, snooze_until, reason, created_by, is_active)
                VALUES (?, ?, ?, ?, 'NV0001', 1);
                """,
                (product_code, snooze_days, snooze_until, clean_reason),
            )
            conn.commit()
        finally:
            conn.close()

        return {
            "success": True,
            "product_code": product_code,
            "snooze_until": snooze_until,
            "message": f"Đã tạm hoãn cảnh báo {product_code} đến ngày {snooze_until}.",
        }
