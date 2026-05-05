"""assemble_md.py — paper-survey 阶段 4 markdown 组装入口。

Usage:
    python assemble_md.py <workdir> [--out <path>]

读取 <workdir>/_work/{survey_spec.md, outline.md, extracts/*.md}
输出 <workdir>/<slug>_综述报告.md（顶层）

替代旧 generate_survey.js + template_11chapters.js + build_table.js 三件套。仅依赖 Python 标准库。

Dry-run 自检：
- fenced JSON parse 成功
- LaTeX $ / $$ 配对（数量为偶数）

应用 Codex review 修订：
- B-01: chapter5_organization 优先匹配「选择：**xxx**」非枚举集合首值
- N-01: subtitle regex 支持 `[)）]` 全角括号
"""

import sys
import re
import json
import argparse
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def norm_method(s: str) -> str:
    """method 名归一化（B5 修复）：strip 末尾 .0 + 仅保留字母数字 + 小写"""
    if not s:
        return ""
    s = re.sub(r"\.0+$", "", s)
    s = re.sub(r"[^a-zA-Z0-9]", "", s)
    return s.lower()


def check_latex_pairing(text: str) -> bool:
    """$ / $$ 配对检测"""
    inline_text = re.sub(r"\$\$[\s\S]*?\$\$", "", text)
    inline_count = inline_text.count("$")
    display_count = text.count("$$")
    return (inline_count % 2 == 0) and (display_count % 2 == 0)


def parse_paper_list(md: str) -> list:
    m = re.search(r"## 论文清单[\s\S]*?\n((?:\|[^\n]+\n)+)", md)
    if not m:
        return []
    lines = m.group(1).strip().split("\n")
    papers = []
    for line in lines:
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if not cols or all(re.match(r"^:?-+:?$", c) for c in cols):
            continue
        if cols[0] == "#" or (len(cols) > 1 and cols[1] == "简称"):
            continue
        papers.append({
            "idx": cols[0],
            "method": cols[1] if len(cols) > 1 else "",
            "arxiv_id": cols[2] if len(cols) > 2 else "",
            "doi": cols[3] if len(cols) > 3 else "",
            "title": cols[4] if len(cols) > 4 else "",
            "first_author": cols[5] if len(cols) > 5 else "",
            "venue": cols[6] if len(cols) > 6 else "",
            "year": cols[7] if len(cols) > 7 else "",
            "pdf_filename": cols[8] if len(cols) > 8 else "",
        })
    return papers


def parse_spec_md(md: str, workdir: Path = None) -> dict:
    def get(re_pat, fallback=""):
        m = re.search(re_pat, md)
        return m.group(1).strip() if m else fallback

    title = get(r"\*\*主题（中文）\*\*[:：]\s*(.+)")
    # N-01 修复：支持全角右括号
    subtitle = get(r"\*\*主题（英文.*?[)）]\*\*[:：]\s*(.+)")
    tpl_branch = get(r"\*\*模板分支\*\*[:：]\s*(\S+)", "general-academic")
    if tpl_branch.startswith("non-technical"):
        tpl_branch = "non-technical"
    else:
        tpl_branch = "general-academic"

    # B-01 修复：优先匹配「选择：**method-taxonomy**」非枚举集合首值
    m_choice = re.search(r"选择[:：]\s*\*?\*?(timeline|method-taxonomy|subtask)\*?\*?", md)
    if m_choice:
        ch5_org = m_choice.group(1)
    else:
        m_eq = re.search(r"`chapter5_organization`\s*=\s*[\"\"“]([^\"\"”]+)[\"\"”]", md)
        if m_eq and m_eq.group(1) in ("timeline", "method-taxonomy", "subtask"):
            ch5_org = m_eq.group(1)
        else:
            ch5_org = "method-taxonomy"

    if workdir:
        slug = Path(workdir).name
    else:
        wd_abs = get(r"\*\*绝对路径\*\*[:：]\s*(.+)")
        wd_abs = re.sub(r"^[`'\"]+|[`'\"]+$", "", wd_abs)
        slug = Path(wd_abs.rstrip("/\\")).name if wd_abs else "survey"

    return {
        "title": title or "文献综述报告",
        "subtitle": subtitle,
        "template_branch": tpl_branch,
        "chapter5_organization": ch5_org,
        "slug": slug,
        "paper_list": parse_paper_list(md),
    }


def split_by_h2(md: str) -> dict:
    out = {}
    parts = re.split(r"^## ", md, flags=re.MULTILINE)
    for part in parts[1:]:
        lines = part.split("\n", 1)
        title = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""
        out[title] = body
    return out


def extract_h3_body(section_md: str, h3_title: str) -> str:
    pat = r"^### " + re.escape(h3_title) + r"\s*\n([\s\S]+?)(?=\n### |\n## |(?![\s\S]))"
    m = re.search(pat, section_md, re.MULTILINE)
    return m.group(1).strip() if m else ""


def parse_h3_subsections(section_md: str) -> list:
    subs = []
    matches = re.finditer(
        r"^### ([^\n]+)\n([\s\S]+?)(?=\n### |\n## |(?![\s\S]))",
        section_md,
        re.MULTILINE,
    )
    for m in matches:
        subs.append({"title": m.group(1).strip(), "content": m.group(2).strip()})
    return subs


def parse_chapter5(section_md: str) -> list:
    subs = []
    matches = re.finditer(
        r"^### ([^\n]+)\n([\s\S]+?)(?=\n### |\n## |(?![\s\S]))",
        section_md,
        re.MULTILINE,
    )
    for m in matches:
        title = m.group(1).strip()
        body = m.group(2)
        papers_block = re.search(r"```json\s*([\s\S]+?)```", body)
        papers, intro, summary = [], body, ""
        if papers_block:
            try:
                papers = json.loads(papers_block.group(1))
            except json.JSONDecodeError as e:
                raise ValueError(f"第 5 章子节 {title} fenced JSON 解析失败: {e}")
            parts = re.split(r"```json[\s\S]+?```", body, maxsplit=1)
            intro = parts[0].strip() if parts else body
            summary = parts[1].strip() if len(parts) > 1 else ""
        subs.append({"title": title, "intro": intro, "papers": papers, "summary": summary})
    return subs


def parse_outline_md(md: str) -> dict:
    sections = split_by_h2(md)

    abstract = sections.get("摘要", "").strip()
    keywords_raw = sections.get("关键词", "").strip()
    keywords = [k.strip() for k in re.split(r"[；;,，、 ]+", keywords_raw) if k.strip()]

    intro_section = sections.get("引言", "")
    intro = {
        "background": extract_h3_body(intro_section, "1.1 研究背景与意义"),
        "definition": extract_h3_body(intro_section, "1.2 问题定义"),
        "organization": extract_h3_body(intro_section, "1.3 本文组织结构"),
    }

    preliminaries = parse_h3_subsections(sections.get("相关概念与基础理论", ""))
    chapter5 = parse_chapter5(sections.get("国内外研究现状", ""))

    perf_section = sections.get("性能对比与分析", "")
    perf_block = re.search(r"```json\s*([\s\S]+?)```", perf_section)
    perf_table, perf_analysis, perf_fallback = [], "", ""
    if perf_block:
        try:
            perf_table = json.loads(perf_block.group(1))
        except json.JSONDecodeError as e:
            raise ValueError(f"第 7 章 fenced JSON 解析失败: {e}")
        perf_analysis = re.sub(r"```json[\s\S]+?```", "", perf_section).strip()
    else:
        perf_fallback = perf_section

    return {
        "abstract": abstract,
        "keywords": keywords,
        "intro": intro,
        "preliminaries": preliminaries,
        "chapter5": chapter5,
        "datasets": sections.get("数据集与评价指标", "").strip(),
        "performance_table": perf_table,
        "performance_analysis": perf_analysis,
        "performance_qualitative_fallback": perf_fallback,
        "challenges": sections.get("存在的问题与挑战", "").strip(),
        "future": sections.get("未来发展趋势与展望", "").strip(),
        "conclusion": sections.get("总结", "").strip(),
    }


def collect_references(extracts: list, paper_list: list) -> list:
    """B5 修复：method 名 norm 强化"""
    by_method = {}
    for ex in extracts:
        m = re.search(r"参考文献条目（GB/T\s*7714）[:：]\s*(.+)", ex["content"])
        if not m:
            continue
        method_m = re.search(r"^###\s*#?\d+\s+([^\n(（]+?)\s*[(（]", ex["content"], re.MULTILINE)
        if method_m:
            by_method[norm_method(method_m.group(1))] = m.group(1).strip()
    return [{
        "method": p["method"],
        "gb_t_7714": by_method.get(norm_method(p["method"]),
                                    f"[未匹配] {p['title']}, {p['first_author']}, {p['venue']} {p['year']}"),
    } for p in paper_list]


def load_extracts(extracts_dir: Path) -> list:
    if not extracts_dir.exists():
        return []
    return [
        {"filename": f.name, "content": f.read_text(encoding="utf-8")}
        for f in sorted(extracts_dir.glob("*.md"))
        if not f.name.startswith("_tmp")
    ]


def render_papers_block(papers: list) -> str:
    out = []
    for p in papers:
        method = p.get("method_name", "?")
        summary = p.get("summary_with_citations", "").strip()
        out.append(f"#### {method}\n\n{summary}\n")
    return "\n".join(out)


def render_pipe_table(rows: list) -> str:
    if not rows:
        return ""
    cols = ["method", "dataset", "metric", "value", "citation"]
    headers = ["方法", "数据集", "指标", "数值", "引用"]
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join(lines)


def render_references_section(refs: list) -> str:
    if not refs:
        return ""
    out = []
    for i, r in enumerate(refs, 1):
        out.append(f"[{i}] {r['gb_t_7714']}\n")
    return "\n".join(out)


def build_markdown(spec: dict, outline: dict, refs: list) -> str:
    parts = []
    title = spec["title"]
    if spec.get("subtitle"):
        title = f"{title}\n\n*{spec['subtitle']}*"
    parts.append(f"# {title}\n")

    parts.append(f"## 摘要\n\n{outline['abstract']}\n")
    parts.append(f"## 关键词\n\n{'；'.join(outline['keywords'])}\n")

    intro = outline["intro"]
    parts.append("## 引言\n")
    parts.append(f"### 1.1 研究背景与意义\n\n{intro['background']}\n")
    parts.append(f"### 1.2 问题定义\n\n{intro['definition']}\n")
    parts.append(f"### 1.3 本文组织结构\n\n{intro['organization']}\n")

    if spec["template_branch"] != "non-technical":
        parts.append("## 相关概念与基础理论\n")
        for i, sub in enumerate(outline["preliminaries"], 1):
            parts.append(f"### 2.{i} {sub['title']}\n\n{sub['content']}\n")

    parts.append("## 国内外研究现状\n")
    for sub in outline["chapter5"]:
        parts.append(f"### {sub['title']}\n")
        if sub["intro"]:
            parts.append(f"{sub['intro']}\n")
        papers_block = render_papers_block(sub["papers"])
        if papers_block:
            parts.append(papers_block)
        if sub["summary"]:
            parts.append(f"{sub['summary']}\n")

    parts.append(f"## 数据集与评价指标\n\n{outline['datasets']}\n")

    parts.append("## 性能对比与分析\n")
    if outline["performance_table"]:
        parts.append(render_pipe_table(outline["performance_table"]))
        parts.append("")
        if outline["performance_analysis"]:
            parts.append(outline["performance_analysis"])
    else:
        parts.append(outline.get("performance_qualitative_fallback") or "本章因可比数值不足，未生成性能对比表。")

    parts.append(f"\n## 存在的问题与挑战\n\n{outline['challenges']}\n")
    parts.append(f"## 未来发展趋势与展望\n\n{outline['future']}\n")
    parts.append(f"## 总结\n\n{outline['conclusion']}\n")
    parts.append(f"## 参考文献\n\n{render_references_section(refs)}\n")

    return "\n".join(parts)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="paper-survey 阶段 4 markdown 组装")
    parser.add_argument("workdir", help="工作目录绝对路径（含 _work/ 子目录）")
    parser.add_argument("--out", default=None, help="输出 md 路径")
    args = parser.parse_args(argv)

    workdir = Path(args.workdir).resolve()
    work_subdir = workdir / "_work"

    spec_path = work_subdir / "survey_spec.md"
    outline_path = work_subdir / "outline.md"
    extracts_dir = work_subdir / "extracts"

    if not spec_path.exists():
        print(json.dumps({"status": "error", "msg": f"spec 缺失: {spec_path}"}, ensure_ascii=False))
        return 1
    if not outline_path.exists():
        print(json.dumps({"status": "error", "msg": f"outline 缺失: {outline_path}"}, ensure_ascii=False))
        return 1

    try:
        spec = parse_spec_md(spec_path.read_text(encoding="utf-8"), workdir)
        outline = parse_outline_md(outline_path.read_text(encoding="utf-8"))
    except ValueError as e:
        print(json.dumps({"status": "error", "msg": f"解析失败: {e}"}, ensure_ascii=False))
        return 1

    extracts = load_extracts(extracts_dir)
    refs = collect_references(extracts, spec["paper_list"])
    md = build_markdown(spec, outline, refs)

    if not check_latex_pairing(md):
        print(json.dumps({"status": "error", "msg": "LaTeX $/$$ 配对失败"}, ensure_ascii=False))
        return 1

    out_path = Path(args.out) if args.out else workdir / f"{spec['slug']}_综述报告.md"
    out_path.write_text(md, encoding="utf-8")
    print(json.dumps({
        "status": "ok",
        "path": str(out_path),
        "size_bytes": out_path.stat().st_size,
        "cn_chars": len(re.findall(r"[一-鿿]", md)),
        "papers": len(spec["paper_list"]),
        "refs": len(refs),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
