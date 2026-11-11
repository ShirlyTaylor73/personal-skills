# 报告字段与计算参考

## 表 1：验证集组成

建议列：

| suite | task ID | rollouts | seed | 任务类型/实际目标 | swap/扰动 | 选择理由 |
|---|---:|---:|---:|---|---|---|

共同设置至少包含：

- planner、model、reasoning effort
- max model responses / turns
- planner timeout、max episode steps、watchdog、cleanup
- policy、memory、代码版本、硬件和 headless/EGL 设置

任务清单中的指令应来自实际 manifest 或 benchmark API。不要根据任务名臆测目标。

## 表 2：结果

建议列：

| 范围 | success/failure/unknown/not-run | valid n | total tokens (M) | avg tokens (M) | avg rollout wall (s) | avg simulator (s) | avg rollout excluding sim (s) | official equivalent cost (USD) |
|---|---|---:|---:|---:|---:|---:|---:|---:|

可在表后补充 raw integer totals、median、用量来源、失败归因、计时来源。表中平均值的分母必须是对应列的有效样本数，不一定等于结果条数。

## 结果分类

- success：环境 finalizer/solved 状态明确成功。
- failure：任务未完成，包括 harness 决策/步数预算耗尽及规划、代码、控制失败；保留有效用量。
- infrastructure_interrupted：服务或网络故障使任务无法继续，尚无可判定结果。
- unknown：核对工具、预算和原始轨迹后仍无法判断任务结果，写明缺少的证据；缺少 finalizer 本身不构成未知。
- not-run：因续跑、预算或调度未执行。

未知和未运行不能计入成功率分子或分母；除非另有定义，不把失败从成功率分母排除。

## Token 与费用

按 SKILL.md 的归因规则选择有效请求，使用其最新去重累计 usage。任务结果和用量来源分开记录：

- input_tokens
- cached_input_tokens
- output_tokens
- reasoning_output_tokens（若有；不再次加入 output）
- total_tokens = input_tokens + output_tokens
- included_attempt_ids / included_response_ids：纳入的尝试或响应；可用独立映射文件存储
- excluded_requests：请求/尝试 ID、服务失败原因、日志来源和已知被排除用量
- termination_cause / evidence：任务结束原因及预算、工具或 finalizer 证据
- usage_source / coverage：累计记录来源、覆盖哪些有效响应
- missing_valid_usage：确实缺失的有效响应 ID、字段、原因；没有则为空
- token_n / timing_n：各指标的任务分母及其选择原因

不用 `complete | partial` 标记代替因果判断。累计值覆盖全部已选有效响应时即可统计，不要求一定存在终结 usage 事件。

## 归因示例

| 原始证据 | 结果与用量处理 |
|---|---|
| 前两次连接/容量失败无 usage，第三次完整尝试成功且有 usage | 任务成功；第三次尝试全部有效 usage 纳入总量与均值，前两次排除；有效任务数为 1 |
| 有效交互后用完 40 次工具决策，finish(failure)，随后外层 timeout | 任务失败且计入分母；恢复全部有效响应的累计 usage，不因外层 timeout 或缺少 turn.completed 剔除 |
| API 重连到上限，未产生有效响应 | 服务失败，单列基础设施中断；没有 usage 不填零，不归为能力失败 |
| 模型给出错误代码、反复调整但最终预算耗尽 | 有效模型响应仍计入用量与费用，任务失败计入分母 |
| 只有累计记录但不能确认是否覆盖某个有效响应 | 指明该响应及缺失证据，保留已记录用量与任务结果；不凭猜测补齐，也不用 partial 自动剔除整条 |

替换已授权补跑的服务中断 episode 时，新旧来源分别记录；同一 episode 不重复计数。任务内有效多轮响应应累计，不能只保留最后一次响应。

费用计算前保存官方价格页 URL、读取日期和模型版本。长上下文加价必须按请求逐条判断，不能只按平均输入长度判断。

## 外推

设 suite 为 s，目标全集条数为 N_s，有效样本平均 token 为 mean_tokens_s，则：

estimated_total_tokens = Σ_s N_s × mean_tokens_s

费用同理。若某 suite 没有有效样本，整体估算应为 null 或明确列出未覆盖 suite；禁止用零填充。外推行的成功率、真实任务结果和完整性写“未评测”。

## 复现清单

汇总前检查：

1. 输出目录和 run manifest 是否对应同一 run。
2. 清单哈希、代码版本、模型、policy、memory 是否记录。
3. 任务数是否等于预期，task ID 和 seed 是否唯一。
4. 每条结果是否能区分成功、失败、未知、未运行。
5. token/timing 的有效样本数是否分别计算。
6. 服务请求重试与任务决策预算是否区分；每次排除是否有原因、ID 和证据；能力失败的有效用量是否保留。
7. 外推目标（例如 8 suites × 10 tasks × 10 seeds）是否明确。
