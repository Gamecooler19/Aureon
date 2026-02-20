# REST API Reference

**Base URL:** `http://localhost:3297` (default)

**Workflow:**
1. `POST /release_task` → receive `task_id`
2. `POST /query_result` → poll until `status == 1` (success) or `2` (failed)
3. `GET /v1/audio?path=...` → download audio

---

## 1. Authentication

When `ACESTEP_API_KEY` is set, all requests must include it via:

**Method A — request body:**
```json
{ "ai_token": "your-api-key", "prompt": "..." }
```

**Method B — Authorization header:**
```bash
curl -H 'Authorization: Bearer your-api-key' ...
```

Set the key via `.env`:
```bash
ACESTEP_API_KEY=your-secret-key
```

---

## 2. Response Envelope

All endpoints return:

```json
{
  "data": { ... },
  "code": 200,
  "error": null,
  "timestamp": 1700000000000,
  "extra": null
}
```

---

## 3. Task Status Codes

| Code | Meaning |
|------|---------|
| `0` | Queued or running |
| `1` | Succeeded — result ready |
| `2` | Failed |

---

## 4. POST /release_task — Submit Generation Job

**Content-Types:** `application/json`, `multipart/form-data`, `application/x-www-form-urlencoded`

### Core Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | string | `""` | Music description (alias: `caption`) |
| `lyrics` | string | `""` | Lyrics content |
| `thinking` | bool | `false` | Use 5Hz LM for audio code generation (lm-dit mode) |
| `vocal_language` | string | `"en"` | Lyrics language ISO code |
| `audio_format` | string | `"mp3"` | Output format: `mp3`, `wav`, `flac` |

### Description / Sample Mode

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sample_mode` | bool | `false` | Auto-generate caption/lyrics/metadata via LM |
| `sample_query` | string | `""` | Natural language description (aliases: `description`, `desc`) |
| `use_format` | bool | `false` | LM-enhance provided caption and lyrics (alias: `format`) |

### Model Selection

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | null | DiT model name (e.g., `"acestep-v15-turbo"`). Use `/v1/models` to list available. |

### Music Metadata

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `bpm` | int | null | Tempo in BPM (30–300) |
| `key_scale` | string | `""` | Key, e.g., `"C Major"`, `"Am"` (aliases: `keyscale`, `keyScale`) |
| `time_signature` | string | `""` | `"2"`, `"3"`, `"4"`, `"6"` for 2/4, 3/4, 4/4, 6/8 (aliases: `timesignature`, `timeSignature`) |
| `audio_duration` | float | null | Target duration in seconds, 10–600 (aliases: `duration`, `target_duration`) |

### Generation Control

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `inference_steps` | int | `8` | Denoising steps. Turbo: 1–20 (rec. 8). Base: 1–200 (rec. 32–64). |
| `guidance_scale` | float | `7.0` | Classifier-free guidance (base model only) |
| `use_random_seed` | bool | `true` | Random seed per generation |
| `seed` | int | `-1` | Fixed seed (when `use_random_seed=false`) |
| `batch_size` | int | `2` | Number of outputs (max 8) |

### Advanced DiT Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `shift` | float | `3.0` | Timestep shift factor (1.0–5.0). Effective for base models. |
| `infer_method` | string | `"ode"` | `"ode"` (Euler, faster) or `"sde"` (stochastic) |
| `timesteps` | string | null | Custom timestep schedule as comma-separated floats, e.g., `"0.97,0.76,0.5,0.28,0.085,0"` |
| `use_adg` | bool | `false` | Adaptive Dual Guidance (base model only) |
| `cfg_interval_start` | float | `0.0` | CFG start ratio (0.0–1.0) |
| `cfg_interval_end` | float | `1.0` | CFG end ratio (0.0–1.0) |
| `use_tiled_decode` | bool | `false` | Tiled VAE decode for very long audio |

### 5Hz LM Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lm_model_path` | string | null | Override LM checkpoint name |
| `lm_backend` | string | `"vllm"` | `vllm` or `pt` |
| `lm_temperature` | float | `0.85` | Sampling temperature |
| `lm_cfg_scale` | float | `2.5` | LM CFG scale |
| `lm_negative_prompt` | string | `"NO USER INPUT"` | LM negative prompt |
| `lm_top_k` | int | null | Top-k (0/null disables) |
| `lm_top_p` | float | `0.9` | Top-p nucleus sampling |
| `lm_repetition_penalty` | float | `1.0` | Repetition penalty |

### LM CoT Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `use_cot_caption` | bool | `true` | LM rewrites/enhances caption via CoT |
| `use_cot_language` | bool | `true` | LM detects vocal language via CoT |
| `constrained_decoding` | bool | `true` | FSM-based constrained LM decoding |
| `constrained_decoding_debug` | bool | `false` | Debug logging for constrained decoding |
| `allow_lm_batch` | bool | `true` | Batch LM processing for efficiency |

### Edit / Cover Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `task_type` | string | `"text2music"` | `text2music`, `cover`, `repaint`, `lego`, `extract`, `complete` |
| `instruction` | string | auto | Edit instruction (auto-set per task_type) |
| `src_audio` | file / string | null | Source audio upload or server path |
| `reference_audio` | file / string | null | Reference audio upload or server path |
| `repainting_start` | float | `0.0` | Repaint start time (seconds) |
| `repainting_end` | float | null | Repaint end time (seconds); `-1` = end of audio |
| `audio_cover_strength` | float | `1.0` | Cover influence (0.0–1.0); set ~0.2 for loose style transfer |

### Auth

| Parameter | Type | Description |
|-----------|------|-------------|
| `ai_token` | string | API key (alternative to Authorization header) |

### Response

```json
{
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "queued",
    "queue_position": 1
  },
  "code": 200
}
```

### Examples

**Basic text2music:**
```bash
curl -X POST http://localhost:3297/release_task \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "upbeat pop song", "lyrics": "Hello world", "inference_steps": 8}'
```

**With thinking (LM generates audio codes + fills missing metadata):**
```bash
curl -X POST http://localhost:3297/release_task \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "upbeat pop song", "lyrics": "Hello world", "thinking": true, "lm_temperature": 0.85}'
```

**Description-driven generation:**
```bash
curl -X POST http://localhost:3297/release_task \
  -H 'Content-Type: application/json' \
  -d '{"sample_query": "a soft Bengali love song for a quiet evening", "thinking": true}'
```

**Format + generate:**
```bash
curl -X POST http://localhost:3297/release_task \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "pop rock", "lyrics": "[Verse 1]\nWalking down the street...", "use_format": true, "thinking": true}'
```

**File upload (source audio for cover/repaint):**
```bash
curl -X POST http://localhost:3297/release_task \
  -F "prompt=remix this song" \
  -F "src_audio=@/path/to/song.mp3" \
  -F "task_type=repaint"
```

**Custom timesteps:**
```bash
curl -X POST http://localhost:3297/release_task \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "jazz piano trio", "timesteps": "0.97,0.76,0.615,0.5,0.395,0.28,0.18,0.085,0"}'
```

---

## 5. POST /query_result — Poll for Results

```bash
curl -X POST http://localhost:3297/query_result \
  -H 'Content-Type: application/json' \
  -d '{"task_id_list": ["550e8400-e29b-41d4-a716-446655440000"]}'
```

**Response:**

```json
{
  "data": [
    {
      "task_id": "550e8400-...",
      "status": 1,
      "result": "[{\"file\": \"/v1/audio?path=...\", \"status\": 1, \"prompt\": \"upbeat pop song\", \"metas\": {\"bpm\": 120, \"duration\": 30, \"keyscale\": \"C Major\"}, \"generation_info\": \"...\", \"seed_value\": \"12345\"}]"
    }
  ],
  "code": 200
}
```

**Result fields** (after parsing the `result` JSON string):

| Field | Type | Description |
|-------|------|-------------|
| `file` | string | Audio URL — use with `GET /v1/audio?path=...` |
| `status` | int | `0`=running, `1`=success, `2`=failed |
| `prompt` | string | Prompt used |
| `metas` | object | `{bpm, duration, keyscale, timesignature, genres}` |
| `generation_info` | string | Timing summary |
| `seed_value` | string | Comma-separated seeds used |
| `lm_model` | string | LM model name |
| `dit_model` | string | DiT model name |

---

## 6. POST /format_input — LM-Enhance Caption & Lyrics

```bash
curl -X POST http://localhost:3297/format_input \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "pop rock", "lyrics": "Walking down the street", "param_obj": "{\"duration\": 180}"}'
```

**Response:**

```json
{
  "data": {
    "caption": "Enhanced description",
    "lyrics": "Formatted lyrics...",
    "bpm": 120,
    "key_scale": "C Major",
    "time_signature": "4",
    "duration": 180,
    "vocal_language": "en"
  }
}
```

---

## 7. POST /create_random_sample — Get Random Preset

```bash
curl -X POST http://localhost:3297/create_random_sample \
  -H 'Content-Type: application/json' \
  -d '{"sample_type": "simple_mode"}'
```

`sample_type`: `"simple_mode"` (default) or `"custom_mode"`

---

## 8. GET /v1/models — List Available Models

```bash
curl http://localhost:3297/v1/models
```

**Response:**

```json
{
  "data": {
    "models": [
      {"name": "acestep-v15-turbo", "is_default": true},
      {"name": "acestep-v15-turbo-shift3", "is_default": false}
    ],
    "default_model": "acestep-v15-turbo"
  }
}
```

---

## 9. GET /v1/stats — Server Statistics

```bash
curl http://localhost:3297/v1/stats
```

**Response:**

```json
{
  "data": {
    "jobs": {"total": 100, "queued": 5, "running": 1, "succeeded": 90, "failed": 4},
    "queue_size": 5,
    "queue_maxsize": 200,
    "avg_job_seconds": 8.5
  }
}
```

---

## 10. GET /v1/audio — Download Audio

```bash
curl "http://localhost:3297/v1/audio?path=%2Ftmp%2Fapi_audio%2Fabc123.mp3" -o output.mp3
```

---

## 11. GET /health — Health Check

```bash
curl http://localhost:3297/health
```

**Response:**

```json
{"data": {"status": "ok", "service": "ACE-Step API", "version": "1.0"}, "code": 200}
```

---

## 12. Environment Variables

### Server

| Variable | Default | Description |
|----------|---------|-------------|
| `ACESTEP_API_HOST` | `0.0.0.0` | Bind address |
| `ACESTEP_API_PORT` | `3297` | Port |
| `ACESTEP_API_KEY` | *(empty)* | Auth key; empty disables auth |
| `ACESTEP_QUEUE_MAXSIZE` | `200` | Max queue depth |
| `ACESTEP_QUEUE_WORKERS` | `1` | Worker thread count |

### Model

| Variable | Default | Description |
|----------|---------|-------------|
| `ACESTEP_CONFIG_PATH` | `acestep-v15-turbo` | Primary DiT model |
| `ACESTEP_CONFIG_PATH2` | *(empty)* | Secondary DiT model (multi-model) |
| `ACESTEP_CONFIG_PATH3` | *(empty)* | Third DiT model (multi-model) |
| `ACESTEP_DEVICE` | `auto` | Compute device |
| `ACESTEP_OFFLOAD_TO_CPU` | `false` | CPU offload for low-VRAM |

### LM

| Variable | Default | Description |
|----------|---------|-------------|
| `ACESTEP_INIT_LLM` | `auto` | `auto` / `true` / `false` |
| `ACESTEP_LM_MODEL_PATH` | `acestep-5Hz-lm-0.6B` | Default LM checkpoint |
| `ACESTEP_LM_BACKEND` | `vllm` | `vllm` / `pt` / `mlx` |

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `400` | Bad request |
| `401` | Unauthorized (invalid/missing API key) |
| `404` | Not found |
| `429` | Queue full |
| `500` | Server error |

---

## Best Practices

1. Use `thinking=true` for best quality — the LM generates audio codes and fills metadata.
2. Use `sample_query` for quick generation from a natural language description.
3. Use `use_format=true` when you have rough caption/lyrics and want LM to clean them up.
4. Batch query results using `/query_result` — pass multiple `task_id` values at once.
5. Check `/v1/stats` to understand queue load and estimated wait time.
6. For multi-model deployments, set `ACESTEP_CONFIG_PATH2` and select via the `model` field.
7. Set `ACESTEP_API_KEY` in production to protect your server.
