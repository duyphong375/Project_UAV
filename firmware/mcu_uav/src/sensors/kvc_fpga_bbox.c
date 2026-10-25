/**
 * @file kvc_fpga_bbox.c
 * @brief Hiện thực driver thu nhận và giải mã BBox từ FPGA qua UART1 trên MCU Sonix SN34F788.
 *
 * Đối chiếu tài liệu đặc tả chuẩn:
 * - docs/interfaces/IF_FPGA_MCU_UART.md (IF-01)
 * - docs/hardware/KVC_MASTER_PINOUT_WIRING.md (Mục 3.5: P2.3 URXD1, P2.2 UTXD1)
 *
 * Người phụ trách phân hệ MCU UAV: Nguyễn Tá Duy Phong
 */

#include "kvc_fpga_bbox.h"
#include <string.h>

#if defined(__arm__) || defined(__CC_ARM) || defined(__ARMCC_VERSION) || defined(SN34F780)
#include "SN34F780.h"
#include "kvc_pinout.h"
#define KVC_FPGA_HAS_SONIX_HW 1
#else
#define KVC_FPGA_HAS_SONIX_HW 0
#endif

/* ============================================================================
 * 1. MÁY TRẠNG THÁI GIẢI MÃ (FSM)
 * ============================================================================ */
typedef enum {
    STATE_WAIT_SYNC0 = 0,
    STATE_WAIT_SYNC1,
    STATE_READ_HEADER,
    STATE_READ_PAYLOAD,
    STATE_READ_CRC
} FpgaRxState_t;

static FpgaRxState_t     s_fsm_state = STATE_WAIT_SYNC0;
static uint8_t           s_rx_buf[180];      /* Đệm tối đa 8 + 20*8 + 2 = 170 bytes */
static uint16_t          s_buf_idx   = 0;
static uint16_t          s_expected_len = 0;
static KvcFpgaFrameState s_frame_state;

/* ============================================================================
 * 2. HÀM TÍNH TOÁN CRC-16/CCITT-FALSE
 * Poly: 0x1021, Init: 0xFFFF, RefIn: false, RefOut: false, XorOut: 0x0000
 * ============================================================================ */
static uint16_t kvc_bbox_calc_crc16(const uint8_t *data, size_t length) {
    uint16_t crc = 0xFFFFU;
    size_t i;
    uint8_t bit;
    for (i = 0; i < length; i++) {
        crc ^= (uint16_t)((uint16_t)data[i] << 8);
        for (bit = 0; bit < 8; bit++) {
            if (crc & 0x8000U) {
                crc = (uint16_t)(((uint32_t)crc << 1) ^ 0x1021U);
            } else {
                crc = (uint16_t)((uint32_t)crc << 1);
            }
        }
    }
    return crc;
}

/* ============================================================================
 * 3. KHỞI TẠO VÀ ĐẶT LẠI DRIVER
 * ============================================================================ */
void kvc_fpga_bbox_reset(void) {
    s_fsm_state = STATE_WAIT_SYNC0;
    s_buf_idx = 0;
    s_expected_len = 0;
    memset(&s_frame_state, 0, sizeof(s_frame_state));
    s_frame_state.valid = false;
}

void kvc_fpga_bbox_init(void) {
    kvc_fpga_bbox_reset();

#if KVC_FPGA_HAS_SONIX_HW
    /* 1. Cấp xung nhịp ngoại vi UART1 (APB0CLKG bit 4) và GPIO Port 2 (APB1CLKG bit 19) */
    SN_SCU->APB0CLKG |= (1U << 4);                 /* Bit 4: UART1CLKEN */
    SN_SCU->APB1CLKG |= (1U << 14) | (1U << 19);   /* Bit 19: P2CLKEN (kèm bit 14 dự phòng theo DFP) */

    /* 2. Cấu hình chức năng phụ AFIO trong SN_ALWAYSON->P2_AFIO0:
     *    - Chân P2.2: IO2 = 1 -> Chức năng phần cứng UTXD1 (Pin 16 LQFP64 | JP3 Pin 5/6)
     *    - Chân P2.3: IO3 = 1 -> Chức năng phần cứng URXD1 (Pin 17 LQFP64 | JP3 Pin 7/8)
     */
    SN_ALWAYSON->P2_AFIO0 = (SN_ALWAYSON->P2_AFIO0 & ~((0x1FU << 10) | (0x1FU << 15)))
                          | (1U << 10)  /* IO2 = 1: UTXD1 */
                          | (1U << 15); /* IO3 = 1: URXD1 */

    /* 3. Cài đặt Baudrate trên SN_UART1 (Xung nhịp UCLK = 12 MHz):
     *    Bật DLAB (bit 7 LC) để truy cập DLL và DLM */
    SN_UART1->LC |= (1U << 7);
    SN_UART1->DLL = KVC_FPGA_UART_DLL;
    SN_UART1->DLM = 0x00;

    /* 4. Cấu hình khung truyền 8N1 (8 bit dữ liệu, 1 stop bit, không parity) và trả DLAB = 0 */
    SN_UART1->LC = 0x03;          /* WLS = 3 (8-bit), SBS = 0 (1 stop bit), PE = 0 (no parity) */

    /* 5. Kích hoạt và thiết lập lại bộ đệm FIFO 16-byte phần cứng */
    SN_UART1->FIFOCTRL = 0x07;    /* FIFOEN = 1, RXFIFORST = 1, TXFIFORST = 1 */

    /* 6. Vô hiệu hóa ngắt phần cứng UART1 (dùng polling không chặn định kỳ 1 ms) */
    SN_UART1->IE = 0x00;
#endif
}

/* ============================================================================
 * 4. XỬ LÝ DỮ LIỆU TỪNG BYTE (FSM)
 * ============================================================================ */
void kvc_fpga_bbox_feed_byte(uint8_t b, uint32_t now_ms) {
    switch (s_fsm_state) {
        case STATE_WAIT_SYNC0:
            if (b == KVC_FPGA_SYNC0) {
                s_rx_buf[0] = b;
                s_buf_idx = 1;
                s_fsm_state = STATE_WAIT_SYNC1;
            }
            break;

        case STATE_WAIT_SYNC1:
            if (b == KVC_FPGA_SYNC1) {
                s_rx_buf[1] = b;
                s_buf_idx = 2;
                s_fsm_state = STATE_READ_HEADER;
            } else if (b == KVC_FPGA_SYNC0) {
                /* Giữ nguyên chờ Sync1 nếu nhận lại Sync0 liên tiếp */
                s_buf_idx = 1;
            } else {
                s_fsm_state = STATE_WAIT_SYNC0;
            }
            break;

        case STATE_READ_HEADER:
            s_rx_buf[s_buf_idx++] = b;
            /* Header có tổng cộng 8 byte:
             * Byte 0..1: Sync (0x5A 0xA5)
             * Byte 2:    Version (0x01)
             * Byte 3:    Candidate Count N (0..20)
             * Byte 4..7: Timestamp uint32 Little-Endian
             */
            if (s_buf_idx == 8) {
                uint8_t ver = s_rx_buf[2];
                uint8_t count = s_rx_buf[3];

                if (ver != KVC_FPGA_VERSION || count > KVC_FPGA_MAX_CANDIDATES) {
                    /* Sai version hoặc số mục tiêu vượt quá ngưỡng an toàn -> hủy frame */
                    s_fsm_state = STATE_WAIT_SYNC0;
                } else {
                    /* Tính độ dài toàn bộ gói gồm: 8B Header + N * 8B BBox + 2B CRC */
                    s_expected_len = 8U + ((uint16_t)count * 8U) + 2U;
                    if (count == 0) {
                        /* Không có mục tiêu -> nhảy thẳng tới đọc 2 byte CRC */
                        s_fsm_state = STATE_READ_CRC;
                    } else {
                        s_fsm_state = STATE_READ_PAYLOAD;
                    }
                }
            }
            break;

        case STATE_READ_PAYLOAD:
            s_rx_buf[s_buf_idx++] = b;
            if (s_buf_idx == (s_expected_len - 2U)) {
                s_fsm_state = STATE_READ_CRC;
            }
            break;

        case STATE_READ_CRC:
            s_rx_buf[s_buf_idx++] = b;
            if (s_buf_idx == s_expected_len) {
                /* Đã nhận đủ toàn bộ frame! Kiểm tra mã CRC-16 */
                uint16_t received_crc = (uint16_t)s_rx_buf[s_expected_len - 2U] |
                                       ((uint16_t)s_rx_buf[s_expected_len - 1U] << 8);

                uint16_t calculated_crc = kvc_bbox_calc_crc16(s_rx_buf, (size_t)(s_expected_len - 2U));

                if (calculated_crc == received_crc) {
                    /* CRC HỢP LỆ: Trích xuất dữ liệu an toàn */
                    s_frame_state.candidate_count = s_rx_buf[3];
                    s_frame_state.timestamp_ms = (uint32_t)s_rx_buf[4] |
                                                ((uint32_t)s_rx_buf[5] << 8) |
                                                ((uint32_t)s_rx_buf[6] << 16) |
                                                ((uint32_t)s_rx_buf[7] << 24);

                    for (uint8_t i = 0; i < s_frame_state.candidate_count; i++) {
                        const uint8_t *p = &s_rx_buf[8U + (uint16_t)i * 8U];
                        s_frame_state.targets[i].x_center   = (uint16_t)p[0] | ((uint16_t)p[1] << 8);
                        s_frame_state.targets[i].y_center   = (uint16_t)p[2] | ((uint16_t)p[3] << 8);
                        s_frame_state.targets[i].width      = p[4];
                        s_frame_state.targets[i].height     = p[5];
                        s_frame_state.targets[i].class_id   = p[6];
                        s_frame_state.targets[i].confidence = p[7];
                    }

                    s_frame_state.valid = true;
                    s_frame_state.last_rx_ms = now_ms;
                    s_frame_state.rx_frame_count++;
                } else {
                    /* Lỗi CRC */
                    s_frame_state.crc_err_count++;
                }

                /* Quay về chờ frame mới */
                s_fsm_state = STATE_WAIT_SYNC0;
            }
            break;

        default:
            s_fsm_state = STATE_WAIT_SYNC0;
            break;
    }
}

/* ============================================================================
 * 5. POLLING VÀ CÁC HÀM TRUY VẤN DỮ LIỆU
 * ============================================================================ */
void kvc_fpga_bbox_poll(uint32_t now_ms) {
#if KVC_FPGA_HAS_SONIX_HW
    /* Đọc cạn toàn bộ các byte trong FIFO UART1 mà không bao giờ gây treo CPU */
    while (SN_UART1->LS & 0x01) { /* Bit 0: RDR (Receiver Data Ready) */
        uint8_t b = (uint8_t)(SN_UART1->RB & 0xFF);
        kvc_fpga_bbox_feed_byte(b, now_ms);
    }
#endif
    kvc_fpga_bbox_check_expiry(now_ms);
}

void kvc_fpga_bbox_check_expiry(uint32_t now_ms) {
    if (s_frame_state.valid) {
        if ((now_ms - s_frame_state.last_rx_ms) > KVC_FPGA_TIMEOUT_MS) {
            s_frame_state.valid = false;
        }
    }
}

bool kvc_fpga_bbox_is_valid(void) {
    return s_frame_state.valid;
}

const KvcFpgaFrameState* kvc_fpga_bbox_get_state(void) {
    return &s_frame_state;
}

const KvcFpgaBBoxItem* kvc_fpga_bbox_get_primary_target(void) {
    if (!s_frame_state.valid || s_frame_state.candidate_count == 0) {
        return NULL;
    }

    /* Tìm mục tiêu có độ tin cậy cao nhất */
    uint8_t best_idx = 0;
    uint8_t max_conf = s_frame_state.targets[0].confidence;

    for (uint8_t i = 1; i < s_frame_state.candidate_count; i++) {
        if (s_frame_state.targets[i].confidence > max_conf) {
            max_conf = s_frame_state.targets[i].confidence;
            best_idx = i;
        }
    }

    return &s_frame_state.targets[best_idx];
}
