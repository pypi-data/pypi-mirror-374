# Changelog

All notable changes to the Chirality Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [17.1.1] - 2025-09-06

### Fixed
-   **Release Workflow Fixes**: Resolved PyPI publishing issues preventing automated releases
    -   Fixed Architecture Tests to use existing test files instead of missing ones
    -   Updated PyPI publishing to use correct 'pypi' environment (not 'release')
    -   Switch to trusted publishing authentication instead of legacy token auth
    -   Aligned with working python-publish.yml workflow configuration
-   **CI Formatting Issues**: Applied Black formatting to all failing files
-   **Prompt Asset Validation**: Fixed CI to check for correct asset name 'lens_shift_z'

## [17.1.0] - 2025-09-06

### Added
-   **Complete Semantic Content Implementation**: All maintainer-authored prompt assets have been populated with canonical semantic content
    -   System prompt with complete framework context, semantic operations, and JSON output contract
    -   Station briefs for Requirements, Objectives, Verification, Validation, and Evaluation stations
    -   Stage 2 operators: multiplication and element-wise semantic operations
    -   Stage 3 lensing: combined lensing and Z-specific shift operations
-   **Enhanced Placeholder Support**: Added `{{station_id}}` placeholder for dynamic station identification in prompts
-   **Path B D-Matrix Implementation**: Hard-coded D formula (`A(i,j) + " applied to frame the problem; " + F(i,j) + " to resolve the problem."`) in operations.py as mechanical operation

### Changed
-   **Prompt Builder Architecture**: Enhanced to prepend system.md to all Stage 2/3 LLM calls for consistent context
-   **Z Matrix Handling**: Implemented dedicated shift lensing template for Validation context transformation
-   **Strategies Module**: Added `get_station_meta()` method for station metadata and updated Z matrix routing to `lens_shift_z` asset
-   **Documentation Consistency**: Updated both AGENTS.md and docs/PROMPT_ENGINEERING.md to include `{{station_id}}` as allowed placeholder
-   **Package Data**: Extended pyproject.toml to include new ops/operators/*.md and ops/lensing/*.md files

### Fixed
-   **OpenAI Responses API Integration**: Fixed critical API compatibility issues
    -   Updated API calls to use `input` parameter instead of `prompt` (Responses API requirement)
    -   Removed unsupported `max_tokens` parameter from API calls
    -   Temporarily removed `response_format` parameter (relying on System Prompt JSON contract)
    -   Implemented robust response parsing with fallback logic for `output_text` and `output[].content[].text`
    -   Added improved JSON error diagnostics with truncated response previews for debugging
    -   Upgraded minimum OpenAI SDK requirement to >=1.50.0
-   **Critical Tracer System**: Fixed semantic journey tracking after SemanticContext removal
    -   Updated tracer to extract matrix information from `extras` dict instead of removed SemanticContext
    -   Fixed all attribute access errors that were breaking semantic diagnostic capabilities
    -   Restored critical artifacts for diagnosing semantic incoherence and drift
-   **Asset Registry**: Updated metadata.yml with correct SHA256 checksums, file sizes, and versions for all prompt assets
-   **Test Compatibility**: Fixed all test expectations to match new asset naming conventions
-   **Environment Configuration**: Removed model and temperature from environment variables, making llm_config.py the single source of truth for LLM parameters

### Technical
-   **Full Semantic Resolution Operational**: OpenAI resolver now successfully processes complete pipeline with authentic semantic transformation
-   All 81 tests passing with new architecture
-   Echo resolver validation successful for all matrices (C, D, F, X, Z, E)  
-   OpenAI resolver validation successful for complete semantic pipeline (C through E)
-   Complete 3-stage provenance structure implemented and validated
-   Asset integrity checking via SHA256 validation functional
-   Semantic tracing system fully operational for coherence diagnostics

## [17.0.0] - 2025-09-05

### Added
-   **Asset-Based Prompt System**: Introduced a new `chirality/prompt_assets/` directory to externalize all semantic content (system prompts, station briefs, operator instructions) into maintainer-authored markdown files.
-   **Prompt Assembly Engine**: Added a new `chirality/lib/` module containing:
    -   `PromptRegistry`: Loads and validates all prompt assets against a `metadata.yml` manifest, checking versions and SHA256 checksums.
    -   `PromptBuilder`: Assembles prompts from assets according to a canonical pipeline.
    -   `Strategies`: Defines the fixed order of asset assembly for each pipeline stage.
-   **Dedicated LLM Client**: Added `llm_client.py` and `llm_config.py` to create a single, exclusive wrapper for the OpenAI Responses API and centralize model configuration.

### Changed
-   **Major Architectural Refactoring**: The core semantic pipeline has been completely rewritten.
    -   Replaced the old 3-step lensing process (column, row, synthesis) with a single, unified **Combined Lensing** call for all interpretations.
    -   The `CellResolver` class was completely refactored with a new, canonical API (`run_stage2_multiply`, `run_combined_lens`, etc.).
    -   All `compute_cell_*` functions in `operations.py` were updated to use the new canonical pipeline.
-   **Semantic Update**: The axiomatic matrices `A`, `B`, and `J` were updated with new canonical definitions.
-   **API Correction**: The OpenAI API client was updated to exclusively use the `Responses` API, as per maintainer directive.
-   **Provenance Schema**: Simplified the provenance structure to reflect the new pipeline, replacing the separate lensing stages with a single `stage_3_combined_lensed` field.

### Removed
-   **`chirality/core/prompts.py`**: This file has been deleted. All prompt content now lives as assets in `chirality/prompt_assets/`.
-   **Old Lensing Logic**: Removed the `_perform_three_step_lensing` helper function and all associated code for the separate column/row/synthesis steps from the codebase.

### BREAKING CHANGES

-   The internal Python API for cell computation (specifically the methods in `CellResolver` and the structure of `operations.py`) has been completely redesigned and is not backward-compatible.
-   The detailed 5-stage provenance structure previously exported is now obsolete and has been replaced by a simpler 3-stage structure. Any tools that consume trace or provenance data will need to be updated.

## [16.2.0] - 2025-09-04

### Fixed
- **OpenAI Integration**: Fixed critical OpenAI API client implementation
  - Corrected `client.responses.create()` to `client.chat.completions.create()`
  - Fixed response parsing to use `resp.choices[0].message.content`
  - Made JSON validation more permissive for `terms_used` and `warnings` fields
  - Restored correct model name "gpt-4.1-nano"
- **Matrix Context Handling**: Simplified Matrix X and E context to use `{"content": combined_concepts}`
- **Prompt Engineering**: Enhanced final synthesis prompt for 1-2 compact sentences without structural scaffolding

### Enhanced
- **Error Handling**: More robust JSON validation that gracefully handles model variations
- **Output Quality**: Eliminated COL[...], ROW[...], SYN[...] prefixes for clean semantic output

## [16.1.0] - 2025-09-03

### Added
- **Station 6 (Evaluation)**: Complete implementation with matrices G, T, P, E:
  - Matrix G: First 3 rows of Z (Evaluation Input, 3×4)
  - Matrix T: Transpose of first 3 rows of B (Evaluation Criteria, 4×3)  
  - Array P: Fourth row of Z as 1×4 (Evaluation Context)
  - Matrix E: G * T semantic multiplication (Evaluation, 3×3)
- **CLI Enhancement**: New `compute-matrix` command for complete matrix computation:
  - Supports all 13 matrices (A, B, J, C, F, D, K, X, Z, G, P, T, E)
  - JSONL snapshot export with atomic writes to `snapshots/<run_id>/`
  - Run ID correlation between traces and snapshots
  - `--trace-only` convenience flag for development debugging
- **Pipeline Computing**: New `compute-pipeline` command for batch matrix computation:
  - Dependency management with smart caching to avoid re-computation
  - `--include-base` flag to include canonical matrices (A, B, J)
  - `--only` flag for selective matrix computation with validation
  - Correlated trace and snapshot outputs with single run ID
- **Matrix Viewer**: New `render-viewer` command for HTML visualization:
  - Elegant static HTML generation from snapshot files
  - Responsive design with navigation and provenance display
  - `--latest` and `--run-id` selection with automatic run discovery
  - `--include` filtering and `--open` browser integration
- **Snapshot Export**: Robust MatrixSnapshotWriter with atomic file operations:
  - Safe atomic writes using temp file + rename pattern
  - Structured JSON export with complete cell data and provenance
  - Run-scoped directory organization for correlation

### Enhanced
- **Trace Settings**: Advanced precedence handling for trace/export flags:
  - `--trace-only` overrides `--neo4j-export` with user feedback
  - `CHIRALITY_DISABLE_EXPORT` environment variable support
  - Proper resource cleanup in try/finally blocks
- **Error Handling**: Comprehensive input validation and helpful error messages
- **Documentation**: Complete examples for all new commands and workflows

### Technical
- UTC timestamp standardization across all components
- 5-stage provenance support for compute_E operations
- Enhanced test coverage: 54 total tests including viewer and CLI functionality
- Package preparation with proper .gitignore and MANIFEST.in

## [16.0.1] - 2025-08-31

### Fixed
- Fixed version synchronization between VERSION.md and pyproject.toml to ensure correct PyPI packaging
- Fixed indentation error in Neo4j working memory exporter that was causing import failures
- Updated PyPI deployment workflow with correct project URL

### Changed
- Added version synchronization checker script (`scripts/check_version_sync.py`)
- Added comprehensive PyPI deployment documentation (`docs/PYPI_DEPLOYMENT.md`)

## [16.0.0] - 2025-08-31

### Added
- Universal, metadata-rich 5-stage provenance schema for all matrices (C, F, D):
  - stage_1_construct, stage_2_semantic, stage_3_column_lensed, stage_4_row_lensed, stage_5_final_synthesis.
- RichResult response type across resolvers with text, terms_used, warnings, and resolver metadata (modelId, latencyMs, promptHash, createdAt, phase).
- Universal Neo4j exporter with a single UNWIND-based Cypher that persists all five stages, rich metadata, and full context.
- Run/session scoping in exporter: (:Run {id}) nodes with (:Run)-[:CONTAINS]->(:Cell|:Stage) relationships; CLI generates a run_id per invocation for Neo4j exports.

### Changed
- Standardized API naming for D: `compute_cell_D`, `compute_matrix_D` (previously `synthesize_*`).
- Centralized prompt construction in `chirality/core/prompts.py` using explicit builders; resolver no longer exposes `assemble_prompt`.
- CLI verbose flows now display universal lensing steps: Column → Row → Final.

### Removed
- Backward compatibility shims and legacy fields/methods:
  - Removed `apply_ontological_lens` and any `assemble_prompt` usage.
  - Removed legacy provenance keys: `stage_1_products`, `stage_2_resolved`, `stage_3_lensed`, `stage_1_synthesis`.
  - Exporter no longer accepts legacy formats; provenance must be dict-shaped per stage with text/texts, terms_used, warnings, metadata.

### BREAKING CHANGES
- Provenance schema and resolver API changed:
  - Per-stage provenance is now dict-shaped and mandatory.
  - D functions renamed to `compute_*`; the CLI no longer accepts a custom `--problem` for D (canonical problem only).
- Export graph schema changed:
  - Universal five-stage pipeline with new labels and properties.
  - Run scoping added; existing queries should include `(:Run)` where appropriate.

## [15.0.2] - 2025-08-29

### Changed
- Refactored versioning to use `VERSION.md` as a single source of truth, removing hardcoded versions from the CLI and documentation.
- Updated core concept description from "deterministic" to "procedurally-rigorous methodology on a stochastic process" to more accurately reflect the architecture.

### Fixed
- Removed all outdated "CF14" version identifiers from current documentation and code for consistency.
- Renamed `CF14ValidationError` to `FrameworkValidationError` to align with the current project branding.

## [15.0.1] - 2025-08-29

### Fixed
- Corrected `.env` loading to ensure proper environment variable handling.
- Fixed a bug in the JSONL tracer to ensure accurate trace output.
- Resolved a missing import for Neo4j integration.

### Changed
- Enabled dual output for JSONL traces and Neo4j working memory for enhanced observability.

### Added
- Completed API reference documentation.
- Added a comprehensive prompt engineering guide.
- Included Neo4j query examples for advanced analysis.
- Added a tutorial for new users.

## [15.0.0] - 2025-08-29

### Added
- **Core Algorithm**: Introduced a three-stage interpretation pipeline (Combinatorial, Semantic Resolution, Ontological Lensing).
- **CLI**: Added a new `compute-cell` command with flags for verbosity, tracing, and Neo4j export.

### Changed
- **Major Architectural Refactoring**: This is a complete rewrite with a new CLI, simplified types, and different import paths. The project is transformed from a flexible framework into a fixed "semantic calculator" algorithm.

### BREAKING CHANGES
- This release is a complete architectural rewrite and is not backward-compatible.
- The CLI has been completely changed, with `compute-cell` as the new primary command.
- All import paths have been updated due to the new structure.
## [16.3.0] - 2025-09-04

### Added
- App Integration Mode in `compute-pipeline` with `--out`, `--problem-file`, and `--max-seconds`:
  - Writes per-cell `cells-jsonl-v1` snapshots for C/D/X/E under `runs/<run_id>/snapshots/`.
  - Writes `runs/<run_id>/index.json` manifest last and atomically, including checksums, bytes, and record counts.
  - Emits a single final stdout JSON line with `run_id` and manifest path.
  - Exit codes standardized: 0 OK; 2 invalid args; 3 timeout; 4 I/O; 5 resolver; 1 general.
- Dual-write legacy snapshots for all computed matrices to `snapshots/<run_id>/` for viewer compatibility.
- New `chirality/exporters/manifest_exporter.py` and tests.
- New producer-side `docs/INTERFACE.md` and documentation updates (README, API_REFERENCE, TUTORIAL, AGENTS, CLAUDE).
