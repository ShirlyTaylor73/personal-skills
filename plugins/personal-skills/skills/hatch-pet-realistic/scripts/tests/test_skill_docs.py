"""Regression checks for SKILL.md command examples."""
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[2]
SKILL = SKILL_ROOT / "SKILL.md"
REFERENCE_DOCS = [
    SKILL,
    SKILL_ROOT / "references" / "animation-rows.md",
    SKILL_ROOT / "references" / "qa-rubric.md",
    SKILL_ROOT / "references" / "realistic-style-guide.md",
]


def test_skill_doc_uses_current_cli_flags():
    text = SKILL.read_text(encoding="utf-8")
    required = [
        "--reference",
        "--job-id",
        "--source",
        "--frames-root",
        "--json-out",
        "--spritesheet",
    ]
    for flag in required:
        assert flag in text


def test_skill_doc_does_not_use_stale_cli_flags():
    text = SKILL.read_text(encoding="utf-8")
    stale = [
        "--reference-image",
        "--row base",
        "--row <state>",
        "--image <ig_*.png>",
        "--atlas ",
        "package_custom_pet.py --run-dir",
        "matte_frames.py --force",
    ]
    for flag in stale:
        assert flag not in text
    assert "--frames-dir <run-dir>/frames \\" not in text


def test_skill_doc_is_clean_utf8_not_mojibake():
    for path in REFERENCE_DOCS:
        text = path.read_text(encoding="utf-8")
        for marker in ["\u00c3", "\u00c2", "\u6d5c", "\u677b"]:
            assert marker not in text, f"{path} contains mojibake marker {marker!r}"


def test_skill_doc_covers_large_readable_human_framing():
    text = SKILL.read_text(encoding="utf-8")
    required = [
        "92-96%",
        "192x208",
        "no extra empty margin",
        "Subject too small",
        "--target-height-ratio",
        "--running-target-height-ratio",
        "--edge-padding",
    ]
    for marker in required:
        assert marker in text


def test_skill_doc_has_no_process_or_history_noise():
    forbidden = [
        "this change",
        "this time",
        "version history",
        "change log",
        "discussion",
        "thinking process",
        "\u65b0\u589e",
        "\u4e0d\u518d\u8981\u6c42",
        "\u4e0e hatch-pet",
        "Character Lockdown",
        "manifest.json#character_lock",
        "matte_frames.py --force",
    ]
    for path in REFERENCE_DOCS:
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            assert marker not in text, f"{path} contains non-actionable marker {marker!r}"
