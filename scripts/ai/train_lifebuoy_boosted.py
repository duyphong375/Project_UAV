"""
KVC SAR UAV - Huấn Luyện Tinh Chỉnh Nâng Cao Recall Phao Cứu Sinh (Lifebuoy-Boosted)
=====================================================================================
Mục tiêu:
  - Khởi tạo từ checkpoint tối ưu hiện có: ai_training/runs/yolo11n_2class_hardware/weights/best.pt
  - Huấn luyện tiếp 35 epochs trên tập dữ liệu đã tăng cường cân bằng mẫu phao cứu sinh
  - Duy trì độ chính xác cao của lớp 'person' (Precision ~78%) đồng thời đột phá
    Recall và mAP50 của lớp 'lifebuoy' (từ 37.3% lên >60%)
  - Tự động chạy validation trên tập val nguyên bản để đo lường định lượng kết quả.
"""

import os
import sys
import argparse
import time
import torch
from ultralytics import YOLO

sys.stdout.reconfigure(encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description="KVC SAR UAV - Fine-tuning YOLO11 Boosted Lifebuoy")
    parser.add_argument('--epochs', type=int, default=35, help='Số epoch huấn luyện tinh chỉnh (mặc định 35)')
    parser.add_argument('--batch', type=int, default=16, help='Batch size (mặc định 16 cho RTX 4060)')
    parser.add_argument('--lr0', type=float, default=0.005, help='Tốc độ học ban đầu cho fine-tune (mặc định 0.005)')
    args = parser.parse_args()

    print("=" * 68)
    print("  KVC SAR UAV - HUẤN LUYỆN YOLO11 BOOSTED LIFEBUOY (RTX 4060)")
    print("=" * 68)

    if not torch.cuda.is_available():
        print("❌ Lỗi: Cần GPU CUDA để huấn luyện mô hình!")
        sys.exit(1)

    gpu_name = torch.cuda.get_device_name(0)
    vram = round(torch.cuda.get_device_properties(0).total_memory / 1e9, 2)
    print(f"✅ GPU sẵn sàng: {gpu_name} ({vram} GB VRAM)")

    workspace_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    runs_dir = os.path.join(workspace_dir, 'ai_training', 'runs')
    base_checkpoint = os.path.join(runs_dir, 'yolo11n_2class_hardware', 'weights', 'best.pt')
    data_yaml = os.path.join(workspace_dir, 'ai_training', 'dataset_4k_yolo', 'data.yaml')

    if not os.path.exists(base_checkpoint):
        print(f"❌ Không tìm thấy checkpoint gốc: {base_checkpoint}")
        sys.exit(1)

    if not os.path.exists(data_yaml):
        print(f"❌ Không tìm thấy data.yaml: {data_yaml}")
        sys.exit(1)

    print(f"📁 Checkpoint gốc: {base_checkpoint}")
    print(f"📁 Cấu hình dữ liệu: {data_yaml}")
    print(f"🎯 Epochs: {args.epochs} | Batch: {args.batch} | Base LR: {args.lr0}")

    # Nạp mô hình gốc
    print("\n🔄 Đang nạp mô hình từ checkpoint gốc...")
    model = YOLO(base_checkpoint)

    # Bắt đầu huấn luyện fine-tune
    start_time = time.time()
    print("\n🚀 Bắt đầu quá trình huấn luyện nâng cấp mô hình...")
    train_results = model.train(
        data=data_yaml,
        epochs=args.epochs,
        patience=12,
        imgsz=640,
        batch=args.batch,
        device=0,
        workers=4,
        project=runs_dir,
        name='yolo11n_2class_boosted',
        lr0=args.lr0,
        lrf=0.01,
        weight_decay=0.0005,
        save=True,
        plots=True,
        exist_ok=True
    )
    elapsed = time.time() - start_time
    print(f"\n✅ Hoàn tất huấn luyện sau {elapsed / 60:.2f} phút!")

    # Đường dẫn checkpoint tốt nhất mới
    boosted_best = os.path.join(runs_dir, 'yolo11n_2class_boosted', 'weights', 'best.pt')
    if not os.path.exists(boosted_best):
        print(f"⚠️ Không tìm thấy {boosted_best}, kiểm tra trong thư mục chạy.")
        return

    print("\n" + "=" * 68)
    print("📊 ĐÁNH GIÁ ĐỊNH LƯỢNG TRÊN TẬP VALIDATION NGUYÊN BẢN (KHÔNG CHẠM VÀO)")
    print("=" * 68)
    val_model = YOLO(boosted_best)
    val_res = val_model.val(data=data_yaml, split='val', imgsz=640, device=0)

    # In kết quả chi tiết
    metrics = val_res.results_dict
    print("\n📈 Kết quả Validation Chi Tiết:")
    print(f"  + Overall mAP50:    {metrics.get('metrics/mAP50(B)', 0)*100:.2f}%")
    print(f"  + Overall mAP50-95: {metrics.get('metrics/mAP50-95(B)', 0)*100:.2f}%")
    print(f"  + Precision(B):     {metrics.get('metrics/precision(B)', 0)*100:.2f}%")
    print(f"  + Recall(B):        {metrics.get('metrics/recall(B)', 0)*100:.2f}%")

    # In từng lớp
    if hasattr(val_res, 'box') and hasattr(val_res.box, 'ap50'):
        classes = ['person', 'lifebuoy']
        ap50s = val_res.box.ap50
        ap_all = val_res.box.ap
        ps = val_res.box.p
        rs = val_res.box.r
        print("\n🏆 Chi tiết từng lớp mục tiêu:")
        for idx, cname in enumerate(classes):
            if idx < len(ap50s):
                p_c = ps[idx] * 100 if idx < len(ps) else 0
                r_c = rs[idx] * 100 if idx < len(rs) else 0
                map50_c = ap50s[idx] * 100
                map95_c = ap_all[idx] * 100 if idx < len(ap_all) else 0
                print(f"  [{cname.upper()}] P: {p_c:.1f}% | R: {r_c:.1f}% | mAP50: {map50_c:.1f}% | mAP50-95: {map95_c:.1f}%")

    print("\n" + "=" * 68)
    print(f"💾 Checkpoint tối ưu mới: {boosted_best}")
    print("=" * 68)

if __name__ == '__main__':
    main()
