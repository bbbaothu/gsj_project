# HỆ THỐNG THIẾT KẾ & QUY CHUẨN UI-STYLING (DESIGN SYSTEM SPECIFICATION)
## HỆ THỐNG QUẢN LÝ KHO HÀNG & PHÂN PHỐI ĐIỆN MÁY THÔNG MINH - STOCK SENSE
### CHUYÊN BIỆT CHO NGÀNH HÀNG: ĐIỆN MÁY BÁN LẺ & KHO VẬN LOGISTICS (CONSUMER ELECTRONICS & WAREHOUSING)
#### Chuẩn hóa giao diện phục vụ xây dựng Prototype HTML (Tailwind CSS + HTML5)

---

## THÔNG TIN HỆ THỐNG THIẾT KẾ (DESIGN SYSTEM CONTROL)

| Mục | Đặc tả chi tiết |
| :--- | :--- |
| **Tên Design System** | **Stock Sense Design System (SSDS)** |
| **Phiên bản** | `1.0.0` (Production Ready) |
| **Triết lý thiết kế (Design Philosophy)**| **Industrial Flat & High-Density Precision** (Phẳng hiện đại, mật độ dữ liệu cao, ưu tiên tính chính xác tài chính và khả năng quét nhanh trong 3 giây) |
| **Chỉ số Design Dials (ui-ux-pro-max)** | • **Variance:** `6/10` (Cân bằng, hiện đại, chuẩn ERP/SaaS B2B)<br>• **Motion:** `4/10` (Vi mô tinh tế, chuyển trạng thái 150-200ms, không gây trễ thao tác kho)<br>• **Density:** `8/10` (Mật độ cao cho Dashboard vận hành, khoảng cách 4-16px) |
| **Công nghệ mục tiêu** | **HTML5 + Tailwind CSS v3/v4 + Google Fonts (Inter & JetBrains Mono) + Lucide / Heroicons SVG** |
| **Tài liệu nghiệp vụ tham chiếu** | [URD_01 đến URD_06](file:///Users/doanphambaothu/Documents/gsj_project/docs/) và [SRS_01 đến SRS_06](file:///Users/doanphambaothu/Documents/gsj_project/docs/reference/) |

---

## 1. NGUYÊN TẮC THIẾT KẾ CỐT LÕI (CORE DESIGN PRINCIPLES)

1. **Nguyên tắc "3 Giây Ra Quyết Định" (3-Second Decision Making):**
   Chủ cửa hàng điện máy kiêm nhiệm nhiều vai trò (bán hàng, thu ngân, giao nhận). Giao diện phải làm nổi bật ngay các điểm nóng: hàng sắp cháy, hàng đọng vốn, đơn giữ quá hạn 48h thông qua hệ thống màu sắc ngữ nghĩa mạnh mẽ, không bắt người dùng phải cộng trừ thủ công.
2. **Nguyên tắc "Toàn vẹn Dòng hàng 4 Trụ cột" (4-Pillar Inventory Flow):**
   Trong ngành điện máy, không bao giờ chỉ hiển thị một con số tồn kho duy nhất. Mọi bảng biểu và thẻ chỉ số bắt buộc phải thể hiện rõ:
   $$\text{Tồn thực tế (SOH)} \quad \rightarrow \quad \text{Hàng giữ đơn (RES)} \quad \rightarrow \quad \text{Hàng khả dụng (AVL)} \quad \rightarrow \quad \text{Hàng đang về (INC)}$$
3. **Nguyên tắc "Định danh Cá thể Thiết bị" (Serial/IMEI First-class Citizen):**
   Mỗi chiếc Tivi, Tủ lạnh, Điều hòa đều có giá trị lớn và gắn với một số Serial/IMEI vật lý duy nhất. Mã SKU, số Serial, mã đơn hàng phải luôn được trình bày bằng phông chữ đơn khoảng (Monospace), có cơ chế sao chép nhanh 1 chạm và truy vết bảo hành.
4. **Bảo mật phân quyền tại chỗ (Role-based In-place Masking):**
   Giao diện tự động thích ứng theo vai trò người dùng: Tài khoản Chủ tiệm (`ROLE_OWNER`) xem đầy đủ giá vốn, tổng tài sản két; Tài khoản Nhân viên (`ROLE_SALES`) tự động che giấu giá vốn bằng ký tự bảo mật `****** đ` mà không làm xô lệch cấu trúc bảng.

---

## 2. HỆ THỐNG BẢNG MÀU NGỮ NGHĨA (SEMANTIC COLOR SYSTEM)

Hệ thống màu sắc được xây dựng dựa trên sự kết hợp giữa **Industrial Slate (Đá xám công nghiệp)** và **Stock Emerald / Alert Coral**, đảm bảo độ tương phản đạt chuẩn **WCAG 2.1 AA ($\ge 4.5:1$)**.

```
+---------------------------------------------------------------------------------------------------+
| BẢNG MÀU NỀN TẢNG (FOUNDATION PALETTE)                                                            |
| [ Primary: #1E293B ]   [ Slate Dark: #0F172A ]   [ Surface Bg: #F8FAFC ]   [ Border: #E2E8F0 ]    |
+---------------------------------------------------------------------------------------------------+
| BẢNG MÀU DÒNG HÀNG 4 TRỤ CỘT (4-PILLAR FLOW COLORS)                                               |
| [ SOH - Tồn thực tế: #334155 (Slate) ]       [ RES - Giữ đơn: #EA580C (Amber Orange) ]           |
| [ AVL - Khả dụng bán: #059669 (Emerald) ]     [ INC - Xe đang về: #2563EB (Logistics Blue) ]      |
+---------------------------------------------------------------------------------------------------+
```

### 2.1. Bảng mã màu chi tiết (Design Tokens)

| Vai trò ngữ nghĩa | Tên biến CSS | Mã Hex | Tailwind Class | Ứng dụng thực tế trong Điện máy |
| :--- | :--- | :--- | :--- | :--- |
| **Primary (Chính)** | `--color-primary` | `#1E293B` | `bg-slate-800` / `text-slate-800` | Thanh điều hướng Header, tiêu đề chính, nút bấm chính |
| **Primary Hover** | `--color-primary-hover` | `#0F172A` | `bg-slate-900` | Trạng thái rê chuột của nút chính |
| **Secondary (Phụ)** | `--color-secondary` | `#475569` | `bg-slate-600` / `text-slate-600` | Nút thứ cấp, nhãn phụ, icon hệ thống |
| **Canvas Background** | `--color-bg-canvas` | `#F1F5F9` | `bg-slate-100` | Màu nền tổng thể trang màn hình (giảm mỏi mắt) |
| **Surface Card** | `--color-bg-card` | `#FFFFFF` | `bg-white` | Màu nền các khối thẻ KPI, bảng dữ liệu, Drawer |
| **Border / Divider** | `--color-border` | `#E2E8F0` | `border-slate-200` | Đường phân cách bảng, viền thẻ card, viền input |
| **Text Primary** | `--color-text-main` | `#0F172A` | `text-slate-900` | Văn bản chính, số liệu KPI, tên thiết bị |
| **Text Muted** | `--color-text-muted` | `#64748B` | `text-slate-500` | Nhãn chú thích, đơn vị đo, ngày tháng |

### 2.2. Màu sắc Trạng thái Vận hành Kho & Cảnh báo Rủi ro

| Trạng thái kho hàng | Biến CSS | Mã Hex | Màu nền Badge | Viền Badge | Ứng dụng nghiệp vụ |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tồn kho an toàn** | `--status-success` | `#059669` | `bg-emerald-50` | `border-emerald-200` | Tồn kho nằm trong ngưỡng Min - Max, đơn hàng hoàn tất |
| **Hàng khả dụng (AVL)**| `--flow-avl` | `#059669` | `bg-emerald-100` | `border-emerald-300` | Lượng máy có thể mở bán ngay |
| **Hàng đã giữ đơn (RES)**| `--flow-res` | `#D97706` | `bg-amber-50` | `border-amber-200` | Đơn hàng cọc giữ máy, chờ thẩm định hồ sơ trả góp |
| **Hàng đang về (INC)** | `--flow-inc` | `#2563EB` | `bg-blue-50` | `border-blue-200` | Đơn nhập PO đang vận chuyển trên xe tải |
| **Cảnh báo cần nhập gấp**| `--status-warning` | `#D97706` | `bg-amber-50` | `border-amber-300` | $SOH \le min\_stock$, hàng sắp hết mùa hè/mùa đông |
| **Cháy hàng / Tồn chết** | `--status-danger` | `#DC2626` | `bg-rose-50` | `border-rose-200` | $SOH = 0$ (OOS), Tồn kho chết $> 60$ ngày chưa bán |
| **Đơn giữ quá hạn 48h** | `--status-expired` | `#E11D48` | `bg-rose-100` | `border-rose-300` | Cảnh báo đơn cọc giữ máy quá thời hạn quy định |
| **Ngừng bán (EOL)** | `--status-eol` | `#64748B` | `bg-slate-100` | `border-slate-300` | Sản phẩm hãng đã khai tử, chuẩn bị xả sạch |

---

## 3. HỆ THỐNG TYPOGRAPHY CHUẨN TIẾNG VIỆT & DỮ LIỆU ĐIỆN MÁY

Hệ thống kết hợp bộ đôi phông chữ:
1. **Phông chữ giao diện chính:** **Inter** – Đạt chuẩn hiển thị $100\%$ các ký tự dấu tiếng Việt phức tạp (ví dụ: `ẩ`, `ẫ`, `ỡ`, `ự`, `ề`), không bị nhảy dòng, không lỗi chân chữ.
2. **Phông chữ số liệu & mã định danh:** **JetBrains Mono** – Phông chữ đơn khoảng với tính năng cố định bề ngang chữ số (`tabular-nums`), đảm bảo các bảng giá tiền và số Serial thẳng hàng tăm tắp khi hiển thị theo cột dọc.

### 3.1. Nhúng phông chữ (Google Fonts Import)
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

### 3.2. Thang tỷ lệ chữ (Typography Scale)

| Cấp bậc | Kích thước / Line-height | Phông chữ & Trọng số | Lớp Tailwind tương ứng | Mục đích sử dụng |
| :--- | :--- | :--- | :--- | :--- |
| **Display / Hero** | `28px / 36px` (`1.75rem`) | Inter Bold (`font-bold`) | `text-2xl font-bold tracking-tight` | Tiêu đề phân hệ chính, số tiền tổng vốn kẹt |
| **Heading 1 (H1)** | `22px / 28px` (`1.375rem`)| Inter SemiBold (`font-semibold`) | `text-xl font-semibold` | Tiêu đề từng màn hình làm việc |
| **Heading 2 (H2)** | `18px / 24px` (`1.125rem`)| Inter SemiBold (`font-semibold`) | `text-lg font-semibold` | Tiêu đề bảng biểu, tiêu đề khối Drawer |
| **Heading 3 (H3)** | `15px / 20px` (`0.9375rem`)| Inter Medium (`font-medium`) | `text-sm font-medium` | Tiêu đề thẻ Card, nhãn nhóm bộ lọc |
| **Body Regular** | `14px / 20px` (`0.875rem`)| Inter Regular (`font-normal`) | `text-sm font-normal text-slate-700` | Tên sản phẩm, nội dung thông báo, văn bản bảng |
| **Data Monospace** | `13px / 18px` (`0.8125rem`)| JetBrains Mono Medium | `font-mono text-xs tracking-wide` | Mã SKU, Số Serial/IMEI, Mã đơn hàng PO |
| **Price / Number** | `14px / 20px` (`0.875rem`)| JetBrains Mono SemiBold | `font-mono text-sm font-semibold tabular-nums`| Giá vốn, Giá bán, Thành tiền VNĐ |
| **Caption / Badge**| `11px / 16px` (`0.6875rem`)| Inter SemiBold (`font-semibold`) | `text-[11px] font-semibold tracking-wider uppercase`| Huy hiệu trạng thái, nhãn phân loại chip |

---

## 4. HỆ THỐNG MẬT ĐỘ KHOẢNG CÁCH (SPACING & DENSITY - DENSITY 8/10)

Vì đây là ứng dụng quản lý kho vận chuyên sâu (Operations Console) cần hiển thị nhiều dòng thiết bị trên một màn hình laptop mà không phải cuộn trang quá nhiều, hệ thống áp dụng thang khoảng cách nén chặt (Dense Grid):

```css
:root {
  --space-2xs: 2px;   /* Gaps giữa các icon nhỏ, border padding */
  --space-xs:  4px;   /* Khoảng cách trong badge, chip tag */
  --space-sm:  8px;   /* Padding ô bảng data, khoảng cách button icon */
  --space-md:  12px;  /* Padding trong input, khoảng cách giữa các phần tử form */
  --space-lg:  16px;  /* Padding card con, khoảng cách giữa các cột bộ lọc */
  --space-xl:  20px;  /* Padding trong thẻ Card KPI vĩ mô */
  --space-2xl: 24px;  /* Khoảng cách giữa các khối chức năng chính */
}
```

---

## 5. BỘ COMPONENT CHUẨN ĐẶC THÙ NGÀNH ĐIỆN MÁY (HTML + TAILWIND READY)

### 5.1. Thẻ KPI Vĩ mô Dòng hàng (Macro Metric Card)
Dùng ở đầu mỗi màn hình để hiển thị số lượng thiết bị, giá trị vốn tồn hoặc doanh số:

```html
<!-- Component: Metric Card Thống kê Vốn kẹt / Dòng hàng -->
<div class="bg-white rounded-xl border border-slate-200 p-4 shadow-sm hover:shadow-md transition-shadow duration-200">
  <div class="flex items-center justify-between mb-2">
    <span class="text-xs font-semibold uppercase tracking-wider text-slate-500">Tổng Vốn Tồn Kho (SOH)</span>
    <span class="inline-flex items-center justify-center w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>
    </span>
  </div>
  <div class="flex items-baseline space-x-2">
    <span class="font-mono text-2xl font-bold tracking-tight text-slate-900">14.280.500.000 <span class="text-sm font-normal text-slate-500">đ</span></span>
  </div>
  <div class="mt-2 flex items-center text-xs">
    <span class="inline-flex items-center font-medium text-rose-600 bg-rose-50 px-1.5 py-0.5 rounded border border-rose-200">
      <svg class="w-3 h-3 mr-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M14.707 12.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l2.293-2.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
      74.9% vốn kẹt
    </span>
    <span class="text-slate-400 ml-2">ở nhóm tồn quá cao</span>
  </div>
</div>
```

---

### 5.2. Huy hiệu Trạng thái Dòng hàng & Cảnh báo (Status Badges)

```html
<!-- Badge 1: Tồn kho an toàn -->
<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
  <span class="w-1.5 h-1.5 mr-1.5 rounded-full bg-emerald-500"></span> An toàn
</span>

<!-- Badge 2: Cảnh báo cần nhập gấp -->
<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-300">
  <span class="w-1.5 h-1.5 mr-1.5 rounded-full bg-amber-500"></span> Cần nhập gấp
</span>

<!-- Badge 3: Tồn chết / Cháy hàng (OOS) -->
<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-rose-50 text-rose-700 border border-rose-200">
  <span class="w-1.5 h-1.5 mr-1.5 rounded-full bg-rose-500"></span> Cháy hàng (OOS)
</span>

<!-- Badge 4: Hàng đang trên đường về (INC) -->
<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200">
  <svg class="w-3 h-3 mr-1 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0"/></svg>
  Đang về (15 bộ)
</span>

<!-- Badge 5: Cảnh báo đơn giữ quá hạn 48h (Pulse Animation) -->
<span class="relative inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-300">
  <span class="flex h-2 w-2 mr-1.5 relative">
    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
    <span class="relative inline-flex rounded-full h-2 w-2 bg-rose-600"></span>
  </span>
  Quá hạn 48h
</span>
```

---

### 5.3. Thẻ chip hiển thị Số Serial / IMEI (Monospace Tag with Copy)

```html
<!-- Tag hiển thị Serial/IMEI với phông đơn khoảng và nút sao chép nhanh -->
<div class="inline-flex items-center space-x-1.5 bg-slate-100 border border-slate-300 rounded px-2 py-1 font-mono text-xs text-slate-800">
  <span class="text-slate-400 select-none">#</span>
  <span class="font-medium tracking-wider select-all">SN-DK25-20261012-0045</span>
  <button type="button" class="text-slate-400 hover:text-slate-700 p-0.5 rounded hover:bg-slate-200 transition-colors cursor-pointer" title="Sao chép mã Serial">
    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
  </button>
</div>
```

---

### 5.4. Bảng Dữ liệu Tồn kho Mật độ cao (High-Density Data Table)

```html
<div class="overflow-hidden bg-white rounded-xl border border-slate-200 shadow-sm">
  <div class="overflow-x-auto">
    <table class="w-full text-left border-collapse text-sm">
      <thead>
        <tr class="bg-slate-50 border-b border-slate-200 text-xs font-semibold uppercase tracking-wider text-slate-500">
          <th class="py-3 px-4">Mã SKU</th>
          <th class="py-3 px-4">Tên Thiết Bị Điện Máy</th>
          <th class="py-3 px-4">Hãng</th>
          <th class="py-3 px-4 text-right">Giá Vốn</th>
          <th class="py-3 px-4 text-right">Giá Bán</th>
          <th class="py-3 px-3 text-center">SOH</th>
          <th class="py-3 px-3 text-center">RES</th>
          <th class="py-3 px-3 text-center">AVL</th>
          <th class="py-3 px-4 text-center">Trạng Thái</th>
          <th class="py-3 px-4 text-center">Thao Tác</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-100 text-slate-700">
        <!-- Dòng 1: Hàng bình thường an toàn -->
        <tr class="hover:bg-slate-50/80 transition-colors">
          <td class="py-2.5 px-4 font-mono text-xs font-medium text-slate-900">ML-DK-FTKB25</td>
          <td class="py-2.5 px-4 font-medium text-slate-900">
            Điều hòa Daikin Inverter 1HP FTKB25
            <span class="block text-xs font-normal text-slate-400">Model 2023 • Gas R32 • 9000 BTU</span>
          </td>
          <td class="py-2.5 px-4 text-slate-600">Daikin</td>
          <!-- Giá vốn có role-masking: nếu Sales thì đổi thành text-slate-400 '****** đ' -->
          <td class="py-2.5 px-4 text-right font-mono text-xs tabular-nums text-slate-600">8.200.000 đ</td>
          <td class="py-2.5 px-4 text-right font-mono text-xs font-semibold tabular-nums text-slate-900">10.490.000 đ</td>
          <td class="py-2.5 px-3 text-center font-mono font-medium">45</td>
          <td class="py-2.5 px-3 text-center font-mono font-medium text-amber-600">7</td>
          <td class="py-2.5 px-3 text-center font-mono font-bold text-emerald-600">38</td>
          <td class="py-2.5 px-4 text-center">
            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">An toàn</span>
          </td>
          <td class="py-2.5 px-4 text-center">
            <button class="px-2.5 py-1 text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded border border-slate-300 transition-colors cursor-pointer">Serial (45)</button>
          </td>
        </tr>
        
        <!-- Dòng 2: Hàng cháy hàng (SOH = 0, AVL = 0) -->
        <tr class="bg-rose-50/30 hover:bg-rose-50/60 transition-colors">
          <td class="py-2.5 px-4 font-mono text-xs font-medium text-rose-900">DH-CS-09</td>
          <td class="py-2.5 px-4 font-medium text-slate-900">
            Điều hòa Casper Inverter 9000BTU TC-09IS33
            <span class="block text-xs font-normal text-rose-500">Cháy hàng vật lý • 15 bộ đang trên xe về</span>
          </td>
          <td class="py-2.5 px-4 text-slate-600">Casper</td>
          <td class="py-2.5 px-4 text-right font-mono text-xs tabular-nums text-slate-600">4.200.000 đ</td>
          <td class="py-2.5 px-4 text-right font-mono text-xs font-semibold tabular-nums text-slate-900">5.690.000 đ</td>
          <td class="py-2.5 px-3 text-center font-mono font-bold text-rose-600">0</td>
          <td class="py-2.5 px-3 text-center font-mono font-medium text-slate-400">0</td>
          <td class="py-2.5 px-3 text-center font-mono font-bold text-rose-600">0</td>
          <td class="py-2.5 px-4 text-center">
            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-rose-50 text-rose-700 border border-rose-200">Cháy hàng</span>
          </td>
          <td class="py-2.5 px-4 text-center">
            <button class="px-2.5 py-1 text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 rounded transition-colors cursor-pointer shadow-sm">Xem PO về</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
```

---

### 5.5. Thanh Chuyển đổi Vai trò Bảo mật (RBAC Role Switcher)

```html
<!-- Bộ chuyển vai trò kiểm tra tức thì cơ chế Masking Giá vốn -->
<div class="inline-flex items-center p-1 bg-slate-200 rounded-lg border border-slate-300">
  <button type="button" class="flex items-center px-3 py-1.5 text-xs font-semibold rounded-md transition-all shadow-sm bg-white text-slate-900 cursor-pointer">
    <span class="mr-1.5">👑</span> Chủ Cửa Hàng (Xem Giá Vốn)
  </button>
  <button type="button" class="flex items-center px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 rounded-md transition-all cursor-pointer">
    <span class="mr-1.5">👤</span> Nhân Viên Bán Hàng (Che Vốn)
  </button>
</div>
```

---

### 5.6. Drawer / Modal Chi tiết Tác chiến (Slide-Over Drawer)

```html
<!-- Slide-over Drawer cho Tra cứu Serial hoặc Kịch bản CSKH -->
<div class="fixed inset-0 z-50 overflow-hidden" aria-labelledby="slide-over-title" role="dialog" aria-modal="true">
  <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity"></div>
  <div class="fixed inset-y-0 right-0 pl-10 max-w-full flex">
    <div class="w-screen max-w-md bg-white shadow-2xl border-l border-slate-200 flex flex-col">
      <!-- Drawer Header -->
      <div class="p-4 bg-slate-800 text-white flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold" id="slide-over-title">Chi Tiết Serial / IMEI Thiết Bị</h2>
          <p class="text-xs text-slate-300">SKU: ML-DK-FTKB25 (Tồn kho: 45 máy)</p>
        </div>
        <button class="text-slate-400 hover:text-white p-1 rounded-lg cursor-pointer">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>
      <!-- Drawer Content -->
      <div class="p-4 flex-1 overflow-y-auto space-y-3">
        <div class="p-3 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between">
          <div>
            <div class="font-mono text-xs font-bold text-slate-900">SN-DK25-20261012-0045</div>
            <div class="text-[11px] text-slate-500">Nhập kho: 12/10/2026 (Lưu kho 28 ngày)</div>
          </div>
          <span class="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-100 text-emerald-800">IN_STOCK</span>
        </div>
      </div>
      <!-- Drawer Footer -->
      <div class="p-4 border-t border-slate-200 bg-slate-50 flex justify-end space-x-2">
        <button class="px-3 py-2 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-100 cursor-pointer">Đóng</button>
        <button class="px-3 py-2 text-xs font-semibold text-white bg-slate-800 rounded-lg hover:bg-slate-900 cursor-pointer">In Danh Sách Mã</button>
      </div>
    </div>
  </div>
</div>
```

---

## 6. MẪU CẤU HÌNH TAILWIND CSS (`tailwind.config.js`) DÀNH RIÊNG CHO DỰ ÁN

Để nhúng trực tiếp vào dự án Prototype HTML bằng Tailwind CLI hoặc Play CDN:

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,js}",
    "./templates/**/*.{html,jinja}",
    "./prototypes/**/*.html"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#f8fafc',
          100: '#f1f5f9',
          500: '#64748b',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
        flow: {
          soh: '#334155', // Slate
          res: '#ea580c', // Orange Amber
          avl: '#059669', // Emerald
          inc: '#2563eb', // Logistics Blue
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      fontSize: {
        '2xs': ['0.6875rem', { lineHeight: '1rem' }], // 11px
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05)',
        'dropdown': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
      }
    },
  },
  plugins: [],
}
```

---

## 7. MẪU KHUNG HTML MASTER PROTOTYPE HOÀN CHỈNH (`prototype_template.html`)

Bạn có thể lưu đoạn mã sau thành file `.html` độc lập và mở trực tiếp trên bất kỳ trình duyệt nào để trải nghiệm ngay giao diện mẫu đạt chuẩn:

```html
<!DOCTYPE html>
<html lang="vi" class="h-full bg-slate-100">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Stock Sense - Prototype Quản Lý Kho Điện Máy</title>
  <!-- Google Fonts: Inter & JetBrains Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          fontFamily: {
            sans: ['Inter', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace'],
          }
        }
      }
    }
  </script>
</head>
<body class="h-full flex flex-col font-sans text-slate-800 antialiased selection:bg-emerald-500 selection:text-white">

  <!-- TOP HEADER -->
  <header class="bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-40">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-9 h-9 rounded-lg bg-emerald-500 flex items-center justify-center font-mono font-bold text-slate-950 text-lg shadow-sm">SS</div>
        <div>
          <h1 class="text-base font-bold tracking-tight leading-none text-white">STOCK SENSE</h1>
          <span class="text-xs text-slate-400">Điện Máy Tuấn Hưng • Kho Tổng 108 Cầu Giấy</span>
        </div>
      </div>
      
      <!-- Role Switcher -->
      <div class="flex items-center space-x-4">
        <div class="inline-flex items-center p-1 bg-slate-800 rounded-lg border border-slate-700 text-xs">
          <button class="px-2.5 py-1 font-semibold rounded bg-emerald-600 text-white shadow">👑 Chủ Tiệm</button>
          <button class="px-2.5 py-1 text-slate-400 hover:text-white">👤 Bán Hàng</button>
        </div>
        <div class="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-xs font-bold text-slate-300">TH</div>
      </div>
    </div>
  </header>

  <!-- 6 MAIN MODULE NAVIGATION TABS -->
  <nav class="bg-white border-b border-slate-200 sticky top-16 z-30 shadow-xs">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex space-x-1 overflow-x-auto text-sm font-medium">
      <a href="#" class="py-3 px-3 border-b-2 border-emerald-600 text-emerald-700 font-semibold flex items-center space-x-1.5 whitespace-nowrap">
        <span>📦</span><span>1. Tổng Quan Kho</span>
      </a>
      <a href="#" class="py-3 px-3 border-b-2 border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300 flex items-center space-x-1.5 whitespace-nowrap">
        <span>🚨</span><span>2. Cần Xử Lý Hôm Nay</span><span class="ml-1 px-1.5 py-0.2 bg-rose-100 text-rose-700 rounded-full text-xs font-bold">12</span>
      </a>
      <a href="#" class="py-3 px-3 border-b-2 border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300 flex items-center space-x-1.5 whitespace-nowrap">
        <span>🏷️</span><span>3. Gợi Ý Xả Hàng</span>
      </a>
      <a href="#" class="py-3 px-3 border-b-2 border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300 flex items-center space-x-1.5 whitespace-nowrap">
        <span>🚚</span><span>4. Gợi Ý Nhập Hàng</span>
      </a>
      <a href="#" class="py-3 px-3 border-b-2 border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300 flex items-center space-x-1.5 whitespace-nowrap">
        <span>👥</span><span>5. Khách Hàng CSKH</span>
      </a>
      <a href="#" class="py-3 px-3 border-b-2 border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300 flex items-center space-x-1.5 whitespace-nowrap">
        <span>📈</span><span>6. Hiệu Quả Kinh Doanh</span>
      </a>
    </div>
  </nav>

  <!-- MAIN BODY -->
  <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
    <!-- Macro KPIs -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Card 1 -->
      <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
        <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Tổng Tồn Thực Tế (SOH)</span>
        <div class="text-2xl font-bold font-mono text-slate-900 mt-1">1.820 <span class="text-sm font-normal text-slate-500">Thiết bị</span></div>
        <div class="text-xs text-slate-500 mt-1">Hiện diện tại kho 108 Cầu Giấy</div>
      </div>
      <!-- Card 2 -->
      <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
        <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Đang Giữ Đơn (RES)</span>
        <div class="text-2xl font-bold font-mono text-amber-600 mt-1">45 <span class="text-sm font-normal text-slate-500">Máy</span></div>
        <div class="text-xs text-amber-700 mt-1">28 Đơn cọc / Trả góp đang khóa</div>
      </div>
      <!-- Card 3 -->
      <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
        <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Khả Dụng Mở Bán (AVL)</span>
        <div class="text-2xl font-bold font-mono text-emerald-600 mt-1">1.775 <span class="text-sm font-normal text-slate-500">Máy</span></div>
        <div class="text-xs text-emerald-700 mt-1">Sẵn sàng chốt khách mới ngay</div>
      </div>
      <!-- Card 4 -->
      <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
        <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Xe Đang Về Kho (INC)</span>
        <div class="text-2xl font-bold font-mono text-blue-600 mt-1">47 <span class="text-sm font-normal text-slate-500">Máy</span></div>
        <div class="text-xs text-blue-700 mt-1">3 Chuyến xe Casper, Aqua về hôm nay</div>
      </div>
    </div>
  </main>
</body>
</html>
```

---

## 8. DANH MỤC BIỂU TƯỢNG (ICONS) CHUẨN HÓA THEO LUCIDE/HEROICONS

Tuyệt đối **không sử dụng Emoji** trong giao diện sản xuất để tránh vỡ font trên các hệ điều hành Windows/Linux cũ. Sử dụng các Icon SVG sau:
- **Tồn kho / Box:** `<svg ... d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>`
- **Xe tải giao hàng / In-Transit:** `<svg ... d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0"/>`
- **Cảnh báo nguy hiểm / Rủi ro:** `<svg ... d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>`
- **Sao chép mã Serial:** `<svg ... d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>`
- **Bộ lọc tìm kiếm:** `<svg ... d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/>`

---
*Tài liệu Hệ thống Thiết kế Stock Sense (SSDS) đã được đồng bộ hoàn toàn với Skill `ui-ux-pro-max` và sẵn sàng phục vụ lập trình giao diện Prototype HTML.*
