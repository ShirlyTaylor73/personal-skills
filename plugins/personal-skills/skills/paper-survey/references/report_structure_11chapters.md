# 11 章综述报告结构规范（Markdown 版）

本文档是 paper-survey skill 的权威章节结构规范，被 spec_writer、outline_writer、assemble_md.py 及 validation.py 引用。最终交付为 **markdown 文档**（含 LaTeX 公式可渲染），所有综述报告必须严格遵循本文档定义的章节顺序与内容要求。

公式约定见 `markdown_formula_convention.md`（GFM `$..$` / `$$..$$`，中文紧邻空格强制）。

---

## 1. 调研主题（H1 标题）

报告首行 H1：`# {题目}`

题目句式（任选）：
- `{XXX} 研究综述`
- `{XXX} 的研究进展`
- `面向 {XXX} 的 {YYY} 方法综述`

---

## 2. 摘要与关键词

### 中文摘要

- 中文字符数：**200–400**（validation #08，用 `re.findall(r'[一-鿿]', body)` 严格统计）
- markdown 标题：`## 摘要`
- 内容要点：调研领域 + 主要方法分类 + 结论 + 展望

### 关键词

- 数量：**3–6 个**（validation #09）
- markdown 标题：`## 关键词`
- 渲染：分隔符任选 `；` `,` `、`，单行段落

```markdown
## 摘要

近年来，VLA 模型在机器人操作领域...（200-400 中文字符）

## 关键词

视觉-语言-动作；具身智能；机器人操作；流匹配；扩散策略
```

---

## 3. 引言（绪论）

`## 引言` H2 + 3 个 H3 子节：

### 1.1 研究背景与意义（H3，中文 300-500 字）

说明该问题为什么重要、应用价值。

### 1.2 问题定义（H3，中文 200-400 字）

形式化或概念化定义；**鼓励** LaTeX 公式（如策略 $\pi_\theta(a|s)$ 形式化）。

### 1.3 本文组织结构（H3，中文 ~200 字）

简述后续各章的安排逻辑。

---

## 4. 相关概念与基础理论（条件性，general-academic 保留）

`## 相关概念与基础理论` H2 + 多个 H3 子节（`### 2.{i} {子节标题}`）。

**强制公式要求（validation #17 关联）**：每个 H3 子节至少含 1 个核心定义/损失/算法公式（行内 `$..$` 或行间 `$$..$$`）。

子节示例（VLA 类报告）：

```markdown
### 2.1 视觉-语言-动作（VLA）模型形式化

VLA 模型将策略参数化为 $\pi_\theta(a_t \mid o_t, l)$，其中 $o_t$ 是观测、$l$ 是语言指令、$a_t$ 是动作 token。训练目标通常为模仿学习：

$$
\mathcal{L}_{\text{IL}}(\theta) = \mathbb{E}_{(o,l,a) \sim \mathcal{D}}\left[-\log \pi_\theta(a \mid o, l)\right]
$$

其中 $\mathcal{D}$ 是机器人轨迹数据集。

### 2.2 流匹配（Flow Matching）

...
```

> 模板分支 `template_branch=non-technical` 时省略整章（含标题）。

---

## 5. 国内外研究现状（核心章节，篇幅最大）

`## 国内外研究现状` H2 + 若干 H3 子节（`### 5.{i} {子节标题}`，**子节编号沿用 spec.md `chapter5_organization` 子节列表**，二级切分时如 `5.2A` / `5.2B`）。

每个 H3 子节内含：

1. **子节简介**段（中文 100-300 字）
2. **每篇代表论文**单独 H4（`#### 5.{i}.{j} {method_name}`）+ 中文段（200-400 字含 `[N]` 引用回链）
3. **子节小结**段（中文 100-200 字）

assemble_md.py 把 outline.md 中第 5 章 fenced JSON 的 papers 数组按此结构展开。

---

## 6. 数据集与评价指标

`## 数据集与评价指标` H2 + 中文 500-800 字段。

合并各 extract 的 `数据集` + `评价指标` 字段，按主流 benchmark 排序。

---

## 7. 性能对比与分析

`## 性能对比与分析` H2 + **markdown pipe table** + 中文 300-500 字定性分析。

assemble_md.py 把 outline.md 中第 7 章 fenced JSON `performance_table` 数组转 pipe table：

```markdown
| 方法 | 数据集 | 指标 | 数值 | 引用 |
|---|---|---|---|---|
| RT-1 | Real Robot Seen Tasks | Success Rate | 97% | [2, p.9, Tab.2] |
| RT-2 | Language-Table sim | Success Rate | 90±10% | [5, p.9, Tab.1] |
| ... | ... | ... | ... | ... |
```

---

## 8. 存在的问题与挑战

`## 存在的问题与挑战` H2 + 中文 300-500 字。

归纳各 extract 的 `局限性` 字段 + 0b 预调研笔记的开放问题。

---

## 9. 未来发展趋势与展望

`## 未来发展趋势与展望` H2 + 中文 300-500 字。

---

## 10. 总结

`## 总结` H2 + 中文 200-400 字。

呼应引言研究背景与问题定义，简要概括各章主要发现。

---

## 11. 参考文献

`## 参考文献` H2 + 列表段。

assemble_md.py 从 `_work/extracts/*.md` 抽取每篇的「参考文献条目（GB/T 7714）：...」行，按 spec.md paperList 顺序编号 `[1] [2] ... [N]` 输出：

```markdown
## 参考文献

[1] NAIR S, RAJESWARAN A, KUMAR V, et al. R3M: A Universal Visual Representation for Robot Manipulation[C]//Proceedings of the Conference on Robot Learning. 2022.

[2] BROHAN A, BROWN N, CARBAJAL J, et al. RT-1: Robotics Transformer for Real-World Control at Scale[J]. arXiv preprint arXiv:2212.06817, 2022.

...
```

GB/T 7714 详细格式见 `gb_t_7714_format.md`。文献类型标识必含 `[J] [C] [D] [M] [N] [P] [S] [R] [A] [G] [Z]` 之一，可附 `/OL` `/MT` `/DK` `/CD` 载体后缀（validation #12）。

---

## skill 内引用规则

- **spec_writer** 在 0c 阶段写 spec.md 时按本 11 章顺序起草章节大纲
- **outline_writer** 在阶段 3 严格遵循本 H1/H2/H3 层级（assemble_md.py 按 H2 切分）
- **assemble_md.py** 在阶段 4 把 outline.md 渲染为顶层最终 md（展开 fenced JSON、插入 GB/T 7714 参考列表）
- **validation.py** 阶段 5 按本规范做 17 项核查（含 #01 md_headings 层级合规、#17 latex_formula 配对）
- **第 4 章「相关概念与基础理论」**：当 `spec.template_branch = non-technical` 时跳过整章
- **第 5 章三种组织方式**：spec.md `chapter5_organization` ∈ {`timeline`, `method-taxonomy`, `subtask`}，subagent 分组按此切分
