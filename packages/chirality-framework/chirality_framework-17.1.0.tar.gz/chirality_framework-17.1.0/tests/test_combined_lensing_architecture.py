"""
Essential tests for Combined Lensing Architecture

Tests the core functionality that matters:
1. Prompt assets load correctly
2. Combined lensing replaces 3-step lensing
3. New API methods work
4. Pipeline efficiency (fewer LLM calls)
"""

import pytest
from unittest.mock import patch
from chirality.lib.prompt_registry import PromptRegistry
from chirality.lib.strategies import PromptStrategy
from chirality.core.cell_resolver import CellResolver
from chirality.core.types import RichResult


class TestPromptSystemCore:
    """Test that the prompt system loads and works."""

    def test_prompt_assets_load(self):
        """Test that we can load all required prompt assets."""
        registry = PromptRegistry()
        registry.load()

        # Should have our core assets
        assert "stage2_multiply" in registry._assets
        assert "combined_lens" in registry._assets
        assert "lens_shift_z" in registry._assets

        # Should have station briefs
        assert "station_brief.requirements" in registry._assets
        assert "station_brief.evaluation" in registry._assets

    def test_strategy_planning(self):
        """Test that strategy planning returns correct assets."""

        # Stage 2 multiply should return single asset
        assets = PromptStrategy.plan("stage2_multiply", "C")
        assert assets == ["stage2_multiply"]

        # Combined lens should return single asset
        assets = PromptStrategy.plan("combined_lens", "C")
        assert assets == ["combined_lens"]

        # Z should use shift
        assets = PromptStrategy.plan("shift", "Z")
        assert assets == ["lens_shift_z"]


class TestCombinedLensingAPI:
    """Test that the new resolver API works."""

    def test_stage2_multiply_method_exists(self):
        """Test that run_stage2_multiply method exists and is callable."""
        resolver = CellResolver()

        # Should have the method
        assert hasattr(resolver, "run_stage2_multiply")
        assert callable(resolver.run_stage2_multiply)

    def test_combined_lens_method_exists(self):
        """Test that run_combined_lens method exists and is callable."""
        resolver = CellResolver()

        # Should have the method
        assert hasattr(resolver, "run_combined_lens")
        assert callable(resolver.run_combined_lens)

    def test_shift_method_exists(self):
        """Test that run_shift method exists and is callable."""
        resolver = CellResolver()

        # Should have the method
        assert hasattr(resolver, "run_shift")
        assert callable(resolver.run_shift)


class TestArchitectureEfficiency:
    """Test that the new architecture is more efficient."""

    def test_combined_lensing_single_call(self):
        """Test that combined lensing makes only one LLM call instead of three."""
        resolver = CellResolver()

        # Mock the LLM call
        with patch("chirality.core.cell_resolver.call_responses_api") as mock_api:
            mock_api.return_value = (
                {"text": "test result", "terms_used": ["test"], "warnings": []},
                {"total_tokens": 100},
            )

            result = resolver.run_combined_lens(
                content="test content", component_id="C", row_label="normative", col_label="guiding"
            )

            # Should make exactly 1 API call (not 3 like old architecture)
            assert mock_api.call_count == 1
            assert isinstance(result, RichResult)
            assert result.text == "test result"


class TestPipelineIntegration:
    """Test that the full pipeline works end-to-end."""

    def test_echo_resolver_pipeline(self):
        """Test that echo resolver works with new architecture."""
        from chirality.core.matrices import MATRIX_A, MATRIX_B
        from chirality.core.operations import compute_cell_C
        from chirality.core.resolvers import EchoResolver

        resolver = EchoResolver()
        cell = compute_cell_C(0, 0, MATRIX_A, MATRIX_B, resolver)

        # Should have 3-stage provenance
        assert "stage_1_construct" in cell.provenance
        assert "stage_2_semantic" in cell.provenance
        assert "stage_3_combined_lensed" in cell.provenance

        # Should have meaningful result
        assert cell.value
        assert isinstance(cell.value, str)

    def test_matrix_z_uses_shift(self):
        """Test that Matrix Z uses shift instead of combined lensing."""
        from chirality.core.matrices import MATRIX_A, MATRIX_B, MATRIX_J
        from chirality.core.operations import (
            compute_matrix_C,
            compute_matrix_F,
            compute_matrix_D,
            compute_matrix_K,
            compute_matrix_X,
            compute_cell_Z,
        )
        from chirality.core.resolvers import EchoResolver

        resolver = EchoResolver()

        # Build up to X matrix
        C = compute_matrix_C(MATRIX_A, MATRIX_B, resolver, "test")
        F = compute_matrix_F(MATRIX_J, C, resolver, "test")
        D = compute_matrix_D(MATRIX_A, F, resolver, "test")
        K = compute_matrix_K(D)
        X = compute_matrix_X(K, MATRIX_J, resolver, "test")

        # Test Z cell computation
        z_cell = compute_cell_Z(0, 0, X, resolver, "test")

        # Z should have empty stage_3 (uses shift in stage_2)
        assert z_cell.provenance["stage_3_combined_lensed"] == {}
        assert z_cell.provenance["stage_2_semantic"]["text"]  # Should have shift result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
