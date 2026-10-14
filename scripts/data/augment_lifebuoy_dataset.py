"""
KVC SAR UAV - Tăng Cường Dữ Liệu Phao Cứu Sinh (Copy-Paste & Synthetic Marine Augmentation)
========================================================================================
Mục tiêu:
  Trích xuất các mẫu phao cứu sinh (class 1: lifebuoy) thực tế từ tập train,
  áp dụng các phép biến đổi quang học (xoay 360°, đổi kích thước theo độ cao UAV,
  làm mờ viền Gaussian feathering) và cấy ghép lên các ảnh mặt nước âm tính
  để cân bằng tỷ lệ mẫu (giải quyết độ lệch lớp 20:1 và nâng cao Recall).

Quy tắc:
  - Chỉ bổ sung vào tập train (images/train, labels/train).
  - TUYỆT ĐỐI KHÔNG can thiệp vào tập val (để bảo đảm tính khách quan khi đo kiểm).
"""

import os
import sys
import glob
import random
import cv2
import numpy as np

def progress_iter(iterable, desc=""):
    total = len(iterable)
    for i, item in enumerate(iterable):
        if i % 100 == 0 or i == total - 1:
            print(f"[{desc}] Tiến trình: {i+1}/{total} ({(i+1)/total*100:.1f}%)")
        yield item

sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATASET_DIR = os.path.join(WORKSPACE_DIR, "ai_training", "dataset_4k_yolo")
TRAIN_IMG_DIR = os.path.join(DATASET_DIR, "images", "train")
TRAIN_LBL_DIR = os.path.join(DATASET_DIR, "labels", "train")
PATCH_CACHE_DIR = os.path.join(DATASET_DIR, "lifebuoy_patch_cache")


def extract_lifebuoy_patches(max_patches=1000):
    """
    Trích xuất toàn bộ các mẫu phao cứu sinh từ ảnh train ban đầu.
    """
    os.makedirs(PATCH_CACHE_DIR, exist_ok=True)
    existing_cached = glob.glob(os.path.join(PATCH_CACHE_DIR, "*.png"))
    if len(existing_cached) >= 200:
        print(f"📦 Đã tìm thấy {len(existing_cached)} mẫu phao cứu sinh trong bộ nhớ tạm cache.")
        patches = [cv2.imread(p, cv2.IMREAD_UNCHANGED) for p in existing_cached]
        return [p for p in patches if p is not None]

    print("🔍 Đang quét và trích xuất các mẫu phao cứu sinh (class 1) từ tập train...")
    lbl_files = glob.glob(os.path.join(TRAIN_LBL_DIR, "*.txt"))

    patches = []
    patch_idx = 0

    for lpath in progress_iter(lbl_files, desc="Trích xuất phao"):
        # Bỏ qua các file đã được augment từ trước (nếu có)
        if "aug_lifebuoy_" in os.path.basename(lpath):
            continue

        buoy_boxes = []
        with open(lpath, 'r', encoding='utf-8') as fp:
            for line in fp:
                parts = line.strip().split()
                if parts and int(parts[0]) == 1:
                    buoy_boxes.append([float(x) for x in parts[1:5]])

        if not buoy_boxes:
            continue

        base_name = os.path.splitext(os.path.basename(lpath))[0]
        # Tìm file ảnh tương ứng (jpg, png, jpeg)
        img_path = None
        for ext in ['.jpg', '.png', '.jpeg', '.JPG']:
            candidate = os.path.join(TRAIN_IMG_DIR, base_name + ext)
            if os.path.exists(candidate):
                img_path = candidate
                break

        if not img_path:
            continue

        img = cv2.imread(img_path)
        if img is None:
            continue

        h_img, w_img = img.shape[:2]

        for cx_n, cy_n, w_n, h_n in buoy_boxes:
            cx, cy = cx_n * w_img, cy_n * h_img
            bw, bh = w_n * w_img, h_n * h_img

            # Mở rộng biên an toàn 10% để lấy viền nước bao quanh
            margin_x = bw * 0.1
            margin_y = bh * 0.1

            x1 = max(0, int(cx - bw / 2.0 - margin_x))
            y1 = max(0, int(cy - bh / 2.0 - margin_y))
            x2 = min(w_img, int(cx + bw / 2.0 + margin_x))
            y2 = min(h_img, int(cy + bh / 2.0 + margin_y))

            patch_w = x2 - x1
            patch_h = y2 - y1

            # Bỏ qua nếu phao quá nhỏ hoặc không hợp lệ
            if patch_w < 15 or patch_h < 15:
                continue

            crop = img[y1:y2, x1:x2].copy()

            # Tạo kênh Alpha với mặt nạ hình elip và làm mờ viền Gaussian
            mask = np.zeros((patch_h, patch_w), dtype=np.uint8)
            center = (patch_w // 2, patch_h // 2)
            axes = (int(patch_w * 0.45), int(patch_h * 0.45))
            cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)

            # Feathering viền mặt nạ bằng Gaussian Blur
            ksize = max(5, int(min(patch_w, patch_h) * 0.15) | 1)
            mask_feathered = cv2.GaussianBlur(mask, (ksize, ksize), 0)

            # Ghép thành ảnh RGBA (4 kênh)
            rgba = cv2.cvtColor(crop, cv2.COLOR_BGR2BGRA)
            rgba[:, :, 3] = mask_feathered

            # Lưu vào cache để tái sử dụng
            cache_file = os.path.join(PATCH_CACHE_DIR, f"buoy_patch_{patch_idx:04d}.png")
            cv2.imwrite(cache_file, rgba)
            patches.append(rgba)
            patch_idx += 1

            if len(patches) >= max_patches:
                break
        if len(patches) >= max_patches:
            break

    print(f"✅ Đã trích xuất và tối ưu {len(patches)} mẫu phao cứu sinh thực tế.")
    return patches


def transform_patch(patch_rgba, scale_factor=1.0, angle_deg=0):
    """
    Xoay tự do góc và thay đổi kích thước phao cứu sinh mô phỏng góc nhìn UAV.
    """
    h, w = patch_rgba.shape[:2]

    # 1. Resize theo tỷ lệ
    new_w = max(16, int(round(w * scale_factor)))
    new_h = max(16, int(round(h * scale_factor)))
    resized = cv2.resize(patch_rgba, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    # 2. Xoay góc tự do
    center = (new_w // 2, new_h // 2)
    rot_mat = cv2.getRotationMatrix2D(center, angle_deg, 1.0)

    # Tính kích thước bounding box bao quanh góc xoay
    cos = np.abs(rot_mat[0, 0])
    sin = np.abs(rot_mat[0, 1])
    bound_w = int((new_h * sin) + (new_w * cos))
    bound_h = int((new_h * cos) + (new_w * sin))
    rot_mat[0, 2] += (bound_w / 2) - center[0]
    rot_mat[1, 2] += (bound_h / 2) - center[1]

    rotated = cv2.warpAffine(
        resized,
        rot_mat,
        (bound_w, bound_h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0)
    )

    # 3. Biến đổi độ sáng nhẹ (ánh nắng / phản chiếu nước)
    bgr = rotated[:, :, :3]
    alpha = rotated[:, :, 3]

    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    val_mult = random.uniform(0.9, 1.15)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * val_mult, 0, 255)
    bgr_jitter = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    final_rgba = np.dstack([bgr_jitter, alpha])
    return final_rgba


def blend_patch_onto_image(bg_img, patch_rgba, x_topleft, y_topleft):
    """
    Hòa trộn phao cứu sinh lên ảnh nền mặt nước sử dụng kênh Alpha làm mờ viền.
    """
    bg_h, bg_w = bg_img.shape[:2]
    p_h, p_w = patch_rgba.shape[:2]

    x1 = max(0, x_topleft)
    y1 = max(0, y_topleft)
    x2 = min(bg_w, x_topleft + p_w)
    y2 = min(bg_h, y_topleft + p_h)

    crop_w = x2 - x1
    crop_h = y2 - y1

    if crop_w <= 0 or crop_h <= 0:
        return bg_img, None

    # Vùng patch tương ứng
    px1 = x1 - x_topleft
    py1 = y1 - y_topleft
    px2 = px1 + crop_w
    py2 = py1 + crop_h

    patch_crop = patch_rgba[py1:py2, px1:px2]
    patch_bgr = patch_crop[:, :, :3].astype(np.float32)
    alpha = (patch_crop[:, :, 3].astype(np.float32) / 255.0)[:, :, np.newaxis]

    bg_roi = bg_img[y1:y2, x1:x2].astype(np.float32)
    blended_roi = patch_bgr * alpha + bg_roi * (1.0 - alpha)

    bg_img[y1:y2, x1:x2] = np.clip(blended_roi, 0, 255).astype(np.uint8)

    # Trả về tọa độ bounding box chuẩn hóa YOLO
    cx_norm = (x1 + crop_w / 2.0) / bg_w
    cy_norm = (y1 + crop_h / 2.0) / bg_h
    w_norm = crop_w / bg_w
    h_norm = crop_h / bg_h

    return bg_img, (cx_norm, cy_norm, w_norm, h_norm)


def augment_dataset(num_new_images=800):
    """
    Tạo thêm num_new_images ảnh mới có chứa phao cứu sinh,
    cấy lên các ảnh mặt nước âm tính và ảnh train ngẫu nhiên.
    """
    patches = extract_lifebuoy_patches(max_patches=1000)
    if not patches:
        print("❌ Không có mẫu phao cứu sinh nào được trích xuất!")
        return

    # Lấy danh sách ảnh train gốc (không lấy ảnh đã augment)
    all_train_imgs = sorted(glob.glob(os.path.join(TRAIN_IMG_DIR, "*.*")))
    pure_train_imgs = [p for p in all_train_imgs if "aug_lifebuoy_" not in os.path.basename(p)]

    # Ưu tiên các ảnh Hard-Negative (ảnh mặt nước không có nhãn hoặc rỗng)
    negative_imgs = []
    other_imgs = []

    for img_path in pure_train_imgs:
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        lbl_path = os.path.join(TRAIN_LBL_DIR, base_name + ".txt")
        if os.path.exists(lbl_path):
            with open(lbl_path, 'r', encoding='utf-8') as fp:
                lines = [line.strip() for line in fp if line.strip()]
            if not lines:
                negative_imgs.append(img_path)
            else:
                other_imgs.append(img_path)
        else:
            negative_imgs.append(img_path)

    print(f"\n📊 Phân bố ảnh nền sẵn có: {len(negative_imgs)} ảnh mặt nước âm tính, {len(other_imgs)} ảnh có mục tiêu.")
    print(f"🚀 Bắt đầu sinh {num_new_images} ảnh tăng cường phao cứu sinh (Copy-Paste)...")

    # Chọn danh sách ảnh nền để cấy phao
    bg_candidates = (negative_imgs * 2 + other_imgs)
    random.shuffle(bg_candidates)
    selected_bgs = bg_candidates[:num_new_images]

    generated_count = 0
    total_new_buoys = 0

    for idx, bg_path in enumerate(progress_iter(selected_bgs, desc="Tạo ảnh cấy phao")):
        bg_img = cv2.imread(bg_path)
        if bg_img is None:
            continue

        bg_h, bg_w = bg_img.shape[:2]
        base_name = os.path.splitext(os.path.basename(bg_path))[0]
        lbl_path = os.path.join(TRAIN_LBL_DIR, base_name + ".txt")

        # Đọc các nhãn sẵn có trên ảnh nền
        existing_labels = []
        if os.path.exists(lbl_path):
            with open(lbl_path, 'r', encoding='utf-8') as fp:
                existing_labels = [line.strip() for line in fp if line.strip()]

        # Cấy từ 1 đến 3 chiếc phao cứu sinh vào ảnh nền
        num_buoys_to_paste = random.choices([1, 2, 3], weights=[0.5, 0.35, 0.15])[0]
        new_labels = list(existing_labels)

        for _ in range(num_buoys_to_paste):
            patch = random.choice(patches)

            # Biến đổi góc xoay ngẫu nhiên 0..360° và tỷ lệ 0.6x..1.4x
            scale = random.uniform(0.65, 1.35)
            angle = random.uniform(0.0, 360.0)
            trans_patch = transform_patch(patch, scale_factor=scale, angle_deg=angle)

            tp_h, tp_w = trans_patch.shape[:2]
            if tp_w >= bg_w or tp_h >= bg_h:
                continue

            # Vị trí ngẫu nhiên trên mặt nước
            pos_x = random.randint(10, bg_w - tp_w - 10)
            pos_y = random.randint(10, bg_h - tp_h - 10)

            bg_img, bbox_norm = blend_patch_onto_image(bg_img, trans_patch, pos_x, pos_y)
            if bbox_norm is not None:
                cx_n, cy_n, w_n, h_n = bbox_norm
                new_labels.append(f"1 {cx_n:.6f} {cy_n:.6f} {w_n:.6f} {h_n:.6f}")
                total_new_buoys += 1

        # Lưu ảnh mới
        out_img_name = f"aug_lifebuoy_{idx:04d}.jpg"
        out_lbl_name = f"aug_lifebuoy_{idx:04d}.txt"

        out_img_path = os.path.join(TRAIN_IMG_DIR, out_img_name)
        out_lbl_path = os.path.join(TRAIN_LBL_DIR, out_lbl_name)

        cv2.imwrite(out_img_path, bg_img)
        with open(out_lbl_path, 'w', encoding='utf-8') as ofp:
            ofp.write("\n".join(new_labels) + "\n")

        generated_count += 1

    print("=" * 65)
    print("🎉 HOÀN TẤT TĂNG CƯỜNG DỮ LIỆU PHAO CỨU SINH!")
    print("=" * 65)
    print(f"  + Số ảnh mới được sinh ra: {generated_count} ảnh")
    print(f"  + Số lượng phao cứu sinh (class 1) bổ sung thêm: +{total_new_buoys} phao")
    print(f"  + Lưu trực tiếp tại: {TRAIN_IMG_DIR} & {TRAIN_LBL_DIR}")


if __name__ == '__main__':
    augment_dataset(num_new_images=800)
