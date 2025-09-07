"""
Neo4j Exporter for Chirality Framework "Working Memory" - Universal 5-Stage Pipeline.

This module exports the complete semantic journey of each cell computation to a Neo4j
graph database using a universal schema that preserves both type distinctions (via labels)
and instance distinctions (via unique IDs) across all matrices (C, F, D).

Key Design Principles:
- Single atomic transaction per cell export
- Universal 5-stage provenance schema for all matrices
- Rich metadata preservation (modelId, latencyMs, promptHash, terms_used, warnings)
- Self-contained stage nodes with full context
- Idempotent exports via deterministic stage_ids
"""

import os
import logging
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from ..core.types import Cell

try:
    from neo4j import GraphDatabase, Driver
except ImportError:
    GraphDatabase = None
    Driver = None


class Neo4jWorkingMemoryExporter:
    """
    Universal Neo4j exporter for the 5-stage semantic pipeline.

    Exports all matrices (C, F, D) using the same universal schema:
    - (:Matrix)-[:CONTAINS]->(:Cell)
    - (:Cell)-[:HAS_STAGE {order}]->(:Stage)
    - Stage nodes have specific labels: :Construct, :Semantic, :ColumnLensed, :RowLensed, :FinalSynthesis

    Preserves full metadata and context per stage for rich analytics.
    """

    def __init__(
        self,
        uri: str = None,
        user: str = None,
        password: str = None,
        run_id: Optional[str] = None,
        run_tag: Optional[str] = None,
        run_user: Optional[str] = None,
        run_git_sha: Optional[str] = None,
        run_model: Optional[str] = None,
        started_at: Optional[str] = None,
    ):
        if GraphDatabase is None:
            raise ImportError("The 'neo4j' package is required. Install with: pip install neo4j")

        uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = user or os.getenv("NEO4J_USER", "neo4j")
        password = password or os.getenv("NEO4J_PASSWORD", "password")

        self.driver: Driver = GraphDatabase.driver(uri, auth=(user, password))
        self.logger = logging.getLogger(__name__)
        self._ensure_schema()
        # Initialize run/session context (for graph scoping and lifecycle)
        self.run: Dict[str, Any] = {
            "id": run_id or os.getenv("CHIRALITY_RUN_ID") or self._default_run_id(),
            "tag": run_tag or os.getenv("CHIRALITY_RUN_TAG"),
            "user": run_user or os.getenv("CHIRALITY_RUN_USER"),
            "gitSha": run_git_sha or os.getenv("CHIRALITY_RUN_GIT_SHA"),
            "model": run_model or os.getenv("CHIRALITY_RUN_MODEL"),
            "startedAt": started_at or datetime.now(timezone.utc).isoformat(),
        }

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures driver is closed."""
        self.close()
        return False

    def _ensure_schema(self):
        """
        Ensures necessary constraints and indexes are created in the database.

        Creates:
        - Unique constraints on Matrix.name, Cell.id, Stage.stage_id
        - Index on Stage.timestamp for temporal queries
        """
        try:
            with self.driver.session() as session:
                # Unique constraints for data integrity
                session.run(
                    "CREATE CONSTRAINT IF NOT EXISTS FOR (m:Matrix) REQUIRE m.name IS UNIQUE"
                )
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Cell) REQUIRE c.id IS UNIQUE")
                session.run(
                    "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Stage) REQUIRE s.stage_id IS UNIQUE"
                )

                # Performance indexes
                session.run("CREATE INDEX IF NOT EXISTS FOR (s:Stage) ON (s.timestamp)")

                self.logger.info("Neo4j schema constraints and indexes ensured")
        except Exception as e:
            self.logger.warning(f"Failed to create Neo4j schema: {e}")

    def export_cell_computation(self, cell: Cell, context: Dict[str, Any]):
        """
        Exports the complete 5-stage semantic journey for a single cell.

        Creates a comprehensive graph representation:
        - Matrix node with station and valley context
        - Cell node with coordinates and final result
        - 5 Stage nodes with rich metadata and specific labels
        - Proper relationships with sequence order

        Uses single atomic transaction with UNWIND for efficiency.

        Args:
            cell: Computed cell with rich provenance
            context: Dict with matrix position and ontological coordinates
        """
        try:
            # Build parameters for the universal export
            matrix_params = self._build_matrix_params(context)
            cell_params = self._build_cell_params(cell, context)
            stage_params = self._build_stage_params(cell, context)
            run_params = self._build_run_params()

            with self.driver.session() as session:
                # Single atomic transaction exports everything
                session.run(
                    self._get_export_cypher(),
                    run=run_params,
                    matrix=matrix_params,
                    cell=cell_params,
                    stages=stage_params,
                )

            self.logger.debug(
                f"Exported cell {context.matrix}[{cell.row},{cell.col}] with {len(stage_params)} stages"
            )

        except Exception as e:
            cell_id = f"{context.matrix}-{cell.row}-{cell.col}"
            self.logger.error(f"Failed to export cell {cell_id} to Neo4j: {e}")
            # Don't re-raise - export failure shouldn't break computation

    def _build_matrix_params(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build matrix node parameters from context."""
        return {
            "name": context["matrix"],
            "station": context["station_context"],
            "valley_summary": context["valley_summary"],
        }

    def _build_cell_params(self, cell: Cell, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build cell node parameters from cell and context."""
        return {
            "id": f"{context['matrix']}-{cell.row}-{cell.col}",
            "row": cell.row,
            "col": cell.col,
            "value": cell.value,
            "row_label": context["row_label"],
            "col_label": context["col_label"],
            "operation": cell.provenance.get("operation"),
            "coordinates": cell.provenance.get("coordinates"),
            "sources": cell.provenance.get("sources", []),
            "timestamp": cell.provenance.get("timestamp"),
        }

    def _build_run_params(self) -> Dict[str, Any]:
        """Build run/session parameters for Run node."""
        return {
            "id": self.run.get("id"),
            "tag": self.run.get("tag"),
            "user": self.run.get("user"),
            "gitSha": self.run.get("gitSha"),
            "model": self.run.get("model"),
            "startedAt": self.run.get("startedAt"),
        }

    def _build_stage_params(self, cell: Cell, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Build stage parameters from the universal 5-stage provenance schema.

        Each stage gets:
        - Unique stage_id for instance distinction
        - Rich metadata from resolver (modelId, latencyMs, promptHash, etc.)
        - Stage-specific payload data
        - Full context for self-contained analytics

        Returns list of 5 stage parameter dictionaries.
        """
        provenance = cell.provenance
        cell_id = f"{context.matrix}-{cell.row}-{cell.col}"
        base_timestamp = datetime.now(timezone.utc).isoformat()

        stages = []
        stage_definitions = [
            ("Construct", 1, "stage_1_construct"),
            ("Semantic", 2, "stage_2_semantic"),
            ("ColumnLensed", 3, "stage_3_column_lensed"),
            ("RowLensed", 4, "stage_4_row_lensed"),
            ("FinalSynthesis", 5, "stage_5_final_synthesis"),
        ]

        for kind, order, prov_key in stage_definitions:
            stage_data = provenance.get(prov_key, {})
            # Strict: no backward compatibility — require dict with text/texts
            if not isinstance(stage_data, dict):
                raise ValueError(
                    f"Provenance for {prov_key} must be a dict; got {type(stage_data).__name__}"
                )
            text = stage_data.get("text")
            texts = stage_data.get("texts")
            metadata = stage_data.get("metadata", {}) or {}
            terms_used = stage_data.get("terms_used", [])
            warnings = stage_data.get("warnings", [])

            # Generate unique stage_id for instance distinction
            stage_timestamp = f"{base_timestamp}-{order:02d}"
            stage_id = self._generate_stage_id(cell_id, kind, order, stage_timestamp)

            # Build stage parameters with full context
            stage_params = {
                "stage_id": stage_id,
                "kind": kind,
                "order": order,
                "timestamp": stage_timestamp,
                # Content (text or texts for list stages like stage_1_construct)
                "text": text,
                "texts": texts,
                "terms_used": terms_used,
                "warnings": warnings,
                # Resolver metadata (when available)
                "modelId": metadata.get("modelId"),
                "latencyMs": metadata.get("latencyMs"),
                "promptHash": metadata.get("promptHash"),
                "createdAt": metadata.get("createdAt"),
                "phase": self._get_phase_for_stage(kind),
                # Context duplication for self-contained stage nodes
                "station": context.station_context,
                "valley_summary": context.valley_summary,
                "row_label": context.row_label,
                "col_label": context.col_label,
                # Stage-specific payload
                "payload": self._build_stage_payload(kind, stage_data, context.matrix),
            }

            stages.append(stage_params)

        return stages

    def _generate_stage_id(self, cell_id: str, kind: str, order: int, timestamp: str) -> str:
        """
        Generate deterministic unique stage_id for instance distinction.

        Format: <cell_id>-<order>-<kind>-<hash>
        Hash includes timestamp to ensure uniqueness across runs.
        """
        content = f"{self.run.get('id')}|{cell_id}-{order}-{kind}-{timestamp}"
        hash_suffix = hashlib.sha256(content.encode()).hexdigest()[:8]
        return f"{cell_id}-{order}-{kind}-{hash_suffix}"

    def _get_phase_for_stage(self, kind: str) -> str:
        """Map stage kind to resolver phase name."""
        phase_map = {
            "Construct": "construct",
            "Semantic": "semantic",
            "ColumnLensed": "interpret_col",
            "RowLensed": "interpret_row",
            "FinalSynthesis": "synthesize_final",
        }
        return phase_map.get(kind, "unknown")

    def _build_stage_payload(self, kind: str, stage_data: Any, matrix: str) -> Dict[str, Any]:
        """
        Build stage-specific payload for richer analytics.

        Different stages store different contextual information:
        - Construct: products/element_pair/synthesis_statement
        - Others: minimal payload
        """
        payload = {}

        if kind == "Construct":
            # Strict: stage_data is a dict with text/texts
            text = stage_data.get("text")
            texts = stage_data.get("texts")

            if matrix == "C" and isinstance(texts, list):
                payload["products"] = texts
            elif matrix == "X" and isinstance(texts, list):
                payload["products"] = texts
            elif matrix == "E" and isinstance(texts, list):
                payload["products"] = texts
            elif matrix == "F" and isinstance(text, str):
                payload["element_pair"] = text
            elif matrix == "D" and isinstance(text, str):
                payload["construction_formula"] = text

        return payload

    def _get_export_cypher(self) -> str:
        """
        Returns the universal export Cypher query.

        Single atomic transaction that:
        1. Merges Matrix and Cell nodes with full properties
        2. Uses UNWIND to create all 5 Stage nodes with dynamic labeling
        3. Creates relationships with proper sequencing

        Idempotent via MERGE on unique IDs.
        """
        return """
        // 0) Upsert Run and set metadata
        MERGE (r:Run {id: $run.id})
        SET
            r.startedAt = coalesce(r.startedAt, $run.startedAt),
            r.tag       = $run.tag,
            r.user      = $run.user,
            r.gitSha    = $run.gitSha,
            r.model     = $run.model

        // 1) Upsert Matrix and Cell and link them
        MERGE (m:Matrix {name: $matrix.name})
        SET 
            m.station = $matrix.station,
            m.valley_summary = $matrix.valley_summary

        MERGE (c:Cell {id: $cell.id})
        SET 
            c.row = $cell.row,
            c.col = $cell.col,
            c.value = $cell.value,
            c.row_label = $cell.row_label,
            c.col_label = $cell.col_label,
            c.operation = $cell.operation,
            c.coordinates = $cell.coordinates,
            c.sources = $cell.sources,
            c.timestamp = $cell.timestamp

        MERGE (m)-[:CONTAINS]->(c)
        MERGE (r)-[:CONTAINS]->(c)

        // 2) Create the 5 stage nodes and link them (idempotent via stage_id)
        UNWIND $stages AS stage
        MERGE (s:Stage {stage_id: stage.stage_id})
        SET 
            s.kind = stage.kind,
            s.order = stage.order,
            s.timestamp = stage.timestamp,
            
            // Universal per-stage content
            s.text = stage.text,
            s.texts = stage.texts,
            s.terms_used = stage.terms_used,
            s.warnings = stage.warnings,
            
            // Resolver metadata (when available)
            s.modelId = stage.modelId,
            s.latencyMs = stage.latencyMs,
            s.promptHash = stage.promptHash,
            s.createdAt = stage.createdAt,
            s.phase = stage.phase,
            
            // Context for self-contained stage nodes
            s.station = stage.station,
            s.valley_summary = stage.valley_summary,
            s.row_label = stage.row_label,
            s.col_label = stage.col_label
            
        // Add stage-specific payload (merged into node properties)
        SET s += coalesce(stage.payload, {})

        // Add sub-type labels dynamically (preserves type distinctions)
        FOREACH (_ IN CASE WHEN stage.kind = 'Construct' THEN [1] ELSE [] END |
            SET s:Construct)
        FOREACH (_ IN CASE WHEN stage.kind = 'Semantic' THEN [1] ELSE [] END |
            SET s:Semantic)
        FOREACH (_ IN CASE WHEN stage.kind = 'ColumnLensed' THEN [1] ELSE [] END |
            SET s:ColumnLensed)
        FOREACH (_ IN CASE WHEN stage.kind = 'RowLensed' THEN [1] ELSE [] END |
            SET s:RowLensed)
        FOREACH (_ IN CASE WHEN stage.kind = 'FinalSynthesis' THEN [1] ELSE [] END |
            SET s:FinalSynthesis)

        // Connect stage to cell with explicit order (preserves sequence)
        MERGE (c)-[:HAS_STAGE {order: stage.order}]->(s)
        MERGE (r)-[:CONTAINS]->(s)
        """

    def close(self):
        """Closes the database connection."""
        try:
            if self.driver:
                self.driver.close()
                self.driver = None
                self.logger.debug("Neo4j connection closed")
        except Exception as e:
            self.logger.error(f"Error closing Neo4j driver: {e}")

    def __del__(self):
        """Cleanup on garbage collection."""
        self.close()

    def _default_run_id(self) -> str:
        """Generate a default run id when not provided."""
        return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
