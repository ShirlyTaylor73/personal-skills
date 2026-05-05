"""Tests for prepare_pet_run.py realistic-human prompt generation."""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import prepare_pet_run as ppr


def test_character_lock_constant_exists():
    assert hasattr(ppr, "CHARACTER_LOCK_KEY")
    assert ppr.CHARACTER_LOCK_KEY == "character_lock"


def test_human_row_prompt_starts_with_lock():
    """Every row prompt must start with the character lock."""
    lock = (
        "young east-asian woman, mid-20s, shoulder-length wavy black hair, "
        "fair skin, hazel eyes, cream oversized sweater"
    )
    prompt = ppr.build_human_row_prompt(state="waving", character_lock=lock)
    assert prompt.startswith(lock), f"prompt must start with character lock, got: {prompt[:80]}"
    assert "waving" in prompt.lower() or "wave" in prompt.lower()


def test_human_row_prompt_includes_realistic_anchors():
    """Row prompts must include realistic visual anchors."""
    prompt = ppr.build_human_row_prompt(state="idle", character_lock="test character")
    for required in ["photo-realistic", "natural skin", "neutral plain background"]:
        assert required.lower() in prompt.lower(), f"missing required anchor: {required!r}"


def test_human_base_prompt_requests_tight_full_body_framing():
    """Base prompt should prevent distant full-body framing."""
    prompt = ppr.build_human_base_prompt("adult person").lower()
    for required in [
        "92-96%",
        "4-8 px",
        "no extra empty margin",
        "avoid distant full-body framing",
    ]:
        assert required in prompt, f"missing tight framing constraint: {required!r}"


def test_human_row_prompt_requests_tight_slot_framing():
    """Row prompts should make every 192x208 slot readable in the desktop pet UI."""
    prompt = ppr.build_human_row_prompt(state="idle", character_lock="test character").lower()
    for required in [
        "192x208",
        "as large as possible",
        "head, hands, and shoes visible",
        "no extra empty margin",
    ]:
        assert required in prompt, f"missing tight slot constraint: {required!r}"


def test_layout_guide_uses_tight_safe_margins(tmp_path):
    """Layout guides should leave little margin so imagegen fills each pet slot."""
    metadata = ppr.create_layout_guide(tmp_path / "idle.png", "idle", 6)
    assert metadata["safe_margin_x"] == 8
    assert metadata["safe_margin_y"] == 6


def test_human_row_prompt_excludes_anime_terms_from_positive_prompt():
    """Stylized terms are allowed only in the negative prompt."""
    prompt = ppr.build_human_row_prompt(state="idle", character_lock="test character")
    if "negative:" in prompt.lower():
        idx = prompt.lower().index("negative:")
        positive_part = prompt[:idx].lower()
    else:
        positive_part = prompt.lower()
    for forbidden in ["chibi", "anime", "cel-shaded", "cartoon", "pixar"]:
        assert forbidden.lower() not in positive_part, (
            f"forbidden term leaked into positive prompt: {forbidden!r}"
        )


def test_running_left_prompt_does_not_mention_mirror():
    """running-left must be independently redrawn, not prompted as a mirror."""
    prompt = ppr.build_human_row_prompt(state="running-left", character_lock="test")
    assert "mirror" not in prompt.lower()
    assert "left" in prompt.lower()


def test_human_row_prompt_uses_placeholder_when_lock_empty():
    """An empty character lock should emit the literal placeholder."""
    prompt = ppr.build_human_row_prompt(state="idle", character_lock="")
    assert prompt.startswith("{{character_lock}}"), f"expected placeholder, got: {prompt[:60]}"
