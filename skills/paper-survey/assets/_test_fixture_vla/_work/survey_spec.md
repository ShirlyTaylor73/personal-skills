# Embodied AI 视觉-语言-动作（VLA）模型研究综述 — 文献调研 spec

> 本文件由 paper-survey skill 生成与维护。是整个调研流程的契约文件，跨 session 可恢复。
> 用户可手工编辑修正主题/清单/章节安排，下次 skill 启动时会重读此文件。
> **「当前阶段」字段是权威状态源**（启动检测优先看此字段，文件存在性是辅助验证）。

## 主题词与边界

- **主题（中文）**：Embodied AI 视觉-语言-动作（VLA）模型研究综述
- **主题（英文，用于检索）**：Embodied AI Vision-Language-Action (VLA) Models — survey
- **范围**：聚焦机器人**操作（manipulation）**方向的 VLA 模型 + 配套**仿真/数据基础设施**。
  - **包含**：早期 VLA（视觉表征 / 可扩展 Transformer 控制 / 动作分块 / 多任务模仿）、大模型驱动 VLA（VLM-as-VLA、分层 S2+S1、Flow Matching/Diffusion 动作头）、仿真器与数据生成器。
  - **不包含**：纯视觉表征学习（除 R3M 作为早期 VLA 代表保留）、纯多模态 VQA（无动作输出）、导航专用 VLA（VLN）、纯 LLM 任务规划无低层动作。
- **目标深度**：技术调研
- **目标论文数**：14 篇（含主线综述 1 篇引用，但主线综述本身不计入 14 篇分析清单）
- **报告字数目标**：5500（弹性档，N=14 自动推算）
- **模板分支**：general-academic（11 章完整模板）

## 工作目录

- **绝对路径**：`d:/WorkSpace/code/coding-agent-workspace/llm-router/embodied-ai-vla/`
- **创建时间**：2026-05-01

## 主线综述

- 用户指定：李浩然等《面向具身操作的视觉-语言-动作模型综述》（自动化学报投稿，2025），arXiv:**2508.15201v2**，简称 **VLAManipSurvey**。
- 用户限制：以该综述为时间脉络/分类骨架的主线，可补搜其他综述但不强制纳入 14 篇主清单。
- 0b 自动补搜结果：已在 `pdfs/_pre/` 完成 PDF 与全文抽取。其他备选综述未纳入清单（5 维度横切组织方式与本任务"按代表性论文纵列"组织方式不直接对齐，仅作时间脉络印证）。

## 检索关键词集合

### 主关键词

- Vision-Language-Action model
- VLA robot manipulation
- robot foundation model
- embodied AI manipulation policy

### 子领域关键词（按第 5 章组织方式分组）

- **5.1 早期 VLA（萌芽阶段）**：visual representation pretraining for robot, language-conditioned imitation learning, action chunking, robotics transformer, semantic augmentation
- **5.2A 大模型驱动 VLA — 闭源/企业系**：vision-language model robotic control, embodied multimodal LLM, open-source VLA, generalist humanoid foundation model, web-knowledge transfer to robot
- **5.2B 大模型驱动 VLA — Pi 系列**：flow matching action head, PaliGemma robot policy, open-world generalization VLA, Physical Intelligence pi-zero
- **5.3 仿真与基础设施**：visuomotor diffusion policy, world model robotic simulation, bimanual manipulation benchmark, domain randomization data generator, scalable robot data

### 反检索词（避免误命中）

- "VLA" 避免命中 "Vehicle Lateral Acceleration"（汽车工程）/ "Visual Linear Algebra" / "Vertical Launching Array"
- "embodied" 避免命中 "embodied cognition philosophy"（哲学/心理学）
- "manipulation" 避免命中 "image manipulation detection" / "social manipulation"
- "π0 / pi0" 避免命中 "π0 meson"（粒子物理）
- "GR00T" / "Genie" 避免命中 Google Genie 游戏世界模型（除非确为机器人方向）

## 论文清单（结构化表格）

| # | 简称 | arXiv ID | DOI | 标题 | 第一作者 | venue | 录用年 | PDF 文件名 | 备注 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | R3M | 2203.12601 | — | R3M: A Universal Visual Representation for Robot Manipulation | Suraj Nair | CoRL | 2022 | 2022_CoRL_R3M.pdf | 综述未直接引用，作为早期 VLA 视觉表征代表保留；视觉编码器路线 |
| 2 | RT1 | 2212.06817 | — | RT-1: Robotics Transformer for Real-World Control at Scale | Anthony Brohan | arXiv (RSS '23) | 2022 | 2022_arXiv_RT1.pdf | 综述高频引用（[22]），EfficientNet+动作离散化代表 |
| 3 | RoboAgent | 2309.01918 | — | RoboAgent: Generalization and Efficiency in Robot Manipulation via Semantic Augmentations and Action Chunking | Homanga Bharadhwaj | arXiv | 2023 | 2023_arXiv_RoboAgent.pdf | 综述未直接引用，作为多任务模仿+动作分块工程代表保留 |
| 4 | ACT | 2304.13705 | — | Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware | Tony Z. Zhao | RSS | 2023 | 2023_RSS_ACT.pdf | 综述高频引用（[27]），动作分块思想原始出处，CVAE 多模态建模 |
| 5 | RT2 | 2307.15818 | — | RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control | Anthony Brohan | arXiv | 2023 | 2023_arXiv_RT2.pdf | 综述极高频（[11]），VLA 概念首提者，55B VLM-as-VLA |
| 6 | PaLME | 2303.03378 | — | PaLM-E: An Embodied Multimodal Language Model | Danny Driess | ICML | 2023 | 2023_ICML_PaLME.pdf | 综述中频（[37]），RT-2 继承 VLM 权重来源 |
| 7 | OpenVLA | 2406.09246 | — | OpenVLA: An Open-Source Vision-Language-Action Model | Moo Jin Kim | CoRL | 2024 | 2024_CoRL_OpenVLA.pdf | 综述极高频（[40]），7B 开源 LIBERO/SimplerEnv 基线常客 |
| 8 | GR00TN1 | 2503.14734 | — | GR00T N1: An Open Foundation Model for Generalist Humanoid Robots | NVIDIA et al. | arXiv | 2025 | 2025_arXiv_GR00TN1.pdf | 综述极高频（[58]），DiT-as-S1 分层代表，提出训练数据金字塔 |
| 9 | Pi0 | 2410.24164 | — | π0: A Vision-Language-Action Flow Model for General Robot Control | Kevin Black | arXiv | 2024 | 2024_arXiv_Pi0.pdf | 综述极高频（[43]），Flow Matching 动作头，PaliGemma 继承权重 |
| 10 | Pi05 | 2504.16054 | — | π0.5: a Vision-Language-Action Model with Open-World Generalization | Physical Intelligence | arXiv | 2025 | 2025_arXiv_Pi05.pdf | 综述高频（[79]），开放世界泛化，RoboArena 当前 SOTA |
| 11 | Pi06 | 2511.18674 | — | π0.6 (Physical Intelligence 系列最新版) | Physical Intelligence | arXiv | 2025 | 2025_arXiv_Pi06.pdf | 综述未单独命名引用（截稿后增量），arxiv_id 用户直供，待阶段 1 抓取确认 |
| 12 | DiffusionPolicy | 2303.04137 | — | Diffusion Policy: Visuomotor Policy Learning via Action Diffusion | Cheng Chi | RSS | 2023 | 2023_RSS_DiffusionPolicy.pdf | 综述高频（[28]），扩散模型引入策略建模的开创工作 |
| 13 | GenieEnvisioner | 2508.05635 | — | Genie Envisioner: A Unified World Foundation Platform for Robotic Manipulation | Yue Liao (ByteDance Seed) | arXiv | 2025 | 2025_arXiv_GenieEnvisioner.pdf | 综述未直接引用，作为世界模型+仿真+策略统一平台代表保留；arxiv_id 已 paper-search 验证 ✓ |
| 14 | RoboTwin2 | 2506.18088 | — | RoboTwin 2.0: A Scalable Data Generator and Benchmark with Strong Domain Randomization for Robust Bimanual Robotic Manipulation | Tianxing Chen | arXiv | 2025 | 2025_arXiv_RoboTwin2.pdf | 综述中频（[116]），多模态 LLM + 仿真在环双臂数据生成器 |

> arXiv ID 缺失允许（标 `待阶段 1 检索`），但阶段 1 结束前必须补全或走"已剔除"。本清单 14 个 arxiv_id 均为用户直供，已抽样验证 GenieEnvisioner（2508.05635 ✓）；Pi06（2511.18674）因 paper-search 未直接命中，标注为"待阶段 1 抓取确认"。

### 已剔除论文

| # | 原简称 | 原因 | 决定时间 |
|---|---|---|---|
| — | — | 用户在 0a 已锁定 14 篇范围，无主动剔除 | 2026-05-01 |

> 综述高频但本任务未列入候选（备选扩展池）：Octo / RDT-1B / CogACT / RoboFlamingo / GR-1, GR-2, GR-3 / HPT / SpatialVLA / OpenVLA-OFT / FAST。详见 `pre_survey_notes.md` §2.2。

## 报告章节大纲

### 第 5 章组织方式

`chapter5_organization` ∈ {"timeline", "method-taxonomy", "subtask"}

选择：**method-taxonomy**（按机构谱系细分 5.2，时间轴隐含于子节内部排列；与综述"3 阶段时间脉络"高度吻合，并补充仿真基础设施维度）

### 第 5 章子节列表（决定 subagent 分组）

- **5.1 早期 VLA（萌芽阶段）**：包含论文 #1 R3M, #2 RT1, #3 RoboAgent, #4 ACT（共 4 篇）
- **5.2 大模型驱动 VLA（探索 + 快速发展阶段）**——按机构谱系二级切分：
  - **5.2A 闭源/企业系（Google/DeepMind/Stanford 衍生开源/英伟达）**：包含论文 #5 RT2, #6 PaLME, #7 OpenVLA, #8 GR00TN1（共 4 篇）
  - **5.2B Pi 系列（Physical Intelligence 同源）**：包含论文 #9 Pi0, #10 Pi05, #11 Pi06（共 3 篇）
- **5.3 仿真与基础设施**：包含论文 #12 DiffusionPolicy, #13 GenieEnvisioner, #14 RoboTwin2（共 3 篇）

> 单子节 > 6 篇时，阶段 2 自动二级切分（如 5.1-A / 5.1-B），总并发上限 5。
> 本任务 5.2 已用户主动二级切分（5.2A=4 篇 / 5.2B=3 篇），其余子节均 ≤4 篇无需进一步切分。
> 子节归属并集：{1,2,3,4} ∪ {5,6,7,8} ∪ {9,10,11} ∪ {12,13,14} = {1..14}（覆盖完整且无重复）。

## 命名规则

见 `assets/naming_convention.md`，本调研无特殊覆盖。
- PDF 命名：`{年}_{venue}_{简称}.pdf`，arXiv 预印本 venue 字段写 `arXiv`。
- 抽取文件命名：`{年}_{venue}_{简称}_full.md`（同名后缀 `_full.md`），存放于 `extracts/`。
- 评审文件命名：`{年}_{venue}_{简称}_review.md`，存放于 `reviews/`。

## 当前阶段

- 阶段：`5-completed`
- 最后更新：2026-05-01 18:50

> **「当前阶段」字段是启动检测的权威状态源**。每阶段完成时主 Claude 必须 Edit 此字段为 `{N}-completed`。
> 文件存在性是辅助验证：若与本字段不一致，启动检测会调 AskUserQuestion 升级用户。

## 已知缺陷（如有）

- 暂无；阶段 1 下载后若 RoboAgent / Pi06 部分 venue 字段不可考，allow 退化为 `arXiv`。

## 已知备注

- **14 篇综述覆盖率 71%**：14 篇中 **R3M / RoboAgent / Pi06 / GenieEnvisioner** 4 篇未在主线综述 VLAManipSurvey 中直接引用（详见 `pre_survey_notes.md` §2.1 表格）。
  - R3M：早期视觉表征代表，独立检索保留；
  - RoboAgent：多任务模仿+动作分块工程代表，独立检索保留；
  - Pi06：综述截稿后增量（2025-11 发布），arXiv 2511.18674；
  - GenieEnvisioner：综述截稿后/未覆盖的 ByteDance 世界模型平台，arxiv_id 已经 paper-search 验证。
- **Pi06 (2511.18674) arxiv_id 抽样验证未直接命中**，已标注"待阶段 1 抓取确认"；阶段 1 下载若失败，需用户复核或剔除。
- **GenieEnvisioner (2508.05635)** paper-search 验证成功，第一作者为 Yue Liao（已校正，原清单仅标注 ByteDance Seed 机构）。
- **5.2 二级切分理由**：用户主动选择按机构谱系切分（5.2A 闭源/企业系 vs 5.2B Pi 系列），便于第 5 章对比"VLM-as-VLA 主流路线 vs Flow Matching 流派"两条平行技术演化线。
- **主线综述 VLAManipSurvey (2508.15201v2)** 本身不计入 14 篇分析清单，仅作为骨架/背景引用。
