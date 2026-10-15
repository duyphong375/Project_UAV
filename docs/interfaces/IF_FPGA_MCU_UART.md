# Đặc tả giao diện: FPGA OneKiwi ↔ MCU Tải Sonix (UART BBox)

- **Mã giao diện:** `IF-01`
- **Hai đầu kết nối:** FPGA OneKiwi Primer 20K (**Nguyễn Tất Vững** - Đầu phát TX) ↔ MCU Sonix SN34F788 (**Nguyễn Tá Duy Phong** - Đầu nhận RX)
- **Trạng thái:** `DRAFT ABI` (Dự thảo kỹ thuật theo mục IV.2 [KVC_ThietKeHeThong.md](../KVC_ThietKeHeThong.md); cần Vững và Phong thống nhất trước khi khóa ABI)

---

## 1. Kết nối vật lý và đường truyền

| Tín hiệu | Hướng | Mức điện áp | Mô tả kỹ thuật |
| :--- | :---: | :---: | :--- |
| **UART_TX (FPGA)** → **UART_RX (MCU)** | FPGA → MCU | 3,3 V CMOS | Đường truyền dữ liệu nối tiếp khung kết quả BBox |
| **DATA_READY** | FPGA → MCU | 3,3 V CMOS | Chân báo hiệu khung ảnh mới sẵn sàng; kích hoạt ngắt ngoài (EXTI) trên MCU |
| **GND** | Hai chiều | 0 V | **Nối chung GND bắt buộc** giữa bo OneKiwi và kit Sonix |

### Tham số UART
- **Baudrate:** Khởi đầu ở **115.200 bps** để kiểm tra tính đúng đắn; sau khi đo sai số xung nhịp ổn định có thể nâng lên **460.800 bps** hoặc **921.600 bps**.
- **Cấu hình bit:** 8N1 (8 bit dữ liệu, No Parity, 1 Stop bit).

---

## 2. Cấu trúc khung truyền BBox (AI Detection Frame)

Toàn bộ số nguyên nhiều byte lưu theo định dạng **Little-Endian** (byte thấp trước).

```text
+---------------+-----------+-----------------+----------------+--------------------+-----------+
| Sync (2B)     | Ver (1B)  | Count N (1B)    | Timestamp (4B) | N x BBox (N x 8B)  | CRC (2B)  |
| 0x5A 0xA5     | 0x01      | 0 .. 20         | uint32 (ms)    | Mỗi BBox 8 byte    | CRC-16    |
+---------------+-----------+-----------------+----------------+--------------------+-----------+
```

### Bảng phân rã khung truyền

| Offset | Độ dài | Tên trường | Kiểu dữ liệu | Mô tả |
| :---: | :---: | :--- | :--- | :--- |
| **0–1** | 2 byte | Sync Header | `uint8[2]` | Cố định `0x5A 0xA5` (nhận diện đầu khung) |
| **2** | 1 byte | Version | `uint8` | Phiên bản giao thức (giá trị `1`) |
| **3** | 1 byte | Candidate Count ($N$) | `uint8` | Số lượng mục tiêu phát hiện trong frame (tối đa 20 mục tiêu) |
| **4–7** | 4 byte | Timestamp | `uint32` | Thời điểm chụp/suy luận của khung ảnh (ms) |
| **8 .. (8+8N-1)** | $N \times 8$ byte | Danh sách BBox | Mảng struct BBox | Chứa thông tin vị trí và phân loại của $N$ đối tượng |
| **Cuối** | 2 byte | CRC-16 Checksum | `uint16` | **CRC-16/CCITT-FALSE** tính từ byte 0 đến hết danh sách BBox |

---

## 3. Cấu trúc chi tiết 8 byte của từng Bounding Box (BBox)

Mỗi mục tiêu được mã hóa trong đúng 8 byte:

| Byte | Tên trường | Kiểu dữ liệu | Đơn vị / Phạm vi | Ý nghĩa |
| :---: | :--- | :--- | :--- | :--- |
| **0–1** | `X_center` | `uint16` | pixel | Tọa độ tâm X của BBox trên khung ảnh gốc |
| **2–3** | `Y_center` | `uint16` | pixel | Tọa độ tâm Y của BBox trên khung ảnh gốc |
| **4** | `Width` | `uint8` | pixel (0–255) | Chiều rộng BBox (nếu ảnh scale chuẩn) |
| **5** | `Height` | `uint8` | pixel (0–255) | Chiều cao BBox (nếu ảnh scale chuẩn) |
| **6** | `Class_ID` | `uint8` | Enum | `1`: `person` (người trôi dạt)<br>`2`: `lifebuoy` (phao cứu sinh) |
| **7** | `Confidence` | `uint8` | 0 – 100 (%) | Mức độ tin cậy của thuật toán AI |

---

## 4. Cơ chế đồng bộ và xử lý lỗi đường truyền

1. **Phía FPGA (Vững):**
   - Khi có kết quả suy luận AI từ camera, ghi danh sách BBox vào bộ đệm FIFO UART.
   - Kéo chân `DATA_READY` lên mức HIGH trong 1–5 µs để kích hoạt ngắt trên MCU Sonix.
   - Bắt đầu truyền luồng byte qua UART. Nếu không có mục tiêu nào trong khung ảnh ($N = 0$), vẫn gửi gói tin rỗng hợp lệ (độ dài 10 byte: 2B Sync + 1B Ver + 1B Count=0 + 4B Time + 2B CRC).
2. **Phía MCU Sonix (Phong):**
   - Nhận diện ngắt chân `DATA_READY`, kích hoạt DMA hoặc bộ đệm vòng Ring Buffer UART để thu nhận toàn bộ frame.
   - Kiểm tra 2 byte đầu khung `0x5A 0xA5`. Nếu sai, trượt tìm lại mốc đồng bộ (Resynchronization).
   - Kiểm tra CRC-16; nếu đúng, nạp BBox vào bài toán giao điểm tia quang học tính tọa độ. Nếu sai, bỏ qua frame và tăng bộ đếm lỗi `uart_crc_err`.
