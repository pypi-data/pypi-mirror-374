"""
Fixed canonical matrices for Chirality Framework semantic calculator.

These matrices are constants - they represent the fixed ontological structure
of the Chirality Framework. They are not dynamic or configurable.

This embodies the "semantic calculator" philosophy: we have specific,
unchanging inputs that undergo constrained stochastic processing through
a fixed ontological structure with reproducible methodology.
"""

from datetime import datetime, timezone
from .types import Matrix, Cell


def _create_cell(row: int, col: int, value: str) -> Cell:
    """Helper to create a canonical matrix cell with proper provenance."""
    return Cell(
        row=row,
        col=col,
        value=value,
        provenance={
            "operation": "canonical_definition",
            "sources": [],  # No source matrices for canonical definitions
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "coordinates": f"({row}, {col})",
        },
    )


def _create_matrix_cells(content: list[list[str]]) -> list[list[Cell]]:
    """Convert 2D string array to 2D Cell array."""
    return [
        [_create_cell(row, col, content[row][col]) for col in range(len(content[row]))]
        for row in range(len(content))
    ]


# Fixed canonical Matrix A (3x4)
MATRIX_A = Matrix(
    name="A",
    station="Problem Statement",
    row_labels=["normative", "operative", "iterative"],
    col_labels=["guiding", "applying", "judging", "reflecting"],
    cells=_create_matrix_cells(
        [
            ["objectives", "actions", "benchmarks", "feedback"],
            ["standards", "methods", "criteria", "adaptation"],
            ["development", "coordination", "evaluation", "refinement"],
        ]
    ),
)

# Fixed canonical Matrix B (4x4)
MATRIX_B = Matrix(
    name="B",
    station="Problem Statement",
    row_labels=["data", "information", "knowledge", "wisdom"],
    col_labels=["necessity (vs contingency)", "sufficiency", "completeness", "consistency"],
    cells=_create_matrix_cells(
        [
            ["necessary", "sufficient", "complete", "consistent"],
            ["contingent", "actionable", "contextual", "congruent"],
            ["purposeful", "effective", "comprehensive", "coherent"],
            ["constitutive", "optimal", "holistic", "principled"],
        ]
    ),
)

# Fixed canonical Matrix J (3x4) - First 3 rows of Matrix B (truncated without "Wisdom" row)
# J is a proper subset of B, used for verification operations where "Wisdom" level is excluded
# to maintain grounding in observable/verifiable criteria rather than abstract principles
MATRIX_J = Matrix(
    name="J",
    station="Verification",
    row_labels=["data", "information", "knowledge", "wisdom"],
    col_labels=["necessity (vs contingency)", "sufficiency", "completeness", "consistency"],
    cells=_create_matrix_cells(
        [
            ["necessary", "sufficient", "complete", "consistent"],
            ["contingent", "actionable", "contextual", "congruent"],
            ["purposeful", "effective", "comprehensive", "coherent"],
        ]
    ),
)


def get_canonical_matrix(name: str) -> Matrix:
    """
    Get a canonical matrix by name.

    Args:
        name: Matrix name ("A", "B", or "J")

    Returns:
        The canonical matrix

    Raises:
        ValueError: If matrix name is not recognized
    """
    matrices = {"A": MATRIX_A, "B": MATRIX_B, "J": MATRIX_J}

    if name not in matrices:
        raise ValueError(f"Unknown canonical matrix: {name}. Available: A, B, J")

    return matrices[name]


def validate_canonical_matrices():
    """
    Validate that the canonical matrices have the expected structure.

    This is a sanity check to ensure the fixed matrices are properly defined.
    """
    # Validate Matrix A (3x4)
    assert MATRIX_A.shape == (3, 4), f"Matrix A should be 3x4, got {MATRIX_A.shape}"
    assert len(MATRIX_A.row_labels) == 3, "Matrix A should have 3 row labels"
    assert len(MATRIX_A.col_labels) == 4, "Matrix A should have 4 column labels"

    # Validate Matrix B (4x4)
    assert MATRIX_B.shape == (4, 4), f"Matrix B should be 4x4, got {MATRIX_B.shape}"
    assert len(MATRIX_B.row_labels) == 4, "Matrix B should have 4 row labels"
    assert len(MATRIX_B.col_labels) == 4, "Matrix B should have 4 column labels"

    # Validate Matrix J (3x4) - truncated B
    assert MATRIX_J.shape == (3, 4), f"Matrix J should be 3x4, got {MATRIX_J.shape}"
    assert len(MATRIX_J.row_labels) == 3, "Matrix J should have 3 row labels"
    assert len(MATRIX_J.col_labels) == 4, "Matrix J should have 4 column labels"

    # Ensure J is properly truncated B (first 3 rows with same values)
    # This validates that J is a true subset of B, not a different matrix
    for i in range(3):
        for j in range(4):
            assert MATRIX_B.cells[i][j].value == MATRIX_J.cells[i][j].value, (
                f"Matrix J cell [{i}][{j}] should match Matrix B cell [{i}][{j}]: "
                f"B='{MATRIX_B.cells[i][j].value}' vs J='{MATRIX_J.cells[i][j].value}'"
            )


if __name__ == "__main__":
    # Run validation if script is executed directly
    validate_canonical_matrices()
    print("✓ All canonical matrices validated successfully")
    print(f"✓ Matrix A: {MATRIX_A.shape} - {MATRIX_A.station}")
    print(f"✓ Matrix B: {MATRIX_B.shape} - {MATRIX_B.station}")
    print(f"✓ Matrix J: {MATRIX_J.shape} - {MATRIX_J.station}")
