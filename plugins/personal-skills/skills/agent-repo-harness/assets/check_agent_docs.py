#!/usr/bin/env python3
"""检查仓库的 agent 文档体系：相对链接、Agent Notes 结构、常驻文档预算、归档冻结。

只依赖 Python 标准库。复制到目标仓库（如 scripts/check_agent_docs.py）后，
按目标仓库实际情况修改下方「配置」区；规则文字的出处是 docs/AGENTS.md
与 notes 目录的 README，两者与这里的配置必须保持一致。

用法：
    python3 scripts/check_agent_docs.py              # 运行全部检查
    python3 scripts/check_agent_docs.py links notes  # 只运行指定检查
    python3 scripts/check_agent_docs.py budgets --list
    python3 scripts/check_agent_docs.py archive --write  # 归档新 note 后登记哈希

发现问题时逐条输出「文件:行号: 原因」并以退出码 1 结束；配置错误退出码 2。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

# ---------------------------------------------------------------- 配置 ----

# 仓库根目录：默认脚本位于 <root>/scripts/ 下。
ROOT = Path(__file__).resolve().parents[1]

# 不扫描的目录（相对根目录的路径前缀或任意层级的目录名）。
EXCLUDE_DIR_NAMES = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__"}
EXCLUDE_PATH_PREFIXES: list[str] = []  # 例如 ["vendor/", "docs/generated/"]

NOTES_DIR = ".agents/notes"
NOTE_CLASSES = {"feature", "bug-fix", "simplification", "architecture", "process", "testing"}
# 为空集合表示不分类，路径为 {lifecycle}/YYYY-MM-DD-slug.md。

# 节名需与 notes README 中写的一致；可改为英文（Problem / Decision ...）。
SEC_PROBLEM = "## 问题"
SEC_ALTERNATIVES = "## 备选方案"
REQUIRED_SECTIONS = {
    "proposed": ["## 方案", "## 验收标准", "## 风险"],
    "implemented": ["## 决策", "## 影响"],
    "rejected": ["## 方案"],
}
BANNED_IN_IMPLEMENTED = ["## 方案", "## 计划", "## 迁移计划", "## 验收标准"]
STATUS_PATTERNS = {
    "proposed": re.compile(r"^Status: proposed$"),
    "implemented": re.compile(r"^Status: implemented$"),
    "rejected": re.compile(r"^Status: rejected — \S.*$"),
}

BUDGET_MANIFEST = "scripts/doc-budgets.json"  # {"AGENTS.md": 1800, ...}
ARCHIVE_LOCK = "scripts/archived-notes.lock.json"  # {"路径": "sha256", ...}

# ------------------------------------------------------------ 公共工具 ----

NOTE_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
LIFECYCLES = set(REQUIRED_SECTIONS)
NOTE_META_FILES = {"AGENTS.md", "README.md", "CLAUDE.md", ".gitkeep"}
CJK = re.compile(r"[㐀-䶿一-鿿豈-﫿　-〿＀-￯]")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def add(self, path: Path | str, line: int | None, msg: str) -> None:
        rel = path if isinstance(path, str) else rel_path(path)
        loc = f"{rel}:{line}" if line else rel
        self.errors.append(f"{loc}: {msg}")


def rel_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def is_excluded(rel: str) -> bool:
    parts = rel.split("/")
    if any(p in EXCLUDE_DIR_NAMES for p in parts[:-1]):
        return True
    return any(rel.startswith(prefix) for prefix in EXCLUDE_PATH_PREFIXES)


def archived_prefix() -> str:
    return f"{NOTES_DIR.strip('/')}/archived/"


def markdown_files() -> list[Path]:
    files = []
    for path in sorted(ROOT.rglob("*.md")):
        rel = rel_path(path)
        if is_excluded(rel) or rel.startswith(archived_prefix()):
            continue
        files.append(path)
    return files


def prose_lines(text: str) -> list[tuple[int, str]]:
    """返回不在围栏代码块内的 (行号, 行)。"""
    out, fence = [], None
    for no, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip()
        marker = stripped[:3]
        if marker in ("```", "~~~"):
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            continue
        if fence is None:
            out.append((no, line))
    return out


def load_json(rel: str, report: Report) -> dict | None:
    path = ROOT / rel
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        report.add(rel, None, f"JSON 无法解析：{exc}")
        return None
    if not isinstance(data, dict):
        report.add(rel, None, "顶层必须是 JSON 对象")
        return None
    return data


# --------------------------------------------------------------- links ----

INLINE_CODE = re.compile(r"`[^`]*`")
LINK = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
REF_DEF = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?(?:\s+.*)?$")
EXTERNAL = re.compile(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|//|#)")


def check_links(report: Report) -> None:
    """相对链接的目标文件或目录必须存在（不检查锚点和外部 URL）。"""
    for path in markdown_files():
        for no, line in prose_lines(path.read_text(encoding="utf-8")):
            line = INLINE_CODE.sub("", line)
            targets = LINK.findall(line)
            ref = REF_DEF.match(line)
            if ref:
                targets.append(ref.group(1))
            for target in targets:
                if EXTERNAL.match(target):
                    continue
                file_part = target.split("#", 1)[0].split("?", 1)[0]
                if not file_part:
                    continue
                file_part = unquote(file_part)
                base = ROOT if file_part.startswith("/") else path.parent
                resolved = (base / file_part.lstrip("/")).resolve()
                if not resolved.exists():
                    report.add(path, no, f"链接目标不存在：{target}")


# --------------------------------------------------------------- notes ----


def check_notes(report: Report) -> None:
    """notes 的路径、分类、状态行与目录一致性、生命周期必需节。"""
    notes_root = ROOT / NOTES_DIR
    if not notes_root.exists():
        report.add(NOTES_DIR, None, "notes 目录不存在（若不使用 notes，请从检查列表中移除 notes）")
        return
    allowed_top = LIFECYCLES | {"archived"}
    for path in sorted(notes_root.rglob("*")):
        if path.is_dir():
            continue
        parts = path.relative_to(notes_root).parts
        if len(parts) == 1:
            if parts[0] not in NOTE_META_FILES and not parts[0].endswith(".md"):
                report.add(path, None, "notes 根目录只放规则文件")
            continue
        lifecycle = parts[0]
        if lifecycle not in allowed_top:
            report.add(path, None, f"未知的生命周期目录 {lifecycle!r}，允许：{sorted(allowed_top)}")
            continue
        if parts[-1] in NOTE_META_FILES:
            continue
        expected_depth = 3 if NOTE_CLASSES else 2
        if len(parts) != expected_depth:
            layout = "{lifecycle}/{class}/" if NOTE_CLASSES else "{lifecycle}/"
            report.add(path, None, f"路径应为 {layout}YYYY-MM-DD-topic.md")
            continue
        if NOTE_CLASSES and parts[1] not in NOTE_CLASSES:
            report.add(path, None, f"未知分类 {parts[1]!r}，允许：{sorted(NOTE_CLASSES)}")
        if not NOTE_NAME.match(parts[-1]):
            report.add(path, None, "文件名应为 YYYY-MM-DD-小写连字符标题.md")
        if lifecycle == "archived":
            continue  # 冻结内容由 archive 检查负责
        check_note_body(path, lifecycle, report)


def check_note_body(path: Path, lifecycle: str, report: Report) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    head = lines + [""] * 4
    if not head[0].startswith("# Agent Note: ") or not head[0][14:].strip():
        report.add(path, 1, "第 1 行必须是 `# Agent Note: <标题>`")
    if head[1] != "":
        report.add(path, 2, "第 2 行必须为空")
    if not STATUS_PATTERNS[lifecycle].match(head[2]):
        report.add(path, 3, f"状态行与所在目录 {lifecycle}/ 不符：{head[2]!r}")
    if head[3] != "":
        report.add(path, 4, "第 4 行必须为空")

    prose = prose_lines("\n".join(lines))
    h2 = [(no, l.rstrip()) for no, l in prose if l.startswith("## ")]
    names = [l for _, l in h2]
    if not names or names[0] != SEC_PROBLEM:
        report.add(path, h2[0][0] if h2 else None, f"第一个二级标题必须是 `{SEC_PROBLEM}`")
    for section in REQUIRED_SECTIONS[lifecycle] + [SEC_ALTERNATIVES]:
        if section not in names:
            report.add(path, None, f"缺少必需节 `{section}`")
    if lifecycle == "implemented":
        for no, name in h2:
            if name in BANNED_IN_IMPLEMENTED:
                report.add(path, no, f"implemented note 不应包含提案期节 `{name}`，请改写为现在时的决策 / 影响")
    extra_status = [no for no, l in prose if l.startswith("Status:") and no != 3]
    for no in extra_status:
        report.add(path, no, "只允许第 3 行出现 Status 行")


# ------------------------------------------------------------- budgets ----


def count_units(text: str) -> int:
    """每个 CJK 字符计 1，其余按空白分隔的词计 1。"""
    cjk = len(CJK.findall(text))
    rest = CJK.sub(" ", text)
    return cjk + len(rest.split())


def check_budgets(report: Report, list_only: bool) -> None:
    """只约束清单中列出的常驻文档；清单内文件缺失同样失败。"""
    manifest = load_json(BUDGET_MANIFEST, report)
    if manifest is None:
        if not (ROOT / BUDGET_MANIFEST).exists():
            report.add(BUDGET_MANIFEST, None, "预算清单不存在")
        return
    for rel, ceiling in manifest.items():
        if not isinstance(ceiling, int) or isinstance(ceiling, bool) or ceiling <= 0:
            report.add(BUDGET_MANIFEST, None, f"{rel} 的上限必须是正整数，当前为 {ceiling!r}")
            continue
        path = ROOT / rel
        if not path.exists():
            report.add(rel, None, f"预算清单中的文件不存在（改名或删除时请同步更新 {BUDGET_MANIFEST}）")
            continue
        used = count_units(path.read_text(encoding="utf-8"))
        if list_only:
            flag = "ok  " if used <= ceiling else "OVER"
            print(f"{flag} {used:>6} / {ceiling:<6} {rel}")
        elif used > ceiling:
            report.add(rel, None, f"{used} 超过上限 {ceiling}：先迁移到正确的层，再压缩，确有必要才在说明理由后提高上限")


# ------------------------------------------------------------- archive ----


def archived_files() -> dict[str, str]:
    root = ROOT / NOTES_DIR / "archived"
    if not root.exists():
        return {}
    out = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name not in NOTE_META_FILES:
            out[rel_path(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out


def check_archive(report: Report, write: bool) -> None:
    """归档 note 一经登记即冻结：内容不变、不删除；新归档文件需登记。"""
    lock_path = ROOT / ARCHIVE_LOCK
    lock = load_json(ARCHIVE_LOCK, report) if lock_path.exists() else {}
    if lock is None:
        return
    current = archived_files()
    for rel, digest in lock.items():
        if rel not in current:
            report.add(rel, None, "已冻结的归档 note 被删除或移动")
        elif current[rel] != digest:
            report.add(rel, None, "已冻结的归档 note 内容被修改")
    new = {rel: d for rel, d in current.items() if rel not in lock}
    for rel in new:
        text = (ROOT / rel).read_text(encoding="utf-8").splitlines() + [""] * 4
        if text[2] != "Status: implemented" or not re.match(r"^Archived: \d{4}-\d{2}-\d{2}$", text[3]):
            report.add(rel, 3, "归档 note 的第 3、4 行应为 `Status: implemented` 与 `Archived: YYYY-MM-DD`")
    if write:
        if report.errors:
            return  # 有错误时不写入，避免把破坏冻结的状态登记进去
        merged = {**lock, **new}
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"已登记 {len(new)} 个新归档文件到 {ARCHIVE_LOCK}")
    else:
        for rel in new:
            report.add(rel, None, "新的归档 note 尚未登记，确认归档无误后运行 `archive --write`")


# ---------------------------------------------------------------- main ----

CHECKS = ("links", "notes", "budgets", "archive")


def main() -> int:
    global ROOT
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("checks", nargs="*", help=f"可选：{', '.join(CHECKS)}；默认全部")
    parser.add_argument("--root", type=Path, help="仓库根目录（默认为脚本上一级目录）")
    parser.add_argument("--list", action="store_true", help="budgets：列出各文档用量")
    parser.add_argument("--write", action="store_true", help="archive：登记新的归档文件哈希")
    args = parser.parse_args()
    if args.root:
        ROOT = args.root.resolve()
    selected = args.checks or list(CHECKS)
    unknown = [c for c in selected if c not in CHECKS]
    if unknown:
        print(f"未知检查：{unknown}，可选：{list(CHECKS)}", file=sys.stderr)
        return 2

    report = Report()
    if "links" in selected:
        check_links(report)
    if "notes" in selected:
        check_notes(report)
    if "budgets" in selected:
        check_budgets(report, args.list)
    if "archive" in selected:
        check_archive(report, args.write)

    if report.errors:
        print(f"文档检查失败（{len(report.errors)} 处）：", file=sys.stderr)
        for err in report.errors:
            print(f"  {err}", file=sys.stderr)
        print("规则见 docs/AGENTS.md 与 notes 目录的 README。", file=sys.stderr)
        return 1
    print(f"文档检查通过：{', '.join(selected)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
