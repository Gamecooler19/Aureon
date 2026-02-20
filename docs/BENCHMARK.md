# Benchmarking & Profiling

ACE-Step ships with `profile_inference.py` for performance profiling, automated benchmarking, and tier regression testing.

---

## Quick Start

```bash
# Profile a single generation (default DiT model, 1.7B LM)
python profile_inference.py --mode profile

# Run a full benchmark suite
python profile_inference.py --mode benchmark

# Test all GPU tier configurations automatically
python profile_inference.py --mode tier-test
```

---

## Modes

| Mode | Description |
|------|-------------|
| `profile` | Time a single generation end-to-end; show per-stage breakdown |
| `benchmark` | Run repeated generations; compute mean / std / percentiles |
| `tier-test` | Iterate through all GPU tiers, test each configuration |
| `understand` | Run `understand_music` helper and report LM output |
| `create_sample` | Run `create_sample` helper with specified params |
| `format_sample` | Run `format_sample` caption formatter |

---

## CLI Reference

| Flag | Default | Description |
|------|---------|-------------|
| `--mode` | `profile` | Run mode (see table above) |
| `--model` | `turbo` | DiT model: `turbo`, `sft`, `base`, `turbo-shift1`, etc. |
| `--lm-model` | `1.7B` | LM model size: `none`, `0.6B`, `1.7B`, `4B` |
| `--steps` | `8` | Diffusion inference steps |
| `--duration` | `30` | Generation duration in seconds |
| `--batch-size` | `1` | Batch size per run |
| `--runs` | `5` | Number of repetitions for benchmark averaging |
| `--device` | auto | Device: `cuda`, `mps`, `cpu` |
| `--seed` | `42` | RNG seed for reproducibility |
| `--output` | `benchmark_results.json` | Output file for results |

---

## Tier Testing

Simulate different VRAM tiers using the `MAX_CUDA_VRAM` environment variable, which caps GPU memory and triggers the corresponding tier configuration:

```bash
# Test Tier 1 (≤4 GB)
MAX_CUDA_VRAM=4 python profile_inference.py --mode tier-test

# Test Tier 4 (8 GB)
MAX_CUDA_VRAM=8 python profile_inference.py --mode tier-test

# Test Tier 6b (20+ GB)
MAX_CUDA_VRAM=20 python profile_inference.py --mode tier-test

# Test Tier 6b with full server (not just script)
MAX_CUDA_VRAM=20 python run.py
```

The tier-test mode automatically selects appropriate LM model and offload strategy for each simulated VRAM level and reports pass/fail per configuration.

### Boundary Testing

```bash
# Find maximum batch size at current VRAM
python profile_inference.py --mode benchmark --batch-size 8 --runs 3

# Test near-max duration
python profile_inference.py --mode profile --duration 120

# Stress-test LM at 4B
python profile_inference.py --mode profile --lm-model 4B --duration 60
```

---

## Sample Output

```
ACE-Step Profiling Report
=========================
Device:          NVIDIA RTX 4090 (24 GB)
Detected Tier:   Unlimited
DiT Model:       turbo
LM Model:        1.7B
Duration:        30s
Batch Size:      1

Stage Timings (mean over 5 runs):
  LM inference:      1.82s  ±0.04s
  DiT denoising:     3.41s  ±0.08s
  VAE decode:        0.62s  ±0.01s
  Total:             5.85s  ±0.09s

Real-time factor:    0.195× (5.1× faster than real-time)
Peak VRAM:           9.2 GB
```

---

## Interpreting Results

| Metric | Description |
|--------|-------------|
| **LM inference** | Time for language model to produce semantic codes and metadata |
| **DiT denoising** | Core diffusion steps — most of the compute cost |
| **VAE decode** | Converting latent representation back to audio waveform |
| **Real-time factor** | `total_time / audio_duration` — lower is faster |
| **Peak VRAM** | Maximum GPU memory used during generation |

A real-time factor below 0.5× (2× faster than real-time) is comfortable for interactive use. The turbo model on an RTX 3080+ typically achieves 3–6× faster than real-time for 30-second clips.

---

## Combining with the Live Server

For end-to-end latency measurement including HTTP overhead:

```bash
# Start the server
python run.py &

# Time a request via the API
time curl -X POST http://localhost:3297/release_task \
  -H 'Content-Type: application/json' \
  -d '{"caption":"lo-fi hip-hop beats","duration":30}' | python3 -c "
import sys, json
r = json.load(sys.stdin)
print('Task ID:', r['task_id'])
"
```

See [API.md](API.md) for polling the result endpoint.
