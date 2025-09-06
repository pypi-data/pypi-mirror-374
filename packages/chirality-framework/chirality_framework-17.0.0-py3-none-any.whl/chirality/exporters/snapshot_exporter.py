"""
Matrix Snapshot Exporter for Chirality Framework

Safely exports matrix data to JSONL format for verification and analysis.
Uses atomic writes to prevent corruption and maintains consistent run correlation.
"""

import json
import os
import tempfile
from pathlib import Path
from datetime import datetime, timezone

from ..core.types import Matrix


class MatrixSnapshotWriter:
    """
    Safely writes matrix snapshots to JSONL files with atomic operations.

    Each snapshot contains a single JSON object with complete matrix data,
    written atomically to prevent corruption during interruptions.
    """

    def __init__(self, run_id: str, base_path: str = "snapshots"):
        """
        Initialize the snapshot writer.

        Args:
            run_id: Unique identifier for this run (correlates with traces)
            base_path: Base directory for snapshots (default: "snapshots")
        """
        self.run_id = run_id
        self.base_path = Path(base_path)
        self.run_directory = self.base_path / run_id

    def write_matrix(self, matrix: Matrix, resolver_name: str) -> Path:
        """
        Write a matrix snapshot to a JSONL file atomically.

        Args:
            matrix: The Matrix object to snapshot
            resolver_name: Name of the resolver used (e.g., "echo", "openai")

        Returns:
            Path to the written snapshot file
        """
        # Ensure the target directory exists
        self.run_directory.mkdir(parents=True, exist_ok=True)

        # Generate timestamp and filename
        timestamp = datetime.now(timezone.utc)
        timestamp_str = timestamp.strftime("%Y%m%d-%H%M%S")
        filename = f"{matrix.name}-{timestamp_str}.jsonl"
        target_path = self.run_directory / filename

        # Prepare the snapshot data
        snapshot = {
            "matrix_name": matrix.name,
            "station": matrix.station,
            "shape": matrix.shape,
            "row_labels": matrix.row_labels,
            "col_labels": matrix.col_labels,
            "run_id": self.run_id,
            "resolver": resolver_name,
            "timestamp": timestamp.isoformat(),
            "cells": [],
        }

        # Extract cell data
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                cell = matrix.get_cell(i, j)
                if cell:
                    cell_data = {
                        "row": cell.row,
                        "col": cell.col,
                        "value": cell.value,
                        "row_label": matrix.row_labels[i] if i < len(matrix.row_labels) else None,
                        "col_label": matrix.col_labels[j] if j < len(matrix.col_labels) else None,
                        "provenance": {
                            "operation": cell.provenance.get("operation"),
                            "sources": cell.provenance.get("sources", []),
                            "timestamp": cell.provenance.get("timestamp"),
                            "coordinates": cell.provenance.get("coordinates"),
                        },
                    }

                    # Include stage data if present
                    stage_fields = [
                        "stage_1_construct",
                        "stage_2_semantic",
                        "stage_3_column_lensed",
                        "stage_4_row_lensed",
                        "stage_5_final_synthesis",
                    ]

                    for field in stage_fields:
                        if field in cell.provenance:
                            stage_data = cell.provenance[field]
                            # Extract just the text/texts for readability
                            if isinstance(stage_data, dict):
                                if "text" in stage_data:
                                    cell_data["provenance"][field] = stage_data["text"]
                                elif "texts" in stage_data:
                                    cell_data["provenance"][field] = stage_data["texts"]
                                else:
                                    # Include empty stages as-is (for Z matrix compatibility)
                                    cell_data["provenance"][field] = stage_data

                    snapshot["cells"].append(cell_data)

        # Atomic write: write to temp file first, then rename
        # This prevents corruption if the process is interrupted
        with tempfile.NamedTemporaryFile(
            mode="w", dir=self.run_directory, delete=False, suffix=".tmp"
        ) as temp_file:
            json.dump(snapshot, temp_file, ensure_ascii=False)
            temp_file.write("\n")  # Ensure newline at end for JSONL format
            temp_path = temp_file.name

        # Atomically rename temp file to target (atomic on POSIX systems)
        os.replace(temp_path, target_path)

        return target_path

    def get_snapshot_directory(self) -> Path:
        """
        Get the directory where snapshots are being written.

        Returns:
            Path to the snapshot directory for this run
        """
        return self.run_directory

    # --- New: cells-jsonl-v1 writer for app consumption ---
    def write_matrix_cells_jsonl(
        self,
        matrix: Matrix,
        out_dir: Path,
        fixed_filename: str,
    ) -> Path:
        """
        Write per-cell JSONL (one object per line) using the app contract.

        Schema per line:
          {
            "id": "{matrix}:r{row}:c{col}",
            "matrix": "C|D|X|E",
            "row": int,
            "col": int,
            "row_label": str,
            "col_label": str,
            "station": str,
            "text": str,
            "citations": [],
            "refs": [],
            "meta": {"order": int}
          }

        Args:
            matrix: Matrix to serialize
            out_dir: directory to write into (must exist)
            fixed_filename: e.g., "C.jsonl"
        """
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        target_path = out_dir / fixed_filename

        tmp_path = target_path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            # Determine matrix code from filename when available
            try:
                matrix_code = Path(fixed_filename).stem.upper()
            except Exception:
                matrix_code = str(matrix.name).upper()

            def _to_array(v):
                if v is None:
                    return []
                if isinstance(v, list):
                    return v
                if isinstance(v, str):
                    return [v]
                return []

            # Canonical label orders expected by chirality-app importer to derive coordinates
            CANONICAL_ORDERS = {
                "C": {
                    "row": ["Evaluative", "Normative", "Operative"],
                    "col": [
                        "Completeness",
                        "Consistency",
                        "Necessity (vs Contingency)",
                        "Sufficiency",
                    ],
                },
                "D": {
                    "row": ["Evaluative", "Normative", "Operative"],
                    "col": ["Applying", "Guiding", "Judging", "Reviewing"],
                },
                "X": {
                    "row": ["Applying", "Guiding", "Judging", "Reviewing"],
                    "col": [
                        "Completeness",
                        "Consistency",
                        "Necessity (vs Contingency)",
                        "Sufficiency",
                    ],
                },
                "E": {
                    "row": ["Applying", "Guiding", "Judging"],
                    "col": ["Data", "Information", "Knowledge"],
                },
            }

            orders = CANONICAL_ORDERS.get(matrix_code)
            order = 0
            for i in range(matrix.shape[0]):
                for j in range(matrix.shape[1]):
                    cell = matrix.get_cell(i, j)
                    if cell is None:
                        continue
                    row_label = matrix.row_labels[i] if i < len(matrix.row_labels) else ""
                    col_label = matrix.col_labels[j] if j < len(matrix.col_labels) else ""
                    # Default to producer indices
                    row_idx = i
                    col_idx = j
                    # Try to derive canonical coordinates from labels for consumer alignment
                    if orders is not None:
                        try:
                            row_idx = orders["row"].index(row_label)
                        except Exception:
                            row_idx = i
                        try:
                            col_idx = orders["col"].index(col_label)
                        except Exception:
                            col_idx = j
                    citations = (
                        _to_array(cell.provenance.get("citations"))
                        if isinstance(cell.provenance, dict)
                        else []
                    )
                    refs = (
                        _to_array(cell.provenance.get("refs"))
                        if isinstance(cell.provenance, dict)
                        else []
                    )
                    obj = {
                        "id": f"{matrix_code}:r{row_idx}:c{col_idx}",
                        "matrix": matrix_code,
                        "row": row_idx,
                        "col": col_idx,
                        "row_label": row_label,
                        "col_label": col_label,
                        "station": matrix.station,
                        "text": str(cell.value) if cell.value is not None else "",
                        "citations": citations,
                        "refs": refs,
                        "meta": {"order": order},
                    }
                    f.write(json.dumps(obj, ensure_ascii=False, separators=(",", ":")))
                    f.write("\n")
                    order += 1

        os.replace(tmp_path, target_path)
        return target_path
