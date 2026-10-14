# KVC — Danh mục tài liệu chuẩn

Cập nhật 14/10/2026 (Asia/Saigon), KVC-DOC-CONSISTENCY-20261014-001; kế thừa snapshot KVC-STATUS-DOC-20261014-001. Owner: Codex; SELF-REVIEW, chưa human approval.

Đồng bộ hiện hành: **KVC-PROJECT-SYNC-CLEAN-20261014-001**. Thiết kế mục III chứa chức năng/In/Out cho 29 linh kiện; source UI bám cấu hình và không tự báo chỉ số phần cứng chưa có dữ liệu. Report lịch sử không được sửa thành kết quả mới.

## Bộ tài liệu làm việc

| Tài liệu | Vai trò / nguồn chuẩn | Trạng thái |
| --- | --- | --- |
| [README](../README.md) | Điểm vào dự án, cấu trúc và lệnh chạy | Hướng dẫn software; giới hạn hardware được nêu riêng |
| [Phân công 5 người](planning/KVC_PHAN_CONG_5_NGUOI.md) | Nhiệm vụ chính từng người | Kế hoạch, chưa xác nhận hoàn thành |
| [Checklist 5 người](planning/KVC_CONG_VIEC_CHI_TIET_5_NGUOI.md) | Việc triển khai, kiểm thử và demo | Danh sách việc cần làm |
| [Backlog kỹ thuật](planning/KVC_TODO_FROM_NOW.md) | Tham khảo task và phụ thuộc kỹ thuật | Vai A–E/kịch bản cũ phải đối chiếu kế hoạch hiện hành |
| [Tiến độ dự án](KVC_PROJECT_STATUS.md) | Tiến độ phân hệ, gates, bằng chứng và công việc còn thiếu | Snapshot 14/10; không phải kết quả đo mới |
| [Thiết kế hệ thống](KVC_ThietKeHeThong.md) | Kiến trúc, BOM mục III, giao thức draft mục IV, nghiệm thu mục VII | OneKiwi V1.1 đã có; camera/bộ nhớ/AI và ABI cần chốt |
| [Phân tích](planning/KVC_RUI_RO.md) | Rủi ro, ưu tiên và phụ thuộc | Phân biệt ưu tiên công việc với bug |
| [Demo](demo/KVC_DEMO.md) | Kịch bản, nhãn nguồn và checklist demo | DESIGN; chưa nghiệm thu phần cứng |
| [Kế hoạch GCS](gcs/KVC_GCS_PLAN.md) | Phân rã task D và acceptance dự kiến | Có implementation từng phần; không mặc định DONE |
| [Data contract](gcs/KVC_GCS_DATA_CONTRACT.md) | Semantics JSON ứng dụng và wire draft | Đọc mục semantics source hiện hành; wire chưa duyệt |
| [Thiết kế GCS](gcs/KVC_GCS_DESIGN_SPEC.md) | UI/UX và hành vi mục tiêu | Spec phải đối chiếu frontend hiện có |
| [Backend README](../Dashboard/backend/README.md) | Cài/chạy MOCK, API, SQLite, replay và test | SOURCE-VERIFIED hướng dẫn; không REAL ingress |
| [Frontend README](../Dashboard/frontend/README.md) | LOCAL/BACKEND, Vite và scripts kiểm thử | Source hiện hành; offline/browser cần nghiệm thu |
| [AI data preparation](ai/KVC_AI_DATA_PREPARATION.md) | Ontology, split, manifests và QA | DATA_PROVENANCE_PENDING |
| [AI README](../ai_training/README.md) | Adapter, dataset inventory, generator/validator và giới hạn metrics | PC_REFERENCE; release BLOCKED |
| [OneKiwi/Gowin](hardware/CHIP_ONEKIWI_20K_GOWIN_GW2A.md) | Ghi chú chip/board, tài liệu hãng và SDK | DOCUMENTED; không dùng pin candidate chưa duyệt để đấu nối |
| [SONiX](hardware/CHIP_SONIX_SN34F788_MCU.md) | Ghi chú MCU và tài liệu hãng | DOCUMENTED; project/board mapping/build còn cần xác minh |

## Quy tắc giữ tài liệu bám sát thực tế

- Tiến độ cập nhật vào KVC_PROJECT_STATUS; kiến trúc/BOM/nghiệm thu trong KVC_ThietKeHeThong. Bản thiết kế hiện tại không chứa lịch 21 ngày; ngày G0–G5 trong các file cũ chỉ để tra lịch sử. Công việc hiện hành theo checklist 5 người, không tự đặt lịch mới.
- Từng claim hoàn thành cần candidate/version/hash, lệnh, exit code, log và mức bằng chứng. Nêu tests lịch sử nếu chưa chạy lại; không dùng lịch để ghi gate PASS.
- RF32/USB48 vẫn DESIGN; ghi nhận telemetry20 là lịch sử, parser hiện tại chưa có. Không tự đổi hardware protocol để khớp tài liệu/UI.
- OneKiwi V1.1 được xác nhận cùng mẫu; pinout/camera/DDR chưa được duyệt cho KVC. Thiết kế Tang/DVP cũ không phải wiring chuẩn của board hiện tại.
- Reports trong review là snapshot lịch sử, không sửa lại để làm sai evidence. Tài liệu mới liên kết report và mô tả phần đã FIXED/BLOCKED.
- Task plan là đề xuất; khi triển khai phải lập manifest owner/allowed files/acceptance/tests/status cho đúng source hiện tại. Self-review và tests PASS không phải approval.

## Gói tải lại lịch sử

Lượt xuất trước ghi nhận outputs/KVC_MD_20261014.zip; file này không có trong inventory ngày 14/10/2026 khi sắp xếp KVC-ORGANIZE-20261014-001. Nội dung dưới đây mô tả lượt xuất lịch sử, với đường dẫn tương đối của tài liệu bên trong. Thư mục giải nén outputs/KVC_MD_20261014 đã được dọn trong KVC-CLEAN-20261014-002 sau khi đối chiếu đủ 30 file với ZIP. MANIFEST.json bên trong ZIP ghi SHA-256 cho từng file xuất. Chỉ đóng gói Markdown chuẩn và evidence tổng quan được chọn; không chứa source ứng dụng, weights, datasets, SDK, PDF, secrets hoặc build artifacts. Các link tới source/media/SDK/log ngoài gói cần workspace gốc; không coi gói Markdown là bộ cài phần mềm hoặc backup dữ liệu.

Kiểm chứng lượt xuất và các lệnh NOT RUN nằm tại [TEST_RESULTS](../review/KVC-STATUS-DOC-20261014-001/TEST_RESULTS.md). Không upload tới Page/Space hoặc dịch vụ ngoài; gói được cung cấp trực tiếp để tải từ workspace.
