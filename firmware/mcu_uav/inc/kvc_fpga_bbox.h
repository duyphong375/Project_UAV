/**
 * @file kvc_fpga_bbox.h
 * @brief Driver thu nhận và giải mã khung BBox từ FPGA OneKiwi qua UART1 trên MCU Sonix SN34F788.
 *
 * Đối chiếu tài liệu đặc tả chuẩn:
 * - docs/interfaces/IF_FPGA_MCU_UART.md (IF-01)
 * - docs/hardware/KVC_MASTER_PINOUT_WIRING.md (Mục 3.5: P2.3 URXD1, P2.2 UTXD1)
 * - firmware/mcu_uav/inc/kvc_pinout.h
 *
 * Người phụ trách phân hệ MCU UAV: Nguyễn Tá Duy Phong
 */

#ifndef KVC_FPGA_BBOX_H
#define KVC_FPGA_BBOX_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ============================================================================
 * 1. HẰNG SỐ GIAO THỨC BBOX IF-01 (FPGA -> MCU)
 * ============================================================================ */
#define KVC_FPGA_SYNC0              0x5AU
#define KVC_FPGA_SYNC1              0xA5U
#define KVC_FPGA_VERSION            0x01U
#define KVC_FPGA_MAX_CANDIDATES     20U     /* Tối đa 20 mục tiêu trong 1 frame */
#define KVC_FPGA_TIMEOUT_MS         2000UL  /* Hạn định thời dữ liệu mới (2.0 giây) */

/* Cấu hình UART1 */
#define KVC_FPGA_UART_BAUD          38400UL
/* Với UCLK = 12 MHz, Divisor = round(12000000 / (16 * Baud)) */
#if (KVC_FPGA_UART_BAUD == 115200UL)
#define KVC_FPGA_UART_DLL           0x06U   /* DLL = 6 */
#elif (KVC_FPGA_UART_BAUD == 38400UL)
#define KVC_FPGA_UART_DLL           0x14U   /* DLL = 20 (0x14) */
#else
#define KVC_FPGA_UART_DLL           0x4EU   /* DLL = 78 cho 9600 */
#endif

/* Phân loại mục tiêu từ AI */
#define KVC_FPGA_CLASS_NONE         0U
#define KVC_FPGA_CLASS_PERSON       1U      /* Người trôi dạt */
#define KVC_FPGA_CLASS_LIFEBUOY     2U      /* Phao cứu sinh / Thuyền bè */

/* ============================================================================
 * 2. CẤU TRÚC DỮ LIỆU BBOX VÀ FRAME TRẠNG THÁI (LITTLE-ENDIAN)
 * ============================================================================ */
#pragma pack(push, 1)
typedef struct {
    uint16_t x_center;      /* Tọa độ tâm X trên ảnh (pixel, 0..640) */
    uint16_t y_center;      /* Tọa độ tâm Y trên ảnh (pixel, 0..480) */
    uint8_t  width;         /* Bề rộng BBox (pixel) */
    uint8_t  height;        /* Chiều cao BBox (pixel) */
    uint8_t  class_id;      /* 1 = person, 2 = lifebuoy */
    uint8_t  confidence;    /* Mức độ tin cậy AI (0..100 %) */
} KvcFpgaBBoxItem;
#pragma pack(pop)

/* Đảm bảo struct BBox Item đúng 8 byte chuẩn IF-01 */
typedef char kvc_bbox_item_size_check[(sizeof(KvcFpgaBBoxItem) == 8) ? 1 : -1];

typedef struct {
    uint32_t        timestamp_ms;       /* Thời điểm chụp/suy luận của ảnh từ FPGA (ms) */
    uint32_t        last_rx_ms;         /* Timestamp mili-giây nhận frame hợp lệ gần nhất */
    uint8_t         candidate_count;    /* Số lượng mục tiêu trong frame (0..20) */
    KvcFpgaBBoxItem targets[KVC_FPGA_MAX_CANDIDATES];
    bool            valid;              /* true khi có dữ liệu hợp lệ trong 2.0 giây */
    uint32_t        rx_frame_count;     /* Tổng số frame nhận thành công */
    uint32_t        crc_err_count;      /* Tổng số frame lỗi CRC */
} KvcFpgaFrameState;

/* ============================================================================
 * 3. GIAO DIỆN HÀM API NGOÀI
 * ============================================================================ */

/**
 * @brief Khởi tạo phần cứng UART1 trên Sonix SN34F788 (P2.3 URXD1, P2.2 UTXD1)
 */
void kvc_fpga_bbox_init(void);

/**
 * @brief Đặt lại máy trạng thái và xóa dữ liệu BBox
 */
void kvc_fpga_bbox_reset(void);

/**
 * @brief Đọc bộ đệm FIFO UART1 theo cơ chế Polling không chặn.
 *        Cần gọi định kỳ trong vòng lặp chính (ví dụ mỗi nhịp 1 ms).
 * @param now_ms Timestamp hiện tại (mili-giây).
 */
void kvc_fpga_bbox_poll(uint32_t now_ms);

/**
 * @brief Nạp trực tiếp 1 byte dữ liệu UART vào bộ giải mã.
 *        Hàm này độc lập phần cứng, dùng cho cả Polling thực tế và Host Unit Test.
 * @param b Byte dữ liệu nhận được.
 * @param now_ms Timestamp mili-giây tại thời điểm nhận.
 */
void kvc_fpga_bbox_feed_byte(uint8_t b, uint32_t now_ms);

/**
 * @brief Kiểm tra xem dữ liệu BBox hiện tại có hợp lệ và còn mới trong 2 giây hay không.
 * @return true nếu còn mới và hợp lệ.
 */
bool kvc_fpga_bbox_is_valid(void);

/**
 * @brief Trả về con trỏ hằng tới cấu trúc trạng thái frame nội bộ.
 */
const KvcFpgaFrameState* kvc_fpga_bbox_get_state(void);

/**
 * @brief Lấy mục tiêu ưu tiên số 1 (độ tin cậy cao nhất hoặc mục tiêu đầu tiên).
 * @return Con trỏ tới BBox mục tiêu, hoặc NULL nếu không có mục tiêu nào.
 */
const KvcFpgaBBoxItem* kvc_fpga_bbox_get_primary_target(void);

/**
 * @brief Kiểm tra hạn định thời dữ liệu và hạ cờ valid nếu quá 2.0 giây không có bản tin mới.
 */
void kvc_fpga_bbox_check_expiry(uint32_t now_ms);

#ifdef __cplusplus
}
#endif

#endif /* KVC_FPGA_BBOX_H */
