"""Modo 2 — aula gravada em duas fontes: o OBS na tela e o celular em quem fala.

Antes disto eram quatro cópias em `videos/aula-*/work/`, já divergentes: a chapa
em 78 e 111 linhas, o render em 70, 80 e 93. Um defeito corrigido na quarta aula
ficava nas outras três, e nada no repositório indicava isso. A quinta aula custava
um fork e uma chance em quatro de copiar a versão certa.

O que muda entre aulas é **dado**, não código: caminho do OBS e do celular, offset
do clap, recorte da tarja, caixas de borrão, geometria da chapa. Uma correção aqui
vale para as aulas já feitas.

    chapa(geometria, saida)              # desenha o fundo, a janela e a moldura
    segmentos(plano, trechos)            # os comandos que montam trecho a trecho
    confere_cobertura(plano, trechos)    # aborta antes do render se faltar câmera

O plano declara **pares**: cada par é um OBS, um celular e o offset do clap entre
os dois. A aula gravada de uma sentada tem um par; a gravada em três partes tem
três. É o mesmo código — antes eram dois programas diferentes.

    "pares": {
      "1": {"obs": "...18-08-11.mp4", "celular": "...IMG_2667.MOV", "offset": 1.25},
      "2": {"obs": "...18-20-31.mp4", "celular": "...IMG_2668.MOV", "offset": -0.4}
    }
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

import ff


@dataclass(frozen=True)
class Geometria:
    """Onde cada coisa fica na chapa. Sai do recorte do OBS daquela gravação —
    **meça a tarja a cada aula**: numa foi 47px, na de 12/08 foram 80px."""
    largura: int = 1920
    altura: int = 1080
    # A tela, colada na borda esquerda. Encostar à esquerda libera a faixa da
    # direita inteira, e é ela que tira a câmera de cima da spec e dos tickets —
    # quatro de quatro alunos relataram a câmera cobrindo o conteúdo.
    tela: tuple[int, int, int, int] = (0, 57, 1690, 994)     # x, y, largura, altura
    chrome: int = 28
    # A câmera cabe FORA da tela: borda esquerda em 1710, tela terminando em 1690.
    # Sobreposição zero.
    camera: tuple[int, int, int, int] = (1710, 362, 200, 356)
    borda: int = 4                      # traço laranja, desenhado POR FORA do vídeo
    raio: int = 18

    fundo: tuple = (26, 22, 20)
    grade: tuple = (42, 36, 31)
    painel: tuple = (22, 18, 15)
    chrome_cor: tuple = (36, 31, 28)
    fio: tuple = (58, 50, 44)
    laranja: tuple = (218, 119, 86)


# A geometria de 12/08 é a antiga, de antes de a tela encostar à esquerda. Fica
# nomeada para que refazer aquela aula não seja adivinhar.
ANTIGA = Geometria(tela=(65, 123, 1552, 873), camera=(1500, 198, 384, 683))

GEOMETRIAS = {"atual": Geometria(), "antiga": ANTIGA}


def chapa(g: Geometria, saida: Path) -> Path:
    """Desenha o fundo da aula: grade, mock de janela e moldura da câmera.

    A geometria mora num lugar só. Ela já esteve duplicada entre a chapa e o
    render, e a chapa ficou desenhada para um layout que o render não usava mais:
    a moldura saía do tamanho exato do vídeo, o vídeo cobria o traço, e sobrava um
    resto de laranja embaixo.
    """
    im = Image.new("RGB", (g.largura, g.altura), g.fundo)
    d = ImageDraw.Draw(im)

    for x in range(0, g.largura, 40):
        d.line([(x, 0), (x, g.altura)], fill=g.grade)
    for y in range(0, g.altura, 40):
        d.line([(0, y), (g.largura, y)], fill=g.grade)

    sx, sy, sw, sh = g.tela
    d.rounded_rectangle([sx, sy - g.chrome, sx + sw, sy + sh], radius=14,
                        fill=g.painel, outline=g.fio)
    d.rounded_rectangle([sx, sy - g.chrome, sx + sw, sy], radius=14, fill=g.chrome_cor)
    for i, cor in enumerate(((255, 95, 87), (254, 188, 46), (40, 200, 64))):
        d.ellipse([sx + 14 + i * 20, sy - g.chrome // 2 - 5,
                   sx + 24 + i * 20, sy - g.chrome // 2 + 5], fill=cor)

    cx, cy, cw, ch = g.camera
    d.rounded_rectangle([cx - g.borda, cy - g.borda, cx + cw + g.borda, cy + ch + g.borda],
                        radius=g.raio + g.borda, outline=g.laranja, width=g.borda)

    saida.parent.mkdir(parents=True, exist_ok=True)
    im.save(saida)
    return saida


def confere_cobertura(plano: dict, trechos: list[dict]) -> None:
    """Todo trecho mantido tem imagem de câmera?

    O celular para de gravar no meio da aula mais vezes do que parece. Se um
    trecho mantido cai num buraco, o render entrega uma aula com um vazio — e
    isso aparece depois de vinte minutos de encode. Aqui aparece antes.
    """
    buracos = [tuple(b) for b in plano.get("buracos", [])]
    for i, t in enumerate(trechos):
        a, b = float(t["start"]), float(t["end"])
        for ini, fim in buracos:
            if a < fim and b > ini:
                raise ValueError(
                    f"o trecho {i} ({a:.1f}→{b:.1f}) cai num buraco sem câmera "
                    f"({ini:.1f}→{fim:.1f}). Ajuste a janela ou regrave."
                )


def _borroes(caixas: list[list[int]]) -> str:
    """As caixas de borrão como dado, para que a lista de dados sensíveis de uma
    aula seja legível sem ler código."""
    return "".join(
        f",boxblur=20:enable='between(t,0,1e9)':"
        f"x={x}:y={y}:w={w}:h={h}" for x, y, w, h in caixas
    ) if caixas else ""


def segmentos(plano: dict, trechos: list[dict], g: Geometria,
              chapa_png: Path, trabalho: Path) -> tuple[list[list[str]], list[Path]]:
    """Um comando por trecho: OBS e celular sobre a chapa, já cortados."""
    pares = plano.get("pares") or {}
    if not pares:
        raise KeyError("o plano do modo 2 não declara nenhum par OBS+celular")
    recorte = plano.get("tarja", "")
    borrao = _borroes(plano.get("borroes", []))

    sx, sy, sw, sh = g.tela
    cx, cy, cw, ch = g.camera

    cmds, partes = [], []
    for i, t in enumerate(trechos):
        a, b = float(t["start"]), float(t["end"])
        dur = b - a
        qual = t.get("par") or (next(iter(pares)) if len(pares) == 1 else None)
        if qual is None:
            raise KeyError(
                f"o trecho {i} não diz de qual par ele vem. "
                f"Pares: {', '.join(sorted(pares))}"
            )
        if qual not in pares:
            raise KeyError(f"o par '{qual}' do trecho {i} não existe. "
                           f"Pares: {', '.join(sorted(pares))}")
        par = pares[qual]
        off = float(par.get("offset", 0.0))
        saida = trabalho / "seg" / f"{i:03d}.mp4"
        partes.append(saida)

        # setpts=PTS-STARTPTS nas DUAS fontes: o -ss de entrada faz o primeiro
        # quadro nascer com PTS diferente de zero, e a emenda pisca preto.
        fc = (
            f"[1:v]{recorte + ',' if recorte else ''}"
            f"setpts=PTS-STARTPTS,scale={sw}:{sh}{borrao}[tela];"
            f"[2:v]setpts=PTS-STARTPTS,scale={cw}:{ch}:force_original_aspect_ratio=increase,"
            f"crop={cw}:{ch}[cam];"
            f"[0:v][tela]overlay={sx}:{sy}[a];"
            f"[a][cam]overlay={cx}:{cy}[v]"
        )
        cmds.append([
            "ffmpeg", "-y", "-v", "error",
            # A chapa é imagem parada: entrada em laço, e ela SEMPRE leva -t.
            # Sem isso o render fica esperando um quadro que não acaba.
            "-loop", "1", "-t", f"{dur:.3f}", "-i", str(chapa_png),
            "-ss", f"{a:.3f}", "-t", f"{dur:.3f}", "-i", str(par["obs"]),
            "-ss", f"{a + off:.3f}", "-t", f"{dur:.3f}", "-i", str(par["celular"]),
            "-filter_complex", fc,
            "-map", "[v]", "-map", "1:a",
            *ff.args_video("composicao"), *ff.args_audio(),
            str(saida),
        ])
    return cmds, partes
