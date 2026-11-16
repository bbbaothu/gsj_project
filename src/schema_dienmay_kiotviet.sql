-- ============================================================================
-- CƠ SỞ DỮ LIỆU BÁN HÀNG LĨNH VỰC ĐIỆN MÁY (TƯƠNG THÍCH POS KIOTVIET)
-- HỆ QUẢN TRỊ CSDL: SQLite 3
-- MÔ HÌNH: STAR SCHEMA / DATA WAREHOUSE HYBRID FOR RETAIL ANALYTICS
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- 1. BẢNG CHI NHÁNH / KHO HÀNG (DIM_BRANCHES)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS FACT_COMMISSION_LEDGER;
DROP TABLE IF EXISTS FACT_SERVICE_APPOINTMENTS;
DROP TABLE IF EXISTS SYS_CRM_INTERACTION_LOG;
DROP TABLE IF EXISTS FACT_CLEARANCE_CAMPAIGNS;
DROP TABLE IF EXISTS EXT_MARKET_PRICES;
DROP TABLE IF EXISTS SYS_ALERT_SNOOZE_LOG;
DROP TABLE IF EXISTS FACT_WARRANTIES;
DROP TABLE IF EXISTS FACT_INVOICE_SERIALS;
DROP TABLE IF EXISTS FACT_INVOICES_LINES;
DROP TABLE IF EXISTS FACT_INVOICES;
DROP TABLE IF EXISTS FACT_ORDERS_LINES;
DROP TABLE IF EXISTS FACT_ORDERS;
DROP TABLE IF EXISTS PO_ITEMS;
DROP TABLE IF EXISTS PURCHASE_ORDERS;
DROP TABLE IF EXISTS DIM_PRODUCT_SERIALS;
DROP TABLE IF EXISTS DIM_PRODUCTS;
DROP TABLE IF EXISTS DIM_EMPLOYEES;
DROP TABLE IF EXISTS DIM_CUSTOMERS;
DROP TABLE IF EXISTS DIM_BRANCHES;

CREATE TABLE DIM_BRANCHES (
    branch_code TEXT PRIMARY KEY,                       -- Mã chi nhánh / kho hàng (VD: CN01, KHO_TONG)
    branch_name TEXT NOT NULL,                          -- Tên chi nhánh (VD: Chi nhánh Điện máy Quận 1)
    phone TEXT,                                         -- Số điện thoại chi nhánh
    address TEXT,                                       -- Địa chỉ chi nhánh
    ward TEXT,                                          -- Phường / Xã
    district TEXT,                                      -- Quận / Huyện
    province TEXT,                                      -- Tỉnh / Thành phố
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime'))
);

-- ----------------------------------------------------------------------------
-- 2. BẢNG KHÁCH HÀNG (DIM_CUSTOMERS)
-- Tương thích template Excel KiotViet: Khách cá nhân & Khách tổ chức (VAT)
-- ----------------------------------------------------------------------------
CREATE TABLE DIM_CUSTOMERS (
    customer_code TEXT PRIMARY KEY,                     -- Mã khách hàng (VD: KH00001)
    customer_type TEXT NOT NULL DEFAULT 'Cá nhân' CHECK (customer_type IN ('Cá nhân', 'Công ty')),
    customer_name TEXT NOT NULL,                        -- Tên khách hàng / Đại diện
    phone TEXT NOT NULL,                                -- Số điện thoại (dùng tra cứu bảo hành, lịch sử mua sắm)
    email TEXT,                                         -- Email nhận hóa đơn điện tử / bảo hành
    birth_date TEXT,                                    -- Ngày sinh (YYYY-MM-DD)
    gender TEXT CHECK (gender IN ('Nam', 'Nữ', 'Khác', NULL)),
    address TEXT,                                       -- Địa chỉ giao hàng / lắp đặt
    area TEXT,                                          -- Khu vực giao hàng (Quận / Huyện)
    ward TEXT,                                          -- Phường / Xã
    company TEXT,                                       -- Tên công ty (nếu là khách doanh nghiệp)
    tax_code TEXT,                                      -- Mã số thuế (xuất hóa đơn VAT)
    current_debt REAL NOT NULL DEFAULT 0.0 CHECK (current_debt >= 0), -- Nợ cần thu hiện tại
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)), -- 1: Đang hoạt động, 0: Ngừng hoạt động
    created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime'))
);

CREATE INDEX idx_customers_phone ON DIM_CUSTOMERS(phone);
CREATE INDEX idx_customers_tax_code ON DIM_CUSTOMERS(tax_code);

-- ----------------------------------------------------------------------------
-- 3. BẢNG NHÂN VIÊN (DIM_EMPLOYEES)
-- Master-data nhân viên: Tư vấn bán hàng, Kỹ thuật lắp đặt, Thu ngân
-- ----------------------------------------------------------------------------
CREATE TABLE DIM_EMPLOYEES (
    employee_code TEXT PRIMARY KEY,                     -- Mã nhân viên (VD: NV0001)
    employee_name TEXT NOT NULL,                        -- Tên nhân viên
    phone TEXT NOT NULL,                                -- Số điện thoại
    department TEXT NOT NULL,                           -- Phòng ban: Bán hàng, Kỹ thuật - Lắp đặt, Kế toán, Kho
    title TEXT NOT NULL,                                -- Chức danh: Chuyên viên tư vấn, Kỹ thuật viên, Thu ngân
    login_account TEXT UNIQUE,                          -- Tài khoản đăng nhập hệ thống KiotViet
    branch_code TEXT NOT NULL,                          -- Chi nhánh làm việc chính
    salary REAL DEFAULT 0.0 CHECK (salary >= 0),        -- Lương cơ bản
    hire_date TEXT,                                     -- Ngày bắt đầu làm việc (YYYY-MM-DD)
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
    FOREIGN KEY (branch_code) REFERENCES DIM_BRANCHES(branch_code) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX idx_employees_branch ON DIM_EMPLOYEES(branch_code);
CREATE INDEX idx_employees_department ON DIM_EMPLOYEES(department);

-- ----------------------------------------------------------------------------
-- 4. BẢNG HÀNG HÓA / DỊCH VỤ ĐIỆN MÁY (DIM_PRODUCTS)
-- Đặc thù điện máy: Quản lý Serial/IMEI, Bảo hành, Thông số kỹ thuật
-- ----------------------------------------------------------------------------
CREATE TABLE DIM_PRODUCTS (
    product_code TEXT PRIMARY KEY,                      -- Mã hàng (SKU) (VD: TV-SN-55X80K, ML-DK-FTKB25, DV-LAPDAT)
    barcode TEXT UNIQUE,                                -- Mã vạch (EAN-13 / UPC)
    product_name TEXT NOT NULL,                         -- Tên hàng hóa / dịch vụ
    product_type TEXT NOT NULL DEFAULT 'Hàng hóa' CHECK (product_type IN ('Hàng hóa', 'Dịch vụ', 'Combo')),
    category_path TEXT NOT NULL,                        -- Nhóm hàng 3 cấp (VD: Điện tử > Tivi > Tivi Sony 55 inch)
    brand TEXT,                                         -- Thương hiệu (Sony, Daikin, Samsung, Panasonic, LG,...)
    model_code TEXT,                                    -- Ký hiệu Model nhà sản xuất (VD: 55X80K, FTKB25WAVMV)
    uom TEXT NOT NULL DEFAULT 'Cái',                     -- Đơn vị tính (Cái, Bộ, Mét, Gói)
    weight_gram INTEGER DEFAULT 0 CHECK (weight_gram >= 0), -- Trọng lượng (phục vụ tính phí vận chuyển)
    sale_price REAL NOT NULL CHECK (sale_price >= 0),    -- Giá bán niêm yết (VNĐ)
    cost_price REAL NOT NULL CHECK (cost_price >= 0),    -- Giá vốn nhập hàng (VNĐ)
    stock_on_hand INTEGER NOT NULL DEFAULT 0 CHECK (stock_on_hand >= 0), -- Tồn kho tức thời
    min_stock INTEGER DEFAULT 0 CHECK (min_stock >= 0),  -- Tồn nhỏ nhất (điểm đặt hàng lại ROP)
    max_stock INTEGER DEFAULT 1000 CHECK (max_stock >= min_stock), -- Tồn lớn nhất
    warranty_months INTEGER NOT NULL DEFAULT 12 CHECK (warranty_months >= 0), -- Thời hạn bảo hành chính hãng (tháng)
    has_serial INTEGER NOT NULL DEFAULT 1 CHECK (has_serial IN (0, 1)), -- 1: Quản lý theo Serial/IMEI, 0: Hàng phụ kiện/dịch vụ
    is_direct_sale INTEGER NOT NULL DEFAULT 1 CHECK (is_direct_sale IN (0, 1)), -- Cho phép bán trực tiếp tại POS
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)), -- Đang kinh doanh
    lead_time_days INTEGER NOT NULL DEFAULT 3 CHECK (lead_time_days >= 1), -- Thời gian giao hàng chuẩn của NCC (ngày)
    moq INTEGER NOT NULL DEFAULT 1 CHECK (moq >= 1),    -- Số lượng đặt hàng tối thiểu (MOQ)
    pack_size INTEGER NOT NULL DEFAULT 1 CHECK (pack_size >= 1), -- Quy cách đóng thùng/kiện chẵn
    seasonality TEXT NOT NULL DEFAULT 'YEAR_ROUND' CHECK (seasonality IN ('SUMMER', 'WINTER', 'YEAR_ROUND')), -- Tính mùa vụ
    lifecycle_status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (lifecycle_status IN ('ACTIVE', 'EOL')), -- Vòng đời sản phẩm
    map_price REAL NOT NULL DEFAULT 0.0 CHECK (map_price >= 0), -- Giá bán công khai tối thiểu theo cam kết hãng (MAP)
    specifications TEXT,                                -- Thông số kỹ thuật (JSON string: công suất, kích thước màn hình, inverter...)
    created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime'))
);

CREATE INDEX idx_products_brand ON DIM_PRODUCTS(brand);
CREATE INDEX idx_products_category ON DIM_PRODUCTS(category_path);
CREATE INDEX idx_products_has_serial ON DIM_PRODUCTS(has_serial);

-- ----------------------------------------------------------------------------
-- 5. BẢNG QUẢN LÝ SERIAL / IMEI TỪNG THIẾT BỊ (DIM_PRODUCT_SERIALS)
-- Cực kỳ cốt lõi trong ngành điện máy: Mỗi máy có 1 Serial riêng biệt trong kho
-- ----------------------------------------------------------------------------
CREATE TABLE DIM_PRODUCT_SERIALS (
    serial_number TEXT PRIMARY KEY,                     -- Số Serial/IMEI duy nhất (VD: SN-SNY55-20261001-098)
    product_code TEXT NOT NULL,                         -- Mã hàng SKU tương ứng
    branch_code TEXT NOT NULL,                          -- Đang nằm tại chi nhánh / kho nào
    status TEXT NOT NULL DEFAULT 'IN_STOCK' CHECK (status IN ('IN_STOCK', 'SOLD', 'DEFECTIVE_RETURN', 'WARRANTY_REPAIR')),
    import_date TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')), -- Ngày nhập kho
    sold_invoice_code TEXT,                             -- Mã hóa đơn đã bán (NULL nếu còn tồn kho)
    created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
    FOREIGN KEY (product_code) REFERENCES DIM_PRODUCTS(product_code) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (branch_code) REFERENCES DIM_BRANCHES(branch_code) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX idx_serials_product ON DIM_PRODUCT_SERIALS(product_code);
CREATE INDEX idx_serials_status ON DIM_PRODUCT_SERIALS(status);
CREATE INDEX idx_serials_branch ON DIM_PRODUCT_SERIALS(branch_code);

-- ----------------------------------------------------------------------------
-- 6. BẢNG ĐƠN ĐẶT HÀNG (FACT_ORDERS)
-- Giai đoạn giữ chỗ / đặt trước thiết bị điện máy (chưa xuất kho, chưa ghi nhận doanh thu)
-- ----------------------------------------------------------------------------
CREATE TABLE FACT_ORDERS (
    order_code TEXT PRIMARY KEY,                        -- Mã đơn hàng (VD: DH00001, format DHxxxxx)
    order_time TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')), -- Thời gian đặt hàng
    customer_code TEXT NOT NULL,                        -- Khách hàng đặt
    seller_code TEXT NOT NULL,                          -- Nhân viên tiếp nhận đơn
    branch_code TEXT NOT NULL,                          -- Chi nhánh tiếp nhận
    total_amount REAL NOT NULL CHECK (total_amount >= 0),-- Tổng giá trị đơn hàng
    discount_amount REAL NOT NULL DEFAULT 0.0 CHECK (discount_amount >= 0), -- Giảm giá
    amount_due REAL NOT NULL CHECK (amount_due >= 0),   -- Khách cần thanh toán
    amount_paid REAL NOT NULL DEFAULT 0.0 CHECK (amount_paid >= 0), -- Khách đã đặt cọc / trả trước
    pay_cash REAL NOT NULL DEFAULT 0.0 CHECK (pay_cash >= 0),       -- Tiền mặt đã đặt cọc
    pay_card REAL NOT NULL DEFAULT 0.0 CHECK (pay_card >= 0),       -- Quẹt thẻ đã cọc
    pay_transfer REAL NOT NULL DEFAULT 0.0 CHECK (pay_transfer >= 0), -- Chuyển khoản đã cọc
    pay_installment REAL NOT NULL DEFAULT 0.0 CHECK (pay_installment >= 0), -- Đăng ký trả góp
    status TEXT NOT NULL DEFAULT 'Chờ xử lý' CHECK (status IN ('Chờ xử lý', 'Đã xác nhận', 'Đang giao hàng', 'Hoàn thành', 'Đã hủy')),
    note TEXT,                                          -- Ghi chú hẹn ngày giao / lắp đặt
    created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
    FOREIGN KEY (customer_code) REFERENCES DIM_CUSTOMERS(customer_code) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (seller_code) REFERENCES DIM_EMPLOYEES(employee_code) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (branch_code) REFERENCES DIM_BRANCHES(branch_code) ON UPDATE CASCADE ON DELETE RESTRICT,
    CHECK (order_code LIKE 'DH%')                       -- Ràng buộc format mã đơn hàng
);

CREATE INDEX idx_orders_customer ON FACT_ORDERS(customer_code);
CREATE INDEX idx_orders_time ON FACT_ORDERS(order_time);
CREATE INDEX idx_orders_status ON FACT_ORDERS(status);

-- ----------------------------------------------------------------------------
-- 7. BẢNG CHI TIẾT ĐƠN ĐẶT HÀNG (FACT_ORDERS_LINES)
-- ----------------------------------------------------------------------------
CREATE TABLE FACT_ORDERS_LINES (
    order_line_id INTEGER PRIMARY KEY AUTOINCREMENT,    -- Khóa chính dòng chi tiết
    order_code TEXT NOT NULL,                           -- Mã đơn đặt hàng
    product_code TEXT NOT NULL,                         -- Mã sản phẩm
    quantity INTEGER NOT NULL CHECK (quantity > 0),     -- Số lượng đặt mua (> 0)
    unit_price REAL NOT NULL CHECK (unit_price >= 0),   -- Đơn giá niêm yết tại thời điểm đặt
    discount_percent REAL NOT NULL DEFAULT 0.0 CHECK (discount_percent BETWEEN 0.0 AND 100.0),
    discount_amount REAL NOT NULL DEFAULT 0.0 CHECK (discount_amount >= 0),
    line_total REAL NOT NULL CHECK (line_total >= 0),   -- Thành tiền sau chiết khấu
    created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
    FOREIGN KEY (order_code) REFERENCES FACT_ORDERS(order_code) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (product_code) REFERENCES DIM_PRODUCTS(product_code) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX idx_order_lines_order ON FACT_ORDERS_LINES(order_code);
CREATE INDEX idx_order_lines_product ON FACT_ORDERS_LINES(product_code);

-- ----------------------------------------------------------------------------
-- 7B. BẢNG ĐƠN NHẬP HÀNG TỪ NHÀ CUNG CẤP (PURCHASE_ORDERS)
-- Phục vụ quản lý dòng hàng đang trên đường về kho (In-Transit Pipeline)
-- ----------------------------------------------------------------------------
CREATE TABLE PURCHASE_ORDERS (
    purchase_code TEXT PRIMARY KEY,                     -- Mã đơn nhập (VD: PO00001)
    order_time TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')), -- Ngày đặt nhập
    vendor_code TEXT NOT NULL,                          -- Mã nhà cung cấp / Hãng
    vendor_name TEXT NOT NULL,                          -- Tên nhà cung cấp (Sony VN, Daikin VN,...)
    branch_code TEXT NOT NULL,                          -- Chi nhánh nhập về
    total_amount REAL NOT NULL CHECK (total_amount >= 0), -- Tổng tiền hàng
    amount_paid REAL NOT NULL DEFAULT 0.0 CHECK (amount_paid >= 0),
    amount_due REAL NOT NULL CHECK (amount_due >= 0),
    expected_delivery_date TEXT,                        -- Ngày dự kiến cập kho (YYYY-MM-DD)
    status TEXT NOT NULL DEFAULT 'Đang vận chuyển' CHECK (status IN ('Đang vận chuyển', 'Đã nhập hàng', 'Nháp', 'Đã hủy')),
    note TEXT,
    created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
    FOREIGN KEY (branch_code) REFERENCES DIM_BRANCHES(branch_code) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX idx_po_vendor ON PURCHASE_ORDERS(vendor_code);
CREATE INDEX idx_po_status ON PURCHASE_ORDERS(status);
CREATE INDEX idx_po_delivery_date ON PURCHASE_ORDERS(expected_delivery_date);

CREATE TABLE PO_ITEMS (
    po_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    purchase_code TEXT NOT NULL,
    product_code TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    line_total REAL NOT NULL CHECK (line_total >= 0),
    created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
    FOREIGN KEY (purchase_code) REFERENCES PURCHASE_ORDERS(purchase_code) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (product_code) REFERENCES DIM_PRODUCTS(product_code) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX idx_po_items_po ON PO_ITEMS(purchase_code);
CREATE INDEX idx_po_items_prod ON PO_ITEMS(product_code);

-- ----------------------------------------------------------------------------
-- 8. BẢNG HÓA ĐƠN BÁN HÀNG (FACT_INVOICES)
-- Rule R1: Bắt buộc prefix HDIP... (hoặc HD...)
-- Rule R3: Tổng tiền thanh toán pay_cash + pay_card + pay_transfer + pay_installment = amount_due
-- ----------------------------------------------------------------------------
CREATE TABLE FACT_INVOICES (
    invoice_code TEXT PRIMARY KEY,                      -- Mã hóa đơn (VD: HDIP00001, quy chuẩn KiotViet)
    order_code TEXT,                                    -- Kế thừa từ đơn đặt hàng (nếu có)
    invoice_time TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')), -- Thời điểm giao dịch
    seller_code TEXT NOT NULL,                          -- Nhân viên bán hàng (tính KPI doanh số)
    technician_code TEXT,                               -- Kỹ thuật viên giao hàng & lắp đặt (nếu có)
    branch_code TEXT NOT NULL,                          -- Chi nhánh xuất bán
    customer_code TEXT NOT NULL,                        -- Khách hàng mua
    sales_channel TEXT NOT NULL DEFAULT 'Bán trực tiếp' CHECK (sales_channel IN ('Bán trực tiếp', 'Website', 'Facebook', 'Điện thoại', 'Shopee/Lazada')),
    pricebook TEXT DEFAULT 'Bảng giá chuẩn',            -- Bảng giá áp dụng
    total_amount REAL NOT NULL CHECK (total_amount >= 0), -- Tổng tiền hàng chưa trừ chiết khấu
    invoice_discount_amount REAL NOT NULL DEFAULT 0.0 CHECK (invoice_discount_amount >= 0),
    invoice_discount_percent REAL NOT NULL DEFAULT 0.0 CHECK (invoice_discount_percent BETWEEN 0.0 AND 100.0),
    amount_due REAL NOT NULL CHECK (amount_due >= 0),   -- Khách cần trả sau chiết khấu
    pay_cash REAL NOT NULL DEFAULT 0.0 CHECK (pay_cash >= 0),               -- Thanh toán tiền mặt
    pay_card REAL NOT NULL DEFAULT 0.0 CHECK (pay_card >= 0),               -- Quẹt thẻ POS
    pay_transfer REAL NOT NULL DEFAULT 0.0 CHECK (pay_transfer >= 0),       -- Chuyển khoản ngân hàng
    pay_installment REAL NOT NULL DEFAULT 0.0 CHECK (pay_installment >= 0), -- Trả góp qua công ty tài chính / thẻ tín dụng
    delivery_status TEXT NOT NULL DEFAULT 'Đã nhận' CHECK (delivery_status IN ('Đã nhận', 'Đang giao & lắp đặt', 'Đã lắp đặt hoàn tất')),
    vat_invoice_issued INTEGER NOT NULL DEFAULT 0 CHECK (vat_invoice_issued IN (0, 1)), -- Đã xuất hóa đơn đỏ VAT
    note TEXT,                                          -- Ghi chú hóa đơn
    created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
    FOREIGN KEY (seller_code) REFERENCES DIM_EMPLOYEES(employee_code) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (technician_code) REFERENCES DIM_EMPLOYEES(employee_code) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (branch_code) REFERENCES DIM_BRANCHES(branch_code) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (customer_code) REFERENCES DIM_CUSTOMERS(customer_code) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (order_code) REFERENCES FACT_ORDERS(order_code) ON UPDATE CASCADE ON DELETE SET NULL,
    CHECK (invoice_code LIKE 'HDIP%' OR invoice_code LIKE 'HD%'),           -- Rule R1
    CHECK (ROUND(pay_cash + pay_card + pay_transfer + pay_installment, 2) >= ROUND(amount_due, 2) - 1.0) -- Rule R3 (dung sai 1đ)
);

CREATE INDEX idx_invoices_customer ON FACT_INVOICES(customer_code);
CREATE INDEX idx_invoices_seller ON FACT_INVOICES(seller_code);
CREATE INDEX idx_invoices_branch ON FACT_INVOICES(branch_code);
CREATE INDEX idx_invoices_time ON FACT_INVOICES(invoice_time);

-- ----------------------------------------------------------------------------
-- 9. BẢNG CHI TIẾT HÓA ĐƠN BÁN HÀNG (FACT_INVOICES_LINES)
-- ----------------------------------------------------------------------------
CREATE TABLE FACT_INVOICES_LINES (
    invoice_line_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Khóa chính dòng hóa đơn
    invoice_code TEXT NOT NULL,                         -- Mã hóa đơn
    product_code TEXT NOT NULL,                         -- Mã sản phẩm
    quantity INTEGER NOT NULL CHECK (quantity > 0),     -- Số lượng mua (> 0)
    unit_price REAL NOT NULL CHECK (unit_price >= 0),   -- Giá bán thực tế trên đơn vị
    cost_price REAL NOT NULL CHECK (cost_price >= 0),   -- Giá vốn tại thời điểm bán (để tính lãi gộp tức thời)
    line_discount_percent REAL NOT NULL DEFAULT 0.0 CHECK (line_discount_percent BETWEEN 0.0 AND 100.0),
    line_discount_amount REAL NOT NULL DEFAULT 0.0 CHECK (line_discount_amount >= 0),
    line_total REAL NOT NULL CHECK (line_total >= 0),   -- Thành tiền (quantity * unit_price - line_discount_amount)
    warranty_months INTEGER NOT NULL DEFAULT 12 CHECK (warranty_months >= 0),
    created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
    FOREIGN KEY (invoice_code) REFERENCES FACT_INVOICES(invoice_code) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (product_code) REFERENCES DIM_PRODUCTS(product_code) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX idx_invoice_lines_invoice ON FACT_INVOICES_LINES(invoice_code);
CREATE INDEX idx_invoice_lines_product ON FACT_INVOICES_LINES(product_code);

-- ----------------------------------------------------------------------------
-- 10. BẢNG CHI TIẾT SERIAL XUẤT BÁN CHO HÓA ĐƠN (FACT_INVOICE_SERIALS)
-- Ánh xạ 1:N giữa 1 dòng hóa đơn và danh sách Serial/IMEI thực tế bàn giao cho khách
-- ----------------------------------------------------------------------------
CREATE TABLE FACT_INVOICE_SERIALS (
    invoice_serial_id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_line_id INTEGER NOT NULL,                   -- Dòng hóa đơn
    invoice_code TEXT NOT NULL,                         -- Mã hóa đơn
    serial_number TEXT NOT NULL UNIQUE,                 -- Số Serial/IMEI đã giao
    product_code TEXT NOT NULL,                         -- Mã SKU
    created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
    FOREIGN KEY (invoice_line_id) REFERENCES FACT_INVOICES_LINES(invoice_line_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (invoice_code) REFERENCES FACT_INVOICES(invoice_code) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (serial_number) REFERENCES DIM_PRODUCT_SERIALS(serial_number) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (product_code) REFERENCES DIM_PRODUCTS(product_code) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX idx_inv_serials_serial ON FACT_INVOICE_SERIALS(serial_number);
CREATE INDEX idx_inv_serials_invoice ON FACT_INVOICE_SERIALS(invoice_code);

-- ----------------------------------------------------------------------------
-- 11. BẢNG THEO DÕI BẢO HÀNH THIẾT BỊ (FACT_WARRANTIES)
-- Đặc thù ngành điện máy: Quản lý kích hoạt bảo hành điện tử, lịch sử sửa chữa/đổi trả
-- ----------------------------------------------------------------------------
CREATE TABLE FACT_WARRANTIES (
    warranty_id INTEGER PRIMARY KEY AUTOINCREMENT,
    serial_number TEXT NOT NULL,                        -- Số Serial/IMEI thiết bị
    product_code TEXT NOT NULL,                         -- Mã hàng SKU
    customer_code TEXT NOT NULL,                        -- Khách hàng sở hữu
    invoice_code TEXT NOT NULL,                         -- Hóa đơn mua hàng ban đầu
    warranty_start_date TEXT NOT NULL,                  -- Ngày bắt đầu bảo hành (thường là ngày mua)
    warranty_end_date TEXT NOT NULL,                    -- Ngày hết hạn bảo hành
    status TEXT NOT NULL DEFAULT 'Hiệu lực' CHECK (status IN ('Hiệu lực', 'Hết hạn', 'Đang xử lý sửa chữa', 'Đã đổi mới máy')),
    claim_count INTEGER NOT NULL DEFAULT 0 CHECK (claim_count >= 0), -- Số lần mang đến bảo hành
    created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
    FOREIGN KEY (serial_number) REFERENCES DIM_PRODUCT_SERIALS(serial_number) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (product_code) REFERENCES DIM_PRODUCTS(product_code) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (customer_code) REFERENCES DIM_CUSTOMERS(customer_code) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (invoice_code) REFERENCES FACT_INVOICES(invoice_code) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX idx_warranties_serial ON FACT_WARRANTIES(serial_number);
CREATE INDEX idx_warranties_customer ON FACT_WARRANTIES(customer_code);
CREATE INDEX idx_warranties_end_date ON FACT_WARRANTIES(warranty_end_date);

-- ============================================================================
DROP VIEW IF EXISTS VW_DAILY_SALES_PERFORMANCE;
DROP VIEW IF EXISTS VW_CUSTOMER_RFM_METRICS;
DROP VIEW IF EXISTS VW_PRODUCT_PERFORMANCE;

-- View 1: Tổng quan chỉ số kinh doanh hàng ngày (Daily Sales & Gross Profit KPI)
CREATE VIEW IF NOT EXISTS VW_DAILY_SALES_PERFORMANCE AS
SELECT 
    DATE(i.invoice_time) AS sale_date,
    COUNT(DISTINCT i.invoice_code) AS total_orders,
    COUNT(DISTINCT i.customer_code) AS unique_customers,
    ROUND(SUM(i.amount_due), 2) AS total_revenue,
    ROUND(SUM(l.quantity * l.cost_price), 2) AS total_cogs,
    ROUND(SUM(l.line_total) - SUM(l.quantity * l.cost_price), 2) AS gross_profit,
    ROUND(AVG(i.amount_due), 2) AS average_order_value
FROM FACT_INVOICES i
JOIN FACT_INVOICES_LINES l ON i.invoice_code = l.invoice_code
GROUP BY DATE(i.invoice_time);

-- View 2: Ma trận dữ liệu RFM khách hàng (Customer RFM Analysis)
CREATE VIEW IF NOT EXISTS VW_CUSTOMER_RFM_METRICS AS
SELECT 
    c.customer_code,
    c.customer_name,
    c.phone,
    c.customer_type,
    MAX(i.invoice_time) AS last_purchase_date,
    CAST(JULIANDAY('now', 'localtime') - JULIANDAY(MAX(i.invoice_time)) AS INTEGER) AS recency_days,
    COUNT(DISTINCT i.invoice_code) AS frequency,
    ROUND(SUM(i.amount_due), 2) AS monetary
FROM DIM_CUSTOMERS c
LEFT JOIN FACT_INVOICES i ON c.customer_code = i.customer_code
GROUP BY c.customer_code, c.customer_name, c.phone, c.customer_type;

-- View 3: Hiệu suất sản phẩm và cảnh báo tồn kho (Product Turnover & Inventory Health)
CREATE VIEW IF NOT EXISTS VW_PRODUCT_PERFORMANCE AS
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
    COALESCE(SUM(l.quantity), 0) AS total_units_sold,
    COALESCE(ROUND(SUM(l.line_total), 2), 0.0) AS total_sales_volume,
    COALESCE(ROUND(SUM(l.line_total - (l.quantity * l.cost_price)), 2), 0.0) AS total_profit,
    CASE 
        WHEN p.stock_on_hand <= p.min_stock THEN 'Cảnh báo: Cần nhập gấp'
        WHEN p.stock_on_hand > p.max_stock THEN 'Cảnh báo: Tồn kho quá cao'
        ELSE 'Tồn kho an toàn'
    END AS inventory_status
FROM DIM_PRODUCTS p
LEFT JOIN FACT_INVOICES_LINES l ON p.product_code = l.product_code
GROUP BY p.product_code;

-- View 4: Tổng quan dòng hàng 4 trạng thái (SOH, RES, AVL, INC) & Cảnh báo dòng tiền
DROP VIEW IF EXISTS VW_INVENTORY_FLOW_OVERVIEW;
CREATE VIEW IF NOT EXISTS VW_INVENTORY_FLOW_OVERVIEW AS
SELECT 
    p.product_code,
    p.product_name,
    p.category_path,
    p.brand,
    p.cost_price,
    p.sale_price,
    p.has_serial,
    p.stock_on_hand AS soh,
    COALESCE(res.reserved_qty, 0) AS res,
    (p.stock_on_hand - COALESCE(res.reserved_qty, 0)) AS avl,
    COALESCE(inc.in_transit_qty, 0) AS inc,
    (p.stock_on_hand - COALESCE(res.reserved_qty, 0) + COALESCE(inc.in_transit_qty, 0)) AS projected_stock,
    p.min_stock,
    p.max_stock,
    ROUND(p.stock_on_hand * p.cost_price, 2) AS capital_tied,
    CASE 
        WHEN p.stock_on_hand <= p.min_stock THEN 'Cảnh báo: Cần nhập gấp'
        WHEN p.stock_on_hand > p.max_stock THEN 'Cảnh báo: Tồn kho quá cao'
        ELSE 'Tồn kho an toàn'
    END AS inventory_status,
    CASE
        WHEN (p.stock_on_hand - COALESCE(res.reserved_qty, 0)) > 0 THEN 'Sẵn sàng bán'
        WHEN COALESCE(inc.in_transit_qty, 0) > 0 THEN 'Chờ hàng đang về'
        ELSE 'Hết hàng (OOS)'
    END AS flow_status
FROM DIM_PRODUCTS p
LEFT JOIN (
    SELECT fol.product_code, SUM(fol.quantity) AS reserved_qty
    FROM FACT_ORDERS_LINES fol
    JOIN FACT_ORDERS fo ON fol.order_code = fo.order_code
    WHERE fo.status IN ('Chờ xử lý', 'Đã xác nhận')
    GROUP BY fol.product_code
) res ON p.product_code = res.product_code
LEFT JOIN (
    SELECT poi.product_code, SUM(poi.quantity) AS in_transit_qty
    FROM PO_ITEMS poi
    JOIN PURCHASE_ORDERS po ON poi.purchase_code = po.purchase_code
    WHERE po.status = 'Đang vận chuyển'
    GROUP BY poi.product_code
) inc ON p.product_code = inc.product_code;

-- ============================================================================
-- 13. TRIGGERS KIỂM SOÁT TỰ ĐỘNG CÁC RÀNG BUỘC NGHIỆP VỤ ĐIỆN MÁY
-- ============================================================================

-- Rule R5: Kiểm soát tính hợp lệ của Khách hàng tổ chức / Doanh nghiệp
CREATE TRIGGER IF NOT EXISTS TRG_CHECK_CUSTOMER_COMPANY_INSERT
BEFORE INSERT ON DIM_CUSTOMERS
FOR EACH ROW
WHEN NEW.customer_type = 'Công ty' AND (NEW.tax_code IS NULL OR LENGTH(TRIM(NEW.tax_code)) < 10 OR NEW.company IS NULL OR LENGTH(TRIM(NEW.company)) = 0)
BEGIN
    SELECT RAISE(ABORT, 'Lỗi R5: Khách hàng tổ chức/Công ty bắt buộc phải có Tên công ty và Mã số thuế từ 10-14 ký tự!');
END;

CREATE TRIGGER IF NOT EXISTS TRG_CHECK_CUSTOMER_COMPANY_UPDATE
BEFORE UPDATE ON DIM_CUSTOMERS
FOR EACH ROW
WHEN NEW.customer_type = 'Công ty' AND (NEW.tax_code IS NULL OR LENGTH(TRIM(NEW.tax_code)) < 10 OR NEW.company IS NULL OR LENGTH(TRIM(NEW.company)) = 0)
BEGIN
    SELECT RAISE(ABORT, 'Lỗi R5: Khách hàng tổ chức/Công ty bắt buộc phải có Tên công ty và Mã số thuế từ 10-14 ký tự!');
END;

-- Rule R2: Kiểm tra trạng thái tồn kho và vị trí chi nhánh của Serial trước khi bán
CREATE TRIGGER IF NOT EXISTS TRG_CHECK_SERIAL_BEFORE_SALE
BEFORE INSERT ON FACT_INVOICE_SERIALS
FOR EACH ROW
BEGIN
    SELECT 
        CASE 
            WHEN (SELECT status FROM DIM_PRODUCT_SERIALS WHERE serial_number = NEW.serial_number) IS NULL THEN
                RAISE(ABORT, 'Lỗi R2: Số Serial/IMEI không tồn tại trong danh mục thiết bị của kho!')
            WHEN (SELECT status FROM DIM_PRODUCT_SERIALS WHERE serial_number = NEW.serial_number) != 'IN_STOCK' THEN
                RAISE(ABORT, 'Lỗi R2: Thiết bị có số Serial/IMEI này không ở trạng thái tồn kho (IN_STOCK), không thể xuất bán!')
            WHEN (SELECT branch_code FROM DIM_PRODUCT_SERIALS WHERE serial_number = NEW.serial_number) != (SELECT branch_code FROM FACT_INVOICES WHERE invoice_code = NEW.invoice_code) THEN
                RAISE(ABORT, 'Lỗi R2: Thiết bị có số Serial này đang ở chi nhánh khác, không khớp với chi nhánh lập hóa đơn!')
        END;
END;

-- Rule R2 & R4: Tự động đổi trạng thái Serial, trừ tồn kho SKU và kích hoạt Bảo hành điện tử
CREATE TRIGGER IF NOT EXISTS TRG_ON_SERIAL_SOLD
AFTER INSERT ON FACT_INVOICE_SERIALS
FOR EACH ROW
BEGIN
    -- 1. Chuyển trạng thái Serial sang SOLD và lưu mã hóa đơn
    UPDATE DIM_PRODUCT_SERIALS 
    SET status = 'SOLD', sold_invoice_code = NEW.invoice_code
    WHERE serial_number = NEW.serial_number;

    -- 2. Tự động giảm số lượng tồn kho của SKU trong kho
    UPDATE DIM_PRODUCTS 
    SET stock_on_hand = stock_on_hand - 1
    WHERE product_code = NEW.product_code;

    -- 3. Tự động kích hoạt phiếu bảo hành điện tử chính hãng (Rule R4)
    INSERT INTO FACT_WARRANTIES (
        serial_number,
        product_code,
        customer_code,
        invoice_code,
        warranty_start_date,
        warranty_end_date,
        status,
        claim_count
    )
    VALUES (
        NEW.serial_number,
        NEW.product_code,
        (SELECT customer_code FROM FACT_INVOICES WHERE invoice_code = NEW.invoice_code),
        NEW.invoice_code,
        (SELECT DATE(invoice_time) FROM FACT_INVOICES WHERE invoice_code = NEW.invoice_code),
        DATE((SELECT invoice_time FROM FACT_INVOICES WHERE invoice_code = NEW.invoice_code), '+' || (SELECT warranty_months FROM DIM_PRODUCTS WHERE product_code = NEW.product_code) || ' months'),
        'Hiệu lực',
        0
    );
END;

-- ============================================================================
-- 14. CÁC BẢNG NGHIỆP VỤ MỞ RỘNG CHO MODULE 02 - 06 (STOCK SENSE V2)
-- ============================================================================

-- M2 (FR-ACT-04): Nhật ký tạm hoãn cảnh báo tồn kho (Snooze Log)
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

-- M3 (FR-CLR-05): Radar đối chiếu giá thị trường & đối thủ cạnh tranh
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

-- M3 (FR-CLR-01..04): Chiến dịch xả hàng thông minh
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

-- M5 (FR-CRM-03..04): Nhật ký tương tác CSKH & Kiểm soát Cooldown 30 ngày
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

-- M5 (FR-CRM-05): Lịch hẹn Kỹ thuật viên bảo dưỡng / lắp đặt tại nhà
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

-- M6 (FR-PRF-04): Sổ hoa hồng bán kèm Phụ kiện & Dịch vụ
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
