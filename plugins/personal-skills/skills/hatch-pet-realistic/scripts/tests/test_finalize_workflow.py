"""Tests for finalize_pet_run.py orchestration."""
import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import finalize_pet_run


def test_finalize_uses_raw_then_matted_frames(monkeypatch, tmp_path):
    """Finalize should never compose directly from un-matted frames_raw."""
    run_dir = tmp_path / "run"
    qa_dir = run_dir / "qa"
    qa_dir.mkdir(parents=True)
    (run_dir / "pet_request.json").write_text(
        json.dumps(
            {
                "pet_id": "demo",
                "display_name": "Demo",
                "description": "Demo pet",
            }
        ),
        encoding="utf-8",
    )

    calls = []

    def fake_require_complete_jobs(run_dir_arg, *, allow_synthetic_test_sources):
        assert run_dir_arg == run_dir.resolve()
        assert allow_synthetic_test_sources is False

    def fake_run(command, *, check=True):
        calls.append(command)
        if "inspect_frames.py" in command[1]:
            review_index = command.index("--json-out") + 1
            Path(command[review_index]).write_text(json.dumps({"ok": True}), encoding="utf-8")
        return None

    monkeypatch.setattr(finalize_pet_run, "require_complete_jobs", fake_require_complete_jobs)
    monkeypatch.setattr(finalize_pet_run, "run", fake_run)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "finalize_pet_run.py",
            "--run-dir",
            str(run_dir),
            "--skip-package",
            "--skip-videos",
        ],
    )
    finalize_pet_run.main()

    extract = next(command for command in calls if "extract_strip_frames.py" in command[1])
    matte = next(command for command in calls if "matte_frames.py" in command[1])
    inspect = next(command for command in calls if "inspect_frames.py" in command[1])
    compose = next(command for command in calls if "compose_atlas.py" in command[1])
    validate = next(command for command in calls if "validate_atlas.py" in command[1])

    assert extract[extract.index("--output-dir") + 1].endswith("frames_raw")
    assert "--no-matte" in extract
    assert extract[extract.index("--method") + 1] == "slots"
    assert matte[matte.index("--frames-dir") + 1].endswith("frames_raw")
    assert matte[matte.index("--output-dir") + 1].endswith("frames")
    assert "--target-height-ratio" in matte
    assert matte[matte.index("--target-height-ratio") + 1] == "0.94"
    assert "--running-target-height-ratio" in matte
    assert matte[matte.index("--running-target-height-ratio") + 1] == "0.88"
    assert "--edge-padding" in matte
    assert matte[matte.index("--edge-padding") + 1] == "2"
    assert inspect[inspect.index("--frames-root") + 1].endswith("frames")
    assert compose[compose.index("--frames-root") + 1].endswith("frames")
    assert not compose[compose.index("--frames-root") + 1].endswith("frames_raw")
    assert validate[2].endswith("spritesheet.png")


def test_finalize_rejects_deterministic_mirror_provenance(tmp_path):
    """Realistic humans must generate running-left independently, not via mirroring."""
    run_dir = tmp_path / "run"
    generated_dir = tmp_path / "generated_images" / "job"
    decoded_dir = run_dir / "decoded"
    generated_dir.mkdir(parents=True)
    decoded_dir.mkdir(parents=True)

    source = generated_dir / "ig_001.png"
    output = decoded_dir / "running-left.png"
    source.write_bytes(b"source")
    output.write_bytes(b"output")

    job = {
        "id": "running-left",
        "source_path": str(source),
        "output_path": str(output),
        "source_provenance": "deterministic-mirror",
        "derived_from": "running-right",
    }

    try:
        finalize_pet_run.validate_completed_job_source(
            job,
            run_dir=run_dir,
            allow_synthetic_test_sources=False,
        )
    except SystemExit as exc:
        assert "running-left must be generated independently" in str(exc)
    else:
        raise AssertionError("deterministic mirror provenance should be rejected")
