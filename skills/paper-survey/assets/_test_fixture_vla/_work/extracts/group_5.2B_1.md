### #1 Pi0 (Black et al., arXiv 2024)

- 标题：π0: A Vision-Language-Action Flow Model for General Robot Control
- 作者：Kevin Black, Noah Brown, Danny Driess, Adnan Esmail, Michael Equi, Chelsea Finn, Sergey Levine 等（Physical Intelligence）
- 发表年份：2024
- venue：arXiv 2024（Physical Intelligence 公司技术报告）
- arXiv ID：2410.24164

- 中文摘要：本文提出 π0——首个面向通用机器人控制的视觉-语言-动作（VLA）流匹配模型。π0 以 PaliGemma 3B 视觉-语言模型（VLM）作为骨干，额外引入 300M 参数的"动作专家"（action expert）模块输出连续动作分布，总参数量 3.3B，使用条件流匹配（conditional flow matching）建模高频灵巧动作。模型在自有 7 类机器人形态、68 个任务的灵巧操作数据集 + Open-X-Embodiment 子集（OXE Magic Soup）上联合预训练，并通过高质量后训练数据微调到下游任务。π0 演示了端到端机器人学习中迄今最长的灵巧任务，包括叠衣、清桌、装杂货袋、装盒等 5 至 20 分钟时长的多阶段操作。

- 核心方法：在 PaliGemma VLM 骨干基础上接入独立动作专家头并用 Flow Matching 训练连续动作分布；关键创新：(1) 把 VLM 互联网级语义先验迁移到机器人控制 〔p.4: "VLM backbone weights are initialized from PaliGemma"〕；(2) Flow Matching 取代 autoregressive 离散化，原生支持高频动作 chunk 〔p.4: "uses conditional flow matching to model the continuous distribution of actions"〕；(3) Mixture-of-Experts 风格分离：图像/语言走 VLM 权重，动作/状态走 action expert 权重 〔p.5: "analogous to a mixture of experts with two mixture elements"〕；(4) 推理仅 10 步欧拉积分 〔p.5: "We use 10 integration steps"〕

- 主要贡献：(1) 首个统一架构覆盖 7 类机器人形态和 68 个灵巧任务的通用机器人 VLA 模型；(2) 把 Flow Matching 引入 VLA 动作建模，原生支持高频灵巧控制；(3) 演示端到端机器人学习中最长的灵巧任务（折衣、清桌、装盒）〔p.4: "demonstrates the longest dexterous tasks in the end-to-end robot learning literature"〕

- 与本调研主题的关系：本论文是 5.2B Pi 系列开山之作，奠定了"VLM 继承 + Flow Matching 动作头"双模块架构范式，是后续 Pi05 / Pi06 / 以及第三方 GR00T-N1 等分层 VLA 的直接技术起点；同时是 5.2 内部 OpenVLA（自回归动作离散化）路线的明确反例。

- 优点：跨多种机器人形态泛化（包括 UR5e / Franka / Bimanual / Mobile）〔p.6: "trained jointly on all of these platforms"〕；高频灵巧控制能力 〔p.4: "high-frequency dexterous tasks"〕；Out-of-Box 评估在 5 个任务上大幅优于 OpenVLA 与 Octo 基线 〔p.8: "π0 achieves the best results by a large margin"〕

- 局限性 / 缺陷：参数量 3.3B 在实时机器人控制场景下推理负担仍重 〔p.4: "comparatively small size (which is useful for real-time control)"〕（隐含表明大模型实时性是关键约束）；π0-small 缺 VLM 预训练时语言遵循能力显著退化 〔p.9: "due to π0-small's limited language following ability"〕，说明依赖大规模 VLM 预训练

- 典型应用场景：双臂灵巧操作（叠衣、清桌、设餐桌、装杂货袋、装盒）〔p.4: "laundry folding, table cleaning, and assembling boxes"〕；语言指令多阶段执行（含 high-level VLM 规划）〔p.7: "high-level VLM policy"〕

- 使用的数据集名 + 规模：自有数据集（7 种机器人形态、68 任务、903M 步）〔p.5-6: "903M timesteps of data from our own datasets"〕；OXE Magic Soup（OXE [10] / Bridge v2 / DROID 子集，占 9.1% 时间步）〔p.5: "9.1% of the training mixture consists of open-source datasets"〕

- 评价指标名 + 定义：normalized score——每任务 10 episodes 平均，full success=1.0，partial=分数（如 bussing 是正确放置物品比例）〔p.8: "scoreof1.0forafullsuccess,andafractionalscoreforpartial success"〕

- benchmark 数值：
  - Out-of-Box（5 任务平均）/ normalized score / 接近 1.0（远超 OpenVLA / Octo） 〔p.8, Fig.7〕
  - Shirt Folding / score / 接近 1.0（near-perfect） 〔p.8, Fig.7〕
  - Bussing Easy / score / 接近 1.0 〔p.8, Fig.7〕
  - Language following（π0-flat vs π0-small-flat）/ accuracy / π0 显著优于 π0-small 〔p.9, Fig.9〕
  - Fine-tuning new tasks (5 tiers) / score / 优于 ACT 与 Diffusion Policy 基线 〔p.10, Fig.11〕

- 一句话评述：π0 用 "VLM 骨干 + Flow Matching 动作专家" 把 LLM 时代的预训练红利首次完整地接入机器人灵巧操作，并在叠衣等长程任务上把 VLA 实用化基线拉到 5-20 分钟时长，是 Physical Intelligence Pi 系列的奠基坐标。

- 参考文献条目（GB/T 7714）：BLACK K, BROWN N, DRIESS D, et al. π0: A Vision-Language-Action Flow Model for General Robot Control[J]. arXiv preprint arXiv:2410.24164, 2024.
