import type { HardwareLink, SourceMode } from '@/types/telemetry'

export type Esp32PhysicalStatus =
  | 'MOCK'          // Đang ở chế độ mô phỏng
  | 'BACKEND_DOWN'  // Trình duyệt mất kết nối với GCS Backend (:8000)
  | 'WAITING'       // Backend đang lắng nghe, chờ ESP32 Gateway truyền tin
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
    return {
      status: 'MOCK',
      label: 'MÔ PHỎNG (VIRTUAL BUS)',
      shortLabel: 'MÔ PHỎNG',
      description: 'Đang chạy kịch bản mô phỏng kiểm thử giao diện',
      badgeVariant: 'outline',
      badgeColorClass: 'border-purple-500/40 text-purple-600 dark:text-purple-300 bg-purple-500/10',
      dotColorClass: 'bg-purple-500',
      pingClass: null,
      iconName: 'flask',
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
      description: `Đang nhận gói tin 32-byte trực tiếp từ Gateway ESP32 qua ${hardwareLink.port || 'Wi-Fi SoftAP'}.`,
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

  // Backend đã sẵn sàng nhưng ESP32 Gateway chưa kết nối hoặc chưa truyền gói tin nào
  return {
    status: 'WAITING',
    label: 'CHƯA KẾT NỐI ESP32',
    shortLabel: 'CHƯA KẾT NỐI',
    description: 'Chưa có kết nối với Gateway ESP32-C3. Hãy cấp nguồn kit ESP32 và đảm bảo kết nối Wi-Fi hoặc WebSocket.',
    badgeVariant: 'destructive',
    badgeColorClass: 'border-rose-500/50 text-rose-600 dark:text-rose-400 bg-rose-500/10',
    dotColorClass: 'bg-rose-500',
    pingClass: null,
    iconName: 'radio-off',
  }
}
