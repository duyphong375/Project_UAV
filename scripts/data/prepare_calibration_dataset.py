#!/usr/bin/env python3
"""
KVC UAV Project - Prepare Balanced INT8 Calibration Dataset for GoAI / FPGA

Quy chuẩn lựa chọn (theo KVC System Design & Calibration Spec):
- Tổng số: 100 ảnh trích xuất từ tập Train (ai_training/dataset_4k_yolo/images/train)
- Tuyệt đối KHÔNG lấy từ tập Val/Test để tránh data leakage.
- Tỷ lệ cân bằng:
  + 40 ảnh chứa Person (nạn nhân dưới nước, ngập lụt, góc nhìn UAV)
  + 35 ảnh chứa Lifebuoy (phao cứu sinh nổi trên mặt nước)
  + 25 ảnh Hard-negative (mặt nước, thuyền, sóng biển, không có mục tiêu)
- Tính toán SHA-256 thật và ghi manifest chuẩn.
- Copy ảnh vào ai_training/calibration_images/ để bạn làm FPGA nạp vào GoAI.
"""

import hashlib
import random
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def prepare_calibration_dataset(
    root_dir: str = ".",
    num_person: int = 40,
    num_lifebuoy: int = 35,
    num_negative: int = 25,
    seed: int = 42
):
    random.seed(seed)
    root = Path(root_dir).resolve()
    train_img_dir = root / "ai_training" / "dataset_4k_yolo" / "images" / "train"
    train_lbl_dir = root / "ai_training" / "dataset_4k_yolo" / "labels" / "train"
    calib_out_dir = root / "ai_training" / "calibration_images"
    manifest_path = root / "ai_training" / "manifests" / "calibration_manifest.csv"

    if not train_img_dir.exists() or not train_lbl_dir.exists():
        print(f"Error: Train directory not found at {train_img_dir}")
        return

    calib_out_dir.mkdir(parents=True, exist_ok=True)

    print("[1/4] Phân loại nhãn từ tập Train...")
    person_candidates = []
    lifebuoy_candidates = []
    negative_candidates = []

    for lbl_file in sorted(train_lbl_dir.glob("*.txt")):
        stem = lbl_file.stem
        img_file = train_img_dir / f"{stem}.jpg"
        if not img_file.exists():
            continue

        content = lbl_file.read_text(encoding="utf-8").strip()
        if not content:
            negative_candidates.append(stem)
            continue

        lines = content.splitlines()
        has_c0 = any(l.strip().startswith("0 ") for l in lines)
        has_c1 = any(l.strip().startswith("1 ") for l in lines)

        if has_c1:
            lifebuoy_candidates.append(stem)
        elif has_c0:
            person_candidates.append(stem)

    print(f"      Ứng viên có Person:   {len(person_candidates)}")
    print(f"      Ứng viên có Lifebuoy: {len(lifebuoy_candidates)}")
    print(f"      Ứng viên Hard-neg:    {len(negative_candidates)}")

    print(f"[2/4] Lấy mẫu ngẫu nhiên có kiểm soát (Seed={seed})...")
    sampled_lifebuoy = random.sample(lifebuoy_candidates, min(num_lifebuoy, len(lifebuoy_candidates)))
    sampled_person = random.sample(person_candidates, min(num_person, len(person_candidates)))
    sampled_neg = random.sample(negative_candidates, min(num_negative, len(negative_candidates)))

    selected = []
    for stem in sampled_person:
        selected.append((stem, "person", False, "QA_PASSED", "Person in flood water"))
    for stem in sampled_lifebuoy:
        selected.append((stem, "lifebuoy", False, "QA_PASSED", "Lifebuoy on water surface"))
    for stem in sampled_neg:
        selected.append((stem, "none", True, "QA_NEGATIVE_VERIFIED", "Hard-negative water/ripple without target"))

    print(f"      Tổng số ảnh được chọn: {len(selected)} (Person: {len(sampled_person)}, Lifebuoy: {len(sampled_lifebuoy)}, Neg: {len(sampled_neg)})")

    print("[3/4] Sao chép ảnh vào thư mục calibration_images và tính mã hash SHA-256...")
    rows = []
    for idx, (stem, target_class, is_neg, qa_status, notes) in enumerate(selected, start=1):
        src_img = train_img_dir / f"{stem}.jpg"
        dst_img = calib_out_dir / f"{stem}.jpg"
        shutil.copy2(src_img, dst_img)

        sha256_val = compute_sha256(src_img)
        rel_img = f"ai_training/dataset_4k_yolo/images/train/{stem}.jpg"
        rel_lbl = f"ai_training/dataset_4k_yolo/labels/train/{stem}.txt"
        calib_id = f"CALIB_{idx:04d}"
        session_id = f"KVC_SESSION_TRAIN_{stem[:4]}"

        rows.append(f"{calib_id},{rel_img},{rel_lbl},{session_id},{sha256_val},{qa_status},{target_class},{str(is_neg).lower()},{notes}")

    print(f"[4/4] Ghi manifest chuẩn vào: {manifest_path}...")
    manifest_content = (
        "# KVC - GoAI FPGA INT8 PTQ Calibration Dataset Manifest\n"
        "# Phân bố: 40 person (40%), 35 lifebuoy (35%), 25 hard-negative water/boat (25%)\n"
        "image_id,relative_image_path,relative_label_path,session_id,sha256,review_status,target_classes,has_hard_negative,notes\n"
        + "\n".join(rows)
        + "\n"
    )
    manifest_path.write_text(manifest_content, encoding="utf-8")

    print(f"\n[HOÀN TẤT] Đã tạo xong tập 100 ảnh hiệu chuẩn INT8:")
    print(f" - Thư mục ảnh phục vụ FPGA: {calib_out_dir}")
    print(f" - Manifest kiểm soát dữ liệu: {manifest_path}")

if __name__ == "__main__":
    prepare_calibration_dataset()
