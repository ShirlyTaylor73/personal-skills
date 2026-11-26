#!/usr/bin/env python3
"""Launch or stop a detached local background HTTP server for an analysis output directory.

Serves pipeline_timeline.html (and sibling analysis artifacts) read-only on localhost
so the user can click the printed URL directly in chat.
Zero external dependencies (Python 3.10+ standard library only).
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

STATE_FILENAME = ".timeline_server.json"


def _is_pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _is_port_open(host: str, port: int, timeout: float = 0.25) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((host, port)) == 0


def _pick_free_port(host: str, preferred_port: int | None) -> int:
    candidates: list[int] = []
    if preferred_port and preferred_port > 0:
        candidates.append(preferred_port)
    candidates.extend(range(8765, 8800))
    for port in candidates:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
                return port
            except OSError:
                continue
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


def _read_state(out_dir: Path) -> dict | None:
    state_path = out_dir / STATE_FILENAME
    if not state_path.is_file():
        return None
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def stop_server(out_dir: Path) -> bool:
    state = _read_state(out_dir)
    state_path = out_dir / STATE_FILENAME
    if not state:
        return False
    pid = int(state.get("pid") or 0)
    stopped = False
    if _is_pid_alive(pid):
        try:
            os.kill(pid, signal.SIGTERM)
            stopped = True
        except OSError:
            pass
    try:
        state_path.unlink(missing_ok=True)
    except OSError:
        pass
    return stopped


def start_server(
    out_dir: Path,
    *,
    host: str = "127.0.0.1",
    port: int | None = None,
    html_file: str = "pipeline_timeline.html",
) -> dict:
    out_resolved = out_dir.resolve()
    target = out_resolved / html_file
    if not target.is_file():
        raise FileNotFoundError(f"HTML file not found: {target}")

    # Reuse an already-running server for the same output directory & host
    existing = _read_state(out_resolved)
    if existing:
        ex_pid = int(existing.get("pid") or 0)
        ex_host = str(existing.get("host") or host)
        ex_port = int(existing.get("port") or 0)
        if (
            ex_host == host
            and (port is None or port == 0 or ex_port == port)
            and _is_pid_alive(ex_pid)
            and _is_port_open(ex_host, ex_port)
        ):
            return {
                "status": "already_running",
                "pid": ex_pid,
                "host": ex_host,
                "port": ex_port,
                "url": f"http://{ex_host}:{ex_port}/{html_file}",
                "directory": str(out_resolved),
            }

    chosen_port = _pick_free_port(host, port)
    cmd = [
        sys.executable,
        "-m",
        "http.server",
        str(chosen_port),
        "--bind",
        host,
        "--directory",
        str(out_resolved),
    ]
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
        close_fds=True,
    )

    deadline = time.monotonic() + 3.0
    ready = False
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(
                f"Background http.server exited early with code {proc.returncode}"
            )
        if _is_port_open(host, chosen_port):
            ready = True
            break
        time.sleep(0.05)

    if not ready:
        proc.terminate()
        raise RuntimeError(f"Timed out waiting for http.server on {host}:{chosen_port}")

    info = {
        "status": "started",
        "pid": proc.pid,
        "host": host,
        "port": chosen_port,
        "url": f"http://{host}:{chosen_port}/{html_file}",
        "directory": str(out_resolved),
    }
    (out_resolved / STATE_FILENAME).write_text(
        json.dumps(info, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return info


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Start or stop a detached local HTTP server for pipeline_timeline.html."
    )
    parser.add_argument("out_dir", type=Path, help="Analysis output directory containing the HTML file")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="Preferred TCP port (default: auto-pick free port starting at 8765)",
    )
    parser.add_argument(
        "--file",
        default="pipeline_timeline.html",
        help="HTML filename inside out_dir (default: pipeline_timeline.html)",
    )
    parser.add_argument(
        "--stop",
        action="store_true",
        help="Stop a previously started background server for out_dir",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output",
    )
    args = parser.parse_args(argv)

    if args.stop:
        stopped = stop_server(args.out_dir.resolve())
        if args.json:
            print(json.dumps({"stopped": stopped, "directory": str(args.out_dir.resolve())}))
        else:
            print(
                f"[OK] Stopped background server for {args.out_dir}"
                if stopped
                else f"[INFO] No running background server recorded for {args.out_dir}"
            )
        return 0

    info = start_server(
        args.out_dir,
        host=args.host,
        port=args.port or None,
        html_file=args.file,
    )
    if args.json:
        print(json.dumps(info, ensure_ascii=False))
    else:
        print(f"[OK] {info['status']}: {info['url']} (pid={info['pid']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
