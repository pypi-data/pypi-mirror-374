"""
Clean resolvers for Chirality Framework v16.0.0 semantic calculator.

Contains only the essential EchoResolver for testing purposes.
All production semantic resolution goes through the CellResolver.
"""

from .context import SemanticContext
from .types import RichResult


class EchoResolver:
    """
    Deterministic, zero-LLM resolver for testing.
    
    Returns predictable outputs that match the CellResolver interface.
    Perfect for testing the 3-stage pipeline without LLM calls.
    """
    
    def resolve_semantic_pair(self, pair: str, context: SemanticContext) -> RichResult:
        """
        Mock semantic multiplication - reverses the order of terms.
        
        Args:
            pair: String like "term1 * term2"
            context: Full semantic context (ignored in mock)
            
        Returns:
            Reversed terms as mock resolution
        """
        if " * " in pair:
            left, right = pair.split(" * ", 1)
            text = f"{right} {left}"
            terms = [left, right]
        else:
            text = f"Resolved({pair})"
            terms = [pair]
        
        return RichResult(
            text=text,
            terms_used=terms,
            warnings=[],
            metadata={"modelId": "echo_resolver"}
        )
    
    def apply_column_lens(self, content: str, context: SemanticContext) -> RichResult:
        """Mock column lens - adds column label."""
        return RichResult(
            text=f"COL[{context.col_label}]: {content}",
            terms_used=[content],
            warnings=[],
            metadata={"modelId": "echo_resolver"}
        )
    
    def apply_row_lens(self, content: str, context: SemanticContext) -> RichResult:
        """Mock row lens - adds row label."""  
        return RichResult(
            text=f"ROW[{context.row_label}]: {content}",
            terms_used=[content],
            warnings=[],
            metadata={"modelId": "echo_resolver"}
        )
    
    def synthesize_lensed_perspectives(self, column_perspective: str, row_perspective: str, context: SemanticContext) -> RichResult:
        """Mock final synthesis - combines both perspectives."""
        return RichResult(
            text=f"SYN[{column_perspective} | {row_perspective}]",
            terms_used=[column_perspective, row_perspective],
            warnings=[],
            metadata={"modelId": "echo_resolver"}
        )
    
    def shift_station_context(self, content: str, context: SemanticContext) -> RichResult:
        """
        Mock station shift - transforms verification to validation context.
        
        Following colleague_1's guidance for clear Validation-oriented output with coordinates.
        """
        return RichResult(
            text=f"VALIDATION[{context.row_label},{context.col_label}]: {content}",
            terms_used=[content],
            warnings=[],
            metadata={"modelId": "echo_resolver"}
        )