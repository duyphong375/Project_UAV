# KVC — Phân hệ MCU Tải trên UAV (Sonix SN34F788)

- **Người phụ trách:** **Nguyễn Tá Duy Phong**
- **Phần cứng mục tiêu:** **Sonix SN34F788FG** (ARM Cortex-M4F, tối đa 192 MHz, 160 KB SRAM, 512 KB Flash; đối chiếu chip/kit thực tế và DFP trước khi tạo project)
- **Công cụ phát triển (IDE / Toolchain):** **Keil MDK-ARM (v5.xx)** + Bộ nạp **SN-Link**
- **Tài liệu & SDK hãng:** [docs/hardware/sonix_sn34f788/](file:///d:/Project_UAV_KVC/docs/hardware/sonix_sn34f788) và [docs/hardware/CHIP_SONIX_SN34F788_MCU.md](file:///d:/Project_UAV_KVC/docs/hardware/CHIP_SONIX_SN34F788_MCU.md)

---

## 1. Nhiệm vụ của phân hệ MCU tải

1. **Nhận kết quả từ FPGA:** Bắt ngắt `DATA_READY`, nhận luồng UART và bóc tách khung BBox.
2. **Đọc đồng bộ 3 cảm biến:**
   - **TF-Luna LiDAR:** Đọc cự ly bề mặt nước qua UART / I2C (đơn vị: cm).
   - **GY-87 IMU 10-DOF:** Đọc góc nghiêng Roll, Pitch, Yaw qua I2C.
   - **NEO-M8N GNSS:** Đọc tọa độ GPS/NMEA qua UART.
3. **Giải thuật toán định vị không gian (Georeferencing):**
   - Kết hợp góc quay camera, góc nghiêng IMU và cự ly LiDAR để giải phương trình giao điểm tia quang học với mặt phẳng nước.
   - Tính toán tọa độ thực tế của mục tiêu (WGS-84 hoặc Local Grid cm).
4. **Đóng gói và phát LoRa:** Điều khiển module LoRa Ra-02 (SX1278) qua SPI phát gói tin telemetry về trạm đất.

---

## 2. Giao diện kỹ thuật bắt buộc tuân thủ

Phân hệ MCU Sonix là cầu nối trung tâm, cần tuân thủ 3 giao diện:
1. **Đầu vào Cảm biến (LiDAR, IMU, GNSS):** 👉 **[docs/interfaces/IF_MCU_SENSORS.md](file:///d:/Project_UAV_KVC/docs/interfaces/IF_MCU_SENSORS.md)**
   - Đọc TF-Luna (UART2 115k), GY-87 (I2C0 400k), NEO-M8N (UART3 9k6). Cấm cấp 5V vào GPIO Sonix.
2. **Đầu vào Nhận diện (Nhận từ FPGA):** 👉 **[docs/interfaces/IF_FPGA_MCU_UART.md](file:///d:/Project_UAV_KVC/docs/interfaces/IF_FPGA_MCU_UART.md)**
   - Bắt ngắt DATA_READY, giải mã gói bắt đầu bằng `0x5A 0xA5`, kiểm tra CRC-16/CCITT.
3. **Đầu ra Telemetry (Phát sang ESP32 Trạm Đất):** 👉 **[docs/interfaces/IF_MCU_LORA_RF.md](file:///d:/Project_UAV_KVC/docs/interfaces/IF_MCU_LORA_RF.md)**
   - RF payload 32 byte (Header `0xAA 0x55`, Little-Endian, CRC-16) hiện là **DRAFT ABI / PENDING**; chưa nạp hoặc coi là chuẩn đã duyệt.
   - Tham số RF cũng chưa khóa. Thiết kế đang tính airtime cho các candidate SF7/SF8 ở 433 MHz, BW 125 kHz, CR 4/5; chốt cấu hình với owner trước khi lập trình và đo.

---

## 3. Cấu trúc tổ chức thư mục khuyến nghị cho Phong

Khi mở Keil MDK để tạo project mới (*New µVision Project*), Phong lưu vào thư mục này:

```text
firmware/mcu_uav/
├── project_keil/        # Chứa file project Keil (*.uvprojx, *.uvoptx)
├── src/                 # Toàn bộ mã nguồn C (*.c)
│   ├── drivers/         # Cấu hình UART, SPI, I2C, GPIO, System Clock của chip Sonix
│   ├── sensors/         # Driver đọc TF-Luna, GY-87, NEO-M8N
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
