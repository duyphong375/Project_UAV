# KVC — Phân hệ Mã Nguồn Nhúng Vi Điều Khiển (Firmware)

Phân hệ này quản lý toàn bộ mã nguồn nhúng (C/C++) chạy trên các vi điều khiển thuộc hệ thống tải nhiệm vụ cứu nạn UAV KVC. Hệ thống chia thành 2 phân hệ MCU độc lập với vai trò, phần cứng và công cụ biên dịch hoàn toàn tách biệt:

1. **`mcu_uav/`**: Vi điều khiển quản lý tải nhiệm vụ trên máy bay (On-drone Payload MCU).
2. **`gateway_esp32/`**: Vi điều khiển trạm thu mặt đất (Ground Station Gateway).

---

## 1. Bảng Phân Định Phân Hệ Nhúng

| Phân hệ / Thư mục | Người phụ trách | Phần cứng mục tiêu | Công cụ (IDE / Toolchain) | Nhiệm vụ chính & Hợp đồng giao diện |
| :--- | :--- | :--- | :--- | :--- |
| **[`mcu_uav/`](file:///d:/Project_UAV_KVC/firmware/mcu_uav)** | **Nguyễn Tá Duy Phong** | **Sonix SN34F788FG**<br>(ARM Cortex-M4F, tối đa 192 MHz, 160 KB SRAM, 512 KB Flash; xem hồ sơ chip và đối chiếu kit/DFP) | **Keil MDK-ARM**<br>(Mạch nạp SN-Link) | • Thu thập cảm biến: [IF_MCU_SENSORS.md](file:///d:/Project_UAV_KVC/docs/interfaces/IF_MCU_SENSORS.md)<br>• Nhận BBox từ FPGA qua UART: [IF_FPGA_MCU_UART.md](file:///d:/Project_UAV_KVC/docs/interfaces/IF_FPGA_MCU_UART.md)<br>• Giao diện LoRa còn là draft: [IF_MCU_LORA_RF.md](file:///d:/Project_UAV_KVC/docs/interfaces/IF_MCU_LORA_RF.md) |
| **[`gateway_esp32/`](file:///d:/Project_UAV_KVC/firmware/gateway_esp32)** | **Đoàn Thanh Trường Thịnh** | **ESP32-C3**<br>(kit/board cụ thể TBD; nguồn riêng theo thiết kế) | **PlatformIO**<br>(`framework = arduino`, board khai báo trong `platformio.ini`) | • Giao diện LoRa còn là draft: [IF_MCU_LORA_RF.md](file:///d:/Project_UAV_KVC/docs/interfaces/IF_MCU_LORA_RF.md)<br>• Wi-Fi SoftAP/WebSocket là baseline thiết kế chưa xác minh: [IF_ESP32_GCS_WS.md](file:///d:/Project_UAV_KVC/docs/interfaces/IF_ESP32_GCS_WS.md) |

---

## 2. Cấu Trúc Thư Mục Phân Hệ Firmware

```text
firmware/
├── mcu_uav/
│   ├── inc/
│   │   ├── kvc_pinout.h      # Header cấu hình chân ngoại vi chuẩn (LoRa, Siêu âm, IMU, GNSS, FPGA)
│   │   └── kvc_telemetry.h   # Định nghĩa gói tin 32 byte Little-Endian và CRC-16
│   ├── project_keil/main.c   # Khởi động và kiểm tra chuỗi ngoại vi cơ bản
│   └── README.md             # Hướng dẫn chi tiết phân hệ MCU Sonix SN34F788
├── gateway_esp32/
│   ├── platformio.ini        # Board mục tiêu esp32-c3-devkitm-1, framework Arduino
│   ├── src/main.cpp          # Mã nguồn Gateway thu LoRa SX1278 (433 MHz, SPI)
│   └── README.md             # Hướng dẫn chi tiết phân hệ Gateway ESP32
└── README.md                 # Tài liệu tổng quan này
```

Bản đồ chân Master và sơ đồ đấu nối toàn hệ thống được quy định tập trung tại:
👉 **[docs/hardware/KVC_MASTER_PINOUT_WIRING.md](file:///d:/Project_UAV_KVC/docs/hardware/KVC_MASTER_PINOUT_WIRING.md)**

---

## 3. Quy Tắc Kỹ Thuật Bắt Buộc

1. **Tuân thủ trạng thái đặc tả giao diện:**
   - UART FPGA ➔ MCU được mô tả trong IF-01; trạng thái hiện là DRAFT ABI. Không coi các giá trị trong tài liệu dự thảo là cấu hình đã khóa.
   - LoRa MCU ➔ Gateway được mô tả trong IF-02; RF payload 32 byte và tham số vô tuyến còn chờ duyệt. Telemetry 20 byte chỉ là ghi nhận từ source cũ.
   - Không tự ý thay đổi baudrate, layout gói tin, thuật toán CRC, pinout hoặc sơ đồ ngắt; mọi triển khai phải theo đặc tả đã được các owner thống nhất.
2. **Quy tắc Git & Artifacts:**
   - File cấu hình [`.gitignore`](file:///d:/Project_UAV_KVC/.gitignore) đã tự động loại bỏ các thư mục build tạm của Keil (`Objects/`, `Listings/`, `*.axf`, `*.hex`) và PlatformIO (`.pio/`).
   - Thành viên chỉ commit file mã nguồn `.c`, `.cpp`, `.h`, `.ini`, `.uvprojx` và tài liệu `.md`.
3. **Quy tắc an toàn phần cứng:**
   - AI (Codex / Antigravity) **tuyệt đối không tự ý nạp flash (flash firmware)** vào MCU hay FPGA. Việc nạp chip thực tế do thành viên phụ trách phần cứng thực hiện.
4. **Chuẩn phân bổ chân Master:**
   - Toàn bộ cấu hình chân I/O, ngoại vi UART/SPI/I2C và jumper kit phải tuân thủ nghiêm ngặt theo [KVC_MASTER_PINOUT_WIRING.md](file:///d:/Project_UAV_KVC/docs/hardware/KVC_MASTER_PINOUT_WIRING.md). Cấm cấp nguồn 5V trực tiếp vào chân GPIO 3.3V của Sonix SN34F788 hoặc ESP32-C3.
