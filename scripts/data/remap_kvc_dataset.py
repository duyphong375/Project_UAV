import os
import sys
import shutil
import glob
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATASET_DIR = os.path.join(WORKSPACE_DIR, "ai_training", "dataset_4k_yolo")
LABELS_DIR = os.path.join(DATASET_DIR, "labels")
BACKUP_DIR = os.path.join(DATASET_DIR, "labels_5class_backup")
DATA_YAML_PATH = os.path.join(DATASET_DIR, "data.yaml")

# Hardware Contract 2-class mapping:
#   Original Class 0: swimmer -> Class 0: person
#     [Ngữ nghĩa]: Người bơi / người trôi dạt trên mặt nước. Khớp trực tiếp định nghĩa
#     ontology KVC "person" (người nhìn thấy được trên mặt nước, thuyền hoặc bờ).
#   Original Class 3: life_saving_appliances -> Class 1: lifebuoy
#     [Ngữ nghĩa & Giới hạn]: Trong bộ dữ liệu gốc, class 3 đại diện cho các thiết bị
#     cứu sinh nổi (phao tròn cứu sinh, phao móng ngựa). Khớp định nghĩa KVC "lifebuoy".
#     Lưu ý QA: Cần rà soát ảnh để đảm bảo không lẫn áo phao (lifejacket) bị gán nhầm.
#   Original Class 1: boat, Class 2: jetski, Class 4: buoy -> DROPPED (Chuyển thành ảnh âm tính)
#     [Ngữ nghĩa & Giới hạn]: Thuyền, mô tô nước và phao tiêu/phao neo biển không thuộc
#     đối tượng cứu nạn cốt lõi KVC. Việc loại bỏ các lớp này có chủ đích giúp tạo ra các
#     mẫu Hard-Negative tự nhiên, rèn luyện mô hình triệt tiêu báo động giả khi gặp phương
#     tiện đường thủy hoặc phao báo hiệu luồng lạch.
CLASS_MAPPING = {
    0: 0, # swimmer -> person
    3: 1  # life_saving_appliances -> lifebuoy
}

DROPPED_CLASSES = {
    1: "boat",
    2: "jetski",
    4: "buoy"
}

def backup_labels():
    if os.path.exists(BACKUP_DIR):
        print(f"ℹ️ Thư mục sao lưu đã tồn tại: {BACKUP_DIR}")
        return
    print(f"📦 Đang sao lưu nhãn gốc 5 lớp sang: {BACKUP_DIR} ...")
    shutil.copytree(LABELS_DIR, BACKUP_DIR)
    print("✅ Sao lưu nhãn gốc thành công.")

def remap_dataset():
    backup_labels()

    print("\n🚀 Bắt đầu chuyển đổi nhãn sang chuẩn phần cứng KVC 2 lớp:")
    print("   - Class 0: person (từ swimmer)")
    print("   - Class 1: lifebuoy (từ life_saving_appliances)")
    print("   - Loại bỏ boat, jetski, buoy -> chuyển thành ảnh nền âm tính (Hard-Negative)\n")

    overall_stats = {}

    for split in ['train', 'val']:
        src_split_dir = os.path.join(BACKUP_DIR, split)
        dst_split_dir = os.path.join(LABELS_DIR, split)
        os.makedirs(dst_split_dir, exist_ok=True)

        txt_files = glob.glob(os.path.join(src_split_dir, "*.txt"))

        box_counts = Counter()
        total_files = len(txt_files)
        empty_files = 0
        total_boxes = 0

        for fpath in txt_files:
            fname = os.path.basename(fpath)
            out_path = os.path.join(dst_split_dir, fname)

            remapped_lines = []
            with open(fpath, 'r', encoding='utf-8') as fp:
                for line in fp:
                    parts = line.strip().split()
                    if not parts:
                        continue
                    cls_id = int(parts[0])
                    if cls_id in CLASS_MAPPING:
                        new_cls_id = CLASS_MAPPING[cls_id]
                        remapped_line = f"{new_cls_id} " + " ".join(parts[1:])
                        remapped_lines.append(remapped_line)
                        box_counts[new_cls_id] += 1
                        total_boxes += 1

            if not remapped_lines:
                empty_files += 1

            with open(out_path, 'w', encoding='utf-8') as out_fp:
                if remapped_lines:
                    out_fp.write("\n".join(remapped_lines) + "\n")
                else:
                    out_fp.write("") # File rỗng cho ảnh âm tính (YOLO standard)

        neg_ratio = (empty_files / total_files * 100) if total_files > 0 else 0
        overall_stats[split] = {
            'total_files': total_files,
            'empty_files': empty_files,
            'neg_ratio': neg_ratio,
            'total_boxes': total_boxes,
            'box_counts': box_counts
        }

        print(f"=== KẾT QUẢ SPLIT: {split.upper()} ===")
        print(f"  + Tổng số ảnh/nhãn: {total_files}")
        print(f"  + Số ảnh có mục tiêu (person / lifebuoy): {total_files - empty_files} ({100 - neg_ratio:.1f}%)")
        print(f"  + Số ảnh âm tính (Hard-Negative): {empty_files} ({neg_ratio:.1f}%)")
        print(f"  + Tổng số BBox: {total_boxes}")
        print(f"    - Class 0 (person):   {box_counts[0]} boxes")
        print(f"    - Class 1 (lifebuoy): {box_counts[1]} boxes\n")

    # Cập nhật data.yaml
    yaml_content = f"""path: {DATASET_DIR.replace('\\', '/')}
train: images/train
val: images/val
nc: 2
names:
  0: person
  1: lifebuoy
"""
    with open(DATA_YAML_PATH, 'w', encoding='utf-8') as yfp:
        yfp.write(yaml_content)
    print(f"✅ Đã cập nhật file cấu hình dataset: {DATA_YAML_PATH}")

def audit_dataset_semantics():
    """
    Kiem tra QA ngu nghia giua nhan 5 lop goc va nhan 2 lop sau khi remap.
    Xac minh so luong nhan bi loai (boat, jetski, buoy) va ty le tao thanh Hard-Negative.
    """
    if not os.path.exists(BACKUP_DIR):
        print(f"❌ Khong tim thay thu muc sao luu nhan goc: {BACKUP_DIR}")
        return

    print("=" * 65)
    print("      KVC AI DATASET - KIỂM TOÁN NGỮ NGHĨA (SEMANTIC AUDIT)")
    print("=" * 65)

    ORIGINAL_NAMES = {
        0: "swimmer",
        1: "boat",
        2: "jetski",
        3: "life_saving_appliances",
        4: "buoy"
    }

    for split in ['train', 'val']:
        src_split_dir = os.path.join(BACKUP_DIR, split)
        txt_files = glob.glob(os.path.join(src_split_dir, "*.txt"))

        orig_counts = Counter()
        images_with_dropped_only = 0
        images_with_co_occurrence = 0
        pure_negative_images = 0

        for fpath in txt_files:
            classes_in_file = set()
            with open(fpath, 'r', encoding='utf-8') as fp:
                for line in fp:
                    parts = line.strip().split()
                    if parts:
                        cls_id = int(parts[0])
                        orig_counts[cls_id] += 1
                        classes_in_file.add(cls_id)

            target_present = bool(classes_in_file.intersection({0, 3}))
            dropped_present = bool(classes_in_file.intersection({1, 2, 4}))

            if not classes_in_file:
                pure_negative_images += 1
            elif dropped_present and not target_present:
                images_with_dropped_only += 1
            elif dropped_present and target_present:
                images_with_co_occurrence += 1

        print(f"\n📊 KẾT QUẢ KIỂM TOÁN SPLIT [{split.upper()}]:")
        print(f"  + Tổng số file nhãn: {len(txt_files)}")
        print("  + Phân bố nhãn gốc 5 lớp:")
        for cid in sorted(ORIGINAL_NAMES.keys()):
            mapped_action = "-> person (0)" if cid == 0 else ("-> lifebuoy (1)" if cid == 3 else "-> DROPPED (Hard-Negative)")
            print(f"    - Class {cid} ({ORIGINAL_NAMES[cid]:22s}): {orig_counts[cid]:5d} boxes [{mapped_action}]")
        print(f"  + Số ảnh chuyển thành Hard-Negative do chứa thuyền/phao tiêu không có mục tiêu: {images_with_dropped_only}")
        print(f"  + Số ảnh mục tiêu xuất hiện cùng phương tiện (co-occurrence): {images_with_co_occurrence}")
        print(f"  + Số ảnh nền rỗng thuần túy ban đầu: {pure_negative_images}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="KVC SAR UAV - Remap và kiểm toán nhãn 2 lớp")
    parser.add_argument('--audit', action='store_true', help='Chỉ kiểm toán ngữ nghĩa nhãn gốc và nhãn chuyển đổi')
    args = parser.parse_args()

    if args.audit:
        audit_dataset_semantics()
    else:
        remap_dataset()
        audit_dataset_semantics()
