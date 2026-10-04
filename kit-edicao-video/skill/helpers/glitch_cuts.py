"""Add a brief CRT/VHS glitch burst over the BIG cuts of a stitched lesson.

A lesson EDL stitches several source windows; where two kept ranges are far apart
in source time (a topic/tangent was dropped), the hard join feels abrupt. This drops
a ~0.4s glitch (chromatic aberration + noise + flash, strongest at the seam) right on
those joins so the jump reads as an intentional transition.

It reads the EDL to find each join's OUTPUT timestamp (= cumulative kept duration) and
the source gap, and only glitches joins whose gap exceeds --min-gap seconds.

Usage:
    python helpers/glitch_cuts.py <in.mp4> <edl.json> -o <out.mp4> [--min-gap 30] [--intensity subtle|strong]
    python helpers/glitch_cuts.py <in.mp4> --at 23.99 --at 60.0 -o <out.mp4>   # explicit times
"""
import argparse, json, subprocess, sys

import emenda
import ff
from pathlib import Path


def cuts_from_edl(edl_path, min_gap):
    d = json.loads(Path(edl_path).read_text(encoding="utf-8"))
    ranges = d.get("ranges") or d.get("segments") or d.get("keep") or []
    cum, prev_end, cuts = 0.0, None, []
    for r in ranges:
        s = float(r.get("start", r.get("s"))); e = float(r.get("end", r.get("e")))
        # any large source discontinuity — forward (dropped tangent) OR backward (reordered windows)
        if prev_end is not None and abs(s - prev_end) >= min_gap:
            cuts.append(round(cum, 3))           # output time of this seam
        cum += e - s; prev_end = e
    return cuts


def build_filter(cuts, intensity, fps):
    half = 0.20                                   # glitch half-width (s)
    hit = 1.0 / fps * 1.5                         # hard-seam half-width (~1.5 frames)
    win = "+".join(f"between(t,{t-half:.3f},{t+half:.3f})" for t in cuts)
    seam = "+".join(f"between(t,{t-hit:.3f},{t+hit:.3f})" for t in cuts)
    if intensity == "strong":
        rh, rh2, noise, bri = 14, 30, 55, 0.10
    else:                                          # subtle (default)
        rh, rh2, noise, bri = 7, 18, 30, 0.05
    return (
        f"rgbashift=rh={rh}:bh=-{rh}:enable='{win}',"
        f"noise=alls={noise}:allf=t:enable='{win}',"
        f"eq=brightness={bri}:saturation=1.35:enable='{win}',"
        f"rgbashift=rh={rh2}:bh=-{rh2}:gv=6:enable='{seam}'"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video", type=Path)
    ap.add_argument("edl", nargs="?", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--min-gap", type=float, default=30.0)
    ap.add_argument("--at", type=float, action="append", default=[], help="explicit output time(s) to glitch")
    ap.add_argument("--intensity", choices=["subtle", "strong"], default="subtle")
    args = ap.parse_args()

    fps = ff.probe(args.video).fps
    cuts = list(args.at) or (cuts_from_edl(args.edl, args.min_gap) if args.edl else [])
    if not cuts:
        print("no big cuts found — copying through");
        ff.run(["ffmpeg", "-y", "-i", str(args.video), "-c", "copy", str(args.output)], quiet=True)
        return
    print("glitching seams at (s):", ", ".join(f"{c:.2f}" for c in cuts))

    # Cada emenda muda poucos quadros. Antes disto o filtro passava no vídeo
    # inteiro e recodificava 54 s para trocar 12 quadros — 16,5 s medidos, com
    # 0,7% de trabalho útil. Agora só os trechos das emendas são recodificados.
    JANELA = 0.20                      # o glitch dura isto em volta da emenda
    trechos = [emenda.Trecho(max(0.0, c - JANELA / 2), c + JANELA / 2, f"g{i}")
               for i, c in enumerate(cuts)]
    plano = emenda.planeja(args.video, trechos, args.output)

    trab = args.output.parent / f"_glitch_{args.output.stem}"
    trab.mkdir(parents=True, exist_ok=True)
    prontos = {}
    for pedaco in [p for p in plano.pedacos if not p.copia]:
        # A emenda junta trechos que caem no mesmo grupo de quadros, então um
        # pedaço pode carregar MAIS DE UMA emenda. Percorrer por pedaço e pôr
        # dentro dele todas as que caem ali — casar um a um perdia a segunda,
        # calado.
        dentro = [c - pedaco.inicio for c in cuts
                  if pedaco.inicio <= c <= pedaco.fim]
        alvo = trab / f"{pedaco.nome}.mp4"
        vf = build_filter(dentro or [pedaco.dur / 2], args.intensity, fps)
        ff.run(["ffmpeg", "-y", "-v", "error",
                "-ss", f"{pedaco.inicio:.3f}", "-to", f"{pedaco.fim:.3f}",
                "-i", str(args.video), "-vf", vf,
                *ff.args_video("efeito", fps=None), *ff.args_audio(), str(alvo)],
               quiet=True)
        prontos[pedaco.nome] = alvo

    emenda.executa(plano, prontos)
    print(f"done -> {args.output}  "
          f"(recodificou {plano.recodificado:.1f}s de {plano.total:.1f}s)")


if __name__ == "__main__":
    main()
