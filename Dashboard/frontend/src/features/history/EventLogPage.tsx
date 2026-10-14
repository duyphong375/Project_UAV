import React, { useMemo, useState } from 'react'
import {
  Download,
  FilterX,
  History,
  RotateCcw,
  Search,
} from 'lucide-react'
import { PageHeader } from '@/components/shared/PageHeader'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useMission } from '@/state/MissionProvider'
import type { AlertLevel, AlertSourceCategory } from '@/types/telemetry'
import { EventLogTable } from './EventLogTable'

export const EventLogPage: React.FC = () => {
  const { state } = useMission()
  const { event_logs, source_mode } = state

  const [searchKeyword, setSearchKeyword] = useState('')
  const [levelFilter, setLevelFilter] = useState<'ALL' | AlertLevel>('ALL')
  const [sourceFilter, setSourceFilter] = useState<'ALL' | AlertSourceCategory>('ALL')

  // Lọc dữ liệu nhật ký
  const filteredLogs = useMemo(() => {
    return event_logs.filter((log) => {
      if (levelFilter !== 'ALL' && log.level !== levelFilter) {
        return false
      }
      if (sourceFilter !== 'ALL' && log.source !== sourceFilter) {
        return false
      }
      if (searchKeyword.trim()) {
        const q = searchKeyword.toLowerCase()
        const matchCode = log.code.toLowerCase().includes(q)
        const matchMsg = log.message.toLowerCase().includes(q)
        const matchSource = log.source.toLowerCase().includes(q)
        if (!matchCode && !matchMsg && !matchSource) {
          return false
        }
      }
      return true
    })
  }, [event_logs, levelFilter, sourceFilter, searchKeyword])

  const hasActiveFilter = searchKeyword.trim() !== '' || levelFilter !== 'ALL' || sourceFilter !== 'ALL'

  const handleResetFilter = () => {
    setSearchKeyword('')
    setLevelFilter('ALL')
    setSourceFilter('ALL')
  }

  // Xuất file CSV từ dữ liệu đã lọc
  const handleExportCsv = () => {
    if (filteredLogs.length === 0) return

    const headers = ['Thời gian', 'Mức độ', 'Nguồn', 'Mã sự kiện', 'Nội dung', 'Phiên']
    const rows = filteredLogs.map((item) => [
      `"${item.timestamp_iso}"`,
      `"${item.level}"`,
      `"${item.source}"`,
      `"${item.code.replace(/"/g, '""')}"`,
      `"${item.message.replace(/"/g, '""')}"`,
      `"${item.session_id}"`,
    ])

    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\r\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.setAttribute('href', url)
    link.setAttribute('download', `kvc_rescue_evidence_${Date.now()}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="flex-1 flex flex-col p-3 sm:p-5 gap-3.5 sm:gap-4 overflow-y-auto max-w-7xl mx-auto w-full select-none">
      {/* 1. Header Trang */}
      <PageHeader
        breadcrumb="Dữ liệu · Nhật ký sự kiện"
        title="Nhật ký phiên & Bằng chứng cứu hộ"
        subtitle={`Lưu trữ chuỗi sự kiện hoạt động, mốc thời gian phát hiện mục tiêu và xuất file bằng chứng cứu nạn [${source_mode}].`}
        badge={
          <Badge variant="outline" className="text-xs font-mono">
            {event_logs.length} bản ghi
          </Badge>
        }
        actions={
          <div className="flex items-center gap-2">
            {hasActiveFilter && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleResetFilter}
                className="h-8 text-xs gap-1 text-muted-foreground hover:text-foreground"
              >
                <RotateCcw className="h-3.5 w-3.5" />
                <span>Đặt lại</span>
              </Button>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={handleExportCsv}
              disabled={filteredLogs.length === 0}
              className="h-8 text-xs gap-1.5 border-border shadow-xs hover:border-primary/50"
            >
              <Download className="h-3.5 w-3.5 text-primary" />
              <span>Xuất CSV bằng chứng ({filteredLogs.length})</span>
            </Button>
          </div>
        }
      />

      {/* 2. Thanh Tìm Kiếm và Bộ Lọc */}
      <div className="flex flex-wrap items-center gap-2 p-2.5 rounded-xl border border-border bg-card text-xs shadow-xs">
        {/* Ô Tìm Kiếm */}
        <div className="flex items-center gap-2 flex-1 min-w-[200px] px-2.5 py-1.5 rounded-lg border border-input bg-background">
          <Search className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
          <input
            type="text"
            placeholder="Tìm theo mã sự kiện, nội dung hoặc nguồn..."
            value={searchKeyword}
            onChange={(e) => setSearchKeyword(e.target.value)}
            className="w-full bg-transparent text-xs text-foreground placeholder:text-muted-foreground focus:outline-none"
          />
        </div>

        {/* Lọc Mức Độ */}
        <div className="flex items-center gap-1.5">
          <span className="text-muted-foreground font-medium">Mức độ:</span>
          <Select
            value={levelFilter}
            onValueChange={(val) => setLevelFilter(val as 'ALL' | AlertLevel)}
          >
            <SelectTrigger className="h-8 w-[120px] text-xs">
              <SelectValue placeholder="Tất cả" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">Tất cả</SelectItem>
              <SelectItem value="INFO">INFO</SelectItem>
              <SelectItem value="WARN">WARN</SelectItem>
              <SelectItem value="CRITICAL">CRITICAL</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Lọc Nguồn */}
        <div className="flex items-center gap-1.5">
          <span className="text-muted-foreground font-medium">Nguồn:</span>
          <Select
            value={sourceFilter}
            onValueChange={(val) => setSourceFilter(val as 'ALL' | AlertSourceCategory)}
          >
            <SelectTrigger className="h-8 w-[130px] text-xs">
              <SelectValue placeholder="Tất cả" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">Tất cả nguồn</SelectItem>
              <SelectItem value="GPS">GNSS / GPS</SelectItem>
              <SelectItem value="VIDEO">Video Stream</SelectItem>
              <SelectItem value="TELEMETRY">Telemetry / RF</SelectItem>
              <SelectItem value="SENSORS">Cảm biến</SelectItem>
              <SelectItem value="STORAGE">Lưu trữ</SelectItem>
              <SelectItem value="SYSTEM">Hệ thống</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* 3. Bảng Dữ Liệu hoặc Trạng Thái Rỗng */}
      <div className="flex-1 pb-6">
        {event_logs.length === 0 ? (
          <div className="py-16 border border-border rounded-2xl bg-card text-center flex flex-col items-center justify-center gap-2 shadow-xs">
            <History className="h-10 w-10 stroke-[1.5] text-muted-foreground/40" />
            <span className="text-sm font-semibold text-foreground">
              Chưa có sự kiện nào được ghi nhận trong phiên
            </span>
            <span className="text-xs text-muted-foreground max-w-sm">
              Nhật ký sẽ tự động cập nhật khi có thông tin bám bắt mục tiêu, lưu bằng chứng hoặc thay đổi trạng thái phần cứng.
            </span>
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="py-16 border border-border rounded-2xl bg-card text-center flex flex-col items-center justify-center gap-2 shadow-xs">
            <FilterX className="h-10 w-10 stroke-[1.5] text-muted-foreground/40" />
            <span className="text-sm font-semibold text-foreground">
              Không có sự kiện phù hợp với từ khóa hoặc bộ lọc
            </span>
            <span className="text-xs text-muted-foreground">
              Thử xóa từ khóa tìm kiếm hoặc chọn &quot;Tất cả&quot; ở các bộ lọc mức độ.
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={handleResetFilter}
              className="mt-2 text-xs"
            >
              Xóa bộ lọc
            </Button>
          </div>
        ) : (
          <EventLogTable entries={filteredLogs} />
        )}
      </div>
    </div>
  )
}
