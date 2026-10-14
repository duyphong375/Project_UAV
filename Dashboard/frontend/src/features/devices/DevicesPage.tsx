import React from 'react'
import {
  Activity,
  ArrowDownUp,
  Camera,
  Compass,
  Cpu,
  HardDrive,
  Radio,
  RotateCcw,
  Server,
} from 'lucide-react'
import { PageHeader } from '@/components/shared/PageHeader'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { APP_CONFIG } from '@/config/appConfig'
import { useMission } from '@/state/MissionProvider'

export const DevicesPage: React.FC = () => {
  const { state, reconnect, switchSourceMode } = useMission()
  const {
    ws_connected,
    hardware_link,
    diagnostics,
    telemetry,
    camera_position,
    video,
    inference_device,
    source_mode,
    rx_age_ms,
    is_stale,
  } = state

  return (
    <div className="flex-1 flex flex-col p-3 sm:p-5 gap-4 overflow-y-auto max-w-7xl mx-auto w-full select-none">
      {/* 1. Header Trang Thiết Bị */}
      <PageHeader
        breadcrumb="Hệ thống · Chẩn đoán thiết bị"
        title="Thiết bị & kết nối phần cứng"
        subtitle="Theo dõi tình trạng liên kết truyền thông, cụm cảm biến và thiết bị suy luận AI trên trạm giám sát GCS."
        badge={
          <Badge
            variant={ws_connected ? 'default' : 'destructive'}
            className="text-xs font-mono"
          >
            {ws_connected ? 'GCS LINK OK' : 'LINK DOWN'}
          </Badge>
        }
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => switchSourceMode(source_mode === 'REAL' ? 'MOCK' : 'REAL')}
              className="h-8 text-xs gap-1.5 border-border shadow-xs"
              title="Chuyển đổi nhanh giữa chế độ Mô phỏng và Thực địa"
            >
              <span>Nguồn: {source_mode}</span>
            </Button>
            <Button
              variant="default"
              size="sm"
              onClick={reconnect}
              className="h-8 text-xs gap-1.5 bg-primary text-primary-foreground hover:bg-primary/90 shadow-xs"
              title="Thử kết nối lại kênh WebSocket tới GCS backend"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              <span>Kết nối lại</span>
            </Button>
          </div>
        }
      />

      {/* 2. Nhóm 1: Kết Nối Mạng & Kênh Truyền Viễn Thông */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
        {/* Card: Trình duyệt <-> Backend GCS */}
        <Card className="border-border bg-card shadow-xs">
          <CardHeader className="py-3 px-4 border-b border-border/60 bg-muted/20">
            <CardTitle className="text-xs font-semibold text-foreground uppercase tracking-wider flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Server className="h-4 w-4 text-cyan-500" />
                <span>Trình duyệt ↔ Backend GCS</span>
              </div>
              <Badge
                variant={ws_connected ? 'default' : 'destructive'}
                className="text-[10px] py-0 px-1.5 font-mono"
              >
                {ws_connected ? 'ĐÃ KẾT NỐI' : 'MẤT KẾT NỐI'}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 flex flex-col gap-2.5 text-xs">
            <div className="flex items-center justify-between py-1 border-b border-border/40">
              <span className="text-muted-foreground">Địa chỉ WebSocket:</span>
              <span className="font-mono text-foreground font-semibold">{APP_CONFIG.WS_URL}</span>
            </div>
            <div className="flex items-center justify-between py-1 border-b border-border/40">
              <span className="text-muted-foreground">Nguồn dữ liệu hiện tại:</span>
              <Badge
                variant="outline"
                className={`font-mono text-[10px] ${
                  source_mode === 'MOCK'
                    ? 'border-purple-500/40 text-purple-600 dark:text-purple-300 bg-purple-500/10'
                    : 'border-emerald-500/40 text-emerald-600 dark:text-emerald-400 bg-emerald-500/10'
                }`}
              >
                {source_mode}
              </Badge>
            </div>
            <div className="flex items-center justify-between py-1 border-b border-border/40">
              <span className="text-muted-foreground">Tuổi gói tin nhận (rx_age):</span>
              <span className={`font-mono font-semibold ${is_stale ? 'text-red-500' : 'text-emerald-600 dark:text-emerald-400'}`}>
                {rx_age_ms} ms {is_stale ? '(STALE)' : ''}
              </span>
            </div>
            <div className="flex items-center justify-between py-1">
              <span className="text-muted-foreground">Tổng gói tin đã nhận:</span>
              <span className="font-mono font-bold text-foreground">
                {diagnostics.packets_received_total}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Card: Backend GCS <-> Thiết Bị / Tải Nhiệm Vụ */}
        <Card className="border-border bg-card shadow-xs">
          <CardHeader className="py-3 px-4 border-b border-border/60 bg-muted/20">
            <CardTitle className="text-xs font-semibold text-foreground uppercase tracking-wider flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Radio className="h-4 w-4 text-primary" />
                <span>Backend GCS ↔ Tải nhiệm vụ</span>
              </div>
              <Badge variant="outline" className="text-[10px] py-0 px-1.5 font-mono">
                {hardware_link.status}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 flex flex-col gap-2.5 text-xs">
            <div className="flex items-center justify-between py-1 border-b border-border/40">
              <span className="text-muted-foreground">Cổng kết nối phần cứng:</span>
              <span className="font-mono text-foreground font-semibold">
                {hardware_link.port || (source_mode === 'MOCK' ? 'Virtual Serial / Mock Bus' : 'Chưa có dữ liệu')}
              </span>
            </div>
            <div className="flex items-center justify-between py-1 border-b border-border/40">
              <span className="text-muted-foreground">Chất lượng RSSI / SNR:</span>
              <span className="font-mono text-foreground">
                {telemetry.packet_rssi_dbm !== null
                  ? `${telemetry.packet_rssi_dbm} dBm / ${telemetry.packet_snr_db ?? 'N/A'} dB`
                  : source_mode === 'MOCK'
                  ? '-82 dBm / 7.5 dB (Mô phỏng)'
                  : 'Chưa có dữ liệu'}
              </span>
            </div>
            <div className="flex items-center justify-between py-1 border-b border-border/40">
              <span className="text-muted-foreground">Lỗi giải mã (Decode errors):</span>
              <span className="font-mono text-foreground font-semibold">
                {diagnostics.decode_errors_total}
              </span>
            </div>
            <div className="flex items-center justify-between py-1">
              <span className="text-muted-foreground">Gói rớt (Ingress drops):</span>
              <span className="font-mono text-foreground font-semibold">
                {diagnostics.ingress_drops_total}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 3. Nhóm 2: Bảng Trạng Thái Cảm Biến & Khí Tài Đo Lường */}
      <div className="flex flex-col gap-2">
        <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
          Trạng thái chi tiết các Module cảm biến & Xử lý trên tải KVC
        </h2>
        <div className="border border-border rounded-xl bg-card overflow-hidden shadow-xs">
          <Table>
            <TableHeader className="bg-muted/40">
              <TableRow className="border-border">
                <TableHead className="w-[200px] text-xs font-semibold py-2.5">
                  Thành phần / Module
                </TableHead>
                <TableHead className="w-[140px] text-xs font-semibold py-2.5">
                  Trạng thái tín hiệu
                </TableHead>
                <TableHead className="text-xs font-semibold py-2.5">
                  Dữ liệu đo lường trực tiếp
                </TableHead>
                <TableHead className="w-[220px] text-xs font-semibold py-2.5">
                  Ghi chú tích hợp
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {/* GNSS / GPS */}
              <TableRow className="border-border/60 hover:bg-muted/30">
                <TableCell className="text-xs font-semibold text-foreground flex items-center gap-2 py-3">
                  <Compass className="h-4 w-4 text-cyan-500 shrink-0" />
                  <span>Module Định vị GNSS</span>
                </TableCell>
                <TableCell className="py-3">
                  <Badge
                    variant={telemetry.gps_valid && camera_position.is_valid ? 'default' : 'outline'}
                    className={`text-[10px] py-0 px-1.5 font-mono ${
                      telemetry.gps_valid && camera_position.is_valid
                        ? 'bg-emerald-600 text-white'
                        : 'border-amber-500/40 text-amber-500 bg-amber-500/10'
                    }`}
                  >
                    {telemetry.gps_valid && camera_position.is_valid ? '3D FIX' : 'NO FIX'}
                  </Badge>
                </TableCell>
                <TableCell className="text-xs font-mono text-foreground py-3">
                  {camera_position.latitude !== null && camera_position.longitude !== null
                    ? `Lat: ${camera_position.latitude.toFixed(6)}, Lon: ${camera_position.longitude.toFixed(6)}`
                    : 'Chưa có tọa độ WGS-84'}
                </TableCell>
                <TableCell className="text-xs text-muted-foreground py-3">
                  Định vị vị trí cụm camera và UAV.
                </TableCell>
              </TableRow>

              {/* LiDAR */}
              <TableRow className="border-border/60 hover:bg-muted/30">
                <TableCell className="text-xs font-semibold text-foreground flex items-center gap-2 py-3">
                  <ArrowDownUp className="h-4 w-4 text-emerald-500 shrink-0" />
                  <span>Cảm biến đo cao LiDAR</span>
                </TableCell>
                <TableCell className="py-3">
                  <Badge
                    variant={telemetry.lidar_valid ? 'default' : 'outline'}
                    className={`text-[10px] py-0 px-1.5 font-mono ${
                      telemetry.lidar_valid
                        ? 'bg-emerald-600 text-white'
                        : 'border-amber-500/40 text-amber-500 bg-amber-500/10'
                    }`}
                  >
                    {telemetry.lidar_valid ? 'HỢP LỆ' : 'KHÔNG HỢP LỆ'}
                  </Badge>
                </TableCell>
                <TableCell className="text-xs font-mono text-foreground py-3">
                  {telemetry.lidar_range_cm !== null ? `${telemetry.lidar_range_cm} cm (Đo dọc tia)` : 'Chưa có dữ liệu'}
                </TableCell>
                <TableCell className="text-xs text-muted-foreground py-3">
                  Đo khoảng cách đến mặt nước (20–800cm).
                </TableCell>
              </TableRow>

              {/* IMU */}
              <TableRow className="border-border/60 hover:bg-muted/30">
                <TableCell className="text-xs font-semibold text-foreground flex items-center gap-2 py-3">
                  <Activity className="h-4 w-4 text-amber-500 shrink-0" />
                  <span>Cảm biến góc nghiêng IMU</span>
                </TableCell>
                <TableCell className="py-3">
                  <Badge
                    variant={telemetry.imu_valid ? 'default' : 'outline'}
                    className={`text-[10px] py-0 px-1.5 font-mono ${
                      telemetry.imu_valid
                        ? 'bg-emerald-600 text-white'
                        : 'border-amber-500/40 text-amber-500 bg-amber-500/10'
                    }`}
                  >
                    {telemetry.imu_valid ? 'HOẠT ĐỘNG' : 'CHƯA SẴN SÀNG'}
                  </Badge>
                </TableCell>
                <TableCell className="text-xs font-mono text-foreground py-3">
                  {camera_position.heading_deg !== null && camera_position.heading_deg !== undefined
                    ? `Heading: ${camera_position.heading_deg.toFixed(1)}° • Ống kính: 45° chúc`
                    : 'Ống kính: 45° chúc'}
                </TableCell>
                <TableCell className="text-xs text-muted-foreground py-3">
                  Đo góc nghiêng và hướng cụm khí tài.
                </TableCell>
              </TableRow>

              {/* AI Inference Hardware */}
              <TableRow className="border-border/60 hover:bg-muted/30">
                <TableCell className="text-xs font-semibold text-foreground flex items-center gap-2 py-3">
                  <Cpu className="h-4 w-4 text-primary shrink-0" />
                  <span>Thiết bị suy luận AI</span>
                </TableCell>
                <TableCell className="py-3">
                  <Badge
                    variant="outline"
                    className={`text-[10px] py-0 px-1.5 font-mono ${
                      inference_device === 'FPGA_GW2A'
                        ? 'border-emerald-500/40 text-emerald-600 dark:text-emerald-400 bg-emerald-500/10'
                        : inference_device === 'PC_REFERENCE'
                        ? 'border-cyan-500/40 text-cyan-600 dark:text-cyan-400 bg-cyan-500/10'
                        : 'border-purple-500/40 text-purple-600 dark:text-purple-300 bg-purple-500/10'
                    }`}
                  >
                    {inference_device}
                  </Badge>
                </TableCell>
                <TableCell className="text-xs text-foreground py-3">
                  {telemetry.ai_detected ? (
                    <span className="text-emerald-600 dark:text-emerald-400 font-semibold font-mono">
                      PHÁT HIỆN ĐỐI TƯỢNG (AI DETECTED)
                    </span>
                  ) : (
                    <span className="text-muted-foreground">Không có mục tiêu trong khung hình</span>
                  )}
                </TableCell>
                <TableCell className="text-xs text-muted-foreground py-3">
                  Mô hình mục tiêu YOLO11n-SAR phân loại người/phao.
                </TableCell>
              </TableRow>

              {/* Video Stream */}
              <TableRow className="border-border/60 hover:bg-muted/30">
                <TableCell className="text-xs font-semibold text-foreground flex items-center gap-2 py-3">
                  <Camera className="h-4 w-4 text-muted-foreground shrink-0" />
                  <span>Kênh truyền hình ảnh Video</span>
                </TableCell>
                <TableCell className="py-3">
                  <Badge
                    variant={video.is_connected ? 'default' : 'outline'}
                    className={`text-[10px] py-0 px-1.5 font-mono ${
                      video.is_connected ? 'bg-emerald-600 text-white' : 'border-red-500/40 text-red-500'
                    }`}
                  >
                    {video.source_type}
                  </Badge>
                </TableCell>
                <TableCell className="text-xs font-mono text-foreground py-3">
                  {video.url || 'Mock Test Pattern (Cục bộ)'}
                </TableCell>
                <TableCell className="text-xs text-muted-foreground py-3">
                  Khung hình 16:9 với lớp Bounding Box AI HUD.
                </TableCell>
              </TableRow>

              {/* Logger Storage */}
              <TableRow className="border-border/60 hover:bg-muted/30">
                <TableCell className="text-xs font-semibold text-foreground flex items-center gap-2 py-3">
                  <HardDrive className="h-4 w-4 text-muted-foreground shrink-0" />
                  <span>Bộ ghi log nhiệm vụ</span>
                </TableCell>
                <TableCell className="py-3">
                  <Badge
                    variant={diagnostics.logger_status === 'OK' ? 'default' : 'outline'}
                    className={`text-[10px] py-0 px-1.5 font-mono ${
                      diagnostics.logger_status === 'OK'
                        ? 'bg-emerald-600 text-white'
                        : 'border-red-500 text-red-500'
                    }`}
                  >
                    {diagnostics.logger_status}
                  </Badge>
                </TableCell>
                <TableCell className="text-xs text-muted-foreground py-3">
                  {diagnostics.logger_status === 'OK' ? 'Ghi liên tục bình thường' : 'Lỗi thiết bị ghi'}
                </TableCell>
                <TableCell className="text-xs text-muted-foreground py-3">
                  Lưu trữ dữ liệu chuyến bay trên thẻ SD tải.
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  )
}
