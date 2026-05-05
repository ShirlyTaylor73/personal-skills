#!/usr/bin/env python3
"""Create a Codex pet run folder, prompts, and imagegen job manifest."""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image
from PIL import ImageDraw

ATLAS = {"columns": 8, "rows": 9, "cell_width": 192, "cell_height": 208}
ATLAS["width"] = ATLAS["columns"] * ATLAS["cell_width"]
ATLAS["height"] = ATLAS["rows"] * ATLAS["cell_height"]

ROWS = [
    ("idle", 0, 6, "neutral breathing/blinking loop"),
    ("running-right", 1, 8, "rightward locomotion loop"),
    ("running-left", 2, 8, "leftward locomotion loop"),
    ("waving", 3, 4, "greeting gesture with raised wave and return"),
    ("jumping", 4, 5, "anticipation, lift, peak, descent, settle"),
    ("failed", 5, 8, "sad, failed, or deflated reaction"),
    ("waiting", 6, 6, "patient waiting loop with small motion"),
    ("running", 7, 6, "generic in-place running loop"),
    ("review", 8, 6, "focused inspecting or review loop"),
]

CHARACTER_LOCK_KEY = "character_lock"
REALISTIC_STYLE_GUIDE_PATH = "references/realistic-style-guide.md"

REALISTIC_ANCHORS = (
    "photo-realistic, photographic quality, cinematic lighting",
    "natural skin texture with pores and subtle imperfections",
    "realistic hair strands with individual fiber detail",
    "accurate human anatomy, head-to-body ratio approximately 1:7.5",
    "subject framed against neutral plain background for downstream segmentation",
)

TIGHT_BASE_FRAMING = (
    "tight full-body pet framing: subject fills 92-96% of frame height, "
    "hair or head within 4-8 px of the top safe area, shoes within 4-8 px "
    "of the bottom safe area, no extra empty margin, avoid distant full-body framing"
)

TIGHT_ROW_FRAMING = (
    "tight 192x208 slot framing: each invisible frame slot is cropped around one "
    "complete full-body person, the person is as large as possible while keeping "
    "the full head, hands, and shoes visible, no extra empty margin, avoid distant "
    "full-body framing"
)

REALISTIC_NEGATIVES = (
    "cartoon, anime, manga, chibi, cel-shaded, flat colors, "
    "3d render, cgi, pixar style, plastic skin, "
    "illustration, painting, painterly, concept art, "
    "oversized head, super-deformed, motion lines, speech bubbles, text overlays, watermarks, "
    "shadow on ground, cast shadow under feet"
)

ROW_HUMAN_DESCRIPTIONS = {
    "idle": "standing in a neutral pose, gentle weight shift, occasional blink, body remains stationary, 6 frames of a calm idle loop",
    "running-right": "side view running to the right, full body, 8 frames of one complete gait cycle (contact, down, passing, high-point) repeated twice, arms swinging in counter-rhythm with legs",
    "running-left": "side view running toward the left, full body, character faces left throughout the row, 8 frames of one complete gait cycle drawn independently from scratch (do NOT flip or reuse the right-facing artwork), arms swinging in counter-rhythm with legs",
    "waving": "facing camera, raising right arm to wave, 4 frames: arm rising, peak wave, wrist tilted out, arm returning",
    "jumping": "5 frames of a vertical jump: knee bend preparation, push-off, peak airborne with both feet off ground, landing cushion, settled stance",
    "failed": "8 frames expressing failure / disappointment: realization, head shake, both hands on head, head down, sigh, palms-up shrug, rubbing temple, slow recovery",
    "waiting": "6 frames of a patient wait loop: checking wristwatch, hands in pockets, weight shift, looking into distance, arms folded, returning to neutral",
    "running": "front view running toward camera, full body, 6 frames of legs alternating, arms pumping",
    "review": "6 frames thinking pose: hand on chin, head tilted, holding magnifying glass or document, nodding, focused gaze, returning",
}


def build_human_row_prompt(state: str, character_lock: str) -> str:
    """构造单行 row strip prompt，强制以 character_lock 开头 + 写实锚定 + 禁止词。

    若 character_lock 为空，则用 ``{{character_lock}}`` 字面量占位符代替；
    parent 在 base 确认并写入真正的 lock 字符串后再做一次替换。
    """
    if state not in ROW_HUMAN_DESCRIPTIONS:
        raise ValueError(f"unknown state: {state}")
    lock = character_lock.strip() if character_lock else "{{character_lock}}"
    parts = [
        lock,
        ROW_HUMAN_DESCRIPTIONS[state],
        ", ".join(REALISTIC_ANCHORS),
        f"layout: 1 row of frames laid out horizontally, count matches {state} row contract",
        TIGHT_ROW_FRAMING,
        "negative: " + REALISTIC_NEGATIVES,
    ]
    return ". ".join(parts)


def build_human_base_prompt(description: str) -> str:
    """全身正面中性站姿 base prompt（T-pose 变体）。"""
    return ". ".join([
        description.strip(),
        "full-body front view, neutral standing pose, arms relaxed at sides, feet shoulder-width apart",
        ", ".join(REALISTIC_ANCHORS),
        "layout: single subject centered",
        TIGHT_BASE_FRAMING,
        "negative: " + REALISTIC_NEGATIVES,
    ])

CHROMA_KEY_CANDIDATES = [
    ("magenta", "#FF00FF"),
    ("cyan", "#00FFFF"),
    ("yellow", "#FFFF00"),
    ("blue", "#0000FF"),
    ("orange", "#FF7F00"),
    ("green", "#00FF00"),
]

DEFAULT_PET_NAME = "Sprout"
CANONICAL_BASE_PATH = "references/canonical-base.png"
LAYOUT_GUIDE_DIR = "references/layout-guides"
LAYOUT_GUIDE_SAFE_MARGIN_X = 8
LAYOUT_GUIDE_SAFE_MARGIN_Y = 6


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-")


def display_from_slug(value: str) -> str:
    words = [word for word in re.split(r"[^a-zA-Z0-9]+", value.strip()) if word]
    return " ".join(word.capitalize() for word in words)


def concept_words(value: str) -> list[str]:
    stop_words = {
        "a",
        "an",
        "and",
        "app",
        "based",
        "codex",
        "compact",
        "digital",
        "for",
        "from",
        "in",
        "of",
        "on",
        "pet",
        "ready",
        "small",
        "the",
        "to",
        "with",
    }
    words = [
        word.lower()
        for word in re.findall(r"[a-zA-Z0-9]+", value)
        if word.lower() not in stop_words
    ]
    return words


def infer_name(args: argparse.Namespace, reference_paths: list[Path]) -> str:
    for raw_value in [args.display_name, args.pet_name]:
        value = raw_value.strip()
        if value:
            return value

    if args.pet_id.strip():
        display = display_from_slug(args.pet_id)
        if display:
            return display

    for raw_value in [args.pet_notes, args.description]:
        words = concept_words(raw_value)
        if words:
            return words[0].capitalize()

    for path in reference_paths:
        display = display_from_slug(path.stem)
        if display:
            return display

    return DEFAULT_PET_NAME


def sentence(value: str) -> str:
    value = " ".join(value.strip().split())
    if not value:
        return value
    if value[-1] not in ".!?":
        value += "."
    return value


def infer_description(args: argparse.Namespace, reference_paths: list[Path]) -> str:
    if args.description.strip():
        return sentence(args.description)
    if args.pet_notes.strip():
        return sentence(f"A compact Codex digital pet: {args.pet_notes}")
    if reference_paths:
        return "A compact Codex digital pet based on the provided reference image."
    return "A compact original Codex digital pet ready for animation."


def infer_pet_notes(args: argparse.Namespace, reference_paths: list[Path]) -> str:
    if args.pet_notes.strip():
        return args.pet_notes.strip()
    if args.description.strip():
        return args.description.strip().rstrip(".")
    if reference_paths:
        return "the pet shown in the reference image(s)"
    return "a compact original Codex digital pet"


def default_output_dir(pet_id: str) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path.cwd() / "output" / "hatch-pet" / f"{pet_id}-{timestamp}"


def rel(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve()))


def image_metadata(path: Path) -> dict[str, object]:
    with Image.open(path) as image:
        return {
            "path": str(path),
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
            "format": image.format,
        }


def draw_dashed_line(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    *,
    fill: str,
    dash: int = 8,
    gap: int = 6,
) -> None:
    x1, y1 = start
    x2, y2 = end
    if x1 == x2:
        step = dash + gap
        for y in range(min(y1, y2), max(y1, y2), step):
            draw.line((x1, y, x2, min(y + dash, max(y1, y2))), fill=fill)
        return
    if y1 == y2:
        step = dash + gap
        for x in range(min(x1, x2), max(x1, x2), step):
            draw.line((x, y1, min(x + dash, max(x1, x2)), y2), fill=fill)
        return
    raise ValueError("draw_dashed_line only supports horizontal or vertical lines")


def create_layout_guide(path: Path, state: str, frames: int) -> dict[str, object]:
    width = frames * ATLAS["cell_width"]
    height = ATLAS["cell_height"]
    cell_width = ATLAS["cell_width"]
    image = Image.new("RGB", (width, height), "#f7f7f7")
    draw = ImageDraw.Draw(image)

    for index in range(frames):
        left = index * cell_width
        right = left + cell_width - 1
        draw.rectangle((left, 0, right, height - 1), outline="#111111", width=2)

        safe_left = left + LAYOUT_GUIDE_SAFE_MARGIN_X
        safe_top = LAYOUT_GUIDE_SAFE_MARGIN_Y
        safe_right = right - LAYOUT_GUIDE_SAFE_MARGIN_X
        safe_bottom = height - 1 - LAYOUT_GUIDE_SAFE_MARGIN_Y
        draw.rectangle(
            (safe_left, safe_top, safe_right, safe_bottom),
            outline="#2f80ed",
            width=2,
        )

        center_x = left + cell_width // 2
        center_y = height // 2
        draw_dashed_line(
            draw,
            (center_x, safe_top),
            (center_x, safe_bottom),
            fill="#b8b8b8",
        )
        draw_dashed_line(
            draw,
            (safe_left, center_y),
            (safe_right, center_y),
            fill="#b8b8b8",
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return {
        "state": state,
        "path": str(path),
        "width": width,
        "height": height,
        "frames": frames,
        "cell_width": ATLAS["cell_width"],
        "cell_height": ATLAS["cell_height"],
        "safe_margin_x": LAYOUT_GUIDE_SAFE_MARGIN_X,
        "safe_margin_y": LAYOUT_GUIDE_SAFE_MARGIN_Y,
        "usage": "layout guide input only; do not copy visible guide lines into generated sprite strips",
    }


def create_layout_guides(run_dir: Path) -> list[dict[str, object]]:
    guide_dir = run_dir / LAYOUT_GUIDE_DIR
    return [
        create_layout_guide(guide_dir / f"{state}.png", state, frames)
        for state, _row, frames, _purpose in ROWS
    ]


def parse_hex_color(value: str) -> tuple[int, int, int]:
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        raise SystemExit(f"invalid chroma key color: {value}; expected #RRGGBB")
    return tuple(int(value[index : index + 2], 16) for index in (1, 3, 5))


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


def color_distance(left: tuple[int, int, int], right: tuple[int, int, int]) -> float:
    return math.sqrt(sum((left[index] - right[index]) ** 2 for index in range(3)))


def sampled_reference_pixels(paths: list[Path]) -> list[tuple[int, int, int]]:
    pixels: list[tuple[int, int, int]] = []
    for path in paths:
        with Image.open(path) as opened:
            image = opened.convert("RGBA")
            image.thumbnail((128, 128), Image.Resampling.LANCZOS)
            data = image.tobytes()
            for index in range(0, len(data), 4):
                red, green, blue, alpha = data[index : index + 4]
                if alpha <= 16:
                    continue
                pixels.append((red, green, blue))

    non_background = [
        pixel
        for pixel in pixels
        if not (pixel[0] > 244 and pixel[1] > 244 and pixel[2] > 244)
    ]
    return non_background or pixels


def choose_chroma_key(reference_paths: list[Path], requested: str) -> dict[str, object]:
    if requested.lower() != "auto":
        rgb = parse_hex_color(requested)
        return {
            "hex": rgb_to_hex(rgb),
            "rgb": list(rgb),
            "name": "user-selected",
            "selection": "manual",
        }

    pixels = sampled_reference_pixels(reference_paths)
    if not pixels:
        rgb = parse_hex_color("#FF00FF")
        return {
            "hex": "#FF00FF",
            "rgb": list(rgb),
            "name": "magenta",
            "selection": "fallback",
        }

    scored: list[tuple[float, int, str, tuple[int, int, int]]] = []
    for preference_index, (name, hex_color) in enumerate(CHROMA_KEY_CANDIDATES):
        rgb = parse_hex_color(hex_color)
        distances = sorted(color_distance(rgb, pixel) for pixel in pixels)
        percentile_index = max(0, min(len(distances) - 1, int(len(distances) * 0.01)))
        scored.append((distances[percentile_index], -preference_index, name, rgb))

    score, _preference, name, rgb = max(scored)
    return {
        "hex": rgb_to_hex(rgb),
        "rgb": list(rgb),
        "name": name,
        "selection": "auto",
        "score": round(score, 2),
    }


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def make_jobs(
    run_dir: Path, copied_refs: list[dict[str, object]]
) -> list[dict[str, object]]:
    reference_inputs = [
        {"path": rel(Path(str(ref["copied_path"])), run_dir), "role": "pet reference"}
        for ref in copied_refs
    ]
    identity_reference_paths = [CANONICAL_BASE_PATH, "decoded/base.png"]
    jobs: list[dict[str, object]] = [
        {
            "id": "base",
            "kind": "base-pet",
            "status": "pending",
            "prompt_file": "prompts/base-pet.md",
            "input_images": reference_inputs,
            "output_path": "decoded/base.png",
            "depends_on": [],
            "generation_skill": "$imagegen",
            "requires_grounded_generation": bool(reference_inputs),
            "allow_prompt_only_generation": not reference_inputs,
            "recording_owner": "parent",
        }
    ]
    for state, _row, frames, _purpose in ROWS:
        depends_on = ["base"]
        extra_inputs: list[dict[str, str]] = []
        mirror_policy: dict[str, object] = {}
        if state == "running-left":
            depends_on.append("running-right")
            extra_inputs.append(
                {
                    "path": "decoded/running-right.png",
                    "role": "rightward gait reference for leftward row decision",
                }
            )
            mirror_policy = {
                "may_derive_from": "running-right",
                "derivation": "horizontal-mirror",
                "requires_explicit_approval": True,
                "fallback_generation_skill": "$imagegen",
            }
        jobs.append(
            {
                "id": state,
                "kind": "row-strip",
                "status": "pending",
                "prompt_file": f"prompts/rows/{state}.md",
                "input_images": [
                    *reference_inputs,
                    {
                        "path": f"{LAYOUT_GUIDE_DIR}/{state}.png",
                        "role": f"layout guide for {frames} frame slots; use for spacing only, do not copy guide lines",
                    },
                    {
                        "path": CANONICAL_BASE_PATH,
                        "role": "canonical identity reference",
                    },
                    {"path": "decoded/base.png", "role": "approved base pet"},
                    *extra_inputs,
                ],
                "output_path": f"decoded/{state}.png",
                "depends_on": depends_on,
                "generation_skill": "$imagegen",
                "requires_grounded_generation": True,
                "allow_prompt_only_generation": False,
                "identity_reference_paths": identity_reference_paths,
                "parallelizable_after": depends_on,
                "mirror_policy": mirror_policy,
                "recording_owner": "parent",
            }
        )
    return jobs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pet-name",
        default="",
        help="User-facing pet name. Ask the user for this when practical; otherwise choose a short appropriate name.",
    )
    parser.add_argument(
        "--pet-id",
        default="",
        help="Stable pet folder/id slug. Defaults to the slugified pet name.",
    )
    parser.add_argument(
        "--display-name",
        default="",
        help="Display label. Defaults to the pet name.",
    )
    parser.add_argument("--description", default="")
    parser.add_argument("--reference", action="append", default=[])
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--pet-notes", default="")
    parser.add_argument("--style-notes", default="")
    parser.add_argument(
        "--chroma-key",
        default="auto",
        help="Chroma key as #RRGGBB, or auto to choose a safe key from reference colors.",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    raw_reference_paths = [
        Path(raw_path).expanduser().resolve() for raw_path in args.reference
    ]

    args.display_name = infer_name(args, raw_reference_paths)
    args.pet_name = (args.pet_name or args.display_name).strip()
    args.description = infer_description(args, raw_reference_paths)
    args.pet_notes = infer_pet_notes(args, raw_reference_paths)
    args.pet_id = slugify(args.pet_id or args.pet_name or args.display_name)
    if not args.pet_id:
        raise SystemExit("pet id must contain at least one letter or digit")

    run_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else default_output_dir(args.pet_id).resolve()
    )
    if run_dir.exists() and any(run_dir.iterdir()) and not args.force:
        raise SystemExit(
            f"{run_dir} already exists and is not empty; pass --force to reuse it"
        )
    run_dir.mkdir(parents=True, exist_ok=True)

    ref_dir = run_dir / "references"
    prompt_dir = run_dir / "prompts"
    row_prompt_dir = prompt_dir / "rows"
    for directory in [
        ref_dir,
        prompt_dir,
        row_prompt_dir,
        run_dir / "decoded",
        run_dir / "qa",
    ]:
        directory.mkdir(parents=True, exist_ok=True)

    copied_refs: list[dict[str, object]] = []
    copied_ref_paths: list[Path] = []
    for index, source in enumerate(raw_reference_paths, start=1):
        if not source.is_file():
            raise SystemExit(f"reference not found: {source}")
        suffix = source.suffix.lower() or ".png"
        copied = ref_dir / f"reference-{index:02d}{suffix}"
        shutil.copy2(source, copied)
        meta = image_metadata(copied)
        meta["source_path"] = str(source)
        meta["copied_path"] = str(copied)
        copied_refs.append(meta)
        copied_ref_paths.append(copied)

    args.chroma_key = choose_chroma_key(copied_ref_paths, args.chroma_key)
    layout_guides = create_layout_guides(run_dir)

    request = {
        "pet_id": args.pet_id,
        "display_name": args.display_name,
        "description": args.description,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "atlas": ATLAS,
        "rows": [
            {"state": state, "row": row, "frames": frames, "purpose": purpose}
            for state, row, frames, purpose in ROWS
        ],
        "layout_guides": [
            {**guide, "path": rel(Path(str(guide["path"])), run_dir)}
            for guide in layout_guides
        ],
        "references": copied_refs,
        "chroma_key": args.chroma_key,
        "pet_notes": args.pet_notes,
        "style_notes": args.style_notes,
        "house_style_reference": REALISTIC_STYLE_GUIDE_PATH,
        "primary_generation_skill": "$imagegen",
        CHARACTER_LOCK_KEY: "",
    }
    (run_dir / "pet_request.json").write_text(
        json.dumps(request, indent=2) + "\n", encoding="utf-8"
    )

    character_lock = request.get(CHARACTER_LOCK_KEY, "")
    write_text(prompt_dir / "base-pet.md", build_human_base_prompt(args.description))
    for state, _row, _frames, _purpose in ROWS:
        write_text(
            row_prompt_dir / f"{state}.md",
            build_human_row_prompt(state=state, character_lock=character_lock),
        )

    jobs = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "primary_generation_skill": "$imagegen",
        "jobs": make_jobs(run_dir, copied_refs),
    }
    (run_dir / "imagegen-jobs.json").write_text(
        json.dumps(jobs, indent=2) + "\n", encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "ok": True,
                "run_dir": str(run_dir),
                "request": str(run_dir / "pet_request.json"),
                "jobs": str(run_dir / "imagegen-jobs.json"),
                "ready_jobs": ["base"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
