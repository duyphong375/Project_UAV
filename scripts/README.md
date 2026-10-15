# Công cụ dự án KVC

Chạy từ thư mục gốc dự án. Đọc tham số và điều kiện trước khi chạy script.

| Vị trí | Dùng để |
| --- | --- |
| kvc-review.ps1 | Chuẩn bị review theo workflow; dùng -DryRun trước review |
| test_video.py | Chạy AI tham chiếu PC trên video |
| test_webcam.py | Chạy AI tham chiếu PC từ camera máy tính |
| ai/ | Training, theo dõi training và tạo báo cáo |
| data/ | Remap/tăng cường dữ liệu, tạo manifest và kiểm hồ sơ AI |

Script video/webcam không phải unit test: có thể mở camera hoặc nạp model. Script biến đổi dữ liệu có thể ghi file; dùng chế độ dry-run nếu hỗ trợ. Các bài test phần mềm ở tests/, Dashboard/backend/tests/ và Dashboard/frontend/src/*.test.*.

Đã bỏ script sync_80ep_display.py cũ khỏi công cụ hiện hành: cộng offset epoch không chứng minh lịch sử huấn luyện. Dataset, checkpoint và báo cáo lịch sử trong ai_training/ được giữ để đối chiếu.

Mô hình mục tiêu là YOLO11n hai lớp person/lifebuoy. Video/webcam ưu tiên `ai_training/weights/yolo11n_2class_best.pt`, rồi fallback sang checkpoint trong các run boosted và hardware; video cho phép chỉ định `--weights`. Tên file/run không xác nhận kiến trúc; không tự nạp model legacy. Script video và browser lấy đường dẫn theo vị trí dự án để có thể chuyển thư mục.
