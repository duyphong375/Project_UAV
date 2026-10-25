/**
 * @file kvc_usound_ajsr04m.h
 * @brief Driver giao tiếp UART 9600 bps cho Cảm biến Siêu âm chống nước AJ-SR04M trên MCU Sonix SN34F788.
 *
 * Chế độ hoạt động: Serial UART 9600 bps (8N1) sau khi hàn điện trở 47 kΩ tại pad R19 trên bo cảm biến.
 * Sơ đồ chân theo docs/hardware/KVC_MASTER_PINOUT_WIRING.md (Mục 3.2):
 * - VCC  -> 5.0V (Nguồn Buck DC-DC ngoài, cấm cấp 3.3V)
 * - GND  -> VSS / GND chung toàn hệ thống
 * - TX cảm biến (chân Echo cũ, xuất mức 5V TTL) -> Cầu phân áp 4.7kΩ nối tiếp và 10kΩ xuống GND
 *                                                -> P2.15 (URXD2, Pin 31 LQFP64 | JP3 Pin 31/32)
 * - RX cảm biến (chân Trig cũ, nhận mức 3.3V)   -> P2.14 (UTXD2, Pin 30 LQFP64 | JP3 Pin 29/30)
 *
 * Đặc tả khung truyền nhận 4 byte từ cảm biến:
 * - Byte 0: 0xFF (Start Header cố định)
 * - Byte 1: Data_H (Byte cao khoảng cách tính bằng mm)
 * - Byte 2: Data_L (Byte thấp khoảng cách tính bằng mm)
 * - Byte 3: Checksum = (0xFF + Data_H + Data_L) & 0xFF
 * Distance_mm = (Data_H << 8) | Data_L; Distance_cm = Distance_mm / 10.
 *
 * Người phụ trách: Nguyễn Tá Duy Phong
 */

#ifndef KVC_USOUND_AJSR04M_H
#define KVC_USOUND_AJSR04M_H

#include <stdint.h>
#include <stdbool.h>
#include "SN34F780.h"
#include "kvc_pinout.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ============================================================================
 * 1. CÁC HẰNG SỐ ĐẶC TẢ CẢM BIẾN VÀ MÃ TRẠNG THÁI
 * ============================================================================ */
#define KVC_USOUND_MIN_RANGE_CM       20U     /* Vùng mù dưới 20 cm */
#define KVC_USOUND_MAX_RANGE_CM       500U    /* Trần đo tin cậy phục vụ tải UAV cứu nạn */
#define KVC_USOUND_TIMEOUT_MS         150U    /* Timeout tối đa 150 ms chờ phản hồi khung */

/* Mã trạng thái đo đạc */
#define KVC_USOUND_OK                 0U      /* Đo cự ly thành công, nằm trong dải tin cậy 20–500 cm */
#define KVC_USOUND_ERR_TIMEOUT        1U      /* Quá timeout không nhận đủ 4 byte hợp lệ */
#define KVC_USOUND_ERR_CHECKSUM       2U      /* Mã Checksum khung dữ liệu 4 byte không khớp */
#define KVC_USOUND_ERR_OUT_OF_RANGE   3U      /* Cự ly vượt trần 500 cm hoặc cảm biến báo mã 6000 mm (No Echo) */
#define KVC_USOUND_ERR_BLIND_ZONE     4U      /* Vật cản nằm trong vùng mù dưới 20 cm */

/* ============================================================================
 * 2. HÀM TRỄ VI GIÂY (MICROSECOND) BẰNG VÒNG LẶP LỆNH CHUẨN XÁC, AN TOÀN TUYỆT ĐỐI
 * ============================================================================ */
static inline void kvc_usound_delay_us(uint32_t us) {
    /* Xung nhịp 12 MHz: 1 µs tương đương 12 chu kỳ clock CPU Cortex-M4.
     * Vòng lặp decrement volatile tốn khoảng 3-4 chu kỳ -> nhân hệ số 4.
     * Tuyệt đối không dùng DWT CYCCNT để tránh bị treo khi MCU chạy standalone không cắm mạch nạp.
     */
    volatile uint32_t count = us * 4U;
    while (count > 0U) {
        count--;
        __NOP();
    }
}

/* ============================================================================
 * 3. HÀM PHÁT 1 BYTE QUA NGOẠI VI UART2 (P2.14 - UTXD2)
 * ============================================================================ */
static inline void kvc_usound_uart_tx_byte(uint8_t b) {
    /* Chờ đệm phát sẵn sàng (THRE = 1 trong LS) với giới hạn lặp an toàn */
    uint32_t timeout = 50000U;
    while (((SN_UART2->LS & (1U << 5)) == 0) && (--timeout > 0)) {
        __NOP();
    }
    SN_UART2->TH = b;
}

/* ============================================================================
 * 4. HÀM KHỞI TẠO PHẦN CỨNG UART2 VÀ AFIO CHO SONIX SN34F788
 * ============================================================================ */
static inline void kvc_usound_init(void) {
    /* 1. Cấp xung nhịp cho khối UART2 (APB0CLKG bit 5) và GPIO Port 2 (APB1CLKG bit 19) */
    SN_SCU->APB0CLKG |= (1U << 5);                 /* Bit 5: UART2CLKEN */
    SN_SCU->APB1CLKG |= (1U << 14) | (1U << 19);   /* Bit 19: P2CLKEN (kèm bit 14 dự phòng theo đặc tả) */

    /* 2. Cấu hình chức năng phụ AFIO trong SN_ALWAYSON->P2_AFIO2 (User Manual v1.7 trang 121 & 169):
     *    - Chân P2.14: IO14 = 1 -> Chức năng phần cứng UTXD2 (Pin 30 LQFP64)
     *    - Chân P2.15: IO15 = 1 -> Chức năng phần cứng URXD2 (Pin 31 LQFP64)
     */
    SN_ALWAYSON->P2_AFIO2 = (SN_ALWAYSON->P2_AFIO2 & ~((0x1FU << 10) | (0x1FU << 15)))
                          | (1U << 10)   /* IO14 = 1: UTXD2 */
                          | (1U << 15);  /* IO15 = 1: URXD2 */

    /* 3. Cài đặt Baudrate 9600 bps trên SN_UART2 (Xung nhịp UCLK = 12 MHz):
     *    Divisor = 12000000 / (16 * 9600) = 78 = 0x004E
     */
    SN_UART2->LC |= (1U << 7);    /* DLAB = 1: Cho phép ghi DLL/DLM */
    SN_UART2->DLL = 0x4E;         /* DLL = 78 (0x4E) */
    SN_UART2->DLM = 0x00;         /* DLM = 0 */

    /* 4. Cấu hình khung 8N1 (8 bit dữ liệu, 1 stop bit, không parity) và trả DLAB = 0 */
    SN_UART2->LC = 0x03;          /* WLS = 3 (8-bit), SBS = 0 (1 stop bit), PE = 0 (no parity), DLAB = 0 */

    /* 5. Kích hoạt và thiết lập lại bộ đệm FIFO 16-byte */
    SN_UART2->FIFOCTRL = 0x07;    /* FIFOEN = 1, RXFIFORST = 1, TXFIFORST = 1 */

    /* 6. Vô hiệu hóa ngắt phần cứng UART2 (sử dụng giải mã polling / non-blocking theo chu kỳ) */
    SN_UART2->IE = 0x00;
}

/* ============================================================================
 * 5. MÁY TRẠNG THÁI GIẢI MÃ LIÊN TỤC VÀ HÀM POLLING KHÔNG CHẶN (ZERO LATENCY)
 * ============================================================================ */
typedef enum {
    KVC_USOUND_STATE_HEADER = 0,
    KVC_USOUND_STATE_DATA_H,
    KVC_USOUND_STATE_DATA_L,
    KVC_USOUND_STATE_CHECKSUM
} KvcUsoundRxState;

static KvcUsoundRxState s_usound_rx_state       = KVC_USOUND_STATE_HEADER;
static uint8_t          s_usound_data_h          = 0;
static uint8_t          s_usound_data_l          = 0;
static uint16_t         s_usound_latest_mm       = 0;
static uint16_t         s_usound_latest_cm       = 0;
static bool             s_usound_has_fresh_data  = false;
static uint8_t          s_usound_last_err        = KVC_USOUND_ERR_TIMEOUT;
static uint32_t         s_usound_poll_count      = 0;
static uint32_t         s_usound_last_rx_tick    = 0;

/**
 * @brief Nạp và giải mã từng byte từ UART2 theo máy trạng thái.
 */
static inline void kvc_usound_feed_byte(uint8_t b) {
    switch (s_usound_rx_state) {
        case KVC_USOUND_STATE_HEADER:
            if (b == 0xFF) {
                s_usound_rx_state = KVC_USOUND_STATE_DATA_H;
            }
            break;

        case KVC_USOUND_STATE_DATA_H:
            s_usound_data_h = b;
            s_usound_rx_state = KVC_USOUND_STATE_DATA_L;
            break;

        case KVC_USOUND_STATE_DATA_L:
            s_usound_data_l = b;
            s_usound_rx_state = KVC_USOUND_STATE_CHECKSUM;
            break;

        case KVC_USOUND_STATE_CHECKSUM: {
            uint8_t checksum = b;
            uint8_t expected_cs = (uint8_t)((0xFFU + (uint16_t)s_usound_data_h + (uint16_t)s_usound_data_l) & 0xFFU);
            if (checksum == expected_cs) {
                uint32_t calc_mm = ((uint32_t)s_usound_data_h << 8) | (uint32_t)s_usound_data_l;
                uint32_t calc_cm = calc_mm / 10UL;

                /* Xử lý mã hết tầm 6000 mm (No Echo) hoặc vượt ngưỡng tối đa 500 cm */
                if (calc_cm >= 600U || calc_cm > KVC_USOUND_MAX_RANGE_CM) {
                    s_usound_latest_mm = 0;
                    s_usound_latest_cm = 0;
                    s_usound_has_fresh_data = false;
                    s_usound_last_err = KVC_USOUND_ERR_OUT_OF_RANGE;
                } else if (calc_cm < KVC_USOUND_MIN_RANGE_CM) {
                    s_usound_latest_mm = 0;
                    s_usound_latest_cm = 0;
                    s_usound_has_fresh_data = false;
                    s_usound_last_err = KVC_USOUND_ERR_BLIND_ZONE;
                } else {
                    s_usound_latest_mm = (uint16_t)calc_mm;
                    s_usound_latest_cm = (uint16_t)calc_cm;
                    s_usound_has_fresh_data = true;
                    s_usound_last_err = KVC_USOUND_OK;
                    s_usound_last_rx_tick = s_usound_poll_count;
                }
            } else {
                s_usound_last_err = KVC_USOUND_ERR_CHECKSUM;
            }
            /* Nếu byte hiện tại là 0xFF, khóa ngay làm Header của khung kế tiếp */
            s_usound_rx_state = (b == 0xFF) ? KVC_USOUND_STATE_DATA_H : KVC_USOUND_STATE_HEADER;
            break;
        }
    }
}

/**
 * @brief Đọc cạn toàn bộ byte trong bộ đệm nhận FIFO UART2 (Polling không chặn).
 *        Cần gọi đều đặn trong vòng lặp 1ms để giữ bộ đệm luôn rỗng và bắt gói tin mới nhất.
 */
static inline void kvc_usound_poll(void) {
    s_usound_poll_count++;

    /* Đọc cạn toàn bộ byte đang sẵn sàng trong RX FIFO */
    while (SN_UART2->LS & 0x01) {
        uint8_t b = (uint8_t)(SN_UART2->RB & 0xFF);
        kvc_usound_feed_byte(b);
    }

    /* Nếu quá 1500 nhịp poll (~1.5 giây) không có khung tin hợp lệ mới, hủy cờ fresh data */
    if (s_usound_has_fresh_data && (s_usound_poll_count - s_usound_last_rx_tick > 1500U)) {
        s_usound_has_fresh_data = false;
        s_usound_last_err = KVC_USOUND_ERR_TIMEOUT;
    }
}

/* ============================================================================
 * 6. HÀM ĐO CỰ LY THÔNG MINH, TỨC THÌ, KHÔNG DELAY (DRAIN TO LATEST FRAME)
 * ============================================================================ */
static inline uint8_t kvc_usound_measure(uint16_t *dist_cm, uint16_t *dist_mm) {
    /* 1. Xả sạch và giải mã toàn bộ các byte đang có trong FIFO để lấy gói tin MỚI NHẤT */
    kvc_usound_poll();

    /* 2. Nếu đã có dữ liệu hợp lệ (vừa giải mã hoặc đã được poll ngầm) */
    if (s_usound_has_fresh_data) {
        if (dist_mm != 0) *dist_mm = s_usound_latest_mm;
        if (dist_cm != 0) *dist_cm = s_usound_latest_cm;
        return KVC_USOUND_OK;
    }

    /* 3. Nếu chưa có dữ liệu hợp lệ trong FIFO (vừa bật nguồn hoặc mất tín hiệu),
     *    gửi byte trigger 0x01 (phục vụ nếu cảm biến dùng Mode 3) và chờ tối đa 100 ms */
    kvc_usound_uart_tx_byte(0x01);

    uint32_t wait_us = 100000U; /* 100 ms (đúng 1 chu kỳ phát của AJ-SR04M) */
    while (wait_us > 0U) {
        while (SN_UART2->LS & 0x01) {
            uint8_t b = (uint8_t)(SN_UART2->RB & 0xFF);
            kvc_usound_feed_byte(b);
            if (s_usound_has_fresh_data) {
                if (dist_mm != 0) *dist_mm = s_usound_latest_mm;
                if (dist_cm != 0) *dist_cm = s_usound_latest_cm;
                return KVC_USOUND_OK;
            }
        }
        kvc_usound_delay_us(500);
        if (wait_us >= 500U) wait_us -= 500U;
        else wait_us = 0;
    }

    if (dist_mm != 0) *dist_mm = 0;
    if (dist_cm != 0) *dist_cm = 0;
    return s_usound_last_err;
}

/* ============================================================================
 * 7. HÀM ĐỌC CỰ LY ỔN ĐỊNH, PHẢN HỒI TỨC THÌ (FAST RESPONSIVE ROBUST READ)
 * ============================================================================ */
static inline uint8_t kvc_usound_read_robust(uint16_t *filtered_cm) {
    static uint16_t s_last_valid_cm = 0;
    static uint8_t  s_drop_count    = 0;

    uint16_t cm = 0;
    uint8_t res = kvc_usound_measure(&cm, 0);

    if (res == KVC_USOUND_OK) {
        s_last_valid_cm = cm;
        s_drop_count = 0;
        if (filtered_cm != 0) *filtered_cm = cm;
        return KVC_USOUND_OK;
    }

    /* Nếu gặp sự cố tạm thời (dội trượt 1 nhịp do bề mặt nước sóng sánh):
     * Chỉ giữ lại 1 chu kỳ để tránh làm trễ việc hiển thị khoảng cách mới */
    if (s_last_valid_cm > 0 && s_drop_count < 1) {
        s_drop_count++;
        if (filtered_cm != 0) *filtered_cm = s_last_valid_cm;
        return KVC_USOUND_OK;
    }

    /* Mất tín hiệu liên tục -> Hạ cờ báo lỗi thực sự */
    s_last_valid_cm = 0;
    if (filtered_cm != 0) *filtered_cm = 0;
    return res;
}

/* ============================================================================
 * 7. HÀM ĐỌC LỌC TRUNG VỊ (MEDIAN FILTER 3 MẪU) KHỬ NHIỄU MẶT NƯỚC DAO ĐỘNG
 * ============================================================================ */
static inline uint8_t kvc_usound_read_filtered(uint16_t *filtered_cm) {
    uint16_t samples[3];
    uint8_t valid_count = 0;

    for (uint8_t i = 0; i < 3; i++) {
        uint16_t cm = 0;
        uint8_t res = kvc_usound_measure(&cm, 0);
        if (res == KVC_USOUND_OK) {
            samples[valid_count++] = cm;
        }
        /* Giãn cách 20ms giữa 2 lần đo */
        kvc_usound_delay_us(20000);
    }

    if (valid_count == 0) {
        if (filtered_cm != 0) *filtered_cm = 0;
        return KVC_USOUND_ERR_TIMEOUT;
    }

    if (valid_count == 1) {
        if (filtered_cm != 0) *filtered_cm = samples[0];
        return KVC_USOUND_OK;
    }

    if (valid_count == 2) {
        if (filtered_cm != 0) *filtered_cm = (samples[0] + samples[1]) / 2;
        return KVC_USOUND_OK;
    }

    /* Đủ 3 mẫu hợp lệ: Sắp xếp lấy giá trị trung vị (Median of 3) */
    if (samples[0] > samples[1]) {
        uint16_t tmp = samples[0]; samples[0] = samples[1]; samples[1] = tmp;
    }
    if (samples[1] > samples[2]) {
        uint16_t tmp = samples[1]; samples[1] = samples[2]; samples[2] = tmp;
    }
    if (samples[0] > samples[1]) {
        uint16_t tmp = samples[0]; samples[0] = samples[1]; samples[1] = tmp;
    }

    if (filtered_cm != 0) *filtered_cm = samples[1];
    return KVC_USOUND_OK;
}

#ifdef __cplusplus
}
#endif

#endif /* KVC_USOUND_AJSR04M_H */
