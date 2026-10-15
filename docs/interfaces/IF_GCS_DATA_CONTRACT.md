# Đặc tả giao diện: Backend GCS ↔ Frontend Dashboard Web (Localhost WebSocket & REST)

- **Mã giao diện:** `IF-04`
- **Hai đầu kết nối:** Dịch vụ Backend Python FastAPI trên Laptop (**Đoàn Thanh Trường Thịnh**) ↔ Giao diện Web Dashboard trên Trình duyệt (**Đoàn Thanh Trường Thịnh**)
- **Tài liệu toàn văn chi tiết:** 👉 **[docs/gcs/KVC_GCS_DATA_CONTRACT.md](../gcs/KVC_GCS_DATA_CONTRACT.md)**
- **Trạng thái:** `IMPLEMENTED / TESTING` (Mã nguồn đã có sẵn trong `Dashboard/backend/schemas.py` và `Dashboard/frontend/src/`)

---

## 1. Kiến trúc kết nối nội bộ Host

Giao diện IF-04 hoạt động hoàn toàn cục bộ trong nội bộ máy tính laptop (Localhost Loopback):
* **REST API:** Chạy tại `http://127.0.0.1:8000/api` phục vụ cấu hình, chuyển chế độ phiên (MOCK / REAL / REPLAY), danh sách phiên ghi và xuất nhật ký.
* **WebSocket Dispatcher:** Chạy tại `ws://127.0.0.1:8000/ws` để phát sóng dữ liệu thời gian thực tới tất cả các tab trình duyệt đang mở Dashboard.

---

## 2. Tóm tắt các Endpoint chính

| Giao thức | Endpoint URL | Hướng dữ liệu | Chức năng chính |
| :---: | :--- | :---: | :--- |
| **WS** | `ws://127.0.0.1:8000/ws` | Backend ➔ Frontend | Luồng phát sóng JSON telemetry, radar target, cảnh báo, nhịp tim link |
| **GET** | `/api/status` | Frontend ➔ Backend | Lấy trạng thái hiện tại của Backend, chế độ nguồn (`MOCK`, `REAL`, `REPLAY`) |
| **GET** | `/api/sessions` | Frontend ➔ Backend | Lấy danh sách các file log chuyến bay SQLite có trong thư mục lưu trữ |
| **POST**| `/api/replay/start` | Frontend ➔ Backend | Kích hoạt phát lại phiên bay từ file log SQLite theo virtual clock |
| **POST**| `/api/replay/pause` | Frontend ➔ Backend | Tạm dừng hoặc tiếp tục phát lại |
| **POST**| `/api/replay/seek` | Frontend ➔ Backend | Nhảy thời gian phát lại tới giây mong muốn |

---

## 3. Cấu trúc bản tin JSON qua WebSocket

Chi tiết đầy đủ các trường dữ liệu, quy tắc validate, null handling và trạng thái stale xem toàn văn tại:
👉 **[docs/gcs/KVC_GCS_DATA_CONTRACT.md](../gcs/KVC_GCS_DATA_CONTRACT.md)**
