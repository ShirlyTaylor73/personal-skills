# Outline

## 摘要

视觉-语言-动作（Vision-Language-Action, VLA）模型是连接互联网级预训练知识与机器人物理操作的关键范式，已成为具身智能领域的核心研究方向。本文以「面向具身操作」为边界，系统调研 VLA 模型的发展脉络与代表性工作。按时间与方法谱系将该领域划分为三大阶段四个子方向：早期 VLA 萌芽阶段以 R3M 视觉表征、RT-1 可扩展 Transformer、ACT 动作分块、RoboAgent 多任务模仿为代表，奠定了视觉前端、动作头与多任务模仿的基础组件；大模型驱动阶段沿两条平行路线展开——以 RT-2、PaLM-E、OpenVLA、GR00T N1 为代表的闭源/企业系沿用「VLM 主干 + 动作 token 化或 DiT 双系统」范式，而以 π0、π0.5、π*0.6 为代表的 Physical Intelligence 系列则确立了「PaliGemma 主干 + Flow Matching 动作专家」流派；仿真与基础设施层面，Diffusion Policy 开创扩散动作头、Genie Envisioner 构建视频世界模型平台、RoboTwin 2.0 提供 MLLM 驱动的可扩展双臂数据工厂。本文进一步整理了 OXE、DROID、LIBERO、SimplerEnv、RoboArena 等主流 benchmark 与成功率/任务进度/能力对数等评价指标，横向对比了 14 篇代表性工作的性能数据，归纳出泛化能力受限、精细接触操作困难、实时推理瓶颈、数据飞轮缺失、评估可复现性弱等五大开放问题，并展望了跨本体泛化、思维链推理、在线强化学习后训练、世界模型仿真协同的未来方向。

## 关键词

视觉-语言-动作模型；具身智能；机器人操作；流匹配；扩散策略；仿真数据生成

## 引言

### 1.1 研究背景与意义

近年来大语言模型（LLM）与视觉-语言模型（VLM）在自然语言处理、视觉理解领域取得突破性进展，其规模化预训练所带来的强大泛化能力与语义先验使研究者开始思考：能否将互联网规模的预训练知识直接迁移到机器人控制任务中，让机器人具备类似人类的开放世界理解与决策能力？这一思路催生了视觉-语言-动作（VLA）模型这一新兴范式。VLA 模型以图像与自然语言指令为输入、直接输出机器人动作，是具身智能领域将「感知-语言-行动」统一在同一神经网络中的关键尝试。从家庭服务到工业装配、从厨房清洁到双臂精细操作，VLA 模型正在重新定义机器人能力边界。Google 的 RT-2 在 2023 年首次提出 VLA 概念后，短短两年内涌现出 OpenVLA、π0、GR00T N1、π0.5 等一系列重磅工作，而以 RoboTwin 2.0、Genie Envisioner 为代表的仿真与数据生成基础设施则解决了 VLA 训练的「数据饥渴」难题。系统梳理 VLA 模型的发展脉络、代表性方法、性能边界与未解难题，对推动具身操作走向真正的开放世界落地具有重要的理论与工程价值。

### 1.2 问题定义

视觉-语言-动作（VLA）模型可形式化定义为一个映射 π: (I_t, ℓ, s_t) → a_{t:t+H}，其中 I_t 为多视角 RGB（可选含历史帧）、ℓ 为自然语言指令、s_t 为机器人本体感知状态（关节位置/速度/末端位姿等）、a_{t:t+H} 为长度 H 的未来动作序列（chunk）。VLA 与传统机器人策略的核心差异在于：一是输入端融入互联网级预训练 VLM/LLM 提供的开放词汇语言理解与视觉常识；二是输出端从单步动作扩展到动作分块以缓解非马尔可夫性与复合误差；三是训练目标从纯模仿学习扩展到 co-fine-tune（机器人轨迹与 web VQA 联合训练）、Flow Matching、扩散去噪等连续动作生成范式。本调研聚焦机器人操作（manipulation）方向的 VLA 模型，包含早期 VLA（视觉表征 / 可扩展 Transformer / 动作分块 / 多任务模仿）、大模型驱动 VLA（VLM-as-VLA、分层 S2+S1、Flow Matching/Diffusion 动作头）、仿真器与数据生成器三大维度，不包含纯视觉表征学习、纯多模态 VQA、导航专用 VLA 与无低层动作的 LLM 任务规划。

### 1.3 本文组织结构

本文共分十一章。第二章介绍 VLA 模型、模仿学习与动作分块、流匹配与扩散策略、仿真器与跨形态数据等相关概念与基础理论；第五章作为核心章节按方法谱系展开国内外研究现状，分为 5.1 早期 VLA、5.2A 闭源/企业系大模型 VLA、5.2B Pi 系列流匹配 VLA、5.3 仿真与基础设施四个子节，共综述 14 篇代表性工作；第六章归纳常用数据集与评价指标，涵盖 OXE、DROID、LIBERO、SimplerEnv 等主流 benchmark；第七章用表格形式横向对比 14 篇工作的关键性能数值并给出文字分析；第八章梳理领域开放问题；第九章展望未来发展趋势；第十章总结全文呼应引言；第十一章列出参考文献。

## 相关概念与基础理论

### 2.1 视觉-语言-动作（VLA）模型

VLA 模型最早由 Google DeepMind 在 RT-2 [5, p.1] 中正式命名，定义为「将互联网规模视觉-语言模型（VLM）经动作 token 化与机器人轨迹微调直接产出机器人动作」的端到端模型族。其核心范式包含三种主流架构：一是「动作即文本 token」自回归路线，将 6-DoF 动作离散化为 256 bins 后复用 VLM 词表（RT-2 [5]、OpenVLA [7]）；二是「VLM 主干 + 独立动作专家」分层路线，VLM 提供高层语义、独立模块输出连续动作（π0 [9]、GR00T N1 [8]）；三是「LLM-as-Planner + 低层策略」松耦合路线，VLM 仅产出语义子目标（PaLM-E [6]）。VLA 模型相比传统机器人策略的关键优势在于继承 VLM 的开放词汇视觉理解、长尾物体识别、跨任务语言泛化能力，同时具备符号推理、思维链等涌现行为 [5, p.9]。本调研的 14 篇代表性工作中，10 篇可归入 VLA 范畴，其余 4 篇（R3M、ACT、Diffusion Policy、RoboTwin2）虽不严格属于 VLA 但分别提供了 VLA 时代的视觉前端、动作头、生成式策略、数据基础设施关键组件。

### 2.2 模仿学习与动作分块

模仿学习（Imitation Learning）通过专家示教数据训练机器人策略，行为克隆（Behavior Cloning, BC）是其最简单形式，损失函数为预测动作与专家动作的负对数似然。但单步 BC 存在两大痛点：复合误差（compounding error）随时长指数增长、人类示教中存在的非马尔可夫性导致策略学不到正确条件分布。动作分块（Action Chunking）由 ACT [4, p.5] 首次提出，将策略输出从单步 a_t 改为长度 k 的动作序列 a_{t:t+k}，使有效任务时长缩短 k 倍，同时通过执行时的时序聚合（temporal ensemble）缓解轨迹突变。RoboAgent [3, p.6] 进一步将动作分块推广到多任务条件设置，π0 [9] 与 GR00T N1 [8] 则把动作分块与 Flow Matching/扩散动作头结合，输出 16 步乃至 50 步动作 chunk，成为当代 VLA 实时控制的标配组件。

### 2.3 流匹配与扩散策略

扩散模型（Diffusion Model）通过条件去噪过程建模数据分布，Diffusion Policy [12, p.1] 首次将其引入机器人 visuomotor 策略，将动作序列建模为以视觉观测 O_t 为条件的 DDPM 去噪过程，通过 K 步迭代优化生成多模态动作分布。该形式化天然支持高维输出与多模态目标，在 15 个任务上相对 SOTA 平均提升 46.9% [12, p.6]。流匹配（Flow Matching）作为扩散模型的连续时间推广，由 π0 [9, p.4] 首次引入 VLA 动作头，仅需 10 步欧拉积分即可生成动作 chunk，推理效率显著优于扩散模型 100 步采样。GR00T N1 [8, p.4] 则把 Flow Matching 与 DiT 结合作为分层架构的 System 1 低层策略，K=4 步推理即可在 L40 GPU 上 63.9 ms 内输出 16 步动作。流匹配与扩散动作头已成为 VLA 应对高维连续动作空间与多模态人类示教的事实标准。

### 2.4 仿真器与跨形态数据

VLA 模型的训练数据需求远超传统机器人策略，但真实机器人数据相比 LLM/VLM 仍小 3-4 个数量级，仿真器与跨形态数据成为关键基础设施。Open X-Embodiment（OXE）[7, p.5] 整合 22 种机器人、527 种技能、1M+ 轨迹，是 VLA 跨形态预训练的黄金标准；DROID 提供 76k 真实演示覆盖 564 真实场景；LIBERO 与 SimplerEnv 是 VLA 性能横向对比的主流仿真基准。RoboTwin 2.0 [14, p.2] 提出 MLLM + 仿真在环反馈的自动数据生成框架，发布 731 物体、50 任务、5 本体、10 万+ 轨迹的开源工厂；Genie Envisioner [13, p.5] 则把视频扩散模型转化为「神经仿真器」，支持千 episode/小时的闭环评测。NVIDIA 在 GR00T N1 [8, p.2] 中提出「数据金字塔」概念，把网页视频、合成数据、真机遥操作分层组织协同训练，是当前应对人形机器人数据稀缺的代表方案。

## 国内外研究现状

### 5.1 早期 VLA（萌芽阶段）

VLA 概念尚未提出但已出现「语言+视觉→机器人控制」相似功能的萌芽阶段，代表工作集中在视觉表征预训练（R3M）、可扩展 Transformer 骨干（RT-1）、动作分块（ACT）、多任务模仿（RoboAgent）四个维度。本子节按时间顺序综述 4 篇代表性工作，覆盖 2022-2023 年早期 VLA 形成期的关键技术组件。这些工作虽未引入互联网级 VLM/LLM 主干，但分别奠定了视觉前端、可扩展骨干、动作头与多任务训练范式，为后续大模型驱动 VLA 提供了不可或缺的技术基础。

```json
[
  {"method_name": "R3M", "summary_with_citations": "Nair 等人 [1, p.1] 提出 R3M——面向机器人操控的通用视觉表征。作者使用 Ego4D 人类视频数据集，结合时间对比学习、视频-语言对齐与 L1 稀疏正则三项目标，预训练 ResNet 编码器作为下游策略的冻结感知模块 [1, p.1]。在 12 个仿真操控任务（Adroit、Franka-Kitchen、MetaWorld）上 R3M 比从头训练高 20% 以上、比 CLIP/MoCo 高 10% 以上 [1, p.7]；在真实 Franka 平台上仅用 20 条演示即可学会放生菜、折毛巾等家务任务，平均成功率约为 CLIP 的两倍 [1, p.8]。R3M 作为早期 VLA 时代「视觉表征」方向的代表，证明从人类视频预训练的视觉表征可作为机器人感知前端，开启了「免机器人交互的视觉预训练」范式，但其本身不直接产出动作，仍依赖下游 BC 策略，泛化范围受限于固定任务集合 [1, p.8]。"},
  {"method_name": "RT1", "summary_with_citations": "Brohan 等人 [2, p.2] 提出 Robotics Transformer 1（RT-1），一种可在真实世界大规模控制的机器人 Transformer 策略。模型架构由 FiLM 条件化的 EfficientNet-B3、TokenLearner 压缩器和 decoder-only Transformer 组成（35M 参数），输入历史 6 帧图像与自然语言指令、输出离散化的臂/底盘动作 token，在 3 Hz 下闭环运行 [2, p.2]。作者用 13 台机器人在 17 个月内采集了约 130k 条演示、覆盖 700+ 任务指令构成训练集 [2, p.4]。在 3000+ 真实试验中 RT-1 在已见任务上达 97% 成功率，未见任务达 76%，干扰物 83%，背景 59% [2, p.9]，并能与 SayCan 结合执行最长 50 步的长程任务，吸收异构数据（仿真、跨形态 Kuka）后亦不损性能 [2, p.10]。RT-1 是早期 VLA「可扩展骨干」方向的旗舰工作，首次证明纯 Transformer 策略 + 大规模机器人数据可在真实世界生成动作，是后续 VLA（如 RT-2）的直接前身。"},
  {"method_name": "RoboAgent", "summary_with_citations": "Bharadhwaj 等人 [3, p.2] 提出 RoboAgent——在有限数据预算下训练通用多任务机器人操控智能体的高效框架。核心方法 MT-ACT 包含两阶段：首先利用 Segment Anything 与文本引导扩散模型对预采集的 7500 条演示进行帧级物体/背景 inpainting 语义增强 [3, p.5]；其次基于 CVAE + Transformer 预测未来 H 步动作分块，配合时序聚合执行 [3, p.6]。最终单一智能体可执行 12 种技能、38 个任务、6 类厨房活动，在未见场景上比 RT-1、BeT、CACTI、VIL 等基线平均高 40% 以上 [3, p.2]。仅 7500 条轨迹却比 130k 数据级别的 RT-1 在 L2/L3 泛化上更优（L2 约 100% 相对、L3 约 400% 相对提升）[3, p.9]。RoboAgent 是早期 VLA「数据高效多任务模仿」代表，首次把 ACT 思路扩展到语言条件多任务并通过语义增强弥补数据不足，但所有任务仅由单一技能组成、未支持长程技能组合 [3, p.11]。"},
  {"method_name": "ACT", "summary_with_citations": "Zhao 等人 [4, p.2] 提出 ALOHA 低成本双臂遥操作硬件 + ACT（Action Chunking with Transformers）算法的双重贡献。ACT 把策略训练为条件 VAE：编码器从动作序列与本体感知中预测「风格变量」z，解码器结合多视角 RGB、关节位置与 z 用 Transformer 预测未来 k 步动作分块，并在执行时对重叠分块做指数加权时序聚合 [4, p.2]。仅用 10 分钟约 50 条人类示教，ACT 在打开半透明调料杯、装电池等 6 个真实精细任务上达 80–90% 成功率，在 Cube Transfer、Bimanual Insertion 仿真和 4 个真实任务上较 BeT、RT-1、BC-ConvMLP、VINN 平均提升数十百分点 [4, p.8]。关键创新在于动作分块降低有效任务时长 k 倍并缓解非马尔可夫混淆 [4, p.5]，CVAE 建模人类示教多模态/噪声 [4, p.5]。ACT 是早期 VLA「动作分块」方向的奠基算法，为后续所有 VLA 动作头设计提供了关键技术组件。"}
]
```

本子节小结：早期 VLA 阶段四篇工作分别从视觉、骨干、动作头、多任务四个维度建立基础。R3M 证明视觉预训练可与机器人解耦；RT-1 证明 Transformer 策略可在 130k 真实数据上规模化；ACT 用动作分块解决复合误差；RoboAgent 把 ACT 推广到多任务并用语义增强弥补数据稀缺。技术演化路线清晰指向「更大模型 + 更多数据 + 更长动作 chunk」，但这些工作仍以模仿学习为主、尚未引入互联网级 VLM/LLM 主干，为下一阶段大模型驱动 VLA 的诞生埋下伏笔。

### 5.2A 大模型驱动 VLA — 闭源/企业系

2023 年 7 月 RT-2 首次提出 VLA 概念后，主流路线转向「继承 LLM/VLM 权重 + 机器人轨迹微调」。本子节聚焦闭源/企业系（Google/DeepMind、Stanford 衍生开源、英伟达）四篇代表作：RT-2 开创动作 token 化范式、PaLM-E 提供 VLM 基座先验、OpenVLA 实现 7B 完全开源对标 55B 闭源、GR00T N1 探索人形机器人双系统架构。这条路线的共同特征是充分利用 VLM/LLM 的预训练权重，通过 co-fine-tune 或分层架构将互联网级语义知识迁移到机器人控制。

```json
[
  {"method_name": "RT2", "summary_with_citations": "Brohan 等人 [5, p.1] 在 Google DeepMind 提出 RT-2，首次定义并使用「视觉-语言-动作（VLA）」术语。RT-2 将 6-DoF 末端位移/旋转、夹爪、终止信号离散为 256 bins 并复用 PaLI-X (5B/55B) 与 PaLM-E (12B) 等 VLM 词表，与 web VQA/caption 数据混训得到 VLA [5, p.1]。在约 6000 次真机评估中，RT-2 在新物体、新背景、新环境上的泛化能力较 RT-1、VC-1、MOO 等基线显著提升约 2-6 倍 [5, p.9]，并展现出符号理解、推理、人物识别等「涌现能力」，进一步引入 chain-of-thought 后还能完成多阶段语义推理（如挑选岩石作锤子）[5, p.4]。在 Language-Table 仿真上 RT-2-PaLI-3B 达 90% 成功率，远超 LAVA 77%、RT-1 74% [5, p.9]。RT-2 是 5.2A 闭源/企业系的开山之作，但闭源、推理慢（55B-PaLI-X 仅 1-3Hz）、动作技能受限于机器人数据分布 [5, p.11]。"},
  {"method_name": "PaLME", "summary_with_citations": "Driess 等人 [6, p.4] 提出「具身语言模型」PaLM-E，将连续的真实世界传感器模态（图像、状态估计、3D 神经场景表征 OSRT）通过编码器投影到 LLM 词嵌入空间，与文本 token 交织成「多模态句子」端到端送入预训练大语言模型 PaLM [6, p.4]。最大 PaLM-E-562B 由 540B PaLM 与 22B ViT 组成。在 TAMP、Language-Table、移动操作三个机器人域以及 OK-VQA、VQAv2、COCO 等通用视觉-语言任务上同时取得高水平表现：TAMP 1% 数据规划成功率达 94.9% [6, p.7]，Language-Table Task1 成功率 80% [6, p.9]，OK-VQA 准确率 66.1% [6, p.9]。关键创新包括神经场景表征 OSRT 与实体标签 token 显著提升数据效率 [6, p.5]，以及大模型规模化可大幅减少多模态微调灾难性遗忘（562B 仅退化 3.9%）[6, p.9]。PaLM-E 是 RT-2 直接继承的 VLM 基座论文，但其本身止步于高层 planner 不直接输出底层动作。"},
  {"method_name": "OpenVLA", "summary_with_citations": "Kim 等人 [7, p.2] 提出 OpenVLA——首个 7B 参数完全开源的 VLA 模型，使用 Llama 2 7B 作为语言骨干并融合 DINOv2 与 SigLIP 双视觉编码器 [7, p.4]。在 Open-X Embodiment 数据集中精选 970k 真机演示后微调，将连续 7-D 动作离散为 256 bins 并复用 Llama tokenizer 末尾 256 个最少使用 token [7, p.5]。在 BridgeData V2 与 Google robot 共 29 个任务上以 7× 更小参数超越闭源 RT-2-X (55B) 16.5% 绝对成功率：BridgeData V2 平均成功率 70.6% vs RT-2-X 50.6%，Google robot 85.0% vs 78.3% [7, p.26-28]。首次系统研究 VLA 高效微调，LoRA 仅训 1.4% 参数即可与全参微调持平（Franka-Tabletop LoRA r=32 达 68.2% vs 全参 69.7%）[7, p.10]，结合 4-bit 量化可在消费级 GPU 上以 7GB 显存运行。但 OpenVLA 仅支持单图观测、推理频率不足以驱动 ALOHA (50Hz) 等高频双臂任务、整体可靠性仍 <90% 成功率 [7, p.11]。"},
  {"method_name": "GR00TN1", "summary_with_citations": "NVIDIA [8, p.4] 提出 GR00T N1——面向人形机器人的开源 VLA 基础模型，采用「双系统」架构：System 2 是预训练的 Eagle-2 VLM（SmolLM2 + SigLIP-2，1.34B 参数，10Hz 解释指令）；System 1 是 Diffusion Transformer，用 flow-matching 训练，跨注意 VLM 输出 token 并经 embodiment-specific 状态/动作编解码器生成 16 步动作 chunk（120Hz）[8, p.4]。训练语料组成「数据金字塔」：底部网络/人类视频（用 latent action / IDM 伪标签）、中部合成数据（DexMimicGen 模拟 540k 演示 + 视频生成 827h 神经轨迹）、顶部真机遥操作 ~140k+ 轨迹 [8, p.10]。GR00T-N1-2B（2.2B 总参）在 RoboCasa 平均成功率 32.1%、DexMG 66.5%、GR-1 50.0%，比 Diffusion Policy +17.3% [8, p.15]；真机 GR-1 全数据 76.8% vs Diffusion Policy 46.4%，10% 数据下 42.6% vs Diffusion Policy 10.2% [8, p.15]。L40 GPU 上 16 步 chunk 推理仅 63.9 ms [8, p.3]。GR00T N1 是 NVIDIA 把基础模型推进到 humanoid 通用控制的标志作品，但当前只面向短时桌面操作 [8, p.17]。"}
]
```

本子节小结：5.2A 四篇工作展示了大模型驱动 VLA 的两条主流技术路线对决。RT-2 与 OpenVLA 走「动作即 token」自回归路线，简洁但受限于离散化精度与自回归推理速度；PaLM-E 走「LLM-as-Planner」松耦合路线，仅产出高层语义子目标；GR00T N1 则走「VLM 高层 + DiT 低层 flow-matching」双系统分层路线，兼顾语义推理（10Hz）与高频动作生成（120Hz）。从 RT-2 (55B 闭源) → OpenVLA (7B 开源) → GR00T N1 (2.2B 开源 humanoid) 的演化清晰展示了「参数量缩小 + 开源化 + 跨形态」的产业趋势。

### 5.2B 大模型驱动 VLA — Pi 系列

Physical Intelligence 公司的 π 系列代表了与 5.2A 闭源/企业系平行的另一条技术演化线，其核心特征是「PaliGemma VLM 主干 + Flow Matching 动作专家」的混合专家架构。本子节按时间顺序综述 π0、π0.5、π*0.6 三代工作，分别对应基础架构奠定、开放世界泛化、强化学习自我改进三个里程碑。π 系列与 5.2A 的关键差异在于：拒绝动作离散化、坚持连续 Flow Matching 动作头、强调跨形态联合训练与真实家庭部署。

```json
[
  {"method_name": "Pi0", "summary_with_citations": "Black 等人 [9, p.4] 在 Physical Intelligence 提出 π0——首个面向通用机器人控制的视觉-语言-动作流匹配模型。π0 以 PaliGemma 3B VLM 作为骨干，额外引入 300M 参数的「动作专家」（action expert）模块输出连续动作分布，总参数量 3.3B [9, p.4]。使用条件流匹配（conditional flow matching）建模高频灵巧动作，推理仅 10 步欧拉积分 [9, p.5]。模型在自有 7 类机器人形态、68 个任务的灵巧操作数据集（903M 步）+ Open-X-Embodiment 子集 OXE Magic Soup（占 9.1%）上联合预训练 [9, p.5]，并通过高质量后训练数据微调到下游任务。Mixture-of-Experts 风格分离：图像/语言走 VLM 权重，动作/状态走 action expert 权重 [9, p.5]。π0 演示了端到端机器人学习中迄今最长的灵巧任务，包括叠衣、清桌、装杂货袋、装盒等 5 至 20 分钟时长的多阶段操作 [9, p.4]。Out-of-Box 评估在 5 个任务上 normalized score 接近 1.0，远超 OpenVLA 与 Octo [9, p.8]。π0 是 5.2B Pi 系列开山之作，奠定了「VLM 继承 + Flow Matching 动作头」双模块架构范式。"},
  {"method_name": "Pi05", "summary_with_citations": "Physical Intelligence 团队 [10, p.3] 提出 π0.5，致力于解决机器人在开放世界（尤其是从未见过的真实家庭环境）中的泛化问题。π0.5 通过异构多源数据 co-training 实现广泛迁移，包括约 400 小时移动机械臂数据（97.6% 训练样本来自其他源）[10, p.2]、其他非移动机器人数据、跨身体实验室数据（含 OXE）、高层语义子任务预测、人类口头指令以及多模态网络数据（CapsFusion、COCO、Cambrian-7M、PixMo、VQAv2）[10, p.6]。架构上采用两阶段训练：预训练阶段以离散 token 形式融合所有数据源；后训练阶段加入流匹配动作专家以输出连续动作 [10, p.5]。推理时模型先预测高层子任务再输出低层动作。实验显示 π0.5 可在三个全新真实家庭中完成 10-15 分钟时长的厨房与卧室清扫任务（把餐具放进水池、把物品放进抽屉、把衣服放进洗衣篮、铺床、挂毛巾、擦溢出物、关橱柜等）[10, p.7]，端到端学习的机器人系统首次实现这种程度的开放世界长程泛化 [10, p.3]。Mock home 4 任务上 π0.5 显著优于 π0 与 π0-FAST+Flow [10, p.10]。但 π0.5 仍会出错，部分可观测性下表现下降，高层子任务推理易被分散注意力 [10, p.11]。"},
  {"method_name": "Pi06", "summary_with_citations": "Physical Intelligence 团队 [11, p.1] 提出 π*0.6 与 RECAP（RL with Experience and Corrections via Advantage-conditioned Policies）方法，研究如何让 VLA 模型通过真实世界部署中的强化学习不断进步。π*0.6 基于 π0.6（Gemma 3 4B 主干 + 860M 动作专家），新增对二值化 advantage 指示器的条件化能力 [11, p.2]。RECAP 先用离线 RL 预训练通用 VLA 得到 π*0.6，再通过下游任务的机器人数据收集进行专项化，结合示范+自主 rollout+人类干预三类异质数据 [11, p.5]。关键创新包括二值化 advantage 指示器作为 prompt 条件 [11, p.2]、多任务 distributional value function 估计步数到成功 [11, p.4]、Human-gated DAgger 风格干预与自主 rollout 联合训练。在叠衣、装配纸盒、用专业咖啡机制作浓缩咖啡等真实任务上，RECAP 在最难任务上吞吐量翻倍以上、失败率约减半 [11, p.2]。Laundry T-shirt 严格成功率达 97% [11, p.11]，box assembly 子阶段成功率约 90%、第二次迭代后吞吐量 2× 提升 [11, p.10]。能让机器人连续 13 小时制作咖啡、连续 2 小时折叠从未见过的衣物。但系统非完全自主，仍依赖人工标注奖励、人工干预与重置 [11, p.11]。"}
]
```

本子节小结：Pi 系列三代工作呈现「架构奠基 → 数据扩展 → 训练范式革新」的清晰演化路径。π0 用 PaliGemma + Flow Matching 双模块架构突破自回归动作离散化的精度瓶颈；π0.5 用异构多源 co-training 让 VLA 跨入开放世界家庭场景；π*0.6 用 RECAP 离线 RL 配方让 VLA 在部署中持续自我改进。与 5.2A 闭源/企业系相比，Pi 系列的特色在于坚持连续动作流匹配范式、强调跨本体联合训练（7 类机器人形态、68 任务）、注重真实家庭部署而非仿真基准刷分，是当前 VLA 实用化的最前沿代表。

### 5.3 仿真与基础设施

VLA 模型的训练数据需求远超传统机器人策略，仿真器、扩散动作头、世界模型与跨形态数据生成器成为支撑 VLA 发展的关键基础设施。本子节综述 3 篇代表性工作：Diffusion Policy 提供扩散动作头基线、Genie Envisioner 构建视频世界模型平台、RoboTwin 2.0 打造 MLLM 驱动的可扩展双臂数据工厂。三者分别从「动作建模 / 神经仿真 / 数据生成」三个维度为 VLA 训练与评估提供基础设施支撑。

```json
[
  {"method_name": "DiffusionPolicy", "summary_with_citations": "Chi 等人 [12, p.1] 提出 Diffusion Policy，把机器人 visuomotor 策略表示为条件去噪扩散过程。模型学习动作分布得分函数的梯度，并在推理时通过随机 Langevin 动力学迭代优化 [12, p.1]。该形式化天然支持多模态动作分布、高维输出空间、训练稳定，三个特性都直接对应模仿学习的痛点。论文进一步引入 receding horizon 闭环控制、视觉条件化（FiLM 注入）、时间序列扩散 Transformer 三项关键技术 [12, p.2]，使扩散模型可在物理机器人上实时部署。在 4 个基准 15 个任务上系统评测，相对 SOTA 平均提升 46.9% [12, p.6]：Robomimic Square (ph) state success rate DP-T 1.00/0.89 vs LSTM-GMM 0.95/0.73；Push-T image-based DP-C 0.91/0.84 vs LSTM-GMM 0.69/0.54；Franka Kitchen p4 success DP-C 0.99 vs BET 0.44 [12, p.7-8]。在真实世界单臂 Push-T、Mug Flip、Sauce Pour/Spread 与双臂 Egg Beater、Mat Unrolling、Shirt Folding 上验证，Realworld Push-T 95% [12, p.9]。Diffusion Policy 是 2023 年至今几乎所有 VLA 动作 head 的共同祖先，但推理延迟高于 LSTM-GMM、未与离线 RL 结合 [12, p.13]。"},
  {"method_name": "GenieEnvisioner", "summary_with_citations": "Liao 等人 [13, p.1] 提出 Genie Envisioner（GE）——把策略学习、评测与仿真整合到单一视频生成框架内的世界基础平台。核心 GE-Base 是一个指令条件化、多视角的视频扩散模型，在 AgiBot-World-Beta 约 3000 小时、百万级真实双臂操作 episode 上训练，捕获时空与语义动力学 [13, p.5]。GE-Act 用轻量 160M flow-matching 解码器把视觉潜表示映射为可执行动作轨迹，54 步动作 200 ms 内完成 [13, p.3]；GE-Sim 把生成动力学转为动作条件神经仿真器，支持闭环 rollout，千 episode/小时高速并行评测 [13, p.3]。配套 EWMBench 基准从 scene/motion/semantics 三层评测视频世界模型，GE-Base 总分 4.7010 显著高于 Kling 3.8698、Hailuo 3.4125 [13, p.21]。GE-Act 在 AgiBot G1、Dual Franka、Agilex Cobot Magic 上仅需 1 小时遥操数据即超越 GR00T N1、π0、UniVLA [13, p.3]。GE 是「视频世界模型 + 动作头 + 神经仿真器 + 评测」四件套统一在同一个 latent 空间的工业级平台，但训练只用 AgiBot-World-Beta 单一来源、仅限上半身桌面操作 + 平行夹爪 [13, p.23]。"},
  {"method_name": "RoboTwin2", "summary_with_citations": "Chen 等人 [14, p.2] 提出 RoboTwin 2.0——面向鲁棒双臂操作的可扩展仿真数据生成框架。针对现有合成数据三大问题（无自动质控、域随机化粗糙、忽视跨本体差异），系统集成三件套：MLLM + 仿真在环反馈的自动专家代码生成 pipeline，能零样本合成超出 pick-and-place 的双臂行为 [14, p.3]；覆盖 clutter / lighting / background / tabletop height / language instruction 五维的域随机化；embodiment-aware 抓取适配。配套发布 RoboTwin-OD（731 物体 / 147 类别）、50 个双臂任务、5 个本体（Aloha-AgileX、ARX-X5、Piper、Franka、UR5）、10 万+ 预采轨迹 [14, p.6]。代码生成 ASR 提升 10.9%（R2.0+MMFB 71.3% vs R1.0 Vanilla 47.4%）[14, p.8]；VLA 模型混合大规模合成数据 + 仅 10 条真实演示比 10-demo baseline 提升 367% 相对值；零样本仅靠合成数据也提升 228% [14, p.2]。Real-World 4 任务平均（Unseen+Cluttered）10Real+1k RoboTwin2.0 达 42.0% vs 10 Clean Real 9.0% [14, p.10]。RoboTwin 2.0 是当前合成数据驱动 VLA 训练最成熟的开源基础设施。"}
]
```

本子节小结：5.3 三篇工作从动作建模、神经仿真、数据生成三个维度构成 VLA 训练与评估的关键基础设施。Diffusion Policy 把扩散模型引入机器人策略，奠定了 π0/GR00T N1/RDT 等扩散 VLA 的方法基线；Genie Envisioner 用视频扩散模型同时承担「世界模型 + 神经仿真器 + 评测基准」三重角色，把「世界模型 = 仿真器」口号真正落地；RoboTwin 2.0 用 MLLM + 仿真在环反馈打造工业级可控数据工厂。三者分别从「算法层 / 仿真层 / 数据层」为 VLA 提供基础设施支撑，与 5.1/5.2 主线模型形成「算法-数据-评测」闭环生态。

## 数据集与评价指标

VLA 模型的数据集与评价指标体系已基本成熟，分为训练数据集、仿真器/评测基准与评价指标三大类。**训练数据集**层面，Open X-Embodiment（OXE）整合 22 种机器人、527 种技能、1M+ 轨迹，是 VLA 跨形态预训练的黄金标准 [7, p.5]；DROID 含 76k 真实演示覆盖 564 真实场景 86 任务；BridgeData V2 含 60k 轨迹覆盖 WidowX 24 环境 [7, p.7]；RH20T 含 110k 接触序列覆盖视/力/音多模态；AgiBot World 提供 1M+ 轨迹 217 任务 87 技能共 2976 小时 [13, p.5]；π0 自有数据集 7 类机器人形态、68 任务、903M 步 [9, p.5]；GR00T N1 内部含 88h GR-1 人形遥操作数据 [8, p.10]；RoboTwin-OD 提供 731 物体 50 任务 5 本体 10 万+ 轨迹 [14, p.6]。视频预训练数据则包括 Ego4D（>3500 小时）[1, p.4]、EPIC-KITCHENS-100、Something-Something V2 等。**仿真器/评测基准**层面，LIBERO（MuJoCo, 130 程序生成终身学习任务）已成为 π0/OpenVLA/GR00T N1 等 VLA 横向对比的事实标准；SimplerEnv（SAPIEN, WidowX/Google Robot）覆盖多样化语言指令桌面操作；CALVIN（PyBullet, Franka Panda 长序列语言指令）；Meta-World（MuJoCo, 50 元学习/多任务）；RLBench（CoppeliaSim, 100 大规模多样化）；RoboCasa（24 任务厨房原子操作）[8, p.15]；DexMimicGen（9 双手任务）[8, p.10]；Robomimic（PH/MH 5 任务 9 变体）[12, p.7]；Push-T、Block Push、Franka Kitchen 等。RT-1 自评测覆盖 Seen/Unseen/Distractors/Backgrounds 四类 700+ 任务 [2, p.9]。**评价指标**层面，任务成功率（Success Rate）是当前 VLA 评估首选绝对指标 [11, p.9]；任务进度（Task Progress）由 π0.5 推广作为细粒度过程评估 [10, p.7]；吞吐量（Throughput, 每小时成功任务数）由 π*0.6 用作长程任务实用化指标 [11, p.9]；能力对数（RoboArena Score）作为相对评价指标降低主观偏差；归一化分数（Normalized Score）由 π0 用作 partial success 评估 [9, p.8]；语言跟随率（Language Following Rate）评估指令理解；ASR/Top5-ASR 由 RoboTwin 2.0 用作合成数据生成质量指标 [14, p.8]；EWMBench 含 Scene Consistency / Spatial Alignment / Temporal Alignment / Dynamic Consistency 等多维视频世界模型评估 [13, p.21]。

## 性能对比与分析

```json
[
  {"method": "RT1", "dataset": "Real Robot Seen Tasks", "metric": "Success Rate", "value": "97%", "citation": "[2, p.9, Tab.2]"},
  {"method": "RT1", "dataset": "Real Robot Unseen Tasks", "metric": "Success Rate", "value": "76%", "citation": "[2, p.9, Tab.2]"},
  {"method": "R3M", "dataset": "All Domains (12 sim tasks)", "metric": "Success Rate", "value": "62.4%", "citation": "[1, p.7, Tab.1]"},
  {"method": "ACT", "dataset": "Slot Battery (real)", "metric": "Final Insert Success", "value": "96%", "citation": "[4, p.8, Tab.I]"},
  {"method": "RoboAgent", "dataset": "All Activities L1", "metric": "Success Rate", "value": "75%", "citation": "[3, p.8, Fig.7]"},
  {"method": "RT2", "dataset": "Language-Table sim", "metric": "Success Rate", "value": "90%", "citation": "[5, p.9, Tab.1]"},
  {"method": "PaLME", "dataset": "TAMP 1% data", "metric": "Planning Success Rate", "value": "94.9%", "citation": "[6, p.7, Fig.4]"},
  {"method": "OpenVLA", "dataset": "BridgeData V2", "metric": "Mean Success Rate", "value": "70.6%", "citation": "[7, p.26, Tab.4]"},
  {"method": "OpenVLA", "dataset": "Google Robot", "metric": "Mean Success Rate", "value": "85.0%", "citation": "[7, p.28, Tab.6]"},
  {"method": "GR00TN1", "dataset": "Real GR-1 Full Data", "metric": "Mean Success Rate", "value": "76.8%", "citation": "[8, p.15, Tab.3]"},
  {"method": "GR00TN1", "dataset": "DexMG (9 tasks, 100 demos)", "metric": "Mean Success Rate", "value": "66.5%", "citation": "[8, p.15, Tab.2]"},
  {"method": "Pi0", "dataset": "Out-of-Box (5 tasks)", "metric": "Normalized Score", "value": "near 1.0", "citation": "[9, p.8, Fig.7]"},
  {"method": "Pi05", "dataset": "Real Homes (3 kitchen+3 bedroom)", "metric": "Long-horizon Task Progress", "value": "10-15 min stable", "citation": "[10, p.8, Fig.7]"},
  {"method": "Pi06", "dataset": "Laundry T-shirt strict", "metric": "Success Rate", "value": "97%", "citation": "[11, p.11, Fig.12]"},
  {"method": "DiffusionPolicy", "dataset": "Realworld Push-T", "metric": "Success Rate", "value": "95%", "citation": "[12, p.9, Tab.6]"},
  {"method": "DiffusionPolicy", "dataset": "Franka Kitchen p4", "metric": "Success Rate", "value": "99%", "citation": "[12, p.8, Tab.4]"},
  {"method": "GenieEnvisioner", "dataset": "EWMBench Total", "metric": "Score", "value": "4.7010", "citation": "[13, p.21]"},
  {"method": "GenieEnvisioner", "dataset": "AgiBot G1 grasp-cylinder", "metric": "End-to-End Success", "value": "0.89", "citation": "[13, p.12, Tab.1]"},
  {"method": "RoboTwin2", "dataset": "Code Generation R2.0+MMFB", "metric": "ASR", "value": "71.3%", "citation": "[14, p.8, Tab.1]"},
  {"method": "RoboTwin2", "dataset": "Real-World 10Real+1k Synth", "metric": "Mean Success Rate", "value": "42.0%", "citation": "[14, p.10, Tab.4]"}
]
```

横向对比上述 14 篇代表工作的性能数据可得三点关键结论。**第一，方法谱系决定性能上限**：早期 VLA（R3M 12 任务平均 62.4%、RT-1 已见任务 97% 但未见 76%）在固定任务集合上接近饱和，但跨任务泛化弱；大模型驱动 VLA 把跨任务、跨场景泛化推向新高度——RT-2 在新物体/背景/环境上较 RT-1 提升 2-6 倍 [5, p.9]，OpenVLA 以 7B 参数超越 55B RT-2-X 达 16.5% [7, p.2]；Pi 系列则进一步把 VLA 推到 10-15 分钟时长的真实家庭长程操作 [10, p.2]。**第二，参数量与可靠性并非线性关系**：OpenVLA 7B 击败 RT-2-X 55B 表明数据精选与架构选择的重要性高于盲目堆参；GR00T N1 仅 2.2B 参数即可在真实 GR-1 全数据上达 76.8% 平均成功率 [8, p.15]，大幅领先 Diffusion Policy 46.4%。**第三，Flow Matching 与扩散动作头是当前事实标准**：Diffusion Policy 在 15 任务上相对 SOTA 平均提升 46.9%，π0、π0.5、π*0.6、GR00T N1 均采用流匹配/扩散动作头，证明连续动作建模优于离散 token 化。RoboTwin 2.0 + Pi0 混合大规模合成 + 10 真实数据相比 10 真实 baseline 提升 367% 相对值 [14, p.2]，揭示「合成数据 + 少量真实微调」是数据效率最高的训练范式。**第四，π*0.6 标志 VLA 进入「持续部署 + RL 自我改进」时代**：Laundry T-shirt 严格成功率 97%、box assembly 第二次迭代吞吐 2× 提升，把 VLA 从「能做」推向「实用化连续运行 13 小时」级别。

## 存在的问题与挑战

VLA 模型虽在过去三年取得显著进展，但仍面临五大开放性挑战。**第一，泛化能力受限**：现有 VLA 对背景、光照、视角变化敏感，跨形态泛化能力差，几乎无法跨本体复用同一参数；R3M、RT-1、ACT 在「未见任务」上成功率均显著下降（RT-1 已见 97% 降至未见 76% [2, p.9]）；RoboAgent 在 L4 全新厨房上仅 25% 成功率 [3, p.10]。综述也指出「目前 VLA 模型几乎不具备跨任务泛化能力」。**第二，精细接触操作困难**：高频精细操作（插入、堆叠、密集接触）成功率低，遥操作数据动作一致性差，缺乏触觉/力觉模态对齐；OpenVLA「整体可靠性仍 <90% 成功率」[7, p.11]、ACT 仍存在「扣纽扣式衬衫」等硬件与算法均无法处理的任务 [4, p.10]。**第三，实时推理瓶颈**：VLA 大模型继承自 VLM 参数量大（RT-2-PaLI-X 55B 仅 1-3Hz [5, p.6]、OpenVLA 推理频率不足以驱动 ALOHA 50Hz [7, p.11]、π0 3.3B「在实时机器人控制场景下推理负担仍重」[9, p.4]），机器人端侧算力受限；动作分块、异步分层、模型量化是三大缓解方向但优化与泛化能力存在折中。**第四，数据飞轮缺失**：真实机器人数据相比 LLM/VLM 仍小 3-4 个数量级，遥操作采集成本高、操作员一致性差；GR00T N1 指出「现有视频/合成数据生成方法在多样性、反事实场景与物理一致性上仍有局限」[8, p.17]，π*0.6 系统「非完全自主，仍依赖人工标注奖励、人工干预与重置」[11, p.11]。**第五，评估方法的可复现性弱**：真实环境评估场景设计主观且难复现，仿真器与真实差距使结果代表性弱；Genie Envisioner 的 EWMBench 仍依赖代理指标与部分人工验证 [13, p.23]，π0.5 高层子任务推理「易被分散注意力」[10, p.11] 等行为级缺陷尚无标准评估方法。

## 未来发展趋势与展望

针对上述挑战，VLA 模型未来发展呈现五大趋势。**第一，跨本体泛化与统一基础模型**：GR00T N1 的「数据金字塔」与 latent action 共享空间已展示跨人/机器人 embodiment 共享潜力 [8, p.5]，未来通用 VLA 基础模型有望像 LLM 一样以单组权重适配多种机器人本体（人形、双臂、单臂、四足）。**第二，思维链推理与高层语义规划集成**：RT-2 的 chain-of-thought 已展示符号理解、数学推理涌现能力 [5, p.4]，π0.5 的「先预测高层子任务再生成低层动作」也证明同一模型承担高/低层推理可行 [10, p.5]，未来 VLA 将与 LLM Agent 框架深度融合，支持多步推理、工具使用、失败自纠正。**第三，在线强化学习后训练成为标配**：π*0.6 的 RECAP 配方首次将完整离线 RL 配方落到 flow-matching VLA 上端到端训练 [11, p.2]，把 VLA 推向「实用化部署后持续改进」；未来在线 RL 后训练的稠密奖励、安全探索、人机交互式反馈将成为关键技术方向。**第四，世界模型与神经仿真器协同**：Genie Envisioner 的「视频世界模型 + 神经仿真器 + 评测基准」一体化架构 [13, p.2] 与 RoboTwin 2.0 的 MLLM 驱动数据生成 [14, p.3] 互为补充，未来「世界模型驱动的合成数据 + 闭环评测」将大幅缓解真机数据稀缺。**第五，端侧高效推理与开源生态**：OpenVLA 的 LoRA + 4-bit 量化路线 [7, p.10] 已让 VLA 在消费级 GPU 7GB 显存运行，未来模型压缩、推测解码、稀疏激活、专用机器人加速器有望把 VLA 推到 50Hz 以上的高频控制场景，配合开源生态推动产业化落地。

## 总结

本文系统调研了具身操作方向 VLA 模型的发展脉络与代表性工作，覆盖 14 篇关键论文，从早期 VLA 萌芽（R3M、RT-1、RoboAgent、ACT）、大模型驱动 VLA（RT-2、PaLM-E、OpenVLA、GR00T N1、π0、π0.5、π*0.6）到仿真与基础设施（Diffusion Policy、Genie Envisioner、RoboTwin 2.0）三大维度展开。本调研呼应引言中提出的核心问题，揭示了 VLA 模型的两条主流技术演化线——「VLM 主干 + 动作 token 化」自回归路线与「PaliGemma + Flow Matching 动作专家」分层路线，并指出 Flow Matching/扩散动作头已成为当代 VLA 事实标准。横向性能对比显示参数量与可靠性并非线性关系，OpenVLA 7B 击败 RT-2-X 55B、GR00T N1 2.2B 在真机 GR-1 上 76.8% 等案例表明数据精选与架构选择的重要性高于盲目堆参。本调研同时归纳了泛化能力受限、精细接触困难、实时推理瓶颈、数据飞轮缺失、评估可复现性弱五大开放问题，并展望了跨本体基础模型、思维链推理、在线 RL 后训练、世界模型协同、端侧高效推理五大未来方向。本调研的局限性在于聚焦操作方向而未覆盖导航与全身运动 VLA，且截稿时点未能纳入最新的 GR-3、UniVLA 等增量工作。

## 参考文献

由 generate_survey.js 自动从 extracts/ 收集，按引用顺序编号 [1]-[14]。
