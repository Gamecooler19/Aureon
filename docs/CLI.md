# CLI Guide

`cli.py` is an interactive wizard and config-driven CLI for local ACE-Step inference.

The CLI operates in two modes:
- **Wizard mode** (default): interactive prompts to build a config and generate
- **Config mode**: load a `.toml` config and generate immediately

---

## Quick Start

```bash
# Interactive wizard
python cli.py

# Generate from a saved config
python cli.py --config config.toml

# Run wizard without generating (save config only)
python cli.py --configure

# Edit an existing config via wizard
python cli.py --configure --config config.toml
```

---

## Flags

| Flag | Description |
|------|-------------|
| `-c` / `--config` | Path to `.toml` config file to load |
| `--configure` | Wizard mode only — save config, no generation |
| `--log-level` | Logging verbosity: `TRACE`, `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (default: `INFO`) |

---

## Wizard Flow

1. Choose task type (`text2music`, `cover`, `repaint`, `lego`, `extract`, `complete`)
2. Select DiT model (from local models, or auto-download)
3. Select LM model (from local models, or auto-download)
4. Provide task-specific inputs (source audio, track types, etc.)
5. For `text2music`: choose Simple Mode (auto-generate via LM) or Manual input
6. Provide caption / description
7. Choose lyrics mode: instrumental / auto-generate / file / paste
8. Set number of outputs
9. Optionally configure advanced parameters (metadata, DiT, LM, output settings)
10. Review summary and confirm
11. Save configuration to `.toml`

Skipping advanced parameters fills everything with defaults from `GenerationParams` and `GenerationConfig`.

---

## Config Mode (`--configure`)

When `--configure` is passed, the wizard runs **without generating** and always saves a config file.

- If `--config <file>` is provided, that file is pre-loaded as starting values for the wizard.
- After the wizard completes, you choose a filename to save.
- The program exits without generating.

---

## Configuration File (`.toml`)

The wizard saves all parameters to a `.toml` file. Keys map directly to `cli.py` fields and match the `GenerationParams` / `GenerationConfig` dataclass field names.

When loaded via `--config`, all keys override the runtime defaults.

---

## Prompt Editing (`instruction.txt`)

When `thinking=True` and a config is loaded via `--config`, the CLI looks for `instruction.txt` in the project root. If found, its content is used as the pre-loaded formatted prompt for LM audio-token generation (bypassing the interactive editing step).

When running without a config (wizard mode), the CLI writes the LM's formatted prompt to `instruction.txt` and pauses so you can edit it before audio-token generation proceeds.

This allows precise control over exactly what the LM sees before generating audio codes.

---

## Task Types

| Task | Description |
|------|-------------|
| `text2music` | Generate from text description and/or lyrics |
| `cover` | Transform existing audio keeping structure, changing style |
| `repaint` | Regenerate a specific time range of audio |
| `lego` | Generate a specific instrument track in context of existing audio (base model only) |
| `extract` | Extract/isolate a specific instrument from mixed audio (base model only) |
| `complete` | Complete/extend partial tracks (base model only) |

---

## Example: Generating from a Saved Config

```toml
# config.toml
task_type = "text2music"
caption = "upbeat electronic dance music with heavy bass"
lyrics = "[Instrumental]"
bpm = 128
duration = 30.0
thinking = true
batch_size = 2
audio_format = "flac"
```

```bash
python cli.py --config config.toml
```
