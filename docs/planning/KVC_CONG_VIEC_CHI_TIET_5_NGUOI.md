# KVC — Công việc chi tiết để hoàn thiện dự án

**Ngày lập: 14/10/2026.** Dựa trên [phân công 5 người](KVC_PHAN_CONG_5_NGUOI.md), [tiến độ dự án](../KVC_PROJECT_STATUS.md) và [thiết kế hệ thống](../KVC_ThietKeHeThong.md).

Đây là danh sách việc cần làm, chưa xác nhận đã hoàn thành. Các ô chỉ đánh dấu khi có kết quả kiểm tra.
Dashboard, lưu/phát lại dữ liệu và phần AI trên máy tính đã có nền tảng; tiếp tục hoàn thiện các phần này.
Việc còn lại là xây phần FPGA/MCU, nối thiết bị thật, đo kiểm và chuẩn bị trình diễn.

## 1. Duy Phong — MCU trên UAV và tích hợp hệ thống

### 1.1. Chuẩn bị project MCU

- [ ] Xác định đúng chip Sonix, phiên bản bo, công cụ lập trình và tài liệu sử dụng.
- [ ] Tạo project riêng cho KVC, kiểm chương trình khởi động và cấu hình clock.
- [ ] Build chương trình tối thiểu; khi có bo và thao tác nạp được cho phép, thử khởi động và xuất thông tin chẩn đoán.
- [ ] Kiểm đủ cổng giao tiếp cho FPGA, cảm biến và LoRa theo sơ đồ đã chốt.

### 1.2. Nhận dữ liệu từ FPGA

- [ ] Cùng Vững và Thịnh xác nhận bản giao thức được sử dụng: trường dữ liệu, đơn vị, độ dài, thứ tự byte và CRC.
- [ ] Viết phần nhận UART và bộ đệm để không mất dữ liệu khi chương trình đang xử lý việc khác.
- [ ] Giải mã khung nhận diện: loại đối tượng, độ tin cậy, vị trí trên ảnh và thời gian.
- [ ] Xử lý gói thiếu/sai, dữ liệu rác, hết thời gian chờ và bộ đệm đầy; tìm lại đầu gói sau lỗi.
- [ ] Thử trên máy tính bằng dữ liệu mẫu, rồi đối chiếu dữ liệu UART từ FPGA thật.

### 1.3. Đọc và kiểm tra cảm biến

- [ ] Viết phần đọc LiDAR, IMU và GNSS theo module thực tế đã chốt; thử lần lượt từng cảm biến.
- [ ] Kiểm đơn vị, phạm vi đo, hướng trục và thời gian của dữ liệu.
- [ ] Xử lý dữ liệu lỗi, quá cũ, mất kết nối và khôi phục sau khi cảm biến kết nối lại.
- [ ] GNSS không có fix hợp lệ thì không xuất tọa độ GPS hợp lệ.
- [ ] Giữ phần xử lý nặng ngoài ngắt; kiểm chương trình không treo khi một cảm biến lỗi.

### 1.4. Tính vị trí mục tiêu

- [ ] Xác nhận thông số camera, góc lắp, hướng trục và mốc tọa độ dùng cho khu vực thử.
- [ ] Kiểm phép đổi điểm ảnh sang vị trí bằng dữ liệu mẫu có đáp án biết trước.
- [ ] Xử lý tia gần song song mặt phẳng, điểm phía sau camera và thông số lắp đặt không hợp lệ.
- [ ] Kết hợp khoảng cách và góc nghiêng; không coi cự ly LiDAR luôn là độ cao thẳng đứng.
- [ ] So kết quả với 20 vị trí thực đo tại bể bơi; báo sai số và các mẫu không tính được.
- [ ] Phân biệt phát hiện đối tượng, theo dõi và xác nhận mục tiêu; chỉ hiển thị trạng thái đã có cơ sở.

### 1.5. Gửi LoRa và ghép hệ thống

- [ ] Viết phần tạo/gửi gói LoRa theo bản giao thức được duyệt, có hàng đợi và xử lý hết thời gian chờ.
- [ ] Ghi số gói gửi, lỗi gửi và trạng thái cảm biến để đối chiếu với trạm đất.
- [ ] Ghép FPGA → MCU → LoRa → trạm đất → USB → Dashboard bằng dữ liệu giả trước.
- [ ] Chạy chuỗi thử 30 phút, đối chiếu dữ liệu và giải thích số gói mất hoặc bị loại.
- [ ] Thay từng nguồn giả bằng AI/cảm biến thật, kiểm lại sau mỗi lần thay.
- [ ] Chốt model/cấu hình cùng Vững và Thịnh, điều phối kiểm toàn hệ thống và demo trực tiếp.

**Hoàn thành phần của Phong khi:** MCU nhận/đọc/gửi đúng trong các tình huống đã thử, xử lý được lỗi và có kết quả kiểm toàn chuỗi. Tọa độ chỉ được công nhận khi có phép đối chiếu thực tế.

## 2. Vững — FPGA, camera và AI

### 2.1. Xác nhận bo và công cụ

- [ ] Cùng Kiên xác nhận chip, phiên bản bo FPGA, camera và giao diện camera thực tế.
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

### 3.1. Tiếp tục phần mềm hiện có

- [ ] Tự chạy frontend/backend, chế độ dữ liệu giả, lưu dữ liệu và phát lại.
- [ ] Chạy các bài kiểm tra hiện có; ghi lỗi môi trường hoặc chức năng còn thiếu.
- [ ] Xác định phần nối dữ liệu USB cần bổ sung; không tạo lại Dashboard từ đầu.
- [ ] Tiếp tục các task GCS/AI đã có, giữ mã và lịch sử; phần nhận serial theo KVC-GCS-004/009.

### 3.2. Viết chương trình MCU trạm đất

- [ ] Xác định đúng MCU/bo trạm đất và tạo project riêng cho KVC.
- [ ] Viết phần nhận LoRa và kiểm gói theo bản giao thức được duyệt.
- [ ] Đọc thông tin chất lượng tín hiệu từ thiết bị, ghi thời gian và số gói nhận/lỗi.
- [ ] Đóng gói dữ liệu gửi qua USB; thử bằng dữ liệu mẫu trước khi nối RF thật.
- [ ] Kiểm khởi động lại trạm đất, rút/cắm USB và khôi phục kết nối.

### 3.3. Đưa dữ liệu thật lên Dashboard

- [ ] Viết phần đọc cổng USB/COM, tách gói và giải mã dữ liệu.
- [ ] Kiểm dữ liệu bị chia nhỏ, nhiều gói nối nhau, gói sai CRC, mất đầu gói và hết thời gian chờ.
- [ ] Kiểm bộ đệm/hàng đợi khi dữ liệu đến nhanh; ghi gói mất thay vì giấu lỗi.
- [ ] Hiển thị nhận diện, trạng thái link/cảm biến và tọa độ theo dữ liệu hợp lệ.
- [ ] Mất kết nối hoặc dữ liệu quá cũ thì báo đúng trạng thái; không trình bày số cũ như số mới.
- [ ] Kiểm kết nối lại USB/WebSocket, phiên dữ liệu và cảnh báo trên giao diện.
- [ ] Đối chiếu dữ liệu nhận với dữ liệu hiển thị, lưu và phát lại.

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

- [ ] Đóng gói phần mềm, cấu hình, tài nguyên offline, hai video và hướng dẫn chạy.
- [ ] Thử trên đúng laptop demo từ lúc khởi động đến kết thúc phiên.
- [ ] Thử tạo phiên mới, mất link/kết nối lại, lưu và phát lại phiên vừa chạy.
- [ ] Chuẩn bị video/log dự phòng có nhãn và cách khôi phục khi ứng dụng lỗi.

**Hoàn thành phần của Thịnh khi:** dữ liệu trạm đất lên Dashboard đúng, lưu/phát lại được, chạy offline đã kiểm; có kết quả đánh giá AI, hai video và phần mềm demo dùng được trên laptop thi.

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

### 5.1. Kiểm linh kiện phía MCU và trạm đất

- [ ] Lập danh sách MCU hai đầu, cảm biến, LoRa/anten, USB và dụng cụ kết nối.
- [ ] Xác nhận đúng chip, phiên bản bo, chân giao tiếp, nguồn và công cụ lập trình/debug.
- [ ] Ghi module đã có/còn thiếu; xác định đường USB dùng bridge hay MCU hỗ trợ trực tiếp.

### 5.2. Lắp và thử cảm biến

- [ ] Cùng Kiên kiểm nguồn/mức điện trước khi nối từng cảm biến.
- [ ] Lắp LiDAR, IMU và GNSS theo module thực có và sơ đồ đã duyệt.
- [ ] Cùng Phong thử đọc từng cảm biến; kiểm chip GY-87 thực nhận, GNSS/anten và TF-Luna trên mặt nước (amp, góc, timeout), không chỉ đối chiếu khoảng 0,2–8 m.
- [ ] Thử mất kết nối và khôi phục từng module, ghi kết quả.
- [ ] Ghi vị trí/góc cảm biến so với camera để dùng khi tính vị trí.

### 5.3. Hoàn thiện LoRa và trạm đất

- [ ] Lắp LoRa hai đầu, anten, nguồn và dây theo cấu hình đã chốt.
- [ ] Cùng Phong/Thịnh thử truyền nhận trên bàn trước khi đo ngoài khu vực thử.
- [ ] Kiểm gói gửi/nhận/lỗi và chất lượng tín hiệu từ thiết bị.
- [ ] Đo tối thiểu 200 gói theo bài đo trong thiết kế; ghi cự ly, điều kiện, cấu hình và số gói mất.
- [ ] Tính tỷ lệ nhận gói từ log hai đầu; cùng Phong/Thịnh đo độ trễ đầu-cuối.
- [ ] Lắp trạm đất/USB; thử rút/cắm lại, reset và lỗi nguồn/đầu nối cùng Thịnh.

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
- [ ] Chuẩn bị anten, cáp USB, module/phụ kiện dự phòng đang có.
- [ ] Thực hiện thao tác ngắt–kết nối lại đã thử trước và ghi hiện tượng thực tế.
- [ ] Kiểm bộ thiết bị và cấu hình sau khi vận chuyển tới địa điểm thi.

**Hoàn thành phần của Cường khi:** các module đã được kiểm riêng và khi ghép, có kết quả đo đường truyền/vị trí, trạm đất/USB khôi phục được trong các bài thử đã làm.

## 6. Thứ tự ưu tiên để hoàn thiện dự án

1. **Chốt đầu vào:** đúng bo/camera/cảm biến, nguồn/chân nối, công cụ và giao thức; kiểm khả năng AI FPGA sớm.
2. **Ghép dữ liệu giả:** FPGA → MCU → LoRa → trạm đất → USB → Dashboard; chạy 30 phút.
3. **Ghép dữ liệu thật:** lần lượt camera/AI và cảm biến, kiểm sau mỗi lần ghép.
4. **Đo kiểm:** AI, đường truyền, định vị, nguồn/nhiệt, phần mềm offline và phục hồi lỗi.
5. **Chuẩn bị demo:** hai video, bộ thiết bị/laptop cố định và tổng duyệt trực tiếp 5 lượt.

Khi chờ linh kiện, tiếp tục mô phỏng, thử gói mẫu, kiểm Dashboard và dữ liệu AI. Không chờ đủ mọi module mới bắt đầu thử từng phần.
Nếu AI FPGA không khả thi, nhóm quyết định phương án thay thế dựa trên lỗi đo/biên dịch cụ thể và ghi rõ phạm vi thực hiện.

## 7. Điều kiện để coi dự án hoàn thiện

- [ ] Các phần chạy thật đã có log/capture đối chiếu từ đầu vào đến Dashboard; phần giả/tham chiếu được ghi rõ.
- [ ] Kết quả AI, tỷ lệ nhận gói, độ trễ, sai số vị trí và nguồn/nhiệt được so với mục VII của thiết kế; phần chưa đạt có kết luận xử lý.
- [ ] Dashboard chạy offline, báo mất link/dữ liệu cũ đúng, khôi phục kết nối và phát lại đúng phiên.
- [ ] Video lũ lụt và video bể bơi mở được offline, đúng nguồn/cấu hình, giữ file và log gốc.
- [ ] Tổng duyệt 5 lượt: khởi động → đầu vào đã thử → dữ liệu mới → mất link/khôi phục → lưu/phát lại.
- [ ] Cấu hình demo cố định; bộ thiết bị, tài liệu vận hành và bản sao dữ liệu/log đã chuẩn bị.

Các con số trong thiết kế là mục tiêu, không phải kết quả đã đo. Tại gian thi không cần sa bàn; thiếu GPS hoặc thông số định vị thì hiển thị không hợp lệ/chưa có.
LoRa chỉ mang dữ liệu nhận diện/cảm biến, không mang video.

## 8. Quy tắc khi triển khai

- Mỗi task có một người chịu trách nhiệm, phạm vi/file rõ, điều kiện hoàn thành, phép kiểm tra và trạng thái. Bảng này không tự cấp quyền sửa toàn repo.
- Không tự đổi baud, cấu trúc gói, CRC, IRQ hoặc chân nối. Telemetry 20 byte là ghi nhận source; RF32/USB48 trong thiết kế còn cần chốt trước khi triển khai.
- Dùng lại code hiện có và SDK theo tài liệu; không sửa trực tiếp SDK hãng thành code dự án.
- Phân biệt kế hoạch, đã kiểm source, mô phỏng, build và thử trên phần cứng. Công cụ không chạy thì ghi NOT RUN/BLOCKED.
- Ghi lệnh/cách thử, đầu vào, exit code nếu có, kết quả, log và giới hạn; lưu log trong review/ và sao lưu riêng.

<!-- Task ID: KVC-TEAM-DETAIL-20261014-001. Owner: Codex. Scope/allowed files: docs/planning/KVC_CONG_VIEC_CHI_TIET_5_NGUOI.md (file mới duy nhất). Acceptance: checklist chi tiết đúng vai trò 5 người, dựa trên tiến độ/thiết kế, có triển khai/kiểm thử/demo; không có mục bàn giao giữa người. Tests: đối chiếu nội dung, đọc lại UTF-8, kiểm khoảng trắng/link và git diff --check nếu chạy được. Status: READY_FOR_REVIEW; SELF-REVIEW, chưa HUMAN APPROVAL. Không triển khai code hoặc phần cứng trong task này. -->

<!-- Kiểm tra tài liệu: đọc lại UTF-8 khớp; link nội bộ tồn tại; không có khoảng trắng cuối dòng; task chỉ tạo file chi tiết, không ghi vào bản phân công gốc. git diff --check: NOT RUN, exit N/A, process bị chặn (spawn EPERM). Đây là kiểm tài liệu, không phải test triển khai/hardware. -->
