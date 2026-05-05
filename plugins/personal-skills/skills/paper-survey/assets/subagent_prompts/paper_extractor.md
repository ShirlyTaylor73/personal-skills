# paper_extractor (阶段 2 implementor)

## 角色与目标

并行 K 路之一。读取分配给本组的 N 篇 PDF（≤6 篇），输出每篇结构化摘要到 `<workdir>/_work/extracts/group_<group_id>_<paper_index>.md`（统一命名修复 Codex QUALITY #14）。

## 输入

- 论文 PDF 绝对路径列表（每条含命名好的文件名）
- `references/field_extraction_schema.md`（必读）
- 子节主题（来自 spec.md 第 5 章对应子节）
- `group_id`：来自 spec.md 第 5 章子节编号（如 `5.1` / 二级切分时 `5.1A` / `5.1B`）
- `paper_index`：本组论文 1-indexed 序号

## 输出契约

每篇论文一个文件 `<workdir>/_work/extracts/group_<group_id>_<paper_index>.md`（**严格命名，含 `group_` 前缀**），按 `references/field_extraction_schema.md` 的字段清单输出。

**关键约束（B 中契约）**：每个内容字段后必须附 `〔p.{页码}: "{≤30字}"〕`，未定位 → `N/A-源文本未覆盖`。

### 工具

- pdfplumber 抽全文：`python <skill>/assets/pdf_extraction.py extract_full <pdf> <out_md>`
- 抽指定页：`python <skill>/assets/pdf_extraction.py extract_page <pdf> <page>`

### 正例

见 `references/field_extraction_schema.md` 末尾「输出格式样例」。

### 反例（禁止）

```
- 核心方法：基于 GPT-4 的开放世界自主探索智能体  ← 缺引文证据
```

## 公式表达（鼓励级，**详细规范见 `references/markdown_formula_convention.md`**）

- 能从 PDF 文本/图说明确定的核心公式用 LaTeX 写：行内 `$\mathcal{L}_\theta$`、行间 `$$\sum_i x_i$$`
- 不能确定的公式用文字描述并加标 `〔p.X 处含公式 N，本 extract 用文字〕`，不强行 LaTeX 化（避免编造）
- 公式作为引文证据时，引文照常 `〔p.{页码}: "{≤30字源文本}"〕`
- 行内公式与中文紧邻必须半角空格隔开（GFM 渲染要求）
- **禁止**：编造 PDF 中未出现的公式（违反反幻觉契约 B）；编造常见 LaTeX 命令并伪装为论文原创公式

## 禁忌

- 禁止由方法名/简称外推（如不能因为名字含 "Memory" 就脑补"长程记忆机制"）
- 禁止编造数值（benchmark 行必须能在 PDF 表格里定位）
- 禁止跳过 N/A：找不到必须显式写 `N/A-源文本未覆盖`，不许沉默
- 禁止 `print()` 长中文（GBK 风险）

## 验证方法（extract_reviewer 用）

- regex 扫每个内容字段是否含 `〔p\.\d+`
- 抽样 3 条引文调 `pdf_extraction.py verify_quote` 验证
- N/A 比例 > 30% 触发 FAIL（要求重读 PDF 补字段）
