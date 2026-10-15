# KVC — Tiến độ dự án theo bằng chứng

Cập nhật **14/10/2026, Asia/Saigon**. Task: **KVC-STATUS-DOC-20261014-001**; owner tài liệu: Codex. Source author: **AUTHOR UNKNOWN**; tài liệu này **SELF-REVIEW**, chưa human approval. Đây là đánh giá tổng quan source/tài liệu/log, không phải review chi tiết toàn bộ code hoặc chứng nhận an toàn.

> Đồng bộ nội dung trong **KVC-DOC-CONSISTENCY-20261014-001**, owner Codex, 14/10/2026. Các kết quả test phía dưới là lịch sử; lượt này đối chiếu source/tài liệu và sửa Markdown, chưa chạy phần cứng. Xem [báo cáo cập nhật](../review/KVC-DOC-CONSISTENCY-20261014-001/REPORT.md).

> **Cập nhật kiến trúc 15/10/2026:** Thiết kế hiện hành chọn ESP32-WROOM-32D trạm đất có nguồn riêng, Wi-Fi SoftAP/WebSocket tới dịch vụ GCS trên laptop và Dashboard web trong browser. Snapshot/status, test và log bên dưới giữ nguyên mốc 14/10; các chỗ ghi USB/CP2102 hoặc STM32 là lịch sử, không phải cấu hình mục tiêu mới. RF 32 byte vẫn draft; transport Wi-Fi chưa được xác minh trên thiết bị.

## Kết luận hiện tại

**KVC đã có nền tảng phần mềm GCS và AI tham chiếu PC; chưa có bằng chứng hoàn thành payload FPGA–MCU–LoRa–GCS trên phần cứng.** Phần mềm MOCK đã đi xa hơn skeleton, nhưng chưa thay thế serial ingress, định vị bằng cảm biến thật hoặc AI chạy trên FPGA. Không có cơ sở quy toàn dự án thành một tỷ lệ phần trăm.

KVC là tải nhiệm vụ tìm kiếm cứu nạn bão lũ, không phải flight controller. Lịch và KPI ở [thiết kế hệ thống](KVC_ThietKeHeThong.md) là mục tiêu DESIGN. Báo cáo này là nguồn trạng thái tổng hợp; bản thiết kế vẫn là nguồn kiến trúc và lịch.

**Mô hình đã chốt về lựa chọn:** YOLO11n, detection person/lifebuoy. Script/run/template có tên yolo11n; chưa kiểm metadata/graph mọi checkpoint, chưa train lại hoặc xác nhận chạy FPGA trong lượt đồng nhất.

Cập nhật UI trong **KVC-PROJECT-SYNC-CLEAN-20261014-001**: tên thiết bị bám BOM; GNSS/DOP/pin/AI throughput thiếu dữ liệu để N/A, bỏ thông báo lệnh gimbal/eco/ping giả. Đây là sửa nguồn/hiển thị, chưa nghiệm thu runtime hoặc phần cứng. Bảng linh kiện thiết kế đã có chức năng/In/Out.

## Ma trận thực hiện

| Phân hệ | Đã có | Mức bằng chứng hiện có | Còn thiếu để tích hợp/nghiệm thu |
| --- | --- | --- | --- |
| GCS frontend | React/TypeScript/Vite; radar local, bản đồ, cảnh báo, MOCK; adapter/reducer, HTTP/WS và UI replay | SOURCE-VERIFIED; log lịch sử 76 tests và build exit 0 | Browser E2E đúng candidate, offline cold-cache, soak và máy demo sạch |
| Backend GCS | FastAPI loopback; schema/state; MOCK, client queues hữu hạn; API trạng thái/sessions/replay | SOURCE-VERIFIED; SIMULATED theo tests/log lịch sử | ESP32 Wi-Fi/WebSocket ingress, RF decoder, capture thật và reconnect thiết bị |
| SQLite/replay | Logger, WAL/FULL, commit boundary, session replay/seek/pause; tests recovery | SOURCE-VERIFIED; SIMULATED trong log | Phiên dài, tải/concurrent controls; mất điện thật chưa được thử |
| AI tham chiếu PC | Adapter person/lifebuoy, caller video/webcam, dataset, checkpoints và reports | SOURCE-VERIFIED; adapter test bằng dữ liệu giả | Provenance/license, QA có evidence, locked-test, calibration và metrics tái lập trên candidate |
| AI evidence tooling | Generator mặc định dry-run/hash thật, validator chỉ đọc và fixture tests | SOURCE-VERIFIED; SIMULATED trong báo cáo DATAFIX | Manifest cũ chưa được chữa bằng dữ liệu thật; validator ghi 335 issues ở lần chạy đã lưu |
| FPGA KVC | Hồ sơ OneKiwi/Gowin, SDK/tài liệu hãng; người dùng xác nhận cùng mẫu Kiwi Primer 20K V1.1 | DOCUMENTED / HUMAN-CONFIRMED, chưa hardware verified | Project/top-level KVC, RTL/testbench/constraints, camera bring-up, DDR/IP, synthesis/timing, khả năng GoAI |
| MCU KVC | Tài liệu SONiX/SDK và kế hoạch UART/cảm biến/LoRa | DOCUMENTED / DESIGN | Project đúng chip/board, pin mux, compiler/build, ISR/DMA/ring, cảm biến, georef và RF thử trên bo |
| Chuỗi REAL | Kiến trúc, application JSON, draft RF32/UART và baseline ESP32 Wi-Fi/WebSocket | DESIGN; ingress chưa xác minh | C+D duyệt RF ABI/pinout/golden vectors; FPGA→MCU→LoRa→ESP32→Wi-Fi/WebSocket→GCS có log đối chiếu |
| Quản lý dự án | AGENTS, adapter Antigravity, review workflow, Git baseline | SOURCE-VERIFIED tài liệu và metadata Git | Kiểm worktree/staging bằng Git; nghiệm thu task, sao lưu evidence/data; không coi test PASS là approval |

Phạm vi inventory chỉ xác nhận source KVC dạng rời được thấy trong workspace. Source mẫu bên trong SDK không phải implementation payload đã tích hợp; không kết luận công việc trên máy/bo ngoài workspace chưa tồn tại.

## G0–G5: các mốc của kế hoạch trước và tình trạng bằng chứng

| Gate lịch sử | Ngày trong kế hoạch cũ 2026 | Tình trạng đánh giá | Bằng chứng còn cần |
| --- | --- | --- | --- |
| G0 | 12/10 | CHƯA XÁC NHẬN ĐẠT | Inventory/toolchain/license/candidate và baseline AI đầy đủ, biên bản chấp thuận |
| G1 | 14/10 | BLOCKED cho tổng thể | Chốt camera/board/điện/pinout, khả năng AI và ABI; chưa có bằng chứng tensor/ảnh chạy FPGA; UI source không tự chứng minh offline |
| G2 | 18/10 | CHƯA NGHIỆM THU; phần MOCK ứng dụng đã có | Chuỗi theo gate hệ thống chạy 30 phút, log/replay/fault và dữ liệu QA; smoke 6 giây không thay bài 30 phút |
| G3 | 22/10 | CHƯA CÓ BẰNG CHỨNG REAL | Dongle, serial parser, dữ liệu đo RSSI/SNR, validity/session/clock và hiển thị/log từ hardware |
| G4 | 25/10 | CHƯA CÓ BẰNG CHỨNG ĐẠT | 10.000 frame, soak 2 giờ, phục hồi, resource/timing/đo chỉ tiêu và feature freeze |
| G5 | 01/11 | CHƯA CÓ BẰNG CHỨNG ĐẠT | Laptop sạch offline, 5 lượt demo, tài liệu vận hành, bộ bàn giao và backup evidence |

Bản thiết kế hiện tại không còn lịch 21 ngày; bảng G0–G5 giữ để tra kế hoạch cũ, không phải lịch mới được xác nhận. Tiêu chí nghiệm thu hiện hành ở mục VII thiết kế; thứ tự công việc theo [checklist 5 người](planning/KVC_CONG_VIEC_CHI_TIET_5_NGUOI.md). Gate con GCS trong [kế hoạch GCS](gcs/KVC_GCS_PLAN.md) cũng cần đối chiếu phạm vi hiện hành. Các task PROPOSED trong kế hoạch là mẫu phân rã; không dùng trạng thái ban đầu đó thay kết quả source/test mới, và không tự ghi DONE khi thiếu acceptance.

## Những điểm chặn cần quyết định

1. **Board/camera:** nhóm xác nhận đang có OneKiwi Primer 20K V1.1; thiết kế/BOM đã thống nhất dùng bo này, mua thêm 0. Camera/cáp và RX pipeline chưa chốt; không mặc định DVP 24 chân hoặc HDMI cắm là chạy.
2. **Điện và nối FPGA–SONiX:** UART, DATA_READY/IRQ, reset, VCCIO/I/O standard và mapping hai board chưa có phê duyệt đủ dùng. Không còn lấy 128/512 MB làm cấu hình chắc chắn: DDR3 fitted part/density/map và controller chưa được xác minh trên bo. Manual cũng có số Flash không thống nhất; cần đối chiếu revision và mã chip. Các chi tiết này là câu hỏi tích hợp, chưa phải phép đo.
3. **Wire ABI:** RF32 vẫn là draft chưa duyệt; USB48 thuộc kiến trúc cũ. Wi-Fi SoftAP/WebSocket v1 là baseline thiết kế chưa có REAL ingress. Parser telemetry20 không có trong đường ingress hiện tại. UART FPGA có đặc tả riêng, không phải gói telemetry20. Chốt endian/CRC/framing/wrap/session/timeout/status rồi tạo golden vectors C/Python. Giữ nguyên baud/layout/CRC/IRQ/pinout khi chưa được giao thay đổi.
4. **AI release:** guardrails đã sửa cách tạo/kiểm evidence, nhưng không làm dữ liệu release-ready. Cần nguồn/license/consent, session có hash, QA độc lập, test khóa theo phiên và calibration hợp lệ. Không công bố INT8/FPS/GoAI support từ metrics PC hoặc tên file weights.

Nguồn: [ABI report](../review/KVC-G1-ABI-20261014-001/REPORT.md), [hardware report](../review/KVC-G1-HW-DOC-20261014-003/REPORT.md), [AI fix report](../review/KVC-AI-DATAFIX-20261014-001/REPORT.md). Các report là snapshot lịch sử trong review bị Git ignore; vị trí/line của report có thể khác source mới.

## Kiểm thử: lịch sử và lượt đánh giá này

| Lệnh / bằng chứng đã lưu | Exit đã ghi | Kết quả lịch sử và giới hạn |
| --- | --- | --- |
| .venv/Scripts/python.exe -B -m pytest Dashboard/backend/tests tests -q -p no:cacheprovider | 0 | Audit/cleanup: 39 tests + 8 subtests; trước các tests AI tooling mới, không coi là tổng test hiện tại |
| .venv/Scripts/python.exe -B -m Dashboard.backend.tests.test_api_websocket | 0 | Audit: host TCP smoke 6 giây; không phần cứng, không soak |
| npm test (Dashboard/frontend) | 0 | Audit/cleanup: 14 files, 76 tests |
| npm run typecheck; npm run build | 0 | Frontend audit/cleanup; build UI không phải synthesis FPGA |
| npm run lint | 0 | Audit: 8 warnings; không gọi là zero-warning |
| python scripts/data/validate_ai_evidence.py | 1 | DATAFIX: AI_EVIDENCE_BLOCKED, 335 issues; thiếu evidence thật, không phải dataset PASS |

Log gốc: [audit TEST_RESULTS](../review/KVC-MAINT-20261014-001/TEST_RESULTS.json), [cleanup report](../review/KVC-CLEAN-20261014-001/REPORT.md), [DATAFIX commands](../review/KVC-AI-DATAFIX-20261014-001/commands.log).

**Lượt tổng hợp KVC-STATUS-DOC-20261014-001:** dry-run review, git diff --check, git diff --cached --check và git status đã thử gọi nhưng process creation bị chặn (EPERM/Access denied); **NOT RUN, exit N/A**. Không gọi AI CLI review. Không chạy lại pytest/npm/validator, browser, compiler, synthesis, camera, model hoặc hardware. Chỉ kiểm tài liệu, existence, links, hashes bằng Node; kết quả chi tiết ở [TEST_RESULTS](../review/KVC-STATUS-DOC-20261014-001/TEST_RESULTS.md). Không dùng kiểm text thay Git/compiler/testbench.

Lượt đồng bộ Markdown KVC-DOC-CONSISTENCY-20261014-001 đã sửa sai điện áp VDD trong ghi chú Sonix và các khẳng định phần cứng/phần mềm chưa có bằng chứng. Đây là sửa nội dung tài liệu, không phải xác nhận đã xử lý phần cứng hay thay source. Kết quả kiểm links/nội dung và giới hạn Git ghi trong report riêng ở đầu file.

## Baseline và thứ tự tiếp tục

Đọc trực tiếp .git/HEAD và refs/heads/main cho thấy nhánh main có HEAD **0666e4e389571a62bbb7185b6b9b116d53bed7e8**. Reflog ghi baseline trước đó **4464266c5f38d1cd0ace55c200953dba9db26879**. Vì Git không chạy được, chưa xác minh clean/dirty, staging hoặc nội dung commit; không ghi toàn bộ source vẫn untracked. Không suy tác giả module từ commit baseline.

- **Trước tích hợp:** A/C chốt board/camera/pinout/toolchain; B/E cung cấp AI evidence; C/D chốt ABI và golden vectors. Mỗi công việc cần task có một owner, files literal, acceptance và tests.
- **GCS:** tiếp tục frontend/backend có sẵn; hoàn thiện ingress sau ABI, kiểm chunking/resync/CRC/timeout/disconnect; sau đó browser BACKEND/log/replay và phiên 30 phút.
- **FPGA/MCU:** tạo hoặc bàn giao project KVC đúng board; build/testbench trước, đo bring-up và hardware loopback sau. Quyết định GoAI/fallback dựa compiler/resource/timing và mẫu chạy thật.
- **Nghiệm thu:** đo chain REAL, tọa độ và validity; stress/soak/offline; tổng duyệt và bàn giao. Giữ nhãn MOCK/PC_REFERENCE cho mọi phần chưa đo trên bo.

Không phát hành finding P0/P1/P2 code mới trong lượt tổng quan KVC-STATUS-DOC-20261014-001: dry-run và runtime chưa chạy, chưa review đầy đủ module nhỏ. Các blocker là việc chưa được xác minh hoặc chưa triển khai. Không có finding mới không có nghĩa hệ thống đã an toàn.
