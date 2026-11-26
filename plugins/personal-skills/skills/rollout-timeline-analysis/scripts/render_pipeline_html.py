#!/usr/bin/env python3
"""Generate an interactive Perfetto / Chrome Trace Viewer style multi-lane
pipeline timeline HTML for single episodes or Ours-vs-Baseline comparisons.

Both sides share four aligned tracks with unified terminology:
  1. Agent Inference — model HTTP requests (Ours, measured) / gaps between cells (Baseline, inferred, hatched)
  2. Tool Execution  — tool dispatch->return markers (Ours) / python cell execution (Baseline)
  3. Policy Job     — async Policy Job lifecycle, decision waits, pauses, patches
  4. Policy / Robot — Policy units, stateful robot actions, and readonly queries

Self-contained (no external CDN), works both standalone in a browser and inside
T3 Code's inline html_render frame (uses theme CSS variables with safe fallbacks).
"""

from __future__ import annotations

import json
from typing import Any


def _cluster_robot_calls_fallback(
    events: list[dict[str, Any]],
    *,
    policy_wall_s: float | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Fallback clustering for Codex baseline episodes lacking synthetic pipeline_state events."""
    spans: list[tuple[int, int, str, bool]] = []
    for ev in events:
        if ev.get("process") != "robot_backend":
            continue
        s_ns = ev.get("start_ns")
        e_ns = ev.get("end_ns")
        if s_ns is None or e_ns is None:
            continue
        args = ev.get("args") or {}
        tool = str(args.get("tool") or str(ev.get("event_type") or "").split(":", 1)[-1])
        spans.append((int(s_ns), max(int(s_ns), int(e_ns)), tool, bool(args.get("stateful"))))

    spans.sort(key=lambda x: (x[0], x[1]))
    bursts: list[dict[str, Any]] = []
    for cs, ce, tool, stateful in spans:
        if not bursts or cs - bursts[-1]["end_ns"] > 1_500_000_000:
            bursts.append(
                {
                    "start_ns": cs,
                    "end_ns": ce,
                    "calls": 1,
                    "stateful_tools": [tool] if stateful else [],
                }
            )
        else:
            bursts[-1]["end_ns"] = max(bursts[-1]["end_ns"], ce)
            bursts[-1]["calls"] += 1
            if stateful:
                bursts[-1]["stateful_tools"].append(tool)

    agent_items: list[dict[str, Any]] = []
    tool_items: list[dict[str, Any]] = []
    for idx, b in enumerate(bursts, start=1):
        if idx > 1 and b["start_ns"] > bursts[idx - 2]["end_ns"]:
            s = round(bursts[idx - 2]["end_ns"] / 1e9, 4)
            e = round(b["start_ns"] / 1e9, 4)
            agent_items.append(
                {
                    "s": s,
                    "e": max(s, e),
                    "d": 0,
                    "l": f"infer · {max(0.0, e - s):.1f}s",
                    "c": "#60a5fa",
                    "tc": "#09090b",
                    "hatch": True,
                    "t": f"Agent inference before Cell #{idx} (INFERRED from calls.jsonl gap, not a measured HTTP request)",
                }
            )
        s = round(b["start_ns"] / 1e9, 4)
        e = round(b["end_ns"] / 1e9, 4)
        tools_txt = ", ".join(b["stateful_tools"][:4]) if b["stateful_tools"] else "readonly"
        tool_items.append(
            {
                "s": s,
                "e": max(s, e),
                "d": 0,
                "l": f"Cell #{idx}",
                "c": "#34d399",
                "tc": "#052e16",
                "t": f"Tool Execution: python Cell #{idx} ({b['calls']} calls: {tools_txt})",
            }
        )

    if bursts and policy_wall_s is not None:
        last_end_s = bursts[-1]["end_ns"] / 1e9
        if policy_wall_s > last_end_s + 1.0:
            s = round(last_end_s, 4)
            e = round(float(policy_wall_s), 4)
            agent_items.append(
                {
                    "s": s,
                    "e": max(s, e),
                    "d": 0,
                    "l": "head/tail",
                    "c": "#64748b",
                    "tc": "#f8fafc",
                    "hatch": True,
                    "t": "policy_wall_s minus calls.jsonl span (initial think + finish, unattributed, INFERRED)",
                }
            )

    return agent_items, tool_items


def _tool_color(tools: list[str]) -> tuple[str, str]:
    """Shared color for a model round's chosen tool (Agent lane) and its dispatch (Tool lane)."""
    if tools == ["wait_event"]:
        return "#f59e0b", "#1c1917"
    if any(t in {"python_start", "python", "start_graph"} for t in tools):
        return "#34d399", "#052e16"
    if tools:
        return "#a78bfa", "#09090b"
    return "#38bdf8", "#082f49"


def _compact_episode_for_viewer(
    parsed: dict[str, Any],
    *,
    role_label: str,
) -> dict[str, Any]:
    """Extract four unified multi-lane tracks with nested flame depth for one episode."""
    m = parsed["metrics"]
    events = parsed["events"]

    session_measured = m["clock_alignment"].get("clock_domain") == "codex_session_aligned"
    is_graph = m["settings"].get("arm") == "graph" or bool((m.get("graph") or {}).get("jobs"))
    has_http = m["http"].get("requests_total") is not None

    def _ev_item(
        ev: dict[str, Any],
        *,
        label: str,
        color: str,
        tc: str = "#09090b",
        depth: int = 0,
        detail: str = "",
        kind: str = "",
    ) -> dict[str, Any] | None:
        s_ns = ev.get("start_ns")
        e_ns = ev.get("end_ns")
        if s_ns is None or e_ns is None:
            return None
        s = round(s_ns / 1e9, 4)
        e = round(e_ns / 1e9, 4)
        return {
            "s": s,
            "e": max(s, e),
            "d": depth,
            "l": label,
            "c": color,
            "tc": tc,
            "t": detail or str(ev.get("event_type") or ""),
            **({"k": kind} if kind else {}),
        }

    agent_items: list[dict[str, Any]] = []
    tool_items: list[dict[str, Any]] = []
    job_items: list[dict[str, Any]] = []
    policy_robot_items: list[dict[str, Any]] = []

    has_units = any(
        ev.get("process") == "graph_worker" and str(ev.get("event_type") or "").startswith("graph_unit:")
        for ev in events
    )
    has_robot_stateful = any(
        ev.get("process") == "robot_backend" and bool((ev.get("args") or {}).get("stateful"))
        for ev in events
    )

    if has_http:
        for ev in events:
            proc = ev.get("process")
            etype = str(ev.get("event_type") or "")
            args = ev.get("args") or {}

            if proc == "provider_request":
                req_id = ev.get("request_id")
                att = args.get("attempt", 1)
                tok_in = args.get("prompt_tokens")
                tok_out = args.get("completion_tokens")
                tok_info = (
                    f"tok={tok_in}/{tok_out}" if tok_in is not None else "usage=missing"
                )
                err_info = f", err={args.get('error')}" if args.get("error") else ""
                tools = args.get("triggered_tools") or []
                t_str = ",".join(tools) if tools else ""

                # Agent Inference lane: one block per model HTTP request (measured).
                # Colour = tool the model chose this round (shared with the Tool Execution lane).
                dur_s = max(0.0, (ev["end_ns"] - ev["start_ns"]) / 1e9) if ev.get("end_ns") is not None and ev.get("start_ns") is not None else 0.0
                if etype == "model_request_backoff":
                    ag_it = _ev_item(
                        ev,
                        label="backoff",
                        color="#fca5a5",
                        tc="#09090b",
                        depth=1,
                        detail=f"Retry backoff before R{req_id} (att={att})",
                    )
                elif etype == "model_request_failed":
                    code = args.get("status_code") or "ERR"
                    ag_it = _ev_item(
                        ev,
                        label=f"R{req_id} err {code}",
                        color="#ef4444",
                        tc="#ffffff",
                        depth=0,
                        detail=f"R{req_id} failed HTTP {code} (att={att}, {tok_info}{err_info})",
                    )
                elif etype == "model_request_cancelled":
                    ag_it = _ev_item(
                        ev,
                        label=f"R{req_id} cancelled",
                        color="#f97316",
                        tc="#09090b",
                        depth=0,
                        detail=f"R{req_id} cancelled (att={att}, reason={args.get('reason')})",
                    )
                elif etype == "model_request_incomplete":
                    ag_it = _ev_item(
                        ev,
                        label=f"R{req_id} incomplete",
                        color="#ef4444",
                        tc="#ffffff",
                        depth=0,
                        detail=f"R{req_id} incomplete (att={att})",
                    )
                elif etype == "model_request_retry":
                    ag_it = _ev_item(
                        ev,
                        label=f"R{req_id} retry",
                        color="#3b82f6",
                        tc="#ffffff",
                        depth=0,
                        detail=f"R{req_id} retry (att={att}, {tok_info})",
                    )
                else:
                    col, tcol = _tool_color(tools)
                    nxt = f" -> {t_str}" if t_str else ""
                    ag_it = _ev_item(
                        ev,
                        label=f"R{req_id} · {dur_s:.1f}s",
                        color=col,
                        tc=tcol,
                        depth=0,
                        detail=f"Agent inference R{req_id}{nxt} (att={att}, {tok_info}); colour = tool chosen this round",
                    )
                if ag_it:
                    agent_items.append(ag_it)

            elif proc == "policy_runtime":
                if etype.startswith("tool_dispatch:"):
                    # Tool Execution lane: real dispatch->return interval, drawn as a labelled marker.
                    tname = etype.split(":", 1)[1]
                    el_s = args.get("elapsed_s")
                    el_txt = f"elapsed={el_s:.3f}s, " if isinstance(el_s, (int, float)) else ""
                    col, _tc = _tool_color([tname])
                    it = _ev_item(
                        ev,
                        label=tname,
                        color=col,
                        tc=_tc,
                        depth=0,
                        detail=(
                            f"Tool dispatch->return: {tname} (R{ev.get('request_id')}, {el_txt}"
                            f"images={args.get('images', 0)}, status={ev.get('status')})"
                        ),
                        kind="m",
                    )
                    if it:
                        tool_items.append(it)
                elif etype.startswith("lifecycle:"):
                    lname = etype.split(":", 1)[1]
                    it = _ev_item(
                        ev,
                        label=f"lifecycle:{lname}",
                        color="#94a3b8",
                        tc="#09090b",
                        depth=2,
                        detail=f"Lifecycle: {lname} (status={ev.get('status')})",
                    )
                    if it:
                        tool_items.append(it)

            elif proc == "graph_manager":
                if etype.startswith("graph_job:"):
                    jid = str(ev.get("job_id") or "")
                    it = _ev_item(
                        ev,
                        label=f"job:{jid[:6]}",
                        color="#38bdf8",
                        tc="#082f49",
                        depth=0,
                        detail=f"Policy Job {jid} (status={ev.get('status')})",
                    )
                    if it:
                        job_items.append(it)
                elif etype.startswith("decision_wait:"):
                    it = _ev_item(
                        ev,
                        label="wait_decision",
                        color="#ef4444",
                        tc="#ffffff",
                        depth=1,
                        detail=f"Policy blocked waiting for Agent decision ({etype}, choice={args.get('choice')})",
                    )
                    if it:
                        job_items.append(it)
                elif etype == "pause_interval":
                    it = _ev_item(
                        ev,
                        label="paused",
                        color="#fb923c",
                        tc="#1c1917",
                        depth=1,
                        detail="Policy job paused",
                    )
                    if it:
                        job_items.append(it)
                elif etype.startswith("graph_patched:"):
                    it = _ev_item(
                        ev,
                        label="patch",
                        color="#e879f9",
                        tc="#09090b",
                        depth=2,
                        detail=f"{etype} changed={args.get('changed')}",
                    )
                    if it:
                        job_items.append(it)
                elif etype in {"cancelled", "pause_requested"}:
                    it = _ev_item(
                        ev,
                        label="cancelled" if etype == "cancelled" else "pause_req",
                        color="#ef4444" if etype == "cancelled" else "#fb923c",
                        tc="#ffffff" if etype == "cancelled" else "#1c1917",
                        depth=2,
                        detail=f"Policy Job {etype}",
                    )
                    if it:
                        job_items.append(it)

            elif proc == "graph_worker":
                if etype.startswith("graph_unit:"):
                    uname = ev.get("unit_id") or "unit"
                    it = _ev_item(
                        ev,
                        label=f"unit:{uname}",
                        color="#4ade80",
                        tc="#052e16",
                        depth=0,
                        detail=f"Policy unit: {uname} (primitive={args.get('primitive')}, rev={args.get('plan_revision')})",
                    )
                    if it:
                        policy_robot_items.append(it)
                elif etype.startswith("graph_action:") and not has_robot_stateful:
                    prim = args.get("primitive") or "action"
                    it = _ev_item(
                        ev,
                        label=str(prim),
                        color="#10b981",
                        tc="#052e16",
                        depth=1 if has_units else 0,
                        detail=f"Policy/Robot: {prim} (unit={ev.get('unit_id')}, env_steps={args.get('env_steps')})",
                    )
                    if it:
                        policy_robot_items.append(it)
                elif etype.startswith("error:"):
                    it = _ev_item(
                        ev,
                        label="err",
                        color="#ef4444",
                        tc="#ffffff",
                        depth=2 if has_units else 1,
                        detail=str(args.get("error") or etype),
                    )
                    if it:
                        policy_robot_items.append(it)

            elif proc == "robot_backend":
                tname = args.get("tool") or etype.split(":", 1)[-1]
                st = bool(args.get("stateful"))
                depth = (1 if st else 2) if has_units else (0 if st else 1)
                it = _ev_item(
                    ev,
                    label=str(tname),
                    color="#10b981" if st else "#64748b",
                    tc="#052e16" if st else "#f8fafc",
                    depth=depth,
                    detail=f"Policy/Robot: {tname} (stateful={st}, env_steps={args.get('env_steps')})",
                )
                if it:
                    policy_robot_items.append(it)
    else:
        # Baseline (Codex / calls_epoch_relative): same 4 aligned tracks
        for ev in events:
            proc = ev.get("process")
            etype = str(ev.get("event_type") or "")
            args = ev.get("args") or {}

            if proc == "pipeline_state":
                if etype == "pipeline:baseline_round":
                    tool = args.get("tool")
                    rno = args.get("round")
                    col, tcol = _tool_color([tool] if tool else [])
                    cut = bool(args.get("cut_by_timeout"))
                    it = _ev_item(
                        ev,
                        label=f"R{rno}",
                        color="#f97316" if cut else col,
                        tc="#09090b" if cut else tcol,
                        depth=0,
                        detail=(
                            f"Agent inference R{rno}"
                            + (f" -> {tool}" if tool else " (final reply)")
                            + (" (cut by timeout)" if cut else "")
                            + " (measured from Codex session); colour = tool chosen this round"
                        ),
                    )
                    if it:
                        it["l"] = f"R{rno} · {it['e'] - it['s']:.1f}s"
                        agent_items.append(it)
                elif etype == "pipeline:baseline_attempt_error":
                    it = _ev_item(
                        ev,
                        label="err",
                        color="#ef4444",
                        tc="#ffffff",
                        depth=0,
                        detail=f"Planner attempt {args.get('attempt')} failed: {args.get('error')}",
                    )
                    if it:
                        it["l"] = f"att{args.get('attempt')} err · {it['e'] - it['s']:.1f}s"
                        agent_items.append(it)
                elif etype == "pipeline:baseline_backoff":
                    it = _ev_item(
                        ev,
                        label="backoff",
                        color="#fca5a5",
                        tc="#09090b",
                        depth=0,
                        detail=f"Retry backoff before planner attempt {args.get('attempt')}",
                    )
                    if it:
                        it["l"] = f"backoff · {it['e'] - it['s']:.1f}s"
                        agent_items.append(it)
                elif etype == "pipeline:baseline_tool_exec":
                    tname = str(args.get("tool") or "tool")
                    col, tcol = _tool_color([tname])
                    it = _ev_item(
                        ev,
                        label=tname,
                        color=col,
                        tc=tcol,
                        depth=0,
                        detail=f"Tool dispatch->return: {tname} (measured from Codex session)",
                        kind="m",
                    )
                    if it:
                        tool_items.append(it)
                elif etype == "pipeline:baseline_llm_gap":
                    before_cell = args.get("before_cell")
                    before_txt = f" before Cell #{before_cell}" if before_cell else ""
                    it = _ev_item(
                        ev,
                        label="infer",
                        color="#60a5fa",
                        tc="#09090b",
                        depth=0,
                        detail=f"Agent inference{before_txt} (INFERRED from calls.jsonl gap, not a measured HTTP request)",
                    )
                    if it:
                        it["l"] = f"infer · {it['e'] - it['s']:.1f}s"
                        it["hatch"] = True
                        agent_items.append(it)
                elif etype == "pipeline:baseline_unattributed_tail":
                    it = _ev_item(
                        ev,
                        label="head/tail",
                        color="#64748b",
                        tc="#f8fafc",
                        depth=0,
                        detail="policy_wall_s beyond the observed span (unattributed, INFERRED)",
                    )
                    if it:
                        it["hatch"] = True
                        if session_measured:
                            it["l"] = "tail"
                        agent_items.append(it)
                elif etype == "pipeline:baseline_cell_exec":
                    cidx = args.get("cell_index", "")
                    stools = args.get("stateful_tools") or []
                    tools_txt = ", ".join(stools[:4]) if stools else "readonly"
                    it = _ev_item(
                        ev,
                        label=f"Cell #{cidx}",
                        color="#34d399",
                        tc="#052e16",
                        depth=0,
                        detail=f"Tool Execution: python Cell #{cidx} ({args.get('calls')} calls: {tools_txt})",
                    )
                    if it:
                        tool_items.append(it)
            elif proc == "policy_runtime" and etype.startswith("lifecycle:"):
                lname = etype.split(":", 1)[1]
                it = _ev_item(
                    ev,
                    label=f"lifecycle:{lname}",
                    color="#94a3b8",
                    tc="#09090b",
                    depth=2,
                    detail=f"Lifecycle: {lname}",
                )
                if it:
                    tool_items.append(it)
            elif proc == "robot_backend":
                tname = args.get("tool") or etype.split(":", 1)[-1]
                st = bool(args.get("stateful"))
                it = _ev_item(
                    ev,
                    label=str(tname),
                    color="#10b981" if st else "#64748b",
                    tc="#052e16" if st else "#f8fafc",
                    depth=0 if st else 1,
                    detail=f"Policy/Robot: {tname} (stateful={st}, env_steps={args.get('env_steps')})",
                )
                if it:
                    policy_robot_items.append(it)

        # Fallback if baseline events lacked synthetic pipeline_state rows
        if not agent_items and not tool_items and policy_robot_items:
            agent_items, tool_items = _cluster_robot_calls_fallback(
                events,
                policy_wall_s=m["timings_s"].get("policy_wall_s"),
            )

    lanes = [
        {
            "name": "Agent Inference",
            "sub": (
                "model HTTP requests (measured)"
                if has_http
                else "model rounds from Codex session (measured)"
                if session_measured
                else "gap between cells (inferred)"
            ),
            "items": agent_items,
            "emptyNote": "" if agent_items else "No per-request Agent timestamps",
        },
        {
            "name": "Tool Execution",
            "sub": "dispatch → return (measured)" if has_http else "python cell execution (measured)",
            "rows": 3,
            "items": tool_items,
            "emptyNote": "" if tool_items else "No tool calls recorded",
        },
        {
            "name": "Policy Job",
            "sub": "async policy job" if is_graph else "n/a (sync mode)",
            "items": job_items,
            "emptyNote": "No async policy job" if is_graph else "Sync mode (no async policy job)",
        },
        {
            "name": "Policy / Robot",
            "sub": "units, actions, queries",
            "items": policy_robot_items,
            "emptyNote": "" if policy_robot_items else "No robot calls recorded",
        },
    ]

    max_t = 0.0
    for lane in lanes:
        for it in lane["items"]:
            if it["e"] > max_t:
                max_t = it["e"]
    roll_s = m["timings_s"].get("rollout_wall_time_s")
    pol_s = m["timings_s"].get("policy_wall_s")
    ref_s = roll_s if roll_s is not None else pol_s
    if ref_s and float(ref_s) > max_t:
        max_t = float(ref_s)

    # Unified meta summary line
    meta_parts: list[str] = []
    if roll_s is not None:
        meta_parts.append(f"rollout={roll_s:.1f}s")
    elif pol_s is not None:
        meta_parts.append(f"policy_wall={pol_s:.1f}s")
    if m["timings_s"].get("agent_inference_s") is not None:
        meta_parts.append(f"Agent={m['timings_s']['agent_inference_s']:.1f}s")
    if m["timings_s"].get("tool_execution_s") is not None:
        meta_parts.append(f"Tool={m['timings_s']['tool_execution_s']:.1f}s")
    if m["timings_s"].get("robot_action_union_s") is not None:
        meta_parts.append(f"Policy={m['timings_s']['robot_action_union_s']:.1f}s")
    if m["timings_s"].get("http_robot_overlap_s") is not None:
        meta_parts.append(f"overlap={m['timings_s']['http_robot_overlap_s']:.1f}s")
    rounds = (m.get("counts") or {}).get("agent_rounds")
    if rounds is not None:
        waits = (m.get("counts") or {}).get("wait_event_rounds")
        meta_parts.append(f"rounds={rounds}" + (f"(wait_event {waits})" if waits is not None else ""))
    if m["http"].get("requests_total") is not None:
        meta_parts.append(
            f"req={m['http']['requests_total']}(f{m['http'].get('requests_failed') or 0}/r{m['http'].get('retry_attempts') or 0})"
        )
    if (m.get("codex_session") or {}).get("failed_attempts"):
        meta_parts.append(f"failed_attempts={m['codex_session']['failed_attempts']}")
    meta_parts.append(f"clock={m['clock_alignment']['clock_domain']}")

    arm_str = m["settings"].get("arm") or "unknown"
    rt_str = m["settings"].get("runtime") or "unknown"
    role_display = f"{role_label} ({arm_str}/{rt_str})"

    return {
        "role": role_display,
        "episode_id": m["episode_id"],
        "suite": m["suite"],
        "attempt": m["attempt"],
        "arm": arm_str,
        "runtime": rt_str,
        "outcome": m["outcome"],
        "clock_domain": m["clock_alignment"]["clock_domain"],
        "max_t": round(max_t, 3),
        "meta": " · ".join(meta_parts),
        "lanes": lanes,
    }


def render_pipeline_timeline_html(
    primary_parsed: list[dict[str, Any]],
    *,
    primary_label: str,
    other_parsed: list[dict[str, Any]] | None = None,
    other_label: str | None = None,
    default_episode: str | None = None,
    comparison_scope: str | None = None,
    confounders: list[str] | None = None,
) -> str:
    """Build standalone interactive Perfetto-like 4-track aligned pipeline timeline HTML."""
    p_by_id = {
        p["metrics"]["episode_id"]: _compact_episode_for_viewer(p, role_label=primary_label)
        for p in primary_parsed
    }
    o_by_id = (
        {
            p["metrics"]["episode_id"]: _compact_episode_for_viewer(
                p, role_label=other_label or "baseline"
            )
            for p in other_parsed
        }
        if other_parsed
        else {}
    )
    ep_ids = sorted(p_by_id.keys())
    if not default_episode or default_episode not in p_by_id:
        preferred = None
        for cand in ("10_task_t0_s0", "10_swap_t0_s0", "spatial_task_t0_s0"):
            if cand in p_by_id:
                preferred = cand
                break
        default_episode = preferred or (ep_ids[0] if ep_ids else "")

    payload = {
        "primary_label": primary_label,
        "other_label": other_label,
        "comparison_scope": comparison_scope,
        "confounders": confounders or [],
        "episode_ids": ep_ids,
        "default_episode": default_episode,
        "primary": p_by_id,
        "other": o_by_id,
    }
    data_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<title>Rollout Pipeline Timeline Viewer</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 0;
    font-family: var(--font-sans, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif);
    color: var(--foreground, #e5e7eb);
    background: var(--background, #09090b);
    font-size: 12px;
    line-height: 1.4;
    user-select: none;
  }}
  .app {{ display: flex; flex-direction: column; gap: 10px; width: 100%; padding: 10px; }}
  .toolbar {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    background: var(--card, #18181b);
    border: 1px solid var(--border, #27272a);
    border-radius: var(--radius, 8px);
    padding: 9px 12px;
  }}
  .tb-group {{ display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }}
  select, button {{
    background: var(--secondary, #27272a);
    color: var(--foreground, #f4f4f5);
    border: 1px solid var(--border, #3f3f46);
    border-radius: 5px;
    padding: 4px 8px;
    font-size: 11.5px;
    cursor: pointer;
    font-family: inherit;
  }}
  select {{ font-family: var(--font-mono, monospace); }}
  button:hover {{ border-color: var(--ring, #60a5fa); }}
  button.active {{
    background: var(--primary, #2563eb);
    color: var(--primary-foreground, #ffffff);
    border-color: var(--primary, #2563eb);
  }}
  .banner {{
    font-size: 11px;
    padding: 6px 10px;
    border-radius: 6px;
    background: var(--warning-surface, rgba(234,179,8,0.14));
    color: var(--warning, #eab308);
    border: 1px solid var(--border, #3f3f46);
  }}
  .legend {{
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    font-size: 11px;
    color: var(--muted-foreground, #a1a1aa);
    padding: 0 2px;
  }}
  .lg {{ display: inline-flex; align-items: center; gap: 5px; }}
  .sw {{ width: 10px; height: 10px; border-radius: 2px; display: inline-block; }}
  .sw.hatch {{ background-image: repeating-linear-gradient(45deg, rgba(9,9,11,.45) 0 1.5px, transparent 1.5px 4px); }}
  .track-card {{
    background: var(--card, #18181b);
    border: 1px solid var(--border, #27272a);
    border-radius: var(--radius, 8px);
    overflow: hidden;
  }}
  .track-head {{
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: var(--secondary, #202024);
    border-bottom: 1px solid var(--border, #27272a);
  }}
  .track-title {{ font-weight: 600; font-size: 12.5px; }}
  .track-meta {{
    font-family: var(--font-mono, monospace);
    font-size: 11px;
    color: var(--muted-foreground, #a1a1aa);
  }}
  .canvas-wrap {{ position: relative; width: 100%; cursor: grab; }}
  .canvas-wrap:active {{ cursor: grabbing; }}
  canvas {{ display: block; width: 100%; }}
  .inspector {{
    background: var(--card, #18181b);
    border: 1px solid var(--border, #27272a);
    border-radius: var(--radius, 8px);
    padding: 8px 12px;
    font-family: var(--font-mono, monospace);
    font-size: 11px;
    color: var(--muted-foreground, #a1a1aa);
    min-height: 36px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: center;
  }}
  .inspector strong {{ color: var(--foreground, #f4f4f5); }}
</style>
</head>
<body>
<div class="app">
  <div class="toolbar">
    <div class="tb-group">
      <span style="color:var(--muted-foreground)">Episode:</span>
      <select id="ep-select"></select>
      <button id="btn-sync" class="active" title="两端使用相同最大时间轴刻度，直观比较总时长">同轴刻度</button>
      <button id="btn-fit" title="重置缩放到完整 episode">重置缩放</button>
      <button id="btn-zin" title="放大时间轴 (+)">放大 +</button>
      <button id="btn-zout" title="缩小时间轴 (-)">缩小 -</button>
    </div>
    <div class="tb-group" style="font-size:11px;color:var(--muted-foreground)">
      <span>滚轮缩放 · 拖拽平移 · 悬停/点击切片看详情</span>
    </div>
  </div>

  <div id="scope-banner" class="banner" style="display:none"></div>

  <div class="legend">
    <span class="lg"><b>Agent Inference</b> (Rn = round, colour = tool chosen):</span>
    <span class="lg"><span class="sw" style="background:#34d399"></span>→ python_start / Cell</span>
    <span class="lg"><span class="sw" style="background:#f59e0b"></span>→ wait_event (polling)</span>
    <span class="lg"><span class="sw" style="background:#a78bfa"></span>→ patch / resolve / finish</span>
    <span class="lg"><span class="sw" style="background:#ef4444"></span>HTTP error / wait_decision</span>
    <span class="lg"><span class="sw" style="background:#fca5a5"></span>backoff</span>
    <span class="lg"><span class="sw hatch" style="background:#60a5fa"></span>inferred (Baseline, not measured)</span>
    <span style="flex-basis:100%;height:0"></span>
    <span class="lg"><b>Tool Execution</b>: marker = dispatch→return (≈0s), block = Cell</span>
    <span class="lg"><span class="sw" style="background:#94a3b8"></span>lifecycle</span>
    <span style="flex-basis:100%;height:0"></span>
    <span class="lg"><b>Policy</b>:</span>
    <span class="lg"><span class="sw" style="background:#38bdf8"></span>Policy Job</span>
    <span class="lg"><span class="sw" style="background:#10b981"></span>Policy / Robot (action)</span>
    <span class="lg"><span class="sw" style="background:#64748b"></span>readonly / head-tail</span>
  </div>

  <div class="track-card" id="card-primary">
    <div class="track-head">
      <div class="track-title" id="title-primary"></div>
      <div class="track-meta" id="meta-primary"></div>
    </div>
    <div class="canvas-wrap"><canvas id="cv-primary"></canvas></div>
  </div>

  <div class="track-card" id="card-other" style="display:none">
    <div class="track-head">
      <div class="track-title" id="title-other"></div>
      <div class="track-meta" id="meta-other"></div>
    </div>
    <div class="canvas-wrap"><canvas id="cv-other"></canvas></div>
  </div>

  <div class="inspector" id="inspector">
    <span>悬停或点击任意时间块以查看精确起止时间、持续时长与事件详情。</span>
  </div>
</div>

<script>
const DATA = {data_json};
const LABEL_W = 158;
const RULER_H = 22;
const ROW_H = 18;
const LANE_PAD = 6;

let currentEp = DATA.default_episode;
let syncScale = true;
const viewState = {{
  primary: {{ start: 0, end: 100 }},
  other: {{ start: 0, end: 100 }},
}};
let hitBoxes = {{ primary: [], other: [] }};

const sel = document.getElementById("ep-select");
for (const id of DATA.episode_ids) {{
  const opt = document.createElement("option");
  opt.value = id;
  const pe = DATA.primary[id];
  const oe = DATA.other[id];
  const gS = pe ? Math.round(pe.max_t) + "s" : "-";
  const bS = oe ? " vs " + Math.round(oe.max_t) + "s" : "";
  opt.textContent = `${{id}} (${{gS}}${{bS}})`;
  if (id === currentEp) opt.selected = true;
  sel.appendChild(opt);
}}

if (DATA.comparison_scope === "system_level") {{
  const b = document.getElementById("scope-banner");
  b.style.display = "block";
  b.textContent = "系统级比较提示：两侧存在配置/口径差异（" + DATA.confounders.join(", ") + "）；Ours 的 Agent Inference 来自逐次 HTTP 请求；Baseline 来自 Codex model_sessions 的逐轮时间戳（实测，非 HTTP 口径），缺少 session 时才退化为 calls.jsonl 间隔推断（斜线区间）。";
}}

function cssVar(name, fallback) {{
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return v || fallback;
}}

function laneHeight(lane) {{
  let maxD = 0;
  for (const it of lane.items) if (it.d > maxD) maxD = it.d;
  return Math.max(38, (lane.rows || (maxD + 1)) * ROW_H + LANE_PAD * 2);
}}

function resetZoom() {{
  const pe = DATA.primary[currentEp];
  const oe = DATA.other[currentEp];
  const pMax = Math.max(1, pe ? pe.max_t : 1);
  const oMax = Math.max(1, oe ? oe.max_t : 1);
  const common = Math.max(pMax, oMax);
  viewState.primary = {{ start: 0, end: syncScale && oe ? common : pMax }};
  viewState.other = {{ start: 0, end: syncScale && oe ? common : oMax }};
  renderAll();
}}

function zoom(factor, centerRatio = 0.5) {{
  for (const key of ["primary", "other"]) {{
    const st = viewState[key];
    const span = st.end - st.start;
    const center = st.start + span * centerRatio;
    const newSpan = Math.max(0.5, span * factor);
    const ep = key === "primary" ? DATA.primary[currentEp] : DATA.other[currentEp];
    const maxBound = syncScale && DATA.other[currentEp]
      ? Math.max(DATA.primary[currentEp]?.max_t || 1, DATA.other[currentEp]?.max_t || 1)
      : (ep?.max_t || 1);
    let ns = center - newSpan * centerRatio;
    let ne = ns + newSpan;
    if (ns < 0) {{ ns = 0; ne = Math.min(maxBound, newSpan); }}
    if (ne > maxBound) {{ ne = maxBound; ns = Math.max(0, maxBound - newSpan); }}
    viewState[key] = {{ start: ns, end: ne }};
  }}
  renderAll();
}}

function fmtSec(s) {{
  if (s >= 60) {{
    const m = Math.floor(s / 60);
    const r = (s - m * 60).toFixed(s - m * 60 >= 10 ? 1 : 2);
    return `${{m}}m${{r}}s`;
  }}
  return s >= 10 ? s.toFixed(1) + "s" : s.toFixed(2) + "s";
}}

function showInspector(b) {{
  const insp = document.getElementById("inspector");
  const dur = (b.it.e - b.it.s).toFixed(3);
  insp.replaceChildren();
  const s1 = document.createElement("strong");
  s1.textContent = `[${{b.role}} · ${{b.lane}}]`;
  const s2 = document.createElement("strong");
  s2.textContent = b.it.l;
  const s3 = document.createElement("span");
  s3.textContent = `[${{b.it.s.toFixed(2)}}s .. ${{b.it.e.toFixed(2)}}s]`;
  const s4 = document.createElement("span");
  s4.textContent = "dur=";
  const s4b = document.createElement("strong");
  s4b.textContent = `${{dur}}s`;
  s4.appendChild(s4b);
  const s5 = document.createElement("span");
  s5.textContent = b.it.t;
  insp.append(s1, s2, s3, s4, s5);
}}

function drawPanel(key, epData, canvasId, titleId, metaId) {{
  const card = document.getElementById(key === "primary" ? "card-primary" : "card-other");
  if (!epData) {{
    card.style.display = "none";
    hitBoxes[key] = [];
    return;
  }}
  card.style.display = "block";
  document.getElementById(titleId).textContent =
    `${{epData.role}} · ${{epData.episode_id}} [${{epData.outcome}}]`;
  document.getElementById(metaId).textContent = epData.meta;

  const canvas = document.getElementById(canvasId);
  const dpr = window.devicePixelRatio || 1;
  const width = Math.max(320, canvas.parentElement.clientWidth || 700);
  let totalH = RULER_H;
  for (const lane of epData.lanes) totalH += laneHeight(lane);
  canvas.style.height = totalH + "px";
  canvas.width = Math.round(width * dpr);
  canvas.height = Math.round(totalH * dpr);

  const ctx = canvas.getContext("2d");
  ctx.scale(dpr, dpr);

  const fg = cssVar("--foreground", "#e5e7eb");
  const muted = cssVar("--muted-foreground", "#a1a1aa");
  const border = cssVar("--border", "#2e2e34");
  const cardBg = cssVar("--card", "#18181b");
  const stripeBg = cssVar("--secondary", "#202026");

  ctx.fillStyle = cardBg;
  ctx.fillRect(0, 0, width, totalH);

  const st = viewState[key];
  const span = Math.max(0.01, st.end - st.start);
  const plotW = Math.max(80, width - LABEL_W - 8);
  const xOf = (t) => LABEL_W + ((t - st.start) / span) * plotW;

  ctx.fillStyle = stripeBg;
  ctx.fillRect(0, 0, width, RULER_H);
  const rawStep = span / Math.max(4, Math.floor(plotW / 85));
  const pow10 = Math.pow(10, Math.floor(Math.log10(rawStep)));
  const nice = [1, 2, 5, 10].find((m) => m * pow10 >= rawStep) * pow10;
  const firstTick = Math.ceil(st.start / nice) * nice;

  ctx.font = "10px ui-monospace, SFMono-Regular, Menlo, monospace";
  ctx.textBaseline = "middle";
  for (let t = firstTick; t <= st.end + nice * 0.01; t += nice) {{
    const x = xOf(t);
    if (x < LABEL_W || x > width - 4) continue;
    ctx.strokeStyle = border;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x + 0.5, RULER_H);
    ctx.lineTo(x + 0.5, totalH);
    ctx.stroke();
    ctx.fillStyle = muted;
    ctx.fillText(fmtSec(t), x + 3, RULER_H / 2);
  }}

  const boxes = [];
  let y = RULER_H;
  epData.lanes.forEach((lane, idx) => {{
    const lh = laneHeight(lane);
    if (idx % 2 === 1) {{
      ctx.fillStyle = stripeBg;
      ctx.globalAlpha = 0.45;
      ctx.fillRect(0, y, width, lh);
      ctx.globalAlpha = 1.0;
    }}
    ctx.strokeStyle = border;
    ctx.beginPath();
    ctx.moveTo(0, y + 0.5);
    ctx.lineTo(width, y + 0.5);
    ctx.stroke();

    ctx.fillStyle = fg;
    ctx.font = "600 11px system-ui, -apple-system, sans-serif";
    ctx.fillText(lane.name, 8, y + LANE_PAD + 7);
    if (lane.sub) {{
      ctx.fillStyle = muted;
      ctx.font = "9.5px system-ui, -apple-system, sans-serif";
      ctx.fillText(lane.sub, 8, y + LANE_PAD + 21);
    }}

    ctx.save();
    ctx.beginPath();
    ctx.rect(LABEL_W, y, plotW + 4, lh);
    ctx.clip();

    if (!lane.items.length && lane.emptyNote) {{
      ctx.fillStyle = muted;
      ctx.font = "italic 10.5px system-ui, -apple-system, sans-serif";
      ctx.fillText(lane.emptyNote, LABEL_W + 10, y + lh / 2);
    }}

    // Markers (tool dispatch->return): thin line + staggered name flag outside the line.
    const flagEnd = [-1e9, -1e9];
    const items = lane.items.slice().sort((p, q) => p.s - q.s);
    for (const it of items) {{
      if (it.e < st.start || it.s > st.end) continue;
      const x1 = Math.max(LABEL_W, xOf(it.s));
      const x2 = Math.min(LABEL_W + plotW, xOf(it.e));
      if (it.k === "m") {{
        const w = Math.max(2.5, x2 - x1);
        const top = y + LANE_PAD;
        ctx.fillStyle = it.c;
        ctx.fillRect(x1, top, w, ROW_H * 2 - 3);
        ctx.font = "600 10px ui-monospace, SFMono-Regular, Menlo, monospace";
        const tw = ctx.measureText(it.l).width + 6;
        let lvl = -1;
        for (let k = 0; k < 2; k++) {{
          if (x1 + w + 2 >= flagEnd[k]) {{ lvl = k; break; }}
        }}
        if (lvl >= 0 && x1 + w + 3 + tw <= LABEL_W + plotW + 4) {{
          flagEnd[lvl] = x1 + w + 3 + tw + 4;
          ctx.fillStyle = it.c;
          ctx.fillText(it.l, x1 + w + 3, top + lvl * ROW_H + (ROW_H - 3) / 2 + 0.5);
          boxes.push({{ x: x1 + w + 3, y: top + lvl * ROW_H, w: tw, h: ROW_H - 3, lane: lane.name, role: epData.role, it }});
        }}
        boxes.push({{ x: x1 - 3, y: top, w: w + 6, h: ROW_H * 2 - 3, lane: lane.name, role: epData.role, it }});
        continue;
      }}
      const w = Math.max(1.8, x2 - x1);
      const ry = y + LANE_PAD + it.d * ROW_H;
      const rh = ROW_H - 3;

      ctx.fillStyle = it.c;
      ctx.fillRect(x1, ry, w, rh);
      if (it.hatch) {{
        ctx.save();
        ctx.beginPath();
        ctx.rect(x1, ry, w, rh);
        ctx.clip();
        ctx.strokeStyle = "rgba(9,9,11,0.45)";
        ctx.lineWidth = 1.2;
        for (let hx = x1 - rh; hx < x1 + w + rh; hx += 5) {{
          ctx.beginPath();
          ctx.moveTo(hx, ry + rh);
          ctx.lineTo(hx + rh, ry);
          ctx.stroke();
        }}
        ctx.restore();
      }}
      if (w >= 28) {{
        ctx.fillStyle = it.tc || "#09090b";
        ctx.font = "600 10px ui-monospace, SFMono-Regular, Menlo, monospace";
        const maxChars = Math.max(1, Math.floor((w - 6) / 6.1));
        const txt = it.l.length > maxChars ? it.l.slice(0, maxChars - 1) + "…" : it.l;
        ctx.fillText(txt, x1 + 3, ry + rh / 2 + 0.5);
      }}
      boxes.push({{ x: x1, y: ry, w, h: rh, lane: lane.name, role: epData.role, it }});
    }}
    ctx.restore();
    y += lh;
  }});

  ctx.strokeStyle = border;
  ctx.beginPath();
  ctx.moveTo(LABEL_W - 0.5, 0);
  ctx.lineTo(LABEL_W - 0.5, totalH);
  ctx.stroke();

  hitBoxes[key] = boxes;
}}

function renderAll() {{
  drawPanel("primary", DATA.primary[currentEp], "cv-primary", "title-primary", "meta-primary");
  drawPanel("other", DATA.other[currentEp], "cv-other", "title-other", "meta-other");
}}

function attachInteraction(key, canvasId) {{
  const cv = document.getElementById(canvasId);
  let dragging = false;
  let dragStartX = 0;
  let dragOrig = null;

  cv.addEventListener("wheel", (e) => {{
    e.preventDefault();
    const rect = cv.getBoundingClientRect();
    const ratio = Math.min(1, Math.max(0, (e.clientX - rect.left - LABEL_W) / Math.max(1, rect.width - LABEL_W)));
    zoom(e.deltaY > 0 ? 1.25 : 0.8, ratio);
  }}, {{ passive: false }});

  cv.addEventListener("mousedown", (e) => {{
    dragging = true;
    dragStartX = e.clientX;
    dragOrig = {{
      primary: {{ ...viewState.primary }},
      other: {{ ...viewState.other }},
    }};
  }});

  window.addEventListener("mouseup", () => {{ dragging = false; }});
  window.addEventListener("mousemove", (e) => {{
    if (!dragging) return;
    const rect = cv.getBoundingClientRect();
    const dx = e.clientX - dragStartX;
    const plotW = Math.max(80, rect.width - LABEL_W - 8);
    const keysToMove = syncScale && DATA.other[currentEp] ? ["primary", "other"] : [key];
    for (const k of keysToMove) {{
      const orig = dragOrig[k];
      const span = orig.end - orig.start;
      const dt = -(dx / plotW) * span;
      const ep = k === "primary" ? DATA.primary[currentEp] : DATA.other[currentEp];
      const maxBound = syncScale && DATA.other[currentEp]
        ? Math.max(DATA.primary[currentEp]?.max_t || 1, DATA.other[currentEp]?.max_t || 1)
        : (ep?.max_t || 1);
      let ns = Math.max(0, Math.min(maxBound - span, orig.start + dt));
      viewState[k] = {{ start: ns, end: ns + span }};
    }}
    renderAll();
  }});

  const inspectHit = (e) => {{
    if (dragging) return;
    const rect = cv.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const boxes = hitBoxes[key] || [];
    for (let i = boxes.length - 1; i >= 0; i--) {{
      const b = boxes[i];
      if (mx >= b.x && mx <= b.x + b.w && my >= b.y && my <= b.y + b.h) {{
        showInspector(b);
        return;
      }}
    }}
  }};
  cv.addEventListener("mousemove", inspectHit);
  cv.addEventListener("click", inspectHit);
}}

sel.addEventListener("change", () => {{ currentEp = sel.value; resetZoom(); }});
document.getElementById("btn-sync").addEventListener("click", (e) => {{
  syncScale = !syncScale;
  e.target.classList.toggle("active", syncScale);
  resetZoom();
}});
document.getElementById("btn-fit").addEventListener("click", resetZoom);
document.getElementById("btn-zin").addEventListener("click", () => zoom(0.65));
document.getElementById("btn-zout").addEventListener("click", () => zoom(1.5));

attachInteraction("primary", "cv-primary");
attachInteraction("other", "cv-other");
window.addEventListener("resize", renderAll);
resetZoom();
</script>
</body>
</html>
"""
