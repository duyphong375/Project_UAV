# KVC — checkpoint tham chiếu PC

## File được chọn

- **File:** `yolo11n_2class_best.pt`
- **Dung lượng:** 5.449.747 bytes
- **SHA-256:** `F70D9EBE7088A6017389DC92596DD6588E7A36C03F7CA94C845ECBF1CEC1FAC7`
- **Nguồn theo hồ sơ train:** run `yolo11n_2class_boosted`, khởi tạo từ `yolo11n_2class_hardware`.
- **Trạng thái:** checkpoint tham chiếu PC; chưa xác minh độc lập kiến trúc từ metadata/graph và chưa HARDWARE-VERIFIED.

Tên file mô tả model dự kiến, không tự chứng minh kiến trúc hoặc mapping lớp. Trước khi export, bàn giao làm model phần cứng, hoặc công bố metric, cần kiểm tra metadata/graph, hash và kết quả đánh giá có dữ liệu ground truth. Mapping dự kiến trong ontology là class 0 `person`, class 1 `lifebuoy`; wire ID vẫn `PROPOSED_PENDING_G1_ABI`.

## Hồ sơ các run

- `../runs/yolo11n_rtx4060_80ep/`: baseline RTX 4060; checkpoint gốc được giữ trong run này.
- `../runs/yolo11n_2class_hardware/`: run 65 epoch.
- `../runs/yolo11n_2class_boosted/`: run boosted 13 epoch; checkpoint trong run trùng byte với file được chọn ở trên.

Các checkpoint trong `runs/` là đầu ra gắn với hồ sơ từng run. Thư mục `archive/` đã được dọn; không dùng checkpoint legacy làm model hiện hành.
