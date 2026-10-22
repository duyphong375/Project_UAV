/**
 * @file main.c
 * @brief Chương trình phát gói Telemetry 32-byte định kỳ để kiểm thử Anten LoRa Ra-02 trên MCU Sonix SN34F788.
 *
 * Đối chiếu tài liệu đặc tả chuẩn:
 * - docs/hardware/KVC_MASTER_PINOUT_WIRING.md (Mục 2 & 3.1)
 * - firmware/mcu_uav/inc/kvc_pinout.h
 * - firmware/mcu_uav/inc/kvc_telemetry.h (IF-02)
 *
 * Người phụ trách: Nguyễn Tá Duy Phong
 */

#include "SN34F780.h"
#include "kvc_pinout.h"
#include "kvc_telemetry.h"
#include "kvc_imu_gy87.h"
#include "kvc_usound_ajsr04m.h"
#include <string.h>

/* Hàm trễ thời gian phần cứng chuẩn xác tuyệt đối qua bộ đếm SysTick của Cortex-M4 (Xung 12 MHz) */
static void delay_ms(uint32_t ms) {
    while (ms--) {
        SysTick->LOAD = (12000000UL / 1000UL) - 1UL; /* Đúng 12000 chu kỳ cho 1.0 ms */
        SysTick->VAL  = 0UL;
        SysTick->CTRL = SysTick_CTRL_CLKSOURCE_Msk | SysTick_CTRL_ENABLE_Msk;
        while ((SysTick->CTRL & SysTick_CTRL_COUNTFLAG_Msk) == 0) {
            __NOP();
        }
        SysTick->CTRL = 0UL;
    }
}

/* ============================================================================
 * ĐIỀU KHIỂN CHÂN SPI VÀ GPIO CHO MODULE LORA RA-02 (SX1278)
 * ============================================================================ */
static inline void lora_nss(uint8_t level) {
    if (level) SN_GPIO2->BSET = (1U << KVC_PIN_LORA_NSS_PIN);
    else       SN_GPIO2->BCLR = (1U << KVC_PIN_LORA_NSS_PIN);
}

static inline void lora_sck(uint8_t level) {
    if (level) SN_GPIO2->BSET = (1U << KVC_PIN_LORA_SCK_PIN);
    else       SN_GPIO2->BCLR = (1U << KVC_PIN_LORA_SCK_PIN);
}

static inline void lora_mosi(uint8_t level) {
    if (level) SN_GPIO2->BSET = (1U << KVC_PIN_LORA_MOSI_PIN);
    else       SN_GPIO2->BCLR = (1U << KVC_PIN_LORA_MOSI_PIN);
}

static inline uint8_t lora_miso(void) {
    return (SN_GPIO2->DATAIN & (1U << KVC_PIN_LORA_MISO_PIN)) ? 1 : 0;
}

/* Truyền nhận 1 byte SPI qua bit-banging tốc độ khoảng 500kHz - 1MHz ổn định trên dây cắm */
static uint8_t spi_transfer(uint8_t data) {
    uint8_t rx = 0;
    for (int i = 7; i >= 0; i--) {
        lora_sck(0);
        lora_mosi((data >> i) & 1);
        for (volatile int d = 0; d < 25; d++) { __NOP(); }
        lora_sck(1);
        if (lora_miso()) rx |= (1 << i);
        for (volatile int d = 0; d < 25; d++) { __NOP(); }
    }
    lora_sck(0);
    return rx;
}

static uint8_t sx1278_read_reg(uint8_t addr) {
    lora_nss(0);
    spi_transfer(addr & 0x7F);
    uint8_t val = spi_transfer(0x00);
    lora_nss(1);
    return val;
}

static void sx1278_write_reg(uint8_t addr, uint8_t val) {
    lora_nss(0);
    spi_transfer(addr | 0x80);
    spi_transfer(val);
    lora_nss(1);
}

/* Khởi tạo module LoRa Ra-02 ở chế độ Phát */
static uint8_t sx1278_init_tx(void) {
    /* 1. Đặt mức logic tĩnh an toàn trước khi bật DIR */
    lora_nss(1);
    lora_sck(0);
    SN_GPIO2->BSET = (1U << KVC_PIN_LORA_RST_PIN);

    /* Thiết lập hướng chân GPIO Port 2 (DIR: 1 = Output, 0 = Input) */
    SN_GPIO2->DIR |= (1U << KVC_PIN_LORA_NSS_PIN) |
                     (1U << KVC_PIN_LORA_SCK_PIN) |
                     (1U << KVC_PIN_LORA_MOSI_PIN) |
                     (1U << KVC_PIN_LORA_RST_PIN);
    SN_GPIO2->DIR &= ~((1U << KVC_PIN_LORA_MISO_PIN) | (1U << KVC_PIN_LORA_DIO0_PIN));

    /* 2. Reset cứng module Ra-02 qua chân P2.9: Kéo LOW 50ms, nhả HIGH chờ 50ms cho thạch anh SX1278 ổn định */
    SN_GPIO2->BCLR = (1U << KVC_PIN_LORA_RST_PIN);
    delay_ms(50);
    SN_GPIO2->BSET = (1U << KVC_PIN_LORA_RST_PIN);
    delay_ms(50);

    /* 3. Kiểm tra thanh ghi nhận diện chip RegVersion (0x42) phải là 0x12 */
    uint8_t ver = sx1278_read_reg(0x42);
    if (ver != 0x12) {
        return 0; /* Lỗi nối dây SPI hoặc tiếp xúc lỏng */
    }

    /* 4. Chuyển sang LoRa Sleep rồi Standby */
    sx1278_write_reg(0x01, 0x80);
    delay_ms(10);
    sx1278_write_reg(0x01, 0x81);
    delay_ms(10);

    /* 5. Cấu hình tần số sóng mang 433.0 MHz (0x6C4000) */
    sx1278_write_reg(0x06, 0x6C);
    sx1278_write_reg(0x07, 0x40); /* 0x40 khớp chuẩn 433.0 MHz (7094272 * 61.035 Hz) */
    sx1278_write_reg(0x08, 0x00);

    /* 6. Công suất phát +16 dBm qua chân PA_BOOST (tăng biên độ sóng, giúp SNR luôn cao an toàn trên ngưỡng -7.5 dB) */
    sx1278_write_reg(0x09, 0x8E);

    /* 7. Cấu hình Modem: Băng thông 125kHz, Coding Rate 4/5 */
    sx1278_write_reg(0x1D, 0x72);
    /* Spreading Factor 7 (SF7), Bật kiểm tra CRC phần cứng */
    sx1278_write_reg(0x1E, 0x74);
    /* Bật tự động điều chỉnh độ lợi (AGC Auto) */
    sx1278_write_reg(0x26, 0x04);
    /* Khóa mạng nội bộ KVC Sync Word 0x12 (Khớp 100% với ESP32 Gateway) */
    sx1278_write_reg(0x39, KVC_LORA_SYNC_WORD);

    /* Đặt con trỏ cơ sở hàng đợi FIFO TX */
    sx1278_write_reg(0x0E, 0x00);
    sx1278_write_reg(0x0F, 0x00);

    return 1;
}

/* Phát 1 gói tin dữ liệu ra Anten */
static void sx1278_send_packet(const uint8_t *payload, uint8_t len) {
    /* 1. Đưa về chế độ Standby */
    sx1278_write_reg(0x01, 0x81);

    /* 2. Xóa sạch mọi cờ ngắt cũ còn sót lại */
    sx1278_write_reg(0x12, 0xFF);

    /* 3. Đặt con trỏ bộ đệm FIFO về vị trí gốc TX (0x00) */
    sx1278_write_reg(0x0E, 0x00);
    sx1278_write_reg(0x0D, 0x00);
    sx1278_write_reg(0x22, len);

    /* 4. Nạp mảng byte vào thanh ghi FIFO 0x00 */
    lora_nss(0);
    spi_transfer(0x00 | 0x80);
    for (uint8_t i = 0; i < len; i++) {
        spi_transfer(payload[i]);
    }
    lora_nss(1);

    /* 5. Chuyển sang chế độ TX để bắt đầu bắn sóng ra anten */
    sx1278_write_reg(0x01, 0x83);

    /* 6. Chờ cờ phát xong TxDone (bit 3 của thanh ghi 0x12 RegIrqFlags) */
    /* Thời gian truyền 32 bytes ở SF7/125kHz là khoảng 67ms. Cho phép tối đa 300ms */
    uint32_t timeout = 300;
    while (((sx1278_read_reg(0x12) & 0x08) == 0) && (--timeout > 0)) {
        delay_ms(1);
    }

    /* 7. Xóa cờ ngắt sau khi phát xong */
    sx1278_write_reg(0x12, 0xFF);

    /* 8. Đưa chip về Standby để giải phóng khối khuếch đại công suất PA */
    sx1278_write_reg(0x01, 0x81);
}

int main(void) {
    /* 1. Cấp xung nhịp APB1 cho GPIO Port 0 (IMU), Port 1 (LED) và Port 2 (LoRa Ra-02) */
    SN_SCU->APB1CLKG |= (1U << 17) | (1U << 18) | (1U << 19);

    /* Đảm bảo chân LED1 (P1.12) và LED2 (P1.13) là GPIO */
    SN_ALWAYSON->P1_AFIO2 &= ~((0x1FU << 0) | (0x1FU << 5));

    /* 2. Cấu hình đèn LED1 (P1.12) và LED2 (P1.13) trên kit làm đèn chỉ báo */
    SN_GPIO1->DIR |= (1U << KVC_PIN_BOARD_LED1_PIN) | (1U << KVC_PIN_BOARD_LED2_PIN);

    /* TEST ĐÈN LED KHỞI ĐỘNG (0.5 giây): Bật cả 2 LED1 và LED2 sáng để kiểm tra phần cứng và Jumper JP10/JP11 */
    KVC_BOARD_LED1_ON();
    KVC_BOARD_LED2_ON();
    delay_ms(500);
    KVC_BOARD_LED1_OFF();
    KVC_BOARD_LED2_OFF();
    delay_ms(200);

    /* 3. Khởi tạo module LoRa Ra-02 (Chờ đến khi SPI nhận đúng chip 0x12) */
    while (!sx1278_init_tx()) {
        /* Chớp LED1 nhanh nếu chưa nối được dây SPI với Ra-02 */
        KVC_BOARD_LED1_TOGGLE();
        delay_ms(300);
    }

    /* ĐÃ NHẬN CHIP RA-02 THÀNH CÔNG: Sáng LED1 đứng 0.3 giây để xác nhận SPI hoạt động OK */
    KVC_BOARD_LED1_ON();
    delay_ms(300);
    KVC_BOARD_LED1_OFF();
    delay_ms(200);

    /* 4. Khởi tạo cảm biến tư thế IMU GY-87 (MPU-6050) qua bus I2C0 */
    uint8_t imu_addr = 0;
    uint8_t imu_status = mpu6050_init(&imu_addr);
    uint8_t imu_ready = (imu_status == MPU6050_ERR_OK);

    if (imu_ready) {
        /* ĐÃ NHẬN IMU MPU-6050: Bật sáng LED2 đứng yên vững chắc để báo hiệu cảm biến đã sẵn sàng */
        KVC_BOARD_LED2_ON();
    } else {
        /* BÁO MÃ LỖI IMU QUA ĐÈN LED2:
         * - Chớp 1 nhịp: Bus I2C bị kẹt (SDA/SCL bị chập mass hoặc chạm sai chân)
         * - Chớp 2 nhịp: Cả địa chỉ 0x68 và 0x69 đều không có ACK (chưa nối nguồn hoặc lỏng dây SCL/SDA)
         * - Chớp 3 nhịp: Có ACK nhưng đọc WHO_AM_I trả về 0x00 hoặc 0xFF
         * - Chớp 4 nhịp: Ghi lệnh đánh thức chip thất bại
         * Chớp 3 chu kỳ để người dùng dễ quan sát trực tiếp trên bo mạch */
        for (int cycle = 0; cycle < 3; cycle++) {
            for (int b = 0; b < (int)imu_status; b++) {
                KVC_BOARD_LED2_ON(); // Bật LED2
                delay_ms(150);
                KVC_BOARD_LED2_OFF(); // Tắt LED2
                delay_ms(150);
            }
            delay_ms(700);
        }
        KVC_BOARD_LED2_OFF();
    }

    /* 5. Khởi tạo cảm biến siêu âm chống nước AJ-SR04M (P2.14 Trig, P2.15 Echo) */
    kvc_usound_init();

    /* 6. Chuẩn bị khung dữ liệu Telemetry 32 bytes */
    KvcTelemetryPacket32 pkt;
    memset(&pkt, 0, sizeof(pkt));

    pkt.msg_id         = KVC_MSG_ID_TELEMETRY;
    pkt.target_lat     = 160738520;   /* 16.0738520 N (Vĩ độ Đà Nẵng) */
    pkt.target_lon     = 1081499210;  /* 108.1499210 E (Kinh độ Đà Nẵng) */
    pkt.alt_dist_cm    = 0;           /* Cập nhật cự ly thực tế từ cảm biến AJ-SR04M */
    pkt.class_id       = KVC_CLASS_ID_PERSON; /* Phát hiện Người gặp nạn */
    pkt.confidence     = 95;          /* Độ tin cậy 95% */
    pkt.sensor_flags   = KVC_FLAG_GNSS_VALID | KVC_FLAG_AI_DETECTED;
    pkt.battery_raw    = 126;         /* 12.6V */

    uint8_t seq = 1;

    /* 7. Vòng lặp phát sóng định kỳ mỗi 1.0 giây */
    while (1) {
        pkt.seq_num = seq++;
        pkt.timestamp_ms += 1000;

        /* Nếu IMU chưa nhận diện được, tự động dò tìm lại mỗi chu kỳ để người dùng cắm lại dây là nhận ngay */
        if (!imu_ready) {
            imu_status = mpu6050_init(&imu_addr);
            if (imu_status == MPU6050_ERR_OK) {
                imu_ready = 1;
                /* BẬT SÁNG ĐÈN LED2 ĐỨNG YÊN NGAY LẬP TỨC KHI CẢM BIẾN ĐƯỢC KẾT NỐI */
                KVC_BOARD_LED2_ON();
            } else {
                KVC_BOARD_LED2_OFF();
            }
        } else {
            /* Giữ LED2 luôn sáng đứng yên báo hiệu IMU đang kết nối tốt */
            KVC_BOARD_LED2_ON();
        }

        /* Đọc dữ liệu góc nghiêng từ cảm biến IMU GY-87 nếu có cắm */
        if (imu_ready) {
            int16_t roll_deg10 = 0;
            int16_t pitch_deg10 = 0;
            if (mpu6050_read_angles(imu_addr, &roll_deg10, &pitch_deg10)) {
                pkt.sensor_flags |= KVC_FLAG_IMU_VALID;
                /* Ghi Roll và Pitch (đơn vị 0.1 độ, ví dụ 152 = 15.2°) vào 4 byte reserved */
                pkt.reserved[0] = (uint8_t)(roll_deg10 & 0xFF);
                pkt.reserved[1] = (uint8_t)((roll_deg10 >> 8) & 0xFF);
                pkt.reserved[2] = (uint8_t)(pitch_deg10 & 0xFF);
                pkt.reserved[3] = (uint8_t)((pitch_deg10 >> 8) & 0xFF);
            }
        } else {
            /* Chưa có IMU: Đảm bảo xóa cờ IMU */
            pkt.sensor_flags &= ~KVC_FLAG_IMU_VALID;
            pkt.reserved[0] = 0;
            pkt.reserved[1] = 0;
            pkt.reserved[2] = 0;
            pkt.reserved[3] = 0;
        }

        /* Đọc cự ly bề mặt nước thực tế từ cảm biến siêu âm chống nước AJ-SR04M */
        uint16_t usound_cm = 0;
        uint8_t usound_res = kvc_usound_measure(&usound_cm, 0);
        if (usound_res == KVC_USOUND_OK) {
            pkt.alt_dist_cm = usound_cm;
            pkt.sensor_flags |= KVC_FLAG_ALT_VALID;
        } else {
            pkt.alt_dist_cm = 0;
            pkt.sensor_flags &= ~KVC_FLAG_ALT_VALID;
        }

        /* Tự động điền Sync Header 0xAA 0x55 và tính mã CRC-16 chuẩn xác */
        kvc_finalize_telemetry_packet(&pkt);

        /* Bật đèn LED1 chỉ báo bắt đầu bắn gói tin */
        KVC_BOARD_LED1_ON();

        /* Bắn gói tin 32 bytes ra Anten */
        sx1278_send_packet((const uint8_t *)&pkt, sizeof(pkt));

        /* Tắt đèn LED1 sau khi bắn xong */
        KVC_BOARD_LED1_OFF();

        delay_ms(1000); /* Chu kỳ phát 1 giây / gói */
    }
}
