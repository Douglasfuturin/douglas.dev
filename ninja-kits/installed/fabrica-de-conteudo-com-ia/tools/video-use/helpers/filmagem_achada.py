#!/usr/bin/env python3
"""Acabamento de filmagem achada (found footage) para as cenas do banco.

    python filmagem_achada.py cena.mp4 saida.mp4 --tipo celular|cctv|filmadora|telejornal|documentario [--hora 03:12:47] [--cam 02] [--data 2026-09-27]

A cena gerada sai limpa demais: câmera estável, foco perfeito, compressão nenhuma.
Filmagem de verdade treme, caça o foco, perde detalhe no arquivo e carrega o que o
aparelho escreve na imagem (REC, hora, número da câmera). Isto põe essas marcas por
cima, iguais em todo o banco, e é o que costura cenas de modelos diferentes.

- `celular`: tremor de mão, foco caçando no começo, compressão, REC com relógio.
- `cctv`: câmera parada, grão forte, cor lavada, vinheta, CAM e relógio correndo.
- `filmadora`: tremor leve, cor deslocada nas bordas, imagem mole, data no canto (padrão: hoje).
- `telejornal`: imagem limpa com selo "AO VIVO" e "PLANTÃO" e o relógio (o Plantão dos ninjas).
- `documentario`: teleobjetiva de documentário de natureza; nada escrito na imagem.

O texto na imagem entra aqui, nunca no prompt (o modelo embaralha letra).
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import ff

W, H = 1080, 1920
# A do Mac e, quando ela não existe nesta máquina, a livre que viaja junto (OFL, em assets/fontes),
# com o mesmo aviso da legenda: o carimbo da câmera é mono, o selo do telejornal é negrito.
LIVRES = Path(__file__).resolve().parents[1] / "assets" / "fontes"
FONTE = ("/System/Library/Fonts/Menlo.ttc", LIVRES / "IBMPlexMono-Regular.ttf", "")
NEGRITO = ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", LIVRES / "Montserrat[wght].ttf", "Bold")
_avisadas: set[str] = set()


def fonte(qual: tuple, corpo: int) -> ImageFont.FreeTypeFont:
    mac, livre, inst = qual
    if Path(mac).exists():
        return ImageFont.truetype(mac, corpo)
    if mac not in _avisadas:
        print(f"  fonte '{Path(mac).name}' não está nesta máquina; usando a {livre.stem}", file=sys.stderr)
        _avisadas.add(mac)
    f = ImageFont.truetype(str(livre), corpo)
    if inst:                           # fonte variável cai na instância fina sem isto
        f.set_variation_by_name(inst)
    return f


TIPOS = {
    # tremor (px), grão, saturação, contraste, vinheta, cor deslocada (px), resolução do "arquivo"
    #
    # Em 28/09/2026 o dono reclamou da qualidade dos anúncios na Meta. A 1ª versão encolhia a
    # cena pra 480 com crf 33–36 e grão 11–20: já saía mole daqui, e a Meta recomprime pra
    # ~1,4 Mbps em 720p, onde grão vira bloco. O que diz "filmagem achada" é o selo, o
    # relógio, o tremor e a cor; a resolução fica, e o grão é só um sopro.
    "celular":   dict(tremor=6, grao=3, sat=0.97, con=1.02, vinheta=False, desloca=0, arquivo=1080, crf=19),
    "cctv":      dict(tremor=0, grao=5, sat=0.70, con=1.06, vinheta=True,  desloca=0, arquivo=720,  crf=22),
    "filmadora": dict(tremor=3, grao=4, sat=1.08, con=0.95, vinheta=True,  desloca=1, arquivo=720,  crf=22),
    # transmissão de TV é limpa; o que diz "telejornal" é o selo
    "telejornal": dict(tremor=0, grao=2, sat=1.05, con=1.03, vinheta=False, desloca=0, arquivo=1080, crf=19),
    # teleobjetiva de documentário: tripé que treme pouco, imagem boa, nada escrito
    "documentario": dict(tremor=2, grao=2, sat=1.02, con=1.06, vinheta=True, desloca=0, arquivo=1080, crf=19),
}
# A cor é da estética, não do aparelho: vale por cima de qualquer tipo. "technicolor" (escolha do dono,
# 29/09): o modelo não entrega a cor saturada nem pedindo no prompt, sai azul-esverdeado moderno; aqui
# ela entra depois, com vermelho e azul mais fundos e sombra quente.
CORES = {
    "neutra": "",
    "technicolor": "eq=saturation=1.4:contrast=1.08,colorbalance=rs=.08:gs=-.03:bs=.02:rm=.06:bm=.03:rh=.04",
}


MESES = "JAN FEV MAR ABR MAI JUN JUL AGO SET OUT NOV DEZ".split()


def selo(data: str | None = None) -> str:
    """A data da filmadora ("SET 27 2026"), de uma data AAAA-MM-DD; sem ela, a de hoje."""
    d = date.fromisoformat(data) if data else date.today()
    return f"{MESES[d.month - 1]} {d.day:02d} {d.year}"


def rotulo(tipo: str, hora: str, cam: str, dur: float, pasta: Path, fps: int = 30,
           data: str | None = None, canto: tuple[int, int] = (48, 62)) -> Path:
    """Os quadros do texto do aparelho, com o relógio andando de verdade. `canto` é onde começa o texto
    de cima; fora do padrão, todo o texto anda junto (o anúncio põe ele no canto da zona segura)."""
    h, m, s = (int(x) for x in hora.split(":"))
    dia = selo(data)
    mono, negrito = fonte(FONTE, 44), fonte(NEGRITO, 46)
    n = int(dur * fps) + 1
    for i in range(n):
        seg = s + i // fps
        relogio = f"{h + (m + seg // 60) // 60:02d}:{(m + seg // 60) % 60:02d}:{seg % 60:02d}"
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        if tipo == "celular":
            if (i // (fps // 2)) % 2 == 0:              # o ponto do REC pisca
                d.ellipse((48, 70, 78, 100), fill=(235, 40, 40, 235))
            d.text((92, 62), "REC", font=mono, fill=(255, 255, 255, 230))
            d.text((W - 300, 62), relogio, font=mono, fill=(255, 255, 255, 230))
        elif tipo == "cctv":
            d.text((48, 62), f"CAM {cam}", font=mono, fill=(255, 255, 255, 220))
            d.text((W - 300, 62), relogio, font=mono, fill=(255, 255, 255, 220))
        elif tipo == "telejornal":
            # selo nosso, sem logo de emissora: logo de terceiro é o que derruba a conta
            d.rectangle((48, 58, 336, 124), fill=(206, 28, 28, 240))
            d.ellipse((66, 78, 92, 104), fill=(255, 255, 255, 255))
            d.text((106, 66), "AO VIVO", font=negrito, fill=(255, 255, 255, 255))
            d.rectangle((48, 130, 336, 196), fill=(242, 199, 68, 245))
            d.text((66, 138), "PLANTÃO", font=negrito, fill=(20, 20, 20, 255))
            d.text((W - 300, 62), relogio, font=mono, fill=(255, 255, 255, 230))
        elif tipo == "documentario":
            pass                                     # documentário de natureza não escreve na imagem
        else:
            d.text((W - 360, H - 150), dia, font=mono, fill=(255, 190, 60, 225))
            d.text((W - 360, H - 96), relogio, font=mono, fill=(255, 190, 60, 225))
        if canto != (48, 62):
            fora, im = im, Image.new("RGBA", (W, H), (0, 0, 0, 0))
            im.paste(fora, (canto[0] - 48, canto[1] - 62))
        im.save(pasta / f"r_{i:05d}.png")
    return pasta / "r_%05d.png"


def filtro(t: dict, cor: str = "neutra") -> str:
    """A cadeia de imagem. O tremor é soma de senos: parece mão, não oscilação."""
    partes = [f"scale={W}:{H}:flags=lanczos,setsar=1"]
    if t["tremor"]:
        a = t["tremor"]
        partes.append(
            f"crop=iw-{4*a}:ih-{4*a}:"
            f"{2*a}+{a}*sin(t*7.1)+{a*0.6}*sin(t*13.7):"
            f"{2*a}+{a}*cos(t*6.3)+{a*0.5}*sin(t*17.3),scale={W}:{H}")
    if t["desloca"]:
        partes.append(f"rgbashift=rh={t['desloca']}:bh=-{t['desloca']}")
    partes.append(f"eq=saturation={t['sat']}:contrast={t['con']}")
    if CORES[cor]:
        partes.append(CORES[cor])
    if t["vinheta"]:
        partes.append("vignette=PI/4.5")
    partes.append(f"noise=alls={t['grao']}:allf=t")
    # o crop do tremor seguido de scale deixa o pixel não quadrado (SAR 464:471), e aí
    # a cena não emenda com as outras: a emenda exige a mesma proporção de pixel
    partes.append("setsar=1")
    return ",".join(partes)


def acabar(entrada: Path, saida: Path, tipo: str, hora: str = "03:12:47", cam: str = "02",
           cor: str = "neutra", data: str | None = None, canto: tuple[int, int] = (48, 62)) -> Path:
    t = TIPOS[tipo]
    dur = ff.dur(entrada)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # 1) o "arquivo": resolução baixa e compressão pesada, como veio do aparelho
        arq = tmp / "arquivo.mp4"
        foco = "" if tipo != "celular" else ",boxblur=6:enable='between(t,0.05,0.35)'"
        ff.run(["ffmpeg", "-y", "-i", str(entrada), "-an",
                "-vf", f"scale=-2:{int(t['arquivo'] * 16 / 9) // 2 * 2}{foco}",
                "-c:v", ff.CODEC_VIDEO, "-crf", str(t["crf"]), "-preset", "veryfast", str(arq)], quiet=True)
        # 2) de volta a 1080x1920, com tremor, cor, grão e o texto do aparelho por cima. A cena gerada
        # vem a 24: o rótulo a 30 a levava por cópia (4,5 cópias/s nos ninjas do Crachá, 04/10); o
        # ff.taxa mistura os vizinhos
        padrao = rotulo(tipo, hora, cam, dur, tmp, data=data, canto=canto)
        ff.run(["ffmpeg", "-y", "-i", str(arq), "-framerate", "30", "-i", str(padrao),
                "-filter_complex", f"[0:v]{ff.taxa(ff.probe(arq).fps)},{filtro(t, cor)}[v];"
                                   "[v][1:v]overlay=0:0:shortest=1,format=yuv420p[o]",
                "-map", "[o]", "-t", f"{dur:.3f}", *ff.args_video(), str(saida)], quiet=True)
    return saida


def _autoteste() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        src = tmp / "src.mp4"
        ff.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc2=size=720x1280:rate=30:duration=1.5",
                *ff.args_video(), str(src)], quiet=True)
        for tipo in TIPOS:
            out = acabar(src, tmp / f"{tipo}.mp4", tipo, cor="technicolor" if tipo == "cctv" else "neutra")
            s = ff.probe(out)
            assert (s.largura, s.altura) == (W, H), (tipo, s.largura, s.altura)
            assert abs(ff.dur(out) - 1.5) < 0.1, (tipo, ff.dur(out))
            sar = ff.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=sample_aspect_ratio",
                          "-of", "csv=p=0", str(out)], capture=True, quiet=True).stdout.strip()
            assert sar in ("1:1", "N/A", ""), (tipo, sar)
    print("autoteste ok")


def main() -> None:
    if "--autoteste" in sys.argv:
        _autoteste()
        return
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada", type=Path)
    ap.add_argument("saida", type=Path)
    ap.add_argument("--tipo", choices=list(TIPOS), required=True)
    ap.add_argument("--hora", default="03:12:47", help="relógio no começo da cena (hh:mm:ss)")
    ap.add_argument("--cam", default="02", help="número da câmera, no tipo cctv")
    ap.add_argument("--cor", choices=list(CORES), default="neutra", help="a cor da estética, por cima do tipo")
    ap.add_argument("--data", help="a data da filmadora (AAAA-MM-DD); padrão: hoje")
    a = ap.parse_args()
    print(acabar(a.entrada, a.saida, a.tipo, a.hora, a.cam, a.cor, a.data))


if __name__ == "__main__":
    main()
