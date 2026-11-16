#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE TẠO DỮ LIỆU GIẢ LẬP (SYNTHETIC DATA) CHO HỘ KINH DOANH CÁ THỂ (SOLE TRADER) ĐIỆN MÁY
Đặc thù:
1. 1 chi nhánh duy nhất (Cửa hàng Điện máy Anh Tâm).
2. 1 người duy nhất vận hành (Nguyễn Anh Tâm - Chủ tiệm kiêm Bán hàng, Kỹ thuật, Thu ngân, Quản lý).
3. Lượng nhập hàng dựa nhiều theo cảm tính (Gut-feeling inventory bias: Overstock hàng kén khách, Stockout hàng bình dân bán chạy).
"""

import os
import sys
import random
import sqlite3
import datetime
import numpy as np
import pandas as pd

from sdv.metadata import SingleTableMetadata
from sdv.single_table import GaussianCopulaSynthesizer

DB_PATH = "data/retail_dienmay.db"
SCHEMA_PATH = "src/schema_dienmay_kiotviet.sql"

def init_database():
    print(">>> [1/5] Khởi tạo cấu trúc CSDL từ schema_dienmay_kiotviet.sql...")
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON;")
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = f.read()
    con.executescript(schema)
    con.close()
    print("    Hoàn tất khởi tạo CSDL với 11 bảng, 3 view và 4 triggers.")

def insert_master_data():
    print(">>> [2/5] Tạo Master Data cho Cửa hàng Sole Trader (1 chi nhánh, 1 người vận hành)...")
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON;")
    cur = con.cursor()

    # 1. DUY NHẤT 1 CHI NHÁNH
    branches = [
        ('CN01', 'Cửa hàng Điện máy Anh Tâm', '0912345678', '108 Cầu Giấy', 'Quan Hoa', 'Cầu Giấy', 'Hà Nội', 1),
    ]
    cur.executemany("""
        INSERT INTO DIM_BRANCHES (branch_code, branch_name, phone, address, ward, district, province, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, branches)

    # 2. ĐỘI NGŨ VẬN HÀNH (Chủ cửa hàng & 2 Kỹ thuật viên phụ trợ)
    employees = [
        ('NV0001', 'Nguyễn Anh Tâm', '0912345678', 'Chủ cửa hàng & Vận hành', 'Chủ hộ kinh doanh (Kiêm Bán hàng & Kỹ thuật)', 'anhtam', 'CN01', 25000000, '2020-05-01'),
        ('NV0002', 'Trần Đình Khang', '0913456789', 'Kỹ thuật - Lắp đặt', 'Kỹ thuật viên', 'khangtd', 'CN01', 12000000, '2023-03-15'),
        ('NV0003', 'Nguyễn Tuấn Long', '0914567890', 'Kỹ thuật - Lắp đặt', 'Kỹ thuật trưởng', 'longnt', 'CN01', 15000000, '2022-01-10'),
    ]
    cur.executemany("""
        INSERT INTO DIM_EMPLOYEES (employee_code, employee_name, phone, department, title, login_account, branch_code, salary, hire_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, employees)

    # 3. DANH MỤC SẢN PHẨM & MỨC TỒN KHO CẢM TÍNH (GUT-FEELING STOCKING)
    # Đặc thù cảm tính:
    # - Hàng chủ tiệm thích/nghe sale hãng dụ: Nhập ồ ạt 25-40 cái (dù giá cao, khách quanh khu ít mua) -> Ứ đọng vốn
    # - Hàng bình dân thị trường chuộng: Chủ tiệm nhập dè dặt 2-4 cái -> Thường xuyên cháy hàng (OOS)
    products = [
        # Nhóm 1: Tivi
        # TV-SN-55X80K: Dòng vừa tiền, nhập vừa phải (12 cái)
        ('TV-SN-55X80K', '893600100001', 'Smart Tivi Sony 4K 55 inch KD-55X80K', 'Hàng hóa', 'Điện tử > Tivi > Tivi Sony', 'Sony', 'KD-55X80K', 'Cái', 18500, 16490000, 13200000, 12, 3, 20, 24, 1, 1, 1, '{"screen": "55 inch", "resolution": "4K"}'),
        # TV-LG-55C3: OLED cao cấp 28 triệu -> Chủ tiệm mê công nghệ OLED nên nhập hẳn 28 cái theo cảm tính!
        ('TV-LG-55C3', '893600100005', 'Smart Tivi OLED LG 4K 55 inch 55C3PSA', 'Hàng hóa', 'Điện tử > Tivi > Tivi LG', 'LG', '55C3PSA', 'Cái', 19000, 27990000, 22500000, 28, 2, 10, 24, 1, 1, 1, '{"screen": "55 inch", "panel": "OLED"}'),
        # TV-CS-43FG6: Tivi Casper 6 triệu khách bình dân hỏi mua liên tục -> Chủ tiệm chê lãi ít nhập có 3 cái!
        ('TV-CS-43FG6', '893600100006', 'Smart Tivi Casper 43 inch Full HD 43FG610', 'Hàng hóa', 'Điện tử > Tivi > Tivi Casper', 'Casper', '43FG610', 'Cái', 11000, 5990000, 4600000, 3, 5, 20, 24, 1, 1, 1, '{"screen": "43 inch", "resolution": "Full HD"}'),
        # TV-SS-55AU7: Samsung phổ thông
        ('TV-SS-55AU7', '893600100003', 'Smart Tivi Samsung 4K 55 inch 55AU7002', 'Hàng hóa', 'Điện tử > Tivi > Tivi Samsung', 'Samsung', '55AU7002', 'Cái', 17000, 11490000, 8900000, 10, 3, 15, 24, 1, 1, 1, '{"screen": "55 inch", "resolution": "4K"}'),

        # Nhóm 2: Điều hòa
        # ML-DK-FTKB25: Daikin 1HP chuẩn khách tin dùng
        ('ML-DK-FTKB25', '893600200001', 'Điều hòa Daikin Inverter 1 HP FTKB25WAVMV', 'Hàng hóa', 'Điện lạnh > Điều hòa > Điều hòa Daikin', 'Daikin', 'FTKB25WAVMV', 'Bộ', 32000, 10990000, 8600000, 15, 4, 25, 12, 1, 1, 1, '{"capacity": "1 HP", "inverter": true}'),
        # ML-PN-XPU12: Panasonic 1.5HP giá 14 triệu -> Được sale hãng hứa tặng chuyến du lịch nên nhập ôm 30 bộ!
        ('ML-PN-XPU12', '893600200004', 'Điều hòa Panasonic Inverter 1.5 HP CU/CS-XPU12XKH-8', 'Hàng hóa', 'Điện lạnh > Điều hòa > Điều hòa Panasonic', 'Panasonic', 'CU/CS-XPU12XKH-8', 'Bộ', 35000, 13990000, 11000000, 30, 4, 15, 12, 1, 1, 1, '{"capacity": "1.5 HP", "inverter": true}'),
        # ML-CS-TC09: Casper 1HP giá rẻ sinh viên/người thuê trọ hỏi mua rất nhiều -> Chủ tiệm chỉ nhập 4 bộ
        ('ML-CS-TC09', '893600200005', 'Điều hòa Casper Inverter 1 HP TC-09IS35', 'Hàng hóa', 'Điện lạnh > Điều hòa > Điều hòa Casper', 'Casper', 'TC-09IS35', 'Bộ', 28000, 6490000, 5100000, 4, 6, 25, 36, 1, 1, 1, '{"capacity": "1 HP", "inverter": true}'),

        # Nhóm 3: Tủ lạnh
        # TL-SS-647L: Tủ lạnh Side by Side to đùng 19 triệu -> Nhập 18 chiếc chật kín showroom
        ('TL-SS-647L', '893600300002', 'Tủ lạnh Samsung Side by Side 647 lít RS62R5001M9', 'Hàng hóa', 'Điện lạnh > Tủ lạnh > Tủ lạnh Samsung', 'Samsung', 'RS62R5001M9', 'Cái', 110000, 18990000, 14900000, 18, 2, 8, 24, 1, 1, 1, '{"volume": "647 L", "side_by_side": true}'),
        # TL-PN-322L: Ngăn đông dưới vừa tiền
        ('TL-PN-322L', '893600300001', 'Tủ lạnh Panasonic Inverter 322 lít NR-BC360QKVN', 'Hàng hóa', 'Điện lạnh > Tủ lạnh > Tủ lạnh Panasonic', 'Panasonic', 'NR-BC360QKVN', 'Cái', 65000, 13490000, 10600000, 8, 3, 12, 24, 1, 1, 1, '{"volume": "322 L", "inverter": true}'),
        # TL-AQ-180L: Aqua 180L giá rẻ bán chạy nhất khu dân cư -> Nhập có 3 cái!
        ('TL-AQ-180L', '893600300004', 'Tủ lạnh Aqua 180 lít AQR-T220FA(FB)', 'Hàng hóa', 'Điện lạnh > Tủ lạnh > Tủ lạnh Aqua', 'Aqua', 'AQR-T220FA', 'Cái', 42000, 4890000, 3800000, 3, 5, 20, 24, 1, 1, 1, '{"volume": "180 L"}'),

        # Nhóm 4: Máy giặt
        ('MG-LG-FV1409', '893600400001', 'Máy giặt LG AI DD Inverter 9 kg FV1409S4W', 'Hàng hóa', 'Điện lạnh > Máy giặt > Máy giặt LG', 'LG', 'FV1409S4W', 'Cái', 70000, 9490000, 7400000, 10, 3, 15, 24, 1, 1, 1, '{"load": "9 kg"}'),
        ('MG-TB-85K', '893600400003', 'Máy giặt Toshiba 8.5 kg AW-K905DV(SG)', 'Hàng hóa', 'Điện lạnh > Máy giặt > Máy giặt Toshiba', 'Toshiba', 'AW-K905DV', 'Cái', 45000, 4790000, 3700000, 5, 4, 15, 24, 1, 1, 1, '{"load": "8.5 kg"}'),

        # Nhóm 5: Dịch vụ & Phụ kiện (Do chính chủ tiệm đi lắp ráp)
        ('DV-LAPDAT-ML', '893600900001', 'Gói công thợ lắp đặt điều hòa tiêu chuẩn', 'Dịch vụ', 'Dịch vụ > Lắp đặt > Lắp đặt điều hòa', 'Anh Tâm', 'DV-AC', 'Lần', 0, 350000, 50000, 999, 0, 9999, 3, 0, 1, 1, '{"owner_install": true}'),
        ('DV-TREO-TV', '893600900002', 'Gói công thợ lắp đặt giá treo Tivi tận nhà', 'Dịch vụ', 'Dịch vụ > Lắp đặt > Lắp đặt Tivi', 'Anh Tâm', 'DV-TV', 'Lần', 0, 200000, 30000, 999, 0, 9999, 3, 0, 1, 1, '{"owner_install": true}'),
        ('PK-GIATREO-55', '893600900003', 'Giá treo Tivi nghiêng cao cấp 43-65 inch', 'Hàng hóa', 'Phụ kiện > Giá treo > Giá treo Tivi', 'Vogel', 'GT-4365', 'Cái', 2500, 390000, 190000, 40, 10, 60, 12, 0, 1, 1, '{"support": "43-65 inch"}'),
        ('PK-ONGDONG-M', '893600900004', 'Ống đồng Thái Lan Toàn Phát bọc bảo ôn (mét)', 'Hàng hóa', 'Vật tư > Ống đồng > Ống đồng điều hòa', 'Toàn Phát', 'OD-610', 'Mét', 300, 180000, 110000, 150, 30, 300, 0, 0, 1, 1, '{"origin": "Thailand"}'),
    ]
    cur.executemany("""
        INSERT INTO DIM_PRODUCTS (product_code, barcode, product_name, product_type, category_path, brand, model_code, uom, weight_gram, sale_price, cost_price, stock_on_hand, min_stock, max_stock, warranty_months, has_serial, is_direct_sale, is_active, specifications)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, products)

    con.commit()
    con.close()
    print("    Hoàn tất tạo Master Data (1 Chi nhánh, 1 Người vận hành, 16 Sản phẩm phân phối tồn kho cảm tính).")

def generate_customers_with_sdv(num_customers=45):
    print(f">>> [3/5] Sử dụng SDV để sinh phân phối {num_customers} Khách hàng quen quanh khu vực...")
    # Cửa hàng cá thể: 90% khách cá nhân trong bán kính 3-5km, 10% quán cafe/tiểu thương gần đó
    seed_customers = pd.DataFrame({
        'is_corporate': [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        'age': [32, 45, 50, 28, 38, 42, 55, 60, 40, 35],
        'debt_ratio': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.0]
    })

    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(seed_customers)
    synth = GaussianCopulaSynthesizer(metadata)
    synth.fit(seed_customers)
    samples = synth.sample(num_rows=num_customers)

    ho_viet = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Phan', 'Vũ', 'Đặng', 'Bùi', 'Đỗ']
    dem_viet = ['Văn', 'Thị', 'Đức', 'Quang', 'Hải', 'Thanh', 'Hữu', 'Ngọc', 'Minh']
    ten_viet = ['An', 'Bình', 'Cường', 'Dũng', 'Hương', 'Huy', 'Khoa', 'Linh', 'Long', 'Nam', 'Nhi', 'Phúc', 'Quân', 'Sơn', 'Tú', 'Trang']

    streets = ['Cầu Giấy', 'Quan Hoa', 'Dịch Vọng', 'Trần Thái Tông', 'Xuân Thủy', 'Nguyễn Khánh Toàn', 'Nguyễn Phong Sắc', 'Chùa Hà']
    wards = ['Quan Hoa', 'Dịch Vọng', 'Dịch Vọng Hậu', 'Nghĩa Tân', 'Nghĩa Đô']

    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON;")
    cur = con.cursor()

    cust_records = []
    for idx, row in samples.iterrows():
        c_code = f"KH{idx+1:05d}"
        is_corp = row['is_corporate'] > 0.8
        phone = f"09{random.randint(10000000, 99999999)}"
        street = random.choice(streets)
        ward = random.choice(wards)
        address = f"Số {random.randint(12, 180)} {street}"

        if is_corp:
            c_type = 'Công ty'
            company = f"Công ty TNHH Dịch Vụ & Thương Mại {random.choice(ten_viet)} Phát"
            c_name = f"{company} (Đại diện: {random.choice(ho_viet)} {random.choice(ten_viet)})"
            tax_code = f"01{random.randint(10000000, 99999999)}"
            email = f"ketoan@{c_code.lower()}.vn"
            birth_date = None
            gender = None
            debt = 0.0
        else:
            c_type = 'Cá nhân'
            c_name = f"{random.choice(ho_viet)} {random.choice(dem_viet)} {random.choice(ten_viet)}"
            company = None
            tax_code = None
            email = f"{c_code.lower()}@gmail.com"
            age = int(np.clip(row['age'], 22, 68))
            birth_date = f"{2026 - age}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            gender = random.choice(['Nam', 'Nữ'])
            debt = 0.0

        cust_records.append((
            c_code, c_type, c_name, phone, email, birth_date, gender,
            address, 'Cầu Giấy', ward, company, tax_code, debt, 1
        ))

    cur.executemany("""
        INSERT INTO DIM_CUSTOMERS (
            customer_code, customer_type, customer_name, phone, email, birth_date, gender,
            address, area, ward, company, tax_code, current_debt, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, cust_records)

    con.commit()
    con.close()
    print(f"    Đã sinh {len(cust_records)} khách hàng quen thuộc địa bàn Cầu Giấy.")

def generate_serials_and_invoices_with_sdv(num_invoices=75):
    print(f">>> [4/5] Sử dụng SDV để sinh {num_invoices} Hóa đơn bán lẻ (Do 1 chủ tiệm Anh Tâm phục vụ)...")
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON;")
    cur = con.cursor()

    # 1. Sinh danh sách Serial theo đúng số lượng tồn kho cảm tính ban đầu
    cur.execute("SELECT product_code, brand, model_code, stock_on_hand FROM DIM_PRODUCTS WHERE has_serial = 1;")
    prods = cur.fetchall()

    serial_records = []
    serial_counter = 1001

    for prod in prods:
        p_code, brand, model, initial_stock = prod
        # Sinh đúng bằng lượng nhập ban đầu của chủ tiệm
        for _ in range(initial_stock):
            sn = f"SN-{brand[:3].upper()}-{model.replace('/', '').replace(' ', '')}-{serial_counter}"
            serial_records.append((sn, p_code, 'CN01', 'IN_STOCK', '2026-08-01 08:30:00', None))
            serial_counter += 1

    cur.executemany("""
        INSERT INTO DIM_PRODUCT_SERIALS (serial_number, product_code, branch_code, status, import_date, sold_invoice_code)
        VALUES (?, ?, ?, ?, ?, ?);
    """, serial_records)
    con.commit()
    print(f"    - Đã nạp {len(serial_records)} số Serial vào kho CN01 phản ánh tồn kho cảm tính.")

    # 2. Sử dụng SDV để học phân phối giờ bán hàng và giá trị hóa đơn của Sole Trader
    seed_orders = pd.DataFrame({
        'hour': [8, 9, 10, 11, 14, 15, 17, 18, 19, 20],
        'discount_ratio': [0.0, 0.02, 0.0, 0.05, 0.0, 0.03, 0.0, 0.05, 0.0, 0.0], # Cửa hàng tư nhân ít chiết khấu sâu
        'payment_mode': ['Tiền mặt', 'Chuyển khoản', 'Chuyển khoản', 'Tiền mặt', 'Chuyển khoản', 'Chuyển khoản', 'Tiền mặt', 'Chuyển khoản', 'Tiền mặt', 'Chuyển khoản']
    })

    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(seed_orders)
    synth = GaussianCopulaSynthesizer(metadata)
    synth.fit(seed_orders)
    sampled_orders = synth.sample(num_rows=num_invoices)

    cur.execute("SELECT customer_code FROM DIM_CUSTOMERS;")
    cust_codes = [r[0] for r in cur.fetchall()]

    cur.execute("SELECT product_code, sale_price, cost_price, warranty_months, has_serial FROM DIM_PRODUCTS;")
    product_dict = {r[0]: {'sale_price': r[1], 'cost_price': r[2], 'warranty': r[3], 'has_serial': r[4]} for r in cur.fetchall()}

    # Phân loại xác suất nhu cầu thực tế của khách hàng (Market Demand Reality):
    # Khách chuộng: Casper, Daikin 1HP, Aqua 180L, Sony 55 inch
    # Khách ít mua: LG OLED 28tr, Samsung Side-by-side 19tr, Panasonic 14tr
    high_demand_skus = ['TV-CS-43FG6', 'ML-CS-TC09', 'TL-AQ-180L', 'ML-DK-FTKB25', 'TV-SN-55X80K', 'MG-TB-85K']
    low_demand_skus = ['TV-LG-55C3', 'TL-SS-647L', 'ML-PN-XPU12', 'TV-SS-65Q60B']

    start_date = datetime.date(2026, 7, 20)
    end_date = datetime.date(2026, 10, 12)
    day_range = (end_date - start_date).days

    invoice_count = 0

    for idx, row in sampled_orders.iterrows():
        inv_code = f"HDIP{idx+1:06d}"
        random_day = start_date + datetime.timedelta(days=random.randint(0, day_range))
        hour = int(np.clip(row['hour'], 8, 20))
        inv_time = f"{random_day} {hour:02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"

        cust_code = random.choice(cust_codes)

        # Quyết định mặt hàng bán: 80% chọn hàng nhu cầu cao, 20% hàng cao cấp
        if random.random() < 0.8:
            candidate_skus = [s for s in high_demand_skus if s in product_dict]
        else:
            candidate_skus = [s for s in low_demand_skus if s in product_dict]

        chosen_sku = random.choice(candidate_skus)

        # Kiểm tra xem Serial còn tồn kho không!
        cur.execute("""
            SELECT serial_number FROM DIM_PRODUCT_SERIALS
            WHERE product_code = ? AND branch_code = 'CN01' AND status = 'IN_STOCK'
            LIMIT 1;
        """, (chosen_sku,))
        ser_row = cur.fetchone()

        # Nếu hàng đã hết sạch trong kho (Stockout do nhập cảm tính quá ít) -> Bỏ qua giao dịch này (Khách hỏi nhưng không có máy bán)
        if not ser_row:
            continue

        serial_num = ser_row[0]
        p_info = product_dict[chosen_sku]

        lines_to_insert = [{
            'product_code': chosen_sku,
            'qty': 1,
            'unit_price': p_info['sale_price'],
            'cost_price': p_info['cost_price'],
            'line_total': p_info['sale_price'],
            'warranty': p_info['warranty'],
            'has_serial': 1,
            'serial_num': serial_num
        }]
        total_inv_amount = p_info['sale_price']

        # Kèm công thợ lắp đặt hoặc giá treo do Anh Tâm trực tiếp làm
        if 'ML-' in chosen_sku:
            pk = 'DV-LAPDAT-ML'
            pk_info = product_dict[pk]
            lines_to_insert.append({
                'product_code': pk,
                'qty': 1,
                'unit_price': pk_info['sale_price'],
                'cost_price': pk_info['cost_price'],
                'line_total': pk_info['sale_price'],
                'warranty': pk_info['warranty'],
                'has_serial': 0,
                'serial_num': None
            })
            total_inv_amount += pk_info['sale_price']
        elif 'TV-' in chosen_sku and random.random() < 0.6:
            pk = 'PK-GIATREO-55'
            pk_info = product_dict[pk]
            lines_to_insert.append({
                'product_code': pk,
                'qty': 1,
                'unit_price': pk_info['sale_price'],
                'cost_price': pk_info['cost_price'],
                'line_total': pk_info['sale_price'],
                'warranty': pk_info['warranty'],
                'has_serial': 0,
                'serial_num': None
            })
            total_inv_amount += pk_info['sale_price']

        disc_ratio = float(np.clip(row['discount_ratio'], 0.0, 0.05))
        inv_discount = round(total_inv_amount * disc_ratio, -4)
        amount_due = total_inv_amount - inv_discount

        # Thanh toán hộ cá thể: Tiền mặt hoặc Chuyển khoản VietQR
        mode = row['payment_mode']
        if mode == 'Tiền mặt':
            pay_cash = amount_due
            pay_transfer = 0.0
        else:
            pay_cash = 0.0
            pay_transfer = amount_due

        channel = 'Bán trực tiếp' if random.random() < 0.85 else 'Điện thoại'

        # Insert FACT_INVOICES (Seller và Technician đều là NV0001 - Nguyễn Anh Tâm)
        cur.execute("""
            INSERT INTO FACT_INVOICES (
                invoice_code, invoice_time, seller_code, technician_code, branch_code, customer_code,
                sales_channel, pricebook, total_amount, invoice_discount_amount, amount_due,
                pay_cash, pay_card, pay_transfer, pay_installment, delivery_status, vat_invoice_issued, note
            ) VALUES (?, ?, 'NV0001', 'NV0001', 'CN01', ?, ?, 'Bảng giá chuẩn', ?, ?, ?, ?, 0.0, ?, 0.0, 'Đã lắp đặt hoàn tất', 0, 'Anh Tâm trực tiếp bàn giao & lắp đặt');
        """, (
            inv_code, inv_time, cust_code, channel, total_inv_amount, inv_discount, amount_due, pay_cash, pay_transfer
        ))

        for line in lines_to_insert:
            cur.execute("""
                INSERT INTO FACT_INVOICES_LINES (
                    invoice_code, product_code, quantity, unit_price, cost_price, line_total, warranty_months
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (
                inv_code, line['product_code'], line['qty'], line['unit_price'], line['cost_price'], line['line_total'], line['warranty']
            ))
            line_id = cur.lastrowid

            if line['has_serial'] == 1:
                cur.execute("""
                    INSERT INTO FACT_INVOICE_SERIALS (
                        invoice_line_id, invoice_code, serial_number, product_code
                    ) VALUES (?, ?, ?, ?);
                """, (line_id, inv_code, line['serial_num'], line['product_code']))

        invoice_count += 1

    con.commit()
    print(f"    - Đã lập thành công {invoice_count} hóa đơn thực tế do Nguyễn Anh Tâm trực tiếp phục vụ.")

    # Mô phỏng 2-3 ca bảo hành được chủ tiệm hỗ trợ tận nhà
    cur.execute("SELECT warranty_id, serial_number FROM FACT_WARRANTIES ORDER BY RANDOM() LIMIT 3;")
    claims = cur.fetchall()
    for c in claims:
        cur.execute("UPDATE FACT_WARRANTIES SET claim_count = 1, status = 'Đang xử lý sửa chữa' WHERE warranty_id = ?;", (c[0],))
        cur.execute("UPDATE DIM_PRODUCT_SERIALS SET status = 'WARRANTY_REPAIR' WHERE serial_number = ?;", (c[1],))

    con.commit()
    con.close()
    print("    Hoàn tất pipeline sinh dữ liệu Sole Trader.")

def generate_purchase_orders():
    print(">>> [4B/6] Tạo đơn nhập hàng từ Nhà cung cấp (PURCHASE_ORDERS & PO_ITEMS)...")
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON;")
    cur = con.cursor()

    today = datetime.date(2026, 11, 4)
    pos = [
        ('PO00001', '2026-11-02 09:30:00', 'NCC_CASPER', 'Công ty Cổ phần Casper Việt Nam', 'CN01', 
         15 * 5100000 + 10 * 4600000, 50000000, 15 * 5100000 + 10 * 4600000 - 50000000,
         str(today + datetime.timedelta(days=2)), 'Đang vận chuyển', 'Xe tải container số 29C-789.12 đang chuyển về kho Cầu Giấy'),
        ('PO00002', '2026-11-03 14:00:00', 'NCC_AQUA', 'Công ty TNHH Điện Máy Aqua Việt Nam', 'CN01',
         12 * 3800000, 45600000, 0,
         str(today + datetime.timedelta(days=1)), 'Đang vận chuyển', 'Giao hỏa tốc bổ sung kho Cầu Giấy'),
        ('PO00003', '2026-11-01 10:15:00', 'NCC_TOSHIBA', 'Toshiba Consumer Products Vietnam', 'CN01',
         10 * 3700000, 37000000, 0,
         str(today + datetime.timedelta(days=3)), 'Đang vận chuyển', 'Lô máy giặt nhập khẩu Thái Lan đang thông quan')
    ]

    cur.executemany("""
        INSERT INTO PURCHASE_ORDERS (purchase_code, order_time, vendor_code, vendor_name, branch_code, total_amount, amount_paid, amount_due, expected_delivery_date, status, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, pos)

    po_lines = [
        ('PO00001', 'ML-CS-TC09', 15, 5100000, 15 * 5100000),
        ('PO00001', 'TV-CS-43FG6', 10, 4600000, 10 * 4600000),
        ('PO00002', 'TL-AQ-180L', 12, 3800000, 12 * 3800000),
        ('PO00003', 'MG-TB-85K', 10, 3700000, 10 * 3700000),
    ]

    cur.executemany("""
        INSERT INTO PO_ITEMS (purchase_code, product_code, quantity, unit_price, line_total)
        VALUES (?, ?, ?, ?, ?);
    """, po_lines)

    con.commit()
    con.close()
    print("    Hoàn tất tạo 3 đơn nhập hàng (47 thiết bị đang trên đường về kho).")

def generate_orders_with_sdv(num_orders=35):
    print(f">>> [4C/6] Sinh {num_orders} Đơn đặt hàng & Giữ cọc (FACT_ORDERS & FACT_ORDERS_LINES)...")
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON;")
    cur = con.cursor()

    cur.execute("SELECT customer_code FROM DIM_CUSTOMERS;")
    cust_codes = [r[0] for r in cur.fetchall()]

    cur.execute("SELECT product_code, sale_price, stock_on_hand FROM DIM_PRODUCTS WHERE has_serial = 1;")
    prods = cur.fetchall()

    today = datetime.datetime(2026, 11, 4, 15, 30, 0)

    # 18 đơn Đã xác nhận (đã cọc hoặc trả đủ, chuẩn bị giao)
    # 10 đơn Chờ xử lý (6 đơn trả góp, 4 đơn cọc thông thường)
    # 4 đơn Chờ xử lý quá hạn 48h (Hold time violation)
    # 3 đơn Đã hủy (Khách hủy cọc / Hồ sơ trượt)
    orders_meta = []
    
    # 18 đơn Đã xác nhận (Tạo trong vòng 12-24h qua)
    for i in range(18):
        orders_meta.append({
            'status': 'Đã xác nhận',
            'hours_ago': random.uniform(2, 24),
            'type': random.choice(['Cọc COD', 'Trả đủ']),
            'is_expired': False
        })

    # 10 đơn Chờ xử lý (Tạo trong 4-30h qua, gồm 6 trả góp)
    for i in range(10):
        o_type = 'Trả góp' if i < 6 else 'Cọc giữ chỗ'
        orders_meta.append({
            'status': 'Chờ xử lý',
            'hours_ago': random.uniform(4, 30),
            'type': o_type,
            'is_expired': False
        })

    # 4 đơn Chờ xử lý QUÁ HẠN 48h (Tạo từ 55 - 96 giờ trước)
    for i in range(4):
        orders_meta.append({
            'status': 'Chờ xử lý',
            'hours_ago': random.uniform(55, 96),
            'type': random.choice(['Cọc giữ chỗ', 'Trả góp']),
            'is_expired': True
        })

    # 3 đơn Đã hủy
    for i in range(3):
        orders_meta.append({
            'status': 'Đã hủy',
            'hours_ago': random.uniform(72, 120),
            'type': 'Trả góp trượt',
            'is_expired': False
        })

    order_lines = []
    order_records = []

    for idx, meta in enumerate(orders_meta):
        order_code = f"DH{idx+1:05d}"
        order_time = (today - datetime.timedelta(hours=meta['hours_ago'])).strftime("%Y-%m-%d %H:%M:%S")
        cust_code = random.choice(cust_codes)
        seller_code = 'NV0001'
        branch_code = 'CN01'

        chosen_prod = random.choice(prods)
        p_code, price, soh = chosen_prod
        qty = 1 if 'TV-' in p_code or 'TL-' in p_code else random.choice([1, 2])
        total_amt = price * qty
        discount = 0.0
        amt_due = total_amt

        pay_cash = 0.0
        pay_transfer = 0.0
        pay_card = 0.0
        pay_installment = 0.0
        amt_paid = 0.0

        if meta['type'] == 'Trả đủ':
            amt_paid = amt_due
            if random.random() < 0.5:
                pay_cash = amt_due
            else:
                pay_transfer = amt_due
            note = f"Khách hẹn giao lắp lúc {(today + datetime.timedelta(hours=random.randint(4, 24))).strftime('%H:%M %d/%m')}"
        elif meta['type'] == 'Cọc COD' or meta['type'] == 'Cọc giữ chỗ':
            deposit = round(amt_due * random.choice([0.1, 0.15, 0.2]), -4)
            amt_paid = deposit
            pay_transfer = deposit
            if meta['is_expired']:
                note = "CẢNH BÁO: Đơn giữ máy quá 48h, khách chưa xác nhận lịch nhận - Cần liên hệ lại!"
            else:
                note = f"Đã nhận cọc {deposit:,.0f}đ. Còn thu COD {(amt_due - deposit):,.0f}đ khi giao hàng."
        elif 'Trả góp' in meta['type']:
            deposit = round(amt_due * 0.1, -4) if random.random() < 0.5 else 0.0
            amt_paid = deposit
            pay_transfer = deposit
            pay_installment = amt_due - deposit
            partner = random.choice(['FE Credit', 'Home Credit', 'HD Saison', 'Mpos 0%'])
            if meta['status'] == 'Đã hủy':
                note = f"Hồ sơ trả góp qua {partner} bị từ chối thẩm định. Hủy đơn nhả tồn."
            elif meta['is_expired']:
                note = f"Hồ sơ {partner} quá hạn duyệt 48h chưa có kết quả."
            else:
                note = f"Đăng ký trả góp qua {partner}. Mã hồ sơ HS-{random.randint(100000, 999999)}."

        order_records.append((
            order_code, order_time, cust_code, seller_code, branch_code,
            total_amt, discount, amt_due, amt_paid, pay_cash, pay_card, pay_transfer, pay_installment,
            meta['status'], note
        ))

        order_lines.append((
            order_code, p_code, qty, price, 0.0, 0.0, total_amt
        ))

    cur.executemany("""
        INSERT INTO FACT_ORDERS (
            order_code, order_time, customer_code, seller_code, branch_code,
            total_amount, discount_amount, amount_due, amount_paid,
            pay_cash, pay_card, pay_transfer, pay_installment, status, note
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, order_records)

    cur.executemany("""
        INSERT INTO FACT_ORDERS_LINES (
            order_code, product_code, quantity, unit_price, discount_percent, discount_amount, line_total
        ) VALUES (?, ?, ?, ?, ?, ?, ?);
    """, order_lines)

    con.commit()
    con.close()
    print(f"    Hoàn tất sinh {len(order_records)} đơn đặt hàng và chi tiết đơn hàng.")

def verify_data():
    print(">>> [5/5] Kiểm tra tổng hợp các chỉ số cửa hàng...")
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM DIM_BRANCHES;")
    branches = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*), employee_name FROM DIM_EMPLOYEES;")
    emps = cur.fetchone()

    cur.execute("SELECT COUNT(*) FROM FACT_INVOICES;")
    num_inv = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM FACT_ORDERS;")
    num_orders = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM PURCHASE_ORDERS;")
    num_pos = cur.fetchone()[0]

    cur.execute("SELECT ROUND(SUM(total_revenue), 0), ROUND(SUM(gross_profit), 0) FROM VW_DAILY_SALES_PERFORMANCE;")
    rev, profit = cur.fetchone()

    print(f"    ✔ Số chi nhánh: {branches} (Chỉ có CN01)")
    print(f"    ✔ Người vận hành: {emps[1]} (Duy nhất 1 người)")
    print(f"    ✔ Tổng số hóa đơn phát sinh: {num_inv} hóa đơn")
    print(f"    ✔ Doanh thu tích lũy: {rev:,.0f} VNĐ")
    print(f"    ✔ Lợi nhuận gộp: {profit:,.0f} VNĐ (Tỷ suất lợi nhuận: {(profit/rev)*100:.1f}%)")
    print(f"    ✔ Tổng số đơn đặt hàng (FACT_ORDERS): {num_orders} đơn")
    print(f"    ✔ Tổng số đơn nhập hàng đang về (PURCHASE_ORDERS): {num_pos} đơn")

    # Kiểm tra tính chất cảm tính của tồn kho
    print("\n--- PHÂN TÍCH RỦI RO TỒN KHO CẢM TÍNH (GUT-FEELING STOCKING BIAS) ---")
    cur.execute("""
        SELECT product_name, stock_on_hand, total_units_sold, 
               ROUND(stock_on_hand * cost_price, 0) AS capital_tied,
               inventory_status
        FROM VW_PRODUCT_PERFORMANCE
        WHERE has_serial = 1
        ORDER BY capital_tied DESC;
    """)
    rows = cur.fetchall()
    for r in rows:
        print(f"    • {r[0][:38]:<38} | Tồn kho: {r[1]:>2} | Đã bán: {r[2]:>2} | Vốn đọng: {r[3]:>12,.0f} đ | {r[4]}")

    print("\n--- TỔNG QUAN DÒNG HÀNG 4 TRẠNG THÁI (VW_INVENTORY_FLOW_OVERVIEW) ---")
    cur.execute("""
        SELECT product_code, product_name, soh, res, avl, inc, projected_stock, flow_status, inventory_status
        FROM VW_INVENTORY_FLOW_OVERVIEW
        WHERE has_serial = 1
        ORDER BY soh DESC;
    """)
    flow_rows = cur.fetchall()
    print(f"{'Mã SKU':<14} | {'Tên sản phẩm':<32} | {'SOH':>3} | {'RES':>3} | {'AVL':>3} | {'INC':>3} | {'Dự kiến':>7} | {'Dòng hàng':<16} | {'Trạng thái'}")
    print("-" * 125)
    for r in flow_rows:
        print(f"{r[0]:<14} | {r[1][:32]:<32} | {r[2]:>3} | {r[3]:>3} | {r[4]:>3} | {r[5]:>3} | {r[6]:>7} | {r[7]:<16} | {r[8]}")

    con.close()

def seed_extended_modules_data(db_path: str = DB_PATH):
    """
    Nâng cấp non-destructive schema & seed dữ liệu mở rộng phục vụ Module 02 - 06.
    Giữ nguyên toàn bộ 16 SKU, hóa đơn, đơn hàng và PO hiện có của Module 01.
    """
    print(">>> [V2] Kiểm tra & nạp dữ liệu mở rộng cho Module 02 - 06...")
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON;")
    cur = con.cursor()

    # 1. Bổ sung cột mở rộng vào DIM_PRODUCTS nếu chưa tồn tại
    existing_cols = {r[1] for r in cur.execute("PRAGMA table_info(DIM_PRODUCTS);").fetchall()}
    alter_statements = [
        ("lead_time_days", "ALTER TABLE DIM_PRODUCTS ADD COLUMN lead_time_days INTEGER NOT NULL DEFAULT 3;"),
        ("moq", "ALTER TABLE DIM_PRODUCTS ADD COLUMN moq INTEGER NOT NULL DEFAULT 1;"),
        ("pack_size", "ALTER TABLE DIM_PRODUCTS ADD COLUMN pack_size INTEGER NOT NULL DEFAULT 1;"),
        ("seasonality", "ALTER TABLE DIM_PRODUCTS ADD COLUMN seasonality TEXT NOT NULL DEFAULT 'YEAR_ROUND';"),
        ("lifecycle_status", "ALTER TABLE DIM_PRODUCTS ADD COLUMN lifecycle_status TEXT NOT NULL DEFAULT 'ACTIVE';"),
        ("map_price", "ALTER TABLE DIM_PRODUCTS ADD COLUMN map_price REAL NOT NULL DEFAULT 0.0;"),
    ]
    for col_name, sql in alter_statements:
        if col_name not in existing_cols:
            cur.execute(sql)

    # 2. Khởi tạo 6 bảng nghiệp vụ mới nếu chưa tồn tại
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS SYS_ALERT_SNOOZE_LOG (
            snooze_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_code TEXT NOT NULL,
            snooze_days INTEGER NOT NULL CHECK (snooze_days IN (7, 14, 30)),
            snooze_until TEXT NOT NULL,
            reason TEXT NOT NULL,
            created_by TEXT NOT NULL DEFAULT 'NV0001',
            is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
            created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
            FOREIGN KEY (product_code) REFERENCES DIM_PRODUCTS(product_code) ON UPDATE CASCADE ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_snooze_product ON SYS_ALERT_SNOOZE_LOG(product_code, is_active);

        CREATE TABLE IF NOT EXISTS EXT_MARKET_PRICES (
            market_price_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_code TEXT NOT NULL,
            competitor_name TEXT NOT NULL,
            competitor_price REAL NOT NULL CHECK (competitor_price >= 0),
            promo_note TEXT,
            crawled_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
            FOREIGN KEY (product_code) REFERENCES DIM_PRODUCTS(product_code) ON UPDATE CASCADE ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_market_prices_product ON EXT_MARKET_PRICES(product_code);

        CREATE TABLE IF NOT EXISTS FACT_CLEARANCE_CAMPAIGNS (
            campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_code TEXT NOT NULL,
            tactic_code TEXT NOT NULL CHECK (tactic_code IN ('PA1', 'PA2', 'PA3', 'PA4')),
            target_qty INTEGER NOT NULL CHECK (target_qty > 0),
            clearance_price REAL NOT NULL CHECK (clearance_price >= 0),
            promo_cost_per_unit REAL NOT NULL DEFAULT 0.0 CHECK (promo_cost_per_unit >= 0),
            expected_profit REAL NOT NULL DEFAULT 0.0,
            status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('DRAFT', 'SIMULATED', 'PENDING_APPROVAL', 'ACTIVE', 'COMPLETED', 'CANCELLED')),
            approved_by TEXT,
            created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
            FOREIGN KEY (product_code) REFERENCES DIM_PRODUCTS(product_code) ON UPDATE CASCADE ON DELETE RESTRICT
        );
        CREATE INDEX IF NOT EXISTS idx_clearance_product ON FACT_CLEARANCE_CAMPAIGNS(product_code, status);

        CREATE TABLE IF NOT EXISTS SYS_CRM_INTERACTION_LOG (
            interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_code TEXT NOT NULL,
            product_code TEXT NOT NULL,
            serial_number TEXT,
            trigger_type TEXT NOT NULL,
            channel TEXT NOT NULL DEFAULT 'CALL' CHECK (channel IN ('CALL', 'ZALO_ZNS')),
            outcome TEXT NOT NULL,
            cooldown_until TEXT NOT NULL,
            note TEXT,
            created_by TEXT NOT NULL DEFAULT 'NV0001',
            created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
            FOREIGN KEY (customer_code) REFERENCES DIM_CUSTOMERS(customer_code) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (product_code) REFERENCES DIM_PRODUCTS(product_code) ON UPDATE CASCADE ON DELETE RESTRICT
        );
        CREATE INDEX IF NOT EXISTS idx_crm_log_customer ON SYS_CRM_INTERACTION_LOG(customer_code, cooldown_until);

        CREATE TABLE IF NOT EXISTS FACT_SERVICE_APPOINTMENTS (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_code TEXT NOT NULL,
            product_code TEXT NOT NULL,
            serial_number TEXT,
            technician_code TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            service_name TEXT NOT NULL,
            expected_fee REAL NOT NULL DEFAULT 0.0 CHECK (expected_fee >= 0),
            status TEXT NOT NULL DEFAULT 'WORK_ASSIGNED' CHECK (status IN ('CONVERTED_BOOKING', 'WORK_ASSIGNED', 'WORK_DONE', 'CANCELLED')),
            note TEXT,
            created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
            FOREIGN KEY (customer_code) REFERENCES DIM_CUSTOMERS(customer_code) ON UPDATE CASCADE ON DELETE RESTRICT,
            FOREIGN KEY (product_code) REFERENCES DIM_PRODUCTS(product_code) ON UPDATE CASCADE ON DELETE RESTRICT,
            FOREIGN KEY (technician_code) REFERENCES DIM_EMPLOYEES(employee_code) ON UPDATE CASCADE ON DELETE RESTRICT
        );
        CREATE INDEX IF NOT EXISTS idx_appt_tech_slot ON FACT_SERVICE_APPOINTMENTS(technician_code, appointment_date, time_slot);

        CREATE TABLE IF NOT EXISTS FACT_COMMISSION_LEDGER (
            ledger_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_code TEXT NOT NULL,
            period_label TEXT NOT NULL DEFAULT 'Tháng 10-11/2026',
            accessory_sales REAL NOT NULL DEFAULT 0.0 CHECK (accessory_sales >= 0),
            accessory_profit REAL NOT NULL DEFAULT 0.0,
            service_sales REAL NOT NULL DEFAULT 0.0 CHECK (service_sales >= 0),
            service_profit REAL NOT NULL DEFAULT 0.0,
            commission_amount REAL NOT NULL DEFAULT 0.0 CHECK (commission_amount >= 0),
            status TEXT NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED')),
            approved_at TEXT,
            approved_by TEXT,
            FOREIGN KEY (employee_code) REFERENCES DIM_EMPLOYEES(employee_code) ON UPDATE CASCADE ON DELETE RESTRICT
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_comm_emp_period ON FACT_COMMISSION_LEDGER(employee_code, period_label);
    """)

    # 3. Bổ sung 2 Kỹ thuật viên phụ trợ vào DIM_EMPLOYEES
    cur.executemany("""
        INSERT OR IGNORE INTO DIM_EMPLOYEES (
            employee_code, employee_name, phone, department, title, login_account, branch_code, salary, hire_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, [
        ('NV0002', 'Trần Đình Khang', '0913456789', 'Kỹ thuật - Lắp đặt', 'Kỹ thuật viên', 'khangtd', 'CN01', 12000000, '2023-03-15'),
        ('NV0003', 'Nguyễn Tuấn Long', '0914567890', 'Kỹ thuật - Lắp đặt', 'Kỹ thuật trưởng', 'longnt', 'CN01', 15000000, '2022-01-10'),
    ])

    # 4. Cập nhật tham số tồn kho, mùa vụ, MOQ và MAP cho 16 SKU
    product_params = [
        # (lead_time_days, moq, pack_size, seasonality, lifecycle_status, map_price, product_code)
        (4, 2, 1, 'YEAR_ROUND', 'ACTIVE', 14800000, 'TV-SN-55X80K'),
        (4, 2, 1, 'YEAR_ROUND', 'ACTIVE', 25190000, 'TV-LG-55C3'),
        (3, 5, 2, 'YEAR_ROUND', 'ACTIVE', 5490000, 'TV-CS-43FG6'),
        (4, 2, 1, 'YEAR_ROUND', 'ACTIVE', 10200000, 'TV-SS-55AU7'),
        (7, 2, 1, 'SUMMER', 'ACTIVE', 9890000, 'ML-DK-FTKB25'),
        (4, 2, 1, 'SUMMER', 'ACTIVE', 12490000, 'ML-PN-XPU12'),
        (3, 4, 2, 'SUMMER', 'ACTIVE', 5990000, 'ML-CS-TC09'),
        (5, 1, 1, 'YEAR_ROUND', 'ACTIVE', 16990000, 'TL-SS-647L'),
        (4, 2, 1, 'YEAR_ROUND', 'ACTIVE', 11990000, 'TL-PN-322L'),
        (3, 4, 2, 'YEAR_ROUND', 'ACTIVE', 4390000, 'TL-AQ-180L'),
        (4, 2, 1, 'YEAR_ROUND', 'ACTIVE', 8490000, 'MG-LG-FV1409'),
        (3, 3, 1, 'YEAR_ROUND', 'ACTIVE', 4290000, 'MG-TB-85K'),
        (1, 1, 1, 'YEAR_ROUND', 'ACTIVE', 200000, 'DV-LAPDAT-ML'),
        (1, 1, 1, 'YEAR_ROUND', 'ACTIVE', 150000, 'DV-TREO-TV'),
        (2, 10, 5, 'YEAR_ROUND', 'ACTIVE', 290000, 'PK-GIATREO-55'),
        (2, 20, 10, 'YEAR_ROUND', 'ACTIVE', 150000, 'PK-ONGDONG-M'),
    ]
    cur.executemany("""
        UPDATE DIM_PRODUCTS
        SET lead_time_days = ?, moq = ?, pack_size = ?, seasonality = ?, lifecycle_status = ?, map_price = ?
        WHERE product_code = ?;
    """, product_params)

    # 5. Seed Radar Giá đối thủ (EXT_MARKET_PRICES) nếu trống
    if cur.execute("SELECT COUNT(*) FROM EXT_MARKET_PRICES;").fetchone()[0] == 0:
        market_rows = [
            ('TV-LG-55C3', 'Điện Máy Xanh (ĐMX)', 28990000, 'Kèm công lắp + BH hãng', '2026-11-04 07:30:00'),
            ('TV-LG-55C3', 'MediaMart Hai Bà Trưng', 27490000, 'Tặng voucher 500k', '2026-11-04 07:30:00'),
            ('TV-LG-55C3', 'Đại lý Online Min (Shopee/Lazada)', 26200000, 'Chưa gồm phí ship cồng kềnh', '2026-11-04 07:30:00'),
            ('ML-PN-XPU12', 'Điện Máy Xanh (ĐMX)', 14290000, 'Bao công lắp đặt', '2026-11-04 07:30:00'),
            ('ML-PN-XPU12', 'MediaMart Hai Bà Trưng', 13690000, 'Chưa kèm ống đồng', '2026-11-04 07:30:00'),
            ('ML-PN-XPU12', 'Đại lý Online Min (Shopee/Lazada)', 12950000, 'Giao tại kho, tự lắp', '2026-11-04 07:30:00'),
            ('TL-SS-647L', 'Điện Máy Xanh (ĐMX)', 19490000, 'Giao lắp miễn phí nội thành', '2026-11-04 07:30:00'),
            ('TL-SS-647L', 'MediaMart Hai Bà Trưng', 18590000, 'Tặng hộp bảo quản', '2026-11-04 07:30:00'),
            ('TL-SS-647L', 'Đại lý Online Min (Shopee/Lazada)', 17650000, 'Chưa gồm phí khiêng tầng', '2026-11-04 07:30:00'),
            ('MG-LG-FV1409', 'Điện Máy Xanh (ĐMX)', 9990000, 'Tặng nước giặt OMO', '2026-11-04 07:30:00'),
            ('MG-LG-FV1409', 'MediaMart Hai Bà Trưng', 9290000, 'Hỗ trợ trả góp 0%', '2026-11-04 07:30:00'),
            ('MG-LG-FV1409', 'Đại lý Online Min (Shopee/Lazada)', 8790000, 'Chưa gồm dây cấp dài', '2026-11-04 07:30:00'),
            ('ML-DK-FTKB25', 'Điện Máy Xanh (ĐMX)', 10990000, 'Bao công lắp + BH 1 năm', '2026-11-04 07:30:00'),
            ('ML-DK-FTKB25', 'MediaMart Hai Bà Trưng', 10290000, 'Chưa bao gồm vật tư ống đồng', '2026-11-04 07:30:00'),
            ('ML-DK-FTKB25', 'Đại lý Online Min (Shopee/Lazada)', 9790000, 'Giá online tại kho', '2026-11-04 07:30:00'),
        ]
        cur.executemany("""
            INSERT INTO EXT_MARKET_PRICES (product_code, competitor_name, competitor_price, promo_note, crawled_at)
            VALUES (?, ?, ?, ?, ?);
        """, market_rows)

    # 6. Seed Chiến dịch xả hàng (FACT_CLEARANCE_CAMPAIGNS) nếu trống
    if cur.execute("SELECT COUNT(*) FROM FACT_CLEARANCE_CAMPAIGNS;").fetchone()[0] == 0:
        cur.executemany("""
            INSERT INTO FACT_CLEARANCE_CAMPAIGNS (
                product_code, tactic_code, target_qty, clearance_price, promo_cost_per_unit, expected_profit, status, approved_by, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, [
            ('TV-LG-55C3', 'PA2', 10, 26990000, 220000, 42700000, 'ACTIVE', 'NV0001', '2026-11-02 09:00:00'),
            ('ML-PN-XPU12', 'PA3', 8, 12990000, 150000, 14720000, 'ACTIVE', 'NV0001', '2026-11-03 10:15:00'),
            ('TL-SS-647L', 'PA4', 8, 18490000, 462250, 25022000, 'PENDING_APPROVAL', None, '2026-11-04 08:30:00'),
        ])

    # 7. Seed Nhật ký CSKH & Chống spam (SYS_CRM_INTERACTION_LOG) nếu trống
    if cur.execute("SELECT COUNT(*) FROM SYS_CRM_INTERACTION_LOG;").fetchone()[0] == 0:
        cust_rows = cur.execute("SELECT DISTINCT i.customer_code, l.product_code FROM FACT_INVOICES i JOIN FACT_INVOICES_LINES l ON i.invoice_code = l.invoice_code LIMIT 6;").fetchall()
        crm_logs = []
        for idx, (c_code, p_code) in enumerate(cust_rows):
            if idx < 4:
                # Đang trong Cooldown 30 ngày tính từ mốc 2026-11-10
                crm_logs.append((c_code, p_code, None, 'CARE_MAINT_AC', 'CALL', 'CONVERTED_BOOKING' if idx < 2 else 'SNOOZED', '2026-12-05', 'Đã liên hệ chăm sóc định kỳ', 'NV0001', '2026-11-05 10:00:00'))
            else:
                # Đã hết Cooldown (>30 ngày) để kiểm chứng khách vẫn hợp lệ gọi lại
                crm_logs.append((c_code, p_code, None, 'CARE_ACCESSORY', 'ZALO_ZNS', 'SNOOZED', '2026-10-15', 'Nhắn tin cảm ơn sau lắp đặt', 'NV0001', '2026-09-15 09:00:00'))
        if crm_logs:
            cur.executemany("""
                INSERT INTO SYS_CRM_INTERACTION_LOG (
                    customer_code, product_code, serial_number, trigger_type, channel, outcome, cooldown_until, note, created_by, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, crm_logs)

    # 8. Seed Lịch hẹn Kỹ thuật viên (FACT_SERVICE_APPOINTMENTS) nếu trống
    if cur.execute("SELECT COUNT(*) FROM FACT_SERVICE_APPOINTMENTS;").fetchone()[0] == 0:
        ac_rows = cur.execute("""
            SELECT DISTINCT i.customer_code, l.product_code
            FROM FACT_INVOICES i JOIN FACT_INVOICES_LINES l ON i.invoice_code = l.invoice_code
            WHERE l.product_code LIKE 'ML-%' OR l.product_code LIKE 'TV-%'
            LIMIT 3;
        """).fetchall()
        techs = ['NV0003', 'NV0002', 'NV0001']
        slots = ['09:00 (Sáng)', '14:00 (Chiều)', '16:30 (Chiều)']
        appts = []
        for idx, (c_code, p_code) in enumerate(ac_rows):
            appts.append((c_code, p_code, None, techs[idx % 3], '2026-11-12', slots[idx % 3], 'Bảo dưỡng xịt rửa & kiểm tra gas định kỳ', 150000, 'WORK_ASSIGNED', 'Lịch hẹn chăm sóc khách quen', '2026-11-10 11:00:00'))
        if appts:
            cur.executemany("""
                INSERT INTO FACT_SERVICE_APPOINTMENTS (
                    customer_code, product_code, serial_number, technician_code, appointment_date, time_slot, service_name, expected_fee, status, note, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, appts)

    # 9. Seed Sổ Hoa hồng Bán kèm (FACT_COMMISSION_LEDGER) cho 3 nhân sự
    if cur.execute("SELECT COUNT(*) FROM FACT_COMMISSION_LEDGER;").fetchone()[0] == 0:
        ledger_rows = [
            ('NV0001', 'Tháng 10-11/2026', 24000000.0, 13000000.0, 28800000.0, 32500000.0, round(13000000 * 0.15 + 32500000 * 0.20, 0), 'APPROVED', '2026-11-10 17:00:00', 'NV0001'),
            ('NV0003', 'Tháng 10-11/2026', 10500000.0, 6500000.0, 8000000.0, 9000000.0, round(6500000 * 0.15 + 9000000 * 0.20, 0), 'PENDING', None, None),
            ('NV0002', 'Tháng 10-11/2026', 8100000.0, 5100000.0, 6000000.0, 6750000.0, round(5100000 * 0.15 + 6750000 * 0.20, 0), 'PENDING', None, None),
        ]
        cur.executemany("""
            INSERT INTO FACT_COMMISSION_LEDGER (
                employee_code, period_label, accessory_sales, accessory_profit, service_sales, service_profit, commission_amount, status, approved_at, approved_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, ledger_rows)

    con.commit()
    con.close()
    print("    Hoàn tất nâng cấp schema & seed dữ liệu mở rộng cho Module 02 - 06.")


if __name__ == '__main__':
    if '--migrate-v2' in sys.argv:
        seed_extended_modules_data()
    else:
        init_database()
        insert_master_data()
        generate_customers_with_sdv(num_customers=45)
        generate_serials_and_invoices_with_sdv(num_invoices=75)
        generate_purchase_orders()
        generate_orders_with_sdv(num_orders=35)
        seed_extended_modules_data()
        verify_data()
        print("\n" + "=" * 80)
        print("HOÀN TẤT ĐIỀU CHỈNH DỮ LIỆU GIẢ LẬP PHÙ HỢP HOÀN TOÀN MÔ HÌNH SOLE TRADER & 6 MODULES!")
        print("=" * 80)
