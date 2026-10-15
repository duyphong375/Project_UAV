# KVC — Chuẩn tài liệu Markdown

**Trạng thái:** Accepted làm quy ước biên tập tài liệu. Quy ước này không phê duyệt thiết kế phần cứng, giao thức hoặc kết quả thử nghiệm.

**Áp dụng:** KVC-MD-UNIFY-20261015-001; owner Codex; SELF-REVIEW, chưa human approval. Phạm vi là rà soát và đồng bộ Markdown trong workspace; thay đổi chỉ được ghi vào file `.md`.

## 1. Nguồn chuẩn và phạm vi

- `AGENTS.md` là nguồn chuẩn cho quyền, phạm vi task, bảo toàn thay đổi và mức bằng chứng. `.agents/rules/kvc.md` chỉ là adapter trỏ tới quy tắc đó.
- [Thiết kế hệ thống](KVC_ThietKeHeThong.md) là nguồn kiến trúc, BOM, giao thức mục tiêu/dự thảo và tiêu chí nghiệm thu.
- [Tiến độ dự án](KVC_PROJECT_STATUS.md) là snapshot theo bằng chứng; README và kế hoạch không thay thế báo cáo này.
- [Danh mục tài liệu](KVC_DOCUMENT_INDEX.md) mô tả vai trò, đối tượng đọc và liên kết giữa các tài liệu.
- Tài liệu chuyên ngành chỉ là nguồn chuẩn trong phạm vi được giao. Khi có mâu thuẫn, ghi rõ hai nguồn và trạng thái cần quyết định; không tự suy ra thay đổi kỹ thuật.

## 2. Cấu trúc và cách viết

- Mỗi tài liệu có một tiêu đề `#`; dùng `##` cho mục chính, `###` cho mục con và `####` khi thật cần. Không bỏ cấp tiêu đề.
- Đặt ngày cập nhật, Task ID, owner, trạng thái review và loại tài liệu gần đầu tài liệu khi thông tin đó có ý nghĩa. Tài liệu tham chiếu ổn định không cần metadata task giả.
- Viết tiếng Việt làm ngôn ngữ chính; giữ nguyên tên API, identifier, enum, tên chip/module và thuật ngữ gốc khi cần tìm kiếm hoặc đối chiếu source.
- Dùng nhất quán `FPGA`, `MCU tải`, `ESP32 trạm đất`, `LoRa`, `GCS`, `Dashboard web`, `Wi-Fi SoftAP`, `WebSocket`, `MOCK`, `REAL`, `REPLAY`.
- Viết tên file/thư mục đúng chữ hoa-thường theo repository. Link nội bộ dùng đường dẫn tương đối từ file hiện tại và đích đã tồn tại; ưu tiên nhãn link mô tả thay cho URL trần.
- Dùng đơn vị SI và ghi đơn vị tại tiêu đề/cột hoặc ngay sau trị số: `433 MHz`, `125 kHz`, `3,3 V`, `20 cm`, `3000 ms`. Không suy diễn phép đo từ trị số thiết kế.
- Bảng dành cho dữ liệu có cấu trúc, không nhồi đoạn văn dài. Danh sách checklist dùng `- [ ]` cho việc chưa hoàn thành và `- [x]` chỉ khi có evidence trong phạm vi.
- Dùng code fence có nhãn ngôn ngữ (`text`, `json`, `powershell`, `python`, `mermaid`). Không đặt secret, mật khẩu, token hoặc dữ liệu cá nhân vào ví dụ.
- Sơ đồ Mermaid mô tả luồng/quan hệ; phải phù hợp với phần văn bản và không biến giao thức dự thảo thành quyết định đã duyệt. Hình ảnh cần alt text và đường dẫn tương đối hợp lệ.

## 3. Trạng thái và mức khẳng định

Ghi trạng thái bằng từ khóa rõ ràng, kèm phạm vi và bằng chứng khi cần:

| Nhãn | Ý nghĩa |
| --- | --- |
| `Proposed` / `PROPOSED` | Đề xuất để xem xét; chưa được chốt hoặc giao triển khai. |
| `Accepted` / `ACCEPTED` | Quyết định đã được nhóm/owner có thẩm quyền chốt; phải dẫn nguồn quyết định nếu không nằm trong chính tài liệu. |
| `Pending` / `PENDING` | Còn thiếu quyết định hoặc đầu vào; nêu người/điều kiện cần để giải quyết nếu đã biết. |
| `Deprecated` / `DEPRECATED` | Không dùng làm phương án hiện hành; giữ lý do và đường dẫn phương án thay thế. Không đồng nghĩa xóa lịch sử. |
| `DESIGN` | Mục tiêu/spec, chưa chứng minh hoạt động. |
| `SOURCE-VERIFIED` | Đối chiếu source/config; chưa hàm ý build hoặc chạy thiết bị. |
| `SIMULATED` | Có kiểm tra mô phỏng/mock/host; nêu lệnh, input và giới hạn. |
| `BUILT` / `SYNTHESIZED` | Chỉ ghi cho đúng firmware/compiler hoặc FPGA/synthesis candidate và log tương ứng. |
| `HARDWARE-VERIFIED` | Có phép thử đúng phần cứng/candidate, điều kiện, log và kết quả. |
| `BLOCKED` / `NOT RUN` | Chưa thực hiện; nêu blocker hoặc lý do. Không dùng như kết quả đạt. |

Tách riêng **Requirement** (phải đáp ứng), **Decision** (đã chốt), **Assumption** (giả định cần xác nhận), **Proposal** (đề xuất) và **Open question** (vấn đề Pending). Không gọi giả định là quyết định.

## 4. Bảo toàn thông tin và lịch sử

- Không đổi pinout, baud, packet layout, CRC, IRQ, giao thức phần cứng hoặc linh kiện từ tài liệu biên tập nếu chưa có căn cứ/phê duyệt trong task.
- Report, log, kết quả đo và snapshot có ngày là hồ sơ lịch sử. Không sửa số liệu cũ để phản ánh lần kiểm tra mới; tạo snapshot mới và liên kết report cũ.
- Khi kế hoạch lỗi thời, đánh dấu rõ phạm vi đã superseded và dẫn tài liệu hiện hành; không xóa file hoặc làm mất lịch sử task.
- Khi nguồn hiện tại không thống nhất, để `PENDING`, mô tả mâu thuẫn và yêu cầu quyết định cụ thể. Không tự tạo đường dẫn/report/evidence.

## 5. Kiểm tra biên tập

Trước khi hoàn tất thay đổi tài liệu, kiểm tra cấp tiêu đề, fence code, bảng, sơ đồ Mermaid, link tương đối, tên module/đơn vị/trạng thái và mâu thuẫn với tài liệu nguồn chuẩn. Chạy script tài liệu nếu repository có; ghi rõ lệnh, exit code và giới hạn. `git diff --check` kiểm khoảng trắng, không chứng minh tính đúng kỹ thuật.
