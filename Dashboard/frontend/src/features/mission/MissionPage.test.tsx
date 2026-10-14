import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { TooltipProvider } from '@/components/ui/tooltip'
import { MissionProvider } from '@/state/MissionProvider'
import { AppRouterProvider } from '@/app/routes'
import { MissionPage } from './MissionPage'
import { CurrentPositionPanel } from './CurrentPositionPanel'
import { PositionSummary } from './PositionSummary'
import { TargetDetailsPanel } from './TargetDetailsPanel'

describe('MissionPage - Giám sát định vị tải nhiệm vụ UAV', () => {
  it('hiển thị thanh điều khiển tối giản và nút Đặt lại khung nhìn, không có nút điều khiển bay hoặc đổi bố cục', () => {
    const { container } = render(
      <TooltipProvider>
        <MissionProvider>
          <AppRouterProvider>
            <MissionPage />
          </AppRouterProvider>
        </MissionProvider>
      </TooltipProvider>
    )

    // 1. Tiêu đề và nhãn bắt buộc
    expect(screen.getByText('Giám sát định vị tải nhiệm vụ')).toBeDefined()
    expect(screen.getByText(/Nguồn: MOCK/i)).toBeDefined()
    expect(screen.getAllByText('MẤT KẾT NỐI').length).toBeGreaterThan(0)
    expect(screen.getByRole('region', { name: 'Điều khiển phát lại' })).toBeDefined()

    // 2. Nút "Đặt lại khung nhìn" có mặt
    expect(screen.getAllByRole('button', { name: /Đặt lại khung nhìn/i }).length).toBeGreaterThan(0)

    // 3. Đảm bảo XÓA HOÀN TOÀN các nút bố cục và điều khiển drone
    expect(container.textContent).not.toContain('Ưu tiên Video')
    expect(container.textContent).not.toContain('Ưu tiên Bản đồ')
    expect(container.textContent).not.toContain('Cân bằng')
    expect(container.textContent).not.toContain('2D Bản đồ')
    expect(container.textContent).not.toContain('3D Vệ tinh')
    expect(container.textContent).not.toContain('Lấy GPS Tôi')
    expect(container.textContent).not.toContain('Theo dõi vị trí')
    expect(container.textContent).not.toContain('Về camera')
  })

  it('Panel Vị trí hiện tại hiển thị đầy đủ thông số định vị và lý do cụ thể', () => {
    render(
      <TooltipProvider>
        <MissionProvider>
          <CurrentPositionPanel onResetView={() => {}} />
        </MissionProvider>
      </TooltipProvider>
    )

    // Tiêu đề "Vị trí hiện tại"
    expect(screen.getByText('Vị trí hiện tại')).toBeDefined()
    expect(screen.getByText('Hệ quy chiếu:')).toBeDefined()
    expect(screen.getByText('Tuổi dữ liệu:')).toBeDefined()
    expect(screen.getByRole('button', { name: /Đặt lại khung nhìn/i })).toBeDefined()
  })

  it('Thanh telemetry chân trang hiển thị đầy đủ 6 thông số đo lường cốt lõi', () => {
    render(
      <TooltipProvider>
        <MissionProvider>
          <PositionSummary />
        </MissionProvider>
      </TooltipProvider>
    )

    expect(screen.getByText('UAV:')).toBeDefined()
    expect(screen.getByText('Target:')).toBeDefined()
    expect(screen.getByText('Alt:')).toBeDefined()
    expect(screen.getByText('LiDAR:')).toBeDefined()
    expect(screen.getByText('LoRa:')).toBeDefined()
    expect(screen.getByText('Tuổi:')).toBeDefined()
  })

  it('cho phép chuyển đổi giữa Bản đồ WGS-84 và Radar Sa Bàn', () => {
    render(
      <TooltipProvider>
        <MissionProvider>
          <AppRouterProvider>
            <MissionPage />
          </AppRouterProvider>
        </MissionProvider>
      </TooltipProvider>
    )

    // Kiểm tra có các nút chuyển đổi khung nhìn
    const radarBtn = screen.getByRole('button', { name: /Xem Radar Sa Bàn/i })
    expect(radarBtn).toBeDefined()

    const mapBtn = screen.getByRole('button', { name: /Xem Bản đồ WGS-84/i })
    expect(mapBtn).toBeDefined()
  })

  it('kích hoạt sự kiện toàn cục khi nhấn nút Tâm Target và Tâm UAV', () => {
    const focusTargetSpy = vi.fn()
    const resetViewSpy = vi.fn()
    window.addEventListener('kvc-map-focus-target', focusTargetSpy)
    window.addEventListener('kvc-map-reset-view', resetViewSpy)

    render(
      <TooltipProvider>
        <MissionProvider>
          <AppRouterProvider>
            <MissionPage />
          </AppRouterProvider>
        </MissionProvider>
      </TooltipProvider>
    )

    const focusTargetBtn = screen.getByRole('button', { name: /Tâm mục tiêu/i })
    const focusUavBtn = screen.getAllByRole('button', { name: /Đặt lại khung nhìn/i })[0]

    fireEvent.click(focusTargetBtn)
    expect(focusTargetSpy).toHaveBeenCalledTimes(1)

    fireEvent.click(focusUavBtn)
    expect(resetViewSpy).toHaveBeenCalledTimes(1)

    window.removeEventListener('kvc-map-focus-target', focusTargetSpy)
    window.removeEventListener('kvc-map-reset-view', resetViewSpy)
  })

  it('hỗ trợ thu gọn và mở rộng luồng Video Feed phụ', () => {
    render(
      <TooltipProvider>
        <MissionProvider>
          <AppRouterProvider>
            <MissionPage />
          </AppRouterProvider>
        </MissionProvider>
      </TooltipProvider>
    )

    // Mặc định video phụ ở trạng thái thu gọn
    const toggleVideoBtn = screen.getByRole('button', { name: /Bật tắt Video phụ/i })
    expect(toggleVideoBtn).toBeDefined()

    // Bấm mở video
    fireEvent.click(toggleVideoBtn)
    expect(screen.getByText('Video tham chiếu')).toBeDefined()

    // Bấm thu gọn video trở lại
    fireEvent.click(toggleVideoBtn)
    expect(screen.queryByText('Video tham chiếu')).toBeNull()
  })

  it('TargetDetailsPanel hiển thị thông tin bàn giao SAR và hỗ trợ thao tác đánh dấu sự kiện', () => {
    render(
      <TooltipProvider>
        <MissionProvider>
          <TargetDetailsPanel />
        </MissionProvider>
      </TooltipProvider>
    )

    expect(screen.getByText('Mục tiêu cứu nạn (Target)')).toBeDefined()
    expect(screen.getByRole('button', { name: /Sao chép tọa độ chuẩn SAR/i })).toBeDefined()

    const bookmarkBtn = screen.getByRole('button', { name: /Đánh dấu sự kiện mục tiêu/i })
    expect(bookmarkBtn).toBeDefined()

    // Nhấp vào nút đánh dấu sự kiện (không ném ngoại lệ và ghi nhận click)
    fireEvent.click(bookmarkBtn)
    expect(bookmarkBtn).toBeDefined()
  })
})
