import json
from pathlib import Path
from click.testing import CliRunner

from chirality.cli import cli


def test_compute_pipeline_app_mode_success(tmp_path: Path):
    runs_dir = tmp_path / "runs"
    out_dir = runs_dir / "test-run-1"
    problem = tmp_path / "problem.json"
    problem.write_text(json.dumps({"title": "T", "statement": "S"}), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "compute-pipeline",
            "--resolver",
            "echo",
            "--out",
            str(out_dir),
            "--problem-file",
            str(problem),
            "--max-seconds",
            "900",
        ],
    )

    assert result.exit_code == 0, f"stdout/stderr: {result.output}"
    # The only stdout should be the final JSON line
    out = result.output.strip().splitlines()
    assert len(out) == 1
    payload = json.loads(out[0])
    assert payload["run_id"] == "test-run-1"
    (
        Path(payload["manifest"])
        if payload["manifest"].startswith(str(tmp_path))
        else out_dir / "index.json"
    )
    # Make sure manifest exists at expected path
    assert (out_dir / "index.json").exists()
    data = json.loads((out_dir / "index.json").read_text(encoding="utf-8"))
    mats = data["matrices"]
    # Required matrices present
    assert set([*mats.keys()]) >= {"C", "D", "X", "E"}
    for k in ["C", "D", "X", "E"]:
        meta = mats[k]
        assert meta["format"] == "cells-jsonl-v1"
        # Paths are run-dir relative
        p = out_dir / meta["path"]
        assert p.exists()
