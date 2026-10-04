"""Fix audio/video sync in a recording by shifting the audio, losslessly.

Video stream is copied (no re-encode); only the audio timeline is offset.

--audio-offset is in milliseconds:
  POSITIVE  -> delay the audio (use when audio is EARLY / ahead of the picture)
  NEGATIVE  -> advance the audio (use when audio is LATE / behind the picture)

Typical OBS-on-Mac case: mic is near-realtime but screen capture is buffered
~100-150ms, so the voice runs AHEAD of the screen -> use a positive offset
(start around +120, tune by eye).

Usage:
    python helpers/resync.py <in.mp4> -o <out.mp4> --audio-offset 120
    python helpers/resync.py <in.mp4> -o <out.mp4> --audio-offset -80

Drift (offset grows over the recording) is a clock mismatch, not a constant
offset — this tool won't fix that; lock everything to 48 kHz / use a dedicated
capture instead. Pass --drift-end to linearly correct a measured end offset
(advanced): audio is resampled so start uses --audio-offset and the end uses
--drift-end.
"""
from __future__ import annotations
import argparse, subprocess, sys

import ff
from pathlib import Path


dur = ff.dur


def main():
    ap = argparse.ArgumentParser(description="Shift audio to fix A/V sync (lossless video)")
    ap.add_argument("input", type=Path)
    ap.add_argument("-o","--output", type=Path, required=True)
    ap.add_argument("--audio-offset", type=float, required=True,
                    help="ms; +delay audio (audio early), -advance audio (audio late)")
    ap.add_argument("--drift-end", type=float, default=None,
                    help="ms; if set, linearly ramp from --audio-offset (start) to this (end)")
    ap.add_argument("--reencode-audio", action="store_true",
                    help="re-encode audio to AAC (needed for drift correction; auto-on with --drift-end)")
    args = ap.parse_args()

    src = args.input.resolve()
    out = args.output.resolve()
    off = args.audio_offset / 1000.0

    if args.drift_end is not None:
        # Linear drift: total stretch so the offset goes start->end over the file.
        # delta seconds across the whole duration:
        d = dur(src)
        end_off = args.drift_end / 1000.0
        # audio must span (d - (end_off-off)); tempo factor = d / (d - (end_off-off))
        denom = d - (end_off - off)
        if denom <= 0:
            sys.exit("invalid drift values")
        tempo = d / denom
        if not (0.5 <= tempo <= 2.0):
            sys.exit(f"drift too large for atempo ({tempo:.4f}); fix at capture instead")
        af = f"adelay={max(0,int(off*1000))}|{max(0,int(off*1000))},atempo={tempo:.6f}"
        cmd = ["ffmpeg","-y","-i",str(src),"-map","0:v","-map","0:a",
               "-af", af, "-c:v","copy","-c:a","aac","-b:a","192k","-ar","48000",
               "-movflags","+faststart", str(out)]
    else:
        # Constant offset: shift the audio input's timestamps, copy video.
        acodec = ["-c:a","aac","-b:a","192k"] if args.reencode_audio else ["-c:a","copy"]
        cmd = ["ffmpeg","-y","-i",str(src),"-itsoffset",f"{off:.3f}","-i",str(src),
               "-map","0:v","-map","1:a","-c:v","copy", *acodec,
               "-shortest","-movflags","+faststart", str(out)]
    r = ff.run(cmd, quiet=True, check=False)
    if r.returncode != 0:
        sys.exit("ffmpeg failed:\n" + r.stderr[-1500:])
    print(f"done: {out}  (audio offset {args.audio_offset:+.0f}ms"
          + (f" -> {args.drift_end:+.0f}ms drift-corrected" if args.drift_end is not None else "") + ")")


if __name__ == "__main__":
    main()
