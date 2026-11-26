#!/usr/bin/env python3
"""Offline unit & fixture tests for rollout-timeline-analysis."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_rollout as ar  # noqa: E402


def _write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")


class TestIntervalAlgebra(unittest.TestCase):
    def test_union_and_overlap_never_double_count(self) -> None:
        http = [
            (0, 10_000_000_000),
            (5_000_000_000, 15_000_000_000),
            (20_000_000_000, 30_000_000_000),
        ]
        # Cumulative = 10 + 10 + 10 = 30s; Union = [0,15] + [20,30] = 25s
        u = ar.union_intervals(http)
        self.assertEqual(u, [(0, 15_000_000_000), (20_000_000_000, 30_000_000_000)])
        self.assertEqual(ar.total_interval_ns(u), 25_000_000_000)

        robot = [(10_000_000_000, 22_000_000_000), (18_000_000_000, 25_000_000_000)]
        # Robot union = [10,25] = 15s; HTTP ∩ Robot = [10,15] + [20,25] = 10s
        inter = ar.intersect_intervals(http, robot)
        self.assertEqual(
            inter, [(10_000_000_000, 15_000_000_000), (20_000_000_000, 25_000_000_000)]
        )
        self.assertEqual(ar.total_interval_ns(inter), 10_000_000_000)


class TestFixtureEndToEnd(unittest.TestCase):
    def _create_graph_episode(self, root: Path) -> Path:
        ep_dir = root / "libero" / "task_a" / "attempt-01"
        pol = ep_dir / "policy" / "task_a"
        t0 = 1_795_000_000.0

        _write_json(
            ep_dir / "run.json",
            {
                "robot": "libero",
                "id": "task_a",
                "run_id": "run-fixture-1",
                "attempt": 1,
                "status": "success",
                "started_at": t0 - 10.0,
                "process_wall_time_s": 55.0,
                "source_commit": "deadbeef",
                "source_worktree_dirty": False,
                "settings": {
                    "arm": "graph",
                    "runtime": "openai",
                    "model": "gpt-6-astra",
                    "reasoning_effort": "xhigh",
                    "max_turns": 40,
                    "budget_s": 7200,
                },
            },
        )
        _write_json(
            pol / "result.json",
            {
                "arm": "graph",
                "robot": "libero",
                "suite": "libero_spatial_task",
                "model": "gpt-6-astra",
                "reasoning_effort": "xhigh",
                "max_turns": 40,
                "environment_success": True,
                "status": "completed",
                "policy_wall_s": 40.0,
                "startup_s": 10.0,
                "total_wall_s": 55.0,
                "calls": 2,
                "stateful_calls": 2,
                "env_steps_total": 30,
                "generation": {
                    "runtime": "openai",
                    "model": "gpt-6-astra",
                    "elapsed_s": 40.0,
                    "usage_status": "partial",
                    "input_tokens": None,
                    "output_tokens": None,
                    "total_tokens": None,
                    "known_usage": {
                        "prompt": 1000,
                        "completion": 100,
                        "cached": 500,
                        "reasoning": 20,
                    },
                },
                "graph": {"drained": True, "decisions_used": 1, "jobs": []},
                "timing": {
                    "schema_version": 1,
                    "source": "rpent_env_handlers",
                    "timing_status": "complete",
                    "rollout_wall_time_s": 40.0,
                    "simulator_wall_time_s": 6.0,
                    "rollout_excluding_sim_s": 34.0,
                    "intervals": [
                        {
                            "wall_ns": 40_000_000_000,
                            "sim_ns": 6_000_000_000,
                            "start_snapshot": {"server_id": "srv1", "elapsed_ns": 0},
                            "end_snapshot": {"server_id": "srv1", "elapsed_ns": 6_000_000_000},
                        }
                    ],
                },
            },
        )
        # Req 1 [0,10] ok; Tool python_start [10,10.2];
        # Req 2 [10.2,15.2] HTTP 500 fail; Req 3 [15.5,25.5] attempt=2 retry ok (missing usage);
        # Req 4 [25.6,30.0] cancelled;
        # Meanwhile Graph job runs from 10.2 to 24.0 with robot action [11.0,17.0] overlapping Req 2 & Req 3!
        _write_jsonl(
            pol / "openai_events.jsonl",
            [
                {"t": 0.0, "type": "request_started", "request_id": 1, "attempt": 1, "messages": 1},
                {
                    "t": 10.0,
                    "type": "request",
                    "request_id": 1,
                    "attempt": 1,
                    "status_code": 200,
                    "latency_s": 10.0,
                    "ok": True,
                    "usage": {
                        "prompt_tokens": 1000,
                        "completion_tokens": 100,
                        "prompt_tokens_details": {"cached_tokens": 500},
                        "completion_tokens_details": {"reasoning_tokens": 20},
                    },
                    "error": None,
                },
                {
                    "t": 10.0,
                    "type": "assistant",
                    "tool_calls": ["python_start"],
                    "finish_reason": "tool_calls",
                },
                {
                    "t": 10.2,
                    "type": "tool",
                    "tool": "python_start",
                    "call_id": "c1",
                    "elapsed_s": 0.2,
                    "ok": True,
                    "images": 0,
                },
                {
                    "t": 10.2,
                    "type": "request_started",
                    "request_id": 2,
                    "attempt": 1,
                    "messages": 3,
                },
                {
                    "t": 15.2,
                    "type": "request",
                    "request_id": 2,
                    "attempt": 1,
                    "status_code": 500,
                    "latency_s": 5.0,
                    "ok": False,
                    "usage": None,
                    "error": "upstream 500",
                },
                {
                    "t": 15.5,
                    "type": "request_started",
                    "request_id": 3,
                    "attempt": 2,
                    "messages": 3,
                },
                {
                    "t": 25.5,
                    "type": "request",
                    "request_id": 3,
                    "attempt": 2,
                    "status_code": 200,
                    "latency_s": 10.0,
                    "ok": True,
                    "usage": None,
                    "error": None,
                },
                {
                    "t": 25.6,
                    "type": "request_started",
                    "request_id": 4,
                    "attempt": 1,
                    "messages": 5,
                },
                {
                    "t": 30.0,
                    "type": "request_cancelled",
                    "request_id": 4,
                    "attempt": 1,
                    "latency_s": 4.4,
                    "usage": None,
                    "reason": "episode_end",
                },
            ],
        )
        _write_jsonl(
            pol / "lifecycle.jsonl",
            [
                {"stage": "graph_drain_started", "timestamp": t0 + 39.0, "monotonic": 100.0},
                {
                    "stage": "graph_drain_finished",
                    "timestamp": t0 + 39.5,
                    "monotonic": 100.5,
                    "drained": True,
                },
                {"stage": "messages_write_started", "timestamp": t0 + 39.6, "monotonic": 100.6},
                {"stage": "messages_write_finished", "timestamp": t0 + 40.0, "monotonic": 101.0},
            ],
        )
        _write_jsonl(
            pol / "calls.jsonl",
            [
                {
                    "index": 0,
                    "tool": "move_to",
                    "started_at": t0 + 11.0,
                    "elapsed_s": 6.0,
                    "ok": True,
                    "stateful": True,
                    "env_steps": 30,
                }
            ],
        )
        _write_jsonl(
            pol / "workspace" / "execution" / "job12345678" / "events.jsonl",
            [
                {
                    "job_id": "job12345678",
                    "event_seq": 1,
                    "kind": "started",
                    "plan_revision": 1,
                    "timestamp": t0 + 10.2,
                },
                {
                    "job_id": "job12345678",
                    "event_seq": 2,
                    "kind": "unit_started",
                    "plan_revision": 1,
                    "unit_id": "u1",
                    "instance_id": 1,
                    "primitive": "move_to",
                    "timestamp": t0 + 10.5,
                },
                {
                    "job_id": "job12345678",
                    "event_seq": 3,
                    "kind": "action_completed",
                    "plan_revision": 1,
                    "unit_id": "u1",
                    "instance_id": 1,
                    "elapsed_s": 6.0,
                    "env_steps": 30,
                    "timestamp": t0 + 17.0,
                },
                {
                    "job_id": "job12345678",
                    "event_seq": 4,
                    "kind": "unit_completed",
                    "plan_revision": 1,
                    "unit_id": "u1",
                    "instance_id": 1,
                    "timestamp": t0 + 17.1,
                },
                {
                    "job_id": "job12345678",
                    "event_seq": 5,
                    "kind": "pause_requested",
                    "plan_revision": 1,
                    "timestamp": t0 + 18.0,
                },
                {
                    "job_id": "job12345678",
                    "event_seq": 6,
                    "kind": "graph_patched",
                    "plan_revision": 2,
                    "changed": ["u2"],
                    "timestamp": t0 + 19.0,
                },
                {
                    "job_id": "job12345678",
                    "event_seq": 7,
                    "kind": "resumed",
                    "plan_revision": 2,
                    "timestamp": t0 + 20.0,
                },
                {
                    "job_id": "job12345678",
                    "event_seq": 8,
                    "kind": "cancelled",
                    "plan_revision": 2,
                    "timestamp": t0 + 24.0,
                },
            ],
        )
        return ep_dir

    def _create_codex_baseline_episode(self, root: Path) -> Path:
        ep_dir = root / "task_a"
        _write_json(
            ep_dir / "result.json",
            {
                "arm": "cells",
                "robot": "libero",
                "model": "gpt-6-astra",
                "reasoning_effort": "xhigh",
                "max_turns": 40,
                "environment_success": True,
                "status": "completed",
                "policy_wall_s": 100.0,
                "startup_s": 12.0,
                "total_wall_s": 115.0,
                "generation": {
                    "turns": 1,
                    "input_tokens": 5000,
                    "cached_input_tokens": 2000,
                    "output_tokens": 300,
                    "reasoning_output_tokens": 50,
                    "total_tokens": 5300,
                },
            },
        )
        _write_jsonl(
            ep_dir / "codex_events.jsonl",
            [
                {"type": "thread.started", "thread_id": "th1"},
                {"type": "turn.started"},
                {
                    "type": "item.completed",
                    "item": {
                        "id": "i1",
                        "type": "mcp_tool_call",
                        "tool": "python",
                        "status": "completed",
                    },
                },
                {"type": "turn.completed", "usage": {"input_tokens": 5000, "output_tokens": 300}},
            ],
        )
        _write_jsonl(
            ep_dir / "calls.jsonl",
            [
                {
                    "index": 0,
                    "tool": "move_to",
                    "started_at": 1_793_000_010.0,
                    "elapsed_s": 4.0,
                    "ok": True,
                    "stateful": True,
                    "env_steps": 20,
                }
            ],
        )
        return ep_dir

    def test_graph_overlap_failures_viztracer_and_comparison(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            graph_root = tmp_path / "graph_run"
            base_root = tmp_path / "baseline_run"
            out_dir = tmp_path / "analysis_out"
            ep_dir = self._create_graph_episode(graph_root)
            self._create_codex_baseline_episode(base_root)

            # Create an uncalibrated VizTracer JSON
            viz_path = tmp_path / "viz.json"
            _write_json(
                viz_path,
                {
                    "traceEvents": [
                        {
                            "ph": "X",
                            "name": "worker_loop",
                            "ts": 100000.0,
                            "dur": 2500.0,
                            "pid": 99,
                            "tid": 1,
                            "cat": "FEE",
                        }
                    ]
                },
            )

            # Single episode with VizTracer + comparison against baseline
            payload = ar.run_analysis(
                ep_dir,
                out_dir,
                compare_path=base_root,
                viztracer_path=viz_path,
            )

            ep = payload["episodes"][0]
            # HTTP requests: 10s + 5s + 10s + 4.4s = 29.4s
            self.assertAlmostEqual(ep["timings_s"]["http_cumulative_s"], 29.4, places=3)
            self.assertAlmostEqual(ep["timings_s"]["agent_inference_s"], 29.4, places=3)
            self.assertEqual(ep["agent_inference_basis"], "http_measured")
            self.assertIsNotNone(ep["timings_s"]["tool_execution_s"])
            self.assertIn("agent_rounds", ep["counts"])
            rep_text = (out_dir / "report.md").read_text(encoding="utf-8")
            self.assertIn("Agent Inference 均值 (s)", rep_text)
            self.assertIn("Tool Execution 均值 (s)", rep_text)
            self.assertAlmostEqual(ep["timings_s"]["http_critical_path_s"], 29.4, places=3)
            # Robot action [11.0, 17.0] overlaps Req2 [10.2, 15.2] by 4.2s and Req3 [15.5, 25.5] by 1.5s => 5.7s
            self.assertAlmostEqual(ep["timings_s"]["robot_action_union_s"], 6.0, places=3)
            self.assertAlmostEqual(ep["timings_s"]["http_robot_overlap_s"], 5.7, places=3)
            # Failures, retries, cancellations, partial usage preserved without filling 0
            self.assertEqual(ep["http"]["requests_failed"], 1)
            self.assertEqual(ep["http"]["retry_attempts"], 1)
            self.assertEqual(ep["http"]["requests_cancelled"], 1)
            self.assertEqual(ep["http"]["missing_usage_requests"], 3)
            self.assertEqual(ep["tokens"]["usage_status"], "partial")
            self.assertIsNone(ep["tokens"]["total_tokens"])
            self.assertEqual(ep["tokens"]["known_usage"]["prompt"], 1000)
            # Graph pause, revision, cancel, drain visible
            self.assertEqual(ep["graph"]["pauses"], 1)
            self.assertEqual(ep["graph"]["revisions"], 1)
            self.assertEqual(ep["graph"]["cancellations"], 1)
            self.assertAlmostEqual(ep["timings_s"]["lifecycle_s"]["graph_drain"], 0.5, places=3)
            # Uncalibrated VizTracer kept in separate lane
            self.assertEqual(ep["viztracer"]["clock_domain"], "viztracer_uncalibrated")
            self.assertFalse(ep["viztracer"]["calibrated"])
            # Cross-runtime comparison forced to system_level
            self.assertEqual(payload["comparison"]["comparison_scope"], "system_level")
            self.assertIn("runtime", payload["comparison"]["confounders"])

            # Verify Perfetto trace JSON validity, aligned 4-track layout, HTML viewer, and flow links
            trace_file = out_dir / payload["trace_paths"][ep["key"]]
            pf = json.loads(trace_file.read_text(encoding="utf-8"))
            self.assertIn("traceEvents", pf)
            flow_starts = [e for e in pf["traceEvents"] if e.get("ph") == "s"]
            flow_ends = [e for e in pf["traceEvents"] if e.get("ph") == "f"]
            self.assertGreaterEqual(len(flow_starts), 3)  # req->tool, tool->job, action->robot
            self.assertEqual(len(flow_starts), len(flow_ends))
            proc_names = {
                e["args"]["name"]
                for e in pf["traceEvents"]
                if e.get("ph") == "M" and e.get("name") == "process_name"
            }
            for expected_proc in ("Agent Inference", "Tool Execution", "Policy Job", "Policy / Robot"):
                self.assertIn(expected_proc, proc_names)
            self.assertNotIn("Graph Manager", proc_names)
            self.assertNotIn("Pipeline State", proc_names)

            # Verify compare (Codex baseline) Perfetto trace also uses aligned track names
            self.assertIsNotNone(payload.get("compare_trace_paths"))
            cmp_key = next(iter(payload["compare_trace_paths"].keys()))
            cmp_pf = json.loads(
                (out_dir / payload["compare_trace_paths"][cmp_key]).read_text(encoding="utf-8")
            )
            cmp_proc_names = {
                e["args"]["name"]
                for e in cmp_pf["traceEvents"]
                if e.get("ph") == "M" and e.get("name") == "process_name"
            }
            for expected_proc in ("Agent Inference", "Tool Execution", "Policy / Robot"):
                self.assertIn(expected_proc, cmp_proc_names)

            # Verify HTML viewer embeds the exact 4 aligned lanes on both sides
            html_file = out_dir / payload["pipeline_timeline_html"]
            self.assertTrue(html_file.is_file())
            html_text = html_file.read_text(encoding="utf-8")
            marker = "const DATA = "
            idx_start = html_text.index(marker) + len(marker)
            idx_end = html_text.index(";\nconst LABEL_W", idx_start)
            viewer_data = json.loads(html_text[idx_start:idx_end])
            ep_id = ep["episode_id"]
            p_lanes = [lane["name"] for lane in viewer_data["primary"][ep_id]["lanes"]]
            o_lanes = [lane["name"] for lane in viewer_data["other"][ep_id]["lanes"]]
            lanes4 = ["Agent Inference", "Tool Execution", "Policy Job", "Policy / Robot"]
            self.assertEqual(p_lanes, lanes4)
            self.assertEqual(o_lanes, lanes4)
            # Ours: Agent lane = measured HTTP rounds; Tool lane = dispatch->return markers
            p_agent_labels = [it["l"] for it in viewer_data["primary"][ep_id]["lanes"][0]["items"]]
            self.assertTrue(any(lbl.startswith("R1 ·") for lbl in p_agent_labels))
            p_tool_items = viewer_data["primary"][ep_id]["lanes"][1]["items"]
            self.assertTrue(
                any(it["l"] == "python_start" and it.get("k") == "m" for it in p_tool_items)
            )
            self.assertFalse(any(it["l"].startswith("R1→") for it in p_tool_items))
            o_tool_labels = [it["l"] for it in viewer_data["other"][ep_id]["lanes"][1]["items"]]
            self.assertTrue(any(lbl.startswith("Cell #") for lbl in o_tool_labels))
            self.assertEqual(
                viewer_data["other"][ep_id]["lanes"][2]["emptyNote"],
                "Sync mode (no async policy job)",
            )

            # Verify background HTTP server CLI stays alive after exit, serves HTML, and stops cleanly
            import subprocess
            import urllib.request

            serve_script = Path(__file__).resolve().parent / "serve_timeline.py"
            res = subprocess.run(
                [sys.executable, str(serve_script), str(out_dir), "--json"],
                check=True,
                capture_output=True,
                text=True,
            )
            srv = json.loads(res.stdout)
            try:
                self.assertEqual(srv["status"], "started")
                with urllib.request.urlopen(srv["url"], timeout=3) as resp:
                    self.assertEqual(resp.status, 200)
                    body = resp.read().decode("utf-8")
                    self.assertIn("Rollout Pipeline Timeline Viewer", body)
                res_again = subprocess.run(
                    [sys.executable, str(serve_script), str(out_dir), "--json"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                srv_again = json.loads(res_again.stdout)
                self.assertEqual(srv_again["status"], "already_running")
                self.assertEqual(srv_again["pid"], srv["pid"])
            finally:
                stop_res = subprocess.run(
                    [sys.executable, str(serve_script), str(out_dir), "--stop", "--json"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertTrue(json.loads(stop_res.stdout)["stopped"])

            # Refuse overwriting inside input directory
            with self.assertRaises(ValueError):
                ar.run_analysis(ep_dir, ep_dir / "nested_out")

    def test_codex_model_sessions_anchor_rounds_and_failed_attempts(self) -> None:
        import datetime

        t0 = 1_793_000_000.0

        def iso(offset: float) -> str:
            dt = datetime.datetime.fromtimestamp(t0 + offset, datetime.timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

        def ev(offset: float, rtype: str, payload: dict) -> dict:
            return {"timestamp": iso(offset), "type": rtype, "payload": payload}

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = tmp_path / "baseline_run"
            ep_dir = root / "task_a"
            _write_json(
                ep_dir / "result.json",
                {
                    "arm": "cells",
                    "robot": "libero",
                    "environment_success": True,
                    "status": "completed",
                    "policy_wall_s": 32.0,
                    "generation": {"thread_ids": ["th-fail", "th-ok"]},
                },
            )
            # attempt 1: planner failure (model at capacity); attempt 2: python cell then finish
            _write_jsonl(
                ep_dir / "model_sessions" / "rollout-2026-th-fail.jsonl",
                [
                    ev(0.0, "event_msg", {"type": "task_started"}),
                    ev(
                        3.0,
                        "event_msg",
                        {"type": "task_complete", "error": {"message": "at capacity"}},
                    ),
                ],
            )
            _write_jsonl(
                ep_dir / "model_sessions" / "rollout-2026-th-ok.jsonl",
                [
                    ev(10.0, "event_msg", {"type": "task_started"}),
                    ev(14.0, "response_item", {"type": "function_call", "name": "python", "call_id": "c1"}),
                    ev(16.0, "response_item", {"type": "function_call_output", "call_id": "c1"}),
                    ev(21.0, "response_item", {"type": "function_call", "name": "finish", "call_id": "c2"}),
                    ev(21.1, "response_item", {"type": "function_call_output", "call_id": "c2"}),
                    ev(30.0, "event_msg", {"type": "task_complete"}),
                ],
            )
            # a stale session from another run must not be mixed in
            _write_jsonl(
                ep_dir / "model_sessions" / "rollout-2026-other.jsonl",
                [ev(500.0, "event_msg", {"type": "task_started"})],
            )
            _write_jsonl(
                ep_dir / "calls.jsonl",
                [
                    {
                        "index": 0,
                        "tool": "move_to",
                        "started_at": t0 + 14.5,
                        "elapsed_s": 1.0,
                        "ok": True,
                        "stateful": True,
                        "env_steps": 10,
                    }
                ],
            )

            out_dir = tmp_path / "out"
            payload = ar.run_analysis(root, out_dir)
            ep = payload["episodes"][0]
            self.assertEqual(ep["clock_alignment"]["clock_domain"], "codex_session_aligned")
            self.assertEqual(ep["clock_alignment"]["epoch_t0"], t0)  # first task_started, not first call
            self.assertEqual(ep["codex_session"]["failed_attempts"], 1)
            self.assertEqual(ep["codex_session"]["rounds"], 3)  # R1->python, R2->finish, R3 final reply
            self.assertEqual(ep["codex_session"]["sessions"].count("rollout-2026-other.jsonl"), 0)
            self.assertAlmostEqual(ep["codex_session"]["anchor_check_s"], 0.5, places=3)
            # unified Agent Inference / Tool Execution metrics shared by HTML meta and report.md
            self.assertEqual(ep["agent_inference_basis"], "codex_session_measured")
            # rounds [10,14] + [16,21] + [21.1,30] + failed attempt [0,3] (backoff excluded)
            self.assertAlmostEqual(ep["timings_s"]["agent_inference_s"], 3.0 + 4.0 + 5.0 + 8.9, places=2)
            # tool execution: python cell [14,16] + finish [21,21.1]
            self.assertAlmostEqual(ep["timings_s"]["tool_execution_s"], 2.1, places=2)
            self.assertEqual(ep["counts"]["agent_rounds"], 3)
            self.assertIsNone(ep["counts"]["wait_event_rounds"])
            self.assertNotIn("codex_events_no_per_request_timestamps", ep["missing_data"])
            report_text = (out_dir / "report.md").read_text(encoding="utf-8")
            self.assertIn("Agent Inference", report_text)
            self.assertIn("Codex session 逐轮（实测，非 HTTP 口径）", report_text)
            self.assertIn("Codex session 逐轮还原", report_text)

            rows = [
                json.loads(line)
                for line in (out_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            pipe = {
                r["event_type"]: [x for x in rows if x["event_type"] == r["event_type"]]
                for r in rows
                if r["process"] == "pipeline_state"
            }
            rounds = pipe["pipeline:baseline_round"]
            expected = [(10.0, 14.0), (16.0, 21.0), (21.1, 30.0)]
            self.assertEqual(len(rounds), len(expected))
            for r, (es, ee) in zip(rounds, expected, strict=True):
                self.assertAlmostEqual(r["start_ns"] / 1e9, es, places=3)
                self.assertAlmostEqual(r["end_ns"] / 1e9, ee, places=3)
            self.assertEqual([r["args"]["tool"] for r in rounds], ["python", "finish", None])
            self.assertAlmostEqual(pipe["pipeline:baseline_attempt_error"][0]["end_ns"] / 1e9, 3.0, places=3)
            backoff = pipe["pipeline:baseline_backoff"][0]
            self.assertAlmostEqual(backoff["start_ns"] / 1e9, 3.0, places=3)
            self.assertAlmostEqual(backoff["end_ns"] / 1e9, 10.0, places=3)
            cell = pipe["pipeline:baseline_cell_exec"][0]
            self.assertEqual(cell["args"]["calls"], 1)
            self.assertEqual(cell["args"]["stateful_tools"], ["move_to"])
            self.assertEqual(pipe["pipeline:baseline_tool_exec"][0]["args"]["tool"], "finish")
            self.assertAlmostEqual(
                pipe["pipeline:baseline_unattributed_tail"][0]["end_ns"] / 1e9, 32.0, places=3
            )

            html_text = (out_dir / payload["pipeline_timeline_html"]).read_text(encoding="utf-8")
            marker = "const DATA = "
            start = html_text.index(marker) + len(marker)
            data = json.loads(html_text[start : html_text.index(";\nconst LABEL_W", start)])
            lanes = data["primary"][ep["episode_id"]]["lanes"]
            self.assertEqual(lanes[0]["sub"], "model rounds from Codex session (measured)")
            self.assertIn("R1 · 4.0s", [it["l"] for it in lanes[0]["items"]])
            self.assertTrue(any(it["l"].startswith("att1 err") for it in lanes[0]["items"]))
            self.assertFalse(any(it.get("hatch") for it in lanes[0]["items"] if it["l"].startswith("R")))

    def test_missing_artifacts_returns_missing_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            empty_in = tmp_path / "empty"
            empty_in.mkdir()
            out_dir = tmp_path / "out"
            res = ar.run_analysis(empty_in, out_dir)
            self.assertEqual(res["status"], "no_artifacts_found")
            self.assertTrue((out_dir / "report.md").is_file())


if __name__ == "__main__":
    unittest.main()
