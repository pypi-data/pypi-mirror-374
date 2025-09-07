"""
Three-Stage Cell Pipeline Implementation for Chirality Framework v16.0.0

This is the "secret sauce" - the core algorithm that transforms
structural combinations into meaningful semantic insights through
a precise 3-stage interpretation process:

Stage 1 (Combinatorial): Mechanical generation of k-products
Stage 2 (Semantic): LLM resolution of word pairs into concepts
Stage 3 (Lensing): Ontological interpretation through row/column coordinates

This embodies the "semantic calculator" philosophy: procedurally rigorous
methodology with fixed ontological structure that produces meaningful outputs
through constrained stochastic processing of canonical inputs.
"""

from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
from .types import Cell, Matrix
from .cell_resolver import CellResolver
from .tracer import JSONLTracer
from .provenance_schema import create_provenance
from .constants import CANONICAL_PROBLEM
from ..exporters.working_memory_exporter import Neo4jWorkingMemoryExporter


@dataclass
class SimpleResult:
    """Simple result object for tracer compatibility."""

    text: str
    terms_used: List[str]
    warnings: List[str]


## NOTE: Combined lensing replaces legacy 3-step approach. Canonical pipeline uses a single
## combined lensing call via CellResolver.run_combined_lens.


def compute_cell_C(
    i: int,
    j: int,
    A: Matrix,
    B: Matrix,
    resolver: CellResolver,
    valley_summary: str = None,
    tracer: Optional[JSONLTracer] = None,
    exporter: Optional["Neo4jWorkingMemoryExporter"] = None,
) -> Cell:
    """
    Canonical 2-stage pipeline for computing C[i,j] = A[i,:] dot B[:,j]

    Uses new combined lensing approach with maintainer-authored prompt assets.

    Stage 1 (Combinatorial): Generate k-products mechanically (no LLM)
    Stage 2 (Semantic): Resolve k-products via multiplication (LLM)
    Stage 3 (Combined Lensing): Apply unified row × col × station lens (LLM)

    Args:
        i: Row index in result matrix C
        j: Column index in result matrix C
        A: Left input matrix (3x4)
        B: Right input matrix (4x4)
        resolver: CellResolver for LLM operations
        valley_summary: Legacy parameter (ignored)

    Returns:
        Cell with final semantic result and complete provenance
    """

    # Stage 1: Combinatorial (mechanical, no LLM)
    raw_products = []
    for k in range(A.shape[1]):  # A is 3x4, so k goes 0-3
        a_cell = A.get_cell(i, k)
        b_cell = B.get_cell(k, j)
        product_pair = f"{a_cell.value} * {b_cell.value}"
        raw_products.append(product_pair)

    # Stage 2: Semantic Resolution using new resolver
    stage2_result = resolver.run_stage2_multiply(raw_products, "C")

    # Stage 3: Combined Lensing using new resolver
    final_result = resolver.run_combined_lens(
        content=stage2_result.text,
        component_id="C",
        row_label=A.row_labels[i],
        col_label=B.col_labels[j],
    )

    # Build cell with new provenance structure
    cell = Cell(
        row=i,
        col=j,
        value=final_result.text,
        provenance=create_provenance(
            operation="compute_C",
            coordinates=f"({A.row_labels[i]}, {B.col_labels[j]})",
            stage_data={
                "stage_1_construct": {
                    "texts": raw_products,
                    "metadata": {},
                    "terms_used": [f"k={k}" for k in range(len(raw_products))],
                    "warnings": [],
                },
                "stage_2_semantic": {
                    "text": stage2_result.text,
                    "metadata": stage2_result.metadata,
                    "terms_used": stage2_result.terms_used,
                    "warnings": stage2_result.warnings,
                },
                "stage_3_combined_lensed": {
                    "text": final_result.text,
                    "metadata": final_result.metadata,
                    "terms_used": final_result.terms_used,
                    "warnings": final_result.warnings,
                },
            },
            sources=["A", "B"],
            traced=tracer is not None,
        ),
    )

    # Legacy tracer support (simplified)
    if tracer:
        # Create minimal context for compatibility
        context = SimpleResult(
            text=final_result.text,
            terms_used=final_result.terms_used,
            warnings=final_result.warnings,
        )
        tracer.trace_stage(
            "compute_C_complete", context, context, {"component": "C", "coordinates": f"({i},{j})"}
        )

    return cell


def compute_cell_F(
    i: int,
    j: int,
    J: Matrix,
    C: Matrix,
    resolver: CellResolver,
    valley_summary: str,
    tracer: Optional[JSONLTracer] = None,
    exporter: Optional["Neo4jWorkingMemoryExporter"] = None,
) -> Cell:
    """
    Element-wise operation F[i,j] = J[i,j] ⊙ C[i,j] with lensing

    Since coordinates match, skip combinatorial stage.
    Stage 1: Direct semantic multiplication
    Stage 2: Apply ontological lens for objectives context

    Args:
        i: Row index
        j: Column index
        J: Judgment matrix (3x4)
        C: Composition matrix (3x4)
        resolver: CellResolver for LLM operations
        valley_summary: Current position in semantic valley

    Returns:
        Cell with element-wise multiplication result
    """

    # Stage 1: Direct element-wise multiplication (same coordinates)
    j_cell = J.get_cell(i, j)
    c_cell = C.get_cell(i, j)
    element_pair = f"{j_cell.value} * {c_cell.value}"
    # Stage 2 (LLM): element-wise semantic operation
    stage2_result = resolver.run_stage2_elementwise([j_cell.value, c_cell.value], "F")
    # Stage 3: Combined lensing (Objectives)
    final_result = resolver.run_combined_lens(
        content=stage2_result.text,
        component_id="F",
        row_label=J.row_labels[i],
        col_label=J.col_labels[j],
    )

    cell = Cell(
        row=i,
        col=j,
        value=final_result.text,
        provenance=create_provenance(
            operation="compute_F",
            coordinates=f"({J.row_labels[i]}, {J.col_labels[j]})",
            stage_data={
                "stage_1_construct": {
                    "text": element_pair,
                    "metadata": {},
                    "terms_used": element_pair.split(" * "),
                    "warnings": [],
                },
                "stage_2_semantic": {
                    "text": stage2_result.text,
                    "metadata": stage2_result.metadata,
                    "terms_used": stage2_result.terms_used,
                    "warnings": stage2_result.warnings,
                },
                "stage_3_combined_lensed": {
                    "text": final_result.text,
                    "metadata": final_result.metadata,
                    "terms_used": final_result.terms_used,
                    "warnings": final_result.warnings,
                },
            },
            sources=["J", "C"],
            traced=tracer is not None,
        ),
    )

    # Export to Neo4j if exporter is provided
    # TODO: Fix context object
    # if exporter:
    #     exporter.export_cell_computation(cell, context)

    return cell


def compute_cell_D(
    i: int,
    j: int,
    A: Matrix,
    F: Matrix,
    resolver: CellResolver,
    valley_summary: str,
    tracer: Optional[JSONLTracer] = None,
    exporter: Optional["Neo4jWorkingMemoryExporter"] = None,
) -> Cell:
    """
    Compute D[i,j] using the canonical D formula with fixed problem statement.
    D[i,j] = A[i,j] + "applied to frame the problem;" + F[i,j] + " to resolve the problem."

    Stage 1: Apply canonical synthesis formula mechanically
    Stage 2: Combined ontological lensing (same as C and F)

    Args:
        i: Row index
        j: Column index
        A: Axioms matrix (3x4)
        F: Functions matrix (3x4)
        resolver: CellResolver for LLM operations
        valley_summary: Current position in semantic valley

    Returns:
        Cell with synthesized solution objective
    """

    # Stage 1: Apply the canonical synthesis formula (Path B - hard-coded)
    # D(i,j) = A(i,j) + " applied to frame the problem; " + F(i,j) + " to resolve the problem."
    a_cell = A.get_cell(i, j)
    f_cell = F.get_cell(i, j)
    synthesis_statement = (
        f"{a_cell.value} applied to frame the problem; {f_cell.value} to resolve the problem."
    )

    # Trace Stage 1 (mechanical synthesis)
    if tracer:
        stage1_context = {
            "station_context": "Solution Objectives",
            "valley_summary": valley_summary,
            "row_label": A.row_labels[i],
            "col_label": A.col_labels[j],
            "operation_type": "synthesis",
            "terms": {"formula": synthesis_statement},
            "matrix": "D",
            "i": i,
            "j": j,
        }
        tracer.trace_stage(
            "mechanical_synthesis",
            stage1_context,
            SimpleResult(
                text=synthesis_statement, terms_used=[a_cell.value, f_cell.value], warnings=[]
            ),
            {
                "station": "Solution Objectives",
                "valley_summary": valley_summary,
                "products": [synthesis_statement],
            },
        )

    # Stage 2: Combined lensing (Objectives)
    final_result = resolver.run_combined_lens(
        content=synthesis_statement,
        component_id="D",
        row_label=A.row_labels[i],
        col_label=A.col_labels[j],
    )

    cell = Cell(
        row=i,
        col=j,
        value=final_result.text,
        provenance=create_provenance(
            operation="compute_D",
            coordinates=f"({A.row_labels[i]}, {A.col_labels[j]})",
            stage_data={
                "stage_1_construct": {
                    "text": f"A[{i},{j}] + F[{i},{j}]",
                    "metadata": {},
                    "terms_used": [a_cell.value, f_cell.value],
                    "warnings": [],
                },
                "stage_2_semantic": {
                    "text": synthesis_statement,
                    "metadata": {},
                    "terms_used": [a_cell.value, f_cell.value],
                    "warnings": [],
                },
                "stage_3_combined_lensed": {
                    "text": final_result.text,
                    "metadata": final_result.metadata,
                    "terms_used": final_result.terms_used,
                    "warnings": final_result.warnings,
                },
            },
            sources=["A", "F"],
            traced=tracer is not None,
            problem=CANONICAL_PROBLEM,
        ),
    )

    # Export to Neo4j if exporter is provided
    # TODO: Fix context object
    # if exporter:
    #     exporter.export_cell_computation(cell, context)

    return cell


def compute_matrix_C(
    A: Matrix,
    B: Matrix,
    resolver: CellResolver,
    valley_summary: str,
    tracer: Optional[JSONLTracer] = None,
    exporter: Optional["Neo4jWorkingMemoryExporter"] = None,
) -> Matrix:
    """
    Convenience wrapper - loops over compute_cell_C. NO semantic logic here.

    Simple iteration over the 3x4 result matrix, calling compute_cell_C for each position.
    This follows the "semantic calculator" principle: matrix operations are just
    organized collections of cell operations.
    """
    cells = []
    for i in range(3):  # A is 3x4
        row_cells = []
        for j in range(4):  # B is 4x4, so result is 3x4
            cell = compute_cell_C(i, j, A, B, resolver, valley_summary, tracer, exporter)
            row_cells.append(cell)
        cells.append(row_cells)

    return Matrix(
        name="C",
        station="Problem Requirements",
        row_labels=A.row_labels,
        col_labels=B.col_labels,
        cells=cells,
    )


def compute_matrix_F(
    J: Matrix,
    C: Matrix,
    resolver: CellResolver,
    valley_summary: str,
    tracer: Optional[JSONLTracer] = None,
    exporter: Optional["Neo4jWorkingMemoryExporter"] = None,
) -> Matrix:
    """Convenience wrapper - loops over compute_cell_F"""
    cells = []
    for i in range(3):  # Both J and C are 3x4
        row_cells = []
        for j in range(4):
            cell = compute_cell_F(i, j, J, C, resolver, valley_summary, tracer, exporter)
            row_cells.append(cell)
        cells.append(row_cells)

    return Matrix(
        name="F",
        station="Solution Objectives",
        row_labels=J.row_labels,
        col_labels=J.col_labels,
        cells=cells,
    )


def compute_matrix_D(
    A: Matrix,
    F: Matrix,
    resolver: CellResolver,
    valley_summary: str,
    tracer: Optional[JSONLTracer] = None,
    exporter: Optional[Neo4jWorkingMemoryExporter] = None,
) -> Matrix:
    """Convenience wrapper - loops over compute_cell_D with canonical problem"""
    cells = []
    for i in range(3):
        row_cells = []
        for j in range(4):
            cell = compute_cell_D(i, j, A, F, resolver, valley_summary, tracer, exporter)
            row_cells.append(cell)
        cells.append(row_cells)

    return Matrix(
        name="D",
        station="Solution Objectives",
        row_labels=A.row_labels,  # D uses A's row labels
        col_labels=A.col_labels,  # D uses A's col labels
        cells=cells,
    )


def compute_matrix_K(D: Matrix) -> Matrix:
    """
    Generate Matrix K as the transpose of Matrix D.

    K transforms the Solution Objectives (D) into a form suitable for Verification.
    The transposition swaps the perspective from row-dominant to column-dominant,
    preparing for verification against the truncated decision criteria (J).

    Args:
        D: Matrix D (Solution Objectives) of size 3x4

    Returns:
        Matrix K of size 4x3 (transposed D)
    """
    K = D.transpose()
    K.name = "K"
    K.station = "Pre-Verification Transform"
    return K


def compute_cell_X(
    i: int,
    j: int,
    K: Matrix,
    J: Matrix,
    resolver: CellResolver,
    valley_summary: str,
    tracer: Optional[JSONLTracer] = None,
    exporter: Optional["Neo4jWorkingMemoryExporter"] = None,
) -> Cell:
    """
    Complete 3-stage pipeline for computing X[i,j] = K[i,:] dot J[:,j]

    X represents the Verification matrix, where Solution Objectives (transposed as K)
    are verified against decision criteria (J).

    Stage 1 (Combinatorial): Generate k-products mechanically (no LLM)
    Stage 2 (Semantic): Resolve word pairs into concepts (LLM)
    Stage 3 (Lensing): Apply ontological interpretation (LLM with deep context)

    Args:
        i: Row index in result matrix X
        j: Column index in result matrix X
        K: Matrix K (transposed D) of size 4x3
        J: Matrix J (truncated B) of size 3x4
        resolver: CellResolver for LLM operations
        valley_summary: Current position in semantic valley

    Returns:
        Cell with final semantic result and complete provenance
    """

    # Stage 1: Combinatorial (mechanical, no LLM)
    raw_products = []
    for k in range(K.shape[1]):  # K is 4x3, so k goes 0-2
        k_cell = K.get_cell(i, k)
        j_cell = J.get_cell(k, j)
        product_pair = f"{k_cell.value} * {j_cell.value}"
        raw_products.append(product_pair)

    # Trace Stage 1 (combinatorial - no LLM call, just mechanical result)
    if tracer:
        stage1_context = {
            "station_context": "Verification",
            "valley_summary": valley_summary,
            "row_label": K.row_labels[i],
            "col_label": J.col_labels[j],
            "operation_type": "combinatorial",
            "terms": {"products": raw_products},
            "matrix": "X",
            "i": i,
            "j": j,
        }
        tracer.trace_stage(
            "product:combinatorial",
            stage1_context,
            SimpleResult(
                text=", ".join(raw_products),
                terms_used=[f"k={k}" for k in range(len(raw_products))],
                warnings=[],
            ),
            {
                "station": "Verification",
                "valley_summary": valley_summary,
                "products": raw_products,
            },
        )

    # Stage 2: Semantic resolution (LLM) and Stage 3: Combined lensing
    stage2_result = resolver.run_stage2_multiply(raw_products, "X")
    final_result = resolver.run_combined_lens(
        content=stage2_result.text,
        component_id="X",
        row_label=K.row_labels[i],
        col_label=J.col_labels[j],
    )

    # Create final cell
    cell = Cell(
        row=i,
        col=j,
        value=final_result.text,
        provenance=create_provenance(
            operation="compute_X",
            coordinates=f"({K.row_labels[i]}, {J.col_labels[j]})",
            stage_data={
                "stage_1_construct": {
                    "texts": raw_products,
                    "metadata": {},
                    "terms_used": [f"k={k}" for k in range(len(raw_products))],
                    "warnings": [],
                },
                "stage_2_semantic": {
                    "text": stage2_result.text,
                    "metadata": stage2_result.metadata,
                    "terms_used": stage2_result.terms_used,
                    "warnings": stage2_result.warnings,
                },
                "stage_3_combined_lensed": {
                    "text": final_result.text,
                    "metadata": final_result.metadata,
                    "terms_used": final_result.terms_used,
                    "warnings": final_result.warnings,
                },
            },
            sources=["K", "J"],
            traced=tracer is not None,
        ),
    )

    # TODO: Fix context object for exporter
    # if exporter:
    #     exporter.export_cell_computation(cell, context)

    return cell


def compute_matrix_X(
    K: Matrix,
    J: Matrix,
    resolver: CellResolver,
    valley_summary: str,
    tracer: Optional[JSONLTracer] = None,
    exporter: Optional["Neo4jWorkingMemoryExporter"] = None,
) -> Matrix:
    """
    Convenience wrapper - loops over compute_cell_X.

    Generates the Verification matrix X by applying K * J.

    Args:
        K: Matrix K (transposed D) of size 4x3
        J: Matrix J (truncated B) of size 3x4
        resolver: CellResolver for semantic operations
        valley_summary: Current semantic valley position

    Returns:
        Matrix X of size 4x4
    """
    cells = []
    # K is 4x3, J is 3x4, so result X is 4x4
    for i in range(K.shape[0]):
        row_cells = []
        for j in range(J.shape[1]):
            cell = compute_cell_X(i, j, K, J, resolver, valley_summary, tracer, exporter)
            row_cells.append(cell)
        cells.append(row_cells)

    return Matrix(
        name="X",
        station="Verification",
        row_labels=K.row_labels,
        col_labels=J.col_labels,
        cells=cells,
    )


def compute_cell_Z(
    i: int,
    j: int,
    X: Matrix,
    resolver: CellResolver,
    valley_summary: str,
    tracer: Optional[JSONLTracer] = None,
    exporter: Optional["Neo4jWorkingMemoryExporter"] = None,
) -> Cell:
    """
    Lean 2-stage pipeline for computing Z[i,j] via station context shift.

    Z represents the Validation matrix, where Verification results (X)
    are transformed into validation context through station shift operation.

    Stage 1 (Construct): Direct extraction of verification content (no LLM)
    Stage 2 (Semantic): Station shift from Verification to Validation (LLM)

    Args:
        i: Row index in result matrix Z
        j: Column index in result matrix Z
        X: Matrix X (Verification) of size 4x4
        resolver: CellResolver for LLM operations
        valley_summary: Current position in semantic valley

    Returns:
        Cell with validation result and lean 2-stage provenance
    """

    # Stage 1: Construct (direct extraction, no LLM)
    x_cell = X.get_cell(i, j)
    verification_content = x_cell.value

    # Trace Stage 1
    if tracer:
        stage1_context = {
            "station_context": "Validation",
            "valley_summary": valley_summary,
            "row_label": X.row_labels[i],
            "col_label": X.col_labels[j],
            "operation_type": "construct",
            "terms": {"verification_content": verification_content},
            "matrix": "Z",
            "i": i,
            "j": j,
        }
        tracer.trace_stage(
            "construct:direct_extract",
            stage1_context,
            SimpleResult(
                text=verification_content,
                terms_used=[verification_content],
                warnings=[],
            ),
            {
                "station": "Validation",
                "valley_summary": valley_summary,
                "source_matrix": "X",
            },
        )

    # Stage 2: Station shift from Verification to Validation context
    validation_result = resolver.run_shift(content=verification_content, component_id="Z")

    # Trace Stage 2
    if tracer:
        # Create minimal context for tracing
        context = {"operation": "station_shift", "stage": "semantic"}
        tracer.trace_stage(
            "semantic:station_shift",
            context,
            SimpleResult(
                text=validation_result.text,
                terms_used=validation_result.terms_used,
                warnings=validation_result.warnings,
            ),
            {
                "station": "Validation",
                "valley_summary": valley_summary,
                "source_content": verification_content,
            },
        )

    # Create final cell provenance using combined lensing stage
    cell = Cell(
        row=i,
        col=j,
        value=validation_result.text,
        provenance=create_provenance(
            operation="compute_Z",
            coordinates=f"({X.row_labels[i]}, {X.col_labels[j]})",
            stage_data={
                "stage_1_construct": {
                    "text": verification_content,
                    "metadata": {},
                    "terms_used": [verification_content],
                    "warnings": [],
                },
                "stage_2_semantic": {
                    "text": validation_result.text,
                    "metadata": validation_result.metadata,
                    "terms_used": validation_result.terms_used,
                    "warnings": validation_result.warnings,
                },
                "stage_3_combined_lensed": {},  # Empty for lean 2-stage Z pipeline
            },
            sources=["X"],
            traced=tracer is not None,
        ),
    )

    # TODO: Fix context object for exporter
    # if exporter:
    #     exporter.export_cell_computation(cell, context)

    return cell


def compute_matrix_Z(
    X: Matrix,
    resolver: CellResolver,
    valley_summary: str,
    tracer: Optional[JSONLTracer] = None,
    exporter: Optional["Neo4jWorkingMemoryExporter"] = None,
) -> Matrix:
    """
    Convenience wrapper - loops over compute_cell_Z.

    Generates the Validation matrix Z by applying station shift to X.

    Args:
        X: Matrix X (Verification) of size 4x4
        resolver: CellResolver for station shift operations
        valley_summary: Current semantic valley position

    Returns:
        Matrix Z of size 4x4
    """
    cells = []
    # X is 4x4, so result Z is also 4x4
    for i in range(X.shape[0]):
        row_cells = []
        for j in range(X.shape[1]):
            cell = compute_cell_Z(i, j, X, resolver, valley_summary, tracer, exporter)
            row_cells.append(cell)
        cells.append(row_cells)

    return Matrix(
        name="Z",
        station="Validation",
        row_labels=X.row_labels,
        col_labels=X.col_labels,
        cells=cells,
    )


def compute_matrix_T_from_B(B: Matrix) -> Matrix:
    """
    Generate Matrix T by slicing and transposing the first 3 rows of Matrix B.

    T represents the evaluation criteria derived from the first three knowledge levels
    (Data, Information, Knowledge) of the decision basis, excluding Wisdom for
    grounding in observable/evaluative criteria.

    Args:
        B: Matrix B (Decision Basis) of size 4x4

    Returns:
        Matrix T of size 4x3 (transposed 3x4 slice of B)
    """
    # Slice first 3 rows from B to create 3x4 matrix
    sliced_cells = []
    for i in range(3):  # First 3 rows only
        row_cells = []
        for j in range(4):
            original_cell = B.get_cell(i, j)
            # Create new cell with same value but different coordinates for the slice
            new_cell = Cell(
                row=i,
                col=j,
                value=original_cell.value,
                provenance={
                    "operation": "slice_and_transpose_B",
                    "sources": ["B"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "coordinates": f"({i}, {j})",
                },
            )
            row_cells.append(new_cell)
        sliced_cells.append(row_cells)

    # Create the 3x4 sliced matrix
    sliced_matrix = Matrix(
        name="B_slice",
        station="Pre-Evaluation Transform",
        row_labels=B.row_labels[:3],  # Data, Information, Knowledge (no Wisdom)
        col_labels=B.col_labels,
        cells=sliced_cells,
    )

    # Transpose the sliced matrix to create T
    T = sliced_matrix.transpose()
    T.name = "T"
    T.station = "Evaluation Criteria"

    return T


def compute_matrix_G(Z: Matrix) -> Matrix:
    """
    Generate Matrix G by slicing the first 3 rows of Matrix Z.

    G represents the validated objectives that will be evaluated against
    the evaluation criteria (T), focusing on the observable levels
    (excluding the fourth row for evaluation grounding).

    Args:
        Z: Matrix Z (Validation) of size 4x4

    Returns:
        Matrix G of size 3x4 (first 3 rows of Z)
    """
    cells = []
    for i in range(3):  # First 3 rows only
        row_cells = []
        for j in range(4):
            original_cell = Z.get_cell(i, j)
            # Create new cell preserving value and updating provenance
            new_cell = Cell(
                row=i,
                col=j,
                value=original_cell.value,
                provenance={
                    "operation": "slice_Z",
                    "sources": ["Z"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "coordinates": f"({i}, {j})",
                },
            )
            row_cells.append(new_cell)
        cells.append(row_cells)

    return Matrix(
        name="G",
        station="Evaluation Input",
        row_labels=Z.row_labels[:3],  # First 3 row labels from Z
        col_labels=Z.col_labels,  # All column labels from Z
        cells=cells,
    )


def compute_array_P(Z: Matrix) -> Matrix:
    """
    Generate Array P by extracting the fourth row of Matrix Z.

    P represents the validation perspective that will be used in
    subsequent evaluation operations, maintaining the matrix interface
    as a 1x4 matrix.

    Args:
        Z: Matrix Z (Validation) of size 4x4

    Returns:
        Matrix P of size 1x4 (fourth row of Z)
    """
    cells = []
    row_cells = []
    for j in range(4):
        original_cell = Z.get_cell(3, j)  # Fourth row (index 3)
        # Create new cell with row=0 for the 1x4 matrix
        new_cell = Cell(
            row=0,  # Reset to row 0 for 1x4 matrix consistency
            col=j,
            value=original_cell.value,
            provenance={
                "operation": "extract_Z_row4",
                "sources": ["Z"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "coordinates": f"(0, {j})",
            },
        )
        row_cells.append(new_cell)
    cells.append(row_cells)

    return Matrix(
        name="P",
        station="Evaluation Context",
        row_labels=[Z.row_labels[3]],  # Fourth row label from Z
        col_labels=Z.col_labels,  # All column labels from Z
        cells=cells,
    )


def compute_cell_E(
    i: int,
    j: int,
    G: Matrix,
    T: Matrix,
    resolver: CellResolver,
    valley_summary: str,
    tracer: Optional[JSONLTracer] = None,
    exporter: Optional["Neo4jWorkingMemoryExporter"] = None,
) -> Cell:
    """
    Complete 3-stage pipeline for computing E[i,j] = G[i,:] dot T[:,j]

    E represents the Evaluation matrix, where validated objectives (G)
    are evaluated against evaluation criteria (T) using the full pipeline.

    Stage 1 (Combinatorial): Generate k-products mechanically (no LLM)
    Stage 2 (Semantic): Resolve word pairs into concepts (LLM)
    Stage 3 (Lensing): Apply ontological interpretation (LLM with deep context)

    Args:
        i: Row index in result matrix E
        j: Column index in result matrix E
        G: Matrix G (Evaluation Input) of size 3x4
        T: Matrix T (Evaluation Criteria) of size 4x3
        resolver: CellResolver for LLM operations
        valley_summary: Current position in semantic valley

    Returns:
        Cell with final semantic result and complete provenance
    """

    # Stage 1: Combinatorial (mechanical, no LLM)
    raw_products = []
    for k in range(G.shape[1]):  # G is 3x4, so k goes 0-3
        g_cell = G.get_cell(i, k)
        t_cell = T.get_cell(k, j)
        product_pair = f"{g_cell.value} * {t_cell.value}"
        raw_products.append(product_pair)

    # Trace Stage 1 (combinatorial - no LLM call, just mechanical result)
    if tracer:
        stage1_context = {
            "station_context": "Evaluation",
            "valley_summary": valley_summary,
            "row_label": G.row_labels[i],
            "col_label": T.col_labels[j],
            "operation_type": "combinatorial",
            "terms": {"products": raw_products},
            "matrix": "E",
            "i": i,
            "j": j,
        }
        tracer.trace_stage(
            "product:combinatorial",
            stage1_context,
            SimpleResult(
                text=", ".join(raw_products),
                terms_used=[f"k={k}" for k in range(len(raw_products))],
                warnings=[],
            ),
            {"station": "Evaluation", "valley_summary": valley_summary, "products": raw_products},
        )

    # Stage 2: Semantic resolution (LLM) in a single multiply call
    stage2_result = resolver.run_stage2_multiply(raw_products, "E")

    # Stage 3: Combined ontological lensing
    # Perform combined lensing instead of 3-step lensing
    final_result = resolver.run_combined_lens(
        content=stage2_result.text,
        component_id="E",
        row_label=G.row_labels[i],
        col_label=T.col_labels[j],
    )

    cell = Cell(
        row=i,
        col=j,
        value=final_result.text,
        provenance=create_provenance(
            operation="compute_E",
            coordinates=f"({G.row_labels[i]}, {T.col_labels[j]})",
            stage_data={
                "stage_1_construct": {
                    "texts": raw_products,
                    "metadata": {},
                    "terms_used": [f"k={k}" for k in range(len(raw_products))],
                    "warnings": [],
                },
                "stage_2_semantic": {
                    "text": stage2_result.text,
                    "metadata": stage2_result.metadata,
                    "terms_used": stage2_result.terms_used,
                    "warnings": stage2_result.warnings,
                },
                "stage_3_combined_lensed": {
                    "text": final_result.text,
                    "metadata": final_result.metadata,
                    "terms_used": final_result.terms_used,
                    "warnings": final_result.warnings,
                },
            },
            sources=["G", "T"],
            traced=tracer is not None,
        ),
    )

    # Export to Neo4j if exporter is provided
    # TODO: Fix context object
    # if exporter:
    #     exporter.export_cell_computation(cell, context)

    return cell


def compute_matrix_E(
    G: Matrix,
    T: Matrix,
    resolver: CellResolver,
    valley_summary: str,
    tracer: Optional[JSONLTracer] = None,
    exporter: Optional["Neo4jWorkingMemoryExporter"] = None,
) -> Matrix:
    """
    Convenience wrapper - loops over compute_cell_E.

    Generates the Evaluation matrix E by applying G * T.

    Args:
        G: Matrix G (Evaluation Input) of size 3x4
        T: Matrix T (Evaluation Criteria) of size 4x3
        resolver: CellResolver for semantic operations
        valley_summary: Current semantic valley position

    Returns:
        Matrix E of size 3x3
    """
    cells = []
    # G is 3x4, T is 4x3, so result E is 3x3
    for i in range(G.shape[0]):
        row_cells = []
        for j in range(T.shape[1]):
            cell = compute_cell_E(i, j, G, T, resolver, valley_summary, tracer, exporter)
            row_cells.append(cell)
        cells.append(row_cells)

    return Matrix(
        name="E",
        station="Evaluation",
        row_labels=G.row_labels,
        col_labels=T.col_labels,
        cells=cells,
    )
