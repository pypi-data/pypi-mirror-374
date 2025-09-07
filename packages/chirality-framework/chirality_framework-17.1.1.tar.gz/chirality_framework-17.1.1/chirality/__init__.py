"""
Chirality Framework - A Semantic Calculator

This package provides a direct implementation of the Chirality Framework, a fixed,
canonical algorithm for structured problem-solving. It functions as a "semantic
calculator" that executes a specific sequence of semantic and structural matrix
operations to traverse a "semantic valley" from problem to evaluation.

The primary user interface is the command-line tool, which provides orchestration
for computing the entire pipeline and visualizing the results.
"""

# Read version from VERSION.md (single source of truth)
from pathlib import Path

try:
    version_path = Path(__file__).parent.parent / "VERSION.md"
    with open(version_path, "r") as f:
        __version__ = f.readline().split("—")[0].strip()
except Exception:
    __version__ = "0.0.0"  # Fallback version
__author__ = "Chirality Framework Team"

from .core.types import Cell, Matrix
from .core.cell_resolver import CellResolver
from .core.resolvers import EchoResolver
from .core.operations import (
    compute_cell_C,
    compute_cell_F,
    compute_cell_D,
    compute_cell_X,
    compute_cell_Z,
    compute_cell_E,
    compute_matrix_C,
    compute_matrix_F,
    compute_matrix_D,
    compute_matrix_K,
    compute_matrix_X,
    compute_matrix_Z,
    compute_matrix_T_from_B,
    compute_matrix_G,
    compute_array_P,
    compute_matrix_E,
)
from .core.matrices import MATRIX_A, MATRIX_B, MATRIX_J
from .core.validate import FrameworkValidationError, validate_matrix, validate_cell
from .core.tracer import JSONLTracer

__all__ = [
    # Core types
    "Cell",
    "Matrix",
    # Canonical matrices
    "MATRIX_A",
    "MATRIX_B",
    "MATRIX_J",
    # Resolvers
    "CellResolver",
    "EchoResolver",
    # Cell-level operations
    "compute_cell_C",
    "compute_cell_F",
    "compute_cell_D",
    "compute_cell_X",
    "compute_cell_Z",
    "compute_cell_E",
    # Matrix-level operations
    "compute_matrix_C",
    "compute_matrix_F",
    "compute_matrix_D",
    "compute_matrix_K",
    "compute_matrix_X",
    "compute_matrix_Z",
    "compute_matrix_T_from_B",
    "compute_matrix_G",
    "compute_array_P",
    "compute_matrix_E",
    # Validation
    "FrameworkValidationError",
    "validate_matrix",
    "validate_cell",
    # Tracing
    "JSONLTracer",
]
