"""
Lớp dịch vụ xử lý nghiệp vụ Theo dõi Đơn hàng & Điều phối dòng hàng (US-1.2).
"""
import sqlite3
import datetime
from typing import Dict, Any, List, Optional
import pandas as pd

class OrderService:
    def __init__(self, db_path: str = "data/retail_dienmay.db"):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def _mask_vnd(self, val: Optional[float], role: str) -> str:
        if role == "ROLE_SALES" or val is None:
            return "****** đ"
        abs_val = abs(float(val))
        if abs_val >= 1_000_000_000:
            return f"{abs_val / 1_000_000_000:.2f}".replace(".", ",") + " tỷ"
        if abs_val >= 1_000_000:
            return f"{abs_val / 1_000_000:.1f}".replace(".", ",") + " tr"
        return f"{abs_val:,.0f} đ"

    def get_order_flow_kpis(self, role: str = "ROLE_OWNER") -> Dict[str, Any]:
        """
        FR-ORD-01 & FR-ORD-05: Thống kê 4 thẻ KPI của phân hệ Đơn hàng & Dòng hàng.
        """
        conn = self._get_connection()
        cur = conn.cursor()

        # 1. Đơn đang giữ chỗ (Chờ xử lý, Đã xác nhận) + tổng vốn/giá trị đang giữ
        cur.execute("""
            SELECT 
                COUNT(DISTINCT fo.order_code) AS reserved_orders,
                COALESCE(SUM(fol.quantity), 0) AS reserved_units,
                COALESCE(SUM(fol.quantity * p.cost_price), 0) AS reserved_capital
            FROM FACT_ORDERS fo
            JOIN FACT_ORDERS_LINES fol ON fo.order_code = fol.order_code
            JOIN DIM_PRODUCTS p ON fol.product_code = p.product_code
            WHERE fo.status IN ('Chờ xử lý', 'Đã xác nhận');
        """)
        res_info = cur.fetchone()

        # 2. Hàng đang trên đường về kho từ PURCHASE_ORDERS
        cur.execute("""
            SELECT COALESCE(SUM(poi.quantity), 0) AS in_transit_units,
                   COUNT(DISTINCT po.purchase_code) AS po_count
            FROM PURCHASE_ORDERS po
            JOIN PO_ITEMS poi ON po.purchase_code = poi.purchase_code
            WHERE po.status = 'Đang vận chuyển';
        """)
        po_info = cur.fetchone()

        # 3. Đơn đăng ký trả góp
        cur.execute("""
            SELECT COUNT(*) AS installment_count
            FROM FACT_ORDERS
            WHERE pay_installment > 0;
        """)
        inst_count = cur.fetchone()["installment_count"]

        # 4. Đơn quá hạn 48 giờ (Hold time policy violation) & tổng vốn bị kẹt
        cur.execute("""
            SELECT 
                COUNT(DISTINCT fo.order_code) AS expired_count,
                COALESCE(SUM(fol.quantity * p.cost_price), 0) AS expired_capital
            FROM FACT_ORDERS fo
            JOIN FACT_ORDERS_LINES fol ON fo.order_code = fol.order_code
            JOIN DIM_PRODUCTS p ON fol.product_code = p.product_code
            WHERE fo.status = 'Chờ xử lý'
              AND (fo.note LIKE '%48h%' OR fo.order_time <= '2026-11-02 15:30:00');
        """)
        exp_row = cur.fetchone()

        # 5. Đơn cần giao hôm nay (Đã xác nhận)
        cur.execute("""
            SELECT COUNT(*) AS today_dispatch
            FROM FACT_ORDERS
            WHERE status = 'Đã xác nhận';
        """)
        dispatch_count = cur.fetchone()["today_dispatch"]

        conn.close()

        raw_res_cap = float(res_info["reserved_capital"] or 0.0)
        raw_exp_cap = float(exp_row["expired_capital"] or 0.0)

        return {
            "reserved_orders_count": res_info["reserved_orders"] or 0,
            "reserved_units_count": res_info["reserved_units"] or 0,
            "reserved_capital": None if role == "ROLE_SALES" else round(raw_res_cap, 0),
            "display_reserved_capital": self._mask_vnd(raw_res_cap, role),
            "in_transit_units": po_info["in_transit_units"] or 0,
            "in_transit_po_count": po_info["po_count"] or 0,
            "installment_orders_count": inst_count or 0,
            "expired_orders_count": exp_row["expired_count"] or 0,
            "expired_capital": None if role == "ROLE_SALES" else round(raw_exp_cap, 0),
            "display_expired_capital": self._mask_vnd(raw_exp_cap, role),
            "today_dispatch_count": dispatch_count or 0,
        }

    def get_order_detail(self, order_code: str, role: str = "ROLE_OWNER") -> Dict[str, Any]:
        """Truy vấn thông tin chi tiết khách hàng & mặt hàng của 1 đơn giữ chỗ."""
        conn = self._get_connection()
        hdr = conn.execute(
            """
            SELECT
                fo.order_code, fo.order_time, fo.customer_code,
                c.customer_name, c.phone, c.address,
                fo.total_amount, fo.amount_due, fo.amount_paid,
                fo.pay_installment, fo.status AS order_status, fo.note
            FROM FACT_ORDERS fo
            JOIN DIM_CUSTOMERS c ON fo.customer_code = c.customer_code
            WHERE fo.order_code = ?;
            """,
            (order_code,),
        ).fetchone()
        if not hdr:
            conn.close()
            return {"error": f"Không tìm thấy đơn hàng {order_code}"}

        lines = conn.execute(
            """
            SELECT
                fol.product_code, p.product_name, p.brand,
                fol.quantity, fol.unit_price, fol.line_total, p.cost_price
            FROM FACT_ORDERS_LINES fol
            JOIN DIM_PRODUCTS p ON fol.product_code = p.product_code
            WHERE fol.order_code = ?;
            """,
            (order_code,),
        ).fetchall()
        conn.close()

        is_exp = False
        if hdr["order_status"] == "Chờ xử lý":
            if "48h" in str(hdr["note"] or ""):
                is_exp = True
            else:
                try:
                    ot = datetime.datetime.strptime(hdr["order_time"], "%Y-%m-%d %H:%M:%S")
                    is_exp = ((datetime.datetime(2026, 11, 4, 15, 30, 0) - ot).total_seconds() / 3600) > 48
                except Exception:
                    is_exp = False

        pay_type = "Trả góp" if float(hdr["pay_installment"] or 0) > 0 else (
            "Trả đủ" if float(hdr["amount_paid"] or 0) >= float(hdr["amount_due"] or 0) else "Đặt cọc (COD)"
        )
        items = []
        for l in lines:
            d = dict(l)
            if role == "ROLE_SALES":
                d["cost_price"] = None
            items.append(d)

        return {
            "order_code": hdr["order_code"],
            "order_time": hdr["order_time"],
            "customer_code": hdr["customer_code"],
            "customer_name": hdr["customer_name"],
            "phone": hdr["phone"],
            "address": hdr["address"],
            "status": hdr["order_status"],
            "note": hdr["note"] or "",
            "payment_type": pay_type,
            "is_expired": is_exp,
            "total_amount": float(hdr["total_amount"] or 0),
            "amount_paid": float(hdr["amount_paid"] or 0),
            "amount_due": float(hdr["amount_due"] or 0),
            "items": items,
        }

    def get_inventory_flow_matrix(self) -> pd.DataFrame:
        """
        FR-ORD-01 & FR-ORD-04: Truy vấn ma trận dòng hàng 4 trạng thái từ View CSDL.
        """
        conn = self._get_connection()
        query = """
            SELECT 
                product_code, product_name, category_path, brand,
                cost_price, sale_price, soh, res, avl, inc, projected_stock,
                flow_status, inventory_status
            FROM VW_INVENTORY_FLOW_OVERVIEW
            WHERE has_serial = 1
            ORDER BY soh DESC;
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_orders_dataframe(
        self,
        status: str = "Tất cả",
        payment_type: str = "Tất cả",
        flow_status: str = "Tất cả",
        search: str = ""
    ) -> pd.DataFrame:
        """
        FR-ORD-01, FR-ORD-03, FR-ORD-05: Lấy danh sách đơn hàng kèm tính toán trạng thái thanh toán và quá hạn.
        """
        conn = self._get_connection()
        query = """
            SELECT 
                fo.order_code,
                fo.order_time,
                fo.customer_code,
                c.customer_name,
                c.phone AS customer_phone,
                fo.total_amount,
                fo.amount_due,
                fo.amount_paid,
                fo.pay_cash,
                fo.pay_transfer,
                fo.pay_card,
                fo.pay_installment,
                fo.status AS order_status,
                fo.note,
                fol.product_code,
                p.product_name,
                fol.quantity,
                fol.unit_price,
                v.flow_status
            FROM FACT_ORDERS fo
            JOIN FACT_ORDERS_LINES fol ON fo.order_code = fol.order_code
            JOIN DIM_PRODUCTS p ON fol.product_code = p.product_code
            JOIN DIM_CUSTOMERS c ON fo.customer_code = c.customer_code
            LEFT JOIN VW_INVENTORY_FLOW_OVERVIEW v ON p.product_code = v.product_code
            ORDER BY fo.order_time DESC;
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        # Tính toán loại thanh toán
        def classify_payment(row):
            if row["pay_installment"] > 0:
                return "Trả góp"
            elif row["amount_paid"] >= row["amount_due"]:
                return "Trả đủ"
            return "Cọc (COD)"

        df["payment_type"] = df.apply(classify_payment, axis=1)

        # Tính toán cờ quá hạn 48h
        def check_expired(row):
            if row["order_status"] != "Chờ xử lý":
                return False
            if "48h" in str(row["note"]):
                return True
            try:
                ot = datetime.datetime.strptime(row["order_time"], "%Y-%m-%d %H:%M:%S")
                # Giả định mốc kiểm tra là ngày 2026-11-04
                delta_h = (datetime.datetime(2026, 11, 4, 15, 30, 0) - ot).total_seconds() / 3600
                return delta_h > 48
            except Exception:
                return False

        df["is_expired"] = df.apply(check_expired, axis=1)

        # Áp dụng bộ lọc
        if status != "Tất cả":
            df = df[df["order_status"] == status]

        if payment_type != "Tất cả":
            df = df[df["payment_type"] == payment_type]

        if flow_status != "Tất cả":
            df = df[df["flow_status"] == flow_status]

        if search:
            kw = search.lower()
            df = df[
                df["order_code"].str.lower().str.contains(kw) |
                df["customer_name"].str.lower().str.contains(kw) |
                df["customer_phone"].str.contains(kw) |
                df["product_name"].str.lower().str.contains(kw)
            ]

        return df

    def cancel_order(self, order_code: str, reason: str = "Khách hủy đơn") -> Dict[str, Any]:
        """
        FR-ORD-03: Hủy đơn hàng và tự động giải phóng tồn giữ chỗ (RES).
        """
        conn = self._get_connection()
        cur = conn.cursor()

        cur.execute("SELECT status FROM FACT_ORDERS WHERE order_code = ?;", (order_code,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return {"success": False, "error": f"Không tìm thấy đơn hàng {order_code}"}

        if row["status"] in ("Đang giao hàng", "Hoàn thành"):
            conn.close()
            return {"success": False, "error": "Đơn hàng đang giao hoặc đã hoàn thành, không thể hủy trực tiếp."}

        # Cập nhật trạng thái thành Đã hủy
        new_note = f"ĐÃ HỦY: {reason}"
        cur.execute("""
            UPDATE FACT_ORDERS 
            SET status = 'Đã hủy', note = ?
            WHERE order_code = ?;
        """, (new_note, order_code))

        conn.commit()
        conn.close()

        return {
            "success": True,
            "order_code": order_code,
            "order_status": "Đã hủy",
            "message": "Đã hủy đơn hàng và giải phóng lượng hàng giữ chỗ thành công."
        }
