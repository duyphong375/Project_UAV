# KVC — Phân hệ Gateway Trạm Đất ESP32-C3

- **Người phụ trách:** **Đoàn Thanh Trường Thịnh**
- **Phần cứng mục tiêu:** Bo mạch **ESP32-C3 DevKit** (Kiến trúc 32-bit RISC-V đơn nhân 160 MHz, nguồn pin riêng độc lập, kèm module LoRa Ra-02 433 MHz)
- **Công cụ phát triển (IDE / Toolchain):** **PlatformIO IDE** (trên VS Code) với **`framework = arduino`** (Arduino Core for ESP32, board `esp32-c3-devkitm-1`)
- **File cấu hình dự án đã tạo sẵn:** [platformio.ini](platformio.ini)

---

## 1. Nhiệm vụ của phân hệ Gateway ESP32

1. **Thu tín hiệu LoRa:** Đọc gói từ MCU Sonix trên UAV; RF payload 32 byte và cấu hình điều chế còn là DRAFT/PENDING, chưa có cấu hình phần cứng được xác minh. Thiết kế nêu candidate 433 MHz, BW 125 kHz, SF7/SF8, CR 4/5.
2. **Đo lường chất lượng sóng:** Trích xuất chỉ số cường độ sóng **RSSI (dBm)** và tỷ số tín hiệu trên nhiễu **SNR (dB)** từ chip SX1278.
3. **Phát Wi-Fi SoftAP:** Khởi tạo mạng Wi-Fi nội bộ `KVC_GCS_AP` (IP `192.168.4.1`).
4. **Chạy WebSocket Server:** Endpoint mục tiêu `ws://192.168.4.1:8080/telemetry` theo IF-03; chưa có firmware ingress để xác minh.
5. **Duy trì hoạt động độc lập:** ESP32 dùng nguồn pin riêng, tiếp tục nhận và đếm gói LoRa ngay cả khi laptop tắt hoặc ngắt kết nối Wi-Fi.

---

## 2. Giao diện kỹ thuật bắt buộc tuân thủ

Phân hệ Gateway là cầu nối trung chuyển vô tuyến sang mạng cục bộ:
1. **Đầu vào (Thu sóng LoRa từ MCU Sonix):** 👉 **[docs/interfaces/IF_MCU_LORA_RF.md](file:///d:/Project_UAV_KVC/docs/interfaces/IF_MCU_LORA_RF.md)**
   - Dự kiến nhận RF payload 32 byte bắt đầu bằng `0xAA 0x55`; IF-02 còn là DRAFT ABI. CRC-16 của payload do firmware kiểm tra; CRC LoRa PHY là lớp riêng.
2. **Đầu ra (Phát Wi-Fi sang Backend Laptop):** 👉 **[docs/interfaces/IF_ESP32_GCS_WS.md](file:///d:/Project_UAV_KVC/docs/interfaces/IF_ESP32_GCS_WS.md)**
   - Forward envelope transport IF-03 qua WebSocket tới Backend laptop (`ws://192.168.4.1:8080/telemetry` theo baseline thiết kế; chưa có firmware ingress để xác minh).

> ⚠️ **LƯU Ý:** Trình duyệt Web Dashboard trên laptop kết nối tới Backend Python (`ws://127.0.0.1:8000/ws`), **KHÔNG kết nối trực tiếp vào ESP32**.

---

## 3. Cấu trúc tổ chức thư mục khuyến nghị cho Thịnh

Dự án đã được cấu hình sẵn theo chuẩn PlatformIO:

```text
firmware/gateway_esp32/
├── platformio.ini       # File cấu hình PlatformIO (đã khóa board & thư viện LoRa, WebSocket, ArduinoJson)
├── src/                 # Toàn bộ mã nguồn C/C++ (*.cpp, *.c)
│   ├── lora_receiver.cpp# Khởi tạo SX1278 qua SPI, ngắt DIO0 đọc gói LoRa & RSSI/SNR
│   ├── wifi_softap.cpp  # Cấu hình phát Wi-Fi AP KVC_GCS_AP (192.168.4.1)
│   ├── ws_server.cpp    # WebSocket Server; endpoint mục tiêu theo IF-03, chưa triển khai
│   └── main.cpp         # Setup & loop chính
├── include/             # File header (*.h)
└── README.md            # Tài liệu chỉ dẫn này
```

---

## 4. Hướng dẫn mở dự án bằng PlatformIO trên VS Code

1. Cài đặt extension **PlatformIO IDE** trên VS Code.
2. Mở thư mục `firmware/gateway_esp32/` bằng PlatformIO (*Open Project*).
3. PlatformIO sẽ tự động tải đúng phiên bản toolchain `espressif32` cho kiến trúc RISC-V (`esp32-c3-devkitm-1`) và các thư viện `LoRa`, `WebSockets`, `ArduinoJson`.
4. Bấm biểu tượng **Build (✓)** ở thanh trạng thái dưới cùng để biên dịch.

---

## 5. Lưu ý kỹ thuật quan trọng khi lập trình ESP32-C3

1. **Kiến trúc đơn nhân (Single-Core RISC-V):**
   - ESP32-C3 chỉ có 1 lõi CPU (160 MHz). Tuyệt đối **không gọi `xTaskCreatePinnedToCore` sang Core 1** như trên ESP32 classic. Tất cả tác vụ (LoRa RX ISR, SoftAP Wi-Fi, WebSocket broadcast) chạy phối hợp non-blocking hoặc định thời trên Core 0.
2. **Cảnh báo chân Strapping Pins khi đấu nối:**
   - `GPIO 2`, `GPIO 8`, `GPIO 9` là các chân quyết định chế độ boot của chip. Đặc biệt `GPIO 8` và `GPIO 9` không được để mức kéo LOW bất thường khi khởi động làm chip rơi vào chế độ nạp ROM.
3. **Gợi ý phân bổ chân kết nối ngoại vi (Pinout tham khảo):**
   - **Bus SPI (Module LoRa Ra-02):**
     * `SCK`: GPIO 4 (hoặc 6)
     * `MISO`: GPIO 5 (hoặc 2)
     * `MOSI`: GPIO 6 (hoặc 7)
     * `NSS / CS`: GPIO 7 (hoặc 10)
     * `DIO0 (Ngắt RxDone)`: GPIO 3 (hoặc 1)
     * `RST`: GPIO 1 (hoặc 0)
   - **Bus I2C (Màn hình OLED SSD1306 0.96"):**
     * `SDA`: GPIO 8 (hoặc 4)
     * `SCL`: GPIO 9 (hoặc 5)
4. **Cổng nạp & Debug Serial (USB-CDC vs USB-to-UART):**
   - Nếu bo devkit ESP32-C3 dùng cổng Type-C nối trực tiếp vào chân USB phần cứng của SoC (`GPIO 18 / 19`), cần bật cờ `-D ARDUINO_USB_CDC_ON_BOOT=1` trong `platformio.ini` để `Serial.print()` xuất ra đúng cổng USB máy tính.
   - Nếu bo dùng chip chuyển đổi trung gian (CH340 / CP2102) nối vào `GPIO 20 / 21` (UART0) thì dùng cấu hình mặc định.
