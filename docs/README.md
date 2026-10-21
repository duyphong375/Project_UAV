# Tài liệu dự án KVC

## Đọc nhanh

1. [Tiến độ dự án](KVC_PROJECT_STATUS.md): phần đã có và phần còn thiếu.
2. [Phân công 5 người](planning/KVC_PHAN_CONG_5_NGUOI.md): nhiệm vụ chính.
3. [Checklist chi tiết](planning/KVC_CONG_VIEC_CHI_TIET_5_NGUOI.md): việc cần làm để hoàn thiện.
4. [Thiết kế hệ thống](KVC_ThietKeHeThong.md): kiến trúc, bảng 29 linh kiện kèm chức năng/In/Out, giao thức dự thảo và tiêu chí đo.
5. [Kịch bản demo](demo/KVC_DEMO.md): hai video và thử trực tiếp không sa bàn.
6. [Chuẩn Markdown](KVC_MARKDOWN_STANDARD.md): quy tắc cấu trúc, thuật ngữ, trạng thái và tham chiếu.
7. [Đặc tả giao diện](interfaces/): ma trận giao diện toàn chuỗi (IF-01 UART BBox, IF-02 LoRa RF, IF-03 Wi-Fi WS).
8. [Bản đồ chân Master](hardware/KVC_MASTER_PINOUT_WIRING.md): bản đồ phân bổ chân và đấu nối toàn hệ thống KVC (MCU Sonix, cảm biến, LoRa, ESP32, FPGA).

## Các nhóm tài liệu

| Thư mục/file | Nội dung |
| --- | --- |
| interfaces/ | Đặc tả hợp đồng giao diện toàn chuỗi (UART BBox, LoRa RF, Wi-Fi SoftAP/WS) |
| planning/ | Phân công, checklist, backlog kỹ thuật và phân tích rủi ro |
| demo/ | Kịch bản trình diễn hiện hành |
| gcs/ | Kế hoạch, dữ liệu và thiết kế Dashboard |
| ai/ | Chuẩn bị và kiểm dữ liệu AI |
| hardware/ | Hồ sơ bo/chip, bản đồ chân master, datasheet, tài liệu và SDK hãng |
| KVC_AI_WORKFLOW.md | Quy trình task, kiểm thử và review |
| KVC_DOCUMENT_INDEX.md | Danh mục đầy đủ và vai trò từng tài liệu |
| KVC_MARKDOWN_STANDARD.md | Chuẩn biên tập dùng chung cho tài liệu Markdown |

## Cấu trúc thư mục tài liệu

```text
docs/
├── KVC_ThietKeHeThong.md     # Tài liệu thiết kế hệ thống gốc: kiến trúc, 29 linh kiện, giao thức
├── KVC_AI_WORKFLOW.md        # Quy trình task, vai trò Codex/Antigravity, kiểm thử và review
├── KVC_DOCUMENT_INDEX.md     # Danh mục toàn bộ tài liệu dự án và vai trò từng file
├── KVC_MARKDOWN_STANDARD.md  # Chuẩn biên tập Markdown, định dạng bảng, link và thuật ngữ
├── KVC_PROJECT_STATUS.md     # Báo cáo tiến độ: phần đã có vs phần còn thiếu
│
├── interfaces/               # [TRUNG TÂM GIAO DIỆN] Đặc tả hợp đồng toàn chuỗi (IF-01 -> IF-03)
│   ├── README.md             # Ma trận tổng quan luồng dữ liệu toàn hệ thống
│   ├── IF_CAMERA_FPGA.md     # Giao diện Camera quang học -> FPGA OneKiwi
│   ├── IF_FPGA_MCU_UART.md   # [IF-01] UART BBox: FPGA -> MCU Sonix (0x5A 0xA5, 115.200 bps)
│   ├── IF_MCU_SENSORS.md     # Giao tiếp UART/I2C: Cảm biến (AJ-SR04M siêu âm, GY-87 IMU 10-DOF, NEO-M8N) -> MCU
│   ├── IF_MCU_LORA_RF.md     # [IF-02] Gói tin không dây LoRa 433MHz: MCU -> Gateway ESP32
│   ├── IF_ESP32_GCS_WS.md    # [IF-03] Wi-Fi SoftAP / WebSocket: Gateway ESP32 -> Backend GCS
│   └── IF_GCS_DATA_CONTRACT.md # Chuẩn dữ liệu JSON nội bộ GCS giữa Backend và Frontend
│
├── hardware/                 # Hồ sơ kỹ thuật phần cứng, datasheet và SDK
│   ├── onekiwi20k/           # Sơ đồ khối, User Guide, pinout kit FPGA OneKiwi Primer 20K
│   ├── sonix_sn34f788/       # Datasheet, User Manual, Keil Pack & SDK chip Sonix SN34F788
│   ├── KVC_MASTER_PINOUT_WIRING.md # [MASTER] Bản đồ phân bổ chân và đấu nối toàn hệ thống KVC
│   ├── CHIP_ONEKIWI_20K_GOWIN_GW2A.md # Tóm tắt thông số FPGA Gowin GW2A-LV18
│   └── CHIP_SONIX_SN34F788_MCU.md     # Tóm tắt thông số MCU ARM Cortex-M4F 192 MHz Sonix
│
├── planning/                 # Kế hoạch phát triển, phân công và quản lý rủi ro
│   ├── KVC_PHAN_CONG_5_NGUOI.md       # Phân công trách nhiệm 5 thành viên trong nhóm
│   ├── KVC_CONG_VIEC_CHI_TIET_5_NGUOI.md # Checklist công việc chi tiết từng giai đoạn
│   └── KVC_RUI_RO.md                  # Đánh giá và kế hoạch giảm thiểu rủi ro kỹ thuật
│
├── gcs/                      # Tài liệu phân hệ trạm mặt đất GCS
│   ├── KVC_GCS_DESIGN_SPEC.md         # Đặc tả thiết kế giao diện và trải nghiệm người dùng
│   ├── KVC_GCS_DATA_CONTRACT.md       # Chuẩn dữ liệu nội bộ GCS
│   └── KVC_GCS_PLAN.md                # Kế hoạch triển khai frontend/backend GCS
│
├── ai/                       # Tài liệu dữ liệu huấn luyện AI
│   └── KVC_AI_DATA_PREPARATION.md     # Quy chuẩn thu thập, gán nhãn dataset cứu nạn
│
└── demo/                     # Kịch bản demo
    └── KVC_DEMO.md                    # Kịch bản trình diễn video và thử nghiệm thực tế
```

Thiết kế là mục tiêu. Bản thiết kế hiện tại không chứa lịch 21 ngày; mốc cũ trong backlog/GCS chỉ là lịch sử. Kết quả đã làm theo báo cáo tiến độ và log kiểm tra; không suy ra phần cứng đã chạy từ tài liệu.

Kiến trúc GCS hiện hành là LoRa → ESP32 trạm đất có nguồn riêng → Wi-Fi SoftAP/WebSocket → backend GCS trên laptop → Dashboard web. ESP32 không phụ thuộc laptop để nhận LoRa. RF 32 byte còn là dự thảo; giao diện Wi-Fi là baseline thiết kế chưa xác minh. Tài liệu GCS cũ ghi STM32/USB cần được đọc theo nhãn lịch sử/superseded trong chính tài liệu.
