import React from 'react'
import { Cpu, Zap } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { useMission } from '@/state/MissionProvider'

export const UavHardwareGaugeCard: React.FC<{ className?: string }> = ({ className = '' }) => {
  const { state } = useMission()
  const { telemetry, source_mode, inference_device, hardware_link, is_stale } = state
  const batteryPct = is_stale ? null : telemetry.battery_pct
  const isDanger = batteryPct !== null && batteryPct <= 20
  const arcLength = 298.45
  const strokeDashoffset = arcLength * (1 - (batteryPct ?? 0) / 100)
  const dataStatus = is_stale ? 'DỮ LIỆU CŨ' : source_mode === 'MOCK' ? 'MÔ PHỎNG' : source_mode === 'REPLAY' ? 'PHÁT LẠI' : 'CÓ DỮ LIỆU'
  const subsystems = [
    { id: 'gnss', title: '1. GNSS NEO-M8N / ATGM336H', detail: !is_stale && telemetry.gps_valid ? 'Fix hợp lệ theo nguồn' : 'Fix: N/A', status: !is_stale && telemetry.gps_valid ? dataStatus : 'N/A' },
    { id: 'lidar', title: '2. LiDAR TF-Luna', detail: !is_stale && telemetry.lidar_valid && telemetry.lidar_range_cm !== null ? 'Cự ly dọc tia: ' + (telemetry.lidar_range_cm / 100).toFixed(2) + ' m' : 'Cự ly: N/A', status: !is_stale && telemetry.lidar_valid ? dataStatus : 'N/A' },
    { id: 'imu', title: '3. IMU GY-87', detail: 'Tư thế cần dữ liệu/hiệu chuẩn', status: !is_stale && telemetry.imu_valid ? dataStatus : 'N/A' },
    { id: 'camera', title: '4. Camera RGB', detail: 'Module/giao diện chưa chốt', status: 'N/A' },
    { id: 'fpga', title: '5. OneKiwi Primer 20K V1.1', detail: 'YOLO11n mục tiêu • ' + inference_device, status: 'CHƯA XÁC MINH BO' },
    { id: 'sonix', title: '6. Sonix SN34F788', detail: 'MCU tải: cảm biến/định vị/RF', status: 'N/A' },
    { id: 'lora', title: '7. LoRa Ra-02 SX1278', detail: !is_stale && telemetry.packet_rssi_dbm !== null ? 'RSSI ' + telemetry.packet_rssi_dbm + ' dBm • SNR ' + (telemetry.packet_snr_db ?? 'N/A') : 'RSSI/SNR: N/A', status: !is_stale && telemetry.packet_rssi_dbm !== null ? dataStatus : 'N/A' },
    { id: 'ground', title: '8. STM32F103C8T6 + CP2102', detail: 'Trạm đất • ' + (hardware_link.port ?? 'COM: N/A'), status: hardware_link.status },
  ]

  return (
    <div className={'shrink-0 grid grid-cols-1 lg:grid-cols-12 gap-4 ' + className}>
      <Card className="lg:col-span-5 flex flex-col p-4 sm:p-5 rounded-2xl border-border">
        <div className="flex items-center justify-between gap-2 border-b border-border pb-2">
          <h3 className="flex items-center gap-2 text-sm font-bold"><Zap className="h-4 w-4" />Nguồn và pin tải KVC</h3>
          <Badge variant="outline">{source_mode}</Badge>
        </div>
        <div className="relative flex flex-col items-center justify-center my-4">
          <svg className="w-full max-w-[270px] h-36" viewBox="0 0 240 140" aria-label="Mức pin tải">
            <path d="M 25 115 A 95 95 0 0 1 215 115" fill="none" stroke="currentColor" className="text-muted" strokeWidth="14" strokeLinecap="round" />
            <path d="M 25 115 A 95 95 0 0 1 215 115" fill="none" stroke="currentColor" className={isDanger ? 'text-rose-500' : 'text-emerald-500'} strokeWidth="14" strokeLinecap="round" strokeDasharray={arcLength} strokeDashoffset={strokeDashoffset} />
            <text x="22" y="138" className="fill-muted-foreground text-[10px]">0%</text>
            <text x="206" y="138" className="fill-muted-foreground text-[10px]">100%</text>
          </svg>
          <div className="absolute bottom-5 text-center">
            <p className={'font-mono text-3xl font-bold ' + (isDanger ? 'text-rose-500' : 'text-foreground')}>{batteryPct === null ? 'N/A' : batteryPct + '%'}</p>
            <p className="text-xs text-muted-foreground">{isDanger ? 'PIN YẾU' : batteryPct === null ? 'Chưa có dữ liệu pin hiện hành' : dataStatus}</p>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3 text-xs">
          {['Điện áp', 'Dòng tải', 'Nhiệt độ', 'Thời lượng còn lại'].map((label) => <div key={label} className="rounded-lg bg-muted/30 p-2"><p className="text-muted-foreground">{label}</p><p className="font-mono">N/A</p></div>)}
        </div>
        <p className="mt-3 text-xs text-muted-foreground">Phần trăm pin không đủ để suy điện áp, số cell hay thời lượng. KVC không gửi lệnh điều khiển bay.</p>
      </Card>
      <Card className="lg:col-span-7 flex flex-col p-4 sm:p-5 rounded-2xl border-border">
        <div className="flex items-center justify-between gap-2 border-b border-border pb-2">
          <h3 className="flex items-center gap-2 text-sm font-bold"><Cpu className="h-4 w-4" />Các khối trong cấu hình KVC</h3>
          <Badge variant="outline">{source_mode}</Badge>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2.5 my-3">
          {subsystems.map((sub) => <div key={sub.id} className="p-2.5 rounded-xl bg-muted/30 border border-border flex flex-col gap-2">
            {sub.id === 'gnss' ? <button type="button" className="text-left text-xs font-bold text-cyan-600" onClick={() => window.dispatchEvent(new CustomEvent('kvc-open-satellite-sheet'))}>{sub.title}</button> : <p className="text-xs font-bold">{sub.title}</p>}
            <p className="text-[11px] text-muted-foreground">{sub.detail}</p>
            <p className="font-mono text-[10px]">{sub.status}</p>
          </div>)}
        </div>
        <p className="text-xs text-muted-foreground mt-auto border-t border-border pt-2">FPGA → UART → Sonix → SPI/LoRa → STM32 → CP2102 → Dashboard. Kết nối ứng dụng không tự xác nhận mọi bo đã chạy.</p>
      </Card>
    </div>
  )
}
