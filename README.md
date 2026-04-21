<h1 align="center">Aureon — Music</h1>
<h2 align="center">AI-Powered Music Generation · Built by Aureon By VRIP7</h2>
<p align="center">
    <a href="https://huggingface.co/ACE-Step/Ace-Step1.5">Models (HuggingFace)</a> |
    <a href="https://modelscope.cn/models/ACE-Step/Ace-Step1.5">ModelScope</a> |
    <a href="docs/API.md">REST API</a> |
    <a href="docs/INSTALL.md">Install</a> |
    <a href="docs/studio.md">Studio UI</a>
</p>

---

## About Aureon — Music

**Aureon - Music** is the official AI-powered music channel of **Aureon By VRIP7**.

Aureon By VRIP7 is an Indian student-led alternative to Hack Club — focused on:

- Building real-world tech projects
- Hackathons
- AI experimentation
- Open-source development
- Technical creativity
- Digital innovation

This channel represents the sound of builders, coders, and creators shaping the future.

> Music for developers.  
> Music for engineers.  
> Music for Indian hackathons.  
> Music for momentum.

---

## What This Is

This is a **production-grade, self-hosted AI music generation server** powered by [ACE-Step 1.5](https://github.com/ACE-Step/ACE-Step-1.5) — a hybrid LM + Diffusion Transformer architecture capable of generating commercial-quality audio in under 10 seconds on consumer GPUs.

The server exposes:
- A **Studio web UI** at `http://localhost:3297/` — a full-featured single-page app with all generation parameters
- A **REST API** at `http://localhost:3297/release_task` — async job queue for programmatic use
- A **health endpoint** at `http://localhost:3297/health`
- A **model listing** at `http://localhost:3297/v1/models`

Everything runs on a single port (default **3297**) via `python run.py` or `docker compose up`.

---

## Features

### Performance
- Under 2s per full song on A100, under 10s on RTX 3090
- Flexible duration: 10 seconds up to 10 minutes (600s)
- Batch generation: up to 8 songs simultaneously

### Generation Quality
- Commercial-grade output quality
- 1000+ instrument and style combinations
- Multi-language lyrics in 50+ languages

### Control & Editing

| Feature | Description |
|---------|-------------|
| Reference Audio Input | Use audio to guide generation style |
| Cover Generation | Create covers from existing audio |
| Repaint & Edit | Selective local audio editing |
| Track Separation | Split audio into stems |
| Multi-Track Generation | Add instrumental layers |
| Vocal2BGM | Auto-generate accompaniment for vocal tracks |
| Metadata Control | Duration, BPM, key/scale, time signature |
| Query Rewriting | Auto LM expansion of tags and lyrics |
| Audio Understanding | Extract BPM, key, time signature from audio |
| LoRA Training | Fine-tune on custom style (8 songs, ~1 hour on RTX 3090) |
| Quality Scoring | Automatic quality assessment |

---

## Quick Start

**Requirements:** Python 3.11–3.12, CUDA GPU (also supports MPS / ROCm / Intel XPU / CPU), 4 GB+ VRAM

```bash
# 1. Clone
git clone https://github.com/Gamecooler19/Aureon.git
cd Aureon

# 2. Create environment & install
conda create -n aureon python=3.11 -y
conda activate aureon
pip install -e .

# 3. Launch  (models auto-download on first run)
python run.py
```

Open **http://localhost:3297** in your browser.

### Docker

```bash
# Build & start
docker compose up -d --build

# View logs
docker compose logs -f app

# Stop
docker compose down
```

Studio UI available at **http://localhost:3297** once the health check passes (~2 minutes first run for model download).

---

## Environment Variables

Create a `.env` file in the project root. `run.py` and `docker compose` both load it automatically.

```bash
# .env — override any of these
ACESTEP_API_PORT=3297
ACESTEP_API_HOST=0.0.0.0
ACESTEP_CONFIG_PATH=acestep-v15-turbo
ACESTEP_LM_MODEL_PATH=acestep-5Hz-lm-1.7B
ACESTEP_INIT_LLM=auto
ACESTEP_DOWNLOAD_SOURCE=auto
ACESTEP_API_KEY=                     # leave empty to disable auth
```

---

## Which Model Should I Use?

| GPU VRAM | LM Model | Backend | Notes |
|----------|----------|---------|-------|
| ≤6 GB | None (DiT only) | — | INT8 + full CPU offload |
| 6–8 GB | `acestep-5Hz-lm-0.6B` | `pt` | Lightweight LM |
| 8–16 GB | `0.6B` / `1.7B` | `vllm` | 0.6B for 8–12 GB, 1.7B for 12–16 GB |
| 16–24 GB | `acestep-5Hz-lm-1.7B` | `vllm` | 4B available at 20 GB+ |
| ≥24 GB | `acestep-5Hz-lm-4B` | `vllm` | Best quality |

The server auto-detects your GPU tier and configures itself accordingly.

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/INSTALL.md](docs/INSTALL.md) | Full installation guide (all platforms) |
| [docs/studio.md](docs/studio.md) | Studio UI reference |
| [docs/API.md](docs/API.md) | REST API reference (all 50+ parameters) |
| [docs/INFERENCE.md](docs/INFERENCE.md) | Python API usage |
| [docs/CLI.md](docs/CLI.md) | CLI reference |
| [docs/LoRA_Training_Tutorial.md](docs/LoRA_Training_Tutorial.md) | LoRA fine-tuning guide |
| [docs/GPU_COMPATIBILITY.md](docs/GPU_COMPATIBILITY.md) | GPU tiers, VRAM limits, batch sizes |
| [docs/GPU_TROUBLESHOOTING.md](docs/GPU_TROUBLESHOOTING.md) | GPU detection and ROCm troubleshooting |
| [docs/Tutorial.md](docs/Tutorial.md) | Design philosophy and usage guide |

---

## Model Zoo

### DiT Models

| Model | Steps | Quality | Fine-Tunability | HuggingFace |
|-------|:-----:|---------|:---------------:|-------------|
| `acestep-v15-base` | 50 | Medium | Easy | [Link](https://huggingface.co/ACE-Step/acestep-v15-base) |
| `acestep-v15-sft` | 50 | High | Easy | [Link](https://huggingface.co/ACE-Step/acestep-v15-sft) |
| `acestep-v15-turbo` | 8 | Very High | Medium | [Link](https://huggingface.co/ACE-Step/Ace-Step1.5) |

### LM Models

| Model | Params | Composition | HuggingFace |
|-------|:------:|-------------|-------------|
| `acestep-5Hz-lm-0.6B` | 0.6B | Medium | [Link](https://huggingface.co/ACE-Step/acestep-5Hz-lm-0.6B) |
| `acestep-5Hz-lm-1.7B` | 1.7B | Medium | [Link](https://huggingface.co/ACE-Step/acestep-5Hz-lm-1.7B) |
| `acestep-5Hz-lm-4B` | 4B | Strong | [Link](https://huggingface.co/ACE-Step/acestep-5Hz-lm-4B) |

---

## License

This project is built on [ACE-Step 1.5](https://github.com/ACE-Step/ACE-Step-1.5), licensed under [MIT](./LICENSE).

All generated audio should be used responsibly. Users are responsible for verifying originality, disclosing AI involvement, and complying with applicable copyright laws.
