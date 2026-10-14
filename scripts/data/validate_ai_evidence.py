"""Read-only validation for KVC AI provenance, QA, test and calibration evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


WORKSPACE_DIR = Path(__file__).resolve().parents[2]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EVIDENCE_PREFIXES = ("http://", "https://", "spdx:", "consent:", "internal-record:")


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    row: int | None
    message: str

    def format(self) -> str:
        location = f"{self.path}:{self.row}" if self.row is not None else self.path
        return f"{self.code} | {location} | {self.message}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_csv(path: Path, *, allow_comments: bool = False) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        lines: Iterable[str] = stream
        if allow_comments:
            lines = (line for line in stream if not line.lstrip().startswith("#"))
        reader = csv.DictReader(lines)
        return list(reader.fieldnames or []), list(reader)


def _resolve_existing(root: Path, value: str) -> Path | None:
    raw = Path(value)
    candidates = [raw] if raw.is_absolute() else [root / raw, root / "ai_training" / raw]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _missing_columns(fieldnames: list[str], required: set[str]) -> set[str]:
    return required.difference(fieldnames)


def _issue(code: str, path: Path, row: int | None, message: str) -> Issue:
    return Issue(code, path.as_posix(), row, message)


def validate_session_manifest(root: Path, path: Path) -> tuple[list[Issue], set[str]]:
    issues: list[Issue] = []
    fieldnames, rows = _read_csv(path)
    required = {
        "session_id",
        "source_path",
        "license_or_url",
        "actual_split",
        "sha256",
    }
    missing = _missing_columns(fieldnames, required)
    if missing:
        issues.append(_issue("SESSION_SCHEMA", path, None, f"missing columns: {sorted(missing)}"))
        return issues, set()

    seen: set[str] = set()
    valid_sessions: set[str] = set()
    test_sessions = 0
    for index, row in enumerate(rows, start=2):
        session_id = row["session_id"].strip()
        if not session_id or session_id in seen:
            issues.append(_issue("SESSION_ID", path, index, "session_id is empty or duplicated"))
        else:
            seen.add(session_id)

        license_value = row["license_or_url"].strip().lower()
        if not license_value.startswith(EVIDENCE_PREFIXES):
            issues.append(
                _issue(
                    "LICENSE_EVIDENCE",
                    path,
                    index,
                    "license/consent must reference a URL, SPDX id or evidence record",
                )
            )

        source = _resolve_existing(root, row["source_path"].strip())
        if source is None:
            issues.append(_issue("SESSION_SOURCE_MISSING", path, index, "source_path does not exist"))
        elif source.is_dir():
            issues.append(
                _issue(
                    "SESSION_DIRECTORY_HASH",
                    path,
                    index,
                    "directory source needs a versioned file-list manifest; one sha256 is not verifiable",
                )
            )
        else:
            expected = row["sha256"].strip().lower()
            if not SHA256_RE.fullmatch(expected) or sha256_file(source) != expected:
                issues.append(_issue("SESSION_HASH", path, index, "sha256 is missing or does not match source"))

        if row["actual_split"].strip().lower() == "test":
            test_sessions += 1
            if source is None or not source.is_file():
                issues.append(_issue("LOCKED_TEST", path, index, "test asset is not an existing hashed file"))

        if not any(issue.row == index for issue in issues):
            valid_sessions.add(session_id)

    if test_sessions == 0:
        issues.append(_issue("LOCKED_TEST", path, None, "no actual_split=test session is declared"))
    return issues, valid_sessions


def validate_image_manifest(root: Path, path: Path, known_sessions: set[str]) -> list[Issue]:
    issues: list[Issue] = []
    fieldnames, rows = _read_csv(path)
    required = {
        "image_id",
        "source_path",
        "session_id",
        "sha256",
        "review_status",
        "review_evidence",
    }
    missing = _missing_columns(fieldnames, required)
    if missing:
        issues.append(_issue("IMAGE_SCHEMA", path, None, f"missing columns: {sorted(missing)}"))

    seen: set[str] = set()
    for index, row in enumerate(rows, start=2):
        image_id = row.get("image_id", "").strip()
        if not image_id or image_id in seen:
            issues.append(_issue("IMAGE_ID", path, index, "image_id is empty or duplicated"))
        seen.add(image_id)

        source = _resolve_existing(root, row.get("source_path", "").strip())
        expected = row.get("sha256", "").strip().lower()
        if source is None or not source.is_file():
            issues.append(_issue("IMAGE_SOURCE_MISSING", path, index, "source_path does not exist"))
        elif not SHA256_RE.fullmatch(expected) or sha256_file(source) != expected:
            issues.append(_issue("IMAGE_HASH", path, index, "sha256 is missing, placeholder or mismatched"))

        session_id = row.get("session_id", "").strip()
        if not session_id or session_id not in known_sessions:
            issues.append(_issue("IMAGE_SESSION", path, index, "session_id lacks valid session evidence"))

        status = row.get("review_status", "").strip().upper()
        review_evidence = row.get("review_evidence", "").strip()
        if status not in {"QA_PASSED", "QA_NEGATIVE_VERIFIED"}:
            issues.append(_issue("IMAGE_QA", path, index, "semantic QA is not complete"))
        elif not review_evidence or _resolve_existing(root, review_evidence) is None:
            issues.append(_issue("IMAGE_QA_EVIDENCE", path, index, "QA status lacks an evidence file"))
    return issues


def validate_calibration_manifest(
    root: Path,
    path: Path,
    *,
    min_items: int = 100,
) -> list[Issue]:
    issues: list[Issue] = []
    fieldnames, rows = _read_csv(path, allow_comments=True)
    required = {
        "image_id",
        "relative_image_path",
        "relative_label_path",
        "session_id",
        "sha256",
        "review_status",
    }
    missing = _missing_columns(fieldnames, required)
    if missing:
        issues.append(_issue("CALIBRATION_SCHEMA", path, None, f"missing columns: {sorted(missing)}"))
    if len(rows) < min_items:
        issues.append(_issue("CALIBRATION_SIZE", path, None, f"has {len(rows)} rows; requires at least {min_items}"))

    for index, row in enumerate(rows, start=2):
        raw_image_path = row.get("relative_image_path", "").strip()
        image = _resolve_existing(root, raw_image_path)
        label = _resolve_existing(root, row.get("relative_label_path", "").strip())
        if image is None or not image.is_file():
            issues.append(_issue("CALIBRATION_IMAGE", path, index, "image path does not exist"))
        else:
            expected = row.get("sha256", "").strip().lower()
            if not SHA256_RE.fullmatch(expected) or sha256_file(image) != expected:
                issues.append(_issue("CALIBRATION_HASH", path, index, "sha256 does not match image"))
        if label is None or not label.is_file():
            issues.append(_issue("CALIBRATION_LABEL", path, index, "label path does not exist"))
        if "/val/" in raw_image_path.replace("\\", "/"):
            issues.append(_issue("CALIBRATION_USES_VAL", path, index, "validation image is used for calibration"))
        if not row.get("session_id", "").strip():
            issues.append(_issue("CALIBRATION_SESSION", path, index, "session_id is missing"))
        if row.get("review_status", "").strip().upper() not in {
            "QA_PASSED",
            "QA_NEGATIVE_VERIFIED",
        }:
            issues.append(_issue("CALIBRATION_QA", path, index, "semantic QA is not complete"))
    return issues


def validate_workspace(root: Path, *, min_calibration_items: int = 100) -> list[Issue]:
    manifests = root / "ai_training" / "manifests"
    session_path = manifests / "session_manifest.csv"
    image_path = manifests / "image_manifest.csv"
    calibration_path = manifests / "calibration_manifest.csv"
    issues: list[Issue] = []

    for path in (session_path, image_path, calibration_path):
        if not path.is_file():
            issues.append(_issue("MANIFEST_MISSING", path, None, "required manifest does not exist"))
    if issues:
        return issues

    session_issues, valid_sessions = validate_session_manifest(root, session_path)
    issues.extend(session_issues)
    issues.extend(validate_image_manifest(root, image_path, valid_sessions))
    issues.extend(
        validate_calibration_manifest(root, calibration_path, min_items=min_calibration_items)
    )
    return issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=WORKSPACE_DIR)
    parser.add_argument("--min-calibration-items", type=int, default=100)
    parser.add_argument("--max-issues", type=int, default=50)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    issues = validate_workspace(args.root.resolve(), min_calibration_items=args.min_calibration_items)
    if not issues:
        print("AI_EVIDENCE_READY: all configured evidence checks passed")
        return 0

    for issue in issues[: args.max_issues]:
        print(issue.format())
    counts = Counter(issue.code for issue in issues)
    print(f"AI_EVIDENCE_BLOCKED: {len(issues)} issue(s); by code={dict(sorted(counts.items()))}")
    if len(issues) > args.max_issues:
        print(f"Output limited to first {args.max_issues} issue(s)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
