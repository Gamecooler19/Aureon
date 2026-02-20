# Inference API

Python-level API for direct integration with ACE-Step generation infrastructure.

---

## Quick Start

```python
from acestep.handler import AceStepHandler
from acestep.llm_inference import LLMHandler
from acestep.inference import GenerationParams, GenerationConfig, generate_music

# Initialize handlers
dit_handler = AceStepHandler()
llm_handler = LLMHandler()

dit_handler.initialize_service(
    project_root="/path/to/project",
    config_path="acestep-v15-turbo",
    device="cuda"
)

llm_handler.initialize(
    checkpoint_dir="/path/to/checkpoints",
    lm_model_path="acestep-5Hz-lm-0.6B",
    backend="vllm",
    device="cuda"
)

params = GenerationParams(
    caption="upbeat electronic dance music with heavy bass",
    bpm=128,
    duration=30,
)

config = GenerationConfig(batch_size=2, audio_format="flac")

result = generate_music(dit_handler, llm_handler, params, config, save_dir="/output")

if result.success:
    for audio in result.audios:
        print(f"Generated: {audio['path']} (seed: {audio['params']['seed']})")
else:
    print(f"Error: {result.error}")
```

---

## GenerationParams

### Text Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `caption` | `str` | `""` | Text description of desired music. Max 512 chars. |
| `lyrics` | `str` | `""` | Lyrics text. Use `"[Instrumental]"` for instrumental tracks. Max 4096 chars. |
| `instrumental` | `bool` | `False` | If True, generate instrumental regardless of lyrics. |

### Music Metadata

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `bpm` | `Optional[int]` | `None` | Tempo (30–300). `None` = auto via LM. |
| `keyscale` | `str` | `""` | Key (e.g., `"C Major"`, `"Am"`). Empty = auto. |
| `timesignature` | `str` | `""` | Time signature (`"2"`, `"3"`, `"4"`, `"6"`). |
| `vocal_language` | `str` | `"unknown"` | ISO 639-1 language code or `"unknown"` for auto. |
| `duration` | `float` | `-1.0` | Target length in seconds (10–600). ≤0 = auto. |

### Generation Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `inference_steps` | `int` | `8` | Denoising steps. Turbo: 1–20 (rec. 8). Base: 1–200 (rec. 32–64). |
| `guidance_scale` | `float` | `7.0` | CFG scale (base model only). Typical: 5.0–9.0. |
| `seed` | `int` | `-1` | Random seed. `-1` = random each time. |

### Advanced DiT Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `use_adg` | `bool` | `False` | Adaptive Dual Guidance (base model only). |
| `cfg_interval_start` | `float` | `0.0` | CFG start ratio (0.0–1.0). |
| `cfg_interval_end` | `float` | `1.0` | CFG end ratio (0.0–1.0). |
| `shift` | `float` | `1.0` | Timestep shift factor (1.0–5.0). Rec. `3.0` for turbo models. |
| `infer_method` | `str` | `"ode"` | `"ode"` (Euler, faster) or `"sde"` (stochastic). |
| `timesteps` | `Optional[List[float]]` | `None` | Custom timestep list from 1.0→0.0. Overrides `inference_steps` + `shift`. |

### Task-Specific Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `task_type` | `str` | `"text2music"` | Task type. See Task Types section. |
| `instruction` | `str` | auto | Task-specific instruction prompt. |
| `reference_audio` | `Optional[str]` | `None` | Path to reference audio for style transfer. |
| `src_audio` | `Optional[str]` | `None` | Path to source audio for `cover`/`repaint`/etc. |
| `audio_codes` | `str` | `""` | Pre-extracted 5Hz audio semantic codes. Advanced use only. |
| `repainting_start` | `float` | `0.0` | Repaint start time (seconds). |
| `repainting_end` | `float` | `-1` | Repaint end time (seconds). `-1` = end of audio. |
| `audio_cover_strength` | `float` | `1.0` | Cover influence (0.0–1.0). `~0.2` for loose style transfer. |

### 5Hz LM Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `thinking` | `bool` | `True` | Enable LM Chain-of-Thought for audio code generation. |
| `lm_temperature` | `float` | `0.85` | LM sampling temperature. |
| `lm_cfg_scale` | `float` | `2.0` | LM CFG scale. |
| `lm_top_k` | `int` | `0` | Top-k (0 = disabled). |
| `lm_top_p` | `float` | `0.9` | Top-p nucleus sampling. |
| `lm_negative_prompt` | `str` | `"NO USER INPUT"` | LM negative prompt. |
| `use_cot_metas` | `bool` | `True` | Generate metadata via LM CoT. |
| `use_cot_caption` | `bool` | `True` | Refine caption via LM CoT. |
| `use_cot_language` | `bool` | `True` | Detect vocal language via LM CoT. |
| `use_constrained_decoding` | `bool` | `True` | FSM-based constrained decoding. |

---

## GenerationConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `batch_size` | `int` | `2` | Number of samples to generate (1–8). |
| `allow_lm_batch` | `bool` | `False` | Allow batch LM processing for speed. |
| `use_random_seed` | `bool` | `True` | Random seed per generation. |
| `seeds` | `Optional[List[int]]` | `None` | Explicit seed list for batch. |
| `lm_batch_chunk_size` | `int` | `8` | Max LM batch chunk size (GPU memory). |
| `constrained_decoding_debug` | `bool` | `False` | Debug constrained decoding. |
| `audio_format` | `str` | `"flac"` | Output format: `"mp3"`, `"wav"`, `"flac"`. |

---

## Task Types

| Task | Description |
|------|-------------|
| `text2music` | Generate from text description and/or lyrics |
| `cover` | Transform audio keeping structure, changing style |
| `repaint` | Regenerate a specific time segment |
| `lego` | Add an instrument track in context of existing audio (base model only) |
| `extract` | Isolate a specific instrument from a mix (base model only) |
| `complete` | Extend or complete a partial track (base model only) |

---

## Helper Functions

### `understand_music`

Analyze audio semantic codes to extract metadata.

```python
from acestep.inference import understand_music

result = understand_music(
    llm_handler=llm_handler,
    audio_codes="<|audio_code_10695|>...",
    temperature=0.85,
    use_constrained_decoding=True,
)

if result.success:
    print(f"Caption: {result.caption}")
    print(f"Lyrics: {result.lyrics}")
    print(f"BPM: {result.bpm}")
    print(f"Key: {result.keyscale}")
    print(f"Duration: {result.duration}s")
```

### `create_sample`

Generate a complete music blueprint from a natural language description.

```python
from acestep.inference import create_sample

result = create_sample(
    llm_handler=llm_handler,
    query="a soft Bengali love song for a quiet evening",
    instrumental=False,
    vocal_language="bn",
    temperature=0.85,
)

if result.success:
    params = GenerationParams(
        caption=result.caption,
        lyrics=result.lyrics,
        bpm=result.bpm,
        duration=result.duration,
        keyscale=result.keyscale,
        vocal_language=result.language,
    )
```

### `format_sample`

Format and enhance user-provided caption and lyrics.

```python
from acestep.inference import format_sample

result = format_sample(
    llm_handler=llm_handler,
    caption="Latin pop, reggaeton",
    lyrics="[Verse 1]\nBailando en la noche...",
    user_metadata={"bpm": 95},
    temperature=0.85,
)

if result.success:
    print(f"Enhanced Caption: {result.caption}")
    print(f"Formatted Lyrics: {result.lyrics}")
    print(f"BPM: {result.bpm}, Key: {result.keyscale}")
```

---

## Complete Examples

### Text-to-Music with Custom Timesteps

```python
params = GenerationParams(
    task_type="text2music",
    caption="jazz fusion with complex harmonies",
    timesteps=[0.97, 0.76, 0.615, 0.5, 0.395, 0.28, 0.18, 0.085, 0],
    thinking=True,
)
config = GenerationConfig(batch_size=1)
result = generate_music(dit_handler, llm_handler, params, config, save_dir="/output")
```

### Batch with Specific Seeds

```python
params = GenerationParams(caption="epic cinematic trailer music")
config = GenerationConfig(
    batch_size=4,
    seeds=[42, 123, 456],
    use_random_seed=False,
    lm_batch_chunk_size=2,
)
result = generate_music(dit_handler, llm_handler, params, config, save_dir="/output")
```

### High-Quality Base Model Generation

```python
params = GenerationParams(
    caption="intricate jazz fusion",
    inference_steps=64,
    guidance_scale=8.0,
    use_adg=True,
    shift=3.0,
    seed=42,
)
config = GenerationConfig(batch_size=1, use_random_seed=False, audio_format="wav")
result = generate_music(dit_handler, llm_handler, params, config, save_dir="/output")
```

### Cover Generation

```python
params = GenerationParams(
    task_type="cover",
    src_audio="original_song.mp3",
    caption="orchestral symphonic arrangement",
    audio_cover_strength=0.7,
    thinking=True,
)
config = GenerationConfig(batch_size=1)
result = generate_music(dit_handler, llm_handler, params, config, save_dir="/output")
```

---

## Best Practices

**For best quality:** Use base model with `inference_steps=64`, `use_adg=True`, `guidance_scale=7.0-9.0`, `shift=3.0`, `audio_format="wav"`.

**For speed:** Use turbo model with `inference_steps=8`, `use_adg=False`, `infer_method="ode"`, `audio_format="mp3"` or `"flac"`.

**For reproducibility:** Set `use_random_seed=False` in config, provide `seeds` list or `seed` in params, keep `lm_temperature` low (0.7–0.85).

**Enable LM** (`thinking=True`) when you need auto metadata, caption refinement, or better quality from minimal input.

**Disable LM** (`thinking=False`) when you already have precise metadata and want maximum speed.

**Accessing timing data:**

```python
time_costs = result.extra_outputs.get("time_costs", {})
print(f"LM Phase 1: {time_costs.get('lm_phase1_time', 0):.2f}s")
print(f"DiT Total: {time_costs.get('dit_total_time_cost', 0):.2f}s")
print(f"Pipeline Total: {time_costs.get('pipeline_total_time', 0):.2f}s")
```
