"""
Lớp cơ sở dùng chung cho các Service của Stock Sense (DB connection, RBAC masking, Velocity metrics).
"""
import datetime
import sqlite3
from typing import Dict, Optional, Tuple


class BaseService:
    """Base SQLite service providing connection handling and shared domain helpers."""

    CORE_CATEGORIES = ("Tivi", "Điều hòa", "Tủ lạnh", "Máy giặt")

    def __init__(self, db_path: str = "data/retail_dienmay.db"):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def mask_currency(amount: Optional[float], role: str) -> str:
        """Ẩn giá trị tiền tệ nếu tài khoản không có quyền xem giá vốn/lãi."""
        if role == "ROLE_SALES" or amount is None:
            return "****** đ"
        return f"{amount:,.0f} đ"

    @staticmethod
    def get_effective_sales_anchor(conn: sqlite3.Connection, ref_date: str) -> str:
        """
        Xác định mốc ngày bán hàng hiệu lực gần nhất <= ref_date để tính Run-Rate ổn định
        ngay cả khi snapshot hóa đơn và đơn đặt hàng lệch pha thời gian.
        """
        row = conn.execute(
            "SELECT MAX(DATE(invoice_time)) AS max_d FROM FACT_INVOICES WHERE DATE(invoice_time) <= ?;",
            (ref_date,),
        ).fetchone()
        if row and row["max_d"]:
            return str(row["max_d"])
        return ref_date

    @classmethod
    def classify_product_group(cls, product_type: str, category_path: str) -> str:
        """Phân nhóm sản phẩm chuẩn hóa phục vụ phân tích Attach-Rate & Thác nước lợi nhuận."""
        if product_type == "Dịch vụ" or category_path.startswith("Dịch vụ"):
            return "Dịch vụ"
        if category_path.startswith("Phụ kiện") or category_path.startswith("Vật tư"):
            return "Phụ kiện"
        for cat in cls.CORE_CATEGORIES:
            if cat in category_path:
                return cat
        return "Thiết bị khác"

    @staticmethod
    def load_sales_velocity_map(
        conn: sqlite3.Connection, ref_date: str
    ) -> Tuple[str, Dict[str, Dict[str, float]]]:
        """
        Tính toán tập trung tốc độ bán (RR7, RR14, RR30, ngày bán cuối, độ lệch chuẩn 30d)
        cho từng SKU để dùng thống nhất ở Module 02 và Module 04.
        """
        anchor_str = BaseService.get_effective_sales_anchor(conn, ref_date)
        anchor_d = datetime.date.fromisoformat(anchor_str)
        ref_d = datetime.date.fromisoformat(ref_date)

        rows = conn.execute(
            """
            SELECT
                l.product_code,
                DATE(i.invoice_time) AS sale_date,
                SUM(l.quantity) AS qty
            FROM FACT_INVOICES_LINES l
            JOIN FACT_INVOICES i ON l.invoice_code = i.invoice_code
            WHERE DATE(i.invoice_time) <= ?
            GROUP BY l.product_code, DATE(i.invoice_time);
            """,
            (ref_date,),
        ).fetchall()

        per_sku_dates: Dict[str, Dict[datetime.date, float]] = {}
        for r in rows:
            p_code = r["product_code"]
            d_val = datetime.date.fromisoformat(r["sale_date"])
            per_sku_dates.setdefault(p_code, {})
            per_sku_dates[p_code][d_val] = per_sku_dates[p_code].get(d_val, 0.0) + float(r["qty"])

        velocity_map: Dict[str, Dict[str, float]] = {}
        for p_code, date_qty in per_sku_dates.items():
            last_sale_d = max(date_qty.keys())
            days_since_last = max(0, (ref_d - last_sale_d).days)

            qty_7 = sum(q for d, q in date_qty.items() if 0 <= (anchor_d - d).days < 7)
            qty_14 = sum(q for d, q in date_qty.items() if 0 <= (anchor_d - d).days < 14)
            qty_30 = sum(q for d, q in date_qty.items() if 0 <= (anchor_d - d).days < 30)
            total_hist = sum(date_qty.values())

            rr_7 = qty_7 / 7.0
            rr_14 = qty_14 / 14.0
            rr_30 = qty_30 / 30.0

            # Tính độ lệch chuẩn 30 ngày phục vụ Confidence Score (FR-REP-04)
            daily_series = [date_qty.get(anchor_d - datetime.timedelta(days=offset), 0.0) for offset in range(30)]
            mean_30 = rr_30
            variance = sum((x - mean_30) ** 2 for x in daily_series) / 30.0
            std_30 = variance ** 0.5

            velocity_map[p_code] = {
                "qty_7": qty_7,
                "qty_14": qty_14,
                "qty_30": qty_30,
                "total_hist": total_hist,
                "rr_7": rr_7,
                "rr_14": rr_14,
                "rr_30": rr_30,
                "std_30": std_30,
                "days_since_last_sale": float(days_since_last),
                "last_sale_date": last_sale_d.isoformat(),
            }

        return anchor_str, velocity_map
