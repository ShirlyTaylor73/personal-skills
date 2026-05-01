# Subagent 字段提取契约

paper_extractor implementor（阶段 2）输出每篇论文的结构化摘要时，必须遵循本契约。

## B 中契约：每个字段附引文证据

每个**内容字段**后必须附：`〔p.{页码}: "{≤30字引文}"〕`

未在原文定位到 → 必须输出 `N/A-源文本未覆盖`，**禁止**外推。

通用字段（标题/作者/年份/venue/arxiv_id）和 implementor 自答字段（与本调研主题的关系/一句话评述）不需要引文。

## 字段清单

### 通用字段（每篇必填）

- 标题 / 作者 / 发表年份 / venue / arXiv ID 或 DOI
- 中文摘要（150-250 字，源自原文翻译压缩）
- 核心方法：1 句话技术路线 + 关键创新点 1-3 条 〔p.{页码}: "{引文}"〕
- 主要贡献：原文 contributions 直译/转述 〔p.{页码}: "{引文}"〕
- 与本调研主题的关系（implementor 自答，无需引文）
- 一句话评述（implementor 自答主观）

### 支撑第 5 章「研究现状」

- 优点（原文宣称 + implementor 评估） 〔p.{页码}: "{引文}"〕
- 局限性 / 缺陷（原文 limitations 段或讨论段） 〔p.{页码}: "{引文}"〕 或 `N/A-源文本未覆盖`
- 典型应用场景 〔p.{页码}: "{引文}"〕

### 支撑第 6 章「数据集与指标」

- 使用的数据集名 + 规模（如有） 〔p.{页码}: "{引文}"〕
- 评价指标名 + 定义（如原文给出） 〔p.{页码}: "{引文}"〕

### 支撑第 7 章「性能对比表」

在主流 benchmark 上的关键数值（最多 5 行）：
```
- {benchmark} / {metric} / {value} 〔p.{页码}, Tab.{N}〕
```

### 支撑第 11 章「参考文献」

- GB/T 7714 完整条目（按 references/gb_t_7714_format.md 字段拼装）

## 抽样 C：reviewer 验证

阶段 2 extract_reviewer 收到 implementor 产出后，按论文数自适应：

- 本组论文数 N，随机抽 min(N, 3) 篇
- 每篇随机抽 1 个内容字段（非通用字段）
- 调 `pdf_extraction.py verify_quote <pdf> <page> "<quote>"` 验证（fuzzy ≥ 80%）
- 抽样命中 1 处幻觉 → reviewer 标 FAIL（升级到 γ 修复回路）
- N/A 比例 > 30% 也触发 FAIL

## 阶段 5 核查抽样（**激进版，约 49 处**，覆盖全部内容章节）

阶段 5 validation_reviewer 按章节自适应抽样规则：

| 章节 | 抽样规则 | 数量（N=20 篇 / K=5 子节示例） |
|---|---|---|
| 第 2 章 摘要 | 1 处（核心论断回链至少 1 篇 extract） | 1 |
| 第 3 章 引言 | 2 处（背景陈述 + 问题定义） | 2 |
| 第 4 章 相关概念（如存在） | 1 处 | 0-1 |
| **第 5 章 研究现状** | 每子节 1 处 + **每篇论文核心方法字段必抽**（最易幻觉） | K + N = 25 |
| 第 6 章 数据集与指标 | 2 处（数据集声称 + 指标定义） | 2 |
| **第 7 章 性能对比表** | **表格每行必抽**（数值是高错率字段） | 表行数 ≈ 15 |
| 第 8 章 挑战 | 1 处 | 1 |
| 第 9 章 未来展望 | 1 处 | 1 |
| 第 10 章 总结 | 1 处 | 1 |
| 第 4 章公式 | 每 H3 子节抽 1 公式语法/命令拼写 | template_branch=general-academic 时 H3 子节数（典型 3-5） |
| **总计** | | **~49 处** |

**核心思想（防幻觉杠杆）**：

- 第 5 章「核心方法」字段是 subagent 最易由方法名外推的地方 → 每篇必抽
- 第 7 章数值是用户最容易察觉错误的地方 → 全表每行必抽（不抽样，全验）
- 其他章节维持每章 1-2 处

**并行实现**：

- 全部 ~49 处用 `pdf_extraction.py verify_quotes_batch <claims.json> --workers 8`
- 内部按 PDF 分组 + ProcessPoolExecutor，实测 100 处 × 16 PDF 仅需 4 秒
- 49 处实测约 2 秒（线性外推）

**抽样命中处理**：

- 任一抽样幻觉命中 → reviewer 标 FAIL，进入 γ 修复（FAIL 上限 3 次，详见 SKILL.md 阶段 5）
- 命中 ≥ 3 处 → 整章重写

## 输出格式样例

```
### #3 VOYAGER (Wang et al., TMLR 2024)
- 标题：Voyager: An Open-Ended Embodied Agent with Large Language Models
- 作者：Guanzhi Wang, Yuke Zhu, Anima Anandkumar, ...
- venue：TMLR 2024
- arXiv ID：2305.16291
- 中文摘要：本文提出 Voyager...（180 字）
- 核心方法：基于 GPT-4 的开放世界 Minecraft 自主探索智能体，含技能库、自动课程、迭代代码生成 〔p.2: "an LLM-powered embodied lifelong learning agent in Minecraft"〕
- 主要贡献：1. 自动课程模块；2. 可累积技能库；3. 迭代式代码生成 〔p.3: "Voyager consists of three key components"〕
- 与本调研主题的关系：作为 Planning 维度典型工作，演示 LLM 自主规划+技能复用
- 优点：不需任务标注，技能可累积复用 〔p.3: "without human intervention"〕
- 局限性：依赖 GPT-4 强能力，开源模型表现下降 〔p.9: "weaker LLMs lead to substantial drop"〕
- 典型应用场景：Minecraft 长程任务 〔p.4〕
- 数据集：Minecraft 〔p.4〕
- 评价指标：unique items obtained 〔p.4: "unique items obtained"〕
- benchmark 数值：
  - Minecraft / unique items / 63 〔p.5, Tab.1〕
- 一句话评述：是 Embodied Agent 与 LLM Planning 的关键桥接工作
- 参考文献条目（GB/T 7714）：WANG G, ZHU Y, ANANDKUMAR A, et al. Voyager: An open-ended embodied agent with large language models[C]//Proc. TMLR. 2024.
```
