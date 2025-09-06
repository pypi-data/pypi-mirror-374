"""
Clean resolvers for Chirality Framework with new prompt system architecture.

Contains only the essential EchoResolver for testing purposes.
All production semantic resolution goes through the CellResolver.
"""

from typing import List
from .types import RichResult


class EchoResolver:
    """
    Deterministic, zero-LLM resolver for testing.

    Returns predictable outputs that match the new CellResolver interface.
    Perfect for testing the prompt system architecture without LLM calls.
    """

    def run_stage2_multiply(self, terms: List[str], component_id: str = "C") -> RichResult:
        """
        Mock Stage 2 semantic multiplication.

        Args:
            terms: List of terms for multiplication (typically 2 items)
            component_id: Matrix component for strategy selection

        Returns:
            RichResult with mock multiplication result
        """
        if len(terms) >= 2:
            # Reverse order as deterministic mock behavior
            text = f"{terms[1]} × {terms[0]}"
            used_terms = terms[:2]
        else:
            text = f"MULTIPLY({', '.join(terms)})"
            used_terms = terms

        return RichResult(
            text=text,
            terms_used=used_terms,
            warnings=[],
            metadata={
                "resolver": "echo",
                "operation": "stage2_multiply",
                "component": component_id,
            },
        )

    def run_stage2_elementwise(self, terms: List[str], component_id: str = "F") -> RichResult:
        """
        Mock Stage 2 element-wise multiplication.

        Args:
            terms: List of terms for element-wise operation
            component_id: Matrix component for strategy selection

        Returns:
            RichResult with mock element-wise result
        """
        if len(terms) >= 2:
            text = f"{terms[0]} ⊙ {terms[1]}"
            used_terms = terms[:2]
        else:
            text = f"ELEMENTWISE({', '.join(terms)})"
            used_terms = terms

        return RichResult(
            text=text,
            terms_used=used_terms,
            warnings=[],
            metadata={
                "resolver": "echo",
                "operation": "stage2_elementwise",
                "component": component_id,
            },
        )

    def run_stage2_addition(self, parts: List[str], component_id: str = "D") -> str:
        """
        Mock Stage 2 mechanical addition (Matrix D).

        This is mechanical string construction, no LLM call.

        Args:
            parts: List of parts to concatenate
            component_id: Matrix component (should be 'D')

        Returns:
            Constructed sentence string
        """
        if len(parts) == 2:
            return f"{parts[0]} applied to frame the problem; {parts[1]} to resolve the problem."
        else:
            return f"ADDITION({' + '.join(parts)})"

    def run_combined_lens(
        self, content: str, component_id: str, row_label: str, col_label: str
    ) -> RichResult:
        """
        Mock combined ontological lensing (row × col × station).

        This replaces the old three-step lensing process with a single
        unified semantic operation.

        Args:
            content: Stage 2 content to interpret
            component_id: Matrix component ('C', 'D', 'F', 'X', 'Z', 'E')
            row_label: Row ontology name
            col_label: Column ontology name

        Returns:
            RichResult with mock combined lensing result
        """
        # Map components to stations for mock output
        station_map = {
            "C": "Requirements",
            "D": "Objectives",
            "F": "Objectives",
            "X": "Verification",
            "Z": "Validation",
            "E": "Evaluation",
        }

        station = station_map.get(component_id, "Unknown")

        # Generate deterministic mock combined lensing output
        text = f"[{station}] {row_label} × {col_label}: {content}"

        return RichResult(
            text=text,
            terms_used=[content],
            warnings=[],
            metadata={
                "resolver": "echo",
                "operation": "combined_lens",
                "component": component_id,
                "station": station,
                "row_label": row_label,
                "col_label": col_label,
            },
        )

    def run_shift(self, content: str, component_id: str = "Z") -> RichResult:
        """
        Mock station context shift (Verification → Validation).

        Used for Matrix Z transformation.

        Args:
            content: Verification content to transform
            component_id: Matrix component (should be 'Z')

        Returns:
            RichResult with mock shifted content
        """
        if component_id != "Z":
            raise ValueError(f"Shift operation only valid for component Z, got {component_id}")

        # Mock shift from verification to validation context
        text = f"VALIDATION_SHIFT: {content}"

        return RichResult(
            text=text,
            terms_used=[content],
            warnings=[],
            metadata={"resolver": "echo", "operation": "shift", "component": component_id},
        )
