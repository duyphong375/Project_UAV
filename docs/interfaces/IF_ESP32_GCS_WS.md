# Đặc tả giao diện: ESP32 Trạm Đất ↔ Backend GCS Laptop (Wi-Fi SoftAP / WebSocket)

- **Mã giao diện:** `IF-03`
- **Hai đầu kết nối:** ESP32-C3 Gateway Trạm Đất (kit/board TBD; **Đoàn Thanh Trường Thịnh** - Wi-Fi SoftAP & WebSocket Server) ↔ Dịch vụ Backend Python trên Laptop GCS (**Đoàn Thanh Trường Thịnh** - WebSocket Client Ingress)
- **Trạng thái:** `DESIGN BASELINE / CHƯA XÁC MINH`. Endpoint mục tiêu theo mục IV.4 [KVC_ThietKeHeThong.md](../KVC_ThietKeHeThong.md) là `ws://192.168.4.1:8080/telemetry`; chưa có firmware ingress/capture để xác nhận hoạt động.

---

## 1. Kiến trúc kết nối và Topology mạng

```text
+------------------------------------+
|    ESP32-C3 Gateway (kit TBD)       |
|    - Nguồn độc lập (Pin/Power Bank)|
|    - Thu LoRa SX1278 (SPI)         |
|    - Phát Wi-Fi SoftAP             |
|    - WebSocket Server (:8080/telemetry) |
+-----------------+------------------+
                  │
                  │  Sóng Wi-Fi 802.11 b/g/n (SSID: KVC_GCS_AP)
                  │  Giao thức: WebSocket (ws://192.168.4.1:8080/telemetry)
                  ▼
+------------------------------------+
|    Backend GCS trên Laptop (Host)  |
|    - Kết nối Wi-Fi vào ESP32       |
|    - Chạy Client WebSocket Ingress | ──► Ghi nhật ký vào SQLite WAL (sqlite_logger.py)
|    - Quản lý trạng thái State      | ──► Động cơ phát lại (replay_engine.py)
|    - Mở WebSocket Server nội bộ    |
|      (ws://127.0.0.1:8000/ws)      |
+-----------------+------------------+
                  │
                  │  Localhost WebSocket nội bộ máy tính
                  ▼
+------------------------------------+
|    Frontend Dashboard trên Browser |
|    - React + TypeScript + Vite     |
|    - Vẽ Radar Canvas, Bản đồ OSM   |
|    - Bảng cảnh báo và trạng thái   |
+------------------------------------+
```

> ⚠️ **QUY TẮC CỐT LÕI:**
> 1. Trình duyệt Web (Dashboard) **tuyệt đối không kết nối trực tiếp vào ESP32**. Trình duyệt chỉ kết nối vào Backend Python tại `ws://127.0.0.1:8000/ws`.
> 2. Backend Python trên laptop là client ingress mục tiêu. Việc ghi bền vững/replay phụ thuộc ứng dụng và chưa được xác minh với ingress ESP32.

---

## 2. Cấu hình mạng Wi-Fi SoftAP của ESP32

ESP32 tự khởi tạo một Access Point (AP) độc lập không cần router Internet:

| Tham số | Giá trị thiết lập | Ghi chú |
| :--- | :--- | :--- |
| **SSID** | `KVC_GCS_AP` | Tên mạng Wi-Fi phát từ ESP32 |
| **Mật khẩu (Password)** | Cấu hình riêng khi triển khai; không ghi giá trị vào tài liệu/source/log | Dùng cơ chế bảo mật được duyệt; không commit credential |
| **Địa chỉ IP của ESP32** | `192.168.4.1` | Địa chỉ IP mặc định của SoftAP ESP32 |
| **Subnet Mask** | `255.255.255.0` | Dải mạng cục bộ |
| **WebSocket Port** | `8080` | Endpoint mục tiêu theo thiết kế; chưa xác minh trên firmware |
| **Endpoint URL** | `ws://192.168.4.1:8080/telemetry` | Backend Python kết nối tới; baseline DESIGN, chưa kiểm thử thiết bị |

---

## 3. Transport envelope WebSocket v1 (DESIGN)

Mỗi message JSON UTF-8 chuyển tiếp một RF payload 32 byte còn nguyên vẹn. ESP32 loại payload không qua CRC-16 trước khi tạo message; không bóc tách target/application fields tại boundary này. `rf_payload_hex` giữ đúng thứ tự 32 byte nhận được. Backend GCS chịu trách nhiệm decode/mapping theo RF ABI sau khi ABI được duyệt. Phần parser/ingress REAL hiện chưa triển khai.

```json
{
  "transport_version": 1,
  "gateway_session_id": 3,
  "gateway_sequence": 42,
  "rx_monotonic_ms": 125430,
  "rf_payload_hex": "aa5501010000000000000000000000000000000000000000000000000000798f",
  "rssi_dbm": -76,
  "snr_db": 8.5,
  "rx_drop_count": 0
}
```

| Trường | Kiểu / quy tắc |
| --- | --- |
| `transport_version` | Integer; hiện bằng `1`. |
| `gateway_session_id` | `uint32`; thay đổi khi ESP32 khởi động lại. |
| `gateway_sequence` | `uint32`; tăng theo message, wrap modulo `2^32`. |
| `rx_monotonic_ms` | `uint32`; thời gian monotonic kể từ lúc ESP32 boot, không phải UTC. |
| `rf_payload_hex` | 64 ký tự hex thường, đúng 32 byte đã qua kiểm tra CRC-16; không sửa field/endian. |
| `rssi_dbm`, `snr_db` | Số đo nhận từ SX1278 theo đơn vị dBm và dB. |
| `rx_drop_count` | `uint32`; số message hợp lệ bị loại ở ESP32 do buffer đầy kể từ boot. |

Heartbeat riêng không thuộc envelope v1 đã mô tả. Link stale/disconnect được suy ra ở backend theo thời gian nhận message hợp lệ; muốn thêm loại message trạng thái cần schema/version được duyệt.

---

## 4. Xử lý mất kết nối và tự động phục hồi (Reconnection & Fallback)

1. **Khi laptop tắt hoặc mất sóng Wi-Fi:**
   - ESP32 trạm đất vẫn duy trì nguồn pin riêng, tiếp tục nhận và đếm gói LoRa.
   - Thiết kế mục tiêu giữ tối đa 64 message hợp lệ trong FIFO RAM; đầy thì loại message cũ nhất và tăng `rx_drop_count`. Chưa triển khai/xác minh.
2. **Phía Backend Python trên laptop:**
   - Khởi chạy client ingress mục tiêu tới `ws://192.168.4.1:8080/telemetry`.
   - Thiết kế đề xuất reconnect backoff 1–5 giây; trạng thái sequence reset khi `gateway_session_id` đổi.
   - Backend đánh dấu dữ liệu stale khi không có message RF hợp lệ trong 3 giây. Buffer/reconnect/stale values chưa được xác minh bằng integration test.
