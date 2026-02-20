# Studio UI

ACE-Step Studio is the primary web interface served directly by the API server at `http://localhost:3297/`.

## Quick Start

```bash
# Activate environment
conda activate aureon   # or: source .venv/bin/activate

# Launch (serves both Studio UI and REST API on port 3297)
python run.py
```

Open **http://localhost:3297** in any modern browser.

## Network Access

| Scenario | Command |
|----------|---------|
| Local only (default) | `python run.py` |
| LAN / server | `ACESTEP_API_HOST=0.0.0.0 python run.py` |
| Docker Compose | `docker compose up -d` |
| Docker standalone | `docker run --gpus all -p 3297:3297 --env-file .env blu3scr33n-music:latest` |

## URL Routes

| Path | Description |
|------|-------------|
| `GET /` | Redirects to `/studio` |
| `GET /studio` | Serves `ui/studio.html` |
| `POST /release_task` | Submit a generation job |
| `POST /query_result` | Poll for job results |
| `GET /v1/models` | List available models |
| `GET /v1/stats` | Server statistics |
| `GET /health` | Health check |
| `GET /v1/audio` | Download generated audio |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ACESTEP_API_PORT` | `3297` | Port for the server |
| `ACESTEP_API_HOST` | `0.0.0.0` | Bind address |
| `ACESTEP_API_KEY` | *(empty)* | Bearer token for auth (leave empty to disable) |

Set these in a `.env` file at the project root (auto-loaded by `run.py`) or export before running.

## UI Features

### Parameter Sections

The Studio UI exposes all 50+ API parameters organized into accordion sections:

| Section | Parameters |
|---------|-----------|
| **Generation Mode** | task_type, thinking, sample_mode, sample_query, use_format |
| **Text Input** | prompt, lyrics, vocal_language |
| **Metadata** | audio_duration, bpm, key_scale, time_signature, audio_format |
| **DiT Settings** | inference_steps, guidance_scale, infer_method, shift, timesteps |
| **Seed** | use_random_seed, seed |
| **CFG & ADG** | cfg_interval_start, cfg_interval_end, use_adg, use_tiled_decode |
| **Batch** | batch_size, model |
| **Edit / Cover** | audio_cover_strength, task_type, instruction, src_audio, repainting_start, repainting_end |
| **LM Settings** | lm_model_path, lm_backend, lm_temperature, lm_cfg_scale, lm_repetition_penalty, lm_top_k, lm_top_p, lm_negative_prompt |
| **CoT / Decoding** | use_cot_caption, use_cot_language, constrained_decoding, allow_lm_batch, constrained_decoding_debug |

### Toolbar Buttons

| Button | Description |
|--------|-------------|
| **Generate** | Submit current parameters as a generation job |
| **Format Input** | Call `/format_input` to LM-enhance caption and lyrics before generating |
| **Random Sample** | Fill form with a random preset via `/create_random_sample` |
| **Description Mode** | Toggle simple-query mode (`sample_query` replaces manual fields) |

### Results Area

- Each completed job shows individual audio players (WaveSurfer.js waveform)
- Stats bar displays: inference time, RTFX, model used, seed
- Audio can be downloaded directly from the player
- Batch results are displayed as separate cards side by side

## Authentication

If `ACESTEP_API_KEY` is set, all API requests require a Bearer token. The Studio UI includes an **API Key** input field that is sent with every request automatically.
