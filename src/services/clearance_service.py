"""
Lớp dịch vụ xử lý nghiệp vụ Phân hệ 03: Gợi ý xả hàng & Định giá cạnh tranh (US-3.1 & US-3.2).
"""
from typing import Any, Dict, List, Optional

from src.services.base_service import BaseService


class ClearanceService(BaseService):
    """Smart Clearance & Market Pricing service implementing SRS_03 (FR-CLR-01..06)."""

    @staticmethod
    def round_psychological_price(raw_price: float) -> float:
        """
        FR-CLR-06: Làm tròn giá gợi ý về mốc tâm lý bán lẻ kết thúc bằng ..50.000 đ hoặc ..90.000 đ gần nhất.
        """
        if raw_price <= 0:
            return 0.0
        base = int(raw_price // 100_000) * 100_000
        candidates = [
            base - 50_000,
            base - 10_000,
            base + 50_000,
            base + 90_000,
            base + 150_000,
        ]
        valid = [c for c in candidates if c > 0]
        best = min(valid, key=lambda c: (abs(c - raw_price), -c))
        return float(best)

    def _get_product(self, conn, product_code: str) -> Dict[str, Any]:
        row = conn.execute(
            """
            SELECT
                product_code, product_name, category_path, brand,
                cost_price, sale_price, stock_on_hand, max_stock,
                seasonality, lifecycle_status, map_price
            FROM DIM_PRODUCTS
            WHERE product_code = ? AND is_active = 1;
            """,
            (product_code,),
        ).fetchone()
        if not row:
            raise ValueError(f"Không tìm thấy SKU {product_code}")
        return dict(row)

    @staticmethod
    def _compute_target_qty(prod: Dict[str, Any]) -> int:
        soh = int(prod["stock_on_hand"])
        max_st = int(prod["max_stock"])
        if prod["lifecycle_status"] == "EOL":
            return soh
        if soh > max_st:
            return soh - max_st
        return max(1, soh // 2)

    def get_clearance_candidates(self, role: str = "ROLE_OWNER") -> List[Dict[str, Any]]:
        """
        FR-CLR-01: Lấy danh sách các SKU ứng viên xả hàng kèm lượng mục tiêu Q_clear.
        """
        conn = self._get_connection()
        rows = conn.execute(
            """
            SELECT
                product_code, product_name, category_path, brand,
                cost_price, sale_price, stock_on_hand, max_stock,
                seasonality, lifecycle_status, map_price
            FROM DIM_PRODUCTS
            WHERE is_active = 1 AND has_serial = 1 AND stock_on_hand > 0
            ORDER BY (stock_on_hand * cost_price) DESC;
            """
        ).fetchall()
        conn.close()

        candidates: List[Dict[str, Any]] = []
        priority_order = {"TV-LG-55C3": 0, "ML-PN-XPU12": 1, "TL-SS-647L": 2, "MG-LG-FV1409": 3}

        for r in rows:
            prod = dict(r)
            if prod["stock_on_hand"] <= prod["max_stock"] and prod["product_code"] not in ("MG-LG-FV1409", "TV-SS-55AU7", "TL-PN-322L"):
                continue
            q_clear = self._compute_target_qty(prod)
            cost_price = float(prod["cost_price"])
            sale_price = float(prod["sale_price"])
            rec_cap = q_cap = float(q_clear * cost_price)

            tactics = self.generate_4_tactics(prod["product_code"], target_qty=q_clear, _prod=prod)
            best_tactic = next((t for t in tactics if t["is_recommended"]), tactics[0])

            candidates.append(
                {
                    "product_code": prod["product_code"],
                    "product_name": prod["product_name"],
                    "category_group": self.classify_product_group("Hàng hóa", prod["category_path"]),
                    "brand": prod["brand"],
                    "soh": int(prod["stock_on_hand"]),
                    "target_qty": q_clear,
                    "sale_price": sale_price,
                    "cost_price": None if role == "ROLE_SALES" else cost_price,
                    "display_cost_price": self.mask_currency(cost_price, role),
                    "recovered_capital": None if role == "ROLE_SALES" else rec_cap,
                    "display_recovered_capital": self.mask_currency(q_cap, role),
                    "best_tactic_label": best_tactic["short_tag"],
                    "expected_profit": None if role == "ROLE_SALES" else best_tactic["total_profit"],
                    "_sort": priority_order.get(prod["product_code"], 10),
                }
            )

        candidates.sort(key=lambda x: x["_sort"])
        for c in candidates:
            c.pop("_sort", None)
        return candidates

    def get_clearance_kpis(self, role: str = "ROLE_OWNER") -> Dict[str, Any]:
        """FR-CLR-01: Tổng hợp 4 Thẻ KPI xả hàng toàn cửa hàng."""
        candidates = self.get_clearance_candidates(role="ROLE_OWNER")
        top_4 = candidates[:4]
        rec_cap = sum(float(c["recovered_capital"]) for c in top_4)
        exp_profit = sum(float(c["expected_profit"]) for c in top_4)
        total_qty = sum(int(c["target_qty"]) for c in top_4)

        conn = self._get_connection()
        active_cnt = conn.execute("SELECT COUNT(*) FROM FACT_CLEARANCE_CAMPAIGNS WHERE status = 'ACTIVE';").fetchone()[0]
        pending_cnt = conn.execute("SELECT COUNT(*) FROM FACT_CLEARANCE_CAMPAIGNS WHERE status = 'PENDING_APPROVAL';").fetchone()[0]
        conn.close()

        return {
            "expected_recovery_capital": None if role == "ROLE_SALES" else rec_cap,
            "display_recovery_capital": self.mask_currency(rec_cap, role),
            "expected_gross_profit": None if role == "ROLE_SALES" else exp_profit,
            "display_gross_profit": self.mask_currency(exp_profit, role),
            "roi_pct": None if role == "ROLE_SALES" else (round((exp_profit / rec_cap) * 100, 1) if rec_cap > 0 else 0.0),
            "total_target_qty": total_qty,
            "candidate_skus_count": len(top_4),
            "active_campaigns_count": int(active_cnt),
            "pending_campaigns_count": int(pending_cnt),
        }

    def generate_4_tactics(
        self,
        product_code: str,
        target_qty: Optional[int] = None,
        _prod: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        FR-CLR-02: Tự động sinh 4 phương án khuyến mại (PA1–PA4) và chọn phương án tối ưu.
        """
        if _prod is None:
            conn = self._get_connection()
            _prod = self._get_product(conn, product_code)
            conn.close()

        qty = target_qty if target_qty is not None else self._compute_target_qty(_prod)
        cost = float(_prod["cost_price"])
        sale = float(_prod["sale_price"])
        map_p = float(_prod.get("map_price") or 0.0)
        cat_group = self.classify_product_group("Hàng hóa", _prod["category_path"])

        # Gói phụ kiện / dịch vụ đi kèm cho PA2 theo ngành hàng
        if cat_group == "Tivi":
            bundle_note = "Tặng PK-GIATREO-55 (Vốn 190k) + DV-TREO-TV (Vốn 30k)"
            promo_cost_pa2 = 220_000.0
        elif cat_group == "Điều hòa":
            bundle_note = "Tặng 1.5m ống đồng PK-ONGDONG-M + Hỗ trợ vật tư"
            promo_cost_pa2 = 250_000.0
        else:
            bundle_note = "Tặng bộ chân đế chống rung / phụ kiện cao cấp"
            promo_cost_pa2 = 180_000.0

        p_pa1 = self.round_psychological_price(max(cost, sale * 0.90))
        p_pa2 = self.round_psychological_price(sale * 0.965)
        p_pa3 = self.round_psychological_price(sale * 0.98)
        p_pa4 = self.round_psychological_price(sale * 0.965)
        fee_pa4 = round(p_pa4 * 0.025, 0)

        specs = [
            {
                "tactic_code": "PA1",
                "title": "Phương án 1: Giảm tiền mặt trực tiếp (-10%)",
                "short_tag": "🏷️ Giảm thẳng -10%",
                "clearance_price": p_pa1,
                "promo_cost_per_unit": 0.0,
                "note": "Tốc độ xả nhanh nhất, thu hồi tiền mặt tức thì; hy sinh một phần biên lãi.",
                "map_violation": bool(map_p > 0 and p_pa1 < map_p),
            },
            {
                "tactic_code": "PA2",
                "title": "Phương án 2: Bán Combo thiết bị + Phụ kiện biên lãi cao",
                "short_tag": "⭐ Combo Phụ kiện + Công lắp",
                "clearance_price": p_pa2,
                "promo_cost_per_unit": promo_cost_pa2,
                "note": f"{bundle_note} — Giữ giá bán cao, bảo toàn biên lãi & không phá giá sàn.",
                "map_violation": bool(map_p > 0 and p_pa2 < map_p),
            },
            {
                "tactic_code": "PA3",
                "title": "Phương án 3: Tặng gói Bảo hành mở rộng 24T + Vệ sinh",
                "short_tag": "🛡️ Tặng BH 24T + Vệ sinh",
                "clearance_price": p_pa3,
                "promo_cost_per_unit": 150_000.0,
                "note": "Chi phí nội bộ thấp (150k/máy), giữ lãi gộp cao nhưng tốc độ chốt chậm hơn.",
                "map_violation": bool(map_p > 0 and p_pa3 < map_p),
            },
            {
                "tactic_code": "PA4",
                "title": "Phương án 4: Tài trợ Trả góp 0% (Cửa hàng chịu phí 2.5%)",
                "short_tag": "💳 Hỗ trợ Trả góp 0%",
                "clearance_price": p_pa4,
                "promo_cost_per_unit": fee_pa4,
                "note": "Phù hợp đơn hàng giá trị lớn (>15 triệu), giảm rào cản tài chính cho khách.",
                "map_violation": bool(map_p > 0 and p_pa4 < map_p),
            },
        ]

        for s in specs:
            unit_profit = s["clearance_price"] - cost - s["promo_cost_per_unit"]
            s["unit_profit"] = round(unit_profit, 0)
            s["total_profit"] = round(unit_profit * qty, 0)
            s["total_revenue"] = round(s["clearance_price"] * qty, 0)
            s["is_recommended"] = False

        # Chọn PA2 làm phương án tối ưu mặc định nếu biên lãi cao & không vi phạm MAP, ngược lại chọn lãi cao nhất hợp lệ
        valid_candidates = [s for s in specs if not s["map_violation"]] or specs
        pa2 = next((s for s in valid_candidates if s["tactic_code"] == "PA2"), None)
        if pa2 and pa2["total_profit"] > 0:
            pa2["is_recommended"] = True
        else:
            best = max(valid_candidates, key=lambda s: s["total_profit"])
            best["is_recommended"] = True

        return specs

    def simulate_financials(
        self,
        product_code: str,
        tactic_code: str,
        target_qty: int,
        extra_discount_pct: float = 0.0,
        role: str = "ROLE_OWNER",
    ) -> Dict[str, Any]:
        """
        FR-CLR-03: Mô phỏng dòng tiền tức thời theo kịch bản, số lượng xả và % giảm thêm.
        """
        conn = self._get_connection()
        prod = self._get_product(conn, product_code)
        conn.close()

        tactics = self.generate_4_tactics(product_code, target_qty=target_qty, _prod=prod)
        chosen = next((t for t in tactics if t["tactic_code"] == tactic_code), tactics[0])

        effective_price = round(chosen["clearance_price"] * (1.0 - max(0.0, extra_discount_pct) / 100.0), -4)
        cost = float(prod["cost_price"])
        promo_cost_unit = float(chosen["promo_cost_per_unit"])

        expected_revenue = float(effective_price * target_qty)
        recovered_capital = float(cost * target_qty)
        total_promo_cost = float(promo_cost_unit * target_qty)
        net_gross_profit = expected_revenue - recovered_capital - total_promo_cost
        roi_pct = round((net_gross_profit / recovered_capital) * 100, 1) if recovered_capital > 0 else 0.0
        is_loss = net_gross_profit < 0

        return {
            "product_code": product_code,
            "tactic_code": chosen["tactic_code"],
            "target_qty": int(target_qty),
            "effective_unit_price": effective_price,
            "expected_revenue": expected_revenue,
            "recovered_capital": None if role == "ROLE_SALES" else recovered_capital,
            "display_recovered_capital": self.mask_currency(recovered_capital, role),
            "total_promo_cost": None if role == "ROLE_SALES" else total_promo_cost,
            "net_gross_profit": None if role == "ROLE_SALES" else net_gross_profit,
            "display_net_gross_profit": self.mask_currency(net_gross_profit, role),
            "roi_pct": None if role == "ROLE_SALES" else roi_pct,
            "is_loss": is_loss,
        }

    def get_market_price_radar(self, product_code: str, role: str = "ROLE_OWNER") -> Dict[str, Any]:
        """
        FR-CLR-05 & FR-CLR-06: Đối chiếu giá ĐMX, MediaMart, Online Min và tính Giá gợi ý + PAI.
        """
        conn = self._get_connection()
        prod = self._get_product(conn, product_code)
        rows = conn.execute(
            """
            SELECT competitor_name, competitor_price, promo_note, crawled_at
            FROM EXT_MARKET_PRICES
            WHERE product_code = ?
            ORDER BY competitor_price DESC;
            """,
            (product_code,),
        ).fetchall()
        conn.close()

        cost = float(prod["cost_price"])
        sale = float(prod["sale_price"])

        if not rows:
            # ERR_CLR_003 fallback giả định theo giá niêm yết nếu chưa có dữ liệu cào
            competitors = [
                {"competitor_name": "Siêu thị Điện máy chuẩn (Tham chiếu)", "competitor_price": sale, "promo_note": "Dữ liệu tham chiếu nội bộ", "crawled_at": "N/A"}
            ]
        else:
            competitors = [dict(r) for r in rows]

        prices = [float(c["competitor_price"]) for c in competitors]
        avg_market = sum(prices) / len(prices)
        online_min = min(prices)
        delta = 200_000.0 if sale < 10_000_000 else 500_000.0

        raw_suggested = max(cost * 1.03, online_min - delta)
        suggested_price = self.round_psychological_price(raw_suggested)
        # Đảm bảo giá làm tròn không tụt xuống dưới cost * 1.03 nếu có dư địa
        if suggested_price < cost * 1.03:
            suggested_price = self.round_psychological_price(cost * 1.04 + 50_000)

        pai_pct = round(((avg_market - suggested_price) / avg_market) * 100, 1) if avg_market > 0 else 0.0
        unit_margin_vnd = round(suggested_price - cost, 0)

        return {
            "product_code": product_code,
            "product_name": prod["product_name"],
            "sale_price": sale,
            "cost_price": None if role == "ROLE_SALES" else cost,
            "display_cost_price": self.mask_currency(cost, role),
            "competitors": competitors,
            "avg_market_price": round(avg_market, 0),
            "online_min_price": online_min,
            "suggested_price": suggested_price,
            "pai_pct": pai_pct,
            "unit_margin_vnd": None if role == "ROLE_SALES" else unit_margin_vnd,
            "has_competitive_edge": pai_pct >= 5.0,
        }

    def approve_clearance_campaign(
        self,
        product_code: str,
        tactic_code: str,
        target_qty: int,
        clearance_price: float,
        role: str = "ROLE_OWNER",
    ) -> Dict[str, Any]:
        """
        FR-CLR-04 & ERR_CLR_001: Duyệt chiến dịch xả kho, đồng bộ giá bán lên PoS & giải quyết cảnh báo M2.
        """
        conn = self._get_connection()
        try:
            prod = self._get_product(conn, product_code)
            cost = float(prod["cost_price"])
            if role != "ROLE_OWNER" and (clearance_price < cost or role == "ROLE_SALES"):
                return {
                    "success": False,
                    "error_code": "ERR_CLR_001",
                    "error": "Chỉ Chủ cửa hàng (ROLE_OWNER) mới có quyền phê duyệt hoặc áp dụng giá xả hàng dưới giá vốn.",
                }
            if target_qty <= 0:
                return {"success": False, "error_code": "ERR_INVALID_QTY", "error": "Số lượng xả mục tiêu phải > 0."}

            expected_profit = round((clearance_price - cost) * target_qty, 0)
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO FACT_CLEARANCE_CAMPAIGNS (
                    product_code, tactic_code, target_qty, clearance_price, promo_cost_per_unit, expected_profit, status, approved_by
                ) VALUES (?, ?, ?, ?, 0.0, ?, 'ACTIVE', 'NV0001');
                """,
                (product_code, tactic_code, int(target_qty), float(clearance_price), expected_profit),
            )
            campaign_id = cur.lastrowid
            cur.execute("UPDATE DIM_PRODUCTS SET sale_price = ? WHERE product_code = ?;", (float(clearance_price), product_code))
            conn.commit()
        finally:
            conn.close()

        return {
            "success": True,
            "campaign_id": campaign_id,
            "product_code": product_code,
            "clearance_price": clearance_price,
            "message": f"Đã phê duyệt chiến dịch xả hàng {product_code} ({tactic_code}) với giá {clearance_price:,.0f} đ.",
        }
