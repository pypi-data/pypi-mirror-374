"""
Consolidated OpenAI interface for Chirality Framework semantic operations.

This is the ONLY file in the codebase that imports OpenAI.
All semantic operations (multiplication, addition, interpretation) 
go through this centralized resolver with robust error handling,
retry logic, and JSON validation.
"""

import os
import json
import time
import hashlib
import unicodedata
import re
from typing import Dict, Any, List, Optional, Literal, Tuple
from datetime import datetime

try:
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # Defer hard failure until actually instantiated

from .types import Cell, Matrix, RichResult
from .context import SemanticContext
from .prompts import SYSTEM_PROMPT, build_stage2_prompt, build_column_lensing_prompt, build_row_lensing_prompt, build_final_lensing_prompt, build_station_shift_prompt


def normalize_text(s: str) -> str:
    """Normalize unicode and whitespace for consistent processing."""
    if s is None:
        return ""
    s = unicodedata.normalize("NFKC", str(s))
    s = re.sub(r"\s+", " ", s).strip()
    return s



class CellResolver:
    """
    Consolidated OpenAI interface for all Chirality Framework semantic operations.
    
    This is the centralized resolver that handles all LLM calls with:
    - Robust retry logic with exponential backoff
    - JSON validation and error handling  
    - Temperature control per operation type
    - Deterministic prompt hashing
    - Comprehensive error recovery
    
    Prompts are constructed using builders from prompts.py:
    - build_stage2_prompt: For semantic pair resolution
    - build_column_lensing_prompt: For column ontology lens interpretation
    - build_row_lensing_prompt: For row ontology lens interpretation  
    - build_final_lensing_prompt: For synthesizing both perspectives
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4.1-nano", seed: int = 42):
        if OpenAI is None:
            raise ImportError("OpenAI package required. Install with: pip install openai")

        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.seed = seed
        
        # Temperature settings for different operations (consolidated from ops.py)
        self.temperatures = {
            "multiply": 0.7,  # Creative intersection for semantic multiplication
            "add": 0.5,       # Tighter integration for semantic addition
            "interpret": 0.5, # Clear explanation for interpretation
            "*": 0.7,         # Alias for multiply
            "+": 0.5,         # Alias for add
            "⊙": 0.7          # Element-wise multiplication
        }
        
        # Retry configuration (from OpenAIResolver)
        self.max_retries = 3
        self.base_delay = 0.4
        
        # Default system frame for fragment composition (from prompts.py)
        self.default_system_frame = SYSTEM_PROMPT
    

    def resolve_semantic_pair(self, pair: str, context: SemanticContext) -> RichResult:
        """
        Stage 2: Use fragment composition for semantic multiplication.
        
        Takes a word pair like 'Values * Necessary' and resolves it to a concept
        like 'Essential Values' using the full SemanticContext for guidance.
        """
        system_prompt = context.system_frame or self.default_system_frame

        # Split pair into terms for the new builder signature
        if " * " in pair:
            term_a, term_b = pair.split(" * ", 1)
            terms = [term_a, term_b]
        else:
            terms = [pair]
        
        user_prompt = build_stage2_prompt("*", terms, context)

        response, metadata = self._call_openai(system_prompt, user_prompt, "multiply")
        return RichResult(
            text=response.get("text", ""),
            terms_used=response.get("terms_used", []),
            warnings=response.get("warnings", []),
            metadata=metadata
        )

    def apply_column_lens(self, content: str, context: SemanticContext) -> RichResult:
        """
        Universal Lensing Step 1: Apply column ontology lens to content.
        
        Used by all matrices (C, F, D, future) as first step of ontological lensing.
        """
        system_prompt = context.system_frame or self.default_system_frame
        user_prompt = build_column_lensing_prompt(content, context)
        response, metadata = self._call_openai(system_prompt, user_prompt, "interpret_col")
        return RichResult(
            text=response.get("text", ""),
            terms_used=response.get("terms_used", []),
            warnings=response.get("warnings", []),
            metadata=metadata
        )

    def apply_row_lens(self, content: str, context: SemanticContext) -> RichResult:
        """
        Universal Lensing Step 2: Apply row ontology lens to content.
        
        Used by all matrices (C, F, D, future) as second step of ontological lensing.
        """
        system_prompt = context.system_frame or self.default_system_frame
        user_prompt = build_row_lensing_prompt(content, context)
        response, metadata = self._call_openai(system_prompt, user_prompt, "interpret_row")
        return RichResult(
            text=response.get("text", ""),
            terms_used=response.get("terms_used", []),
            warnings=response.get("warnings", []),
            metadata=metadata
        )

    def synthesize_lensed_perspectives(self, column_perspective: str, row_perspective: str, context: SemanticContext) -> RichResult:
        """
        Universal Lensing Step 3: Synthesize column and row perspectives into final narrative.
        
        Used by all matrices (C, F, D, future) as final step of ontological lensing.
        """
        system_prompt = context.system_frame or self.default_system_frame
        user_prompt = build_final_lensing_prompt(column_perspective, row_perspective, context)
        response, metadata = self._call_openai(system_prompt, user_prompt, "synthesize_final")
        return RichResult(
            text=response.get("text", ""),
            terms_used=response.get("terms_used", []),
            warnings=response.get("warnings", []),
            metadata=metadata
        )

    def shift_station_context(self, content: str, context: SemanticContext) -> RichResult:
        """
        Station 5 operation: Transform verification results into validation context.
        
        This operation shifts from Verification (X matrix) to Validation (Z matrix)
        by recontextualizing the verification results within a validation framework.
        
        Args:
            content: The verification content to transform
            context: SemanticContext with validation station context
            
        Returns:
            RichResult with validation-contextualized content
        """
        system_prompt = context.system_frame or self.default_system_frame
        user_prompt = build_station_shift_prompt(content, context)
        response, metadata = self._call_openai(system_prompt, user_prompt, "validation_shift")
        return RichResult(
            text=response.get("text", ""),
            terms_used=response.get("terms_used", []),
            warnings=response.get("warnings", []),
            metadata=metadata
        )

    def _call_openai(self, system_prompt: str, user_prompt: str, operation: str = "semantic") -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Consolidated OpenAI call with robust error handling.
        
        Combines the best patterns from ops.py OpenAIResolver:
        - Exponential backoff retry logic
        - JSON extraction and validation
        - Prompt hashing for audit trails
        - Comprehensive error recovery
        
        Returns:
            Tuple of (parsed_response, metadata)
        """
        temperature = self.temperatures.get(operation, 0.5)
        prompt_hash_val = self._prompt_hash(system_prompt, user_prompt)
        
        attempt = 0
        last_err: Optional[Exception] = None
        t0 = time.time()

        while attempt <= self.max_retries:
            try:
                # Use the OpenAI Chat Completions API
                resp = self.client.chat.completions.create(
                    model=self.model,
                    temperature=temperature,
                    top_p=0,
                    seed=self.seed,
                    max_tokens=200,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )

                # Extract and validate JSON content from Chat Completions response
                raw = resp.choices[0].message.content or ""

                raw = raw or ""
                js = self._extract_json(raw)
                obj = json.loads(js)
                self._validate_obj(obj)

                # Calculate metadata
                dt = int((time.time() - t0) * 1000)
                model_id = resp.model
                meta = {
                    "modelId": model_id,
                    "latencyMs": dt,
                    "promptHash": prompt_hash_val,
                    "systemVersion": self._system_version_hash(),
                    "rawLen": len(raw),
                    "attempts": attempt + 1,
                    "temperature": temperature,
                    "maxTokens": 200,
                    "createdAt": self._now_iso(),
                    "phase": operation,
                }

                return obj, meta

            except Exception as e:
                last_err = e
                if attempt >= self.max_retries:
                    break
                    
                # Exponential backoff (from ops.py)
                wait_time = self.base_delay * (2 ** attempt)
                time.sleep(wait_time)
                attempt += 1

        # All retries exhausted - return error response
        error_response = {
            "text": f"ERROR: Failed to process {operation}",
            "terms_used": [],
            "warnings": [f"openai_failure: {last_err}"]
        }
        error_meta = {
            "modelId": self.model,
            "latencyMs": 0,
            "promptHash": prompt_hash_val,
            "error": str(last_err),
            "operation": operation,
            "createdAt": self._now_iso(),
            "attempts": attempt + 1,
            "phase": "error"
        }
        return error_response, error_meta
    
    # Consolidated helper methods from ops.py OpenAIResolver
    
    def _prompt_hash(self, system: str, user: str) -> str:
        """Generate deterministic hash for system + user prompt combination."""
        h = hashlib.sha256()
        h.update(normalize_text(system).encode("utf-8"))
        h.update(b"\n\n")
        h.update(normalize_text(user).encode("utf-8"))
        return h.hexdigest()

    def _system_version_hash(self) -> str:
        """Hash of current system prompt for versioning."""
        return hashlib.sha256(normalize_text(SYSTEM_PROMPT).encode("utf-8")).hexdigest()

    def _now_iso(self) -> str:
        """Generate ISO-8601 timestamp for graph compatibility."""
        return datetime.utcnow().isoformat(timespec="seconds") + "Z"

    def _extract_json(self, text: str) -> str:
        """Extract JSON object from model output, handling stray prose."""
        if not text:
            raise ValueError("Empty model output")
        
        # Find the first '{' and last '}' to guard against stray prose
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("No JSON object found in model output")
        
        return text[start:end+1]

    def _validate_obj(self, obj: Dict[str, Any]) -> None:
        """Validate that object conforms to expected framework schema."""
        if not isinstance(obj, dict):
            raise ValueError("Output must be a JSON object")
        
        # Check required keys
        if "text" not in obj or "terms_used" not in obj or "warnings" not in obj:
            raise ValueError("Missing required keys (text, terms_used, warnings)")
        
        # Type validation
        if not isinstance(obj["text"], str):
            raise ValueError("'text' must be string")
        
        # Ensure terms_used is a list - convert if needed
        if "terms_used" not in obj:
            obj["terms_used"] = []
        elif not isinstance(obj["terms_used"], list):
            # Convert single item or other format to list
            if isinstance(obj["terms_used"], str):
                obj["terms_used"] = [obj["terms_used"]]
            else:
                obj["terms_used"] = []
        # Ensure all items are strings
        obj["terms_used"] = [str(item) for item in obj["terms_used"]]
        
        # Ensure warnings is a list - convert if needed
        if "warnings" not in obj:
            obj["warnings"] = []
        elif not isinstance(obj["warnings"], list):
            if isinstance(obj["warnings"], str):
                obj["warnings"] = [obj["warnings"]]
            else:
                obj["warnings"] = []
        # Ensure all items are strings  
        obj["warnings"] = [str(item) for item in obj["warnings"]]
