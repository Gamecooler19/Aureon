"""
Standalone generation info formatter.

Extracted from the Gradio UI layer so the API server has zero dependency
on any Gradio module.  Pure Python / stdlib — no UI framework required.
"""
from __future__ import annotations

from typing import Any, Dict, Optional


def _build_generation_info(
    lm_metadata: Optional[Dict[str, Any]],
    time_costs: Dict[str, float],
    seed_value: str,
    inference_steps: int,
    num_audios: int,
    audio_format: str = "flac",
) -> str:
    """Build a compact generation timing summary string.

    Args:
        lm_metadata:     LM-generated metadata dictionary (unused, kept for
                         API compatibility with existing callers).
        time_costs:      Unified time-costs dictionary produced by the
                         generation pipeline.
        seed_value:      Seed value string (unused, kept for API compat).
        inference_steps: Number of inference steps (unused, kept for API compat).
        num_audios:      Number of generated audio files in this batch.
        audio_format:    Output audio format label (e.g. "flac", "mp3", "wav32").

    Returns:
        Multi-line markdown string summarising timing, or ``""`` if no data.
    """
    if not time_costs or num_audios <= 0:
        return ""

    songs_label = f"({num_audios} song{'s' if num_audios > 1 else ''})"
    info_parts: list[str] = []

    # ── Block 1: generation time (LM + DiT) ──────────────────────────────────
    lm_total  = time_costs.get("lm_total_time", 0.0)
    dit_total = time_costs.get("dit_total_time_cost", 0.0)
    gen_total = lm_total + dit_total

    if gen_total > 0:
        avg   = gen_total / num_audios
        lines = [f"**🎵 Total generation time {songs_label}: {gen_total:.2f}s**"]
        lines.append(f"- {avg:.2f}s per song")
        if lm_total  > 0:
            lines.append(f"- LM phase {songs_label}: {lm_total:.2f}s")
        if dit_total > 0:
            lines.append(f"- DiT phase {songs_label}: {dit_total:.2f}s")
        info_parts.append("\n".join(lines))

    # ── Block 2: processing time (conversion + scoring + LRC) ────────────────
    audio_conversion_time = time_costs.get("audio_conversion_time", 0.0)
    auto_score_time       = time_costs.get("auto_score_time",        0.0)
    auto_lrc_time         = time_costs.get("auto_lrc_time",          0.0)
    proc_total            = audio_conversion_time + auto_score_time + auto_lrc_time

    if proc_total > 0:
        fmt_label = audio_format.upper() if audio_format != "wav32" else "WAV 32-bit"
        lines = [f"**🔧 Total processing time {songs_label}: {proc_total:.2f}s**"]
        if audio_conversion_time > 0:
            lines.append(f"- to {fmt_label} {songs_label}: {audio_conversion_time:.2f}s")
        if auto_score_time > 0:
            lines.append(f"- scoring {songs_label}: {auto_score_time:.2f}s")
        if auto_lrc_time   > 0:
            lines.append(f"- LRC detection {songs_label}: {auto_lrc_time:.2f}s")
        info_parts.append("\n".join(lines))

    return "\n\n".join(info_parts)
