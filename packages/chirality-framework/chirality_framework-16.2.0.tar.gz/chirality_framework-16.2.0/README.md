# Chirality Framework: A Semantic Calculator

[![PyPI](https://img.shields.io/pypi/v/chirality-framework.svg)](https://pypi.org/project/chirality-framework/)
[![Python versions](https://img.shields.io/pypi/pyversions/chirality-framework.svg)](https://pypi.org/project/chirality-framework/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Publish](https://github.com/sgttomas/chirality-framework/actions/workflows/python-publish.yml/badge.svg)](https://github.com/sgttomas/chirality-framework/actions/workflows/python-publish.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/tag/sgttomas/chirality-framework?sort=semver&label=release)](https://github.com/sgttomas/chirality-framework/tags)

**Version: 16.1.0** | **Status: Active Development**

The Chirality Framework is a "semantic calculator" designed to execute a fixed, canonical algorithm for structured problem-solving. It transforms a set of base matrices through a multi-stage semantic pipeline, producing a series of derived matrices that represent a complete traversal of a "semantic valley" from problem to evaluation.

The value of this project is in the unique, insightful **output** of the calculation and the **observability** of the process, not in the flexibility of the code.

## Core Concept: The Semantic Valley Pipeline

The framework computes a sequence of matrices, each representing a station in the semantic valley. The primary operations involve:
1.  **Semantic Dot Product:** A multi-stage process involving mechanical term combination, LLM-driven semantic resolution, and ontological lensing.
2.  **Station Shifting:** An LLM-driven transformation of a matrix from one context (e.g., Verification) to another (e.g., Validation).
3.  **Structural Operations:** Standard matrix operations like transposing and slicing.

For a complete technical description, see the **[Canonical Algorithm Documentation](docs/ALGORITHM.md)**.

## Quick Start: The End-to-End Workflow

The recommended way to use the framework is to compute the entire pipeline and view the results in the generated HTML viewer.

### Prerequisites
- Python 3.9+
- An OpenAI API key set as the `OPENAI_API_KEY` environment variable.

### Step 1: Compute the Full Pipeline
This command runs the entire semantic pipeline (Matrices C through E), generates snapshots of every matrix (including the base matrices A, B, and J), and creates detailed trace files for debugging.

```bash
# Install with OpenAI support
pip install 'chirality-framework[openai]'

# Set your API key (add to your shell profile for persistence)
export OPENAI_API_KEY="sk-..."

# Run the full pipeline with the OpenAI resolver
python3 -m chirality.cli compute-pipeline --resolver openai --snapshot-jsonl --include-base
```
This will create two directories, `snapshots/<run_id>/` and `traces/<run_id>/`, containing the output files.

### Step 2: Render and View the Results
This command reads the generated snapshots and creates a self-contained HTML file to display all the matrices in an elegant, readable format.

```bash
# Render the latest run and open it in your browser
python3 -m chirality.cli render-viewer --latest --open
```
This will create a `viewer-output/` directory containing the `index.html` and `style.css` files and automatically open the page for you. You can change the output location with `--output-dir`.

## Advanced Usage

### Computing Individual Matrices
The `compute-matrix` command allows you to compute and snapshot any single matrix, automatically handling its prerequisites.

```bash
# Compute just the final Evaluation matrix (E)
python3 -m chirality.cli compute-matrix E --resolver openai --snapshot-jsonl

# Snapshot a base matrix for reference
python3 -m chirality.cli compute-matrix A --snapshot-jsonl
```

### Inspecting a Single Cell
For detailed debugging, the `compute-cell` command lets you observe the full multi-stage pipeline for any single cell in a matrix.

```bash
# Observe the computation of cell C[0,0] with verbose output
python3 -m chirality.cli compute-cell C --i 0 --j 0 --resolver openai --verbose --trace
```

### Viewing Options
The `render-viewer` command has several options for customizing the output:

```bash
# Render a specific run with a custom title
python3 -m chirality.cli render-viewer --run-id "<run_id>" --title "My Analysis"

# Render with the "Elements" style for a more code-like view
python3 -m chirality.cli render-viewer --latest --style elements

# Disable the default value sanitization to see raw output
python3 -m chirality.cli render-viewer --latest --style elements --no-sanitize-values
```

## Development

To set up the development environment and run tests, please refer to the instructions in `CONTRIBUTING.md`.
