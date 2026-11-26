# Perfetto 泳道规范与 Trace Processor SQL

## 1. Perfetto Trace Event JSON 泳道布局（与 HTML 四轨道对齐）

生成的 `traces/*.perfetto.json`（以及 `--compare` 时的 `traces/compare/*.perfetto.json`）采用标准 Chrome Trace Event Format，可直接拖入 [ui.perfetto.dev](https://ui.perfetto.dev/) 或由 Perfetto `trace_processor_shell` 加载。

固定进程泳道（`process_sort_index` 从上到下，与 `pipeline_timeline.html` 保持一致）：

| `pid` | 进程名 (`process_name`) | 主要子泳道 (`thread_name`) | 用途与切片命名（Ours vs Baseline 统一） |
| --- | --- | --- | --- |
| 1 | `Agent Inference` | `agent_inference`, `agent_backoff`, `agent_incomplete`, `agent_inferred`, `codex_session` | 模型推理时间：Ours 每次 HTTP 请求一个切片 `R#→<tool>` / `R# retry` / `R# err <code>` / `backoff`；Codex Baseline 有 session 时展示同形的 `R#→<tool>`（`att# err`、`backoff`、末轮超时截断标 `(cut by timeout)`），无 session 时退化为 `infer (inferred)` / `tail (inferred)` |
| 2 | `Tool Execution` | `tool_dispatch`, `tool_cell`, `lifecycle` | 工具执行区间：`tool_dispatch` 为工具分发到返回的真实区间（切片名即工具名，如 `python_start`、`wait_event`，多为近零时长）；Baseline 的 python cell 在 `tool_cell` 展示 `Cell #1..N`，其余工具（如 `finish`）进 `tool_dispatch`；收尾为 `lifecycle:*` |
| 3 | `Policy Job` | `jobs`, `control` | 异步策略作业生命周期：`job:<id6>`、`wait_decision`、`paused`、`patch:rev#`、`pause_requested`、`cancelled`（同步 Baseline 无异步作业时不生成切片） |
| 4 | `Policy / Robot` | `policy_units`, `robot_actions`, `robot_readonly` | 策略单元与机器人后端：Graph 展示 `unit:<id>`、`action:<prim>`、`error:<unit>` 及底层 `robot_actions`（stateful）/ `robot_readonly`（只读查询）；Baseline 同样在 `robot_actions` / `robot_readonly` 中展示同名原语 |
| 5 | `Environment Service` | `env_timing_intervals` | 服务端 handler 累计 timing 区间（聚合区间，标注 `is_aggregate=true`） |
| 6 | `VizTracer (Uncalibrated)` / `VizTracer (Calibrated)` | 原始 VizTracer 进程/线程 | 仅在 `--viztracer` 启用时出现；未校准时不平移 |

因果流事件（Flow Events，`ph: "s"` -> `ph: "f"`）：
- `Agent Inference (agent_inference) -> Tool Execution (tool_dispatch)`：连接模型请求与它触发的本地工具执行。
- `Tool Execution (tool_dispatch) -> Policy Job (jobs)`：连接 `python_start` 工具分发与后台异步 Policy Job。
- `Policy / Robot (policy_units) -> Policy / Robot (robot_actions)`：连接 Graph 动作完成事件与底层机器人状态调用。

## 2. 最小 Trace Processor SQL 查询集

完整可执行 SQL 已保存在 [scripts/queries.sql](../scripts/queries.sql)。在 Perfetto UI 左侧 **Query (SQL)** 面板或 CLI 中运行：

```bash
trace_processor_shell -q ~/.codex/skills/rollout-timeline-analysis/scripts/queries.sql <episode>.perfetto.json
```

核心查询说明：

1. **泳道汇总**：按进程与线程统计切片数、总时长（秒）与最大单次耗时。
2. **Agent HTTP 请求与失败/重试筛选**：筛选 `Agent / agent_inference` 中所有 `status != 'ok'`、`attempt > 1` 或 `usage_present = 0` 的切片。
3. **区间并集（Critical Path）**：使用窗口函数（running max `end_ts` + 合并重叠段）计算 `Agent / agent_inference` 的真实并集总时长，避免将并发重叠区间直接求和，与 `metrics.json` 中的 `http_critical_path_s` 逐项一致。
4. **Agent HTTP 与 Policy / Robot 动作重叠时长**：先对 `Agent / agent_inference` 与 `Policy / Robot / robot_actions` 各自求并集，再对交集区间 `max(a.start, b.start) < min(a.end, b.end)` 求和，得到被并行隐藏掉的动作耗时（与 `http_robot_overlap_s` 一致）。
5. **Policy Job 控制与收尾诊断**：筛选 `Policy Job / control`（`wait_decision`、`paused`、`patch`、`cancelled`）、`Policy / Robot` 错误切片与 `Tool Call / lifecycle:graph_drain` 切片。

## 3. 无 `trace_processor_shell` 环境时的对账

当本机未安装 `trace_processor_shell` 或 Python `perfetto` 包时，`scripts/analyze_rollout.py` 内置与上述 SQL 完全等价的区间并集与交集计算，输出到 `metrics.json` 和 `report.md`。只要将生成的 `*.perfetto.json` 打开于 Perfetto UI 并运行 `scripts/queries.sql`，各项并集和重叠指标即可逐项对账。
