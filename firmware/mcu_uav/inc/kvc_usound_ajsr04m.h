/**
 * @file kvc_usound_ajsr04m.h
 * @brief Driver giao tiếp cảm biến siêu âm chống nước AJ-SR04M / JSN-SR04T cho MCU Sonix SN34F788.
 *
 * Chế độ hoạt động: Mode 1 (Xung Trigger 10µs / Đo độ rộng xung phản hồi Echo).
 * Sơ đồ chân theo docs/hardware/KVC_MASTER_PINOUT_WIRING.md (Mục 3.2):
 * - VCC  -> 5.0V (Nguồn Buck DC-DC ngoài, cấm cấp 3.3V)
 * - GND  -> VSS / GND chung toàn hệ thống
 * - Trig -> P2.14 (Pin 30 LQFP64 | JP3 Pin 29/30 - Xung kích 10µs từ MCU)
 * - Echo -> Đi qua cầu phân áp (4.7kΩ / 10kΩ hoặc 1kΩ / 2kΩ) -> P2.15 (Pin 31 LQFP64 | JP3 Pin 31/32)
 *
 * Sử dụng bộ đếm chu kỳ phần cứng Cortex-M4 DWT (Data Watchpoint and Trace)
 * để đo độ rộng xung vi giây (µs) với độ phân giải tuyệt đối, không phụ thuộc delay_ms.
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
#define KVC_USOUND_TIMEOUT_MS         36U     /* Timeout tối đa cho xung Echo (~617 cm) */

/* Mã trạng thái đo đạc */
#define KVC_USOUND_OK                 0U      /* Đo cự ly thành công, nằm trong dải tin cậy 20–500 cm */
#define KVC_USOUND_ERR_BUSY           1U      /* Đường Echo bị kẹt mức cao trước khi kích xung */
#define KVC_USOUND_ERR_TIMEOUT        2U      /* Quá 5ms không thấy chân Echo chuyển sang mức cao */
#define KVC_USOUND_ERR_OUT_OF_RANGE   3U      /* Cự ly vượt trần 500 cm hoặc Echo quá 36ms không về thấp */
#define KVC_USOUND_ERR_BLIND_ZONE     4U      /* Vật cản nằm trong vùng mù dưới 20 cm */

/* ============================================================================
 * 2. HÀM TRỄ VI GIÂY (MICROSECOND) QUA BỘ ĐẾM CHU KỲ DWT CORTEX-M4
 * ============================================================================ */
static inline void kvc_usound_delay_us(uint32_t us) {
    uint32_t start_cycles = DWT->CYCCNT;
    /* SystemCoreClock thường là 12000000 (12 MHz) -> 12 clock cycles / µs */
    uint32_t cycles_to_wait = us * (SystemCoreClock / 1000000UL);
    while ((DWT->CYCCNT - start_cycles) < cycles_to_wait) {
        __NOP();
    }
}

/* ============================================================================
 * 3. HÀM KHỞI TẠO PHẦN CỨNG GPIO VÀ BỘ ĐẾM DWT
 * ============================================================================ */
static inline void kvc_usound_init(void) {
    /* 1. Cấp xung nhịp APB1 cho Port 2 (Chân P2.14 và P2.15) */
    SN_SCU->APB1CLKG |= (1U << 19);

    /* 2. Cấu hình chân P2.14 (Trig) làm ngõ ra Output, ban đầu kéo LOW (0V) */
    SN_GPIO2->BCLR = (1U << KVC_PIN_USOUND_TRIG_PIN);
    SN_GPIO2->DIR |= (1U << KVC_PIN_USOUND_TRIG_PIN);

    /* 3. Cấu hình chân P2.15 (Echo) làm ngõ vào Input */
    SN_GPIO2->DIR &= ~(1U << KVC_PIN_USOUND_ECHO_PIN);

    /* 4. Kích hoạt khối đếm chu kỳ Cortex-M4 DWT nếu chưa được bật */
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

/* ============================================================================
 * 4. HÀM ĐO ĐỘ RỘNG XUNG ECHO VÀ TÍNH KHOẢNG CÁCH (ĐƠN VỊ MM VÀ CM)
 * ============================================================================ */
static inline uint8_t kvc_usound_measure(uint16_t *dist_cm, uint16_t *dist_mm) {
    uint32_t cycles_per_us = SystemCoreClock / 1000000UL;
    if (cycles_per_us == 0) cycles_per_us = 12; /* Dự phòng mặc định 12 MHz */

    /* 1. Kiểm tra chân Echo trước khi bắn: nếu đang ở mức cao là có lỗi dây hoặc nhiễu */
    if (SN_GPIO2->DATAIN & (1U << KVC_PIN_USOUND_ECHO_PIN)) {
        /* Chờ tối đa 2ms cho chân Echo về LOW */
        uint32_t wait_low = DWT->CYCCNT;
        uint32_t wait_low_limit = 2000UL * cycles_per_us;
        while (SN_GPIO2->DATAIN & (1U << KVC_PIN_USOUND_ECHO_PIN)) {
            if ((DWT->CYCCNT - wait_low) > wait_low_limit) {
                return KVC_USOUND_ERR_BUSY;
            }
        }
    }

    /* 2. Kích hoạt chân Trig: Kéo HIGH trong 10 µs rồi kéo LOW */
    SN_GPIO2->BSET = (1U << KVC_PIN_USOUND_TRIG_PIN);
    kvc_usound_delay_us(10);
    SN_GPIO2->BCLR = (1U << KVC_PIN_USOUND_TRIG_PIN);

    /* 3. Chờ chân Echo chuyển sang mức CAO (bắt đầu đo). Cho phép tối đa 10 ms */
    uint32_t t_wait_start = DWT->CYCCNT;
    uint32_t t_wait_limit = 10000UL * cycles_per_us; /* 10 ms */
    while ((SN_GPIO2->DATAIN & (1U << KVC_PIN_USOUND_ECHO_PIN)) == 0) {
        if ((DWT->CYCCNT - t_wait_start) > t_wait_limit) {
            return KVC_USOUND_ERR_TIMEOUT; /* Mất phản hồi hoặc lỏng dây */
        }
    }

    /* 4. Chân Echo đã lên mức CAO: Ghi nhận thời điểm bắt đầu */
    uint32_t t_echo_start = DWT->CYCCNT;
    uint32_t t_echo_max = KVC_USOUND_TIMEOUT_MS * 1000UL * cycles_per_us; /* 36 ms tương đương 617 cm */

    /* 5. Chờ chân Echo chuyển về mức THẤP (sóng âm đã phản xạ về đầu thu) */
    while (SN_GPIO2->DATAIN & (1U << KVC_PIN_USOUND_ECHO_PIN)) {
        if ((DWT->CYCCNT - t_echo_start) > t_echo_max) {
            return KVC_USOUND_ERR_OUT_OF_RANGE; /* Quá tầm đo hoặc mất sóng phản xạ */
        }
    }
    uint32_t t_echo_end = DWT->CYCCNT;

    /* 6. Tính thời gian xung Echo (micro-giây) */
    uint32_t duration_us = (t_echo_end - t_echo_start) / cycles_per_us;

    /* 7. Tính khoảng cách:
     * Vận tốc âm thanh: 343 m/s ở 20°C = 0.343 mm/µs.
     * Sóng truyền đi và về: Khoảng cách = (duration_us * 0.343) / 2
     *                       = (duration_us * 343) / 2000 (mm)
     */
    uint32_t calc_mm = (duration_us * 343UL) / 2000UL;
    uint32_t calc_cm = calc_mm / 10UL;

    if (dist_mm != 0) {
        *dist_mm = (uint16_t)calc_mm;
    }
    if (dist_cm != 0) {
        *dist_cm = (uint16_t)calc_cm;
    }

    /* 8. Kiểm tra dải đo tin cậy */
    if (calc_cm < KVC_USOUND_MIN_RANGE_CM) {
        return KVC_USOUND_ERR_BLIND_ZONE; /* Nằm trong vùng mù < 20cm */
    }
    if (calc_cm > KVC_USOUND_MAX_RANGE_CM) {
        return KVC_USOUND_ERR_OUT_OF_RANGE; /* Vượt trần 500cm */
    }

    return KVC_USOUND_OK;
}

/* ============================================================================
 * 5. HÀM ĐỌC LỌC TRUNG VỊ (MEDIAN FILTER 3 MẪU) KHỬ NHIỄU MẶT NƯỚC DAO ĐỘNG
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
        /* Giãn cách 20ms giữa 2 lần đo để tiêu tán tiếng vang trong không gian */
        kvc_usound_delay_us(20000);
    }

    if (valid_count == 0) {
        return KVC_USOUND_ERR_TIMEOUT;
    }

    if (valid_count == 1) {
        *filtered_cm = samples[0];
        return KVC_USOUND_OK;
    }

    if (valid_count == 2) {
        *filtered_cm = (samples[0] + samples[1]) / 2;
        return KVC_USOUND_OK;
    }

    /* Đủ 3 mẫu hợp lệ: Lấy giá trị trung vị (Median of 3) */
    if (samples[0] > samples[1]) {
        uint16_t tmp = samples[0]; samples[0] = samples[1]; samples[1] = tmp;
    }
    if (samples[1] > samples[2]) {
        uint16_t tmp = samples[1]; samples[1] = samples[2]; samples[2] = tmp;
    }
    if (samples[0] > samples[1]) {
        uint16_t tmp = samples[0]; samples[0] = samples[1]; samples[1] = tmp;
    }

    *filtered_cm = samples[1]; /* Lấy phần tử đứng giữa */
    return KVC_USOUND_OK;
}

#ifdef __cplusplus
}
#endif

#endif /* KVC_USOUND_AJSR04M_H */
