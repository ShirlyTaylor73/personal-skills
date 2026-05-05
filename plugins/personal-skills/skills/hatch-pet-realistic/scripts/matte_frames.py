#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "rembg[cpu]>=2.0.50",
#     "pillow>=10.0",
#     "numpy>=1.24",
# ]
# ///
"""Matte frame PNGs with rembg human segmentation and write transparent RGBA PNGs.

Model weights are stored under <skill-base>/models/ instead of ~/.u2net/.
"""
from __future__ import annotations

import argparse
import json
import sys
from io import BytesIO
from pathlib import Path

# Allow direct script execution without relying on cwd/sys.path defaults.
sys.path.insert(0, str(Path(__file__).resolve().parent))

# IMPORTANT: import _skill_base before rembg; it sets U2NET_HOME.
from _skill_base import MODEL_NAME, SKILL_BASE  # noqa: E402,F401

import numpy as np  # noqa: E402
from PIL import Image, ImageFilter  # noqa: E402
from rembg import new_session, remove  # noqa: E402

_SESSION = None
MIN_ALPHA_RATIO = 0.05
MAX_ALPHA_RATIO = 0.95
CELL_WIDTH = 192
CELL_HEIGHT = 208
DEFAULT_TARGET_HEIGHT_RATIO = 0.94
DEFAULT_RUNNING_TARGET_HEIGHT_RATIO = 0.88
DEFAULT_EDGE_PADDING = 2


def _session():
    global _SESSION
    if _SESSION is None:
        _SESSION = new_session(MODEL_NAME)
    return _SESSION


def normalize_foreground(
    image: Image.Image,
    *,
    target_height_ratio: float,
    edge_padding: int,
) -> Image.Image:
    """Scale the transparent foreground to the requested pet-cell occupancy."""
    rgba = image.convert("RGBA")
    alpha_bbox = rgba.getchannel("A").getbbox()
    if alpha_bbox is None:
        return Image.new("RGBA", (CELL_WIDTH, CELL_HEIGHT), (0, 0, 0, 0))

    foreground = rgba.crop(alpha_bbox)
    max_width = max(1, CELL_WIDTH - edge_padding * 2)
    max_height = max(1, CELL_HEIGHT - edge_padding * 2)
    target_height = max(1, round(CELL_HEIGHT * target_height_ratio))
    scale = min(
        target_height / foreground.height,
        max_width / foreground.width,
        max_height / foreground.height,
    )
    new_size = (
        max(1, round(foreground.width * scale)),
        max(1, round(foreground.height * scale)),
    )
    if new_size != foreground.size:
        foreground = foreground.resize(new_size, Image.Resampling.LANCZOS)

    target = Image.new("RGBA", (CELL_WIDTH, CELL_HEIGHT), (0, 0, 0, 0))
    left = (CELL_WIDTH - foreground.width) // 2
    top = (CELL_HEIGHT - foreground.height) // 2
    target.alpha_composite(foreground, (left, top))
    return target


def matte_frame(
    src: Path,
    dst: Path,
    *,
    qa_dir: Path | None = None,
    source_label: str | None = None,
    feather_px: int = 1,
    normalize_scale: bool = True,
    target_height_ratio: float = DEFAULT_TARGET_HEIGHT_RATIO,
    edge_padding: int = DEFAULT_EDGE_PADDING,
) -> dict:
    """Matte one PNG into an RGBA PNG and return {ok, alpha_ratio}."""
    input_bytes = src.read_bytes()
    output_bytes = remove(input_bytes, session=_session())
    img = Image.open(BytesIO(output_bytes)).convert("RGBA")

    if feather_px > 0:
        r, g, b, a = img.split()
        a = a.filter(ImageFilter.GaussianBlur(radius=feather_px))
        img = Image.merge("RGBA", (r, g, b, a))

    if normalize_scale:
        img = normalize_foreground(
            img,
            target_height_ratio=target_height_ratio,
            edge_padding=edge_padding,
        )

    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, "PNG")

    alpha = np.array(img.split()[-1])
    ratio = float((alpha > 16).sum()) / alpha.size
    result = {"ok": True, "alpha_ratio": ratio, "src": str(src), "dst": str(dst)}

    if qa_dir is not None and (ratio < MIN_ALPHA_RATIO or ratio > MAX_ALPHA_RATIO):
        qa_dir.mkdir(parents=True, exist_ok=True)
        failures_json = qa_dir / "matte_failures.json"
        existing = []
        if failures_json.is_file():
            existing = json.loads(failures_json.read_text(encoding="utf-8"))
        existing.append(
            {
                "source": source_label or str(src),
                "alpha_ratio": ratio,
                "reason": "alpha_ratio_out_of_bounds",
            }
        )
        failures_json.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
        result["ok"] = False

    return result


def target_ratio_for(src: Path, default_ratio: float, running_ratio: float) -> float:
    if src.parent.name in {"running", "running-left", "running-right"}:
        return running_ratio
    return default_ratio


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def source_frame_paths(frames_root: Path, output_root: Path | None) -> list[Path]:
    paths = []
    for png in sorted(frames_root.rglob("*.png")):
        if png.name.endswith(".matted.png"):
            continue
        if output_root is not None and is_relative_to(png.resolve(), output_root):
            continue
        paths.append(png)
    return paths


def destination_for(src: Path, frames_root: Path, output_root: Path | None) -> Path:
    if output_root is None:
        return src.with_name(src.stem + ".matted.png")
    return output_root / src.relative_to(frames_root)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--frames-dir",
        required=True,
        help="Root directory containing row frame subdirectories.",
    )
    parser.add_argument(
        "--output-dir",
        help=(
            "Optional clean output root. When set, row subdirectories and frame "
            "filenames are preserved instead of writing sibling *.matted.png files."
        ),
    )
    parser.add_argument("--qa-dir", help="QA output directory for matte failure JSON.")
    parser.add_argument("--feather", type=int, default=1, help="Alpha edge feather radius in pixels.")
    parser.add_argument(
        "--target-height-ratio",
        type=float,
        default=DEFAULT_TARGET_HEIGHT_RATIO,
        help="Target alpha-bbox height ratio for non-running 192x208 frames.",
    )
    parser.add_argument(
        "--running-target-height-ratio",
        type=float,
        default=DEFAULT_RUNNING_TARGET_HEIGHT_RATIO,
        help="Target alpha-bbox height ratio for running rows.",
    )
    parser.add_argument(
        "--edge-padding",
        type=int,
        default=DEFAULT_EDGE_PADDING,
        help="Minimum transparent padding to preserve after scale normalization.",
    )
    parser.add_argument(
        "--no-normalize-scale",
        action="store_true",
        help="Disable rembg-after foreground scale normalization.",
    )
    args = parser.parse_args()

    frames_root = Path(args.frames_dir).expanduser().resolve()
    output_root = Path(args.output_dir).expanduser().resolve() if args.output_dir else None
    qa_dir = Path(args.qa_dir).expanduser().resolve() if args.qa_dir else None
    if output_root is not None and output_root == frames_root:
        raise SystemExit("--output-dir must be different from --frames-dir")

    results = []
    for png in source_frame_paths(frames_root, output_root):
        dst = destination_for(png, frames_root, output_root)
        result = matte_frame(
            png,
            dst,
            qa_dir=qa_dir,
            source_label=str(png),
            feather_px=args.feather,
            normalize_scale=not args.no_normalize_scale,
            target_height_ratio=target_ratio_for(
                png,
                args.target_height_ratio,
                args.running_target_height_ratio,
            ),
            edge_padding=args.edge_padding,
        )
        results.append(result)

    print(json.dumps({"ok": all(r["ok"] for r in results), "count": len(results)}, indent=2))


if __name__ == "__main__":
    main()
