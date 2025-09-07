"""
Tests for CLI functionality

This module tests the CLI helper functions and argument processing,
focusing on the resolve_run_settings precedence logic.
"""

import os
import pytest
from unittest.mock import patch

from chirality.cli import resolve_run_settings, setup_resolver


class TestResolveRunSettings:
    """Test the resolve_run_settings argument precedence logic."""

    def test_trace_only_overrides_everything(self):
        """Test that --trace-only flag overrides all other settings."""
        # trace_only should enable trace and disable neo4j_export regardless of other flags
        final_trace, final_neo4j_export = resolve_run_settings(
            trace=False, neo4j_export=True, trace_only=True
        )
        assert final_trace is True
        assert final_neo4j_export is False

        # Should also work when trace=True
        final_trace, final_neo4j_export = resolve_run_settings(
            trace=True, neo4j_export=True, trace_only=True
        )
        assert final_trace is True
        assert final_neo4j_export is False

    def test_environment_variable_precedence(self):
        """Test that CHIRALITY_DISABLE_EXPORT environment variable is respected."""
        with patch.dict(os.environ, {"CHIRALITY_DISABLE_EXPORT": "1"}):
            final_trace, final_neo4j_export = resolve_run_settings(
                trace=False, neo4j_export=True, trace_only=False
            )
            assert final_trace is False  # trace unaffected by env var
            assert final_neo4j_export is False  # neo4j disabled by env var

        # Test other truthy values
        for env_value in ["true", "yes", "on"]:
            with patch.dict(os.environ, {"CHIRALITY_DISABLE_EXPORT": env_value}):
                final_trace, final_neo4j_export = resolve_run_settings(
                    trace=False, neo4j_export=True, trace_only=False
                )
                assert final_trace is False
                assert final_neo4j_export is False

    def test_environment_variable_falsy_values(self):
        """Test that falsy environment variable values don't disable export."""
        for env_value in ["0", "false", "no", "off", ""]:
            with patch.dict(os.environ, {"CHIRALITY_DISABLE_EXPORT": env_value}):
                final_trace, final_neo4j_export = resolve_run_settings(
                    trace=False, neo4j_export=True, trace_only=False
                )
                assert final_trace is False
                assert final_neo4j_export is True  # Should remain enabled

    def test_user_flags_respected_when_no_overrides(self):
        """Test that user flags are respected when no overrides are active."""
        with patch.dict(os.environ, {}, clear=True):  # No environment variables
            # Test all combinations of user flags
            final_trace, final_neo4j_export = resolve_run_settings(
                trace=True, neo4j_export=True, trace_only=False
            )
            assert final_trace is True
            assert final_neo4j_export is True

            final_trace, final_neo4j_export = resolve_run_settings(
                trace=False, neo4j_export=False, trace_only=False
            )
            assert final_trace is False
            assert final_neo4j_export is False

            final_trace, final_neo4j_export = resolve_run_settings(
                trace=True, neo4j_export=False, trace_only=False
            )
            assert final_trace is True
            assert final_neo4j_export is False

    def test_trace_only_precedence_over_environment(self):
        """Test that --trace-only overrides environment variable."""
        with patch.dict(os.environ, {"CHIRALITY_DISABLE_EXPORT": "0"}):  # Should enable export
            final_trace, final_neo4j_export = resolve_run_settings(
                trace=False, neo4j_export=True, trace_only=True
            )
            assert final_trace is True
            assert final_neo4j_export is False  # trace_only overrides env var

    def test_no_environment_variable_set(self):
        """Test behavior when CHIRALITY_DISABLE_EXPORT is not set."""
        with patch.dict(os.environ, {}, clear=True):
            final_trace, final_neo4j_export = resolve_run_settings(
                trace=False, neo4j_export=True, trace_only=False
            )
            assert final_trace is False
            assert final_neo4j_export is True  # Should respect user flag


class TestSetupResolver:
    """Test the setup_resolver function for robust OpenAI handling."""

    def test_echo_resolver_always_succeeds(self):
        """Test that echo resolver always succeeds regardless of dependencies."""
        # Should work with or without API key
        setup_resolver("echo", None, verbose=False)
        setup_resolver("echo", "", verbose=False)
        setup_resolver("echo", "fake-key", verbose=False)
        # If we get here, no SystemExit was raised - success!

    @patch("chirality.cli.OPENAI_AVAILABLE", False)
    def test_openai_resolver_missing_dependencies(self):
        """Test that OpenAI resolver fails gracefully when dependencies missing."""
        with pytest.raises(SystemExit) as excinfo:
            setup_resolver("openai", "sk-test-key", verbose=False)
        assert excinfo.value.code == 1

    @patch("chirality.cli.OPENAI_AVAILABLE", True)
    def test_openai_resolver_missing_api_key(self):
        """Test that OpenAI resolver fails gracefully when API key missing."""
        # Test with None
        with pytest.raises(SystemExit) as excinfo:
            setup_resolver("openai", None, verbose=False)
        assert excinfo.value.code == 1

        # Test with empty string
        with pytest.raises(SystemExit) as excinfo:
            setup_resolver("openai", "", verbose=False)
        assert excinfo.value.code == 1

        # Test with whitespace only
        with pytest.raises(SystemExit) as excinfo:
            setup_resolver("openai", "   ", verbose=False)
        assert excinfo.value.code == 1

    @patch("chirality.cli.OPENAI_AVAILABLE", True)
    def test_openai_resolver_valid_key(self):
        """Test that OpenAI resolver succeeds with valid setup."""
        # Should not raise SystemExit
        setup_resolver("openai", "sk-test-key", verbose=False)
        # If we get here, no SystemExit was raised - success!

    def test_unknown_resolver(self):
        """Test that unknown resolvers are handled gracefully."""
        # Should work for any resolver name (framework handles validation elsewhere)
        setup_resolver("unknown", None, verbose=False)
