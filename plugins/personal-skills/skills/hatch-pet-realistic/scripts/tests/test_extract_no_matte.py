"""Tests for extract_strip_frames.py --no-matte behavior."""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

SCRIPT = Path(__file__).resolve().parent.parent / "extract_strip_frames.py"


def test_no_matte_skips_chroma_key(tmp_path):
    decoded = tmp_path / "decoded"
    decoded.mkdir()
    strip = Image.new("RGB", (1152, 208), (0, 255, 0))
    strip.save(decoded / "idle.png")
    (decoded.parent / "pet_request.json").write_text(
        json.dumps({"chroma_key": {"hex": "#00FF00"}}),
        encoding="utf-8",
    )

    out = tmp_path / "frames"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--decoded-dir",
            str(decoded),
            "--output-dir",
            str(out),
            "--states",
            "idle",
            "--no-matte",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    frame0 = Image.open(out / "idle" / "00.png").convert("RGB")
    pixels = list(frame0.getdata())
    green_count = sum(1 for pixel in pixels if pixel == (0, 255, 0))
    assert green_count > len(pixels) * 0.8, "--no-matte should preserve the green background"

    manifest = json.loads((out / "frames-manifest.json").read_text(encoding="utf-8"))
    assert manifest.get("matted") is False
