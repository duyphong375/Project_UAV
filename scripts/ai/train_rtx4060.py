import os
import sys
import argparse
import torch
from ultralytics import YOLO

sys.stdout.reconfigure(encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description="KVC SAR UAV - Huấn luyện YOLO11 2 lớp phần cứng")
    parser.add_argument('--resume', action='store_true', help='Tiếp tục train từ checkpoint last.pt gần nhất')
    args = parser.parse_args()

    print("=" * 60)
    print("  KVC SAR UAV - HUẤN LUYỆN YOLO11 CHUẨN 2 LỚP PHẦN CỨNG")
    print("  (Class 0: person | Class 1: lifebuoy | Tích hợp Hard-Negatives)")
    print("=" * 60)

    if not torch.cuda.is_available():
        print("❌ Cảnh báo: Không tìm thấy GPU CUDA! Sẽ chạy trên CPU.")
        device = 'cpu'
    else:
        gpu_name = torch.cuda.get_device_name(0)
        vram = round(torch.cuda.get_device_properties(0).total_memory / 1e9, 2)
        print(f"✅ Đang sử dụng GPU: {gpu_name} ({vram} GB VRAM)")
        device = 0

    workspace_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    runs_project_dir = os.path.join(workspace_dir, 'ai_training', 'runs')
    last_checkpoint = os.path.join(runs_project_dir, 'yolo11n_2class_hardware', 'weights', 'last.pt')
    initial_model = os.path.join(workspace_dir, 'ai_training', 'weights', 'best.pt')
    data_path = os.path.join(workspace_dir, 'ai_training', 'dataset_4k_yolo', 'data.yaml')

    if args.resume:
        if not os.path.exists(last_checkpoint):
            print(f"❌ Không tìm thấy checkpoint để tiếp tục tại: {last_checkpoint}!")
            return
        print(f"\n🔄 [RESUME] Đang nạp checkpoint gần nhất: {last_checkpoint}")
        model = YOLO(last_checkpoint)
        print(">>> Tiếp tục huấn luyện từ epoch đã lưu...")
        results = model.train(resume=True)
    else:
        if not os.path.exists(initial_model):
            print(f"❌ Không tìm thấy model tại {initial_model}!")
            return
        if not os.path.exists(data_path):
            print(f"❌ Không tìm thấy cấu hình dataset tại {data_path}!")
            return

        print(f"\n>>> Nạp mô hình trọng số ban đầu: {initial_model}")
        model = YOLO(initial_model)

        print("\n>>> Bắt đầu huấn luyện mô hình 2 lớp trên RTX 4060...")
        print(">>> (Bấm Ctrl + C nếu muốn dừng, có thể resume lại sau)\n")

        results = model.train(
            data=data_path,
            epochs=65,
            patience=15,
            imgsz=640,
            batch=16,
            device=device,
            workers=4,
            project=runs_project_dir,
            name='yolo11n_2class_hardware',
            save=True
        )

    print("\n" + "=" * 60)
    print("🎉 HOÀN TẤT HUẤN LUYỆN MÔ HÌNH 2 LỚP!")
    print("📁 File trọng số tối ưu nhất đã được lưu tại:")
    print("   ai_training/runs/yolo11n_2class_hardware/weights/best.pt")
    print("=" * 60)

if __name__ == '__main__':
    main()
