"""
Test to ensure we're using the correct OpenAI API.
This test MUST pass or the framework is using the wrong API.
"""

import ast
from pathlib import Path


def test_responses_api_only():
    """Ensure cell_resolver.py uses ONLY the Responses API, never Chat Completions."""

    # Read the cell_resolver.py file
    resolver_path = Path(__file__).parent.parent / "chirality" / "core" / "cell_resolver.py"
    with open(resolver_path, "r") as f:
        source = f.read()

    # Parse the AST
    tree = ast.parse(source)

    # Check for forbidden API calls
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            # Check for chat.completions (FORBIDDEN)
            if (
                hasattr(node, "attr")
                and node.attr == "completions"
                and isinstance(node.value, ast.Attribute)
                and hasattr(node.value, "attr")
                and node.value.attr == "chat"
            ):
                raise AssertionError(
                    f"FORBIDDEN: Found 'chat.completions' in cell_resolver.py at line {node.lineno}. "
                    "Must use 'responses.create()' instead!"
                )

            # Check for responses.create (REQUIRED)
            if hasattr(node, "attr") and node.attr == "responses":
                # This is correct!
                pass

    # Ensure we use our Responses API wrapper
    assert "call_responses_api" in source, (
        "REQUIRED: cell_resolver.py must use 'call_responses_api()' wrapper. "
        "This ensures Responses API compliance."
    )

    print("✓ API Compliance Test Passed: Using Responses API correctly")


if __name__ == "__main__":
    test_responses_api_only()
