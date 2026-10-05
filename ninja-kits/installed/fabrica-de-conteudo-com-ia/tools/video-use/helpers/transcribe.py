"""Transcribe a video LOCALLY with faster-whisper (Scribe-compatible output).

Drop-in replacement for the original ElevenLabs Scribe transcriber. Emits the
SAME JSON shape the rest of the pipeline consumes:

    {"language": "en", "text": "...",
     "words": [{"type": "word", "text": "Hello", "start": 0.12, "end": 0.41,
                "speaker_id": "speaker_0"}, ...]}

Downstream (pack_transcripts.py, render.py) only need `words` with
`type == "word"` and `text/start/end`. Speaker diarization is collapsed to a
single speaker (these are solo talking-head/lesson recordings).

Why local Whisper instead of Scribe: no API key, no cost, runs on-device.
Tradeoff: vanilla Whisper tends to normalize away disfluencies ("um", "uh").
We counter that with `hotwords` seeded with fillers + word-level timestamps
+ VAD, which keeps most of them. Silence-gap cutting works
regardless, since gaps come from word start/end deltas.

Usage:
    python helpers/transcribe.py <video_path>
    python helpers/transcribe.py <video_path> --edit-dir /custom/edit
    python helpers/transcribe.py <video_path> --language en
    python helpers/transcribe.py <video_path> --model medium.en

Model is chosen via (highest priority first): --model, env
VIDEO_USE_WHISPER_MODEL, else the default below. CPU/int8 by default; override
with env VIDEO_USE_WHISPER_DEVICE / VIDEO_USE_WHISPER_COMPUTE.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

import ff

# Default model. MULTILINGUAL "medium" (not ".en") because the primary user
# records in Portuguese; an English-only model returns garbage on PT audio.
# medium = good verbatim accuracy, ~1.5GB, sane on Apple Silicon CPU. Drop to
# "small" for speed, bump to "large-v3" for max accuracy. Override via env.
DEFAULT_MODEL = os.environ.get("VIDEO_USE_WHISPER_MODEL", "medium")
DEFAULT_DEVICE = os.environ.get("VIDEO_USE_WHISPER_DEVICE", "cpu")
DEFAULT_COMPUTE = os.environ.get("VIDEO_USE_WHISPER_COMPUTE", "int8")
# Language: default Portuguese (primary user). Set "" / "auto" to auto-detect,
# or any ISO code. CLI --language overrides this.
DEFAULT_LANG = os.environ.get("VIDEO_USE_WHISPER_LANG", "pt") or None
if DEFAULT_LANG in ("", "auto", "none"):
    DEFAULT_LANG = None

# Seed prompt biases Whisper toward transcribing disfluencies verbatim instead
# of silently cleaning them up. This is the single most important knob for
# filler-word editing. Per-language so PT fillers ("é", "tipo", "né") survive.
FILLER_PROMPTS = {
    "pt": "Então, é, tipo, né, hum, ãã, assim, sabe, quer dizer, "
          "bom, na verdade, basicamente, aí, então tá.",
    "en": "Okay, so, um, you know, like, uh, I mean, well, hmm, "
          "actually, basically, right, so yeah, uh-huh.",
}


def _filler_prompt(lang: str | None) -> str:
    return FILLER_PROMPTS.get((lang or "en").lower(), FILLER_PROMPTS["en"])


# Nomes que o canal fala o tempo todo e o whisper erra ("cloud code").
TERMOS = ("Claude Code, Claude, Anthropic, n8n, Kiwify, ngrok, ChatGPT, MCP, "
          "Composio, Hermes Agent, vibe coding, JSON, localhost.")


def _dica(lang: str | None) -> str:
    """Vai no `hotwords`, que entra em TODA janela de 30s. Era `initial_prompt`,
    que só valia na primeira: com `condition_on_previous_text=False` o
    faster-whisper descarta o prompt depois dela, e o resto da gravação saía sem
    os fillers que o `clean_edl` corta. Medido em 5 min de live, large-v3:
    fillers depois dos 30s 21 -> 32, "Claude" 0 -> 6 de 8 (o resto seguia
    "cloud"), nenhum termo da lista inventado. Custo: ~50% mais tempo."""
    return f"{_filler_prompt(lang)} {TERMOS}"

# Module-level model cache. CTranslate2 inference is thread-safe, so a single
# shared model serves transcribe_batch.py's parallel workers without N copies
# in RAM. Guarded so only one thread pays the load cost.
_MODEL_CACHE: dict[str, object] = {}
_MODEL_LOCK = threading.Lock()


def load_api_key() -> str:
    """Compatibility shim. The Scribe transcriber needed an API key; the local
    Whisper backend does not. transcribe_batch.py imports this symbol, so it
    must keep existing. Returns an empty string."""
    return ""


def _get_model(model_name: str, device: str, compute_type: str):
    key = f"{model_name}|{device}|{compute_type}"
    cached = _MODEL_CACHE.get(key)
    if cached is not None:
        return cached
    with _MODEL_LOCK:
        cached = _MODEL_CACHE.get(key)
        if cached is not None:
            return cached
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            sys.exit(
                "faster-whisper not installed. Run `uv add faster-whisper` "
                "(or `uv sync`) inside the video-use repo."
            )
        model = WhisperModel(model_name, device=device, compute_type=compute_type)
        _MODEL_CACHE[key] = model
        return model


def extract_audio(video_path: Path, dest: Path) -> None:
    # Normalize loud + level BEFORE transcription so whisper word-timestamps land
    # precisely on word edges. Quiet/variable audio makes faster-whisper report word
    # `end`s early (and VAD trim consonant tails) -> silence-cut clips mid-word.
    #   loudnorm  -> consistent perceived loudness (I=-14)
    #   dynaudnorm-> lifts quiet passages so soft consonants (s/t/d tails) stay audible
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vn", "-ac", "1", "-ar", "16000",
        "-af", ff.TRANSCRICAO_AF,
        "-c:a", "pcm_s16le",
        str(dest),
    ]
    ff.run(cmd, quiet=True)


def _transcribe_audio(
    audio_path: Path,
    model_name: str,
    device: str,
    compute_type: str,
    language: str | None,
) -> dict:
    model = _get_model(model_name, device, compute_type)

    # English-only models (".en") reject a language arg of anything else.
    lang = language
    if model_name.endswith(".en"):
        lang = "en"

    segments, info = model.transcribe(
        str(audio_path),
        language=lang,
        word_timestamps=True,
        vad_filter=True,
        condition_on_previous_text=False,  # avoids runaway repetition loops
        hotwords=_dica(lang),
        beam_size=5,
    )

    words: list[dict] = []
    text_parts: list[str] = []
    prev_end: float | None = None
    for seg in segments:
        seg_words = getattr(seg, "words", None) or []
        for w in seg_words:
            raw = (w.word or "").strip()
            if not raw:
                continue
            start = float(w.start)
            end = float(w.end)
            # Synthesize a 'spacing' token in gaps so pack_transcripts.py
            # phrase-breaking has the same shape it expects from Scribe. The
            # gap-from-prev-end path also handles this, but emitting spacing
            # keeps the JSON maximally Scribe-like.
            if prev_end is not None and start - prev_end > 0.0:
                words.append({
                    "type": "spacing",
                    "text": " ",
                    "start": round(prev_end, 3),
                    "end": round(start, 3),
                    "speaker_id": "speaker_0",
                })
            words.append({
                "type": "word",
                "text": raw,
                "start": round(start, 3),
                "end": round(end, 3),
                "speaker_id": "speaker_0",
            })
            text_parts.append(raw)
            prev_end = end

    return {
        "language": getattr(info, "language", lang or "en"),
        "language_probability": getattr(info, "language_probability", None),
        "duration": getattr(info, "duration", None),
        "text": " ".join(text_parts),
        "words": words,
    }


def transcribe_one(
    video: Path,
    edit_dir: Path,
    api_key: str | None = None,  # ignored; kept for signature compatibility
    language: str | None = DEFAULT_LANG,
    num_speakers: int | None = None,  # ignored; single-speaker collapse
    model_name: str = DEFAULT_MODEL,
    device: str = DEFAULT_DEVICE,
    compute_type: str = DEFAULT_COMPUTE,
    verbose: bool = True,
) -> Path:
    transcripts_dir = edit_dir / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    out_path = transcripts_dir / f"{video.stem}.json"

    # A fonte refeita no mesmo nome (a voz gerada de novo) invalida a transcrição: o
    # cache só pelo nome devolvia o que a voz velha disse.
    if out_path.exists() and out_path.stat().st_mtime >= video.stat().st_mtime:
        if verbose:
            print(f"cached: {out_path}")
        return out_path

    if verbose:
        print(f"transcribing {video.name} with faster-whisper [{model_name}] ...")
    t0 = time.time()

    with tempfile.TemporaryDirectory() as td:
        audio_path = Path(td) / "audio.wav"
        extract_audio(video, audio_path)
        result = _transcribe_audio(audio_path, model_name, device, compute_type, language)

    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if verbose:
        n = sum(1 for w in result["words"] if w.get("type") == "word")
        print(f"  -> {out_path}  ({n} words, {time.time() - t0:.1f}s)")
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Transcribe a video locally with faster-whisper (Scribe-compatible JSON)"
    )
    ap.add_argument("video", type=Path, help="Path to video file")
    ap.add_argument("--edit-dir", type=Path, default=None,
                    help="Edit output directory (default: <video_parent>/edit)")
    ap.add_argument("--language", type=str, default=DEFAULT_LANG,
                    help=f"ISO language code (default: {DEFAULT_LANG or 'auto'}). "
                         "Pass 'auto' to force detection.")
    ap.add_argument("--num-speakers", type=int, default=None,
                    help="Ignored (single-speaker). Kept for CLI compatibility.")
    ap.add_argument("--model", type=str, default=DEFAULT_MODEL,
                    help=f"faster-whisper model (default: {DEFAULT_MODEL}). "
                         "e.g. small.en, medium.en, large-v3")
    args = ap.parse_args()

    video = args.video.resolve()
    if not video.exists():
        sys.exit(f"video not found: {video}")

    edit_dir = (args.edit_dir or (video.parent / "edit")).resolve()

    lang = args.language
    if lang in ("", "auto", "none"):
        lang = None

    transcribe_one(
        video=video,
        edit_dir=edit_dir,
        language=lang,
        model_name=args.model,
    )


if __name__ == "__main__":
    main()
