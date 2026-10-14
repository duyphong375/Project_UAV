# KVC — Hiện trạng và phân công 5 người

## 1. Dự án đã làm được những gì?

Theo [báo cáo tiến độ ngày 14/10/2026](../KVC_PROJECT_STATUS.md):

- Đã có Dashboard cơ bản gồm giao diện và phần xử lý phía máy tính.
- Đã có hiển thị dữ liệu giả để thử giao diện, bản đồ và cảnh báo.
- Đã có chức năng lưu dữ liệu và phát lại các phiên đã ghi.
- Đã có phần training AI cơ bản, model và chương trình nhận diện tham chiếu trên máy tính.
- Đã có các bài kiểm tra phần mềm, tài liệu thiết kế và kế hoạch triển khai.

**Hiện tại chưa xác nhận toàn bộ chuỗi FPGA → MCU → LoRa → Dashboard chạy trên thiết bị thật; AI trên FPGA cũng chưa được xác nhận.**

## 2. Nhiệm vụ chính của từng người

| Người | Nhiệm vụ chính |
| --- | --- |
| **Duy Phong** | Viết chương trình MCU trên UAV: nhận kết quả từ FPGA, đọc cảm biến, tính vị trí khi đủ dữ liệu và gửi xuống trạm đất. Điều phối ghép và kiểm tra toàn hệ thống. |
| **Vững** | Lập trình FPGA: kết nối camera, xử lý ảnh, thử đưa AI lên FPGA và gửi kết quả nhận diện cho MCU. |
| **Thịnh** | Viết chương trình MCU trạm đất, đưa dữ liệu thật lên Dashboard, hoàn thiện hiển thị/lưu/phát lại. Làm nhãn/kiểm chất lượng dữ liệu và model AI, làm hai video demo và chuẩn bị phần mềm trình diễn. |
| **Kiên** | Phụ trách nguồn điện, dây nối FPGA–MCU, camera và gá lắp. Kiểm tra nguồn, nhiệt độ và chuẩn bị bộ thiết bị mang đi thi. |
| **Cường** | Phụ trách lắp MCU, cảm biến, LoRa hai đầu và trạm đất. Kiểm tra đường truyền, thu ảnh/video thực tế và chuẩn bị buổi thử tại bể bơi. |

<!-- Task: KVC-TEAM-SIMPLE-20261014-001 (tiếp tục). Owner: Codex. Scope/allowed files: docs/planning/KVC_PHAN_CONG_5_NGUOI.md. Acceptance: chỉ nêu hiện trạng và nhiệm vụ chính 5 người, không có bàn giao hoặc bước chi tiết. Tests: đối chiếu KVC_PROJECT_STATUS.md, kiểm văn bản và git diff --check. Status: tài liệu đã chỉnh; SELF-REVIEW, chưa human approval. -->

<!-- Verification: đối chiếu văn bản hoàn tất, không có khoảng trắng cuối dòng. git diff --check: NOT RUN, exit N/A; process bị chặn: spawn EPERM. -->
