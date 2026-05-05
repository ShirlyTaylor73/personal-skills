#!/usr/bin/env python3
"""Generate Claude marketplace metadata for the bundled plugin."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PLUGIN_NAME = "personal-skills"
PLUGIN_VERSION = "0.1.0"
MARKETPLACE_DESCRIPTION = "Personal agent skills collection."
PLUGIN_SOURCE = "./plugins/personal-skills"
OWNER = {
    "name": "ShirlyTaylor73",
    "email": "shirlytaylor73@gmail.com",
}
AUTHOR = {
    **OWNER,
    "url": "https://github.com/ShirlyTaylor73",
}


def collect_skill_names(skills_root: Path) -> list[str]:
    if not skills_root.exists():
        raise FileNotFoundError(f"Missing skills root: {skills_root}")

    skill_names: list[str] = []
    for skill_dir in sorted(skills_root.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith("."):
            continue

        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            raise ValueError(f"{skill_dir} is missing SKILL.md")
        skill_names.append(skill_dir.name)

    if not skill_names:
        raise ValueError(f"No skills found in {skills_root}")
    return skill_names


def build_marketplace(skills_root: Path) -> dict[str, Any]:
    collect_skill_names(skills_root)
    return {
        "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
        "name": PLUGIN_NAME,
        "description": MARKETPLACE_DESCRIPTION,
        "owner": OWNER,
        "plugins": [
            {
                "name": PLUGIN_NAME,
                "description": MARKETPLACE_DESCRIPTION,
                "version": PLUGIN_VERSION,
                "source": PLUGIN_SOURCE,
                "author": AUTHOR,
            }
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate .claude-plugin/marketplace.json for personal-skills"
    )
    parser.add_argument(
        "--skills-root",
        type=Path,
        default=Path("plugins/personal-skills/skills"),
        help="Root directory containing bundled skill subdirectories",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".claude-plugin/marketplace.json"),
        help="Output marketplace JSON path",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    marketplace = build_marketplace(args.skills_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(marketplace, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.output} for plugin {PLUGIN_NAME}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
