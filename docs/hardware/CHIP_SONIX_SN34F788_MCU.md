# KVC — MCU tải Sonix SN34F788

Cập nhật 14/10/2026. MCU mục tiêu là **SN34F788 trên Sonix Starter Kit**. Không nhầm với SN32F788. Hồ sơ/SDK đã có trong workspace; chưa có bằng chứng firmware KVC build/chạy trên bo.

## 1. Thông số cần dùng

| Mục | Thông tin từ datasheet SN34F780/SN34F788 v1.7 |
| --- | --- |
| CPU | Cortex-M4F, tối đa 192 MHz; cấu hình clock/FPU thực tế phải kiểm trong project |
| Bộ nhớ | Flash 512 KB gồm 8 KB Boot; SRAM 160 KB |
| VDD chip | **2,4–3,6 V**, danh định 3,3 V |
| I/O | Có miền VDDIO1 riêng; mức logic phụ thuộc rail/chân. Không coi GPIO chịu 5 V |
| Giao tiếp dự kiến dùng | UART cho FPGA/LiDAR/GNSS; I2C cho IMU/OLED; SPI cho Ra-02; chọn instance/pin mux theo kit thực |
| Debug | SWD với SN-LINK phù hợp; kiểm kit/debugger và connector thực nhận |

Nguồn: [SONiX User Manual v1.7](https://www.sonix.com.tw/webapi/fl219471/SN34F788_V1.7_EN.pdf), phần Product Overview và Electrical Characteristic (trang in 510–512).

**Sửa thông tin nguồn:** mức 2,5–5,5 V trong bản ghi chú cũ là sai đối với VDD chip này. Nguồn 5 V ở cổng USB của kit đi qua mạch nguồn theo schematic; không cấp 5 V trực tiếp vào VDD/GPIO. VDDIO1 cần được kiểm cùng mức điện FPGA và cảm biến.

## 2. Starter Kit, mạch nạp và công cụ

Manual mô tả kit có SN-LINK Lite và connector cho SN-LINK rời; cấu hình bán kèm có thể khác. Kiểm revision/ảnh bo và thử nhận debugger. Không mua trùng nếu kit đã có debugger phù hợp; nếu thiếu thì chuẩn bị SN-LINK-V3 tương thích. ST-Link của STM32 không mặc định thay được SN-LINK.

Workspace có gói SONiX.SN34F7_DFP.2.0.4.pack, SDK và driver. File có trên đĩa không có nghĩa đã được cài đúng, license compiler phù hợp hoặc đã build firmware. Phong cần kiểm device, startup, linker/memory map, FPU ABI và flash algorithm trên project thực tế.

Không dùng các số CoreMark, baud sai số 0%, pin mux, boot strap, địa chỉ thanh ghi hoặc clock suy diễn trong ghi chú cũ như thông số đã xác minh. Tra manual/header của đúng pack và ghi log build/đo. Chưa có pinout KVC được duyệt nên tài liệu này không cấp sơ đồ đấu nối mới.

## 3. Vai trò trong KVC

**DESIGN:** nhận BBox từ FPGA → đọc cảm biến có thời gian → kiểm validity → tính tọa độ khi đủ pose/calibration → gửi metadata qua LoRa. Tracking một mục tiêu, watchdog và khôi phục lỗi cần triển khai/kiểm thử; chưa được xác nhận bằng SDK mẫu.

- **Phong:** project/firmware MCU tải, parser, cảm biến, định vị và tích hợp.
- **Cường:** chuẩn bị/lắp kit, cảm biến và LoRa, kiểm từng đường tín hiệu và thu số đo cùng Phong.
- **Kiên:** sơ đồ nguồn, dây/gá và kiểm mức điện trước đấu nối.
- **Vững:** phối hợp đầu ra FPGA/UART/IRQ.
- **Thịnh:** phối hợp wire ABI trạm đất/GCS và golden vectors.

Ba luồng FPGA, LiDAR, GNSS cần kiểm đủ instance/pin/DMA/IRQ mà không xung đột SWD hoặc chân boot. ISR xử lý ngắn, phần tính toán chạy ngoài ISR; kiểm timeout/ring overflow/reset/disconnect theo task firmware.

RF32/USB48 và UART trong [thiết kế mục IV](../KVC_ThietKeHeThong.md) là **DRAFT**, chưa được duyệt để nạp bo. Giữ nguyên baud/CRC/layout/IRQ/pinout đến khi có task triển khai được giao và cấu hình đã chốt. Không mặc định 921600 bps đã ổn định chỉ từ khả năng UART chip.

## 4. Kiểm trước tích hợp

1. Xác nhận mã chip/revision kit, jumper nguồn/VDDIO1 và debugger.
2. Tạo project đúng device/pack; build chương trình tối thiểu, kiểm map/stack/heap/FPU.
3. Kiểm UART loopback, lỗi framing/CRC/timeout/overflow và golden vectors theo ABI đã duyệt.
4. Đọc riêng từng cảm biến, ghi timestamp/đơn vị/validity; TF-Luna phải thử mặt nước và cường độ phản xạ, GY-87 cần kiểm chip thực.
5. Ghép RF, đo nguồn khi phát và lỗi phục hồi; sau đó kiểm cả chuỗi với Dashboard.

Mỗi phép thử ghi lệnh, exit code, candidate/hash và log. Build/simulation không thay HARDWARE-VERIFIED; hồ sơ này không phải kết quả test.

## 5. Tài liệu và công cụ trên đĩa

- [Manual v1.7](sonix_sn34f788/SN34F780_StartKit_Package_V1.10R/Document/SN34F780_V1.7.pdf).
- [Quick Start v1.1](sonix_sn34f788/SN34F780_StartKit_Package_V1.10R/Document/QuickStart/SN34F780_QuickStart_V1.1R_EN.pdf).
- [Schematic Starter Kit](<sonix_sn34f788/SN34F780_StartKit_Package_V1.10R/Reference Circuit/SN34F780_STARTKIT_V1.1.pdf>).
- [Device Family Pack 2.0.4](sonix_sn34f788/SN34F780_StartKit_Package_V1.10R/Pack/SONiX.SN34F7_DFP.2.0.4.pack).
- [Readme gói kit](sonix_sn34f788/SN34F780_StartKit_Package_V1.10R/SN34F780_Readme.pdf).
- SDK: thư mục sonix_sn34f788/SN34F780_SDK_V2.1.4; driver/ICP ở thư mục cha. Giữ nguyên cấu trúc gói hãng, không coi các ví dụ trong SDK là firmware KVC.

Các PDF/SDK gốc không bị sửa. Bản ghi chú trước sửa được lưu trong evidence task KVC-DOC-CONSISTENCY-20261014-001.
