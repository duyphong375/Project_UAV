# Đặc tả giao diện: MCU Tải Sonix ↔ ESP32 Trạm Đất (LoRa RF Telemetry)

- **Mã giao diện:** `IF-02`
- **Hai đầu kết nối:** MCU Sonix SN34F788 trên UAV (**Nguyễn Tá Duy Phong** - Đầu phát TX) ↔ ESP32-C3 Gateway Trạm Đất (kit/board TBD; **Đoàn Thanh Trường Thịnh** - Đầu thu RX)
- **Trạng thái:** `DRAFT ABI` (Dự thảo kỹ thuật theo mục IV.3 [KVC_ThietKeHeThong.md](../KVC_ThietKeHeThong.md); Phong và Thịnh cần thống nhất trước khi nạp phần cứng)

---

## 1. Cấu hình vô tuyến LoRa (RF Physical Parameters)

Hệ thống sử dụng 02 module **LoRa Ra-02 (chip Semtech SX1278)** giao tiếp qua SPI:

| Tham số | Giá trị thiết lập | Ghi chú kỹ thuật |
| :--- | :---: | :--- |
| **Tần số trung tâm (Frequency)** | **433.0 MHz** | Băng tần ISM không cần xin phép, phù hợp module Ra-02 |
| **Băng thông (Bandwidth - BW)** | **125 kHz** | Cân bằng giữa độ nhạy thu và tốc độ truyền |
| **Hệ số trải phổ (Spreading Factor - SF)** | **Candidate SF7/SF8; PENDING** | Khớp các phép tính airtime trong thiết kế; chưa được duyệt hoặc đo trên module thực |
| **Tỷ lệ mã sửa sai (Coding Rate - CR)** | **4/7** (hoặc 4/5) | Bảo vệ chống nhiễu xung vô tuyến |
| **Độ dài Preamble** | **8 symbols** | Preamble tiêu chuẩn cho SX1278 |
| **Sync Word** | **`0x12`** | Phân biệt mạng nội bộ KVC (tránh xung đột mạng LoRaWAN 0x34) |
| **Công suất phát (Tx Power)** | **+17 dBm** (tối đa +20 dBm) | Điều chỉnh theo quy định và giới hạn dòng nguồn |
| **CRC phần cứng SX1278** | **BẬT (Enabled)** | Tự động loại bỏ gói lỗi ở tầng PHY |

---

## 2. Cấu trúc gói tin Telemetry (RF Payload Format)

> **LƯU Ý LỊCH SỬ:** Mã nguồn cũ ghi nhận telemetry 20 byte. Bản thiết kế hệ thống đề xuất gói tin tiêu chuẩn **32 byte** dưới đây để chứa đủ cờ hợp lệ cảm biến và định vị kép (WGS-84 / Local Grid). Toàn bộ số nguyên đa byte lưu theo chuẩn **Little-Endian**.

```text
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Sync (0xAA 0x55)        |  Msg_ID (1B)  |   Seq_Num (1B)|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                          Timestamp (4B)                       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Target_Lat (4B, int32)                  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Target_Lon (4B, int32)                  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|      Target_X_local (2B)      |      Target_Y_local (2B)      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|   Altitude_Dist_cm(2B,uint16) |  Class_ID (1B)| Confidence(1B)|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Sensor_Flags |  UAV_Battery  |         CRC-16/CCITT          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### Bảng phân rã 32 byte chi tiết:

| Offset | Kích thước | Tên trường | Kiểu dữ liệu | Đơn vị / Ý nghĩa |
| :---: | :---: | :--- | :--- | :--- |
| **0–1** | 2 byte | Sync Header | `uint8[2]` | Cố định `0xAA 0x55` |
| **2** | 1 byte | Message ID | `uint8` | `0x01`: Telemetry mục tiêu, `0x02`: Heartbeat/Ping |
| **3** | 1 byte | Sequence Number | `uint8` | Bộ đếm gói (0–255, xoay vòng) phát hiện mất gói |
| **4–7** | 4 byte | Timestamp | `uint32` | Thời gian MCU (ms) tính từ lúc khởi động |
| **8–11** | 4 byte | Target Latitude | `int32` | Vĩ độ WGS-84 mục tiêu ($\times 10^7$ độ); `0` nếu không có GNSS fix |
| **12–15** | 4 byte | Target Longitude | `int32` | Kinh độ WGS-84 mục tiêu ($\times 10^7$ độ); `0` nếu không có GNSS fix |
| **16–17** | 2 byte | Target X Local | `int16` | Tọa độ X so với mốc bể bơi/sa bàn (đơn vị: cm) |
| **18–19** | 2 byte | Target Y Local | `int16` | Tọa độ Y so với mốc bể bơi/sa bàn (đơn vị: cm) |
| **20–21** | 2 byte | Altitude Distance | `uint16` | Khoảng cách đo mặt nước từ cảm biến siêu âm AJ-SR04M (đơn vị: cm) |
| **22** | 1 byte | Class ID | `uint8` | `1`: `person` (người), `2`: `lifebuoy` (phao) |
| **23** | 1 byte | Confidence | `uint8` | Độ tin cậy nhận diện (0–100%) |
| **24** | 1 byte | Sensor Status Flags | `uint8` | Bit 0: GNSS 3D Fix hợp lệ<br>Bit 1: Cự ly siêu âm hợp lệ (ALT_VALID)<br>Bit 2: IMU hợp lệ<br>Bit 3: FPGA BBox có mục tiêu<br>Bit 4–7: Dự phòng |
| **25** | 1 byte | Battery / Status | `uint8` | Điện áp pin UAV (0,1 V / bit, vd: 126 = 12.6V) |
| **26–29** | 4 byte | Dự phòng mở rộng | `uint8[4]` | Đệm mở rộng cho độ cao barometer / nhiệt độ |
| **30–31** | 2 byte | CRC-16 Checksum | `uint16` | **CRC-16/CCITT-FALSE** (Poly `0x1021`, Init `0xFFFF`) tính từ byte 0 đến byte 29 |

---

## 3. Quy trình xác nhận và nghiệm thu (Verification)

1. **Phía MCU Sonix (Phong):**
   - Đóng gói đúng 32 byte theo thứ tự Little-Endian.
   - Tính CRC-16 trước khi nạp buffer SPI vào SX1278.
   - Thiết kế tính airtime khoảng 71,9 ms (SF7) / 133,6 ms (SF8) với các giả định đã nêu tại mục IV.3. Chưa xác minh trên thanh ghi thực; chu kỳ phát và giới hạn duty-cycle còn chờ cấu hình/địa điểm được duyệt.
2. **Phía ESP32 Trạm Đất (Thịnh):**
   - Đọc gói tin khi chân DIO0 (RxDone) kích hoạt ngắt.
   - Đọc kèm 2 thông số chất lượng sóng từ thanh ghi SX1278:
     * **RSSI** (Received Signal Strength Indicator, dBm)
     * **SNR** (Signal-to-Noise Ratio, dB)
   - Kiểm tra CRC-16 gói tin; nếu sai, tăng bộ đếm lỗi và bỏ qua gói.
