# Embodied AI VLA（视觉-语言-动作模型）预调研笔记

> 主线综述：李浩然等《面向具身操作的视觉-语言-动作模型综述》（自动化学报投稿，2025），简称 **VLAManipSurvey**。
> 文件：`pdfs/_pre/2025_arXiv_VLAManipSurvey.pdf`，全文抽取：`pdfs/_pre/2025_arXiv_VLAManipSurvey_full.md`。
> 综述结构（5 维度）：模型结构 / 训练数据 / 预训练方法 / 后训练方法 / 模型评估。

---

## 1. 该领域子分类（→ 第 5 章组织方式）

### 推荐组织方式：时间脉络 + 仿真基础设施补充

综述将 VLA 发展划分为 **3 个阶段**——萌芽 / 探索 / 快速发展——明确以"时间脉络"作为发展叙事主线。但综述本身是按"5 维度横切"组织内容，而不是按"代表性论文纵列"。本任务采用「5.1 早期 VLA / 5.2 大模型驱动 VLA / 5.3 仿真与基础设施」的三段切分，与综述的时间脉络高度吻合，并额外补充了"仿真/基础设施"维度。

下面给出综述对每个阶段的核心定义，以印证 5.1/5.2/5.3 划分的合理性：

- **5.1 早期 VLA（萌芽阶段）**：VLA 概念尚未提出，但已出现"语言+视觉→机器人控制"的相似功能模型；以 CNN/RNN 或轻量 Transformer 为主，通常针对固定任务集合，泛化性受限。代表工作集中在视觉表征（R3M）、可扩展骨干（RT-1）、动作分块（ACT）、多任务模仿（RoboAgent）。
  - 〔VLAManipSurvey p.4: "VLA 模型发展大致经历了 3 个阶段"〕
  - 〔VLAManipSurvey p.5: "ACT[27] 提出了一种动作分块的思路"〕
  - 〔VLAManipSurvey p.5: "RT-1[22] 使用 EﬀicientNet[23] 和语句编码器"〕

- **5.2 大模型驱动 VLA（探索 + 快速发展阶段）**：2023.7 RT-2 首次提出 VLA 概念后，主流路线变为"继承 LLM/VLM 权重 + 机器人轨迹微调"；2024 年底起进入快速发展阶段，分层架构（S2 大模型 + S1 小动作模型）和 Diffusion/Flow Matching 动作头成为主流。
  - 〔VLAManipSurvey p.5: "VLA 的概念被首次提出来,并且同时推出了参数量为 55B 的 VLA 模型 RT-2"〕
  - 〔VLAManipSurvey p.5-6: "OpenVLA继承了 LLaMA 的权重...π0 继承了 PaliGemma 的权重"〕
  - 〔VLAManipSurvey p.6: "从 2024 年底开始, VLA 模型进入快速发展阶段"〕
  - 〔VLAManipSurvey p.6: "分层架构的 VLA 模型在这一阶段成为解决复杂操作问题的热门选择"〕

- **5.3 仿真与基础设施**：综述用专章（第 4 节训练数据 + 第 7 节模型评估）讨论数据/仿真/评估三件套，并给出"数据金字塔"概念（互联网图文 / 视频 / 仿真 / 真机），仿真器与合成数据生成器是支撑 VLA 训练与评估的关键基础设施。
  - 〔VLAManipSurvey p.11: "英伟达的研究人员提出了 VLA 训练数据金字塔的概念"〕
  - 〔VLAManipSurvey p.12: "RoboTwin2.0...构建了一个自动化的数据生成流程"〕
  - 〔VLAManipSurvey p.5: "扩散模型被用于建模机器人策略,并取得优异的效果"〕（Diffusion Policy 作为 5.3 的"动作建模基础设施"印证）

> **更细粒度的内部讨论**（综述未显式分组，仅作附记）：5.2 内部综述并未按"机构/时间"细分，而是按"继承权重来源"（LLM 权重 vs VLM 权重 vs 视频预训练）和"架构层次"（单层 vs 分层）切分。这与本任务 5.2 内部按时间排列（PaLM-E → RT-2 → OpenVLA → π0 → π0.5 → π0.6 → GR00T-N1）一致——时间顺序大致对应了"VLM 继承能力增强 + 分层架构出现"的演化曲线。

---

## 2. 综述高频引用论文（→ 14 篇清单引用密度评估）

### 2.1 用户清单 14 篇 × 综述引用密度

| 简称 | 引用编号 | 综述引用次数估计 | 综述定位 | 章节 |
|---|---|---|---|---|
| **R3M** | — | **0**（综述未直接引用 R3M） | 未列入 | 5.1 |
| **RT-1** | [22] | 高频（≥6 次） | 探索阶段早期代表，EﬀicientNet 骨干、动作离散化 | 5.1 |
| **RoboAgent** | — | **0**（综述未直接引用） | 未列入 | 5.1 |
| **ACT** | [27] | 高频（≥4 次） | 动作分块思想首次提出，CVAE 建模多模态 | 5.1 |
| **RT-2** | [11] | **极高频**（≥10 次） | VLA 概念首次提出者，55B VLM-as-VLA 范式 | 5.2 |
| **PaLM-E** | [37] | 中频（2-3 次） | RT-2 继承的 VLM 权重来源 | 5.2 |
| **OpenVLA** | [40] | **极高频**（≥10 次） | 7B 开源跨域分阶段训练代表，LIBERO/SimplerEnv 基线常客 | 5.2 |
| **π0** (Pi0) | [43] | **极高频**（≥10 次） | Flow Matching 动作头，PaliGemma 继承权重 | 5.2 |
| **π0.5** (Pi05) | [79] | 高频（≥5 次） | 开放世界泛化，RoboArena 当前 SOTA | 5.2 |
| **π0.6** (Pi06) | — | 综述未单独命名引用（最新版未覆盖） | 弱覆盖 | 5.2 |
| **GR00T-N1** | [58] | **极高频**（≥8 次） | DiT-as-S1 分层代表，提出训练数据金字塔 | 5.2 |
| **Diffusion Policy** | [28] | 高频（≥4 次） | 把扩散模型引入策略建模的开创性工作 | 5.3 |
| **GenieEnvisioner** | — | **0**（综述未直接引用） | 未列入 | 5.3 |
| **RoboTwin2** | [116] | 中频（2-3 次） | 多模态 LLM + 仿真在环的双臂数据生成器 | 5.3 |

> **覆盖率**：14 篇中**有 10 篇**在综述里被直接引用（占 71%）；4 篇在综述外（**R3M / RoboAgent / π0.6 / GenieEnvisioner**），需要在 0c 阶段补充独立检索；其中 π0.6 是 π0/π0.5 系列的延续，可视为"综述截稿后增量"。
>   - 〔VLAManipSurvey p.5: "RT-2[11]…推动 VLA 进入快速发展阶段"〕
>   - 〔VLAManipSurvey p.18: 表 3 列出 π0/GR00T N1/GR-1/GR-2/GR-3/Helix/HPT/Magma/Octo/OpenVLA/RDT/RoboFlamingo/RT-2/UniVLA 作为监督微调主线〕

### 2.2 综述高频但本任务未选的候选（已剔除清单 ≥ 3 篇）

下列工作在综述中也具有较高引用密度，本任务 14 篇清单中未列入，可作为未来扩展候选：

- **Octo** [31]——开源轻量级 VLA，WidowX/UR5/RT-1 多机器人评估，SimplerEnv 常用基线。〔VLAManipSurvey p.5: "Octo[31] 被设计成一种参数量更小的 VLA 模型"〕
- **RDT-1B** [32]——双臂操作 DiT 基础模型，1M 轨迹预训练。〔VLAManipSurvey p.5: "RDT-1B[32] 使用改进的 Diffusion Transformer"〕
- **CogACT** [41]——清华 LLaMA 继承权重 VLA，SimplerEnv 强基线。〔VLAManipSurvey p.6: "OpenVLA和清华大学提出的 CogACT[41] 继承了 LLaMA 的权重"〕
- **RoboFlamingo** [38]——字节跳动 Flamingo 继承 VLA 早期开源代表。〔VLAManipSurvey p.6: "RoboFlamingo[38] 继承了 Flamingo 的权重"〕
- **GR-1 / GR-2 / GR-3** [48,49,139]——字节跳动视频预训练 VLA 系列。〔VLAManipSurvey p.16: "GR-1[48] 将视频预测与动作生成融合在一个模型中"〕
- **HPT** [34]——异构跨形态 Stem-Trunk-Head 三层架构。〔VLAManipSurvey p.5: "HPT[34] 采用了包含编码器(Stem)..."〕
- **SpatialVLA** [70]——3D 空间理解 + Ego3D 位置编码。〔VLAManipSurvey p.7: "SpatialVLA 引入了 Ego3D 位置编码机制"〕
- **OpenVLA-OFT** [78]——OpenVLA 的速度/成功率优化版，LIBERO 强基线。〔VLAManipSurvey p.23: 表 6 LIBERO 95% Average〕
- **FAST** [80]——VLA 动作分词通用方案。〔VLAManipSurvey p.10: "FAST[80] 提出了将时序信号压缩的经典方法与现代自然语言处理中的分词方法相结合"〕

---

## 3. 主流 benchmark / 数据集 / 指标（→ 第 6 章预填）

### 3.1 训练数据集（综述第 4 节）

| 数据集 | 规模 | 用途 | 引文 |
|---|---|---|---|
| **OXE** (Open X-Embodiment) | 22 种机器人, 527 种技能, 160k 任务, 1M+ 轨迹 | 跨形态 VLA 预训练黄金标准 | 〔VLAManipSurvey p.5: "整合了来自 21 个不同机构...构建了包含 1M+ 机器人轨迹的大规模数据集 OXE"〕 |
| **DROID** | 76k 演示轨迹, 350h 交互, 564 真实场景, 86 任务 | 多模态真实机器人多任务 | 〔VLAManipSurvey p.12-15: "76k 条演示轨迹...覆盖 564 个真实场景和 86 项任务类型"〕 |
| **BridgeData V2** | 60k 轨迹, WidowX 24 环境 | 多任务跨场景预训练 | 〔VLAManipSurvey p.14 表 2〕 |
| **RH20T** | 110k 接触序列, 147 任务, 42 技能, 含视/力/音 | 多模态跨形态 | 〔VLAManipSurvey p.15: "上海交通大学构建了 RH20T...110k 个密集接触的机器人操作序列"〕 |
| **RoboMIND** | 107k 轨迹, 479 任务, 96 物体 | 标准化多形态 | 〔VLAManipSurvey p.15: "RoboMIND[135] 构建了包含 107k 条轨迹"〕 |
| **AgiBot World** | 1M+ 轨迹, 217 任务, 87 技能, 2976h | 通用桌面/工业大规模真机 | 〔VLAManipSurvey p.14 表 2: "智元机器人...采集了超过 1M 条轨迹"〕 |
| **Ego4D / EPIC-KITCHENS-100 / Something-Something V2** | 3670h / 100h+20M / 220k 片段 | 视频预训练（人类活动） | 〔VLAManipSurvey p.11-13 表 2〕 |
| **RoboCasa** | 2500+ 3D 物体, 100k+ 轨迹, 120 厨房 | 仿真合成 | 〔VLAManipSurvey p.12: "RoboCasa[114]...包含了超过 120 个逼真的厨房场景和 2500 多个高质量的 3D 物体"〕 |
| **RoboTwin 2.0** | 731 物体, 100k+ 专家双臂轨迹, 50 任务, 5 形态 | 仿真在环数据生成器 | 〔VLAManipSurvey p.12: "RoboTwin2.0[116]...构建了一个自动化的数据生成流程"〕 |

### 3.2 仿真器/评测基准（综述第 7.3 节，表 5）

| 仿真器 | 引擎 | 任务数 | 机器人 | 综述列出的代表方法 |
|---|---|---|---|---|
| **CALVIN** [171] | PyBullet | 长序列、语言指令桌面操作 | Franka Panda | GR-1 / GR-2 / RoboFlamingo / VPP / UniVLA |
| **LIBERO** [174] | MuJoCo | 130 程序生成终身学习任务 | Franka Panda | π0 / OpenVLA / OpenVLA-OFT / GR00T-N1 / Hume / SpatialVLA / UniVLA / SmolVLA |
| **SimplerEnv** [173] | SAPIEN | 多样化语言指令桌面操作 | WidowX, Google Robot | π0 / CogACT / Octo / OpenVLA / RT-1 / SpatialVLA / RoboVLMs |
| **Meta-World** [177] | MuJoCo | 50 元学习/多任务 | Sawyer | HPT / TinyVLA / VPP |
| **RLBench** [179] | CoppeliaSim | 100 大规模多样化 | Franka Panda | HybridVLA |
| **Franka-Kitchen** [172] | MuJoCo | 厨房多目标 | Franka Panda | HiRT |
| **RoboMimic** [180] | MuJoCo | 模仿学习任务集 | Franka Panda | HPT |

〔VLAManipSurvey p.23: 表 5 仿真器与 VLA 模型评估〕

### 3.3 评价指标（综述第 7.1 节）

- **任务成功率（Success Rate）**：当前 VLA 评估首选绝对指标。〔VLAManipSurvey p.22: "机器人操作任务成功率是评价 VLA 模型操作性能的主要指标"〕
- **能力对数（RoboArena Score）**：相对评价指标，双盲成对模型策略，降低主观偏差。〔VLAManipSurvey p.21-22: "RoboArena[169] 提出了一种能力对数的相对评价指标"〕
- **分阶段任务成功率 / 任务进度（Task Progress）**：过程评估指标。〔VLAManipSurvey p.22: "RobotArena∞[165] 使用任务进度实现更细粒度的模型在当前操作任务下的完成情况"〕
- **意图（Intent）评估（INT-ACT）**：评估任务理解与推理能力，与执行能力解耦。〔VLAManipSurvey p.22: "INT-ACT[164] 使用意图来评估 VLA 模型在操作过程中的任务理解能力"〕
- **泛化三轴**：形态泛化 / 任务泛化 / 环境泛化。〔VLAManipSurvey p.21: "本文将 VLA 操作泛化能力大致分为 3 个维度: 形态泛化, 任务泛化和环境泛化"〕
- **行为细粒度指标**：轨迹/空间/协调指标（RoboEval）。〔VLAManipSurvey p.22: "RoboEval[170] 使用细粒度的行为指标"〕

### 3.4 排行参考（节选）

- **RoboArena 真机榜首（截至综述）**：π0.5-DROID（Score 1883）> PaliGemma-FAST-specialist-DROID > π0-FAST-DROID。〔VLAManipSurvey p.22: 表 4〕
- **LIBERO 平均成功率榜首**：Hume 98% > UniVLA/OpenVLA-OFT 95% ≈ π0/BitVLA/GR00T-N1 94%。〔VLAManipSurvey p.23: 表 6〕
- **SimplerEnv WidowX 部分**：UniVLA / Hume / RoboVLMs 整体领先，OpenVLA/RT-1 较弱。〔VLAManipSurvey p.24: 表 7〕

---

## 4. 综述指出的开放问题（→ 第 8 章预填）

综述第 9 节"具身操作的 VLA 模型展望"明确归纳出 **3 大未来挑战**，本任务可在第 8 章扩展为 5 条开放问题：

1. **泛化能力（视觉/形态/任务）**：现有 VLA 对背景、光照、视角变化敏感；跨形态泛化能力差，几乎无法跨本体复用同一参数；跨任务泛化"几乎不具备"。〔VLAManipSurvey p.25: "目前 VLA 模型的泛化能力仍然面临诸多挑战"〕〔VLAManipSurvey p.26: "目前 VLA 相关工作中对于跨任务泛化研究相对较少, 有研究工作发现当前 VLA 模型几乎不具备跨任务泛化能力"〕

2. **精细操作（contact-rich）**：高频精细操作（插入、堆叠、密集接触）成功率低；遥操作数据动作一致性差；缺乏触觉/力觉模态对齐。〔VLAManipSurvey p.26: "在处理精细操作任务,尤其是需要密集接触的精细操作任务中,其成功率相对比较低"〕

3. **实时推理（latency vs capability）**：VLA 大模型继承自 VLM，参数量大、机器人端侧算力受限；动作分块/异步分层/模型量化是三大缓解方向，但优化与泛化能力存在折中。〔VLAManipSurvey p.26: "目前的 VLA 大模型很难满足机器人高频的实时控制需求"〕

4. **数据飞轮缺失**：真实机器人数据相比 LLM/VLM 仍小 3-4 个数量级；遥操作采集成本高、操作员一致性差；仿真到真实差距明显。〔VLAManipSurvey p.15: "包含机器人动作的 VLA 训练数据集...都相差甚远...阻碍具身操作实现真正的落地应用"〕

5. **评估方法的可复现性与可扩展性**：真实环境评估场景设计主观且难复现；仿真器与真实差距使结果代表性弱；世界模型评估虽起步但难以建立准确物理交互。〔VLAManipSurvey p.24-25: "传统的评估体系需要人工操作员重置场景和成功判定,人工监督阶段可能会引入偏见"〕

> 配套：综述第 5.5 节还指出"思维链/推理范式如何在 VLA 上稳定生效"是预训练侧的开放问题；第 6.4 节指出"在线 RL 后训练的稠密奖励 + 安全探索"是后训练侧的开放问题——可在 8 章作为补充次级问题。
> 〔VLAManipSurvey p.17: "构造何种思维链数据仍然是一个开放性问题"〕
> 〔VLAManipSurvey p.21: "如何获得稠密且可扩展的奖励函数是当前强化学习后训练的关键之一"〕
