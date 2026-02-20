# LoRA Training Tutorial

Train a custom LoRA adapter to reshape ACE-Step's style preferences with your own audio data.

---

## Hardware Requirements

| VRAM | Notes |
|------|-------|
| 16 GB (minimum) | Generally sufficient; very long songs may OOM |
| 20 GB+ (recommended) | Handles full-length songs; usage typically ~17 GB during training |

---

## Disclaimer

Please use your own original works to train your LoRA. Technology should be used reasonably and lawfully. Respect artists' creations.

---

## Data Preparation

> **Tip:** If you are uncomfortable with scripting, you can paste this document into any AI coding tool (Claude, Copilot, Cursor, etc.) and ask it to handle the scripting tasks for you.

### Dataset Structure

Training data for each song consists of three files:

```
dataset/
├── song1.mp3               # Audio (mp3/wav/flac/ogg/opus)
├── song1.lyrics.txt        # Lyrics
├── song1.json              # Metadata annotations (optional)
├── song1.caption.txt       # Caption (optional, or in JSON)
├── song2.mp3
├── song2.lyrics.txt
└── ...
```

JSON annotation format (all fields optional):

```json
{
    "caption": "A high-energy J-pop track with synthesizer leads and fast tempo",
    "bpm": 190,
    "keyscale": "D major",
    "timesignature": "4",
    "language": "ja"
}
```

### Lyrics

Save lyrics as `{filename}.lyrics.txt` alongside the audio file. The scanner also recognises `{filename}.txt` for backward compatibility.

**Getting lyrics if you don't have them:**

| Tool | Structural Tags | Service Type |
|------|----------------|-------------|
| [Whisper](https://github.com/openai/whisper) | No | Self-hosted / Paid API |
| [ElevenLabs](https://elevenlabs.io/app/developers) | No | Paid API (generous free tier) |
| [Gemini](https://aistudio.google.com/) | Yes | Paid API |
| [acestep-transcriber](https://huggingface.co/ACE-Step/acestep-transcriber) | No | Self-hosted |

Batch processing scripts are under `scripts/lora_data_prepare/`:
- `whisper_transcription.py` — via OpenAI Whisper API
- `elevenlabs_transcription.py` — via ElevenLabs API

**Always manually review and correct transcribed lyrics.** If you have LRC-format lyrics, strip the timestamps:

```python
import re

def clean_lrc_content(lines):
    result = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        cleaned = re.sub(r"\[\d{2}:\d{2}\.\d{1,3}\]", "", line)
        result.append(cleaned)
    while result and not result[-1]:
        result.pop()
    return result
```

**Adding structural tags (optional but helpful):**

Tags like `[Verse]`, `[Chorus]`, `[Bridge]` help the model learn song structure. Use Gemini to add these to existing lyrics automatically.

```
[Intro]
La la la...

[Verse 1]
Walking down the empty street
Echoes dancing at my feet

[Chorus]
We are the stars tonight
```

### Getting BPM and Key

Use [Key-BPM-Finder](https://vocalremover.org/key-bpm-finder) online:

1. Open the site, click **Browse my files** and select your audio files.
2. Processing is local — no files are uploaded to a server.
3. Click **Export CSV** to download annotations.

CSV example:
```
File,Artist,Title,BPM,Key,Camelot
song1.wav,,,190,D major,10B
song2.wav,,,128,A minor,8A
```

Place the CSV in your dataset folder. The scanner reads it automatically.

### Getting Captions

Options:
- **Auto Label via the server**: start the server with `ACESTEP_INIT_LLM=true`, then use the LoRA Training section in the Studio UI.
- **Gemini API**: use `scripts/lora_data_prepare/gemini_caption.py` for batch processing — generates both `{filename}.lyrics.txt` and `{filename}.caption.txt`.

---

## Data Preprocessing

Once data is prepared, use the Studio UI (`http://localhost:3297`) for review and preprocessing.

> **Important:** During preprocessing you don't want models pre-loaded in GPU. Start the server with service init disabled:
> ```bash
> ACESTEP_INIT_SERVICE=false python run.py
> ```

### Step 1: Load Models

In the Studio UI, initialise the server. If you need LM for caption generation, select a model (0.6B / 1.7B / 4B). If you already have captions, skip LM loading.

### Step 2: Load Data

Navigate to the **LoRA Training** section of the UI. Enter your dataset directory path and click **Scan**.

The scanner recognises:

| File | Description |
|------|-------------|
| `*.mp3` / `*.wav` / `*.flac` / ... | Audio |
| `{filename}.lyrics.txt` | Lyrics |
| `{filename}.caption.txt` | Caption |
| `{filename}.json` | BPM / key / caption / language metadata |
| `*.csv` | Batch BPM+key from Key-BPM-Finder |

### Step 3: Review Dataset

Check the loaded table:
- **Duration** — read from audio
- **Lyrics** — ✅ if `.lyrics.txt` found, ❌ otherwise
- **Labeled** — ✅ if caption exists
- **All Instrumental** — uncheck unless your dataset is purely instrumental
- **Genre Ratio** — keep at 0 (LM-generated genre tags are less descriptive than captions)

### Step 4: Auto Label (if needed)

If captions are missing and LM is loaded: click **Auto Label** to run inference. BPM/key must already exist — LM will hallucinate metadata if BPM/key are absent.

### Step 5: Review and Edit Entries

Review individual entries. Click **Save** after editing each one.

### Step 6: Save Dataset

Export the dataset as a JSON file by entering a save path and clicking Save.

### Step 7: Preprocess — Generate Tensor Files

> If you used LM for captions and VRAM is tight, restart the server **without LM** before this step:
> ```bash
> ACESTEP_INIT_LLM=false python run.py
> ```

Enter the save path for tensor files and click **Start Preprocessing**. Wait for completion.

---

## Training

> After preprocessing, restart the server again to free VRAM before training.

1. In the Studio UI, navigate to **Train LoRA**.
2. Load the tensor file path.
3. Configure parameters (defaults are reasonable for most use cases).

### Parameter Reference

| Parameter | Description | Suggested Value |
|-----------|-------------|-----------------|
| **Max Epochs** | Depends on dataset size | ~100 songs → 500 epochs; ~15 songs → 800 epochs |
| **Batch Size** | Increase if VRAM allows | 1 (default); try 2–4 if you have headroom |
| **Save Every N Epochs** | Checkpoint interval | Lower for small epoch counts |

> **LoKr Recommendation:** LoKR (Kronecker-factored LoRA) is ~10× faster than standard LoRA training at the same quality. Use the **Train LoKr** tab in the Studio UI, or the Side-Step CLI toolkit.

4. Click **Start Training** and wait.

---

## Using Your LoRA

1. Restart the server and load models (no LM needed at inference):
   ```bash
   python run.py
   ```
2. In the Studio UI, locate **Load LoRA** and enter the path to your trained adapter weights.
3. Generate.

---

## Advanced Training with Side-Step

For CLI-based workflows, corrected timestep sampling, LoKR adapters, VRAM optimisation, and gradient sensitivity analysis, use the community **[Side-Step](https://github.com/koda-dernet/Side-Step)** toolkit.

| Topic | Description |
|-------|-------------|
| Getting Started | Installation, prerequisites, first-run setup |
| End-to-End Tutorial | Complete walkthrough from raw audio to generation |
| Dataset Preparation | JSON schema, audio formats, metadata, custom tags |
| Training Guide | LoRA vs LoKR, corrected vs vanilla mode, hyperparameter guide |
| Using Your Adapter | Output layout, loading in Studio UI, LoKR limitations |
| VRAM Optimisation | GPU memory profiles and strategies |
| Estimation Guide | Gradient sensitivity analysis for targeted training |
| Shift and Timestep Sampling | How training timesteps work and why Side-Step differs |
