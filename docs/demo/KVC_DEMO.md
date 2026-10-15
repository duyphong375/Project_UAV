# KVC — Kịch bản trình diễn

**Cập nhật 14/10/2026.** Đây là kế hoạch trình diễn; từng phần cần được thử trước khi công bố đã chạy thật. Theo mục II.3 của [thiết kế hệ thống](../KVC_ThietKeHeThong.md).

## 1. Video nhận diện trên cảnh lũ lụt

Thịnh chuẩn bị video nguồn và kết quả nhận diện người/phao. Phong xác nhận model, cấu hình và nội dung kỹ thuật; Vững kiểm mô tả phần FPGA.

- Giữ nguồn/quyền sử dụng, video gốc, model/cấu hình và log chạy.
- Hiển thị khung nhận diện, lớp và độ tin cậy; có đoạn không có mục tiêu để thấy báo động giả nếu xảy ra.
- Nói rõ AI chạy trên laptop hay FPGA, đang chạy trên file hay chiếu kết quả đã ghi.
- Mở được video gốc và kết quả khi không có Internet. Video demo không thay phép đánh giá độ chính xác.

## 2. Video thử tại bể bơi và Dashboard

Thịnh quay màn hình/dựng video; Kiên quay toàn cảnh và lo nguồn/gá; Cường chuẩn bị trạm đất/cảm biến/đo thực tế; Phong vận hành MCU; Vững vận hành camera/FPGA.

- Quay mục tiêu, camera, thiết bị, trạm đất và laptop trong cùng phiên thử.
- Có mốc thời gian/sự kiện chung giữa toàn cảnh, màn hình, dữ liệu nhận và log.
- Thể hiện dữ liệu lên Dashboard, trạng thái link/cảm biến và lưu/phát lại đúng phiên.
- Chỉ trình bày tọa độ khi có thông số camera, góc lắp, mốc đo và dữ liệu hợp lệ; thiếu thì hiển thị INVALID/N/A.
- Giữ video gốc, dữ liệu gốc và cấu hình; ghi rõ phần thật, dữ liệu giả hoặc AI tham chiếu PC.

## 3. Test trực tiếp tại cuộc thi — không sa bàn

Phong điều phối; Vững lo FPGA/camera; Thịnh lo ESP32 gateway và Dashboard/log; Kiên lo nguồn/dây; Cường lo LoRa và trạm đất.

### Chuẩn bị

- [ ] Đúng bộ thiết bị, nguồn, dây và anten đã thử; kiểm trước khi bật.
- [ ] Cấu hình/model/firmware/FPGA cố định, có phiên bản và cách chạy.
- [ ] Laptop có ứng dụng/tài nguyên offline, hai video và bản sao log dự phòng.
- [ ] Chốt đầu vào camera trực tiếp hay video-file trước tổng duyệt, thử được đường đưa đầu vào tới nơi chạy AI.
- [ ] Không yêu cầu sa bàn/bể nước tại gian thi; không giả định GPS có fix hoặc có sẵn hiệu chuẩn định vị.

### Thao tác

1. Cấp nguồn riêng cho ESP32 trạm đất; mở Dashboard web và dịch vụ GCS trên laptop, kết nối Wi-Fi SoftAP/WebSocket theo cấu hình đã kiểm, rồi tạo phiên mới.
2. Đưa đầu vào đã tổng duyệt; đối chiếu sự kiện với nhận diện, dữ liệu và màn hình.
3. Thử ngắt/kết nối lại link theo thao tác đã kiểm. Màn hình phải báo mất link/dữ liệu cũ và khôi phục đúng.
4. Kết thúc phiên, mở log/phát lại phiên vừa tạo với nhãn REPLAY.
5. Ghi kết quả từng bước, thực hiện 5 lượt tổng duyệt với đúng bộ mang đi thi.

## 4. Khi có sự cố

- Live thất bại thì ghi lỗi; mở video/log dự phòng bằng thao tác rõ ràng và nói đó là kết quả ghi trước.
- Không tự thay nguồn REAL bằng MOCK khi mất kết nối.
- LoRa chỉ truyền dữ liệu nhận diện/cảm biến, không truyền video. Kênh video phải được mô tả riêng.
- Một đoạn chạy được chưa chứng minh toàn chuỗi FPGA → MCU tải → LoRa → ESP32 → Wi-Fi/WebSocket → GCS/Dashboard chạy thật.
- Không tự đổi baud/gói/CRC/IRQ/chân nối để xử lý demo.

Hướng dẫn phần mềm: [backend](../../Dashboard/backend/README.md), [frontend](../../Dashboard/frontend/README.md). Việc cần hoàn thiện: [checklist 5 người](../planning/KVC_CONG_VIEC_CHI_TIET_5_NGUOI.md). Tiến độ: [báo cáo hiện tại](../KVC_PROJECT_STATUS.md).
