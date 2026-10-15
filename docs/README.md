# Tài liệu dự án KVC

## Đọc nhanh

1. [Tiến độ dự án](KVC_PROJECT_STATUS.md): phần đã có và phần còn thiếu.
2. [Phân công 5 người](planning/KVC_PHAN_CONG_5_NGUOI.md): nhiệm vụ chính.
3. [Checklist chi tiết](planning/KVC_CONG_VIEC_CHI_TIET_5_NGUOI.md): việc cần làm để hoàn thiện.
4. [Thiết kế hệ thống](KVC_ThietKeHeThong.md): kiến trúc, bảng 29 linh kiện kèm chức năng/In/Out, giao thức dự thảo và tiêu chí đo.
5. [Kịch bản demo](demo/KVC_DEMO.md): hai video và thử trực tiếp không sa bàn.
6. [Chuẩn Markdown](KVC_MARKDOWN_STANDARD.md): quy tắc cấu trúc, thuật ngữ, trạng thái và tham chiếu.

## Các nhóm tài liệu

| Thư mục/file | Nội dung |
| --- | --- |
| planning/ | Phân công, checklist, backlog kỹ thuật và phân tích rủi ro |
| demo/ | Kịch bản trình diễn hiện hành |
| gcs/ | Kế hoạch, dữ liệu và thiết kế Dashboard |
| ai/ | Chuẩn bị và kiểm dữ liệu AI |
| hardware/ | Hồ sơ bo/chip, datasheet, tài liệu và SDK hãng |
| KVC_AI_WORKFLOW.md | Quy trình task, kiểm thử và review |
| KVC_DOCUMENT_INDEX.md | Danh mục đầy đủ và vai trò từng tài liệu |
| KVC_MARKDOWN_STANDARD.md | Chuẩn biên tập dùng chung cho tài liệu Markdown |

Thiết kế là mục tiêu. Bản thiết kế hiện tại không chứa lịch 21 ngày; mốc cũ trong backlog/GCS chỉ là lịch sử. Kết quả đã làm theo báo cáo tiến độ và log kiểm tra; không suy ra phần cứng đã chạy từ tài liệu.

Kiến trúc GCS hiện hành là LoRa → ESP32 trạm đất có nguồn riêng → Wi-Fi SoftAP/WebSocket → backend GCS trên laptop → Dashboard web. ESP32 không phụ thuộc laptop để nhận LoRa. RF 32 byte còn là dự thảo; giao diện Wi-Fi là baseline thiết kế chưa xác minh. Tài liệu GCS cũ ghi STM32/USB cần được đọc theo nhãn lịch sử/superseded trong chính tài liệu.
