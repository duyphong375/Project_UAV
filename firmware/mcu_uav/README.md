# KVC — Phân hệ MCU Tải trên UAV (Sonix SN34F788)

- **Người phụ trách:** **Nguyễn Tá Duy Phong**
- **Phần cứng mục tiêu:** **Sonix SN34F788FG** (ARM Cortex-M4F, tối đa 192 MHz, 160 KB SRAM, 512 KB Flash; đối chiếu chip/kit thực tế và DFP trước khi tạo project)
- **Công cụ phát triển (IDE / Toolchain):** **Keil MDK-ARM (v5.xx)** + Bộ nạp **SN-Link**
- **Tài liệu & SDK hãng:** [docs/hardware/sonix_sn34f788/](file:///d:/Project_UAV_KVC/docs/hardware/sonix_sn34f788) và [docs/hardware/CHIP_SONIX_SN34F788_MCU.md](file:///d:/Project_UAV_KVC/docs/hardware/CHIP_SONIX_SN34F788_MCU.md)

---

## 1. Nhiệm vụ của phân hệ MCU tải

1. **Nhận kết quả từ FPGA:** Bắt ngắt `DATA_READY`, nhận luồng UART và bóc tách khung BBox.
2. **Đọc đồng bộ 3 cảm biến:**
   - **AJ-SR04M Siêu âm chống nước:** Đọc cự ly bề mặt nước qua UART (đơn vị: cm).
   - **GY-87 IMU 10-DOF:** Đọc góc nghiêng Roll, Pitch, Yaw qua I2C.
   - **NEO-M10N GNSS:** Đọc tọa độ GPS/NMEA qua UART.
3. **Giải thuật toán định vị không gian (Georeferencing):**
   - Kết hợp góc quay camera, góc nghiêng IMU và cự ly siêu âm để giải phương trình giao điểm tia quang học với mặt phẳng nước.
   - Tính toán tọa độ thực tế của mục tiêu (WGS-84 hoặc Local Grid cm).
4. **Đóng gói và phát LoRa:** Điều khiển module LoRa Ra-02 (SX1278) qua SPI phát gói tin telemetry về trạm đất.

---

## 2. Giao diện kỹ thuật bắt buộc tuân thủ

Phân hệ MCU Sonix là cầu nối trung tâm, cần tuân thủ bảng sơ đồ chân tổng thể và 3 giao diện:
- 📌 **Bản đồ chân & Đấu nối Master:** 👉 **[docs/hardware/KVC_MASTER_PINOUT_WIRING.md](file:///d:/Project_UAV_KVC/docs/hardware/KVC_MASTER_PINOUT_WIRING.md)**
1. **Đầu vào Cảm biến (Siêu âm AJ-SR04M, IMU, GNSS):** 👉 **[docs/interfaces/IF_MCU_SENSORS.md](file:///d:/Project_UAV_KVC/docs/interfaces/IF_MCU_SENSORS.md)**
   - Đọc AJ-SR04M (GPIO Trigger/Echo P2.14/P2.15 hoặc UART2), GY-87 (I2C0 400k P0.10/P0.11), NEO-M10N (UART3 9k6 P2.0/P2.1). Cấm cấp 5V vào GPIO Sonix.
2. **Đầu vào Nhận diện (Nhận từ FPGA):** 👉 **[docs/interfaces/IF_FPGA_MCU_UART.md](file:///d:/Project_UAV_KVC/docs/interfaces/IF_FPGA_MCU_UART.md)**
   - Bắt ngắt DATA_READY, giải mã gói bắt đầu bằng `0x5A 0xA5`, kiểm tra CRC-16/CCITT.
3. **Đầu ra Telemetry (Phát sang ESP32 Trạm Đất):** 👉 **[docs/interfaces/IF_MCU_LORA_RF.md](file:///d:/Project_UAV_KVC/docs/interfaces/IF_MCU_LORA_RF.md)**
   - Cấu trúc gói 32 byte (`KvcTelemetryPacket32`, Little-Endian, CRC-16) đã được định nghĩa tại [`firmware/mcu_uav/inc/kvc_telemetry.h`](file:///d:/Project_UAV_KVC/firmware/mcu_uav/inc/kvc_telemetry.h).
   - Tham số RF: 433.0 MHz, Sync Word `0x12`, BW 125 kHz, candidate SF7/SF8, CR 4/5; chốt cấu hình với owner trước khi nạp phần cứng và đo.

---

## 3. Cấu trúc tổ chức thư mục khuyến nghị cho Phong

Khi mở Keil MDK để tạo project mới (*New µVision Project*), Phong lưu vào thư mục này:

```text
firmware/mcu_uav/
├── project_keil/        # Chứa file project Keil (*.uvprojx, *.uvoptx)
├── src/                 # Toàn bộ mã nguồn C (*.c)
│   ├── drivers/         # Cấu hình UART, SPI, I2C, GPIO, System Clock của chip Sonix
│   ├── sensors/         # Driver đọc AJ-SR04M, GY-87, NEO-M10N
│   ├── protocol/        # Parser giải mã FPGA và Encoder đóng gói LoRa
│   ├── geo/             # Hàm giải phương trình tia cắt mặt phẳng nước
│   └── main.c           # Vòng lặp chính điều phối
├── inc/                 # Toàn bộ file header (*.h)
├── tests/               # Unit test độc lập cho logic toán học / parser chạy trên PC (gcc/pytest)
└── README.md            # Tài liệu chỉ dẫn này
```

---

## 4. Lưu ý về Git và rác build nhị phân

File cấu hình [.gitignore](file:///d:/Project_UAV_KVC/.gitignore) của dự án đã tự động chặn các file build tạm của Keil:
* Thư mục `Objects/` và `Listings/`.
* Các file nạp nhị phân: `*.hex`, `*.axf`, `*.elf`, `*.o`, `*.bin`.

👉 **Phong chỉ cần commit mã nguồn `.c`, `.h` và file cấu hình project `.uvprojx`.**

---

## 5. Driver GNSS u-blox NEO-M10 (Task KVC-GNSS-M10-001)

Phân hệ GNSS thu thập tọa độ định vị vị trí UAV phục vụ đối chiếu và thuật toán cứu nạn:

- **Tệp nguồn:**
  - Header: [`firmware/mcu_uav/inc/kvc_gnss_neo_m10.h`](file:///d:/Project_UAV_KVC/firmware/mcu_uav/inc/kvc_gnss_neo_m10.h)
  - C Source: [`firmware/mcu_uav/src/sensors/kvc_gnss_neo_m10.c`](file:///d:/Project_UAV_KVC/firmware/mcu_uav/src/sensors/kvc_gnss_neo_m10.c)
  - Host Unit Test: [`firmware/mcu_uav/tests/test_kvc_gnss_neo_m10.c`](file:///d:/Project_UAV_KVC/firmware/mcu_uav/tests/test_kvc_gnss_neo_m10.c)
- **Cấu hình phần cứng UART3 Sonix SN34F788:**
  - Tốc độ: **9600 bps**, khung truyền 8N1 (hằng số `KVC_GNSS_BAUD_RATE`), không dùng ngắt (no IRQ).
  - Pin mux (`SN_ALWAYSON->P2_AFIO0`):
    - `P2.1` (`URXD3`, Pin 15 LQFP64 | JP3 Pin 3/4): Nhận NMEA từ chân TX của module.
    - `P2.0` (`UTXD3`, Pin 14 LQFP64 | JP3 Pin 1/2): Nối RX của module (không phát lệnh đổi cấu hình).
  - Clock: `SN_SCU->APB0CLKG` bit 6 (`UART3CLKEN`), `SN_SCU->APB1CLKG` bit 19 (`P2CLKEN`).
  - UCLK = 12 MHz, Baudrate = 38400 bps, Divisor = 20 (`DLL = 0x14`, `DLM = 0x00`).
- **Cơ chế Polling:**
  - Đọc cạn FIFO UART3 không chặn (non-blocking) trong vòng lặp theo từng nhịp 1 ms.
  - Phục hồi sau câu lỗi, nhiễu rác đường truyền hoặc câu bị cắt cụt.
- **Tiêu chuẩn nghiệm thu Fix hợp lệ (`KVC_FLAG_GNSS_VALID` - Chuẩn TinyGPSPlus):**
  1. Hỗ trợ đa dạng câu NMEA: `$??GGA`, `$??GSA`, `$??RMC` ($GNGGA, $GNRMC, $GPGGA, $GPRMC...).
  2. GGA Fix Quality >= 1 hoặc RMC Status == 'A' (Active).
  3. GSA Fix Mode >= 2 (2D hoặc 3D Fix; từ chối Mode 1 No Fix).
  4. Số vệ tinh theo dõi >= 4 (chuẩn định vị không gian 3 chiều).
  5. Sai số hình học mặt ngang HDOP <= 5.00.
  6. Tọa độ hợp lệ trong biên chuẩn WGS-84 (-90° <= Lat <= +90°, -180° <= Lon <= +180°).
  7. Dữ liệu còn mới trong 3.0 giây (3000 ms). Hết hạn 3 giây tự động xóa trạng thái hợp lệ.
- **Kiểm thử Host Test:**
  ```powershell
  gcc -Wall -Wextra -O2 -DKVC_HOST_TEST=1 -Ifirmware/mcu_uav/inc firmware/mcu_uav/src/sensors/kvc_gnss_neo_m10.c firmware/mcu_uav/tests/test_kvc_gnss_neo_m10.c -o test_kvc_gnss.exe
  .\test_kvc_gnss.exe
  ```
- **Build Keil Target:**
  ```powershell
  & "C:\Keil_v5\UV4\UV4.exe" -b "firmware\mcu_uav\project_keil\mcu_uav.uvprojx" -j0 -o "build.log"
  ```
