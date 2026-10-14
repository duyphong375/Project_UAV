import React, { useState } from 'react'
import {
  Battery,
  Clock,
  FlaskConical,
  Menu,
  Radio,
  Satellite,
  Wifi,
  WifiOff,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { GnssSatelliteSheet } from '@/features/telemetry/GnssSatelliteSheet'
import { ThemeToggle } from '@/features/theme/ThemeToggle'
import { useMission } from '@/state/MissionProvider'
import { APP_ROUTES, useAppRouter } from './routes'

interface AppHeaderProps {
  onOpenMobileMenu: () => void
}

export const AppHeader: React.FC<AppHeaderProps> = ({
  onOpenMobileMenu,
}) => {
  const { currentPath } = useAppRouter()
  const { state, switchSourceMode } = useMission()
  const { ws_connected, is_stale, rx_age_ms, telemetry, camera_position, source_mode, hardware_link } = state

  const [satelliteSheetOpen, setSatelliteSheetOpen] = useState(false)

  React.useEffect(() => {
    const handleOpen = () => setSatelliteSheetOpen(true)
    window.addEventListener('kvc-open-satellite-sheet', handleOpen)
    return () => window.removeEventListener('kvc-open-satellite-sheet', handleOpen)
  }, [])

  const routeConfig = APP_ROUTES[currentPath] || APP_ROUTES['/mission']

  // Chuyển đổi chế độ có thông báo hệ quả khi đang ở phiên REAL (Review điểm 7)
  const handleSwitchSourceMode = (targetMode: 'MOCK' | 'REAL') => {
    if (targetMode === source_mode) return
    if (source_mode === 'REAL' && targetMode === 'MOCK') {
      const confirmed = window.confirm(
        'Hệ thống đang ở phiên nhận dữ liệu thực địa (REAL). Chuyển sang MOCK sẽ tạm ngắt liên kết phần cứng và chuyển sang dữ liệu mô phỏng. Tiếp tục chuyển?'
      )
      if (!confirmed) return
    }
    switchSourceMode(targetMode)
  }

  // Màu trạng thái rx_age_ms
  const getAgeStatus = (age: number, stale: boolean) => {
    if (stale || age > 3000) {
      return {
        color: 'text-red-500 bg-red-500/10 border-red-500/30',
        dot: 'bg-red-500',
        label: `${(age / 1000).toFixed(1)}s (STALE)`,
      }
    }
    if (age > 1000) {
      return {
        color: 'text-amber-500 bg-amber-500/10 border-amber-500/30',
        dot: 'bg-amber-500',
        label: `${(age / 1000).toFixed(1)}s`,
      }
    }
    return {
      color: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/30',
      dot: 'bg-emerald-500',
      label: `${age}ms`,
    }
  }

  const ageStatus = getAgeStatus(rx_age_ms, is_stale)

  // Nhãn trạng thái phần cứng khi chọn REAL
  const isHardwareConnected = hardware_link.status === 'CONNECTED'
  const realStatusLabel = isHardwareConnected ? 'REAL (Thiết bị OK)' : 'REAL (Chờ thiết bị)'

  return (
    <header className="h-14 bg-card border-b border-border px-3 sm:px-4 flex items-center justify-between gap-3 shrink-0 select-none">
      {/* 1. Bên trái: Nút Menu Mobile + Tên trang / Breadcrumb */}
      <div className="flex items-center gap-2.5 min-w-0">
        <Button
          variant="ghost"
          size="icon"
          onClick={onOpenMobileMenu}
          className="md:hidden min-h-[36px] h-9 w-9 text-muted-foreground hover:text-foreground shrink-0 cursor-pointer"
          aria-label="Mở menu điều hướng"
        >
          <Menu className="h-4 w-4" />
        </Button>

        <div className="flex flex-col min-w-0">
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground font-medium uppercase tracking-wider truncate">
            <span>{routeConfig.breadcrumb}</span>
          </div>
          <span className="text-sm font-bold text-foreground tracking-tight truncate leading-tight">
            {routeConfig.title}
          </span>
        </div>
      </div>

      {/* 2. Ở giữa: Bộ chuyển chế độ MOCK vs REAL (Touch target 36px, phân biệt rõ chọn nguồn vs trạng thái thiết bị) */}
      <div className="flex items-center p-1 rounded-xl border border-border/80 bg-muted/50 dark:bg-[#111622] shadow-2xs">
        <button
          type="button"
          onClick={() => handleSwitchSourceMode('MOCK')}
          className={`flex items-center gap-1.5 px-3 py-1.5 min-h-[32px] rounded-lg text-xs font-bold transition-all cursor-pointer focus-visible:ring-2 focus-visible:ring-primary ${
            source_mode === 'MOCK'
              ? 'bg-purple-600 text-white shadow-[0_0_12px_rgba(168,85,247,0.35)]'
              : 'text-muted-foreground hover:text-foreground'
          }`}
          title="Chuyển sang chế độ giả lập mô phỏng MOCK"
          aria-label="Chế độ Mô phỏng MOCK"
        >
          <FlaskConical className="h-4 w-4" />
          <span>MOCK</span>
        </button>
        <button
          type="button"
          onClick={() => handleSwitchSourceMode('REAL')}
          className={`flex items-center gap-1.5 px-3 py-1.5 min-h-[32px] rounded-lg text-xs font-bold transition-all cursor-pointer focus-visible:ring-2 focus-visible:ring-primary ${
            source_mode === 'REAL'
              ? isHardwareConnected
                ? 'bg-emerald-600 text-white shadow-[0_0_12px_rgba(16,185,129,0.35)]'
                : 'bg-emerald-700/80 text-white border border-emerald-400/40'
              : 'text-muted-foreground hover:text-foreground'
          }`}
          title={
            source_mode === 'REAL'
              ? isHardwareConnected
                ? 'Đang nhận telemetry trực tiếp từ phần cứng'
                : 'Đang ở chế độ REAL nhưng chưa phát hiện cổng phần cứng kết nối'
              : 'Chuyển sang chế độ nhận Telemetry thực tế REAL'
          }
          aria-label="Chế độ Thực tế REAL"
        >
          <Radio className="h-4 w-4" />
          <span>{source_mode === 'REAL' ? realStatusLabel : 'REAL'}</span>
          {source_mode === 'REAL' && isHardwareConnected && (
            <span className="relative flex h-2 w-2 ml-0.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-300 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-white"></span>
            </span>
          )}
        </button>
      </div>

      {/* 3. Bên phải: Chỉ số hệ thống tóm tắt & Công cụ */}
      <div className="flex items-center gap-2 sm:gap-3 shrink-0">
        {/* Kết nối WebSocket */}
        <div
          className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1 min-h-[32px] rounded-lg border text-xs font-semibold ${
            ws_connected
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-600 dark:text-emerald-400'
              : 'bg-red-500/10 border-red-500/30 text-red-600 dark:text-red-400'
          }`}
          title={ws_connected ? 'WebSocket đang kết nối' : 'Mất kết nối WebSocket'}
        >
          {ws_connected ? (
            <Wifi className="h-4 w-4 shrink-0" />
          ) : (
            <WifiOff className="h-4 w-4 shrink-0" />
          )}
          <span className="hidden md:inline font-mono">
            {ws_connected ? 'LINK OK' : 'MẤT KẾT NỐI'}
          </span>
        </div>


        {/* Tuổi dữ liệu telemetry (rx_age) */}
        <div
          className={`flex items-center gap-1.5 px-2 py-1 rounded-md border text-xs font-mono font-medium ${ageStatus.color}`}
          title="Tuổi dữ liệu gói tin nhận gần nhất"
        >
          <Clock className="h-3.5 w-3.5 shrink-0 opacity-80" />
          <span>{ageStatus.label}</span>
        </div>

        {/* Trạng thái Định vị GNSS - Nhấp để mở Phần Vệ Tinh chi tiết */}
        <button
          type="button"
          onClick={() => setSatelliteSheetOpen(true)}
          className="hidden lg:flex items-center gap-1.5 px-2 py-1 rounded-md border border-border/80 bg-muted/30 hover:bg-muted/70 hover:border-cyan-500/50 transition-all text-xs cursor-pointer group"
          title="Xem trạng thái GNSS và các chỉ số có dữ liệu"
          aria-label="Xem chi tiết vệ tinh GNSS"
        >
          <Satellite className="h-3.5 w-3.5 text-cyan-500 shrink-0 group-hover:scale-110 transition-transform" />
          <span className="text-muted-foreground">GNSS:</span>
          <span
            className={`font-semibold font-mono ${
              camera_position.is_valid && telemetry.gps_valid
                ? 'text-emerald-500'
                : 'text-amber-500'
            }`}
          >
            {camera_position.is_valid && telemetry.gps_valid ? 'FIX HỢP LỆ' : 'NO FIX'}
          </span>
        </button>

        {/* Pin tải nhiệm vụ */}
        {telemetry.battery_pct !== null && (
          <div className="hidden md:flex items-center gap-1.5 px-2 py-1 rounded-md border border-border/80 bg-muted/30 text-xs font-mono">
            <Battery className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
            <span
              className={`font-semibold ${
                telemetry.battery_pct <= 20
                  ? 'text-red-500'
                  : telemetry.battery_pct <= 35
                  ? 'text-amber-500'
                  : 'text-foreground'
              }`}
            >
              {telemetry.battery_pct}%
            </span>
          </div>
        )}

        {/* Nút chuyển đổi Theme Light/Dark/System */}
        <ThemeToggle />
      </div>

      {/* Drawer GNSS NEO-M8N / ATGM336H */}
      <GnssSatelliteSheet
        open={satelliteSheetOpen}
        onOpenChange={setSatelliteSheetOpen}
      />
    </header>
  )
}
