"""
Prompt Builder for Chirality Framework

Assembles prompts from maintainer-authored assets with placeholder substitution.
Enforces the principle that only explicitly present placeholders are substituted.
"""

import re
from typing import Dict, Any, Optional, Literal

# Type alias for message compatibility
Message = Dict[str, str]
from .prompt_registry import get_registry, PromptRegistry  # noqa: E402
from .strategies import PromptStrategy  # noqa: E402


class PromptBuilder:
    """
    Assembles prompts from maintainer-authored assets.

    Substitutes only placeholders explicitly present in assets.
    No implicit context injection beyond what maintainer includes.
    """

    def __init__(self, registry: Optional[PromptRegistry] = None):
        """
        Initialize builder with prompt registry.

        Args:
            registry: PromptRegistry instance. Uses global if None.
        """
        self.registry = registry or get_registry()

    def build_stage2_multiply_messages(self, terms: list[str]) -> list[Message]:
        """
        Build messages for Stage 2 semantic multiplication.

        Args:
            terms: List of terms for multiplication (typically 2 items)

        Returns:
            List of message dicts for LLM API
        """
        # Stage-2 multiply uses the same assets regardless of component. We
        # request the canonical multiply assets via strategy; the component is
        # irrelevant here.
        asset_ids = PromptStrategy.plan("stage2_multiply", "C")
        import json

        return self._build_messages(
            asset_ids, {"raw_products": json.dumps(terms), "component_id": "C"}
        )

    def build_stage2_elementwise_messages(self, terms: list[str]) -> list[Message]:
        """
        Build messages for Stage 2 element-wise multiplication.

        Args:
            terms: List of terms for element-wise operation

        Returns:
            List of message dicts for LLM API
        """
        # Stage-2 elementwise uses the same assets regardless of component.
        asset_ids = PromptStrategy.plan("stage2_elementwise", "F")
        return self._build_messages(asset_ids, {"terms": terms})

    def build_stage2_addition(self, parts: list[str]) -> str:
        """
        Build mechanical sentence for Stage 2 addition (Matrix D).

        This is mechanical string construction, not LLM messages.

        Args:
            parts: List of parts to concatenate

        Returns:
            Constructed sentence string
        """
        # For Matrix D: A(i,j) + " applied to frame the problem; " + F(i,j) + " to resolve the problem."
        if len(parts) != 2:
            raise ValueError(f"Stage 2 addition expects 2 parts, got {len(parts)}")

        return f"{parts[0]} applied to frame the problem; {parts[1]} to resolve the problem."

    def build_combined_lens_messages(
        self,
        component_id: Literal["C", "D", "E", "F", "X", "Z"],
        row_label: str,
        col_label: str,
        content: str,
    ) -> list[Message]:
        """
        Build messages for combined lensing (row × col × station).

        Args:
            component_id: Matrix component ('C', 'D', 'F', 'X', 'Z', 'E').
                          Used to select the correct station brief internally.
            row_label: Row ontology name
            col_label: Column ontology name
            content: Stage 2 content to interpret

        Returns:
            List of message dicts for LLM API
        """
        if component_id == "Z":
            asset_ids = PromptStrategy.plan("shift", component_id)
        else:
            asset_ids = PromptStrategy.plan("combined_lens", component_id)

        # Get station brief content for inlining
        station_brief_id = PromptStrategy.get_station_brief_id(component_id)
        station_brief_text = self.registry.get_text(station_brief_id)

        # Get station metadata for station_id
        station_meta = PromptStrategy.get_station_meta(component_id)
        station_id = station_meta["name"]

        context = {
            "row_label": row_label,
            "col_label": col_label,
            "content": content,
            "station_brief": station_brief_text,
            "station_id": station_id,
        }

        return self._build_messages(asset_ids, context)

    def _build_messages(self, asset_ids: list[str], context: Dict[str, Any]) -> list[Message]:
        """
        Build messages from asset IDs with placeholder substitution.
        System prompt is prepended to all LLM calls.

        Args:
            asset_ids: List of asset IDs to assemble
            context: Context variables for placeholder substitution

        Returns:
            List of message dicts with 'role' and 'content'
        """
        if not asset_ids:
            return []

        messages = []

        # Always prepend system prompt to all Stage 2/3 calls
        system_asset = self.registry.get("system")
        system_content = self._substitute_placeholders(system_asset.text, context)
        messages.append({"role": "user", "content": system_content.strip()})

        for i, asset_id in enumerate(asset_ids):
            asset = self.registry.get(asset_id)
            content = self._substitute_placeholders(asset.text, context)

            # All messages are user role
            role = "user"
            messages.append({"role": role, "content": content.strip()})

        return messages

    def _substitute_placeholders(self, text: str, context: Dict[str, Any]) -> str:
        """
        Substitute placeholders in text using context.

        Only substitutes placeholders that are explicitly present in the text.
        Uses {{placeholder}} format.

        Args:
            text: Text with potential placeholders
            context: Variables for substitution

        Returns:
            Text with placeholders substituted
        """
        # Find all placeholders in text
        placeholder_pattern = r"\{\{(\w+)\}\}"
        placeholders = re.findall(placeholder_pattern, text)

        result = text
        for placeholder in placeholders:
            if placeholder in context:
                value = context[placeholder]
                # Handle different value types
                if isinstance(value, list):
                    # Convert list to JSON array string for {{terms}}
                    import json

                    value_str = json.dumps(value)
                else:
                    value_str = str(value)

                # Replace placeholder
                pattern = f"\\{{\\{{{re.escape(placeholder)}\\}}\\}}"
                result = re.sub(pattern, value_str, result)

        return result

    def get_asset_provenance(self, asset_ids: list[str]) -> list[Dict[str, str]]:
        """
        Get provenance information for a list of assets.

        Args:
            asset_ids: List of asset IDs used in prompt building

        Returns:
            List of provenance dicts with id, sha256, version
        """
        return [self.registry.get_provenance(asset_id) for asset_id in asset_ids]


# Convenience functions for external use
def build_multiply_messages(terms: list[str]) -> list[Message]:
    """Build Stage 2 multiply messages. Convenience wrapper."""
    builder = PromptBuilder()
    return builder.build_stage2_multiply_messages(terms)


def build_elementwise_messages(terms: list[str]) -> list[Message]:
    """Build Stage 2 elementwise messages. Convenience wrapper."""
    builder = PromptBuilder()
    return builder.build_stage2_elementwise_messages(terms)


def build_addition_sentence(parts: list[str]) -> str:
    """Build Stage 2 addition sentence. Convenience wrapper."""
    builder = PromptBuilder()
    return builder.build_stage2_addition(parts)


def build_combined_lens_messages(
    component_id: Literal["C", "D", "E", "F", "X", "Z"],
    row_label: str,
    col_label: str,
    content: str,
) -> list[Message]:
    """Build combined lensing messages. Convenience wrapper."""
    builder = PromptBuilder()
    return builder.build_combined_lens_messages(component_id, row_label, col_label, content)
