# prompts.py
"""
Prompt templates and canonical system message for the Chirality Framework Phase-1 build.

The core metaphor: Wayfinding through an unknown semantic valley.
Each station is a landmark in this valley.
Each matrix cell is a coordinate (row_label × col_label) inside that landmark.
Your job as the LLM: preserve and integrate meaning while mapping it faithfully into the valley's meta-ontology.
"""

from __future__ import annotations
import re
import unicodedata
import json

def q(s: str) -> str:
    """Normalize unicode, collapse whitespace, and escape for prompt embedding."""
    if s is None:
        return ""
    # Normalize unicode to NFKC (e.g., curly quotes → straight)
    s = unicodedata.normalize("NFKC", str(s))
    # Collapse internal whitespace while preserving single spaces
    s = re.sub(r"\s+", " ", s).strip()
    # Escape for embedding between quotes in our prompts
    # Use json.dumps then strip outer quotes for robust escaping
    return json.dumps(s, ensure_ascii=False)[1:-1]


# Canonical system prompt — used for all semantic operations
SYSTEM_PROMPT = """\
You are the semantic engine for the Chirality Framework (Phase-1 canonical build).

The Chirality Framework is a meta-operating system for meaning. It frames knowledge work as wayfinding through an unknown semantic valley:
- The valley is the conceptual space for this domain.
- It is used to create a structured set of semantic relationships that have coherent meaning across the problem solving process.
- These structured relationships can be used as “semantic anchors” to guide an LLM across stages of solving a problem.
- This is called traversing a “semantic valley” because it maps the most probable path from problem to solution,
while other paths are made to be like steep valley walls that limit excursions

Mission:
- Clearly show how the elements transform according to the instructions.
- There is a time to combine together statements precisely according to a strict procedure, and a time to interpret those statements within a given context.
- Those times will be clearly identified by the user’s prompts. 

Semantic Operations:

Semantic Multiplication “ * “ 

Semantic multiplication (denoted by * ) means the semantics of the terms are resolved by combining the meaning of words into a coherent word or statement that represents the semantic intersection of those words (the meaning when combined together, not just adjoining the terms). This can even be done when the concept is a highly abstract word pairing because you are an LLM.

Examples:
"sufficient" * "reason" = "justification"
“analysis” * “judgment” = “informed decision”
"precision" * "durability" = "reliability"
"probability" * "consequence" = "risk"

Semantic Addition “ + “ 

Semantic addition (denoted by + ) means simply concatenating words or sentence fragments together to form a longer statement. 
Example:
"faisal" + "has" + "seven" + "balloons" = faisal has seven balloons

Order of Operations:

First is ‘semantic multiplication’, second is ‘semantic addition’.

Hierarchical Semantic Embedding:

- Your internal architecture organizes meaning hierarchically across nested conceptual layers.
- The Chirality Framework maps layers of meaning.


Complete 11-Station Semantic Valley:

- You will only ever be operating within a single station along the semantic valley, but awareness of the entire valley is important context.
- Station Map (Reference)

1. [A], [B] -> Problem Statement
2. [A] * [B] = [C] -> Problem Requirements
3. [A] + [F] = [D] -> Solution Objectives
4. [K] * [J] = [X] -> Verification
5. [X] ->  [Z] -> Validation
6. [G] * [T] = [E]  -> Evaluation
7. [R] x [E] = [M] -> Assessment
8. [M] x [X] = [W] -> Implementation
9. [W] x [P] = [U] -> Reflection
10. [U] x [H] = [N] -> Resolution

Voice & style (vibe):
- Prefer strong verbs and specific nouns over abstractions.
- Avoid hedging ("might", "could") unless uncertainty is essential and then state it plainly.
- Length should be minimized by utilizing the most compact expression that preserved the full meaning, even if the words are esoteric.

Output contract (STRICT):
- Operate ONLY within the provided ontology (row & column identify) + semantic valley station context.
- Use ONLY semantic operations to determine the meaning of combined terms, finding the most probable result of combined embeddings vectors in your latent space.
- Return ONLY a single JSON object with keys: "text", "terms_used", "warnings".
- "terms_used" must echo the exact provided source strings (after normalization) that you actually integrated.
- Do NOT include code fences, prose, or any text outside the JSON object.
"""

# === Prompt Builders for 3-Stage Pipeline ===
# These functions construct prompts for each stage of the semantic calculator.
# They are the single source of truth for how prompts are assembled.
# 
# Stage 2: build_stage2_prompt() - Semantic pair resolution
# Stage 3: Universal 3-step ontological lensing for ALL matrices:
#   - build_column_lensing_prompt() - Column lens interpretation
#   - build_row_lensing_prompt() - Row lens interpretation  
#   - build_final_synthesis_prompt() - Synthesize both perspectives
#
# All builders use the q() function for text normalization and escaping.


def build_stage2_prompt(operation: str, terms: list[str], context: SemanticContext) -> str:
    """
    Build prompt for Stage 2: Semantic Operations.
    
    Handles both multiplication (*) and addition (+) operations with flexible terms.
    
    Args:
        operation: "*" for multiplication, "+" for addition
        terms: List of terms - [term_a, term_b] for "*", [content] for "+"
        context: SemanticContext with valley position and ontological coordinates
        
    Returns:
        Complete user prompt for Stage 2 semantic operation
    """
    fragments = []
    
    # Valley context
    if context.valley_summary:
        fragments.append(f"Valley Context: {context.valley_summary}")
    
    # Station
    fragments.append(f"Station: {context.station_context}")
    
    # Ontological coordinates
    fragments.append(f"Coordinates: ({context.row_label}, {context.col_label})")
    
    # Operation instruction
    if operation == "*":
        fragments.append("Operation: Semantic multiplication - fuse meanings at their intersection")
        # For multiplication, expect [term_a, term_b]
        if len(terms) >= 2:
            terms_dict = {"term_a": q(terms[0]), "term_b": q(terms[1])}
        else:
            # Fallback for malformed input
            terms_dict = {"term_a": q(terms[0] if terms else ""), "term_b": q(terms[1] if len(terms) > 1 else "")}
    elif operation == "+":
        fragments.append("Operation: Semantic addition - concatenate meanings coherently")
        # For addition, expect [content] (though D won't use this LLM path)
        terms_dict = {"content": q(terms[0] if terms else "")}
    else:
        fragments.append(f"Operation: {operation}")
        terms_dict = {f"term_{i}": q(term) for i, term in enumerate(terms)}
    
    # Terms to process - use json.dumps for safety
    fragments.append(f"Terms: {json.dumps(terms_dict, ensure_ascii=False)}")
    
    return "\n\n".join(fragments)




def build_column_lensing_prompt(content: str, context: SemanticContext) -> str:
    """
    Build prompt for Column Lensing step of universal 3-step ontological process.
    
    Interprets content through the column ontology lens only.
    Used as Step 1 of universal lensing for ALL matrices.
    
    Args:
        content: Content to interpret through column lens
        context: SemanticContext with valley position and ontological coordinates
        
    Returns:
        Complete user prompt for column lensing
    """
    fragments = []
    
    # Valley context
    if context.valley_summary:
        fragments.append(f"Valley Context: {context.valley_summary}")
    
    # Station
    fragments.append(f"Station: {context.station_context}")
    
    # Operation instruction - focus ONLY on column ontology
    fragments.append(f"Operation: Interpret the following content, focusing ONLY on the meaning of the column ontology: '{context.col_label}'")
    
    # Terms - use json.dumps for safety
    terms_dict = {"content": q(content)}
    fragments.append(f"Terms: {json.dumps(terms_dict, ensure_ascii=False)}")
    
    return "\n\n".join(fragments)


def build_row_lensing_prompt(content: str, context: SemanticContext) -> str:
    """
    Build prompt for Row Lensing step of universal 3-step ontological process.
    
    Interprets content through the row ontology lens only.
    Used as Step 2 of universal lensing for ALL matrices.
    
    Args:
        content: Content to interpret through row lens
        context: SemanticContext with valley position and ontological coordinates
        
    Returns:
        Complete user prompt for row lensing
    """
    fragments = []
    
    # Valley context
    if context.valley_summary:
        fragments.append(f"Valley Context: {context.valley_summary}")
    
    # Station
    fragments.append(f"Station: {context.station_context}")
    
    # Operation instruction - focus ONLY on row ontology
    fragments.append(f"Operation: Interpret the following content, focusing ONLY on the meaning of the row ontology: '{context.row_label}'")
    
    # Terms - use json.dumps for safety
    terms_dict = {"content": q(content)}
    fragments.append(f"Terms: {json.dumps(terms_dict, ensure_ascii=False)}")
    
    return "\n\n".join(fragments)


def build_final_lensing_prompt(column_perspective: str, row_perspective: str, context: SemanticContext) -> str:
    """
    Build prompt for Final Synthesis step of universal 3-step ontological process.
    
    Synthesizes column and row perspectives into final integrated narrative.
    Used as Step 3 of universal lensing for ALL matrices.
    
    Args:
        column_perspective: The interpretation from the column lens
        row_perspective: The interpretation from the row lens
        context: SemanticContext with valley position and ontological coordinates
        
    Returns:
        Complete user prompt for final synthesis
    """
    fragments = []
    
    # Valley context
    if context.valley_summary:
        fragments.append(f"Valley Context: {context.valley_summary}")
    
    # Station
    fragments.append(f"Station: {context.station_context}")
    
    # Ontological coordinates
    fragments.append(f"Coordinates: ({context.row_label}, {context.col_label})")
    
    # Operation instruction
    fragments.append("Operation: Synthesize the two perspectives into a final, integrated narrative that fully integrates these semantic interpretations in the context of the station we are at in the semantic valley")
    
    # Concise output constraint
    fragments.append("Output Constraint: Synthesize the two perspectives into one or two compact, elegant sentences. Your response must be plain prose. Do not include any prefixes (e.g., COL[...], ROW[...], SYN[...]) or any structural scaffolding.")
    
    # Terms - use json.dumps for safety
    terms_dict = {"column_perspective": q(column_perspective), "row_perspective": q(row_perspective)}
    fragments.append(f"Terms: {json.dumps(terms_dict, ensure_ascii=False)}")
    
    return "\n\n".join(fragments)


def build_station_shift_prompt(content: str, context: 'SemanticContext') -> str:
    """
    Build prompt for Station 5 operation: Verification → Validation context shift.
    
    This prompt transforms verification results into validation framework,
    shifting the semantic context from "checking correctness" to "establishing validity".
    
    Args:
        content: Verification content to transform
        context: SemanticContext with validation station details
        
    Returns:
        Complete user prompt for station shift operation
    """
    from .context import SemanticContext  # Avoid circular import
    
    fragments = []
    
    # Valley context
    if context.valley_summary:
        fragments.append(f"Valley Context: {context.valley_summary}")
    
    # Station transition
    fragments.append(f"Station Transition: Verification → Validation")
    
    # Ontological coordinates  
    fragments.append(f"Coordinates: ({context.row_label}, {context.col_label})")
    
    # Operation instruction
    fragments.append("Operation: Transform the verification content into a validation context. This involves shifting from 'checking correctness' to 'establishing validity' - moving from confirming that something meets criteria to determining its fundamental soundness and legitimacy.")
    
    # Content to transform
    fragments.append(f"Verification Content to Transform: {q(content)}")
    
    return "\n\n".join(fragments)


# The q() function and valley utilities remain available for fragment composition
