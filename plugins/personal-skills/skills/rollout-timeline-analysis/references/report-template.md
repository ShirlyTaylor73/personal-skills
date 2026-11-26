# Rollout 时序分析报告模板与归因规则

报告以中文 Markdown 输出（`report.md`），同时保留机器可读的 `metrics.json` 与 `events.jsonl`。

## 1. 必须包含的章节

1. **运行元信息与复现背景**
   - 输入目录、run ID、代码提交（`source_commit` 及 dirty 标志）、arm、runtime、模型、`reasoning_effort`、最大轮次、超时预算、`images`/`feedback` 配置、attempt 选取策略（`latest` vs `all` 及排除的旧 attempt 列表）。
2. **整体与按 Suite 汇总表**
   - 列项：`Suite`、`Episodes`、`Success`、`Failure`、`Timeout`、`InfraError`、`Unknown`、`Rollout 总/均值 (s)`、`Simulator 总/均值 (s)`、`排除仿真总/均值 (s)`、`Agent Inference (s)`、`Tool Execution (s)`、`Agent 轮数(其中 wait_event)`、`HTTP 累计 (s)`、`HTTP 关键路径 (s)`、`Robot 动作并集 (s)`、`HTTP∩动作重叠 (s)`、`请求数(失败/重试/取消)`、`Token(完整性)`。
   - **`Agent Inference` 与 `Tool Execution` 必须与 `pipeline_timeline.html` 的前两条轨道同一口径、同一份 `metrics.json` 字段**（`timings_s.agent_inference_s` / `tool_execution_s` / `wait_event_inference_s`，`counts.agent_rounds` / `wait_event_rounds`，`agent_inference_basis`），不得在报告里另算一套。
   - **缺失值一律显示 `N/A`（底层为 `null`），绝不填 `0`**。
   - 若输入含官方 `summary.json`，附加 **对账表（Reconciliation）**，逐项比对 `episodes`、`success`、`rollout_wall_time_s`、`simulator_wall_time_s`、`rollout_excluding_sim_s` 与 `known_usage`。
3. **三层独立结论（强制分层）**
   - **层 1：真实端到端体验**：基于完整 `rollout_wall_time_s`（不扣除 HTTP）与 `process_wall_time_s`（含启动与收尾），说明用户等待的真实耗时和成败分布。
   - **层 2：Agent 推理等待占比与稳定性**：基于 `agent_inference_s`（占 `rollout_wall_time_s`，缺失时占 `policy_wall_s`）、轮数、其中选择 `wait_event` 的纯轮询轮数与累计时间；并列出 HTTP 层面的 `http_critical_path_s`、单请求均值/P95、失败重试次数、取消请求数、`usage_status=partial` 覆盖度，单独分离模型服务波动影响。必须写明口径（`http_measured` / `codex_session_measured` / `calls_gap_inferred`）；`calls_gap_inferred` 只有推断间隔，Agent Inference 记 `N/A`，不拿推断值充数。
   - **层 3：Harness 本地调度、并行覆盖与环境执行效率**：基于 `simulator_wall_time_s`、`robot_action_union_s`、`http_robot_overlap_s`（以及并行覆盖率 `http_robot_overlap_s / robot_action_union_s`）、Graph 决策等待/暂停/修订/取消/drain 耗时、HTTP 之外暴露时间（`rollout_wall_time_s - http_critical_path_s`）和纯本地非 HTTP 非动作暴露开销（`rollout_wall_time_s - union(http, robot_action)`，避免并行仿真与 HTTP 被重复扣除）。
4. **单条 Episode 时间线明细**
   - 展示每条 episode 的核心时间拆分（含 `Agent Inference`、`Tool Execution`、轮数与其中 `wait_event` 轮数）、关键事件摘要（Graph job 数、pause/revise/cancel/decision wait 次数、HTTP 失败/重试/取消、usage 状态）及对应 Perfetto trace 文件路径。
5. **Baseline 与 Harness 对比（仅当提供 `--compare` 时）**
   - 首先输出 **配置差异审计表**：逐项比对 `arm`, `runtime`, `model`, `reasoning_effort`, `max_turns`, `budget_s`, `timing.source`。
   - 只要任一非实验自变量存在差异（例如 `codex` vs `openai` runtime、不同模型或不同预算），在对比表顶部插入醒目警告：
     > **系统级比较（System-Level Comparison）**：两侧存在 runtime / 模型 / 预算 / 计时口径差异，差异结果反映整套系统表现，不能直接归因于单一并行调度改动。
   - 只对两侧共同存在且同一任务 ID 的样本计算配对差异；若一侧缺失 `timing` 字段，仅在可比字段（如 `policy_wall_s`）上对照并标明口径。
   - 配对表必须同时给出两侧的 `Agent Inference`、`Tool Execution` 与轮数，并写出两侧时钟域与 Agent Inference 口径（Ours 为 HTTP 请求，Baseline 为 Codex session 逐轮，口径不同只作量级对照）；有 session 时说明失败 attempt 次数与锚点最大偏差。
6. **缺失数据与时钟对齐清单**
   - 明确列出缺失文件、缺失 `timing`、缺失 `usage`、无逐请求/逐轮时间戳（如找不到 `model_sessions` 的 Codex baseline）、多 attempt 排除记录及每条 episode 采用的时钟桥接方式；使用 Codex session 时附“逐轮还原”小节（条数、失败 attempt、锚点偏差）。

## 2. 禁止事项

- 禁止将 `rollout_wall_time_s - http_critical_path_s` 称为主 rollout 时间。
- 禁止把重叠动作区间或重叠 HTTP 区间直接求和作为关键路径。
- 禁止把 `usage_status=partial` 或失败任务排除出已记录 token/请求统计，也不得将缺失 token 填零。
- 禁止在无时钟桥接的情况下强行拼合跨进程绝对时间。
