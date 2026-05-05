"""Tests for matte_frames.py rembg-based portrait matting."""
import os
import sys
from pathlib import Path

from PIL import Image
from PIL import ImageDraw

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import matte_frames

FIXTURE = Path(__file__).parent / "fixtures" / "sample_with_bg.png"


def test_skill_base_resolves_correctly():
    """matte_frames.SKILL_BASE points to the hatch-pet-realistic skill root."""
    assert matte_frames.SKILL_BASE.name == "hatch-pet-realistic"
    assert (matte_frames.SKILL_BASE / "scripts" / "matte_frames.py").is_file()


def test_u2net_home_set_to_skill_models():
    """The script sets U2NET_HOME to <skill>/models/ before importing rembg."""
    expected = str(matte_frames.SKILL_BASE / "models")
    assert os.environ["U2NET_HOME"] == expected


def test_matte_frame_produces_alpha_channel(tmp_path):
    """A matted portrait fixture should produce an alpha channel."""
    out = tmp_path / "matted.png"
    matte_frames.matte_frame(FIXTURE, out)
    assert out.is_file()
    with Image.open(out) as img:
        assert img.mode == "RGBA"
        alpha = img.split()[-1]
        extrema = alpha.getextrema()
        assert extrema[0] < 255 and extrema[1] > 0, f"alpha extrema {extrema} show matting failed"


def test_matte_frame_failure_detection_writes_qa_json(tmp_path):
    """Extreme alpha coverage should be reported in qa/matte_failures.json."""
    white = tmp_path / "white.png"
    Image.new("RGB", (192, 208), (255, 255, 255)).save(white)
    out = tmp_path / "matted.png"
    qa_dir = tmp_path / "qa"
    qa_dir.mkdir()
    result = matte_frames.matte_frame(white, out, qa_dir=qa_dir, source_label="white")
    failures_json = qa_dir / "matte_failures.json"
    if result.get("alpha_ratio", 0.5) < 0.05 or result.get("alpha_ratio", 0.5) > 0.95:
        assert failures_json.is_file(), "failure should be written to qa/matte_failures.json"


def test_output_dir_preserves_row_layout_and_clean_names(monkeypatch, tmp_path):
    """--output-dir writes clean row/frame paths instead of sibling *.matted.png files."""
    frames_root = tmp_path / "frames_raw"
    idle_dir = frames_root / "idle"
    idle_dir.mkdir(parents=True)
    src = idle_dir / "00.png"
    Image.new("RGB", (12, 12), (255, 255, 255)).save(src)

    monkeypatch.setattr(matte_frames, "_SESSION", object())
    monkeypatch.setattr(matte_frames, "remove", lambda input_bytes, session: input_bytes)

    output_root = tmp_path / "frames"
    results = []
    for path in matte_frames.source_frame_paths(frames_root, output_root):
        dst = matte_frames.destination_for(path, frames_root, output_root)
        results.append(matte_frames.matte_frame(path, dst, feather_px=0))

    assert all(result["ok"] for result in results)
    assert (output_root / "idle" / "00.png").is_file()
    assert not (idle_dir / "00.matted.png").exists()
    with Image.open(output_root / "idle" / "00.png") as image:
        assert image.mode == "RGBA"


def test_matte_frame_normalizes_small_transparent_subject(monkeypatch, tmp_path):
    """Default matting should enlarge small transparent foregrounds to pet-readable scale."""
    src = tmp_path / "small.png"
    image = Image.new("RGBA", (192, 208), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((86, 70, 106, 149), fill=(20, 20, 20, 255))
    image.save(src)

    monkeypatch.setattr(matte_frames, "_SESSION", object())
    monkeypatch.setattr(matte_frames, "remove", lambda input_bytes, session: input_bytes)

    out = tmp_path / "out.png"
    result = matte_frames.matte_frame(src, out, feather_px=0)

    assert result["ok"]
    with Image.open(out) as opened:
        normalized = opened.convert("RGBA")
    assert normalized.size == (192, 208)
    assert normalized.mode == "RGBA"
    bbox = normalized.getchannel("A").getbbox()
    assert bbox is not None
    assert 192 <= bbox[3] - bbox[1] <= 196
