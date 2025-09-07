#!/usr/bin/env python3
"""
CLI for Chirality Framework Semantic Calculator

Provides direct access to the 3-stage pipeline for debugging and observability.

Modes:
- Developer mode (default): rich console UX, tracing, viewer snapshots under `snapshots/`.
- App integration mode: use `compute-pipeline --out runs/<run_id> [--problem-file ...] [--max-seconds ...]` to write contract snapshots and a manifest under `runs/<run_id>/`, and print a single JSON line to stdout on success.
"""

import click
import os
import uuid
import webbrowser
from datetime import datetime, timezone
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

try:
    # Python 3.8+
    from importlib import metadata as _im
except Exception:  # pragma: no cover
    _im = None


def _get_version():
    """Return installed package version; fallback to VERSION.md then 0.0.0."""
    # Prefer the canonical installed package/distribution version
    if _im is not None:
        try:
            return _im.version("chirality-framework")
        except Exception:
            pass
    # Fallback to VERSION.md when running from source tree
    try:
        version_path = Path(__file__).parent.parent / "VERSION.md"
        with open(version_path, "r") as f:
            return f.readline().split("—")[0].strip()
    except Exception:
        return "0.0.0"


# Load environment variables from .env file in project root
load_dotenv(override=True)

# Import core components
from .core.types import Cell, Matrix  # noqa: E402
from .core.matrices import MATRIX_A, MATRIX_B, MATRIX_J  # noqa: E402
from .core.operations import (  # noqa: E402
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
from .core.resolvers import EchoResolver  # noqa: E402

# Conditional import for OpenAI resolver
try:
    from .core.cell_resolver import CellResolver

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    CellResolver = None
from .exporters.working_memory_exporter import Neo4jWorkingMemoryExporter  # noqa: E402
from .core.tracer import JSONLTracer  # noqa: E402
from .exporters.snapshot_exporter import MatrixSnapshotWriter  # noqa: E402
from .viewer.render import (  # noqa: E402
    load_snapshots_for_run,
    render_page,
    render_elements_page,
    write_assets,
    get_latest_run_dir,
    CANONICAL_ORDER,
)

# Click styling for better output
STAGE_STYLE = {"fg": "cyan", "bold": True}
SUCCESS_STYLE = {"fg": "green", "bold": True}
ERROR_STYLE = {"fg": "red", "bold": True}
INFO_STYLE = {"fg": "yellow"}
DIM_STYLE = {"dim": True}


def setup_resolver(resolver_name: str, api_key: Optional[str], verbose: bool = False):
    """
    Setup resolver with robust dependency and API key checking.

    Args:
        resolver_name: Name of resolver ('echo' or 'openai')
        api_key: OpenAI API key (required for openai resolver)
        verbose: Whether to print confirmation messages

    Returns:
        Configured resolver instance

    Raises:
        SystemExit: On configuration errors
    """
    if resolver_name == "openai":
        # Dependency guard
        if not OPENAI_AVAILABLE:
            click.echo(
                click.style(
                    "Error: OpenAI resolver requires additional dependencies.\n"
                    "Install with: pip install 'chirality-framework[openai]'",
                    **ERROR_STYLE,
                )
            )
            sys.exit(1)

        # API key guard
        if not api_key or api_key.strip() == "":
            click.echo(
                click.style(
                    "Error: OpenAI API key required.\n"
                    "Set OPENAI_API_KEY environment variable or use --api-key",
                    **ERROR_STYLE,
                )
            )
            sys.exit(1)

        # Smoke banner
        if verbose:
            click.echo(click.style("Using OpenAI resolver...", **INFO_STYLE))

        return CellResolver()
    else:
        # Smoke banner
        if verbose:
            click.echo(click.style("Using Echo resolver (deterministic mock)", **INFO_STYLE))

        return EchoResolver()


def resolve_run_settings(trace: bool, neo4j_export: bool, trace_only: bool) -> tuple[bool, bool]:
    """
    Resolve final trace and neo4j_export settings based on precedence rules.

    Precedence order:
    1. --trace-only flag overrides everything
    2. CHIRALITY_DISABLE_EXPORT environment variable
    3. User's explicit flags

    Args:
        trace: User's --trace flag value
        neo4j_export: User's --neo4j-export flag value
        trace_only: User's --trace-only flag value

    Returns:
        Tuple of (final_trace, final_neo4j_export)
    """
    final_trace = trace
    final_neo4j_export = neo4j_export

    # Precedence 1: --trace-only flag
    if trace_only:
        final_trace = True
        if neo4j_export:
            click.echo(click.style("Trace-only mode active; Neo4j export disabled.", **INFO_STYLE))
        final_neo4j_export = False
    # Precedence 2: CHIRALITY_DISABLE_EXPORT environment variable
    elif not trace_only:
        disable_export_env = os.getenv("CHIRALITY_DISABLE_EXPORT", "").lower()
        if disable_export_env in {"1", "true", "yes", "on"}:
            if neo4j_export:
                click.echo(
                    click.style(
                        "Neo4j export disabled by CHIRALITY_DISABLE_EXPORT environment variable.",
                        **INFO_STYLE,
                    )
                )
            final_neo4j_export = False
    # Precedence 3: User flags are respected if no overrides

    return final_trace, final_neo4j_export


@click.group()
@click.version_option(version=_get_version(), prog_name="Chirality Framework")
def cli():
    """
    Chirality Framework - Semantic Calculator

    A procedurally-rigorous methodology for structured problem-solving
    through a 3-stage semantic interpretation pipeline:

    \b
    Stage 1 (Combinatorial): Mechanical k-product generation
    Stage 2 (Semantic): LLM resolution of word pairs
    Stage 3 (Lensing): Ontological interpretation through coordinates

    Use 'compute-cell' to debug individual cells through the pipeline.
    """
    pass


@cli.command()
@click.argument(
    "matrix",
    type=click.Choice(["C", "F", "D", "K", "X", "Z", "G", "P", "T", "E"], case_sensitive=False),
)
@click.option("--i", "row", type=int, required=True, help="Row index")
@click.option("--j", "col", type=int, required=True, help="Column index")
@click.option("--verbose", "-v", is_flag=True, help="Show intermediate results from each stage")
@click.option(
    "--resolver",
    type=click.Choice(["echo", "openai"], case_sensitive=False),
    default="echo",
    help="Resolver to use (default: echo for testing)",
)
@click.option(
    "--api-key", envvar="OPENAI_API_KEY", help="OpenAI API key (or set OPENAI_API_KEY env var)"
)
@click.option("--trace/--no-trace", default=False, help="Enable JSONL tracing to traces/ directory")
@click.option(
    "--neo4j-export/--no-neo4j-export", default=False, help="Enable writing output to Neo4j."
)
@click.option("--trace-only", is_flag=True, help="Enable tracing and force-disable Neo4j export.")
def compute_cell(
    matrix: str,
    row: int,
    col: int,
    verbose: bool,
    resolver: str,
    api_key: Optional[str],
    trace: bool,
    neo4j_export: bool,
    trace_only: bool,
):
    """
    Compute a single cell through the 3-stage pipeline.

    \b
    Examples:
        chirality compute-cell C --i 0 --j 0 -v
        chirality compute-cell F --i 1 --j 2 --verbose
        chirality compute-cell D --i 2 --j 1
    """
    resolver_obj = None
    tracer_obj = None
    exporter_obj = None

    try:
        # Use the helper to determine final trace and neo4j_export settings
        final_trace, final_neo4j_export = resolve_run_settings(trace, neo4j_export, trace_only)

        # Setup resolver with robust checking
        resolver_obj = setup_resolver(resolver, api_key, verbose=True)

        # Setup tracer and exporter using final settings
        tracer_obj = JSONLTracer() if final_trace else None
        if final_trace:
            click.echo(click.style("Tracing enabled -> traces/", **INFO_STYLE))

        exporter_obj = None
        if final_neo4j_export:
            # Generate a unique run/session id for this CLI invocation
            run_id = (
                f"cli-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
            )
            run_tag = "cli"
            run_user = os.getenv("USER") or os.getenv("USERNAME")
            exporter_obj = Neo4jWorkingMemoryExporter(
                run_id=run_id,
                run_tag=run_tag,
                run_user=run_user,
            )
            click.echo(click.style(f"Neo4j export enabled (run_id={run_id})", **INFO_STYLE))

        # Get canonical matrices and context
        A, B, J = MATRIX_A, MATRIX_B, MATRIX_J
        valley_summary = "Problem Statement -> [Problem Requirements] -> Solution Objectives"

        click.echo()
        click.echo(click.style(f"Computing {matrix}[{row},{col}]", **STAGE_STYLE))
        click.echo(click.style("=" * 50, **DIM_STYLE))

        # Compute the requested cell based on matrix type
        if matrix.upper() == "C":
            if verbose:
                # Show explicit 3-stage breakdown for C using helper
                _show_c_computation_verbose(
                    row, col, A, B, resolver_obj, valley_summary, tracer_obj
                )
            # Always compute final cell to show consolidated result and provenance
            cell = compute_cell_C(
                row, col, A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj
            )
            _show_cell_result(cell, A.row_labels[row], B.col_labels[col])

        elif matrix.upper() == "F":
            C = compute_matrix_C(A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            if verbose:
                # Minimal staged view for F: element-wise pair → resolve → lens
                click.echo()
                click.echo(click.style("STAGE 1: Element-wise (J ⊙ C)", **STAGE_STYLE))
                click.echo(click.style("-" * 40, **DIM_STYLE))
                j_cell = J.get_cell(row, col)
                c_cell = C.get_cell(row, col)
                pair = f"{j_cell.value} * {c_cell.value}"
                click.echo(f"  Pair: {pair}")

                click.echo(click.style("STAGE 2: Semantic Resolution (LLM)", **STAGE_STYLE))
                click.echo(click.style("-" * 40, **DIM_STYLE))
                click.echo("  Resolving element-wise semantics via canonical pipeline...")
                click.echo()
                click.echo(click.style("STAGE 3: Combined Lensing", **STAGE_STYLE))
                click.echo(click.style("-" * 40, **DIM_STYLE))
                click.echo("  Applying unified row × col × station lens (Objectives)...")

            cell = compute_cell_F(
                row, col, J, C, resolver_obj, valley_summary, tracer_obj, exporter_obj
            )
            _show_cell_result(cell, J.row_labels[row], J.col_labels[col])

        elif matrix.upper() == "D":
            C = compute_matrix_C(A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            F = compute_matrix_F(J, C, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            if verbose:
                # Minimal staged view for D: synthesis formula → lens
                click.echo()
                click.echo(click.style("STAGE 1: Mechanical Formation", **STAGE_STYLE))
                click.echo(click.style("-" * 40, **DIM_STYLE))
                a_cell = A.get_cell(row, col)
                f_cell = F.get_cell(row, col)
                synthesis = f"{a_cell.value} applied to frame the problem; {f_cell.value} to resolve the problem."
                click.echo(f"  {synthesis}")

                click.echo()
                click.echo(click.style("STAGE 2: Semantic Operation (Mechanical +)", **STAGE_STYLE))
                click.echo(click.style("-" * 40, **DIM_STYLE))
                click.echo(f"  A[{row},{col}] + F[{row},{col}] → {synthesis}")

                click.echo()
                click.echo(click.style("STAGE 3: Ontological Lensing", **STAGE_STYLE))
                click.echo(click.style("-" * 40, **DIM_STYLE))
                # Note: Combined lensing now handled directly in operations.py

                click.echo("  Applying unified row × col × station lens (Objectives)...")

            cell = compute_cell_D(
                row, col, A, F, resolver_obj, valley_summary, tracer_obj, exporter_obj
            )
            _show_cell_result(cell, A.row_labels[row], A.col_labels[col])

        elif matrix.upper() == "K":
            # K is the transpose of D
            C = compute_matrix_C(A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            F = compute_matrix_F(J, C, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            D = compute_matrix_D(A, F, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            K = compute_matrix_K(D)

            # Validate indices for K (4x3)
            if row < 0 or row >= 4:
                click.echo(
                    click.style(f"Error: Row index {row} out of range for K (0-3)", **ERROR_STYLE)
                )
                sys.exit(1)
            if col < 0 or col >= 3:
                click.echo(
                    click.style(
                        f"Error: Column index {col} out of range for K (0-2)", **ERROR_STYLE
                    )
                )
                sys.exit(1)

            if verbose:
                click.echo()
                click.echo(click.style("K = D^T (Transpose of Solution Objectives)", **STAGE_STYLE))
                click.echo(click.style("-" * 40, **DIM_STYLE))
                d_cell = D.get_cell(col, row)  # Swapped indices for transpose
                click.echo(f"  D[{col},{row}] → K[{row},{col}]")
                click.echo(f"  Value: {d_cell.value}")

            cell = K.get_cell(row, col)
            _show_cell_result(cell, K.row_labels[row], K.col_labels[col])

        elif matrix.upper() == "X":
            # X = K * J (Verification matrix)
            valley_summary = (
                "Problem Statement -> Problem Requirements -> Solution Objectives -> [Verification]"
            )

            # Compute prerequisite matrices
            C = compute_matrix_C(A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            F = compute_matrix_F(J, C, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            D = compute_matrix_D(A, F, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            K = compute_matrix_K(D)

            # Validate indices for X (4x4)
            if row < 0 or row >= 4:
                click.echo(
                    click.style(f"Error: Row index {row} out of range for X (0-3)", **ERROR_STYLE)
                )
                sys.exit(1)
            if col < 0 or col >= 4:
                click.echo(
                    click.style(
                        f"Error: Column index {col} out of range for X (0-3)", **ERROR_STYLE
                    )
                )
                sys.exit(1)

            if verbose:
                # Show verbose computation for X
                click.echo()
                click.echo(click.style("STAGE 1: Combinatorial (K * J)", **STAGE_STYLE))
                click.echo(click.style("-" * 40, **DIM_STYLE))

                raw_products = []
                for k in range(K.shape[1]):  # K is 4x3
                    k_cell = K.get_cell(row, k)
                    j_cell = J.get_cell(k, col)
                    product = f"{k_cell.value} * {j_cell.value}"
                    raw_products.append(product)
                    click.echo(f"  k={k}: {product}")

                click.echo()
                click.echo(click.style("STAGE 2: Semantic Resolution (LLM)", **STAGE_STYLE))
                click.echo(click.style("-" * 40, **DIM_STYLE))

                click.echo("  Resolving semantic products via canonical pipeline...")

                click.echo()
                click.echo(click.style("STAGE 3: Combined Lensing", **STAGE_STYLE))
                click.echo(click.style("-" * 40, **DIM_STYLE))
                click.echo("  Applying unified row × col × station lens (Verification)...")

            cell = compute_cell_X(
                row, col, K, J, resolver_obj, valley_summary, tracer_obj, exporter_obj
            )
            _show_cell_result(cell, K.row_labels[row], J.col_labels[col])

        elif matrix.upper() == "Z":
            # Z = station shift from X (Verification → Validation)
            valley_summary = "Problem Statement -> Problem Requirements -> Solution Objectives -> Verification -> [Validation]"

            # Compute prerequisite matrices
            C = compute_matrix_C(A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            F = compute_matrix_F(J, C, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            D = compute_matrix_D(A, F, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            K = compute_matrix_K(D)
            X = compute_matrix_X(K, J, resolver_obj, valley_summary, tracer_obj, exporter_obj)

            # Validate indices for Z (4x4)
            if row < 0 or row >= 4:
                click.echo(
                    click.style(f"Error: Row index {row} out of range for Z (0-3)", **ERROR_STYLE)
                )
                sys.exit(1)
            if col < 0 or col >= 4:
                click.echo(
                    click.style(
                        f"Error: Column index {col} out of range for Z (0-3)", **ERROR_STYLE
                    )
                )
                sys.exit(1)

            if verbose:
                # Show verbose computation for Z
                click.echo()
                click.echo(click.style("STAGE 1: Construct (Direct Extract)", **STAGE_STYLE))
                click.echo(click.style("-" * 40, **DIM_STYLE))

                x_cell = X.get_cell(row, col)
                click.echo(f"  Extracting X[{row},{col}]: {x_cell.value[:100]}...")

                click.echo()
                click.echo(
                    click.style("STAGE 2: Combined Lensing (includes Station Shift)", **STAGE_STYLE)
                )
                click.echo(click.style("-" * 40, **DIM_STYLE))
                click.echo("  Applying unified row × col × station lens (Validation)...")

            cell = compute_cell_Z(
                row, col, X, resolver_obj, valley_summary, tracer_obj, exporter_obj
            )
            _show_cell_result(cell, X.row_labels[row], X.col_labels[col])

        elif matrix.upper() == "G":
            # G is first 3 rows of Z
            valley_summary = "Problem Statement -> Problem Requirements -> Solution Objectives -> Verification -> Validation -> [Evaluation Input]"

            # Compute prerequisite matrices up to Z
            C = compute_matrix_C(A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            F = compute_matrix_F(J, C, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            D = compute_matrix_D(A, F, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            K = compute_matrix_K(D)
            X = compute_matrix_X(K, J, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            Z = compute_matrix_Z(X, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            G = compute_matrix_G(Z)

            # Validate indices for G (3x4)
            if row < 0 or row >= 3:
                click.echo(
                    click.style(f"Error: Row index {row} out of range for G (0-2)", **ERROR_STYLE)
                )
                sys.exit(1)
            if col < 0 or col >= 4:
                click.echo(
                    click.style(
                        f"Error: Column index {col} out of range for G (0-3)", **ERROR_STYLE
                    )
                )
                sys.exit(1)

            if verbose:
                click.echo()
                click.echo(click.style("G = Z[0:3,:] (First 3 rows of Validation)", **STAGE_STYLE))
                click.echo(click.style("-" * 40, **DIM_STYLE))
                z_cell = Z.get_cell(row, col)
                click.echo(f"  Z[{row},{col}] → G[{row},{col}]")
                click.echo(f"  Value: {z_cell.value[:100]}...")

            cell = G.get_cell(row, col)
            _show_cell_result(cell, G.row_labels[row], G.col_labels[col])

        elif matrix.upper() == "P":
            # P is fourth row of Z as 1x4 matrix
            valley_summary = "Problem Statement -> Problem Requirements -> Solution Objectives -> Verification -> Validation -> [Evaluation Context]"

            # Compute prerequisite matrices up to Z
            C = compute_matrix_C(A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            F = compute_matrix_F(J, C, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            D = compute_matrix_D(A, F, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            K = compute_matrix_K(D)
            X = compute_matrix_X(K, J, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            Z = compute_matrix_Z(X, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            P = compute_array_P(Z)

            # Validate indices for P (1x4)
            if row != 0:
                click.echo(
                    click.style(
                        f"Error: Row index {row} out of range for P (0 only)", **ERROR_STYLE
                    )
                )
                sys.exit(1)
            if col < 0 or col >= 4:
                click.echo(
                    click.style(
                        f"Error: Column index {col} out of range for P (0-3)", **ERROR_STYLE
                    )
                )
                sys.exit(1)

            if verbose:
                click.echo()
                click.echo(
                    click.style("P = Z[3,:] (Fourth row of Validation as 1x4)", **STAGE_STYLE)
                )
                click.echo(click.style("-" * 40, **DIM_STYLE))
                z_cell = Z.get_cell(3, col)
                click.echo(f"  Z[3,{col}] → P[0,{col}]")
                click.echo(f"  Value: {z_cell.value[:100]}...")

            cell = P.get_cell(row, col)
            _show_cell_result(cell, P.row_labels[row], P.col_labels[col])

        elif matrix.upper() == "T":
            # T is transpose of first 3 rows of B
            valley_summary = "Problem Statement -> Problem Requirements -> Solution Objectives -> Verification -> Validation -> [Evaluation Criteria]"

            T = compute_matrix_T_from_B(B)

            # Validate indices for T (4x3)
            if row < 0 or row >= 4:
                click.echo(
                    click.style(f"Error: Row index {row} out of range for T (0-3)", **ERROR_STYLE)
                )
                sys.exit(1)
            if col < 0 or col >= 3:
                click.echo(
                    click.style(
                        f"Error: Column index {col} out of range for T (0-2)", **ERROR_STYLE
                    )
                )
                sys.exit(1)

            if verbose:
                click.echo()
                click.echo(
                    click.style("T = (B[0:3,:])^T (Transpose of first 3 rows of B)", **STAGE_STYLE)
                )
                click.echo(click.style("-" * 40, **DIM_STYLE))
                # Show the source cell from B that was transposed
                b_cell = B.get_cell(col, row)  # Swapped indices for transpose
                click.echo(f"  B[{col},{row}] → T[{row},{col}]")
                click.echo(f"  Value: {b_cell.value}")

            cell = T.get_cell(row, col)
            _show_cell_result(cell, T.row_labels[row], T.col_labels[col])

        elif matrix.upper() == "E":
            # E = G * T (Evaluation matrix)
            valley_summary = "Problem Statement -> Problem Requirements -> Solution Objectives -> Verification -> Validation -> [Evaluation]"

            # Compute prerequisite matrices
            C = compute_matrix_C(A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            F = compute_matrix_F(J, C, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            D = compute_matrix_D(A, F, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            K = compute_matrix_K(D)
            X = compute_matrix_X(K, J, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            Z = compute_matrix_Z(X, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            G = compute_matrix_G(Z)
            T = compute_matrix_T_from_B(B)

            # Validate indices for E (3x3)
            if row < 0 or row >= 3:
                click.echo(
                    click.style(f"Error: Row index {row} out of range for E (0-2)", **ERROR_STYLE)
                )
                sys.exit(1)
            if col < 0 or col >= 3:
                click.echo(
                    click.style(
                        f"Error: Column index {col} out of range for E (0-2)", **ERROR_STYLE
                    )
                )
                sys.exit(1)

            if verbose:
                # Show verbose computation for E
                click.echo()
                click.echo(click.style("STAGE 1: Combinatorial (G * T)", **STAGE_STYLE))
                click.echo(click.style("-" * 40, **DIM_STYLE))

                raw_products = []
                for k in range(G.shape[1]):  # G is 3x4
                    g_cell = G.get_cell(row, k)
                    t_cell = T.get_cell(k, col)
                    product = f"{g_cell.value} * {t_cell.value}"
                    raw_products.append(product)
                    click.echo(f"  k={k}: {product}")

                click.echo()
                click.echo(click.style("STAGE 2: Semantic Resolution (LLM)", **STAGE_STYLE))
                click.echo(click.style("-" * 40, **DIM_STYLE))
                click.echo("  Resolving semantic products via canonical pipeline...")

                click.echo()
                click.echo(click.style("STAGE 3: Combined Lensing", **STAGE_STYLE))
                click.echo(click.style("-" * 40, **DIM_STYLE))
                click.echo("  Applying unified row × col × station lens (Evaluation)...")

            cell = compute_cell_E(
                row, col, G, T, resolver_obj, valley_summary, tracer_obj, exporter_obj
            )
            _show_cell_result(cell, G.row_labels[row], T.col_labels[col])

    except Exception as e:
        click.echo(click.style(f"Error: {e}", **ERROR_STYLE))
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)
    finally:
        # Safely close connections
        if tracer_obj:
            tracer_obj.close()
            click.echo(click.style("✓ Trace file closed.", **DIM_STYLE))
        if exporter_obj:
            exporter_obj.close()
            click.echo(click.style("✓ Neo4j connection closed.", **DIM_STYLE))


def _show_c_computation_verbose(
    row: int, col: int, A: Matrix, B: Matrix, resolver, valley_summary: str, tracer
):
    """Show verbose output for C matrix cell computation."""
    click.echo()
    click.echo(click.style("STAGE 1: Combinatorial (Mechanical)", **STAGE_STYLE))
    click.echo(click.style("-" * 40, **DIM_STYLE))

    # Stage 1: Generate k-products
    raw_products = []
    for k in range(A.shape[1]):
        a_cell = A.get_cell(row, k)
        b_cell = B.get_cell(k, col)
        product = f"{a_cell.value} * {b_cell.value}"
        raw_products.append(product)
        click.echo(f"  k={k}: {product}")

    click.echo()
    click.echo(click.style("STAGE 2: Semantic Resolution (LLM)", **STAGE_STYLE))
    click.echo(click.style("-" * 40, **DIM_STYLE))

    click.echo("  Resolving semantic products via canonical pipeline...")

    click.echo()
    click.echo(click.style("STAGE 3: Combined Lensing", **STAGE_STYLE))
    click.echo(click.style("-" * 40, **DIM_STYLE))
    click.echo("  Applying unified row × col × station lens (Requirements)...")

    click.echo()
    click.echo(click.style("FINAL RESULT:", **SUCCESS_STYLE))
    click.echo(click.style("-" * 40, **DIM_STYLE))
    click.echo("  [Cell computation completed]")


def _show_cell_result(cell: Cell, row_label: str, col_label: str):
    """Show the final cell result and provenance."""
    click.echo()
    click.echo(click.style("Result:", **SUCCESS_STYLE))
    click.echo(f"  Coordinates: ({row_label}, {col_label})")
    click.echo(f"  Value: {cell.value}")

    click.echo()
    click.echo(click.style("Provenance:", **INFO_STYLE))
    _show_provenance(cell.provenance)


def _show_provenance(provenance: dict, indent: int = 2):
    """Pretty print provenance dictionary."""
    for key, value in provenance.items():
        if isinstance(value, list) and len(value) > 3:
            # Abbreviate long lists
            click.echo(f"{' ' * indent}{key}: [{len(value)} items]")
            for item in value[:2]:
                click.echo(f"{' ' * (indent + 2)}- {item}")
            click.echo(f"{' ' * (indent + 2)}... ({len(value) - 2} more)")
        else:
            click.echo(f"{' ' * indent}{key}: {value}")


@cli.command()
@click.argument(
    "matrix",
    type=click.Choice(
        ["A", "B", "J", "C", "F", "D", "K", "X", "Z", "G", "P", "T", "E"], case_sensitive=False
    ),
)
@click.option(
    "--resolver",
    type=click.Choice(["echo", "openai"], case_sensitive=False),
    default="echo",
    help="Resolver to use (default: echo for testing)",
)
@click.option(
    "--api-key", envvar="OPENAI_API_KEY", help="OpenAI API key (or set OPENAI_API_KEY env var)"
)
@click.option("--trace/--no-trace", default=False, help="Enable JSONL tracing to traces/ directory")
@click.option(
    "--neo4j-export/--no-neo4j-export", default=False, help="Enable writing output to Neo4j."
)
@click.option("--trace-only", is_flag=True, help="Enable tracing and force-disable Neo4j export.")
@click.option("--snapshot-jsonl", is_flag=True, help="Save a JSONL snapshot of the final matrix")
@click.option("--verbose", "-v", is_flag=True, help="Show progress messages")
def compute_matrix(
    matrix: str,
    resolver: str,
    api_key: Optional[str],
    trace: bool,
    neo4j_export: bool,
    trace_only: bool,
    snapshot_jsonl: bool,
    verbose: bool,
):
    """
    Compute a complete matrix through the pipeline.

    \b
    Examples:
        chirality compute-matrix C --verbose
        chirality compute-matrix X --resolver openai --trace-only
        chirality compute-matrix E --snapshot-jsonl
        chirality compute-matrix A --snapshot-jsonl  # Snapshot base matrices
    """
    resolver_obj = None
    tracer_obj = None
    exporter_obj = None
    snapshot_writer = None

    try:
        # Use the helper to determine final trace and neo4j_export settings
        final_trace, final_neo4j_export = resolve_run_settings(trace, neo4j_export, trace_only)

        # Generate a single run ID for correlation
        run_id = (
            f"matrix-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
        )

        # Setup resolver with robust checking
        resolver_obj = setup_resolver(resolver, api_key, verbose)

        # Setup tracer using final settings
        tracer_obj = JSONLTracer() if final_trace else None
        if final_trace and verbose:
            click.echo(click.style(f"Tracing enabled -> traces/ (run_id: {run_id})", **INFO_STYLE))

        # Setup exporter using final settings
        exporter_obj = None
        if final_neo4j_export:
            run_tag = "matrix-cli"
            run_user = os.getenv("USER") or os.getenv("USERNAME")
            exporter_obj = Neo4jWorkingMemoryExporter(
                run_id=run_id,
                run_tag=run_tag,
                run_user=run_user,
            )
            if verbose:
                click.echo(click.style(f"Neo4j export enabled (run_id: {run_id})", **INFO_STYLE))

        # Setup snapshot writer if requested
        if snapshot_jsonl:
            snapshot_writer = MatrixSnapshotWriter(run_id)
            if verbose:
                click.echo(click.style(f"Snapshot enabled -> snapshots/{run_id}/", **INFO_STYLE))

        # Get canonical matrices
        A, B, J = MATRIX_A, MATRIX_B, MATRIX_J
        valley_summary = "Problem Statement -> Problem Requirements -> Solution Objectives -> Verification -> Validation -> Evaluation"

        if verbose:
            click.echo()
            click.echo(click.style(f"Computing Matrix {matrix.upper()}", **STAGE_STYLE))
            click.echo(click.style("=" * 50, **DIM_STYLE))

        # Determine which matrix to compute and its dependencies
        result_matrix = None
        matrix_upper = matrix.upper()

        if matrix_upper == "A":
            result_matrix = A
        elif matrix_upper == "B":
            result_matrix = B
        elif matrix_upper == "J":
            result_matrix = J
        elif matrix_upper == "C":
            if verbose:
                click.echo("Computing C = A * B...")
            result_matrix = compute_matrix_C(
                A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj
            )
        elif matrix_upper == "F":
            if verbose:
                click.echo("Computing prerequisites: C...")
            C = compute_matrix_C(A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            if verbose:
                click.echo("Computing F = J ⊙ C...")
            result_matrix = compute_matrix_F(
                J, C, resolver_obj, valley_summary, tracer_obj, exporter_obj
            )
        elif matrix_upper == "D":
            if verbose:
                click.echo("Computing prerequisites: C, F...")
            C = compute_matrix_C(A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            F = compute_matrix_F(J, C, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            if verbose:
                click.echo("Computing D = synthesis(A, F)...")
            result_matrix = compute_matrix_D(
                A, F, resolver_obj, valley_summary, tracer_obj, exporter_obj
            )
        elif matrix_upper == "K":
            if verbose:
                click.echo("Computing prerequisites: C, F, D...")
            C = compute_matrix_C(A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            F = compute_matrix_F(J, C, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            D = compute_matrix_D(A, F, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            if verbose:
                click.echo("Computing K = D^T...")
            result_matrix = compute_matrix_K(D)
        elif matrix_upper == "X":
            if verbose:
                click.echo("Computing prerequisites: C, F, D, K...")
            C = compute_matrix_C(A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            F = compute_matrix_F(J, C, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            D = compute_matrix_D(A, F, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            K = compute_matrix_K(D)
            if verbose:
                click.echo("Computing X = K * J...")
            result_matrix = compute_matrix_X(
                K, J, resolver_obj, valley_summary, tracer_obj, exporter_obj
            )
        elif matrix_upper == "Z":
            if verbose:
                click.echo("Computing prerequisites: C, F, D, K, X...")
            C = compute_matrix_C(A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            F = compute_matrix_F(J, C, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            D = compute_matrix_D(A, F, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            K = compute_matrix_K(D)
            X = compute_matrix_X(K, J, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            if verbose:
                click.echo("Computing Z = shift(X)...")
            result_matrix = compute_matrix_Z(
                X, resolver_obj, valley_summary, tracer_obj, exporter_obj
            )
        elif matrix_upper == "G":
            if verbose:
                click.echo("Computing prerequisites: C, F, D, K, X, Z...")
            C = compute_matrix_C(A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            F = compute_matrix_F(J, C, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            D = compute_matrix_D(A, F, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            K = compute_matrix_K(D)
            X = compute_matrix_X(K, J, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            Z = compute_matrix_Z(X, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            if verbose:
                click.echo("Computing G = Z[0:3,:]...")
            result_matrix = compute_matrix_G(Z)
        elif matrix_upper == "P":
            if verbose:
                click.echo("Computing prerequisites: C, F, D, K, X, Z...")
            C = compute_matrix_C(A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            F = compute_matrix_F(J, C, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            D = compute_matrix_D(A, F, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            K = compute_matrix_K(D)
            X = compute_matrix_X(K, J, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            Z = compute_matrix_Z(X, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            if verbose:
                click.echo("Computing P = Z[3,:]...")
            result_matrix = compute_array_P(Z)
        elif matrix_upper == "T":
            if verbose:
                click.echo("Computing T = (B[0:3,:])^T...")
            result_matrix = compute_matrix_T_from_B(B)
        elif matrix_upper == "E":
            if verbose:
                click.echo("Computing prerequisites: C, F, D, K, X, Z, G, T...")
            C = compute_matrix_C(A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            F = compute_matrix_F(J, C, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            D = compute_matrix_D(A, F, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            K = compute_matrix_K(D)
            X = compute_matrix_X(K, J, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            Z = compute_matrix_Z(X, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            G = compute_matrix_G(Z)
            T = compute_matrix_T_from_B(B)
            if verbose:
                click.echo("Computing E = G * T...")
            result_matrix = compute_matrix_E(
                G, T, resolver_obj, valley_summary, tracer_obj, exporter_obj
            )

        # Display summary
        if result_matrix:
            click.echo()
            click.echo(
                click.style(f"Matrix {matrix.upper()} Computed Successfully", **SUCCESS_STYLE)
            )
            click.echo(click.style("-" * 40, **DIM_STYLE))
            click.echo(f"  Name: {result_matrix.name}")
            click.echo(f"  Station: {result_matrix.station}")
            click.echo(f"  Shape: {result_matrix.shape[0]}×{result_matrix.shape[1]}")
            click.echo(
                f"  Row Labels: {', '.join(result_matrix.row_labels[:3])}..."
                if len(result_matrix.row_labels) > 3
                else f"  Row Labels: {', '.join(result_matrix.row_labels)}"
            )
            click.echo(
                f"  Column Labels: {', '.join(result_matrix.col_labels[:3])}..."
                if len(result_matrix.col_labels) > 3
                else f"  Column Labels: {', '.join(result_matrix.col_labels)}"
            )

            # Save snapshot if requested
            if snapshot_writer:
                snapshot_path = snapshot_writer.write_matrix(result_matrix, resolver)
                click.echo()
                click.echo(click.style(f"✓ Snapshot saved: {snapshot_path}", **SUCCESS_STYLE))
                click.echo(f"  Cells: {result_matrix.shape[0] * result_matrix.shape[1]}")
                click.echo(f"  Query with: jq -r '.cells | length' {snapshot_path}")

    except Exception as e:
        click.echo(click.style(f"Error: {e}", **ERROR_STYLE))
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)
    finally:
        # Safely close connections
        if tracer_obj:
            tracer_obj.close()
            if verbose:
                click.echo(click.style("✓ Trace file closed.", **DIM_STYLE))
        if exporter_obj:
            exporter_obj.close()
            if verbose:
                click.echo(click.style("✓ Neo4j connection closed.", **DIM_STYLE))


@cli.command()
@click.option(
    "--resolver",
    type=click.Choice(["echo", "openai"], case_sensitive=False),
    default="echo",
    help="Resolver to use (default: echo for testing)",
)
@click.option(
    "--api-key", envvar="OPENAI_API_KEY", help="OpenAI API key (or set OPENAI_API_KEY env var)"
)
@click.option("--trace-only", is_flag=True, help="Enable tracing and force-disable Neo4j export.")
@click.option("--snapshot-jsonl", is_flag=True, help="Save JSONL snapshots of computed matrices")
@click.option(
    "--include-base", is_flag=True, help="Include base matrices (A, B, J) in the pipeline"
)
@click.option("--only", help='Compute only specific matrices (comma-separated list, e.g., "C,F,D")')
@click.option("--verbose", "-v", is_flag=True, help="Show progress messages")
@click.option(
    "--out",
    "out_dir",
    type=click.Path(file_okay=False, dir_okay=True),
    help="App mode: output run directory (e.g., runs/<run_id>)",
)
@click.option(
    "--problem-file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help='App mode: JSON file with {"title": str, "statement": str}',
)
@click.option(
    "--max-seconds", type=int, help="App mode: best-effort hard timeout in seconds (e.g., 900)"
)
def compute_pipeline(
    resolver: str,
    api_key: Optional[str],
    trace_only: bool,
    snapshot_jsonl: bool,
    include_base: bool,
    only: Optional[str],
    verbose: bool,
    out_dir: Optional[str],
    problem_file: Optional[str],
    max_seconds: Optional[int],
):
    """
    Compute multiple matrices through the pipeline with correlated tracing and snapshots.

    \b
    Examples:
        chirality compute-pipeline --trace-only --snapshot-jsonl --include-base
        chirality compute-pipeline --resolver openai --only "C,F,D" --verbose
        chirality compute-pipeline --include-base --snapshot-jsonl
    """
    resolver_obj = None
    tracer_obj = None
    exporter_obj = None
    snapshot_writer = None

    # App-integration mode is engaged when --out or --problem-file or --max-seconds provided
    app_mode = bool(out_dir or problem_file or max_seconds)

    # If in app mode, suppress non-essential stdout (treat stdout as data channel)
    # We still respect --verbose (logs go to stderr via click.echo if needed)

    # Define canonical matrix list for validation
    VALID_MATRICES = ["A", "B", "J", "C", "F", "D", "K", "X", "Z", "G", "P", "T", "E"]

    try:
        # Use the helper to determine final trace and neo4j_export settings
        final_trace, final_neo4j_export = resolve_run_settings(False, False, trace_only)

        # Generate a single run ID for correlation (non-app mode)
        run_id = f"pipeline-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"

        # Input validation for --only flag
        matrices_to_compute = []
        if only:
            requested_matrices = [m.strip().upper() for m in only.split(",")]
            for matrix_name in requested_matrices:
                if matrix_name not in VALID_MATRICES:
                    click.echo(
                        click.style(
                            f"Error: Invalid matrix '{matrix_name}'. Valid matrices: {', '.join(VALID_MATRICES)}",
                            **ERROR_STYLE,
                        )
                    )
                    sys.exit(1)
            matrices_to_compute = requested_matrices
        else:
            # Default: compute all derived matrices
            matrices_to_compute = ["C", "F", "D", "K", "X", "Z", "G", "P", "T", "E"]

            # Include base matrices if requested
            if include_base:
                matrices_to_compute = ["A", "B", "J"] + matrices_to_compute

        # User feedback about final settings
        if not final_neo4j_export and trace_only:
            click.echo(click.style("Neo4j export disabled (trace-only mode active).", **INFO_STYLE))

        # Setup resolver with robust checking
        resolver_obj = setup_resolver(resolver, api_key, verbose)

        # Setup tracer using final settings
        tracer_obj = JSONLTracer(thread_id=run_id) if final_trace else None
        if final_trace and verbose:
            click.echo(click.style(f"Tracing enabled -> traces/ (run_id: {run_id})", **INFO_STYLE))

        # Setup exporter using final settings
        exporter_obj = None
        if final_neo4j_export:
            run_tag = "pipeline-cli"
            run_user = os.getenv("USER") or os.getenv("USERNAME")
            exporter_obj = Neo4jWorkingMemoryExporter(
                run_id=run_id,
                run_tag=run_tag,
                run_user=run_user,
            )
            if verbose:
                click.echo(click.style(f"Neo4j export enabled (run_id: {run_id})", **INFO_STYLE))

        # Setup snapshot writer if requested
        if snapshot_jsonl:
            snapshot_writer = MatrixSnapshotWriter(run_id)
            if verbose:
                click.echo(click.style(f"Snapshot enabled -> snapshots/{run_id}/", **INFO_STYLE))

        # Dictionary to cache computed matrices and avoid re-computation
        computed_matrices = {}

        # Get canonical matrices
        A, B, J = MATRIX_A, MATRIX_B, MATRIX_J
        computed_matrices["A"] = A
        computed_matrices["B"] = B
        computed_matrices["J"] = J

        valley_summary = "Problem Statement -> Problem Requirements -> Solution Objectives -> Verification -> Validation -> Evaluation"

        if verbose and not app_mode:
            click.echo()
            click.echo(
                click.style(f"Computing Pipeline: {', '.join(matrices_to_compute)}", **STAGE_STYLE)
            )
            click.echo(click.style("=" * 50, **DIM_STYLE))

        # In app mode, jump to contract-compliant writer path
        if app_mode:
            import json as _json
            import re as _re
            import time as _time
            from pathlib import Path as _Path
            from .exporters.manifest_exporter import ManifestExporter

            start_ts = _time.time()
            # Resolve run_dir and run_id
            runs_root = _Path("runs")
            if out_dir:
                run_path = _Path(out_dir)
                run_id = run_path.name
                # Validate run_id
                if not _re.fullmatch(r"^[a-z0-9-_]{1,64}$", run_id):
                    raise click.BadParameter(
                        f"Invalid run_id '{run_id}'. Must match ^[a-z0-9-_]{1,64}$"
                    )
                # Disallow traversal in out_dir
                if ".." in run_path.parts:
                    raise click.BadParameter("Invalid --out path (no traversal allowed)")
            else:
                # Auto-generate run_id
                import time

                timestamp = int(time.time())
                run_id = f"run_{timestamp}_{uuid.uuid4().hex[:6]}"
                run_path = runs_root / run_id
            # Ensure directories
            snapshots_out = run_path / "snapshots"
            snapshots_out.mkdir(parents=True, exist_ok=True)

            # Problem payload
            problem_dict = None
            if problem_file:
                with open(problem_file, "r", encoding="utf-8") as pf:
                    problem_dict = _json.load(pf)
                # Minimal validation
                if (
                    not isinstance(problem_dict, dict)
                    or "title" not in problem_dict
                    or "statement" not in problem_dict
                ):
                    raise click.BadParameter('--problem-file must contain {"title", "statement"}')
            else:
                problem_dict = {"title": "", "statement": ""}

            # Compute required matrices with dependencies
            computed: dict[str, Matrix] = {}
            computed["C"] = compute_matrix_C(
                A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj
            )
            computed["F"] = compute_matrix_F(
                J, computed["C"], resolver_obj, valley_summary, tracer_obj, exporter_obj
            )
            computed["D"] = compute_matrix_D(
                A, computed["F"], resolver_obj, valley_summary, tracer_obj, exporter_obj
            )
            computed["K"] = compute_matrix_K(computed["D"])
            computed["X"] = compute_matrix_X(
                computed["K"], J, resolver_obj, valley_summary, tracer_obj, exporter_obj
            )
            # Validation/Evaluation deps for E
            computed["Z"] = compute_matrix_Z(
                computed["X"], resolver_obj, valley_summary, tracer_obj, exporter_obj
            )
            computed["G"] = compute_matrix_G(computed["Z"])
            computed["T"] = compute_matrix_T_from_B(B)
            computed["E"] = compute_matrix_E(
                computed["G"], computed["T"], resolver_obj, valley_summary, tracer_obj, exporter_obj
            )
            # Optional derived for viewer ergonomics
            try:
                computed["P"] = compute_array_P(computed["Z"])
            except Exception:
                pass

            # Timeout checks (best-effort)
            def _check_deadline():
                if max_seconds is None:
                    return
                if (_time.time() - start_ts) > max_seconds:
                    raise TimeoutError("max-seconds exceeded")

            _check_deadline()

            # Write per-cell JSONL snapshots for C, D, X, E (contract)
            writer = MatrixSnapshotWriter(run_id)
            files: dict[str, tuple[_Path, str]] = {}
            for m in ["C", "D", "X", "E"]:
                _check_deadline()
                path = writer.write_matrix_cells_jsonl(computed[m], snapshots_out, f"{m}.jsonl")
                files[m] = (path, "cells-jsonl-v1")

            # Dual-write legacy snapshots for viewer and existing workflows
            legacy_writer = MatrixSnapshotWriter(run_id)
            for m_name, m_val in computed.items():
                _check_deadline()
                try:
                    legacy_writer.write_matrix(m_val, resolver)
                except Exception:
                    # Continue on best-effort basis; app contract relies on runs/ manifest
                    pass

            # Build and write manifest last (atomic)
            exporter = ManifestExporter(
                run_path, "chirality-framework", _get_version(), framework_schema_version="1.0.0"
            )
            durations = {"total_ms": int((_time.time() - start_ts) * 1000)}
            manifest_path = exporter.write_manifest(run_id, problem_dict, durations, files)

            # Final stdout JSON (and nothing else)
            click.echo(
                _json.dumps({"run_id": run_id, "manifest": str(manifest_path).replace("\\", "/")}),
                nl=True,
            )
            return

        # Iterate through required matrices, computing dependencies as needed (legacy path)
        for matrix_name in matrices_to_compute:
            if verbose:
                click.echo(f"\n  Computing Matrix {matrix_name}...")

            if matrix_name == "A":
                result_matrix = A
            elif matrix_name == "B":
                result_matrix = B
            elif matrix_name == "J":
                result_matrix = J
            elif matrix_name == "C":
                if "C" not in computed_matrices:
                    computed_matrices["C"] = compute_matrix_C(
                        A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj
                    )
                result_matrix = computed_matrices["C"]
            elif matrix_name == "F":
                if "C" not in computed_matrices:
                    computed_matrices["C"] = compute_matrix_C(
                        A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj
                    )
                if "F" not in computed_matrices:
                    computed_matrices["F"] = compute_matrix_F(
                        J,
                        computed_matrices["C"],
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                result_matrix = computed_matrices["F"]
            elif matrix_name == "D":
                if "C" not in computed_matrices:
                    computed_matrices["C"] = compute_matrix_C(
                        A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj
                    )
                if "F" not in computed_matrices:
                    computed_matrices["F"] = compute_matrix_F(
                        J,
                        computed_matrices["C"],
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                if "D" not in computed_matrices:
                    computed_matrices["D"] = compute_matrix_D(
                        A,
                        computed_matrices["F"],
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                result_matrix = computed_matrices["D"]
            elif matrix_name == "K":
                # Ensure D is computed first
                if "C" not in computed_matrices:
                    computed_matrices["C"] = compute_matrix_C(
                        A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj
                    )
                if "F" not in computed_matrices:
                    computed_matrices["F"] = compute_matrix_F(
                        J,
                        computed_matrices["C"],
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                if "D" not in computed_matrices:
                    computed_matrices["D"] = compute_matrix_D(
                        A,
                        computed_matrices["F"],
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                if "K" not in computed_matrices:
                    computed_matrices["K"] = compute_matrix_K(computed_matrices["D"])
                result_matrix = computed_matrices["K"]
            elif matrix_name == "X":
                # Ensure K is computed first
                if "C" not in computed_matrices:
                    computed_matrices["C"] = compute_matrix_C(
                        A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj
                    )
                if "F" not in computed_matrices:
                    computed_matrices["F"] = compute_matrix_F(
                        J,
                        computed_matrices["C"],
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                if "D" not in computed_matrices:
                    computed_matrices["D"] = compute_matrix_D(
                        A,
                        computed_matrices["F"],
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                if "K" not in computed_matrices:
                    computed_matrices["K"] = compute_matrix_K(computed_matrices["D"])
                if "X" not in computed_matrices:
                    computed_matrices["X"] = compute_matrix_X(
                        computed_matrices["K"],
                        J,
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                result_matrix = computed_matrices["X"]
            elif matrix_name == "Z":
                # Ensure X is computed first
                if "C" not in computed_matrices:
                    computed_matrices["C"] = compute_matrix_C(
                        A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj
                    )
                if "F" not in computed_matrices:
                    computed_matrices["F"] = compute_matrix_F(
                        J,
                        computed_matrices["C"],
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                if "D" not in computed_matrices:
                    computed_matrices["D"] = compute_matrix_D(
                        A,
                        computed_matrices["F"],
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                if "K" not in computed_matrices:
                    computed_matrices["K"] = compute_matrix_K(computed_matrices["D"])
                if "X" not in computed_matrices:
                    computed_matrices["X"] = compute_matrix_X(
                        computed_matrices["K"],
                        J,
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                if "Z" not in computed_matrices:
                    computed_matrices["Z"] = compute_matrix_Z(
                        computed_matrices["X"],
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                result_matrix = computed_matrices["Z"]
            elif matrix_name == "G":
                # Ensure Z is computed first
                if "C" not in computed_matrices:
                    computed_matrices["C"] = compute_matrix_C(
                        A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj
                    )
                if "F" not in computed_matrices:
                    computed_matrices["F"] = compute_matrix_F(
                        J,
                        computed_matrices["C"],
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                if "D" not in computed_matrices:
                    computed_matrices["D"] = compute_matrix_D(
                        A,
                        computed_matrices["F"],
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                if "K" not in computed_matrices:
                    computed_matrices["K"] = compute_matrix_K(computed_matrices["D"])
                if "X" not in computed_matrices:
                    computed_matrices["X"] = compute_matrix_X(
                        computed_matrices["K"],
                        J,
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                if "Z" not in computed_matrices:
                    computed_matrices["Z"] = compute_matrix_Z(
                        computed_matrices["X"],
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                if "G" not in computed_matrices:
                    computed_matrices["G"] = compute_matrix_G(computed_matrices["Z"])
                result_matrix = computed_matrices["G"]
            elif matrix_name == "P":
                # Ensure Z is computed first
                if "C" not in computed_matrices:
                    computed_matrices["C"] = compute_matrix_C(
                        A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj
                    )
                if "F" not in computed_matrices:
                    computed_matrices["F"] = compute_matrix_F(
                        J,
                        computed_matrices["C"],
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                if "D" not in computed_matrices:
                    computed_matrices["D"] = compute_matrix_D(
                        A,
                        computed_matrices["F"],
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                if "K" not in computed_matrices:
                    computed_matrices["K"] = compute_matrix_K(computed_matrices["D"])
                if "X" not in computed_matrices:
                    computed_matrices["X"] = compute_matrix_X(
                        computed_matrices["K"],
                        J,
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                if "Z" not in computed_matrices:
                    computed_matrices["Z"] = compute_matrix_Z(
                        computed_matrices["X"],
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                if "P" not in computed_matrices:
                    computed_matrices["P"] = compute_array_P(computed_matrices["Z"])
                result_matrix = computed_matrices["P"]
            elif matrix_name == "T":
                if "T" not in computed_matrices:
                    computed_matrices["T"] = compute_matrix_T_from_B(B)
                result_matrix = computed_matrices["T"]
            elif matrix_name == "E":
                # Ensure G and T are computed first
                if "C" not in computed_matrices:
                    computed_matrices["C"] = compute_matrix_C(
                        A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj
                    )
                if "F" not in computed_matrices:
                    computed_matrices["F"] = compute_matrix_F(
                        J,
                        computed_matrices["C"],
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                if "D" not in computed_matrices:
                    computed_matrices["D"] = compute_matrix_D(
                        A,
                        computed_matrices["F"],
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                if "K" not in computed_matrices:
                    computed_matrices["K"] = compute_matrix_K(computed_matrices["D"])
                if "X" not in computed_matrices:
                    computed_matrices["X"] = compute_matrix_X(
                        computed_matrices["K"],
                        J,
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                if "Z" not in computed_matrices:
                    computed_matrices["Z"] = compute_matrix_Z(
                        computed_matrices["X"],
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                if "G" not in computed_matrices:
                    computed_matrices["G"] = compute_matrix_G(computed_matrices["Z"])
                if "T" not in computed_matrices:
                    computed_matrices["T"] = compute_matrix_T_from_B(B)
                if "E" not in computed_matrices:
                    computed_matrices["E"] = compute_matrix_E(
                        computed_matrices["G"],
                        computed_matrices["T"],
                        resolver_obj,
                        valley_summary,
                        tracer_obj,
                        exporter_obj,
                    )
                result_matrix = computed_matrices["E"]

            # Save snapshot if requested
            if snapshot_jsonl:
                if snapshot_writer is None:
                    snapshot_writer = MatrixSnapshotWriter(run_id)

                snapshot_path = snapshot_writer.write_matrix(result_matrix, resolver)
                if verbose:
                    click.echo(f"    ✓ Snapshot: {snapshot_path.name}")

            if verbose:
                cell_count = result_matrix.shape[0] * result_matrix.shape[1]
                click.echo(
                    f"    ✓ {matrix_name} ({result_matrix.shape[0]}×{result_matrix.shape[1]}, {cell_count} cells)"
                )

        # Final summary (legacy path)
        click.echo()
        click.echo(click.style("Pipeline Computation Complete", **SUCCESS_STYLE))
        click.echo(click.style("-" * 40, **DIM_STYLE))
        click.echo(f"  Run ID: {run_id}")
        click.echo(f"  Matrices computed: {len(matrices_to_compute)}")

        if final_trace:
            click.echo("  Trace files: traces/")
        if snapshot_jsonl:
            snapshot_dir = (
                snapshot_writer.get_snapshot_directory()
                if snapshot_writer
                else f"snapshots/{run_id}/"
            )
            click.echo(f"  Snapshots: {snapshot_dir}")

    except click.BadParameter as e:
        click.echo(click.style(f"Error: {e}", **ERROR_STYLE), err=True)
        sys.exit(2)
    except TimeoutError as e:
        click.echo(click.style(f"Timeout: {e}", **ERROR_STYLE), err=True)
        sys.exit(3)
    except (OSError, IOError) as e:
        click.echo(click.style(f"I/O Error: {e}", **ERROR_STYLE), err=True)
        sys.exit(4)
    except ImportError as e:
        # Likely resolver dependency (e.g., openai)
        click.echo(click.style(f"Resolver Error: {e}", **ERROR_STYLE), err=True)
        sys.exit(5)
    except Exception as e:
        click.echo(click.style(f"Error: {e}", **ERROR_STYLE), err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)
    finally:
        # Resource Management: Ensure tracer.close() is called if tracer was initialized
        if tracer_obj:
            tracer_obj.close()
            if verbose:
                click.echo(click.style("✓ Trace file closed.", **DIM_STYLE))
        if exporter_obj:
            exporter_obj.close()
            if verbose:
                click.echo(click.style("✓ Neo4j connection closed.", **DIM_STYLE))


@cli.command()
@click.option(
    "--run-id", help='Specific run ID to render (e.g., "pipeline-20250903-214419-ec5359")'
)
@click.option("--latest", is_flag=True, help="Use the most recent run directory")
@click.option(
    "--source-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default="snapshots",
    help="Directory containing snapshot runs (default: snapshots)",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True),
    default="viewer-output",
    help="Directory to write HTML files (default: viewer-output)",
)
@click.option("--title", help="Custom title for the HTML page")
@click.option(
    "--include", help='Include only specific matrices (comma-separated list, e.g., "A,C,F")'
)
@click.option(
    "--style",
    type=click.Choice(["tables", "elements"], case_sensitive=False),
    default="tables",
    help="Display style: tables (default) or elements",
)
@click.option(
    "--no-sanitize-values",
    is_flag=True,
    help="Disable default value sanitization for Elements style (keeps prefixes like VALIDATION[...], COL[...], etc.)",
)
@click.option(
    "--open",
    "open_browser",
    is_flag=True,
    help="Open the generated HTML file in the default web browser",
)
def render_viewer(
    run_id: Optional[str],
    latest: bool,
    source_dir: str,
    output_dir: str,
    title: Optional[str],
    include: Optional[str],
    style: str,
    no_sanitize_values: bool,
    open_browser: bool,
):
    """
    Generate a static HTML viewer from matrix snapshot files.

    \b
    Examples:
        chirality render-viewer --latest --open
        chirality render-viewer --latest --style elements --open
        chirality render-viewer --latest --style elements --no-sanitize-values --open
        chirality render-viewer --run-id "pipeline-20250903-214419-ec5359" --style tables
        chirality render-viewer --latest --include "A,C,F" --title "Core Matrices"
    """
    try:
        # Convert paths to Path objects
        snapshots_dir = Path(source_dir)
        output_path = Path(output_dir)

        # Directory handling: check if snapshots directory exists
        if not snapshots_dir.exists():
            click.echo(
                click.style(
                    f"Error: Snapshots directory '{snapshots_dir}' not found. "
                    f"Generate snapshots first using 'compute-pipeline --snapshot-jsonl'.",
                    **ERROR_STYLE,
                )
            )
            sys.exit(1)

        # Run selection logic
        target_run_id = None
        if run_id and latest:
            click.echo(
                click.style("Error: Cannot specify both --run-id and --latest", **ERROR_STYLE)
            )
            sys.exit(1)
        elif run_id:
            # Validate specified run ID exists
            run_dir = snapshots_dir / run_id
            if not run_dir.exists():
                click.echo(
                    click.style(
                        f"Error: Run directory '{run_id}' not found in {snapshots_dir}",
                        **ERROR_STYLE,
                    )
                )
                sys.exit(1)
            target_run_id = run_id
        elif latest:
            # Find latest run
            target_run_id = get_latest_run_dir(snapshots_dir)
            if not target_run_id:
                click.echo(
                    click.style(
                        f"Error: No run directories found in {snapshots_dir}", **ERROR_STYLE
                    )
                )
                sys.exit(1)
        else:
            click.echo(
                click.style("Error: Must specify either --run-id or --latest", **ERROR_STYLE)
            )
            sys.exit(1)

        # Print selected run_id for user confirmation
        click.echo(click.style(f"Using run ID: {target_run_id}", **INFO_STYLE))

        # Matrix selection
        include_matrices = None
        if include:
            requested_matrices = [m.strip().upper() for m in include.split(",")]
            # Validate matrix names
            for matrix_name in requested_matrices:
                if matrix_name not in CANONICAL_ORDER:
                    click.echo(
                        click.style(
                            f"Error: Invalid matrix '{matrix_name}'. Valid matrices: {', '.join(CANONICAL_ORDER)}",
                            **ERROR_STYLE,
                        )
                    )
                    sys.exit(1)
            include_matrices = requested_matrices

        # Load snapshot data
        run_dir = snapshots_dir / target_run_id
        snapshot_data_by_matrix = load_snapshots_for_run(run_dir, include_matrices)

        if not snapshot_data_by_matrix:
            click.echo(
                click.style(f"Error: No valid snapshot files found in {run_dir}", **ERROR_STYLE)
            )
            sys.exit(1)

        click.echo(f"Loaded {len(snapshot_data_by_matrix)} matrix snapshots")

        # Generate HTML page based on style
        if style.lower() == "elements":
            # For Elements style, sanitization is default unless disabled
            sanitize = not no_sanitize_values
            html_content = render_elements_page(
                snapshot_data_by_matrix, target_run_id, title, sanitize
            )
        else:
            html_content = render_page(snapshot_data_by_matrix, target_run_id, title)

        # Write assets atomically
        html_file_path = write_assets(html_content, output_path)

        click.echo()
        click.echo(click.style("Matrix Viewer Generated Successfully", **SUCCESS_STYLE))
        click.echo(click.style("-" * 40, **DIM_STYLE))
        click.echo(f"  HTML file: {html_file_path}")
        click.echo(f"  Matrices: {', '.join(sorted(snapshot_data_by_matrix.keys()))}")

        # Open in browser if requested
        if open_browser:
            try:
                webbrowser.open(f"file://{html_file_path.absolute()}")
                click.echo(click.style("✓ Opened in default web browser", **SUCCESS_STYLE))
            except Exception as e:
                click.echo(click.style(f"Warning: Could not open browser: {e}", **INFO_STYLE))

    except Exception as e:
        click.echo(click.style(f"Error: {e}", **ERROR_STYLE))
        import traceback

        traceback.print_exc()
        sys.exit(1)


@cli.command()
def info():
    """
    Display information about the Chirality Framework semantic calculator.
    """
    click.echo(click.style("Chirality Framework - Semantic Calculator", **STAGE_STYLE))
    click.echo(click.style("=" * 50, **DIM_STYLE))
    click.echo()
    click.echo(f"Version: {_get_version()}")
    click.echo("Algorithm: 3-stage semantic interpretation pipeline")
    click.echo()
    click.echo(click.style("Canonical Matrices:", **INFO_STYLE))
    # Matrix A
    click.echo("  A: 3×4 (Axioms / Problem Statement)")
    click.echo(f"    Station: {MATRIX_A.station}")
    click.echo(f"    Rows:   {', '.join(MATRIX_A.row_labels)}")
    click.echo(f"    Columns:{' ' if MATRIX_A.col_labels else ''}{', '.join(MATRIX_A.col_labels)}")
    # Matrix B
    click.echo("  B: 4×4 (Bridge / Decision Basis)")
    click.echo(f"    Station: {MATRIX_B.station}")
    click.echo(f"    Rows:   {', '.join(MATRIX_B.row_labels)}")
    click.echo(f"    Columns:{' ' if MATRIX_B.col_labels else ''}{', '.join(MATRIX_B.col_labels)}")
    # Matrix J
    click.echo("  J: 3×4 (Judgment / Verification)")
    click.echo(f"    Station: {MATRIX_J.station}")
    click.echo(f"    Rows:   {', '.join(MATRIX_J.row_labels)}")
    click.echo(f"    Columns:{' ' if MATRIX_J.col_labels else ''}{', '.join(MATRIX_J.col_labels)}")
    click.echo()
    click.echo(click.style("Result Matrices:", **INFO_STYLE))
    click.echo("  C = A * B: Problem Requirements (3×4)")
    click.echo("  F = J ⊙ C: Solution Objectives (3×4)")
    click.echo("  D = synthesis(A, F): Solution Objectives (3×4)")
    click.echo("  K = D^T: Pre-Verification Transform (4×3)")
    click.echo("  X = K * J: Verification (4×4)")
    click.echo("  Z = shift(X): Validation (4×4)")
    click.echo("  G = Z[0:3,:]: Evaluation Input (3×4)")
    click.echo("  T = (B[0:3,:])^T: Evaluation Criteria (4×3)")
    click.echo("  P = Z[3,:]: Evaluation Context (1×4)")
    click.echo("  E = G * T: Evaluation (3×3)")
    # Explicit axes for derived matrices (without computing them)
    # F axes mirror J's rows × J's columns
    click.echo("    F Axes:")
    click.echo("      Station: Solution Objectives")
    click.echo(f"      Rows:   {', '.join(MATRIX_J.row_labels)}")
    click.echo(
        f"      Columns:{' ' if MATRIX_J.col_labels else ''}{', '.join(MATRIX_J.col_labels)}"
    )
    # D axes mirror A's rows × A's columns (station is Objectives)
    click.echo("    D Axes:")
    click.echo("      Station: Solution Objectives")
    click.echo(f"      Rows:   {', '.join(MATRIX_A.row_labels)}")
    click.echo(
        f"      Columns:{' ' if MATRIX_A.col_labels else ''}{', '.join(MATRIX_A.col_labels)}"
    )
    # K axes are transposed D
    click.echo("    K Axes:")
    click.echo("      Station: Pre-Verification Transform")
    click.echo(f"      Rows:   {', '.join(MATRIX_A.col_labels)}")  # Transposed from D columns
    click.echo(
        f"      Columns:{' ' if MATRIX_A.row_labels else ''}{', '.join(MATRIX_A.row_labels)}"
    )  # Transposed from D rows
    # X axes are K rows × J columns
    click.echo("    X Axes:")
    click.echo("      Station: Verification")
    click.echo(f"      Rows:   {', '.join(MATRIX_A.col_labels)}")  # K row labels
    click.echo(
        f"      Columns:{' ' if MATRIX_J.col_labels else ''}{', '.join(MATRIX_J.col_labels)}"
    )  # J column labels
    # Z axes mirror X (station shift preserves dimensions)
    click.echo("    Z Axes:")
    click.echo("      Station: Validation")
    click.echo(f"      Rows:   {', '.join(MATRIX_A.col_labels)}")  # Same as X
    click.echo(
        f"      Columns:{' ' if MATRIX_J.col_labels else ''}{', '.join(MATRIX_J.col_labels)}"
    )  # Same as X
    # G axes are first 3 rows of Z
    click.echo("    G Axes:")
    click.echo("      Station: Evaluation Input")
    click.echo(f"      Rows:   {', '.join(MATRIX_A.col_labels[:3])}")  # First 3 from Z
    click.echo(
        f"      Columns:{' ' if MATRIX_J.col_labels else ''}{', '.join(MATRIX_J.col_labels)}"
    )  # Same as Z
    # T axes are transposed first 3 rows of B
    click.echo("    T Axes:")
    click.echo("      Station: Evaluation Criteria")
    click.echo(f"      Rows:   {', '.join(MATRIX_B.col_labels)}")  # B columns become T rows
    click.echo(
        f"      Columns:{' ' if MATRIX_B.row_labels[:3] else ''}{', '.join(MATRIX_B.row_labels[:3])}"
    )  # First 3 B rows become T columns
    # P axes are fourth row of Z as 1x4
    click.echo("    P Axes:")
    click.echo("      Station: Evaluation Context")
    click.echo(f"      Rows:   {MATRIX_A.col_labels[3]}")  # Fourth label from Z
    click.echo(
        f"      Columns:{' ' if MATRIX_J.col_labels else ''}{', '.join(MATRIX_J.col_labels)}"
    )  # Same as Z
    # E axes are G rows × T columns
    click.echo("    E Axes:")
    click.echo("      Station: Evaluation")
    click.echo(
        f"      Rows:   {', '.join(MATRIX_A.col_labels[:3])}"
    )  # G row labels (first 3 from Z)
    click.echo(
        f"      Columns:{' ' if MATRIX_B.row_labels[:3] else ''}{', '.join(MATRIX_B.row_labels[:3])}"
    )  # T column labels
    click.echo()
    click.echo(click.style("3-Stage Pipeline:", **INFO_STYLE))
    click.echo("  Stage 1: Combinatorial (mechanical k-products)")
    click.echo("  Stage 2: Semantic (LLM pair resolution)")
    click.echo("  Stage 3: Lensing (ontological interpretation)")
    click.echo()
    click.echo("Use 'chirality compute-cell --help' for debugging individual cells")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    cli()
