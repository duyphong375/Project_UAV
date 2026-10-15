# KVC — Bộ Kiểm Thử Cấp Hệ Thống Trên Máy Tính (Tests)

Thư mục này chứa bộ kiểm thử tự động (automated tests) viết bằng Python (`pytest`) chạy trực tiếp trên môi trường máy tính (PC). Mục đích là kiểm tra tính đúng đắn của logic xử lý dữ liệu AI, chuyển đổi bounding box, tính toàn vẹn manifest và chuỗi tích hợp phần mềm trước khi đưa lên phần cứng.

---

## 1. Phân Định Ranh Giới Kiểm Thử Trong KVC

Để tránh nhầm lẫn giữa các tầng công nghệ trong dự án tải UAV KVC, các bộ kiểm thử được tách biệt theo phạm vi:

| Vị trí bộ test | Loại kiểm thử & Công nghệ | Mục đích kiểm tra | Người phụ trách / Quy tắc |
| :--- | :--- | :--- | :--- |
| **`tests/`** (thư mục này) | **Python (`pytest`)** | Logic suy luận AI tham chiếu PC, adapter BBox, công cụ xử lý dữ liệu | Toàn nhóm (Kiểm tra phần mềm cấp hệ thống) |
| **[`fpga/tb/`](file:///d:/Project_UAV_KVC/fpga/tb)** | **Verilog Testbench** (`iverilog` / ModelSim) | Mô phỏng dạng sóng RTL, FSM UART, bộ đệm FIFO, timing phần cứng FPGA | **Nguyễn Tất Vững** (Độc lập, không chạy qua pytest) |
| **[`Dashboard/backend/tests/`](file:///d:/Project_UAV_KVC/Dashboard/backend/tests)** | **Python (`pytest`)** | API REST, WebSocket telemetry, SQLite logger, replay engine | **Đoàn Thanh Trường Thịnh** (Backend GCS) |
| **`Dashboard/frontend/`** | **Vitest (`npm run test`)** | Render component HUD, bản đồ Leaflet, chuyển đổi trạng thái giao diện | **Đoàn Thanh Trường Thịnh** (Frontend GCS) |

> [!WARNING]
> Các bài test trong thư mục này sử dụng dữ liệu giả lập (mock data) và adapter chuyển đổi; kết quả **PASS** chỉ xác nhận tính đúng đắn ở mức mã nguồn (**SOURCE-VERIFIED**), chưa chứng minh hệ thống đã chạy trên vi điều khiển hoặc FPGA thật (**HARDWARE-VERIFIED**).

---

## 2. Cấu Trúc Thư Mục `tests/`

```text
tests/
├── __init__.py                   # File đánh dấu package Python
│
├── test_ai_data_tools.py         # Kiểm thử các công cụ dữ liệu:
│                                 # • Kiểm tra logic remap nhãn 2 lớp (person, lifebuoy)
│                                 # • Kiểm tra manifest generator và tính băm SHA-256
│                                 # • Kiểm tra phân chia train/val không rò rỉ dữ liệu
│
├── test_inference_adapter.py     # Kiểm thử adapter suy luận YOLO11n tham chiếu:
│                                 # • Ánh xạ nhãn model (0 -> wire ID 1: person, 1 -> wire ID 2: lifebuoy)
│                                 # • Chuyển đổi tọa độ box giữa original-image và letterbox
│                                 # • Xác thực ngưỡng confidence và giới hạn biên [0, 1]
│
├── test_inference_integration.py # Kiểm thử tích hợp chuỗi xử lý AI:
│                                 # • Đảm bảo pipeline nhận diện chạy thông suốt với input giả lập
│                                 # • Kiểm tra định dạng đầu ra tương thích với giao tiếp UART FPGA-MCU
│
└── README.md                     # Tài liệu hướng dẫn này
```

---

## 3. Hướng Dẫn Chạy Kiểm Thử

Toàn bộ kiểm thử cần được chạy bằng Python từ môi trường ảo `.venv` của dự án tại thư mục gốc:

```powershell
# Chạy toàn bộ test trong thư mục tests/
.venv/Scripts/python.exe -m pytest tests -q -p no:cacheprovider

# Chạy có hiển thị chi tiết từng test case
.venv/Scripts/python.exe -m pytest tests -v -p no:cacheprovider

# Chạy một file test cụ thể
.venv/Scripts/python.exe -m pytest tests/test_inference_adapter.py -v
```

### Tiêu chuẩn nghiệm thu (Acceptance Criteria):
- Tất cả các test cases phải đạt trạng thái **PASSED**.
- Không phát sinh cảnh báo warning nghiêm trọng hoặc lỗi import phụ thuộc phần cứng bên ngoài.
- Tuân thủ quy định tại [AGENTS.md](file:///d:/Project_UAV_KVC/AGENTS.md): Ghi nhận rõ trạng thái kiểm thử kèm lệnh thực thi và exit code.
