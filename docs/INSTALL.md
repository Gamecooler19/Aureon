# Installation Guide

---

## Requirements

| Item | Requirement |
|------|-------------|
| Python | 3.11–3.12 (stable release, not pre-release) |
| GPU | CUDA GPU recommended; MPS / ROCm / Intel XPU / CPU also supported |
| VRAM | ≥4 GB for DiT-only mode; ≥6 GB for LLM+DiT |
| Disk | ~10 GB for core models |

---

## Quick Start — Local (All Platforms)

### 1. Clone

```bash
git clone https://github.com/Blu3scr3en/Aureon.git
cd Aureon
```

### 2. Install

**Recommended — conda:**

```bash
conda create -n aureon python=3.11 -y
conda activate aureon
pip install -e .
```

**Alternative — uv:**

```bash
uv sync
```

**Alternative — plain pip (venv):**

```bash
python3.11 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

### 3. Launch

```bash
python run.py
```

Models are downloaded automatically on first run.  
Open **http://localhost:3297** in your browser.

---

## Quick Start — Docker Compose

```bash
# Copy example env and edit as needed
cp .env.example .env

# Build & start (first run downloads models inside the container)
docker compose up -d --build

# Stream logs
docker compose logs -f app

# Stop
docker compose down
```

Studio UI: **http://localhost:3297**

> **GPU requirement:** Docker GPU access requires [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

---

## Quick Start — Docker (standalone)

```bash
docker build -t blu3scr33n-music:latest .
docker run --gpus all -p 3297:3297 --env-file .env blu3scr33n-music:latest
```

---

## Environment Variables

Create a `.env` file in the project root. `run.py`, `docker compose`, and the Dockerfile all load it automatically.

```bash
# .env — all values are optional (shown with defaults)

# Server
ACESTEP_API_PORT=3297
ACESTEP_API_HOST=0.0.0.0
ACESTEP_API_KEY=              # leave empty to disable auth

# Model selection
ACESTEP_CONFIG_PATH=acestep-v15-turbo
ACESTEP_LM_MODEL_PATH=acestep-5Hz-lm-0.6B
ACESTEP_INIT_LLM=auto         # auto | true | false
ACESTEP_DEVICE=auto
ACESTEP_LM_BACKEND=pt         # pt | vllm | mlx
ACESTEP_DOWNLOAD_SOURCE=auto  # auto | huggingface | modelscope

# Low-VRAM options
ACESTEP_OFFLOAD_TO_CPU=false
```

### Key Variable Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `ACESTEP_API_PORT` | `3297` | Server port |
| `ACESTEP_API_HOST` | `0.0.0.0` | Bind address (`127.0.0.1` for local-only) |
| `ACESTEP_API_KEY` | *(empty)* | Bearer token; leave empty to disable auth |
| `ACESTEP_CONFIG_PATH` | `acestep-v15-turbo` | DiT model path |
| `ACESTEP_LM_MODEL_PATH` | `acestep-5Hz-lm-0.6B` | LM model path |
| `ACESTEP_INIT_LLM` | `auto` | `auto` detects GPU; `true`/`false` forces on/off |
| `ACESTEP_DEVICE` | `auto` | `cuda`, `mps`, `cpu`, or `auto` |
| `ACESTEP_LM_BACKEND` | `pt` | `vllm` (faster), `pt` (safer), `mlx` (Apple) |
| `ACESTEP_DOWNLOAD_SOURCE` | `auto` | `huggingface` or `modelscope` |

### `ACESTEP_INIT_LLM` Behavior

| Value | Behavior |
|-------|----------|
| `auto` (default) | Auto-detect based on available VRAM |
| `true` / `1` / `yes` | Force LLM on (may OOM on low VRAM) |
| `false` / `0` / `no` | DiT-only mode — faster, lower VRAM |

---

## Command Line Options

`run.py` and `api_server.py` accept the same CLI flags, which override `.env`:

| Option | Default | Description |
|--------|---------|-------------|
| `--port` | 3297 | Server port |
| `--host` | `0.0.0.0` | Bind address |
| `--batch_size` | auto | Default batch size for generation |
| `--init_service` | `false` | Pre-load models at startup |
| `--init_llm` | `auto` | LLM init: `true` / `false` / `auto` |
| `--config_path` | `auto` | DiT model (e.g., `acestep-v15-turbo`) |
| `--lm_model_path` | `auto` | LM model (e.g., `acestep-5Hz-lm-1.7B`) |
| `--offload_to_cpu` | `auto` | CPU offload (auto-enabled if VRAM < 20 GB) |
| `--download-source` | `auto` | `huggingface` / `modelscope` |
| `--api-key` | none | API authentication key |
| `--backend` | `auto` | LM backend: `vllm` / `pt` / `mlx` |

**Examples:**

```bash
# Network access with specific model
python run.py --host 0.0.0.0 --lm_model_path acestep-5Hz-lm-1.7B

# Pre-initialize models on startup
python run.py --init_service true --config_path acestep-v15-turbo

# DiT-only mode (no LLM) — lowest VRAM
python run.py --init_llm false

# ModelScope download source
python run.py --download-source modelscope

# With API key
python run.py --api-key sk-your-secret-key
```

---

## Model Download

Models auto-download on first request. To download in advance:

```bash
# Download main bundle (vae, embeddings, turbo DiT, 1.7B LM)
python -m acestep.model_downloader

# Download all available models
python -m acestep.model_downloader --all

# From ModelScope
python -m acestep.model_downloader --download-source modelscope

# Specific model
python -m acestep.model_downloader --model acestep-v15-sft

# List available
python -m acestep.model_downloader --list
```

**Manual download (huggingface-cli):**

```bash
huggingface-cli download ACE-Step/Ace-Step1.5 --local-dir ./checkpoints
huggingface-cli download ACE-Step/acestep-5Hz-lm-0.6B --local-dir ./checkpoints/acestep-5Hz-lm-0.6B
```

---

## Which Model Should I Choose?

| GPU VRAM | LM Model | Backend | Notes |
|----------|----------|---------|-------|
| ≤6 GB | None (DiT only) | — | `ACESTEP_INIT_LLM=false`; INT8 + full CPU offload |
| 6–8 GB | `acestep-5Hz-lm-0.6B` | `pt` | Lightweight LM |
| 8–16 GB | `0.6B` / `1.7B` | `vllm` | 0.6B for 8–12 GB, 1.7B for 12–16 GB |
| 16–24 GB | `acestep-5Hz-lm-1.7B` | `vllm` | 4B available at 20 GB+ |
| ≥24 GB | `acestep-5Hz-lm-4B` | `vllm` | Best quality |

See [GPU_COMPATIBILITY.md](GPU_COMPATIBILITY.md) for full tier table, duration limits, and batch sizes.

---

## AMD / ROCm GPUs

```bash
# Linux — ROCm 6.0+
python3.11 -m venv .venv
source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/rocm6.0
pip install -e .
python run.py
```

> `torchcodec` is unavailable on ROCm. ACE-Step falls back to `soundfile` automatically.

**RDNA3/RDNA4 — GFX version override (if GPU not detected):**

```bash
export HSA_OVERRIDE_GFX_VERSION=11.0.0   # RX 7900 XT/XTX, RX 9070 XT
export HSA_OVERRIDE_GFX_VERSION=11.0.1   # RX 7800 XT, RX 7700 XT
export HSA_OVERRIDE_GFX_VERSION=11.0.2   # RX 7600
python run.py
```

---

## Intel GPUs

Intel XPU is supported via [Intel Extension for PyTorch](https://pytorch-extension.intel.com/).

```bash
pip install torch --index-url https://download.pytorch.org/whl/xpu
pip install -e .
ACESTEP_DEVICE=xpu python run.py
```

> `torchcodec` and `nanovllm` acceleration are unavailable on Intel XPU. ACE-Step uses `soundfile` as fallback.

---

## macOS (Apple Silicon / MLX)

```bash
conda activate aureon  # Python 3.11
pip install -e .
ACESTEP_LM_BACKEND=mlx ACESTEP_DEVICE=mps python run.py
```

---

## CPU-Only Mode

```bash
ACESTEP_DEVICE=cpu ACESTEP_INIT_LLM=false python run.py
```

CPU inference is very slow. DiT-only mode (`ACESTEP_INIT_LLM=false`) is strongly recommended.

---

## Linux Notes

### Python 3.11 Pre-Release

Some Linux distributions (e.g., older Ubuntu) ship Python 3.11.0rc1, which is a pre-release. This can cause segmentation faults with the vLLM backend.

**Fix:** Use a stable Python ≥3.11.12 (deadsnakes PPA on Ubuntu) or switch to the PyTorch backend:

```bash
ACESTEP_LM_BACKEND=pt python run.py
```

---

## Development

```bash
# Install in editable mode with dev extras
pip install -e ".[dev]"

# Add a dependency
uv add package-name

# Update all dependencies
uv sync --upgrade
```
