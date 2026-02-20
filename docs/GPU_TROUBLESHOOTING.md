# GPU Troubleshooting

Use this guide if you encounter GPU detection or performance issues when running ACE-Step.

---

## Initial Diagnosis

Run the built-in GPU check script:

```bash
python scripts/check_gpu.py
```

This reports:
- Detected device (cuda/hip/mps/cpu)
- ROCm / CUDA version
- Available VRAM
- Recommended tier and settings

---

## Issue 1: AMD GPU (ROCm) Not Detected

**Symptom:** PyTorch uses CPU despite an AMD GPU being present, or reports an error like `HIP error: invalid device`.

**Cause:** ROCm may not recognise your GPU's GFX architecture by default.

**Fix — set `HSA_OVERRIDE_GFX_VERSION`** for your GPU before running:

| GPU | Architecture | Override Value |
|-----|-------------|----------------|
| RX 7900 XTX / 7800 XT / 9070 XT | RDNA 3 / 4 | `11.0.0` |
| RX 6800 / 6700 / 6600 | RDNA 2 | `10.3.0` |
| RX 5700 / 5600 | RDNA 1 | `10.1.0` |

```bash
# Linux (add to ~/.bashrc or set per-session)
export HSA_OVERRIDE_GFX_VERSION=11.0.0
python run.py

# Or inline for a single session
HSA_OVERRIDE_GFX_VERSION=11.0.0 python run.py
```

For the RX 9070 XT specifically, also add:

```bash
export MIOPEN_FIND_MODE=FAST
export HSA_OVERRIDE_GFX_VERSION=11.0.0
python run.py
```

Add these to `.env` for persistent effect:

```ini
HSA_OVERRIDE_GFX_VERSION=11.0.0
MIOPEN_FIND_MODE=FAST
```

---

## Issue 2: CPU-Only PyTorch Installed

**Symptom:** `torch.cuda.is_available()` returns `False`; no GPU recognised at all.

**Cause:** The `torch` package installed is the CPU-only variant.

**Fix — reinstall with the correct hardware index:**

```bash
# For NVIDIA CUDA 12.x
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# For AMD ROCm 6.x
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.0
```

Verify after reinstall:

```python
import torch
print(torch.cuda.is_available())  # True
print(torch.version.hip)          # ROCm: version string; NVIDIA: None
```

---

## Issue 3: NVIDIA GPU Not Detected

**Symptom:** CUDA not available despite having an NVIDIA GPU.

**Steps:**

1. Verify the driver: `nvidia-smi` — should list your GPU and CUDA version.
2. If `nvidia-smi` fails, reinstall the NVIDIA driver for your OS.
3. Check CUDA toolkit compatibility: PyTorch's CUDA version must be ≤ the installed driver's CUDA version (visible in `nvidia-smi` top-right).
4. Reinstall PyTorch with the correct CUDA index URL (see Issue 2 above).
5. On multi-GPU systems, set `CUDA_VISIBLE_DEVICES=0` (or the appropriate device index).

---

## Issue 4: WSL2

**NVIDIA on WSL2:** Supported. Install the [CUDA on WSL2](https://developer.nvidia.com/cuda/wsl) driver package — do **not** install a separate CUDA toolkit inside WSL2.

**AMD on WSL2:** ROCm support inside WSL2 is limited and not officially supported. Running natively on Linux is strongly recommended for AMD GPUs.

---

## GPU-Specific Notes

### AMD RX 9070 XT (RDNA 4)

```bash
export HSA_OVERRIDE_GFX_VERSION=11.0.0
export MIOPEN_FIND_MODE=FAST
python run.py
```

MIOpen kernel tuning on first launch is slow (~5–10 min). Subsequent runs are fast.

---

## LoRA Training — Memory Fix

**Status: FIXED** (commit 731fabd — `deepcopy` → `state_dict` on CPU).

The fix saves 10–15 GB of VRAM during LoRA training by moving checkpoint save ops to CPU, eliminating the temporary GPU spike.

Validate the fix is active in your install:

```bash
python scripts/validate_lora_memory.py
```

If training still OOMs, ensure you are on the latest version and that `LORA_CPU_SAVE=1` is set (enabled by default since the fix landed).

---

## Environment Variable Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `HSA_OVERRIDE_GFX_VERSION` | Override ROCm GFX architecture string | `11.0.0` |
| `MIOPEN_FIND_MODE` | MIOpen kernel selection mode | `FAST` |
| `CUDA_VISIBLE_DEVICES` | Restrict PyTorch to specific GPUs | `0` or `0,1` |
| `MAX_CUDA_VRAM` | Simulate lower VRAM (testing only) | `8` (GB) |
| `THESE_STEP_TORCH_DTYPE` | Force dtype (`float16`/`bfloat16`) | `float16` |
| `LORA_CPU_SAVE` | Move checkpoint saves to CPU | `1` (default: on) |

---

## Still Having Issues?

1. Run `python scripts/check_gpu.py` and include the output in your report.
2. Include `torch.__version__` and (for NVIDIA) `nvidia-smi` / (for AMD) `rocminfo` output.
3. Open an issue at [github.com/ACE-Step/ACE-Step-1.5](https://github.com/ACE-Step/ACE-Step-1.5/issues).
