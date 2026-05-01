# outline_writer (阶段 3 implementor)

## 角色与目标

合并所有 K 路 extract 文件 + 0b 预调研笔记 + 主线综述要点，撰写 `<workdir>/_work/outline.md`，作为阶段 4 docx 生成的输入。

## 输入

- `<workdir>/_work/survey_spec.md`
- `<workdir>/_work/extracts/*.md`（K 路全部产出）
- `<workdir>/_work/pre_survey_notes.md`
- `references/report_structure_11chapters.md`

## 公式 LaTeX 约定（强制）

**详细规范见 `references/markdown_formula_convention.md`，本节为契约摘要。**

- **行内公式**：`$x^2$`（前后用半角空格隔开中文）
- **行间公式**：`$$\sum_i x_i$$`（独占一行，前后空行）
- **第 4 章「相关概念与基础理论」每个 H3 子节强制 ≥ 1 公式**（行内或行间均可）
- **第 5 章每篇论文核心方法描述：能确定的核心损失/架构公式用 LaTeX 写**（鼓励，不强制）
- **配对**：`$` 总数为偶数；`$$` 总数为偶数（assemble_md.py / validation #17 会检查）
- **禁止**：编造 PDF 中未出现的公式（违反反幻觉契约 B）

### 第 4 章子节示例（VLA 类报告）

```markdown
### 2.1 视觉-语言-动作（VLA）模型形式化

VLA 模型将策略参数化为 $\pi_\theta(a_t \mid o_t, l)$ ，其中 $o_t$ 是观测、$l$ 是语言指令。训练目标为：

$$
\mathcal{L}_{\text{IL}}(\theta) = \mathbb{E}_{(o,l,a) \sim \mathcal{D}}\left[-\log \pi_\theta(a \mid o, l)\right]
$$

其中 $\mathcal{D}$ 是机器人轨迹数据集。
```

## 输出契约（**严格标题层级 + 第 5/7 章 fenced JSON block — 修复 Codex BLOCKING #4**）

`outline.md` 必须是机器可解析的格式，由 `assets/assemble_md.py` 的 `parse_outline_md` 反序列化为 markdown 组装入参。**严格遵守如下结构**：

````markdown
# Outline

## 摘要

{**中文字符数** 200-400 字（validation.py 用 `[一-鿿]` 正则严格统计，含大量英文术语/数字/标点的摘要需相应扩中文以达标），含本调研主题 + 主要方法分类 + 结论 + 展望}

## 关键词

{kw1; kw2; kw3; ...}（3-6 个，分隔符任选 ; / , / 、）

## 引言

### 1.1 研究背景与意义
{**中文字符数** 300-500 字纯文本。**注**：`纯文本` 仅指不含 fenced JSON / pipe table 框架，不限制行内 LaTeX `$..$`}

### 1.2 问题定义
{**中文字符数** 200-400 字，含形式化或概念定义}

### 1.3 本文组织结构
{**中文字符数** 约 200 字，简述 3-10 章排布}

## 相关概念与基础理论

> **条件性章节**：仅当 `spec.template_branch != non-technical` 时存在；否则**整段省略**（连标题一起）。

### 2.1 {子节标题 1}
{每子节中文字符数 200-400 字，正文可含 GFM LaTeX 公式（行内 `$..$` / 行间 `$$..$$`），且至少 1 个核心定义/损失公式}

### 2.2 {子节标题 2}
...

## 国内外研究现状

> **核心章节，篇幅 ≥ 全文一半。子节数严格 = spec.md 第 5 章子节列表 + 二级切分。**

### {chN}.{i} {子节标题}（如 3.1 / 3.2 ...）

{子节简介中文 100-300 字，鼓励含核心方法 LaTeX 公式，含本子节方法论概览}

```json
[
  {
    "method_name": "MoA",
    "summary_with_citations": "Wang 等人 [1] 提出 Mixture-of-Agents...（200-400 字，含引文回链 [N]，承自 extract 文件）"
  },
  {
    "method_name": "Self-MoA",
    "summary_with_citations": "Li 等人 [2] 反思 MoA 的多样性假设..."
  }
]
```

{子节小结：中文 100-200 字，跨论文的横向对比 / 演进路线。**注**：`纯文本` 仅指不含 fenced JSON / pipe table 框架，不限制行内 LaTeX `$..$`}

### {chN}.{i+1} {下一子节} ...

## 数据集与评价指标

{**中文字符数** 500-800 字纯文本，合并 extracts 中所有 dataset/metric 字段，按主流 benchmark 排序。**注**：`纯文本` 仅指不含 fenced JSON / pipe table 框架，不限制行内 LaTeX `$..$`}

## 性能对比与分析

```json
[
  {"method": "MoA", "dataset": "AlpacaEval 2.0", "metric": "win rate", "value": "65.4%", "citation": "[1, p.5]"},
  {"method": "Self-MoA", "dataset": "AlpacaEval 2.0", "metric": "win rate", "value": "72.0%", "citation": "[2, p.7]"}
]
```

{表格分析：**中文字符数** 300-500 字，让读者一眼看出 SOTA + 方法间差距。**注**：`纯文本` 仅指不含 fenced JSON / pipe table 框架，不限制行内 LaTeX `$..$`}

> **降级方案**：若 extracts 中可比数值少于 N×0.5 行，**省略 fenced JSON block**（仅留分析文字 + 在 spec.md `## 已知缺陷` 段注明）。`assemble_md.py` 检测无 JSON 时自动降级为定性段落。

## 存在的问题与挑战

{**中文字符数** 300-500 字，归纳 extracts 中所有 limitation 字段 + 0b 预调研笔记的开放问题}

## 未来发展趋势与展望

{**中文字符数** 300-500 字}

## 总结

{**中文字符数** 200-400 字，呼应引言}

## 参考文献

{此段不在此处展开，参考文献由 `assemble_md.py` 的 `collect_references` 从 extracts 自动收集，按引用顺序编号 [1]-[N]}
````

**数据契约关键约束**：

- H1 / H2 / H3 标题必须严格按上面格式（`## 摘要` / `### 1.1 研究背景与意义` 不可加序号前缀如 "1. "）
- 第 5 章子节用 `### {chN}.{i} ` 格式（`chN` 由 spec.template_branch 决定：non-technical 时是 2，general 时是 3）
- 第 5 章每子节 papers 数组放在 ```json 围栏内，JSON.parse 必须成功
- 第 7 章性能表也用 ```json 围栏；空表情况下省略整个围栏
- `assemble_md.py parse_outline_md` 按 H2 章节标题分块，每块按 H3 进一步细分

## 工作流

1. 主 Claude 在阶段 3 启动时把所有 extracts/*.md 与 pre_survey_notes.md 合并到上下文
2. 按上述严格结构逐章生成（注意：第 5/7 章必须含 ```json 围栏）
3. 每用一处事实必须能回链到 extract 文件 + 引文括号
4. 完成后写入 outline.md
5. 主 Claude 立即跑 `node -e "JSON.parse(...)"` dry run 验证所有 fenced JSON block 都能解析

## 禁忌

- 禁止编造未在 extracts 中出现的论文
- 禁止跨章节重复同一个事实
- 禁止把 N/A 字段写进 outline（绕开它，写其他可用字段）
- 禁止 fenced JSON block 内出现注释或 trailing comma（JSON.parse 不容忍）

## 验证方法（outline_reviewer 用）

- 11 章结构齐全（条件性章节按 spec.template_branch 决定）
- 每段 [N] 引用编号在 extracts/ 中存在对应 GB/T 7714 条目
- 抽样 5 处事实陈述，回链到 extract 文件验证
- 摘要字数 / 关键词数量符合 spec
- 所有 ```json 围栏 JSON.parse 成功
