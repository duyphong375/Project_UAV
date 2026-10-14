from __future__ import annotations

import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.data.generate_image_manifest import (
    build_manifest_rows,
    write_manifest,
)
from scripts.data.validate_ai_evidence import validate_workspace


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


class GenerateImageManifestTests(unittest.TestCase):
    def test_generated_rows_use_real_hash_and_do_not_claim_provenance_or_qa(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            dataset = root / "ai_training" / "dataset_4k_yolo"
            image = dataset / "images" / "train" / "sample.jpg"
            label = dataset / "labels" / "train" / "sample.txt"
            image.parent.mkdir(parents=True)
            label.parent.mkdir(parents=True)
            image.write_bytes(b"test-image")
            label.write_text("1 0.5 0.5 0.2 0.2\n", encoding="utf-8")

            rows = build_manifest_rows(dataset, workspace_dir=root, limit_per_split=10)

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["sha256"], _sha256(image))
            self.assertEqual(rows[0]["classes_present"], "lifebuoy")
            self.assertEqual(rows[0]["session_id"], "")
            self.assertEqual(rows[0]["review_status"], "UNREVIEWED")
            self.assertEqual(rows[0]["qa_reviewer"], "")

    def test_writer_refuses_to_replace_existing_manifest_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "manifest.csv"
            output.write_text("preserve-me", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                write_manifest([], output)

            self.assertEqual(output.read_text(encoding="utf-8"), "preserve-me")


class ValidateAiEvidenceTests(unittest.TestCase):
    session_fields = [
        "session_id",
        "source_path",
        "source",
        "domain",
        "capture_timestamp",
        "operator_or_consent",
        "license_or_url",
        "planned_split",
        "actual_split",
        "frame_sampling",
        "sha256",
        "notes",
    ]
    image_fields = [
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
    calibration_fields = [
        "image_id",
        "relative_image_path",
        "relative_label_path",
        "domain",
        "target_classes",
        "has_hard_negative",
        "session_id",
        "sha256",
        "review_status",
        "notes",
    ]

    def _make_valid_fixture(self, root: Path) -> dict[str, Path]:
        train_image = root / "assets" / "train.jpg"
        train_label = root / "assets" / "train.txt"
        test_asset = root / "assets" / "locked-test.bin"
        review_evidence = root / "evidence" / "train-review.txt"
        for path in (train_image, train_label, test_asset, review_evidence):
            path.parent.mkdir(parents=True, exist_ok=True)
        train_image.write_bytes(b"train-image")
        train_label.write_text("0 0.5 0.5 0.2 0.2\n", encoding="utf-8")
        test_asset.write_bytes(b"locked-test")
        review_evidence.write_text("reviewed by human", encoding="utf-8")

        manifests = root / "ai_training" / "manifests"
        _write_csv(
            manifests / "session_manifest.csv",
            self.session_fields,
            [
                {
                    "session_id": "TRAIN_S001",
                    "source_path": train_image.relative_to(root).as_posix(),
                    "source": "camera",
                    "domain": "real_water",
                    "capture_timestamp": "2026-10-14T00:00:00Z",
                    "operator_or_consent": "CONSENT-001",
                    "license_or_url": "consent:CONSENT-001",
                    "planned_split": "train",
                    "actual_split": "train",
                    "frame_sampling": "single fixture",
                    "sha256": _sha256(train_image),
                    "notes": "fixture",
                },
                {
                    "session_id": "TEST_S001",
                    "source_path": test_asset.relative_to(root).as_posix(),
                    "source": "camera",
                    "domain": "real_water",
                    "capture_timestamp": "2026-10-14T00:00:00Z",
                    "operator_or_consent": "CONSENT-002",
                    "license_or_url": "consent:CONSENT-002",
                    "planned_split": "test",
                    "actual_split": "test",
                    "frame_sampling": "locked fixture",
                    "sha256": _sha256(test_asset),
                    "notes": "fixture",
                },
            ],
        )
        _write_csv(
            manifests / "image_manifest.csv",
            self.image_fields,
            [
                {
                    "image_id": "TRAIN_001",
                    "source_path": train_image.relative_to(root).as_posix(),
                    "session_id": "TRAIN_S001",
                    "frame_index": 0,
                    "capture_timestamp": "2026-10-14T00:00:00Z",
                    "domain": "real_water",
                    "split": "train",
                    "sha256": _sha256(train_image),
                    "classes_present": "person",
                    "occluded": "false",
                    "truncated": "false",
                    "review_status": "QA_PASSED",
                    "annotator": "human-1",
                    "qa_reviewer": "human-2",
                    "review_evidence": review_evidence.relative_to(root).as_posix(),
                    "notes": "fixture",
                }
            ],
        )
        _write_csv(
            manifests / "calibration_manifest.csv",
            self.calibration_fields,
            [
                {
                    "image_id": "CALIB_001",
                    "relative_image_path": train_image.relative_to(root).as_posix(),
                    "relative_label_path": train_label.relative_to(root).as_posix(),
                    "domain": "real_water",
                    "target_classes": "person",
                    "has_hard_negative": "false",
                    "session_id": "TRAIN_S001",
                    "sha256": _sha256(train_image),
                    "review_status": "QA_PASSED",
                    "notes": "fixture",
                }
            ],
        )
        return {"test_asset": test_asset, "image_manifest": manifests / "image_manifest.csv"}

    def test_complete_fixture_passes_read_only_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._make_valid_fixture(root)

            issues = validate_workspace(root, min_calibration_items=1)

            self.assertEqual(issues, [])

    def test_placeholder_hash_and_missing_locked_test_are_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = self._make_valid_fixture(root)
            paths["test_asset"].unlink()
            content = paths["image_manifest"].read_text(encoding="utf-8")
            paths["image_manifest"].write_text(
                content.replace(_sha256(root / "assets" / "train.jpg"), "INDEXED_FROM_DATASET"),
                encoding="utf-8",
            )

            codes = {issue.code for issue in validate_workspace(root, min_calibration_items=1)}

            self.assertIn("IMAGE_HASH", codes)
            self.assertIn("LOCKED_TEST", codes)


if __name__ == "__main__":
    unittest.main()
