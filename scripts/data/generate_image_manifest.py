"""Generate a conservative, provenance-aware image inventory for KVC.

The default invocation is a dry run. Writing requires ``--write`` and an
existing manifest is never replaced unless ``--force`` is also supplied.
Generated rows contain real file hashes but deliberately leave provenance and
human-QA fields unverified instead of inventing evidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path
from typing import Iterable


WORKSPACE_DIR = Path(__file__).resolve().parents[2]
DATASET_DIR = WORKSPACE_DIR / "ai_training" / "dataset_4k_yolo"
MANIFEST_PATH = WORKSPACE_DIR / "ai_training" / "manifests" / "image_manifest.csv"
IMAGE_SUFFIXES = {".bmp", ".jpeg", ".jpg", ".png", ".webp"}

CLASS_NAMES = {0: "person", 1: "lifebuoy"}
FIELDNAMES = [
    "image_id",
    "source_path",
    "session_id",
    "frame_index",
    "capture_timestamp",
    "domain",
    "split",
    "sha256",
    "classes_present",
    "occluded",
    "truncated",
    "review_status",
    "annotator",
    "qa_reviewer",
    "review_evidence",
    "notes",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_classes(label_path: Path) -> tuple[set[str], bool]:
    if not label_path.exists():
        return set(), False

    classes: set[str] = set()
    with label_path.open("r", encoding="utf-8") as stream:
        for line in stream:
            parts = line.strip().split()
            if not parts:
                continue
            try:
                class_id = int(parts[0])
            except ValueError:
                classes.add("invalid_class_id")
                continue
            classes.add(CLASS_NAMES.get(class_id, f"class_{class_id}"))
    return classes, True


def build_manifest_rows(
    dataset_dir: Path = DATASET_DIR,
    *,
    workspace_dir: Path = WORKSPACE_DIR,
    limit_per_split: int | None = None,
) -> list[dict[str, object]]:
    if limit_per_split is not None and limit_per_split < 1:
        raise ValueError("limit_per_split must be positive or None")

    rows: list[dict[str, object]] = []
    for split in ("train", "val"):
        image_dir = dataset_dir / "images" / split
        label_dir = dataset_dir / "labels" / split
        if not image_dir.is_dir():
            continue

        image_paths = sorted(
            path
            for path in image_dir.iterdir()
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
        )
        selected_paths = image_paths[:limit_per_split] if limit_per_split else image_paths

        for frame_index, image_path in enumerate(selected_paths):
            label_path = label_dir / f"{image_path.stem}.txt"
            classes, label_exists = _read_classes(label_path)
            if not label_exists:
                class_value = "unknown"
                notes = "Label file missing; provenance and semantic QA pending"
            elif classes:
                class_value = ";".join(sorted(classes))
                notes = "Classes read from label file; semantic QA pending"
            else:
                class_value = "none"
                notes = "Empty label; negative-image semantic QA pending"

            try:
                source_path = image_path.relative_to(workspace_dir).as_posix()
            except ValueError:
                source_path = image_path.resolve().as_posix()

            rows.append(
                {
                    "image_id": f"{split.upper()}_{image_path.stem}",
                    "source_path": source_path,
                    "session_id": "",
                    "frame_index": frame_index,
                    "capture_timestamp": "",
                    "domain": "UNKNOWN",
                    "split": split,
                    "sha256": sha256_file(image_path),
                    "classes_present": class_value,
                    "occluded": "unknown",
                    "truncated": "unknown",
                    "review_status": "UNREVIEWED",
                    "annotator": "",
                    "qa_reviewer": "",
                    "review_evidence": "",
                    "notes": notes,
                }
            )
    return rows


def write_manifest(
    rows: Iterable[dict[str, object]],
    output_path: Path,
    *,
    force: bool = False,
) -> None:
    if output_path.exists() and not force:
        raise FileExistsError(
            f"Refusing to overwrite existing manifest: {output_path}. "
            "Choose a new --output or pass --force after reviewing the diff."
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-dir", type=Path, default=DATASET_DIR)
    parser.add_argument("--output", type=Path, default=MANIFEST_PATH)
    parser.add_argument(
        "--limit-per-split",
        type=int,
        default=0,
        help="Maximum images per split; default 0 scans all images.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write the manifest. Without this flag the command is read-only.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow replacement of an existing --output; requires --write.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.force and not args.write:
        raise SystemExit("--force requires --write")
    limit = None if args.limit_per_split == 0 else args.limit_per_split
    rows = build_manifest_rows(args.dataset_dir, limit_per_split=limit)
    if args.write and not rows:
        raise SystemExit("Refusing to write an empty manifest; verify --dataset-dir")

    if not args.write:
        print(
            f"DRY-RUN: scanned {len(rows)} images; no file written. "
            f"Requested output would be: {args.output}"
        )
        return 0

    write_manifest(rows, args.output, force=args.force)
    print(f"WROTE: {len(rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
