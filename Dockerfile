# =============================================================================
# ACE-Step 1.5 — Production Docker Image
# NVIDIA CUDA 12.8 · Python 3.11 · FastAPI · Uvicorn
# =============================================================================
# Build:  docker build -t ace-step:latest .
# Run:    docker run --gpus all -p 3297:3297 --env-file .env ace-step:latest
# Studio: http://localhost:3297
# =============================================================================

# ── Stage 1: dependency build ─────────────────────────────────────────────────
FROM nvidia/cuda:12.8.0-runtime-ubuntu22.04 AS base

# System labels
LABEL org.opencontainers.image.title="Blu3scr33n - Music"
LABEL org.opencontainers.image.description="Production API + Web UI for ACE-Step 1.5 music generation"
LABEL org.opencontainers.image.url="https://github.com/ace-step/ACE-Step-1.5"

# Prevent interactive apt prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# ── System packages ──────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 \
        python3.11-dev \
        python3.11-distutils \
        python3-pip \
        python3.11-venv \
        build-essential \
        git \
        curl \
        wget \
        ffmpeg \
        libsndfile1 \
        libsndfile1-dev \
        libopus0 \
        libopusfile0 \
        ca-certificates \
    && ln -sf /usr/bin/python3.11 /usr/bin/python3 \
    && ln -sf /usr/bin/python3.11 /usr/bin/python \
    && python3 -m pip install --upgrade pip setuptools wheel \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Stage 2: Python deps ──────────────────────────────────────────────────────
FROM base AS builder

WORKDIR /build

# Copy only what pip needs first (layer-cache optimisation)
COPY requirements.txt pyproject.toml ./
COPY app/acestep/third_parts/nano-vllm ./acestep/third_parts/nano-vllm

# Install PyTorch for Linux x86_64 CUDA 12.8 first (resolves dependency order)
RUN pip install --no-cache-dir \
        torch==2.10.0+cu128 \
        torchvision==0.25.0+cu128 \
        torchaudio==2.10.0+cu128 \
        --extra-index-url https://download.pytorch.org/whl/cu128

# Install nano-vllm local package
RUN pip install --no-cache-dir -e ./acestep/third_parts/nano-vllm

# Install all remaining requirements (skips torch since already installed)
RUN pip install --no-cache-dir \
        safetensors==0.7.0 \
        "transformers>=4.51.0,<4.58.0" \
        diffusers \
        gradio==6.2.0 \
        matplotlib \
        scipy \
        soundfile \
        loguru \
        einops \
        accelerate \
        fastapi \
        "uvicorn[standard]" \
        numba \
        vector-quantize-pytorch \
        torchao \
        toml \
        modelscope \
        peft \
        lycoris-lora \
        lightning \
        tensorboard \
        python-dotenv \
        diskcache \
        xxhash \
        typer-slim

# Install flash-attn for Linux x86_64 (speeds up attention layers)
RUN pip install --no-cache-dir flash-attn || true
# Install triton (needed for nano-vllm kernel compilation)
RUN pip install --no-cache-dir triton || true
# Install torchcodec (audio decoding, not available on aarch64)
RUN pip install --no-cache-dir torchcodec || true

# ── Stage 3: final production image ──────────────────────────────────────────
FROM base AS production

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source
COPY app/acestep/ ./acestep/
COPY app/cli.py ./
COPY run.py ./
COPY app/ui/ ./ui/
COPY pyproject.toml ./
COPY LICENSE ./

# ── Runtime environment ───────────────────────────────────────────────────────
# Model / device configuration — override in .env or 7docker-compose
ENV ACESTEP_CONFIG_PATH=acestep-v15-turbo
ENV ACESTEP_LM_MODEL_PATH=acestep-5Hz-lm-0.6B
ENV ACESTEP_DEVICE=auto
ENV ACESTEP_LM_BACKEND=pt
ENV ACESTEP_INIT_LLM=auto
ENV ACESTEP_NO_INIT=false
ENV ACESTEP_DOWNLOAD_SOURCE=auto

# API server configuration
ENV ACESTEP_API_HOST=0.0.0.0
ENV ACESTEP_API_PORT=3297
ENV ACESTEP_QUEUE_MAXSIZE=100
ENV ACESTEP_QUEUE_WORKERS=1

# Cache / temp directories (use named volumes for persistence)
ENV ACESTEP_TMPDIR=/app/.cache/tmp
ENV TRITON_CACHE_DIR=/app/.cache/triton
ENV TORCHINDUCTOR_CACHE_DIR=/app/.cache/torchinductor
ENV HF_HOME=/app/.cache/huggingface
ENV TORCH_HOME=/app/.cache/torch

# Create all cache + checkpoint directories
RUN mkdir -p \
        /app/.cache/tmp \
        /app/.cache/triton \
        /app/.cache/torchinductor \
        /app/.cache/huggingface \
        /app/.cache/torch \
        /app/checkpoints \
        /app/outputs

# ── Health check ──────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -sf http://localhost:${ACESTEP_API_PORT}/health | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if d.get('data',{}).get('status')=='ok' else 1)" || exit 1

# ── Expose port ───────────────────────────────────────────────────────────────
EXPOSE 3297

# ── Entry point ───────────────────────────────────────────────────────────────
# Default: start the unified API + Studio server via run.py.
# Override for CLI usage:  docker run ace-step python cli.py --help
ENTRYPOINT ["python3", "run.py"]
CMD []
