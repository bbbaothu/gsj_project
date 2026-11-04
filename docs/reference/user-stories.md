# BÁO CÁO KHẢO SÁT NHU CẦU NGƯỜI DÙNG & XÁC THỰC TÍNH NĂNG
## Dự án Phần mềm Quản lý Kho hàng Điện máy Thông minh - Stock Sense

---

## 1. TỔNG QUAN DỰ ÁN VÀ MỤC ĐÍCH KHẢO SÁT

### 1.1. Bối cảnh
Ngành kinh doanh điện máy tại Việt Nam có đặc thù riêng: giá trị hàng hóa lớn, mẫu mã và công nghệ thay đổi nhanh theo mùa, rủi ro tồn kho, mất giá hoặc lỗi mốt cao. Đối với các chủ cửa hàng và quản lý kho điện máy, việc nắm bắt chính xác dòng tiền đọng trong kho, dự báo thời điểm xả hàng hay nhập hàng là bài toán sống còn. Phần mềm **Stock Sense** được định hướng xây dựng nhằm giải quyết triệt để các bài toán này bằng sự kết hợp giữa quản lý kho truyền thống và công nghệ phân tích thông minh.

### 1.2. Mục đích của tài liệu
Tài liệu này tổng hợp kết quả khảo sát thực tế giữa đội ngũ phân tích nghiệp vụ (BA) và chủ doanh nghiệp điện máy. Cấu trúc nội dung được thiết kế dưới dạng **Câu chuyện người dùng (User Stories)** nhằm giúp các bên liên quan không chuyên sâu về kỹ thuật phần mềm nhưng am hiểu nghiệp vụ kinh doanh dễ dàng đọc hiểu, trao đổi, đóng góp ý kiến và tiến hành phê duyệt danh sách chức năng trước khi chuyển sang bước thiết kế tài liệu yêu cầu người sử dụng (URD) chi tiết.

---

## 2. DANH SÁCH CÁC CÂU CHUYỆN NGƯỜI DÙNG (USER STORIES) THEO CÂY CHỨC NĂNG

### Nhóm 1: Tổng quan kho
Giúp người quản lý nắm bắt toàn diện bức tranh về tài sản tồn kho và tình trạng dòng đơn hàng theo thời gian thực mà không cần kiểm kê thủ công phức tạp.

*   **US-1.1: Tra cứu tổng quan danh mục sản phẩm và lượng tồn kho**
    *   *Là một* Quản lý kho / Chủ cửa hàng điện máy,
    *   *Tôi muốn* xem nhanh tổng số lượng sản phẩm, số lượng tồn kho chi tiết và giá vốn tồn kho hiện tại,
    *   *Để* nắm được tổng giá trị tài sản đang đọng trong kho và có chiến lược phân bổ vốn phù hợp.
*   **US-1.2: Theo dõi trạng thái đơn hàng và dòng hàng linh hoạt**
    *   *Là một* Nhân viên bán hàng / Quản lý cửa hàng,
    *   *Tôi muốn* thống kê và theo dõi trạng thái các đơn hàng cụ thể bao gồm: hàng đã giữ đơn, hàng đang trên đường về, và các hình thức thanh toán (trả góp hoặc trả toàn phần),
    *   *Để* chủ động giao hàng cho khách đúng hẹn và kiểm soát chính xác lượng hàng đã cam kết giao dịch.

---

### Nhóm 2: Cần xử lý hôm nay
Hệ thống tự động sàng lọc và đưa ra danh sách các mặt hàng đang gặp vấn đề rủi ro để người quản lý tập trung xử lý ngay trong ngày, tránh thiệt hại kinh tế.

*   **US-2.1: Cảnh báo hàng bán chậm, hàng ngừng bán và hàng sắp hết mùa**
    *   *Là một* Chủ cửa hàng / Nhân viên phụ trách thu mua,
    *   *Tôi muốn* hệ thống tự động chỉ ra các mặt hàng bán chậm, hàng đã ngừng kinh doanh hoặc các sản phẩm điện máy sắp hết mùa (ví dụ: máy lạnh vào mùa đông, quạt sưởi vào mùa hè),
    *   *Để* kịp thời đưa ra phương án điều chỉnh giá hoặc gom nhóm thanh lý, tránh tồn kho chết.
*   **US-2.2: Cảnh báo sản phẩm sắp thiếu hụt (cháy hàng)**
    *   *Là một* Nhân viên quản lý kho,
    *   *Tôi muốn* nhận diện ngay các sản phẩm điện máy có xu hướng sắp thiếu hụt trong kho dựa trên tốc độ bán thực tế,
    *   *Để* lập kế hoạch bổ sung hàng kịp thời, không để đứt gãy chuỗi cung ứng phục vụ khách hàng.

---

### Nhóm 3: Gợi ý xả hàng
Hỗ trợ chủ doanh nghiệp ra quyết định thanh lý, xả hàng tồn kho một cách khoa học dựa trên số liệu phân tích thị trường và đối thủ.

*   **US-3.1: Nhận đề xuất chiến lược xả hàng thông minh**
    *   *Là một* Chủ cửa hàng điện máy,
    *   *Tôi muốn* hệ thống cung cấp danh sách sản phẩm cần xả kèm theo lý do cảnh báo cụ thể, lượng cần bán, phương án khuyến mại đề xuất và mức lãi dự kiến,
    *   *Để* cân đối giữa việc thu hồi vốn nhanh và tối ưu hóa lợi nhuận cuối cùng.
*   **US-3.2: So sánh giá thị trường và đưa ra giá gợi ý**
    *   *Là một* Nhân viên kinh doanh / Cán bộ định giá,
    *   *Tôi muốn* xem đối chiếu so sánh giá bán của sản phẩm định xả với đối thủ cạnh tranh trên thị trường kèm theo mức giá gợi ý từ hệ thống,
    *   *Để* đưa ra quyết định hạ giá bán cạnh tranh nhưng vẫn đảm bảo tính khả thi về mặt tài chính.

---

### Nhóm 4: Gợi ý nhập hàng
Giúp tối ưu hóa nguồn vốn lưu động bằng cách đề xuất chính xác số lượng cần nhập dựa trên dữ liệu dự báo khoa học thay vì cảm tính.

*   **US-4.1: Nhận đề xuất lượng nhập hàng chuẩn xác**
    *   *Là một* Phụ trách mua hàng / Chủ doanh nghiệp,
    *   *Tôi muốn* xem nhu cầu dự kiến của thị trường, lượng hàng có thể bán, hàng đang trên đường về, lượng nhập đề xuất và độ tin cậy cao của dự báo,
    *   *Để* tiến hành đặt hàng với nhà cung cấp với số lượng vừa đủ, không bị tồn kho dư thừa hay thiếu hụt vốn.

---

### Nhóm 5: Khách hàng cần chăm sóc
Khai thác dữ liệu kho hàng kết hợp lịch sử mua sắm để thúc đẩy hoạt động chăm sóc khách hàng và bán cross-selling/up-selling hiệu quả.

*   **US-5.1: Nhận diện khách hàng tiềm năng cần chăm sóc định kỳ**
    *   *Là một* Nhân viên chăm sóc khách hàng / Nhân viên bán hàng,
    *   *Tôi muốn* xem danh sách bao gồm tên khách hàng, sản phẩm điện máy họ đã mua trước đó, dấu hiệu nhu cầu phát sinh (ví dụ: đã đến hạn bảo dưỡng, sắp đổi đời máy mới, hoặc mua phụ kiện đi kèm), gợi ý nội dung tư vấn và lịch sử liên hệ gần nhất,
    *   *Để* chủ động gọi điện, nhắn tin chăm sóc, tạo dựng mối quan hệ thân thiết và kích thích nhu cầu mua sắm lặp lại.

---

### Nhóm 6: Hiệu quả kinh doanh
Cung cấp góc nhìn đánh giá hiệu quả tài chính sau các chiến dịch bán hàng hoặc sau chu kỳ kinh doanh ngắn hạn.

*   **US-6.1: Thống kê hiệu quả thu hồi vốn và doanh thu bán kèm**
    *   *Là một* Chủ doanh nghiệp điện máy,
    *   *Tôi muốn* theo dõi cụ thể số lượng hàng tồn đã bán được, lượng vốn thực tế đã thu hồi, và tổng doanh thu từ các sản phẩm bán kèm (phụ kiện, dịch vụ lắp đặt, bảo hành mở rộng),
    *   *Để* đánh giá chính xác hiệu quả kinh doanh của cửa hàng và đo lường sự thành công của các chương trình xả hàng/nhập hàng đã triển khai.

---

## 3. KẾ HOẠCH TIẾP THEO VÀ PHÊ DUYỆT

1.  **Thống nhất phạm vi:** Quý đối tác / Chủ doanh nghiệp xem xét các User Stories trên và xác nhận phạm vi tính năng.
2.  **Ký duyệt danh sách:** Thống nhất danh sách chức năng cốt lõi cho phiên bản đầu tiên (MVP) của phần mềm Stock Sense.
3.  **Chuyển giao URD:** Đội ngũ BA sẽ dựa trên bản phê duyệt này để hoàn thiện chi tiết Tài liệu Yêu cầu Người sử dụng (URD) trong thời gian quy định (trong vòng 4 giờ tới).