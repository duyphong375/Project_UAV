# KVC — Danh mục tài liệu dự án

Rà soát 15/10/2026 (Asia/Saigon), KVC-MD-UNIFY-20261015-001; owner: Codex; SELF-REVIEW, chưa human approval. Các snapshot 14/10 bên dưới vẫn là hồ sơ lịch sử.

Đồng bộ hiện hành gồm baseline thiết kế ESP32 trạm đất độc lập, Wi-Fi SoftAP/WebSocket v1 và Dashboard web/GCS trên laptop. RF payload 32 byte còn là draft; ingress ESP32 chưa được xác minh. Thiết kế mục III chứa chức năng/In/Out cho 29 linh kiện; source UI bám cấu hình và không tự báo chỉ số phần cứng chưa có dữ liệu. Report lịch sử không được sửa thành kết quả mới.

## Bộ tài liệu làm việc

| Tài liệu | Vai trò / nguồn chuẩn | Trạng thái |
| --- | --- | --- |
| [README](../README.md) | Điểm vào dự án, cấu trúc và lệnh chạy | Hướng dẫn software; giới hạn hardware được nêu riêng |
| [Phân công 5 người](planning/KVC_PHAN_CONG_5_NGUOI.md) | Nhiệm vụ chính từng người | Kế hoạch, chưa xác nhận hoàn thành |
| [Checklist 5 người](planning/KVC_CONG_VIEC_CHI_TIET_5_NGUOI.md) | Việc triển khai, kiểm thử và demo | Danh sách việc cần làm |
| [Tiến độ dự án](KVC_PROJECT_STATUS.md) | Tiến độ phân hệ, gates, bằng chứng và công việc còn thiếu | Snapshot 14/10; không phải kết quả đo mới |
| [Chuẩn Markdown](KVC_MARKDOWN_STANDARD.md) | Cấu trúc, trạng thái, liên kết và cách ghi evidence trong tài liệu | Accepted; quy ước biên tập, không phải quyết định kỹ thuật |
| [Thiết kế hệ thống](KVC_ThietKeHeThong.md) | Kiến trúc, BOM mục III, giao thức draft mục IV, nghiệm thu mục VII | OneKiwi V1.1 đã có; camera/bộ nhớ/AI và ABI cần chốt |
| [Phân tích](planning/KVC_RUI_RO.md) | Rủi ro, ưu tiên và phụ thuộc | Phân biệt ưu tiên công việc với bug |
| [Demo](demo/KVC_DEMO.md) | Kịch bản, nhãn nguồn và checklist demo | DESIGN; chưa nghiệm thu phần cứng |
| [Kế hoạch GCS](gcs/KVC_GCS_PLAN.md) | Tài liệu phân rã task GCS lịch sử | Các task USB/STM32 đã superseded; không dùng làm backlog hiện hành |
| [Data contract](gcs/KVC_GCS_DATA_CONTRACT.md) | Semantics JSON ứng dụng và wire draft | Đọc mục semantics source hiện hành; wire chưa duyệt |
| [Thiết kế GCS](gcs/KVC_GCS_DESIGN_SPEC.md) | UI/UX và hành vi mục tiêu | Spec phải đối chiếu frontend hiện có |
| [Đặc tả giao diện](interfaces/README.md) | Ma trận luồng dữ liệu, IF-01 UART, IF-02 LoRa, IF-03 Wi-Fi WS | Quản lý hợp đồng kết nối toàn chuỗi; ABI draft |
| [Backend README](../Dashboard/backend/README.md) | Cài/chạy MOCK, API, SQLite, replay và test | SOURCE-VERIFIED hướng dẫn; không REAL ingress |
| [Frontend README](../Dashboard/frontend/README.md) | LOCAL/BACKEND, Vite và scripts kiểm thử | Source hiện hành; offline/browser cần nghiệm thu |
| [AI data preparation](ai/KVC_AI_DATA_PREPARATION.md) | Ontology, split, manifests và QA | DATA_PROVENANCE_PENDING |
| [AI README](../ai_training/README.md) | Adapter, dataset inventory, generator/validator và giới hạn metrics | PC_REFERENCE; release BLOCKED |
| [OneKiwi/Gowin](hardware/CHIP_ONEKIWI_20K_GOWIN_GW2A.md) | Ghi chú chip/board, tài liệu hãng và SDK | DOCUMENTED; không dùng pin candidate chưa duyệt để đấu nối |
| [SONiX](hardware/CHIP_SONIX_SN34F788_MCU.md) | Ghi chú MCU và tài liệu hãng | DOCUMENTED; project/board mapping/build còn cần xác minh |
| [Bản đồ chân Master](hardware/KVC_MASTER_PINOUT_WIRING.md) | Bản đồ phân bổ chân và đấu nối toàn hệ thống KVC | BASELINE RELEASE; chuẩn đấu nối cảm biến (AJ-SR04M, GY-87 I2C0, GNSS u-blox M10 / NEO-M10N), MCU, LoRa, ESP32 và FPGA |
| [Workflow AI](KVC_AI_WORKFLOW.md) | Task/owner/test/review/handoff | Quy tắc hiện hành ở đầu; setup 11/10 là lịch sử |
| [AGENTS](../AGENTS.md) | Quy tắc chung và quyền sửa | Nguồn quy tắc AI chính |
| [Adapter Antigravity](../.agents/rules/kvc.md) | Trỏ IDE về AGENTS | Không tạo bộ policy độc lập |

## Tài liệu hỗ trợ và hồ sơ lịch sử

| Tài liệu | Vai trò / người đọc | Quan hệ và trạng thái |
| --- | --- | --- |
| [README backend](../Dashboard/backend/README.md) | Lập trình viên GCS backend | Hướng dẫn source MOCK/logger/replay hiện có; ingress ESP32 chưa triển khai |
| [README frontend](../Dashboard/frontend/README.md) | Lập trình viên GCS frontend | Lệnh chạy/test và giới hạn UI; theo contract và kiến trúc |
| [README AI](../ai_training/README.md) | Người phụ trách dữ liệu/model AI | Mô tả adapter, dataset, scripts và giới hạn PC_REFERENCE |
| [README scripts](../scripts/README.md) | Người chạy tooling dự án | Danh mục script; phải đọc tác dụng trước khi chạy |
| [README FPGA](../fpga/README.md) | Người phụ trách OneKiwi/FPGA | Ghi chú phân hệ, interface và ràng buộc chân Header J2 (`pins.cst`); camera/RTL chưa xác minh |
| [README MCU](../firmware/mcu_uav/README.md) | Người phụ trách MCU tải | Ghi chú toolchain, interface và header chân chuẩn (`kvc_pinout.h`); RF ABI còn draft |
| [README Gateway](../firmware/gateway_esp32/README.md) | Người phụ trách ESP32-C3 | Cấu hình PlatformIO, transport mục tiêu và mã nguồn (`main.cpp`) đồng bộ chân SPI LoRa |
| [README weights AI](../ai_training/weights/README.md) | Người quản lý checkpoint AI cục bộ | Chính sách giữ và giới hạn evidence của weights |
| [Báo cáo eval 2 lớp](../ai_training/runs/eval_2class_hardware/EVAL_REPORT.md) | Nhóm AI/reviewer | Kết quả lịch sử theo chính candidate trong báo cáo; không phải bằng chứng FPGA |
| [Báo cáo eval boosted](../ai_training/runs/eval_boosted/EVAL_REPORT_BOOSTED.md) | Nhóm AI/reviewer | Kết quả lịch sử; không ghi đè bằng metric mới |
| [Báo cáo eval demo](../ai_training/runs/eval_demo1_boosted/EVAL_REPORT_DEMO1.md) | Nhóm AI/reviewer | Kết quả lịch sử của candidate demo; xem provenance riêng |
| [Báo cáo đồng bộ 80 epoch](../ai_training/runs/yolo11n_rtx4060_80ep/SYNC_80EP_REPORT.md) | Nhóm AI/reviewer | Hồ sơ train/eval PC lịch sử; không chứng nhận chạy trên FPGA |
| [README docs](README.md) | Tất cả thành viên | Điểm vào và nhóm tài liệu; liên kết tới index này |

## Quy tắc giữ tài liệu bám sát thực tế

- Tiến độ cập nhật vào KVC_PROJECT_STATUS; kiến trúc/BOM/nghiệm thu trong KVC_ThietKeHeThong. Bản thiết kế hiện tại không chứa lịch 21 ngày; ngày G0–G5 trong các file cũ chỉ để tra lịch sử. Công việc hiện hành theo checklist 5 người, không tự đặt lịch mới.
- Từng claim hoàn thành cần candidate/version/hash, lệnh, exit code, log và mức bằng chứng. Nêu tests lịch sử nếu chưa chạy lại; không dùng lịch để ghi gate PASS.
- RF payload 32 byte vẫn DESIGN/PENDING duyệt ABI; giao diện ESP32–laptop Wi-Fi SoftAP/WebSocket v1 là baseline thiết kế nhưng chưa triển khai/xác minh. Telemetry 20 byte là ghi nhận source lịch sử; parser hiện tại chưa có. USB Ground Envelope 48 byte là DEPRECATED cho kiến trúc mục tiêu. Không tự đổi hardware protocol để khớp tài liệu/UI.
- OneKiwi V1.1 được xác nhận cùng mẫu; pinout/camera/DDR chưa được duyệt cho KVC. Thiết kế Tang/DVP cũ không phải wiring chuẩn của board hiện tại.
- Reports trong review là snapshot lịch sử, không sửa lại để làm sai evidence. Tài liệu mới liên kết report và mô tả phần đã FIXED/BLOCKED.
- Task plan là đề xuất; khi triển khai phải lập manifest owner/allowed files/acceptance/tests/status cho đúng source hiện tại. Self-review và tests PASS không phải approval.

## Gói tải lại lịch sử

Lượt xuất trước ghi nhận outputs/KVC_MD_20261014.zip; file này không có trong inventory ngày 14/10/2026 khi sắp xếp KVC-ORGANIZE-20261014-001. Nội dung dưới đây mô tả lượt xuất lịch sử, với đường dẫn tương đối của tài liệu bên trong. Thư mục giải nén outputs/KVC_MD_20261014 đã được dọn trong KVC-CLEAN-20261014-002 sau khi đối chiếu đủ 30 file với ZIP. MANIFEST.json bên trong ZIP ghi SHA-256 cho từng file xuất. Chỉ đóng gói Markdown chuẩn và evidence tổng quan được chọn; không chứa source ứng dụng, weights, datasets, SDK, PDF, secrets hoặc build artifacts. Các link tới source/media/SDK/log ngoài gói cần workspace gốc; không coi gói Markdown là bộ cài phần mềm hoặc backup dữ liệu.

Kiểm chứng lượt xuất và các lệnh NOT RUN nằm tại [TEST_RESULTS](../review/KVC-STATUS-DOC-20261014-001/TEST_RESULTS.md). Không upload tới Page/Space hoặc dịch vụ ngoài; gói được cung cấp trực tiếp để tải từ workspace.
