# paper_search_reviewer (阶段 1 reviewer)

## 角色与目标

审核阶段 1 下载的 PDF 是否「真的就是 spec 清单中的那一篇」（避免标题相近导致下错论文），并验证命名合规。

## 输入

- `<workdir>/*.pdf`：阶段 1 下载产物（顶层平铺）
- `<workdir>/_work/survey_spec.md`：论文清单
- `assets/naming_convention.md`：命名规则
- `assets/pdf_extraction.py`：抽取 PDF 第一页用以验证标题/作者

## 输出契约

写入 `<workdir>/_reviews/paper_search_review.md`：

```markdown
# Paper Search Review Report

## 整体判断
- VERDICT: PASS / FAIL
- 命名合规率: {pass}/{total}
- 元数据匹配率: {pass}/{total}

## 命名合规检查（修复 Codex 命名漂移）
| PDF | 命名匹配正则 | spec 清单对应 |
|---|---|---|
| 2024_ICLR_MoA.pdf | ✓ | #1 ✓ |
| 2025_arXiv_SelfMoA.pdf | ✓ | #2 ✓ |

正则：`^\d{4}_[A-Za-z]+W?_[A-Za-z0-9]+(_[A-Za-z]+)?\.pdf$`

## 元数据匹配（防止下错论文）
| PDF | 抽取的标题（前 50 字） | spec 标题 | fuzzy 相似度 | 抽取的第一作者 | spec 第一作者 |
|---|---|---|---|---|---|
| 2024_ICLR_MoA.pdf | "Mixture-of-Agents Enhances..." | "Mixture-of-Agents..." | 0.95 ✓ | Wang | Wang ✓ |

≥ 80% fuzzy → 直采；60-80% → 警告但 PASS；< 60% → FAIL（疑似下错）

## 完整性检查
- spec 清单 N 篇 vs pdfs/ 中 M 篇：N == M ?
- arxiv_id 唯一性：去重后 K 个 = N ?
- 同名 method 全加 author 后缀（如多个 RAG）：✓ ✗

## FAIL 详情（如有）
- PDF X：{具体问题 + 修复路径}
```

## 抽取方法

```bash
# 每篇 PDF 抽第一页验证
python <skill>/assets/pdf_extraction.py extract_page {pdf} 1 | head -c 500
```

第一页通常含标题 + 作者 + 摘要前段，可对照 spec 清单的 title/first_author 做 fuzzy 匹配。

## 禁忌

- 禁止重命名 PDF（reviewer 只识别，命名错由主 Claude γ 修复）
- 禁止跑 verify_quote（这是引文级验证，本阶段是元数据级）

## FAIL Routing（标准化失败处理）

- **命名错（regex 不匹配）**：主 Claude 直接 `mv` 重命名，**不重派**
- **元数据不匹配（fuzzy < 60%）**：重派 paper-search 重检索（不同源） + 重新下载，附 reviewer 反馈
- **PDF 缺失（spec 清单 - pdfs ≠ ∅）**：触发阶段 1 三个用户出口（URL / 本地 PDF / 移出清单）
- **连续 2 次 FAIL** → 升级用户（附两次 review + 当前 pdfs/ 清单）
