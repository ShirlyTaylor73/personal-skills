# 字段映射、时钟桥接与缺失处理规范

本参考记录 baseline（Codex / OpenAI `cells` / `program`）与 REAgent harness（OpenAI `graph`）以及三个仿真环境（LIBERO / RoboCasa / RoboDojo）的产物格式、统一事件映射和缺失处理规则。

## 1. 输入目录形态与文件来源

### 1.1 REAgent Harness 批量目录（例如 `runs/graph-validation-02`）

```text
<run_root>/
├── batch.json                      # 批量清单：仅保留每个任务最终采纳的 attempt
├── summary.json                    # 官方汇总：overall + by_set (libero/robocasa/robodojo)
└── <robot>/<episode_id>/attempt-0N/
    ├── episode.json                # 单任务元数据（suite, task_id, seed, instruction）
    ├── run.json                    # 外层运行器元数据（run_id, attempt, settings, source_commit, process_wall_time_s, timing）
    └── policy/<policy_subdir>/
        ├── result.json             # 权威 episode 结果（status, environment_success, timing, generation, graph）
        ├── openai_events.jsonl     # OpenAI HTTP 请求、assistant、tool 调度事件（相对 t 秒）
        ├── lifecycle.jsonl         # 收尾里程碑（graph_drain / wrap_up / messages_write / resources_close / result_write）
        ├── calls.jsonl             # 机器人后端原语调用（started_at epoch 秒 + elapsed_s + stateful）
        ├── tool_turns.json         # 工具轮次摘要
        └── workspace/execution/<job_id>/events.jsonl  # Graph job/unit/action/decision/pause/patch/cancel 事件
```

### 1.2 Baseline 目录（例如 `PyRUA-Lean/runs/*`）

常见两种形态：
1. **平铺 Codex baseline**（如 `libero-validation`, `libero-validation-01`, `robocasa-validation-01`）：
   - `<run_root>/<episode_id>/` 下直接含 `result.json`、`codex_events.jsonl`、`calls.jsonl`、`tool_turns.json`（无 `run.json`、无 `openai_events.jsonl`、无 `lifecycle.jsonl`，旧 run 通常无 `result.json.timing`）。
   - Codex session JSONL（`<episode>/model_sessions/rollout-*.jsonl`，每个规划 attempt 一个文件；也可用 `--codex-session` 显式指定或放在 episode 根目录）：带毫秒 ISO 时间戳，是还原 Baseline 逐轮推理的依据，见 3.6。
2. **嵌套 OpenAI cells baseline**（如 `robodojo-validation-02`）：
   - `<run_root>/<episode_id>/attempt-01/policy/<policy_subdir>/` 下含 `result.json`、`openai_events.jsonl`、`calls.jsonl`、`tool_turns.json`，`arm="cells"`, `runtime="openai"`。

## 2. 统一事件表 Schema (`events.jsonl`)

每行一个 JSON 对象，必填字段如下：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `event_id` | string | episode 内唯一稳定 ID（如 `ev_0001`） |
| `run_id` | string | `run.json.run_id` 或运行根目录名 |
| `episode_id` | string | 原始任务 ID（如 `spatial_task_t0_s0`） |
| `suite` | string | 数据集/机器人类型（`libero` / `robocasa` / `robodojo`） |
| `attempt` | int | 尝试序号（从 `run.json.attempt` 或目录名 `attempt-NN` 提取，默认 `1`） |
| `process` | string | 逻辑泳道进程：`policy_runtime`, `provider_request`, `graph_manager`, `graph_worker`, `robot_backend`, `environment_service`, `viztracer_uncalibrated` |
| `thread` | string | 子泳道名称（如 `main`, `http`, `tool_dispatch`, `job:<id8>`, `stateful`, `readonly`, `env_handlers`, `lifecycle`） |
| `event_type` | string | 标准化事件类型（见第 3 节） |
| `start_ns` | int \| null | 相对 episode 锚点的开始时间（纳秒）；无时间戳事件为 `null` |
| `end_ns` | int \| null | 相对 episode 锚点的结束时间（纳秒，满足 `end_ns >= start_ns`） |
| `parent_id` | string \| null | 父事件 `event_id`（例如 `tool_dispatch -> model_request`，`graph_unit -> graph_job`） |
| `request_id` | int \| null | OpenAI `request_id` |
| `job_id` | string \| null | Graph `job_id` |
| `unit_id` | string \| null | Graph `unit_id` |
| `instance_id` | int \| null | Graph `instance_id` |
| `status` | string | `ok` / `failed` / `cancelled` / `retry` / `paused` / `completed` / `error` / `unknown` |
| `clock_domain` | string | 时钟对齐域（见第 4 节） |
| `source_path` | string | 原始日志文件路径 |
| `args` | object | 附加属性（`task`, `model`, `reasoning_effort`, `status_code`, `tokens`, `images`, `env_steps`, `error`, `event_seq` 等） |

## 3. 各来源事件映射

### 3.1 `openai_events.jsonl` -> `provider_request` & `policy_runtime`

- `request_started` + 对应 `request`（同 `request_id`）：
  - `start_s = max(0, req_end_t - latency_s)`（或配对 `request_started.t`），`end_s = req_end_t`。
  - `event_type`: `ok=true` 且 `attempt==1` -> `model_request`；`ok=true` 且 `attempt>1` -> `model_request_retry`；`ok=false` -> `model_request_failed`。
  - `args` 保留 `status_code`, `attempt`, `messages`, `latency_s`, `prompt_tokens`, `completion_tokens`, `cached_tokens`, `reasoning_tokens`, `usage_present`, `error`。
- `request_started` + `request_cancelled`：
  - `event_type = "model_request_cancelled"`，`status = "cancelled"`，`args.reason` 保留（如 `episode_end`, `budget_timeout`）。
- 只有 `request_started` 没有结束事件（进程异常中断）：
  - 记为 `model_request_incomplete`，`status = "unknown"`，并记录到 `missing_data`。
- `assistant`：瞬时点事件 `assistant_reply`（`start_ns == end_ns`），记录 `finish_reason`, `tool_calls`, `text_chars`, `reasoning_chars`。
- `tool`：`start_s = max(0, t - elapsed_s)`, `end_s = t`，`event_type = "tool_dispatch"`，关联最近的已完成 `model_request` 为 `parent_id`。

### 3.2 Graph `workspace/execution/<job_id>/events.jsonl` -> `graph_manager` & `graph_worker`

- `started` 到 `completed`/`cancelled`/末事件：`graph_job` 区间（`graph_manager`）。
- `unit_started` 到对应的 `unit_completed`（或 `error` / `cancelled`）：`graph_unit` 区间（`graph_worker`）。
- `action_completed`：`start_s = timestamp - elapsed_s`, `end_s = timestamp`，`event_type = "graph_action"`（`graph_worker`），保留 `unit_id`, `instance_id`, `env_steps`, `primitive`。
- `waiting_decision`（或 `decision_requested`）到对应的 `decision_resolved` / `decision_invalidated` / `cancelled`：`graph_decision_wait` 区间（`graph_manager`）。
- `pause_requested` 到 `resumed` / `cancelled`：`graph_pause` 区间（同时保留 `pause_requested`、`resumed`、`graph_patched`、`decision_invalidated`、`cancelled`、`error` 瞬时标记以便在 Perfetto 中定位控制动作）。

### 3.3 `calls.jsonl` -> `robot_backend`

- 每条记录有 `started_at`（Unix epoch 秒）和 `elapsed_s`、`stateful`（bool）、`tool`、`env_steps`、`ok`、`error`。
- `stateful=true` -> `event_type = "robot_call_stateful"`, `thread = "stateful"`；
- `stateful=false` -> `event_type = "robot_call_readonly"`, `thread = "readonly"`。
- 当与 `graph_action` 区间高度重合且原语名一致时，建立从 `graph_action` 到 `robot_call_stateful` 的 flow 关联。

### 3.4 `lifecycle.jsonl` -> `policy_runtime` (`thread = "lifecycle"`)

- 成对里程碑 `*_started` / `*_finished` 合并为区间事件 `runtime_lifecycle`：
  - `graph_drain_started` .. `graph_drain_finished` -> `lifecycle:graph_drain`
  - `wrap_up_started` .. `wrap_up_finished` -> `lifecycle:wrap_up`
  - `messages_write_started` .. `messages_write_finished` -> `lifecycle:messages_write`
  - `resources_close_started` .. `resources_close_finished` -> `lifecycle:resources_close`
  - `result_write_started` .. `result_write_finished` -> `lifecycle:result_write`

### 3.5 `result.json.timing` -> `environment_service`

- `timing.intervals` 给出 rollout 分段 `wall_ns` 与服务端累计 `sim_ns`（来自 `rpent_env_handlers` 或 `robodojo_client_handlers`）。
- 因为环境服务端只导出累计 `elapsed_ns` 而不提供每次 handler 的单独时间戳，在 `environment_service` 泳道中将其记为 `env_timing_interval`（区间跨度为分段 `wall_ns`，`args` 明确写 `sim_ns`、`timing_source`、`server_id`、`is_aggregate=true`），**不把累计 `sim_ns` 伪造成具体时刻的小切片**。

### 3.6a Baseline Codex session（`model_sessions/rollout-*.jsonl`）-> 逐轮推理与工具执行

- 发现：`<episode>/model_sessions/`、episode 根目录下的 `rollout-*.jsonl` / `session*.jsonl`；若 `result.json.generation.thread_ids` 非空，只保留文件名含这些 thread id 的 session（避免混入其他运行）；多个文件按首条时间戳排序，视为同一 episode 的多次规划 attempt。
- 时间原点：第一个 session 的 `task_started` 作为 `t=0`（`clock_domain = codex_session_aligned`，`bridge_method = codex_session_task_started_anchor`），`calls.jsonl` 的 `started_at` 与 session 时间戳同为 Unix epoch，直接换算。`metrics.json.codex_session.anchor_check_s` 记录"首条机器人调用 − 首个 function_call"，超过 5 秒会写入 `missing_data: codex_session_anchor_drift_over_5s`。
- 轮次定义：第 k 轮 = 上一个 `function_call_output`（或 `task_started`）到下一个 `function_call` 的区间，即选出该调用的那次模型推理；最后一个输出到 `task_complete` 之间是最终回复轮（无工具）。工具执行 = `function_call` -> 对应 `function_call_output`（按 `call_id` 配对）；`python` 记为 `pipeline:baseline_cell_exec`（带 `calls`、`stateful_tools` 统计），其余记为 `pipeline:baseline_tool_exec`。
- 失败 attempt：`task_complete.error` 非空记为 `pipeline:baseline_attempt_error`，与下一个 session 之间的空档记为 `pipeline:baseline_backoff`。
- 超时：最后一个 session 没有 `task_complete` 且尾部有未完成的推理，则该轮延长到 `policy_wall_s`，标 `cut_by_timeout`；正常结束但 `policy_wall_s` 大于 session 末尾 1 秒以上的部分记 `pipeline:baseline_unattributed_tail`（斜线，推断）。
- 没有 session 时退化为 `calls.jsonl` 间隔推断（`pipeline:baseline_llm_gap` / `baseline_unattributed_tail`，斜线填充，并标 inferred），此时无法给出 `R#`。

### 3.6 Baseline `codex_events.jsonl` -> `policy_runtime` (`codex_uncalibrated`)

- `codex_events.jsonl` 记录 `thread.started`, `turn.started`, `item.started`, `item.completed`, `turn.completed`, `error` 等，但 **原生不含时间戳**。
- 处理规则：
  - `mcp_tool_call`（如 `python` / `finish`）按序与 `tool_turns.json` 和 `calls.jsonl` 里的真实 `started_at`/`elapsed_s` 关联；
  - 若存在 `calls.jsonl`，将 `calls.jsonl` 的所有调用放在 `robot_backend` 泳道；没有 session 时时钟域标为 `calls_epoch_relative`（以首条调用为 0，初始思考不在轴上，明确说明缺少 rollout 精确锚点）；有 session 时见下；
  - 没有时间戳的 `codex_events.jsonl` 条目不伪造绝对时间，只记录序次事件与 `turn.completed.usage` 统计，并写入 `missing_data`：`codex_events_no_per_request_timestamps`。

## 4. 时钟桥接优先级

将 Unix epoch 时间戳（`calls.jsonl`, Graph `events.jsonl`, `lifecycle.jsonl`）换算为与 `openai_events.jsonl` 同一原点 `t=0`（即 `epoch_t0`）时，严格按以下优先级：

1. `lifecycle_messages_write_anchor`（最精确，误差通常 < 5ms）：
   - 当 `lifecycle.jsonl` 含 `messages_write_finished` 且 `result.json.generation.elapsed_s` 可用时：
   - `epoch_t0 = ts(messages_write_finished) - generation.elapsed_s`
2. `lifecycle_first_to_openai_last_anchor`：
   - 当 `lifecycle.jsonl` 非空且 `openai_events.jsonl` 非空时：
   - `epoch_t0 = ts(lifecycle[0]) - openai_events[-1].t`
3. `run_startup_anchor`（粗略锚点，标注提醒）：
   - 当 `run.json.started_at` 与 `result.json.startup_s` 可用且存在 `openai_events.jsonl` 时：
   - `epoch_t0 = run.started_at + startup_s`
4. `codex_session_task_started_anchor`（Codex baseline 且找到 `model_sessions`）：`epoch_t0 = 第一个 session 的 task_started`，初始思考、失败重试、最终回复全部在时间轴上。
5. `calls_relative_only`（无桥接，如无 `openai_events.jsonl`、`lifecycle.jsonl` 也无 session 的 Codex baseline）：
   - `calls.jsonl` 相对 `calls[0].started_at` 展示，标为 `calls_epoch_relative`；不强行与 `policy_wall_s` 对齐。

## 5. 三个环境的已知差异

| 维度 | LIBERO (`rpent_libero`) | RoboCasa (`rpent_robocasa`) | RoboDojo (`rpent_robodojo`) |
| --- | --- | --- | --- |
| `timing.source` | `rpent_env_handlers` | `rpent_env_handlers` | `robodojo_client_handlers` |
| `policy` 子目录名 | `<episode_id>` | `<episode_id>` | `<task>_l0_s0-<unix_ts>` |
| 典型原语 | `move_to`, `pi0_pick`, `set_gripper`, `release`, `back_project`, `segment` | `move_to`, `grasp`, `navigate_to`, `open_door` 等 | `move_to`, `pick`, `place`, `push` 等 |
| `simulator_wall_time_s` 占比 | 通常较低（数秒~数十秒） | 显著更高（物理渲染较重，常达百秒级） | 中等偏高（数十秒~百秒级） |
| 旧 baseline `timing` 字段 | 部分旧 run 缺失（记 `null`） | 部分旧 run 缺失（记 `null`） | 部分旧 run 缺失（记 `null`） |
