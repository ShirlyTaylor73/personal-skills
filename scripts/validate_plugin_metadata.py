#!/usr/bin/env python3
"""Validate repository-local Codex and Claude plugin metadata."""

from __future__ import annotations

import difflib
import json
import sys
from pathlib import Path
from typing import Any

from generate_claude_marketplace import PLUGIN_NAME, build_marketplace, collect_skill_names


REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = REPO_ROOT / "plugins" / "personal-skills"
SKILLS_ROOT = PLUGIN_ROOT / "skills"


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def repo_label(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def resolve_plugin_root(repo_root: Path, marketplace_entry: dict[str, Any]) -> Path | None:
    source = marketplace_entry.get("source")
    if not isinstance(source, dict):
        return None

    rel_path = source.get("path")
    if not isinstance(rel_path, str) or not rel_path:
        return None

    return (repo_root / rel_path).resolve()


def validate_plugin_manifest(path: Path) -> tuple[dict[str, Any], list[str]]:
    manifest = load_json(path)
    errors: list[str] = []

    if manifest.get("name") != PLUGIN_NAME:
        errors.append(
            f"{repo_label(path)} name is {manifest.get('name')!r}, expected {PLUGIN_NAME!r}."
        )

    skills_rel = manifest.get("skills")
    if not isinstance(skills_rel, str) or not skills_rel:
        errors.append(f"{repo_label(path)} is missing a string 'skills' path.")
    else:
        skills_path = (path.parent.parent / skills_rel).resolve()
        if skills_path != SKILLS_ROOT.resolve():
            errors.append(
                f"{repo_label(path)} skills path resolves to {repo_label(skills_path)}, "
                f"expected {repo_label(SKILLS_ROOT)}."
            )
        elif not skills_path.exists():
            errors.append(
                f"{repo_label(path)} points to a missing skills path: {skills_rel}"
            )

    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        errors.append(f"{repo_label(path)} is missing an 'interface' object.")

    return manifest, errors


def validate_codex_metadata(repo_root: Path) -> list[str]:
    plugin_manifest_path = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
    marketplace_path = repo_root / ".agents" / "plugins" / "marketplace.json"
    _, errors = validate_plugin_manifest(plugin_manifest_path)
    marketplace = load_json(marketplace_path)

    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        errors.append(f"{repo_label(marketplace_path)} must contain exactly one plugin entry.")
        return errors

    entry = plugins[0]
    if not isinstance(entry, dict):
        errors.append(f"{repo_label(marketplace_path)} plugin entry 0 must be an object.")
        return errors

    if entry.get("name") != PLUGIN_NAME:
        errors.append(
            f"{repo_label(marketplace_path)} plugin entry is named "
            f"{entry.get('name')!r}, expected {PLUGIN_NAME!r}."
        )

    source = entry.get("source")
    if not isinstance(source, dict) or source.get("source") != "local":
        errors.append(
            f"{repo_label(marketplace_path)} plugin entry must use 'source.source': 'local'."
        )
    elif resolve_plugin_root(repo_root, entry) != PLUGIN_ROOT.resolve():
        errors.append(
            f"{repo_label(marketplace_path)} plugin entry must resolve to "
            f"{repo_label(PLUGIN_ROOT)}."
        )

    if not isinstance(source, dict) or source.get("path") != "./plugins/personal-skills":
        errors.append(
            f"{repo_label(marketplace_path)} plugin entry must use "
            "'source.path': './plugins/personal-skills'."
        )

    policy = entry.get("policy")
    if not isinstance(policy, dict):
        errors.append(f"{repo_label(marketplace_path)} plugin entry is missing 'policy'.")
    else:
        for field in ("installation", "authentication"):
            if field not in policy:
                errors.append(
                    f"{repo_label(marketplace_path)} plugin entry is missing "
                    f"'policy.{field}'."
                )

    if "category" not in entry:
        errors.append(f"{repo_label(marketplace_path)} plugin entry is missing 'category'.")

    return errors


def validate_claude_metadata(repo_root: Path) -> list[str]:
    marketplace_path = repo_root / ".claude-plugin" / "marketplace.json"
    actual_marketplace = load_json(marketplace_path)
    expected_marketplace = build_marketplace(SKILLS_ROOT)

    if actual_marketplace == expected_marketplace:
        return []

    diff = "\n".join(
        difflib.unified_diff(
            canonical_json(actual_marketplace).splitlines(),
            canonical_json(expected_marketplace).splitlines(),
            fromfile=repo_label(marketplace_path),
            tofile=f"generated/{repo_label(marketplace_path)}",
            lineterm="",
        )
    )
    return [
        f"{repo_label(marketplace_path)} is out of date with current plugin metadata.\n"
        f"{diff}"
    ]


def main() -> int:
    errors = [
        *validate_codex_metadata(REPO_ROOT),
        *validate_claude_metadata(REPO_ROOT),
    ]
    if errors:
        print("Plugin metadata validation failed.\n", file=sys.stderr)
        for error in errors:
            print(error, file=sys.stderr)
            print(file=sys.stderr)
        return 1

    skill_names = collect_skill_names(SKILLS_ROOT)
    print(
        "Plugin metadata validation passed: "
        f"{PLUGIN_NAME} with {len(skill_names)} skills "
        f"({', '.join(skill_names)})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
