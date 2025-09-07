"""
Strategies for Chirality Framework Prompt Assembly

Defines the canonical order of asset IDs for each stage, driven by the
component being produced/used. Components map deterministically to the
appropriate station brief for combined lensing. This keeps callers simple:
they pass a component_id ('C','D','F','X','Z','E') and the strategy selects
the correct station brief asset internally.
"""

from typing import List, Optional


class PromptStrategy:
    """
    Canonical strategy for prompt assembly.

    Maps stages and components to the correct sequence of asset IDs
    according to the fixed pipeline definitions. For combined lensing,
    the component_id determines which station brief is used; callers do
    not pass a station identifier directly.
    """

    # Component to station brief mapping
    STATION_MAPPING = {
        "C": "station_brief.requirements",
        "D": "station_brief.objectives",
        "F": "station_brief.objectives",
        "X": "station_brief.verification",
        "Z": "station_brief.validation",
        "E": "station_brief.evaluation",
    }

    # Component to Stage 2 operator mapping
    STAGE2_OPERATOR_MAPPING = {
        "C": "stage2_multiply",
        "D": None,  # Mechanical only, no LLM
        "F": "stage2_elementwise",
        "X": "stage2_multiply",
        "Z": None,  # No stage 2, shift in combined lensing
        "E": "stage2_multiply",
    }

    @classmethod
    def plan(cls, stage: str, component_id: str) -> List[str]:
        """
        Get the ordered list of asset IDs for a given stage and component.

        Args:
            stage: One of 'stage2_multiply', 'stage2_elementwise', 'stage2_add',
                   'combined_lens', 'shift'
            component_id: Matrix component ('C', 'D', 'F', 'X', 'Z', 'E')

        Returns:
            List of asset IDs in order for prompt assembly

        Raises:
            ValueError: For invalid stage/component combinations
        """
        if component_id not in cls.STATION_MAPPING:
            raise ValueError(f"Invalid component_id: {component_id}")

        # Stage 2 operations
        if stage == "stage2_multiply":
            if cls.STAGE2_OPERATOR_MAPPING.get(component_id) != "stage2_multiply":
                raise ValueError(f"Component {component_id} does not use multiply operator")
            return ["stage2_multiply"]

        elif stage == "stage2_elementwise":
            if cls.STAGE2_OPERATOR_MAPPING.get(component_id) != "stage2_elementwise":
                raise ValueError(f"Component {component_id} does not use elementwise operator")
            return ["stage2_elementwise"]

        elif stage == "stage2_add":
            # Mechanical operation, returns empty list (no LLM messages needed)
            if cls.STAGE2_OPERATOR_MAPPING.get(component_id) is not None:
                raise ValueError(f"Component {component_id} should not use LLM for add operation")
            return []  # Mechanical, no messages

        # Combined lensing
        elif stage == "combined_lens":
            if component_id == "Z":
                # Z uses station shift instead of combined lensing
                raise ValueError("Component Z should use 'shift' stage, not combined_lens")
            else:
                # Standard combined lensing
                return ["combined_lens"]

        # Standalone shift (for Z matrix)
        elif stage == "shift":
            if component_id != "Z":
                raise ValueError(f"Shift operation only valid for component Z, got {component_id}")
            return ["lens_shift_z"]

        else:
            raise ValueError(f"Invalid stage: {stage}")

    @classmethod
    def get_station_brief_id(cls, component_id: str) -> str:
        """Get the station brief asset ID for a component."""
        if component_id not in cls.STATION_MAPPING:
            raise ValueError(f"Invalid component_id: {component_id}")
        return cls.STATION_MAPPING[component_id]

    @classmethod
    def get_stage2_operator(cls, component_id: str) -> Optional[str]:
        """
        Get the Stage 2 operator for a component.

        Returns:
            Operator asset ID or None for mechanical operations
        """
        if component_id not in cls.STAGE2_OPERATOR_MAPPING:
            raise ValueError(f"Invalid component_id: {component_id}")
        return cls.STAGE2_OPERATOR_MAPPING[component_id]

    @classmethod
    def is_mechanical_stage2(cls, component_id: str) -> bool:
        """Check if component uses mechanical (non-LLM) Stage 2."""
        return cls.get_stage2_operator(component_id) is None

    @classmethod
    def get_pipeline_stages(cls, component_id: str) -> List[str]:
        """
        Get the complete pipeline stages for a component.

        Returns:
            List of stage names in execution order
        """
        if component_id not in cls.STATION_MAPPING:
            raise ValueError(f"Invalid component_id: {component_id}")

        stages = []

        # Stage 1 is always mechanical (not included in LLM pipeline)

        # Stage 2
        operator = cls.get_stage2_operator(component_id)
        if operator == "stage2_multiply":
            stages.append("stage2_multiply")
        elif operator == "stage2_elementwise":
            stages.append("stage2_elementwise")
        elif operator is None and component_id == "D":
            stages.append("stage2_add")  # Mechanical addition
        # Z and other None operators have no stage 2

        # Stage 3 (Combined lensing or shift)
        if component_id == "Z":
            stages.append("shift")
        else:
            stages.append("combined_lens")

        return stages

    @classmethod
    def get_station_meta(cls, component_id: str) -> dict:
        """
        Get station metadata for a component.

        Args:
            component_id: Matrix component ('C', 'D', 'F', 'X', 'Z', 'E')

        Returns:
            Dict with station metadata: {name, ordinal, total}
        """
        station_names = {
            "C": "Requirements",
            "D": "Objectives",
            "F": "Objectives",
            "X": "Verification",
            "Z": "Validation",
            "E": "Evaluation",
        }

        station_ordinals = {
            "C": 2,
            "D": 3,
            "F": 3,
            "X": 4,
            "Z": 5,
            "E": 6,
        }

        if component_id not in station_names:
            raise ValueError(f"Invalid component_id: {component_id}")

        return {
            "name": station_names[component_id],
            "ordinal": station_ordinals[component_id],
            "total": 11,  # Total stations in semantic valley
        }


# Convenience functions for external use
def plan_stage(stage: str, component_id: str) -> List[str]:
    """Get asset IDs for a stage. Convenience wrapper."""
    return PromptStrategy.plan(stage, component_id)


def get_station_brief(component_id: str) -> str:
    """Get station brief asset ID for a component."""
    return PromptStrategy.get_station_brief_id(component_id)


def get_pipeline(component_id: str) -> List[str]:
    """Get complete pipeline stages for a component."""
    return PromptStrategy.get_pipeline_stages(component_id)
