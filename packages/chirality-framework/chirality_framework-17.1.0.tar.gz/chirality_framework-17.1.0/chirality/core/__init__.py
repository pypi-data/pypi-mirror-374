"""
Core Chirality Framework semantic calculator modules.
"""

from .types import Cell, Matrix
from .cell_resolver import CellResolver
from .resolvers import EchoResolver
from .operations import (
    compute_cell_C,
    compute_cell_F,
    compute_cell_D,
    compute_matrix_C,
    compute_matrix_F,
    compute_matrix_D,
)
from .matrices import MATRIX_A, MATRIX_B, MATRIX_J
from .validate import FrameworkValidationError
from .tracer import JSONLTracer

__all__ = [
    # Core types
    "Cell",
    "Matrix",
    # Resolvers
    "CellResolver",
    "EchoResolver",
    # Operations (cell-level)
    "compute_cell_C",
    "compute_cell_F",
    "compute_cell_D",
    # Operations (matrix-level)
    "compute_matrix_C",
    "compute_matrix_F",
    "compute_matrix_D",
    # Canonical matrices
    "MATRIX_A",
    "MATRIX_B",
    "MATRIX_J",
    # Validation
    "FrameworkValidationError",
    # Tracing
    "JSONLTracer",
]
