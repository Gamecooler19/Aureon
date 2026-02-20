# GPU Compatibility

ACE-Step 1.5 automatically adapts to your GPU's VRAM at startup, adjusting generation limits, LM model availability, offloading strategies, and server defaults.

---

## GPU Tier Table

| VRAM | Tier | LM Models | Recommended LM | Backend | Max Duration (LM / No LM) | Max Batch (LM / No LM) | Offload | Quantization |
|------|------|-----------|----------------|---------|---------------------------|------------------------|---------|--------------|
| ≤4 GB | Tier 1 | None | — | pt | 4 min / 6 min | 1 / 1 | CPU + DiT | INT8 |
| 4–6 GB | Tier 2 | None | — | pt | 8 min / 10 min | 1 / 1 | CPU + DiT | INT8 |
| 6–8 GB | Tier 3 | 0.6B | 0.6B | pt | 8 min / 10 min | 2 / 2 | CPU + DiT | INT8 |
| 8–12 GB | Tier 4 | 0.6B | 0.6B | vllm | 8 min / 10 min | 2 / 4 | CPU + DiT | INT8 |
| 12–16 GB | Tier 5 | 0.6B, 1.7B | 1.7B | vllm | 8 min / 10 min | 4 / 4 | CPU | INT8 |
| 16–20 GB | Tier 6a | 0.6B, 1.7B | 1.7B | vllm | 8 min / 10 min | 4 / 8 | CPU | INT8 |
| 20–24 GB | Tier 6b | 0.6B, 1.7B, 4B | 1.7B | vllm | 8 min / 8 min | 8 / 8 | None | None |
| ≥24 GB | Unlimited | All | 4B | vllm | 10 min / 10 min | 8 / 8 | None | None |

### Column Descriptions

| Column | Meaning |
|--------|---------|
| **LM Models** | LM sizes available on this tier |
| **Recommended LM** | Default selection for this tier |
| **Backend** | `vllm` (fastest on NVIDIA), `pt` (universal), `mlx` (Apple Silicon) |
| **Offload — CPU + DiT** | VAE, Text Encoder, and DiT all moved to CPU when idle |
| **Offload — CPU** | VAE and Text Encoder offloaded; DiT stays on GPU |
| **Offload — None** | All models stay on GPU |
| **Quantization** | INT8 weight quantization to reduce VRAM |

---

## Server Auto-Defaults

The API server automatically configures itself based on detected GPU tier:

- **LM initialization**: enabled by default for Tier 3+; disabled for Tier 1–2
- **LM model path**: pre-set to the recommended model for the tier
- **Backend**: restricted to `pt`/`mlx` on Tier 1–3 (vllm KV cache is too large); all backends available on Tier 4+
- **CPU offload**: enabled by default on lower tiers, disabled on higher tiers
- **Quantization**: enabled by default on Tier 1–6a; disabled on Tier 6b+

Override any of these via `.env` or CLI flags. If an incompatible option is selected, the server warns and falls back automatically.

---

## Runtime Safety Features

| Feature | Description |
|---------|-------------|
| **VRAM Guard** | Before each inference, VRAM is estimated; `batch_size` is reduced automatically if needed |
| **Adaptive VAE Decode** | Three-tier fallback: GPU tiled → GPU + CPU offload → full CPU decode |
| **Auto Chunk Size** | VAE decode chunk size adapts to free VRAM (64/128/256/512/1024/1536) |
| **Duration/Batch Clamping** | Requests exceeding tier limits are clamped with a warning |

---

## Common GPUs

| GPU | VRAM | Tier |
|-----|------|------|
| GTX 1050 Ti | 4 GB | Tier 1 |
| GTX 1660 / RTX 2060 | 6 GB | Tier 2 |
| RTX 3060 / 4060 | 8 GB | Tier 4 |
| RTX 3070 / 4070 Ti | 8–12 GB | Tier 4–5 |
| RTX 3080 16GB / 4060 Ti 16GB | 16 GB | Tier 6a |
| RTX 3090 / 4090 | 24 GB | Tier 6b–Unlimited |
| Apple M1/M2/M3 | Shared | Supported via MPS/MLX |

---

## Memory Optimization Tips

| VRAM | Recommendation |
|------|----------------|
| ≤6 GB | DiT-only mode (`ACESTEP_INIT_LLM=false`). INT8 + full CPU offload required. VAE may decode on CPU. |
| 6–8 GB | Use 0.6B LM with `pt` backend. Keep offload enabled. |
| 8–16 GB | Use 0.6B or 1.7B LM. `vllm` works well on Tier 4+. |
| 16–24 GB | Larger LM models available. Quantization optional at 20 GB+. |
| ≥24 GB | All models on GPU. No offload or quantization required. Use 4B LM for best quality. |

---

## Simulating Different VRAM Sizes

For development and testing, use the `MAX_CUDA_VRAM` environment variable to simulate lower VRAM tiers (also enforces a hard cap via `torch.cuda.set_per_process_memory_fraction()`):

```bash
MAX_CUDA_VRAM=4  python run.py   # Tier 1
MAX_CUDA_VRAM=8  python run.py   # Tier 4
MAX_CUDA_VRAM=16 python run.py   # Tier 6a
```

