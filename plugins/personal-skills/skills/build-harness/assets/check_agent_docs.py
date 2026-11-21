#!/usr/bin/env python3
"""检查仓库的 agent 文档体系：相对链接、Agent Notes 结构、常驻文档预算、归档冻结。

只依赖 Python 标准库。复制到目标仓库（如 scripts/check_agent_docs.py）后，
按目标仓库实际情况修改下方「配置」区；规则文字的出处是 docs/AGENTS.md
与 notes 目录的 README，两者与这里的配置必须保持一致。

用法：
    python3 scripts/check_agent_docs.py              # 运行全部检查
    python3 scripts/check_agent_docs.py links notes  # 只运行指定检查
    python3 scripts/check_agent_docs.py budgets --init AGENTS.md docs/AGENTS.md  # 首次建预算清单
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
# notes 根目录与生命周期 / 分类目录中允许的规则文件；其他文件按 note 检查或报错。
NOTE_META_FILES = {"AGENTS.md", "README.md", "CLAUDE.md"}
# 目录占位文件，任何位置都忽略（与规则文件白名单无关）。
PLACEHOLDER_FILES = {".gitkeep", ".keep"}
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


FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def prose_lines(text: str) -> list[tuple[int, str]]:
    """返回不在围栏代码块内的 (行号, 行)。

    按 CommonMark：围栏由 3 个以上同种字符开启，只被同种字符、长度不小于开启
    长度且其后只有空白的行关闭，因此四反引号块内的三反引号示例不会提前关闭。
    """
    out: list[tuple[int, str]] = []
    fence: str | None = None
    for no, line in enumerate(text.splitlines(), 1):
        m = FENCE.match(line)
        if fence is None:
            if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
                fence = m.group(1)
                continue
            out.append((no, line))
        elif m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) and not m.group(2).strip():
            fence = None
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

INLINE_CODE = re.compile(r"(?<!`)(`+)(?!`).*?(?<!`)\1(?!`)")
REF_DEF = re.compile(r"^ {0,3}\[[^\]]+\]:[ \t]*(.*)$")
EXTERNAL = re.compile(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|//|#)")


def read_destination(text: str, i: int) -> str | None:
    """从 text[i] 开始读取链接目标：`<...>` 形式可含空格，否则允许成对括号。"""
    while i < len(text) and text[i] in " \t":
        i += 1
    if i < len(text) and text[i] == "<":
        end = text.find(">", i + 1)
        return text[i + 1:end] if end != -1 else None
    depth, start = 0, i
    while i < len(text):
        ch = text[i]
        if ch == "\\" and i + 1 < len(text):
            i += 2
            continue
        if ch.isspace():
            break
        if ch == "(":
            depth += 1
        elif ch == ")":
            if depth == 0:
                break
            depth -= 1
        i += 1
    return text[start:i] or None


ESCAPE = re.compile(r"\\([!-/:-@\[-`{-~])")


def label_end(line: str, i: int) -> int:
    """line[i] 是未转义的 `[`，返回与之匹配的 `]` 下标；没有则返回 -1。"""
    depth = 0
    while i < len(line):
        ch = line[i]
        if ch == "\\":
            i += 2
            continue
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def line_targets(line: str) -> list[str]:
    """提取一行中的行内链接 / 图片目标和引用式定义目标，并按 Markdown 转义规则还原。

    只识别以未转义 `[` 开头、匹配到 `]` 且紧跟 `(` 的真正链接标签，
    因此普通文本中的 `](`、`\\[字面量](x)` 不会被当作链接。
    """
    ref = REF_DEF.match(line)
    if ref:
        dests = [read_destination(ref.group(1), 0)]
    else:
        dests, i = [], 0
        while i < len(line):
            ch = line[i]
            if ch == "\\":
                i += 2
                continue
            if ch == "[":
                end = label_end(line, i)
                if end != -1 and line[end + 1:end + 2] == "(":
                    dests.append(read_destination(line, end + 2))
            i += 1
    return [ESCAPE.sub(r"\1", d) for d in dests if d]


def check_links(report: Report) -> None:
    """相对链接的目标文件或目录必须存在（不检查锚点和外部 URL）。"""
    for path in markdown_files():
        for no, line in prose_lines(path.read_text(encoding="utf-8")):
            for target in line_targets(INLINE_CODE.sub("", line)):
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
    if not any((notes_root / name).is_file() for name in NOTE_META_FILES):
        report.add(NOTES_DIR, None, f"缺少 notes 规则文件（{sorted(NOTE_META_FILES)} 之一）；不使用这套 notes 布局时请从 CHECKS 移除 notes")
        return
    allowed_top = LIFECYCLES | {"archived"}
    for path in sorted(notes_root.rglob("*")):
        if path.is_dir() or path.name in PLACEHOLDER_FILES:
            continue
        parts = path.relative_to(notes_root).parts
        if len(parts) == 1:
            if parts[0] not in NOTE_META_FILES:
                report.add(path, None, f"notes 根目录只放规则文件 {sorted(NOTE_META_FILES)}；note 应放在 {{lifecycle}}/ 下")
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


def init_budgets(paths: list[str], headroom: float = 0.1) -> int:
    """为指定常驻文档按当前用量加余量生成预算清单。

    先校验全部参数再写文件：清单已存在、路径不在仓库内或不是文件时整体拒绝，
    不产生部分结果。清单只记录相对仓库根、以 `/` 分隔的路径，保证可移植。
    """
    manifest_path = ROOT / BUDGET_MANIFEST
    if manifest_path.exists():
        print(f"{BUDGET_MANIFEST} 已存在；调整上限请直接编辑该文件", file=sys.stderr)
        return 2
    rels: list[str] = []
    bad: list[str] = []
    for arg in paths:
        candidate = Path(arg)
        resolved = (candidate if candidate.is_absolute() else ROOT / candidate).resolve()
        try:
            rel = resolved.relative_to(ROOT).as_posix()
        except ValueError:
            bad.append(f"{arg}（不在仓库 {ROOT} 内）")
            continue
        if not resolved.is_file():
            bad.append(f"{arg}（不是已存在的文件）")
        elif rel not in rels:
            rels.append(rel)
    if bad:
        print("预算清单未写入，以下路径无效：\n  " + "\n  ".join(bad), file=sys.stderr)
        return 2
    manifest = {}
    for rel in rels:
        used = count_units((ROOT / rel).read_text(encoding="utf-8"))
        manifest[rel] = max(used + 1, int(used * (1 + headroom) + 0.999))
        print(f"{used:>6} -> {manifest[rel]:<6} {rel}")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已写入 {BUDGET_MANIFEST}")
    return 0


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
        if path.is_file() and path.name not in NOTE_META_FILES | PLACEHOLDER_FILES:
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

# 目标仓库不使用的机制从这里移除（例如沿用已有 ADR 时去掉 notes / archive，不设预算时去掉 budgets）。
CHECKS = ("links", "notes", "budgets", "archive")


def main() -> int:
    global ROOT
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("checks", nargs="*", help=f"可选：{', '.join(CHECKS)}；默认全部")
    parser.add_argument("--root", type=Path, help="仓库根目录（默认为脚本上一级目录）")
    parser.add_argument("--list", action="store_true", help="budgets：列出各文档用量")
    parser.add_argument("--write", action="store_true", help="archive：登记新的归档文件哈希")
    parser.add_argument("--init", nargs="+", metavar="DOC", help="budgets：按当前用量 +10%% 为这些文档生成预算清单")
    args = parser.parse_args()
    if args.root:
        ROOT = args.root.resolve()
    if args.init:
        if args.checks != ["budgets"] or args.list or args.write:
            print("--init 只能单独用于 `budgets --init DOC...`，不能与其他检查、--list 或 --write 同用", file=sys.stderr)
            return 2
        if "budgets" not in CHECKS:
            print("budgets 检查未启用（不在 CHECKS 中），不生成预算清单", file=sys.stderr)
            return 2
        return init_budgets(args.init)
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
