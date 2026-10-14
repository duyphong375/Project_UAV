# KVC — Tải nhiệm vụ UAV tìm kiếm cứu nạn bão lũ

KVC là tải nhiệm vụ giám sát, phát hiện và định vị mục tiêu cứu nạn cho UAV trong tình huống bão lũ. Hệ thống dự kiến kết hợp camera và AI, cảm biến định vị, liên kết vô tuyến, trạm thu mặt đất và phần mềm GCS (Ground Control Station).

> **Phạm vi:** KVC là payload và hệ thống giám sát nhiệm vụ, không phải flight controller. KVC không điều khiển bay, arm/disarm hoặc lập lộ trình waypoint.

Tài liệu thiết kế mô tả mục tiêu và cấu hình dự kiến; không tự nó chứng minh phần cứng hoặc hiệu năng đã được đo. Xem [Tiến độ dự án](docs/KVC_PROJECT_STATUS.md) để biết phần nào đã có bằng chứng và phần nào còn thiếu.

## Mục lục

- [Tổng quan kiến trúc](#tổng-quan-kiến-trúc)
- [Cấu trúc repository](#cấu-trúc-repository)
- [Trạng thái các phân hệ](#trạng-thái-các-phân-hệ)
- [Bắt đầu chạy phần mềm](#bắt-đầu-chạy-phần-mềm)
- [Kiểm tra source](#kiểm-tra-source)
- [Dữ liệu, model và file cục bộ](#dữ-liệu-model-và-file-cục-bộ)
- [Tài liệu nên đọc](#tài-liệu-nên-đọc)

## Tổng quan kiến trúc

Luồng nhiệm vụ mục tiêu:

```text
Camera + cảm biến
        ↓
AI phát hiện mục tiêu ──→ FPGA / MCU payload
                              ↓ telemetry
                         LoRa / RF link
                              ↓
                   Trạm thu mặt đất / USB
                              ↓
                Backend GCS → Dashboard GCS
                              ↓
                    Lưu phiên / phát lại
```

Source hiện tại tập trung vào **Dashboard GCS**, **backend MOCK có lưu phiên/replay**, và **AI tham chiếu chạy trên PC**. Luồng từ cảm biến/serial/RF trên thiết bị thật vào GCS chưa được triển khai và xác minh. Giao thức RF 32 byte và USB envelope 48 byte trong tài liệu vẫn là thiết kế cần chốt; ghi nhận telemetry 20 byte là trạng thái source lịch sử. Không tự suy ra baud, packet layout, CRC, IRQ hoặc pinout từ sơ đồ trên.

## Cấu trúc repository

```text
KVC/
├── README.md                         # Điểm vào dự án này
├── .gitignore                        # Loại môi trường, artifact và dữ liệu cục bộ
├── Phancongviec.docx                 # Tài liệu phân công tại root
├── Dashboard/
│   ├── frontend/                     # Giao diện React + TypeScript + Vite
│   │   ├── src/
│   │   │   ├── app/                  # Khung ứng dụng và điều hướng
│   │   │   ├── components/           # Thành phần giao diện dùng chung
│   │   │   ├── features/              # Màn hình/nghiệp vụ: mission, map, radar,
│   │   │   │                           # telemetry, alerts, devices, video...
│   │   │   ├── services/              # Kết nối và adapter dữ liệu
│   │   │   ├── state/                 # State/reducer của ứng dụng
│   │   │   ├── mocks/                 # Dữ liệu và kịch bản mô phỏng
│   │   │   ├── types/                 # Kiểu dữ liệu TypeScript
│   │   │   ├── lib/                   # Tiện ích
│   │   │   └── styles/                # CSS/theme
│   │   ├── tests/                     # Kiểm tra browser/UI
│   │   ├── package.json               # Lệnh và dependency frontend
│   │   └── package-lock.json          # Khóa phiên bản npm
│   ├── backend/                      # Backend FastAPI cho ứng dụng GCS
│   │   ├── main.py                    # Khởi tạo API và WebSocket
│   │   ├── config.py                  # Cấu hình backend
│   │   ├── schemas.py                 # Schema dữ liệu ứng dụng
│   │   ├── state.py                   # State, publish và hàng đợi client
│   │   ├── mock_source.py             # Sinh dữ liệu MOCK
│   │   ├── sqlite_logger.py           # Ghi sự kiện vào SQLite
│   │   ├── replay_engine.py           # Đọc và phát lại session đã ghi
│   │   ├── requirements.txt           # Dependency Python backend
│   │   └── tests/                     # Test API, logger, state và replay
│   └── tests/                        # Thư mục kiểm thử Dashboard cấp cao
├── ai_training/
│   ├── inference_adapter.py           # Adapter suy luận tham chiếu PC
│   ├── ontology.yaml                  # Class/ontology và cấu hình dữ liệu
│   ├── releases/                      # Template hồ sơ phát hành model
│   ├── dataset_4k_yolo/                # Dataset và nhãn cục bộ
│   ├── manifests/                     # Manifest ảnh, session, calibration...
│   ├── raw_images/ raw_videos/         # Dữ liệu đầu vào cục bộ
│   ├── dataset_exports/                # Bản xuất dữ liệu
│   ├── evaluation_videos/              # Video đánh giá cục bộ
│   ├── runs/                           # Kết quả train/đánh giá
│   ├── weights/                        # Checkpoint/model cục bộ
│   └── README.md                       # Hướng dẫn và giới hạn evidence AI
├── scripts/
│   ├── ai/                            # Train/monitor AI và báo cáo
│   ├── data/                          # Manifest, remap, augmentation, validator
│   ├── test_video.py                  # Thử pipeline video trên PC
│   ├── test_webcam.py                 # Thử webcam trên PC
│   └── kvc-review.ps1                 # Wrapper workflow review theo dự án
├── tests/                             # Test adapter và công cụ dữ liệu AI
├── docs/
│   ├── KVC_ThietKeHeThong.md           # Kiến trúc, BOM, giao thức draft, nghiệm thu
│   ├── KVC_PROJECT_STATUS.md           # Trạng thái theo bằng chứng và việc còn thiếu
│   ├── KVC_DOCUMENT_INDEX.md           # Danh mục tài liệu chuẩn
│   ├── planning/                       # Phân công, checklist, backlog, rủi ro
│   ├── gcs/                            # Kế hoạch, data contract và thiết kế GCS
│   ├── ai/                             # Chuẩn bị dữ liệu AI
│   ├── demo/                           # Kịch bản demo
│   └── hardware/
│       ├── onekiwi20k/                 # Tài liệu board hãng; file gốc có thể để riêng
│       ├── sonix_sn34f788/             # SDK/tài liệu hãng MCU (nếu có quyền phân phối)
│       ├── CHIP_ONEKIWI_20K_GOWIN_GW2A.md
│       └── CHIP_SONIX_SN34F788_MCU.md
├── media/                              # Tư liệu minh họa cục bộ, không mặc định commit
└── review/                             # Log/evidence review cục bộ, Git ignored
```

**Các thư mục cục bộ có thể không nằm trong Git:** `.venv/` là môi trường Python; `Dashboard/frontend/node_modules/` là dependency npm; `media/`, `review/`, model, dataset và kết quả chạy có thể bị `.gitignore` loại khỏi commit. Vì vậy cây trên mô tả vị trí và vai trò trong workspace, không đảm bảo mọi file dữ liệu được phân phối cùng repository.

## Trạng thái các phân hệ

| Phân hệ | Source hiện có | Giới hạn cần nhớ |
| --- | --- | --- |
| Dashboard frontend | React/TypeScript/Vite; LOCAL dùng generator trong trình duyệt; có adapter cho backend và các màn hình giám sát | UI/fixture không chứng minh dữ liệu phần cứng; bản đồ nền cần tile server hoặc Internet |
| Backend GCS | FastAPI MOCK, schema/state, WebSocket, SQLite logger, session và replay | Chưa có serial ingress/parser RF/USB; MOCK/SIMULATED không phải dữ liệu thiết bị thật |
| AI | YOLO11n hai lớp person/lifebuoy là lựa chọn dự án; có adapter, script PC, dataset/manifests và báo cáo | PC_REFERENCE; provenance/QA/release còn điều kiện; chưa chứng minh chạy trên FPGA hay độ chính xác INT8 |
| FPGA/MCU và RF | Có tài liệu board/chip/SDK tham khảo | Inventory hiện tại chưa có source/project RTL và firmware KVC dạng rời đã xác minh; chưa có build, synthesis, flash hay đo trên bo |

Kết quả test/build được lưu theo từng lượt công việc; không xem test PASS hoặc mục tiêu trong thiết kế là nghiệm thu phần cứng. Trạng thái chi tiết và mức evidence nằm trong [KVC_PROJECT_STATUS.md](docs/KVC_PROJECT_STATUS.md).

## Bắt đầu chạy phần mềm

### Frontend LOCAL (mặc định)

Yêu cầu Node.js/npm tương thích với dependency trong `package-lock.json`.

```powershell
Set-Location Dashboard/frontend
npm ci
npm run dev
```

Vite in địa chỉ local trong terminal. LOCAL dùng dữ liệu mô phỏng trên trình duyệt, không cần backend và không ghi session vào SQLite.

### Backend MOCK và frontend BACKEND

Mở terminal thứ nhất tại thư mục gốc để cài và chạy backend:

```powershell
Set-Location D:\Project_UAV_KVC
# Chỉ tạo môi trường nếu .venv chưa tồn tại.
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r Dashboard/backend/requirements.txt
.venv/Scripts/python.exe -m Dashboard.backend.main
```

Backend mặc định bind `127.0.0.1:8000`. SQLite session mặc định ghi dưới `data/sessions/` tính từ thư mục chạy; dữ liệu này là cục bộ.

Mở terminal thứ hai để chạy frontend ở chế độ BACKEND:

```powershell
Set-Location D:\Project_UAV_KVC\Dashboard\frontend
$env:VITE_MOCK_TRANSPORT = 'BACKEND'
npm ci
npm run dev -- --host 127.0.0.1 --port 5173
```

`VITE_MOCK_TRANSPORT=BACKEND` chọn FastAPI MOCK + SQLite. Backend không tự chuyển sang LOCAL khi WebSocket mất kết nối. Để trở lại mặc định, đóng terminal hoặc chạy `Remove-Item Env:VITE_MOCK_TRANSPORT`. Không đặt API key, token hay mật khẩu trong biến `VITE_*`; giá trị Vite có thể được đóng gói vào mã frontend.

### Chạy test phần mềm

Các lệnh dưới đây chạy từ thư mục gốc, sau khi đã cài dependency tương ứng:

```powershell
.venv/Scripts/python.exe -B -m pytest Dashboard/backend/tests tests -q -p no:cacheprovider
.venv/Scripts/python.exe -B -m Dashboard.backend.tests.test_api_websocket
```

Frontend:

```powershell
Set-Location Dashboard/frontend
npm run typecheck
npm run lint
npm test
npm run build
```

Các test adapter dùng dữ liệu giả. `scripts/test_webcam.py` có thể mở camera; script biến đổi/ghi manifest có thể tạo hoặc sửa dữ liệu. Đọc script và tài liệu liên quan trước khi chạy. Test phần mềm không thay thế testbench, synthesis hoặc kiểm tra trên phần cứng.

## Dữ liệu, model và file cục bộ

- Dataset ảnh/video, nhãn backup, cache, training runs và weights được quản lý riêng; không mặc định đưa lên GitHub. `ai_training/README.md` và [hướng dẫn chuẩn bị dữ liệu](docs/ai/KVC_AI_DATA_PREPARATION.md) nêu provenance, license và QA cần có.
- Manifest là hồ sơ cần kiểm chứng, không tự động đồng nghĩa dữ liệu đã được xác thực.
- Không commit secrets, `.env`, token, private key, môi trường ảo, `node_modules`, build output hoặc dữ liệu phiên bay thật.
- Trước khi chia sẻ tài liệu hãng/SDK trong `docs/hardware/`, kiểm tra quyền phân phối lại. `.gitignore` hiện đã loại một số SDK, nhưng hãy kiểm tra chính xác danh sách staged trước khi push.
- Tài liệu PDF/ảnh của hãng trong `docs/hardware/onekiwi20k/` được bỏ khỏi commit mặc định cho đến khi xác minh quyền phân phối; tham khảo các ghi chú phần cứng trong `docs/hardware/`.
- Khi chuẩn bị commit, xem `git status --short` và `git diff --cached --stat`; stage theo file/thư mục đã rà soát thay vì mặc định thêm toàn bộ workspace.

## Tài liệu nên đọc

1. [Tiến độ dự án](docs/KVC_PROJECT_STATUS.md) — phần đã có, evidence và blocker.
2. [Thiết kế hệ thống](docs/KVC_ThietKeHeThong.md) — kiến trúc, BOM, giao thức draft và tiêu chí nghiệm thu.
3. [Danh mục tài liệu](docs/KVC_DOCUMENT_INDEX.md) — nguồn chuẩn theo chủ đề.
5. [Tài liệu GCS](docs/gcs/) — kế hoạch, data contract và thiết kế frontend/backend.
6. [Tài liệu AI](ai_training/README.md) và [chuẩn bị dữ liệu](docs/ai/KVC_AI_DATA_PREPARATION.md).
7. [Tài liệu phần cứng](docs/hardware/) — OneKiwi, Gowin và Sonix; cần phân biệt tài liệu thiết kế với phép đo thực tế.
8. [Tài liệu Dashboard](Dashboard/frontend/README.md), [Backend](Dashboard/backend/README.md), [scripts](scripts/README.md) và [docs/README.md](docs/README.md).

---

**Quy ước giao thức:** không tự thay baud, packet layout, CRC, IRQ, pinout hoặc giao thức phần cứng. Cần chốt thay đổi qua tài liệu và task được giao trước khi triển khai.
