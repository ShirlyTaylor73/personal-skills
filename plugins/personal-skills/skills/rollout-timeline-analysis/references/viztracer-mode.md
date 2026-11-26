# VizTracer 可选深度模式

默认分析只依赖已有业务日志（`result.json`、`openai_events.jsonl`、`lifecycle.jsonl`、`calls.jsonl`、Graph `events.jsonl` 等），**不要求安装或运行 VizTracer**。

## 1. 何时启用

仅当业务日志时间线已经排除了模型 HTTP 等待和机器人动作耗时，但仍存在无法解释的本地 Python 耗时（例如 `non_http_non_robot_overhead_s` 异常偏高、Graph worker 调度停顿、工具序列化或图像处理阻塞）时，才按需启用 VizTracer 采集 Python 函数、线程和异步任务明细。

## 2. 环境检查与安装

检查当前分析环境（本仓库使用 Conda `RPent`）：

```bash
conda run -n RPent python -c "import viztracer; print(viztracer.__version__)"
```

若未安装且用户明确授权安装深度分析依赖，可在对应分析环境中安装（不要修改系统或 base Python）：

```bash
conda run -n RPent python -m pip install viztracer
```

未安装或未提供 VizTracer 文件时的默认降级行为：
- 分析脚本完全跳过 VizTracer 合并步骤；
- 在 `metrics.json` 中记录 `viztracer.status = "not_provided"`（或 `"skipped"`），不影响主时间线和报告生成。

## 3. 采集建议（仅当用户明确要求重跑定位瓶颈时）

VizTracer 会产生较大的 JSON 文件并带来一定 CPU 开销，因此需限制深度与采样范围：

```bash
viztracer --max_stack_depth 12 --min_duration 500us --ignore_c_function \
  -o <analysis_dir>/viztracer_episode.json -- <command>
```

## 4. 关联到 Perfetto 主 Trace

将已采集的 VizTracer JSON 传入分析脚本：

```bash
python ~/.codex/skills/rollout-timeline-analysis/scripts/analyze_rollout.py \
  <episode_dir> \
  --out <analysis_dir> \
  --viztracer <viztracer_episode.json> \
  [--viztracer-offset-s <calibrated_offset_seconds>]
```

时钟对齐规则：
- **未提供校准偏移且 VizTracer 文件无可靠墙钟锚点时**：脚本绝不强行平移 VizTracer 事件去贴合业务时间线，而是将 VizTracer 切片放入独立进程泳道 `VizTracer (Uncalibrated)`（`pid >= 6`），并在 `metadata` 和报告中显式标注 `clock_domain = "viztracer_uncalibrated"`（不可与业务泳道做直接时间对齐或交集计算）。
- **明确提供 `--viztracer-offset-s` 或文件含已验证同步元数据（与 episode/attempt 匹配）时**：按偏移量校准并标注 `clock_domain = "viztracer_calibrated"`，同时在 `args` 中保留 `episode_id` 和 `attempt` 元数据。
- 为防止 Perfetto JSON 体积失控，脚本默认支持 `--viztracer-max-events 20000` 截断保护并在报告中注明是否截断。
