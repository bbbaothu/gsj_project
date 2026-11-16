"""
TDD Test Suite cho Giai đoạn 1: Kiểm thử Schema SQLite mở rộng (V2) và Dữ liệu giả lập cho Module 2-6.
"""
import os
import sqlite3
import unittest

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "retail_dienmay.db"))


class TestSchemaAndSeedV2(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.row_factory = sqlite3.Row

    def tearDown(self):
        self.conn.close()

    def test_new_tables_exist_and_seeded(self):
        """
        Kiểm tra 6 bảng nghiệp vụ mới cho Module 2-6 đều tồn tại và đã được seed dữ liệu hợp lệ.
        """
        required_tables = [
            "SYS_ALERT_SNOOZE_LOG",
            "EXT_MARKET_PRICES",
            "FACT_CLEARANCE_CAMPAIGNS",
            "SYS_CRM_INTERACTION_LOG",
            "FACT_SERVICE_APPOINTMENTS",
            "FACT_COMMISSION_LEDGER",
        ]
        cur = self.conn.cursor()
        for tbl in required_tables:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (tbl,))
            self.assertIsNotNone(cur.fetchone(), f"Thiếu bảng nghiệp vụ mới: {tbl}")

        cur.execute("SELECT COUNT(*) AS cnt FROM EXT_MARKET_PRICES;")
        self.assertGreaterEqual(cur.fetchone()["cnt"], 12, "EXT_MARKET_PRICES phải có tối thiểu 12 bản ghi giá đối thủ")

        cur.execute("SELECT COUNT(*) AS cnt FROM FACT_CLEARANCE_CAMPAIGNS;")
        self.assertGreaterEqual(cur.fetchone()["cnt"], 2, "FACT_CLEARANCE_CAMPAIGNS phải có >= 2 chiến dịch mẫu")

        cur.execute("SELECT COUNT(*) AS cnt FROM SYS_CRM_INTERACTION_LOG;")
        self.assertGreaterEqual(cur.fetchone()["cnt"], 5, "SYS_CRM_INTERACTION_LOG phải có dữ liệu tương tác CSKH")

        cur.execute("SELECT COUNT(*) AS cnt FROM FACT_SERVICE_APPOINTMENTS;")
        self.assertGreaterEqual(cur.fetchone()["cnt"], 3, "FACT_SERVICE_APPOINTMENTS phải có lịch hẹn kỹ thuật")

        cur.execute("SELECT COUNT(*) AS cnt FROM FACT_COMMISSION_LEDGER;")
        self.assertEqual(cur.fetchone()["cnt"], 3, "FACT_COMMISSION_LEDGER phải có sổ hoa hồng cho 3 nhân sự")

        cur.execute("SELECT COUNT(*) AS cnt FROM DIM_EMPLOYEES WHERE is_active = 1;")
        self.assertEqual(cur.fetchone()["cnt"], 3, "DIM_EMPLOYEES phải có đủ NV0001, NV0002, NV0003")

    def test_product_extended_columns(self):
        """
        Kiểm tra các cột quản trị kho nâng cao trên bảng DIM_PRODUCTS phục vụ Module 2, 3, 4.
        """
        cur = self.conn.cursor()
        cur.execute("""
            SELECT product_code, lead_time_days, moq, pack_size, seasonality, lifecycle_status, map_price
            FROM DIM_PRODUCTS
            WHERE product_code = 'TV-LG-55C3';
        """)
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertGreater(row["lead_time_days"], 0)
        self.assertGreaterEqual(row["moq"], 1)
        self.assertGreaterEqual(row["pack_size"], 1)
        self.assertIn(row["seasonality"], ("SUMMER", "WINTER", "YEAR_ROUND"))
        self.assertIn(row["lifecycle_status"], ("ACTIVE", "EOL"))
        self.assertGreater(row["map_price"], 0)


if __name__ == "__main__":
    unittest.main()
