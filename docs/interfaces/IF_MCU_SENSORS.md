# Đặc tả giao diện: MCU Tải Sonix ↔ Cảm biến Định vị (LiDAR, IMU, GNSS)

- **Mã giao diện:** `IF-00`
- **Hai đầu kết nối:** MCU Sonix SN34F788 trên UAV (**Nguyễn Tá Duy Phong** - Xử lý phần mềm) ↔ Cụm cảm biến tải (**Đàm Nguyễn Mạnh Cường** - Lắp đặt & đo đạc; **Trương Trung Kiên** - Nguồn & dây)
- **Trạng thái:** `BASELINE DESIGN` (Theo mục III và IV.2 [KVC_ThietKeHeThong.md](../KVC_ThietKeHeThong.md))

---

## 1. Quy tắc an toàn điện và nguồn (Bắt buộc tuân thủ)

> ⚠️ **CẢNH BÁO CHỐNG CHÁY CHIP SONIX:**
> 1. Vi điều khiển Sonix SN34F788 hoạt động ở dải điện áp **VDD = 2,4 V – 3,6 V (Chuẩn 3,3 V)**. Các chân GPIO của chip **KHÔNG chịu được mức điện áp 5 V**. Tuyệt đối không cắm nguồn 5 V trực tiếp vào chân GPIO của Sonix.
> 2. **Nối chung GND (Ground):** Toàn bộ dây GND của Kit Sonix, TF-Luna, GY-87, NEO-M8N và nguồn hạ áp Buck DC-DC phải được nối chung với nhau để tạo mốc điện áp chuẩn.
> 3. Cụm cảm biến và MCU tải phải dùng nguồn từ mạch Buck hạ áp riêng (cấp dòng tối thiểu 2 A), **không dùng chân 3.3V của mạch nạp SN-Link hoặc mạch nạp CP2102** để nuôi toàn bộ cảm biến.

---

## 2. Bảng phân bổ chân cắm và mức điện áp trên MCU Sonix

| Cảm biến / Module | Chuẩn giao tiếp | Mức logic tín hiệu | Nguồn cấp VCC | Chân tín hiệu trên Module | Cổng ngoại vi dự kiến trên Sonix SN34F788 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **TF-Luna LiDAR** | UART (115.200 bps) | 3,3 V TTL | **5,0 V** (DC-DC) | TXD ➔ RXD<br>RXD ◄ TXD | **UART2_RX** (`P1.0` / AFIO)<br>**UART2_TX** (`P1.1` / AFIO) |
| **GY-87 IMU 10-DOF** | I2C (100 / 400 kHz) | 3,3 V CMOS | **3,3 V** | SDA (Data)<br>SCL (Clock) | **I2C0_SDA** (`P0.8` / AFIO)<br>**I2C0_SCL** (`P0.9` / AFIO)<br>*(Trở kéo 4,7 kΩ lên 3,3V)* |
| **NEO-M8N GNSS** | UART (9.600 bps) | 3,3 V TTL | **3,3 V – 5,0 V** | TXD ➔ RXD<br>RXD ◄ TXD | **UART3_RX** (`P2.4` / AFIO)<br>**UART3_TX** (`P2.5` / AFIO) |
| **LoRa Ra-02 (SX1278)** | SPI (1–4 MHz) | 3,3 V CMOS | **3,3 V** (DC-DC) | MOSI, MISO, SCK, NSS, DIO0 | **SPI0** (`P0.0..P0.3`) + GPIO ngắt DIO0 (`P0.4`) |
| **FPGA BBox Data** | UART (115.200 bps) | 3,3 V CMOS | Chung nguồn | RXD ◄ TXD (FPGA)<br>DATA_READY | **UART1_RX** (`P0.10`)<br>Chân ngắt EXTI (`P0.12`) |

---

## 3. Đặc tả giao thức chi tiết từng cảm biến

### 3.1. Cảm biến cự ly độ cao TF-Luna LiDAR (Benewake)

* **Chuẩn truyền thông:** UART 115.200 bps, 8 bit dữ liệu, No Parity, 1 Stop bit (8N1).
* **Tần số lấy mẫu:** Mặc định 100 Hz (có thể cấu hình 10–250 Hz).
* **Định dạng khung dữ liệu 9 byte:**

```text
+------+------+--------+--------+-------+-------+--------+--------+----------+
| 0x59 | 0x59 | Dist_L | Dist_H | Amp_L | Amp_H | Temp_L | Temp_H | Checksum |
+------+------+--------+--------+-------+-------+--------+--------+----------+
```

* **Công thức giải mã:**
  * $\text{Distance (cm)} = \text{Dist\_L} + (\text{Dist\_H} \ll 8)$
  * $\text{Signal Amplitude} = \text{Amp\_L} + (\text{Amp\_H} \ll 8)$
  * $\text{Checksum} = (\text{Byte}_0 + \text{Byte}_1 + \dots + \text{Byte}_7) \ \& \ \text{0xFF}$
* **Điều kiện cờ hợp lệ (`lidar_valid`):**
  * Khoảng cách đo nằm trong dải tin cậy: $20\text{ cm} \le \text{Distance} \le 800\text{ cm}$ (độ cao UAV khi quét bão lũ).
  * Cường độ tín hiệu $\text{Amplitude} \ge 100$ (tránh hiện tượng tán xạ trên mặt nước).

---

### 3.2. Cụm cảm biến tư thế GY-87 IMU 10-DOF

Mô-đun GY-87 tích hợp 3 chip trên cùng 1 bus I2C:

#### A. MPU6050 (3-axis Gyroscope + 3-axis Accelerometer)
* **Địa chỉ I2C:** `0x68` (khi chân AD0 nối GND).
* **Thanh ghi cấu hình chính:**
  * `0x6B` (`PWR_MGMT_1`): Ghi `0x00` để đánh thức chip thoát chế độ Sleep.
  * `0x1A` (`CONFIG`): Cấu hình bộ lọc thông thấp số DLPF (42 Hz).
  * `0x1B` (`GYRO_CONFIG`): Dải đo Gyro $\pm 500^\circ/\text{s}$ (Thanh ghi `0x43`..`0x48`).
  * `0x1C` (`ACCEL_CONFIG`): Dải đo Gia tốc $\pm 4g$ (Thanh ghi `0x3B`..`0x40`).
* **Trích xuất góc tư thế:** Kết hợp bộ lọc bù (Complementary Filter) hoặc Madgwick Filter để tính góc nghiêng **Roll ($\phi$)** và **Pitch ($\theta$)** của camera/tải.

#### B. HMC5883L / QMC5883L (La bàn số 3 trục Magnetometer)
* **Địa chỉ I2C:** `0x1E` (HMC5883L) hoặc `0x0D` (nếu dùng chip tương đương QMC5883L — Cường kiểm tra chip thực tế trên bo).
* **Mục đích:** Cung cấp góc hướng Bắc từ trường (Heading / **Yaw ($\psi$)**) để xác định phương vị quang học.

#### C. BMP180 (Cảm biến áp suất khí quyển & độ cao)
* **Địa chỉ I2C:** `0x77`.
* **Mục đích:** Dự phòng đo độ cao tương đối so với mặt nước khi LiDAR gặp góc phản xạ quá lớn.

---

### 3.3. Module định vị vệ tinh NEO-M8N GNSS

* **Chuẩn truyền thông:** UART 9.600 bps (mặc định xuất xưởng) hoặc cấu hình lên 38.400 / 115.200 bps, 8N1.
* **Giao thức:** NMEA-0183 (Câu `$GNGGA` hoặc `$GNRMC` xuất định kỳ 1–5 Hz).
* **Trường dữ liệu cần trích xuất:**
  * **Fix Status:** Trường chất lượng định vị ($0$: No Fix, $1$: GPS 2D/3D Fix, $2$: DGPS Fix). Chỉ chấp nhận khi $\ge 1$.
  * **Latitude & Longitude:** Tọa độ địa lý WGS-84 (độ phút sang độ thập phân $\times 10^7$).
  * **HDOP (Horizontal Dilution of Precision):** Độ chính xác hình học mặt phẳng. Chỉ chấp nhận $\text{HDOP} \le 2.5$.
* **Điều kiện cờ hợp lệ (`gnss_valid`):**
  * $\text{Fix Status} \ge 1$ VÀ Số lượng vệ tinh theo dõi $\ge 5$ VÀ $\text{HDOP} \le 2.5$.
  * Khi thiếu các điều kiện trên, MCU xuất cờ `GNSS_INVALID` và không công bố tọa độ WGS-84 mục tiêu (chỉ dùng tọa độ phẳng Local Grid cm).

---

## 4. Trách nhiệm phối hợp kiểm thử giữa Phong và Cường

1. **Cường (Phần cứng):**
   - Kiểm tra thông mạch và đo điện áp các chân cấp nguồn bằng đồng hồ VOM trước khi cắm vào Kit Sonix.
   - Thử nghiệm độ phản xạ của LiDAR TF-Luna trên mặt nước thật (bể bơi/chậu nước) với các góc nghiêng từ $0^\circ$ đến $30^\circ$, ghi lại suy giảm tín hiệu `Amplitude`.
2. **Phong (Firmware):**
   - Viết module đọc lần lượt từng cảm biến trong `firmware/mcu_uav/src/sensors/`.
   - Cài đặt cơ chế Timeout cho các hàm đọc I2C/UART: nếu 1 cảm biến bị tuột dây hoặc treo bus, chương trình chính vẫn tiếp tục chạy điều phối, **tuyệt đối không bị treo vô hạn trong vòng lặp chờ**.
