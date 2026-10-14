> **Backlog kỹ thuật tham khảo.** Phân công theo tên và checklist đang dùng ở [phân công](KVC_PHAN_CONG_5_NGUOI.md) và [công việc chi tiết](KVC_CONG_VIEC_CHI_TIET_5_NGUOI.md). Các vai A–E/kịch bản sa bàn trong backlog này là nội dung cũ; demo hiện hành theo [kịch bản demo](../demo/KVC_DEMO.md).

# KVC — Backlog kỹ thuật tham khảo từ kế hoạch trước

**Mốc lập: 14/10/2026, Asia/Saigon.** Task tài liệu: KVC-TODO-DOC-20261014-001. Owner tài liệu: Codex; SELF-REVIEW, chưa human approval. Mọi việc dưới đây là **PROPOSED**, trừ chỗ ghi rõ chờ đầu vào. Tài liệu này lập backlog, không tự giao triển khai, flash hoặc duyệt thay đổi phần cứng.

Nguồn: [tiến độ hiện tại](../KVC_PROJECT_STATUS.md), [thiết kế/lịch hệ thống](../KVC_ThietKeHeThong.md), [kế hoạch GCS](../gcs/KVC_GCS_PLAN.md), [contract](../gcs/KVC_GCS_DATA_CONTRACT.md), [dữ liệu AI](../ai/KVC_AI_DATA_PREPARATION.md).

## 1. Điểm xuất phát và cách dùng

- GCS đã có frontend, backend MOCK, SQLite và replay. Tiếp tục source hiện tại; không tạo lại dashboard hoặc logger từ đầu.
- AI có adapter, dữ liệu và reports PC. Generator/validator đã có guardrails, nhưng evidence release còn BLOCKED; 335 issues là kết quả lần chạy cũ, cần kiểm lại candidate hiện tại.
- Chưa có bằng chứng project RTL/firmware KVC dạng rời đã build hoặc chuỗi FPGA–MCU–LoRa–USB–GCS đã chạy. SDK mẫu không thay implementation KVC.
- OneKiwi V1.1 đã được người dùng xác nhận cùng mẫu; camera, DDR3, nối SONiX, VCCIO/reset/IRQ chưa được chốt đủ dùng. Không dùng pinout Tang/DVP trong thiết kế cũ để đấu nối OneKiwi.
- RF32/USB48 và UART FPGA là DESIGN; ABI chưa được duyệt. Parser telemetry20 cũ không có trong ingress hiện tại; không tự dựng lại layout từ ghi nhận lịch sử.
- Không giả định tất cả linh kiện đều thiếu. Từng việc hardware được mở khi **chính các linh kiện và đầu vào của việc đó** đã có, không đợi đủ toàn bộ bộ kit.

**Ưu tiên công việc:** ƯT1 = làm trước để gỡ điểm chặn/đường tích hợp; ƯT2 = hoàn thiện khả năng kiểm thử và tích hợp; ƯT3 = tối ưu/hoàn thiện sau khi chuỗi cơ bản ổn. Đây không phải severity P0/P1/P2 của finding code.

**Phân vai theo thiết kế:** A = FPGA/RTL; B = AI; C = MCU; D = GCS; E = thực nghiệm/cơ khí/QA. Cột phụ trách là người chịu trách nhiệm đầu ra. Writer triển khai vẫn phải chọn **đúng một Codex hoặc Antigravity** cho từng task; chưa chọn thì chưa có quyền sửa source.

**Mỗi việc khi mở task:** ghi owner, allowed files literal, acceptance, lệnh test và status. Các đường dẫn dưới đây là phạm vi dự kiến để lập task, không phải quyền sửa tự động; file hardware mới chỉ được đặt tên sau khi chốt project. Không cho hai writer cùng sửa file. Cùng một ID GCS cũ phải giữ lịch sử review khi tiếp tục; ID TODO chỉ là ID dòng backlog, không reset quota review.

## 2. Thứ tự ưu tiên tổng hợp

| Đợt | Việc cần tập trung | Điều kiện bắt đầu / kết quả cần có |
| --- | --- | --- |
| Làm ngay | N01–N04: inventory/đầu vào, toolchain, ABI; N05: AI evidence; N08: hồi quy software | Không cần chờ đủ linh kiện. Những quyết định chưa rõ được ghi blocker và người giải quyết |
| Tiếp theo, làm song song | N06–N07 AI; N09–N10 GCS; N11–N13 host/RTL; N14 sa bàn | Từng việc phụ thuộc đầu vào riêng; chưa chốt ABI vẫn test application JSON/logic độc lập được |
| Khi từng phần về | H01 tiếp nhận → H02/H03 bring-up; H04/H05 truyền thông; H06/H07 camera/cảm biến | Đúng board, nguồn, mapping và task được duyệt; firmware/RTL đã qua kiểm trên host khi có thể |
| Ghép tối thiểu | H08, sau đó H09 | Ưu tiên metadata/mock BBox chạy hết chuỗi trước; AI FPGA là nhánh cần chứng minh riêng |
| Đo và bàn giao | H10–H12 | Chuỗi ổn, candidate cố định, tiêu chí đo được chốt; sửa lỗi theo task nhỏ |

**Đường phụ thuộc chính:** N01/N02/N03 + N04 → N11/N12/N13 → H02/H03/H04/H05 → H08 → H09/H10 → H11 → H12.

**Nhánh AI:** N05 → N06 → N07, song song với phần truyền thông. H09 cần thêm H06 và bằng chứng khả năng GoAI ở N02/H06; model PC tốt không thay compiler/resource/timing/ảnh chạy trên FPGA.

## 3. Khi chưa có đủ linh kiện: việc có thể thực hiện ngay

### N01 — Kiểm kê linh kiện và đầu vào còn thiếu [ƯT1; phụ trách E]

- [ ] Ghi từng board/module **đã có / đang chờ / chưa đặt / chưa xác định**, model/revision, số lượng, người giữ, thời điểm có thể bàn giao. Phân biệt FPGA, SONiX payload, MCU trạm đất, camera/adapter/cáp, LoRa hai đầu, cảm biến, USB bridge, nguồn và dụng cụ đo theo thiết kế.
- [ ] Thu ảnh marking/connector và tài liệu đúng revision; liệt kê phần đang ở máy/bo khác cần bàn giao source/project/log. Không kết luận thiếu source chỉ từ workspace này.
- **Đầu ra/phạm vi dự kiến:** bảng inventory và blocker trong hồ sơ hardware; chỉ metadata, không credentials/binary trong prompt.
- **Hoàn thành khi:** mỗi mục có người phụ trách và tình trạng rõ; mỗi việc H01–H09 biết đang thiếu gì. **Xác minh:** đối chiếu inventory với vật tư thực có hoặc bằng chứng giao nhận. Chưa có vật tư ghi NOT VERIFIED.
- **Phụ thuộc/song song:** không phụ thuộc; A/C xác nhận kỹ thuật cùng E, B/D vẫn làm N05/N08.

### N02 — Xác minh toolchain và khả năng build trên máy [ƯT1; phụ trách A]

- [ ] Kiểm phiên bản/license/IP Gowin và khả năng chọn đúng FPGA; C kiểm compiler/DFP/project đúng SONiX; B kiểm runtime/export cần dùng. D kiểm Python/Node/lockfile của GCS.
- [ ] Chạy compile/synthesis mẫu tối thiểu trên host nếu có tool/project hợp lệ; lưu lệnh, exit, log, target và resource/timing. Không cần flash để chứng minh build.
- [ ] A+B tạo operator inventory của candidate AI và thử compiler GoAI khi có môi trường; liệt kê supported/unsupported/chưa kiểm. Không suy hỗ trợ từ tên YOLO hoặc SDK tồn tại.
- **Đầu ra/phạm vi:** evidence toolchain và compatibility report; project mẫu mới chỉ trong scope được giao, không sửa SDK hãng.
- **Hoàn thành khi:** mỗi trục có build hợp lệ hoặc blocker cụ thể cùng người gỡ. **Tests:** compiler/export/synthesis phù hợp; thiếu license/tool/project ghi BLOCKED, không PASS.
- **Phụ thuộc/song song:** inventory target N01; có thể bắt đầu kiểm môi trường trước khi vật tư về. Tách A/B/C/D theo file và công cụ, tránh cùng sửa config môi trường.

### N03 — Chốt cấu hình hardware và bản nối dây [ƯT1; phụ trách C, A cung cấp FPGA mapping]

- [ ] Chốt board target OneKiwi/SONiX/trạm đất, camera thực tế và interface. Giải quyết Tang/DVP so với OneKiwi/HDMI; nếu cần adapter, có schematic và mapping đầy đủ.
- [ ] Xác minh bo OneKiwi thực có bộ nhớ ngoài nào, part/density/map và IP/controller; không chọn 128/512 MB từ mô tả cũ.
- [ ] Lập bảng đầu cuối UART TX/RX, DATA_READY, common ground, nguồn, reset; ball → header → chân MCU → peripheral. Xác minh VCCIO, mức điện và I/O standard.
- **Đầu ra/phạm vi:** quyết định kiến trúc, sơ đồ wiring được duyệt và danh sách chỗ chưa xác minh; không tạo constraint từ pin candidate chưa duyệt.
- **Hoàn thành khi:** các giao tiếp sẽ dùng có mapping/direction/điện/reset/handshake được người phụ trách và người dùng chấp thuận; chưa được đo trên bo vẫn ghi DOCUMENTED.
- **Tests:** rà chéo manual/schematic đúng revision; measurement để H01/H02. **Phụ thuộc:** N01; có thể draft khi chưa có linh kiện, phần xác nhận vật lý chờ H01.

### N04 — Khóa ABI và tạo golden vectors [ƯT1; phụ trách C, D xác nhận consumer]

- [ ] Duyệt riêng UART FPGA→MCU, RF payload và USB envelope: fields/offset/size, signedness, scale/sentinel, endian, CRC params/coverage/storage order.
- [ ] Chốt version/type/reserved bits, session/sequence wrap, status/origin cache, timestamp/timeout, CRC-fail policy và DATA_READY/backpressure; giải quyết các câu hỏi trong report ABI.
- [ ] Sau quyết định C+D, tạo fixture version hóa có hash; có gói đúng và sai, min/max/invalid, LOCAL/WGS-84, session mới, wrap và frames bị cắt/nối/rác. Producer C và consumer Python phải đối chiếu cùng byte chuẩn.
- **Đầu ra/phạm vi dự kiến:** contract/decision và fixture ở Dashboard/fixtures theo task; không phụ thuộc duy nhất vector trong review bị ignore.
- **Hoàn thành khi:** biên bản ABI được duyệt và các vector C/Python khớp; chưa có hardware ghi SIMULATED. **Tests:** round-trip byte-for-byte, CRC reference và reject fixtures.
- **Phụ thuộc/song song:** N03 xác định interface; không cần bo để thử vectors. Trong lúc ABI chờ duyệt, D làm N08–N10 trên JSON, C làm N12 logic không gắn wire layout.

### N05 — Khắc phục hồ sơ nguồn dữ liệu và QA [ƯT1; phụ trách B, E cung cấp QA]

- [ ] Chạy validator chỉ đọc trên snapshot hiện tại, gom issue theo nguồn/session/hash/QA/test/calibration; không dùng số 335 cũ thay kết quả mới.
- [ ] Bổ sung nguồn/license/consent và danh sách assets có hash thật; liên kết ảnh với phiên/source. Không tự gán QA_PASSED hoặc tạo URL/evidence giả.
- [ ] E rà ảnh và nhãn person/lifebuoy/negative; ghi reviewer, ngày, version và evidence. B kiểm duplicate theo phiên/frame gần nhau, cân bằng lớp và split leakage.
- **Đầu ra/phạm vi:** manifests và QA evidence, reports; dataset/nhãn chỉ sửa khi task nêu literal files và có backup. Generator đã có guardrails, không viết lại hoặc ghi đè mặc định.
- **Hoàn thành khi:** issue được FIXED bằng evidence thật hoặc có blocker cụ thể; validator exit 0 chỉ khi đủ các yêu cầu, không ép PASS bằng nới validator.
- **Tests:** python scripts/data/validate_ai_evidence.py; hash/pairing/semantic QA. **Phụ thuộc:** không cần hardware; E có thể QA dữ liệu đang có ngay, ảnh sa bàn đúng camera bổ sung sau H07.

### N06 — Khóa train/val/test và calibration [ƯT1; phụ trách B]

- [ ] Tách theo phiên/source để tránh cùng cảnh/frame lọt train/test; chốt test độc lập theo tiêu chí thiết kế và lưu hash trước chọn candidate cuối.
- [ ] Chọn calibration có QA, đại diện điều kiện mục tiêu, đúng preprocessing; không dùng locked-test để tuning/calibration.
- [ ] Ghi version dataset, preprocessing, ontology hai lớp, model IDs và application/wire mapping có trạng thái rõ.
- **Đầu ra/phạm vi:** split/session manifest, calibration manifest, release metadata; không ghi test đã khóa nếu assets chưa đủ.
- **Hoàn thành khi:** test/calibration thực tồn tại, truy nguồn được và được duyệt; thiếu ảnh mục tiêu ghi BLOCKED/PARTIAL, không lấy metrics PC để lấp thiếu dữ liệu.
- **Tests:** validator và kiểm split/hash/session độc lập. **Phụ thuộc:** N05; có thể thiết kế split rules song song QA, chỉ khóa sau QA đủ.

### N07 — Tái lập baseline AI trên PC và chọn candidate [ƯT2; phụ trách B]

- [ ] Ghi environment, config, seed, dataset/checkpoint hash; tái đo precision/recall/mAP riêng person/lifebuoy và negative false positives theo validation protocol.
- [ ] Kiểm adapter original-image/letterbox, confidence/class mapping; vẫn ghi PC_REFERENCE/NOT_TRACKED khi chưa tracker thật.
- [ ] Chạy export/INT8 chỉ khi toolchain và calibration phù hợp; báo cáo candidate riêng, so sánh FP/quantized trên tập được phép. Locked-test chỉ dùng đánh giá cuối theo thiết kế, không lặp để chọn model.
- **Đầu ra/phạm vi:** model card/release candidate và log; weights giữ cục bộ, không nạp vào prompt.
- **Hoàn thành khi:** một candidate tái lập được và compatibility N02 rõ; chưa FPGA ghi chưa HARDWARE-VERIFIED.
- **Tests:** adapter unit/integration bằng fixture; eval có log đúng hash/input. **Phụ thuộc:** N05/N06 cho claims release, N02 cho compiler; có thể kiểm môi trường/adapter trước đó.

### N08 — Chạy lại hồi quy GCS và AI tooling hiện tại [ƯT1; phụ trách D]

- [ ] Kiểm Git status/diff và dependencies trên máy chạy được process; ghi đúng candidate/hash. Không coi số test cũ là số tests hiện tại.
- [ ] Chạy pytest backend/adapter/data tooling; frontend typecheck/lint/test/build; smoke WebSocket không mở camera/serial/model ngoài scope.
- [ ] Ghi lỗi thực có bằng chứng; mở task fix nhỏ theo AGENTS. GCS không cần build lại từ đầu vì dist bị dọn chỉ là output tái tạo.
- **Đầu ra/phạm vi:** logs và test report, chưa tự sửa source trong task chỉ verification.
- **Hoàn thành khi:** lệnh đều có exit/log hoặc blocker; test PASS không thay approval. **Tests:** xem lệnh mục 8.
- **Phụ thuộc/song song:** không cần hardware; B xác minh tooling AI riêng để D không chiếm GPU hoặc sửa cùng tests.

### N09 — Kiểm UI BACKEND, disconnect và offline [ƯT2; phụ trách D]

- [ ] Browser kiểm LOCAL/BACKEND/REPLAY, cảnh báo invalid/stale, null/sentinel, đổi session, disconnect/reconnect và snapshot; không tự fallback LOCAL gây hiểu nhầm nguồn.
- [ ] Chạy cold-cache/WAN-off giữ loopback; radar, fonts/icons cục bộ và log/replay phải hoạt động. Ghi tile/video online là chức năng riêng.
- [ ] Kiểm kích thước màn hình máy demo và manual flows; thu screenshot/log đúng candidate.
- **Đầu ra/phạm vi:** browser test evidence; tiếp tục frontend hiện tại và acceptance KVC-GCS-002/003/005/010, không reset task history.
- **Hoàn thành khi:** checklist browser/offline đã chạy thực; lỗi là finding/fix scope cụ thể. **Tests:** browser E2E/manual cold-cache có điều kiện đo.
- **Phụ thuộc:** N08; không cần bo. Có thể song song N10 nếu backend fixtures/session test tách riêng và không cùng writer files.

### N10 — Độ bền logger/replay và tải host [ƯT2; phụ trách D]

- [ ] MOCK BACKEND chạy 30 phút: ghi session, replay/pause/speed/seek; so sánh state, clocks/provenance và không giữ mục tiêu tương lai sau seek.
- [ ] Thử slow clients/queue overflow/logger fault, crash process và đọc lại committed records; phân biệt crash process với mất điện thật.
- [ ] Chuẩn bị stress 10.000 frame và soak 2 giờ/4 clients theo kế hoạch; JSON application stress thực hiện ngay, binary frame stress chỉ sau N11. Đo RAM/drop/error/time, không chỉ nhìn UI còn mở.
- **Đầu ra/phạm vi:** tests/evidence của KVC-GCS-006/007/008; session test biệt lập, không ghi đè log thật.
- **Hoàn thành khi:** report có tiêu chí, dữ liệu đo và recovery; phiên MOCK host không được gọi G2 hardware chain đạt.
- **Tests:** pytest recovery/replay + harness load/soak. **Phụ thuộc:** N08; wire load phụ thuộc N04/N11, host JSON không cần linh kiện.

### N11 — Implement/test framer và serial ingress trên host [ƯT1 sau ABI; phụ trách D]

- [ ] Tiếp tục task KVC-GCS-004: USB framing/resync → RF parser → queue → application events/state/logger; không đổi schema/wire để vừa UI.
- [ ] Test mọi kiểu chunking, garbage/sync trong payload, CRC/version/len/type sai, timeout, overflow/drop và session/wrap theo ABI duyệt.
- [ ] Serial transport có fake source/recorded bytes để test reconnect/error lifecycle trước khi cắm dongle; không gán RSSI/SNR đo cho MOCK.
- **Đầu ra/phạm vi dự kiến:** serial_ingress/framer/parser và tests/fixtures trong task literal; thư mục đề xuất trong plan không phải source đã có.
- **Hoàn thành khi:** vectors N04 pass, frame sai không đi vào state, queue bounded và diagnostics đúng; mới SIMULATED, hot-plug thật chờ H04/H10.
- **Tests:** pytest golden/chunking/recovery; stress binary. **Phụ thuộc:** N04 duyệt, N08 baseline; làm song song N12/N13 bằng fixture đã khóa, không cùng sửa fixture.

### N12 — Logic firmware độc lập hardware và project MCU [ƯT1; phụ trách C]

- [ ] Sau N02/N03, lập project đúng chip/pack và phân lớp driver/HAL với logic; compile tối thiểu trước hardware.
- [ ] Unit test C trên host cho parser UART, serializer RF/USB, CRC/session/wrap, ring/timeout/recovery; hardware registers chỉ theo tài liệu đúng chip.
- [ ] Thiết kế/test georef local bằng input tổng hợp: ray-plane, unit/cm, sign/axis/rotation, near-parallel/behind-camera, sensor invalid/stale; WGS-84 test tách riêng. Đặt tiêu chí sai số numerical trước chạy.
- **Đầu ra/phạm vi:** firmware payload/trạm đất mới và test fixtures, tên đường dẫn phải chốt trong task; không sửa SDK hoặc pin/IRQ tự chọn.
- **Hoàn thành khi:** compiler/host tests có logs; logic và hardware access tách đủ để test. Không gọi SIMULATED thành sensor verified.
- **Tests:** host unit vectors + compiler MCU, stack/FPU ABI/static diagnostics khi tool hỗ trợ. **Phụ thuộc:** N02/N03; wire theo N04, geometry tổng hợp có thể bắt đầu sớm.

### N13 — RTL UART/FIFO/reset và testbench [ƯT1; phụ trách A]

- [ ] Lập top-level/mock BBox source, UART/FIFO/FSM/reset theo project đã duyệt; CDC/reset/backpressure/DATA_READY chỉ theo semantics chốt.
- [ ] Test reset giữa frame, FIFO empty/full, burst/max candidates, CRC/payload, clock crossings và timeout/handshake; không giả lập độ an toàn CDC bằng một testbench đơn giản.
- [ ] Compile/simulate rồi synthesis/timing/resource trên target; constraints cho clock/I/O chỉ khi N03 đủ dữ liệu và được duyệt.
- **Đầu ra/phạm vi:** RTL/testbench/project/constraints được giao literal; chưa camera/GoAI không ngăn mock UART testbench.
- **Hoàn thành khi:** simulation evidence và build/timing đúng constraints, hoặc blocker rõ; board UART vẫn phải H05 kiểm.
- **Tests:** HDL compiler/testbench, CDC/reset review, synthesis/STA. **Phụ thuộc:** N02/N03/N04; song song N11/N12. Compile module thuần có thể làm trước pin constraints, nhưng không gọi timing sign-off.

### N14 — Chuẩn bị sa bàn, kế hoạch đo và demo [ƯT2; phụ trách E]

- [ ] Thiết kế gá/origin/axis/unit, danh sách 20 điểm chuẩn và cách đo ground truth theo thiết kế; chuẩn bị bảng ghi pose/camera/calibration/error.
- [ ] Chuẩn bị checklist nguồn/nhiệt, log Tx/Rx/session để tính PRR, điều kiện đo cự ly và demo/mất link/recovery; giới hạn từng phép đo cần chốt trước thu dữ liệu.
- [ ] Thu/QA dữ liệu hiện có; ảnh đúng camera/gá thực và calibration chờ H07. Có thể dựng demo MOCK có nhãn ngay.
- **Đầu ra/phạm vi:** test procedures, biểu mẫu measurement và kịch bản; không công bố khoảng cách/sai số/FPS từ mục tiêu thiết kế.
- **Hoàn thành khi:** procedure tái lập, tiêu chí phê duyệt và người đo rõ. **Tests:** dry-run checklist bằng MOCK, không coi hardware PASS.
- **Phụ thuộc/song song:** N03 cho gá/camera final; procedure/QA làm song song A/B/C/D.

## 4. Khi linh kiện về: kiểm từng phần rồi ghép hệ thống

### H01 — Tiếp nhận và xác nhận linh kiện thực [ƯT1; phụ trách E]

- [ ] Đối chiếu marking/revision/connector/phụ kiện với N01/N03; cập nhật ảnh và serial/asset ID cần thiết, không đoán tương thích theo tên chip.
- [ ] Kiểm nguồn, polarity, wiring/continuity và voltage theo tài liệu của đúng board trước nối liên board; ghi kết quả/thay đổi cần duyệt.
- **Đầu ra:** reception checklist + wiring version. **Hoàn thành khi:** từng module được xác nhận riêng, chỗ khác thiết kế được xử lý hoặc cách ly.
- **Tests:** kiểm vật lý/điện có thiết bị đo và log. **Phụ thuộc:** N01/N03, chỉ cần module của phép kiểm. Mỗi module khác nhau có thể kiểm song song với người và nguồn/dụng cụ riêng.

### H02 — Bring-up FPGA tối thiểu [ƯT1; phụ trách A]

- [ ] Sau task nạp được người dùng giao, chạy clock/reset/LED hoặc UART test tối thiểu trên đúng board; đối chiếu log/logic analyzer với target constraints.
- [ ] Đo reset/clock/UART mức điện và timing; xác minh nguồn ổn. Chưa gắn camera/AI/DDR cùng lúc để có baseline dễ chẩn đoán.
- **Đầu ra:** project/hash/bitstream candidate và bring-up report. **Hoàn thành khi:** bài kiểm tối thiểu lặp được trên board; hardware evidence ghi rõ phần nào.
- **Tests:** compiler/synthesis/STA trước nạp; board smoke theo acceptance. **Phụ thuộc:** H01 FPGA, N02/N03/N13; song song H03 trên board khác. Codex không tự flash theo backlog này.

### H03 — Bring-up MCU payload và MCU trạm đất [ƯT1; phụ trách C]

- [ ] Xác minh project/DFP/startup/reset/clocks, UART loopback và pin mux đúng board; đọc lỗi compiler/stack/FPU ABI trước chạy tính toán.
- [ ] Kiểm ISR/DMA/ring, timeout/recovery và timestamp đơn điệu; reset giữa frame, không treo do buffer/IRQ.
- **Đầu ra:** firmware/hash/build logs và bring-up của từng MCU. **Hoàn thành khi:** từng board hoạt động độc lập theo test đã giao.
- **Tests:** compiler + UART loopback/timer/reset trên bo. **Phụ thuộc:** H01 MCU, N02/N03/N12; payload/ground có thể kiểm riêng nếu đủ board/người, nhưng không hai writer cùng sửa common library.

### H04 — Dongle/USB → GCS thật [ƯT1; phụ trách D, C bàn giao bytes]

- [ ] Cho MCU đất/serial fixture phát vectors đã duyệt; đối chiếu raw capture, decoded state, log/replay. Chưa LoRa vẫn kiểm USB→GCS được.
- [ ] Kiểm COM/disconnect/reconnect và rút/cắm USB, corrupted/truncated bytes; restore session đúng, không duplicate/link false fresh.
- **Đầu ra:** serial capture/hash và GCS hardware test của KVC-GCS-009. **Hoàn thành khi:** byte→UI/log/replay khớp và lỗi link được báo/phục hồi.
- **Tests:** hardware golden loopback/hot-plug. **Phụ thuộc:** H01 USB bridge, H03 ground hoặc nguồn phát thử hợp lệ, N04/N11. Song song H05/H06 nếu cổng/board test tách riêng.

### H05 — FPGA mock BBox → MCU và LoRa hai đầu [ƯT1; phụ trách C, A bàn giao producer]

- [ ] Kiểm riêng FPGA UART→MCU trước; logic analyzer xác minh baud/frame/IRQ/burst theo ABI, đối chiếu golden vectors.
- [ ] Kiểm riêng RF payload→MCU đất trên bàn: Tx/Rx counters, CRC/reject/drop/session/timeout, RSSI/SNR từ phần cứng. Chuỗi mock có AI label SIMULATED, không FPGA inference.
- **Đầu ra:** raw captures, counters và interface report. **Hoàn thành khi:** cả hai đường riêng ổn và không có lỗi bytes/validity chưa giải quyết.
- **Tests:** link loopback, burst/reset/mất link ngắn. **Phụ thuộc:** H02/H03, đủ LoRa/nguồn/anten theo cấu hình được duyệt cho RF; N04. Thiếu LoRa vẫn kiểm UART, chưa ghi phần RF đạt.

### H06 — Camera/DDR và khả năng AI FPGA [ƯT1; phụ trách A, B bàn giao candidate]

- [ ] Bring-up camera đúng interface đã chọn; kiểm frame geometry/pixel order/clock/CDC. Nếu dùng DDR, kiểm BIST/data integrity trên đúng memory/project/IP.
- [ ] Probe tensor/ảnh nhỏ, compiler/operator/resource/STA trước ghép candidate; đối chiếu output với reference cùng preprocessing.
- [ ] Nếu không khả thi, ghi bằng chứng blocker và đề xuất fallback A/B của thiết kế cho người dùng quyết định; không âm thầm trình PC inference thành AI FPGA.
- **Đầu ra:** compatibility decision và camera/memory/AI probe report. **Hoàn thành khi:** chọn được đường khả thi có evidence hoặc fallback được duyệt; không bắt buộc giữ một model không compile được.
- **Tests:** camera pattern/frame integrity, DDR BIST nếu dùng, compiler/STA/tensor comparison trên bo. **Phụ thuộc:** H01 camera/adapter/FPGA, H02, N02/N03; AI candidate N07, probe tối thiểu không cần đợi full training. Không cùng flash board A đang dùng cho H05.

### H07 — Cảm biến, gá camera và calibration thực [ƯT1; phụ trách E, C tích hợp driver]

- [ ] C bring-up từng LiDAR/IMU/GNSS có thật: frame/register/CRC nếu có, timestamp, invalid/stale/timeout và recovery theo tài liệu đúng module.
- [ ] E đo intrinsics/distortion/pose/origin/mốc ground truth của camera/gá thực; ghi dataset/calibration hash và điều kiện đo.
- [ ] C chạy geometry trên input cảm biến đã xác minh; LOCAL_GRID không cần giả GNSS valid. WGS-84 chỉ mở khi dữ liệu GNSS và biến đổi đã kiểm.
- **Đầu ra:** sensor logs + calibration package version + local georef test. **Hoàn thành khi:** driver/đơn vị/validity rõ và calibration tái lập; chưa đủ sensor thì test subset, phần thiếu BLOCKED.
- **Tests:** known input/range/pose, disconnect/stale, địa điểm/mốc chuẩn. **Phụ thuộc:** H03, N12/N14; camera/gá H06 cho calibration final. Thu ảnh mục tiêu và QA N05/N06 có thể bổ sung song song.

### H08 — Chuỗi tối thiểu 30 phút [ƯT1; phụ trách C, D ghi log, E nghiệm thu]

- [ ] Chạy FPGA mock UART→MCU payload→LoRa→MCU đất→USB→GCS liên tục 30 phút theo G2; so counts/sequence/session/time giữa các tầng.
- [ ] UI/SQLite/replay cùng phản ánh nguồn MOCK, validity và link; kiểm ngắt/kết nối và reset theo procedure, ghi lost/reject/drop có nguyên nhân.
- **Đầu ra:** evidence chain, session/captures/hash, replay và issue list. **Hoàn thành khi:** đúng acceptance G2 được xác minh; G2 còn cần đầu ra dữ liệu QA theo thiết kế, không chỉ transport.
- **Tests:** integrated 30-minute run + replay verification. **Phụ thuộc:** H04/H05, N10/N11, nguồn ổn H01; AI FPGA và camera chưa là điều kiện để kiểm transport mock.

### H09 — Ghép chuỗi thật và khóa candidate [ƯT1; phụ trách A, B/C/D/E bàn giao từng tầng]

- [ ] Thay mock BBox bằng output AI FPGA đã kiểm, ghép georef MCU và đường RF/USB ổn; đồng bộ resolution/letterbox/class/confidence/track/validity/timestamps.
- [ ] Kiểm đủ Camera→FPGA AI→MCU định vị→LoRa→GCS→log/replay; inference provenance đúng nguồn. Nhánh fallback PC_REFERENCE phải trình bày riêng nếu được duyệt, không gọi G3 FPGA AI đạt.
- [ ] Khóa candidate, đánh giá độc lập locked-test theo thiết kế; không tuning dựa test sau đánh giá.
- **Đầu ra:** release candidate và G3 evidence. **Hoàn thành khi:** chain và tiêu chí G3 được đo đúng candidate hoặc báo blocker/fallback cụ thể.
- **Tests:** integrated outputs vs reference/ground truth, locked-test và replay. **Phụ thuộc:** H06/H07/H08, N06/N07; cần đúng bộ linh kiện của kiến trúc đã chốt.

### H10 — Đo chỉ tiêu và fault/recovery [ƯT2; phụ trách E]

- [ ] Đo 20 mốc sa bàn: ground truth, predicted coordinates, error theo từng điểm; báo cả invalid/rejected và điều kiện camera/pose.
- [ ] Đo RF PRR/cự ly trong điều kiện mô tả; công suất/nhiệt 60 phút; FPS/latency với input/candidate xác định nếu có AI FPGA. Không công bố các mục tiêu như số đo.
- [ ] D chạy stress/soak/binary; C/A kiểm reset/mất link/nguồn/cảm biến invalid theo procedure, đảm bảo UI stale/invalid và log recovery đúng. Thử crash process không thay thử mất nguồn.
- **Đầu ra:** measurement/fault reports với số liệu, logs và giới hạn. **Hoàn thành khi:** tiêu chí thiết kế được đối chiếu, failed items thành task fix, không che bằng số trung bình.
- **Tests:** đo hardware + host load; thiết bị đo phải đủ cho phép kiểm. **Phụ thuộc:** H08 cho transport/fault; đo end-to-end AI/georef phụ thuộc H09/H07. Không chạy soak trên cùng máy/board đang thu metrics benchmark.

### H11 — Feature freeze, hồi quy và đóng gói offline [ƯT2; phụ trách D]

- [ ] Sau quyết định G4, cố định hashes của source/config/model/firmware/bitstream/calibration/ABI; chỉ sửa bug có task và chạy hồi quy phù hợp.
- [ ] Chuẩn bị lockfiles/dependency packages/assets và launcher theo KVC-GCS-010; kiểm laptop sạch/WAN-off/cold-cache, log/replay và recovery. Không xóa .venv/node_modules trước khi có gói offline được kiểm.
- [ ] A/B/C/E bàn giao build/measurement instructions và tài nguyên riêng; full evidence review bị ignore phải được sao lưu/bàn giao riêng.
- **Đầu ra:** bundle + verification matrix + hướng dẫn vận hành; binary/model không đưa vào prompt.
- **Hoàn thành khi:** máy demo sạch chạy được, candidate không trôi và còn cách khôi phục; không thêm UI tính năng mới sau freeze.
- **Tests:** full regression, offline install/start/replay, checksums. **Phụ thuộc:** H10 và quyết định freeze; nghiên cứu dependency packaging có thể làm sớm song song N09.

### H12 — Tổng duyệt và bàn giao [ƯT2; phụ trách E]

- [ ] 5 lượt demo liên tiếp theo thiết kế, mỗi lượt có input/conditions/log/outcome; quay video 2–3 phút đúng nguồn inference và mức chứng minh.
- [ ] Bàn giao source/build instructions, ABI/vectors, calibration/model card, measurements, inventory, user manual, limitations và backup evidence.
- [ ] Người dùng nghiệm thu; Git commit/release/flash/deploy chỉ theo yêu cầu riêng, không tự thực hiện từ checklist này.
- **Đầu ra:** gói bàn giao và biên bản G5. **Hoàn thành khi:** tiêu chí G5 được kiểm và human approval rõ; phần BLOCKED được công bố.
- **Tests:** rehearsal checklist + restore/readability/hash checks. **Phụ thuộc:** H11; viết manual/script demo có thể chuẩn bị từ N14.

## 5. Linh kiện về từng phần: mở việc nào trước?

| Hiện có | Có thể làm | Tiếp tục chờ / giới hạn |
| --- | --- | --- |
| Chỉ máy tính | N01–N14 theo dependency; JSON MOCK/UI/logger/replay, host C tests, RTL simulation/compile, AI evidence | Không báo UART/RF/camera/cảm biến/hardware đạt |
| FPGA đã có, camera/MCU chưa có | H01/H02; mock UART với thiết bị đo phù hợp; compiler/probe khả thi | H05 liên MCU, camera và chuỗi thật chờ phần thiếu |
| MCU đã có, FPGA/cảm biến chưa có | H01/H03; UART bytes fixture, timer/ring/reset, geometry tổng hợp | Không gọi sensor/georef hardware đạt |
| MCU đất + USB bridge | H04 với producer fixture đúng ABI; GCS hot-plug/capture/log/replay | RSSI/SNR measured cần RF receiver thực |
| Hai MCU + cặp LoRa | H05 đoạn RF; H04 USB; truyền fixture/mock từ payload | G2 còn yêu cầu FPGA mock UART; chưa đủ chain thì báo partial |
| FPGA + MCU payload | H05 đoạn UART/IRQ/burst, chưa LoRa | RF/USB chain chờ ground side; không cần camera để kiểm mock |
| Camera/adapter + FPGA | H06; E chuẩn bị thu ảnh/calibration N05/N06/H07 khi có gá | Định vị thật cần pose/cảm biến/input được chốt |
| Cảm biến + MCU | H07 driver/invalid/stale và dữ liệu từng sensor | Calibration/geometry camera final còn phụ thuộc camera/gá |
| Đủ transport, thiếu AI/camera | H08 mock chain 30 phút và fault/replay | H09 chuỗi AI thật chưa mở; giữ nhãn MOCK/SIMULATED |
| Đủ bộ theo kiến trúc được duyệt | H09–H12 theo thứ tự | Có linh kiện không đồng nghĩa đủ project/toolchain/ABI/evidence |

## 6. Việc có thể thực hiện song song

| Luồng | Khi chưa đủ linh kiện | Khi linh kiện về | Điểm trao đổi bắt buộc |
| --- | --- | --- | --- |
| A — FPGA | N02/N03/N13, probe compiler với B | H02/H06; bàn giao UART H05 | Target/interface/clock/IRQ duyệt; UART vectors N04; candidate/preprocessing N07 |
| B — AI | N05/N06/N07 | Candidate comparison H06/H09; QA dữ liệu mới với E | Dataset/calibration/test hashes, class mapping và compatibility |
| C — MCU | N03/N04/N12 | H03/H05/H07; phối hợp H08 | ABI cùng D/A; pinout; invalid/time/session rules |
| D — GCS | N08/N09/N10; N11 sau ABI | H04; log/replay H08/H09; offline H11 | Golden vectors/capture C, provenance và clocks |
| E — QA/thực nghiệm | N01/N05/N14 | H01/H07/H10/H12 | Vật tư/wiring, QA evidence, ground truth và điều kiện đo |

**Ba cụm nên chạy ngay:** (1) A+C+E chốt đầu vào hardware/toolchain, (2) B+E provenance/QA/split, (3) D hồi quy/browser/MOCK logging. E chia giờ cho QA và inventory, không giả định một người làm hai phép đo cùng lúc.

**Sau khóa ABI:** A làm RTL producer, C làm MCU logic/serializer, D làm parser consumer trên cùng fixtures version hóa. Đây là ba task khác file, mỗi task một writer; người quản fixture cập nhật có báo version, các bên không tự sửa expected bytes để test PASS.

**Sau bring-up riêng:** H04 USB/GCS có thể song song H05 RF hoặc H06 camera khi board/cổng/dụng cụ và người phụ trách không bị trùng. H08/H09 là phiên tích hợp chung có một coordinator, chốt candidate trước phiên; các writer tạm dừng sửa source đang đo.

**Các việc phải tuần tự:** duyệt ABI → serializer/parser wire; duyệt wiring/điện → constraint/đấu nối/nạp; QA+split khóa → release evaluation; bring-up riêng → chain integration; đo/khắc phục → freeze → offline qualification → rehearsal/approval.

**Không chạy song song trên cùng tài nguyên:** hai coder sửa cùng file/common library, hai người flash cùng board, benchmark cùng GPU đang train, load test cùng máy đang đo latency, sửa calibration/fixture/model giữa phiên measurement. Nếu tách worktree cần baseline và handoff theo workflow; không bật Codex multi-agent.

## 7. Checklist mở việc từ hôm nay và điều kiện đổi nhánh

### Trong phiên làm việc tiếp theo

- [ ] E điền N01 và xác định linh kiện nào đã có để mở H01 tương ứng ngay.
- [ ] A/C ghi blocker N02/N03: camera interface, board map, điện/reset/IRQ, project/toolchain.
- [ ] C/D lập danh sách quyết định ABI N04; chưa duyệt thì không implement wire layout.
- [ ] B chạy validator N05, phân công QA cho E và kế hoạch test/calibration N06.
- [ ] D chạy N08, rồi N09/N10 trên source hiện có; sau build dist sẽ được tái tạo.
- [ ] Người phụ trách chọn task nhỏ và writer theo manifest mẫu mục 9; cập nhật việc nào làm được hôm nay, việc nào chờ đầu vào cụ thể.

### Trước mở phiên tích hợp hardware

- [ ] Inventory, wiring, nguồn và ABI đúng version; testbench/host/compile phù hợp đã chạy hoặc blocker được công bố.
- [ ] Producer/consumer dùng cùng vectors; flash/nạp chỉ do người dùng giao trong task hardware riêng.
- [ ] Lưu candidate hashes, captures và cách rollback/khôi phục do người dùng quyết định.
- [ ] Coordinator kiểm đúng nhãn MOCK/REAL/REPLAY và inference provenance; không coi serial fixture là toàn chuỗi REAL.

### Nếu linh kiện/toolchain về trễ

Duy trì N05–N14 và host MOCK, đồng thời ghi gate liên quan BLOCKED theo từng input. Người dùng quyết định fallback hoặc điều chỉnh cam kết sau khi có evidence. Không âm thầm giảm acceptance, thay hardware protocol hoặc đổi ngày thiết kế thành ngày đã hoàn thành.

Các mốc G1 14/10, G2 18/10, G3 22/10, G4 25/10, G5 01/11/2026 thuộc kế hoạch trước; bản thiết kế hiện tại không còn lịch này. Đây là **tham chiếu lịch sử, không phải hạn hiện hành đã được xác nhận**. Kế hoạch chi tiết theo ngày chỉ lập sau N01 xác định vật tư, nhân lực và giờ công thực có. G1 hiện chưa đủ bằng chứng đạt; G2 cần toàn chuỗi transport mock, không chỉ GCS MOCK.

## 8. Lệnh kiểm thử software tham khảo

Chạy từ đúng cwd và chỉ khi môi trường cho phép; ghi lệnh, exit, log, candidate và giới hạn. Các lệnh dưới đây **chưa được thực hiện trong task lập backlog này**.

~~~powershell
# Từ root D:\Project_UAV_KVC
.venv/Scripts/python.exe -B -m pytest Dashboard/backend/tests tests -q -p no:cacheprovider
.venv/Scripts/python.exe -B -m Dashboard.backend.tests.test_api_websocket
.venv/Scripts/python.exe -B scripts/data/validate_ai_evidence.py
git diff --check
git diff --cached --check

# Từ Dashboard/frontend
npm run typecheck
npm run lint
npm test
npm run build
~~~

Validator exit 1/AI_EVIDENCE_BLOCKED phải được đọc và khắc phục bằng evidence thật. Compiler/HDL/firmware/E2E/stress commands sẽ điền từ project/harness của task tương ứng; không chạy mọi scripts như unit tests vì train/remap/augment/webcam có tác dụng ghi hoặc mở thiết bị.

## 9. Mẫu task triển khai và cách đánh dấu hoàn thành

~~~text
Task ID: [ID task gốc nếu tiếp tục; ID mới nếu scope mới]
Backlog link: [Nxx hoặc Hxx trong file này]
Scope: [hành vi/đầu ra cụ thể]
Phụ trách nghiệm thu: [A/B/C/D/E, chọn một coordinator]
Writer/Owner: [Codex hoặc Antigravity — đúng một]
Allowed files: [danh sách đường dẫn literal, kể cả tests/fixtures/config]
Inputs/dependencies: [ABI/candidate/wiring/data versions và hashes]
Acceptance criteria: [điều kiện đo/quan sát được]
Tests: [lệnh, cwd, input và tiêu chí]
Status: PROPOSED → READY → IMPLEMENTING → READY_FOR_REVIEW → HUMAN_APPROVAL
Blocker: [đầu vào nào thiếu, ai giải quyết; BLOCKED nếu không thể tiếp tục]
Evidence: [review/<Task ID>/..., command/exit/log/hash/limitations]
~~~

Chỉ tích checkbox của đầu ra đã kiểm đúng scope; ghi DESIGN, SOURCE-VERIFIED, SIMULATED, BUILT/SYNTHESIZED hoặc HARDWARE-VERIFIED theo bằng chứng. Self-review và tests PASS không phải approval. Tài liệu này sẽ được cập nhật status sau từng task được giao; hiện không có task hardware nào được tự đánh dấu DONE.
