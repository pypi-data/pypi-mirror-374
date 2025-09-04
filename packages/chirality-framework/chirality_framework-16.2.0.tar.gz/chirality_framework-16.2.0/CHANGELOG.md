# Changelog

All notable changes to the Chirality Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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