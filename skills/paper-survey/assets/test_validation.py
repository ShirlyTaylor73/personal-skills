"""test_validation.py — validation.py md 版单元/集成测试"""

import sys
import re
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from validation import (
    load_md_text,
    check_md_headings_well_formed,
    check_chapters_present,
    check_chapter_order,
    check_first_paragraph_nonempty,
    check_paper_coverage,
    check_chapter5_subsections,
    check_performance_table,
    check_abstract_length,
    check_keywords,
    check_total_word_count,
    check_references_count,
    check_gb_t_7714_format,
    check_citation_alignment,
    check_reviewer_anti_hallucination,
    check_no_na_residual,
    check_figure_table_numbering,
    check_latex_formula_well_formed,
    parse_paper_list,
    parse_chapter5_subsections,
    parse_word_threshold,
    parse_template_branch,
    main,
)

FIXTURE = Path(__file__).parent / "_test_fixture_vla"
FIXTURE_MD = FIXTURE / "_test_fixture_vla_综述报告.md"
SPEC_MD = FIXTURE / "_work" / "survey_spec.md"

results = []


def assert_eq(name, actual, expected):
    ok = actual == expected
    results.append((name, ok, f"expected={expected!r} actual={actual!r}" if not ok else ""))


def assert_pass(name, check_result):
    ok = check_result.get("PASS") is True
    results.append((name, ok, check_result.get("msg", "") if not ok else ""))


def test_load_md_text():
    text = load_md_text(FIXTURE_MD)
    assert_eq("md text non-empty", len(text) > 1000, True)


def test_md_headings_well_formed():
    text = load_md_text(FIXTURE_MD)
    assert_pass("01 md_headings_well_formed", check_md_headings_well_formed(text))


def test_chapters_present():
    text = load_md_text(FIXTURE_MD)
    assert_pass("02 chapters_present", check_chapters_present(text, "general-academic"))


def test_chapter5_subsections_match():
    """M-01: parse_chapter5_subsections 返 list[str] / check 比有序 list"""
    text = load_md_text(FIXTURE_MD)
    spec = SPEC_MD.read_text(encoding="utf-8")
    expected = parse_chapter5_subsections(spec)
    assert_eq("expected labels from spec", expected, ["5.1", "5.2A", "5.2B", "5.3"])
    assert_pass("06 chapter5_subsections", check_chapter5_subsections(text, expected))


def test_chapter5_label_mismatch_fails():
    """M-01 反例：5.1/5.2/5.3/5.4 数量为 4 但与期望 5.1/5.2A/5.2B/5.3 不等必须 FAIL"""
    bad_text = "## 国内外研究现状\n\n### 5.1 a\n\n### 5.2 b\n\n### 5.3 c\n\n### 5.4 d\n\n## 数据集与评价指标\nx"
    expected_labels = ["5.1", "5.2A", "5.2B", "5.3"]
    r = check_chapter5_subsections(bad_text, expected_labels)
    assert_eq("06 mismatch FAILs (5.1/5.2/5.3/5.4 vs 5.1/5.2A/5.2B/5.3)", r["PASS"], False)


def test_performance_pipe_table():
    text = load_md_text(FIXTURE_MD)
    assert_pass("07 performance_table (pipe)", check_performance_table(text))


def test_total_word_count_elastic():
    text = load_md_text(FIXTURE_MD)
    spec = SPEC_MD.read_text(encoding="utf-8")
    threshold = parse_word_threshold(spec)
    assert_eq("threshold N=14 elastic 5500", threshold, 5500)
    assert_pass("10 total_word_count", check_total_word_count(text, threshold))


def test_gb_t_7714_includes_J_OL():
    """B-09: J/OL 等组合载体应被识别"""
    sample = "## 参考文献\n\n[1] FOO. Title[J]. arXiv 2024.\n\n[2] BAR. Title2[J/OL]. preprint 2025.\n\n[3] BAZ. Title3[C/OL]. 2025.\n"
    r = check_gb_t_7714_format(sample, expected=3)
    assert_pass("12 gb_t_7714 with /OL", r)


def test_latex_formula_well_formed_returns_dict():
    """fixture md 来自旧 docx 时代 outline，无公式 → 预期 FAIL，但应返回 dict 不抛异常"""
    text = load_md_text(FIXTURE_MD)
    r = check_latex_formula_well_formed(text)
    assert_eq("17 latex_formula returns dict", isinstance(r, dict) and "PASS" in r, True)


def test_latex_formula_per_subsection_required():
    """B-02: 第 4 章每子节 ≥1 公式，仅整章 ≥2 不够"""
    # 反例：2.1 有 2 公式，2.2 无公式 → 整章 ≥2 但子节级别 FAIL
    bad_text = (
        "# T\n\n## 摘要\nx\n\n## 关键词\na;b;c;d\n\n## 引言\n\n### 1.1 研究背景与意义\nx\n\n"
        "### 1.2 问题定义\nx\n\n### 1.3 本文组织结构\nx\n\n"
        "## 相关概念与基础理论\n\n"
        "### 2.1 子节A\n损失 $\\mathcal{L} = 1$ 和 $f(x) = x$\n\n"
        "### 2.2 子节B\n纯文字无公式\n\n"
        "## 国内外研究现状\n\n### 5.1 a\nx\n\n## 数据集与评价指标\nx\n\n"
        "## 性能对比与分析\nx\n\n## 存在的问题与挑战\nx\n\n## 未来发展趋势与展望\nx\n\n## 总结\nx\n\n"
        "## 参考文献\n[1] x.\n"
    )
    r = check_latex_formula_well_formed(bad_text)
    assert_eq("17 per-subsection enforcement", r["PASS"], False)
    # 反例：2.1 + 2.2 都有公式 → PASS
    good_text = bad_text.replace("### 2.2 子节B\n纯文字无公式\n", "### 2.2 子节B\n含公式 $g(x) = x^2$\n")
    r2 = check_latex_formula_well_formed(good_text)
    assert_eq("17 per-subsection PASS when both have formula", r2["PASS"], True)


def test_latex_formula_unbalanced_fails():
    bad = "## 相关概念与基础理论\n\n### 2.1 a\n$x = 1\n"
    r = check_latex_formula_well_formed(bad)
    assert_eq("17 unbalanced $ FAILs", r["PASS"], False)


def test_reviewer_report_bold_pass(tmp_path=None):
    """B-08: parse_reviewer_report 容忍 **PASS** 加粗 + 多状态"""
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("# Validation Reviewer Report\n\n- VERDICT：**PASS**\n\n## 抽样汇总\n抽样 47/47\n")
        report_path = Path(f.name)
    r = check_reviewer_anti_hallucination(report_path)
    assert_pass("14 reviewer **PASS** bold", r)
    report_path.unlink()


def test_main_full_run():
    """端到端：跑完整 17 项核查 - main 应返回 0/1（无异常）"""
    rc = main([str(FIXTURE), "--reviewer-report", "/dev/null"])
    assert_eq("main exits with 0 or 1", rc in (0, 1), True)


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
