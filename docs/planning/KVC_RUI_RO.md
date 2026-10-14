# KVC — Phân tích quyết định và rủi ro PoC

Cập nhật 14/10/2026 trong KVC-MAINT-20261014-001. Đồng bộ nội dung KVC-DOC-CONSISTENCY-20261014-001: kiến trúc/BOM ở [thiết kế hệ thống](../KVC_ThietKeHeThong.md), nghiệm thu mục VII. Bản thiết kế không còn lịch 21 ngày; ngày/gate bên dưới là lịch sử audit. Tài liệu này phân biệt tiến độ source/kiểm thử với mục tiêu thiết kế. Không có docs/archive trong inventory hiện tại.

## Tiến độ theo bằng chứng

Nguồn trạng thái tổng hợp hiện hành: [KVC_PROJECT_STATUS](../KVC_PROJECT_STATUS.md), task KVC-STATUS-DOC-20261014-001. Baseline Git đã có; AI DATAFIX đã thêm guardrails nhưng hồ sơ release còn BLOCKED. Các số test bên dưới là log lịch sử, không chạy lại trong lượt tài liệu này.

| Phần | Trạng thái có bằng chứng | Chưa thể kết luận |
| --- | --- | --- |
| GCS UI | Có source; 76 unit tests và build baseline PASS | Chưa nghiệm thu browser, cold cache/WAN-off, máy triển khai |
| MOCK backend | FastAPI/state/schema/WS, client queue hữu hạn; tests ứng dụng | Chưa có serial ingress và chuỗi RF/USB |
| SQLite/replay | Có writer riêng, WAL/FULL, commit ticket, overflow/loss, replay/seek/pause và test crash process | Không phải thử mất điện thật; chưa xác minh session rất dài và mọi race control |
| AI PC | Dataset, training/eval reports, adapter và caller scripts có thật | Provenance/QA và metrics chưa đủ để chứng nhận mô hình trên bo |
| FPGA/MCU | Có gói tài liệu/SDK | Không thấy project KVC dạng rời; chưa compiler/synthesis/timing/hardware evidence mới |

Báo cáo và log trước/sau tại [review/KVC-MAINT-20261014-001/REPORT.md](../../review/KVC-MAINT-20261014-001/REPORT.md), Git ignored. Đây là audit source và SELF-REVIEW các bản sửa; không phải approval. Không quy tiến độ thành phần trăm hoặc đánh dấu G0/G1 đạt chỉ từ lịch.

## Ưu tiên P0–P3 và phụ thuộc

| Mức | Công việc | Lý do/ảnh hưởng và đầu vào | Thứ tự/điều kiện hoàn thành |
| --- | --- | --- | --- |
| P0 | Chưa có finding đủ bằng chứng P0 trong audit | Không đồng nghĩa hệ thống an toàn ngoài thực địa | Chỉ nâng P0 khi có hỏng dữ liệu/hành vi nguy hiểm đã chứng minh |
| P1 | Xác minh dữ liệu và evidence AI | Generator đã sửa dry-run/hash thật/UNREVIEWED; manifest cũ và provenance vẫn chưa hợp lệ; reports không chứng minh training lineage | Truy nguồn/license/session/hash, QA người/phao/negative và khóa test trước chọn model/INT8 |
| P1 | Chốt đầu vào G1 và đường tích hợp | Source RTL/MCU/serial chưa có; GoAI/DFP/ABI chưa có bằng chứng kiểm trong audit | A/B/C/D chốt candidate, vectors, toolchain và khả năng AI theo gate; không tự thay wire protocol |
| P1 | Bảo toàn baseline và dữ liệu | Baseline đã có; status/staging hiện tại chưa xác minh vì Git bị chặn | Người dùng kiểm worktree và sao lưu source/data/evidence; AI không tự stage/commit |
| P2 | Serial parser và tích hợp ứng dụng | MOCK không thay hardware ingress | Sau ABI: test chunking/resync/CRC/timeout/session, sau đó chạy loopback hardware và thử mất link |
| P2 | Độ bền/tải và browser/offline | Replay nạp toàn bộ session RAM, seek từ đầu; browser E2E và soak chưa chạy lại | Đo session dài, concurrent controls, WAN-off/cold-cache và phục hồi trước tích hợp thật |
| P2 | Tái lập môi trường AI/kiểm thử | Backend requirements không có runtime AI; scripts có đường dẫn máy và thao tác ghi dữ liệu | Tách environment/lock cho training, guard/dry-run data tooling, chuẩn hóa browser harness |
| P3 | Giảm nợ UI/dependencies | Audit trước dọn ghi 13 module chưa tới entrypoint; KVC-ORGANIZE đã bỏ 12, giữ utils.ts do cấu hình alias. Warnings/bundle size là số đo cũ | Đánh giá lint/bundle lại khi có task phần mềm; không coi module đã xóa vẫn là việc chưa làm |

P1/P2 trong bảng là ưu tiên công việc; phần chưa triển khai không tự được coi là bug. Finding có lỗi/bằng chứng/điều kiện cụ thể nằm trong report audit.

## Roadmap ngắn hạn, giữ lịch chung

1. Ngay sau audit: người dùng kiểm diff/backup và chốt baseline; B/E rà provenance/QA; A/B/C/D ghi evidence hoặc blocker G1. Các bản sửa kiểm thử trong audit không thay quyết định phần cứng.
2. Trong 1–2 ngày làm việc tiếp: sau chốt ABI, D/C chuẩn bị golden vectors và task serial parser nhỏ; D kiểm UI BACKEND/replay trên browser, thêm tải dài/concurrency theo rủi ro. B/E bổ sung provenance/QA/session có thật; generator đã có guardrails, không ghi đè manifest hiện có.
3. Hướng đến G2 18/10: chỉ báo đạt khi có chuỗi FPGA mock UART → MCU → LoRa → GCS chạy 30 phút và dữ liệu QA theo thiết kế. Nếu thiếu bo/toolchain/ABI, ghi BLOCKED và tiếp tục host MOCK có nhãn; không đổi ngày mục tiêu thành kết quả thực tế.

## Nguyên tắc kiến trúc và mức bằng chứng

KVC là payload, không điều khiển bay. LoRa truyền metadata; video tham chiếu là kênh riêng. LOCAL_GRID cm không thay WGS-84. Giữ REAL/MOCK/REPLAY và inference provenance độc lập. Telemetry 20 byte là source lịch sử; RF 32/USB 48 vẫn DESIGN cần C+D xác nhận.

- DESIGN: mục tiêu/spec; không phải số đo.
- SOURCE-VERIFIED: đối chiếu code/config và references.
- SIMULATED: unit tests/mock/host loopback có log; không chứng minh RF/bo.
- BUILT/SYNTHESIZED: ghi riêng build frontend, compiler MCU hoặc synthesis FPGA; không hoán đổi mức này.
- HARDWARE-VERIFIED: cần đúng board/candidate/input/log/điều kiện đo; chưa thực hiện trong audit này.
