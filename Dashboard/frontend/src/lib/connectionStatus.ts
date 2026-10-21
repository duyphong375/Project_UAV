import { APP_CONFIG } from '@/config/appConfig'
import type { HardwareLink, SourceMode } from '@/types/telemetry'

export type Esp32PhysicalStatus =
  | 'MOCK'          // Đang ở chế độ mô phỏng (LOCAL hoặc BACKEND)
  | 'REPLAY'        // Đang ở chế độ phát lại nhật ký
  | 'BACKEND_DOWN'  // Trình duyệt mất kết nối với GCS Backend (:8000)
  | 'WAITING'       // Chế độ REAL chưa khả dụng do thiếu Ingress hoặc chưa có tin từ ESP32
  | 'LIVE'          // ESP32 Gateway đang truyền dữ liệu trực tiếp (< 3000ms)
  | 'LOST_SIGNAL'   // Mất tín hiệu từ ESP32 Gateway (> 3000ms)

export interface Esp32StatusDescriptor {
  status: Esp32PhysicalStatus
  label: string
  shortLabel: string
  description: string
  badgeVariant: 'default' | 'destructive' | 'outline' | 'secondary'
  badgeColorClass: string
  dotColorClass: string
  pingClass: string | null
  iconName: 'radio' | 'radio-off' | 'wifi-off' | 'flask'
}

/**
 * Xác định chính xác tình trạng kết nối vật lý giữa Gateway ESP32-C3 và Backend GCS
 * theo nguyên tắc không suy đoán, phản ánh đúng tín hiệu thực tế.
 */
export function getEsp32PhysicalStatus(
  sourceMode: SourceMode,
  wsConnected: boolean,
  hardwareLink: HardwareLink,
  isStale: boolean,
  rxAgeMs: number
): Esp32StatusDescriptor {
  if (sourceMode === 'MOCK') {
    const isBackend = APP_CONFIG.MOCK_TRANSPORT === 'BACKEND'
    return {
      status: 'MOCK',
      label: isBackend ? 'MÔ PHỎNG BACKEND (LOOPBACK)' : 'MÔ PHỎNG CỤC BỘ (LOCAL)',
      shortLabel: isBackend ? 'MÔ PHỎNG (BACKEND)' : 'MÔ PHỎNG (LOCAL)',
      description: isBackend
        ? 'Dữ liệu giả lập phát từ dịch vụ Backend FastAPI (:8000) lưu SQLite'
        : 'Trình duyệt tự sinh kịch bản mô phỏng offline (không kết nối Backend)',
      badgeVariant: 'outline',
      badgeColorClass: 'border-purple-500/40 text-purple-600 dark:text-purple-300 bg-purple-500/10',
      dotColorClass: 'bg-purple-500',
      pingClass: null,
      iconName: 'flask',
    }
  }

  if (sourceMode === 'REPLAY') {
    return {
      status: 'REPLAY',
      label: 'PHÁT LẠI NHẬT KÝ (REPLAY)',
      shortLabel: 'REPLAY',
      description: 'Đang phát lại dữ liệu nhật ký từ cơ sở dữ liệu SQLite đã ghi',
      badgeVariant: 'outline',
      badgeColorClass: 'border-cyan-500/40 text-cyan-700 dark:text-cyan-300 bg-cyan-500/10',
      dotColorClass: 'bg-cyan-500',
      pingClass: null,
      iconName: 'radio',
    }
  }

  // Chế độ REAL nhưng chưa kết nối được tới dịch vụ GCS Backend nội bộ
  if (!wsConnected) {
    return {
      status: 'BACKEND_DOWN',
      label: 'MẤT KẾT NỐI GCS BACKEND',
      shortLabel: 'GCS DOWN',
      description: 'Trình duyệt mất kết nối tới Backend FastAPI (cổng 8000). Hãy kiểm tra dịch vụ backend.',
      badgeVariant: 'destructive',
      badgeColorClass: 'border-red-500/40 text-red-600 dark:text-red-400 bg-red-500/10',
      dotColorClass: 'bg-red-500',
      pingClass: null,
      iconName: 'wifi-off',
    }
  }

  const isHardwareConnected = hardwareLink.status === 'CONNECTED'
  const isFresh = !isStale && rxAgeMs <= 3000 && isHardwareConnected

  // ESP32 đang truyền gói tin đều đặn và tín hiệu còn tươi (< 3000ms)
  if (isFresh) {
    return {
      status: 'LIVE',
      label: `ESP32 TRỰC TUYẾN (${rxAgeMs}ms)`,
      shortLabel: 'ESP32 LIVE',
      description: `Đang nhận gói tin trực tiếp từ Gateway ESP32 qua ${hardwareLink.port || 'Wi-Fi SoftAP'}.`,
      badgeVariant: 'default',
      badgeColorClass: 'border-emerald-500/40 text-emerald-600 dark:text-emerald-400 bg-emerald-500/10',
      dotColorClass: 'bg-emerald-500',
      pingClass: 'bg-emerald-400',
      iconName: 'radio',
    }
  }

  // Đang kết nối nhưng bị gián đoạn tín hiệu quá 3s (Stale / Timeout)
  if (isHardwareConnected && (isStale || rxAgeMs > 3000)) {
    const ageSeconds = (rxAgeMs / 1000).toFixed(1)
    return {
      status: 'LOST_SIGNAL',
      label: `MẤT SÓNG ESP32 (>${ageSeconds}s)`,
      shortLabel: 'MẤT SÓNG ESP32',
      description: `Đã quá 3,000ms không nhận được gói tin từ Gateway ESP32 (Trễ: ${rxAgeMs}ms). Kiểm tra nguồn ESP32 hoặc cự ly thu phát.`,
      badgeVariant: 'destructive',
      badgeColorClass: 'border-red-500/40 text-red-600 dark:text-red-400 bg-red-500/10',
      dotColorClass: 'bg-red-500',
      pingClass: 'bg-red-400',
      iconName: 'radio-off',
    }
  }

  // Backend đã sẵn sàng nhưng REAL Ingress chưa được triển khai hoặc ESP32 Gateway chưa kết nối
  return {
    status: 'WAITING',
    label: 'CHƯA KHẢ DỤNG (CHƯA CÓ INGRESS)',
    shortLabel: 'CHƯA KHẢ DỤNG',
    description: 'Chế độ REAL chưa khả dụng: Backend GCS hiện chưa triển khai Ingress nhận tin từ Gateway ESP32-C3 / giải mã RF.',
    badgeVariant: 'destructive',
    badgeColorClass: 'border-rose-500/50 text-rose-600 dark:text-rose-400 bg-rose-500/10',
    dotColorClass: 'bg-rose-500',
    pingClass: null,
    iconName: 'radio-off',
  }
}
