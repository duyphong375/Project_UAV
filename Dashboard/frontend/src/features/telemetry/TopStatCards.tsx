import React from 'react'
import {
  AlertCircle,
  BatteryCharging,
  Bot,
  Navigation,
} from 'lucide-react'
import { Card } from '@/components/ui/card'
import { useMission } from '@/state/MissionProvider'

export const TopStatCards: React.FC<{ className?: string }> = ({ className = '' }) => {
  const { state } = useMission()
  const {
    telemetry,
    has_target,
    target,
    bounding_boxes,
    inference_device,
    source_mode,
    is_stale,
  } = state

  const targetCount = is_stale ? 0 : bounding_boxes.length || (has_target ? 1 : 0)
  const hasValidTarget = !is_stale && has_target && target?.pos_valid && target.coordinate_frame === 'WGS84' && telemetry.gps_valid
  const targetLatStr = hasValidTarget && target.latitude !== null ? target.latitude.toFixed(6) + '°' : 'N/A'
  const targetLonStr = hasValidTarget && target.longitude !== null ? target.longitude.toFixed(6) + '°' : 'N/A'
  const targetTrackId = !is_stale ? target?.track_id ?? 'N/A' : 'N/A'
  const isLidarLocked = !is_stale && telemetry.lidar_valid && telemetry.lidar_range_cm !== null
  const lidarMeters = isLidarLocked ? (telemetry.lidar_range_cm! / 100).toFixed(2) : 'N/A'
  const batteryPct = is_stale ? null : telemetry.battery_pct
  const isLowBattery = batteryPct !== null && batteryPct <= 20
  const rawConfidence = is_stale ? null : target?.confidence ?? (bounding_boxes[0] ? bounding_boxes[0].confidence * 100 : null)
  const confidenceStr = rawConfidence === null ? 'N/A' : rawConfidence.toFixed(1) + '%'
  const targetClassLabel = targetCount === 0 ? 'Chưa có nhận diện hiện hành' : target?.class_name === 'lifebuoy' ? 'Phao cứu sinh' : target?.class_name === 'person' ? 'Người' : 'Đối tượng nhận diện'
  const deviceLabel = inference_device === 'FPGA_GW2A' ? 'FPGA GW2A' : inference_device === 'PC_REFERENCE' ? 'PC_REFERENCE' : inference_device === 'SIMULATED' ? 'SIMULATED' : 'UNKNOWN'

  return (
    <div className={`shrink-0 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3 sm:gap-4 ${className}`}>
      {/* Stat 1: Mục tiêu cứu nạn */}
      <Card className="relative overflow-hidden flex flex-col justify-between p-4 sm:p-5 rounded-2xl bg-card border border-border shadow-xs hover:border-rose-500/40 transition-colors">
        <div className="absolute -top-12 -right-12 w-28 h-28 bg-rose-500/10 rounded-full blur-2xl pointer-events-none" />
        <div className="flex items-center justify-between">
          <span className="font-mono text-xs uppercase tracking-wider text-muted-foreground font-semibold">
            Mục tiêu cứu nạn
          </span>
          <span className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full font-mono text-[10px] font-bold ${
            targetCount > 0
              ? 'bg-rose-500/20 text-rose-600 dark:text-rose-400'
              : 'bg-muted text-muted-foreground'
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${targetCount > 0 ? 'bg-rose-500 animate-pulse' : 'bg-muted-foreground'}`} />
            {targetCount > 0 ? 'ACTIVE SAR' : 'QUÉT DÒNG NƯỚC'}
          </span>
        </div>

        <div className="my-3">
          <div className="flex items-baseline gap-2">
            <span className="font-mono text-3xl font-black text-rose-500 tracking-tight">
              {targetCount.toString().padStart(2, '0')}
            </span>
            <span className="text-sm font-bold text-foreground">Mục tiêu</span>
          </div>
          <div className="mt-1 font-mono text-xs text-foreground font-semibold truncate" title={`Track #${targetTrackId} • WGS84: ${targetLatStr}, ${targetLonStr}`}>
            Track #{targetTrackId} • WGS84: {targetLatStr}, {targetLonStr}
          </div>
        </div>

        <div className="pt-1 text-muted-foreground flex items-center justify-between text-xs">
          <span className="truncate">
            {targetCount > 0 ? 'Thông tin nhận diện theo nguồn ' + source_mode : 'Đang quét phân loại người & phao'}
          </span>
          <AlertCircle className="h-4 w-4 text-rose-500 shrink-0 ml-1" />
        </div>
      </Card>

      {/* Stat 2: Cự ly cảm biến */}
      <Card className="relative overflow-hidden flex flex-col justify-between p-4 sm:p-5 rounded-2xl bg-card border border-border shadow-xs hover:border-cyan-500/40 transition-colors">
        <div className="absolute -top-12 -right-12 w-28 h-28 bg-cyan-500/10 rounded-full blur-2xl pointer-events-none" />
        <div className="flex items-center justify-between">
          <span className="font-mono text-xs uppercase tracking-wider text-muted-foreground font-semibold">
            Động lực học bay
          </span>
          <span className="font-mono text-[10px] font-bold text-cyan-600 dark:text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded-full border border-cyan-500/20">
            {isLidarLocked ? 'LIDAR LOCKED' : 'N/A'}
          </span>
        </div>

        <div className="my-3">
          <div className="flex items-baseline gap-1.5">
            <span className="font-mono text-3xl font-black text-primary tracking-tight">
              {lidarMeters}
            </span>
            <span className="text-xs font-semibold text-muted-foreground">m dọc tia LiDAR</span>
          </div>
          <div className="mt-1 font-mono text-xs text-foreground truncate">
            Pose/góc camera: N/A
          </div>
        </div>

        <div className="pt-1 text-muted-foreground flex items-center justify-between text-xs">
          <span className="truncate">
            {!is_stale && telemetry.gps_valid ? 'Fix GNSS hợp lệ theo nguồn' : 'MẤT FIX GNSS • Chờ vệ tinh'}
          </span>
          <Navigation className="h-4 w-4 text-primary shrink-0 ml-1" />
        </div>
      </Card>

      {/* Stat 3: Nguồn & Pin tải KVC */}
      <Card className="relative overflow-hidden flex flex-col justify-between p-4 sm:p-5 rounded-2xl bg-card border border-border shadow-xs hover:border-emerald-500/40 transition-colors">
        <div className="absolute -top-12 -right-12 w-28 h-28 bg-emerald-500/10 rounded-full blur-2xl pointer-events-none" />
        <div className="flex items-center justify-between">
          <span className="font-mono text-xs uppercase tracking-wider text-muted-foreground font-semibold">
            Nguồn & Pin tải KVC
          </span>
          <span className={`font-mono text-[10px] font-bold px-2 py-0.5 rounded-full border ${
            isLowBattery
              ? 'text-rose-500 bg-rose-500/10 border-rose-500/30'
              : 'text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
          }`}>
            {isLowBattery ? 'PIN YẾU' : batteryPct === null ? 'N/A' : source_mode}
          </span>
        </div>

        <div className="my-3">
          <div className="flex items-baseline gap-1.5">
            <span className={`font-mono text-3xl font-black tracking-tight ${
              isLowBattery ? 'text-rose-500' : 'text-emerald-600 dark:text-emerald-400'
            }`}>
              {batteryPct === null ? 'N/A' : batteryPct + '%'}
            </span>
            <span className="text-xs font-semibold text-muted-foreground">Điện áp: N/A</span>
          </div>
          <div className="mt-1 font-mono text-xs text-foreground truncate">
            Thời lượng còn lại: N/A
          </div>
        </div>

        <div className="pt-1 text-muted-foreground flex items-center justify-between text-xs">
          <span className="truncate">
            Dòng tải: N/A • Không điều khiển bay
          </span>
          <BatteryCharging className="h-4 w-4 text-emerald-500 shrink-0 ml-1" />
        </div>
      </Card>

      {/* Stat 4: Độ tin cậy AI YOLO11n */}
      <Card className="relative overflow-hidden flex flex-col justify-between p-4 sm:p-5 rounded-2xl bg-card border border-border shadow-xs hover:border-purple-500/40 transition-colors">
        <div className="absolute -top-12 -right-12 w-28 h-28 bg-purple-500/10 rounded-full blur-2xl pointer-events-none" />
        <div className="flex items-center justify-between">
          <span className="font-mono text-xs uppercase tracking-wider text-muted-foreground font-semibold">
            Độ tin cậy nhận diện AI
          </span>
          <span className="font-mono text-[10px] font-bold text-purple-600 dark:text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded-full border border-purple-500/20">
            {deviceLabel}
          </span>
        </div>

        <div className="my-3">
          <div className="flex items-baseline gap-1.5">
            <span className="font-mono text-3xl font-black text-purple-600 dark:text-purple-400 tracking-tight">
              {confidenceStr}
            </span>
            <span className="text-xs font-semibold text-muted-foreground">{targetClassLabel}</span>
          </div>
          <div className="mt-1 font-mono text-xs text-foreground truncate">
            YOLO11n mục tiêu • Hiệu năng cần phép đo
          </div>
        </div>

        <div className="pt-1 text-muted-foreground flex items-center justify-between text-xs">
          <span className="truncate">
            {targetCount > 0 ? `${targetCount} Phát hiện (${targetClassLabel})` : 'Đang phân tích dòng nước SAR'}
          </span>
          <Bot className="h-4 w-4 text-purple-500 shrink-0 ml-1" />
        </div>
      </Card>
    </div>
  )
}
