"""
Manifest exporter for chirality-framework app integrations.

Writes a single index.json manifest that summarizes a run and its
snapshot artifacts with checksums, record counts, and sizes.

Contract highlights:
- Manifest is written atomically and only after all referenced files
  are successfully created.
- Supports per-matrix "format" metadata so consumers can parse files
  appropriately (e.g., "cells-jsonl-v1").
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Tuple


def _sha256_file(path: Path) -> Tuple[str, int, int]:
    """Compute sha256, byte size, and line count for a file.

    Returns (sha256_hex, bytes, records)
    """
    h = hashlib.sha256()
    total_bytes = 0
    line_count = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            if not chunk:
                break
            h.update(chunk)
            total_bytes += len(chunk)
            line_count += chunk.count(b"\n")
    return h.hexdigest(), total_bytes, line_count


@dataclass
class FileMeta:
    path: str
    format: str
    sha256: str
    bytes: int
    records: int


class ManifestExporter:
    """Writes the run manifest (index.json) atomically.

    Usage:
        exporter = ManifestExporter(run_dir, tool_name, tool_version,
                                    framework_schema_version)
        exporter.write_manifest(run_id, problem, durations, matrices)
    """

    def __init__(
        self,
        run_dir: Path,
        tool_name: str,
        tool_version: str,
        framework_schema_version: str = "1.0.0",
    ) -> None:
        self.run_dir = Path(run_dir)
        self.tool_name = tool_name
        self.tool_version = tool_version
        self.framework_schema_version = framework_schema_version

    def build_files_meta(self, files: Dict[str, Tuple[Path, str]]) -> Dict[str, Dict]:
        """Build matrices mapping with sha256/bytes/records.

        Args:
            files: mapping of matrix name -> (absolute file path, format)

        Returns:
            dict suitable for embedding under manifest["matrices"].
        """
        matrices: Dict[str, Dict] = {}
        for key, (path, fmt) in files.items():
            # Compute checksum and counts
            sha, size_bytes, records = _sha256_file(path)
            # Path in manifest should be run-dir relative
            rel_path = os.path.relpath(path, start=self.run_dir)
            matrices[key] = {
                "path": rel_path.replace("\\", "/"),
                "format": fmt,
                "sha256": sha,
                "bytes": size_bytes,
                "records": records,
            }
        return matrices

    def write_manifest(
        self,
        run_id: str,
        problem: Optional[Dict],
        durations: Dict[str, int],
        matrices: Dict[str, Tuple[Path, str]],
    ) -> Path:
        """Write index.json atomically.

        Args:
            run_id: the run identifier
            problem: {"title": str, "statement": str} or None
            durations: e.g., {"total_ms": int}
            matrices: mapping of matrix code -> (file path, format)
        """
        self.run_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = self.run_dir / "index.json"

        created_at = datetime.now(timezone.utc).isoformat()
        manifest = {
            "run_id": run_id,
            "created_at": created_at,
            "tool": {"name": self.tool_name, "version": self.tool_version},
            "framework_schema_version": self.framework_schema_version,
            "problem": problem or {"title": "", "statement": ""},
            "durations": durations,
            "matrices": self.build_files_meta(matrices),
        }

        # Atomic write
        tmp = manifest_path.with_suffix(".json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=None, separators=(",", ":"))
            f.write("\n")
        os.replace(tmp, manifest_path)
        return manifest_path
