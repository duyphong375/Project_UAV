"""
KVC SAR UAV - Script Huấn Luyện Chuẩn 80 Epochs (Standard YOLO11n 2-Class)
==========================================================================
Cấu hình tối ưu cho GPU NVIDIA GeForce RTX 4060 Laptop (8GB VRAM)
Tác vụ: Detection 2 lớp (0: person, 1: lifebuoy)
Dataset: ai_training/dataset_4k_yolo/data.yaml
"""

import os
import sys
import time
import argparse
import torch

sys.stdout.reconfigure(encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description="KVC SAR UAV - Huấn luyện chuẩn 80 Epochs trên RTX 4060")
    parser.add_argument('--epochs', type=int, default=80, help='Số epoch huấn luyện (mặc định 80)')
    parser.add_argument('--batch', type=int, default=16, help='Batch size (mặc định 16 cho 8GB VRAM)')
    parser.add_argument('--patience', type=int, default=20, help='Patience dừng sớm nếu không tiến bộ (mặc định 20; đặt 0 để chạy đủ 80 epoch)')
    parser.add_argument('--resume', action='store_true', help='Tiếp tục train từ checkpoint last.pt nếu bị ngắt')
    parser.add_argument('--from-boosted', action='store_true', help='Khởi tạo từ yolo11n_2class_best.pt thay vì yolo11n.pt gốc')
    args = parser.parse_args()

    print("=" * 70)
    print("  KVC SAR UAV - HUẤN LUYỆN CHUẨN 80 EPOCHS (YOLO11n 2 LỚP)")
    print("=" * 70)

    # 1. Kiểm tra phần cứng CUDA
    if not torch.cuda.is_available():
        print("❌ LỖI: Không tìm thấy GPU CUDA! Script này yêu cầu NVIDIA GPU.")
        sys.exit(1)

    gpu_name = torch.cuda.get_device_name(0)
    vram_gb = round(torch.cuda.get_device_properties(0).total_memory / 1e9, 2)
    print(f"✅ GPU Phát hiện: {gpu_name} ({vram_gb} GB VRAM)")

    # 2. Thiết lập đường dẫn thư mục
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_yaml = os.path.join(root_dir, 'ai_training', 'dataset_4k_yolo', 'data.yaml')
    runs_dir = os.path.join(root_dir, 'ai_training', 'runs')
    run_name = 'yolo11n_standard_80ep'
    last_ckpt = os.path.join(runs_dir, run_name, 'weights', 'last.pt')

    if not os.path.exists(data_yaml):
        print(f"❌ Không tìm thấy file dữ liệu: {data_yaml}")
        sys.exit(1)

    # 3. Lựa chọn model khởi tạo
    from ultralytics import YOLO

    patience_val = None if args.patience <= 0 else args.patience

    if args.resume:
        if not os.path.exists(last_ckpt):
            print(f"❌ Không tìm thấy checkpoint last.pt tại: {last_ckpt}")
            sys.exit(1)
        print(f"\n🔄 [RESUME] Đang nạp lại checkpoint: {last_ckpt}")
        model = YOLO(last_ckpt)
        print(">>> Tiếp tục huấn luyện...")
        model.train(resume=True)
    else:
        if args.from_boosted:
            base_model = os.path.join(root_dir, 'ai_training', 'weights', 'yolo11n_2class_best.pt')
            print(f"\n📦 Khởi tạo từ checkpoint tối ưu hiện có: {base_model}")
        else:
            base_model = 'yolo11n.pt'
            print(f"\n📦 Khởi tạo từ mô hình gốc Ultralytics: {base_model}")

        model = YOLO(base_model)

        print("\n🚀 Bắt đầu huấn luyện...")
        print(f"  • Tổng Epochs:      {args.epochs}")
        print(f"  • Batch size:       {args.batch}")
        print(f"  • Kích thước ảnh:   640x640")
        print(f"  • Dừng sớm:         {'Tắt (chạy trọn vẹn)' if patience_val is None else f'{patience_val} epochs'}")
        print(f"  • Output Directory: ai_training/runs/{run_name}/")
        print("-" * 70)

        start_time = time.time()
        results = model.train(
            data=data_yaml,
            epochs=args.epochs,
            patience=patience_val,
            batch=args.batch,
            imgsz=640,
            device=0,
            workers=4,
            project=runs_dir,
            name=run_name,
            amp=True,
            plots=True,
            save=True,
            exist_ok=True
        )
        total_mins = round((time.time() - start_time) / 60, 2)
        print("\n" + "=" * 70)
        print(f"🎉 HOÀN TẤT HUẤN LUYỆN SAU {total_mins} PHÚT!")
        print("=" * 70)

    # 4. Đánh giá kiểm định mô hình tốt nhất vừa train
    new_best = os.path.join(runs_dir, run_name, 'weights', 'best.pt')
    if os.path.exists(new_best):
        print("\n📊 Đang chạy kiểm thử Validation chi tiết trên weights/best.pt...")
        eval_model = YOLO(new_best)
        val_metrics = eval_model.val(data=data_yaml, split='val', imgsz=640, device=0)
        
        rd = val_metrics.results_dict
        print("\n🏆 KẾT QUẢ NGHIỆM THU ĐỢT 80 EPOCHS:")
        print(f"  • Precision:   {rd.get('metrics/precision(B)', 0)*100:.2f}%")
        print(f"  • Recall:      {rd.get('metrics/recall(B)', 0)*100:.2f}%")
        print(f"  • mAP@50:      {rd.get('metrics/mAP50(B)', 0)*100:.2f}%")
        print(f"  • mAP@50-95:   {rd.get('metrics/mAP50-95(B)', 0)*100:.2f}%")
        print(f"\n📁 File weights tối ưu: {new_best}")
        print("=" * 70)

if __name__ == '__main__':
    main()
