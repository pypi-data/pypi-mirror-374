"""
Simplified types for Chirality Framework semantic calculator.

Contains only the essential data structures: Cell, Matrix.
All abstractions removed - this is a fixed algorithm, not a flexible framework.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class RichResult:
    """
    Structured result object containing both text output and associated metadata.

    Used by CellResolver methods to return comprehensive information about
    LLM operations, including the resolved text and all metadata needed
    for provenance tracking and Neo4j export.

    Attributes:
        text: The final resolved text from the LLM operation
        terms_used: List of input terms that were processed
        warnings: List of any warnings generated during processing
        metadata: Dict containing resolver metadata (modelId, latencyMs, promptHash, etc.)
    """

    text: str
    terms_used: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]


@dataclass
class Cell:
    """
    Fundamental semantic unit in Chirality Framework semantic calculator.

    Stores the result of the 3-stage interpretation pipeline:
    - Stage 1 (Combinatorial): k-products generated mechanically
    - Stage 2 (Semantic): Word pairs resolved to concepts
    - Stage 3 (Lensing): Ontological interpretation applied

    Attributes:
        row: Row position in matrix
        col: Column position in matrix
        value: Final semantic result after 3-stage pipeline
        provenance: Dict storing all intermediate results from each stage
    """

    row: int
    col: int
    value: str
    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Matrix:
    """
    2D semantic matrix for Chirality Framework semantic calculator.

    Contains cells arranged in a fixed ontological structure where:
    - row_labels define the row ontological axis
    - col_labels define the column ontological axis
    - Each cell represents the semantic intersection of its row/column coordinates

    Attributes:
        name: Matrix identifier (A, B, C, D, F, J)
        station: Valley station where matrix exists
        row_labels: Ontological labels for rows (e.g. ["Normative", "Operative", "Evaluative"])
        col_labels: Ontological labels for columns (e.g. ["Determinacy", "Sufficiency", etc.])
        cells: 2D array of cells [row][col]
    """

    name: str
    station: str
    row_labels: List[str]
    col_labels: List[str]
    cells: List[List[Cell]]

    @property
    def shape(self) -> tuple[int, int]:
        """Get matrix dimensions."""
        return (len(self.row_labels), len(self.col_labels))

    def get_cell(self, row: int, col: int) -> Optional[Cell]:
        """Get cell at specific position."""
        if 0 <= row < len(self.cells) and 0 <= col < len(self.cells[row]):
            return self.cells[row][col]
        return None

    def transpose(self) -> "Matrix":
        """
        Transposes the matrix by swapping rows and columns.

        Returns a new Matrix instance with transposed dimensions, labels, and cells.
        """
        transposed_cells = []

        for j in range(self.shape[1]):
            new_row = []
            for i in range(self.shape[0]):
                original_cell = self.get_cell(i, j)
                if original_cell:
                    new_row.append(
                        Cell(
                            row=j,
                            col=i,
                            value=original_cell.value,
                            provenance=original_cell.provenance,
                        )
                    )
            transposed_cells.append(new_row)

        return Matrix(
            name=f"{self.name}_transposed",
            station=self.station,
            row_labels=self.col_labels,
            col_labels=self.row_labels,
            cells=transposed_cells,
        )
