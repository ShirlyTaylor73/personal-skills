#!/usr/bin/env python3
"""Offline parser, Perfetto Trace Event JSON exporter, and critical-path analyzer
for baseline (Codex / OpenAI cells) and REAgent harness (Graph) robot rollout logs.

Read-only with respect to input artifacts; writes all outputs to --out.
Zero external dependencies (Python 3.10+ standard library only).
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

# Fixed Perfetto process lanes (aligned with HTML viewer: Agent Inference / Tool Execution / Policy Job / Policy / Robot)
PID_AGENT = 1
PID_TOOL_CALL = 2
PID_POLICY_JOB = 3
PID_POLICY_ROBOT = 4
PID_ENV = 5
PID_VIZTRACER = 6

PROCESS_META = {
    "agent": (PID_AGENT, "Agent Inference"),
    "tool_call": (PID_TOOL_CALL, "Tool Execution"),
    "policy_job": (PID_POLICY_JOB, "Policy Job"),
    "policy_robot": (PID_POLICY_ROBOT, "Policy / Robot"),
    "environment_service": (PID_ENV, "Environment Service"),
    "viztracer_uncalibrated": (PID_VIZTRACER, "VizTracer (Uncalibrated)"),
    "viztracer_calibrated": (PID_VIZTRACER, "VizTracer (Calibrated)"),
}

IGNORED_DIR_NAMES = {
    "_robodojo_runtime",
    "_validation-codex-home",
    "_validation-tools",
    "_empty-memory",
    "_empty-memory-robocasa",
    "_empty-memory-robotwin",
    "__pycache__",
}

ATTEMPT_RE = re.compile(r"^attempt-(\d+)$")


# ---------------------------------------------------------------------------
# Interval algebra (union & intersection; never sum overlapping intervals)
# ---------------------------------------------------------------------------


def union_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Return sorted disjoint union of [start_ns, end_ns] intervals with end > start."""
    valid = sorted((s, e) for s, e in intervals if s is not None and e is not None and e > s)
    if not valid:
        return []
    merged: list[tuple[int, int]] = [valid[0]]
    for s, e in valid[1:]:
        prev_s, prev_e = merged[-1]
        if s <= prev_e:
            if e > prev_e:
                merged[-1] = (prev_s, e)
        else:
            merged.append((s, e))
    return merged


def total_interval_ns(intervals: list[tuple[int, int]]) -> int:
    return sum(e - s for s, e in intervals)


def intersect_intervals(
    a_intervals: list[tuple[int, int]], b_intervals: list[tuple[int, int]]
) -> list[tuple[int, int]]:
    """Return disjoint intersection of two interval sets (computed on their unions)."""
    ua = union_intervals(a_intervals)
    ub = union_intervals(b_intervals)
    out: list[tuple[int, int]] = []
    i = j = 0
    while i < len(ua) and j < len(ub):
        s = max(ua[i][0], ub[j][0])
        e = min(ua[i][1], ub[j][1])
        if s < e:
            out.append((s, e))
        if ua[i][1] < ub[j][1]:
            i += 1
        else:
            j += 1
    return out


def ns_to_s(ns: int | None) -> float | None:
    if ns is None:
        return None
    return round(ns / 1e9, 6)


def s_to_ns(sec: float | None) -> int | None:
    if sec is None:
        return None
    return int(round(sec * 1e9))


# ---------------------------------------------------------------------------
# Safe IO helpers
# ---------------------------------------------------------------------------


def read_json(path: Path) -> Any | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def read_jsonl(path: Path) -> tuple[list[dict[str, Any]], int]:
    """Return (parsed_rows, malformed_line_count)."""
    if not path.is_file():
        return [], 0
    rows: list[dict[str, Any]] = []
    bad = 0
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    rows.append(obj)
                else:
                    bad += 1
            except json.JSONDecodeError:
                bad += 1
    return rows, bad


def is_nonneg_int(v: Any) -> bool:
    return type(v) is int and v >= 0


def safe_float(v: Any) -> float | None:
    if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v):
        return float(v)
    return None


def parse_iso_ts(val: Any) -> float | None:
    if not isinstance(val, str) or not val:
        return None
    try:
        s = val.replace("Z", "+00:00")
        return datetime.datetime.fromisoformat(s).timestamp()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Input discovery
# ---------------------------------------------------------------------------


class EpisodeLocator:
    def __init__(
        self,
        *,
        result_path: Path,
        policy_dir: Path,
        attempt_dir: Path | None,
        run_json_path: Path | None,
        episode_json_path: Path | None,
        suite: str,
        episode_id: str,
        attempt: int,
        run_id: str,
    ) -> None:
        self.result_path = result_path
        self.policy_dir = policy_dir
        self.attempt_dir = attempt_dir
        self.run_json_path = run_json_path
        self.episode_json_path = episode_json_path
        self.suite = suite
        self.episode_id = episode_id
        self.attempt = attempt
        self.run_id = run_id

    @property
    def key(self) -> str:
        return f"{self.suite}__{self.episode_id}__attempt-{self.attempt:02d}"


def _find_attempt_ancestor(policy_dir: Path) -> Path | None:
    for parent in [policy_dir, *policy_dir.parents]:
        if ATTEMPT_RE.match(parent.name):
            return parent
    return None


def _build_locator(result_path: Path, root: Path) -> EpisodeLocator:
    policy_dir = result_path.parent
    attempt_dir = _find_attempt_ancestor(policy_dir)
    run_json_path = (attempt_dir / "run.json") if attempt_dir else None
    if run_json_path and not run_json_path.is_file():
        run_json_path = None
    episode_json_path = (attempt_dir / "episode.json") if attempt_dir else None
    if episode_json_path and not episode_json_path.is_file():
        episode_json_path = None

    run_data = read_json(run_json_path) if run_json_path else None
    ep_data = read_json(episode_json_path) if episode_json_path else None
    res_data = read_json(result_path) or {}

    attempt = 1
    if isinstance(run_data, dict) and isinstance(run_data.get("attempt"), int):
        attempt = run_data["attempt"]
    elif attempt_dir is not None:
        m = ATTEMPT_RE.match(attempt_dir.name)
        if m:
            attempt = int(m.group(1))

    suite = (
        (run_data or {}).get("robot")
        or (ep_data or {}).get("robot")
        or res_data.get("robot")
        or res_data.get("backend")
        or "unknown"
    )

    episode_id = None
    if isinstance(run_data, dict) and run_data.get("id"):
        episode_id = str(run_data["id"])
    elif (
        isinstance(ep_data, dict)
        and isinstance(ep_data.get("episodes"), list)
        and ep_data["episodes"]
    ):
        ep0 = ep_data["episodes"][0]
        if isinstance(ep0, dict) and ep0.get("id"):
            episode_id = str(ep0["id"])
    if not episode_id:
        if attempt_dir is not None:
            episode_id = attempt_dir.parent.name
        else:
            episode_id = policy_dir.name

    run_id = (run_data or {}).get("run_id") or root.name
    return EpisodeLocator(
        result_path=result_path,
        policy_dir=policy_dir,
        attempt_dir=attempt_dir,
        run_json_path=run_json_path,
        episode_json_path=episode_json_path,
        suite=str(suite),
        episode_id=str(episode_id),
        attempt=attempt,
        run_id=str(run_id),
    )


def discover_input(input_path: Path, attempt_policy: str = "latest") -> dict[str, Any]:
    """Discover episodes, batch manifest, summary.json, and excluded attempts."""
    root = input_path.resolve()
    if not root.exists():
        raise FileNotFoundError(f"Input path does not exist: {root}")

    batch_json = read_json(root / "batch.json") if root.is_dir() else None
    summary_json = read_json(root / "summary.json") if root.is_dir() else None

    result_files: list[Path] = []
    if root.is_file() and root.name == "result.json":
        result_files.append(root)
        root = root.parent
    else:
        for p in sorted(root.rglob("result.json")):
            rel_parts = set(p.relative_to(root).parts)
            if rel_parts & IGNORED_DIR_NAMES:
                continue
            result_files.append(p)

    all_locators = [_build_locator(p, root) for p in result_files]

    # Map batch.json selected attempts if present
    batch_selected: dict[tuple[str, str], int] = {}
    if isinstance(batch_json, dict) and isinstance(batch_json.get("episodes"), list):
        for entry in batch_json["episodes"]:
            if not isinstance(entry, dict):
                continue
            ep_id = entry.get("id")
            robot = entry.get("robot")
            att = entry.get("attempt")
            if ep_id and robot and isinstance(att, int):
                batch_selected[(str(robot), str(ep_id))] = att

    selected: list[EpisodeLocator] = []
    excluded: list[dict[str, Any]] = []

    if attempt_policy == "all":
        selected = sorted(all_locators, key=lambda x: (x.suite, x.episode_id, x.attempt))
    else:
        grouped: dict[tuple[str, str], list[EpisodeLocator]] = defaultdict(list)
        for loc in all_locators:
            grouped[(loc.suite, loc.episode_id)].append(loc)
        for key in sorted(grouped.keys()):
            locs = sorted(grouped[key], key=lambda x: x.attempt)
            chosen_att = batch_selected.get(key)
            chosen = None
            if chosen_att is not None:
                for loc in locs:
                    if loc.attempt == chosen_att:
                        chosen = loc
                        break
            if chosen is None:
                chosen = locs[-1]
            selected.append(chosen)
            for loc in locs:
                if loc is not chosen:
                    res = read_json(loc.result_path) or {}
                    run_j = read_json(loc.run_json_path) if loc.run_json_path else {}
                    excluded.append(
                        {
                            "suite": loc.suite,
                            "episode_id": loc.episode_id,
                            "attempt": loc.attempt,
                            "selected_attempt": chosen.attempt,
                            "result_status": res.get("status"),
                            "run_status": (run_j or {}).get("status"),
                            "reason": res.get("reason") or "superseded by later attempt",
                            "result_path": str(loc.result_path),
                        }
                    )

    return {
        "root": root,
        "batch_json": batch_json,
        "summary_json": summary_json,
        "selected": selected,
        "excluded_attempts": excluded,
        "total_discovered_results": len(all_locators),
    }


# ---------------------------------------------------------------------------
# Episode parser -> Unified event model + Perfetto flows + episode metrics
# ---------------------------------------------------------------------------


def _classify_outcome(
    res: dict[str, Any], run_data: dict[str, Any] | None
) -> tuple[str, str | None]:
    """Separate success, capability_failure, timeout, infra_error, unknown."""
    env_ok = res.get("environment_success")
    status = res.get("status")
    reason = res.get("reason")
    run_status = (run_data or {}).get("status")

    if env_ok is True:
        return "success", reason
    if status == "timeout" or run_status == "timeout":
        return "timeout", reason or "timeout"
    if status in {"planner_error", "boot_error", "infra_error", "error"} or run_status in {
        "infra_error",
        "boot_error",
    }:
        return "infra_error", reason or status or run_status
    if env_ok is False:
        return "failure", reason or (status if status not in (None, "completed") else None)
    return "unknown", reason or status or "missing environment_success"


def _extract_codex_session_events(
    session_path: Path,
    base_meta: dict[str, Any],
    next_id: Any,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Optional parser for Codex session JSONL with ISO timestamps."""
    rows, bad = read_jsonl(session_path)
    events: list[dict[str, Any]] = []
    parsed_ts: list[float] = []
    for row in rows:
        ts = parse_iso_ts(row.get("timestamp"))
        if ts is not None:
            parsed_ts.append(ts)
    if not parsed_ts:
        return [], {"status": "no_timestamps", "malformed_lines": bad}

    t0 = min(parsed_ts)
    token_records = 0
    for idx, row in enumerate(rows):
        ts = parse_iso_ts(row.get("timestamp"))
        if ts is None:
            continue
        rel_ns = s_to_ns(ts - t0)
        rtype = str(row.get("type") or "session_event")
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        sub_type = payload.get("type") if isinstance(payload, dict) else None
        if sub_type == "token_count":
            token_records += 1
        events.append(
            {
                **base_meta,
                "event_id": next_id(),
                "process": "policy_runtime",
                "thread": "codex_session",
                "event_type": f"codex_session:{sub_type or rtype}",
                "start_ns": rel_ns,
                "end_ns": rel_ns,
                "parent_id": None,
                "request_id": None,
                "job_id": None,
                "unit_id": None,
                "instance_id": None,
                "status": "ok",
                "clock_domain": "codex_session_iso",
                "source_path": str(session_path),
                "args": {"line_index": idx, "record_type": rtype, "sub_type": sub_type},
            }
        )
    return events, {
        "status": "parsed",
        "events": len(events),
        "token_count_events": token_records,
        "malformed_lines": bad,
        "span_s": round(max(parsed_ts) - t0, 3),
    }


def _discover_codex_sessions(
    policy_dir: Path,
    extra_dirs: list[Path | None],
    thread_ids: Any,
    explicit: Path | None,
) -> list[Path]:
    """Find Codex session JSONL files for one episode, oldest first.

    Codex harnesses store them under ``<episode>/model_sessions/rollout-*.jsonl`` (one file per
    planner attempt); older layouts keep ``rollout-*.jsonl``/``session*.jsonl`` next to
    ``calls.jsonl``. When ``result.json`` lists ``generation.thread_ids`` only matching files
    are used so stale sessions from other runs are never mixed in.
    """
    if explicit is not None:
        return [explicit] if explicit.is_file() else []
    bases: list[Path] = []
    for b in [policy_dir, *extra_dirs]:
        if b is not None and b not in bases:
            bases.append(b)
    found: list[Path] = []
    for base in bases:
        for d in (base / "model_sessions", base):
            if d.is_dir():
                for pat in ("rollout-*.jsonl", "session*.jsonl"):
                    found.extend(sorted(d.glob(pat)))
    found = list(dict.fromkeys(found))
    ids = [t for t in (thread_ids or []) if isinstance(t, str)]
    if ids:
        matched = [f for f in found if any(t in f.name for t in ids)]
        if matched:
            found = matched

    def first_ts(path: Path) -> float:
        rows, _ = read_jsonl(path)
        for row in rows:
            ts = parse_iso_ts(row.get("timestamp"))
            if ts is not None:
                return ts
        return float("inf")

    return sorted(found, key=first_ts)


def _parse_codex_trace(session_paths: list[Path]) -> dict[str, Any] | None:
    """Reconstruct measured per-round model inference and tool execution from Codex sessions.

    Round k is the interval from the previous tool output (or ``task_started``) to the next
    ``function_call``: it is the model inference that chose that call. A tool execution spans
    ``function_call`` -> ``function_call_output``. Failed planner attempts (``task_complete``
    with an error) are reported separately so retry backoff can be drawn between sessions.
    """
    attempts: list[dict[str, Any]] = []
    for path in session_paths:
        rows, _bad = read_jsonl(path)
        recs = [(parse_iso_ts(r.get("timestamp")), r) for r in rows]
        recs = [(t, r) for t, r in recs if t is not None]
        if not recs:
            continue
        start: float | None = None
        end: float | None = None
        error: str | None = None
        round_start: float | None = None
        pending: dict[str, dict[str, Any]] = {}
        rounds: list[dict[str, Any]] = []
        tools: list[dict[str, Any]] = []
        for t, r in recs:
            rtype = r.get("type")
            p = r.get("payload") if isinstance(r.get("payload"), dict) else {}
            pt = p.get("type")
            if rtype == "event_msg" and pt == "task_started" and start is None:
                start = t
                round_start = t
            elif rtype == "event_msg" and pt == "task_complete":
                end = t
                err = p.get("error")
                if err:
                    error = str(err.get("message") if isinstance(err, dict) else err)
            elif rtype == "response_item" and pt == "function_call":
                cid = str(p.get("call_id") or f"call_{len(tools) + len(pending)}")
                name = str(p.get("name") or "tool")
                if round_start is not None:
                    rounds.append({"start": round_start, "end": t, "tool": name, "call_id": cid})
                    round_start = None
                pending[cid] = {"start": t, "tool": name, "call_id": cid}
            elif rtype == "response_item" and pt == "function_call_output":
                call = pending.pop(str(p.get("call_id")), None)
                if call is not None:
                    call["end"] = t
                    tools.append(call)
                if not pending:
                    round_start = t
        if start is None:
            start = recs[0][0]
        last_ts = recs[-1][0]
        completed = end is not None
        if end is None:
            end = last_ts
        for call in pending.values():  # killed mid-call
            call["end"] = end
            call["unfinished"] = True
            tools.append(call)
        attempts.append(
            {
                "path": path,
                "start": start,
                "end": end,
                "completed": completed,
                "error": error,
                "open_round_start": round_start,
                "rounds": rounds,
                "tools": sorted(tools, key=lambda c: c["start"]),
            }
        )
    if not attempts:
        return None
    attempts.sort(key=lambda a: a["start"])
    n_rounds = sum(len(a["rounds"]) for a in attempts)
    first_call = next((c["start"] for a in attempts for c in a["tools"]), None)
    return {
        "t0": attempts[0]["start"],
        "attempts": attempts,
        "first_call_ts": first_call,
        "info": {
            "status": "parsed_rounds",
            "sessions": [a["path"].name for a in attempts],
            "attempts": len(attempts),
            "failed_attempts": sum(1 for a in attempts if a["error"]),
            "tool_rounds": n_rounds,
            "span_s": round(attempts[-1]["end"] - attempts[0]["start"], 3),
        },
    }


def _parse_viztracer(
    viz_path: Path,
    base_meta: dict[str, Any],
    next_id: Any,
    *,
    offset_s: float | None = None,
    max_events: int = 20000,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    data = read_json(viz_path)
    if not isinstance(data, dict) or not isinstance(data.get("traceEvents"), list):
        return [], {"status": "invalid_file", "path": str(viz_path)}

    raw_events = data["traceEvents"]
    valid_slices = [
        ev
        for ev in raw_events
        if isinstance(ev, dict)
        and ev.get("ph") in {"X", "B", "E", "i"}
        and safe_float(ev.get("ts")) is not None
    ]
    if not valid_slices:
        return [], {"status": "empty", "path": str(viz_path)}

    calibrated = offset_s is not None
    clock_domain = "viztracer_calibrated" if calibrated else "viztracer_uncalibrated"
    process_key = "viztracer_calibrated" if calibrated else "viztracer_uncalibrated"

    min_ts_us = min(float(ev["ts"]) for ev in valid_slices)
    truncated = len(valid_slices) > max_events
    chosen = valid_slices[:max_events]
    events: list[dict[str, Any]] = []
    for ev in chosen:
        ts_us = float(ev["ts"])
        dur_us = float(ev.get("dur") or 0.0)
        if calibrated:
            start_s = (ts_us - min_ts_us) / 1e6 + float(offset_s)
        else:
            start_s = (ts_us - min_ts_us) / 1e6
        end_s = start_s + max(0.0, dur_us / 1e6)
        events.append(
            {
                **base_meta,
                "event_id": next_id(),
                "process": process_key,
                "thread": f"py_tid:{ev.get('tid', 0)}",
                "event_type": f"viz:{ev.get('name', 'fn')}",
                "start_ns": s_to_ns(start_s),
                "end_ns": s_to_ns(end_s),
                "parent_id": None,
                "request_id": None,
                "job_id": None,
                "unit_id": None,
                "instance_id": None,
                "status": "ok",
                "clock_domain": clock_domain,
                "source_path": str(viz_path),
                "args": {
                    "viz_pid": ev.get("pid"),
                    "viz_tid": ev.get("tid"),
                    "viz_cat": ev.get("cat"),
                    "episode_id": base_meta["episode_id"],
                    "attempt": base_meta["attempt"],
                    "calibrated": calibrated,
                },
            }
        )
    return events, {
        "status": "attached",
        "path": str(viz_path),
        "clock_domain": clock_domain,
        "calibrated": calibrated,
        "offset_s": offset_s,
        "events_loaded": len(events),
        "total_events_in_file": len(valid_slices),
        "truncated": truncated,
    }


def parse_episode(
    loc: EpisodeLocator,
    *,
    viztracer_path: Path | None = None,
    viztracer_offset_s: float | None = None,
    viztracer_max_events: int = 20000,
    codex_session_path: Path | None = None,
) -> dict[str, Any]:
    """Parse a single episode directory into unified events, flows, and reconciled metrics."""
    res = read_json(loc.result_path) or {}
    run_data = read_json(loc.run_json_path) if loc.run_json_path else None
    gen = res.get("generation") if isinstance(res.get("generation"), dict) else {}
    timing = res.get("timing") if isinstance(res.get("timing"), dict) else {}
    if not timing and isinstance(run_data, dict) and isinstance(run_data.get("timing"), dict):
        timing = run_data["timing"]

    policy_dir = loc.policy_dir
    openai_path = policy_dir / "openai_events.jsonl"
    codex_path = policy_dir / "codex_events.jsonl"
    lifecycle_path = policy_dir / "lifecycle.jsonl"
    calls_path = policy_dir / "calls.jsonl"
    tool_turns_path = policy_dir / "tool_turns.json"
    exec_root = policy_dir / "workspace" / "execution"
    graph_event_files = sorted(exec_root.glob("*/events.jsonl")) if exec_root.is_dir() else []

    openai_rows, openai_bad = read_jsonl(openai_path)
    codex_rows, codex_bad = read_jsonl(codex_path)
    lifecycle_rows, lifecycle_bad = read_jsonl(lifecycle_path)
    calls_rows, calls_bad = read_jsonl(calls_path)
    tool_turns = read_json(tool_turns_path) if tool_turns_path.is_file() else None

    missing_data: list[str] = []
    if openai_bad:
        missing_data.append(f"malformed_openai_events_lines:{openai_bad}")
    if codex_bad:
        missing_data.append(f"malformed_codex_events_lines:{codex_bad}")
    if lifecycle_bad:
        missing_data.append(f"malformed_lifecycle_lines:{lifecycle_bad}")
    if calls_bad:
        missing_data.append(f"malformed_calls_lines:{calls_bad}")

    runtime_name = (
        gen.get("runtime")
        or (run_data or {}).get("settings", {}).get("runtime")
        or ("codex" if codex_path.is_file() else "openai" if openai_path.is_file() else "unknown")
    )
    arm_name = res.get("arm") or (run_data or {}).get("settings", {}).get("arm") or "unknown"
    model_name = (
        res.get("model") or gen.get("model") or (run_data or {}).get("settings", {}).get("model")
    )
    reasoning_effort = res.get("reasoning_effort") or (run_data or {}).get("settings", {}).get(
        "reasoning_effort"
    )

    # Baseline (Codex) harnesses record every model round with ISO timestamps in model_sessions/.
    codex_trace: dict[str, Any] | None = None
    if not openai_rows:
        session_paths = _discover_codex_sessions(
            policy_dir, [loc.attempt_dir], gen.get("thread_ids"), codex_session_path
        )
        if session_paths:
            codex_trace = _parse_codex_trace(session_paths)

    # Determine clock bridge anchor (epoch_t0 corresponding to openai t=0)
    epoch_t0: float | None = None
    clock_bridge_method = "none"
    lc_by_stage = {r.get("stage"): r for r in lifecycle_rows if isinstance(r.get("stage"), str)}

    if openai_rows:
        gen_elapsed = safe_float(gen.get("elapsed_s"))
        msg_fin = lc_by_stage.get("messages_write_finished")
        if msg_fin and safe_float(msg_fin.get("timestamp")) is not None and gen_elapsed is not None:
            epoch_t0 = float(msg_fin["timestamp"]) - gen_elapsed
            clock_bridge_method = "lifecycle_messages_write_anchor"
        elif lifecycle_rows and safe_float(lifecycle_rows[0].get("timestamp")) is not None:
            last_oe_t = safe_float(openai_rows[-1].get("t")) or 0.0
            epoch_t0 = float(lifecycle_rows[0]["timestamp"]) - last_oe_t
            clock_bridge_method = "lifecycle_first_to_openai_last_anchor"
        elif (
            isinstance(run_data, dict)
            and safe_float(run_data.get("started_at")) is not None
            and safe_float(res.get("startup_s")) is not None
        ):
            epoch_t0 = float(run_data["started_at"]) + float(res["startup_s"])
            clock_bridge_method = "run_startup_anchor"
        elif calls_rows and safe_float(calls_rows[0].get("started_at")) is not None:
            # Anchor using first tool call if present
            first_tool = next((r for r in openai_rows if r.get("type") == "tool"), None)
            if first_tool and safe_float(first_tool.get("t")) is not None:
                tool_start_t = float(first_tool["t"]) - float(first_tool.get("elapsed_s") or 0.0)
                epoch_t0 = float(calls_rows[0]["started_at"]) - tool_start_t
                clock_bridge_method = "first_tool_to_calls_anchor"
            else:
                clock_bridge_method = "openai_unbridged_calls"
                missing_data.append("no_clock_bridge_between_openai_and_calls")
    elif codex_trace is not None:
        # t=0 is the first session's task_started, so initial model thinking is on the axis.
        epoch_t0 = float(codex_trace["t0"])
        clock_bridge_method = "codex_session_task_started_anchor"
        first_call_ts = codex_trace.get("first_call_ts")
        if calls_rows and first_call_ts is not None:
            first_call_started = safe_float(calls_rows[0].get("started_at"))
            if first_call_started is not None:
                drift = first_call_started - float(first_call_ts)
                codex_trace["info"]["anchor_check_s"] = round(drift, 3)
                if abs(drift) > 5.0:
                    missing_data.append("codex_session_anchor_drift_over_5s")
    else:
        if calls_rows and safe_float(calls_rows[0].get("started_at")) is not None:
            epoch_t0 = float(calls_rows[0]["started_at"])
            clock_bridge_method = "calls_relative_only"
            missing_data.append("no_rollout_epoch_anchor_using_first_call_as_zero")
        else:
            clock_bridge_method = "no_timestamped_logs"
            missing_data.append("no_timestamped_event_logs")

    ep_clock_domain = (
        "episode_aligned"
        if clock_bridge_method
        in {
            "lifecycle_messages_write_anchor",
            "lifecycle_first_to_openai_last_anchor",
            "run_startup_anchor",
            "first_tool_to_calls_anchor",
        }
        else "codex_session_aligned"
        if clock_bridge_method == "codex_session_task_started_anchor"
        else "calls_epoch_relative"
        if clock_bridge_method == "calls_relative_only"
        else "uncalibrated"
    )

    counter = 0

    def next_id() -> str:
        nonlocal counter
        counter += 1
        return f"ev_{counter:05d}"

    base_meta = {
        "run_id": loc.run_id,
        "episode_id": loc.episode_id,
        "suite": loc.suite,
        "attempt": loc.attempt,
    }

    events: list[dict[str, Any]] = []
    flows: list[dict[str, Any]] = []

    # 1. Runtime rollout & startup envelope
    policy_wall_s = safe_float(res.get("policy_wall_s"))
    startup_s = safe_float(res.get("startup_s"))
    rollout_wall_s = safe_float(timing.get("rollout_wall_time_s"))
    sim_wall_s = safe_float(timing.get("simulator_wall_time_s"))
    rollout_excl_sim_s = safe_float(timing.get("rollout_excluding_sim_s"))
    process_wall_s = safe_float((run_data or {}).get("process_wall_time_s")) or safe_float(
        res.get("total_wall_s")
    )

    if not timing or timing.get("timing_status") != "complete":
        missing_data.append(
            f"timing_unavailable:{timing.get('timing_status', 'missing')}"
            if timing
            else "timing_field_missing"
        )

    envelope_dur_s = rollout_wall_s if rollout_wall_s is not None else policy_wall_s
    if envelope_dur_s is not None and openai_rows:
        events.append(
            {
                **base_meta,
                "event_id": next_id(),
                "process": "policy_runtime",
                "thread": "rollout",
                "event_type": "runtime_rollout",
                "start_ns": 0,
                "end_ns": s_to_ns(envelope_dur_s),
                "parent_id": None,
                "request_id": None,
                "job_id": None,
                "unit_id": None,
                "instance_id": None,
                "status": str(res.get("status") or "unknown"),
                "clock_domain": "episode_aligned",
                "source_path": str(loc.result_path),
                "args": {
                    "arm": arm_name,
                    "runtime": runtime_name,
                    "model": model_name,
                    "reasoning_effort": reasoning_effort,
                    "environment_success": res.get("environment_success"),
                    "startup_s": startup_s,
                    "policy_wall_s": policy_wall_s,
                    "rollout_wall_time_s": rollout_wall_s,
                    "simulator_wall_time_s": sim_wall_s,
                    "rollout_excluding_sim_s": rollout_excl_sim_s,
                },
            }
        )

    # 2. Parse openai_events.jsonl
    http_intervals: list[tuple[int, int]] = []
    http_ok_intervals: list[tuple[int, int]] = []
    http_fail_intervals: list[tuple[int, int]] = []
    http_cancel_intervals: list[tuple[int, int]] = []
    http_requests_total = 0
    http_requests_ok = 0
    http_requests_failed = 0
    http_retry_attempts = 0
    http_requests_cancelled = 0
    http_requests_incomplete = 0
    http_missing_usage = 0
    http_latencies_s: list[float] = []
    http_error_summary: Counter[str] = Counter()

    pending_req: dict[int, dict[str, Any]] = {}
    last_completed_req_ev: dict[str, Any] | None = None
    last_failed_req_end_ns: int | None = None
    http_backoff_intervals: list[tuple[int, int]] = []
    tool_events_by_time: list[dict[str, Any]] = []

    if openai_rows:
        for row in openai_rows:
            rtype = row.get("type")
            t_s = safe_float(row.get("t"))
            if rtype == "request_started":
                req_id = row.get("request_id")
                start_ns_cand = s_to_ns(t_s or 0.0) or 0
                if (
                    last_failed_req_end_ns is not None
                    and start_ns_cand > last_failed_req_end_ns + 50_000_000
                ):
                    http_backoff_intervals.append((last_failed_req_end_ns, start_ns_cand))
                    events.append(
                        {
                            **base_meta,
                            "event_id": next_id(),
                            "process": "provider_request",
                            "thread": "http_retry_failed",
                            "event_type": "model_request_backoff",
                            "start_ns": last_failed_req_end_ns,
                            "end_ns": start_ns_cand,
                            "parent_id": None,
                            "request_id": req_id if isinstance(req_id, int) else None,
                            "job_id": None,
                            "unit_id": None,
                            "instance_id": None,
                            "status": "backoff",
                            "clock_domain": "episode_aligned",
                            "source_path": str(openai_path),
                            "args": {"attempt": row.get("attempt", 1)},
                        }
                    )
                last_failed_req_end_ns = None
                if isinstance(req_id, int):
                    pending_req[req_id] = {
                        "start_s": t_s or 0.0,
                        "attempt": row.get("attempt", 1),
                        "messages": row.get("messages"),
                    }
            elif rtype == "request":
                req_id = row.get("request_id")
                attempt_n = int(row.get("attempt") or 1)
                latency_s = safe_float(row.get("latency_s"))
                end_s = t_s if t_s is not None else 0.0
                started_info = pending_req.pop(req_id, None) if isinstance(req_id, int) else None
                if started_info is not None:
                    start_s = float(started_info["start_s"])
                elif latency_s is not None:
                    start_s = max(0.0, end_s - latency_s)
                else:
                    start_s = end_s
                if latency_s is not None and abs((end_s - start_s) - latency_s) > 0.05:
                    start_s = max(0.0, end_s - latency_s)
                start_ns = s_to_ns(start_s) or 0
                end_ns = max(start_ns, s_to_ns(end_s) or start_ns)

                ok = bool(row.get("ok"))
                status_code = row.get("status_code")
                err = row.get("error")
                raw_usage = row.get("usage") if isinstance(row.get("usage"), dict) else {}
                p_tok = raw_usage.get("prompt_tokens")
                c_tok = raw_usage.get("completion_tokens")
                cached_tok = (raw_usage.get("prompt_tokens_details") or {}).get("cached_tokens")
                reason_tok = (raw_usage.get("completion_tokens_details") or {}).get(
                    "reasoning_tokens"
                )
                usage_present = is_nonneg_int(p_tok) and is_nonneg_int(c_tok)

                http_requests_total += 1
                if attempt_n > 1:
                    http_retry_attempts += 1
                if not usage_present:
                    http_missing_usage += 1
                if latency_s is not None:
                    http_latencies_s.append(latency_s)
                else:
                    http_latencies_s.append((end_ns - start_ns) / 1e9)

                if ok:
                    http_requests_ok += 1
                    ev_type = "model_request_retry" if attempt_n > 1 else "model_request"
                    thread = "http_retry_failed" if attempt_n > 1 else "http_ok"
                    ev_status = "retry_ok" if attempt_n > 1 else "ok"
                    http_ok_intervals.append((start_ns, end_ns))
                else:
                    http_requests_failed += 1
                    ev_type = "model_request_failed"
                    thread = "http_retry_failed"
                    ev_status = "failed"
                    http_fail_intervals.append((start_ns, end_ns))
                    err_key = f"HTTP {status_code}" if status_code else "transport_error"
                    http_error_summary[err_key] += 1
                http_intervals.append((start_ns, end_ns))

                ev_obj = {
                    **base_meta,
                    "event_id": next_id(),
                    "process": "provider_request",
                    "thread": thread,
                    "event_type": ev_type,
                    "start_ns": start_ns,
                    "end_ns": end_ns,
                    "parent_id": None,
                    "request_id": req_id if isinstance(req_id, int) else None,
                    "job_id": None,
                    "unit_id": None,
                    "instance_id": None,
                    "status": ev_status,
                    "clock_domain": "episode_aligned",
                    "source_path": str(openai_path),
                    "args": {
                        "model": model_name,
                        "reasoning_effort": reasoning_effort,
                        "attempt": attempt_n,
                        "status_code": status_code,
                        "latency_s": latency_s,
                        "messages": row.get("messages"),
                        "usage_present": usage_present,
                        "prompt_tokens": p_tok if is_nonneg_int(p_tok) else None,
                        "completion_tokens": c_tok if is_nonneg_int(c_tok) else None,
                        "cached_tokens": cached_tok if is_nonneg_int(cached_tok) else None,
                        "reasoning_tokens": reason_tok if is_nonneg_int(reason_tok) else None,
                        "error": str(err)[:300] if err else None,
                    },
                }
                events.append(ev_obj)
                if ok:
                    last_completed_req_ev = ev_obj
                    last_failed_req_end_ns = None
                else:
                    last_failed_req_end_ns = end_ns
            elif rtype == "request_cancelled":
                req_id = row.get("request_id")
                attempt_n = int(row.get("attempt") or 1)
                latency_s = safe_float(row.get("latency_s")) or 0.0
                end_s = t_s if t_s is not None else 0.0
                started_info = pending_req.pop(req_id, None) if isinstance(req_id, int) else None
                start_s = (
                    float(started_info["start_s"]) if started_info else max(0.0, end_s - latency_s)
                )
                start_ns = s_to_ns(start_s) or 0
                end_ns = max(start_ns, s_to_ns(end_s) or start_ns)

                http_requests_total += 1
                http_requests_cancelled += 1
                http_missing_usage += 1
                if attempt_n > 1:
                    http_retry_attempts += 1
                http_intervals.append((start_ns, end_ns))
                http_cancel_intervals.append((start_ns, end_ns))
                http_latencies_s.append((end_ns - start_ns) / 1e9)
                http_error_summary[f"cancelled:{row.get('reason', 'unknown')}"] += 1

                events.append(
                    {
                        **base_meta,
                        "event_id": next_id(),
                        "process": "provider_request",
                        "thread": "http_cancelled",
                        "event_type": "model_request_cancelled",
                        "start_ns": start_ns,
                        "end_ns": end_ns,
                        "parent_id": None,
                        "request_id": req_id if isinstance(req_id, int) else None,
                        "job_id": None,
                        "unit_id": None,
                        "instance_id": None,
                        "status": "cancelled",
                        "clock_domain": "episode_aligned",
                        "source_path": str(openai_path),
                        "args": {
                            "model": model_name,
                            "attempt": attempt_n,
                            "latency_s": latency_s,
                            "usage_present": False,
                            "reason": row.get("reason"),
                        },
                    }
                )
            elif rtype == "assistant":
                ts_ns = s_to_ns(t_s or 0.0) or 0
                if last_completed_req_ev is not None:
                    last_completed_req_ev["args"]["triggered_tools"] = row.get("tool_calls") or []
                events.append(
                    {
                        **base_meta,
                        "event_id": next_id(),
                        "process": "policy_runtime",
                        "thread": "assistant",
                        "event_type": "assistant_reply",
                        "start_ns": ts_ns,
                        "end_ns": ts_ns,
                        "parent_id": last_completed_req_ev["event_id"]
                        if last_completed_req_ev
                        else None,
                        "request_id": last_completed_req_ev["request_id"]
                        if last_completed_req_ev
                        else None,
                        "job_id": None,
                        "unit_id": None,
                        "instance_id": None,
                        "status": str(row.get("finish_reason") or "ok"),
                        "clock_domain": "episode_aligned",
                        "source_path": str(openai_path),
                        "args": {
                            "tool_calls": row.get("tool_calls"),
                            "text_chars": row.get("text_chars"),
                            "reasoning_chars": row.get("reasoning_chars"),
                            "finish_reason": row.get("finish_reason"),
                        },
                    }
                )
            elif rtype == "tool":
                elapsed_s = safe_float(row.get("elapsed_s")) or 0.0
                end_s = t_s if t_s is not None else 0.0
                start_s = max(0.0, end_s - elapsed_s)
                start_ns = s_to_ns(start_s) or 0
                end_ns = max(start_ns, s_to_ns(end_s) or start_ns)
                ev_obj = {
                    **base_meta,
                    "event_id": next_id(),
                    "process": "policy_runtime",
                    "thread": "tool_dispatch",
                    "event_type": f"tool_dispatch:{row.get('tool', 'unknown')}",
                    "start_ns": start_ns,
                    "end_ns": end_ns,
                    "parent_id": last_completed_req_ev["event_id"]
                    if last_completed_req_ev
                    else None,
                    "request_id": last_completed_req_ev["request_id"]
                    if last_completed_req_ev
                    else None,
                    "job_id": None,
                    "unit_id": None,
                    "instance_id": None,
                    "status": "ok" if row.get("ok") else "error",
                    "clock_domain": "episode_aligned",
                    "source_path": str(openai_path),
                    "args": {
                        "tool": row.get("tool"),
                        "call_id": row.get("call_id"),
                        "elapsed_s": elapsed_s,
                        "images": row.get("images"),
                        "terminated": row.get("terminated"),
                    },
                }
                events.append(ev_obj)
                tool_events_by_time.append(ev_obj)
                if last_completed_req_ev is not None:
                    flows.append(
                        {
                            "from_event": last_completed_req_ev,
                            "to_event": ev_obj,
                            "cat": "request_to_tool",
                            "name": f"req_{last_completed_req_ev['request_id']}_to_{row.get('tool')}",
                        }
                    )

        # Unfinished request_started records
        for req_id, info in sorted(pending_req.items()):
            http_requests_total += 1
            http_requests_incomplete += 1
            http_missing_usage += 1
            start_ns = s_to_ns(float(info["start_s"])) or 0
            end_ns = max(start_ns, s_to_ns(envelope_dur_s) or start_ns)
            missing_data.append(f"incomplete_http_request:{req_id}")
            events.append(
                {
                    **base_meta,
                    "event_id": next_id(),
                    "process": "provider_request",
                    "thread": "http_retry_failed",
                    "event_type": "model_request_incomplete",
                    "start_ns": start_ns,
                    "end_ns": end_ns,
                    "parent_id": None,
                    "request_id": req_id,
                    "job_id": None,
                    "unit_id": None,
                    "instance_id": None,
                    "status": "unknown",
                    "clock_domain": "episode_aligned",
                    "source_path": str(openai_path),
                    "args": {"attempt": info.get("attempt"), "usage_present": False},
                }
            )
    elif codex_rows:
        if codex_trace is None:
            missing_data.append("codex_events_no_per_request_timestamps")
        codex_tool_count = 0
        codex_errors = 0
        for idx, row in enumerate(codex_rows):
            ctype = str(row.get("type") or "")
            item = row.get("item") if isinstance(row.get("item"), dict) else {}
            if ctype == "item.completed" and item.get("type") == "mcp_tool_call":
                codex_tool_count += 1
            if ctype in {"error", "turn.failed"} or item.get("error"):
                codex_errors += 1
            events.append(
                {
                    **base_meta,
                    "event_id": next_id(),
                    "process": "policy_runtime",
                    "thread": "codex_uncalibrated",
                    "event_type": f"codex:{ctype}"
                    + (f":{item.get('type')}" if item.get("type") else ""),
                    "start_ns": None,
                    "end_ns": None,
                    "parent_id": None,
                    "request_id": None,
                    "job_id": None,
                    "unit_id": None,
                    "instance_id": None,
                    "status": str(item.get("status") or ("error" if ctype == "error" else "ok")),
                    "clock_domain": "uncalibrated_sequence",
                    "source_path": str(codex_path),
                    "args": {
                        "seq": idx,
                        "item_id": item.get("id"),
                        "tool": item.get("tool"),
                        "usage": row.get("usage"),
                        "error": item.get("error") or row.get("error"),
                    },
                }
            )
    else:
        missing_data.append("missing_model_event_log")

    # Optional Codex session file (explicit or auto-discovered in policy_dir)
    codex_session_info: dict[str, Any] | None = None
    candidate_session = codex_session_path
    if codex_trace is not None:
        codex_session_info = codex_trace["info"]
        candidate_session = None
    elif candidate_session is None and codex_rows:
        for pat in ("rollout-*.jsonl", "session*.jsonl"):
            found = sorted(policy_dir.glob(pat))
            if found:
                candidate_session = found[0]
                break
    if candidate_session is not None and candidate_session.is_file():
        sess_events, codex_session_info = _extract_codex_session_events(
            candidate_session, base_meta, next_id
        )
        events.extend(sess_events)

    # 3. Parse lifecycle.jsonl
    lifecycle_durations_s: dict[str, float] = {}
    if lifecycle_rows and epoch_t0 is not None:
        open_stages: dict[str, dict[str, Any]] = {}
        for row in lifecycle_rows:
            stage = str(row.get("stage") or "")
            ts = safe_float(row.get("timestamp"))
            if not stage or ts is None:
                continue
            if stage.endswith("_started"):
                stem = stage[: -len("_started")]
                open_stages[stem] = row
            elif stage.endswith("_finished"):
                stem = stage[: -len("_finished")]
                st_row = open_stages.pop(stem, None)
                start_ts = safe_float(st_row.get("timestamp")) if st_row else ts
                start_ns = s_to_ns(start_ts - epoch_t0) or 0
                end_ns = max(start_ns, s_to_ns(ts - epoch_t0) or start_ns)
                lifecycle_durations_s[stem] = round((end_ns - start_ns) / 1e9, 6)
                events.append(
                    {
                        **base_meta,
                        "event_id": next_id(),
                        "process": "policy_runtime",
                        "thread": "lifecycle",
                        "event_type": f"lifecycle:{stem}",
                        "start_ns": start_ns,
                        "end_ns": end_ns,
                        "parent_id": None,
                        "request_id": None,
                        "job_id": None,
                        "unit_id": None,
                        "instance_id": None,
                        "status": "ok" if row.get("drained", True) else "incomplete_drain",
                        "clock_domain": ep_clock_domain,
                        "source_path": str(lifecycle_path),
                        "args": {k: v for k, v in row.items() if k not in {"stage", "graph"}},
                    }
                )
    elif not lifecycle_path.is_file() and arm_name == "graph":
        missing_data.append("missing_lifecycle_jsonl")

    # 4. Parse Graph workspace/execution/<job_id>/events.jsonl
    graph_unit_intervals: list[tuple[int, int]] = []
    graph_action_intervals: list[tuple[int, int]] = []
    graph_decision_wait_intervals: list[tuple[int, int]] = []
    graph_pause_intervals: list[tuple[int, int]] = []
    graph_action_events: list[dict[str, Any]] = []
    graph_stats = {
        "jobs": 0,
        "units": 0,
        "actions": 0,
        "decision_waits": 0,
        "pauses": 0,
        "revisions": 0,
        "resumes": 0,
        "cancellations": 0,
        "errors": 0,
        "drained": (res.get("graph") or {}).get("drained")
        if isinstance(res.get("graph"), dict)
        else None,
    }
    used_start_tools: set[str] = set()

    for gpath in graph_event_files:
        grows, gbad = read_jsonl(gpath)
        if gbad:
            missing_data.append(f"malformed_graph_events:{gpath.parent.name}:{gbad}")
        if not grows:
            continue
        grows.sort(key=lambda r: (r.get("event_seq") or 0, r.get("timestamp") or 0.0))
        job_id = str(grows[0].get("job_id") or gpath.parent.name)
        short_job = job_id[:8]
        graph_stats["jobs"] += 1

        ts_list = [safe_float(r.get("timestamp")) for r in grows]
        valid_ts = [t for t in ts_list if t is not None]
        if not valid_ts or epoch_t0 is None:
            missing_data.append(f"graph_job_missing_clock:{short_job}")
            continue

        job_start_ns = s_to_ns(min(valid_ts) - epoch_t0) or 0
        job_end_ns = max(job_start_ns, s_to_ns(max(valid_ts) - epoch_t0) or job_start_ns)
        job_status = "completed"
        if any(r.get("kind") == "cancelled" for r in grows):
            job_status = "cancelled"
        elif any(r.get("kind") == "error" for r in grows) and not any(
            r.get("kind") == "completed" for r in grows
        ):
            job_status = "error"

        # Match with triggering python_start tool dispatch
        parent_tool_ev = None
        for tev in tool_events_by_time:
            if tev["event_id"] in used_start_tools:
                continue
            if tev["args"].get("tool") in {"python_start", "start_graph", "python"}:
                if abs(tev["end_ns"] - job_start_ns) <= 3_000_000_000:
                    parent_tool_ev = tev
                    used_start_tools.add(tev["event_id"])
                    break

        job_ev = {
            **base_meta,
            "event_id": next_id(),
            "process": "graph_manager",
            "thread": "jobs",
            "event_type": f"graph_job:{short_job}",
            "start_ns": job_start_ns,
            "end_ns": job_end_ns,
            "parent_id": parent_tool_ev["event_id"] if parent_tool_ev else None,
            "request_id": parent_tool_ev["request_id"] if parent_tool_ev else None,
            "job_id": job_id,
            "unit_id": None,
            "instance_id": None,
            "status": job_status,
            "clock_domain": ep_clock_domain,
            "source_path": str(gpath),
            "args": {"events": len(grows), "job_id": job_id},
        }
        events.append(job_ev)
        if parent_tool_ev is not None:
            flows.append(
                {
                    "from_event": parent_tool_ev,
                    "to_event": job_ev,
                    "cat": "tool_to_graph_job",
                    "name": f"start_{short_job}",
                }
            )

        open_units: dict[tuple[str | None, int | None], dict[str, Any]] = {}
        open_decisions: dict[str, dict[str, Any]] = {}
        open_pause_ts: float | None = None

        for row in grows:
            kind = str(row.get("kind") or "")
            ts = safe_float(row.get("timestamp"))
            if ts is None:
                continue
            rel_ns = s_to_ns(ts - epoch_t0) or 0
            u_id = row.get("unit_id")
            inst_id = row.get("instance_id") if isinstance(row.get("instance_id"), int) else None
            plan_rev = row.get("plan_revision")
            ev_seq = row.get("event_seq")

            if kind == "unit_started":
                open_units[(u_id, inst_id)] = {
                    "start_ns": rel_ns,
                    "primitive": row.get("primitive"),
                    "plan_revision": plan_rev,
                    "event_seq": ev_seq,
                }
            elif kind == "action_completed":
                elapsed_s = safe_float(row.get("elapsed_s")) or 0.0
                act_end_ns = rel_ns
                act_start_ns = max(job_start_ns, act_end_ns - (s_to_ns(elapsed_s) or 0))
                u_info = open_units.get((u_id, inst_id)) or {}
                prim = u_info.get("primitive") or "action"
                graph_stats["actions"] += 1
                graph_action_intervals.append((act_start_ns, act_end_ns))
                act_ev = {
                    **base_meta,
                    "event_id": next_id(),
                    "process": "graph_worker",
                    "thread": f"job:{short_job}",
                    "event_type": f"graph_action:{u_id or 'unit'}:{prim}",
                    "start_ns": act_start_ns,
                    "end_ns": act_end_ns,
                    "parent_id": job_ev["event_id"],
                    "request_id": job_ev["request_id"],
                    "job_id": job_id,
                    "unit_id": u_id,
                    "instance_id": inst_id,
                    "status": "ok",
                    "clock_domain": ep_clock_domain,
                    "source_path": str(gpath),
                    "args": {
                        "primitive": prim,
                        "elapsed_s": elapsed_s,
                        "env_steps": row.get("env_steps"),
                        "plan_revision": plan_rev,
                        "event_seq": ev_seq,
                    },
                }
                events.append(act_ev)
                graph_action_events.append(act_ev)
            elif kind == "unit_completed":
                u_info = open_units.pop((u_id, inst_id), None)
                u_start = u_info["start_ns"] if u_info else rel_ns
                u_end = max(u_start, rel_ns)
                graph_stats["units"] += 1
                graph_unit_intervals.append((u_start, u_end))
                events.append(
                    {
                        **base_meta,
                        "event_id": next_id(),
                        "process": "graph_worker",
                        "thread": f"job:{short_job}",
                        "event_type": f"graph_unit:{u_id or 'unit'}",
                        "start_ns": u_start,
                        "end_ns": u_end,
                        "parent_id": job_ev["event_id"],
                        "request_id": job_ev["request_id"],
                        "job_id": job_id,
                        "unit_id": u_id,
                        "instance_id": inst_id,
                        "status": "completed",
                        "clock_domain": ep_clock_domain,
                        "source_path": str(gpath),
                        "args": {
                            "primitive": (u_info or {}).get("primitive"),
                            "plan_revision": plan_rev,
                            "transition": (row.get("transition") or {}).get("kind")
                            if isinstance(row.get("transition"), dict)
                            else None,
                            "event_seq": ev_seq,
                        },
                    }
                )
            elif kind in {"waiting_decision", "decision_requested"}:
                dec_id = row.get("decision_id")
                if not dec_id and isinstance(row.get("decision"), dict):
                    dec_id = row["decision"].get("id")
                if dec_id and dec_id not in open_decisions:
                    open_decisions[str(dec_id)] = {
                        "start_ns": rel_ns,
                        "unit_id": u_id,
                        "instance_id": inst_id,
                    }
            elif kind in {"decision_resolved", "decision_invalidated"}:
                dec_id = str(row.get("decision_id") or "")
                d_info = open_decisions.pop(dec_id, None)
                if d_info is not None:
                    d_start = d_info["start_ns"]
                    d_end = max(d_start, rel_ns)
                    graph_stats["decision_waits"] += 1
                    graph_decision_wait_intervals.append((d_start, d_end))
                    events.append(
                        {
                            **base_meta,
                            "event_id": next_id(),
                            "process": "graph_manager",
                            "thread": "decisions_and_control",
                            "event_type": f"decision_wait:{kind}",
                            "start_ns": d_start,
                            "end_ns": d_end,
                            "parent_id": job_ev["event_id"],
                            "request_id": None,
                            "job_id": job_id,
                            "unit_id": d_info.get("unit_id"),
                            "instance_id": d_info.get("instance_id"),
                            "status": "resolved" if kind == "decision_resolved" else "invalidated",
                            "clock_domain": ep_clock_domain,
                            "source_path": str(gpath),
                            "args": {
                                "decision_id": dec_id,
                                "choice": row.get("choice"),
                                "event_seq": ev_seq,
                            },
                        }
                    )
            elif kind == "pause_requested":
                graph_stats["pauses"] += 1
                if open_pause_ts is None:
                    open_pause_ts = ts
                events.append(
                    {
                        **base_meta,
                        "event_id": next_id(),
                        "process": "graph_manager",
                        "thread": "decisions_and_control",
                        "event_type": "pause_requested",
                        "start_ns": rel_ns,
                        "end_ns": rel_ns,
                        "parent_id": job_ev["event_id"],
                        "request_id": None,
                        "job_id": job_id,
                        "unit_id": u_id,
                        "instance_id": inst_id,
                        "status": "paused",
                        "clock_domain": ep_clock_domain,
                        "source_path": str(gpath),
                        "args": {"plan_revision": plan_rev, "event_seq": ev_seq},
                    }
                )
            elif kind == "resumed":
                graph_stats["resumes"] += 1
                if open_pause_ts is not None:
                    p_start = s_to_ns(open_pause_ts - epoch_t0) or 0
                    p_end = max(p_start, rel_ns)
                    graph_pause_intervals.append((p_start, p_end))
                    events.append(
                        {
                            **base_meta,
                            "event_id": next_id(),
                            "process": "graph_manager",
                            "thread": "decisions_and_control",
                            "event_type": "pause_interval",
                            "start_ns": p_start,
                            "end_ns": p_end,
                            "parent_id": job_ev["event_id"],
                            "request_id": None,
                            "job_id": job_id,
                            "unit_id": u_id,
                            "instance_id": inst_id,
                            "status": "resumed",
                            "clock_domain": ep_clock_domain,
                            "source_path": str(gpath),
                            "args": {"plan_revision": plan_rev, "event_seq": ev_seq},
                        }
                    )
                    open_pause_ts = None
            elif kind == "graph_patched":
                graph_stats["revisions"] += 1
                events.append(
                    {
                        **base_meta,
                        "event_id": next_id(),
                        "process": "graph_manager",
                        "thread": "decisions_and_control",
                        "event_type": f"graph_patched:rev{plan_rev}",
                        "start_ns": rel_ns,
                        "end_ns": rel_ns,
                        "parent_id": job_ev["event_id"],
                        "request_id": None,
                        "job_id": job_id,
                        "unit_id": u_id,
                        "instance_id": inst_id,
                        "status": "patched",
                        "clock_domain": ep_clock_domain,
                        "source_path": str(gpath),
                        "args": {
                            "plan_revision": plan_rev,
                            "changed": row.get("changed"),
                            "event_seq": ev_seq,
                        },
                    }
                )
            elif kind == "cancelled":
                graph_stats["cancellations"] += 1
                events.append(
                    {
                        **base_meta,
                        "event_id": next_id(),
                        "process": "graph_manager",
                        "thread": "decisions_and_control",
                        "event_type": "cancelled",
                        "start_ns": rel_ns,
                        "end_ns": rel_ns,
                        "parent_id": job_ev["event_id"],
                        "request_id": None,
                        "job_id": job_id,
                        "unit_id": u_id,
                        "instance_id": inst_id,
                        "status": "cancelled",
                        "clock_domain": ep_clock_domain,
                        "source_path": str(gpath),
                        "args": {"plan_revision": plan_rev, "event_seq": ev_seq},
                    }
                )
                if open_pause_ts is not None:
                    p_start = s_to_ns(open_pause_ts - epoch_t0) or 0
                    p_end = max(p_start, rel_ns)
                    graph_pause_intervals.append((p_start, p_end))
                    open_pause_ts = None
            elif kind == "error":
                graph_stats["errors"] += 1
                events.append(
                    {
                        **base_meta,
                        "event_id": next_id(),
                        "process": "graph_worker",
                        "thread": f"job:{short_job}",
                        "event_type": f"error:{u_id or 'job'}",
                        "start_ns": rel_ns,
                        "end_ns": rel_ns,
                        "parent_id": job_ev["event_id"],
                        "request_id": None,
                        "job_id": job_id,
                        "unit_id": u_id,
                        "instance_id": inst_id,
                        "status": "error",
                        "clock_domain": ep_clock_domain,
                        "source_path": str(gpath),
                        "args": {
                            "error": str(row.get("error") or "")[:300],
                            "recovery": row.get("recovery"),
                            "event_seq": ev_seq,
                        },
                    }
                )

        # Close any unclosed units/decisions at job_end_ns
        for (u_id, inst_id), u_info in open_units.items():
            u_start = u_info["start_ns"]
            u_end = max(u_start, job_end_ns)
            graph_stats["units"] += 1
            graph_unit_intervals.append((u_start, u_end))
            events.append(
                {
                    **base_meta,
                    "event_id": next_id(),
                    "process": "graph_worker",
                    "thread": f"job:{short_job}",
                    "event_type": f"graph_unit:{u_id or 'unit'}",
                    "start_ns": u_start,
                    "end_ns": u_end,
                    "parent_id": job_ev["event_id"],
                    "request_id": job_ev["request_id"],
                    "job_id": job_id,
                    "unit_id": u_id,
                    "instance_id": inst_id,
                    "status": job_status,
                    "clock_domain": ep_clock_domain,
                    "source_path": str(gpath),
                    "args": {"primitive": u_info.get("primitive"), "unclosed": True},
                }
            )
        for dec_id, d_info in open_decisions.items():
            d_start = d_info["start_ns"]
            d_end = max(d_start, job_end_ns)
            graph_stats["decision_waits"] += 1
            graph_decision_wait_intervals.append((d_start, d_end))
            events.append(
                {
                    **base_meta,
                    "event_id": next_id(),
                    "process": "graph_manager",
                    "thread": "decisions_and_control",
                    "event_type": "decision_wait:unclosed",
                    "start_ns": d_start,
                    "end_ns": d_end,
                    "parent_id": job_ev["event_id"],
                    "request_id": None,
                    "job_id": job_id,
                    "unit_id": d_info.get("unit_id"),
                    "instance_id": d_info.get("instance_id"),
                    "status": job_status,
                    "clock_domain": ep_clock_domain,
                    "source_path": str(gpath),
                    "args": {"decision_id": dec_id, "unclosed": True},
                }
            )

    # 5. Parse calls.jsonl -> robot_backend
    robot_stateful_intervals: list[tuple[int, int]] = []
    robot_readonly_intervals: list[tuple[int, int]] = []
    matched_graph_actions: set[str] = set()

    if calls_rows and epoch_t0 is not None:
        for row in calls_rows:
            st = safe_float(row.get("started_at"))
            el = safe_float(row.get("elapsed_s")) or 0.0
            if st is None:
                continue
            start_ns = s_to_ns(st - epoch_t0) or 0
            end_ns = max(start_ns, start_ns + (s_to_ns(el) or 0))
            stateful = bool(row.get("stateful"))
            tool = str(row.get("tool") or "unknown")
            if stateful:
                robot_stateful_intervals.append((start_ns, end_ns))
            else:
                robot_readonly_intervals.append((start_ns, end_ns))

            # Link stateful call back to graph_action when aligned & overlapping
            linked_action = None
            if stateful and ep_clock_domain == "episode_aligned":
                for ga in graph_action_events:
                    if ga["event_id"] in matched_graph_actions:
                        continue
                    prim = ga["args"].get("primitive")
                    if (
                        prim == tool
                        and max(ga["start_ns"], start_ns) <= min(ga["end_ns"], end_ns) + 100_000_000
                    ):
                        linked_action = ga
                        matched_graph_actions.add(ga["event_id"])
                        break

            call_ev = {
                **base_meta,
                "event_id": next_id(),
                "process": "robot_backend",
                "thread": "stateful_calls" if stateful else "readonly_calls",
                "event_type": f"robot_call:{tool}",
                "start_ns": start_ns,
                "end_ns": end_ns,
                "parent_id": linked_action["event_id"] if linked_action else None,
                "request_id": linked_action["request_id"] if linked_action else None,
                "job_id": linked_action["job_id"] if linked_action else None,
                "unit_id": linked_action["unit_id"] if linked_action else None,
                "instance_id": linked_action["instance_id"] if linked_action else None,
                "status": "ok" if row.get("ok", True) else "error",
                "clock_domain": ep_clock_domain,
                "source_path": str(calls_path),
                "args": {
                    "call_index": row.get("index"),
                    "tool": tool,
                    "stateful": stateful,
                    "elapsed_s": el,
                    "env_steps": row.get("env_steps"),
                    "error": row.get("error"),
                },
            }
            events.append(call_ev)
            if linked_action is not None:
                flows.append(
                    {
                        "from_event": linked_action,
                        "to_event": call_ev,
                        "cat": "graph_action_to_robot",
                        "name": f"{tool}_{row.get('index')}",
                    }
                )
    elif not calls_path.is_file():
        missing_data.append("missing_calls_jsonl")

    # 6. Environment service aggregate timing intervals
    if isinstance(timing.get("intervals"), list) and timing["intervals"]:
        cursor_ns = 0
        for idx, itv in enumerate(timing["intervals"]):
            if not isinstance(itv, dict):
                continue
            w_ns = itv.get("wall_ns")
            s_ns = itv.get("sim_ns")
            if not is_nonneg_int(w_ns):
                continue
            events.append(
                {
                    **base_meta,
                    "event_id": next_id(),
                    "process": "environment_service",
                    "thread": "env_timing_intervals",
                    "event_type": f"env_timing_interval:{idx}",
                    "start_ns": cursor_ns,
                    "end_ns": cursor_ns + w_ns,
                    "parent_id": None,
                    "request_id": None,
                    "job_id": None,
                    "unit_id": None,
                    "instance_id": None,
                    "status": str(timing.get("timing_status") or "unknown"),
                    "clock_domain": "episode_aligned" if openai_rows else "timing_duration_only",
                    "source_path": str(loc.result_path),
                    "args": {
                        "timing_source": timing.get("source"),
                        "wall_ns": w_ns,
                        "sim_ns": s_ns,
                        "sim_s": ns_to_s(s_ns) if is_nonneg_int(s_ns) else None,
                        "server_id": (itv.get("start_snapshot") or {}).get("server_id"),
                        "is_aggregate": True,
                    },
                }
            )
            cursor_ns += w_ns

    # 7. Optional VizTracer attachment
    viz_info: dict[str, Any] = {"status": "not_provided"}
    if viztracer_path is not None:
        viz_events, viz_info = _parse_viztracer(
            viztracer_path,
            base_meta,
            next_id,
            offset_s=viztracer_offset_s,
            max_events=viztracer_max_events,
        )
        events.extend(viz_events)

    # 8. Compute union / critical path / overlap metrics (NEVER sum overlapping intervals!)
    http_cum_ns = sum(e - s for s, e in http_intervals) if http_intervals else None
    http_union = union_intervals(http_intervals)
    http_crit_ns = total_interval_ns(http_union) if http_intervals else None
    http_ok_union_ns = (
        total_interval_ns(union_intervals(http_ok_intervals)) if http_intervals else None
    )
    http_fail_union_ns = (
        total_interval_ns(union_intervals(http_fail_intervals)) if http_intervals else None
    )
    http_cancel_union_ns = (
        total_interval_ns(union_intervals(http_cancel_intervals)) if http_intervals else None
    )

    robot_source_intervals = robot_stateful_intervals or graph_action_intervals
    robot_union = union_intervals(robot_source_intervals)
    robot_union_ns = (
        total_interval_ns(robot_union) if robot_source_intervals else (0 if calls_rows else None)
    )
    robot_readonly_union_ns = (
        total_interval_ns(union_intervals(robot_readonly_intervals))
        if robot_readonly_intervals
        else (0 if calls_rows else None)
    )
    graph_unit_union_ns = (
        total_interval_ns(union_intervals(graph_unit_intervals)) if graph_unit_intervals else None
    )
    graph_action_union_ns = (
        total_interval_ns(union_intervals(graph_action_intervals))
        if graph_action_intervals
        else None
    )
    graph_dec_wait_union_ns = (
        total_interval_ns(union_intervals(graph_decision_wait_intervals))
        if graph_decision_wait_intervals
        else 0
    )
    graph_pause_union_ns = (
        total_interval_ns(union_intervals(graph_pause_intervals)) if graph_pause_intervals else 0
    )

    # Overlap only valid when HTTP and robot/graph share the same aligned clock domain
    if http_intervals and ep_clock_domain == "episode_aligned":
        http_robot_overlap_ns = total_interval_ns(
            intersect_intervals(http_intervals, robot_source_intervals)
        )
        http_or_robot_union_ns = total_interval_ns(
            union_intervals(http_intervals + robot_source_intervals)
        )
        http_graph_overlap_ns = (
            total_interval_ns(intersect_intervals(http_intervals, graph_unit_intervals))
            if graph_unit_intervals
            else 0
        )
    else:
        http_robot_overlap_ns = None
        http_or_robot_union_ns = None
        http_graph_overlap_ns = None

    # 8b. Emit synthetic Pipeline State track (parallel overlap vs HTTP/wait_event/retry bubbles)
    if http_intervals and ep_clock_domain == "episode_aligned":
        robot_u = union_intervals(robot_source_intervals)
        req_evs = [
            e for e in events if e["process"] == "provider_request" and e["start_ns"] is not None
        ]
        for rev in req_evs:
            rs, re_ = int(rev["start_ns"]), int(rev["end_ns"])
            if re_ <= rs:
                continue
            rtype = rev["event_type"]
            tools = (rev.get("args") or {}).get("triggered_tools") or []
            if rtype in {
                "model_request_failed",
                "model_request_backoff",
                "model_request_cancelled",
            }:
                base_kind = "http_failed_backoff"
            elif tools == ["wait_event"]:
                base_kind = "http_wait_event"
            elif any(t in {"python_start", "python", "start_graph"} for t in tools):
                base_kind = "http_python_start"
            else:
                base_kind = "http_control_finish"

            # Split this HTTP interval by robot_u to highlight exact HTTP ∥ Robot parallel overlap
            overlaps = intersect_intervals([(rs, re_)], robot_u)
            cur = rs
            for os_, oe_ in overlaps:
                if os_ > cur:
                    events.append(
                        {
                            **base_meta,
                            "event_id": next_id(),
                            "process": "pipeline_state",
                            "thread": "pipeline",
                            "event_type": f"pipeline:{base_kind}",
                            "start_ns": cur,
                            "end_ns": os_,
                            "parent_id": rev["event_id"],
                            "request_id": rev["request_id"],
                            "job_id": None,
                            "unit_id": None,
                            "instance_id": None,
                            "status": rev["status"],
                            "clock_domain": "episode_aligned",
                            "source_path": rev["source_path"],
                            "args": {"detail": f"R{rev['request_id']}->{','.join(tools) or rtype}"},
                        }
                    )
                events.append(
                    {
                        **base_meta,
                        "event_id": next_id(),
                        "process": "pipeline_state",
                        "thread": "pipeline",
                        "event_type": "pipeline:parallel_http_robot",
                        "start_ns": os_,
                        "end_ns": oe_,
                        "parent_id": rev["event_id"],
                        "request_id": rev["request_id"],
                        "job_id": None,
                        "unit_id": None,
                        "instance_id": None,
                        "status": "parallel",
                        "clock_domain": "episode_aligned",
                        "source_path": rev["source_path"],
                        "args": {"detail": f"HTTP(R{rev['request_id']}) ∥ Robot stateful action"},
                    }
                )
                cur = oe_
            if cur < re_:
                events.append(
                    {
                        **base_meta,
                        "event_id": next_id(),
                        "process": "pipeline_state",
                        "thread": "pipeline",
                        "event_type": f"pipeline:{base_kind}",
                        "start_ns": cur,
                        "end_ns": re_,
                        "parent_id": rev["event_id"],
                        "request_id": rev["request_id"],
                        "job_id": None,
                        "unit_id": None,
                        "instance_id": None,
                        "status": rev["status"],
                        "clock_domain": "episode_aligned",
                        "source_path": rev["source_path"],
                        "args": {"detail": f"R{rev['request_id']}->{','.join(tools) or rtype}"},
                    }
                )
    elif not openai_rows and codex_trace is not None and epoch_t0 is not None:
        # Baseline (Codex) with model_sessions: measured per-round inference and tool execution.
        def _pipe_event(kind: str, s_ts: float, e_ts: float, status: str, **args: Any) -> None:
            s_ns = s_to_ns(s_ts - epoch_t0) or 0
            e_ns = max(s_ns, s_to_ns(e_ts - epoch_t0) or s_ns)
            events.append(
                {
                    **base_meta,
                    "event_id": next_id(),
                    "process": "pipeline_state",
                    "thread": "baseline_serial",
                    "event_type": f"pipeline:{kind}",
                    "start_ns": s_ns,
                    "end_ns": e_ns,
                    "parent_id": None,
                    "request_id": args.get("round"),
                    "job_id": None,
                    "unit_id": None,
                    "instance_id": None,
                    "status": status,
                    "clock_domain": ep_clock_domain,
                    "source_path": args.pop("_source", None),
                    "args": args,
                }
            )

        def _calls_in(s_ts: float, e_ts: float) -> tuple[int, list[str]]:
            n = 0
            stateful_tools: list[str] = []
            for row in calls_rows:
                st = safe_float(row.get("started_at"))
                if st is None or st < s_ts - 0.05 or st > e_ts + 0.05:
                    continue
                n += 1
                if row.get("stateful"):
                    stateful_tools.append(str(row.get("tool") or ""))
            return n, stateful_tools

        round_no = 0
        cell_no = 0
        last_end = float(codex_trace["t0"])
        attempts = codex_trace["attempts"]
        for ai, att in enumerate(attempts, start=1):
            src = str(att["path"])
            if ai > 1 and att["start"] > last_end + 0.05:
                _pipe_event("baseline_backoff", last_end, att["start"], "backoff", attempt=ai, _source=src)
            for rd in att["rounds"]:
                round_no += 1
                rd["no"] = round_no
                _pipe_event(
                    "baseline_round", rd["start"], rd["end"], "ok",
                    round=round_no, tool=rd["tool"], call_id=rd["call_id"], measured=True, _source=src,
                )
            for call in att["tools"]:
                if call["tool"] == "python":
                    cell_no += 1
                    n_calls, stools = _calls_in(call["start"], call["end"])
                    _pipe_event(
                        "baseline_cell_exec", call["start"], call["end"], "ok",
                        cell_index=cell_no, tool="python", call_id=call["call_id"],
                        calls=n_calls, stateful_tools=stools, _source=src,
                    )
                else:
                    _pipe_event(
                        "baseline_tool_exec", call["start"], call["end"], "ok",
                        tool=call["tool"], call_id=call["call_id"], _source=src,
                    )
            open_start = att["open_round_start"]
            if att["error"]:
                span_start = open_start if open_start is not None else att["start"]
                _pipe_event(
                    "baseline_attempt_error", span_start, att["end"], "error",
                    attempt=ai, error=att["error"], _source=src,
                )
            elif open_start is not None:
                final_end = att["end"]
                cut = not att["completed"]
                if cut and ai == len(attempts) and policy_wall_s is not None:
                    final_end = max(final_end, float(codex_trace["t0"]) + float(policy_wall_s))
                if final_end > open_start + 0.05:
                    round_no += 1
                    _pipe_event(
                        "baseline_round", open_start, final_end, "cut" if cut else "ok",
                        round=round_no, tool=None, measured=True, cut_by_timeout=cut, _source=src,
                    )
            last_end = max(last_end, att["end"])
        if policy_wall_s is not None:
            wall_end = float(codex_trace["t0"]) + float(policy_wall_s)
            if wall_end > last_end + 1.0 and not (
                attempts[-1]["open_round_start"] is not None and not attempts[-1]["completed"]
            ):
                _pipe_event(
                    "baseline_unattributed_tail", last_end, wall_end, "inferred",
                    note="policy_wall_s beyond the last Codex session record (teardown, unattributed)",
                    _source=str(loc.result_path),
                )
        codex_trace["info"]["rounds"] = round_no
        codex_trace["info"]["cells"] = cell_no
    elif not openai_rows and calls_rows and epoch_t0 is not None:
        # Baseline (Codex): cluster calls.jsonl into synchronous Cell bursts and inferred LLM gaps
        all_call_spans: list[tuple[int, int, str, bool]] = []
        for row in calls_rows:
            st = safe_float(row.get("started_at"))
            el = safe_float(row.get("elapsed_s")) or 0.0
            if st is None:
                continue
            cs = s_to_ns(st - epoch_t0) or 0
            ce = max(cs, cs + (s_to_ns(el) or 0))
            all_call_spans.append((cs, ce, str(row.get("tool") or ""), bool(row.get("stateful"))))
        all_call_spans.sort(key=lambda x: (x[0], x[1]))
        bursts: list[dict[str, Any]] = []
        for cs, ce, tool, stateful in all_call_spans:
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
        for idx, b in enumerate(bursts, start=1):
            if idx > 1 and b["start_ns"] > bursts[idx - 2]["end_ns"]:
                events.append(
                    {
                        **base_meta,
                        "event_id": next_id(),
                        "process": "pipeline_state",
                        "thread": "baseline_serial",
                        "event_type": "pipeline:baseline_llm_gap",
                        "start_ns": bursts[idx - 2]["end_ns"],
                        "end_ns": b["start_ns"],
                        "parent_id": None,
                        "request_id": None,
                        "job_id": None,
                        "unit_id": None,
                        "instance_id": None,
                        "status": "inferred",
                        "clock_domain": ep_clock_domain,
                        "source_path": str(calls_path),
                        "args": {"inferred_from": "calls_jsonl_gap", "before_cell": idx},
                    }
                )
            events.append(
                {
                    **base_meta,
                    "event_id": next_id(),
                    "process": "pipeline_state",
                    "thread": "baseline_serial",
                    "event_type": "pipeline:baseline_cell_exec",
                    "start_ns": b["start_ns"],
                    "end_ns": b["end_ns"],
                    "parent_id": None,
                    "request_id": None,
                    "job_id": None,
                    "unit_id": None,
                    "instance_id": None,
                    "status": "ok",
                    "clock_domain": ep_clock_domain,
                    "source_path": str(calls_path),
                    "args": {
                        "cell_index": idx,
                        "calls": b["calls"],
                        "stateful_tools": b["stateful_tools"],
                    },
                }
            )
        if bursts and policy_wall_s is not None:
            pol_ns = s_to_ns(policy_wall_s) or 0
            last_b_end = bursts[-1]["end_ns"]
            if pol_ns > last_b_end + 1_000_000_000:
                events.append(
                    {
                        **base_meta,
                        "event_id": next_id(),
                        "process": "pipeline_state",
                        "thread": "baseline_serial",
                        "event_type": "pipeline:baseline_unattributed_tail",
                        "start_ns": last_b_end,
                        "end_ns": pol_ns,
                        "parent_id": None,
                        "request_id": None,
                        "job_id": None,
                        "unit_id": None,
                        "instance_id": None,
                        "status": "inferred",
                        "clock_domain": ep_clock_domain,
                        "source_path": str(loc.result_path),
                        "args": {
                            "note": "policy_wall_s minus calls_jsonl_span (initial prompt think + finish)"
                        },
                    }
                )

    # Usage & token reconciliation (preserve null on partial; never fill missing with 0)
    usage_status = gen.get("usage_status")
    input_tokens = gen.get("input_tokens") if is_nonneg_int(gen.get("input_tokens")) else None
    output_tokens = gen.get("output_tokens") if is_nonneg_int(gen.get("output_tokens")) else None
    cached_tokens = (
        gen.get("cached_input_tokens") if is_nonneg_int(gen.get("cached_input_tokens")) else None
    )
    reasoning_tokens = (
        gen.get("reasoning_output_tokens")
        if is_nonneg_int(gen.get("reasoning_output_tokens"))
        else None
    )
    total_tokens = (
        input_tokens + output_tokens
        if input_tokens is not None and output_tokens is not None
        else (gen.get("total_tokens") if is_nonneg_int(gen.get("total_tokens")) else None)
    )
    if usage_status is None:
        usage_status = (
            "complete"
            if (input_tokens is not None and output_tokens is not None)
            else "unavailable"
        )

    known_usage_raw = gen.get("known_usage") if isinstance(gen.get("known_usage"), dict) else None
    if known_usage_raw is not None:
        known_usage = {
            "prompt": int(known_usage_raw.get("prompt", 0)),
            "completion": int(known_usage_raw.get("completion", 0)),
            "cached": int(known_usage_raw.get("cached", 0)),
            "reasoning": int(known_usage_raw.get("reasoning", 0)),
        }
    elif input_tokens is not None and output_tokens is not None:
        known_usage = {
            "prompt": input_tokens,
            "completion": output_tokens,
            "cached": cached_tokens or 0,
            "reasoning": reasoning_tokens or 0,
        }
    else:
        known_usage = None

    if usage_status != "complete":
        missing_data.append(f"usage_status:{usage_status}")

    outcome, outcome_reason = _classify_outcome(res, run_data)
    settings_snapshot = {
        "arm": arm_name,
        "runtime": runtime_name,
        "model": model_name,
        "reasoning_effort": reasoning_effort,
        "max_turns": res.get("max_turns") or (run_data or {}).get("settings", {}).get("max_turns"),
        "budget_s": (run_data or {}).get("settings", {}).get("budget_s") or res.get("timeout_s"),
        "images": res.get("images") or (run_data or {}).get("settings", {}).get("images"),
        "feedback": res.get("feedback") or (run_data or {}).get("settings", {}).get("feedback"),
        "timing_source": timing.get("source") if timing else None,
        "source_commit": (run_data or {}).get("source_commit"),
        "source_worktree_dirty": (run_data or {}).get("source_worktree_dirty"),
    }

    # Unified Agent Inference / Tool Execution metrics: same source events as the HTML lanes.
    agent_ivs: list[tuple[int, int]] = []
    tool_ivs: list[tuple[int, int]] = []
    poll_ivs: list[tuple[int, int]] = []
    agent_rounds = 0
    for ev in events:
        s_ns, e_ns = ev.get("start_ns"), ev.get("end_ns")
        if s_ns is None or e_ns is None:
            continue
        et = str(ev.get("event_type") or "")
        if ev.get("process") == "provider_request":
            if et in {"model_request", "model_request_retry"}:
                agent_rounds += 1
                if (ev.get("args") or {}).get("triggered_tools") == ["wait_event"]:
                    poll_ivs.append((int(s_ns), int(e_ns)))
        elif et.startswith("tool_dispatch:"):
            tool_ivs.append((int(s_ns), int(e_ns)))
        elif et == "pipeline:baseline_round":
            agent_ivs.append((int(s_ns), int(e_ns)))
            agent_rounds += 1
        elif et == "pipeline:baseline_attempt_error":
            agent_ivs.append((int(s_ns), int(e_ns)))
        elif et in {"pipeline:baseline_cell_exec", "pipeline:baseline_tool_exec"}:
            tool_ivs.append((int(s_ns), int(e_ns)))
    agent_inference_ns: int | None = None
    agent_inference_basis: str | None = None
    if openai_rows:
        agent_inference_ns = http_crit_ns
        agent_inference_basis = "http_measured" if http_crit_ns is not None else None
    elif codex_trace is not None and agent_ivs:
        agent_inference_ns = total_interval_ns(union_intervals(agent_ivs))
        agent_inference_basis = "codex_session_measured"
    elif any(e.get("event_type") == "pipeline:baseline_llm_gap" for e in events):
        agent_inference_basis = "calls_gap_inferred"  # gaps only; no per-round time is claimed
    tool_exec_ns = total_interval_ns(union_intervals(tool_ivs)) if tool_ivs else None
    poll_ns = total_interval_ns(union_intervals(poll_ivs)) if (openai_rows and poll_ivs) else (
        0 if openai_rows and agent_rounds else None
    )
    share_denominator_s = rollout_wall_s if rollout_wall_s is not None else policy_wall_s
    agent_inference_share = (
        round((agent_inference_ns / 1e9) / share_denominator_s, 4)
        if agent_inference_ns is not None and share_denominator_s and share_denominator_s > 0
        else None
    )

    rollout_non_http_s: float | None = None
    if rollout_wall_s is not None and http_crit_ns is not None:
        rollout_non_http_s = round(rollout_wall_s - (http_crit_ns / 1e9), 6)
    non_http_non_robot_s: float | None = None
    if rollout_wall_s is not None and http_or_robot_union_ns is not None:
        non_http_non_robot_s = round(rollout_wall_s - (http_or_robot_union_ns / 1e9), 6)

    http_share_of_rollout = (
        round((http_crit_ns / 1e9) / rollout_wall_s, 4)
        if http_crit_ns is not None and rollout_wall_s and rollout_wall_s > 0
        else None
    )
    overlap_ratio_of_robot = (
        round((http_robot_overlap_ns / 1e9) / (robot_union_ns / 1e9), 4)
        if http_robot_overlap_ns is not None and robot_union_ns and robot_union_ns > 0
        else None
    )

    lat_sorted = sorted(http_latencies_s)
    p95_lat = (
        lat_sorted[min(len(lat_sorted) - 1, int(math.ceil(0.95 * len(lat_sorted))) - 1)]
        if lat_sorted
        else None
    )

    episode_metrics = {
        "key": loc.key,
        "run_id": loc.run_id,
        "suite": loc.suite,
        "task_suite": res.get("suite"),
        "episode_id": loc.episode_id,
        "attempt": loc.attempt,
        "outcome": outcome,
        "outcome_reason": outcome_reason,
        "environment_success": res.get("environment_success"),
        "result_status": res.get("status"),
        "settings": settings_snapshot,
        "clock_alignment": {
            "clock_domain": ep_clock_domain,
            "bridge_method": clock_bridge_method,
            "epoch_t0": epoch_t0,
        },
        "timings_s": {
            "rollout_wall_time_s": rollout_wall_s,
            "simulator_wall_time_s": sim_wall_s,
            "rollout_excluding_sim_s": rollout_excl_sim_s,
            "policy_wall_s": policy_wall_s,
            "startup_s": startup_s,
            "process_wall_time_s": process_wall_s,
            "http_cumulative_s": ns_to_s(http_cum_ns),
            "agent_inference_s": ns_to_s(agent_inference_ns),
            "tool_execution_s": ns_to_s(tool_exec_ns),
            "wait_event_inference_s": ns_to_s(poll_ns),
            "http_critical_path_s": ns_to_s(http_crit_ns),
            "http_ok_union_s": ns_to_s(http_ok_union_ns),
            "http_failed_union_s": ns_to_s(http_fail_union_ns),
            "http_cancelled_union_s": ns_to_s(http_cancel_union_ns),
            "robot_action_union_s": ns_to_s(robot_union_ns),
            "robot_readonly_union_s": ns_to_s(robot_readonly_union_ns),
            "graph_unit_union_s": ns_to_s(graph_unit_union_ns),
            "graph_action_union_s": ns_to_s(graph_action_union_ns),
            "graph_decision_wait_union_s": ns_to_s(graph_dec_wait_union_ns),
            "graph_pause_union_s": ns_to_s(graph_pause_union_ns),
            "http_robot_overlap_s": ns_to_s(http_robot_overlap_ns),
            "http_or_robot_union_s": ns_to_s(http_or_robot_union_ns),
            "http_graph_overlap_s": ns_to_s(http_graph_overlap_ns),
            "rollout_non_http_s": rollout_non_http_s,
            "non_http_non_robot_overhead_s": non_http_non_robot_s,
            "lifecycle_s": lifecycle_durations_s,
        },
        "ratios": {
            "http_share_of_rollout": http_share_of_rollout,
            "agent_inference_share": agent_inference_share,
            "robot_overlap_coverage": overlap_ratio_of_robot,
        },
        "agent_inference_basis": agent_inference_basis,
        "http": {
            "requests_total": http_requests_total if openai_rows else None,
            "requests_ok": http_requests_ok if openai_rows else None,
            "requests_failed": http_requests_failed if openai_rows else None,
            "retry_attempts": http_retry_attempts if openai_rows else None,
            "requests_cancelled": http_requests_cancelled if openai_rows else None,
            "requests_incomplete": http_requests_incomplete if openai_rows else None,
            "missing_usage_requests": http_missing_usage if openai_rows else None,
            "mean_latency_s": round(sum(http_latencies_s) / len(http_latencies_s), 3)
            if http_latencies_s
            else None,
            "p95_latency_s": round(p95_lat, 3) if p95_lat is not None else None,
            "error_breakdown": dict(http_error_summary),
        },
        "tokens": {
            "usage_status": usage_status,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cached_input_tokens": cached_tokens,
            "reasoning_output_tokens": reasoning_tokens,
            "total_tokens": total_tokens,
            "known_usage": known_usage,
        },
        "graph": graph_stats if (arm_name == "graph" or graph_event_files) else None,
        "counts": {
            "calls": res.get("calls", len(calls_rows)),
            "stateful_calls": res.get("stateful_calls", len(robot_stateful_intervals)),
            "env_steps": res.get("env_steps_total", res.get("env_steps")),
            "tool_turns": res.get(
                "tool_turns", len(tool_turns) if isinstance(tool_turns, list) else None
            ),
            "unified_events": len(events),
            "agent_rounds": agent_rounds if agent_inference_basis else None,
            "wait_event_rounds": (len(poll_ivs) if openai_rows else None),
        },
        "codex_session": codex_session_info,
        "viztracer": viz_info,
        "missing_data": sorted(set(missing_data)),
        "source_paths": {
            "result": str(loc.result_path),
            "run": str(loc.run_json_path) if loc.run_json_path else None,
            "openai_events": str(openai_path) if openai_path.is_file() else None,
            "codex_events": str(codex_path) if codex_path.is_file() else None,
            "lifecycle": str(lifecycle_path) if lifecycle_path.is_file() else None,
            "calls": str(calls_path) if calls_path.is_file() else None,
            "graph_events_count": len(graph_event_files),
        },
    }

    # Sort events deterministically (timestamped first by start_ns, then uncalibrated)
    events.sort(
        key=lambda e: (
            0 if e["start_ns"] is not None else 1,
            e["start_ns"] if e["start_ns"] is not None else 0,
            e["end_ns"] if e["end_ns"] is not None else 0,
            e["event_id"],
        )
    )

    return {"metrics": episode_metrics, "events": events, "flows": flows}


# ---------------------------------------------------------------------------
# Perfetto Chrome Trace Event JSON exporter
# ---------------------------------------------------------------------------


def build_perfetto_trace(
    parsed_episode: dict[str, Any],
    *,
    pid_offset: int = 0,
    ts_offset_us: float = 0.0,
    name_prefix: str = "",
) -> dict[str, Any]:
    """Export one episode to Chrome Trace Event JSON compatible with Perfetto UI & SQL."""
    metrics = parsed_episode["metrics"]
    events = parsed_episode["events"]
    flows = parsed_episode["flows"]

    trace_events: list[dict[str, Any]] = []
    seen_pids: dict[int, str] = {}
    tid_map: dict[tuple[int, str], int] = {}

    def get_pid(process_key: str) -> int:
        base_pid, label = PROCESS_META.get(process_key, (9, process_key))
        pid = pid_offset + base_pid
        if pid not in seen_pids:
            seen_pids[pid] = f"{name_prefix}{label}"
            trace_events.append(
                {
                    "name": "process_name",
                    "ph": "M",
                    "pid": pid,
                    "tid": 0,
                    "args": {"name": seen_pids[pid]},
                }
            )
            trace_events.append(
                {
                    "name": "process_sort_index",
                    "ph": "M",
                    "pid": pid,
                    "tid": 0,
                    "args": {"sort_index": pid},
                }
            )
        return pid

    def get_tid(pid: int, thread_name: str) -> int:
        key = (pid, thread_name)
        if key not in tid_map:
            tid = len([k for k in tid_map if k[0] == pid]) + 1
            tid_map[key] = tid
            trace_events.append(
                {
                    "name": "thread_name",
                    "ph": "M",
                    "pid": pid,
                    "tid": tid,
                    "args": {"name": thread_name},
                }
            )
            trace_events.append(
                {
                    "name": "thread_sort_index",
                    "ph": "M",
                    "pid": pid,
                    "tid": tid,
                    "args": {"sort_index": tid},
                }
            )
        return tid_map[key]

    def _emit_slice(
        process_key: str,
        thread_name: str,
        slice_name: str,
        cat: str,
        ts_us: float,
        dur_us: float,
        clean_args: dict[str, Any],
    ) -> tuple[int, int]:
        pid = get_pid(process_key)
        tid = get_tid(pid, thread_name)
        if dur_us == 0.0:
            trace_events.append(
                {
                    "name": slice_name,
                    "cat": cat,
                    "ph": "i",
                    "s": "t",
                    "ts": ts_us,
                    "pid": pid,
                    "tid": tid,
                    "args": clean_args,
                }
            )
        else:
            trace_events.append(
                {
                    "name": slice_name,
                    "cat": cat,
                    "ph": "X",
                    "ts": ts_us,
                    "dur": dur_us,
                    "pid": pid,
                    "tid": tid,
                    "args": clean_args,
                }
            )
        return pid, tid

    ev_coords: dict[str, tuple[int, int, float, float]] = {}
    for ev in events:
        if ev["start_ns"] is None or ev["end_ns"] is None:
            continue
        ts_us = round(ev["start_ns"] / 1000.0 + ts_offset_us, 3)
        dur_us = round(max(0, ev["end_ns"] - ev["start_ns"]) / 1000.0, 3)
        raw_args = ev.get("args") or {}
        args = {
            "event_id": ev["event_id"],
            "episode_id": ev["episode_id"],
            "attempt": ev["attempt"],
            "status": ev["status"],
            "request_id": ev["request_id"],
            "job_id": ev["job_id"],
            "unit_id": ev["unit_id"],
            "instance_id": ev["instance_id"],
            "clock_domain": ev["clock_domain"],
            **raw_args,
        }
        # Strip None values for cleaner Perfetto arg tables while keeping explicit flags
        clean_args = {k: v for k, v in args.items() if v is not None}

        proc = str(ev["process"])
        etype = str(ev["event_type"])
        coords_pid_tid: tuple[int, int] | None = None

        if proc == "provider_request":
            req_id = ev.get("request_id")
            tools = raw_args.get("triggered_tools") or []
            t_str = ",".join(tools) if tools else ""

            # Agent Inference lane: one slice per model HTTP request (colour/name carries the tool chosen)
            if etype == "model_request_backoff":
                ag_thread, ag_name = "agent_backoff", "backoff"
            elif etype == "model_request_incomplete":
                ag_thread, ag_name = "agent_incomplete", f"R{req_id} incomplete"
            elif etype == "model_request_failed":
                code = raw_args.get("status_code") or "ERR"
                ag_thread, ag_name = "agent_inference", f"R{req_id} err {code}"
            elif etype == "model_request_cancelled":
                ag_thread, ag_name = "agent_inference", f"R{req_id} cancelled"
            elif etype == "model_request_retry":
                ag_thread, ag_name = "agent_inference", f"R{req_id} retry"
            else:
                ag_thread = "agent_inference"
                ag_name = f"R{req_id}→{t_str}" if t_str else f"R{req_id}"
            coords_pid_tid = _emit_slice("agent", ag_thread, ag_name, "agent", ts_us, dur_us, clean_args)

        elif proc == "policy_runtime":
            if etype.startswith("tool_dispatch:"):
                tname = etype.split(":", 1)[1]
                coords_pid_tid = _emit_slice(
                    "tool_call",
                    "tool_dispatch",
                    tname,
                    "tool_call",
                    ts_us,
                    dur_us,
                    clean_args,
                )
            elif etype.startswith("lifecycle:"):
                coords_pid_tid = _emit_slice(
                    "tool_call", "lifecycle", etype, "tool_call", ts_us, dur_us, clean_args
                )
            elif ev.get("thread") == "codex_session":
                coords_pid_tid = _emit_slice(
                    "agent", "codex_session", etype, "agent", ts_us, dur_us, clean_args
                )
            else:
                # runtime_rollout envelope and instant assistant_reply stay in events.jsonl
                continue

        elif proc == "pipeline_state":
            # Baseline (Codex) intervals map to Agent Inference & Tool Execution
            if etype == "pipeline:baseline_round":
                tool = raw_args.get("tool")
                rno = raw_args.get("round")
                nm = f"R{rno}→{tool}" if tool else f"R{rno}"
                if raw_args.get("cut_by_timeout"):
                    nm += " (cut by timeout)"
                coords_pid_tid = _emit_slice(
                    "agent", "agent_inference", nm, "agent", ts_us, dur_us, clean_args
                )
            elif etype == "pipeline:baseline_attempt_error":
                coords_pid_tid = _emit_slice(
                    "agent", "agent_inference", f"att{raw_args.get('attempt')} err",
                    "agent", ts_us, dur_us, clean_args,
                )
            elif etype == "pipeline:baseline_backoff":
                coords_pid_tid = _emit_slice(
                    "agent", "agent_backoff", "backoff", "agent", ts_us, dur_us, clean_args
                )
            elif etype == "pipeline:baseline_llm_gap":
                coords_pid_tid = _emit_slice(
                    "agent", "agent_inferred", "infer (inferred)", "agent", ts_us, dur_us, clean_args
                )
            elif etype == "pipeline:baseline_unattributed_tail":
                coords_pid_tid = _emit_slice(
                    "agent", "agent_inferred", "tail (inferred)", "agent", ts_us, dur_us, clean_args
                )
            elif etype == "pipeline:baseline_cell_exec":
                cidx = raw_args.get("cell_index", "")
                coords_pid_tid = _emit_slice(
                    "tool_call", "tool_cell", f"Cell #{cidx}", "tool_call", ts_us, dur_us, clean_args
                )
            elif etype == "pipeline:baseline_tool_exec":
                coords_pid_tid = _emit_slice(
                    "tool_call", "tool_dispatch", str(raw_args.get("tool") or "tool"),
                    "tool_call", ts_us, dur_us, clean_args,
                )
            else:
                # OpenAI pipeline_state overlays stay in events.jsonl, not duplicated in Perfetto
                continue

        elif proc == "graph_manager":
            if etype.startswith("graph_job:"):
                jid = str(ev.get("job_id") or "")
                coords_pid_tid = _emit_slice(
                    "policy_job",
                    "jobs",
                    f"job:{jid[:6]}",
                    "policy_job",
                    ts_us,
                    dur_us,
                    clean_args,
                )
            elif etype.startswith("decision_wait:"):
                coords_pid_tid = _emit_slice(
                    "policy_job",
                    "control",
                    "wait_decision",
                    "policy_job",
                    ts_us,
                    dur_us,
                    clean_args,
                )
            elif etype == "pause_interval":
                coords_pid_tid = _emit_slice(
                    "policy_job", "control", "paused", "policy_job", ts_us, dur_us, clean_args
                )
            elif etype.startswith("graph_patched:"):
                rev = etype.split(":", 1)[1]
                coords_pid_tid = _emit_slice(
                    "policy_job",
                    "control",
                    f"patch:{rev}",
                    "policy_job",
                    ts_us,
                    dur_us,
                    clean_args,
                )
            else:
                coords_pid_tid = _emit_slice(
                    "policy_job", "control", etype, "policy_job", ts_us, dur_us, clean_args
                )

        elif proc == "graph_worker":
            if etype.startswith("graph_unit:"):
                uname = ev.get("unit_id") or "unit"
                coords_pid_tid = _emit_slice(
                    "policy_robot",
                    "policy_units",
                    f"unit:{uname}",
                    "policy_robot",
                    ts_us,
                    dur_us,
                    clean_args,
                )
            elif etype.startswith("graph_action:"):
                prim = raw_args.get("primitive") or "action"
                coords_pid_tid = _emit_slice(
                    "policy_robot",
                    "policy_units",
                    f"action:{prim}",
                    "policy_robot",
                    ts_us,
                    dur_us,
                    clean_args,
                )
            else:
                coords_pid_tid = _emit_slice(
                    "policy_robot",
                    "policy_units",
                    etype,
                    "policy_robot",
                    ts_us,
                    dur_us,
                    clean_args,
                )

        elif proc == "robot_backend":
            tname = str(raw_args.get("tool") or etype.split(":", 1)[-1])
            st = bool(raw_args.get("stateful"))
            coords_pid_tid = _emit_slice(
                "policy_robot",
                "robot_actions" if st else "robot_readonly",
                tname,
                "policy_robot",
                ts_us,
                dur_us,
                clean_args,
            )

        elif proc in {"environment_service", "viztracer_uncalibrated", "viztracer_calibrated"}:
            coords_pid_tid = _emit_slice(
                proc, str(ev["thread"]), etype, proc, ts_us, dur_us, clean_args
            )
        else:
            coords_pid_tid = _emit_slice(
                proc, str(ev["thread"]), etype, proc, ts_us, dur_us, clean_args
            )

        if coords_pid_tid is not None:
            ev_coords[ev["event_id"]] = (coords_pid_tid[0], coords_pid_tid[1], ts_us, ts_us + dur_us)

    # Emit causal flow events
    for idx, fl in enumerate(flows, start=1):
        src_id = fl["from_event"]["event_id"]
        dst_id = fl["to_event"]["event_id"]
        if src_id not in ev_coords or dst_id not in ev_coords:
            continue
        spid, stid, _sts, sends = ev_coords[src_id]
        dpid, dtid, dts, _dends = ev_coords[dst_id]
        flow_id = pid_offset * 100000 + idx
        trace_events.append(
            {
                "name": fl["name"],
                "cat": fl["cat"],
                "ph": "s",
                "id": flow_id,
                "ts": sends,
                "pid": spid,
                "tid": stid,
            }
        )
        trace_events.append(
            {
                "name": fl["name"],
                "cat": fl["cat"],
                "ph": "f",
                "bp": "e",
                "id": flow_id,
                "ts": dts,
                "pid": dpid,
                "tid": dtid,
            }
        )

    return {
        "traceEvents": trace_events,
        "displayTimeUnit": "ms",
        "metadata": {
            "schema": "rollout-timeline-analysis-v1",
            "episode_id": metrics["episode_id"],
            "suite": metrics["suite"],
            "attempt": metrics["attempt"],
            "run_id": metrics["run_id"],
            "clock_alignment": metrics["clock_alignment"],
            "settings": metrics["settings"],
        },
    }


def build_combined_trace(parsed_episodes: list[dict[str, Any]]) -> dict[str, Any]:
    """Combine multiple episodes into one Perfetto trace using isolated pid blocks."""
    all_events: list[dict[str, Any]] = []
    meta_eps: list[dict[str, Any]] = []
    for idx, parsed in enumerate(parsed_episodes):
        m = parsed["metrics"]
        sub = build_perfetto_trace(
            parsed,
            pid_offset=idx * 20,
            ts_offset_us=0.0,
            name_prefix=f"[{m['suite']}/{m['episode_id']}#a{m['attempt']}] ",
        )
        all_events.extend(sub["traceEvents"])
        meta_eps.append(
            {
                "key": m["key"],
                "suite": m["suite"],
                "episode_id": m["episode_id"],
                "attempt": m["attempt"],
                "clock_domain": m["clock_alignment"]["clock_domain"],
            }
        )
    return {
        "traceEvents": all_events,
        "displayTimeUnit": "ms",
        "metadata": {
            "schema": "rollout-timeline-analysis-combined-v1",
            "note": "Each episode uses its own relative clock origin (t=0) in an isolated PID block.",
            "episodes": meta_eps,
        },
    }


# ---------------------------------------------------------------------------
# Aggregation, reconciliation, comparison, and Markdown report
# ---------------------------------------------------------------------------


def _agg_numeric(values: list[float | None]) -> dict[str, Any]:
    present = [v for v in values if v is not None]
    missing = len(values) - len(present)
    rec_total = round(sum(present), 6) if present else None
    mean_val = round(sum(present) / len(present), 6) if present else None
    return {
        "total": rec_total if missing == 0 and present else None,
        "recorded_total": rec_total,
        "mean": mean_val,
        "recorded_episodes": len(present),
        "missing_episodes": missing,
    }


def _agg_int(values: list[int | None]) -> dict[str, Any]:
    present = [v for v in values if v is not None]
    missing = len(values) - len(present)
    rec_total = sum(present) if present else None
    mean_val = round(sum(present) / len(present), 2) if present else None
    return {
        "total": rec_total if missing == 0 and present else None,
        "recorded_total": rec_total,
        "mean": mean_val,
        "recorded_episodes": len(present),
        "missing_episodes": missing,
    }


def aggregate_group(episodes: list[dict[str, Any]]) -> dict[str, Any]:
    outcomes = Counter(e["outcome"] for e in episodes)
    usage_statuses = Counter(e["tokens"]["usage_status"] for e in episodes)

    known_usage_sum = {"prompt": 0, "completion": 0, "cached": 0, "reasoning": 0}
    known_usage_eps = 0
    for e in episodes:
        ku = e["tokens"]["known_usage"]
        if isinstance(ku, dict):
            known_usage_eps += 1
            for k in known_usage_sum:
                known_usage_sum[k] += int(ku.get(k, 0))

    rollout_agg = _agg_numeric([e["timings_s"]["rollout_wall_time_s"] for e in episodes])
    sim_agg = _agg_numeric([e["timings_s"]["simulator_wall_time_s"] for e in episodes])
    excl_agg = _agg_numeric([e["timings_s"]["rollout_excluding_sim_s"] for e in episodes])
    policy_agg = _agg_numeric([e["timings_s"]["policy_wall_s"] for e in episodes])
    proc_agg = _agg_numeric([e["timings_s"]["process_wall_time_s"] for e in episodes])
    http_cum_agg = _agg_numeric([e["timings_s"]["http_cumulative_s"] for e in episodes])
    http_crit_agg = _agg_numeric([e["timings_s"]["http_critical_path_s"] for e in episodes])
    robot_agg = _agg_numeric([e["timings_s"]["robot_action_union_s"] for e in episodes])
    overlap_agg = _agg_numeric([e["timings_s"]["http_robot_overlap_s"] for e in episodes])
    rollout_non_http_agg = _agg_numeric([e["timings_s"]["rollout_non_http_s"] for e in episodes])
    local_agg = _agg_numeric([e["timings_s"]["non_http_non_robot_overhead_s"] for e in episodes])

    agent_agg = _agg_numeric([e["timings_s"]["agent_inference_s"] for e in episodes])
    tool_agg = _agg_numeric([e["timings_s"]["tool_execution_s"] for e in episodes])
    poll_agg = _agg_numeric([e["timings_s"]["wait_event_inference_s"] for e in episodes])
    rounds_agg = _agg_int([e["counts"]["agent_rounds"] for e in episodes])
    poll_rounds_agg = _agg_int([e["counts"]["wait_event_rounds"] for e in episodes])
    basis_counts = Counter(str(e.get("agent_inference_basis")) for e in episodes)
    agent_pairs = [
        (
            e["timings_s"]["agent_inference_s"],
            e["timings_s"]["rollout_wall_time_s"]
            if e["timings_s"]["rollout_wall_time_s"] is not None
            else e["timings_s"]["policy_wall_s"],
        )
        for e in episodes
        if e["timings_s"]["agent_inference_s"] is not None
    ]
    agent_denominator = sum(d for _, d in agent_pairs if d)
    agent_share = (
        round(sum(a for a, _ in agent_pairs) / agent_denominator, 4)
        if agent_pairs and agent_denominator
        else None
    )
    poll_share = (
        round(poll_agg["recorded_total"] / agent_agg["recorded_total"], 4)
        if poll_agg["recorded_total"] is not None
        and agent_agg["recorded_total"]
        and poll_agg["recorded_episodes"] == agent_agg["recorded_episodes"]
        else None
    )

    http_share = None
    if http_crit_agg["recorded_total"] is not None and rollout_agg["recorded_total"]:
        if http_crit_agg["recorded_episodes"] == rollout_agg["recorded_episodes"]:
            http_share = round(http_crit_agg["recorded_total"] / rollout_agg["recorded_total"], 4)

    overlap_ratio = None
    if overlap_agg["recorded_total"] is not None and robot_agg["recorded_total"]:
        if overlap_agg["recorded_episodes"] == robot_agg["recorded_episodes"]:
            overlap_ratio = round(overlap_agg["recorded_total"] / robot_agg["recorded_total"], 4)

    return {
        "episodes": len(episodes),
        "outcomes": {
            "success": outcomes["success"],
            "failure": outcomes["failure"],
            "timeout": outcomes["timeout"],
            "infra_error": outcomes["infra_error"],
            "unknown": outcomes["unknown"],
        },
        "timings_s": {
            "rollout_wall_time_s": rollout_agg,
            "simulator_wall_time_s": sim_agg,
            "rollout_excluding_sim_s": excl_agg,
            "policy_wall_s": policy_agg,
            "process_wall_time_s": proc_agg,
            "http_cumulative_s": http_cum_agg,
            "http_critical_path_s": http_crit_agg,
            "agent_inference_s": agent_agg,
            "tool_execution_s": tool_agg,
            "wait_event_inference_s": poll_agg,
            "robot_action_union_s": robot_agg,
            "http_robot_overlap_s": overlap_agg,
            "rollout_non_http_s": rollout_non_http_agg,
            "non_http_non_robot_overhead_s": local_agg,
        },
        "ratios": {
            "http_share_of_rollout": http_share,
            "agent_inference_share": agent_share,
            "wait_event_share_of_agent_inference": poll_share,
            "robot_overlap_coverage": overlap_ratio,
        },
        "agent": {
            "rounds": rounds_agg,
            "wait_event_rounds": poll_rounds_agg,
            "basis_counts": dict(basis_counts),
        },
        "http": {
            "requests_total": _agg_int([e["http"]["requests_total"] for e in episodes]),
            "requests_ok": _agg_int([e["http"]["requests_ok"] for e in episodes]),
            "requests_failed": _agg_int([e["http"]["requests_failed"] for e in episodes]),
            "retry_attempts": _agg_int([e["http"]["retry_attempts"] for e in episodes]),
            "requests_cancelled": _agg_int([e["http"]["requests_cancelled"] for e in episodes]),
            "missing_usage_requests": _agg_int(
                [e["http"]["missing_usage_requests"] for e in episodes]
            ),
        },
        "tokens": {
            "usage_status_counts": dict(usage_statuses),
            "input_tokens": _agg_int([e["tokens"]["input_tokens"] for e in episodes]),
            "output_tokens": _agg_int([e["tokens"]["output_tokens"] for e in episodes]),
            "total_tokens": _agg_int([e["tokens"]["total_tokens"] for e in episodes]),
            "cached_input_tokens": _agg_int([e["tokens"]["cached_input_tokens"] for e in episodes]),
            "reasoning_output_tokens": _agg_int(
                [e["tokens"]["reasoning_output_tokens"] for e in episodes]
            ),
            "known_usage": known_usage_sum if known_usage_eps > 0 else None,
            "known_usage_episodes": known_usage_eps,
        },
    }


def reconcile_with_summary(
    computed_overall: dict[str, Any],
    computed_by_suite: dict[str, dict[str, Any]],
    summary_json: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not isinstance(summary_json, dict) or not isinstance(summary_json.get("overall"), dict):
        return None

    def _compare_block(comp: dict[str, Any], ref: dict[str, Any]) -> dict[str, Any]:
        checks: dict[str, Any] = {}
        ref_m = ref.get("metrics") or {}
        checks["episodes"] = {
            "computed": comp["episodes"],
            "summary": ref.get("episodes"),
            "match": comp["episodes"] == ref.get("episodes"),
        }
        checks["success"] = {
            "computed": comp["outcomes"]["success"],
            "summary": ref.get("success"),
            "match": comp["outcomes"]["success"] == ref.get("success"),
        }
        comp_non_success_fail = (
            comp["outcomes"]["failure"]
            + comp["outcomes"]["timeout"]
            + comp["outcomes"]["infra_error"]
        )
        checks["non_success_failures"] = {
            "computed": comp_non_success_fail,
            "summary": ref.get("failure"),
            "match": comp_non_success_fail == ref.get("failure"),
        }
        for metric_name in (
            "rollout_wall_time_s",
            "simulator_wall_time_s",
            "rollout_excluding_sim_s",
        ):
            c_val = comp["timings_s"][metric_name]["recorded_total"]
            r_val = (ref_m.get(metric_name) or {}).get("recorded_total")
            diff = None if (c_val is None or r_val is None) else round(c_val - r_val, 6)
            checks[metric_name] = {
                "computed": c_val,
                "summary": r_val,
                "diff": diff,
                "match": diff is not None and abs(diff) < 1e-3,
            }
        c_ku = comp["tokens"]["known_usage"]
        r_ku = ref.get("known_usage")
        if isinstance(c_ku, dict) and isinstance(r_ku, dict):
            checks["known_usage_prompt"] = {
                "computed": c_ku.get("prompt"),
                "summary": r_ku.get("prompt"),
                "match": c_ku.get("prompt") == r_ku.get("prompt"),
            }
            checks["known_usage_completion"] = {
                "computed": c_ku.get("completion"),
                "summary": r_ku.get("completion"),
                "match": c_ku.get("completion") == r_ku.get("completion"),
            }
        return checks

    rec: dict[str, Any] = {
        "overall": _compare_block(computed_overall, summary_json["overall"]),
        "by_suite": {},
    }
    ref_sets = summary_json.get("by_set") or {}
    for s_name, s_ref in ref_sets.items():
        if s_name in computed_by_suite and isinstance(s_ref, dict):
            rec["by_suite"][s_name] = _compare_block(computed_by_suite[s_name], s_ref)
    return rec


def compare_runs(
    primary_eps: list[dict[str, Any]],
    other_eps: list[dict[str, Any]],
    primary_label: str,
    other_label: str,
) -> dict[str, Any]:
    """Compare two runs while auditing config differences and preventing invalid causal attribution."""
    p_map = {(e["suite"], e["episode_id"]): e for e in primary_eps}
    o_map = {(e["suite"], e["episode_id"]): e for e in other_eps}
    common_keys = sorted(set(p_map.keys()) & set(o_map.keys()))

    def _norm_cfg(v: Any) -> str:
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v)

    def _collect_settings(eps: list[dict[str, Any]]) -> dict[str, list[Any]]:
        keys = (
            "arm",
            "runtime",
            "model",
            "reasoning_effort",
            "max_turns",
            "budget_s",
            "images",
            "feedback",
            "timing_source",
        )
        out: dict[str, list[Any]] = {}
        for k in keys:
            vals = sorted({_norm_cfg(e["settings"].get(k)) for e in eps})
            out[k] = vals
        return out

    p_scope_eps = [p_map[k] for k in common_keys] if common_keys else primary_eps
    o_scope_eps = [o_map[k] for k in common_keys] if common_keys else other_eps
    p_cfg = _collect_settings(p_scope_eps)
    o_cfg = _collect_settings(o_scope_eps)
    confounders = [
        k
        for k in (
            "runtime",
            "model",
            "reasoning_effort",
            "max_turns",
            "budget_s",
            "images",
            "feedback",
            "timing_source",
        )
        if p_cfg.get(k) != o_cfg.get(k)
    ]
    comparison_scope = "system_level" if confounders else "controlled"

    paired_rows: list[dict[str, Any]] = []
    for key in common_keys:
        pe = p_map[key]
        oe = o_map[key]
        p_roll = pe["timings_s"]["rollout_wall_time_s"]
        o_roll = oe["timings_s"]["rollout_wall_time_s"]
        p_pol = pe["timings_s"]["policy_wall_s"]
        o_pol = oe["timings_s"]["policy_wall_s"]
        paired_rows.append(
            {
                "suite": key[0],
                "episode_id": key[1],
                "primary_attempt": pe["attempt"],
                "other_attempt": oe["attempt"],
                "primary_outcome": pe["outcome"],
                "other_outcome": oe["outcome"],
                "primary_rollout_s": p_roll,
                "other_rollout_s": o_roll,
                "rollout_delta_s": round(p_roll - o_roll, 3)
                if (p_roll is not None and o_roll is not None)
                else None,
                "primary_policy_wall_s": p_pol,
                "other_policy_wall_s": o_pol,
                "policy_wall_delta_s": round(p_pol - o_pol, 3)
                if (p_pol is not None and o_pol is not None)
                else None,
                "primary_http_crit_s": pe["timings_s"]["http_critical_path_s"],
                "other_http_crit_s": oe["timings_s"]["http_critical_path_s"],
                "primary_robot_overlap_s": pe["timings_s"]["http_robot_overlap_s"],
                "other_robot_overlap_s": oe["timings_s"]["http_robot_overlap_s"],
                "primary_agent_inference_s": pe["timings_s"]["agent_inference_s"],
                "other_agent_inference_s": oe["timings_s"]["agent_inference_s"],
                "primary_tool_execution_s": pe["timings_s"]["tool_execution_s"],
                "other_tool_execution_s": oe["timings_s"]["tool_execution_s"],
                "primary_agent_rounds": pe["counts"]["agent_rounds"],
                "other_agent_rounds": oe["counts"]["agent_rounds"],
                "primary_basis": pe.get("agent_inference_basis"),
                "other_basis": oe.get("agent_inference_basis"),
                "primary_total_tokens": pe["tokens"]["total_tokens"],
                "other_total_tokens": oe["tokens"]["total_tokens"],
            }
        )

    def _clock_summary(eps: list[dict[str, Any]]) -> dict[str, Any]:
        sessions = [e for e in eps if (e.get("codex_session") or {}).get("rounds") is not None]
        drifts = [
            abs(e["codex_session"]["anchor_check_s"])
            for e in sessions
            if e["codex_session"].get("anchor_check_s") is not None
        ]
        return {
            "clock_domains": dict(Counter(e["clock_alignment"]["clock_domain"] for e in eps)),
            "session_episodes": len(sessions),
            "session_failed_attempts": sum(
                e["codex_session"].get("failed_attempts", 0) for e in sessions
            ),
            "session_max_anchor_drift_s": round(max(drifts), 3) if drifts else None,
        }

    return {
        "primary_label": primary_label,
        "other_label": other_label,
        "primary_clock": _clock_summary(primary_eps),
        "other_clock": _clock_summary(other_eps),
        "comparison_scope": comparison_scope,
        "confounders": confounders,
        "primary_settings": p_cfg,
        "other_settings": o_cfg,
        "paired_count": len(common_keys),
        "primary_only_count": len(p_map) - len(common_keys),
        "other_only_count": len(o_map) - len(common_keys),
        "paired_episodes": paired_rows,
        "caution": (
            "两侧存在 runtime/模型/预算/计时口径差异，属于系统级比较（system-level comparison），"
            "不能将耗时或成功率变化单一归因于并行调度改动。"
            if comparison_scope == "system_level"
            else "两侧核心运行配置一致，可在相同任务与同口径下直接对比。"
        ),
    }


_BASIS_LABEL = {
    "http_measured": "逐次 HTTP 请求（实测）",
    "codex_session_measured": "Codex session 逐轮（实测，非 HTTP 口径）",
    "calls_gap_inferred": "calls.jsonl 间隔（仅推断，不计入）",
    "None": "N/A",
}


def _fmt_basis(counts: dict[str, int] | None) -> str:
    if not counts:
        return "N/A"
    return " / ".join(f"{_BASIS_LABEL.get(k, k)}×{v}" for k, v in sorted(counts.items()))


def _fmt(v: float | int | None, digits: int = 2) -> str:
    if v is None:
        return "N/A"
    if isinstance(v, int):
        return f"{v:,}"
    return f"{v:,.{digits}f}"


def _fmt_pct(v: float | None) -> str:
    if v is None:
        return "N/A"
    return f"{v * 100:.1f}%"


def render_markdown_report(
    *,
    input_root: Path,
    attempt_policy: str,
    overall: dict[str, Any],
    by_suite: dict[str, dict[str, Any]],
    episodes: list[dict[str, Any]],
    excluded_attempts: list[dict[str, Any]],
    reconciliation: dict[str, Any] | None,
    comparison: dict[str, Any] | None,
    trace_paths: dict[str, str],
) -> str:
    lines: list[str] = []
    lines.append(f"# Rollout 时序与关键路径分析报告：`{input_root.name}`")
    lines.append("")

    # 1. Metadata & reproducibility
    arms = sorted({str(e["settings"]["arm"]) for e in episodes})
    runtimes = sorted({str(e["settings"]["runtime"]) for e in episodes})
    models = sorted({str(e["settings"]["model"]) for e in episodes})
    efforts = sorted({str(e["settings"]["reasoning_effort"]) for e in episodes})
    commits = sorted(
        {str(e["settings"]["source_commit"]) for e in episodes if e["settings"]["source_commit"]}
    )
    lines.append("## 1. 运行元信息与统计范围")
    lines.append("")
    lines.append(f"- **输入路径**：`{input_root}`")
    lines.append(
        f"- **分析条目**：{overall['episodes']} 条 episode（attempt 策略：`{attempt_policy}`；排除旧 attempt：{len(excluded_attempts)} 条）"
    )
    lines.append(
        f"- **系统配置**：arm={', '.join(arms)} | runtime={', '.join(runtimes)} | model={', '.join(models)} | reasoning={', '.join(efforts)}"
    )
    if commits:
        lines.append(f"- **代码提交**：`{', '.join(commits)}`")
    lines.append(
        "- **时间口径说明**：主指标同时保留完整 `rollout_wall_time_s`、仿真时间、排除仿真时间、HTTP 累计/关键路径并集及 HTTP 与动作重叠；HTTP 等待不从主 rollout 中扣除；缺失项标为 `N/A` 不填零。"
    )
    lines.append(
        "- **与时序图一致的两条主轨道**：`Agent Inference` = 模型推理区间并集（Ours 取逐次 HTTP 请求，Codex Baseline 取 `model_sessions` 逐轮，不含重试 backoff，口径见各行标注）；"
        "`Tool Execution` = 工具分发→返回区间并集（Ours 的 `python_start`/`wait_event` 等近零时长，Baseline 的 python cell 为真实执行时长）。"
        "Baseline 找不到 session 时只能由 `calls.jsonl` 间隔推断，此时 Agent Inference 记 `N/A`，不拿推断值充数。"
    )
    lines.append("")

    # 2. Summary table
    lines.append("## 2. 整体与分 Suite 汇总")
    lines.append("")
    lines.append(
        "| Suite | Episodes | Success | Failure | Timeout | InfraErr | Unknown | Rollout 均值 (s) | Sim 均值 (s) | 排除 Sim 均值 (s) | Agent Inference 均值 (s) | Tool Execution 均值 (s) | Agent 轮数(其中 wait_event) | HTTP 累计均值 (s) | HTTP 关键路径均值 (s) | Robot 动作并集均值 (s) | HTTP∩动作重叠均值 (s) | HTTP 请求(失败/重试/取消) | Token 完整/Partial |"
    )
    lines.append(
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- | --- |"
    )

    def _row_str(label: str, g: dict[str, Any]) -> str:
        t = g["timings_s"]
        h = g["http"]
        tok = g["tokens"]["usage_status_counts"]
        req_s = (
            f"{_fmt(h['requests_total']['recorded_total'], 0)} "
            f"({_fmt(h['requests_failed']['recorded_total'], 0)}/"
            f"{_fmt(h['retry_attempts']['recorded_total'], 0)}/"
            f"{_fmt(h['requests_cancelled']['recorded_total'], 0)})"
            if h["requests_total"]["recorded_total"] is not None
            else "N/A"
        )
        tok_s = f"{tok.get('complete', 0)}/{tok.get('partial', 0)}"
        ag = g["agent"]
        rounds_s = (
            f"{_fmt(ag['rounds']['recorded_total'], 0)} ({_fmt(ag['wait_event_rounds']['recorded_total'], 0)})"
            if ag["rounds"]["recorded_total"] is not None
            else "N/A"
        )
        return (
            f"| {label} | {g['episodes']} | {g['outcomes']['success']} | {g['outcomes']['failure']} | "
            f"{g['outcomes']['timeout']} | {g['outcomes']['infra_error']} | {g['outcomes']['unknown']} | "
            f"{_fmt(t['rollout_wall_time_s']['mean'])} | {_fmt(t['simulator_wall_time_s']['mean'])} | "
            f"{_fmt(t['rollout_excluding_sim_s']['mean'])} | {_fmt(t['agent_inference_s']['mean'])} | "
            f"{_fmt(t['tool_execution_s']['mean'])} | {rounds_s} | {_fmt(t['http_cumulative_s']['mean'])} | "
            f"{_fmt(t['http_critical_path_s']['mean'])} | {_fmt(t['robot_action_union_s']['mean'])} | "
            f"{_fmt(t['http_robot_overlap_s']['mean'])} | {req_s} | {tok_s} |"
        )

    for s_name in sorted(by_suite.keys()):
        lines.append(_row_str(s_name, by_suite[s_name]))
    lines.append(_row_str("**Overall**", overall))
    lines.append("")

    # 3. Three-tier conclusions
    lines.append("## 3. 三层归因结论")
    lines.append("")
    ot = overall["timings_s"]
    oh = overall["http"]
    oratio = overall["ratios"]
    lines.append(
        f"1. **真实端到端体验**：共 {overall['episodes']} 条，成功 {overall['outcomes']['success']}、"
        f"能力失败 {overall['outcomes']['failure']}、超时 {overall['outcomes']['timeout']}、"
        f"基础设施错误 {overall['outcomes']['infra_error']}、未知 {overall['outcomes']['unknown']}。"
        f"完整 Rollout 均值 {_fmt(ot['rollout_wall_time_s']['mean'])} s（总计 {_fmt(ot['rollout_wall_time_s']['recorded_total'])} s），"
        f"Process 墙钟均值 {_fmt(ot['process_wall_time_s']['mean'])} s（含启动与收尾）。"
    )
    og = overall["agent"]
    wait_part = (
        f"其中选择 `wait_event` 的纯轮询 {_fmt(og['wait_event_rounds']['recorded_total'], 0)} 轮、"
        f"累计 {_fmt(ot['wait_event_inference_s']['recorded_total'])} s"
        f"（占 Agent Inference {_fmt_pct(oratio['wait_event_share_of_agent_inference'])}）；"
        if og["wait_event_rounds"]["recorded_total"] is not None
        else ""
    )
    lines.append(
        f"2. **Agent 推理等待占比与稳定性**（Agent Inference 口径：{_fmt_basis(og['basis_counts'])}）：均值 "
        f"{_fmt(ot['agent_inference_s']['mean'])} s（累计 {_fmt(ot['agent_inference_s']['recorded_total'])} s），"
        f"占{'完整 Rollout' if ot['rollout_wall_time_s']['recorded_total'] is not None else ' policy_wall'} 的比例 "
        f"{_fmt_pct(oratio['agent_inference_share'])}；共 {_fmt(og['rounds']['recorded_total'], 0)} 轮，{wait_part}"
        f"HTTP 层面：关键路径并集均值 {_fmt(ot['http_critical_path_s']['mean'])} s（累计均值 {_fmt(ot['http_cumulative_s']['mean'])} s），"
        f"请求 {_fmt(oh['requests_total']['recorded_total'], 0)} 次，其中失败 {_fmt(oh['requests_failed']['recorded_total'], 0)}、"
        f"重试 {_fmt(oh['retry_attempts']['recorded_total'], 0)}、取消 {_fmt(oh['requests_cancelled']['recorded_total'], 0)}、"
        f"缺失 usage 请求 {_fmt(oh['missing_usage_requests']['recorded_total'], 0)}。"
    )
    lines.append(
        f"3. **Harness 本地调度、并行覆盖与环境执行效率**：仿真环境均值 {_fmt(ot['simulator_wall_time_s']['mean'])} s，"
        f"排除仿真后均值 {_fmt(ot['rollout_excluding_sim_s']['mean'])} s，"
        f"Tool Execution（工具分发→返回）均值 {_fmt(ot['tool_execution_s']['mean'])} s，"
        f"机器人带状态动作并集均值 {_fmt(ot['robot_action_union_s']['mean'])} s，"
        f"HTTP 与机器人动作并行重叠均值 {_fmt(ot['http_robot_overlap_s']['mean'])} s（动作并行覆盖率 {_fmt_pct(oratio['robot_overlap_coverage'])}），"
        f"HTTP 之外暴露时间均值 {_fmt(ot['rollout_non_http_s']['mean'])} s，"
        f"非 HTTP 非动作本地调度/只读/收尾暴露均值 {_fmt(ot['non_http_non_robot_overhead_s']['mean'])} s。"
    )
    lines.append("")

    # 4. Reconciliation with official summary.json
    if reconciliation is not None:
        lines.append("## 4. 官方 `summary.json` 对账")
        lines.append("")
        lines.append("| 范围 | 指标 | 本工具计算值 | `summary.json` | 差值 | 一致 |")
        lines.append("| --- | --- | ---: | ---: | ---: | --- |")
        for k, v in reconciliation["overall"].items():
            lines.append(
                f"| overall | `{k}` | {_fmt(v['computed'])} | {_fmt(v['summary'])} | "
                f"{_fmt(v.get('diff')) if 'diff' in v else '-'} | {'OK' if v['match'] else 'MISMATCH'} |"
            )
        lines.append("")

    # 5. Baseline vs Harness comparison
    if comparison is not None:
        lines.append(
            f"## 5. 对比分析：`{comparison['primary_label']}` vs `{comparison['other_label']}`"
        )
        lines.append("")
        if comparison["comparison_scope"] == "system_level":
            lines.append(
                f"> **警告 — 系统级比较（System-Level Comparison）**：{comparison['caution']}"
            )
            lines.append(f"> 差异配置项：`{', '.join(comparison['confounders'])}`")
            lines.append("")
        else:
            lines.append(f"> **受控比较**：{comparison['caution']}")
            lines.append("")

        lines.append(
            "| 配置项 | " + comparison["primary_label"] + " | " + comparison["other_label"] + " |"
        )
        lines.append("| --- | --- | --- |")
        for k in (
            "arm",
            "runtime",
            "model",
            "reasoning_effort",
            "max_turns",
            "budget_s",
            "timing_source",
        ):
            lines.append(
                f"| `{k}` | {', '.join(comparison['primary_settings'].get(k, []))} | "
                f"{', '.join(comparison['other_settings'].get(k, []))} |"
            )
        lines.append("")
        lines.append(
            f"共同任务配对数：**{comparison['paired_count']}**（仅主组：{comparison['primary_only_count']}，仅对照组：{comparison['other_only_count']}）。"
        )
        lines.append("")
        if comparison["paired_episodes"]:
            lines.append(
                "| Suite | Episode | 主组结果 | 对照结果 | 主组 Policy (s) | 对照 Policy (s) | Policy 差值 (s) | 主组 Rollout (s) | 对照 Rollout (s) | 主组 Agent Inference (s) | 对照 Agent Inference (s) | 主组 Tool Execution (s) | 对照 Tool Execution (s) | 主组/对照 轮数 | 主组 HTTP∩动作 (s) |"
            )
            lines.append(
                "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |"
            )
            for row in comparison["paired_episodes"]:
                lines.append(
                    f"| {row['suite']} | `{row['episode_id']}` | {row['primary_outcome']} | {row['other_outcome']} | "
                    f"{_fmt(row['primary_policy_wall_s'])} | {_fmt(row['other_policy_wall_s'])} | {_fmt(row['policy_wall_delta_s'])} | "
                    f"{_fmt(row['primary_rollout_s'])} | {_fmt(row['other_rollout_s'])} | "
                    f"{_fmt(row['primary_agent_inference_s'])} | {_fmt(row['other_agent_inference_s'])} | "
                    f"{_fmt(row['primary_tool_execution_s'])} | {_fmt(row['other_tool_execution_s'])} | "
                    f"{_fmt(row['primary_agent_rounds'], 0)}/{_fmt(row['other_agent_rounds'], 0)} | "
                    f"{_fmt(row['primary_robot_overlap_s'])} |"
                )
            lines.append("")
            both = [
                r
                for r in comparison["paired_episodes"]
                if r["primary_agent_inference_s"] is not None
                and r["other_agent_inference_s"] is not None
            ]
            if both:
                n = len(both)
                lines.append(
                    f"配对样本（Agent Inference 两侧都有实测的 {n} 条）均值：Agent Inference 主组 "
                    f"{_fmt(sum(r['primary_agent_inference_s'] for r in both) / n)} s / 对照 "
                    f"{_fmt(sum(r['other_agent_inference_s'] for r in both) / n)} s；"
                    f"Tool Execution 主组 "
                    f"{_fmt(sum(r['primary_tool_execution_s'] or 0 for r in both) / n)} s / 对照 "
                    f"{_fmt(sum(r['other_tool_execution_s'] or 0 for r in both) / n)} s。"
                )
            p_basis = sorted({str(r["primary_basis"]) for r in comparison["paired_episodes"]})
            o_basis = sorted({str(r["other_basis"]) for r in comparison["paired_episodes"]})
            for side, key in (("主组", "primary_clock"), ("对照", "other_clock")):
                ck = comparison[key]
                dom = "、".join(f"`{d}`×{n}" for d, n in sorted(ck["clock_domains"].items()))
                extra = (
                    f"；{ck['session_episodes']} 条由 Codex session 逐轮还原（失败 attempt {ck['session_failed_attempts']} 次，"
                    f"锚点最大偏差 {ck['session_max_anchor_drift_s']} s）"
                    if ck["session_episodes"]
                    else ""
                )
                lines.append(f"{side}时钟域：{dom}{extra}。")
            lines.append(
                f"Agent Inference 口径：主组 {' / '.join(_BASIS_LABEL.get(b, b) for b in p_basis)}；"
                f"对照 {' / '.join(_BASIS_LABEL.get(b, b) for b in o_basis)}。两侧口径不同，仅作量级对照，不当作同口径差值。"
            )
            lines.append("")

    # 6. Per-episode timeline table
    lines.append("## 6. 单条 Episode 时间线明细")
    lines.append("")
    lines.append(
        "| Suite | Episode | Att | Outcome | Rollout (s) | Sim (s) | Agent Inference (s) | Tool Execution (s) | 轮数(wait_event) | HTTP 关键路径 (s) | 动作并集 (s) | HTTP∩动作 (s) | 请求(失/重/取) | Graph(Jobs/Pause/Rev/Cancel) | Usage | Clock | Trace |"
    )
    lines.append(
        "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- | --- | --- | --- | --- |"
    )
    for e in episodes:
        t = e["timings_s"]
        h = e["http"]
        g = e["graph"]
        req_cell = (
            f"{h['requests_total']}({h['requests_failed']}/{h['retry_attempts']}/{h['requests_cancelled']})"
            if h["requests_total"] is not None
            else "N/A"
        )
        g_cell = (
            f"{g['jobs']}/{g['pauses']}/{g['revisions']}/{g['cancellations']}"
            if isinstance(g, dict)
            else "N/A"
        )
        tr_rel = trace_paths.get(e["key"], "N/A")
        lines.append(
            f"| {e['suite']} | `{e['episode_id']}` | {e['attempt']} | {e['outcome']} | "
            f"{_fmt(t['rollout_wall_time_s'])} | {_fmt(t['simulator_wall_time_s'])} | "
            f"{_fmt(t['agent_inference_s'])} | {_fmt(t['tool_execution_s'])} | "
            f"{_fmt(e['counts']['agent_rounds'], 0)}({_fmt(e['counts']['wait_event_rounds'], 0)}) | "
            f"{_fmt(t['http_critical_path_s'])} | {_fmt(t['robot_action_union_s'])} | "
            f"{_fmt(t['http_robot_overlap_s'])} | {req_cell} | {g_cell} | "
            f"{e['tokens']['usage_status']} | `{e['clock_alignment']['clock_domain']}` | `{tr_rel}` |"
        )
    lines.append("")

    # 7. Missing data, excluded attempts, and clock notes
    lines.append("## 7. 缺失数据、被排除 Attempt 与时钟对齐说明")
    lines.append("")
    if excluded_attempts:
        lines.append("### 被排除的旧 Attempt（按 `attempt-policy=latest`）")
        lines.append("")
        for ex in excluded_attempts:
            lines.append(
                f"- `{ex['suite']}/{ex['episode_id']}` `attempt-{ex['attempt']:02d}` "
                f"(status=`{ex['result_status']}`, reason=`{ex['reason']}`, 被 `attempt-{ex['selected_attempt']:02d}` 取代)"
            )
        lines.append("")

    missing_counter: Counter[str] = Counter()
    clock_counter: Counter[str] = Counter()
    for e in episodes:
        clock_counter[
            f"{e['clock_alignment']['clock_domain']} ({e['clock_alignment']['bridge_method']})"
        ] += 1
        for m in e["missing_data"]:
            missing_counter[m] += 1

    lines.append("### 时钟桥接分布")
    lines.append("")
    for ck, cnt in sorted(clock_counter.items()):
        lines.append(f"- `{ck}`：{cnt} 条")
    lines.append("")

    session_eps = [e for e in episodes if (e.get("codex_session") or {}).get("rounds") is not None]
    if session_eps:
        drifts = [
            abs(e["codex_session"]["anchor_check_s"])
            for e in session_eps
            if e["codex_session"].get("anchor_check_s") is not None
        ]
        failed = sum(e["codex_session"].get("failed_attempts", 0) for e in session_eps)
        lines.append("### Codex session 逐轮还原")
        lines.append("")
        lines.append(
            f"- {len(session_eps)} 条 episode 由 `model_sessions` 还原逐轮推理（`t=0` 为首个 session 的 `task_started`），"
            f"其中失败的规划 attempt 共 {failed} 次；"
            + (f"首条机器人调用与首个 function_call 的最大偏差 {max(drifts):.3f} s。" if drifts else "无可核对的锚点偏差。")
        )
        lines.append("")

    lines.append("### 缺失与异常数据统计")
    lines.append("")
    if missing_counter:
        for mk, cnt in missing_counter.most_common():
            lines.append(f"- `{mk}`：{cnt} 条")
    else:
        lines.append("- 未检测到缺失文件或缺失核心字段。")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# End-to-end runner
# ---------------------------------------------------------------------------


def run_analysis(
    input_path: Path,
    out_dir: Path,
    *,
    attempt_policy: str = "latest",
    compare_path: Path | None = None,
    combined_trace: bool = False,
    viztracer_path: Path | None = None,
    viztracer_offset_s: float | None = None,
    viztracer_max_events: int = 20000,
    codex_session_path: Path | None = None,
) -> dict[str, Any]:
    in_resolved = input_path.resolve()
    out_resolved = out_dir.resolve()
    if out_resolved == in_resolved or in_resolved in out_resolved.parents:
        raise ValueError(
            f"Refusing to write outputs inside input directory ({out_resolved} inside {in_resolved}). "
            "Pass a separate --out directory so original run artifacts are never overwritten."
        )

    disc = discover_input(in_resolved, attempt_policy=attempt_policy)
    out_resolved.mkdir(parents=True, exist_ok=True)

    if not disc["selected"]:
        missing_report = {
            "status": "no_artifacts_found",
            "input_path": str(in_resolved),
            "missing_data": ["no_result_json_found"],
        }
        (out_resolved / "metrics.json").write_text(
            json.dumps(missing_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        (out_resolved / "report.md").write_text(
            f"# 缺失清单\n\n未在 `{in_resolved}` 下发现任何可解析的 `result.json` 运行产物，未估算任何时间。\n",
            encoding="utf-8",
        )
        return missing_report

    if viztracer_path is not None and len(disc["selected"]) > 1:
        raise ValueError(
            "--viztracer applies to a single episode input; point input_path to one episode directory."
        )

    traces_dir = out_resolved / "traces"
    traces_dir.mkdir(parents=True, exist_ok=True)

    parsed_episodes: list[dict[str, Any]] = []
    trace_paths: dict[str, str] = {}
    all_unified_events: list[dict[str, Any]] = []

    for loc in disc["selected"]:
        parsed = parse_episode(
            loc,
            viztracer_path=viztracer_path,
            viztracer_offset_s=viztracer_offset_s,
            viztracer_max_events=viztracer_max_events,
            codex_session_path=codex_session_path,
        )
        parsed_episodes.append(parsed)
        all_unified_events.extend(parsed["events"])

        pf = build_perfetto_trace(parsed)
        tfile = traces_dir / f"{loc.key}.perfetto.json"
        tfile.write_text(json.dumps(pf, ensure_ascii=False) + "\n", encoding="utf-8")
        trace_paths[loc.key] = str(tfile.relative_to(out_resolved))

    combined_trace_rel = None
    if combined_trace and parsed_episodes:
        comb = build_combined_trace(parsed_episodes)
        cfile = traces_dir / "combined.perfetto.json"
        cfile.write_text(json.dumps(comb, ensure_ascii=False) + "\n", encoding="utf-8")
        combined_trace_rel = str(cfile.relative_to(out_resolved))

    # Write unified event table
    events_path = out_resolved / "events.jsonl"
    with events_path.open("w", encoding="utf-8") as ef:
        for ev in all_unified_events:
            ef.write(json.dumps(ev, ensure_ascii=False) + "\n")

    ep_metrics = [p["metrics"] for p in parsed_episodes]
    overall = aggregate_group(ep_metrics)
    by_suite: dict[str, dict[str, Any]] = {}
    suite_buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for m in ep_metrics:
        suite_buckets[m["suite"]].append(m)
    for s_name in sorted(suite_buckets.keys()):
        by_suite[s_name] = aggregate_group(suite_buckets[s_name])

    reconciliation = reconcile_with_summary(overall, by_suite, disc["summary_json"])

    comparison = None
    other_parsed: list[dict[str, Any]] | None = None
    compare_trace_paths: dict[str, str] | None = None
    if compare_path is not None:
        other_disc = discover_input(compare_path.resolve(), attempt_policy=attempt_policy)
        other_parsed = [parse_episode(loc) for loc in other_disc["selected"]]
        other_metrics = [p["metrics"] for p in other_parsed]
        compare_traces_dir = traces_dir / "compare"
        compare_traces_dir.mkdir(parents=True, exist_ok=True)
        compare_trace_paths = {}
        for loc, parsed_other in zip(other_disc["selected"], other_parsed, strict=True):
            pf_other = build_perfetto_trace(parsed_other)
            c_tfile = compare_traces_dir / f"{loc.key}.perfetto.json"
            c_tfile.write_text(json.dumps(pf_other, ensure_ascii=False) + "\n", encoding="utf-8")
            compare_trace_paths[loc.key] = str(c_tfile.relative_to(out_resolved))
        comparison = compare_runs(
            ep_metrics,
            other_metrics,
            primary_label=in_resolved.name,
            other_label=compare_path.resolve().name,
        )

    # Render interactive Perfetto / Chrome Trace Viewer style pipeline timeline HTML
    pipeline_html_rel = "pipeline_timeline.html"
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from render_pipeline_html import render_pipeline_timeline_html

    pipeline_html = render_pipeline_timeline_html(
        parsed_episodes,
        primary_label=in_resolved.name,
        other_parsed=other_parsed,
        other_label=compare_path.resolve().name if compare_path is not None else None,
        comparison_scope=comparison["comparison_scope"] if comparison else None,
        confounders=comparison["confounders"] if comparison else None,
    )
    (out_resolved / pipeline_html_rel).write_text(pipeline_html, encoding="utf-8")

    output_payload = {
        "schema": "rollout-timeline-analysis-metrics-v1",
        "input_path": str(in_resolved),
        "attempt_policy": attempt_policy,
        "overall": overall,
        "by_suite": by_suite,
        "reconciliation": reconciliation,
        "comparison": comparison,
        "excluded_attempts": disc["excluded_attempts"],
        "trace_paths": trace_paths,
        "compare_trace_paths": compare_trace_paths,
        "combined_trace": combined_trace_rel,
        "pipeline_timeline_html": pipeline_html_rel,
        "episodes": ep_metrics,
    }
    (out_resolved / "metrics.json").write_text(
        json.dumps(output_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    report_md = render_markdown_report(
        input_root=in_resolved,
        attempt_policy=attempt_policy,
        overall=overall,
        by_suite=by_suite,
        episodes=ep_metrics,
        excluded_attempts=disc["excluded_attempts"],
        reconciliation=reconciliation,
        comparison=comparison,
        trace_paths=trace_paths,
    )
    (out_resolved / "report.md").write_text(report_md, encoding="utf-8")
    return output_payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Analyze baseline & REAgent harness rollout logs into unified events, Perfetto traces, and critical-path reports."
    )
    parser.add_argument(
        "input_path", type=Path, help="Single episode directory or batch run directory (read-only)"
    )
    parser.add_argument(
        "--out", type=Path, required=True, help="Output directory for analysis artifacts"
    )
    parser.add_argument(
        "--attempt-policy",
        choices=("latest", "all"),
        default="latest",
        help="When multiple attempts exist for one task: 'latest' (or batch.json selection) vs 'all'",
    )
    parser.add_argument(
        "--compare",
        type=Path,
        default=None,
        help="Optional second run/episode path (e.g. baseline) for paired & config-audited comparison",
    )
    parser.add_argument(
        "--combined-trace",
        action="store_true",
        help="Also emit traces/combined.perfetto.json containing all episodes in isolated PID blocks",
    )
    parser.add_argument(
        "--viztracer",
        type=Path,
        default=None,
        help="Optional VizTracer JSON file (single-episode mode only)",
    )
    parser.add_argument(
        "--viztracer-offset-s",
        type=float,
        default=None,
        help="Explicit calibrated clock offset in seconds for VizTracer; omit to keep uncalibrated separate lane",
    )
    parser.add_argument(
        "--viztracer-max-events",
        type=int,
        default=20000,
        help="Maximum VizTracer slices to import (default 20000)",
    )
    parser.add_argument(
        "--codex-session",
        type=Path,
        default=None,
        help="Optional Codex session JSONL with ISO timestamps for a single Codex baseline episode",
    )
    args = parser.parse_args(argv)

    payload = run_analysis(
        args.input_path,
        args.out,
        attempt_policy=args.attempt_policy,
        compare_path=args.compare,
        combined_trace=args.combined_trace,
        viztracer_path=args.viztracer,
        viztracer_offset_s=args.viztracer_offset_s,
        viztracer_max_events=args.viztracer_max_events,
        codex_session_path=args.codex_session,
    )
    if payload.get("status") == "no_artifacts_found":
        print(f"[WARN] No result.json artifacts found under {args.input_path}")
        return 2
    ov = payload["overall"]
    print(
        f"[OK] Analyzed {ov['episodes']} episode(s) -> {args.out} "
        f"(success={ov['outcomes']['success']}, failure={ov['outcomes']['failure']}, "
        f"timeout={ov['outcomes']['timeout']}, infra_error={ov['outcomes']['infra_error']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
