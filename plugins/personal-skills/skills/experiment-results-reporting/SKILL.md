---
name: experiment-results-reporting
description: Organize RPent or LIBERO evaluation runs into reproducible Chinese Excel reports with validation-set, results, and optional baseline comparison tables, using fixed three-line-table formatting, evidence-based failure attribution, and explicit metric rules. Use when adding a validation set, summarizing a new run, comparing evaluation outputs, or revising these reports; do not use for running evaluations or changing benchmark code.
metadata:
  short-description: Reproducible evaluation tables and metric rules
---

# 实验结果汇总

将已有的评测清单、运行配置和结果产物整理成可复现的中文 Excel 报告。默认交付 `.xlsx`，不能仅在聊天中输出表格。只读取用户指定的产物；不要因汇总请求补跑、重试、修复数据集或修改评测代码。

开始前确认统计范围：验证集名称、run/output 目录、模型与版本、是否包含重试，以及目标全集的定义。若结果来自多个 run，逐条记录来源并避免重复计数。底层计算保留缺失为 null，Excel 显示单个反斜杠 `\`；真实零值正常显示，不把缺失当作零。

## Excel 交付与呈现

生成或修改报告前，必须读取 [报告字段与 Excel 格式规范](references/report-schema.md)，按其中固定的字体、行高、列宽、数字格式、边框及合并规则生成。规范自包含，**新建报告不依赖用户历史 Excel，也不要求用户提供模板**。用户明确要求修改已有文件时，读取最新文件并保留与本次修改无关的手工调整；用户本次明确要求优先于默认规范。

1. **表1 验证集组成与设置**：数据集、原始任务 ID、rollout 数、seed、任务目标。
2. **表2 实验结果汇总**：任务级结果与消耗，保留数据集合计和 Overall。
3. **表3 baseline与ours对比**：仅在有比较需求时增加；同一任务的 `baseline`、`ours` 分别占行，baseline 在前。同一任务 ID 跨两行合并，方法名不附括号说明。

各数据集默认均按原始任务 ID 展示，例如 `10_swap_t0_s0`，不重复拼接 `libero` 前缀，不增加冗余 suite 列。粒度必须对应真实数据：将 suite 汇总改成任务级时重新从任务结果计算，不能只改行名。不同数据集或 run 分组展示，不能静默合并；比较时保持相同统计口径。

数据集独立一列并纵向合并。全表使用白底黑字、宋体 11 磅、水平和垂直居中；采用三线表，同时在数据集边界保留细横分隔线，不加竖线。表头使用“平均 rollout 时间（秒）”等直白名称，不写“墙钟时间”。

不新增长篇表注、说明页或额外说明文件。来源、运行设置、有效分母、缺失、费用估算和影响比较的口径差异，在聊天中简短说明；不能为简洁而隐瞒实质限制或把不同计时字段改成同名后直接比较。用户要求外推时可增加“完整全集外推”行，假设在聊天中交代。

交付前检查 Excel 的值、格式、合并和文本显示；最终回复简短说明范围及关键限制，直接用纯文本或代码块给出文件绝对路径，不使用 Markdown 文件链接，也不在聊天中重复整份表格。

## 先归因，再统计

先串联 episode → attempt/thread → request/response 的时间线，核对模型错误、工具返回、finish/finalizer、预算记录与累计 usage。顶层 `timeout`、进程退出码或缺少终结 usage 不能单独决定失败原因和统计范围。

- **服务端/网络失败**：有证据的断网、代理错误、服务容量不足等失败请求不计入方法 token 与费用。若同一任务随后有完整的有效响应/成功尝试，取该有效部分计算，前面的服务失败不使该任务失去统计资格。记录排除的请求/尝试及原因。
- **harness/模型能力失败**：最大模型请求次数、工具决策次数或环境步数耗尽，以及有效执行中的规划、代码、控制失败，均如实计为任务失败；失败前的有效 usage 与费用全部纳入。API 连接重试上限与任务决策上限是两种预算，必须区分。
- **混合原因**：任务已用尽决策预算并报告失败，随后服务断开或外层超时，仍保留该任务失败及此前有效执行用量。只有服务故障、尚无可判定结果的任务单列为基础设施中断；wall-clock 超时或 watchdog 触发必须沿时间线确认是服务等待还是有效执行耗尽，不能直接归因。
- **请求成功不等于任务成功**：有效响应包括导致任务失败的响应；多轮任务要累计全部有效响应，不能只取最终一次响应或只挑成功任务。独立完整重跑是否替换旧 episode，仍按已确认的 run 合并规则；不得借此删除有有效执行的能力失败。
- **取消笼统的 partial 判定**：不得因某次服务失败无 usage、缺少 turn.completed 或请求数不一致，将整个任务标为 partial 并剔除均值。先恢复 session 最新累计值与逐请求 usage，核对其覆盖的有效执行范围。仅失败请求缺 usage 时不预留“未知费用”或宣称总量是下界。确实缺少有效响应的 usage 时，写明具体请求、缺失字段和证据，保留已有用量及任务结果；不能把缺失编成零，也不能无说明地改变分母。

## 统计口径

- 结果状态分开记录：任务成功、任务失败、启动失败/未知、超时、未运行。成功率分母必须标明；不要把“有效样本成功率”写成完整验证集成功率。
- token 使用选定有效请求对应的 Codex thread/tokenUsage/updated 或 session thread_token_usage / total_token_usage 的最新去重累计值。累计值已覆盖的请求不能再相加；跨线程按 thread ID、跨响应按 response ID 去重。若累计值混有明确服务失败的已记录用量，按对应请求证据排除，不能为“对齐”请求数或终结记录任意扣减。总 token 为 input + output；缓存输入和 reasoning output 已包含在这两个字段中，不重复相加。默认以带千位分隔符的原始整数展示总 token，不缩写为 M；平均 token 的格式见引用规范。
- token 和费用采用相同的有效请求范围，任务均值包含成功与 harness/模型能力失败。分母按有可统计有效用量的任务计算，不按有没有历史服务失败计算；若有效响应用量确实缺失，分别披露已记录量、缺失原因和对应指标分母。不要用“完整 usage n”制造未经归因的筛选。
- rollout 时间是有效执行区间的 wall-clock；环境时间是同一区间内环境服务 handler 的活动区间；扣除后时间为 rollout - simulator。初始场景准备、服务启动、结果持久化和导出不计入 rollout。若计时不可取得或差值为负，写 null 并记录原因。用量归因不自动改变完整 rollout 时间：wall-clock 中的服务等待如需扣除，必须有可定位的时间区间并另标“扣除服务等待后的时间”，不得按失败次数估算扣时。
- 官方费用必须注明模型、价格版本/日期、计费档位和输入缓存处理。标准档位的通用公式为：(uncached_input / 1e6) × input_price + (cached_input / 1e6) × cached_price + (output / 1e6) × output_price。若单请求超过模型价格页规定的长上下文阈值、使用 Batch/Flex/Fast、代理重试或自定义 API，应单独说明；API 等价费用不是实际账单。
- 估算优先按 suite 分层：对每个 suite 用有效样本均值乘以目标全集中该 suite 的条目数，再求和。样本不足、任务选择有偏或数据版本不一致时必须标为粗略预算，不得给出虚假的置信区间。可同时给出整体均值外推作为敏感性参考，但不能替代分层估算。
- 报告实际有效条数、缺失条数、是否包含失败和超预算条目、是否包含重试。历史 run、失败重试和修复后的新 run 默认不合并，除非用户明确要求并提供合并规则。

## 复现信息

记录清单版本/哈希、代码版本与工作区状态、run manifest、模型/effort、策略与 memory 标识、依赖或数据版本、统计时间范围。不要输出 API key 或整份环境变量。需要字段定义、CSV/JSON 映射和归因示例时，读取 [references/report-schema.md](references/report-schema.md)。
