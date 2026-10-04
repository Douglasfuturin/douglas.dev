"""Wrap a video with a CRT TV turn-on (start) and turn-off (end) effect.

Turn-off: the picture flashes bright, squashes vertically to a thin glowing
scanline, collapses horizontally to a dot, then fades to black — the classic
old-television power-down. Turn-on is the same animation reversed.

The animation is built from the first frame (on) and last frame (off) as a
brief freeze (~0.4s) — imperceptible at speed, and keeps it deterministic.
Optional synized CRT static/thunk audio on each effect.

Usage:
    python helpers/tv_effect.py <in.mp4> -o <out.mp4>
    python helpers/tv_effect.py <in.mp4> -o <out.mp4> --on-dur 0.4 --off-dur 0.55
    python helpers/tv_effect.py <in.mp4> -o <out.mp4> --no-sound
"""
from __future__ import annotations
import argparse, json, subprocess, sys, tempfile
from pathlib import Path
import numpy as np
from PIL import Image

import emenda
import ff

# No bundled SFX by default: the synth below is generated here, so it carries no
# third-party rights. Pass --on-sound/--off-sound for custom files, --no-sound to mute.


def probe(path: Path):
    p = ff.probe(path)
    return p.largura, p.altura, p.fps


def grab_frame(path: Path, dest: Path, last: bool):
    cmd = ["ffmpeg","-y"]
    if last:
        cmd += ["-sseof","-0.3"]
    cmd += ["-i", str(path), "-update","1","-frames:v","1", str(dest)]
    ff.run(cmd, quiet=True)


def collapse(base: np.ndarray, n: int, W: int, H: int, ease: str = "in"):
    """Return n frames going from full picture (frame 0) to black (frame n-1).

    ease="in"  : slow start, fast finish (good for turn-ON when reversed).
    ease="out" : fast start, slow finish — the squash snaps on frame 0, so it
                 lands on a percussive SFX whose hit is at t=0 (turn-OFF).
    """
    def shape(x):
        return (1 - (1 - x) ** 2) if ease == "out" else (x ** 2)
    src = Image.fromarray(base)
    frames = []
    for i in range(n):
        p = i/(n-1)
        canvas = np.zeros((H, W, 3), np.float32)
        if p < 0.55:                                  # vertical squash + brighten
            q = shape(p/0.55)
            ch = max(2, int(round(H*(1-q))))
            bright = 1.0 + 1.9*q
            r = np.asarray(src.resize((W, ch), Image.LANCZOS)).astype(np.float32)
            r = np.clip(r*bright, 0, 255)
            y0 = (H-ch)//2
            canvas[y0:y0+ch] = r
        elif p < 0.85:                                # horizontal collapse to dot
            q = shape((p-0.55)/0.30)
            cw = max(2, int(round(W*(1-q))))
            lh = max(2, int(round(4 - 2*q)))
            r = np.asarray(src.resize((cw, lh), Image.LANCZOS)).astype(np.float32)
            r = np.clip(r*2.8, 0, 255)
            x0, y0 = (W-cw)//2, (H-lh)//2
            canvas[y0:y0+lh, x0:x0+cw] = r
        else:                                         # bright dot fades out
            q = (p-0.85)/0.15
            d = max(1, int(round(5*(1-q))))
            v = float(np.clip(255*2.5*(1-q), 0, 255))
            cy, cx = H//2, W//2
            canvas[cy-d:cy+d, cx-d:cx+d] = (v, v, v)
        frames.append(np.clip(canvas, 0, 255).astype(np.uint8))
    return frames


def write_png_seq(frames, d: Path):
    for i, f in enumerate(frames):
        Image.fromarray(f).save(d / f"{i:04d}.png")


def encode_effect(seq_dir: Path, n: int, W: int, H: int, fps: int, dur: float,
                  out: Path, sound: bool, kind: str,
                  audio_file: Path | None = None, gain: float = 1.0):
    """Encode a PNG sequence into a clip. Audio priority: custom file > synth > silent.

    When audio_file is given it is baked in starting at frame 0 — so a sound
    placed on the OFF clip begins exactly when the collapse begins, frame-locked
    (no delay math, no drift)."""
    cmd = ["ffmpeg","-y","-framerate", str(fps), "-i", str(seq_dir/"%04d.png")]
    if audio_file:
        cmd += ["-i", str(audio_file),
                "-filter_complex",
                f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={gain},apad[a]",
                "-map","0:v","-map","[a]"]
    elif sound:
        # static burst (pink noise, fast fade) + low thunk (sine), mixed.
        # anoisesrc/sine are lavfi *generators* inside filter_complex (no -i needed).
        amp, base_fade = (0.25, 0.7) if kind == "off" else (0.22, 0.55)
        freq, sfade = (70, 0.5) if kind == "off" else (90, 0.4)
        a = (f"anoisesrc=color=pink:amplitude={amp}:duration={dur}[n];"
             f"sine=frequency={freq}:duration={dur}[s];"
             f"[n]afade=t=out:st=0:d={dur*base_fade:.3f}[nf];"
             f"[s]afade=t=out:st=0:d={dur*sfade:.3f},volume=0.6[sf];"
             f"[nf][sf]amix=inputs=2:normalize=0[a]")
        cmd += ["-filter_complex", a, "-map","0:v","-map","[a]"]
    else:
        cmd += ["-f","lavfi","-i","anullsrc=r=48000:cl=stereo","-map","0:v","-map","1:a"]
    # PNG frames are already exactly W×H; no scaling needed (avoids -vf vs
    # -filter_complex conflict). SAR defaults to 1:1 for PNG → matches main.
    cmd += ["-t", f"{dur:.3f}", "-r", str(fps),
            *ff.args_video("efeito", fps=None),
            *ff.args_audio(),
            str(out)]
    ff.run(cmd, quiet=True)


audio_dur = ff.dur


def main():
    ap = argparse.ArgumentParser(description="Add CRT TV turn-on/off to a video")
    ap.add_argument("input", type=Path)
    ap.add_argument("-o","--output", type=Path, required=True)
    ap.add_argument("--on-dur", type=float, default=0.40)
    ap.add_argument("--off-dur", type=float, default=0.40)
    ap.add_argument("--on-sound", type=Path, default=None, help="WAV/audio for the turn-on (overrides synth)")
    ap.add_argument("--off-sound", type=Path, default=None, help="WAV/audio for the turn-off (overrides synth)")
    ap.add_argument("--sfx-gain", type=float, default=1.0, help="Volume multiplier for the custom SFX")
    ap.add_argument("--no-sound", action="store_true")
    args = ap.parse_args()

    src = args.input.resolve()
    W, H, fps = probe(src)
    main_dur = audio_dur(src)
    use_sfx = bool(args.on_sound or args.off_sound)
    # effect clips carry the synth sound ONLY when no external SFX and not muted
    clip_sound = (not use_sfx) and (not args.no_sound)
    for s in (args.on_sound, args.off_sound):
        if s and not s.exists():
            sys.exit(f"sound file not found: {s}")

    n_on = max(4, round(args.on_dur*fps))
    n_off = max(4, round(args.off_dur*fps))
    # If the off SFX is longer than the collapse, extend the off clip with black
    # so the sound plays fully over the black tail and resolves at the cut.
    off_sfx_dur = audio_dur(args.off_sound.resolve()) if args.off_sound else 0.0
    off_clip_dur = max(args.off_dur, off_sfx_dur) if args.off_sound else args.off_dur

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        first, last = td/"first.png", td/"last.png"
        grab_frame(src, first, last=False)
        grab_frame(src, last, last=True)

        on_dir, off_dir = td/"on", td/"off"; on_dir.mkdir(); off_dir.mkdir()
        # ON = reverse of collapse(first) ; OFF = collapse(last)
        on_frames = list(reversed(collapse(np.asarray(Image.open(first).convert("RGB")), n_on, W, H)))
        off_frames = collapse(np.asarray(Image.open(last).convert("RGB")), n_off, W, H, ease="out")
        total_off = max(n_off, round(off_clip_dur*fps))
        if total_off > len(off_frames):                       # pad black tail
            off_frames += [np.zeros((H, W, 3), np.uint8)] * (total_off - len(off_frames))
        write_png_seq(on_frames, on_dir)
        write_png_seq(off_frames, off_dir)

        on_clip, off_clip = td/"on.mp4", td/"off.mp4"
        encode_effect(on_dir, n_on, W, H, fps, args.on_dur, on_clip, clip_sound, "on")
        # OFF sound is baked into the off clip -> frame-locked to the collapse start.
        encode_effect(off_dir, total_off, W, H, fps, off_clip_dur, off_clip, clip_sound, "off",
                      audio_file=(args.off_sound.resolve() if args.off_sound else None),
                      gain=args.sfx_gain)

        # Concat on + main + off. The OFF sfx is already inside off_clip.
        # The ON sfx is overlaid from t=0 so it can ring into the lesson.
        inputs = [on_clip, src, off_clip]
        fc = "[0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[v][ca]"
        aout = "[ca]"
        if args.on_sound:
            g = args.sfx_gain
            inputs.append(args.on_sound.resolve())
            fc += (f";[3:a]aresample=48000,aformat=channel_layouts=stereo,volume={g},adelay=0|0[on]"
                   f";[ca][on]amix=inputs=2:normalize=0:dropout_transition=100000,"
                   f"{ff.limitador(0.97)}[a]")
            aout = "[a]"

        # A imagem é COPIADA, e só o som é recodificado.
        #
        # Antes daqui, a junção era por filtro e recodificava o vídeo inteiro
        # para acrescentar 0,8 s de liga-desliga nas pontas: 10,1 s medidos num
        # clipe de 54 s. Mas o som da abertura toca por cima do começo da aula de
        # propósito, então o áudio precisa de uma passada — a imagem, não.
        #
        # A junção pelo demultiplexador exige que os três tenham os mesmos
        # parâmetros, e é por isso que eles moram todos na costura B.
        # A junção é a da emenda, e não uma escrita aqui: um conserto no corte
        # em quadro-chave ou na ordem dos pedaços tem que valer para o glitch E
        # para a abertura. Duas cópias divergem, e este projeto já pagou por
        # isso em cinco arquivos com `run` próprio.
        lista = emenda.lista_de_partes([on_clip, src, off_clip], Path(td))
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lista)]
        mapa = ["-map", "0:v", "-map", "0:a"]
        if args.on_sound:
            g = args.sfx_gain
            cmd += ["-i", str(args.on_sound.resolve())]
            cmd += ["-filter_complex",
                    f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={g}[on];"
                    f"[0:a][on]amix=inputs=2:normalize=0:dropout_transition=100000,"
                    f"{ff.limitador(0.97)}[a]"]
            mapa = ["-map", "0:v", "-map", "[a]"]
        cmd += [*mapa, "-c:v", "copy", *ff.args_audio(),
                "-movflags", "+faststart", str(args.output.resolve())]
        r = ff.run(cmd, quiet=True, check=False)
        if r.returncode != 0:
            sys.exit("ffmpeg failed:\n" + r.stderr[-1800:])
    sfx = "custom SFX" if use_sfx else ("synth" if clip_sound else "silent")
    print(f"done: {args.output}  ({n_on} on + main + {total_off} off frames @ {W}x{H}@{fps}, {sfx})")


if __name__ == "__main__":
    main()
