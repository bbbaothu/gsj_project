# KẾ HOẠCH TRIỂN KHAI NÂNG CẤP GIAO DIỆN & TÍNH NĂNG TOÀN DIỆN (IMPLEMENTATION PLAN V2)
## HỆ THỐNG QUẢN TRỊ KHO & ĐIỀU HÀNH ĐIỆN MÁY THÔNG MINH - STOCK SENSE (6 MODULES)
### Nền tảng: Plotly Dash, Plotly Graph Objects, Tailwind Design Tokens & SQLite
#### Phương pháp luận: Test-Driven Development (TDD: Red → Green → Visual Verify → Commit)

> **Hướng dẫn thực thi:** Lần lượt triển khai theo từng Giai đoạn từ 1 đến 8. Sau mỗi bước phải chạy `unittest` xác nhận xanh (`OK`), kiểm tra ảnh chụp Chrome `1440×1400` bằng Chrome DevTools Protocol và cập nhật dấu tích (`[x]`) vào tài liệu này trước khi commit.

**Goal:** Nâng cấp toàn diện ứng dụng Plotly Dash trong [src/app_dashboard.py](file:///Users/doanphambaothu/Documents/gsj_project/src/app_dashboard.py) và các phân hệ `src/dash_app/` + `src/services/` nhằm đồng bộ 100% thẩm mỹ, typography, thuật ngữ thuần Việt dễ hiểu cho chủ cửa hàng điện máy Việt Nam, và đầy đủ các tính năng/biểu đồ mới theo đúng [prototypes/stock_sense_dashboard.html](file:///Users/doanphambaothu/Documents/gsj_project/prototypes/stock_sense_dashboard.html) cùng 7 nhóm yêu cầu chi tiết.

**Architecture:** Kế thừa kiến trúc 3 tầng đã xây dựng:
1. **Tầng Dữ liệu (`data/retail_dienmay.db`):** Mở rộng có kiểm soát dữ liệu tồn kho/nhu cầu để Module 04 có nhiều mã đề xuất nhập ở nhiều hãng khác nhau, và dữ liệu lịch sử dịch vụ/chăm sóc khách hàng theo các mốc `14 ngày / 30 ngày / 3 tháng` cho biểu đồ tròn doanh thu Module 05 — bảo toàn nguyên vẹn toàn bộ bất biến kiểm thử (`total_skus == 12`, `len(DIM_PRODUCTS) == 16`, `overstock_count == 3`, 63 tests hiện tại Pass).
2. **Tầng Nghiệp vụ (`src/services/*_service.py`):** Bổ sung các hàm truy vấn/tính toán phục vụ: vốn kẹt trong đơn giữ quá hạn & chi tiết khách hàng đơn giữ (M1), cơ cấu doanh thu 5 dịch vụ CSKH theo khoảng thời gian (M5), tính lại xếp hạng & hoa hồng theo chính sách thưởng tùy biến (M6), và phân bổ đa dạng mã nhập (M4).
3. **Tầng Giao diện Plotly Dash (`src/dash_app/` & `src/assets/`):** Tinh chỉnh CSS tokens (`Inter` + `JetBrains Mono`, `.gap-pattern`, `.frozen-striped-bar`, `.cell-hscroll`, bảng màu pastel theo từng Hãng), loại bỏ mọi từ viết tắt khó hiểu (`DOS`, `DSI`, `SKU`, `INC`, `SOH`, `RES`, `AVL`, `PO`, `MOQ`, `PAI`, `Attach-Rate`), thiết kế lại bố cục biểu đồ và tương tác trên từng phân hệ M1–M6.

**Tech Stack:** Python 3.9+, Plotly Dash `2.18.2`, Plotly (`plotly.graph_objects`, `plotly.express`), Tailwind CSS Design Tokens, Pandas, SQLite 3, `unittest`.

**Spec & Reference:**
- Bản mẫu chuẩn: [prototypes/stock_sense_dashboard.html](file:///Users/doanphambaothu/Documents/gsj_project/prototypes/stock_sense_dashboard.html)
- Tài liệu kế hoạch tham chiếu cấu trúc: [docs/IMPLEMENTATION_PLAN_STOCK_SENSE.md](file:///Users/doanphambaothu/Documents/gsj_project/docs/IMPLEMENTATION_PLAN_STOCK_SENSE.md)
- Bộ đặc tả SRS: `docs/SRS_01_TONG_QUAN_KHO.md` đến `docs/SRS_06_HIEU_QUA_KINH_DOANH.md`

---

## BẢNG KIỂM SOÁT TÀI LIỆU (DOCUMENT CONTROL)

| Mục | Nội dung |
| :--- | :--- |
| **Mã tài liệu** | `PLAN-DASH-PARITY-V2-STOCK-SENSE` |
| **Tài liệu tiền nhiệm** | [docs/IMPLEMENTATION_PLAN_PLOTLY_DASH_STOCK_SENSE.md](file:///Users/doanphambaothu/Documents/gsj_project/docs/IMPLEMENTATION_PLAN_PLOTLY_DASH_STOCK_SENSE.md) |
| **Phiên bản** | `2.1.0` (UI/UX Prototype Parity & Domain Enhancements) |
| **Ngày lập kế hoạch** | 18/11/2026 |
| **Đơn vị vận hành mẫu** | **Cửa hàng Điện máy Anh Tâm** (`CN01`, 108 Cầu Giấy, Hà Nội) |
| **Mô hình phát triển** | Test-Driven Development (`Red` → `Green` → `Chrome Visual Parity` → `Commit`) |

---

## RÀNG BUỘC TOÀN CỤC & ĐIỂM TRỌNG TÂM KIỂM TRA (GLOBAL CONSTRAINTS & REVIEW FOCUS)

### Global Constraints
1. **Bảo mật Phân quyền Giá vốn (`ROLE_OWNER` vs `ROLE_SALES`):** Mọi chỉ số mới bổ sung (vốn kẹt trong đơn giữ quá hạn M1, Hover Tooltip vốn kẹt trong Pie Chart M2, giá vốn trong thanh so sánh PA1–PA4 M3, cấu hình % thưởng M6) bắt buộc che `"****** đ"` hoặc khóa thao tác ghi khi chuyển sang `ROLE_SALES`.
2. **Bảo toàn Test Suite hiện hữu (Zero Regression):** Tất cả 63 bài kiểm thử hiện tại (39 tests tầng Service/Integration + 24 tests Dash Shell/M1–M6/E2E) phải tiếp tục chạy Pass 100%, đặc biệt các ràng buộc số lượng trên `DIM_PRODUCTS` (`16` dòng, `12` SKU chính, `3` mã vượt trần) và `test_order_service` (`AVL = SOH - RES`).
3. **Thuần Việt 100% trên Giao diện Người dùng (Plain Vietnamese UX):** Tuyệt đối không hiển thị các cụm viết tắt học thuật/kho vận tiếng Anh thô (`DOS`, `DSI`, `SKU`, `INC`, `SOH`, `RES`, `AVL`, `PO`, `MOQ`, `PAI`, `Cooldown`, `Attach-Rate`, `Lead Time`, `Waterfall`) trên nhãn nút, tiêu đề cột, huy hiệu hay chú giải biểu đồ.
4. **Chuẩn Typography & Brand Color Coding:** Dùng thống nhất font `Inter` cho mọi tiêu đề/nội dung và `JetBrains Mono` riêng cho mã sản phẩm, mã đơn, mã vận đơn và các con số bảng (`tabular-nums`); mỗi Hãng (`Daikin`, `Sony`, `Casper`, `Toshiba`, `LG`, `Samsung`, `Panasonic`, `Aqua`) dùng một bộ màu pastel đồng nhất xuyên suốt M1–M4.

### Review Focus (5 Tình huống bắt buộc kiểm chứng)
1. **Từ thẻ `Đơn giữ quá hạn` M1 nhảy thẳng tới danh sách xử lý đơn gấp:** Khi bấm `Xử lý đơn →` trên thẻ KPI 3 của Module 01, khối `Quản lý những đơn giữ chỗ` bên dưới tự động chuyển sang tab lọc `Cần xử lý gấp (Quá hạn 48h)` và bấm `Xử lý` mở Modal chi tiết khách hàng kèm thao tác `Hủy đơn & Nhả giữ chỗ` ghi xuống SQLite.
2. **Chữ trên Scatter M1 & Ô bảng M2 không đè / không mất thông tin:** Nhãn tên ngắn trên Ma trận Sức khỏe Tồn kho M1 được phân tầng vị trí tránh đè lên bóng khác và có Tooltip đầy đủ 4 trường; các ô cột trong bảng M2 hỗ trợ trượt ngang (`.cell-hscroll`) xem trọn vẹn nội dung dài.
3. **Pie Chart M2 & M5 đúng dải màu và Tooltip nghiệp vụ:** M2 dùng dải màu khẩn cấp Vàng → Cam → Đỏ → Nâu đỏ theo % vốn kẹt; M5 đổi sang Pie Chart % doanh thu theo 5 dịch vụ CSKH lọc được theo `14 ngày / 30 ngày / 3 tháng` với Hover hiển thị số đơn hàng.
4. **Chiều cao đối xứng 7:5 ở Module 05:** Cột trái (Bảng KH có Header & bộ lọc cố định + danh sách trượt dọc bên trong) khớp chiều cao với cột phải (Card Biểu đồ Pie ở trên + Card Hồ sơ tác chiến cuộc gọi ở dưới).
5. **Thay đổi Chính sách Thưởng trực tiếp ở Module 06:** Điều chỉnh `% Phụ kiện`, `% Dịch vụ`, `Thưởng nóng/ca` và `Tiêu chí xếp hạng` tính toán lại ngay hạng `#1–#3`, Quỹ chi và mức thưởng từng nhân sự.

---

## 1. TỔNG QUAN & PHẠM VI NÂNG CẤP 7 NHÓM YÊU CẦU (SCOPE MATRIX)

| Nhóm yêu cầu | File tác động chính | Thay đổi Giao diện & Tính năng trọng tâm | Trạng thái |
| :--- | :--- | :--- | :---: |
| **1. Toàn hệ thống (Thuật ngữ, Font & Màu Hãng)** | `src/assets/stock_sense.css`<br>`layout_shell.py`<br>`m1..m6` pages & callbacks | • Bảng ánh xạ chuẩn 100% thuật ngữ Việt dễ hiểu cho chủ tiệm trung niên<br>• Chuẩn hóa `Inter` (display/body) + `JetBrains Mono` (mã SP, mã đơn, số)<br>• Bảng màu pastel riêng cho từng Hãng đồng bộ M1–M4 | ✅ **ĐÃ HOÀN THÀNH** |
| **2. Module 01: Tổng quan kho** | `order_service.py`<br>`m1_overview.py`<br>`m1_callbacks.py` | • Thẻ 3 KPI hiện **vốn kẹt trong đơn giữ quá hạn** (`Kẹt XX,X tr`) + link xuống tab Gấp<br>• Cột Sức khỏe có **căn cứ số liệu** dưới thanh màu; nút `"Lọc thêm"` lọc Hãng/Ngành/Kệ<br>• **Ma trận full-width** dùng tên ngắn chống đè + Hover chi tiết<br>• Bỏ ô Đơn giữ bên phải $\rightarrow$ thêm **khối Quản lý những đơn giữ chỗ** + Modal xử lý/hủy đơn | ✅ **ĐÃ HOÀN THÀNH** |
| **3. Module 02: Cần xử lý hôm nay** | `m2_alerts.py`<br>`m2_callbacks.py` | • Đổi bar chart Vốn kẹt sang **Pie chart dải Vàng–Cam–Đỏ–Nâu đỏ** + Tooltip 4 thông tin<br>• Bỏ graph Đường băng tồn kho vs Thời gian hãng giao<br>• Cấu trúc bảng 7 cột y hệt Ảnh 1/Prototype + **trượt ngang trong ô (`.cell-hscroll`)** | ✅ **ĐÃ HOÀN THÀNH** |
| **4. Module 03: Gợi ý xả hàng** | `clearance_service.py`<br>`m3_clearance.py`<br>`m3_callbacks.py` | • Bỏ chart So sánh 4 chiến thuật riêng $\rightarrow$ **nhúng thanh dòng tiền vào từng Phương án PA1–PA4**<br>• Đồng bộ **100% Ảnh 2**: Header lý do, Slider Giá/SL, nút Khớp giá đối thủ, Cắt lỗ `-5%`<br>• Radar Giá: nút `Giả lập mất mạng`, **Thang định vị giá & Sàn vốn**, Box `..90k` + **Nhận định chiến lược** | ✅ **ĐÃ HOÀN THÀNH** |
| **5. Module 04: Gợi ý nhập hàng** | `data/retail_dienmay.db`<br>`replenishment_service.py`<br>`m4_replenishment.py`, `m4_callbacks.py` | • Bỏ 2 biểu đồ dự báo & phân bổ theo Hãng<br>• Tinh chỉnh/bổ sung điều kiện & vận tốc dữ liệu để có **5–6 mã đề xuất nhập** nhiều hãng<br>• Cột Nhu cầu dùng **sọc pastel chéo (`.gap-pattern`)** ở phần thiếu; màu badge theo từng hãng | ✅ **ĐÃ HOÀN THÀNH** |
| **6. Module 05: Chăm sóc khách hàng** | `crm_service.py`<br>`m5_crm.py`<br>`m5_callbacks.py` | • Đổi chart 5 điểm chạm thành **Pie chart % Doanh thu CSKH** + lọc `14 ngày / 30 ngày / 3 tháng` + Hover số đơn<br>• Bỏ chart Donut ưu tiên; chuyển Pie chart lên **phía trên Hồ sơ cuộc gọi** bên cột phải<br>• Cột trái 7 phần: **Header + Bộ lọc cố định + Bảng trượt dọc** có chiều cao cân bằng cột phải | ⏳ **KẾ HOẠCH** |
| **7. Module 06: Hiệu quả kinh doanh** | `performance_service.py`<br>`m6_performance.py`<br>`m6_callbacks.py` | • Thêm khối **Điều chỉnh Chính sách Thưởng** (`% Phụ kiện`, `% Dịch vụ`, `Thưởng nóng/ca`, `Tiêu chí xếp hạng`) tính lại xếp hạng & tiền thưởng trực tiếp trong thẻ nhân viên | ⏳ **KẾ HOẠCH** |

---

## 2. KIẾN TRÚC MÃ NGUỒN & TỪ ĐIỂN THUẬT NGỮ CHUẨN HÓA

### 2.1. Từ điển Việt hóa thuật ngữ toàn hệ thống (Glossary Mapping)
Mọi màn hình từ M1 đến M6 đều tuân thủ ánh xạ sau để chủ cửa hàng không gặp từ viết tắt tiếng Anh:

| Thuật ngữ cũ (Cần thay thế) | Thuật ngữ tiếng Việt chuẩn hóa trên UI mới |
| :--- | :--- |
| `SKU` / `Mã SKU` | **Mã sản phẩm** / **Mã hàng** / **Mặt hàng** |
| `SOH` | **Tồn thực tế** (hoặc **Tổng tồn kho**) |
| `RES` | **Đang giữ chỗ** |
| `AVL` | **Có thể bán ngay** (hoặc **Bán ngay**) |
| `INC` | **Hàng đang về** / **Xe đang về** |
| `DSI` | **Ngày tồn đọng** (VD: `Chậm 49 ngày`, `Đóng băng 68 ngày`) |
| `DOS` | **Số ngày đủ bán** (VD: `Đủ bán 1,8 ngày`, `Cạn kho (0 ngày)`) |
| `Lead Time` | **Thời gian hãng giao** (VD: `Giao: 4 ngày`) |
| `PO` / `PO Lifecycle` | **Đơn đặt nhập** / **Theo dõi đơn nhập hàng** |
| `MOQ` / `Pack size` | **Đặt tối thiểu** / **Quy cách kiện** |
| `PAI` | **Chênh lệch so với thị trường** (`Rẻ hơn X%`) |
| `Attach-Rate` | **Tỷ lệ bán kèm** |
| `Cooldown 30d` | **Chặn gọi trùng 30 ngày** |
| `Backorder` | **Đơn nợ giao khách** |

### 2.2. Bảng màu nhận diện theo từng Hãng sản xuất (Brand Badge Map)
Đưa thành helper dùng chung `get_brand_badge_class(brand)` trong `src/dash_app/components/layout_shell.py`:
- `Daikin`: `bg-sky-50 text-sky-700 border-sky-200`
- `Sony`: `bg-indigo-50 text-indigo-700 border-indigo-200`
- `Casper`: `bg-amber-50 text-amber-800 border-amber-200`
- `Toshiba`: `bg-teal-50 text-teal-700 border-teal-200`
- `LG`: `bg-rose-50 text-rose-700 border-rose-200`
- `Samsung`: `bg-blue-50 text-blue-700 border-blue-200`
- `Panasonic`: `bg-emerald-50 text-emerald-700 border-emerald-200`
- `Aqua` / `Electrolux` / `Sanaky`: `bg-cyan-50 text-cyan-800 border-cyan-200` / `bg-purple-50 text-purple-700 border-purple-200` / `bg-slate-100 text-slate-700 border-slate-200`

---

## 3. LỘ TRÌNH TRIỂN KHAI CHI TIẾT THEO GIAI ĐOẠN (TDD ROADMAP)

### GIAI ĐOẠN 1: CHUẨN HÓA DESIGN ASSETS, FONT CHỮ & TỪ ĐIỂN THUẬT NGỮ TOÀN CỤC
**Thời lượng dự kiến:** 0.5 ngày | **Mục tiêu:** Đảm bảo nền CSS, Typography (`Inter` + `JetBrains Mono`), sọc pastel `.gap-pattern`, sọc đóng băng `.frozen-striped-bar`, trượt ngang `.cell-hscroll`, bảng màu Hãng và thuật ngữ tiếng Việt đồng bộ từ App Shell xuống các trang.

#### Task 1: CSS Utilities, Font Rule & `layout_shell.py` Việt hóa
* **Thông tin chức năng:**
  - Cập nhật [src/assets/stock_sense.css](file:///Users/doanphambaothu/Documents/gsj_project/src/assets/stock_sense.css): thêm `.gap-pattern` (pastel hồng chéo theo Prototype L208–L216), `.frozen-striped-bar` (L153–L163), `.cell-hscroll` (`overflow-x: auto; scrollbar-width: thin;` để trượt ngang xem hết nội dung ô bảng M2), chuẩn hóa rule `.font-code` / `.font-mono` ép `JetBrains Mono` cho mã sản phẩm/mã đơn và `Inter` làm font mặc định toàn bộ giao diện.
  - Cập nhật [src/dash_app/components/layout_shell.py](file:///Users/doanphambaothu/Documents/gsj_project/src/dash_app/components/layout_shell.py): thêm `get_brand_badge_class(brand)`, `get_short_product_name(name)`, đổi chữ `"Ctrl K"` / `"Đơn nhập & Giữ cọc"` / mô tả Sidebar & Topbar sang thuần Việt dễ hiểu (`Tìm tên hàng, mã sản phẩm...`, `Phiếu nhập & Giữ cọc`).
* **Files:**
  - Modify: `src/assets/stock_sense.css`, `src/dash_app/components/layout_shell.py`, `src/dash_app/callbacks/global_callbacks.py`, `tests/test_dash_shell.py`
* **Cách thức triển khai (TDD):**
  - [x] **Step 1 (RED):** Mở rộng `tests/test_dash_shell.py` kiểm tra helper `get_brand_badge_class`, `get_short_product_name`, kiểm tra `stock_sense.css` có đủ `.gap-pattern`, `.frozen-striped-bar`, `.cell-hscroll`, và kiểm tra Topbar/Sidebar không chứa chữ viết tắt thô (`SKU`, `PO`, `SOH`, `DSI`, `DOS`, `INC`).
  - [x] **Step 2:** Chạy `tests/test_dash_shell.py` xác nhận **RED**.
  - [x] **Step 3 (GREEN):** Cập nhật CSS, `layout_shell.py` và `global_callbacks.py`.
  - [x] **Step 4:** Chạy `tests/test_dash_shell.py` xác nhận **GREEN**. (`Ran 5 tests in 0.370s - OK`)
  - [x] **Step 5:** Cập nhật Plan & Commit (`style(dash-global): unify plain Vietnamese terminology, fonts and brand color badges`).

---

### GIAI ĐOẠN 2: NÂNG CẤP TẦNG SERVICE & BỔ SUNG DỮ LIỆU THỰC NGHIỆM (M1, M4, M5, M6)
**Thời lượng dự kiến:** 1.0 ngày | **Mục tiêu:** Cung cấp đầy đủ API và dữ liệu SQLite sạch phục vụ 100% tính năng mới trên giao diện mà không phá vỡ bất kỳ test cũ nào.

#### Task 2: Mở rộng Service M1 (`OrderService`) & Service M4 (`ReplenishmentService` + Dữ liệu đề xuất nhập)
* **Thông tin chức năng:**
  - **M1 (`OrderService`):**
    - Bổ sung trường `expired_capital` (tổng giá trị vốn/đơn bị kẹt trong các đơn giữ chỗ quá hạn `>= 48h`) vào `get_order_flow_kpis(role="ROLE_OWNER")` (trả `None` / `"****** đ"` khi `ROLE_SALES`).
    - Bổ sung hàm `get_order_detail(order_code, role="ROLE_OWNER")` trả về: `order_code`, `customer_name`, `phone`, `address`, `order_time`, `hours_held`, `is_expired`, `status`, `amount_due`, `amount_paid`, `items` (chi tiết từng mặt hàng, số lượng, thành tiền) phục vụ Modal xử lý đơn giữ chỗ ở M1.
  - **M4 (`ReplenishmentService` & `data/retail_dienmay.db`):**
    - Kiểm tra & cập nhật tham số dự báo / dữ liệu tốc độ bán cho các mã tồn thấp (`TV-SN-55X80K` Sony, `TL-PN-322L` Panasonic, `MG-TB-85K` Toshiba, `ML-DK-FTKB25` Daikin, `TV-CS-43FG6` Casper) hoặc công thức `safety_stock = max(int(r["min_stock"]), ...)` khi hàng chưa chạm trần, giúp danh sách đề xuất nhập chu kỳ `14 ngày` hiển thị **từ 4–5 mã thuộc ít nhất 3–4 hãng khác nhau** với thanh nhu cầu/khoảng thiếu sinh động (có cả mã `Đủ tồn`, mã `Có hàng đang về`, mã `Thiếu cần nhập`).
    - Bảo toàn 100% bất biến: `DIM_PRODUCTS = 16`, `has_serial = 1` (`12` SKU), `overstock_count = 3`, `all(stockouts["inc"] > 0)`.

#### Task 3: Mở rộng Service M5 (`CrmService` Pie Doanh thu Dịch vụ) & Service M6 (`PerformanceService` Chính sách Thưởng)
* **Thông tin chức năng:**
  - **M5 (`CrmService`):**
    - Bổ sung dữ liệu lịch sử dịch vụ/chăm sóc mẫu vào `FACT_SERVICE_APPOINTMENTS` rải đều trong `14 ngày`, `30 ngày` và `3 tháng` (3–90 ngày trước `2026-11-18`) ở 5 nhóm dịch vụ CSKH (`Bảo dưỡng điều hòa`, `Thay lõi máy lọc nước`, `Lắp đặt & Phụ kiện`, `Kiểm tra bảo hành`, `Chăm sóc VIP định kỳ`). (Đảm bảo KHÔNG làm trùng khung giờ/thợ test trong `test_crm_service.py`!).
    - Thêm hàm `get_service_revenue_breakdown(period_days: int = 30, ref_date: str = "2026-11-18") -> List[Dict[str, Any]]` trả về `service_group`, `order_count`, `total_revenue`, `share_pct`.
  - **M6 (`PerformanceService`):**
    - Thêm hàm `calculate_dynamic_commission_ranking(acc_rate_pct: float = 15.0, srv_rate_pct: float = 20.0, hot_bonus_per_case: float = 50_000.0, sort_by: str = "commission", role: str = "ROLE_OWNER") -> Dict[str, Any]` tính trực tiếp tiền thưởng mới cho từng nhân sự từ doanh số phụ kiện/dịch vụ trong `FACT_COMMISSION_LEDGER`, xếp hạng `#1/#2/#3` theo `sort_by` (`commission` | `attached_sales` | `attached_profit`), trả tổng `total_fund` và che `"****** đ"` khi `ROLE_SALES`.
* **Files:**
  - Modify: `src/services/order_service.py`, `src/services/replenishment_service.py`, `src/services/crm_service.py`, `src/services/performance_service.py`, `data/retail_dienmay.db`, `tests/test_service_v2_enhancements.py` (new TDD test file)
* **Cách thức triển khai (TDD):**
  - [x] **Step 1 (RED):** Viết `tests/test_service_v2_enhancements.py` kiểm tra `expired_capital` + `get_order_detail`, M4 trả `>= 4` mã đề xuất ở `>= 3` hãng, `get_service_revenue_breakdown(14/30/90)` khác nhau theo kỳ, và `calculate_dynamic_commission_ranking(acc_rate_pct=20, srv_rate_pct=25)` đổi hạng & tăng Quỹ chi.
  - [x] **Step 2:** Chạy test xác nhận **RED**.
  - [x] **Step 3 (GREEN):** Triển khai cập nhật 4 services + cập nhật DB sạch.
  - [x] **Step 4:** Chạy cả `tests/test_service_v2_enhancements.py` VÀ 39 tests cũ xác nhận **PASS 100%**. (`37/37 + 4/4 tests - OK`)
  - [x] **Step 5:** Cập nhật Plan & Commit (`feat(services): add overdue order detail, multi-vendor replenishment depth, CRM revenue periods and dynamic commission`).

---

### GIAI ĐOẠN 3: NÂNG CẤP MODULE 01 — TỔNG QUAN KHO (`m1_overview`, `m1_callbacks`)
**Thời lượng dự kiến:** 1.0 ngày | **Tham chiếu:** Yêu cầu mục (2) + Prototype `L435–L668`.

#### Task 4: KPI Vốn giữ quá hạn, Cột Sức khỏe có Căn cứ, Nút "Lọc thêm", Scatter Full-width Tên ngắn & Quản lý Đơn giữ chỗ
* **Thông tin chức năng:**
  - **KPI Card 3 (`ĐƠN GIỮ QUÁ HẠN`):** Đổi badge `"Quá 48h giữ chỗ"` thành mác **`"Kẹt XX,X tr"`** (vốn kẹt trong các đơn giữ quá hạn; ẩn `"****** đ"` nếu `ROLE_SALES`).
  - **Nút `"Lọc thêm"` & Thanh lọc nâng cao:** Đổi nút `"Biểu đồ & Đơn giữ"` thành `"Lọc thêm"`, khi bấm sẽ bật/tắt panel bộ lọc theo **Thương hiệu**, **Ngành hàng**, và **Vị trí kệ kho** (`m1ExtraFilterPanel`) để kết hợp lọc cùng 6 Filter Pills & ô tìm kiếm.
  - **Bảng sản phẩm & Sức khỏe tồn kho:**
    - Đổi tiêu đề cột sang thuần Việt (`TỒN THỰC`, `GIỮ CHỖ`, `BÁN NGAY`, `HÀNG ĐANG VỀ`, `SỨC KHỎE TỒN KHO`, `VỐN TỒN`, `HÀNH ĐỘNG`).
    - Trong cột **SỨC KHỎE TỒN KHO**: bên dưới badge trạng thái & thanh tỷ lệ màu, hiển thị **căn cứ cụ thể** ngay cạnh thanh (VD: `20 / trần 10 máy (+100%)`, `2 / tối thiểu 4 bộ (-50%)`, `+10 máy đang về bù đủ`, `10 / định mức 4–12 máy`).
  - **Ma trận Sức khỏe Tồn kho & Giá trị bán (`m1-scatter-chart` full-width):**
    - Bỏ ô side-by-side `"Đơn giữ chỗ & Chờ xử lý quá hạn 48h"` $\rightarrow$ để khối Ma trận chiếm toàn bộ 12 cột (`w-full`).
    - Đổi text trên các bóng tròn từ mã SP sang **tên sản phẩm ngắn gọn** (`LG OLED 55"`, `ĐH Daikin 1HP`, `Tủ Samsung 647L`, ...), tính toán vị trí `textposition` xen kẽ thông minh (`top center` / `bottom center` / `middle right` / `top left`) theo tọa độ gần nhau để **không bị đè chữ hay chồng bóng**.
    - Thiết lập `customdata` + `hovertemplate` hiển thị Tooltip 4 thông tin khi di chuột: **Tên sản phẩm**, **Mã sản phẩm**, **Giá niêm yết**, **Số lượng tồn thực tế & có thể bán**.
  - **Khối mới dưới Ma trận: `"Quản lý những đơn giữ chỗ"` (`m1ReservedOrdersSection`):**
    - Gồm 2 tab lọc nhanh: **`Tất cả đơn giữ`** và **`Cần xử lý gấp (Quá hạn 48h)`**, bảng danh sách hiển thị: **Mã đơn**, **Sản phẩm & Số lượng**, **Tổng giá trị**, **Thời gian giữ / Cảnh báo quá hạn**, và nút **`Xử lý`**.
    - Link nút **`Xử lý X đơn →`** trên KPI Card 3: bấm vào tự động bật tab **`Cần xử lý gấp (Quá hạn 48h)`** ở khối Quản lý đơn giữ chỗ & cuộn/đánh dấu nổi bật khối này.
    - Bấm **`Xử lý`** trên 1 đơn $\rightarrow$ mở Modal **`m1OrderDetailModal`** hiển thị: **Khách hàng**, **SĐT / Địa chỉ**, **Thời gian đặt hàng**, **Chi tiết sản phẩm / SL / Giá trị / Đã cọc**, nút **`📞 Liên hệ khách hàng`** (ghi nhận/thông báo) và **`✕ Hủy đơn & Nhả giữ chỗ`** (gọi `OrderService.cancel_order()`, cập nhật DB + refresh toàn bộ KPI & Bảng M1).
* **Files:**
  - Modify: `src/dash_app/pages/m1_overview.py`, `src/dash_app/callbacks/m1_callbacks.py`, `tests/test_dash_m1.py`
* **Cách thức triển khai (TDD):**
  - [x] **Step 1 (RED):** Cập nhật `tests/test_dash_m1.py` kiểm tra badge `"Kẹt ..."` trên Card 3 (kèm RBAC), căn cứ sức khỏe trong cột bảng, bộ lọc `"Lọc thêm"`, Scatter dùng tên ngắn + customdata, khối `Quản lý những đơn giữ chỗ` + click `Xử lý` mở Modal + hủy đơn nhả tồn (`rollback` DB sau test), và link từ Card 3 sang tab `Quá hạn 48h`.
  - [x] **Step 2:** Chạy `tests/test_dash_m1.py` xác nhận **RED**.
  - [x] **Step 3 (GREEN):** Lập trình nâng cấp `m1_overview.py` & `m1_callbacks.py`.
  - [x] **Step 4:** Chạy `tests/test_dash_m1.py` xác nhận **GREEN**.
  - [x] **Step 5:** Cập nhật Plan & Commit (`feat(dash-m1): upgrade M1 reserved orders manager, full-width scatter, health evidence and extra filters`).

---

### GIAI ĐOẠN 4: NÂNG CẤP MODULE 02 — CẦN XỬ LÝ HÔM NAY (`m2_alerts`, `m2_callbacks`)
**Thời lượng dự kiến:** 1.0 ngày | **Tham chiếu:** Yêu cầu mục (3), Ảnh đính kèm 1 & Prototype `L820–L916`, `L4055–L4110`.

#### Task 5: Pie Chart Vốn kẹt dải Vàng–Cam–Đỏ–Nâu đỏ, Bỏ Runway Chart & Bảng 7 cột Có Thanh Trượt Ngang Ô
* **Thông tin chức năng:**
  - **Biểu đồ:**
    - Đổi `"Phân bổ vốn kẹt theo mặt hàng bán chậm"` thành **Pie Chart (`go.Pie`)** hiển thị `%` vốn kẹt từng mặt hàng, dùng dải màu **Vàng – Cam – Đỏ – Nâu đỏ** (`["#7F1D1D", "#B91C1C", "#DC2626", "#EA580C", "#D97706", "#F59E0B"]`) giúp phân biệt rõ từng lát cắt và truyền tải mức độ khẩn cấp.
    - Thiết lập Hover Tooltip ngay cạnh con trỏ chuột gồm 4 thông tin: **Tên sản phẩm**, **Mã sản phẩm**, **Lượng vốn kẹt** (che `"****** đ"` nếu `ROLE_SALES`), và **Số lượng tồn thực tế**.
    - **Loại bỏ** biểu đồ `"Đường băng tồn kho (DOS) vs Ngưỡng Lead Time hãng"`. Đặt Pie Chart cùng thẻ tóm tắt phân tích Pareto 80/20 cạnh nhau hoặc căn full card cân đối đẹp mắt.
  - **Bảng cảnh báo 7 cột chuẩn Ảnh 1 & Prototype (`m2DecisionTableBody`):**
    - Giữ chính xác bố cục 7 cột theo Ảnh 1: `[Checkbox] | SẢN PHẨM & VỊ TRÍ KỆ | TỒN THỰC / ĐỊNH MỨC | TỐC ĐỘ BÁN & ĐƯỜNG BĂNG | VỐN ĐỌNG / RỦI RO | NGUYÊN NHÂN CỐT LÕI | HÀNH ĐỘNG QUYẾT ĐỊNH`.
    - Dùng thanh đường băng trực quan chuẩn Prototype (`bg-rose-600`, `.frozen-striped-bar`, `bg-amber-500`, `bg-blue-600`), nhãn tiếng Việt thuần (`Đứt kho`, `Dưới tối thiểu`, `Chậm 49 ngày`, `Đóng băng (~68 ngày không đơn)`, `Hết mùa hè · Vượt 2,3x trần`), tích hợp lọc `Hãng`, `Ngành`, `Sắp xếp` + Footer chú giải đường băng & nút 80/20 `Lọc ngay`.
    - **Trượt ngang trong từng ô bảng (`.cell-hscroll`):** Thay `truncate` cắt chữ bằng wrapper `div.cell-hscroll` (`overflow-x-auto whitespace-nowrap`) cho các ô text dài (`Sản phẩm`, `Tốc độ bán & Đường băng`, `Nguyên nhân cốt lõi`) để người dùng kéo ngang xem trọn 100% thông tin ngay trong ô!
* **Files:**
  - Modify: `src/dash_app/pages/m2_alerts.py`, `src/dash_app/callbacks/m2_callbacks.py`, `tests/test_dash_m2.py`
* **Cách thức triển khai (TDD):**
  - [x] **Step 1 (RED):** Cập nhật `tests/test_dash_m2.py` kiểm tra Pie chart dùng `go.Pie` với palette vàng–cam–đỏ–nâu đỏ & customdata Hover 4 trường, không còn Runway chart (`m2-runway-chart` removed), bảng có đủ 7 cột thuần Việt và class `.cell-hscroll` chống cắt chữ.
  - [x] **Step 2:** Chạy `tests/test_dash_m2.py` xác nhận **RED**.
  - [x] **Step 3 (GREEN):** Nâng cấp `m2_alerts.py` & `m2_callbacks.py`.
  - [x] **Step 4:** Chạy `tests/test_dash_m2.py` xác nhận **GREEN**.
  - [x] **Step 5:** Cập nhật Plan & Commit (`feat(dash-m2): convert capital chart to urgent pie, remove runway chart and match prototype h-scroll table`).

---

### GIAI ĐOẠN 5: NÂNG CẤP MODULE 03 — GỢI Ý XẢ HÀNG (`m3_clearance`, `m3_callbacks`)
**Thời lượng dự kiến:** 1.0 ngày | **Tham chiếu:** Yêu cầu mục (4), Ảnh đính kèm 2 & Prototype `L1048–L1292`.

#### Task 6: Đồng bộ 100% Ảnh 2 (Inline Bar Kịch bản, Simulator Presets & Thang định vị giá + Nhận định chiến lược)
* **Thông tin chức năng:**
  - **Cột trái 7 phần (`1. CHỌN KỊCH BẢN KHUYẾN MẠI XẢ HÀNG`):**
    - Hiển thị lý do xả & mục tiêu tồn ngay dưới tiêu đề, cùng chú giải `[■ Vốn thu hồi  ■ Lãi gộp ròng]` ở góc phải.
    - **Loại bỏ** khung biểu đồ Plotly riêng `"2. So sánh dòng tiền 4 chiến thuật"`; **nhúng trực tiếp thanh tỷ trọng 2 đoạn (Vốn thu hồi + Lãi gộp ròng)** ngay bên phải mỗi thẻ Radio `Phương án 1..4` (khớp 100% Ảnh 2 & Prototype `L4583–L4611`), kèm cột `Xả: XX tr / KM: XX đ` và `Lãi 1 máy / Tổng lãi`.
    - Nâng cấp phần **`Mô phỏng dòng tiền`** bên dưới 4 thẻ: đủ 3 nút preset (`Mặc định`, `⚡ Khớp giá đối thủ`, `Cắt lỗ (-5% vốn)`), thanh kéo **`Giá bán xả`** kèm 4 mốc (`Cắt lỗ`, `Vốn`, `Sàn hãng`, `Niêm yết`), thanh **`SL xả mục tiêu`** với `[−]` / Slider / `[+]`, 4 ô kết quả (`Doanh thu dự kiến`, `Vốn gốc thu hồi`, `Chi phí quà tặng`, `Lợi nhuận gộp`), banner cảnh báo sàn hãng & cắt lỗ, và footer (`Tự dừng khi xả đủ X máy`, `Lưu bản nháp`, `Phê duyệt & Áp dụng lên quầy bán hàng`).
  - **Cột phải 5 phần (`2. RADAR GIÁ THỊ TRƯỜNG` + `Nhận định chiến lược`):**
    - Header có nút **`Giả lập mất mạng`** (test cảnh báo mất kết nối giá đối thủ `ERR_CLR_003`) & nhãn thời gian (`10 phút trước`).
    - 3 thẻ đối thủ (`Điện Máy Xanh`, `MediaMart`, `Đại lý Online`) + **Thanh `Thang định vị giá & Sàn vốn`** (`bg-rose-200 | bg-emerald-200 | bg-slate-300`) kèm 4 nhãn cân đều (`Sàn vốn`, `Gợi ý`, `Online`, `ĐMX`).
    - Khối **Hero Đề xuất viền đỏ (`GIÁ XẢ GỢI Ý TỐI ƯU · Đuôi ..90k`)** y hệt Ảnh 2: badge `🔥 Rẻ hơn X% · Rẻ nhất Cầu Giấy`, dòng so sánh ĐMX/Online, nút **`🪄 Áp dụng giá XX tr vào mô phỏng`** và nút **`🏷 Tem giá`**.
    - Khối **`Nhận định chiến lược từ Hệ thống`** ở dưới Radar đưa ra khuyến nghị cụ thể theo ngành hàng/sản phẩm đang chọn.
* **Files:**
  - Modify: `src/dash_app/pages/m3_clearance.py`, `src/dash_app/callbacks/m3_callbacks.py`, `tests/test_dash_m3.py`
* **Cách thức triển khai (TDD):**
  - [x] **Step 1 (RED):** Cập nhật `tests/test_dash_m3.py` kiểm tra thanh so sánh dòng tiền nằm trong thẻ PA1–PA4 (bỏ `m3-tactic-chart`), nút `Khớp giá đối thủ` & `Cắt lỗ (-5% vốn)` + `Giả lập mất mạng`, khối `Thang định vị giá & Sàn vốn`, `Áp dụng giá gợi ý vào mô phỏng`, và khối `Nhận định chiến lược từ Hệ thống`.
  - [x] **Step 2:** Chạy `tests/test_dash_m3.py` xác nhận **RED**.
  - [x] **Step 3 (GREEN):** Lập trình nâng cấp `m3_clearance.py` & `m3_callbacks.py`.
  - [x] **Step 4:** Chạy `tests/test_dash_m3.py` xác nhận **GREEN**.
  - [x] **Step 5:** Cập nhật Plan & Commit (`feat(dash-m3): match prototype Image 2 with inline scenario bars, price ruler and AI strategic insight`).

---

### GIAI ĐOẠN 6: NÂNG CẤP MODULE 04 — GỢI Ý NHẬP HÀNG (`m4_replenishment`, `m4_callbacks`)
**Thời lượng dự kiến:** 0.5 ngày | **Tham chiếu:** Yêu cầu mục (5) & Prototype `L1296–L1709`, `L5363–L5460`.

#### Task 7: Bỏ 2 Graphs, Sọc Pastel Chéo `.gap-pattern`, Màu Badge Hãng & Thuần Việt
* **Thông tin chức năng:**
  - **Loại bỏ** 2 biểu đồ (`m4DemandChart`, `m4BudgetChart`) khỏi `panel-m4`, nối liền thanh lọc Nhà phân phối xuống Bảng điều phối lượng nhập 8:4 để không gian bảng rộng và tập trung tương tác.
  - Dùng dữ liệu & công thức vừa mở rộng ở Giai đoạn 2 để bảng hiển thị phong phú **4–6 mặt hàng cần nhập** từ nhiều hãng khác nhau (`Daikin`, `Sony`, `Casper`, `Toshiba`, `Panasonic`) kèm chú giải bộ lọc Hãng khớp thực tế.
  - **Cột `SẢN PHẨM & NHÀ PHÂN PHỐI`:** Áp dụng `get_brand_badge_class(brand)` để mỗi hãng mang 1 màu badge đặc trưng; hiển thị `Đặt tối thiểu / Kiện / Tin cậy` bằng tiếng Việt dễ hiểu (không còn `MOQ`, `SKU`, `AVL`, `INC`, `PO`).
  - **Cột `NHU CẦU & KHOẢNG THIẾU`:** Thanh 3 màu `bg-emerald-500` (Khả dụng) + `bg-blue-600` (Đang về) + **`gap-pattern` (sọc pastel hồng/đỏ chéo)** cho phần `Khoảng thiếu cần nhập` (khớp `.gap-pattern` Prototype L208–L216 & L5434).
* **Files:**
  - Modify: `src/dash_app/pages/m4_replenishment.py`, `src/dash_app/callbacks/m4_callbacks.py`, `tests/test_dash_m4.py`
* **Cách thức triển khai (TDD):**
  - [x] **Step 1 (RED):** Cập nhật `tests/test_dash_m4.py` xác nhận đã bỏ `m4DemandChart`/`m4BudgetChart`, có `>= 4` SKU đề xuất nhập, phần thiếu mang class `gap-pattern`, có badge màu hãng riêng biệt, và không còn chữ `SKU`/`AVL`/`INC`/`MOQ`.
  - [x] **Step 2:** Chạy `tests/test_dash_m4.py` xác nhận **RED**.
  - [x] **Step 3 (GREEN):** Cập nhật `m4_replenishment.py` & `m4_callbacks.py`.
  - [x] **Step 4:** Chạy `tests/test_dash_m4.py` xác nhận **GREEN**.
  - [x] **Step 5:** Cập nhật Plan & Commit (`feat(dash-m4): remove top charts, add striped gap bar, per-brand badge colors and multi-SKU replenishment depth`).

---

### GIAI ĐOẠN 7: NÂNG CẤP MODULE 05 (PIE DOANH THU & CÂN ĐỐI 7:5) & MODULE 06 (CẤU HÌNH THƯỞNG)
**Thời lượng dự kiến:** 1.0 ngày | **Tham chiếu:** Yêu cầu mục (6), (7) & Prototype `L1712–L2584`.

#### Task 8: Module 05 — Pie Chart Doanh thu 5 Dịch vụ CSKH theo Kỳ (`14d/30d/3m`), Bỏ Donut & Khớp chiều cao 7:5 Trượt dọc
* **Thông tin chức năng:**
  - **Loại bỏ** biểu đồ Donut `"Cơ cấu mức độ ưu tiên & Hàng đợi Cooldown 30 ngày"` (`m5PriorityChart`).
  - **Nâng cấp Pie Chart mới (`m5ServiceRevenuePie`):** Hiển thị **`%` tổng doanh thu từ 5 dịch vụ CSKH** (`Bảo dưỡng ĐH`, `Thay lõi RO`, `Lắp đặt & Phụ kiện`, `Bảo hành`, `Chăm sóc VIP`), tích hợp **bộ chọn khoảng thời gian (`14 ngày`, `30 ngày`, `3 tháng`)** ngay góc phải card; Hover trên từng slice hiển thị rõ: **Tên dịch vụ**, **Doanh thu**, **Tỷ trọng (%)**, và **Số lượng đơn hàng / ca dịch vụ** trong kỳ đang chọn (ẩn giá tiền nếu cần theo RBAC hoặc giữ minh bạch doanh thu dịch vụ).
  - **Tái cấu trúc bố cục Master-Detail 7:5 (đồng bộ chiều cao 2 cột):**
    - **Cột phải (5 phần):** Xếp dọc 2 Card — **Trên**: Card Biểu đồ tròn `Phân bổ Doanh thu 5 Dịch vụ CSKH`; **Dưới**: Card `Hồ sơ tác chiến cuộc gọi` (Kịch bản gọi, Zalo ZNS, Form 4 kết quả & Chốt lịch thợ).
    - **Cột trái (7 phần):** Cấu trúc `flex flex-col` với chiều cao matching cột phải (`xl:h-[780px]` hoặc `flex-1` đồng bộ với grid `items-stretch` bên phải): phần **Header + Pills lọc điểm chạm + Ô tìm kiếm** và **`<thead>` tiêu đề 4 cột CỐ ĐỊNH (`sticky top-0`)**, chỉ phần **`<tbody>` danh sách khách hàng bên dưới cuộn dọc (`overflow-y-auto`)** bên trong khung bảng, vừa khớp chiều cao tổng cột phải (`Card Pie Chart + Card Hồ sơ cuộc gọi`)!

#### Task 9: Module 06 — Tùy chỉnh Chính sách Thưởng & Xếp hạng Hiệu suất Nhân viên
* **Thông tin chức năng:**
  - Ngay trong khối `Xếp hạng Hiệu suất & Hoa hồng Bán kèm`, bổ sung panel điều chỉnh **Chính sách Thưởng & Xếp hạng (`m6PolicyConfigPanel`)** gồm:
    1. `% Hoa hồng Phụ kiện` (input/slider mặc định `15%`, dải `5%–30%`)
    2. `% Hoa hồng Dịch vụ lắp đặt` (mặc định `20%`, dải `5%–35%`)
    3. `Thưởng nóng / ca chốt bán kèm` (mặc định `50.000 đ` hoặc điều chỉnh `0 / 50k / 100k / 150k`)
    4. `Tiêu chí xếp hạng (#1–#3)` (Dropdown: `Theo tổng tiền thưởng`, `Theo doanh số bán kèm`, `Theo lợi nhuận mang lại`)
  - Nút **`Áp dụng chính sách mới`**: tính lại tức thì bảng xếp hạng `#1/#2/#3`, tiền hoa hồng từng nhân sự, tổng `Quỹ chi`, và lưu trạng thái chính sách hiện hành (khóa không cho chỉnh khi `ROLE_SALES`, vẫn cho `ROLE_OWNER` duyệt chi).
* **Files:**
  - Modify: `src/dash_app/pages/m5_crm.py`, `src/dash_app/callbacks/m5_callbacks.py`, `tests/test_dash_m5.py`
  - Modify: `src/dash_app/pages/m6_performance.py`, `src/dash_app/callbacks/m6_callbacks.py`, `tests/test_dash_m6.py`
* **Cách thức triển khai (TDD):**
  - [ ] **Step 1 (RED):** Cập nhật `tests/test_dash_m5.py` (Pie Chart doanh thu dịch vụ + đổi kỳ `14/30/90 ngày`, bỏ Donut, bố cục 7:5 cột phải có Pie + Call Panel, cột trái có vùng cuộn riêng `overflow-y-auto`) và `tests/test_dash_m6.py` (đổi `% PK / % DV / Thưởng nóng / Tiêu chí xếp hạng` tính lại đúng Quỹ chi & thứ hạng; khóa với `ROLE_SALES`).
  - [ ] **Step 2:** Chạy `tests/test_dash_m5.py tests/test_dash_m6.py` xác nhận **RED**.
  - [ ] **Step 3 (GREEN):** Lập trình nâng cấp M5 & M6.
  - [ ] **Step 4:** Chạy `tests/test_dash_m5.py tests/test_dash_m6.py` xác nhận **GREEN**.
  - [ ] **Step 5:** Cập nhật Plan & Commit (`feat(dash-m5-m6): upgrade M5 service revenue pie + balanced sticky queue and M6 editable bonus policy`).

---

### GIAI ĐOẠN 8: TÍCH HỢP TOÀN CỤC `src/app_dashboard.py`, KIỂM THỬ E2E & ĐỐI CHIẾU CHROME 1440×1400
**Thời lượng dự kiến:** 0.5 ngày | **Mục tiêu:** Đảm bảo toàn hệ thống chạy mượt qua `.venv/bin/python src/app_dashboard.py` ở `http://127.0.0.1:8050/`, không lỗi callback, vượt qua 100% Test Suite và xác nhận từng ảnh chụp Chrome 1440px cho M1–M6.

#### Task 10: Lắp ghép Cuối cùng, Quét thuật ngữ toàn cục, Full Regression Test & Visual Verification
* **Files:**
  - Modify: `src/app_dashboard.py`, `tests/test_dash_e2e_integration.py`, `docs/IMPLEMENTATION_PLAN_DASH_PARITY_V2.md`
* **Cách thức triển khai (Verification Steps):**
  - [ ] **Step 1:** Rà soát toàn bộ `src/dash_app/` + `src/app_dashboard.py` bảo đảm `test_dash_e2e_integration.py` kiểm tra thêm các ID/callback mới (`m1ReservedOrdersSection`, `m1OrderDetailModal`, `m2-capital-pie`, `m5ServiceRevenuePie`, `m6PolicyConfigPanel`) trả HTTP 200 ở `/`, `/_dash-layout`, `/_dash-update-component`.
  - [ ] **Step 2:** Chạy toàn bộ `.venv/bin/python -m unittest discover tests -v` — tất cả tests cũ và mới **PASS 100%**, sau đó `git checkout data/retail_dienmay.db` (hoặc giữ nguyên DB seed mới đã kiểm chứng sạch).
  - [ ] **Step 3:** Chạy server thực `.venv/bin/python src/app_dashboard.py` trên cổng `8050` (`8059` tạm khi test), dùng Chrome DevTools Protocol (`1440×1400`) chụp lại **6 ảnh thực tế M1–M6**, mở bằng `read_file` để kiểm tra kỹ từng mục (không cắt chữ, không đè tên trên scatter, đủ badge/chỉ báo tiếng Việt, Pie chart M2/M5, sọc chéo M4, 7:5 M5, policy M6).
  - [ ] **Step 4:** Khởi chạy server Dash chuẩn trên `http://127.0.0.1:8050/`, tích hoàn tất mọi checkbox trong Plan và Commit Giai đoạn 8 (`feat(dash-v2): complete full prototype parity and plain Vietnamese UX across M1-M6`).

---

## 4. ĐỊNH NGHĨA TIÊU CHÍ HOÀN THÀNH (MASTER DEFINITION OF DONE - DOD)

Đợt nâng cấp V2 chỉ được nghiệm thu khi đạt 100% các tiêu chuẩn sau:

| Mã DoD | Hạng mục kiểm tra | Tiêu chí đạt chuẩn bắt buộc | Phương thức xác minh |
| :--- | :--- | :--- | :--- |
| **DoD-UX-V2-01** | **Thuần Việt & Typography** | 0% từ viết tắt thô (`DOS`, `DSI`, `SKU`, `INC`, `SOH`, `RES`, `AVL`, `PO`, `MOQ`) trên nhãn hiển thị; `Inter` + `JetBrains Mono` đồng bộ và màu riêng cho từng Hãng. | Kiểm thử DOM text + Chrome screenshot |
| **DoD-M1-V2** | **M1 Tổng quan kho** | Card 3 hiện vốn kẹt quá hạn & link xuống tab Gấp; Cột sức khỏe có căn cứ số; Nút `"Lọc thêm"`; Ma trận full-width tên ngắn không đè + Tooltip; Quản lý & Hủy đơn giữ chỗ thật xuống DB. | `tests/test_dash_m1.py` + `dash_m1.png` |
| **DoD-M2-V2** | **M2 Cần xử lý hôm nay** | Pie Chart dải Vàng–Cam–Đỏ–Nâu đỏ + Tooltip 4 trường; Bỏ Runway chart; Bảng 7 cột chuẩn Ảnh 1 có thanh trượt ngang từng ô `.cell-hscroll`. | `tests/test_dash_m2.py` + `dash_m2.png` |
| **DoD-M3-V2** | **M3 Gợi ý xả hàng** | Khớp 100% Ảnh 2: thanh dòng tiền nhúng trong PA1–PA4, Slider & Presets đủ, Radar có `Thang định vị giá & Sàn vốn`, `..90k` box, `Giả lập mất mạng` & `Nhận định chiến lược`. | `tests/test_dash_m3.py` + `dash_m3.png` |
| **DoD-M4-V2** | **M4 Gợi ý nhập hàng** | Bỏ 2 biểu đồ; Có `>= 4` SKU đa hãng cần nhập; Thanh thiếu có sọc chéo `.gap-pattern`; Badge mỗi Hãng 1 màu. | `tests/test_dash_m4.py` + `dash_m4.png` |
| **DoD-M5-V2** | **M5 Smart CRM** | Bỏ Donut ưu tiên; Pie Chart % Doanh thu 5 dịch vụ chọn được `14 ngày / 30 ngày / 3 tháng` + Hover số đơn nằm trên Hồ sơ cuộc gọi; Bảng KH trái trượt dọc cố định Header và khớp chiều cao cột phải. | `tests/test_dash_m5.py` + `dash_m5.png` |
| **DoD-M6-V2** | **M6 Hiệu quả kinh doanh** | Tùy chỉnh `% PK`, `% DV`, `Thưởng nóng`, `Tiêu chí xếp hạng` tính lại trực tiếp bảng xếp hạng & Quỹ chi (khóa khi `ROLE_SALES`). | `tests/test_dash_m6.py` + `dash_m6.png` |
| **DoD-TDD-V2** | **Hồi quy Test Suite** | 100% bộ test (`tests/test_*.py`) Pass không lỗi, 0 rác SQLite, Chrome render `1440×1400` không console error. | `.venv/bin/python -m unittest discover tests -v` |

---

## 5. MA TRẬN QUẢN TRỊ RỦI RO KỸ THUẬT (RISK MITIGATION MATRIX)

| Rủi ro kỹ thuật | Mức độ | Giải pháp kiểm soát |
| :--- | :---: | :--- |
| **Cập nhật DB seed cho M4 & M5 làm hỏng các assertion đếm số bản ghi cố định trong 39 test cũ** | Cao | Giữ nguyên chính xác `16` sản phẩm `DIM_PRODUCTS`, `12` SKU `has_serial=1`, `3` mã vượt trần; chỉ điều chỉnh `min_stock` / `lead_time_days` / logic an toàn để M4 xuất hiện nhiều mã cần nhập hơn, và rải ngày `FACT_SERVICE_APPOINTMENTS` khác ngày/thợ test CRM (`2026-12-25`). |
| **Tên sản phẩm trên Scatter M1 dài dễ đè lên bong bóng khác** | Trung bình | Rút gọn tên ngắn gọn (`<= 14–16` ký tự) bằng bảng ánh xạ chuẩn, kết hợp phân tầng `textposition` (`top center`, `bottom center`, `middle right`, `top left`) theo vùng tọa độ `(SOH, Giá bán)` để tách nhãn rõ ràng. |
| **Ô trượt ngang `.cell-hscroll` trong bảng M2 làm thay đổi độ rộng cột hoặc ẩn thanh cuộn khó thấy** | Trung bình | Khóa `table-fixed` + độ rộng `%` chuẩn trên `<table>` giống Prototype L868 và tạo thanh cuộn ngang mảnh (`height: 4px`) khi hover vào từng ô dài. |
| **Cân bằng chiều cao chính xác của bảng KH bên trái M5 với 2 card bên phải trên màn hình 1440px** | Thấp | Đặt cột phải trong `flex flex-col gap-4` và cột trái dùng khung `xl:h-full max-h-[860px] flex flex-col` với `<thead>` `sticky top-0` trong vùng `flex-1 overflow-y-auto` để luôn khớp đáy ngang hàng với cột phải ở cả chế độ thường và cuộn dài. |
