# {主题} 文献调研 spec

> 本文件由 paper-survey skill 生成与维护。是整个调研流程的契约文件，跨 session 可恢复。
> 用户可手工编辑修正主题/清单/章节安排，下次 skill 启动时会重读此文件。
> **「当前阶段」字段是权威状态源**（启动检测优先看此字段，文件存在性是辅助验证）。

## 主题词与边界

- **主题（中文）**：
- **主题（英文，用于检索）**：
- **范围**：（明确"是什么不是什么"，避免 over-search）
- **目标深度**：（学位综述 / 技术调研 / 文献快报）
- **目标论文数**：（≥ N 篇，含主线综述）
- **报告字数目标**：（**弹性，按论文数 N 选档**，中文字符数；spec_writer 在 0c 阶段按用户目标论文数自动填入下表对应值，validation.py 缺省时也按此表 fallback）
  - N ≤ 3 → 2000（mini test 场景）
  - N ∈ [4, 7] → 3500（小规模）
  - N ∈ [8, 15] → 5500（中等规模）
  - N ≥ 16 → 7000（大规模）
- **模板分支**：general-academic / non-technical（默认 general-academic；non-technical 时跳过第 4 章「相关概念与基础理论」）

## 工作目录

- **绝对路径**：d:/path/to/<topic_slug>/
- **最终交付**：`<topic_slug>/<topic_slug>_综述报告.md`（顶层 markdown 文件，含 LaTeX 公式可渲染）
- **过程文件根目录**：`<topic_slug>/_work/`（spec.md / outline.md / extracts/）
- **reviewer 报告根目录**：`<topic_slug>/_reviews/`
- **预调研综述目录**：`<topic_slug>/_pre/`
- **创建时间**：YYYY-MM-DD

## 主线综述

- 用户指定：（arXiv ID 或 PDF 路径，可空）
- 用户限制：（"只用这一篇" / "可补搜其他"，默认可补搜）
- 0b 自动补搜结果：（paper-search 检出的其他高质量综述列表，含选用理由）

## 检索关键词集合

### 主关键词
- {keyword1}
- {keyword2}

### 子领域关键词（按第 5 章组织方式分组）
- {sub_topic_A}：{kw1}, {kw2}
- {sub_topic_B}：{kw3}, {kw4}

### 反检索词（避免误命中）
- 如 "MoA" 检索时排除 "Method of Adjustments"

## 论文清单（结构化表格）

| # | 简称 | arXiv ID | DOI | 标题 | 第一作者 | venue | 录用年 | PDF 文件名 | 备注 |
|---|---|---|---|---|---|---|---|---|---|
| 1 |  |  |  |  |  |  |  |  |  |
| 2 |  |  |  |  |  |  |  |  |  |

> arXiv ID 缺失允许（标 `待阶段 1 检索`），但阶段 1 结束前必须补全或走"已剔除"。

### 已剔除论文

| # | 原简称 | 原因 | 决定时间 |
|---|---|---|---|

## 报告章节大纲

### 第 5 章组织方式

`chapter5_organization` ∈ {"timeline", "method-taxonomy", "subtask"}

选择：（默认 method-taxonomy）

### 第 5 章子节列表（决定 subagent 分组）

- 5.1 {子节 A}：包含论文 #X, #Y, #Z
- 5.2 {子节 B}：包含论文 #...

> 单子节 > 6 篇时，阶段 2 自动二级切分（如 5.1-A / 5.1-B），总并发上限 5。

## 命名规则

见 `assets/naming_convention.md`，本调研无特殊覆盖。

## 当前阶段

- 阶段：{phase}（取值：`-1-init` / `0a-completed` / `0b-completed` / `0c-completed` / `1-completed` / `2-completed` / `3-completed` / `4-completed` / `5-completed`）
- 最后更新：YYYY-MM-DD HH:MM

> **「当前阶段」字段是启动检测的权威状态源**。每阶段完成时主 Claude 必须 Edit 此字段为 `{N}-completed`。
> 文件存在性是辅助验证：若与本字段不一致，启动检测会调 AskUserQuestion 升级用户。

## 已知缺陷（如有）

- 例：第 7 章性能对比表降级（数值不足）

## 已知备注

- 例：某篇论文有 Spotlight / Oral / Best Paper 荣誉
