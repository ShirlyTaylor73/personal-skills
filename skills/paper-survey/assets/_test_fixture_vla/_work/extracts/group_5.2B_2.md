### #2 Pi05 (Physical Intelligence et al., arXiv 2025)

- 标题：π0.5: a Vision-Language-Action Model with Open-World Generalization
- 作者：Physical Intelligence team（Kevin Black, Noah Brown, James Darpinian, Karan Dhabalia, Danny Driess, Adnan Esmail, Michael Equi, Chelsea Finn, Niccolo Fusai, Manuel Y. Galliker, Dibya Ghosh, Lachy Groom, Karol Hausman, Brian Ichter, Szymon Jakubczak, Tim Jones, Liyiming Ke, Devin LeBlanc, Sergey Levine, Adrian Li-Bell, Mohith Mothukuri, Suraj Nair, Karl Pertsch, Allen Z. Ren, Lucy Xiaoyang Shi, Laura Smith, Jost Tobias Springenberg, Kyle Stachowicz, James Tanner, Quan Vuong, Homer Walke, Anna Walling, Haohuan Wang, Lili Yu, Ury Zhilinsky）
- 发表年份：2025
- venue：arXiv preprint
- arXiv ID：2504.16054

- 中文摘要：本文提出 π0.5，这是基于 π0 的新一代视觉-语言-动作（VLA）模型，致力于解决机器人在开放世界（尤其是从未见过的真实家庭环境）中的泛化问题。π0.5 通过在异构多源数据上的协同训练（co-training）实现广泛迁移，包括约 400 小时移动机械臂数据、其他非移动机器人数据、跨身体（cross-embodiment）实验室数据、高层语义子任务预测、人类口头指令以及多模态网络数据。架构上采用两阶段训练：预训练阶段以离散 token 形式融合所有数据源；后训练阶段加入流匹配（flow matching）动作专家以输出连续动作。推理时模型先预测高层子任务再输出低层动作。实验显示 π0.5 可在三个全新真实家庭中完成 10-15 分钟时长的厨房与卧室清扫任务，端到端学习的机器人系统首次实现这种程度的开放世界长程泛化。

- 核心方法：基于 π0 的 VLA，采用预训练（离散 token 多源数据 co-training）+ 后训练（加入 flow matching 动作专家专门化移动操作）两阶段训练；推理时先预测高层语义子任务再生成低层动作。关键创新点：1) 异构多源 co-training 配方（MM/ME/CE/HL/WD/VI 六类数据）；2) 离散 token 与连续 flow matching 混合动作表示；3) 同一模型同时承担高层与低层推理 〔p.4: "pre-training stage ... and a post-training stage"〕〔p.5: "trained to predict actions both through autoregressive sampling ... and iterative integration of the flow field"〕

- 主要贡献：1）提出可高度泛化的 VLA 训练系统 π0.5 及其概念验证；2）实证评估 π0.5 在新家庭环境中的泛化能力以及各 co-training 组件的贡献；3）首次展示端到端学习机器人系统能在全新家庭中完成厨房/卧室清扫等长程精细操作 〔p.3: "Our central contribution is a system for training a highly generalizable VLA, π0.5"〕〔p.3: "first to demonstrate an end-to-end learning-enabled robotic system that can perform long-horizon and dexterous manipulation skills"〕

- 与本调研主题的关系：作为 π0 的后续版本，是开放世界泛化路线的代表工作，证明通过异构数据 co-training 可使 VLA 在未见过的家庭环境中执行 10-15 分钟长程任务，是 5.2B 子节"VLA 开放世界泛化"维度的关键节点。

- 优点：1) 仅 400 小时移动操作数据即可实现强泛化（97.6% 训练样本来自其他源）；2) 在三个真实新家庭中可完成多阶段长程任务（10-15 分钟）；3) 同一模型统一承担高层与低层推理 〔p.2: "about 400 hours"〕〔p.2: "97.6% during the first training phase"〕〔p.2: "long-horizon manipulation skills 10 to 15 minutes in length"〕

- 局限性：仍会出错；某些环境（不熟悉的抽屉把手、难开的橱柜）持续具有挑战；部分可观测性下表现下降（机械臂遮挡溢出物）；高层子任务推理易被分散注意力（反复开关抽屉）；只能处理相对简单的 prompt；上下文与记忆有限 〔p.11: "it still makes mistakes"〕〔p.11: "high-level subtask inference is easily distracted"〕〔p.11: "processes relatively simple prompts"〕

- 典型应用场景：移动机械臂在真实家庭中清扫厨房与卧室，包括把餐具放进水池、把物品放进抽屉、把衣服放进洗衣篮、铺床、挂毛巾、擦溢出物、关橱柜等多阶段任务 〔p.1: "clean kitchens and bedrooms in new homes"〕〔p.7: "items in drawer", "laundry basket", "dishes in sink"〕

- 数据集：1) 移动机械臂数据（MM）约 400 小时、约 100 个家庭环境；2) 多环境非移动机器人数据（ME）；3) 跨身体实验室数据（CE）含 OXE [15]；4) 高层子任务预测数据（HL）；5) 多模态网络数据（WD），含 CapsFusion、COCO、Cambrian-7M、PixMo、VQAv2；6) 口头指令数据（VI） 〔p.6: "about 400 hours of data of mobile manipulators ... about 100 different home environments"〕〔p.6: "CapsFusion [87], COCO [12]), question answering (Cambrian-7M [77], PixMo [19], VQAv2 [32])"〕

- 评价指标：任务进度 task progress（按评估 rubric 分阶段计算成功完成步骤的百分比，例如把一半碗碟放进水池约对应 50%）；语言跟随率 language following rate（机器人选取语言指定物体的频率）；成功率 success rate（成功放置到目标位置的频率） 〔p.7: "roughly correspond to the percentage of steps in each task that were completed successfully"〕〔p.9: "language following rate, which measures how often the robot selects the object indicated"〕

- benchmark 数值：
  - Mock home 4 tasks / 平均任务进度 / π0.5 显著优于 π0 与 π0-FAST+Flow（具体百分比见 Fig.12，未给出表格数字） 〔p.10, Fig.12: "π0.5 significantly outperforms both π0 and π0-FAST+Flow"〕
  - 104-location 训练 / 平均任务进度 / 与"训练时见过测试家庭"的对照模型表现相当 〔p.9, Fig.8: "achieves similar performance, despite not seeing any data from the test homes"〕
  - 真实家庭（3 厨房 + 3 卧室）/ 任务进度 / 在 items in drawer / laundry basket / dishes in sink 三任务上稳定成功（每任务 10 trials，量化结果见 Fig.7b） 〔p.8, Fig.7: "we evaluate ... averaged over 10 trials"〕
  - 高层推理评估 / 任务进度 / 完整 π0.5 优于 human HL oracle，no VI / no WD / GPT-4 zero-shot 显著更差（具体数值见 Fig.13） 〔p.11, Fig.13: "the full π0.5 model with high-level and low-level inference attains the best results"〕
  - 语言跟随 / 跟随率与成功率 / 训练位置数从 3 增至 104，in-distribution 与 OOD 物体表现稳定提升（见 Fig.9） 〔p.9, Fig.9: "Performance increases steadily as we increase the number of training locations"〕

- 一句话评述：π0.5 是 VLA 开放世界泛化方向的标志性工作，通过异构多源 co-training 配方让 VLA 首次在未见过的真实家庭中完成长程多阶段操作。

- 参考文献条目（GB/T 7714）：BLACK K, BROWN N, DARPINIAN J, et al. π0.5: A vision-language-action model with open-world generalization[J]. arXiv preprint arXiv:2504.16054, 2025.
