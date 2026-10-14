# KVC — Bo OneKiwi Primer 20K V1.1

Cập nhật 14/10/2026. **Nhóm xác nhận đang có OneKiwi Primer 20K V1.1.** Đây là hồ sơ tham chiếu để triển khai, chưa phải pinout đã duyệt hoặc kết quả chạy phần cứng.

## 1. Cấu hình đã xác định

| Nội dung | Căn cứ |
| --- | --- |
| Target | OneKiwi Primer 20K V1.1 theo xác nhận của nhóm |
| FPGA | Gowin ARORA GW2A-LV18PG256; hãng công bố 20.736 LUT |
| Nạp/debug FPGA | GWU2X USB-JTAG tích hợp; chuẩn bị cáp dữ liệu phù hợp |
| Giao diện trên bo | Tài liệu hãng mô tả USB, HDMI, microSD và GPIO mở rộng; đầu nối vật lý không tự cung cấp RTL/IP xử lý |

Nguồn: [trang sản phẩm OneKiwi](https://onekiwi.com.vn/products/kiwi-20k-primer-fpga-board/), [User Guide](https://linuxbsp.onekiwi.com.vn/FPGA/PRIMER_20K/KIWIPRIMER20K_USERGUIDE.pdf).

## 2. Những điểm chưa được phép coi là cấu hình KVC đã chốt

- **Camera:** chưa có module/cáp/pin map đã xác minh. Không lấy đầu nối DVP 24 chân của Tang Primer Dock áp dụng cho OneKiwi. HDMI RX cần IP, constraints và nguồn ảnh phù hợp; GPIO/LVDS không tự tương thích MIPI-CSI. USB webcam cần controller/stack thích hợp, không mặc định cắm là chạy.
- **DDR3:** chưa xác minh fitted part/density/bus/controller trên bo đang có. Bỏ khẳng định chắc chắn DDR3 512 MB, triple buffering hoặc clock DDR 300–400 MHz. Nếu pipeline cần bộ nhớ ngoài, phải kiểm phần cứng rồi mới lập budget.
- **Flash:** tài liệu public có chỗ ghi 128 Mbit và chỗ ghi 64 Mbit; schematic block diagram nêu W25Q128. Cần đối chiếu mã linh kiện thực và revision, không tự chọn dung lượng. SPI Flash không thay DDR/frame buffer.
- **Nguồn:** User Guide mô tả đầu vào 5 V; cần đối chiếu cổng/jumper và schematic đúng bo trước cấp điện. Không nối nguồn ngoài trực tiếp vào rail lõi; không suy toàn bộ GPIO đều 3,3 V từ một chân nguồn header.
- **Pinout:** chưa duyệt UART, DATA_READY, reset hoặc camera cho KVC. Bảng chân chép trong bản ghi chú cũ không được dùng để đấu nối; tra PDF đúng revision, kiểm xung đột chân/chức năng/VCCIO và lưu constraints theo task.
- **Nạp Flash:** không áp dụng hướng dẫn “internal Flash” chung nếu chưa xác nhận chế độ hỗ trợ trên đúng device. Kiểm Programmer/device và chip Flash ngoài; task tài liệu không flash bo.

User Guide public có các mô tả chưa thống nhất; schematic public mang rev v1.0 trong khi bo nhóm là V1.1. Vì vậy tài liệu hãng là đầu vào đối chiếu, không thay việc kiểm đúng revision/bo thực.

## 3. Vai trò trong KVC và trạng thái triển khai

**DESIGN:** camera → nhận/tiền xử lý ảnh → AI → BBox → UART → Sonix. Bộ đệm, accelerator, model và hình thức đưa ảnh vào chưa khóa. Chưa thấy project RTL/top-level/testbench/constraints KVC dạng rời trong workspace; có tài liệu không đồng nghĩa đã synthesis hoặc chạy bo.

Model mục tiêu của KVC là **YOLO11n**, hai lớp person/lifebuoy. GoAI là phương án cần thử khả thi; không suy YOLO11n tương thích GoAI, input 640×640, INT8, FPS, LUT/BRAM/DSP hoặc tần số chạy chỉ từ tên IP/model. Cần compiler/operator report, resource/timing và so kết quả ảnh thật. Model PC phải ghi PC_REFERENCE. Nguồn tham khảo: [Gowin GoAI](https://github.com/gowinsemi/GoAI).

UART/IRQ theo **dự thảo mục IV** của [thiết kế hệ thống](../KVC_ThietKeHeThong.md); chưa chốt pin/baud mới. Không tự đổi cấu hình để vừa module hoặc ví dụ hãng.

## 4. Việc cần làm

- **Vững:** xác minh board/device/toolchain, camera RX, bộ nhớ/IP; tạo project KVC và mô phỏng UART/reset/FIFO/CDC; lưu báo cáo synthesis/timing khi build được.
- **Kiên:** kiểm bo/cổng nguồn/VCCIO, cáp/adapter, sơ đồ nối và gá; đo nguồn dưới tải cùng Vững.
- **Vững + Phong:** chốt nối FPGA–Sonix và golden vectors; thử loopback trước ghép AI/cảm biến.
- **Vững + Thịnh:** chọn model từ evidence PC, kiểm preprocessing/export/INT8 và phép so sánh trên bo.

Bằng chứng cần lưu: ảnh revision/mã chip, schematic tương ứng, pin map đã duyệt, constraints, phiên bản tool/IP, bitstream hash, input/output và log đo. Chỉ đánh dấu HARDWARE-VERIFIED cho phép thử đã thực hiện.

## 5. Tài liệu gốc

- [User Guide trong workspace](onekiwi20k/KIWIPRIMER20K_USERGUIDE.pdf).
- [Schematic trong workspace](onekiwi20k/fpga-kiwi-primer-20k.pdf).
- [Sơ đồ khối trong workspace](onekiwi20k/Block_diagram.png).
- [Schematic công khai từ hãng](https://linuxbsp.onekiwi.com.vn/FPGA/PRIMER_20K/Schematic/fpga-kiwi-primer-20k.pdf).

Lượt này đối chiếu nội dung text tài liệu hãng; ảnh render PDF web không lấy được. Chưa kiểm trực quan đầy đủ mọi net/pin và chưa đo bo. Bản ghi chú trước sửa được giữ trong evidence task KVC-DOC-CONSISTENCY-20261014-001, không dùng làm cấu hình hiện hành.
