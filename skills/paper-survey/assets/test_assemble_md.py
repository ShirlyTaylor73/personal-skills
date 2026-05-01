"""test_assemble_md.py — assemble_md.py 单元/集成测试。

Usage:
    python test_assemble_md.py
"""

import sys
import re
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from assemble_md import (
    parse_spec_md,
    parse_outline_md,
    parse_chapter5,
    collect_references,
    build_markdown,
    norm_method,
    check_latex_pairing,
    main,
)

FIXTURE = Path(__file__).parent / "_test_fixture_vla"
results = []


def assert_eq(name, actual, expected):
    ok = actual == expected
    results.append((name, ok, f"expected={expected!r} actual={actual!r}" if not ok else ""))


def assert_in(name, needle, haystack):
    ok = needle in haystack
    results.append((name, ok, f"missing {needle!r}" if not ok else ""))


def assert_re(name, pattern, text):
    ok = bool(re.search(pattern, text))
    results.append((name, ok, f"regex {pattern!r} not in text" if not ok else ""))


def test_norm_method():
    assert_eq("norm RT-1==RT1", norm_method("RT-1"), norm_method("RT1"))
    assert_eq("norm GR00T N1==GR00TN1", norm_method("GR00T N1"), norm_method("GR00TN1"))
    assert_eq("norm RoboTwin2.0==RoboTwin2", norm_method("RoboTwin2.0"), norm_method("RoboTwin2"))
    assert_eq("norm PaLM-E==PaLME", norm_method("PaLM-E"), norm_method("PaLME"))


def test_parse_spec_md():
    spec_path = FIXTURE / "_work" / "survey_spec.md"
    spec = parse_spec_md(spec_path.read_text(encoding="utf-8"), workdir=FIXTURE)
    assert_eq("spec.paper_count", len(spec["paper_list"]), 14)
    # B-01: 必须返回 method-taxonomy 而非 timeline
    assert_eq("spec.chapter5_org B-01", spec["chapter5_organization"], "method-taxonomy")
    assert_eq("spec.template_branch", spec["template_branch"], "general-academic")
    assert_eq("spec.slug", spec["slug"], "_test_fixture_vla")


def test_parse_outline_md_h2():
    outline_path = FIXTURE / "_work" / "outline.md"
    outline = parse_outline_md(outline_path.read_text(encoding="utf-8"))
    keys = ["abstract", "keywords", "intro", "preliminaries", "chapter5",
            "datasets", "performance_table", "challenges", "future", "conclusion"]
    for k in keys:
        assert_in(f"outline has {k}", k, list(outline.keys()))
    assert_eq("outline.keywords ≥ 4", len(outline["keywords"]) >= 4, True)


def test_parse_chapter5_subsections():
    """N-02: fixture VLA 二级切分覆盖完整（5.1 / 5.2A / 5.2B / 5.3 顺序）"""
    outline_path = FIXTURE / "_work" / "outline.md"
    outline = parse_outline_md(outline_path.read_text(encoding="utf-8"))
    assert_eq("ch5 subsection count", len(outline["chapter5"]), 4)
    titles = [s["title"] for s in outline["chapter5"]]
    title_str = " ".join(titles)
    assert_re("ch5 has 5.1", r"5\.1\b", title_str)
    assert_re("ch5 has 5.2A", r"5\.2A\b", title_str)
    assert_re("ch5 has 5.2B", r"5\.2B\b", title_str)
    assert_re("ch5 has 5.3", r"5\.3\b", title_str)
    pos = lambda label: title_str.index(label) if label in title_str else -1
    assert_eq("ch5 order 5.1 < 5.2A", pos("5.1") < pos("5.2A"), True)
    assert_eq("ch5 order 5.2A < 5.2B", pos("5.2A") < pos("5.2B"), True)
    assert_eq("ch5 order 5.2B < 5.3", pos("5.2B") < pos("5.3"), True)
    for s in outline["chapter5"]:
        assert_eq(f"ch5 {s['title']} has papers", len(s["papers"]) >= 1, True)


def test_parse_chapter5_does_not_truncate():
    """B4 回归：原 generate_survey.js gm-flag $ 截断 bug。每子节正文应 ≥ 500 chars"""
    outline_path = FIXTURE / "_work" / "outline.md"
    outline = parse_outline_md(outline_path.read_text(encoding="utf-8"))
    body_lengths = [len(s["intro"]) + sum(len(p["summary_with_citations"]) for p in s["papers"]) for s in outline["chapter5"]]
    assert_eq("ch5 subsection bodies ≥ 500 chars each", all(L >= 500 for L in body_lengths), True)


def test_collect_references_norm_match():
    """B5 回归：method 名 norm 匹配（RT-1/RT1, GR00T N1/GR00TN1, RoboTwin2.0/RoboTwin2）"""
    spec_path = FIXTURE / "_work" / "survey_spec.md"
    spec = parse_spec_md(spec_path.read_text(encoding="utf-8"), workdir=FIXTURE)
    extract_files = sorted((FIXTURE / "_work" / "extracts").glob("group_*.md"))
    extracts = [{"filename": f.name, "content": f.read_text(encoding="utf-8")} for f in extract_files if not f.name.startswith("_tmp")]
    refs = collect_references(extracts, spec["paper_list"])
    unmatched = [r for r in refs if r["gb_t_7714"].startswith("[未匹配]")]
    assert_eq("collect_references no unmatched", len(unmatched), 0)


def test_build_markdown_includes_chapter5_papers():
    spec_path = FIXTURE / "_work" / "survey_spec.md"
    outline_path = FIXTURE / "_work" / "outline.md"
    spec = parse_spec_md(spec_path.read_text(encoding="utf-8"), workdir=FIXTURE)
    outline = parse_outline_md(outline_path.read_text(encoding="utf-8"))
    extract_files = sorted((FIXTURE / "_work" / "extracts").glob("group_*.md"))
    extracts = [{"filename": f.name, "content": f.read_text(encoding="utf-8")} for f in extract_files if not f.name.startswith("_tmp")]
    refs = collect_references(extracts, spec["paper_list"])
    md = build_markdown(spec, outline, refs)
    methods_to_check = ["R3M", "RT", "RoboAgent", "ACT", "PaLM", "OpenVLA", "GR00T", "Pi0", "DiffusionPolicy", "GenieEnvisioner", "RoboTwin"]
    for m in methods_to_check:
        assert_in(f"final md contains {m}", m, md)
    cn_count = len(re.findall(r"[一-鿿]", md))
    assert_eq("final md cn chars ≥ 5500", cn_count >= 5500, True)


def test_build_markdown_pipe_table():
    spec_path = FIXTURE / "_work" / "survey_spec.md"
    outline_path = FIXTURE / "_work" / "outline.md"
    spec = parse_spec_md(spec_path.read_text(encoding="utf-8"), workdir=FIXTURE)
    outline = parse_outline_md(outline_path.read_text(encoding="utf-8"))
    md = build_markdown(spec, outline, [])
    perf_section = re.search(r"## 性能对比与分析[\s\S]+?(?=\n## |\Z)", md)
    assert_eq("perf section exists", perf_section is not None, True)
    if perf_section:
        assert_re("pipe table separator |---|", r"\|[-:]+\|", perf_section.group(0))


def test_build_markdown_references_section():
    spec_path = FIXTURE / "_work" / "survey_spec.md"
    outline_path = FIXTURE / "_work" / "outline.md"
    spec = parse_spec_md(spec_path.read_text(encoding="utf-8"), workdir=FIXTURE)
    outline = parse_outline_md(outline_path.read_text(encoding="utf-8"))
    extract_files = sorted((FIXTURE / "_work" / "extracts").glob("group_*.md"))
    extracts = [{"filename": f.name, "content": f.read_text(encoding="utf-8")} for f in extract_files if not f.name.startswith("_tmp")]
    refs = collect_references(extracts, spec["paper_list"])
    md = build_markdown(spec, outline, refs)
    refs_section = re.search(r"## 参考文献[\s\S]+\Z", md)
    assert_eq("refs section exists", refs_section is not None, True)
    if refs_section:
        assert_re("refs has [1]", r"\[1\]\s", refs_section.group(0))
        assert_re("refs has [14]", r"\[14\]\s", refs_section.group(0))


def test_dry_run_detects_malformed_json():
    bad_workdir = FIXTURE.parent / "_test_fixture_bad"
    bad_workdir.mkdir(exist_ok=True)
    (bad_workdir / "_work").mkdir(exist_ok=True)
    (bad_workdir / "_work" / "extracts").mkdir(exist_ok=True)
    (bad_workdir / "_work" / "outline.md").write_text(
        "# Outline\n\n## 摘要\n\nabc\n\n## 关键词\n\na;b;c\n\n## 引言\n\n### 1.1 研究背景与意义\n\nx\n\n### 1.2 问题定义\n\nx\n\n### 1.3 本文组织结构\n\nx\n\n## 国内外研究现状\n\n### 5.1 子节\n\n```json\n[BROKEN JSON\n```\n\n## 总结\n\nend",
        encoding="utf-8"
    )
    (bad_workdir / "_work" / "survey_spec.md").write_text(
        "# spec\n**主题（中文）**：test\n**报告字数目标**：2000\n## 论文清单\n\n| # | 简称 |\n|---|---|\n| 1 | A |\n",
        encoding="utf-8"
    )
    rc = main([str(bad_workdir)])
    assert_eq("malformed JSON main exit non-zero", rc != 0, True)
    import shutil
    shutil.rmtree(bad_workdir, ignore_errors=True)


def test_latex_formula_pairing_check():
    assert_eq("balanced $", check_latex_pairing("a $x$ b $y$ c"), True)
    assert_eq("unbalanced $", check_latex_pairing("a $x$ b $y c"), False)
    assert_eq("balanced $$", check_latex_pairing("a\n$$x$$\nb"), True)
    assert_eq("unbalanced $$", check_latex_pairing("a\n$$x\n"), False)


def test_main_writes_top_level_md():
    rc = main([str(FIXTURE)])
    assert_eq("main exit code", rc, 0)
    out_path = FIXTURE / "_test_fixture_vla_综述报告.md"
    assert_eq("output md exists", out_path.exists(), True)
    if out_path.exists():
        out_md = out_path.read_text(encoding="utf-8")
        assert_eq("output md non-empty", len(out_md) > 1000, True)


if __name__ == "__main__":
    test_funcs = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for fn in test_funcs:
        try:
            fn()
        except Exception as e:
            results.append((fn.__name__ + " (raised)", False, str(e)))

    passed = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - passed
    for name, ok, msg in results:
        flag = "PASS" if ok else "FAIL"
        print(f"  [{flag}] {name}{('  ' + msg) if msg else ''}")
    print(f"\nTotal: {passed} passed / {failed} failed")
    sys.exit(0 if failed == 0 else 1)
