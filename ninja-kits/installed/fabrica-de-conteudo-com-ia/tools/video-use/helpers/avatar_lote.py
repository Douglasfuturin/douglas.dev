#!/usr/bin/env python3
"""O avatar montado de um lote de cenas faladas: a Higgsfield no lugar da HeyGen.

    V=tools/video-use/.venv/bin/python
    $V tools/video-use/helpers/avatar_lote.py fatias <pasta>/avatar/lote.json         # a voz de cada cena
    $V tools/video-use/helpers/avatar_lote.py quadro <pasta>/avatar/lote.json <cena> <t>  # o quadro inicial
    $V tools/video-use/helpers/avatar_lote.py monta  <pasta>/avatar/lote.json         # o rosto.webm, com alfa
    $V tools/video-use/helpers/avatar_lote.py foto <pasta>/avatar/lote.json <cena> <t>    # a pose, sem o verde (a capa)

Quem gera é o lote.py (o mesmo lote.json, com --gera depois do pode). As cenas saem com o fundo verde
liso do quadro inicial; aqui o verde vira alfa e cada cena entra na `janela` dela, no relógio da voz.
O resultado é o `avatar.arquivo` do plano do reel editorial, sem `mapa`: o segundo do webm é o da voz.

O que este arquivo lê no lote, além do que o lote.py lê:
  voz       a voz do reel (o relógio), a partir da pasta do lote
  dur       até onde vai o rosto.webm (o fim do último trecho com rosto)
  saida     o webm (rosto.webm)
  desce     px que a pessoa desce no quadro, pra cabeça sair de baixo do que vai no topo (0)
  marcador  a foto da pessoa, PNG com alfa: a cena que ainda não baixou entra como ela, parada, com a
            ficha da cena por cima. É a prévia antes do portão, e o lugar de cada cena fica marcado
  cenas     {id: {..., "voz": [t0, t1], "audio": "fatias/<id>.wav", "janela": [a, b], "tipo": "fala"|"acao"}}
            `voz` é o trecho da voz que vai pra geração (a cena dura t1 - t0) e `audio` é onde ele fica;
            `janela` é o pedaço do reel que a cena cobre. O quadro k da cena é o segundo t0 + k/fps da voz
            A `acao` não tem voz: `desde` diz o segundo dela que cai no começo da janela (o gesto na palavra)
"""
from __future__ import annotations

import argparse
import json
import sys
import wave
from pathlib import Path

import ff

W, H, FPS = 1080, 1920, ff.FPS
FONTE = Path(__file__).resolve().parents[1].parent / "v2" / "nucleo" / "fontes" / "Inter-opsz-wght.ttf"


def ler(arq: Path) -> dict:
    arq = Path(arq)
    return {**json.loads(arq.read_text(encoding="utf-8")), "_pasta": arq.resolve().parent}


def fatias(lo: dict) -> list[Path]:
    """Corta da voz o trecho de cada cena `fala` (o `voz`) e grava no `audio` dela. PCM, sem reamostrar."""
    feitas = []
    with wave.open(str(lo["_pasta"] / lo["voz"]), "rb") as w:
        p, sr = w.getparams(), w.getframerate()
        for c, cena in lo["cenas"].items():
            if "voz" not in cena:
                continue
            t0, t1 = cena["voz"]
            w.setpos(min(int(t0 * sr), p.nframes))
            dados = w.readframes(int((t1 - t0) * sr))
            # a voz acaba antes do fim da cena: completa com silêncio, a geração pede a duração inteira
            dados += b"\0" * (int((t1 - t0) * sr) * p.sampwidth * p.nchannels - len(dados))
            out = lo["_pasta"] / cena["audio"]
            out.parent.mkdir(parents=True, exist_ok=True)
            with wave.open(str(out), "wb") as o:
                o.setparams(p)
                o.writeframes(dados)
            feitas.append(out)
    return feitas


def quadro(lo: dict, cena: str, t: float, out: Path | None = None) -> Path:
    """Um quadro da cena baixada vira a imagem inicial das cenas faladas (o `imagem` delas)."""
    out = out or lo["_pasta"] / f"{cena}.png"
    ff.run(["ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", str(lo["_pasta"] / f"{cena}.mp4"), "-frames:v", "1", str(out)],
           quiet=True)
    return out


def chave(lo: dict) -> str:
    """O filtro que tira o verde: o quanto o verde passa do maior entre o vermelho e o azul. O verde que
    o Wan desenha é escuro e pouco saturado (#2e7148 nos cantos, #448b5c no meio), e a chave de
    croma pegava a camiseta preta e o cabelo junto (o croma do preto fica perto do desse verde).
    Pela folga do verde: fundo 33–47, cabelo 4, camiseta -6, pele -40. Abaixo de `chave[0]` é pessoa,
    acima de `chave[1]` é fundo; entre os dois, a borda. O verde que sobra na borda vira o maior dos
    outros dois (despill)."""
    baixo, alto = lo.get("chave", (12, 28))
    folga = "(g(X,Y)-max(r(X,Y),b(X,Y)))"
    return (f"format=gbrap,geq=r='r(X,Y)':g='min(g(X,Y),max(r(X,Y),b(X,Y)))':b='b(X,Y)':"
            f"a='clip(255*({alto}-{folga})/{alto - baixo},0,255)'")


def foto(lo: dict, cena: str, t: float, out: Path | None = None) -> Path:
    """Um quadro da cena sem o verde, cortado na pessoa: a foto da capa é a pose que ele faz no vídeo."""
    from PIL import Image
    clip, out = lo["_pasta"] / f"{cena}.mp4", out or lo["_pasta"] / f"{cena}-foto.png"
    ff.run(["ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", str(clip), "-frames:v", "1",
            "-vf", f"{chave(lo)},format=rgba", str(out)], quiet=True)
    im = Image.open(out)
    im.crop(im.getchannel("A").getbbox()).save(out)
    return out


def marcador(lo: dict, c: str, cena: dict, out: Path) -> Path:
    """A foto parada com a ficha da cena: quem é, o que faz, que modelo, quanto dura."""
    import textwrap
    from PIL import Image, ImageDraw, ImageFont
    tela = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    foto = Image.open(lo["_pasta"] / lo["marcador"]).convert("RGBA")
    larg = lo.get("marcador_larg", W)
    foto = foto.resize((larg, round(foto.height * larg / foto.width)))
    tela.alpha_composite(foto, ((W - larg) // 2, lo.get("marcador_y", 560)))
    d = ImageDraw.Draw(tela)
    f1, f2 = ImageFont.truetype(str(FONTE), 46), ImageFont.truetype(str(FONTE), 34)
    t0, t1 = cena.get("voz", (0, 0))
    linhas = [(f"{c} · {cena.get('tipo', 'fala')}", f1), *[(l, f2) for l in textwrap.wrap(cena.get("acao", ""), 42)],
              (f"{cena.get('modelo')} · {t1 - t0:.0f} s · marcador", f2)]
    y = lo.get("marcador_ficha", 1280)
    d.rectangle([90, y - 20, W - 90, y + 20 + 52 * len(linhas)], fill=(255, 255, 255, 235), outline=(11, 13, 18, 255), width=6)
    for txt, f in linhas:
        d.text((120, y), txt, font=f, fill=(11, 13, 18, 255))
        y += 52
    tela.save(out)
    return out


def monta(lo: dict) -> Path:
    """O rosto.webm: cada cena na janela dela, o verde virando alfa; o que falta, marcador."""
    pasta, trab = lo["_pasta"], lo["_pasta"] / "_monta"
    trab.mkdir(exist_ok=True)
    cenas = sorted(((c, x) for c, x in lo["cenas"].items() if "janela" in x), key=lambda cx: cx[1]["janela"][0])
    entradas, fs, t, k = [], [], 0.0, 0
    vazio = lambda s: (["-f", "lavfi", "-t", f"{s:.3f}", "-i", f"color=c=black@0:s={W}x{H}:r={FPS},format=yuva420p"],
                       "format=yuva420p")
    for c, x in cenas + [(None, {"janela": [lo["dur"], lo["dur"]]})]:
        a, b = x["janela"]
        if a > t + 1e-3:                               # buraco entre janelas: transparente
            e, cad = vazio(a - t)
            entradas += e
            fs.append(f"[{k}:v]{cad}[v{k}]")
            k += 1
        if c is None:
            break
        clip = pasta / f"{c}.mp4"
        if clip.exists():
            desde = x["desde"] if "desde" in x else a - x["voz"][0]   # a ação: o segundo da cena no começo da janela
            entradas += ["-ss", f"{desde:.3f}", "-t", f"{b - a:.3f}", "-i", str(clip)]
            d = lo.get("desce", 0)                     # o quanto a pessoa desce no quadro (o topo fica vazio)
            fs.append(f"[{k}:v]fps={FPS},{chave(lo)},scale={W}:{H}:flags=lanczos,format=yuva420p,"
                      f"pad={W}:{H + d}:0:{d}:color=black@0,crop={W}:{H}:0:0,"
                      f"trim=duration={b - a:.3f},setpts=PTS-STARTPTS[v{k}]")
        else:
            img = marcador(lo, c, x, trab / f"{c}.png")
            entradas += ["-loop", "1", "-framerate", str(FPS), "-t", f"{b - a:.3f}", "-i", str(img)]
            fs.append(f"[{k}:v]format=yuva420p,setpts=PTS-STARTPTS[v{k}]")
        k += 1
        t = b
    out = pasta / lo.get("saida", "rosto.webm")
    fs.append("".join(f"[v{i}]" for i in range(k)) + f"concat=n={k}:v=1:a=0[out]")
    ff.run(["ffmpeg", "-y", *entradas, "-filter_complex", ";".join(fs), "-map", "[out]",
            "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-auto-alt-ref", "0", "-crf", "22", "-b:v", "0",
            "-deadline", "good", "-cpu-used", "4", "-r", str(FPS), str(out)], quiet=True)
    falta = [c for c, _ in cenas if not (pasta / f"{c}.mp4").exists()]
    print(f"avatar: {out}  {ff.dur(out):.2f}s" + (f"  marcadores: {', '.join(falta)}" if falta else ""))
    return out


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description="O avatar montado de um lote de cenas faladas (Higgsfield).")
    ap.add_argument("cmd", choices=["fatias", "quadro", "monta", "foto"])
    ap.add_argument("lote", type=Path)
    ap.add_argument("cena", nargs="?")
    ap.add_argument("t", nargs="?", type=float, default=1.0)
    a = ap.parse_args(argv)
    lo = ler(a.lote)
    if a.cmd == "fatias":
        print("\n".join(str(p) for p in fatias(lo)))
    elif a.cmd in ("quadro", "foto") and not a.cena:
        sys.exit(f"{a.cmd} pede a cena e o segundo: {a.cmd} <lote.json> <cena> <t>")
    elif a.cmd == "quadro":
        print(quadro(lo, a.cena, a.t))
    elif a.cmd == "foto":
        print(foto(lo, a.cena, a.t))
    else:
        monta(lo)


if __name__ == "__main__":
    main()
