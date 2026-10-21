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
#include <string.h>

/* Hàm trễ thời gian phần mềm (Chuẩn hóa cho xung nhịp nội IHRC 12 MHz của Sonix) */
static void delay_ms(uint32_t ms) {
    for (volatile uint32_t i = 0; i < ms * 1500; i++) {
        __NOP();
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
    
    /* 5. Cấu hình tần số sóng mang 433.0 MHz (0x6C8000) */
    sx1278_write_reg(0x06, 0x6C);
    sx1278_write_reg(0x07, 0x80);
    sx1278_write_reg(0x08, 0x00);
    
    /* 6. Công suất phát +17 dBm qua chân PA_BOOST */
    sx1278_write_reg(0x09, 0x8F);
    
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
    /* 1. Cấp xung nhịp APB1 cho GPIO Port 1 (LED) và GPIO Port 2 (LoRa Ra-02) */
    SN_SCU->APB1CLKG |= (1U << 18) | (1U << 19);
    
    /* 2. Cấu hình đèn LED1 trên kit (P1.12) làm đèn chớp chỉ báo */
    SN_GPIO1->DIR |= (1U << KVC_PIN_BOARD_LED1_PIN);
    SN_GPIO1->BSET = (1U << KVC_PIN_BOARD_LED1_PIN); // Tắt LED ban đầu
    
    /* 3. Khởi tạo module LoRa Ra-02 (Chờ đến khi SPI nhận đúng chip 0x12) */
    while (!sx1278_init_tx()) {
        /* Chớp LED nhanh nếu chưa nối được dây SPI với Ra-02 */
        SN_GPIO1->DATAOUT ^= (1U << KVC_PIN_BOARD_LED1_PIN);
        delay_ms(300);
    }
    
    /* ĐÃ NHẬN CHIP RA-02 THÀNH CÔNG: Sáng LED đứng 1.0 giây để xác nhận SPI hoạt động OK */
    SN_GPIO1->BCLR = (1U << KVC_PIN_BOARD_LED1_PIN);
    delay_ms(1000);
    SN_GPIO1->BSET = (1U << KVC_PIN_BOARD_LED1_PIN);
    delay_ms(500);
    
    /* 4. Chuẩn bị khung dữ liệu Telemetry mẫu 32 bytes */
    KvcTelemetryPacket32 pkt;
    memset(&pkt, 0, sizeof(pkt));
    
    pkt.msg_id         = KVC_MSG_ID_TELEMETRY;
    pkt.target_lat     = 160738520;   /* 16.0738520 N (Vĩ độ Đà Nẵng) */
    pkt.target_lon     = 1081499210;  /* 108.1499210 E (Kinh độ Đà Nẵng) */
    pkt.alt_dist_cm    = 250;         /* Độ cao mặt nước: 2.50 m */
    pkt.class_id       = KVC_CLASS_ID_PERSON; /* Phát hiện Người gặp nạn */
    pkt.confidence     = 95;          /* Độ tin cậy 95% */
    pkt.sensor_flags   = KVC_FLAG_GNSS_VALID | KVC_FLAG_ALT_VALID | KVC_FLAG_AI_DETECTED;
    pkt.battery_raw    = 126;         /* 12.6V */
    
    uint8_t seq = 1;
    
    /* 5. Vòng lặp phát sóng định kỳ mỗi 1.0 giây */
    while (1) {
        pkt.seq_num = seq++;
        pkt.timestamp_ms += 1000;
        
        /* Tự động điền Sync Header 0xAA 0x55 và tính mã CRC-16 chuẩn xác */
        kvc_finalize_telemetry_packet(&pkt);
        
        /* Bật đèn LED chỉ báo bắt đầu bắn gói tin */
        SN_GPIO1->BCLR = (1U << KVC_PIN_BOARD_LED1_PIN);
        
        /* Bắn gói tin 32 bytes ra Anten */
        sx1278_send_packet((const uint8_t *)&pkt, sizeof(pkt));
        
        /* Tắt đèn LED sau khi bắn xong */
        SN_GPIO1->BSET = (1U << KVC_PIN_BOARD_LED1_PIN);
        
        delay_ms(1000); /* Chu kỳ phát 1 giây / gói */
    }
}