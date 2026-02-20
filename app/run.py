#!/usr/bin/env python3
"""
run.py — single entry-point for the Aureon / ACE-Step production server.

Starts the FastAPI application (acestep.api_server) which serves:
  • Studio web frontend  →  GET /  (redirect to /studio)
  •                         GET /studio
  • REST API             →  POST /release_task, POST /query_result, ...
  • Audio download       →  GET /v1/audio
  • Health / monitoring  →  GET /health, GET /v1/stats

Both the frontend (studio.html) and the API backend are served on the
same port — default 3297 — so no reverse proxy is needed.

Usage
-----
    # With the conda/pip environment activated:
    python run.py

    # Custom host / port:
    python run.py --host 0.0.0.0 --port 3297

    # All options (same as api_server CLI):
    python run.py --help

Environment variables (override any CLI default)
-------------------------------------------------
    ACESTEP_API_HOST        bind host  (default: 0.0.0.0)
    ACESTEP_API_PORT        bind port  (default: 3297)
    ACESTEP_API_KEY         optional API auth key
    ACESTEP_CONFIG_PATH     DiT model directory name
    ACESTEP_LM_MODEL_PATH   5Hz-LM model directory name
    ACESTEP_DEVICE          cuda / cpu / auto
    ACESTEP_NO_INIT         true → skip model loading at startup
    ACESTEP_DOWNLOAD_SOURCE huggingface / modelscope / auto

Docker
------
    docker build -t ace-step:latest .
    docker run --gpus all -p 3297:3297 --env-file .env ace-step:latest
"""
from __future__ import annotations

import os
import sys

# ---------------------------------------------------------------------------
# Load .env from project root before anything else so every subsequent
# os.getenv() call in api_server picks up the correct values.
# ---------------------------------------------------------------------------
_ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_ENV_FILE):
    try:
        from dotenv import load_dotenv
        load_dotenv(_ENV_FILE, override=False)  # env vars already set take precedence
    except ImportError:
        pass  # python-dotenv is optional; values from the shell env still work

# ---------------------------------------------------------------------------
# Default port — must be set before api_server imports so that the module-
# level os.getenv("ACESTEP_API_PORT", "3297") inside main() picks it up.
# ---------------------------------------------------------------------------
os.environ.setdefault("ACESTEP_API_PORT", "3297")
os.environ.setdefault("ACESTEP_API_HOST", "0.0.0.0")

# ---------------------------------------------------------------------------
# Delegate fully to the api_server CLI (parses --host / --port / --api-key
# etc.).  Passing sys.argv[1:] lets callers override defaults on the command
# line while the environment-variable defaults above act as the fallback.
# ---------------------------------------------------------------------------
from acestep.api_server import main  # noqa: E402 (import after env setup intentional)

if __name__ == "__main__":
    # Resolve effective host/port for the startup banner.
    host = os.environ.get("ACESTEP_API_HOST", "0.0.0.0")
    port = int(os.environ.get("ACESTEP_API_PORT", "3297"))

    # Show human-readable access URLs before uvicorn output takes over.
    display_host = "localhost" if host in ("0.0.0.0", "::") else host
    print(f"\n{'=' * 60}")
    print(f"  Aureon · ACE-Step Production Server")
    print(f"{'=' * 60}")
    print(f"  Studio  →  http://{display_host}:{port}/")
    print(f"  API     →  http://{display_host}:{port}/release_task")
    print(f"  Health  →  http://{display_host}:{port}/health")
    print(f"  Models  →  http://{display_host}:{port}/v1/models")
    print(f"{'=' * 60}\n")

    main()
