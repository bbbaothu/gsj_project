"""
Lớp dịch vụ xử lý nghiệp vụ Quản lý danh mục & Tồn kho thiết bị (US-1.1).
"""
import sqlite3
from typing import Dict, Any, List, Optional
import pandas as pd

class InventoryService:
    def __init__(self, db_path: str = "data/retail_dienmay.db"):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def get_kpis(self, role: str = "ROLE_OWNER") -> Dict[str, Any]:
        """
        FR-INV-01 & FR-INV-05: Tính toán 4 thẻ chỉ số KPI vĩ mô kèm kiểm soát phân quyền giá vốn.
        """
        conn = self._get_connection()
        cur = conn.cursor()

        # 1. Tổng SKU kinh doanh & Tổng SOH
        cur.execute("""
            SELECT 
                COUNT(DISTINCT product_code) AS total_skus,
                SUM(stock_on_hand) AS total_soh,
                ROUND(SUM(stock_on_hand * cost_price), 0) AS total_capital
            FROM DIM_PRODUCTS
            WHERE is_active = 1 AND has_serial = 1;
        """)
        summary = cur.fetchone()

        # 2. Số lượng cảnh báo tồn kho
        cur.execute("""
            SELECT 
                COUNT(CASE WHEN stock_on_hand <= min_stock THEN 1 END) AS stockout_count,
                COUNT(CASE WHEN stock_on_hand > max_stock THEN 1 END) AS overstock_count,
                ROUND(SUM(CASE WHEN stock_on_hand > max_stock THEN stock_on_hand * cost_price ELSE 0 END), 0) AS overstock_capital
            FROM DIM_PRODUCTS
            WHERE is_active = 1 AND has_serial = 1;
        """)
        alerts = cur.fetchone()
        conn.close()

        total_cap = float(summary["total_capital"]) if summary["total_capital"] else 0.0
        overstock_cap = float(alerts["overstock_capital"]) if alerts["overstock_capital"] else 0.0

        # Phân quyền: ROLE_SALES bị che giấu giá vốn
        if role == "ROLE_SALES":
            display_capital = "****** đ"
            display_overstock_capital = "****** đ"
            return_total_cap = None
        else:
            display_capital = f"{total_cap:,.0f} đ"
            display_overstock_capital = f"{overstock_cap:,.0f} đ"
            return_total_cap = total_cap

        return {
            "total_skus": summary["total_skus"] or 0,
            "total_soh": summary["total_soh"] or 0,
            "total_capital": return_total_cap,
            "display_capital": display_capital,
            "overstock_count": alerts["overstock_count"] or 0,
            "overstock_capital": overstock_cap if role != "ROLE_SALES" else None,
            "display_overstock_capital": display_overstock_capital,
            "stockout_count": alerts["stockout_count"] or 0,
        }

    def get_products_dataframe(
        self,
        category: str = "Tất cả",
        brand: str = "Tất cả",
        status: str = "Tất cả",
        search: str = "",
        role: str = "ROLE_OWNER"
    ) -> pd.DataFrame:
        """
        FR-INV-02: Truy vấn và lọc danh mục sản phẩm theo nhiều tiêu chí.
        """
        conn = self._get_connection()
        query = """
            SELECT 
                p.product_code,
                p.product_name,
                p.category_path,
                p.brand,
                p.sale_price,
                p.cost_price,
                p.stock_on_hand,
                p.min_stock,
                p.max_stock,
                p.has_serial,
                ROUND(p.stock_on_hand * p.cost_price, 0) AS capital_tied,
                CASE 
                    WHEN p.stock_on_hand <= p.min_stock THEN 'Cảnh báo: Cần nhập gấp'
                    WHEN p.stock_on_hand > p.max_stock THEN 'Cảnh báo: Tồn kho quá cao'
                    ELSE 'Tồn kho an toàn'
                END AS inventory_status
            FROM DIM_PRODUCTS p
            WHERE p.is_active = 1
        """
        params: List[Any] = []

        if category != "Tất cả":
            query += " AND p.category_path LIKE ?"
            params.append(f"%{category}%")

        if brand != "Tất cả":
            query += " AND p.brand = ?"
            params.append(brand)

        if search:
            query += " AND (p.product_code LIKE ? OR p.product_name LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        if status != "Tất cả":
            df = df[df["inventory_status"] == status]

        # Kiểm soát phân quyền: Role Sales không được xem cost_price và capital_tied
        if role == "ROLE_SALES":
            df = df.drop(columns=["cost_price", "capital_tied"])

        return df

    def get_serial_drilldown(self, product_code: str) -> Dict[str, Any]:
        """
        FR-INV-03: Lấy danh sách Serial/IMEI thực tế của SKU và kiểm tra tính toàn vẹn.
        """
        conn = self._get_connection()
        cur = conn.cursor()

        cur.execute("SELECT product_name, stock_on_hand FROM DIM_PRODUCTS WHERE product_code = ?;", (product_code,))
        prod = cur.fetchone()
        if not prod:
            conn.close()
            return {"error": f"Không tìm thấy SKU {product_code}"}

        cur.execute("""
            SELECT serial_number, branch_code, status, import_date
            FROM DIM_PRODUCT_SERIALS
            WHERE product_code = ? AND status = 'IN_STOCK'
            ORDER BY import_date ASC;
        """, (product_code,))
        serials = [dict(r) for r in cur.fetchall()]
        conn.close()

        is_integrity_ok = (len(serials) == prod["stock_on_hand"])

        return {
            "product_code": product_code,
            "product_name": prod["product_name"],
            "stock_on_hand": prod["stock_on_hand"],
            "serials": serials,
            "is_integrity_ok": is_integrity_ok,
            "delta": prod["stock_on_hand"] - len(serials)
        }
