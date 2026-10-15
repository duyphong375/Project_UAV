# KVC — Tải nhiệm vụ UAV tìm kiếm cứu nạn bão lũ

KVC là tải nhiệm vụ giám sát, phát hiện và định vị mục tiêu cứu nạn cho UAV trong tình huống bão lũ. Hệ thống dự kiến kết hợp camera và AI, cảm biến định vị, liên kết vô tuyến, trạm thu mặt đất và phần mềm GCS (Ground Control Station).

> **Phạm vi:** KVC là payload và hệ thống giám sát nhiệm vụ, không phải flight controller. KVC không điều khiển bay, arm/disarm hoặc lập lộ trình waypoint.

Tài liệu thiết kế mô tả mục tiêu và cấu hình dự kiến; không tự nó chứng minh phần cứng hoặc hiệu năng đã được đo. Xem [Tiến độ dự án](docs/KVC_PROJECT_STATUS.md) để biết phần nào đã có bằng chứng và phần nào còn thiếu.

## Mục lục

- [Tổng quan kiến trúc](#tổng-quan-kiến-trúc)
- [Cấu trúc repository](#cấu-trúc-repository)
- [Trạng thái các phân hệ](#trạng-thái-các-phân-hệ)
- [Bắt đầu chạy phần mềm](#bắt-đầu-chạy-phần-mềm)
- [Chạy test phần mềm](#chạy-test-phần-mềm)
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
              ESP32 trạm đất (nguồn riêng)
                              ↓ Wi-Fi SoftAP / WebSocket
            Backend GCS trên laptop → Dashboard web
                              ↓
                    Lưu phiên / phát lại
```

Source hiện tại tập trung vào **Dashboard GCS**, **backend MOCK có lưu phiên/replay**, và **AI tham chiếu chạy trên PC**. Luồng từ cảm biến/RF trên thiết bị thật qua ESP32 vào GCS chưa được triển khai và xác minh. ESP32 trạm đất dùng nguồn riêng và tiếp tục thu LoRa khi laptop tắt; laptop chạy backend GCS để nhận/lưu/phát lại dữ liệu và hiển thị Dashboard web. Wi-Fi SoftAP/WebSocket v1 là baseline thiết kế, chưa xác minh. RF 32 byte vẫn là dự thảo ABI; USB envelope 48 byte thuộc kiến trúc cũ và không còn là giao diện mục tiêu. Telemetry 20 byte là ghi nhận source lịch sử. Không tự suy ra baud, packet layout, CRC, IRQ hoặc pinout từ sơ đồ trên.

## Cấu trúc repository

```text
KVC/
├── README.md                         # Điểm vào dự án này
├── .gitignore                        # Loại môi trường, artifact và dữ liệu cục bộ
├── fpga/                             # Phân hệ FPGA OneKiwi Primer 20K (Vững)
│   ├── tb/                           # Testbench mô phỏng RTL riêng biệt
│   └── README.md                     # Hướng dẫn project Gowin EDA và link IF-01
├── firmware/                         # Mã nguồn vi điều khiển
│   ├── README.md                     # Tổng quan phân hệ nhúng, phân định Sonix vs ESP32
│   ├── mcu_uav/                      # Firmware MCU Sonix SN34F788 trên UAV (Phong)
│   │   └── README.md                 # Hướng dẫn project Keil MDK, link IF-01 và IF-02
│   └── gateway_esp32/                # Firmware Gateway trạm đất ESP32 (Thịnh)
│       ├── platformio.ini            # Cấu hình PlatformIO (framework = arduino)
│       └── README.md                 # Hướng dẫn và link IF-02, IF-03
├── Dashboard/
│   ├── README.md                     # Tổng quan trạm mặt đất GCS, kiến trúc 2 tầng (ESP32 -> Backend -> Frontend)
│   ├── frontend/                     # Giao diện React + TypeScript + Vite
│   │   ├── src/
│   │   │   ├── app/                  # Khung ứng dụng và điều hướng
│   │   │   ├── components/           # Thành phần giao diện dùng chung
│   │   │   ├── features/             # Màn hình/nghiệp vụ: mission, map, radar,
│   │   │   │                         # telemetry, alerts, devices, video...
│   │   │   ├── services/             # Kết nối và adapter dữ liệu
│   │   │   ├── state/                # State/reducer của ứng dụng
│   │   │   ├── mocks/                # Dữ liệu và kịch bản mô phỏng
│   │   │   ├── types/                # Kiểu dữ liệu TypeScript
│   │   │   ├── lib/                  # Tiện ích
│   │   │   └── styles/               # CSS/theme
│   │   ├── tests/                    # Kiểm tra browser/UI
│   │   ├── package.json              # Lệnh và dependency frontend
│   │   └── package-lock.json         # Khóa phiên bản npm
│   ├── backend/                      # Backend FastAPI cho ứng dụng GCS
│   │   ├── main.py                   # Khởi tạo API và WebSocket
│   │   ├── config.py                 # Cấu hình backend
│   │   ├── schemas.py                # Schema dữ liệu ứng dụng
│   │   ├── state.py                  # State, publish và hàng đợi client
│   │   ├── mock_source.py            # Sinh dữ liệu MOCK
│   │   ├── sqlite_logger.py          # Ghi sự kiện vào SQLite
│   │   ├── replay_engine.py          # Đọc và phát lại session đã ghi
│   │   ├── requirements.txt          # Dependency Python backend
│   │   └── tests/                    # Test API, logger, state và replay
│   └── tests/                        # Thư mục kiểm thử Dashboard cấp cao
├── ai_training/
│   ├── inference_adapter.py          # Adapter suy luận tham chiếu PC
│   ├── ontology.yaml                 # Class/ontology và cấu hình dữ liệu
│   ├── releases/                     # Template hồ sơ phát hành model
│   ├── weights/                      # Model weights: yolo11n ONNX (FPGA) và PyTorch (.pt)
│   │   ├── yolo11n_2class_best.onnx  # Model ONNX chuẩn hóa cho Gowin GoAI
│   │   ├── yolo11n_2class_best.pt    # Checkpoint gốc PyTorch
│   │   └── README.md                 # Thông số kỹ thuật và mã băm SHA-256
│   ├── calibration_images/           # 100 ảnh hiệu chuẩn cân bằng cho INT8 PTQ
│   ├── manifests/                    # Manifest kiểm soát (calibration_manifest.csv...)
│   ├── dataset_4k_yolo/              # Dataset và nhãn cục bộ (không commit)
│   ├── runs/                         # Kết quả train/đánh giá cục bộ
│   └── README.md                     # Hướng dẫn và giới hạn evidence AI
├── scripts/
│   ├── README.md                     # Tổng quan các công cụ huấn luyện, thẩm định và review
│   ├── ai/                           # Script train, monitor và export_onnx.py
│   ├── data/                         # prepare_calibration_dataset, remap, augment
│   ├── test_video.py                 # Thử pipeline video trên PC
│   └── test_webcam.py                # Thử webcam trên PC
├── tests/                            # Bộ kiểm thử cấp hệ thống trên PC
│   ├── README.md                     # Hướng dẫn bộ test tự động pytest và ranh giới kiểm thử
│   ├── test_ai_data_tools.py         # Test công cụ dữ liệu AI
│   ├── test_inference_adapter.py     # Test adapter suy luận
│   └── test_inference_integration.py # Test tích hợp chuỗi AI
├── docs/
│   ├── README.md                     # Mục lục điều hướng tài liệu toàn dự án
│   ├── KVC_ThietKeHeThong.md         # Kiến trúc, BOM, giao thức draft, nghiệm thu
│   ├── interfaces/                   # Quản lý tập trung hợp đồng giao diện toàn hệ thống
│   │   ├── README.md                 # Ma trận luồng dữ liệu toàn chuỗi và topology
│   │   ├── IF_CAMERA_FPGA.md         # Camera DVP/MIPI ➔ FPGA OneKiwi GW2A
│   │   ├── IF_MCU_SENSORS.md         # [IF-00] Cảm biến định vị tải UAV (LiDAR, IMU, GNSS)
│   │   ├── IF_FPGA_MCU_UART.md       # [IF-01] UART BBox: FPGA (Vững) ➔ MCU Sonix (Phong)
│   │   ├── IF_MCU_LORA_RF.md         # [IF-02] LoRa Telemetry: MCU Sonix (Phong) ➔ ESP32 (Thịnh)
│   │   └── IF_ESP32_GCS_WS.md        # [IF-03] Wi-Fi WS: ESP32 (Thịnh) ➔ Backend GCS Laptop
│   ├── KVC_PROJECT_STATUS.md         # Trạng thái theo bằng chứng và việc còn thiếu
│   ├── KVC_DOCUMENT_INDEX.md         # Danh mục tài liệu chuẩn
│   ├── KVC_MARKDOWN_STANDARD.md      # Chuẩn biên tập tài liệu Markdown
│   ├── planning/                     # Phân công, checklist 5 người, phân tích rủi ro
│   ├── gcs/                          # Kế hoạch, data contract và thiết kế GCS
│   ├── ai/                           # Chuẩn bị dữ liệu AI
│   ├── demo/                         # Kịch bản demo
│   └── hardware/
│       ├── onekiwi20k/               # Tài liệu board hãng; file gốc có thể để riêng
│       ├── sonix_sn34f788/           # SDK/tài liệu hãng MCU (nếu có quyền phân phối)
│       ├── CHIP_ONEKIWI_20K_GOWIN_GW2A.md
│       └── CHIP_SONIX_SN34F788_MCU.md
├── media/                            # Tư liệu minh họa cục bộ, không mặc định commit
└── review/                           # Log/evidence review cục bộ, Git ignored
```

> 🔗 **Lối tắt truy cập nhanh (Bấm để mở trực tiếp):**
> - [📂 **fpga/** — Phân hệ FPGA OneKiwi Primer 20K (Vững)](fpga/README.md)
> - [📂 **firmware/mcu_uav/** — Phân hệ MCU Sonix SN34F788 trên UAV (Phong)](firmware/mcu_uav/README.md)
> - [📂 **firmware/gateway_esp32/** — Phân hệ Gateway ESP32 Trạm Đất (Thịnh)](firmware/gateway_esp32/README.md)
> - [📑 **docs/interfaces/** — Trung tâm quản lý đặc tả giao diện toàn chuỗi](docs/interfaces/README.md)
> - [💻 **Dashboard/** — Trạm mặt đất GCS (Frontend & Backend)](Dashboard/frontend/README.md)
> - [🧠 **ai_training/** — Huấn luyện & Đánh giá mô hình AI](ai_training/README.md)

**Các thư mục cục bộ có thể không nằm trong Git:** `.venv/` là môi trường Python; `Dashboard/frontend/node_modules/` là dependency npm; `media/`, `review/`, model, dataset và kết quả chạy có thể bị `.gitignore` loại khỏi commit. Vì vậy cây trên mô tả vị trí và vai trò trong workspace, không đảm bảo mọi file dữ liệu được phân phối cùng repository.

## Trạng thái các phân hệ

| Phân hệ | Source hiện có | Giới hạn cần nhớ |
| --- | --- | --- |
| Dashboard frontend | React/TypeScript/Vite; LOCAL dùng generator trong trình duyệt; có adapter cho backend và các màn hình giám sát | UI/fixture không chứng minh dữ liệu phần cứng; bản đồ nền cần tile server hoặc Internet |
| Backend GCS | FastAPI MOCK, schema/state, WebSocket, SQLite logger, session và replay | Chưa có ingress Wi-Fi/WebSocket từ ESP32 hoặc parser RF; MOCK/SIMULATED không phải dữ liệu thiết bị thật |
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
# Mở terminal tại thư mục gốc repository
# Chỉ tạo môi trường nếu .venv chưa tồn tại:
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r Dashboard/backend/requirements.txt
.venv/Scripts/python.exe -m Dashboard.backend.main
```

Backend mặc định bind `127.0.0.1:8000`. SQLite session mặc định ghi dưới `data/sessions/` tính từ thư mục chạy; dữ liệu này là cục bộ.

Mở terminal thứ hai để chạy frontend ở chế độ BACKEND:

```powershell
Set-Location Dashboard/frontend
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

- Checkpoint mô hình chính thức đã được xuất chuẩn hóa trong `ai_training/weights/` (`yolo11n_2class_best.onnx` cho FPGA và `yolo11n_2class_best.pt` cho PyTorch), kèm tập 100 ảnh hiệu chuẩn cân bằng `ai_training/calibration_images/` và `calibration_manifest.csv`.
- Toàn bộ tập dataset ảnh/video 4K gốc (`dataset_4k_yolo/images/`, `labels/`), cache và các thư mục `runs/` huấn luyện được quản lý cục bộ trên máy để giữ repository tinh gọn. `ai_training/README.md` và [hướng dẫn chuẩn bị dữ liệu](docs/ai/KVC_AI_DATA_PREPARATION.md) nêu provenance, license và QA cần có.
- Manifest là hồ sơ cần kiểm chứng, không tự động đồng nghĩa dữ liệu đã được xác thực.
- Không commit secrets, `.env`, token, private key, môi trường ảo, `node_modules`, build output hoặc dữ liệu phiên bay thật.
- Trước khi chia sẻ tài liệu hãng/SDK trong `docs/hardware/`, kiểm tra quyền phân phối lại. `.gitignore` hiện đã loại một số SDK, nhưng hãy kiểm tra chính xác danh sách staged trước khi push.
- Tài liệu PDF/ảnh của hãng trong `docs/hardware/onekiwi20k/` được bỏ khỏi commit mặc định cho đến khi xác minh quyền phân phối; tham khảo các ghi chú phần cứng trong `docs/hardware/`.
- Khi chuẩn bị commit, xem `git status --short` và `git diff --cached --stat`; stage theo file/thư mục đã rà soát thay vì mặc định thêm toàn bộ workspace.

## Tài liệu nên đọc

1. [Tiến độ dự án](docs/KVC_PROJECT_STATUS.md) — phần đã có, evidence và blocker.
2. [Thiết kế hệ thống](docs/KVC_ThietKeHeThong.md) — kiến trúc, BOM, giao thức draft và tiêu chí nghiệm thu.
3. [Danh mục tài liệu](docs/KVC_DOCUMENT_INDEX.md) — nguồn chuẩn theo chủ đề.
4. [Đặc tả giao diện toàn chuỗi](docs/interfaces/) — ma trận kết nối cảm biến IF-00, UART BBox IF-01, LoRa RF IF-02 và Wi-Fi WebSocket IF-03.
5. [Tài liệu GCS](docs/gcs/) — kế hoạch, data contract và thiết kế frontend/backend.
6. [Tài liệu AI](ai_training/README.md) và [chuẩn bị dữ liệu](docs/ai/KVC_AI_DATA_PREPARATION.md).
7. [Tài liệu phần cứng](docs/hardware/) — OneKiwi, Gowin và Sonix; cần phân biệt tài liệu thiết kế với phép đo thực tế.
8. [Chuẩn tài liệu Markdown](docs/KVC_MARKDOWN_STANDARD.md) — quy ước định dạng và trạng thái tài liệu.
9. [Tài liệu Dashboard](Dashboard/frontend/README.md), [Backend](Dashboard/backend/README.md), [scripts](scripts/README.md) và [docs/README.md](docs/README.md).

---

**Quy ước giao thức:** không tự thay baud, packet layout, CRC, IRQ, pinout hoặc giao thức phần cứng. Cần chốt thay đổi qua tài liệu và task được giao trước khi triển khai.
