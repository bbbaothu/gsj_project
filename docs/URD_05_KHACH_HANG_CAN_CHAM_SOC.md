# TÀI LIỆU ĐẶC TẢ YÊU CẦU NGƯỜI SỬ DỤNG (USER REQUIREMENTS DOCUMENT - URD)
## HỆ THỐNG QUẢN LÝ KHO HÀNG ĐIỆN MÁY THÔNG MINH - STOCK SENSE
### PHÂN HỆ: KHÁCH HÀNG CẦN CHĂM SÓC (SMART CUSTOMER RETENTION & CRM)
#### Bao gồm: US-5.1

---

## BẢNG THEO DÕI THAY ĐỔI TÀI LIỆU (DOCUMENT REVISION HISTORY)

| Phiên bản | Ngày cập nhật | Tác giả | Trạng thái | Mô tả thay đổi |
| :--- | :--- | :--- | :--- | :--- |
| **1.0.0** | 08/11/2026 | Nhóm Phân tích Nghiệp vụ (BA Team) | Dự thảo (Draft) | Khởi tạo tài liệu đặc tả URD chi tiết cho Nhóm chức năng 5: Khách hàng cần chăm sóc (US-5.1) |

---

## 1. TỔNG QUAN & PHẠM VI (INTRODUCTION & SCOPE)

### 1.1. Bối cảnh nghiệp vụ
Trong cuộc cạnh tranh khốc liệt giữa các cửa hàng điện máy cá thể (Sole Trader) và các chuỗi siêu thị điện máy khổng lồ (Điện Máy Xanh, MediaMart), vũ khí cạnh tranh mạnh nhất của cửa hàng cá thể chính là **mối quan hệ cá nhân thân thiết, sự tận tâm và dịch vụ hỗ trợ kỹ thuật tận nhà**. 
Tuy nhiên, phần lớn các cửa hàng truyền thống hiện nay đang gặp phải các hạn chế lớn:
- **Chăm sóc bị động:** Chỉ liên hệ với khách khi khách gọi điện phàn nàn hỏng hóc hoặc yêu cầu bảo hành.
- **Bỏ quên mỏ vàng khách hàng cũ:** Khách hàng sau khi mua tivi hay điều hòa thường bị lãng quên trong suốt 1-2 năm, trong khi đây chính là đối tượng có nhu cầu rất cao về: bảo dưỡng định kỳ, mua phụ kiện, thay lõi lọc nước hoặc đổi đời thiết bị mới.
- **Không có công cụ ghi nhớ lịch sử tương tác:** Việc theo dõi khách phụ thuộc vào sổ tay hoặc trí nhớ của chủ tiệm; khi đông việc sẽ bỏ sót các đợt chăm sóc quan trọng.

Phân hệ **Khách hàng cần chăm sóc (Customer Retention & Care)** được xây dựng nhằm biến dữ liệu bán hàng và bảo hành trong quá khứ thành **các cơ hội bán hàng lặp lại (Repeat Sales)** và **bán chéo (Cross-selling / Up-selling)** một cách tự động và chuyên nghiệp.

### 1.2. Mục tiêu của phân hệ "Khách hàng cần chăm sóc"
- **Tự động nhận diện thời điểm vàng chăm sóc (Lifecycle Trigger Detection):** Dựa trên ngày mua, chủng loại thiết bị và thời hạn bảo hành để tự động bắn nhắc việc chăm sóc: đến hạn bảo dưỡng điều hòa (6 tháng), đến hạn thay lõi lọc nước (3-6 tháng), hết hạn bảo hành của Hãng (12-24 tháng), hoặc chu kỳ nâng cấp thiết bị mới (3-5 năm).
- **Gợi ý kịch bản tư vấn cá nhân hóa (Personalized Sales Scripts):** Tự động sinh nội dung tin nhắn Zalo ZNS hoặc kịch bản gọi điện thoại chuẩn hóa, xưng hô đúng tên khách, nhắc đúng model máy khách đã mua, mang lại cảm giác quan tâm chu đáo.
- **Quản lý nhật ký liên hệ & Đo lường tỷ lệ chuyển đổi:** Theo dõi lịch sử cuộc gọi/tin nhắn, ghi nhận phản hồi của khách (Đã chốt dịch vụ, Hẹn gọi lại sau, Từ chối) và tạo nhanh đơn bán phụ kiện/dịch vụ trực tiếp từ màn hình chăm sóc.

### 1.3. Bảng thuật ngữ viết tắt (Glossary)

| Thuật ngữ | Tên đầy đủ / Định nghĩa | Giải thích nghiệp vụ |
| :--- | :--- | :--- |
| **Care Trigger** | Điểm chạm kích hoạt chăm sóc | Sự kiện hoặc mốc thời gian gợi ý nhân viên cần chủ động liên hệ với khách hàng. |
| **Cross-selling** | Bán chéo sản phẩm | Chào bán thêm phụ kiện hoặc vật tư liên quan (VD: Bán tivi chào thêm Loa thanh Soundbar hoặc Giá treo đa năng). |
| **Up-selling** | Nâng cấp thiết bị đời mới | Tư vấn khách đổi từ máy cũ lên dòng máy công nghệ mới hơn sau 3 - 5 năm sử dụng. |
| **Maintenance Due** | Đến hạn bảo dưỡng định kỳ | Thời điểm thiết bị cần được vệ sinh, bơm gas hoặc thay linh kiện hao mòn. |
| **Warranty Expiry** | Hết hạn bảo hành gốc | Mốc thời gian máy hết hạn bảo hành chính hãng, mở ra cơ hội bán gói dịch vụ hỗ trợ tại nhà. |
| **Call Script** | Kịch bản cuộc gọi tư vấn | Lời thoại gợi ý được hệ thống sinh tự động dựa trên hồ sơ khách hàng. |

---

## 2. MA TRẬN PHÂN QUYỀN & VAI TRÒ NGƯỜI DÙNG (ROLES & PERMISSIONS)

| Mã vai trò | Tên vai trò | Trách nhiệm chính trong phân hệ Khách hàng cần chăm sóc | Quyền hạn trên US-5.1 |
| :--- | :--- | :--- | :--- |
| **ROLE_OWNER** | Chủ cửa hàng / Giám đốc | Theo dõi tỷ lệ chăm sóc thành công, hiệu quả bán kèm của nhân viên, xử lý khách VIP | Toàn quyền (Xem toàn bộ danh bạ, phân bổ khách cho nhân viên, xem doanh thu tái mua) |
| **ROLE_SALES** | Nhân viên CSKH / Bán hàng | Gọi điện, nhắn tin Zalo, tư vấn bảo dưỡng và ghi nhận kết quả cuộc gọi | Toàn quyền thao tác trên danh sách được giao, ghi nhật ký cuộc gọi, tạo đơn dịch vụ mới |
| **ROLE_WH_MGR** | Quản lý kho / Kỹ thuật viên | Chuẩn bị vật tư linh kiện thay thế (lõi lọc, ống đồng, gas) khi khách chốt lịch bảo dưỡng | Xem lịch hẹn lắp đặt/bảo dưỡng để chuẩn bị vật tư xuất kho |

---

## 3. ĐẶC TẢ CHI TIẾT USER STORY US-5.1

### 3.1. Tóm tắt User Story
* **Mã User Story:** `US-5.1`
* **Tên tính năng:** Nhận diện khách hàng tiềm năng cần chăm sóc định kỳ
* **Người dùng (Actor):** Nhân viên chăm sóc khách hàng / Nhân viên bán hàng
* **Tuyên bố yêu cầu:**
  > *Là một* Nhân viên chăm sóc khách hàng / Nhân viên bán hàng,  
  > *Tôi muốn* xem danh sách bao gồm tên khách hàng, sản phẩm điện máy họ đã mua trước đó, dấu hiệu nhu cầu phát sinh (ví dụ: đã đến hạn bảo dưỡng, sắp đổi đời máy mới, hoặc mua phụ kiện đi kèm), gợi ý nội dung tư vấn và lịch sử liên hệ gần nhất,  
  > *Để* chủ động gọi điện, nhắn tin chăm sóc, tạo dựng mối quan hệ thân thiết và kích thích nhu cầu mua sắm lặp lại.

---

### 3.2. Sơ đồ luồng phân loại & chăm sóc khách hàng (Customer Care Workflow)

```mermaid
flowchart TD
    A([Hệ thống chạy ngầm phân tích Lịch sử Mua sắm & Bảo hành]) --> B[Đối chiếu Ngày mua hàng & Ngày hiện tại]
    B --> C{Kiểm tra Điều kiện Kích hoạt Chăm sóc (Care Triggers)}
    
    C -->|Điều hòa đã mua được 5-6 tháng| D1[Trigger 1: Đến hạn Bảo dưỡng trước mùa nóng]
    C -->|Máy lọc nước đã dùng 3-6 tháng| D2[Trigger 2: Đến hạn Thay lõi lọc thô 1, 2, 3]
    C -->|Thiết bị còn <= 30 ngày hết bảo hành| D3[Trigger 3: Chăm sóc Hết hạn Bảo hành & Hỗ trợ tại nhà]
    C -->|Tivi / Tủ lạnh đã mua >= 3 năm| D4[Trigger 4: Cơ hội Nâng cấp Đổi đời máy mới]
    C -->|Vừa mua thiết bị chính trong 7 ngày| D5[Trigger 5: Bán chéo Phụ kiện & Thăm hỏi sau lắp]

    D1 --> E[Hệ thống tổng hợp Danh sách Khách hàng Cần chăm sóc Hôm nay]
    D2 --> E
    D3 --> E
    D4 --> E
    D5 --> E

    E --> F[Tự động tạo Kịch bản Gọi / Mẫu Zalo ZNS cá nhân hóa]
    F --> G[Nhân viên bấm nút Gọi điện thoại hoặc Nhắn tin Zalo]
    G --> H[Nhân viên ghi nhận Kết quả Tương tác:]
    H --> H1[Khách đồng ý: Tạo ngay Đơn Dịch vụ / Lịch hẹn kỹ thuật]
    H --> H2[Khách bận: Đặt lịch Hẹn gọi lại sau N ngày]
    H --> H3[Khách từ chối: Đóng tác vụ & Ghi chú lý do]
    H1 --> I([Hoàn thành & Cập nhật Doanh thu])
    H2 --> I
    H3 --> I
```

---

### 3.3. Các nhóm kích hoạt chăm sóc cốt lõi (5 Core Care Triggers)

| Nhóm kích hoạt | Chủng loại thiết bị | Chu kỳ thời gian | Dấu hiệu nhu cầu phát sinh | Kịch bản chăm sóc đề xuất |
| :--- | :--- | :--- | :--- | :--- |
| **TRIGGER_AC_MAINT** | Điều hòa nhiệt độ | 6 tháng sau lắp đặt (hoặc tháng 3 - 4 hàng năm) | Bụi bẩn dàn lạnh, thiếu gas, giảm độ mát | Dịch vụ vệ sinh xịt rửa bảo dưỡng điều hòa tại nhà với giá ưu đãi cho khách quen |
| **TRIGGER_WATER_FILTER**| Máy lọc nước RO | 3 đến 6 tháng sau ngày mua | Lõi lọc số 1, 2, 3 bị tắc bẩn, giảm chất lượng nước | Gửi kỹ thuật qua kiểm tra nguồn nước và thay lõi lọc chính hãng tận nhà |
| **TRIGGER_WARRANTY_END**| Tivi, Tủ lạnh, Máy giặt | Còn 30 ngày trước khi hết bảo hành hãng | Lo lắng chi phí sửa chữa đắt đỏ khi máy hết bảo hành | Khảo sát chất lượng vận hành của máy; tặng voucher giảm 20% công sửa chữa trọn đời |
| **TRIGGER_UPGRADE_CYCLE**| Tivi LED/4K, Tủ lạnh cũ | 36 đến 60 tháng sau ngày mua | Model cũ màn hình nhỏ, tốn điện, muốn nâng cấp smart | Chương trình "Thu cũ đổi mới - Lên đời Tivi OLED 4K màn hình lớn đón Tết" |
| **TRIGGER_CROSS_SELL** | Thiết bị mới mua 3-7 ngày | 3 đến 7 ngày sau khi kỹ thuật bàn giao | Đã trải nghiệm máy xong, có nhu cầu sắm thêm phụ kiện | Chào mua Giá treo tivi đa năng, Dàn âm thanh Soundbar, Ổ cắm chống sét điện tử |

---

### 3.4. Mô tả kịch bản thực hiện (Use Case Scenario)

#### A. Luồng chính (Happy Path)
1. **Bước 1:** Nhân viên đăng nhập vào hệ thống, chọn menu **"Khách hàng cần chăm sóc"**.
2. **Bước 2:** Hệ thống hiển thị 4 Thẻ chỉ số tổng quan trong ngày:
   - *Số khách cần liên hệ hôm nay:* Tổng danh sách khách hàng có trigger kích hoạt trong ngày.
   - *Khách đến hạn bảo dưỡng:* Khách cần bảo dưỡng điều hòa / thay lõi lọc nước.
   - *Khách tiềm năng nâng cấp máy:* Khách có máy cũ trên 3 năm.
   - *Doanh thu dịch vụ mang lại tháng này:* Doanh số phụ kiện và tiền công kỹ thuật thu được từ các cuộc gọi CSKH.
3. **Bước 3:** Nhân viên chọn một khách hàng cụ thể trên danh sách (ví dụ: *Chị Mai - Đống Đa, đã mua Điều hòa Daikin từ 6 tháng trước*).
4. **Bước 4:** Hệ thống mở bảng chi tiết thông tin kèm **Kịch bản tư vấn gợi ý tự động (AI Call Script)**:
   > *"Dạ em chào chị Mai, em là nhân viên tại Điện máy Anh Tâm 108 Cầu Giấy ạ. Đợt tháng 4 năm ngoái nhà mình có lắp bộ Điều hòa Daikin Inverter bên em. Đến nay đã tròn 6 tháng sử dụng, sắp vào đợt nắng nóng cao điểm, bên em đang có chương trình tri ân khách quen hỗ trợ vệ sinh lưới lọc và đo áp suất gas miễn phí tiền công cho nhà mình. Em xin phép xếp thợ kỹ thuật qua hỗ trợ chị vào chiều mai lúc 15h được không ạ?"*
5. **Bước 5:** Nhân viên nhấn biểu tượng **"Gọi điện"** (kết nối qua tổng đài ảo hoặc quay số nhanh trên điện thoại) hoặc nhấn **"Gửi Zalo"**.
6. **Bước 6:** Khách hàng đồng ý đặt lịch vệ sinh bảo dưỡng vào 15h ngày mai.
7. **Bước 7:** Nhân viên chọn kết quả **"Đồng ý - Đặt lịch dịch vụ"**, chọn giờ hẹn và tên thợ kỹ thuật phụ trách. Hệ thống tự động tạo phiếu dịch vụ và gửi tin nhắn xác nhận cho khách.

#### B. Luồng thay thế & Ngoại lệ (Alternative & Exception Flows)
* **AF-5.1.1 (Khách đang bận, hẹn gọi lại):** Nhân viên chọn trạng thái **"Khách bận - Hẹn gọi lại"** và chọn thời gian (ví dụ: *18h tối nay*). Hệ thống sẽ tạo thông báo nhắc việc trên màn hình làm việc của nhân viên đúng giờ hẹn.
* **AF-5.1.2 (Khách đã tự bảo dưỡng hoặc không có nhu cầu):** Nhân viên chọn **"Không có nhu cầu lần này"** và nhập ghi chú. Hệ thống sẽ dời lịch kích hoạt chăm sóc của khách hàng này sang chu kỳ 6 tháng tiếp theo, không làm phiền khách liên tục.
* **EF-5.1.3 (Số điện thoại không liên lạc được):** Nếu gọi 3 lần đều thuê bao hoặc sai số, hệ thống gắn cờ vàng: *"Cần xác minh lại SĐT"* để nhân viên kiểm tra lại hợp đồng giấy hoặc hóa đơn gốc.

---

### 3.5. Quy tắc nghiệp vụ (Business Rules - US-5.1)

* **BR-5.1.1 (Quy tắc lọc trùng và Chống làm phiền - Spam Prevention):**
  - Hệ thống **tuyệt đối không được** đưa một khách hàng vào danh sách gọi điện nếu khách hàng đó đã được liên hệ trong vòng **30 ngày qua** (trừ trường hợp khách chủ động hẹn lịch gọi lại).
  - Tối đa một khách hàng chỉ nhận tối đa 1 tin nhắn chăm sóc tự động mỗi tháng.
* **BR-5.1.2 (Quy tắc tính toán Mốc thời gian Bảo dưỡng Điều hòa):**
  $$\text{Maintenance Date} = \text{Invoice Date} + 180 \text{ ngày}$$
  - Cảnh báo được kích hoạt trước 15 ngày so với $\text{Maintenance Date}$ để nhân viên kịp thời xếp lịch trước khi vào mùa cao điểm thợ quá tải.
* **BR-5.1.3 (Quy tắc tính toán Chu kỳ Thay lõi lọc nước):**
  - Lõi số 1 (PP 5 micron): 3 tháng ($\sim 90$ ngày).
  - Lõi số 2 (Than hoạt tính OCB): 6 tháng ($\sim 180$ ngày).
  - Lõi số 3 (PP 1 micron): 6 tháng ($\sim 180$ ngày).
* **BR-5.1.4 (Xếp hạng độ ưu tiên liên hệ - Care Priority Score):**
  Khách hàng được chấm điểm ưu tiên cuộc gọi theo công thức:
  $$\text{Priority Score} = (\text{Total Spent} \times 0.4) + (\text{Urgency Factor} \times 0.4) + (\text{Loyalty Years} \times 0.2)$$
  - Khách hàng VIP chi tiêu lớn và khách có thiết bị đắt tiền sắp hết bảo hành luôn nằm ở đầu danh sách gọi điện mỗi sáng.

---

### 3.6. Tiêu chí nghiệm thu (Acceptance Criteria - Gherkin Syntax)

```gherkin
Feature: Nhận diện khách hàng tiềm năng cần chăm sóc định kỳ (US-5.1)

  Scenario: Tự động kích hoạt thông báo bảo dưỡng điều hòa sau 6 tháng
    Given Khách hàng "Nguyễn Văn Tuấn" mua "Điều hòa Daikin FTKB25" vào ngày "10/05/2026"
    And Ngày hiện tại của hệ thống là "25/10/2026" (sau 168 ngày kể từ ngày mua)
    When Hệ thống quét danh sách chăm sóc khách hàng
    Then Khách hàng "Nguyễn Văn Tuấn" phải xuất hiện trong danh sách "Khách cần bảo dưỡng điều hòa"
    And Hệ thống tự động sinh kịch bản gọi điện nhắc bảo dưỡng máy Daikin FTKB25 kèm số điện thoại

  Scenario: Chặn không gọi làm phiền khách vừa mới được liên hệ
    Given Khách hàng "Trần Thị Lan" đã được nhân viên gọi chăm sóc vào ngày "01/11/2026"
    When Đến ngày "15/11/2026" có trigger mới về thay lõi lọc nước
    Then Hệ thống phải tự động ẩn thông báo gọi điện cho khách này cho đến sau ngày "01/12/2026" (đủ 30 ngày)
    And Đưa vào hàng đợi hoãn liên hệ (Snoozed Queue)
```

---

### 3.7. Từ điển dữ liệu hiển thị (Data Dictionary - US-5.1)

| Tên trường (UI Label) | Mã thuộc tính | Kiểu dữ liệu | Nguồn dữ liệu | Ràng buộc / Ý nghĩa |
| :--- | :--- | :--- | :--- | :--- |
| **Mã khách hàng** | `customer_code` | Text | `DIM_CUSTOMERS.customer_code` | Mã định danh khách |
| **Tên khách hàng** | `customer_name` | Text | `DIM_CUSTOMERS.customer_name` | Họ tên người mua |
| **Số điện thoại** | `phone` | Text | `DIM_CUSTOMERS.phone` | Định dạng 10 chữ số VN |
| **Thiết bị đã mua** | `purchased_products`| Text/List | `FACT_INVOICES_LINES` | Model thiết bị + ngày mua |
| **Lý do chăm sóc** | `care_reason` | Enum/Badge | Phân loại từ Trigger 1 - 5 | `Bảo dưỡng ĐH`, `Thay lõi lọc`, `Hết bảo hành` |
| **Mức độ ưu tiên** | `priority_level` | Badge | Dựa trên Priority Score | 🔴 Cao (VIP), 🟡 Trung bình, 🟢 Bình thường |
| **Lần liên hệ cuối** | `last_contact_date`| Date | Bảng lịch sử CSKH | Ngày gọi gần nhất |
| **Kịch bản gợi ý** | `suggested_script` | Long Text | Hệ thống sinh tự động | Nội dung lời thoại cuộc gọi |
| **Kết quả xử lý** | `call_result` | Enum | Nhân viên ghi nhận | `Đã chốt dịch vụ`, `Hẹn lại`, `Từ chối` |

---

### 3.8. Phác thảo giao diện người dùng (UI Wireframe Concept - US-5.1)

```
+---------------------------------------------------------------------------------------------------------+
| [LOGO] STOCK SENSE - TRUNG TÂM CHĂM SÓC KHÁCH HÀNG & GIA TĂNG DOANH THU LẶP LẠI                         |
+---------------------------------------------------------------------------------------------------------+
| Bộ lọc: [ Phân loại Trigger: Tất cả v] [ Trạng thái: Chưa gọi v] [ Ưu tiên: Cao v] [Tìm Tên/SĐT: Q ]     |
|                                                                                                         |
| +---------------------+ +---------------------+ +---------------------+ +-----------------------------+ |
| | CẦN LIÊN HỆ HÔM NAY | | HẠN BẢO DƯỠNG Đ.HÒA | | THAY LÕI LỌC NƯỚC   | | DOANH SỐ CSKH THÁNG NÀY     | |
| | 18 Khách hàng       | | 8 Khách (Trước hè)  | | 6 Khách             | | 24.600.000 đ (Công + VT)    | |
| +---------------------+ +---------------------+ +---------------------+ +-----------------------------+ |
|                                                                                                         |
| DANH SÁCH KHÁCH HÀNG CẦN CHĂM SÓC THEO THỜI ĐIỂM VÀNG:                                                  |
|---------------------------------------------------------------------------------------------------------|
| Khách hàng       | SĐT        | Thiết bị đã mua         | Ngày mua  | Lý do chăm sóc   | Ưu tiên | Thao tác   |
|------------------|------------|-------------------------|-----------|------------------|---------|------------|
| Chị Mai (Đống Đa)| 0912.345.xx| ĐH Daikin FTKB25 (2 bộ) | 08/05/2026| ❄️ Đến hạn bảo dưỡng| 🔴 Cao  | [📞 Gọi ngay]|
| Anh Tuấn (Hà Đông| 0988.765.xx| Máy lọc nước Karofi 9 lõi| 12/07/2026| 💧 Thay lõi 1,2,3| 🔴 Cao  | [📞 Gọi ngay]|
| Bác Bình (Thanh X| 0903.112.xx| Tivi Sony 55X80K        | 20/11/2024| 🛡️ Sắp hết hạn BH| 🟡 Vừa  | [📞 Gọi ngay]|
| Anh Hoàng (C.Giấy| 0977.888.xx| Tủ lạnh Sharp SideBySide| 15/10/2021| 📺 Đổi đời máy 5n| 🟡 Vừa  | [📞 Gọi ngay]|
|---------------------------------------------------------------------------------------------------------|
| KHUNG CHI TIẾT CUỘC GỌI [Chị Mai - 0912.345.xxx]:                                                       |
| Lời thoại gợi ý: "Dạ em chào chị Mai, em là kỹ thuật Điện Máy Anh Tâm. Đợt hè năm ngoái nhà mình có   |
| lắp 2 bộ Daikin bên em. Sắp vào mùa nóng mới, bên em đang có ưu đãi vệ sinh xịt dàn lạnh và kiểm tra gas |
| tại nhà cho khách quen chỉ 150k/máy. Em xin phép xếp thợ qua làm cho nhà mình vào chiều mai nhé?"        |
|                                                                                                         |
| Ghi nhận kết quả cuộc gọi:                                                                              |
| [ ] Chốt lịch hẹn làm: [ Ngày: 09/11/2026 v ] [ Giờ: 15:30 v ] [ Thợ: Nguyễn Văn Long (Kỹ thuật) v ]   |
| [ ] Khách đang bận, hẹn gọi lại sau [ 2 ] ngày                                                          |
| [ ] Không nghe máy (Tự động nhắc lại sau 4 tiếng)                                                       |
|                                                                                                         |
| [ 💾 Lưu nhật ký & Lên lịch hẹn ]      [ 💬 Nhắn tin Zalo ZNS ]      [ ➕ Tạo đơn bán vật tư ]          |
+---------------------------------------------------------------------------------------------------------+
```

---

## 4. YÊU CẦU PHI CHỨC NĂNG (NON-FUNCTIONAL REQUIREMENTS - NFR)

### 4.1. Bảo mật & Quyền riêng tư thông tin khách hàng (Security & Privacy)
* **NFR-SEC-01:** Bảo vệ thông tin liên lạc cá nhân: Số điện thoại khách hàng trên giao diện danh sách được che bớt 2 số cuối (ví dụ `0912.345.xx*`). Chỉ khi nhân viên bấm nút "Gọi điện" hoặc có tài khoản được cấp quyền mới được hiển thị số đầy đủ.
* **NFR-SEC-02:** Nhật ký cuộc gọi và ghi chú tương tác được lưu trữ mã hóa và không được phép xóa sửa tùy tiện để đảm bảo minh bạch trong việc tính hoa hồng chăm sóc khách hàng.

### 4.2. Khả năng tích hợp viễn thông (Integration & Extensibility)
* **NFR-INT-01:** Hệ thống hỗ trợ giao thức gọi điện một chạm (URI `tel:` click-to-call) để tương thích tức thì với điện thoại di động thông minh của nhân viên hoặc tai nghe tổng đài Softphone.
* **NFR-INT-02:** Hỗ trợ chuẩn kết nối Webhook gửi mẫu tin nhắn chăm sóc qua Zalo Official Account (Zalo ZNS) của cửa hàng khi được tích hợp khóa API.

---

## 5. DANH SÁCH CÂU HỎI THẢO LUẬN CHO KHÁCH HÀNG (OPEN QUESTIONS FOR CLIENT)

1. **Chính sách phân chia khách hàng chăm sóc:**
   - *Câu hỏi:* Cửa hàng có muốn cố định nhân viên nào bán đơn ban đầu thì sẽ chịu trách nhiệm chăm sóc khách đó suốt đời (để hưởng hoa hồng dịch vụ sau này), hay danh sách chăm sóc hàng ngày sẽ được chia đều ngẫu nhiên cho tất cả nhân viên trực quầy?
2. **Kênh liên lạc ưu tiên của khách quen:**
   - *Câu hỏi:* Khách hàng mua điện máy tại cửa hàng của anh thường thích nghe điện thoại trực tiếp hơn hay thích nhận tin nhắn Zalo/SMS nhắc lịch bảo dưỡng hơn?
3. **Chi phí dịch vụ bảo dưỡng cho khách quen:**
   - *Câu hỏi:* Mức giá vệ sinh điều hòa và tiền công thay lõi lọc nước cho khách cũ có bảng giá cố định niêm yết không (ví dụ: vệ sinh 150.000 đ/máy, thay lõi lọc tính nguyên giá linh kiện miễn phí công thay)?

---
*Tài liệu URD phân hệ "Khách hàng cần chăm sóc" được biên soạn bởi Đội ngũ Phân tích Nghiệp vụ (BA) dự án Stock Sense.*
