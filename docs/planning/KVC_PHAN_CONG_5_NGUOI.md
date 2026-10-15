# KVC — Hiện trạng và phân công 5 người

## 1. Hiện trạng theo bằng chứng

Theo [báo cáo tiến độ](../KVC_PROJECT_STATUS.md), KVC đã có nền tảng Dashboard GCS trên máy tính với dữ liệu MOCK, lưu phiên và replay; có AI tham chiếu chạy trên PC. Nhóm xác nhận đã có bo OneKiwi Primer 20K V1.1.

Chưa có bằng chứng toàn chuỗi phần cứng FPGA → MCU tải → LoRa → ESP32 trạm đất → Dashboard chạy với dữ liệu REAL; AI trên FPGA và ingress dữ liệu thật vào GCS cũng chưa được xác nhận. Các KPI trong [thiết kế hệ thống](../KVC_ThietKeHeThong.md) là mục tiêu cần đo, không phải kết quả đã đạt.

## 2. Luồng hệ thống mục tiêu

**Camera → FPGA OneKiwi → MCU Sonix trên UAV + cảm biến → LoRa metadata → ESP32 trạm đất có nguồn riêng → Wi-Fi SoftAP/WebSocket → dịch vụ GCS và Dashboard web trên laptop.**

LoRa không truyền video. ESP32 trạm đất nhận LoRa độc lập với laptop; laptop đảm nhiệm dịch vụ GCS nhận/lưu/replay dữ liệu và giao diện Dashboard web. Thiết kế chọn họ SoC ESP32-C3 với Wi-Fi SoftAP/WebSocket v1; mã kit/board, module, flash và pinout còn phải xác minh trên phần cứng thực tế. Đây là baseline thiết kế, chưa có bằng chứng chạy. RF 32 byte vẫn là dự thảo ABI chưa duyệt; source telemetry 20 byte là hiện trạng lịch sử, không được tự ý đổi giao thức phần cứng. Bluetooth không phải transport mục tiêu hiện hành.

## 3. Nhiệm vụ chính của từng người

| Người | Nhiệm vụ chính |
| --- | --- |
| **Duy Phong** | MCU tải Sonix: nhận BBox từ FPGA, đọc LiDAR/IMU/GNSS, tính tọa độ chỉ khi đủ điều kiện hợp lệ và điều khiển LoRa phát theo giao thức đã được duyệt. Điều phối ghép và kiểm tra toàn chuỗi. |
| **Vững** | FPGA OneKiwi: xác minh giao diện camera/bo, xây đường ảnh và BBox thử, đánh giá tính khả thi AI trên FPGA, xuất dữ liệu sang MCU theo giao diện được nhóm duyệt. |
| **Thịnh** | Firmware ESP32 trạm đất và GCS laptop: nhận LoRa trên ESP32, chuyển dữ liệu qua Wi-Fi SoftAP/WebSocket v1 theo thiết kế; nối ingress vào Dashboard web, lưu/replay và kiểm trạng thái mất link. Phụ trách QA dữ liệu/model AI và hai video demo. |
| **Kiên** | Phụ trách kiểm kê phần cứng, nguồn riêng trạm đất, nguồn tải, dây nối, camera và gá. Đo nguồn/nhiệt, xác minh lắp đặt và chuẩn bị bộ thiết bị trình diễn. |
| **Cường** | Phụ trách lắp/bring-up cảm biến, LoRa hai đầu và anten; phối hợp thử ESP32 trạm đất, đo link theo bài đo thiết kế; tổ chức thu dữ liệu thực tế và thử bể bơi. |

## 4. Ranh giới và điều kiện phối hợp

- Phân công này không xác nhận linh kiện, giao thức hay chức năng đã chạy. Ghi riêng trạng thái DESIGN, SOURCE-VERIFIED, SIMULATED, BUILT và HARDWARE-VERIFIED.
- Thống nhất giao diện và điều kiện nghiệm thu trước khi ghép FPGA–MCU, RF hoặc ESP32–laptop. Không tự đổi baud, packet layout, CRC, IRQ hay pinout.
- ESP32 dùng nguồn riêng, tiếp tục nhận LoRa khi laptop tắt/mất kết nối; không lấy laptop làm bộ điều khiển hay nguồn cho MCU trạm đất.
- Chỉ LoRa metadata; video demo dùng file/kênh riêng. Không trình bày MOCK/REPLAY hoặc AI chạy trên PC như chuỗi REAL/AI FPGA.
- Tọa độ phải INVALID/N/A nếu thiếu GNSS hợp lệ hoặc hiệu chuẩn hệ local cần thiết.
- Tiêu chí và luồng nghiệm thu chi tiết xem [thiết kế hệ thống](../KVC_ThietKeHeThong.md) và [checklist công việc](KVC_CONG_VIEC_CHI_TIET_5_NGUOI.md).

<!-- Task ID: KVC-TEAM-PLAN-20261015-001. Owner: Codex. Scope/allowed files: docs/planning/KVC_PHAN_CONG_5_NGUOI.md and docs/planning/KVC_CONG_VIEC_CHI_TIET_5_NGUOI.md only. Acceptance: both documents align with KVC_ThietKeHeThong.md, clearly mark planned/unverified items and draft interfaces, and describe ESP32 ground gateway + web Dashboard topology without laptop-dependent ground MCU. Tests: content/link/whitespace checks and git diff --check. Status: READY_FOR_REVIEW; SELF-REVIEW, not HUMAN APPROVAL. -->
