# KVC — Công việc chi tiết để hoàn thiện dự án

**Cập nhật: 15/10/2026.** Dựa trên [phân công 5 người](KVC_PHAN_CONG_5_NGUOI.md), [tiến độ dự án](../KVC_PROJECT_STATUS.md) và [thiết kế hệ thống](../KVC_ThietKeHeThong.md).

Đây là danh sách việc cần làm, chưa xác nhận đã hoàn thành. Các ô chỉ đánh dấu khi có kết quả kiểm tra.
Dashboard, lưu/phát lại dữ liệu và phần AI trên máy tính đã có nền tảng; tiếp tục hoàn thiện các phần này.
Việc còn lại là xây phần FPGA/MCU, nối thiết bị thật, đo kiểm và chuẩn bị trình diễn.

## 1. Duy Phong — MCU trên UAV và tích hợp hệ thống

### 1.1. Chuẩn bị project MCU

- [x] Xác định đúng chip Sonix (`SN34F788FG`), phiên bản bo (`SN34F780 Starter-Kit V1.1`), công cụ lập trình (Keil MDK v5) và tài liệu sử dụng.
- [ ] Tạo project riêng cho KVC, kiểm chương trình khởi động và cấu hình clock.
- [ ] Build chương trình tối thiểu; khi có bo và thao tác nạp được cho phép, thử khởi động và xuất thông tin chẩn đoán.
- [x] Kiểm đủ cổng giao tiếp cho FPGA, cảm biến và LoRa theo sơ đồ đã chốt (Xem [KVC_MASTER_PINOUT_WIRING.md](../hardware/KVC_MASTER_PINOUT_WIRING.md) và [firmware/mcu_uav/inc/kvc_pinout.h](../../firmware/mcu_uav/inc/kvc_pinout.h)).

### 1.2. Nhận dữ liệu từ FPGA

- [ ] Cùng Vững và Thịnh xác nhận bản giao thức được sử dụng: trường dữ liệu, đơn vị, độ dài, thứ tự byte và CRC.
- [ ] Viết phần nhận UART và bộ đệm để không mất dữ liệu khi chương trình đang xử lý việc khác.
- [ ] Giải mã khung nhận diện: loại đối tượng, độ tin cậy, vị trí trên ảnh và thời gian.
- [ ] Xử lý gói thiếu/sai, dữ liệu rác, hết thời gian chờ và bộ đệm đầy; tìm lại đầu gói sau lỗi.
- [ ] Thử trên máy tính bằng dữ liệu mẫu, rồi đối chiếu dữ liệu UART từ FPGA thật.

### 1.3. Đọc và kiểm tra cảm biến

- [ ] Viết phần đọc cảm biến siêu âm AJ-SR04M, IMU (GY-87 I2C0) và GNSS (NEO-M10N) theo module thực tế đã chốt; thử lần lượt từng cảm biến.
- [ ] Kiểm đơn vị, phạm vi đo, hướng trục và thời gian của dữ liệu.
- [ ] Xử lý dữ liệu lỗi, quá cũ, mất kết nối và khôi phục sau khi cảm biến kết nối lại.
- [ ] GNSS không có fix hợp lệ thì không xuất tọa độ GPS hợp lệ.
- [ ] Giữ phần xử lý nặng ngoài ngắt; kiểm chương trình không treo khi một cảm biến lỗi.

### 1.4. Tính vị trí mục tiêu

- [ ] Xác nhận thông số camera, góc lắp, hướng trục và mốc tọa độ dùng cho khu vực thử.
- [ ] Kiểm phép đổi điểm ảnh sang vị trí bằng dữ liệu mẫu có đáp án biết trước.
- [ ] Xử lý tia gần song song mặt phẳng, điểm phía sau camera và thông số lắp đặt không hợp lệ.
- [ ] Kết hợp khoảng cách và góc nghiêng; không coi cự ly siêu âm luôn là độ cao thẳng đứng.
- [ ] So kết quả với 20 vị trí thực đo tại bể bơi; báo sai số và các mẫu không tính được.
- [ ] Phân biệt phát hiện đối tượng, theo dõi và xác nhận mục tiêu; chỉ hiển thị trạng thái đã có cơ sở.

### 1.5. Gửi LoRa và ghép hệ thống

- [ ] Viết phần tạo/gửi gói LoRa theo giao thức RF đã được duyệt; RF 32 byte hiện còn là draft, không tự coi là ABI đã chốt.
- [ ] Giữ nguyên cấu hình phần cứng/giao thức đang có tới khi nhóm duyệt thay đổi; telemetry source 20 byte là hiện trạng lịch sử, không tự chuyển sang 32 byte.
- [ ] Ghi số gói TxDone/lỗi và trạng thái cảm biến để đối chiếu với log ESP32 trạm đất.
- [ ] Ghép FPGA → MCU tải → LoRa → ESP32 trạm đất → ingress laptop/Dashboard bằng dữ liệu giả, dùng transport đã được chọn.
- [ ] Chạy bài thử chuỗi theo gate được duyệt; đối chiếu packet capture và giải thích gói mất/bị loại.
- [ ] Thay từng nguồn giả bằng AI/cảm biến thật, kiểm lại sau mỗi lần thay.
- [ ] Chốt giao diện MCU–FPGA và cấu hình LoRa với owner liên quan trước khi khóa tích hợp; triển khai theo baseline Wi-Fi SoftAP/WebSocket v1 cho ESP32–laptop, ghi nhận mọi thay đổi qua quyết định/task.

**Hoàn thành phần của Phong khi:** MCU nhận/đọc/gửi đúng trong các tình huống đã thử, xử lý được lỗi và có kết quả kiểm toàn chuỗi. Tọa độ chỉ được công nhận khi có phép đối chiếu thực tế.

## 2. Vững — FPGA, camera và AI

### 2.1. Xác nhận bo và công cụ

- [x] Cùng Kiên xác nhận chip, phiên bản bo FPGA: Bo mạch OneKiwi Primer 20K V1.1 (GW2A-LV18PG256C8/I7); đã tạo file ràng buộc chân Header J2 sang Sonix MCU ([fpga/constraints/pins.cst](../../fpga/constraints/pins.cst)).
- [ ] Dùng OneKiwi Primer 20K V1.1 nhóm đã có; xác minh camera/cáp, bộ nhớ thực và pin map, không dùng cấu hình Tang/DVP cũ.
- [ ] Tạo project KVC đúng bo, khai báo clock/reset và chân tín hiệu theo bản đã xác nhận.
- [ ] Kiểm công cụ Gowin/GoAI, giấy phép và IP cần dùng; ghi rõ phần còn thiếu.
- [ ] Thử khả năng biên dịch model sớm; kiểm toán tử, bộ nhớ và tài nguyên FPGA.

### 2.2. Tạo đường dữ liệu thử cho MCU

- [ ] Tạo BBox giả theo giao thức đã chốt để thử độc lập với camera/AI.
- [ ] Viết UART, bộ đệm, điều khiển gửi và tín hiệu báo dữ liệu theo thiết kế được duyệt.
- [ ] Mô phỏng reset giữa gói, bộ đệm đầy/rỗng, dữ liệu liên tục và số đối tượng tối đa.
- [ ] Kiểm truyền dữ liệu giữa các miền clock, reset và các ràng buộc timing.
- [ ] Khi có bo, đối chiếu byte/tín hiệu UART thực tế với dữ liệu mẫu MCU đang dùng.

### 2.3. Nhận và xử lý ảnh camera

- [ ] Làm camera xuất ảnh qua giao diện thực tế đã chốt.
- [ ] Kiểm clock, khung ảnh, thứ tự pixel/màu, kích thước và khởi động lại camera.
- [ ] Xử lý đổi kích thước ảnh và phần đệm ảnh đúng với cách model được huấn luyện/đánh giá.
- [ ] Xuất ảnh hoặc dữ liệu đầu vào mẫu để so với chương trình trên máy tính.
- [ ] Nếu cần bộ nhớ ngoài, xác nhận đúng loại/dung lượng và kiểm đọc–ghi trước khi dùng.

### 2.4. Đưa AI lên FPGA

- [ ] Thử dữ liệu nhỏ trước, sau đó model đang được nhóm chọn.
- [ ] So kết quả FPGA với kết quả máy tính trên cùng ảnh và cách xử lý đầu vào.
- [ ] Kiểm khung nhận diện, lớp đối tượng, độ tin cậy và sai lệch sau lượng tử hóa INT8 nếu sử dụng.
- [ ] Đo tốc độ/độ trễ trên bo, kiểm tài nguyên và timing của đúng bản đang chạy.
- [ ] Nếu không khả thi, ghi lỗi cụ thể và đề xuất phương án để nhóm quyết định; không tự gọi AI trên laptop là AI FPGA.

### 2.5. Hoàn thiện bản FPGA dùng để demo

- [ ] Thay BBox giả bằng kết quả nhận diện thật khi AI đã được kiểm.
- [ ] Kiểm lại UART, reset và bộ đệm sau khi ghép camera/AI.
- [ ] Lưu bản project, cấu hình, kết quả build/timing và cách tạo lại bản đang dùng.
- [ ] Thử chạy camera/FPGA trong phiên bể bơi và tổng duyệt với đúng bộ thiết bị mang đi thi.

**Hoàn thành phần của Vững khi:** FPGA tạo được đầu ra đúng với phạm vi đã triển khai, có kiểm tra mô phỏng/build và kiểm trên bo. Khả năng AI phải có kết quả thực tế hoặc phương án thay thế được nhóm thống nhất.

## 3. Thịnh — Trạm đất, Dashboard, AI và video

### 3.1. Tiếp tục phần mềm GCS hiện có

- [ ] Tự chạy frontend/backend, dữ liệu MOCK, lưu dữ liệu và replay theo workflow dự án.
- [ ] Kiểm trạng thái hiện có và lỗi môi trường; không coi kết quả lịch sử là xác minh runtime hiện tại.
- [ ] Tiếp tục dùng Dashboard web và backend GCS hiện có; bổ sung ingress ESP32 theo kiến trúc đã duyệt, không tạo lại Dashboard.
- [ ] Giữ phân biệt MOCK, REPLAY và REAL; ingress thật chưa được xác nhận nếu chưa có capture từ thiết bị.
- [ ] Đối chiếu task GCS/AI đang mở với kiến trúc hiện tại trước khi tiếp tục, nhất là phần còn giả định USB/serial là liên kết gateway.

### 3.2. Viết firmware gateway ESP32 trạm đất

- [ ] Xác minh đúng kit/module ESP32-C3 sẽ dùng; chọn board ID PlatformIO theo mã bo thực tế. PlatformIO + Arduino là toolchain mục tiêu. Kiểm flash, nguồn riêng và GPIO khả dụng trước khi chốt module LoRa, chân SPI/IRQ/reset và OLED; pinout phải theo sơ đồ được nhóm duyệt.
- [ ] ESP32-C3 là CPU đơn nhân: thiết kế các tác vụ LoRa RX, OLED và Wi-Fi SoftAP/WebSocket không chặn nhau; kiểm RAM/heap, độ trễ và mất gói khi chạy đồng thời. Không dùng giả định phân chia Core 0/Core 1; kết quả chỉ được đánh dấu BUILT hoặc HARDWARE-VERIFIED sau khi có phép thử tương ứng.
- [ ] Viết phần nhận LoRa, kiểm CRC phần cứng và đọc RSSI/SNR theo module/cấu hình đã chọn; giữ giao thức RF ở trạng thái draft cho tới khi được duyệt.
- [ ] Thiết kế trạng thái boot, packet counter, timeout và hành vi khi laptop mất kết nối; ESP32 vẫn tiếp tục nhận LoRa khi laptop tắt.
- [ ] Triển khai và kiểm framing/schema, session/sequence, timestamp, integrity, xác thực và reconnect theo baseline Wi-Fi SoftAP/WebSocket v1 trong mục IV.4 thiết kế; các giá trị mục tiêu vẫn cần thử nghiệm.
- [ ] Thử từng lớp bằng gói mẫu trước khi nối RF; lưu log nhận/lỗi và trạng thái link. Không tuyên bố lưu bền hoặc buffer khi disconnect nếu chưa thiết kế và kiểm thử.

### 3.3. Nối ingress ESP32 với Dashboard web

- [ ] Xây ingress phía laptop theo transport/schema đã được chốt; browser hiển thị Dashboard, dịch vụ GCS trên laptop nhận dữ liệu, cập nhật state, lưu log và replay.
- [ ] Giải mã application envelope/RF theo contract đã duyệt; không coi RF32 draft hoặc telemetry source 20 byte là ABI đã được xác nhận.
- [ ] Kiểm frame bị chia/nối, CRC/integrity, sequence/session, timeout, dữ liệu trùng/lỗi và trạng thái stale.
- [ ] Kiểm queue/backpressure và ghi nhận mất dữ liệu khi tốc độ nhận vượt khả năng xử lý; không hiển thị mẫu cũ như dữ liệu mới.
- [ ] Hiển thị trạng thái ESP32/link/cảm biến, detection và tọa độ chỉ khi validity flags/điều kiện định vị hợp lệ.
- [ ] Thử laptop ngắt kết nối, reconnect và phiên mới; ESP32 vẫn có nguồn riêng và tiếp tục nhận LoRa. Xác minh dữ liệu nào được giữ/mất theo cơ chế buffer đã chọn.
- [ ] Đối chiếu packet capture với Dashboard, SQLite và replay cùng phiên.

### 3.4. Kiểm chất lượng AI

- [ ] Ghi nguồn và quyền sử dụng ảnh/video, model và cấu hình đang dùng.
- [ ] Kiểm nhãn người/phao, ảnh trùng, ảnh không có mục tiêu và ảnh sai chất lượng.
- [ ] Tách dữ liệu huấn luyện và kiểm tra theo phiên; khóa tập kiểm tra trước đánh giá cuối.
- [ ] Chuẩn bị tập kiểm tra độc lập theo thiết kế, báo riêng kết quả lũ lụt và bể bơi.
- [ ] Chạy công cụ kiểm hồ sơ dữ liệu; xử lý thiếu sót bằng dữ liệu thật, không sửa điều kiện để ép kết quả đạt.
- [ ] Đánh giá bỏ sót, nhận nhầm và báo động giả; lưu đầu vào, kết quả và log.
- [ ] Chuẩn bị dữ liệu lượng tử hóa/export nếu Vững đã xác nhận công cụ cần; báo riêng kết quả PC và FPGA/INT8.

### 3.5. Kiểm độ ổn định và làm hai video

- [ ] Thử Dashboard không có Internet từ lúc khởi động, gồm bản đồ/ảnh/tài nguyên cần cho demo.
- [ ] Thử chạy lâu và nhiều dữ liệu theo kế hoạch GCS; theo dõi RAM, gói mất và lỗi.
- [ ] Thử tắt ứng dụng đột ngột và kiểm dữ liệu SQLite đã ghi hoàn tất có khôi phục được không.
- [ ] Làm video 1: nhận diện trên video lũ lụt có sẵn; giữ nguồn và file kết quả mở được offline.
- [ ] Làm video 2: thử bể bơi, quay Dashboard cùng phiên với cảnh toàn hệ thống; lưu mốc đồng bộ và log gốc.
- [ ] Ghi rõ AI chạy ở đâu, phần nào giả/thật; không mô tả LoRa truyền video.

### 3.6. Chuẩn bị laptop thi

- [ ] Đóng gói Dashboard web, dịch vụ GCS, cấu hình Wi-Fi SoftAP/WebSocket, tài nguyên offline, hai video và hướng dẫn chạy.
- [ ] Thử trên đúng laptop demo từ lúc khởi động đến kết thúc phiên, không phụ thuộc Internet.
- [ ] Thử tạo phiên mới, mất link/reconnect theo transport đã chốt, lưu và phát lại phiên vừa chạy.
- [ ] Chuẩn bị video/log dự phòng có nhãn và cách khôi phục khi ứng dụng lỗi.

**Hoàn thành phần của Thịnh khi:** ingress ESP32 lên Dashboard đúng theo giao diện được duyệt, lưu/replay đúng phiên, mất link/stale hiển thị đúng; ESP32 tiếp tục thu LoRa bằng nguồn riêng khi laptop tắt. Các chức năng chưa thử phải ghi rõ NOT RUN/BLOCKED.

## 4. Kiên — Nguồn điện, dây nối, camera và gá lắp

### 4.1. Kiểm linh kiện phía FPGA/camera

- [ ] Lập danh sách bo FPGA, camera, cáp, adapter và nguồn: đã có, đang chờ, thiếu hoặc chưa rõ.
- [ ] Ghi đúng tên bo, phiên bản, đầu nối và ảnh thực tế để đối chiếu tài liệu.
- [ ] Xác nhận giao diện camera với Vững; không đoán có DVP chỉ từ thiết kế cũ.

### 4.2. Hoàn thiện bộ nguồn

- [ ] Lập sơ đồ cấp nguồn theo từng module; VDD Sonix 2,4–3,6 V, kiểm VDDIO1; không cấp 5 V vào VDD/GPIO hoặc dùng CP2102 cấp cả MCU+LoRa.
- [ ] Kiểm điện áp, chiều cắm, nối đất và khả năng cấp dòng trước khi nối tải.
- [ ] Đo nguồn khi hệ thống hoạt động và khi LoRa phát cùng Cường.
- [ ] Kiểm sụt áp, nhiễu, reset bất thường và nhiệt; xử lý theo số đo.
- [ ] Đo nguồn/nhiệt 60 phút khi chạy toàn tải; ghi điều kiện và cấu hình đo.

### 4.3. Hoàn thiện dây và gá

- [ ] Lập bảng nối từ chân FPGA qua đầu nối/dây tới chân MCU theo bản đã duyệt.
- [ ] Kiểm thông mạch, mức điện và hướng tín hiệu cùng Phong/Vững/Cường.
- [ ] Đánh nhãn dây, cố định đầu nối và bố trí để dễ kiểm tra/tháo lắp.
- [ ] Lắp camera/gá chắc chắn; ghi góc lắp, hướng trục, kích thước và vị trí cảm biến.
- [ ] Kiểm hình camera và độ ổn định gá khi dùng đúng cấu hình thử.

### 4.4. Chuẩn bị quay và mang đi thi

- [ ] Bố trí nguồn/gá/camera cho buổi thử bể bơi.
- [ ] Quay toàn cảnh mục tiêu, thiết bị, trạm đất và laptop; tạo mốc đồng bộ với màn hình của Thịnh.
- [ ] Chuẩn bị nguồn/cáp/phụ kiện dự phòng, nhãn dây và danh sách đóng gói.
- [ ] Thử bố trí lại bộ thiết bị tại bàn demo, không cần sa bàn hoặc bể nước.

**Hoàn thành phần của Kiên khi:** nguồn/dây/gá đã kiểm và có số đo, camera được lắp đúng cấu hình, bộ thiết bị có thể tháo lắp và mang đi trình diễn.

## 5. Cường — MCU, cảm biến, LoRa và đo thực tế

### 5.1. Kiểm linh kiện MCU, LoRa và trạm đất

- [ ] Lập danh sách MCU tải, ESP32 gateway, cảm biến, module LoRa/anten, nguồn riêng và dụng cụ kết nối.
- [ ] Xác nhận chip/bo thực tế, chân giao tiếp, nguồn, anten và công cụ nạp/debug cùng Kiên/Thịnh.
- [ ] Ghi phần cứng đã có/còn thiếu; laptop không cấp nguồn hoặc làm bộ thu LoRa cho trạm đất.
- [ ] Ghi đúng model module RF hai đầu. Thiết kế hiện ghi Ra-02/SX1278; nếu nhóm chọn E22 hoặc model khác, cập nhật BOM/driver/cấu hình hai đầu trước khi tích hợp.

### 5.2. Lắp và thử cảm biến

- [ ] Cùng Kiên kiểm nguồn/mức điện trước khi nối từng cảm biến.
- [ ] Lắp cảm biến siêu âm AJ-SR04M, IMU và GNSS theo module thực có và sơ đồ đã duyệt.
- [ ] Cùng Phong thử đọc từng cảm biến; kiểm chip GY-87 thực nhận, GNSS/anten và AJ-SR04M trên mặt nước (góc mở chùm sóng, mép bờ, timeout), không chỉ đối chiếu khoảng 0,2–6 m.
- [ ] Thử mất kết nối và khôi phục từng module, ghi kết quả.
- [ ] Ghi vị trí/góc cảm biến so với camera để dùng khi tính vị trí.

### 5.3. Hoàn thiện liên kết LoRa và ESP32 gateway

- [ ] Lắp hai module LoRa, anten và nguồn theo đúng model/cấu hình đã được nhóm chốt.
- [ ] Cùng Phong/Thịnh thử truyền nhận trên bàn; ESP32 gateway có nguồn riêng và laptop nhận dữ liệu qua baseline Wi-Fi SoftAP/WebSocket v1.
- [ ] Kiểm gói gửi/nhận/lỗi, CRC và RSSI/SNR từ module; ghi đúng cấu hình BW/SF/CR/công suất thực dùng.
- [ ] Đo tối thiểu 200 gói như mục VII thiết kế; ghi cự ly, anten, vị trí, môi trường, cấu hình, TxDone và số gói nhận hợp lệ.
- [ ] Tính PRR theo log hai đầu; đo p95 độ trễ chỉ khi có clock đồng bộ hoặc mốc đo chung.
- [ ] Thử laptop ngắt/reconnect và ESP32 reset/mất nguồn; không giả định ESP32 giữ gói khi mất kết nối nếu chưa có cơ chế buffer được thiết kế.


### 5.4. Tổ chức thử bể bơi và đo vị trí

- [ ] Chuẩn bị địa điểm, lịch thử, mục tiêu người/phao và người hỗ trợ.
- [ ] Cùng Kiên xác nhận vị trí camera/gá, mốc tọa độ và điều kiện phiên thử.
- [ ] Đo 20 vị trí đối chiếu khi nghiệm thu định vị; lưu khoảng cách/góc/mốc đo thực tế.
- [ ] Thu ảnh/video và ghi thời gian, cấu hình, model của từng phiên.
- [ ] Đối chiếu số đo với kết quả của Phong và log của Thịnh.

### 5.5. Thu dữ liệu thực tế cho AI

- [ ] Cường lập phiên thu ảnh/video bằng camera thực dùng; Kiên/Vững hỗ trợ góc lắp và cấu hình.
- [ ] Ghi nguồn/quyền sử dụng, session, domain, ánh sáng, khoảng cách, góc nhìn và thời gian; giữ file gốc/hash.
- [ ] Có cảnh người/phao và cảnh âm tính, phản xạ/che khuất; không lấy nhiều frame gần nhau thay phiên độc lập.
- [ ] Thịnh làm nhãn/QA, chia train/val/test theo phiên và khóa test trước chọn model; dữ liệu demo và test phải phân biệt.
- [ ] Phong cùng Thịnh/Vững đánh giá baseline trên dữ liệu mới, xác định thiếu dữ liệu hay model trước quyết định train lại.

### 5.6. Chuẩn bị vận hành tại cuộc thi

- [ ] Kiểm cảm biến/LoRa/trạm đất trước mỗi lượt tổng duyệt.
- [ ] Chuẩn bị anten, dây/đầu nối RF, nguồn và phụ kiện dự phòng đang có; laptop không phải nguồn cho ESP32 trạm đất.
- [ ] Thực hiện thao tác ngắt–kết nối lại đã thử trước và ghi hiện tượng thực tế.
- [ ] Kiểm bộ thiết bị và cấu hình sau khi vận chuyển tới địa điểm thi.

**Hoàn thành phần của Cường khi:** các module đã được kiểm riêng và khi ghép, có kết quả đo đường truyền/vị trí, ESP32 trạm đất có nguồn riêng và khôi phục được theo các bài thử đã làm.

## 6. Thứ tự ưu tiên để hoàn thiện dự án

1. **Xác nhận phần cứng:** đúng OneKiwi, camera/cáp, Sonix, cảm biến, ESP32, module LoRa, anten, nguồn và giao diện chân; chưa chốt pinout thì chưa đấu nối.
2. **Chốt giao diện trước tích hợp:** UART FPGA–Sonix và RF LoRa; tạo vectors mẫu. RF32 là draft; không thay source 20 byte hay giao thức khác khi chưa duyệt. ESP32–laptop dùng baseline Wi-Fi SoftAP/WebSocket v1 trong thiết kế, chưa xác minh triển khai.
3. **Thử độc lập từng phân hệ:** BBox giả/MCU tải, camera/FPGA, cảm biến, ESP32 nhận LoRa, Dashboard MOCK/offline; ghi trạng thái và lỗi.
4. **Ghép theo tầng:** FPGA → MCU tải → LoRa → ESP32 → transport đã chọn → ingress laptop/Dashboard. Đối chiếu log/capture tại mỗi ranh giới.
5. **Đo nghiệm thu:** AI, PRR/độ trễ LoRa, định vị, nguồn/nhiệt, offline/reconnect/log/replay theo mục VII thiết kế. Các KPI là mục tiêu cho đến khi có phép đo.
6. **Chuẩn bị demo:** video lũ lụt, video bể bơi có đối chiếu cùng phiên, bộ thiết bị/laptop cố định và tổng duyệt trực tiếp không sa bàn.

Khi chờ linh kiện, tiếp tục mô phỏng, thử vectors, kiểm Dashboard và QA dữ liệu AI. Không cần chờ đủ mọi module để kiểm từng phần.
Nếu AI FPGA không khả thi, ghi lỗi build/đo cụ thể và để nhóm quyết định phương án; gắn nhãn PC_REFERENCE cho inference trên laptop.

## 7. Điều kiện để coi dự án hoàn thiện

- [ ] Các phần chạy thật có log/capture đối chiếu từ đầu vào đến Dashboard; phần MOCK/PC_REFERENCE/REPLAY được ghi rõ.
- [ ] Kết quả AI, PRR, độ trễ, sai số vị trí và nguồn/nhiệt được đo theo mục VII thiết kế; phần chưa đạt có kết luận và giới hạn.
- [ ] Dashboard web và dịch vụ GCS chạy offline; báo mất link/dữ liệu stale đúng, reconnect và replay đúng phiên.
- [ ] ESP32 trạm đất chạy nguồn riêng, tiếp tục nhận LoRa khi laptop tắt/mất kết nối; không suy ra buffer bền nếu chưa kiểm.
- [ ] Video lũ lụt và video bể bơi mở được offline, đúng nguồn/cấu hình, giữ file và log gốc.
- [ ] Tổng duyệt 5 lượt theo checklist thiết kế: khởi động → đầu vào đã thử → dữ liệu mới → mất link/khôi phục → lưu/phát lại.
- [ ] Cấu hình demo cố định; bộ thiết bị, tài liệu vận hành và bản sao dữ liệu/log đã chuẩn bị.

Các con số trong thiết kế là mục tiêu, không phải kết quả đã đo. Tại gian thi không cần sa bàn; thiếu GPS hoặc thông số định vị thì hiển thị INVALID/N/A. LoRa chỉ mang metadata, không mang video.

## 8. Quy tắc khi triển khai

- Mỗi task có một owner, scope/file, acceptance, phép kiểm tra và status rõ; checklist không tự cấp quyền sửa toàn repo.
- Không tự đổi baud, packet layout, CRC, IRQ, pinout hay giao thức phần cứng. Telemetry 20 byte là hiện trạng lịch sử; RF32 chưa phải ABI đã duyệt. Wi-Fi SoftAP/WebSocket v1 là baseline thiết kế cho ESP32–laptop nhưng chưa được kiểm chứng.
- Dùng lại source và SDK hiện có; không coi code mẫu trong SDK là firmware KVC đã tích hợp.
- Phân biệt PLANNED, SOURCE-VERIFIED, SIMULATED, BUILT và HARDWARE-VERIFIED. Công cụ/thiết bị không chạy thì ghi NOT RUN/BLOCKED.
- Ghi lệnh/cách thử, đầu vào, kết quả, exit code nếu có, log và giới hạn; không khẳng định KPI chưa đo.
- Theo [AGENTS.md](../../AGENTS.md) và [workflow](../KVC_AI_WORKFLOW.md). Không tự commit/push/merge/deploy/nạp FPGA hoặc MCU.

<!-- Task ID: KVC-TEAM-PLAN-20261015-001. Owner: Codex. Scope/allowed files: docs/planning/KVC_PHAN_CONG_5_NGUOI.md and docs/planning/KVC_CONG_VIEC_CHI_TIET_5_NGUOI.md only. Acceptance: both documents align with KVC_ThietKeHeThong.md, clearly mark planned/unverified items and draft interfaces, and describe ESP32 ground gateway + web Dashboard topology without laptop-dependent ground MCU. Tests: content/link/whitespace checks and git diff --check. Status: READY_FOR_REVIEW; SELF-REVIEW, not HUMAN APPROVAL.
