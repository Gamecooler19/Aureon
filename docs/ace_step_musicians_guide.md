# ACE-Step — Musician's Guide

*For creators who make music, not just play with software.*

---

```
┌─────────────────────────────────────────────────────────────┐
│                    How ACE-Step Works                        │
│                                                             │
│  Your Idea  →  [ LM: Planner ]  →  [ DiT: Craftsman ]  →  Audio │
│                Language Model      Diffusion Transformer     │
│                (optional)                                   │
└─────────────────────────────────────────────────────────────┘
```

ACE-Step 1.5 uses two cooperating AI brains:

- **LM (Language Model)** — The optional planner. Reads your description, infers BPM, key, and structure, then builds a "musical blueprint." Available in 0.6B, 1.7B, and 4B sizes.
- **DiT (Diffusion Transformer)** — The performer. Takes that blueprint and produces actual audio, note by note, texture by texture.

If you skip the LM, DiT improvises directly from your text. This is faster and useful when you're doing covers or repaint work.

---

## Getting It Running

```bash
# Install (once)
conda create -n acemusic python=3.11
conda activate acemusic
pip install -r requirements.txt
python -m acestep.model_downloader   # downloads ~5 GB of models

# Start the server
python run.py
```

Then open **http://localhost:3297** in your browser. That's the Studio UI — one page with everything.

For Docker (if you'd rather not deal with Python environments):

```bash
docker compose up -d --build
# open http://localhost:3297
```

---

## The Studio UI at a Glance

```
┌──────────────────────────────────────────────────────┐
│  http://localhost:3297                               │
│                                                      │
│  [Caption] ──────────────────────────────────────    │
│  [Lyrics]  ──────────────────────────────────────    │
│                                                      │
│  ► BPM  ► Key  ► Duration  ► Seed  ► Steps          │
│                                                      │
│  Reference Audio: [ drop file ]                      │
│  Source Audio:    [ drop file ]                      │
│                                                      │
│  [ Generate ]  [ Random Sample ]  [ Format Input ]   │
│                                                      │
│  ▶ output1.wav  ▶ output2.wav  ▶ output3.wav         │
└──────────────────────────────────────────────────────┘
```

**Caption** — describe the sound: style, instruments, emotion, vocal character.  
**Lyrics** — structure tags + actual lyric text (or `[Instrumental]` for no vocals).  
**Reference Audio** — drop in a song to copy its *timbre and mixing style*.  
**Source Audio** — drop in a song to copy its *melody and chord structure* (Cover mode).

---

## Writing Good Captions

Caption is the single most important input. The model responds to natural language — there's no special syntax required.

**Useful dimensions to describe:**

| Dimension | Examples |
|-----------|---------|
| Genre | indie pop, synthwave, jazz, lo-fi hip-hop, Carnatic fusion |
| Mood | melancholic, euphoric, tense, playful, nostalgic |
| Instruments | acoustic guitar, 808 bass, cello, tabla, electric piano |
| Voice | female breathy vocal, male baritone, choir, no vocals |
| Era | 80s synth-pop, 90s grunge, vintage Bollywood, modern trap |
| Texture | warm, crisp, muddy, airy, punchy |

**Practical tips:**

1. **Specific beats vague** — "sad piano ballad, female breathy vocal, strings" works better than "a sad song."
2. **Combine dimensions** — more dimensions = more precise result.
3. **Don't put BPM or key in Caption** — use the dedicated BPM / Key fields instead.
4. **Less detail = more freedom** — if you want surprises, describe loosely.

---

## Writing Lyrics with Structure Tags

Structure tags tell the model *what each section should sound like*, beyond the words alone:

```
[Intro]

[Verse 1]
Walking down the empty street
Quiet echoes at my feet

[Pre-Chorus]
Something's building in the air

[Chorus - anthemic]
We rise tonight
Into the light

[Bridge - whispered]
Hold on, hold on

[Outro - fade out]
```

**Tag rules:**
- One modifier is enough: `[Chorus - anthemic]` ✅ — don't stack five adjectives.
- Separate each section with a blank line.
- Keep lyrics and Caption consistent — if Caption says "violin solo," don't put `[Guitar Solo]` in lyrics.

**For instrumental music:**
```
[Intro - ambient]
[Main Theme]
[Climax]
[Outro - fade out]
```

**Useful energy tags:** `[high energy]`, `[building energy]`, `[explosive drop]`, `[breakdown]`  
**Vocal style tags:** `[raspy vocal]`, `[falsetto]`, `[whispered]`, `[powerful belting]`, `[spoken word]`

---

## Task Types — Your Creative Toolkit

```
┌─────────────────────────────────────────────────────────────────┐
│                    Creative Toolkit                              │
│                                                                  │
│  text2music  →  Generate from scratch                          │
│  cover       →  Reinterpret: same structure, new style          │
│  repaint     →  Fix a section: replace 3–90 seconds             │
│  lego        →  Add a new instrument track to existing audio    │
│  complete    →  Add full accompaniment to a single track        │
│  extract     →  Isolate one track from a mix                    │
└─────────────────────────────────────────────────────────────────┘
```

### Cover — Style Transfer

Drop in a reference track as **Source Audio**. The model copies its melody and chord structure, then regenerates in your specified style.

- Set `audio_cover_strength` higher to stay closer to the original.
- Set it lower to let the model diverge into its own interpretation.
- Change Caption and Lyrics to fully reinterpret the song in a new style.

### Repaint — Fix a Section

Keep a song you mostly like. Upload it as Source Audio, set **Repaint Start** and **Repaint End** (in seconds), and the model regenerates only that window while respecting the surrounding context.

Uses: fix a chorus, change lyrics mid-song, extend with a new ending, stitch two songs together.

### Lego — Add Tracks

Upload a track (e.g., guitar). The model adds new instruments (drums, bass, synth) that fit the groove.

### Extract / Complete

- **Extract**: Pull a single track out of a mix (e.g., isolate vocals).
- **Complete**: Give it vocals, get full accompaniment back.

> Lego, Extract, and Complete require the **Base model**. Switch model in advanced settings.

---

## Hardware & Speed Guide

| GPU VRAM | What You Can Do | Speed |
|----------|----------------|-------|
| ≤6 GB | DiT-only generation, short songs | Slow |
| 8 GB | 0.6B LM + DiT, up to 4–8 min songs | Medium |
| 12–16 GB | 1.7B LM + DiT | Good |
| ≥24 GB | 4B LM, longest songs, full batch | Fast |

**Apple Silicon (M1/M2/M3):** Fully supported via MPS/MLX — set `ACESTEP_LM_BACKEND=mlx` for best performance.

---

## Getting Better Results

```
┌──────────────────────────────────────────────────────────────┐
│  Workflow for Quality                                         │
│                                                              │
│  1. Write Caption + Lyrics                                   │
│  2. Generate 2–4 variations (set batch_size)                │
│  3. Pick best direction, note the seed                       │
│  4. Fix the seed, tune parameters, explore                   │
│  5. Repaint problem sections                                 │
│  6. Done                                                     │
└──────────────────────────────────────────────────────────────┘
```

- **Batch size 2–4** — always generate multiple versions; AI is probabilistic.
- **Fix your seed** when tweaking parameters so you can isolate what each change does.
- **Use Reference Audio** to lock in a timbre you like and reproduce it across songs.
- **Iterate with Repaint** rather than regenerating entire songs — much faster.
- **LM 4B** gives noticeably better results on complex, unusual styles if your VRAM supports it.

---

## Quick Reference

| Task | Caption | Lyrics | Source Audio | Reference Audio |
|------|---------|--------|-------------|----------------|
| Original song | Required | Optional | — | Optional |
| Cover (style transfer) | Required | Optional | Required | Optional |
| Repaint section | Optional | Optional | Required | — |
| Add instruments (Lego) | Required | — | Required | — |
| Extract track | — | — | Required | — |

**Useful env vars:**

```bash
ACESTEP_API_PORT=3297        # change server port
ACESTEP_INIT_LLM=false       # skip LM on low VRAM
ACESTEP_LM_MODEL_PATH=...    # specify LM model path
MAX_CUDA_VRAM=8              # simulate lower VRAM for testing
```

For full API documentation see [API.md](API.md).  
For training your own LoRA see [LoRA_Training_Tutorial.md](LoRA_Training_Tutorial.md).
