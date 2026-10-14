import os
import sys
import time
import csv

sys.stdout.reconfigure(encoding='utf-8')

RESULTS_CSV = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "ai_training", "runs", "yolo11n_2class_hardware", "results.csv"
)

TOTAL_EPOCHS = 65

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def monitor():
    if not os.path.exists(RESULTS_CSV):
        print(f"❌ Chưa tìm thấy file log kết quả tại: {RESULTS_CSV}")
        return

    print("🚀 Bắt đầu theo dõi tiến trình huấn luyện KVC YOLO11...")
    print("   (Bấm Ctrl + C để dừng theo dõi bất cứ lúc nào)\n")

    last_epoch = -1

    while True:
        try:
            with open(RESULTS_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            if rows:
                latest = rows[-1]
                epoch = int(latest.get('epoch', 0))
                elapsed_sec = float(latest.get('time', 0))

                # Metrics
                p = float(latest.get('metrics/precision(B)', 0))
                r = float(latest.get('metrics/recall(B)', 0))
                map50 = float(latest.get('metrics/mAP50(B)', 0))
                map50_95 = float(latest.get('metrics/mAP50-95(B)', 0))

                # Losses
                box_loss = float(latest.get('train/box_loss', 0))
                cls_loss = float(latest.get('train/cls_loss', 0))
                val_box = float(latest.get('val/box_loss', 0))
                val_cls = float(latest.get('val/cls_loss', 0))

                # Best mAP50 so far
                best_map50 = max(float(r_item.get('metrics/mAP50(B)', 0)) for r_item in rows)

                # ETA calculation
                avg_time_per_epoch = elapsed_sec / epoch if epoch > 0 else 0
                remaining_epochs = max(0, TOTAL_EPOCHS - epoch)
                eta_minutes = (remaining_epochs * avg_time_per_epoch) / 60

                clear_screen()
                print("=" * 65)
                print("      📊 KVC SAR UAV - THEO DÕI HUẤN LUYỆN YOLO11 (2 LỚP)")
                print("=" * 65)
                print(f"  • Tiến độ       : [Epoch {epoch}/{TOTAL_EPOCHS}] ({(epoch/TOTAL_EPOCHS*100):.1f}%)")
                print(f"  • Thời gian chạy: {elapsed_sec/60:.1f} phút | Ước tính còn lại (ETA): ~{eta_minutes:.1f} phút")
                print("-" * 65)
                print("  📈 CHỈ SỐ NHẬN DIỆN HIỆN TẠI (VAL):")
                print(f"    - mAP@50       : {map50:.4f}  (🌟 Tốt nhất tạm thời: {best_map50:.4f})")
                print(f"    - mAP@50-95    : {map50_95:.4f}")
                print(f"    - Precision    : {p:.4f}")
                print(f"    - Recall       : {r:.4f}")
                print("-" * 65)
                print("  📉 HÀM MẤT MÁT (LOSS):")
                print(f"    - Train Box/Cls: {box_loss:.4f} / {cls_loss:.4f}")
                print(f"    - Val Box/Cls  : {val_box:.4f} / {val_cls:.4f}")
                print("=" * 65)
                print("💡 Mẹo: Dữ liệu tự động cập nhật sau mỗi epoch (khoảng 1-2 phút).")
                print("        Trọng số tốt nhất tự động lưu vào weights/best.pt.")
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n👋 Đã dừng màn hình theo dõi.")
            break
        except Exception as e:
            time.sleep(5)

if __name__ == '__main__':
    monitor()
