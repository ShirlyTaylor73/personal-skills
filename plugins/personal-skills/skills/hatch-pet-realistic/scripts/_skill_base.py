"""共享：skill 根目录与模型缓存路径定位。

被 matte_frames.py、warmup_models.py 和未来的脚本 import。
副作用：import 时会设置 U2NET_HOME 环境变量并 mkdir <skill>/models/。
**必须在 `import rembg` 之前 import 本模块。**
"""
from __future__ import annotations

import os
from pathlib import Path

SKILL_BASE = Path(__file__).resolve().parent.parent
MODELS_DIR = SKILL_BASE / "models"
MODEL_NAME = "u2net_human_seg"
MODEL_FILE = MODELS_DIR / f"{MODEL_NAME}.onnx"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("U2NET_HOME", str(MODELS_DIR))
