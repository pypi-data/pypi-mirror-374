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
from typing import Optional

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
            "cells": []
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
                            "coordinates": cell.provenance.get("coordinates")
                        }
                    }
                    
                    # Include stage data if present
                    stage_fields = [
                        "stage_1_construct",
                        "stage_2_semantic", 
                        "stage_3_column_lensed",
                        "stage_4_row_lensed",
                        "stage_5_final_synthesis"
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
            mode='w',
            dir=self.run_directory,
            delete=False,
            suffix='.tmp'
        ) as temp_file:
            json.dump(snapshot, temp_file, ensure_ascii=False)
            temp_file.write('\n')  # Ensure newline at end for JSONL format
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