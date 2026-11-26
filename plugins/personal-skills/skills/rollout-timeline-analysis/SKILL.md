---
name: rollout-timeline-analysis
description: Analyze existing baseline and REAgent harness robot rollout logs into unified cross-process event tables, aligned 4-track Perfetto Trace Event JSON timelines, interactive HTML pipeline timelines served on a local background HTTP URL, and critical-path reports covering rollout wall time, simulator time, HTTP latency, parallel action overlap, retries, and failure attribution. Use when inspecting rollout timing, parallelism overlap, critical path, model request latency, or environment cost across baseline and harness runs; do not use for running evaluations, modifying runtime or simulator code, or adding live instrumentation.
metadata:
  short-description: Aligned 4-track Perfetto & HTML timelines and critical-path analysis for rollout logs
---

# Rollout Timeline Analysis

离线解析已有的 baseline 与 REAgent harness 运行产物，生成统一跨进程事件表、上下对齐的四泳道 Perfetto Trace Event JSON 时间线、交互式 HTML 流水线时序图、关键路径统计与可复现中文分析报告。

本 skill 只读取已有产物并输出到独立分析目录，**不启动模拟器、不调用模型服务、不重跑评测、不修改 runtime/环境源码、不覆盖原始运行产物**。唯一允许启动的后台进程是在最后一步对 `<analysis_output_dir>` 启动本地只读 HTTP 预览服务。

## 统一四轨道对齐规范（HTML 与 Perfetto JSON 一致）

Ours（Graph / OpenAI）与 Baseline（Cells / Codex 或 OpenAI）在 `pipeline_timeline.html` 与 `*.perfetto.json` 中强制使用完全一致的四条核心轨道名称与顺序，确保双方法可直接逐行对照：

1. **`Agent Inference`**：只画模型推理，不叠 Policy。Ours 每个色块是一次真实 HTTP 请求 `R# · <秒>`，颜色表示该轮选择的工具（`python_start` 绿、`wait_event` 橙、patch/resolve/finish 紫），失败/重试/backoff 用红色系。Codex Baseline 在能找到 `model_sessions/rollout-*.jsonl` 时同样是逐轮 `R# · <秒>`（实测，非 HTTP 口径，副标题注明）；找不到 session 时才退化为 `calls.jsonl` 间隔推断，用斜线填充并在图例标注"inferred"。
2. **`Tool Execution`**：画工具分发到返回的真实区间。Ours 的 `python_start`/`wait_event`/`patch_graph`/`resolve_decision`/`finish` 多为近零时长，画成带名字的细竖线（名字写在竖线外，错层避让）；Baseline 的 python cell 是有长度的实心块 `Cell #N`，两边第三行都是收尾 `lifecycle:*`。机器人实际在做什么由 `Policy Job` / `Policy / Robot` 轨道负责。
   - `report.md`、`metrics.json` 与 HTML 标题栏共用同一份 `timings_s.agent_inference_s` / `tool_execution_s` / `wait_event_inference_s`、`counts.agent_rounds` / `wait_event_rounds`、`agent_inference_basis`，报告表格里的 Agent Inference / Tool Execution 数字必须能在时序图上对上，不得另算一套。
   - 两侧行名一致；口径差异只写在行名下的副标题里（例如 Ours 为 "model HTTP requests (measured)"，Baseline 为 "model rounds from Codex session (measured)" 或 "gap between cells (inferred)"）。
3. **`Policy Job`**：异步策略作业生命周期（Graph 为 `job:<id>`、`wait_decision`、`paused`、`patch`、`cancelled`；Baseline / 同步模式保留同位置轨道并注明 `Sync mode (no async policy job)`）。
4. **`Policy / Robot`**：策略执行与机器人后端（Graph 为 `unit:<name>` ↳ 动作原语 ↳ 只读查询；Baseline 为动作原语 ↳ 只读查询，同名同色）。

## 工作流

1. **发现输入与清单**：检查输入路径是单条 episode 目录还是批量 run 目录，先定位 `batch.json`、`summary.json`、`run.json`、`episode.json`、`result.json` 与代码提交/运行设置，再确定可用的日志来源（`openai_events.jsonl`、`lifecycle.jsonl`、`calls.jsonl`、`tool_turns.json`、Graph `workspace/execution/*/events.jsonl`、baseline `codex_events.jsonl`，以及 Codex baseline 的 `model_sessions/rollout-*.jsonl` 逐轮 session；`result.json.generation.thread_ids` 存在时只取匹配的 session）。若无任何可定位来源，输出缺失清单并停止，不猜测时间。
2. **解析与导出**：运行内置脚本 [scripts/analyze_rollout.py](scripts/analyze_rollout.py) 生成统一事件表（`events.jsonl`）、单条/对比/合并 Perfetto Trace（`traces/*.perfetto.json`、`traces/compare/*.perfetto.json`）、交互式四泳道时序图（`pipeline_timeline.html`）、结构化指标汇总（`metrics.json`）和 Markdown 报告（`report.md`）：

```bash
python ~/.codex/skills/rollout-timeline-analysis/scripts/analyze_rollout.py \
  <input_path> \
  --out <analysis_output_dir> \
  [--compare <baseline_or_other_input_path>] \
  [--attempt-policy latest|all] \
  [--combined-trace] \
  [--viztracer <viztracer_trace.json>]
```

3. **对账与验证**：若输入目录含 `summary.json` 或 `batch.json`，核对脚本文档中的 `rollout_wall_time_s`、`simulator_wall_time_s`、`rollout_excluding_sim_s`、成功率及 token 覆盖数是否一致；检查 `missing_data` 与 `clock_alignment` 说明。
4. **深度查询（按需）**：
   - 需要用 Perfetto UI 或 `trace_processor_shell` 做自定义 SQL 切片/关键路径/失败筛选时，读取 [references/perfetto-sql.md](references/perfetto-sql.md) 或直接执行 [scripts/queries.sql](scripts/queries.sql)。
   - 需要确认 Codex、OpenAI runtime、Graph、cells/program 与三环境（LIBERO / RoboCasa / RoboDojo）的字段差异、时钟桥接及缺失处理时，读取 [references/field-mapping.md](references/field-mapping.md)。
   - 需要定制报告结构或核对三种结论边界时，读取 [references/report-template.md](references/report-template.md)。
   - 仅在现有业务日志无法解释 Python 函数、线程或异步调度开销时，才启用 VizTracer 深度模式，读取 [references/viztracer-mode.md](references/viztracer-mode.md)。
5. **最后一步：启动本地后台服务并在聊天中提供可打开 URL**：
   - 分析并生成 `pipeline_timeline.html` 后，运行内置脚本 [scripts/serve_timeline.py](scripts/serve_timeline.py) 在本地后台进程托管 `<analysis_output_dir>`（自动挑选空闲端口、`start_new_session` 独立驻留、验证端口已监听后立即返回，不阻塞当前会话）：

```bash
python ~/.codex/skills/rollout-timeline-analysis/scripts/serve_timeline.py <analysis_output_dir>
```

   - **必须在最终回复中直接给出可点击打开的 URL**（例如 `http://127.0.0.1:8765/pipeline_timeline.html`），同时附上生成的文件路径与后台进程 PID / 停止命令（`python ~/.codex/skills/rollout-timeline-analysis/scripts/serve_timeline.py <analysis_output_dir> --stop`），让用户可以直接在浏览器中打开查看，无需手动启服务。

## 核心时间与归因口径

- **保留完整端到端时间**：主指标必须同时保留完整 `rollout_wall_time_s`、`simulator_wall_time_s`、`rollout_excluding_sim_s`、`http_cumulative_s`、`http_critical_path_s` 以及 `http_robot_overlap_s`。**绝不把 HTTP 网络等待从主 rollout 时间中静默扣除**。
- **重叠区间用并集计算**：关键路径（`http_critical_path_s`、`robot_action_union_s`、`graph_active_union_s`）和并发覆盖（`http_robot_overlap_s`、`http_graph_overlap_s`）一律按时间区间并集/交集计算，禁止把重叠区间直接求和。
- **严格区分时钟域**：同一 episode 统一用相对本地 monotonic/anchored 秒数（纳秒存储）；当不同进程或不同文件缺乏可靠时钟桥接（如 Codex `codex_events.jsonl` 无逐事件时间戳，或未校准 VizTracer）时，分别在独立泳道展示并明确标注 `clock_domain`，绝不伪造绝对对齐。
- **失败与缺失分开归因，缺失不填零**：
  - 将 `success`、有效能力 `failure`、`timeout`、`infra_error`（如 `planner_error`、`boot_error`）和 `unknown` 分开统计。
  - HTTP 失败、重试（`attempt > 1`）、取消（`request_cancelled`）与缺失 usage 单独列项。
  - Token 遵循 `total = input + output`（`cached` 和 `reasoning` 已包含在内，不重复相加）；`usage_status=partial` 保留 `null` 总量与 `known_usage` 观测下界，不把缺失当作 0，也不因失败或 `partial` 剔除已记录请求。
- **同口径对比与三种结论**：
  - 只有同一任务、同一 attempt 策略、同一计时口径才能直接比较；若 baseline 与 harness 在 `runtime`、`arm`、`model`、`reasoning_effort` 或预算上不同，报告必须标注为 **系统级比较（system-level comparison）**，禁止将差异归因于单一并行机制改动。
  - 结论必须分成三层表述：（1）真实端到端体验；（2）模型服务等待占比与故障重试影响；（3）harness 本地调度、并行覆盖与环境执行效率。
