# KVC — Phân hệ Trạm Giám Sát Mặt Đất (Dashboard / GCS)

- **Người phụ trách:** **Đoàn Thanh Trường Thịnh**
- **Mục tiêu:** Cung cấp giao diện trạm mặt đất (GCS) chuyên dụng để giám sát tải nhiệm vụ cứu nạn bão lũ (Bounding Box người/phao cứu sinh từ AI, hình ảnh camera, vị trí định vị WGS-84, cảm biến độ cao khí áp/siêu âm AJ-SR04M và pin).
- **Phân định ranh giới khí tài:** KVC là hệ thống giám sát **tải nhiệm vụ cứu nạn** (Payload), **không phải Flight Controller (FC)**. Dashboard không can thiệp điều khiển bay, arm/disarm hay lập lộ trình bay waypoint của máy bay.
- **Tài liệu căn cứ:**
  - Thiết kế kiến trúc tổng thể: [docs/KVC_ThietKeHeThong.md](file:///d:/Project_UAV_KVC/docs/KVC_ThietKeHeThong.md)
  - Đặc tả thiết kế GCS: [docs/gcs/KVC_GCS_DESIGN_SPEC.md](file:///d:/Project_UAV_KVC/docs/gcs/KVC_GCS_DESIGN_SPEC.md)
  - Hợp đồng dữ liệu nội bộ: [docs/interfaces/IF_GCS_DATA_CONTRACT.md](file:///d:/Project_UAV_KVC/docs/interfaces/IF_GCS_DATA_CONTRACT.md)
  - Hướng dẫn kết nối Wi-Fi & ESP32: [HUONG_DAN_KET_NOI_WIFI_VA_ESP32.md](HUONG_DAN_KET_NOI_WIFI_VA_ESP32.md)
  - Giao diện kết nối Gateway ESP32: [docs/interfaces/IF_ESP32_GCS_WS.md](file:///d:/Project_UAV_KVC/docs/interfaces/IF_ESP32_GCS_WS.md)

---

## 1. Kiến Trúc Kết Nối 2 Chặng (2-Tier Topology)

Kiến trúc mục tiêu của trạm mặt đất được thiết kế phân tầng. Trong source hiện có, backend GCS chạy MOCK/logger/replay; ingress từ ESP32 và giải mã RF chưa triển khai. Xem [backend README](backend/README.md) và IF-03 để biết trạng thái chi tiết.

```text
[UAV Tải Nhiệm Vụ]
       │
       ▼ (LoRa; IF-02 còn là DRAFT ABI)
[Gateway ESP32-C3 Trạm Đất] (Nguồn riêng theo thiết kế; kit/board TBD)
       │
       ▼ (Wi-Fi SoftAP / WebSocket; IF-03 là baseline chưa xác minh)
[Dashboard/backend] (Laptop Ground Station - FastAPI; ingress chưa triển khai)
  ├── MOCK: phát dữ liệu mô phỏng và ghi SQLite
  ├── REPLAY: phát lại session đã commit
  └── WebSocket nội bộ cho frontend: ws://127.0.0.1:8000/ws/telemetry
       │
       ▼ (Localhost WebSocket)
[Dashboard/frontend] (Trình duyệt Web - React + TypeScript + Vite + Leaflet)
  └── Hiển thị HUD bay, bản đồ cứu hộ OSM, tọa độ mục tiêu và biểu đồ cảm biến
```

> [!IMPORTANT]
> **Quy tắc bất biến:** Trình duyệt (`frontend`) **tuyệt đối không kết nối trực tiếp** tới Gateway ESP32. Toàn bộ luồng kết nối bắt buộc phải đi qua `backend` trên Laptop để ghi log SQLite, quản lý trạng thái và tránh làm treo vi điều khiển ESP32 khi có nhiều client kết nối.

---

## 2. Cấu Trúc Thư Mục Phân Hệ Dashboard

```text
Dashboard/
├── backend/                  # Dịch vụ Backend trung tâm trên Laptop (FastAPI / Python)
│   ├── main.py               # Điểm khởi chạy FastAPI, WebSocket server/client & REST API
│   ├── config.py             # Cấu hình biến môi trường, cổng, đường dẫn DB
│   ├── state.py              # Quản lý trạng thái xe bay/nhiệm vụ trong bộ nhớ
│   ├── schemas.py            # Pydantic models cho gói tin telemetry, BBox, trạng thái
│   ├── sqlite_logger.py      # Module ghi/đọc telemetry và nhật ký cứu hộ vào SQLite WAL
│   ├── replay_engine.py      # Bộ phát lại dữ liệu bay lịch sử (Replay mode)
│   ├── mock_source.py        # Nguồn sinh dữ liệu giả lập phục vụ kiểm thử độc lập
│   ├── requirements.txt      # Danh mục thư viện Python phụ thuộc
│   ├── tests/                # Bộ kiểm thử tự động pytest cho backend
│   └── README.md             # Hướng dẫn chi tiết vận hành backend
│
├── frontend/                 # Giao diện người dùng Web GCS (React + TypeScript + Vite)
│   ├── src/                  # Mã nguồn ứng dụng giao diện
│   │   ├── app/              # Cấu trúc ứng dụng chính
│   │   ├── components/       # Các UI components (HUD, bản đồ Leaflet, BBox video, sensors)
│   │   ├── features/         # Logic chức năng theo nghiệp vụ (telemetry, alerts, map)
│   │   ├── services/         # Client kết nối WebSocket & gọi REST API backend
│   │   ├── types/            # TypeScript interfaces & types
│   │   └── main.tsx          # Điểm khởi chạy React
│   ├── public/               # Tài nguyên tĩnh, icon cứu nạn, âm thanh cảnh báo
│   ├── tests/                # Bộ kịch bản kiểm tra giao diện bằng Puppeteer/browser
│   ├── package.json          # Quản lý thư viện phụ thuộc npm
│   ├── vite.config.ts        # Cấu hình đóng gói Vite
│   └── README.md             # Hướng dẫn chi tiết vận hành frontend
│
└── README.md                 # Tài liệu chỉ dẫn tổng quan này
```

---

## 3. Hướng Dẫn Vận Hành Nhanh

### 3.1. Khởi chạy Backend (Terminal 1)
```powershell
cd Dashboard/backend
# Kích hoạt môi trường ảo Python
../../.venv/Scripts/Activate.ps1
# Cài đặt thư viện (lần đầu)
pip install -r requirements.txt
# Chạy backend server
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
* API Documentation: `http://127.0.0.1:8000/docs`
* Endpoint WebSocket: `ws://127.0.0.1:8000/ws/telemetry`

### 3.2. Khởi chạy Frontend (Terminal 2)
```powershell
cd Dashboard/frontend
# Cài đặt dependencies (lần đầu)
npm ci
# Chạy Vite dev server
npm run dev
```
* Truy cập giao diện: `http://localhost:5173`

---

## 4. Các Chế Độ Hoạt Động (Operating Modes)

1. **MOCK Mode (Kiểm thử độc lập không phần cứng):**
   - Backend tự động sinh luồng tọa độ UAV bay quỹ đạo quanh khu vực lũ lụt giả lập và phát hiện người/phao giả lập.
   - Thích hợp phát triển giao diện, kiểm thử tính năng HUD, bản đồ mà không cần phần cứng.
2. **REAL ingress (chưa triển khai):**
   - IF-03 nêu endpoint mục tiêu `ws://192.168.4.1:8080/telemetry` và SSID `KVC_GCS_AP`; đây là baseline thiết kế, chưa xác minh trên thiết bị.
   - Backend hiện chưa kết nối gateway hoặc giải mã gói LoRa. Không dùng source hiện tại để nghiệm thu đường dữ liệu phần cứng.
3. **REPLAY Mode (Phát lại dữ liệu lịch sử):**
   - Đọc dữ liệu bay đã ghi trong tệp SQLite để tua lại toàn bộ phiên cứu nạn phục vụ đánh giá sau nhiệm vụ.
