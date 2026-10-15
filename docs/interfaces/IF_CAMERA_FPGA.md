# Đặc tả dự thảo: Camera Quang học ↔ FPGA OneKiwi Primer 20K

- **Mã giao diện:** `IF-CAM`
- **Hai đầu kết nối:** Cụm Camera quang học (**Trương Trung Kiên** - Chọn cáp, nguồn, gá lắp) ↔ Bo FPGA OneKiwi Primer 20K V1.1 (**Nguyễn Tất Vững** - Nhận luồng pixel và cấu hình)
- **Trạng thái:** `DRAFT / CHƯA DUYỆT`; camera, connector, rail và pin map trên board thực chưa xác minh.

---

## 1. Kết nối vật lý và Cáp giao tiếp (Physical Connector)

* **Chuẩn cổng kết nối:** TBD. Chưa có bằng chứng OneKiwi Primer 20K V1.1 có đầu nối FPC 24 chân/DVP như nội dung bảng tham khảo cũ.
* **Module Camera mục tiêu:** TBD. OV5640/DVP trong bản tham khảo cũ không phải lựa chọn đã duyệt; thiết kế hệ thống hiện chưa chốt model.

---

## 2. Bảng tín hiệu DVP tham khảo (không phải pinout OneKiwi đã xác minh)

> Các số chân, mức điện áp và rail dưới đây chỉ là ví dụ phân rã cho một camera DVP candidate; không được dùng để đấu dây hay cấp nguồn. Xác minh schematic/revision OneKiwi, camera module, connector, VCCIO và pin assignment trước khi tạo wiring hoặc constraint.

| Chân FPC | Tên tín hiệu | Hướng | Mức điện áp | Mô tả chức năng |
| :---: | :--- | :---: | :---: | :--- |
| **1** | **GND** | — | 0 V | Nối đất chung |
| **2** | **DOVDD** | Nguồn | 3,3 V / 2,8 V | Nguồn I/O số cho camera (từ LDO bo OneKiwi) |
| **3** | **SIOD** | Hai chiều | 3,3 V | Dữ liệu cấu hình camera (I2C / SCCB SDA, trở kéo 4,7 kΩ) |
| **4** | **AVDD** | Nguồn | 2,8 V | Nguồn tương tự (Analog) cho sensor |
| **5** | **SIOC** | FPGA ➔ Cam | 3,3 V | Xung nhịp cấu hình camera (I2C / SCCB SCL, max 400 kHz) |
| **6** | **RESET** | FPGA ➔ Cam | 3,3 V | Reset phần cứng camera (Active LOW) |
| **7** | **VSYNC** | Cam ➔ FPGA | 3,3 V | Tín hiệu đồng bộ khung ảnh (Báo bắt đầu frame mới) |
| **8** | **PWDN** | FPGA ➔ Cam | 3,3 V | Điều khiển chế độ tiết kiệm năng lượng (Active HIGH, bình thường kéo LOW) |
| **9** | **HREF** | Cam ➔ FPGA | 3,3 V | Tín hiệu đồng bộ dòng quét ảnh (Horizontal Reference) |
| **10** | **DVDD** | Nguồn | 1,5 V | Nguồn nhân số lõi camera |
| **11..18**| **D7 .. D0** | Cam ➔ FPGA | 3,3 V | Bus dữ liệu pixel song song 8-bit |
| **19** | **PCLK** | Cam ➔ FPGA | 3,3 V | Xung nhịp pixel (Pixel Clock ra từ camera, ~24–48 MHz) |
| **20** | **XCLK / MCLK** | FPGA ➔ Cam | 3,3 V | Xung nhịp cấp cho camera (24 MHz phát từ PLL của Gowin) |
| **21..24**| **GND / NC** | — | 0 V | Nối đất bảo vệ chống nhiễu cao tần |

---

## 3. Cấu hình chế độ hoạt động (Camera Operating Mode)

1. **Khởi tạo và cấu hình (I2C / SCCB):**
   - Vững viết FSM trên FPGA gửi các lệnh ghi thanh ghi qua bus I2C (địa chỉ camera `0x78` hoặc `0x3C`).
   - Cấu hình độ phân giải khung hình: **VGA (640 $\times$ 480)** hoặc **640 $\times$ 640** (phù hợp đầu vào YOLO11n).
   - Tốc độ khung hình mục tiêu: **15 – 30 FPS**.
2. **Định dạng dữ liệu Pixel:**
   - **RGB565** (2 byte / pixel, nhận qua 2 chu kỳ PCLK: Byte cao chứa R và nửa G, byte thấp chứa nửa G và B).
   - Hoặc **YUV422** (YUYV) để trích xuất trực tiếp kênh độ sáng Y phục vụ tiền xử lý nhanh.

---

## 4. Trách nhiệm phối hợp giữa Kiên và Vững

* **Kiên (Phần cứng):**
  - Kiểm tra cáp FPC cắm đúng chiều (tiếp xúc mạ vàng úp/ngửa theo socket của bo OneKiwi).
  - Cố định gá camera vững chắc trên thân tải, không để rung lắc hoặc gập gãy cáp khi UAV di chuyển.
  - Đo kiểm điện áp chân cấp nguồn AVDD (2.8V), DVDD (1.5V), DOVDD (3.3V) không bị sụt áp.
* **Vững (FPGA):**
  - Chỉ tạo clock/configuration sau khi xác minh camera và pin map đã chọn.
  - Đánh giá buffering bằng bộ nhớ có thật trên board. Hardware notes cho biết OneKiwi V1.1 không có chip DDR3 ngoài; không thiết kế dựa trên DDR3 chưa lắp.
