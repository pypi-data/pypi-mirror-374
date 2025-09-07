"""
Canonical CellResolver for Chirality Framework

Refactored to use maintainer-authored prompt assets and combined lensing.
Uses OpenAI Responses API exclusively with global configuration.
"""

import hashlib
from typing import Dict, Any, List, Optional

from .types import RichResult
from .llm_client import call_responses_api
from ..lib.prompt_builder import PromptBuilder
from ..lib.strategies import PromptStrategy


class CellResolver:
    """
    Canonical resolver for all Chirality Framework semantic operations.

    Uses maintainer-authored prompt assets and combined lensing approach.
    Records strong provenance for every LLM call.
    """

    def __init__(self):
        """Initialize resolver with prompt builder."""
        self.builder = PromptBuilder()

    def run_stage2_multiply(self, terms: List[str], component_id: str = "C") -> RichResult:
        """
        Run Stage 2 semantic multiplication.

        Args:
            terms: List of terms for multiplication (typically 2 items)
            component_id: Matrix component for strategy selection

        Returns:
            RichResult with multiplication result and provenance
        """
        # Build messages
        messages = self.builder.build_stage2_multiply_messages(terms)

        # Get asset provenance
        asset_ids = PromptStrategy.plan("stage2_multiply", component_id)
        asset_provenance = self.builder.get_asset_provenance(asset_ids)

        # Call LLM
        response, metadata = self._call_llm(messages, asset_provenance, "stage2_multiply")

        return self._build_rich_result(response, metadata, asset_provenance)

    def run_stage2_elementwise(self, terms: List[str], component_id: str = "F") -> RichResult:
        """
        Run Stage 2 element-wise multiplication.

        Args:
            terms: List of terms for element-wise operation
            component_id: Matrix component for strategy selection

        Returns:
            RichResult with element-wise result and provenance
        """
        # Build messages
        messages = self.builder.build_stage2_elementwise_messages(terms)

        # Get asset provenance
        asset_ids = PromptStrategy.plan("stage2_elementwise", component_id)
        asset_provenance = self.builder.get_asset_provenance(asset_ids)

        # Call LLM
        response, metadata = self._call_llm(messages, asset_provenance, "stage2_elementwise")

        return self._build_rich_result(response, metadata, asset_provenance)

    def run_stage2_addition(self, parts: List[str], component_id: str = "D") -> str:
        """
        Run Stage 2 mechanical addition (Matrix D).

        This is mechanical string construction, no LLM call.

        Args:
            parts: List of parts to concatenate
            component_id: Matrix component (should be 'D')

        Returns:
            Constructed sentence string
        """
        return self.builder.build_stage2_addition(parts)

    def run_combined_lens(
        self, content: str, component_id: str, row_label: str, col_label: str
    ) -> RichResult:
        """
        Run combined ontological lensing (row × col × station).

        This replaces the old three-step lensing process with a single
        unified semantic operation.

        Args:
            content: Stage 2 content to interpret
            component_id: Matrix component ('C', 'D', 'F', 'X', 'Z', 'E').
                           Used to select the proper station brief.
            row_label: Row ontology name
            col_label: Column ontology name

        Returns:
            RichResult with combined lensing result and provenance
        """
        # Build messages
        messages = self.builder.build_combined_lens_messages(
            component_id, row_label, col_label, content
        )

        # Get asset provenance - must include station brief since it gets inlined
        asset_ids = PromptStrategy.plan("combined_lens", component_id)
        station_brief_id = PromptStrategy.get_station_brief_id(component_id)

        # Per colleague_1 spec: record asset IDs and sha256 for both the
        # combined lens template AND the station brief (since it's inlined)
        all_asset_ids = asset_ids + [station_brief_id]
        asset_provenance = self.builder.get_asset_provenance(all_asset_ids)

        # Call LLM
        response, metadata = self._call_llm(messages, asset_provenance, "combined_lens")

        return self._build_rich_result(response, metadata, asset_provenance)

    def run_shift(self, content: str, component_id: str = "Z") -> RichResult:
        """
        Run station context shift (Verification → Validation).

        Used for Matrix Z transformation.

        Args:
            content: Verification content to transform
            component_id: Matrix component (should be 'Z')

        Returns:
            RichResult with shifted content and provenance
        """
        if component_id != "Z":
            raise ValueError(f"Shift operation only valid for component Z, got {component_id}")

        # For Z, shift is embedded in combined lensing
        # This method exists for completeness but typically won't be called separately
        asset_ids = PromptStrategy.plan("shift", component_id)

        # Build simple messages (system + shift operator)
        system_text = self.builder.registry.get_text("system")
        shift_text = self.builder.registry.get_text("lens_shift_z")

        # Substitute content placeholder in shift text
        shift_content = shift_text.replace("{{content}}", content)

        messages = [
            {"role": "system", "content": system_text},
            {"role": "user", "content": shift_content},
        ]

        # Get asset provenance
        asset_provenance = self.builder.get_asset_provenance(asset_ids)

        # Call LLM
        response, metadata = self._call_llm(messages, asset_provenance, "shift")

        return self._build_rich_result(response, metadata, asset_provenance)

    def _call_llm(
        self, messages: List[Dict[str, str]], asset_provenance: List[Dict[str, str]], operation: str
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Call LLM with messages and record provenance.

        Args:
            messages: Messages to send to LLM
            asset_provenance: Asset provenance information
            operation: Operation name for metadata

        Returns:
            Tuple of (response_dict, metadata_dict)
        """
        # Calculate prompt hash for provenance
        prompt_hash = self._hash_messages(messages)

        # Call OpenAI Responses API
        response, api_metadata = call_responses_api(messages)

        # Validate response structure
        self._validate_response(response)

        # Build complete metadata with provenance
        metadata = {
            **api_metadata,
            "operation": operation,
            "prompt_hash": prompt_hash,
            "assets": asset_provenance,
            "strategy": "combined",
            "station": self._infer_station(asset_provenance),
        }

        return response, metadata

    def _build_rich_result(
        self,
        response: Dict[str, Any],
        metadata: Dict[str, Any],
        asset_provenance: List[Dict[str, str]],
    ) -> RichResult:
        """
        Build RichResult from LLM response and metadata.

        Args:
            response: Parsed JSON response from LLM
            metadata: Complete metadata dict
            asset_provenance: Asset provenance information

        Returns:
            RichResult with all data
        """
        return RichResult(
            text=response.get("text", ""),
            terms_used=response.get("terms_used", []),
            warnings=response.get("warnings", []),
            metadata=metadata,
        )

    def _validate_response(self, response: Dict[str, Any]) -> None:
        """
        Validate LLM response structure.

        Args:
            response: Parsed JSON response

        Raises:
            ValueError: If response is invalid
        """
        if not isinstance(response, dict):
            raise ValueError("Response must be a JSON object")

        required_fields = ["text", "terms_used", "warnings"]
        for field in required_fields:
            if field not in response:
                raise ValueError(f"Missing required field: {field}")

        # Validate field types
        if not isinstance(response["text"], str):
            raise ValueError("'text' field must be string")

        if not isinstance(response["terms_used"], list):
            raise ValueError("'terms_used' field must be array")

        if not isinstance(response["warnings"], list):
            raise ValueError("'warnings' field must be array")

    def _hash_messages(self, messages: List[Dict[str, str]]) -> str:
        """Generate deterministic hash of messages for provenance."""
        import json

        messages_str = json.dumps(messages, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(messages_str.encode("utf-8")).hexdigest()

    def _infer_station(self, asset_provenance: List[Dict[str, str]]) -> Optional[str]:
        """Infer station name from asset provenance."""
        for asset in asset_provenance:
            asset_id = asset.get("id", "")
            if asset_id.startswith("station."):
                return asset_id[8:]  # Remove 'station.' prefix
        return None
