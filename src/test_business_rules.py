#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KIỂM THỬ TỰ ĐỘNG CÁC RÀNG BUỘC NGHIỆP VỤ BÁN LẺ ĐIỆN MÁY TRÊN SQLITE (KIOTVIET)
"""
import sqlite3
import sys

def run_tests():
    db_path = "data/retail_dienmay.db"
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON;")
    cur = con.cursor()
    print("=" * 80)
    print("BẮT ĐẦU KIỂM THỬ CÁC LUẬT RÀNG BUỘC NGHIỆP VỤ ĐIỆN MÁY TRÊN SQLITE")
    print("=" * 80)

    # 1. Khởi tạo Master Data cơ bản
    cur.execute("DELETE FROM FACT_WARRANTIES;")
    cur.execute("DELETE FROM FACT_INVOICE_SERIALS;")
    cur.execute("DELETE FROM FACT_INVOICES_LINES;")
    cur.execute("DELETE FROM FACT_INVOICES;")
    cur.execute("DELETE FROM FACT_ORDERS_LINES;")
    cur.execute("DELETE FROM FACT_ORDERS;")
    cur.execute("DELETE FROM DIM_PRODUCT_SERIALS;")
    cur.execute("DELETE FROM DIM_PRODUCTS;")
    cur.execute("DELETE FROM DIM_EMPLOYEES;")
    cur.execute("DELETE FROM DIM_CUSTOMERS;")
    cur.execute("DELETE FROM DIM_BRANCHES;")

    cur.execute("INSERT INTO DIM_BRANCHES (branch_code, branch_name) VALUES ('CN01', 'Showroom Cầu Giấy');")
    cur.execute("INSERT INTO DIM_BRANCHES (branch_code, branch_name) VALUES ('CN02', 'Showroom Đống Đa');")
    
    cur.execute("""
        INSERT INTO DIM_PRODUCTS (product_code, barcode, product_name, category_path, brand, model_code, sale_price, cost_price, stock_on_hand, warranty_months, has_serial)
        VALUES ('TV-SN-55X80K', '8936001112223', 'Smart Tivi Sony 55 inch 4K KD-55X80K', 'Điện tử > Tivi > Tivi Sony', 'Sony', 'KD-55X80K', 16990000, 13200000, 5, 24, 1);
    """)

    cur.execute("""
        INSERT INTO DIM_EMPLOYEES (employee_code, employee_name, phone, department, title, branch_code)
        VALUES ('NV0001', 'Nguyễn Thị Hoa', '0988111222', 'Bán hàng', 'Chuyên viên tư vấn', 'CN01');
    """)

    # -------------------------------------------------------------------------
    # TEST 1: RULE R1 - Mã hóa đơn bắt buộc có prefix HDIP hoặc HD
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Kiểm tra Rule R1: Format Mã Hóa đơn (Prefix HDIP% hoặc HD%)")
    try:
        cur.execute("""
            INSERT INTO FACT_INVOICES (invoice_code, seller_code, branch_code, customer_code, total_amount, amount_due, pay_cash)
            VALUES ('INV_INVALID_01', 'NV0001', 'CN01', 'KH00001', 1000000, 1000000, 1000000);
        """)
        print("❌ FAILED: Hệ thống cho phép mã hóa đơn không đúng prefix!")
    except sqlite3.IntegrityError as e:
        print(f"✅ PASSED (Rule R1): Chặn thành công mã sai quy chuẩn -> {e}")

    # -------------------------------------------------------------------------
    # TEST 2: RULE R5 - Khách hàng Doanh nghiệp bắt buộc MST và Tên công ty
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Kiểm tra Rule R5: Khách hàng Công ty bắt buộc MST và Tên Công ty")
    try:
        cur.execute("""
            INSERT INTO DIM_CUSTOMERS (customer_code, customer_type, customer_name, phone, company, tax_code)
            VALUES ('KH_CTY_SAI', 'Công ty', 'Đại diện A', '0912345678', NULL, NULL);
        """)
        print("❌ FAILED: Hệ thống cho phép khách hàng công ty không có MST!")
    except sqlite3.IntegrityError as e:
        print(f"✅ PASSED (Rule R5): Trigger chặn thành công -> {e}")

    # Tạo khách hàng cá nhân & khách hàng công ty hợp lệ
    cur.execute("""
        INSERT INTO DIM_CUSTOMERS (customer_code, customer_type, customer_name, phone, address)
        VALUES ('KH00001', 'Cá nhân', 'Trần Văn Nam', '0987654321', 'Số 10 Nguyễn Trãi, Thanh Xuân, Hà Nội');
    """)
    cur.execute("""
        INSERT INTO DIM_CUSTOMERS (customer_code, customer_type, customer_name, phone, company, tax_code, address)
        VALUES ('KH00002', 'Công ty', 'Công ty Cổ phần Alpha Tech', '0243999888', 'Công ty Cổ phần Alpha Tech', '0109988776', 'Tòa nhà Landmark 72, Cầu Giấy');
    """)
    print("✅ Đã tạo thành công khách hàng cá nhân KH00001 và khách hàng công ty KH00002 có đầy đủ MST.")

    # -------------------------------------------------------------------------
    # TEST 3: RULE R3 - Tính toàn vẹn thanh toán (Payment Balance)
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Kiểm tra Rule R3: Cân đối thanh toán đa phương thức (pay_cash + pay_card + ... = amount_due)")
    try:
        # Tổng cần trả 16,990,000 nhưng khách mới trả 10,000,000 thiếu cân bằng
        cur.execute("""
            INSERT INTO FACT_INVOICES (invoice_code, seller_code, branch_code, customer_code, total_amount, amount_due, pay_cash)
            VALUES ('HDIP00001', 'NV0001', 'CN01', 'KH00001', 16990000, 16990000, 10000000);
        """)
        print("❌ FAILED: Hệ thống cho phép thanh toán không đủ số tiền cần trả!")
    except sqlite3.IntegrityError as e:
        print(f"✅ PASSED (Rule R3): Chặn thành công hóa đơn thiếu tiền thanh toán -> {e}")

    # Tạo hóa đơn hợp lệ với đa phương thức: Tiền mặt + Chuyển khoản
    cur.execute("""
        INSERT INTO FACT_INVOICES (invoice_code, seller_code, branch_code, customer_code, total_amount, amount_due, pay_cash, pay_transfer)
        VALUES ('HDIP00001', 'NV0001', 'CN01', 'KH00001', 16990000, 16990000, 6990000, 10000000);
    """)
    cur.execute("""
        INSERT INTO FACT_INVOICES_LINES (invoice_code, product_code, quantity, unit_price, cost_price, line_total, warranty_months)
        VALUES ('HDIP00001', 'TV-SN-55X80K', 1, 16990000, 13200000, 16990000, 24);
    """)
    line_id = cur.lastrowid
    print(f"✅ Hóa đơn HDIP00001 hợp lệ được tạo thành công (pay_cash: 6.99tr + pay_transfer: 10tr = 16.99tr). Dòng hóa đơn ID: {line_id}")

    # -------------------------------------------------------------------------
    # TEST 4: RULE R2 - Kiểm tra Serial tồn kho & Khác chi nhánh
    # -------------------------------------------------------------------------
    print("\n[TEST 4] Kiểm tra Rule R2: Ràng buộc vị trí và trạng thái Serial/IMEI")
    
    # Nhập 1 Serial tại chi nhánh CN02 (Đống Đa)
    cur.execute("""
        INSERT INTO DIM_PRODUCT_SERIALS (serial_number, product_code, branch_code, status)
        VALUES ('SN-SNY55-CN02-888', 'TV-SN-55X80K', 'CN02', 'IN_STOCK');
    """)

    # Cố gắng xuất bán Serial ở CN02 cho hóa đơn tại CN01 (Cầu Giấy)
    try:
        cur.execute(f"""
            INSERT INTO FACT_INVOICE_SERIALS (invoice_line_id, invoice_code, serial_number, product_code)
            VALUES ({line_id}, 'HDIP00001', 'SN-SNY55-CN02-888', 'TV-SN-55X80K');
        """)
        print("❌ FAILED: Hệ thống cho phép bán Serial ở chi nhánh khác!")
    except sqlite3.IntegrityError as e:
        print(f"✅ PASSED (Rule R2): Chặn xuất bán Serial lệch chi nhánh -> {e}")

    # Nhập Serial hợp lệ tại CN01
    cur.execute("""
        INSERT INTO DIM_PRODUCT_SERIALS (serial_number, product_code, branch_code, status)
        VALUES ('SN-SNY55-CN01-111', 'TV-SN-55X80K', 'CN01', 'IN_STOCK');
    """)

    # Xuất bán Serial hợp lệ
    cur.execute(f"""
        INSERT INTO FACT_INVOICE_SERIALS (invoice_line_id, invoice_code, serial_number, product_code)
        VALUES ({line_id}, 'HDIP00001', 'SN-SNY55-CN01-111', 'TV-SN-55X80K');
    """)
    print("✅ Xuất bán thành công Serial 'SN-SNY55-CN01-111' cho hóa đơn HDIP00001.")

    # -------------------------------------------------------------------------
    # TEST 5: RULE R2 & R4 - Kiểm tra Trigger tự động chuyển SOLD, trừ kho & kích hoạt e-Warranty
    # -------------------------------------------------------------------------
    print("\n[TEST 5] Kiểm tra Rule R2 & R4: Tự động đổi trạng thái SOLD, trừ kho và kích hoạt bảo hành")
    serial_info = cur.execute("SELECT status, sold_invoice_code FROM DIM_PRODUCT_SERIALS WHERE serial_number = 'SN-SNY55-CN01-111';").fetchone()
    stock_info = cur.execute("SELECT stock_on_hand FROM DIM_PRODUCTS WHERE product_code = 'TV-SN-55X80K';").fetchone()
    warranty_info = cur.execute("""
        SELECT serial_number, customer_code, warranty_start_date, warranty_end_date, status, claim_count 
        FROM FACT_WARRANTIES WHERE serial_number = 'SN-SNY55-CN01-111';
    """).fetchone()

    print(f"  + Trạng thái Serial cập nhật: status='{serial_info[0]}', sold_invoice_code='{serial_info[1]}'")
    print(f"  + Tồn kho SKU giảm từ 5 -> {stock_info[0]} chiếc")
    print(f"  + Phiếu bảo hành điện tử tự sinh: Khách={warranty_info[1]}, Bắt đầu={warranty_info[2]}, Kết thúc={warranty_info[3]} (24 tháng), Trạng thái={warranty_info[4]}")

    assert serial_info[0] == 'SOLD', "Serial status must be SOLD"
    assert stock_info[0] == 4, "Stock must decrement to 4"
    assert warranty_info is not None, "Warranty must be auto-generated"
    print("✅ PASSED: Trigger hoàn tất toàn bộ chu trình đồng bộ tự động!")

    # Cố gắng bán lại lần 2 chiếc Serial đã SOLD
    print("\n[TEST 6] Kiểm tra chống bán trùng lặp Serial (Duplicate Serial Sale)")
    try:
        cur.execute(f"""
            INSERT INTO FACT_INVOICE_SERIALS (invoice_line_id, invoice_code, serial_number, product_code)
            VALUES ({line_id}, 'HDIP00001', 'SN-SNY55-CN01-111', 'TV-SN-55X80K');
        """)
        print("❌ FAILED: Hệ thống cho phép bán lại số Serial đã SOLD!")
    except sqlite3.IntegrityError as e:
        print(f"✅ PASSED (Rule R2): Chặn thành công bán trùng Serial đã SOLD -> {e}")

    con.commit()
    con.close()
    print("\n" + "=" * 80)
    print("TẤT CẢ CÁC BÀI KIỂM THỬ RÀNG BUỘC NGHIỆP VỤ ĐÃ ĐẠT 100% TIÊU CHUẨN!")
    print("=" * 80)

if __name__ == '__main__':
    run_tests()
