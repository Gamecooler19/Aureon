# ACE-Step 1.5 — Ultimate Guide

*By Gong Junmin, developer of ACE-Step.*

---

## Mental Models

Before generating anything, establish the right expectations.

### Human-Centered Generation

ACE-Step is not designed for **one-click generation**. It is designed for **human-centered generation**.

**One-click generation** is a finite game: you have a goal, you submit a prompt, you judge the output. AI is a service. Platforms like Suno and Udio are built on this model. Your works are subject to their agreements; you cannot run the model locally, cannot fine-tune it, cannot own it.

**Human-centered generation** is an infinite game: you throw out inspiration seeds, collect results, choose interesting directions, and iterate.

- Adjust prompts and regenerate
- Use **Cover** to maintain structure while changing details
- Use **Repaint** for local modifications
- Use **Lego** to add or remove instrument layers

AI is not a servant here — it is an **inspirer**. You are the one with taste. The model has world knowledge. Together, you make something neither of you would alone.

**For human-centered generation to work, the model must be:**
1. Open-source, locally runnable, trainable — so you own your model and your works forever.
2. Fast — slow generation breaks flow state. The core of human-centered workflow is the rapid cycle of "try, listen, adjust."

---

## The Elephant Rider Metaphor

AI music generation is like the elephant rider metaphor in psychology. Consciousness rides the subconscious; the rider guides the elephant. You can give directions, but the elephant has its own inertia and temperament.

### The Iceberg Model

Text descriptions — style, instruments, emotion, structure — are just the visible tip of the audio iceberg. The most precise control would be feeding reference audio and getting back a variant. As long as you use text, the model has creative room. This is not a bug; it is the nature of the medium.

### The Elephant is Not One

The "elephant" is a fusion of: training data distribution, model scale, algorithm design, annotation bias, evaluation methodology. Any deviation in these causes it to fail to reflect your exact taste.

**You need to learn to guide the elephant, not expect it to automatically understand you.**

Taste also varies person to person. Models optimise for the popular average of human music history. If you find results "not to your taste," this may mean your taste is outside that average — which is a good thing. It means your aesthetic is non-generic. Learn to guide more precisely.

---

## Model Architecture and Selection

### Two Brains

```
User Input → [5Hz LM] → Semantic Blueprint → [DiT] → Audio
                ↓                               ↑
         Metadata Inference           Audio Craftsman
         Caption Optimisation
         Structure Planning
```

**LM — Planner (optional)**
- Infers BPM, key, time signature via Chain-of-Thought
- Rewrites and expands your caption
- Generates semantic codes containing composition and timbre hints

**DiT — Executor**
- Receives semantic codes from LM (or your direct input)
- Gradually "carves" audio from noise through diffusion
- Decides final timbre, mixing, detail

You can skip the LM entirely. In Cover mode, you provide reference audio yourself — you become the planner. In Repaint, DiT works as your editing partner from context.

### Choosing Your LM Size

| LM | Speed | World Knowledge | Memory | Best For |
|----|:-----:|:---------------:|:------:|----------|
| No LM | ⚡⚡⚡⚡ | — | — | Cover, Repaint; you do the planning |
| 0.6B | ⚡⚡⚡ | Basic | Weak | < 8 GB VRAM, rapid prototyping |
| 1.7B | ⚡⚡ | Medium | Medium | **Default recommendation** |
| 4B | ⚡ | Rich | Strong | Complex prompts, high-quality generation |

VRAM guide: < 8 GB → No LM or 0.6B. 8–16 GB → 1.7B. > 16 GB → 1.7B or 4B.

### Choosing Your DiT Model

| Model | Steps | CFG | Speed | Exclusive Tasks | Recommended For |
|-------|:-----:|:---:|:-----:|-----------------|-----------------|
| `turbo` (default) | 8 | ❌ | ⚡⚡⚡ | — | Daily use, rapid iteration |
| `turbo-shift1` | 8 | ❌ | ⚡⚡⚡ | — | Richer details |
| `turbo-shift3` | 8 | ❌ | ⚡⚡⚡ | — | Clearer timbre, minimal orchestration |
| `sft` | 50 | ✅ | ⚡ | — | Pursuing details; like to tune CFG |
| `base` | 50 | ✅ | ⚡ | extract, lego, complete | Special tasks; large-scale fine-tuning |

**Turbo shift explained:** Higher shift = more semantic structure (outline first, then fill). Lower shift = more detail focus. Start with default `turbo`; it is the most tested and balanced.

### Recommended Combinations

| Need | Combination |
|------|------------|
| Fastest speed | `turbo` + No LM or 0.6B |
| Daily use | `turbo` + 1.7B (default) |
| Pursuing details | `sft` + 1.7B or 4B |
| Special tasks (extract/lego) | `base` |
| Low VRAM (< 4 GB) | `turbo` + No LM + CPU offload |

### Downloading Models

```bash
# Default models (turbo + 1.7B LM)
python -m acestep.model_downloader

# All models
python -m acestep.model_downloader --all

# Specific model
python -m acestep.model_downloader --model acestep-v15-turbo
python -m acestep.model_downloader --model acestep-5Hz-lm-1.7B
```

---

## Guiding the Elephant: Input Control

Each generation is determined by three factors: **input**, **hyperparameters**, and **randomness**.

### I. Input — What Do You Want?

| Category | Parameter | Function |
|----------|-----------|----------|
| Task | `task_type` | `text2music`, `cover`, `repaint`, `lego`, `extract`, `complete` |
| Text | `caption` | Overall musical character: style, instruments, emotion, timbre, vocals |
| | `lyrics` | Temporal structure: lyric text, `[Verse]`/`[Chorus]` tags, vocal style hints |
| Metadata | `bpm` | Tempo (30–300) |
| | `keyscale` | Key (e.g., `C Major`, `Am`) |
| | `timesignature` | `4/4`, `3/4`, `6/8` |
| | `duration` | Target duration in seconds |
| Audio | `reference_audio` | Global timbre / mixing reference |
| | `src_audio` | Source audio for Cover / Repaint / Lego / Extract |
| | `audio_cover_strength` | 0.0–1.0: how closely to follow source structure |
| Repaint | `repainting_start` / `repainting_end` | Time window to modify (seconds) |

#### Caption Tips

1. **Be specific**: "sad piano ballad, female breathy vocal, strings" > "a sad song."
2. **Combine dimensions**: style + emotion + instruments + timbre together anchor more precisely.
3. **Leave room when you want surprises**: fewer constraints = more variation.
4. **Don't put BPM/key in Caption** — use the dedicated metadata fields.
5. **Avoid conflicting styles**: if you mix "classical strings" and "hardcore metal," the model will try to fuse them, usually not ideally. Instead, describe style evolution: "starts with strings, builds to metal, ends with hip-hop."

#### Lyrics Tips

- Structure tags are the most powerful part of lyrics. Use `[Verse 1]`, `[Chorus]`, `[Bridge]`, `[Outro - fade out]`.
- Add one modifier: `[Chorus - anthemic]` ✅ — don't stack five.
- Keep syllable counts consistent per section (6–10 per line is reliable).
- **Uppercase for intensity**: `WE ARE THE CHAMPIONS!` signals higher vocal power.
- **Parentheses for harmonies**: `We rise (we rise)` → background vocal.
- Use `[Instrumental]` or structured section tags for purely instrumental music.

**Caption and Lyrics must be consistent.** If Caption says "violin," don't put `[Guitar Solo]` in Lyrics. The model does not resolve contradictions well.

#### About Metadata

These are guidance anchors, not hard commands. `bpm=120` means "around 120 bpm" — results may be 117–123. This is intentional. Extreme values (BPM 30 or 290) have less training data and may be unstable.

**Let LM auto-infer metadata** for daily use. Set them manually only when you have a clear tempo, key, or structure requirement.

#### Audio Control

- **Reference Audio** (`reference_audio`): controls **acoustic features** globally — timbre, mixing style, performance texture. Averages across time; acts on the whole generation.
- **Source Audio** (`src_audio`): controls **semantic structure** — melody, rhythm, chords, orchestration. Used for Cover, Repaint, Lego, Extract.
- **Cover strength** (`audio_cover_strength`, 0.0–1.0): higher → stay closer to source structure; lower → more creative freedom.

---

### II. Hyperparameters — How the Model Generates

**DiT Parameters:**

| Parameter | Default | Effect |
|-----------|---------|--------|
| `inference_steps` | 8 (turbo) | More steps = finer detail, slower |
| `guidance_scale` | 7.0 | CFG strength — Base/SFT only |
| `shift` | 1.0 | Denoising trajectory — affects style balance |
| `infer_method` | `ode` | `ode` = deterministic; `sde` = adds randomness |
| `audio_cover_strength` | 1.0 | Source audio influence |

**LM Parameters:**

| Parameter | Default | Effect |
|-----------|---------|--------|
| `thinking` | True | Enable Chain-of-Thought metadata inference |
| `lm_temperature` | 0.85 | Higher = more creative; lower = more conservative |
| `lm_cfg_scale` | 2.0 | Prompt adherence force |
| `use_cot_metas` | True | LM auto-infers BPM, key, etc. |
| `use_cot_caption` | True | LM rewrites and expands your caption |

**Fix your seed when tuning.** If you change a parameter but also let the seed vary, you cannot tell whether the difference comes from the parameter or the random draw. Lock the seed first, tune, then release it.

---

### III. Random Factors — Uncertainty as a Tool

Even with identical inputs and hyperparameters, two runs may sound different. Sources:

1. **DiT's initial noise** (`seed` controls this)
2. **LM's sampling temperature** — when `lm_temperature > 0`, token selection has randomness
3. **SDE method** — injects additional noise during denoising

**Using randomness well:**

- **Batch size 2–8**: generate multiple versions at once, quickly explore the space.
- **AutoGen**: enable to continuously generate new batches in the background while you listen.
- **Scoring**: DiT Lyrics Alignment Score helps filter versions with better lyric accuracy automatically.
- **Workflow**: generate batch → score → manual pick → fix seed → tune → repaint.

---

## Custom Models via LoRA

LoRA fine-tuning lets you reshape DiT's style preferences with your own data:

- Like a specific timbre? Train with those songs.
- Want a genre the model handles poorly? Fine-tune on examples.
- Building a branded sound? Train on your own tracks.

See [LoRA_Training_Tutorial.md](LoRA_Training_Tutorial.md) for the full training walkthrough.

---

## Conclusion

This guide covers:

- **Mental Models**: human-centered design vs one-click generation.
- **Architecture**: LM planner + DiT executor.
- **Input Control**: caption, lyrics, metadata, audio reference.
- **Hyperparameters**: how to tune and when to fix your seed.
- **Randomness**: batch generation + scoring as a practical workflow.

The model is a creative collaborator. You bring taste and direction; it brings ten thousand musical possibilities. Learn to guide the elephant, and it will take you places you didn't expect.

---

*This guide will continue to be updated. Feedback welcome.*
