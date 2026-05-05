#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "rembg[cpu]>=2.0.50",
# ]
# ///
"""
预热：触发 rembg 下载 u2net_human_seg.onnx 到 <skill-base>/models/。
首次运行约 30-60 秒（取决于网速）；后续幂等，发现已存在直接退出。
"""
from __future__ import annotations

import sys
from pathlib import Path

# 让 _skill_base 可被作为脚本入口直接 import（不依赖 cwd / sys.path 默认）
sys.path.insert(0, str(Path(__file__).resolve().parent))

# IMPORTANT: 必须在 import rembg 之前 import _skill_base，它设置 U2NET_HOME
from _skill_base import MODEL_FILE, MODEL_NAME  # noqa: E402


def main() -> int:
    if MODEL_FILE.is_file():
        print(f"already cached: {MODEL_FILE} ({MODEL_FILE.stat().st_size // 1024 // 1024} MB)")
        return 0
    print(f"downloading {MODEL_NAME} to {MODEL_FILE}...")
    from rembg import new_session
    new_session(MODEL_NAME)  # 触发下载
    if MODEL_FILE.is_file():
        print(f"ok: {MODEL_FILE.stat().st_size // 1024 // 1024} MB")
        return 0
    print("ERROR: model download did not produce expected file", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
