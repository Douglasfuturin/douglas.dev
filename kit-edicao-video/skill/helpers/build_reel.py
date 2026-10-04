"""Reel vertical 9:16 a partir de uma live 16:9. Só ffmpeg.

Pipeline: silence_edl (zero-silêncio, pelo áudio real) -> render.py (corte,
voz tratada, -14 LUFS) -> crop pra 1080x1920 -> legenda queimada POR ÚLTIMO.

A legenda é queimada depois do crop, e não antes: o texto entra no quadro
9:16 já cortado. Queimar antes e cortar depois decepa a legenda pelas laterais.

Config JSON:
{
  "video": "<live.mp4>",
  "transcript": "<edit/<slug>/transcripts/<stem>.json>",   # sem ele, sem legenda
  "output": "<reel.mp4>",
  "windows": [[s, e], ...],          # trechos da live, na ordem
  "crop": "crop=810:1440:555:0",     # opcional; sem ele, faixa central
  "captions": true,                  # opcional, padrão true
  "silence_opts": ["--min-sil", "0.10"]   # opcional, repassado ao silence_edl
}

Uso: python helpers/build_reel.py <config.json>
     python helpers/build_reel.py --selftest
"""
import json, shutil, subprocess, sys
from pathlib import Path

import ff
import legendar
import render

HELP = Path(__file__).resolve().parent
PY = sys.executable
W_OUT, H_OUT = 1080, 1920


def dims(video):
    s = ff.probe(video)
    return s.largura, s.altura


def crop_central(w, h):
    """Faixa 9:16 no centro do quadro.

    Dimensão ímpar quebra o yuv420p, então tudo desce pro par mais próximo.
    """
    cw, ch = w, h
    if w * H_OUT > h * W_OUT:          # fonte mais larga que 9:16 -> corta as laterais
        cw = int(h * W_OUT / H_OUT)
    else:                              # mais alta -> corta em cima e embaixo
        ch = int(w * H_OUT / W_OUT)
    cw -= cw % 2
    ch -= ch % 2
    return f"crop={cw}:{ch}:{(w - cw) // 2}:{(h - ch) // 2}"


def main():
    cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    video = Path(cfg["video"]).resolve()
    out = Path(cfg["output"]).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    # A legenda sai do transcript da live pelos offsets do EDL (render.build_master_srt),
    # que procura em <edit_dir>/transcripts/<stem>.json. Por isso o EDL nasce no edit_dir
    # do transcript: fora dele o render não acha o transcript e o reel sai mudo de legenda.
    tr = cfg.get("transcript")
    edit_dir = Path(tr).resolve().parent.parent if tr else out.parent / "_reel"
    edit_dir.mkdir(parents=True, exist_ok=True)
    edl = edit_dir / f"edl_reel_{out.stem}.json"

    print("1) silence_edl — corta o silêncio pelo áudio real")
    cmd = [PY, str(HELP / "silence_edl.py"), "--video", str(video), "-o", str(edl)]
    for w in cfg["windows"]:
        cmd += ["--range", str(w[0]), str(w[1])]
    cmd += cfg.get("silence_opts", [])
    ff.run(cmd)

    print("2) render — corte, voz tratada, -14 LUFS")
    cut = edit_dir / f"_cut_{out.stem}.mp4"
    # --height na altura da live: sem isso o render entrega o corte reescalado (1080 de
    # altura por padrão) e o `crop`, que foi medido no quadro da live, não cabe mais.
    # ponytail: numa fonte 4K isso deixa o render lento; o jeito de acelerar é medir o
    # crop no quadro reescalado, não aqui.
    lw, lh = dims(video)
    ff.run([PY, str(HELP / "render.py"), str(edl), "-o", str(cut),
            "--height", str(lh), "--voice-enhance", "--no-subtitles"], quiet=True)

    srt = None
    if cfg.get("captions", True) and tr:
        print("3) legenda na linha do tempo já cortada")
        srt = edit_dir / f"_reel_{out.stem}.srt"
        render.build_master_srt(json.loads(edl.read_text(encoding="utf-8")), edit_dir, srt)

    print("4) crop 9:16")
    crop = cfg.get("crop") or crop_central(lw, lh)
    vf = (f"{crop},scale={W_OUT}:{H_OUT}:force_original_aspect_ratio=increase,"
          f"crop={W_OUT}:{H_OUT},setsar=1,fps=30")
    # A legenda entra num passo à parte, depois do crop: queimada antes, ela seria
    # cortada junto com as laterais do quadro.
    alvo = (edit_dir / f"_semlegenda_{out.stem}.mp4") if srt else out
    # O `ff.run` estoura com o comando na mensagem: engolido, um crop que não cabe
    # no quadro falha mudo e o único sinal é a ausência do arquivo.
    # -c:a copy: o render já normalizou em -14 LUFS. Re-encodar aqui só perde.
    ff.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(cut),
            "-vf", vf, *ff.args_video("reel", fps=30),
            "-c:a", "copy", "-movflags", "+faststart", str(alvo)])

    if srt:
        print("5) legenda")
        if legendar.queimar(alvo, srt, out):
            alvo.unlink(missing_ok=True)
        else:
            shutil.move(str(alvo), str(out))
            print(f"       sem legenda; o .srt ficou em {srt}")

    print(f"pronto -> {out}")


def _selftest():
    # 16:9 comum -> corta as laterais, altura inteira
    assert crop_central(1920, 1080) == "crop=606:1080:657:0", crop_central(1920, 1080)
    # já vertical 9:16 -> não corta nada
    assert crop_central(1080, 1920) == "crop=1080:1920:0:0", crop_central(1080, 1920)
    # quadrado -> corta em cima e embaixo? não: 1:1 é mais largo que 9:16, corta lateral
    assert crop_central(1000, 1000) == "crop=562:1000:219:0", crop_central(1000, 1000)
    # mais alto que 9:16 -> corta topo e base
    assert crop_central(1080, 2400) == "crop=1080:1920:0:240", crop_central(1080, 2400)
    # nada ímpar sai daqui
    for w, h in ((1919, 1079), (1281, 721), (999, 1777)):
        c = crop_central(w, h)
        cw, ch = (int(x) for x in c[5:].split(":")[:2])
        assert cw % 2 == 0 and ch % 2 == 0, c
    print("build_reel selftest ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    else:
        main()
