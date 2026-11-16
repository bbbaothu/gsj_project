"""
Lớp dịch vụ xử lý nghiệp vụ Phân hệ 04: Gợi ý nhập hàng & Tự động tạo đơn PO (US-4.1).
"""
import datetime
import io
import math
from typing import Any, Dict, List
import pandas as pd

from src.services.base_service import BaseService


class ReplenishmentService(BaseService):
    """Smart Replenishment & PO Auto-Grouping service implementing SRS_04 (FR-REP-01..06)."""

    DEFAULT_REF_DATE = "2026-11-04"

    VENDOR_MAP = {
        "Casper": ("NCC_CASPER", "Công ty Cổ phần Casper Việt Nam"),
        "Daikin": ("NCC_DAIKIN", "Công ty Cổ phần Daikin Air Conditioning Vietnam"),
        "Aqua": ("NCC_AQUA", "Công ty TNHH Điện Máy Aqua Việt Nam"),
        "Toshiba": ("NCC_TOSHIBA", "Toshiba Consumer Products Vietnam"),
        "Sony": ("NCC_SONY", "Công ty TNHH Sony Electronics Việt Nam"),
        "Panasonic": ("NCC_PANA", "Công ty TNHH Panasonic Việt Nam"),
        "LG": ("NCC_LG", "Công ty TNHH LG Electronics Việt Nam"),
        "Samsung": ("NCC_SAMSUNG", "Công ty TNHH Điện tử Samsung Vina"),
    }

    @staticmethod
    def apply_moq_and_pack_rounding(raw_qty: float, moq: int = 1, pack_size: int = 1) -> int:
        """FR-REP-05: Làm tròn số lượng đề xuất lên theo MOQ và quy cách đóng thùng (pack_size)."""
        if raw_qty <= 0:
            return 0
        qty = max(math.ceil(raw_qty), max(1, int(moq)))
        p_size = max(1, int(pack_size))
        if p_size > 1:
            qty = math.ceil(qty / p_size) * p_size
        return int(qty)

    @staticmethod
    def _seasonality_factor(seasonality: str, ref_date: str) -> float:
        month = int(ref_date.split("-")[1])
        if seasonality == "SUMMER":
            if 5 <= month <= 7:
                return 1.30
            if month >= 8 or month <= 2:
                return 0.60
            return 1.15
        if seasonality == "WINTER":
            return 1.25 if (month >= 11 or month <= 2) else 0.70
        return 1.00

    def get_replenishment_recommendations(
        self,
        cycle_days: int = 14,
        budget_cap: float = 200_000_000.0,
        vendor_filter: str = "Tất cả",
        role: str = "ROLE_OWNER",
        ref_date: str = DEFAULT_REF_DATE,
    ) -> Dict[str, Any]:
        """
        FR-REP-01..05: Dự báo nhu cầu thích ứng (RR14/RR30, S_factor), Safety Stock, Confidence Score và Trần ngân sách.
        """
        conn = self._get_connection()
        _, velocity_map = self.load_sales_velocity_map(conn, ref_date)

        rows = conn.execute(
            """
            SELECT
                v.product_code, v.product_name, v.brand, v.category_path,
                v.cost_price, v.sale_price, v.soh, v.res, v.avl, v.inc,
                p.min_stock, p.max_stock, p.lead_time_days, p.moq, p.pack_size, p.seasonality
            FROM VW_INVENTORY_FLOW_OVERVIEW v
            JOIN DIM_PRODUCTS p ON v.product_code = p.product_code
            WHERE v.has_serial = 1 AND p.is_active = 1;
            """
        ).fetchall()
        conn.close()

        items: List[Dict[str, Any]] = []
        for r in rows:
            p_code = r["product_code"]
            brand = r["brand"] or "Khác"
            if vendor_filter != "Tất cả" and brand != vendor_filter:
                continue

            vel = velocity_map.get(p_code, {})
            rr_14 = vel.get("rr_14", 0.0)
            rr_30 = vel.get("rr_30", 0.0)
            hist_rr = vel.get("total_hist", 0.0) / 85.0
            # Nếu sản phẩm từng cháy hàng hết trước 14 ngày gần nhất (SOH=0), sử dụng tốc độ bán lịch sử
            if rr_14 == 0 and int(r["soh"]) == 0 and hist_rr > 0:
                rr_14 = hist_rr
                rr_30 = max(rr_30, hist_rr)

            s_factor = self._seasonality_factor(r["seasonality"], ref_date)
            blended_rr = (rr_14 * 0.70) + (rr_30 * 0.30)
            demand_t = round(blended_rr * float(cycle_days) * s_factor, 2)

            # Tồn kho an toàn thích ứng (Z = 1.28 ~ 90% mức độ phục vụ)
            lt = int(r["lead_time_days"])
            safety_stock = max(1, math.ceil(rr_14 * lt * 1.28)) if (blended_rr > 0 or int(r["avl"]) <= int(r["min_stock"])) else 0

            avl = int(r["avl"])
            inc = int(r["inc"])
            # Bỏ qua các mặt hàng đang quá tải vượt trần max_stock
            if int(r["soh"]) > int(r["max_stock"]):
                q_raw = 0.0
            else:
                q_raw = demand_t + safety_stock - avl - inc

            suggested_qty = self.apply_moq_and_pack_rounding(q_raw, int(r["moq"]), int(r["pack_size"]))

            # Độ tin cậy dự báo theo biến thiên CV 30 ngày
            std_30 = vel.get("std_30", 0.0)
            cv = std_30 / (rr_30 + 0.001) if rr_30 > 0 else 0.45
            confidence = round(min(99.0, max(50.0, 100.0 - (cv * 12.0))), 1)

            cost_price = float(r["cost_price"])
            line_total = round(suggested_qty * cost_price, 0)
            unit_margin = max(0.0, float(r["sale_price"]) - cost_price)

            items.append(
                {
                    "product_code": p_code,
                    "product_name": r["product_name"],
                    "brand": brand,
                    "avl": avl,
                    "inc": inc,
                    "safety_stock": safety_stock,
                    "forecast_demand": demand_t,
                    "raw_qty": round(max(0.0, q_raw), 2),
                    "suggested_qty": suggested_qty,
                    "moq": int(r["moq"]),
                    "pack_size": int(r["pack_size"]),
                    "confidence_score": confidence,
                    "cost_price": None if role == "ROLE_SALES" else cost_price,
                    "line_total": None if role == "ROLE_SALES" else line_total,
                    "unit_margin": unit_margin,
                    "blended_rr": blended_rr,
                    "status_label": "Đề xuất nhập" if suggested_qty > 0 else "Đủ hàng kinh doanh",
                }
            )

        items.sort(key=lambda x: (x["suggested_qty"] > 0, -x["avl"], x["blended_rr"]), reverse=True)

        total_units = sum(i["suggested_qty"] for i in items)
        skus_need_import = sum(1 for i in items if i["suggested_qty"] > 0)
        avg_conf = round(sum(i["confidence_score"] for i in items) / len(items), 1) if items else 90.0
        est_cap = sum((i["suggested_qty"] * (i["cost_price"] or 0.0)) for i in items)
        if role == "ROLE_SALES":
            est_cap_val = None
            over_budget = False
        else:
            est_cap_val = round(est_cap, 0)
            over_budget = est_cap_val > budget_cap

        return {
            "cycle_days": cycle_days,
            "budget_cap": budget_cap,
            "skus_to_replenish": skus_need_import,
            "total_suggested_units": total_units,
            "estimated_capital": est_cap_val,
            "display_estimated_capital": self.mask_currency(est_cap, role),
            "avg_confidence_score": avg_conf,
            "over_budget": over_budget,
            "items": items,
        }

    def optimize_within_budget(
        self, items: List[Dict[str, Any]], budget_cap: float
    ) -> List[Dict[str, Any]]:
        """
        FR-REP-05: Cân đối danh mục đề xuất nhập trong phạm vi Trần ngân sách,
        ưu tiên giữ lại SKU đang âm/hết hàng và có tốc độ quay vòng cao.
        """
        cloned = [dict(i) for i in items]

        def calc_total(arr: List[Dict[str, Any]]) -> float:
            return sum(int(x["suggested_qty"]) * float(x["cost_price"] or 0.0) for x in arr)

        if calc_total(cloned) <= budget_cap:
            return cloned

        # Cắt giảm từ nhóm ít cấp thiết nhất (AVL cao hơn / blended_rr thấp hơn) trước
        cut_order = sorted(
            range(len(cloned)),
            key=lambda idx: (-cloned[idx]["avl"], cloned[idx].get("blended_rr", 0.0)),
            reverse=True,
        )
        for idx in cut_order:
            item = cloned[idx]
            cost = float(item.get("cost_price") or 0.0)
            if item["suggested_qty"] <= 0 or cost <= 0:
                continue
            step = max(1, int(item.get("pack_size", 1)))
            while item["suggested_qty"] > 0 and calc_total(cloned) > budget_cap:
                new_qty = item["suggested_qty"] - step
                item["suggested_qty"] = max(0, new_qty)
                item["line_total"] = round(item["suggested_qty"] * cost, 0)
            if calc_total(cloned) <= budget_cap:
                break

        return cloned

    def preview_po_grouping(self, selected_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """FR-REP-06: Gom các SKU đã chọn thành từng đơn đặt hàng PO riêng biệt theo Nhà cung cấp."""
        grouped: Dict[str, Dict[str, Any]] = {}
        for item in selected_items:
            qty = int(item.get("suggested_qty", 0))
            if qty <= 0:
                continue
            brand = item.get("brand") or "Khác"
            v_code, v_name = self.VENDOR_MAP.get(brand, (f"NCC_{brand.upper()}", f"Nhà phân phối {brand}"))
            if v_code not in grouped:
                grouped[v_code] = {
                    "brand": brand,
                    "vendor_code": v_code,
                    "vendor_name": v_name,
                    "items": [],
                    "total_units": 0,
                    "total_amount": 0.0,
                }
            cost = float(item.get("cost_price") or 0.0)
            line_amt = round(qty * cost, 0)
            grouped[v_code]["items"].append(
                {
                    "product_code": item["product_code"],
                    "product_name": item.get("product_name", item["product_code"]),
                    "quantity": qty,
                    "unit_price": cost,
                    "line_total": line_amt,
                }
            )
            grouped[v_code]["total_units"] += qty
            grouped[v_code]["total_amount"] += line_amt

        return list(grouped.values())

    def create_grouped_purchase_orders(
        self,
        selected_items: List[Dict[str, Any]],
        role: str = "ROLE_OWNER",
        ref_date: str = DEFAULT_REF_DATE,
    ) -> Dict[str, Any]:
        """FR-REP-06: Sinh đơn mua hàng PO vào PURCHASE_ORDERS và PO_ITEMS theo từng Nhà cung cấp."""
        if role == "ROLE_SALES":
            return {
                "success": False,
                "error_code": "ERR_UNAUTHORIZED",
                "error": "Nhân viên bán hàng không có quyền ký duyệt tạo đơn nhập hàng PO.",
            }
        groups = self.preview_po_grouping(selected_items)
        if not groups:
            return {
                "success": False,
                "error_code": "ERR_EMPTY_PO",
                "error": "Chưa có SKU nào có số lượng nhập > 0 để tạo đơn PO.",
            }

        conn = self._get_connection()
        created_codes: List[str] = []
        try:
            existing = conn.execute("SELECT COUNT(*) FROM PURCHASE_ORDERS;").fetchone()[0]
            seq = int(existing) + 1
            base_d = datetime.date.fromisoformat(ref_date)

            for g in groups:
                while True:
                    po_code = f"PO{seq:05d}"
                    exists = conn.execute("SELECT 1 FROM PURCHASE_ORDERS WHERE purchase_code = ?;", (po_code,)).fetchone()
                    if not exists:
                        break
                    seq += 1

                eta = (base_d + datetime.timedelta(days=3)).isoformat()
                conn.execute(
                    """
                    INSERT INTO PURCHASE_ORDERS (
                        purchase_code, order_time, vendor_code, vendor_name, branch_code,
                        total_amount, amount_paid, amount_due, expected_delivery_date, status, note
                    ) VALUES (?, ?, ?, ?, 'CN01', ?, 0.0, ?, ?, 'Đang vận chuyển', ?);
                    """,
                    (
                        po_code,
                        f"{ref_date} 09:00:00",
                        g["vendor_code"],
                        g["vendor_name"],
                        g["total_amount"],
                        g["total_amount"],
                        eta,
                        f"PO tự động từ Stock Sense Module 04 ({g['total_units']} thiết bị)",
                    ),
                )
                for line in g["items"]:
                    conn.execute(
                        """
                        INSERT INTO PO_ITEMS (purchase_code, product_code, quantity, unit_price, line_total)
                        VALUES (?, ?, ?, ?, ?);
                        """,
                        (po_code, line["product_code"], line["quantity"], line["unit_price"], line["line_total"]),
                    )
                created_codes.append(po_code)
                seq += 1

            conn.commit()
        finally:
            conn.close()

        return {
            "success": True,
            "created_po_codes": created_codes,
            "po_count": len(created_codes),
            "message": f"Đã tạo thành công {len(created_codes)} đơn đặt hàng PO ({', '.join(created_codes)}) gửi Nhà phân phối.",
        }

    def export_po_groups_csv(self, groups: List[Dict[str, Any]]) -> bytes:
        """Xuất danh sách các đơn PO đã gom nhóm sang định dạng CSV UTF-8 BOM cho Excel."""
        flat_rows = []
        for idx, g in enumerate(groups, start=1):
            for line in g["items"]:
                flat_rows.append(
                    {
                        "Nhom_PO": f"PO_NHOM_{idx}",
                        "Nha_Cung_Cap": g["vendor_name"],
                        "Ma_SKU": line["product_code"],
                        "Ten_Thiet_Bi": line["product_name"],
                        "So_Luong": line["quantity"],
                        "Don_Gia_Von": line["unit_price"],
                        "Thanh_Tien": line["line_total"],
                    }
                )
        df = pd.DataFrame(flat_rows)
        buf = io.BytesIO()
        buf.write(df.to_csv(index=False).encode("utf-8-sig"))
        return buf.getvalue()
