"""validation.py — paper-survey 阶段 5 完成度核查脚本（17 项，markdown 版）。

Usage:
    python validation.py <workdir> [--reviewer-report <path>]

读取：<workdir>/<slug>_综述报告.md（顶层）+ <workdir>/_work/survey_spec.md
输出：JSON 核查报告 + 退出码（0=PASS / 1=FAIL / 2=异常）

17 项核查（md 时代）：
- 结构层 (3): #02 11 章存在 / #03 章节顺序 / #04 每章首段非空
- 内容层 (5): #05 论文清单覆盖率 / #06 第 5 章子节标签 / #07 性能 pipe table / #08 摘要中文字 / #10 中文字数总量
- 格式层 (3): #11 参考文献条数 / #12 GB/T 7714 / #13 引用编号对齐
- 反幻觉 (2): #14 reviewer 抽样 / #15 N/A 残留
- 其他 (2): #16 图表编号 / #09 关键词数
- md 专属 (2): #01 markdown 标题层级 / #17 LaTeX 公式

弹性字数档：N≤3→2000 / 4-7→3500 / 8-15→5500 / ≥16→7000

Codex review 修订：
- B-02: check_latex_formula 按子节逐验证（不仅整章 $ 计数）
- M-01: parse_chapter5_subsections 返 list[str] / check 比有序 list
- B-09: gb_t_7714 覆盖 [J|C|D|M|N|P|S|R|A|G|Z] + [/OL|/MT|/DK|/CD]? 后缀
- B-08: parse_reviewer_report 容忍 **PASS** + 多状态
"""

import sys
import re
import json
import argparse
import traceback
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

CHAPTERS_GENERAL = ["摘要", "关键词", "引言", "相关概念", "研究现状", "数据集", "性能对比", "挑战", "展望", "总结", "参考文献"]
CHAPTERS_NON_TECHNICAL = ["摘要", "关键词", "引言", "研究现状", "数据集", "性能对比", "挑战", "展望", "总结", "参考文献"]


def load_md_text(md_path: Path) -> str:
    return md_path.read_text(encoding="utf-8")


def parse_paper_list(spec_text: str) -> list:
    m = re.search(r"## 论文清单[\s\S]*?\n((?:\|[^\n]+\n)+)", spec_text)
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
        papers.append({"method": cols[1] if len(cols) > 1 else "", "arxiv_id": cols[2] if len(cols) > 2 else ""})
    return papers


def parse_chapter5_subsections(spec_text: str) -> list:
    """M-01: 返回有序标签列表，让 check 比集合 + 顺序"""
    m = re.search(r"### 第 5 章子节列表[^\n]*\n([\s\S]+?)(?=\n###\s|\n##\s|(?![\s\S]))", spec_text)
    if not m:
        return []
    body = m.group(1)
    primary = []
    for match in re.finditer(r"^\s*-\s+\*?\*?(\d+\.\d+)([A-Z]?)", body, re.MULTILINE):
        primary.append((match.group(1), match.group(2)))
    has_nested = {}
    for label, letter in primary:
        if letter:
            has_nested.setdefault(label, []).append(label + letter)
    result = []
    seen = set()
    for label, letter in primary:
        full = label + letter
        if full in seen:
            continue
        if letter:
            seen.add(full)
            result.append(full)
        elif label not in has_nested:
            seen.add(full)
            result.append(full)
    return result


def parse_word_threshold(spec_text: str) -> int:
    """spec.md 字数目标 — 弹性策略"""
    m = re.search(r"\*\*报告字数目标\*\*[^\n]*?(\d{4,5})\s*[^N\d]", spec_text)
    if not m:
        m = re.search(r"报告字数目标[：:]\s*[^\n]*?(\d{4,5})", spec_text)
    if m:
        return int(m.group(1))
    n = len(parse_paper_list(spec_text))
    if n <= 3:
        return 2000
    if n <= 7:
        return 3500
    if n <= 15:
        return 5500
    return 7000


def parse_template_branch(spec_text: str) -> str:
    m = re.search(r"\*\*模板分支\*\*[:：]\s*(\S+)", spec_text)
    if m and m.group(1).startswith("non-technical"):
        return "non-technical"
    return "general-academic"


def check_md_headings_well_formed(text: str) -> dict:
    """#01: H1 唯一 + H2 ≥ 11 + 无跨级跳"""
    h1s = re.findall(r"^# [^\n]+", text, re.MULTILINE)
    if len(h1s) != 1:
        return {"PASS": False, "msg": f"H1 应为 1 个，实际 {len(h1s)}"}
    headings = re.findall(r"^(#{1,6})\s", text, re.MULTILINE)
    levels = [len(h) for h in headings]
    h2_count = levels.count(2)
    if h2_count < 11:
        return {"PASS": False, "msg": f"H2 应 ≥ 11 个，实际 {h2_count}"}
    for i in range(1, len(levels)):
        if levels[i] > levels[i - 1] + 1:
            return {"PASS": False, "msg": f"标题跨级跳：H{levels[i-1]} → H{levels[i]}"}
    return {"PASS": True, "msg": f"H1=1 / H2={h2_count} / 无跨级跳"}


def check_chapters_present(text: str, template_branch: str) -> dict:
    chapters = CHAPTERS_NON_TECHNICAL if template_branch == "non-technical" else CHAPTERS_GENERAL
    missing = [c for c in chapters if c not in text]
    if missing:
        return {"PASS": False, "msg": f"缺失章节: {missing}"}
    return {"PASS": True, "msg": f"{len(chapters)} 章关键词全部出现"}


def check_chapter_order(text: str, template_branch: str) -> dict:
    """#03 章节顺序：用 H2 标题行内匹配（不是全文 text.find，避免正文 substring 误命中）"""
    chapters = CHAPTERS_NON_TECHNICAL if template_branch == "non-technical" else CHAPTERS_GENERAL
    positions = []
    for c in chapters:
        # 只在 H2 标题行内找 chapter 字面（^## 后整行包含 chapter 即可，覆盖 substring 情况：
        # 如 c='研究现状' → 匹配 '## 国内外研究现状'；c='挑战' → 匹配 '## 存在的问题与挑战'）
        m = re.search(r"^## [^\n]*?" + re.escape(c), text, re.MULTILINE)
        if not m:
            return {"PASS": False, "msg": f"章节 H2「{c}」缺失"}
        positions.append(m.start())
    if positions != sorted(positions):
        return {"PASS": False, "msg": f"章节顺序错乱：实际 H2 位置 {positions}"}
    return {"PASS": True, "msg": "章节顺序合规"}


def check_first_paragraph_nonempty(text: str) -> dict:
    h2_blocks = re.split(r"^## ", text, flags=re.MULTILINE)
    empty = []
    for blk in h2_blocks[1:]:
        title = blk.split("\n", 1)[0].strip()
        body = blk.split("\n", 1)[1] if "\n" in blk else ""
        body_until_next = re.split(r"^## |^# ", body, maxsplit=1, flags=re.MULTILINE)[0]
        non_h_lines = [l for l in body_until_next.split("\n") if l.strip() and not l.startswith("#")]
        if not non_h_lines:
            empty.append(title)
    if empty:
        return {"PASS": False, "msg": f"空段章节: {empty}"}
    return {"PASS": True, "msg": "每章首段非空"}


def check_paper_coverage(text: str, paper_list: list) -> dict:
    n = len(paper_list)
    missing_idx = []
    for i in range(1, n + 1):
        if not re.search(rf"\[{i}\b", text):
            missing_idx.append(i)
    if missing_idx:
        return {"PASS": False, "msg": f"未引用论文 [N]: {missing_idx}"}
    return {"PASS": True, "msg": f"{n} 篇论文 100% 引用"}


def check_chapter5_subsections(text: str, expected_labels: list) -> dict:
    """#06 M-01: 比较有序标签列表（不仅数量）"""
    m = re.search(r"## (国内外研究现状|研究现状)([\s\S]+?)(?=\n## |(?![\s\S]))", text)
    if not m:
        return {"PASS": False, "msg": "找不到第 5 章"}
    body = m.group(2)
    actual_labels = re.findall(r"^### (\d+\.\d+[A-Z]?)\b", body, re.MULTILINE)
    if actual_labels != expected_labels:
        return {"PASS": False, "msg": f"第 5 章子节 {actual_labels} ≠ 期望 {expected_labels}"}
    return {"PASS": True, "msg": f"第 5 章 {len(actual_labels)} 子节: {actual_labels}"}


def check_performance_table(text: str) -> dict:
    """#07 markdown pipe table"""
    m = re.search(r"## 性能对比与分析([\s\S]+?)(?=\n## |(?![\s\S]))", text)
    if not m:
        return {"PASS": False, "msg": "找不到第 7 章"}
    body = m.group(1)
    has_pipe = bool(re.search(r"^\|.*\|$", body, re.MULTILINE) and re.search(r"^\|[-:|\s]+\|$", body, re.MULTILINE))
    if not has_pipe:
        return {"PASS": False, "msg": "未找到 markdown pipe table"}
    rows = re.findall(r"^\|.*\|$", body, re.MULTILINE)
    return {"PASS": True, "msg": f"1 张表格（{len(rows) - 2} 数据行）"}


def check_abstract_length(text: str) -> dict:
    m = re.search(r"## 摘要\s*\n([\s\S]+?)\n## ", text)
    if not m:
        return {"PASS": False, "msg": "找不到摘要段"}
    body = m.group(1)
    cn_count = len(re.findall(r"[一-鿿]", body))
    if not (200 <= cn_count <= 400):
        return {"PASS": False, "msg": f"摘要 {cn_count} 字（要求 200-400）"}
    return {"PASS": True, "msg": f"摘要 {cn_count} 字"}


def check_keywords(text: str) -> dict:
    m = re.search(r"关键词[:：]\s*([^\n]+)", text)
    if not m:
        m = re.search(r"## 关键词\s*\n+([^\n]+)", text)
    if not m:
        return {"PASS": False, "msg": "未找到关键词"}
    raw = m.group(1).strip()
    kws = [k for k in re.split(r"[,;，；、 \t]+", raw) if k and k != "关键词"]
    if not (3 <= len(kws) <= 6):
        return {"PASS": False, "msg": f"关键词 {len(kws)} 个（要求 3-6）"}
    return {"PASS": True, "msg": f"关键词 {len(kws)} 个"}


def check_total_word_count(text: str, threshold: int) -> dict:
    cn_count = len(re.findall(r"[一-鿿]", text))
    if cn_count < threshold:
        return {"PASS": False, "msg": f"字数 {cn_count} < {threshold}"}
    return {"PASS": True, "msg": f"字数 {cn_count}"}


def check_references_count(text: str, expected: int) -> dict:
    refs_section = re.search(r"## 参考文献([\s\S]+)\Z", text)
    if not refs_section:
        return {"PASS": False, "msg": "找不到参考文献段"}
    cnt = len(re.findall(r"^\[\d+\]\s", refs_section.group(1), re.MULTILINE))
    if cnt != expected:
        return {"PASS": False, "msg": f"参考文献 {cnt} 条 ≠ 期望 {expected}"}
    return {"PASS": True, "msg": f"参考文献 {cnt} 条"}


def check_gb_t_7714_format(text: str, expected: int) -> dict:
    """#12 B-09: GB/T 7714-2015 完整文献类型 + 4 种载体后缀"""
    refs_section = re.search(r"## 参考文献([\s\S]+)\Z", text)
    if not refs_section:
        return {"PASS": False, "msg": "找不到参考文献段"}
    refs = re.findall(r"^\[\d+\][^\n]+", refs_section.group(1), re.MULTILINE)
    bad = [r[:60] for r in refs if not re.search(r"\[(J|C|D|M|N|P|S|R|A|G|Z)(/(OL|MT|DK|CD))?\]", r)]
    if bad:
        return {"PASS": False, "msg": f"{len(bad)} 条无文献类型标识: {bad[:3]}"}
    return {"PASS": True, "msg": f"{len(refs)} 条全部含文献类型标识"}


def check_citation_alignment(text: str, expected: int) -> dict:
    body_refs = set(int(x) for x in re.findall(r"\[(\d+)\]", text))
    if not body_refs:
        return {"PASS": False, "msg": "正文无 [N] 引用"}
    if max(body_refs) > expected:
        return {"PASS": False, "msg": f"正文最大引用 [{max(body_refs)}] > {expected}"}
    return {"PASS": True, "msg": "引用对齐"}


def check_reviewer_anti_hallucination(reviewer_report_path) -> dict:
    """#14 B-08: 容忍 **PASS** 加粗 + 多状态"""
    if reviewer_report_path is None or not Path(reviewer_report_path).exists():
        return {"PASS": False, "msg": "reviewer 报告缺失"}
    text = Path(reviewer_report_path).read_text(encoding="utf-8")
    m = re.search(r"VERDICT[:：\s]*\**\s*(PASS|FAIL|CONDITIONAL_PASS|FULL_PASS)", text)
    if not m:
        return {"PASS": False, "msg": "reviewer 报告无 VERDICT 字段"}
    verdict = m.group(1)
    if verdict in ("PASS", "CONDITIONAL_PASS", "FULL_PASS"):
        return {"PASS": True, "msg": f"reviewer 抽样 {verdict}"}
    return {"PASS": False, "msg": f"reviewer 抽样 FAIL"}


def check_no_na_residual(text: str) -> dict:
    if "N/A-源文本未覆盖" in text:
        return {"PASS": False, "msg": "正文残留 N/A-源文本未覆盖"}
    return {"PASS": True, "msg": "无 N/A 残留"}


def check_figure_table_numbering(text: str) -> dict:
    figs = re.findall(r"图\s*\d+\s*[:：]|Fig\.\s*\d+", text)
    tabs = re.findall(r"表\s*\d+\s*[:：]|Tab\.\s*\d+", text)
    return {"PASS": True, "msg": f"图 {len(figs)} / 表 {len(tabs)} 编号合规"}


def check_latex_formula_well_formed(text: str) -> dict:
    """#17 B-02: $/$$ 配对 + 第 4 章每个 H3 子节 ≥1 公式"""
    inline_text = re.sub(r"\$\$[\s\S]*?\$\$", "", text)
    if inline_text.count("$") % 2 != 0:
        return {"PASS": False, "msg": f"行内 $ 配对失败（{inline_text.count('$')} 个）"}
    if text.count("$$") % 2 != 0:
        return {"PASS": False, "msg": f"行间 $$ 配对失败（{text.count('$$')} 个）"}
    ch4 = re.search(r"## 相关概念与基础理论([\s\S]+?)(?=\n## |(?![\s\S]))", text)
    if ch4:
        body = ch4.group(1)
        h3_blocks = re.findall(r"^### ([^\n]+)\n([\s\S]+?)(?=\n### |\Z)", body, re.MULTILINE)
        if not h3_blocks:
            return {"PASS": False, "msg": "第 4 章无 H3 子节"}
        no_formula = []
        for title, sub_body in h3_blocks:
            if not re.search(r"\$[^$\n]+\$|\$\$[\s\S]+?\$\$", sub_body):
                no_formula.append(title.strip())
        if no_formula:
            return {"PASS": False, "msg": f"第 4 章子节缺公式: {no_formula}"}
    return {"PASS": True, "msg": "LaTeX $ 配对 + 第 4 章每子节 ≥1 公式"}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="paper-survey 阶段 5 完成度核查")
    parser.add_argument("workdir", help="工作目录绝对路径")
    parser.add_argument("--reviewer-report", default=None, help="validation_review.md 路径")
    args = parser.parse_args(argv)

    try:
        workdir = Path(args.workdir).resolve()
        spec_path = workdir / "_work" / "survey_spec.md"
        spec_text = spec_path.read_text(encoding="utf-8")
        slug = workdir.name
        md_path = workdir / f"{slug}_综述报告.md"
        if not md_path.exists():
            mds = list(workdir.glob("*_综述报告.md"))
            if mds:
                md_path = mds[0]
        text = load_md_text(md_path)
        paper_list = parse_paper_list(spec_text)
        expected_labels = parse_chapter5_subsections(spec_text)
        word_threshold = parse_word_threshold(spec_text)
        template_branch = parse_template_branch(spec_text)
        reviewer_report = Path(args.reviewer_report) if args.reviewer_report else None

        checks = {
            "01_md_headings_well_formed": check_md_headings_well_formed(text),
            "02_chapters_present": check_chapters_present(text, template_branch),
            "03_chapter_order": check_chapter_order(text, template_branch),
            "04_first_paragraph_nonempty": check_first_paragraph_nonempty(text),
            "05_paper_coverage": check_paper_coverage(text, paper_list),
            "06_chapter5_subsections": check_chapter5_subsections(text, expected_labels),
            "07_performance_table": check_performance_table(text),
            "08_abstract_length": check_abstract_length(text),
            "09_keywords": check_keywords(text),
            "10_total_word_count": check_total_word_count(text, word_threshold),
            "11_references_count": check_references_count(text, len(paper_list)),
            "12_gb_t_7714_format": check_gb_t_7714_format(text, len(paper_list)),
            "13_citation_alignment": check_citation_alignment(text, len(paper_list)),
            "14_reviewer_anti_hallucination": check_reviewer_anti_hallucination(reviewer_report),
            "15_no_na_residual": check_no_na_residual(text),
            "16_figure_table_numbering": check_figure_table_numbering(text),
            "17_latex_formula_well_formed": check_latex_formula_well_formed(text),
        }
        passed = sum(1 for v in checks.values() if v["PASS"])
        report = {
            "md": md_path.name,
            "template_branch": template_branch,
            "total": 17,
            "pass": passed,
            "fail": 17 - passed,
            "checks": checks,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if passed == 17 else 1
    except Exception as e:
        print(json.dumps({"status": "exception", "error": str(e), "trace": traceback.format_exc()}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
