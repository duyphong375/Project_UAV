# KVC — chuẩn bị và đồng bộ dữ liệu AI

- Task ID: KVC-AI-DATA-001 / KVC-AI-DATA-SYNC-001
- Scope: ontology, cấu trúc dữ liệu, manifest, adapter chuyển đổi model sang wire, quy tắc kiểm toán ngữ nghĩa
- Owner triển khai: Codex hoặc Antigravity được chọn theo task; Codex review (SELF-REVIEW nếu là author), người dùng chọn FIX OWNER.
- Allowed files: `ai_training/README.md`, `ai_training/ontology.yaml`, `ai_training/inference_adapter.py`, `ai_training/manifests/*`, tài liệu này
- Status: ADAPTER_SOURCE_VERIFIED / DATA_PROVENANCE_PENDING (Cập nhật 14/10/2026; không chứng nhận phần cứng)

## Snapshot evidence mới — 14/10/2026

KVC-AI-DATAFIX-20261014-001 đã sửa generator thành dry-run/hash thật/UNREVIEWED, thêm validator chỉ đọc và fixture tests; không sửa dataset/manifest cũ hoặc chứng nhận release. Lần validator được lưu ghi exit 1, AI_EVIDENCE_BLOCKED, 335 issues. Cần nguồn/license/consent, QA người, session có hash, locked-test và calibration thật. Đây là kết quả lịch sử, không chạy lại trong KVC-STATUS-DOC-20261014-001. Xem [AI README](../../ai_training/README.md), [tiến độ dự án](../KVC_PROJECT_STATUS.md) và [báo cáo DATAFIX](../../review/KVC-AI-DATAFIX-20261014-001/REPORT.md). Wire ID 1/2 là mapping ứng dụng và đề xuất wire; RF payload 32 byte vẫn DESIGN_PENDING duyệt ABI. Wi-Fi SoftAP/WebSocket v1 là giao diện mục tiêu ESP32–laptop, chưa triển khai/xác minh; USB48 thuộc kiến trúc cũ.

## Bước 1 — Ontology và Hợp đồng Giao thức (Wire Contract)

1. **Active Profile: `hardware_contract_2class` (Profile 2 lớp phục vụ huấn luyện; wire ABI chưa duyệt)**:
   - **Class 0 (`person`)** -> **Wire ID: 1**: Người thật nhìn thấy được trên mặt nước, thuyền hoặc bờ; vật mẫu/mannequin phải được ghi và đánh giá riêng theo ontology.
   - **Class 1 (`lifebuoy`)** -> **Wire ID: 2**: Phao cứu sinh hình vòng hoặc móng ngựa.
   - **Hard-Negative**: 822/4.800 nhãn train rỗng (17,13%) và 258/1.547 nhãn val rỗng (16,68%) theo kiểm đếm ngày 14/10. Nhãn rỗng chưa chứng minh ảnh âm tính đúng ngữ nghĩa; cần QA ảnh. Baseline trước augment là 4.000 train.
   - **Lệch lớp (Imbalance)**: Hiện train có 21.308 person / 2.390 lifebuoy boxes (~8,92:1), val có 6.206 / 330 (~18,81:1). BẮT BUỘC đo lường Precision, Recall, mAP50 riêng biệt từng lớp; không dùng mAP all gộp để che lấp hiệu năng lớp phao.

2. **Reference Profile: `pc_reference_profile` (Tham chiếu 5 lớp)**:
   - Tham chiếu mở rộng cho Dashboard PC: `person`, `lifebuoy`, `boat`, `life_jacket`, `person_model`. Đây là profile tham chiếu trong ontology; không đồng nhất với backup dataset. `labels_5class_backup/` dùng swimmer/boat/jetski/life_saving_appliances/buoy theo script remap; cần adapter riêng nếu muốn dùng profile tham chiếu.

3. **Ngữ cảnh Phần cứng & Adapter (Inference Adapter)**:
   - Telemetry 20-byte là ghi nhận source lịch sử; inventory hiện không có parser/firmware tương ứng. RF payload 32-byte vẫn cần duyệt ABI và bằng chứng trên bo. USB envelope 48-byte thuộc phương án cũ, không còn là transport mục tiêu.
   - Adapter `ai_training/inference_adapter.py` ánh xạ lớp (0,1) sang ID ứng dụng (1,2) và confidence 0..1 sang 0..100%. Mặc định nhận boxes ở pixel ảnh gốc (`ORIGINAL_IMAGE_XYXY`); chỉ unletterbox khi caller khai báo `LETTERBOX_640_XYXY`. Không unletterbox lần nữa boxes đã ở ảnh gốc của Ultralytics. Adapter chưa đóng gói wire bytes và luôn ghi PC_REFERENCE/NOT_TRACKED.
   - Tiền xử lý (Preprocessing): RGB, letterbox 640x640 với viền màu 114 (114, 114, 114), chuẩn hóa pixel `[0, 255] -> [0.0, 1.0]`.

**Model mục tiêu:** YOLO11n detection hai lớp person/lifebuoy; đối chiếu metadata/graph/hash checkpoint trước chọn candidate. Preprocessing/mapping bám đúng model, không suy kiến trúc từ tên best.pt. Xem [AI README](../../ai_training/README.md).

## Bước 2 — Cấu trúc lưu trữ

Dùng `ai_training/` theo README. Video/ảnh gốc, ZIP Roboflow và weights để ngoài Git. Mỗi phiên có một `session_id`, giữ đường dẫn và SHA-256 trong manifest.

Trước khi upload Roboflow, kiểm tra quyền sử dụng, đặc biệt với video công khai. Nếu workspace Roboflow là Public, không đưa dữ liệu nhạy cảm lên đó.

## Bước 3 — Ma trận thu thập

**Cường** phụ trách thu video/ảnh thực tế theo phiên; **Kiên và Vững** hỗ trợ camera/gá/pose; **Thịnh** làm nhãn, QA, chia tập và đánh giá; **Phong** điều phối và cùng nhóm quyết định train lại sau đánh giá baseline. Bổ sung cảnh từ camera thực dùng, bể bơi và nguồn lũ lụt hợp lệ; lưu domain riêng. Video demo đã chọn không thay locked-test.

Điền `collection_matrix.csv` trước khi quay. Mỗi session thay đổi ít nhất một yếu tố: góc nhìn, ánh sáng, nước, che khuất, chuyển động, kích thước mục tiêu hoặc nền. Có 20–30% ảnh âm tính/hard-negative trong mỗi split là mục tiêu ban đầu.

Video điện thoại/webcam chỉ giúp xác minh pipeline và các miền đã quay. Dữ liệu vật mẫu/synthetic phải báo cáo tách khỏi người thật. Không quay cảnh nguy hiểm để tạo dữ liệu.

Khởi động với pilot khoảng 200 ảnh đã QA. Khi mở rộng PoC, ưu tiên session độc lập thay vì lấy thêm frame liên tiếp từ cùng video.

## Bước 4 — Manifest và split

Ghi session vào `session_manifest.csv` trước khi trích frame. Gán `planned_split` theo phiên: train/val/test. Sau khi khóa, điền `actual_split` và không di chuyển ảnh đơn lẻ giữa các tập.

Các frame gần nhau của cùng video phải cùng split. Tập test khóa trước khi chọn checkpoint, preprocessing, confidence threshold hoặc augmentation.

Đề xuất khởi đầu: 70% session train, 15% validation, 15% test; nếu ít session, ưu tiên độc lập cảnh và bảo đảm mỗi lớp có mặt ở validation/test.

Manifest ảnh phải có hash, session, frame index, domain, class xuất hiện và trạng thái QA. Ảnh không có mục tiêu giữ annotation rỗng, không tạo nhãn `background`.

## Những gì chưa thể hoàn thành trong workspace

Đã có dataset 6.347 ảnh, nhãn, weights và reports huấn luyện/evaluation cục bộ. Audit không nạp weights hoặc tái chạy train. Còn thiếu bằng chứng nguồn/license rõ ràng, split độc lập theo phiên và QA thực tế: image manifest chỉ có 100 dòng với hash placeholder và trạng thái QA do script tự gán. Kiểm SHA-256 không có ảnh trùng byte nhưng không loại trừ frame gần nhau. Cần hoàn thiện provenance/QA và khóa test trước công bố metric nghiệm thu. Xem [AI README](../../ai_training/README.md) và báo cáo audit cục bộ.

## Acceptance criteria

- Ontology có định nghĩa, quy tắc BBox và mapping PC/hardware rõ ràng.
- Mỗi source có session ID, domain, đường dẫn/quyền sử dụng và split theo session.
- Có ảnh âm tính/hard-negative và ma trận điều kiện.
- Không có frame cùng phiên bị chia sang nhiều tập.
- Dataset chưa được gọi là READY_FOR_TRAIN cho đến khi dữ liệu thật, nhãn và QA được ghi nhận.
