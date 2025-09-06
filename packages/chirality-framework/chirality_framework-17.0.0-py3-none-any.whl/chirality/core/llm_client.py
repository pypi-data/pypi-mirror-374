"""
OpenAI Responses API Client for Chirality Framework

Single wrapper for OpenAI Responses API calls.
Enforces JSON output format and global configuration.
"""

import os
import time
from typing import Dict, Any, List, Tuple, Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .llm_config import get_config


class LLMClient:
    """
    Wrapper for OpenAI Responses API.

    Enforces use of Responses API (not Chat Completions) and JSON output format.
    Uses global configuration from llm_config.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize client.

        Args:
            api_key: OpenAI API key. Uses OPENAI_API_KEY env var if None.
        """
        if OpenAI is None:
            raise ImportError("OpenAI package required. Install with: pip install openai")

        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required")

        self.client = OpenAI(api_key=api_key)

    def call_responses(
        self, messages: List[Dict[str, str]]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Call OpenAI Responses API with messages.

        CRITICAL: Uses Responses API, not Chat Completions API.

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            Tuple of (response_dict, metadata_dict)

        Raises:
            ValueError: If response is not valid JSON
            Exception: For API errors
        """
        config = get_config()

        # Convert messages to single prompt for Responses API
        prompt = self._messages_to_prompt(messages)

        start_time = time.time()

        try:
            # CRITICAL: Use responses.create, NOT chat.completions.create
            response = self.client.responses.create(
                model=config.model,
                prompt=prompt,
                temperature=config.temperature,
                top_p=config.top_p,
                max_tokens=config.max_tokens,
                seed=config.seed,
                response_format=config.response_format,
            )

            # Extract response text
            response_text = response.choices[0].text or ""

            # Parse JSON response
            import json

            try:
                response_dict = json.loads(response_text)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON response: {e}\\nResponse: {response_text}")

            # Build metadata
            latency_ms = int((time.time() - start_time) * 1000)
            metadata = {
                "model": response.model,
                "latency_ms": latency_ms,
                "usage": getattr(response, "usage", None),
                "created_at": int(time.time()),
                "response_format": "json_object",
            }

            return response_dict, metadata

        except Exception as e:
            # Add timing info to error metadata
            latency_ms = int((time.time() - start_time) * 1000)
            {
                "error": str(e),
                "latency_ms": latency_ms,
                "created_at": int(time.time()),
            }
            raise Exception(f"LLM API call failed: {e}") from e

    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        Convert messages format to single prompt for Responses API.

        Args:
            messages: List of message dicts

        Returns:
            Combined prompt string
        """
        prompt_parts = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                # System message goes first, no prefix
                prompt_parts.append(content)
            elif role == "user":
                # User message with separator
                if prompt_parts:  # Add separator if not first message
                    prompt_parts.append("\\n\\n")
                prompt_parts.append(content)
            else:
                # Unknown role, treat as user
                if prompt_parts:
                    prompt_parts.append("\\n\\n")
                prompt_parts.append(content)

        return "".join(prompt_parts)


# Global client instance
_client: Optional[LLMClient] = None


def get_client() -> LLMClient:
    """Get global LLM client instance."""
    global _client
    if _client is None:
        _client = LLMClient()
    return _client


def call_responses_api(messages: List[Dict[str, str]]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Convenience function for calling Responses API.

    Args:
        messages: List of message dicts

    Returns:
        Tuple of (response_dict, metadata_dict)
    """
    client = get_client()
    return client.call_responses(messages)
