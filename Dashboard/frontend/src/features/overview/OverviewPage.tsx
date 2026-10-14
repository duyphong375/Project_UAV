import React, { useEffect, useState } from 'react'
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Play,
  Video,
} from 'lucide-react'
import { toast } from 'sonner'
import { useAppRouter } from '@/app/routes'
import { Button } from '@/components/ui/button'
import { RecentDetectionsTable } from '@/features/telemetry/RecentDetectionsTable'
import { TopStatCards } from '@/features/telemetry/TopStatCards'
import { UavHardwareGaugeCard } from '@/features/telemetry/UavHardwareGaugeCard'
import { useMission } from '@/state/MissionProvider'

export const OverviewPage: React.FC = () => {
  const { state, setSelectedScenarioId, switchSourceMode } = useMission()
  const { navigate } = useAppRouter()
  const {
    alerts,
    telemetry,
    session_id,
    camera_position,
    target,
    is_stale,
    source_mode,
  } = state

  const [clockTime, setClockTime] = useState<string>('N/A')

  useEffect(() => {
    const updateTime = () => {
      const now = new Date()
      setClockTime(now.toLocaleTimeString('vi-VN', { hour12: false }))
    }
    updateTime()
    const timer = setInterval(updateTime, 1000)
    return () => clearInterval(timer)
  }, [])

  const activeAlerts = alerts.filter((a) => a.active)

  const handleStartDemoScenario = () => {
    switchSourceMode('MOCK')
    setSelectedScenarioId('NORMAL_GPS_DETECT')
    toast.success('Đã kích hoạt kịch bản diễn tập cứu nạn: Phát hiện người trôi dạt & bám bắt GPS.')
  }

  // Không tạo tọa độ hoặc chất lượng RF khi thiếu/không hợp lệ.
  const gpsReady = !is_stale && camera_position.is_valid && telemetry.gps_valid
  const targetReady = !is_stale && target?.pos_valid && target.coordinate_frame === 'WGS84' && telemetry.gps_valid
  const uavLatStr = gpsReady && camera_position.latitude !== null ? camera_position.latitude.toFixed(6) : 'N/A'
  const uavLonStr = gpsReady && camera_position.longitude !== null ? camera_position.longitude.toFixed(6) : 'N/A'
  const tgtLatStr = targetReady && target.latitude !== null ? target.latitude.toFixed(6) : 'N/A'
  const tgtLonStr = targetReady && target.longitude !== null ? target.longitude.toFixed(6) : 'N/A'
  const lidarM = !is_stale && telemetry.lidar_valid && telemetry.lidar_range_cm !== null ? (telemetry.lidar_range_cm / 100).toFixed(2) : 'N/A'
  const rssiStr = !is_stale && telemetry.packet_rssi_dbm !== null ? telemetry.packet_rssi_dbm + ' dBm' : 'N/A'
  const snrStr = !is_stale && telemetry.packet_snr_db !== null ? telemetry.packet_snr_db + ' dB' : 'N/A'

  return (
    <div className="flex-1 min-h-0 flex flex-col p-3 sm:p-5 gap-4 sm:gap-5 overflow-y-auto max-w-7xl mx-auto w-full select-none">
      {/* 1. Header Trang Tổng Quan Tác Chiến (Mission Banner Title Area) */}
      <div className="shrink-0 flex flex-col lg:flex-row lg:items-center justify-between gap-3 pb-3 border-b border-border/60">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="px-2 py-0.5 rounded bg-primary/15 text-primary font-mono text-[10px] uppercase tracking-widest font-bold border border-primary/25">
              KVC TACTICAL FEED
            </span>
            <span className="font-mono text-xs text-muted-foreground">
              UTC+7 {clockTime}
            </span>
            <span className="text-xs text-muted-foreground hidden sm:inline">•</span>
            <span className="text-xs text-muted-foreground hidden sm:inline">
              Tổng quan nhiệm vụ tìm kiếm cứu nạn
            </span>
          </div>
          <h1 className="text-lg sm:text-xl font-bold tracking-tight uppercase text-foreground">
            BẢNG ĐIỀU KHIỂN TÁC CHIẾN SAR — TỔNG QUAN PHIÊN BAY <span className="text-primary">#{session_id || 'N/A'}</span>
          </h1>
          <p className="text-xs text-muted-foreground">
            Bảng theo dõi chuỗi giá trị cứu nạn: Phát hiện → Định vị → Theo dõi → Cảnh báo → Bằng chứng.
          </p>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          {/* Subsystem Health Badge */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-card border border-border shadow-2xs">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75" />
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500" />
            </span>
            <div className="flex flex-col">
              <span className="text-[9px] font-mono uppercase text-muted-foreground">Trạng thái kết nối tải</span>
              <span className="font-mono text-xs text-emerald-600 dark:text-emerald-400 font-bold">
                BÌNH THƯỜNG (8/8 SUBSYSTEMS)
              </span>
            </div>
            <CheckCircle2 className="h-4 w-4 text-primary ml-1" />
          </div>

          {/* Action Buttons */}
          <Button
            variant="outline"
            size="sm"
            onClick={handleStartDemoScenario}
            className="h-8 text-xs gap-1.5 border-purple-500/40 text-purple-600 dark:text-purple-400 hover:bg-purple-500/10 shadow-2xs"
            title="Kích hoạt nhanh kịch bản diễn tập cứu nạn trong 1 nhấp"
          >
            <Play className="h-3 w-3 fill-current" />
            <span>Diễn tập mẫu</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/alerts')}
            className="h-8 text-xs gap-1.5 border-border hover:border-amber-500/40"
          >
            <AlertTriangle className={`h-3.5 w-3.5 ${activeAlerts.length > 0 ? 'text-amber-500' : 'text-muted-foreground'}`} />
            <span>Cảnh báo ({activeAlerts.length})</span>
          </Button>
          <Button
            size="sm"
            onClick={() => navigate('/mission')}
            className="h-8 text-xs gap-1.5 bg-primary text-primary-foreground hover:bg-primary/90 shadow-2xs"
          >
            <Video className="h-3.5 w-3.5" />
            <span>Mở Trực tiếp</span>
            <ArrowRight className="h-3 w-3" />
          </Button>
        </div>
      </div>

      {/* 2. Row 1: 4 Tactical Stat Cards */}
      <TopStatCards />

      {/* 3. Row 2: Nguồn/pin và các khối theo BOM KVC */}
      <UavHardwareGaugeCard />

      {/* 4. Row 3: Lịch sử nhận diện thời gian thực (Detection Log) */}
      <RecentDetectionsTable />

      {/* 5. Telemetry Ticker Footer Bar */}
      <div className="shrink-0 w-full rounded-xl bg-card border border-border p-2.5 sm:p-3 overflow-hidden shadow-2xs">
        <div className="flex flex-wrap items-center justify-between gap-y-2 gap-x-4 font-mono text-[11px] text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-foreground font-bold uppercase">KVC STREAM:</span>
            <span className="text-primary font-bold">
              UAV [{uavLatStr}, {uavLonStr}]
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-muted-foreground">TARGET #{target?.track_id ?? 'N/A'}:</span>
            <span className="text-rose-500 font-bold">
              [{tgtLatStr}, {tgtLonStr}]
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-muted-foreground">LiDAR dọc tia:</span>
            <span className="text-foreground font-bold">{lidarM} m</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-muted-foreground">VẬN TỐC:</span>
            <span className="text-foreground font-bold">N/A</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-muted-foreground">LORA RSSI:</span>
            <span className="text-emerald-500 font-bold">{rssiStr}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-muted-foreground">SNR:</span>
            <span className="text-emerald-500 font-bold">{snrStr}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-muted-foreground">GÓI TIN:</span>
            <span className="text-emerald-500 font-bold">{source_mode} • ABI chưa duyệt</span>
          </div>
        </div>
      </div>
    </div>
  )
}
