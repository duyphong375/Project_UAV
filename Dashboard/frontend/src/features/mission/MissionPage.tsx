import React, { useState } from 'react'
import {
  AlertCircle,
  AlertTriangle,
  Columns,
  Compass,
  Crosshair,
  LocateFixed,
  Radio,
  Video,
  VideoOff,
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { GpsMapPanel } from '@/features/map/GpsMapPanel'
import { LocalRadarPanel } from '@/features/radar/LocalRadarPanel'
import { ReplayControls } from '@/features/replay/ReplayControls'
import { VideoPanel } from '@/features/video/VideoPanel'
import { useMission } from '@/state/MissionProvider'
import { ActiveAlertsQuickPanel } from './ActiveAlertsQuickPanel'
import { CurrentPositionPanel } from './CurrentPositionPanel'
import { TargetDetailsPanel } from './TargetDetailsPanel'

export type ViewportMode = 'MAP' | 'RADAR' | 'SPLIT'

export const MissionPage: React.FC = () => {
  const { state, selectedScenarioId, dispatch } = useMission()
  const {
    source_mode,
    session_id,
    ws_connected,
    camera_position,
    target,
    has_target,
    alerts,
  } = state

  // Chế độ hiển thị khung nhìn định vị (Bản đồ WGS-84 | Radar Hệ Local | Chia đôi)
  const [viewportMode, setViewportMode] = useState<ViewportMode>('MAP')

  // Bật/tắt video phụ (mặc định thu gọn để ưu tiên bản đồ/radar và dữ liệu định vị)
  const [showVideoFeed, setShowVideoFeed] = useState<boolean>(false)

  const hasGpsFix = Boolean(
    camera_position.is_valid &&
    camera_position.latitude !== null &&
    camera_position.longitude !== null
  )

  const isLocalGrid = target?.coordinate_frame === 'LOCAL_GRID'

  const hasValidTarget = Boolean(
    has_target &&
    target &&
    target.pos_valid &&
    ((target.coordinate_frame === 'LOCAL_GRID' && target.local_x_cm !== null) ||
      (target.latitude !== null && target.longitude !== null))
  )

  // Lọc các cảnh báo nguy cấp đang hoạt động chưa tiếp nhận
  const criticalAlert = alerts.find(
    (a) => a.active && (a.level === 'CRITICAL' || a.level === 'WARN') && !a.acknowledged
  )

  // Tên kịch bản hoặc phiên làm việc
  const sessionOrScenarioName =
    source_mode === 'MOCK'
      ? selectedScenarioId
        ? `Kịch bản: ${selectedScenarioId}`
        : 'Mô phỏng độc lập'
      : source_mode === 'REPLAY'
        ? `Phát lại: ${state.replay?.source_session_id ?? 'đang chờ snapshot'}`
        : `Phiên: ${session_id || 'SES-REAL-001'}`

  // Kích hoạt Đặt lại khung nhìn về vị trí UAV
  const handleTriggerResetView = () => {
    window.dispatchEvent(new CustomEvent('kvc-map-reset-view'))
    window.dispatchEvent(new CustomEvent('kvc-radar-reset-view'))
  }

  // Kích hoạt Đưa tâm bản đồ về vị trí Mục tiêu
  const handleTriggerFocusTarget = () => {
    window.dispatchEvent(new CustomEvent('kvc-map-focus-target'))
  }

  return (
    <div className="flex-1 min-h-0 flex flex-col p-2.5 sm:p-3 gap-2 overflow-hidden select-none">
      {/* 1. Dải cảnh báo khẩn cấp nổi bật nếu có sự cố (Review điểm 8) */}
      {criticalAlert && (
        <div
          className={`px-3 py-1.5 rounded-lg border flex items-center justify-between gap-2 text-xs shrink-0 shadow-xs ${
            criticalAlert.level === 'CRITICAL'
              ? 'bg-red-500/15 border-red-500/40 text-red-700 dark:text-red-300'
              : 'bg-amber-500/15 border-amber-500/40 text-amber-800 dark:text-amber-300'
          }`}
          role="alert"
        >
          <div className="flex items-center gap-2 min-w-0">
            {criticalAlert.level === 'CRITICAL' ? (
              <AlertCircle className="h-4 w-4 shrink-0 text-red-500" />
            ) : (
              <AlertTriangle className="h-4 w-4 shrink-0 text-amber-500" />
            )}
            <span className="font-mono font-bold shrink-0">[{criticalAlert.code}]</span>
            <span className="truncate">{criticalAlert.message}</span>
          </div>
          <Button
            size="sm"
            variant="outline"
            onClick={() => dispatch({ type: 'ACKNOWLEDGE_ALERT', payload: criticalAlert.id })}
            className="h-6 px-2 text-xs font-semibold shrink-0 border-current hover:bg-black/10 dark:hover:bg-white/10"
          >
            Tiếp nhận (ACK)
          </Button>
        </div>
      )}

      {/* 2. Thanh điều khiển tối giản & Toolbar nhiệm vụ */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-1.5 border-b border-border/50 shrink-0">
        {/* Nhóm trái: Tiêu đề, Nguồn dữ liệu, Kết nối, Phiên/Kịch bản */}
        <div className="flex items-center gap-2 flex-wrap min-w-0">
          <h1 className="text-base sm:text-lg font-bold tracking-tight text-foreground truncate">
            Giám sát định vị tải nhiệm vụ
          </h1>

          {/* Nhãn nguồn dữ liệu: MOCK / REAL / REPLAY */}
          <Badge
            variant="outline"
            className={`text-xs px-2 py-0.5 font-mono ${
              source_mode === 'MOCK'
                ? 'border-purple-500/40 text-purple-600 dark:text-purple-300 bg-purple-500/10'
                : source_mode === 'REPLAY'
                ? 'border-cyan-500/40 text-cyan-600 dark:text-cyan-400 bg-cyan-500/10'
                : 'border-emerald-500/40 text-emerald-600 dark:text-emerald-400 bg-emerald-500/10'
            }`}
          >
            Nguồn: {source_mode}
          </Badge>

          {/* Trạng thái kết nối */}
          <Badge
            variant={ws_connected ? 'outline' : 'destructive'}
            className={`text-xs px-2 py-0.5 font-mono ${
              ws_connected
                ? 'border-emerald-500/40 text-emerald-600 dark:text-emerald-400 bg-emerald-500/10'
                : ''
            }`}
          >
            {ws_connected ? 'LINK OK' : 'MẤT KẾT NỐI'}
          </Badge>

          {/* Tên phiên hoặc kịch bản */}
          <span className="text-xs font-mono text-muted-foreground truncate hidden md:inline">
            • {sessionOrScenarioName}
          </span>
        </div>

        {/* Nhóm phải: Chuyển đổi Khung nhìn, Tâm UAV, Tâm Target & Toggle Video */}
        <div className="flex items-center gap-1.5 sm:gap-2 shrink-0 flex-wrap">
          {/* Nhóm chuyển đổi khung nhìn định vị (Bản đồ WGS-84 ↔ Radar Hệ Local ↔ Chia đôi) */}
          <div className="flex items-center bg-muted/60 p-0.5 rounded-lg border border-border/50">
            <Button
              variant={viewportMode === 'MAP' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewportMode('MAP')}
              className="min-h-[36px] h-9 px-2.5 text-xs sm:text-sm gap-1.5 font-semibold focus-visible:ring-2 focus-visible:ring-primary cursor-pointer"
              aria-label="Xem Bản đồ WGS-84"
            >
              <Compass className="h-4 w-4" />
              <span className="hidden sm:inline">Bản đồ WGS-84</span>
            </Button>

            <Button
              variant={viewportMode === 'RADAR' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewportMode('RADAR')}
              className="min-h-[36px] h-9 px-2.5 text-xs sm:text-sm gap-1.5 font-semibold focus-visible:ring-2 focus-visible:ring-primary cursor-pointer"
              aria-label="Xem Radar Hệ Local"
            >
              <Radio className="h-4 w-4" />
              <span className="hidden sm:inline">Radar Hệ Local</span>
            </Button>

            <Button
              variant={viewportMode === 'SPLIT' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewportMode('SPLIT')}
              className="min-h-[36px] h-9 px-2 text-xs sm:text-sm gap-1 font-semibold hidden xl:inline-flex focus-visible:ring-2 focus-visible:ring-primary cursor-pointer"
              aria-label="Xem Chia đôi Bản đồ và Radar"
            >
              <Columns className="h-4 w-4" />
              <span>Chia đôi</span>
            </Button>
          </div>

          {/* Nút "Đặt lại khung nhìn" (Tâm tải UAV) */}
          <Button
            variant="outline"
            size="sm"
            onClick={handleTriggerResetView}
            disabled={viewportMode === 'MAP' && !hasGpsFix}
            className="min-h-[36px] h-9 px-2.5 text-xs sm:text-sm gap-1.5 border-border hover:border-primary/50 text-foreground font-semibold shadow-xs cursor-pointer focus-visible:ring-2 focus-visible:ring-primary"
            title="Đưa tâm bản đồ hoặc local về vị trí tải nhiệm vụ UAV"
            aria-label="Đặt lại khung nhìn"
          >
            <LocateFixed className="h-4 w-4 text-primary" />
            <span className="hidden md:inline">Tâm UAV</span>
            <span className="md:hidden">Đặt lại</span>
          </Button>

          {/* Nút "Tâm Mục tiêu" (Focus Target riêng theo Review điểm 4) */}
          <Button
            variant="outline"
            size="sm"
            onClick={handleTriggerFocusTarget}
            disabled={!hasValidTarget}
            className="min-h-[36px] h-9 px-2.5 text-xs sm:text-sm gap-1.5 border-border hover:border-cyan-500/50 text-foreground font-semibold shadow-xs cursor-pointer focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50"
            title={hasValidTarget ? 'Đưa tâm bản đồ về mục tiêu cứu nạn' : 'Chưa có tọa độ mục tiêu hợp lệ để focus'}
            aria-label="Tâm mục tiêu"
          >
            <Crosshair className="h-4 w-4 text-rose-500" />
            <span className="hidden md:inline">Tâm Target</span>
          </Button>

          {/* Nút bật/tắt Video phụ (Review điểm 1: Video phụ thu gọn/ẩn khi không có stream) */}
          <Button
            variant={showVideoFeed ? 'secondary' : 'outline'}
            size="sm"
            onClick={() => setShowVideoFeed(!showVideoFeed)}
            className="min-h-[36px] h-9 px-2.5 text-xs sm:text-sm gap-1.5 border-border font-medium shadow-xs cursor-pointer focus-visible:ring-2 focus-visible:ring-primary"
            title={showVideoFeed ? 'Thu gọn video tham chiếu' : 'Mở video quang học tham chiếu'}
            aria-label="Bật tắt Video phụ"
          >
            {showVideoFeed ? (
              <Video className="h-4 w-4 text-primary" />
            ) : (
              <VideoOff className="h-4 w-4 text-muted-foreground" />
            )}
            <span className="hidden lg:inline">Video phụ</span>
          </Button>
        </div>
      </div>

      <ReplayControls />

      {/* Thông báo thông minh: Gợi ý chuyển sang Radar khi nhận dữ liệu hệ local LOCAL_GRID */}
      {isLocalGrid && viewportMode === 'MAP' && (
        <div className="bg-cyan-500/10 border border-cyan-500/30 px-3 py-1.5 rounded-lg text-xs text-cyan-800 dark:text-cyan-300 flex items-center justify-between shrink-0 shadow-xs">
          <span className="truncate">
            🎯 Đang nhận gói tin hệ local <strong>LOCAL_GRID</strong> (Mục tiêu #{target?.track_id ?? '101'}:{' '}
            X={target?.local_x_cm ?? 0}cm, Y={target?.local_y_cm ?? 0}cm).
          </span>
          <button
            type="button"
            onClick={() => setViewportMode('RADAR')}
            className="text-xs font-bold text-cyan-600 dark:text-cyan-400 underline hover:text-cyan-500 ml-2 shrink-0 cursor-pointer"
          >
            Chuyển sang Radar Hệ Local &rarr;
          </button>
        </div>
      )}

      {/* 3. Bố cục đề xuất theo UX Review: Vùng radar/map 65–75% + Panel target/health/alerts 25–35% */}
      <div className="flex-1 flex flex-col lg:flex-row gap-2.5 min-h-0 overflow-hidden">
        {/* Vùng chính (65%–75% chiều rộng trên desktop): Radar / Map / Split */}
        <div className="flex-1 lg:w-[68%] xl:w-[72%] h-full min-h-0 flex flex-col overflow-hidden">
          {showVideoFeed ? (
            /* Khi bật Video phụ: Chia phần lớn cho Map/Radar, phần nhỏ cho Video */
            <div className="flex-1 flex flex-col md:flex-row gap-2.5 min-h-0 h-full overflow-hidden">
              <div className="flex-1 h-3/5 md:h-full min-h-0 overflow-hidden">
                {viewportMode === 'MAP' && <GpsMapPanel />}
                {viewportMode === 'RADAR' && (
                  <LocalRadarPanel onSwitchToMap={() => setViewportMode('MAP')} />
                )}
                {viewportMode === 'SPLIT' && (
                  <div className="flex-1 flex flex-col xl:flex-row gap-2 min-h-0 h-full overflow-hidden">
                    <div className="flex-1 h-1/2 xl:h-full min-h-0 overflow-hidden">
                      <GpsMapPanel />
                    </div>
                    <div className="flex-1 h-1/2 xl:h-full min-h-0 overflow-hidden">
                      <LocalRadarPanel onSwitchToMap={() => setViewportMode('MAP')} />
                    </div>
                  </div>
                )}
              </div>
              <div className="w-full md:w-72 lg:w-80 h-2/5 md:h-full min-h-0 shrink-0 overflow-hidden">
                <VideoPanel />
              </div>
            </div>
          ) : (
            /* Khi ẩn Video phụ (mặc định): Tối đa hóa 100% diện tích cho Radar / Map */
            <div className="flex-1 h-full min-h-0 flex flex-col overflow-hidden">
              {viewportMode === 'MAP' && <GpsMapPanel />}
              {viewportMode === 'RADAR' && (
                <LocalRadarPanel onSwitchToMap={() => setViewportMode('MAP')} />
              )}
              {viewportMode === 'SPLIT' && (
                <div className="flex-1 flex flex-col xl:flex-row gap-2.5 min-h-0 h-full overflow-hidden">
                  <div className="flex-1 h-1/2 xl:h-full min-h-0 overflow-hidden">
                    <GpsMapPanel />
                  </div>
                  <div className="flex-1 h-1/2 xl:h-full min-h-0 overflow-hidden">
                    <LocalRadarPanel onSwitchToMap={() => setViewportMode('MAP')} />
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Panel Tác chiến bên cạnh (25%–35% trên desktop, xếp dưới trên màn hình nhỏ):
            Chi tiết mục tiêu bàn giao cứu nạn + Vị trí tải UAV + Cảnh báo nhanh */}
        <div className="w-full lg:w-[32%] xl:w-[28%] lg:max-w-md h-auto lg:h-full min-h-0 flex flex-col gap-2.5 overflow-y-auto shrink-0 pr-0.5">
          {/* 1. Dữ liệu bàn giao cứu nạn chính: Mục tiêu cứu nạn */}
          <TargetDetailsPanel />

          {/* 2. Vị trí & Trạng thái cảm biến tải UAV */}
          <CurrentPositionPanel onResetView={handleTriggerResetView} />

          {/* 3. Cảnh báo kỹ thuật khẩn cấp */}
          <ActiveAlertsQuickPanel />
        </div>
      </div>
    </div>
  )
}
