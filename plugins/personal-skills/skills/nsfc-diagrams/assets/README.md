# 真实参考与组件索引

先按模板选择下表素材，打开对应整图和至少一个相关局部，再规划新图。研究对象和流程仍由正文决定。参考图内的结论、数值、数据集、机器人类型不是可套用模板。

## 机制图素材

| ID | 真实参考 | 适用表达 | 限制 |
|---|---|---|---|
| M1 | [开放集第1页](references/mechanism/open-set-1.png) | 多模态输入、编码器、矩阵、聚类、分布与输出 | 借鉴对象和操作的表达，不照搬检测链 |
| M2 | [开放集第2页](references/mechanism/open-set-2.png) | 数据增强、双分支、共享权重、对比学习 | 两路只有技术上确实并行时才采用 |
| M3 | [开放集第3页](references/mechanism/open-set-3.png) | 局部区域、特征池化、候选与分布对齐 | 分布曲线是机制示意，不代表新项目测量结果 |
| M4 | [模板图3](references/mechanism/template-fig-3.png) | 场景生成、结构化记录、资产配置和反馈 | 参考多种素材组织，不复制长英文提示词 |
| M5 | [模板图4](references/mechanism/template-fig-4.png) | 特征序列演化、加噪/去噪、网络局部展开 | A/B/C/D是原图内容，不固定新图分区 |
| M6 | [模板图8](references/mechanism/template-fig-8.png) | 真实场景、存储、特征、策略和执行闭环 | 图标只在相同研究对象时使用 |
| M7 | [模板图9](references/mechanism/template-fig-9.png) | 数据融合、共享输入、策略到执行对象 | **源文本异常，仅参考形状和连接，禁止模仿缺字** |

原始矢量：[开放集1 EMF](original-vectors/open-set-1.emf)、[2 EMF](original-vectors/open-set-2.emf)、[3 EMF](original-vectors/open-set-3.emf)。它们是PPT内提取的整幅EMF，不是已分解原生组件；需要可编辑片段时另行转换并检查。

## 总体框架图素材

| ID | 真实参考 | 适用表达 | 限制 |
|---|---|---|---|
| F1 | [课题二技术路线图](references/framework/topic-two.png) | 跨框编号标题、分级文字、宽关系箭头，模块内有具体机制 | 默认视觉体系；不复制一大两小布局、三模块数量或双向关系 |
| F2 | [模板图2](references/framework/template-fig-2.png) | 研究块包含简化机制、不同任务块及共同平台 | 拓扑组织参考；细小图内文字和密度不可照搬 |
| F3 | 用户聊天截图（本包无原始附件文件） | 蓝色粗体编号/标题、黑色圆角边框、虚线分组和关系箭头 | **仅样式参考，禁止照搬纯文字框内容架构**；不能伪称已存原图 |

F1的原生字体与主题解析信息见[框架模板](../references/templates/framework.md)。最终默认小标题藏蓝#0E2841来自用户最终确认版，不被原F1中的其他蓝色覆盖。

## 局部表达库（真实裁图）

- [特征编码器](details/encoder.png)：层结构与张量输出。
- [聚类双视图](details/clusters.png)：类簇、样本、关系线。
- [并行对比分支](details/contrast-branches.png)：两类操作对照、虚线容器、矩阵选区。
- [分布对齐](details/distribution-alignment.png)：两分布及相互作用箭头。
- [编号标题与摘要带](details/title-style.png)：标题跨接边框及编号斜切。
- [前向/返回箭头](details/relation-arrows.png)：关系文字与方向、颜色分级。
- [内部文字与对象层级](details/internal-hierarchy.png)：强调文字、辅助标签、具体场景与流程。

裁图保留原始标签与水印作为来源证据；新图不复制无关内容或水印。素材为用户提供的私人参考，不暗示公开再分发授权。来源文件、页码、图号、哈希和裁剪坐标见[清单](reference-manifest.json)。完整申请书未打包。

## 可编辑样式组件（依据参考重绘）

[编号标题栏](components/numbered-title.svg)、[前向宽箭头](components/forward-relation.svg)、[反馈连接](components/feedback.svg)、[公共支撑](components/shared-support.svg)是依据已确认样式制作的矢量组件，**不是从原文件原样提取**。

复制组件时保留内部g和所需defs，不把整张白色背景盖住模块。合并SVG时为渐变ID加唯一前缀并同步引用。标题编号、斜切、背景、文字一组移动；关系标签与箭头间留至少半字；字体不水平压缩，长词先扩框或合理换行。实际印刷字号另行校准。

旧自制样例在[测试目录](../evals/fixtures/examples/)，仅用于格式与渲染回归，不作为视觉设计的主要依据。
