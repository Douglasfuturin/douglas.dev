"""Legenda viral dirigida — o plano manda, o script desenha.

Este ffmpeg não tem libass nem freetype (sem `ass`, sem `drawtext`): o texto sai
do PIL e entra por overlay.

    python captions_viral.py video.mp4 --plan plano.json -o out.mp4
    python captions_viral.py video.mp4 --words t.json --style destaque -o out.mp4

O que o renderer garante sozinho, sem o plano pedir:

  - Nada de interpolação linear. Entrada é mola amortecida.
  - Entrada mexe em três propriedades juntas: escala, opacidade e y.
  - Palavra entra escalonada dentro do card, não o card inteiro de uma vez.
  - Saída existe e é mais rápida que a entrada — quando há respiro depois do card.
  - Amplitude da entrada é proporcional ao VOLUME da fala naquela palavra.
  - Palavra `punch` respira (micro-oscilação) enquanto está na tela.
  - O y do card foge do movimento da cena: o texto não senta em cima da boca.

A linha é diagramada com o tamanho FINAL de cada palavra e cada uma anima em
torno do próprio centro. A escala nunca reflui a linha.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import ff

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W_REF = 1080
ENTRADA = 0.267         # 8 frames a 30fps
STAGGER = 0.067         # 2 frames entre palavras do mesmo card
SAIDA = 0.133           # 4 frames — metade da entrada, como manda a regra


def aplicar_plano(plano: dict) -> None:
    """Ajustes que são do VÍDEO, não do renderer: `ritmo` e `acento`.

    `"acento": "#0640fb"` troca a cor com que a palavra falada acende. O amarelo
    padrão é do reel; numa VSL que tem identidade própria ele briga com a marca.

    `"ritmo": {"entrada": 0.167, "stagger": 0.033}`.

    A entrada é a mesma há oito frames porque a fala de referência tinha 150
    palavras por minuto. A 197 — que é o que ele fala de verdade — o card dura
    0,6s e a entrada come 0,47 deles: a frase aparece e sai sem nunca ter estado
    inteira na tela. Alargar o card pra caber a entrada dá card de oito
    palavras; encurtar a entrada resolve sem tocar no texto.

    Global, e não parâmetro: são seis funções no caminho do desenho, e o script
    roda um plano por vez.
    """
    global ENTRADA, STAGGER, SAIDA, HOT
    if plano.get("acento"):
        c = str(plano["acento"]).lstrip("#")
        HOT = (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))
        ENFASE["chave"]["cor"] = HOT      # ENFASE prendeu o valor antigo na definição
    # TELA DIVIDIDA MANDA NO LAYOUT, e isso mora aqui pra não depender de quem
    # escreve o plano lembrar. Card dentro de uma cena com `janela` vai pro
    # layout `entre` — encostado por baixo do painel. Na `faixa` ele cairia na
    # boca; no `rodape`, largado no pé da tela, longe do gráfico que narra.
    # Layout escrito à mão no card continua valendo: o explícito ganha.
    janelas = [(float(c["t0"]), float(c["t1"]))
               for c in (plano.get("camera") or []) if c.get("janela")]
    # Painel que nasce ou morre junto com a janela não faz fade NENHUM: quem
    # transiciona ali é o corte de câmera. Durante o fade o painel ainda é
    # translúcido e a tarja preta da tela dividida aparece por baixo — um quadro
    # escuro na entrada e outro na saída, em toda peça de painel do vídeo.
    #
    # As duas pontas, e não só a saída: o defeito é simétrico e só a metade
    # dele tinha sido vista.
    inicios = {round(a, 3) for a, _ in janelas}
    fins = {round(b, 3) for _, b in janelas}
    cenas_j = [c for c in (plano.get("camera") or []) if c.get("janela")]
    curvas_ini = {round(float(c["t0"]), 3): curva_da_janela(c) for c in cenas_j}
    curvas_fim = {round(float(c["t1"]), 3): curva_da_janela(c) for c in cenas_j}
    for b in plano.get("brolls") or []:
        if b.get("alfa"):
            continue                       # chip flutua: o fade dele é a entrada
        # Painel que nasce ou morre na borda da janela, e TAMBÉM a peça de tela
        # cheia que assume quando a janela acaba. No fade dela o rosto reaparece
        # por um sexto de segundo entre o painel e o card — não é tarja preta,
        # é um piscar de rosto, e lê como falha de montagem do mesmo jeito.
        if "fade" not in b and round(float(b["t0"]), 3) in (inicios | fins):
            b["fade"] = 0.0
        if "fade_saida" not in b and round(float(b["t1"]), 3) in (inicios | fins):
            b["fade_saida"] = 0.0
        # PAINEL AMARRADO À JANELA anda na mesma curva da câmera: desce na
        # entrada e sobe na saída, sem fade. As durações são as da cena de
        # câmera, pra painel e câmera nunca descolarem. Com a câmera sempre
        # atrás da borda do painel, o recuo de dois quadros que cobria a tarja
        # na entrada deixou de ter o que cobrir.
        if b.get("encaixe") == "topo":
            ini = curvas_ini.get(round(float(b["t0"]), 3))
            fim = curvas_fim.get(round(float(b["t1"]), 3))
            if ini:
                b["_entra"], b["fade"] = ini[0], 0.0
            if fim:
                b["_sai"], b["fade_saida"] = fim[1], 0.0

    for c in plano.get("cards") or []:
        if c.get("layout") or c.get("camada", "legenda") != "legenda":
            continue
        meio = (float(c["t0"]) + float(c["t1"])) / 2
        if any(a <= meio < b for a, b in janelas):
            c["layout"] = "entre"

    r = plano.get("ritmo") or {}
    ENTRADA = float(r.get("entrada", ENTRADA))
    STAGGER = float(r.get("stagger", STAGGER))
    # a saída continua mais rápida que a entrada, como manda a regra
    SAIDA = float(r.get("saida", min(SAIDA, ENTRADA * 0.6)))
RESPIRO_MIN = 0.12      # buraco pro card seguinte que justifica animar a saída
BASE = (255, 255, 255)
HOT = (245, 217, 10)
STROKE = (0, 0, 0)

_SYS = "/System/Library/Fonts"
_USR = str(Path.home() / "Library/Fonts")

# (arquivo, índice na .ttc, instância da fonte variável)
# Escolhidas medindo densidade de tinta e OLHANDO o render, não pelo nome.
# Trocar de fonte só marca a virada se os dois desenhos não se parecerem.
#
# As `capviral-*` vêm do pack pago do Matheus e vivem em ~/Library/Fonts, fora
# do repo — não versione arquivo de fonte aqui.
FONTES = {
    # peso pesado — trilho e herói
    "gotham": (f"{_USR}/capviral-gotham-cd.otf", 0, None),      # Cond Ultra, a mais densa
    "gotham-nr": (f"{_USR}/capviral-gotham-nr.otf", 0, None),   # Narrow Ultra, menos apertada
    "basement": (f"{_USR}/capviral-basement.otf", 0, None),     # Black, larga e moderna
    "creato": (f"{_USR}/capviral-creato.otf", 0, None),         # Black geométrica
    "pilat": (f"{_USR}/capviral-pilat.ttf", 0, None),           # Extended Black — só palavra curta
    # o traço do quadro — estilo 7a, prancha rabiscada
    #
    # Mesma fonte que o board desenha, então a legenda deixa de ser uma camada
    # colada por cima e passa a ser a mesma mão. O repo guarda `.woff2` (é o que
    # o browser lê) e o PIL não abre woff2: o `.ttf` sai do subconjunto mais
    # completo (`a88b72a2`, 212 glifos, os 26 acentos do pt-BR conferidos) com
    # `fontTools` + `brotli`, e mora em ~/Library/Fonts como as outras.
    "excali": (f"{_USR}/Excalifont-Regular.ttf", 0, None),
    # contraste / seção
    "cooper": (f"{_USR}/capviral-cooper.ttf", 0, None),         # serifa 70s, beat retrô
    "slab": (f"{_SYS}/Supplemental/SuperClarendon.ttc", 7, None),
    "serifa": (f"{_USR}/PlayfairDisplay-Variable.ttf", 0, "Black"),
    # condensadas leves — lista, spec, número
    "akzidenz": (f"{_USR}/capviral-akzidenz.ttf", 0, None),
    "bebas": (f"{_USR}/capviral-bebas.otf", 0, None),           # OFL, livre
    "altgothic": (f"{_USR}/capviral-altgothic.ttf", 0, None),
    # neutras
    "haas": (f"{_USR}/capviral-haas.otf", 0, None),             # Neue Haas 75 Bold
    "klavika": (f"{_USR}/capviral-klavika.otf", 0, None),       # técnica
    "helvetica": (f"{_SYS}/HelveticaNeue.ttc", 9, None),
    "futura": (f"{_SYS}/Supplemental/Futura.ttc", 4, None),
    "avenir": (f"{_SYS}/Avenir Next Condensed.ttc", 8, None),
    "redonda": (f"{_USR}/Nunito-Variable.ttf", 0, "Black"),
    "dm": (f"{_USR}/DMSans-Variable.ttf", 0, "Black"),
    "tiktok": (f"{_USR}/TikTokSans-VariableFont_opsz,slnt,wdth,wght.ttf", 0, "Black"),
    # os de sempre
    "impact": (f"{_SYS}/Supplemental/Impact.ttf", 0, None),
    "black": (f"{_SYS}/Supplemental/Arial Black.ttf", 0, None),
    "pixel": (f"{_USR}/PixelifySans-Bold.ttf", 0, None),
    # cursivas do pack — acento conferido. Servem de ACENTO numa linha do bloco,
    # nunca no trilho: script em legenda rolando não se lê.
    "script": (f"{_USR}/capviral-script.ttf", 0, None),          # Vegan Style
    "script-fina": (f"{_USR}/capviral-script-fina.otf", 0, None),  # The Brightside
}
# Padrão escolhido OLHANDO a legenda no tamanho real, não pela medição.
# Densidade de tinta premia condensada, e condensada pesada lê como barata:
# `gotham` (Cond Ultra) ganhou a métrica e perdeu feio na tela. Legenda quer
# letra larga e arejada, não a que enfia mais tinta no mesmo espaço.
FONTE_PADRAO = "creato"

# Fora do registro por não desenharem acento: `cubano` não tem Ç (vira buraco em
# "INTEGRAÇÃO") e `arcade` não tem nenhum. O cmap das duas MAPEIA os códigos —
# só o glifo é oco, então checagem por cmap passa e o vídeo sai errado.
ACENTOS = "ÁÀÂÃÉÊÍÓÔÕÚÜÇáàâãéêíóôõúüç"

# Pasta de origem no pack. A regra é UMA por grupo por reel: as famílias de uma
# mesma pasta se parecem, então duas delas no mesmo vídeo gastam uma troca de
# fonte sem marcar virada nenhuma.
GRUPO_FONTE = {
    "creato": "LEGENDAS", "gotham": "LEGENDAS", "gotham-nr": "LEGENDAS",
    "haas": "LEGENDAS",
    "basement": "YOUTUBE", "pilat": "YOUTUBE", "akzidenz": "YOUTUBE",
    "altgothic": "YOUTUBE", "bebas": "YOUTUBE",
    "cooper": "ANIMADO",
    "klavika": "GAMERS",
}

# zona vertical onde o card pode assentar, em fração da altura; o y exato é
# escolhido dentro dela pelo mapa de movimento
LAYOUTS = {
    "topo": {"zona": (0.05, 0.40), "h": 440, "corpo": 60},
    "centro": {"zona": (0.26, 0.70), "h": 520, "corpo": 78},
    # A faixa desceu 200px (0.55 -> 0.654): medido no short de webhook, a legenda
    # acabava em 1270 e a zona segura do rodape so comeca em 1470 -- 200px de
    # tela util que ninguem usava, com o quadro espremido logo acima.
    # o pe da caixa (zona[1]) e onde a legenda encosta -- 1470 e o comeco da
    # interface no rodape do Shorts/Reels, medido em set/2026
    "faixa": {"zona": (0.505, 0.765), "h": 500, "corpo": 64, "base": True},
    # O pé de 0.765 existe por causa da interface do Reels/Shorts. VSL toca numa
    # landing, sem interface nenhuma por cima — e na tela dividida o rosto vai
    # até o rodapé, então a zona da `faixa` cai na boca. Aqui o texto desce pro
    # peito, que é o único lugar livre.
    #
    # Anúncio reserva MAIS rodapé que Reels orgânico: "patrocinado", conta, a
    # prévia do texto principal e o botão do CTA, empilhados — não só legenda
    # e música. O pé de 0.765 da `faixa` desaparece atrás disso. Pé em 0.68 pro
    # criativo pago, mesma caixa, só mais alto.
    "faixa_criativo": {"zona": (0.42, 0.68), "h": 500, "corpo": 64, "base": True},
    "rodape": {"zona": (0.76, 0.93), "h": 420, "corpo": 62, "base": True},
    # Tela dividida: o texto senta EM CIMA DO DEGRADÊ, não abaixo dele. O painel
    # de 40% é sólido até 0.40 e dissolve até 0.535; a cabeça dele começa entre
    # 0.48 e 0.55 conforme se mexe. Nessa faixa a legenda fica grudada no
    # gráfico e ainda por cima do que já está dissolvendo — mais baixo ela
    # desgruda do painel, mais alto ela bate no conteúdo dele.
    "entre": {"zona": (0.385, 0.515), "h": 230, "corpo": 58},
}

ENFASE = {
    "filler": {"escala": 0.82, "cor": (222, 222, 222), "s0": 0.88},
    "normal": {"escala": 1.00, "cor": BASE, "s0": 0.80},
    "chave": {"escala": 1.20, "cor": HOT, "s0": 0.70},
    "punch": {"escala": 1.50, "cor": (255, 64, 48), "s0": 0.58},
}

MAX_WORDS = 4        # a quebra de linha é por largura medida, não por caractere
LEAD, TAIL = 0.10, 0.50

CORRECOES = {
    "cloud": "Claude", "clode": "Claude", "cláudio": "Claude", "claudio": "Claude",
    "cláudia": "Claude", "claudia": "Claude",   # "comenta CLAUDE aqui embaixo"
    "metaedge": "Meta Ads", "antrop": "Anthropic",
    # Nome de ferramenta que o Whisper nunca ouviu. Os dois primeiros saíram na
    # legenda do short de webhook: "NO NTYN VOCÊ PÕE" e "fingindo ser a QWi-Fi".
    "ntyn": "n8n", "n8m": "n8n", "enoiteene": "n8n",
    "qwifi": "Kiwify", "kiwifi": "Kiwify", "qwi-fi": "Kiwify", "kiwifai": "Kiwify",
    "ngrock": "ngrok", "engrok": "ngrok",
}

_cache_fonte: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}

# A fonte livre que viaja junto (OFL). Quem não tem o pack nem a fonte do sistema
# cai nela: antes, a primeira legenda do aluno dava OSError, porque o padrão
# (`creato`) só existe no ~/Library/Fonts do Matheus. Mesmo caminho relativo no
# tronco (tools/video-use/assets) e no kit (skill/assets).
_KIT_FONTES = Path(__file__).resolve().parents[1] / "assets/fontes"
LIVRE = (str(_KIT_FONTES / "Montserrat[wght].ttf"), 0, "Black")
FONTES["montserrat"] = LIVRE
# Fontes OFL que viajam no kit (não dependem de ~/Library/Fonts do macOS).
FONTES.update({
    "ibm": (str(_KIT_FONTES / "IBMPlexMono-Regular.ttf"), 0, None),
    "bebas": (str(_KIT_FONTES / "BebasNeue-Regular.ttf"), 0, None),
    "oswald": (str(_KIT_FONTES / "Oswald[wght].ttf"), 0, "Bold"),
    "space": (str(_KIT_FONTES / "SpaceGrotesk[wght].ttf"), 0, "Bold"),
    "outfit": (str(_KIT_FONTES / "Outfit[wght].ttf"), 0, "Bold"),
    "archivo": (str(_KIT_FONTES / "ArchivoBlack-Regular.ttf"), 0, None),
    "rubik": (str(_KIT_FONTES / "Rubik[wght].ttf"), 0, "Black"),
    "barlow": (str(_KIT_FONTES / "BarlowCondensed-Bold.ttf"), 0, None),
    "anton": (str(_KIT_FONTES / "Anton-Regular.ttf"), 0, None),
    "bangers": (str(_KIT_FONTES / "Bangers-Regular.ttf"), 0, None),
    "syne": (str(_KIT_FONTES / "Syne[wght].ttf"), 0, "Bold"),
    "rajdhani": (str(_KIT_FONTES / "Rajdhani-Bold.ttf"), 0, None),
    "teko": (str(_KIT_FONTES / "Teko[wght].ttf"), 0, "Bold"),
    "blackops": (str(_KIT_FONTES / "BlackOpsOne-Regular.ttf"), 0, None),
    "kanit": (str(_KIT_FONTES / "Kanit-Bold.ttf"), 0, None),
})
_avisadas: set[str] = set()


def _por_caminho(nome: str) -> tuple[str, int, str | None] | None:
    """`marca/fontes/x.ttf#Black` → (caminho, 0, "Black"). Relativo parte da raiz da fábrica: a fonte
    da marca do aluno não mora no ~/Library/Fonts de ninguém, e no Windows nem existe esse lugar."""
    arq, _, inst = nome.partition("#")
    if Path(arq).suffix.lower() not in (".ttf", ".otf", ".ttc"):
        return None
    p = Path(arq)
    return (str(p if p.is_absolute() else Path(__file__).resolve().parents[3] / p), 0, inst or None)


def fonte(nome: str, corpo: int) -> ImageFont.FreeTypeFont:
    chave = (nome, corpo)
    if chave not in _cache_fonte:
        caminho, idx, inst = FONTES.get(nome) or _por_caminho(nome) or FONTES[FONTE_PADRAO]
        if not Path(caminho).exists():
            if nome not in _avisadas:
                print(f"  fonte '{nome}' não está nesta máquina; usando a Montserrat", file=sys.stderr)
                _avisadas.add(nome)
            caminho, idx, inst = LIVRE
        f = ImageFont.truetype(caminho, corpo, index=idx)
        if inst:                       # fonte variável cai na instância fina sem isto
            f.set_variation_by_name(inst)
        _cache_fonte[chave] = f
    return _cache_fonte[chave]


def acentos_faltando(nome: str, corpo: int = 64) -> str:
    """Acentos que a fonte NÃO desenha. Renderiza e mede tinta — glifo oco
    passa em qualquer checagem de cmap."""
    f = fonte(nome, corpo)

    def tinta_de(ch: str) -> int:
        im = Image.new("L", (corpo * 3, corpo * 3), 0)
        ImageDraw.Draw(im).text((corpo * 1.5, corpo * 1.5), ch, font=f,
                                fill=255, anchor="mm")
        return int((np.array(im) > 128).sum())

    piso = tinta_de("H") * 0.12
    return "".join(c for c in ACENTOS if tinta_de(c) < piso)


def corrigir(txt: str) -> str:
    nucleo, cauda = txt.strip(), ""
    while nucleo and nucleo[-1] in ".,!?;:":
        cauda, nucleo = nucleo[-1] + cauda, nucleo[:-1]
    return CORRECOES.get(nucleo.lower(), nucleo) + cauda


# ------------------------------------------------------------ curvas

def suave(p: float) -> float:
    """ease-out cúbico, saturado."""
    p = min(1.0, max(0.0, p))
    return 1 - (1 - p) ** 3


def mola(p: float, amp: float) -> float:
    """0->1 com overshoot `amp`, amortecida. f(0)=0, assenta em 1."""
    if p >= 1.0:
        return 1.0
    if p <= 0.0:
        return 0.0
    e = math.exp(-5.5 * p)
    return 1 - e * math.cos(3.6 * p) + amp * e * math.sin(3.6 * p)


# TELA DIVIDIDA: painel e câmera num movimento só. Uma curva `p` de 0 a 1 manda
# nos dois; o painel fica em y = -PH + PH·p e a câmera desce atrás da borda dele.
def curva_da_janela(c: dict) -> tuple[float, float]:
    """(entra, sai) da cena. `abre` e `sobe` são nomes antigos de `sai`."""
    sai = c.get("sai", c.get("abre", c.get("sobe", 0.45)))
    return float(c.get("entra", 0.6) or 0), float(sai or 0)


def curva_tela(rel: float, dur: float, entra: float, sai: float) -> float:
    """p do painel: entra em mola curta (back-out c1 1,15, passa de 1 e
    assenta), sai em ease-in-out cúbico. Janela curta encolhe as duas."""
    if dur > 0 and entra + sai > dur:
        k = dur / (entra + sai)
        entra, sai = entra * k, sai * k
    if entra > 0 and rel < entra:
        x = max(0.0, rel) / entra - 1
        return 1 + 2.15 * x ** 3 + 1.15 * x ** 2
    if sai > 0 and rel > dur - sai:
        u = min(1.0, (rel - (dur - sai)) / sai)
        return 1 - (4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2)
    return 1.0


def desce_camera(p: float, ph: float, desce: float, margem: float) -> float:
    """Quanto a câmera desce com o painel em `p`. Ela só sai do lugar depois
    que o painel cobriu `margem` px do alto dela e anda sempre ATRÁS da borda:
    não existe quadro com a câmera à frente do painel, então não existe tarja."""
    pc = min(1.02, max(0.0, (ph * p - margem) / (ph - margem)))
    return desce * pc * ((1 - 0.15 * (1 - pc)) if pc < 1 else 1.0)


# ------------------------------------------------------------ mapas da cena

def preparar_overlays(cards: list[dict], fps: int, dur: float, largura: int,
                      altura: int, tmp: Path) -> dict[int, tuple[Path, dict]]:
    """Extrai os frames dos mattes usados pelos cards.

    O pack do CapCut veio com os RGB truncados e os `.alpha.mp4` INTEIROS. Pra
    gráfico monocromático isso basta: o matte é o desenho. Colorir o estêncil
    reconstrói a placa, a moldura, a barra — e ainda deixa escolher a cor, que o
    mp4 pronto não deixaria.
    """
    mapa: dict[int, tuple[Path, dict]] = {}
    for j, c in enumerate(cards):
        ov = c.get("overlay")
        if not ov:
            continue
        src = Path(ov["arquivo"]).expanduser()
        if not src.exists():
            print(f'  overlay não achado: {src}')
            continue
        sub = tmp / f"ov{j}"
        sub.mkdir(parents=True, exist_ok=True)
        # Asset com alpha próprio (ProRes 4444 recuperado) sai em RGBA e entra
        # com a COR ORIGINAL. Matte cru sai em cinza e vira estêncil colorível.
        # Distinguir importa: extrair o ProRes como gray jogaria a cor fora.
        ov["_rgba"] = not src.name.endswith(".alpha.mp4")
        ff.run(
            ["ffmpeg", "-v", "error", "-ss", f'{ov.get("inicio", 0):.3f}',
             "-t", f'{c["t1"] - c["t0"]:.3f}', "-i", str(src),
             "-vf", f"fps={fps}",
             "-pix_fmt", "rgba" if ov["_rgba"] else "gray",
             f"{sub}/%05d.png"], quiet=True)
        base = int(round(c["t0"] * fps))
        for f in sorted(sub.glob("*.png")):
            idx = base + int(f.stem) - 1
            if 0 <= idx < int(dur * fps):
                mapa[idx] = (f, ov)
    return mapa


def camera_cenas(video: Path, cenas: list[dict], dur: float, fps: int,
                 largura: int, altura: int, tmp: Path) -> Path:
    """Pré-passo: move a CÂMERA antes de qualquer composição.

    Tela dividida não é painel por cima do vídeo — é a câmera saindo do lugar.
    Com painel de 40% e o cabelo dele começando aos 26% da tela, sobrepor sempre
    vai recortar cabelo e armação de óculos, e o recorte serrilha. Encolher e
    descer a câmera deixa o topo limpo e o corte desaparece.

    Cada cena: {t0, t1, escala, dy} — escala 1 é o quadro cheio.
    """
    if not cenas:
        return video

    # Por SEGMENTO, não por expressão de tempo. Escala variável no meio do
    # stream muda a dimensão do frame e o codificador recusa, mesmo com `pad`
    # normalizando depois. Cortar, transformar cada pedaço com valor constante
    # e concatenar é mais código e funciona.
    #
    # TODO segmento leva `fps=` na frente. Sem isso, o trecho com zoompan sai na
    # taxa pedida e os outros na taxa da fonte; a concatenação some com a
    # diferença e, num bruto de 25fps, a legenda dos 53s aparece aos 50.
    cortes = sorted(cenas, key=lambda x: x["t0"])
    zooms: dict[tuple[float, float], list] = {}
    janelas: dict[tuple[float, float], list] = {}
    faixas: list[tuple[float, float, float, float]] = []
    t = 0.0
    for c in cortes:
        if c["t0"] > t:
            faixas.append((t, min(float(c["t0"]), dur), 1.0, 0.0))
        a, b = max(t, float(c["t0"])), min(float(c["t1"]), dur)
        esc, dy = float(c.get("escala", 1.0)), float(c.get("dy", 0))
        faixas.append((a, b, esc, dy))
        if c.get("zoom"):
            # o terceiro item é o andamento e o quarto é o foco; escritos à
            # parte no plano pra não obrigar quem já tem `[1.0, 1.08]` a mexer
            zooms[(a, b)] = (list(c["zoom"])[:2] + [c.get("ease", "sine")]
                             + [c.get("foco", (0.0, 0.0))])
        if c.get("janela"):
            janelas[(a, b)] = (*c["janela"], *curva_da_janela(c))
        t = min(float(c["t1"]), dur)
    if t < dur:
        faixas.append((t, dur, 1.0, 0.0))

    partes = []
    for i, (a0, a1, esc, dy) in enumerate(faixas):
        # menos de um frame não é cena: `fps=` não produz quadro nenhum e o
        # segmento sai só com áudio. Concatenado, o container perde o vídeo de
        # referência e a duração declarada infla (14s viraram 45s uma vez).
        if a1 - a0 < 1.0 / fps:
            continue
        # Quantos quadros ESTE segmento ocupa na linha do tempo final. Vem da
        # diferença entre os índices absolutos, não da duração: com `-t` cada
        # trecho arredonda por conta própria e o erro acumula — no corte s4e5 a
        # janela acabava 0.13s depois do painel que a preenchia, e nesse vão
        # aparecia a tarja preta da tela dividida.
        quadros = int(round(a1 * fps)) - int(round(a0 * fps))
        p_seg = tmp / f"cam{i:03d}.mp4"
        filtro = None                     # filter_complex, quando o -vf não basta
        zm = zooms.get((a0, a1))
        if zm:
            # zoompan devolve dimensão FIXA enquanto amplia — é o que permite
            # zoom de verdade. Com scale+pad a dimensão varia por frame e o
            # codificador recusa, que foi o que me obrigou a segmentar.
            n_fr = max(1, quadros)
            z0, z1 = float(zm[0]), float(zm[1])
            u = f"(on/{n_fr})"
            # O andamento do movimento, e não só o quanto ele anda.
            #
            # Linear era o padrão, e é por isso que todo zoom parecia o mesmo:
            # velocidade constante faz o movimento ANUNCIAR que começou e que
            # parou. `sine` entra e sai macio — a câmera já está andando quando
            # você percebe, e já parou quando você olha.
            #
            # `solta` desacelera no fim e serve pra chegada; `dura` acelera e
            # serve pra sair de uma peça. `reta` existe só pra quando o zoom
            # cobre um corte e qualquer curva denunciaria a emenda.
            prog = {
                "reta":  u,
                "sine":  f"(0.5*(1-cos(PI*{u})))",
                "solta": f"(1-pow(1-{u},2))",
                "dura":  f"(pow({u},2))",
            }.get(str(zm[2] if len(zm) > 2 else "sine"), f"(0.5*(1-cos(PI*{u})))")
            # `fps=` VEM ANTES. O zoompan com d=1 devolve um quadro por quadro
            # de ENTRADA e rotula a saída na taxa pedida: numa fonte de 25fps
            # ele entrega 25 quadros dizendo que são 30, e o segmento encolhe.
            # O FOCO desloca o recorte do centro. Dois enquadramentos do mesmo
            # take, cortados secos, lêem como duas câmeras — que é o jeito mais
            # barato de fazer acontecer alguma coisa num plano parado.
            #
            # O deslocamento é limitado pelo zoom: em 1.2 sobram 8% de imagem de
            # cada lado, e pedir 15% encosta a borda preta no quadro. Por isso
            # ele é aparado aqui e não confiado a quem escreve o plano.
            fx, fy = (list(zm[3]) + [0, 0])[:2] if len(zm) > 3 else (0.0, 0.0)
            teto = (1 - 1 / max(z0, z1)) / 2
            fx = max(-teto, min(teto, float(fx)))
            fy = max(-teto, min(teto, float(fy)))
            vf = (f"fps={fps},"
                  f"zoompan=z='{z0:.4f}+({z1 - z0:.4f})*{prog}':d=1:"
                  f"x='iw/2-(iw/zoom/2)+({fx:.4f})*iw':"
                  f"y='ih/2-(ih/zoom/2)+({fy:.4f})*ih':"
                  f"s={largura}x{altura}:fps={fps}")
        elif janelas.get((a0, a1)):
            # Tela dividida: a câmera em largura cheia, DESLOCADA pra baixo — o
            # que passa do pé some. Encolher deixaria barra preta dos lados.
            #
            # Sem `crop`: recorte de altura variável o codificador recusa, e foi
            # isso que virou escada. O quadro inteiro, em tamanho fixo, é
            # posicionado por `overlay` sobre uma tela do tamanho final, com o y
            # quadro a quadro. Os y vêm da MESMA função que desenha o painel
            # (`curva_tela`), então os dois não descolam. A `janela` diz onde a
            # câmera assenta: a linha `jy` da fonte fica no topo da faixa.
            #
            # A tentativa anterior saía toda preta; o que a faz compor: o fundo
            # com `r=` e `d=`, o vídeo com `setpts=PTS-STARTPTS`, `eval=frame`
            # e `shortest=1`.
            jy, jh, ent, sai = janelas[(a0, a1)]
            ph = altura * (1 - float(jh))
            desce = altura * (1 - float(jy) - float(jh))
            margem = 120 * largura / 1080
            parado = int(desce)
            expr = str(parado)
            for k in reversed(range(quadros)):
                yk = int(desce_camera(curva_tela(k / fps, a1 - a0, ent, sai),
                                      ph, desce, margem))
                # pelo `t` do fundo, não pelo `n`: o `n` do overlay chega
                # adiantado um quadro, e a câmera descia antes do painel
                if yk != parado:
                    expr = f"if(eq(round(t*{fps}),{k}),{yk},{expr})"
            filtro = (f"color=c=black:s={largura}x{altura}:r={fps}:"
                      f"d={quadros / fps + 1:.3f}[bg];"
                      f"[0:v]fps={fps},setpts=PTS-STARTPTS[v];"
                      f"[bg][v]overlay=x=0:y='{expr}':eval=frame:shortest=1,"
                      f"format={ff.PIX_FMT}[o]")
        elif abs(esc - 1.0) < 1e-3 and abs(dy) < 1e-3:
            vf = f"fps={fps}"
        else:
            lw = int(largura * esc) // 2 * 2
            lh = int(altura * esc) // 2 * 2
            vf = (f"fps={fps},scale={lw}:{lh},pad={largura}:{altura}:"
                  f"{(largura - lw) // 2}:{int(dy * altura)}:color=black")
        ff.run(
            ["ffmpeg", "-y", "-v", "error", "-ss", f"{a0:.3f}",
             "-i", str(video),
             *(["-filter_complex", filtro, "-map", "[o]"] if filtro else ["-vf", vf]),
             "-frames:v", str(quadros),
             # SEM ÁUDIO. Cada segmento nasce de uma busca rápida, e busca
             # rápida em áudio é aproximada: sessenta segmentos concatenados
             # acumulam a aproximação e o som anda em relação à imagem. O áudio
             # final vem do arquivo original, que nunca foi cortado.
             "-an",
             "-c:v", ff.CODEC_VIDEO, "-preset", "veryfast", "-crf", "16",
             str(p_seg)], check=True)
        partes.append(p_seg)

    lista = tmp / "cam_lista.txt"
    lista.write_text("".join(f"file '{x}'\n" for x in partes), encoding="utf-8")
    saida = tmp / "camera.mp4"
    ff.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", str(lista), "-c", "copy", str(saida)], check=True)
    return saida


def preparar_brolls(brolls: list[dict], fps: int, dur: float, largura: int,
                    tmp: Path, base_dir: Path,
                    video_fonte: Path | None = None, altura: int = 0
                    ) -> dict[int, list[tuple[Path, dict, float]]]:
    """Trilha de b-roll, independente dos cards.

    Não cabe como campo de card porque os clipes SE SOBREPÕEM: no reel do kit o
    painel de fundo fica 12s no ar enquanto os gráficos entram e saem por cima.
    Amarrar b-roll a card forçaria um clipe por card e perderia a camada.

    Devolve {frame: [(png, cfg, t_relativo), ...]} na ordem de empilhamento.
    """
    mapa: dict[int, list[tuple[Path, dict, float]]] = {}
    for j, b in enumerate(brolls):
        src = Path(b["arquivo"])
        if not src.is_absolute():
            src = base_dir / src
        if not src.exists():
            print(f"  b-roll não achado: {src}")
            continue
        t0, t1 = float(b["t0"]), float(b["t1"])
        # `alt` manda na ALTURA ocupada, não na largura. Pensar por largura é
        # indireto demais: o que importa é quanto da tela o painel toma, e o
        # degradê come parte dele — com `alt` o alvo é o que se vê.
        if b.get("alt") and altura:
            alvo_h = int(altura * float(b["alt"]))
            larg = None                      # calculado abaixo pelo aspecto
        else:
            alvo_h = None
            larg = int(largura * float(b.get("larg", 0.9)))

        # Cor média do fundo na faixa onde o painel vai dissolver. Rampar só o
        # alpha não mescla: painel branco a 40% sobre parede roxa continua sendo
        # uma mancha clara. Puxar a COR do painel pra cor do ambiente conforme
        # desce é o que faz ele sumir em vez de ficar translúcido.
        if b.get("encaixe") == "topo" and b.get("mescla") and video_fonte:
            amostra = ff.run(
                ["ffmpeg", "-v", "error", "-ss", f"{(t0 + t1) / 2:.3f}",
                 "-i", str(video_fonte), "-frames:v", "1",
                 "-vf", "crop=iw:ih/6:0:ih/3,scale=1:1", "-f", "rawvideo",
                 "-pix_fmt", "rgb24", "-"], capture=True, binario=True, quiet=True).stdout
            if len(amostra) >= 3:
                b["_cor_fundo"] = tuple(amostra[:3])
        sub = tmp / f"br{j}"
        sub.mkdir(parents=True, exist_ok=True)
        ff.run(
            ["ffmpeg", "-v", "error", "-ss", f'{b.get("inicio", 0):.3f}',
             "-t", f"{t1 - t0:.3f}", "-i", str(src),
             # Largura CHEIA sempre; a altura é que se ajusta, cortando na
             # vertical pelo centro. Escalar pela altura deixava sobra roxa nas
             # laterais — painel que não sangra de lado a lado lê como card.
             "-vf", (f"fps={fps},scale={largura}:-2,"
                     f"crop={largura}:'min(ih,{alvo_h})':0:'(ih-min(ih,{alvo_h}))/2'"
                     if alvo_h else f"fps={fps},scale={larg}:-2"),
             # `alfa` = a peça flutua sobre o vídeo com a transparência dela
             # própria (ProRes 4444). Sem forçar rgba aqui o alpha se perde na
             # escrita do PNG e a peça volta a ser um retângulo.
             *(["-pix_fmt", "rgba"] if b.get("alfa") else []),
             f"{sub}/%05d.png"], quiet=True)
        # COR DO RODAPÉ, medida UMA VEZ. O degradê replicava a última linha de
        # CADA quadro: numa gravação de tela a borda é preta e vira uma barra;
        # e quando a câmera dá zoom a linha muda de conteúdo, então o degradê
        # pula de cor no meio do plano. Aqui a cor sai da faixa de baixo do
        # PRIMEIRO quadro, ignorando linha preta de borda, e não muda mais.
        quadros = sorted(sub.glob("*.png"))
        if quadros and b.get("encaixe") == "topo" and b.get("mescla"):
            px = np.array(Image.open(quadros[0]).convert("RGB"))
            faixa = px[max(0, px.shape[0] - max(3, px.shape[0] // 30)):]
            vivas = faixa[faixa.reshape(-1, 3).mean(axis=1).reshape(faixa.shape[0], -1)
                          .mean(axis=1) > 12] if faixa.size else faixa
            if vivas.size:
                b["_rodape"] = tuple(int(v) for v in
                                     np.median(vivas.reshape(-1, 3), axis=0))
        if not quadros:
            continue
        # SEGURA O ÚLTIMO QUADRO quando o clipe é mais curto que a janela. Um
        # clipe de 4.80s numa janela de 4.89s deixa três quadros sem peça — e
        # numa tela dividida esses três mostram a tarja preta. Congelar o fim é
        # invisível; sumir não é.
        base = int(round(t0 * fps))
        precisa = int(round(t1 * fps)) - base
        for i in range(precisa):
            idx = base + i
            if 0 <= idx < int(dur * fps):
                mapa.setdefault(idx, []).append(
                    (quadros[min(i, len(quadros) - 1)], b, i / fps))
    return mapa


def pintar_broll(caminho: Path, b: dict, rel: float, largura: int,
                 altura: int) -> Image.Image:
    """Um clipe de b-roll posicionado, com entrada e fade."""
    im = Image.open(caminho).convert("RGBA")
    k = largura / W_REF
    dur = float(b["t1"]) - float(b["t0"])
    encaixe = b.get("encaixe")          # "topo" = sangra no alto, sem cantos
    ph = im.height                      # altura do painel SEM a mescla

    if b.get("alfa"):
        # a máscara do clipe É o recorte: nada de faixa, nada de canto
        # arredondado. Encostar aqui apaga a transparência que a peça trouxe.
        pass
    elif encaixe == "topo":
        # Painel encostado no topo com degradê no rodapé. Card flutuando com
        # sombra lê como adesivo colado por cima; sangrar e dissolver a borda
        # faz o gráfico e a câmera lerem como UMA imagem.
        faixa = int(b.get("mescla", 150) * k)
        if faixa > 0:
            # A mescla ESTENDE o painel pra baixo, não come por dentro. Rampar
            # dentro da altura pedida desperdiça um terço do gráfico: o original
            # fica sólido até o fim e corta seco, e o que se quer é o mesmo
            # conteúdo com a borda dissolvendo depois dele.
            # cor fixa quando `preparar_brolls` mediu; senão, a última linha
            rod = b.get("_rodape")
            rodape = (Image.new("RGB", (im.width, faixa), tuple(rod)).convert("RGBA")
                      if rod else
                      im.crop((0, im.height - 1, im.width, im.height)).resize(
                          (im.width, faixa), Image.NEAREST))
            maior = Image.new("RGBA", (im.width, im.height + faixa))
            maior.paste(im, (0, 0))
            maior.paste(rodape, (0, im.height))
            im = maior
        masc = Image.new("L", im.size, 255)
        if faixa > 0:
            ramp = ImageOps.invert(Image.linear_gradient("L").resize((im.width, faixa)))
            masc.paste(ramp, (0, im.height - faixa))
            cf = b.get("_cor_fundo")
            if cf:
                # a cor do painel caminha pra cor do ambiente na mesma rampa.
                # Só com alpha, branco a 40% sobre parede roxa ainda é mancha
                # clara; com a cor junto, ele se dissolve no fundo.
                alvo = Image.new("RGB", (im.width, faixa), tuple(int(v) for v in cf))
                trecho = im.crop((0, im.height - faixa, im.width, im.height)).convert("RGB")
                im.paste(Image.composite(trecho, alvo, ramp), (0, im.height - faixa))
        im.putalpha(masc)
    elif b.get("raio", 22):
        masc = Image.new("L", im.size, 0)
        ImageDraw.Draw(masc).rounded_rectangle(
            [0, 0, im.width - 1, im.height - 1], radius=int(b.get("raio", 22) * k), fill=255)
        im.putalpha(masc)

    fade = float(b.get("fade", 0.22))
    # `fade_saida` separado da entrada: painel que termina junto com a cena da
    # câmera não pode desaparecer ANTES do corte. Se desaparece, os últimos
    # quadros mostram a tarja preta da tela dividida — que é o que sobra quando
    # o painel sai e a câmera ainda está na janela.
    fade_out = float(b.get("fade_saida", fade))
    a = 1.0
    if fade > 0 or fade_out > 0:
        a = min(suave(rel / fade) if fade > 0 else 1.0,
                suave((dur - rel) / fade_out) if fade_out > 0 else 1.0)
    # entrada deslizando: `anim` diz de que lado o clipe entra
    dx = 0.0
    anim = b.get("anim", "static")
    if anim in ("esquerda", "direita") and rel < fade * 2:
        p = suave(rel / max(0.05, fade * 2))
        dx = (1 - p) * largura * (-0.55 if anim == "esquerda" else 0.55)
    # DESCE E SOBE, contínuo: y = -PH + PH·p, com a mesma `curva_tela` que
    # move a câmera. Amarrado à janela, `aplicar_plano` pôs as durações da cena
    # de câmera em `_entra`/`_sai`; solto, vale o `entra`/`sai` (ou `sobe`) dele.
    p_tela = 1.0
    if encaixe == "topo" and not b.get("alfa"):
        ent = float(b.get("_entra", b.get("entra", 0)) or 0)
        sai = float(b.get("_sai", b.get("sai", b.get("sobe", 0))) or 0)
        p_tela = curva_tela(rel, dur, ent, sai)
        if p_tela <= 0.001:
            return Image.new("RGBA", (largura, altura), (0, 0, 0, 0))
    if a <= 0.01:
        return Image.new("RGBA", (largura, altura), (0, 0, 0, 0))
    im.putalpha(im.split()[3].point(lambda v: int(v * a)))

    fundo = Image.new("RGBA", (largura, altura), (0, 0, 0, 0))
    x = int((largura - im.width) / 2 + b.get("x", 0) * k + dx)
    y = int(b.get("y", 120) * k)
    if b.get("alfa"):
        # posiciona por x/y como qualquer objeto e segue pro passo da sombra:
        # peça que flutua sobre a imagem precisa da sombra pra ler em cima de
        # uma parede clara tanto quanto de uma escura
        pass
    elif encaixe == "topo":
        # sangra: no alto, e a sombra some — a borda agora é o degradê
        x, y = int(dx), int(-ph + ph * p_tela)
        fundo.paste(im, (x, y), im)
        if y > 0:
            # a mola passa de 1 e o painel desce uns px além do topo: a linha
            # de cima dele estica pra cobrir o vão, senão o vão é tarja preta
            topo = im.crop((0, 0, im.width, 1)).resize((im.width, y), Image.NEAREST)
            fundo.paste(topo, (x, 0), topo)
        return fundo
    if b.get("sombra", True):
        s = Image.new("RGBA", im.size, (0, 0, 0, 0))
        s.putalpha(im.split()[3])
        s = s.filter(ImageFilter.GaussianBlur(16 * k))
        fundo.paste(s, (x, y + int(12 * k)), s)
    fundo.paste(im, (x, y), im)
    return fundo


def preparar_telas(cards: list[dict], fps: int, dur: float, largura: int,
                   tmp: Path) -> dict[int, tuple[Path, dict]]:
    """Recorte de outra gravação entrando como card de tela.

    É o que faz o reel ser SOBRE o produto em vez de cabeça falante: quando ele
    diz "eu sei meu faturamento", a tela do faturamento aparece. A fonte é
    qualquer vídeo — no reel-crm vem das aulas do curso, que são captura 2560x1440.
    """
    mapa: dict[int, tuple[Path, dict]] = {}
    for j, c in enumerate(cards):
        tl = c.get("tela")
        if not tl:
            continue
        src = Path(tl["arquivo"]).expanduser()
        if not src.exists():
            print(f"  tela não achada: {src}")
            continue
        sub = tmp / f"tl{j}"
        sub.mkdir(parents=True, exist_ok=True)
        larg = int(largura * float(tl.get("larg", 0.92)))
        # `crop` antes do scale: a captura da aula traz a cabeça em PiP no canto,
        # e levar isso pro reel põe dois rostos na tela ao mesmo tempo.
        vf = f"crop={tl['crop']}," if tl.get("crop") else ""
        ff.run(
            ["ffmpeg", "-v", "error", "-ss", f'{tl.get("inicio", 0):.3f}',
             "-t", f'{c["t1"] - c["t0"]:.3f}', "-i", str(src),
             "-vf", f"{vf}fps={fps},scale={larg}:-2", f"{sub}/%05d.png"], quiet=True)
        base = int(round(c["t0"] * fps))
        for f in sorted(sub.glob("*.png")):
            idx = base + int(f.stem) - 1
            if 0 <= idx < int(dur * fps):
                mapa[idx] = (f, tl)
    return mapa


def pintar_tela(caminho: Path, tl: dict, largura: int, altura: int) -> Image.Image:
    """Canto arredondado + sombra. Retângulo cru colado no vídeo lê como erro
    de montagem; o arredondamento é o que diz 'isto é uma janela'."""
    im = Image.open(caminho).convert("RGBA")
    k = largura / W_REF
    raio = int(tl.get("raio", 26) * k)
    masc = Image.new("L", im.size, 0)
    ImageDraw.Draw(masc).rounded_rectangle([0, 0, im.width - 1, im.height - 1],
                                           radius=raio, fill=255)
    im.putalpha(masc)

    fundo = Image.new("RGBA", (largura, altura), (0, 0, 0, 0))
    x = int((largura - im.width) / 2 + tl.get("x", 0) * k)
    y = int(tl.get("y", 120) * k)
    if tl.get("sombra", True):
        s = Image.new("RGBA", im.size, (0, 0, 0, 0))
        s.putalpha(masc)
        s = s.filter(ImageFilter.GaussianBlur(18 * k))
        fundo.paste(s, (x, y + int(14 * k)), s)
    fundo.paste(im, (x, y), im)
    return fundo


def pintar_overlay(caminho: Path, ov: dict, largura: int, altura: int) -> Image.Image:
    """Gráfico do pack posicionado no quadro.

    Dois caminhos: asset com cor própria entra como está; matte cinza vira
    estêncil e ganha a cor que o plano pedir. `cor:` força o estêncil mesmo
    num asset colorido — útil quando a cor original não serve.
    """
    forca = float(ov.get("forca", 1.0))
    esc = float(ov.get("escala", 1.0))
    if ov.get("_rgba") and not ov.get("cor"):
        g = Image.open(caminho).convert("RGBA")
        if esc != 1.0:
            g = g.resize((max(1, int(g.width * esc)), max(1, int(g.height * esc))),
                         Image.LANCZOS)
        if forca != 1.0:
            g.putalpha(g.split()[3].point(lambda v: min(255, int(v * forca))))
    else:
        im = Image.open(caminho)
        m = im.split()[3] if im.mode == "RGBA" else im.convert("L")
        if esc != 1.0:
            m = m.resize((max(1, int(m.width * esc)), max(1, int(m.height * esc))),
                         Image.LANCZOS)
        if forca != 1.0:
            m = m.point(lambda v: min(255, int(v * forca)))
        g = Image.new("RGBA", m.size, rgb(ov.get("cor", "#FFFFFF")) + (0,))
        g.putalpha(m)
    m = g
    fundo = Image.new("RGBA", (largura, altura), (0, 0, 0, 0))
    k = largura / W_REF
    # x/y são DESLOCAMENTO a partir da posição nativa, e aceitam negativo: o
    # matte já vem posicionado em 1080x1920 e quase sempre só precisa de ajuste.
    x = int((largura - m.width) / 2 + ov.get("x", 0) * k)
    y = int((altura - m.height) / 2 + ov.get("y", 0) * k)
    fundo.paste(g, (x, y), g)          # paste aceita offset negativo, alpha_composite não
    return fundo


def probe(video: Path) -> tuple[int, int, float]:
    """largura, altura e DURAÇÃO em segundos.

    Devolvia `fps` no lugar da duração, e quem chama nomeia o terceiro valor
    `dur_video`. Como todo fps do pipeline é 30, `dur` virava 30 e a linha
    `cards = [c for c in cards if c["t0"] < dur]` jogava fora toda legenda
    depois do meio minuto. No short de webhook: 283 cards no plano, 74 no vídeo.
    """
    p = ff.probe(video)
    return p.largura, p.altura, p.duracao or 30.0



def mapa_movimento(video: Path, dur: float, largura: int, altura: int,
                   taxa: int = 4, lw: int = 160) -> tuple[np.ndarray, int]:
    """Quanto cada LINHA da imagem se mexe ao longo do tempo.

    Movimento é o sinal certo pra decidir onde o texto não pode sentar: a boca e
    as mãos se mexem, o fundo não. Devolve (n_amostras, lh) e a taxa.
    """
    lh = int(round(lw * altura / largura / 2)) * 2
    raw = ff.run(
        ["ffmpeg", "-v", "error", "-t", f"{dur}", "-i", str(video),
         "-vf", f"fps={taxa},scale={lw}:{lh},format=gray",
         "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        capture=True, binario=True, quiet=True).stdout
    n = len(raw) // (lw * lh)
    if n < 2:
        return np.zeros((1, lh), dtype=np.float32), taxa
    a = np.frombuffer(raw[:n * lw * lh], np.uint8).reshape(n, lh, lw).astype(np.int16)
    mov = np.abs(np.diff(a, axis=0)).mean(axis=2).astype(np.float32)   # (n-1, lh)
    k = np.ones(7, dtype=np.float32) / 7                               # alisa por linha
    return np.apply_along_axis(lambda r: np.convolve(r, k, "same"), 1, mov), taxa


def linha_do_ombro(suj: np.ndarray, t_suj: int, t0: float, t1: float,
                   altura: int) -> int:
    """Onde a cabeça acaba e o tronco começa, em px do quadro.

    Legenda por cima do rosto tapa a boca e a expressão — o que se está
    assistindo. Só tela dividida justifica texto em cima. Achar "o mais quieto"
    não basta: em plano fechado o ponto mais quieto é a testa.

    A cabeça é estreita, o ombro é largo. Varrendo de cima, a linha onde a
    largura do sujeito passa de ~1.55x a largura mediana da cabeça é o ombro.
    """
    oc = _janela(suj, t_suj, t0, t1)
    lh = oc.shape[0]
    corpo = np.nonzero(oc > 0.03)[0]
    if corpo.size < 8:
        return int(altura * 0.55)
    topo, base = int(corpo[0]), int(corpo[-1])
    ext = base - topo
    if ext < 8:
        return int(altura * 0.55)

    # Pular a CURVA DO CABELO antes de medir. A largura sobe de 0.02 até o
    # platô da cabeça ao longo do topo; medir a mediana incluindo essa rampa dá
    # um valor baixo demais, o limiar dispara logo abaixo do cocuruto e a
    # legenda volta pro rosto — foi exatamente o que aconteceu.
    a = topo + int(ext * 0.15)
    b = topo + int(ext * 0.45)
    plato = oc[a:max(a + 2, b)]
    plato = plato[plato > 0.03]
    if plato.size < 2:
        return int(altura * 0.55)
    largura_cabeca = float(np.median(plato))
    limite = largura_cabeca * 1.35

    for y in range(b, lh):          # procura a partir do FIM do platô
        if oc[y] >= limite:
            return int(y / lh * altura)
    return int(altura * 0.55)


def _janela(m: np.ndarray, taxa: int, t0: float, t1: float) -> np.ndarray:
    i0 = min(m.shape[0] - 1, max(0, int(t0 * taxa)))
    i1 = min(m.shape[0], max(i0 + 1, int(t1 * taxa)))
    return m[i0:i1].max(axis=0)          # o pior instante do card é quem manda


def melhor_y(suj: np.ndarray, t_suj: int, mov: np.ndarray, t_mov: int,
             t0: float, t1: float, zona: tuple[float, float],
             caixa: int, altura: int) -> tuple[int, float]:
    """y (px, topo da caixa) e quanto dele cai em cima do sujeito (0-1)."""
    lh = suj.shape[1]
    ocup = _janela(suj, t_suj, t0, t1)
    m = _janela(mov, t_mov, t0, t1)
    m = m / (m.max() or 1.0)
    if m.shape[0] != lh:                                    # alinha as resoluções
        m = np.interp(np.linspace(0, 1, lh), np.linspace(0, 1, m.shape[0]), m)

    jan = max(1, int(round(caixa / altura * lh)))
    peso = np.ones(jan, dtype=np.float32)
    custo = np.convolve(ocup * 3.0 + m, peso, "valid")      # sujeito pesa 3x movimento
    ocup_jan = np.convolve(ocup, peso, "valid") / jan
    lo = int(zona[0] * lh)
    hi = min(len(custo), int(zona[1] * lh) - jan + 1)
    if hi <= lo:
        return int(zona[0] * altura), 1.0
    i = lo + int(np.argmin(custo[lo:hi]))
    return int(i / lh * altura), float(ocup_jan[i])


MATTE_PADRAO = "u2net_human_seg"     # 0.4s/frame; birefnet-portrait é 9.6s e limpo
_SESSOES: dict[str, object] = {}


def _sessao(modelo: str):
    if modelo not in _SESSOES:
        from rembg import new_session
        _SESSOES[modelo] = new_session(modelo)
    return _SESSOES[modelo]


def _maior_componente(m: np.ndarray) -> np.ndarray:
    """Só a maior mancha. O u2net confunde pôster com gente — aqui é um estúdio
    com uma máscara do Majora na parede, e ela vira 'sujeito' sem isto."""
    from scipy import ndimage
    lab, n = ndimage.label(m > 128)
    if n < 2:
        return m
    tam = ndimage.sum(m > 128, lab, range(1, n + 1))
    return np.where(lab == int(np.argmax(tam)) + 1, m, 0).astype(np.uint8)


def _alfa(img: Image.Image, modelo: str = MATTE_PADRAO, lado: int = 512) -> np.ndarray:
    """Máscara do sujeito, 0-255, no tamanho da imagem que entrou."""
    from rembg import remove
    w, h = img.size
    p = img.resize((lado, max(2, int(lado * h / w))), Image.BILINEAR)
    m = np.array(remove(p.convert("RGB"), session=_sessao(modelo),
                        only_mask=True, post_process_mask=True))
    m = _maior_componente(m)
    return np.array(Image.fromarray(m).resize((w, h), Image.BILINEAR)
                    .filter(ImageFilter.GaussianBlur(1.5)))


def alfa_do_arquivo(f: Path) -> np.ndarray | None:
    """Alpha que já veio no frame, se houver recorte de verdade.

    Avatar do HeyGen, greenscreen já chavetado, ProRes 4444 — nesses casos a
    silhueta é exata e sai de graça. Rodar rembg em cima seria pagar caro por
    um recorte pior, e foi o que eu quase fiz.
    """
    im = Image.open(f)
    if im.mode != "RGBA":
        return None
    a = np.array(im)[..., 3]
    # alpha tudo-255 é PNG opaco com canal sobrando, não recorte
    if (a < 250).mean() < 0.02:
        return None
    return a


def _alfa_cache(f: Path, cache: Path, modelo: str) -> np.ndarray:
    """Matte por frame com cache em disco — birefnet a 9.6s/frame só é usável
    se re-render não pagar de novo."""
    alvo = cache / f"{f.stem}.png"
    if alvo.exists():
        return np.array(Image.open(alvo))
    a = alfa_do_arquivo(f)
    if a is None:
        a = _alfa(Image.open(f), modelo)
    cache.mkdir(parents=True, exist_ok=True)
    Image.fromarray(a).save(alvo)
    return a


def mapa_sujeito(video: Path, dur: float, largura: int, altura: int,
                 taxa: int = 2, lw: int = 224) -> tuple[np.ndarray, int]:
    """Fração de cada LINHA ocupada pelo sujeito, ao longo do tempo.

    Movimento sozinho não resolve: num plano fechado o olho está parado e ainda
    assim é rosto. Isto sabe onde a pessoa está, não só onde ela se mexe.
    """
    cache = video.parent / f".{video.stem}_sujeito_{int(dur)}.npy"
    lh = int(round(lw * altura / largura / 2)) * 2
    if cache.exists():
        return np.load(cache), taxa
    with tempfile.TemporaryDirectory() as td:
        ff.run(
            ["ffmpeg", "-v", "error", "-t", f"{dur}", "-i", str(video),
             "-vf", f"fps={taxa},scale={lw}:{lh}", f"{td}/%05d.png"], quiet=True)
        arq = sorted(Path(td).glob("*.png"))
        if not arq:
            return np.zeros((1, lh), dtype=np.float32), taxa
        oc = np.stack([(_alfa(Image.open(f), lado=lw) > 128).mean(axis=1)
                       for f in arq]).astype(np.float32)
    np.save(cache, oc)
    return oc, taxa


def mapa_volume(video: Path, dur: float, taxa: int = 100) -> np.ndarray:
    """RMS da fala em janelas de 10ms, normalizado pelo p90 do clipe."""
    raw = ff.run(
        ["ffmpeg", "-v", "error", "-t", f"{dur}", "-i", str(video),
         "-vn", "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
        capture=True, binario=True, quiet=True, check=False).stdout
    if not raw:
        return np.zeros(1, dtype=np.float32)
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
    passo = 8000 // taxa
    n = len(a) // passo
    if n < 1:
        return np.zeros(1, dtype=np.float32)
    rms = np.sqrt((a[:n * passo].reshape(n, passo) ** 2).mean(axis=1))
    p90 = float(np.percentile(rms, 90)) or 1.0
    return np.clip(rms / p90, 0.0, 1.0).astype(np.float32)


def volume_de(vol: np.ndarray, t0: float, t1: float, taxa: int = 100) -> float:
    i0, i1 = int(t0 * taxa), max(int(t1 * taxa), int(t0 * taxa) + 1)
    trecho = vol[i0:i1]
    return float(trecho.mean()) if trecho.size else 0.5


# ------------------------------------------------------------ plano

def carregar_palavras(caminho: Path, ate: float | None) -> list[dict]:
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    saida = []
    for w in dados["words"]:
        if w.get("type") != "word" or w["end"] <= w["start"]:
            continue
        if ate is not None and w["start"] >= ate:
            break
        saida.append({"t0": w["start"], "t1": min(w["end"], ate or w["end"]),
                      "tx": corrigir(w["text"]).upper()})
    return sorted(saida, key=lambda x: x["t0"])


def finalizar(cards: list[dict]) -> list[dict]:
    """Normaliza e resolve a saída de cada card DENTRO DA SUA CAMADA.

    Reel real tem cartela de gancho parada no topo enquanto a legenda rola
    embaixo. São duas sequências independentes: se a saída do gancho for
    calculada contra o card de legenda que vem depois, ele pisca sem motivo.
    """
    cards = sorted(cards, key=lambda c: c["t0"])
    for c in cards:
        c.setdefault("layout", "faixa")
        c.setdefault("anim", "entra")
        c.setdefault("modo", "destaque")
        c.setdefault("camada", "legenda")
        for w in c["words"]:
            w.setdefault("enf", "normal")
            # O `CORRECOES` mora aqui, e não só no caminho `--words`.
            #
            # Ele estava aplicado num lugar só -- a leitura do transcript cru --
            # e todo plano dirigido passava direto. O short de webhook saiu com
            # "NO NTYN VOCÊ PÕE" e "fingindo ser a QWIFI" em letra garrafal,
            # com o termo novo já na tabela. Nome de ferramenta escrito errado
            # na legenda é pior que legenda nenhuma.
            w["tx"] = corrigir(w["tx"])
            # caixa alta é o padrão de legenda, mas script em CAIXA ALTA não se
            # lê: as ligaduras do desenho pressupõem minúscula.
            if w.get("caixa", c.get("caixa", "alta")) == "alta":
                w["tx"] = w["tx"].upper()

    for camada in {c["camada"] for c in cards}:
        fila = [c for c in cards if c["camada"] == camada]
        for i, c in enumerate(fila):
            prox = fila[i + 1]["t0"] if i + 1 < len(fila) else c["t1"] + 9
            c["saida"] = (prox - c["t1"]) >= RESPIRO_MIN
    return cards


def plano_uniforme(palavras: list[dict], dur: float, estilo: str) -> list[dict]:
    grupos, cur = [], []
    for i, w in enumerate(palavras):
        cur.append(w)
        gap = palavras[i + 1]["t0"] - w["t1"] if i + 1 < len(palavras) else 9.0
        if len(cur) >= MAX_WORDS or gap >= 0.4 or w["tx"].endswith((".", "?", "!", ",")):
            grupos.append(cur)
            cur = []
    if cur:
        grupos.append(cur)
    inicios = [max(0.0, g[0]["t0"] - LEAD) for g in grupos]
    cards = []
    for i, g in enumerate(grupos):
        fim = inicios[i + 1] if i + 1 < len(inicios) else min(dur, g[-1]["t1"] + TAIL)
        cards.append({"t0": inicios[i], "t1": fim, "layout": "faixa",
                      "anim": "entra", "modo": estilo,
                      "words": [dict(w, enf="normal") for w in g]})
    return finalizar(cards)


# ------------------------------------------------------------ animação

def anim(card: dict, i: int, w: dict, t: float, vol: float) -> tuple[float, float, float]:
    """(escala, alpha, dy) da palavra i do card, no instante t."""
    if card["anim"] == "revela" and t < w["t0"] - 0.05:
        return 0.0, 0.0, 0.0
    inicio = card["t0"] + (i * STAGGER if card["anim"] != "nenhuma" else 0.0)
    if card["anim"] == "revela":
        inicio = max(inicio, w["t0"] - 0.05)
    idade = t - inicio
    if idade < 0:
        return 0.0, 0.0, 0.0

    s0 = ENFASE.get(w.get("enf", "normal"), ENFASE["normal"])["s0"]
    if card["anim"] == "nenhuma":
        esc, alpha, dy = 1.0, 1.0, 0.0
    elif idade < ENTRADA:
        p = idade / ENTRADA
        amp = 0.12 + 0.30 * vol                    # fala mais alta, entrada mais viva
        esc = s0 + (1 - s0) * mola(p, amp)
        alpha = suave(p / 0.55)
        dy = 26 * (1 - suave(p))
    else:
        esc, alpha, dy = 1.0, 1.0, 0.0

    if card.get("saida"):
        resta = card["t1"] - t
        if resta < SAIDA:
            q = suave(1 - resta / SAIDA)
            esc *= 1 - 0.07 * q
            alpha *= 1 - q
            dy -= 14 * q

    if w.get("enf") == "punch" and idade >= ENTRADA:
        esc *= 1 + 0.016 * math.sin(2 * math.pi * 0.7 * (t - card["t0"]))
    return esc, max(0.0, min(1.0, alpha)), dy


def cor_da_palavra(card: dict, w: dict, t: float) -> tuple[int, int, int]:
    enf = w.get("enf", "normal")
    base = ENFASE.get(enf, ENFASE["normal"])["cor"]
    if w.get("cor"):
        c = w["cor"].lstrip("#")
        return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))
    if enf in ("chave", "punch"):
        return base                                  # ênfase não é ponteiro da fala
    if card["modo"] == "karaoke":
        return HOT if t >= w["t0"] else base
    if card["modo"] == "destaque":
        return HOT if w["t0"] <= t < w["t1"] else base
    return base


def diagramar(card: dict, largura: int, corpo: int, nome_fonte: str,
              d: ImageDraw.ImageDraw, y_caixa: float, alt_caixa: float) -> list[dict]:
    """Posição FINAL de cada palavra. Escala anima em torno destes centros —
    é isto que impede a linha de refluir quando uma palavra cresce."""
    k = largura / W_REF
    for w in card["words"]:
        esc = ENFASE.get(w.get("enf", "normal"), ENFASE["normal"])["escala"]
        # corpo por PALAVRA: bloco de manchete mistura tamanhos na mesma cartela
        base = w["corpo"] * k if w.get("corpo") else corpo
        w["_corpo"] = max(8, int(base * esc))
        w["_fonte"] = w.get("fonte", nome_fonte)
        w["_larg"] = d.textlength(w["tx"], font=fonte(w["_fonte"], w["_corpo"]))

    # Quebra por LARGURA MEDIDA, não por contagem de caractere. "MENOS DE UMA
    # HORA" tem 17 caracteres e passa em qualquer teto de texto — mas com a
    # palavra em punch 1.5x numa fonte larga a linha estoura o quadro e as
    # pontas somem. Caractere não sabe o corpo nem o desenho da fonte.
    maxl = largura * 0.90
    esp = d.textlength(" ", font=fonte(nome_fonte, corpo))
    if card.get("quebra") == "palavra":
        # cartela de gancho manda na própria quebra: cada `tx` é uma linha.
        # Empacotar por largura transforma um bloco de 3 linhas em 2 e encolhe
        # o gancho — que é justamente o elemento que precisa dominar a tela.
        linhas = [[w] for w in card["words"]]
    else:
        linhas, cur, larg = [], [], 0.0
        for w in card["words"]:
            extra = w["_larg"] + (esp if cur else 0.0)
            if cur and larg + extra > maxl:
                linhas.append(cur)
                cur, larg, extra = [], 0.0, w["_larg"]
            cur.append(w)
            larg += extra
        if cur:
            linhas.append(cur)

    # palavra sozinha maior que o quadro: encolhe o card inteiro até caber
    pior = max(sum(w["_larg"] for w in ln) + esp * (len(ln) - 1) for ln in linhas)
    if pior > maxl:
        k = maxl / pior
        for w in card["words"]:
            w["_corpo"] = max(8, int(w["_corpo"] * k))
            w["_larg"] = d.textlength(w["tx"], font=fonte(w["_fonte"], w["_corpo"]))
        corpo = max(8, int(corpo * k))
        esp = d.textlength(" ", font=fonte(nome_fonte, corpo))

    # entrelinha: manchete empilha linhas justas, quase encostando. 1.30 é o
    # espaçamento de legenda corrida e afasta demais pra bloco de cartela.
    ent = float(card.get("entrelinha", 1.30))
    # a altura da linha sai da CAIXA REAL do glifo, não do corpo. Script tem
    # ascendente e descendente muito maiores que o corpo nominal — usar corpo
    # faz a linha de cima sumir atrás dela.
    # Quanto a tinta sobe e desce A PARTIR DA ÂNCORA. Medir a caixa da tinta
    # sozinha não serve: o `anchor="mm"` do PIL centra pelas métricas da fonte,
    # e no script os floreios passam muito do ascendente nominal. Os dois números
    # só batem se a medida for relativa à mesma âncora usada no desenho.
    sobe, desce = [], []
    for ln in linhas:
        u = dn = 0
        for w in ln:
            f = fonte(w["_fonte"], w["_corpo"])
            bb = f.getbbox(w["tx"], anchor="mm")
            traco = max(2, w["_corpo"] // 11)
            u = max(u, -bb[1] + traco, w["_corpo"] * 0.45)
            dn = max(dn, bb[3] + traco, w["_corpo"] * 0.45)
        sobe.append(u)
        desce.append(dn)
    avancos = [(desce[i] + sobe[i + 1]) * ent for i in range(len(linhas) - 1)]
    total = sobe[0] + sum(avancos) + desce[-1]
    # `_base`: o bloco encosta no PE da caixa em vez de centrar nela.
    #
    # Centrado, card de uma linha e card de tres linhas ficam em alturas
    # diferentes -- a legenda sobe e desce a cada troca. Encostando no pe, todos
    # dividem a mesma linha de base, que e como legenda de verdade se comporta,
    # e "desce ate tocar a zona segura" passa a valer pra todos.
    if card.get("_base"):
        y = y_caixa + alt_caixa - total + sobe[0]
    else:
        y = y_caixa + alt_caixa / 2 - total / 2 + sobe[0]
    # Alinhamento e deslocamento por LINHA. Bloco de manchete não é texto
    # centrado: as linhas se escalonam umas em relação às outras, e é isso que
    # faz parecer composição em vez de parágrafo.
    al = card.get("alinhar", "centro")
    mg = largura * 0.055
    for i, linha in enumerate(linhas):
        larg = sum(w["_larg"] for w in linha) + esp * (len(linha) - 1)
        if al == "esquerda":
            x = mg
        elif al == "direita":
            x = largura - mg - larg
        else:
            x = (largura - larg) / 2
        x += linha[0].get("dx", 0) * k
        for w in linha:
            w["_cx"], w["_cy"] = x + w["_larg"] / 2, y
            x += w["_larg"] + esp
        if i < len(avancos):
            y += avancos[i]
    return card["words"]


def alpha_placa(p: dict) -> float:
    """Opacidade da placa. Cheia tapa o vídeo; 0.82 deixa o fundo respirar."""
    return float(p.get("opacidade", 0.82))


def tinta(card: dict, largura: int, altura: int) -> tuple[np.ndarray, list[tuple]]:
    """Alpha do texto assentado + a caixa de CADA letra.

    A caixa por letra é o que importa: medir só a tinta total deixa o herói
    perder as duas últimas letras e ainda marcar 72% — foi assim que "NENHUM"
    virou "NENHU" atrás da cabeça.
    """
    img = Image.new("RGBA", (largura, altura), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lay = LAYOUTS.get(card["layout"], LAYOUTS["faixa"])
    k = largura / W_REF
    corpo = int(card.get("corpo", lay["corpo"]) * k)
    diagramar(card, largura, corpo, card.get("fonte", FONTE_PADRAO), d,
              card["_y"], lay["h"] * k)
    caixas = []
    for w in card["words"]:
        f = fonte(w["_fonte"], w["_corpo"])
        d.text((w["_cx"], w["_cy"]), w["tx"], font=f, anchor="mm",
               fill=(255, 255, 255, 255),
               stroke_width=max(2, f.size // 9), stroke_fill=(255, 255, 255, 255))
        x = w["_cx"] - w["_larg"] / 2
        alt = f.size * 0.66
        for ch in w["tx"]:
            av = d.textlength(ch, font=f)
            if ch.strip():
                caixas.append((int(x), int(w["_cy"] - alt),
                               max(int(x) + 1, int(x + av)), int(w["_cy"] + alt)))
            x += av
    return np.array(img)[..., 3], caixas


def _visibilidade(base: np.ndarray, caixas: list[tuple], livre: np.ndarray,
                  dy: int, dx: int) -> tuple[float, float]:
    """(pior letra, média geral) depois de empurrar por (dy, dx)."""
    H, W = base.shape
    pior, sv, sn = 1.0, 0.0, 0.0
    for x0, y0, x1, y1 in caixas:
        ink = base[max(0, y0):y1, max(0, x0):x1]
        s = float(ink.sum())
        if s < 1:
            continue
        ny0, nx0 = max(0, y0) + dy, max(0, x0) + dx
        ny1, nx1 = ny0 + ink.shape[0], nx0 + ink.shape[1]
        if ny0 < 0 or nx0 < 0 or ny1 > H or nx1 > W:
            return -1.0, -1.0                      # empurrou letra pra fora
        v = float((ink * livre[ny0:ny1, nx0:nx1]).sum())
        pior = min(pior, v / s)
        sv += v
        sn += s
    return pior, (sv / sn if sn else 1.0)


def ajustar_heroi(card: dict, alfas: list[np.ndarray], largura: int, altura: int,
                  piso_letra: float = 0.60,
                  alvo_geral: float = 0.86) -> tuple[float, float, int, int]:
    """Empurra o card herói até TODA LETRA continuar legível sobre a silhueta.

    A profundidade tem que vir da borda mordida, não de letra sumida. Devolve
    (pior letra, geral, dy, dx).
    """
    base, caixas = tinta(card, largura, altura)
    # UNIÃO da silhueta em TODOS os frames do card, não a média de alguns.
    # Com média, letra tapada em metade do card marca 50% e passa — e some na
    # tela justo quando a pessoa vira a cabeça. Aqui a posição escolhida vale
    # pro pior instante, então o que está legível fica legível o card inteiro.
    varrida = np.maximum.reduce([a for a in alfas]) if alfas else None
    livre = (255 - varrida).astype(np.float32) / 255 if varrida is not None \
        else np.ones(base.shape, dtype=np.float32)
    if not caixas:
        return 1.0, 1.0, 0, 0

    ys, xs = np.nonzero(base)
    if not len(xs):
        return 1.0, 1.0, 0, 0
    y0, y1, x0, x1 = int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())
    mx, my = int(0.035 * largura), int(0.03 * altura)
    dx_lo, dx_hi = mx - x0, largura - mx - x1
    dy_lo, dy_hi = my - y0, altura - my - y1
    # A busca respeita a ZONA do layout. Solta, ela varre o quadro inteiro e
    # sobe o herói pra dentro do painel de b-roll, onde o matte do sujeito não
    # vale nada: microfone e mão viram silhueta preta recortada sobre o gráfico.
    z0, z1 = LAYOUTS.get(card.get("layout", "faixa"), LAYOUTS["faixa"])["zona"]
    zona_lo, zona_hi = int(z0 * altura) - y0, int(z1 * altura) - y1
    if zona_lo <= zona_hi:
        dy_lo, dy_hi = max(dy_lo, zona_lo), min(dy_hi, zona_hi)
        if dy_lo > dy_hi:                      # texto mais alto que a zona
            dy_lo = dy_hi = zona_lo
    if dx_lo > dx_hi or dy_lo > dy_hi:
        # texto maior que o quadro: não há deslocamento válido. Devolver 1.0/1.0
        # aqui mentia — lê como "sem oclusão" quando é "não coube".
        return -1.0, -1.0, 0, 0

    melhor = (-1e9, 0, 0, 1.0, 1.0)
    for dy in range(dy_lo, dy_hi + 1, max(1, altura // 80)):
        for dx in range(dx_lo, dx_hi + 1, max(1, largura // 40)):
            pior, geral = _visibilidade(base, caixas, livre, dy, dx)
            if pior < 0:
                continue
            if pior < piso_letra:
                score = pior - 10                       # nenhuma letra pode sumir
            else:
                # letra salva; entre os que passam, o que morde mais borda
                score = -abs(geral - alvo_geral)
            if score > melhor[0]:
                melhor = (score, dy, dx, pior, geral)
    _, dy, dx, pior, geral = melhor
    return pior, geral, dy, dx


def desenhar(t: float, cards: list[dict], largura: int, altura: int,
             vol: np.ndarray) -> Image.Image:
    img = Image.new("RGBA", (largura, altura), (0, 0, 0, 0))
    ativos = [c for c in cards if c["t0"] <= t < c["t1"]]
    if not ativos:
        return img
    # camada != "legenda" desenha primeiro, por baixo: gancho parado no topo
    # não pode cobrir a legenda que está rolando
    for card in sorted(ativos, key=lambda c: c["camada"] == "legenda"):
        ef = card.get("efeito") or {}
        if not ef:
            _desenhar_card(ImageDraw.Draw(img), card, t, largura, altura, vol)
            continue
        # com efeito o card vai pra camada própria: glow precisa borrar a mancha
        # do texto isolada, e borrar em cima do frame borraria o vídeo junto
        k = largura / W_REF
        cam = Image.new("RGBA", (largura, altura), (0, 0, 0, 0))
        _desenhar_card(ImageDraw.Draw(cam), card, t, largura, altura, vol)

        def mancha(cor=(255, 255, 255), desloc=(0.0, 0.0), borda=False):
            m = Image.new("RGBA", (largura, altura), (0, 0, 0, 0))
            _pintar(ImageDraw.Draw(m), card, t, vol, k,
                    desloc=desloc, cor_fixa=cor, borda=borda)
            return m

        # ordem importa: tudo que é "atrás" entra antes, do mais longe pro mais
        # perto. Extrusão depois de glow ficaria flutuando sobre o halo.
        if ef.get("glow"):
            g = ef["glow"]
            al = mancha().split()[3].filter(
                ImageFilter.GaussianBlur(g.get("raio", 18) * k))
            forca = float(g.get("forca", 0.85))
            brilho = Image.new("RGBA", (largura, altura), rgb(g.get("cor", "#F5D90A")) + (0,))
            brilho.putalpha(al.point(lambda v: min(255, int(v * forca * 2.2))))
            img.alpha_composite(brilho)

        if ef.get("sombra"):                     # difusa, diferente do offset duro
            s = ef["sombra"]
            m = mancha(rgb(s.get("cor", "#000000")),
                       (s.get("dx", 8) * k, s.get("dy", 10) * k))
            al = m.split()[3].filter(ImageFilter.GaussianBlur(s.get("blur", 12) * k))
            m.putalpha(al.point(lambda v: int(v * float(s.get("alpha", 0.75)))))
            img.alpha_composite(m)

        if ef.get("extrusao"):                   # N cópias -> volume de cartaz
            e = ef["extrusao"]
            prof = int(e.get("profundidade", 10))
            ang = math.radians(e.get("angulo", 45))
            ce = rgb(e.get("cor", "#2B2B38"))
            for p in range(prof, 0, -1):
                img.alpha_composite(
                    mancha(ce, (math.cos(ang) * p * k, math.sin(ang) * p * k)))

        if ef.get("offset"):                     # deslocamento duro, sem blur
            of = ef["offset"]
            img.alpha_composite(mancha(rgb(of.get("cor", "#000000")),
                                       (of.get("dx", 6) * k, of.get("dy", 6) * k)))

        if ef.get("gradiente"):                  # preenche a letra com degradê
            gr = ef["gradiente"]
            m = mancha(borda=False)
            faixa = Image.new("RGB", (1, altura))
            d1, d2 = rgb(gr.get("de", "#FFFFFF")), rgb(gr.get("para", "#F5D90A"))
            px = faixa.load()
            for y in range(altura):
                q = y / max(1, altura - 1)
                px[0, y] = tuple(int(d1[j] + (d2[j] - d1[j]) * q) for j in range(3))
            deg = faixa.resize((largura, altura)).convert("RGBA")
            deg.putalpha(m.split()[3])
            cam = deg                            # troca a pintura do card
            if _borda(card, 60, k)[0]:           # redesenha só o contorno por baixo
                img.alpha_composite(mancha(_borda(card, 60, k)[1], borda=True))

        img.alpha_composite(cam)
    return img


def _desenhar_card(d: ImageDraw.ImageDraw, card: dict, t: float,
                   largura: int, altura: int, vol: np.ndarray) -> None:

    lay = LAYOUTS.get(card["layout"], LAYOUTS["faixa"])
    k = largura / W_REF
    corpo = int(card.get("corpo", lay["corpo"]) * k)
    alt_caixa = lay["h"] * k
    diagramar(card, largura, corpo, card.get("fonte", FONTE_PADRAO), d,
              card["_y"] + card.get("_dy", 0), alt_caixa)
    if card.get("_dx"):
        for w in card["words"]:
            w["_cx"] += card["_dx"]

    # placa atrás do texto: retângulo arredondado dimensionado pela mancha real
    # das palavras. Entra com a MESMA curva da primeira palavra, senão a placa e
    # o texto chegam em tempos diferentes e parece bug.
    if card.get("placa"):
        p = card["placa"]
        e0, a0, d0 = anim(card, 0, card["words"][0], t,
                          volume_de(vol, card["words"][0]["t0"], card["words"][0]["t1"]))
        if a0 > 0.01:
            xs = [w["_cx"] - w["_larg"] / 2 for w in card["words"]]
            xe = [w["_cx"] + w["_larg"] / 2 for w in card["words"]]
            ys = [w["_cy"] for w in card["words"]]
            px, py = corpo * 0.52, corpo * 0.44
            x0, x1 = min(xs) - px, max(xe) + px
            y0, y1 = min(ys) - corpo * 0.62 - py, max(ys) + corpo * 0.62 + py
            if p.get("tipo") == "cartao":              # notificação: bolinha + placa
                x0 -= corpo * 1.5
            # a placa é dimensionada pelo texto e não sabe onde o quadro acaba:
            # com fonte larga ela vaza pela lateral. Prende com margem.
            mg = largura * 0.03
            x0, x1 = max(mg, x0), min(largura - mg, x1)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            w2, h2 = (x1 - x0) / 2 * e0, (y1 - y0) / 2 * e0
            d.rounded_rectangle(
                [cx - w2, cy - h2 + d0, cx + w2, cy + h2 + d0],
                radius=int(p.get("raio", 26) * k),
                fill=rgb(p.get("cor", "#141414")) + (int(255 * alpha_placa(p) * a0),))
            if p.get("tipo") == "cartao":
                r = corpo * 0.42 * e0
                d.ellipse([cx - w2 + corpo * 0.55 - r, cy - r + d0,
                           cx - w2 + corpo * 0.55 + r, cy + r + d0],
                          fill=rgb(p.get("bolinha", "#F5D90A")) + (int(255 * a0),))

    # marca-texto: tarja atrás de CADA palavra, não do card inteiro como a placa.
    # Marca só a palavra marcada, que é o ponto — grifo, não fundo.
    mt = (card.get("efeito") or {}).get("marca")
    if mt:
        alvo = mt.get("enf")            # None = todas; "chave" = só as chaves
        quais = mt.get("palavras")      # ou índices: [0] marca só a 1ª linha
        for i, w in enumerate(card["words"]):
            if quais is not None and i not in quais:
                continue
            if alvo and w.get("enf") != alvo:
                continue
            esc, alpha, dy = anim(card, i, w, t, volume_de(vol, w["t0"], w["t1"]))
            if alpha <= 0.01:
                continue
            pad = w["_corpo"] * 0.18
            hh = w["_corpo"] * 0.62 * esc
            d.rounded_rectangle(
                [w["_cx"] - w["_larg"] / 2 * esc - pad, w["_cy"] + dy - hh - pad * 0.5,
                 w["_cx"] + w["_larg"] / 2 * esc + pad, w["_cy"] + dy + hh + pad * 0.5],
                radius=int(mt.get("raio", 10) * k),
                fill=rgb(mt.get("cor", "#F5D90A")) + (int(255 * alpha),))

    _pintar(d, card, t, vol, k)


def rgb(s: str, padrao: tuple[int, int, int] = (0, 0, 0)) -> tuple[int, int, int]:
    if not s:
        return padrao
    c = s.lstrip("#")
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))


def _borda(card: dict, tam: int, k: float) -> tuple[int, tuple[int, int, int]]:
    """Contorno da letra. Antes era fixo em corpo//9 e engordava TODA fonte —
    era por isso que serifa, script e display pareciam a mesma coisa. Agora é
    escolha, e o padrão é mais fino."""
    c = card.get("contorno")
    if c is None:
        return max(2, tam // 11), STROKE
    if c is False or c == 0:
        return 0, STROKE
    if isinstance(c, (int, float)):
        return max(0, int(c * k)), STROKE
    return max(0, int(c.get("largura", 7) * k)), rgb(c.get("cor", "#000000"))


def _pintar(d: ImageDraw.ImageDraw, card: dict, t: float, vol: np.ndarray,
            k: float = 1.0,
            desloc: tuple[float, float] = (0.0, 0.0),
            cor_fixa: tuple[int, int, int] | None = None,
            borda: bool = True) -> None:
    """Só as palavras, já diagramadas. Separado do card pra poder ser
    redesenhado — offset, glow, sombra e extrusão são a MESMA pintura em outra
    cor/posição."""
    ox, oy = desloc
    for i, w in enumerate(card["words"]):
        esc, alpha, dy = anim(card, i, w, t, volume_de(vol, w["t0"], w["t1"]))
        if alpha <= 0.01 or esc <= 0.01:
            continue
        f = fonte(w["_fonte"], max(8, int(w["_corpo"] * esc)))
        a = int(255 * alpha)
        cor = cor_fixa or cor_da_palavra(card, w, t)
        bl, bc = _borda(card, f.size, k) if borda else (0, STROKE)
        d.text((w["_cx"] + ox, w["_cy"] + dy + oy), w["tx"], font=f, anchor="mm",
               fill=cor + (a,), stroke_width=bl, stroke_fill=bc + (a,))


def estado(t: float, cards: list[dict], fps: int) -> tuple:
    """Chave do frame. Frame animado é sempre único; card assentado repete.

    A chave cobre TODOS os cards ativos — com duas camadas, o gancho parado
    reaproveitaria o frame errado se só a legenda entrasse na conta.
    """
    chave = []
    for i, c in enumerate(cards):
        if not (c["t0"] <= t < c["t1"]):
            continue
        f = int((t - c["t0"]) * fps)
        movendo = (
            (t - c["t0"]) <= ENTRADA + STAGGER * len(c["words"])
            or (c.get("saida") and c["t1"] - t < SAIDA)
            or c["anim"] == "revela"
            or any(w.get("enf") == "punch" for w in c["words"])
        )
        if movendo:
            chave.append((i, f))
        else:
            chave.append((i, -1,
                          tuple(1 if w["t0"] <= t < w["t1"] else 0 for w in c["words"]),
                          tuple(1 if t >= w["t0"] else 0 for w in c["words"])))
    return tuple(chave) if chave else (-1,)


# ------------------------------------------------------------ main

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=Path)
    ap.add_argument("--plan", type=Path)
    ap.add_argument("--words", type=Path)
    ap.add_argument("--style", choices=["destaque", "pop", "karaoke"], default="destaque")
    ap.add_argument("--dur", type=float, default=None)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--y-fixo", action="store_true",
                    help="usa o y nominal do layout em vez de fugir do sujeito")
    ap.add_argument("--matte", default=MATTE_PADRAO,
                    choices=["u2net_human_seg", "birefnet-portrait"],
                    help="recorte dos cards herói: u2net p/ iterar (0.4s/frame), "
                         "birefnet p/ o corte final (9.6s/frame, com cache)")
    ap.add_argument("--fonte-alpha", type=Path, default=None,
                    help="vídeo com alpha (webm do HeyGen, ProRes 4444) de onde "
                         "tirar o matte. Recorte exato e sem custo de modelo")
    ap.add_argument("--matte-fps", type=int, default=10,
                    help="taxa do matte de b-roll. A silhueta de quem fala muda "
                         "devagar: 10fps custa um terço de 30 e a borda não denuncia")
    ap.add_argument("-o", "--out", type=Path, required=True)
    a = ap.parse_args()

    if not a.plan and not a.words:
        sys.exit("passe --plan (dirigido) ou --words (uniforme)")

    largura, altura, dur_video = probe(a.video)
    dur = min(a.dur, dur_video) if a.dur else dur_video

    brolls: list[dict] = []
    cenas: list[dict] = []
    if a.plan:
        _plano = json.loads(a.plan.read_text(encoding="utf-8"))
        if isinstance(_plano, list):      # a saída crua do cards_da_fala: só cards
            _plano = {"cards": _plano}
        aplicar_plano(_plano)
        brolls = [b for b in (_plano.get("brolls") or []) if float(b["t0"]) < dur]
        cenas = [c for c in (_plano.get("camera") or []) if float(c["t0"]) < dur]
        cards = [c for c in finalizar(_plano["cards"]) if c["t0"] < dur]
    else:
        palavras = carregar_palavras(a.words, dur)
        if not palavras:
            sys.exit("nenhuma palavra no intervalo")
        cards = plano_uniforme(palavras, dur, a.style)

    vol = mapa_volume(a.video, dur)
    k = largura / W_REF
    avisos = []
    # o layout diz se o bloco encosta no pe da caixa (ver `diagramar`)
    for c in cards:
        c["_base"] = LAYOUTS.get(c["layout"], LAYOUTS["faixa"]).get("base", False)
    if a.y_fixo:
        for c in cards:
            lay = LAYOUTS.get(c["layout"], LAYOUTS["faixa"])
            c["_y"] = int((lay["zona"][0] + lay["zona"][1]) / 2 * altura - lay["h"] * k / 2)
    else:
        mov, t_mov = mapa_movimento(a.video, dur, largura, altura)
        suj, t_suj = mapa_sujeito(a.video, dur, largura, altura)
        for c in cards:
            lay = LAYOUTS.get(c["layout"], LAYOUTS["faixa"])
            if c.get("atras"):
                # card herói NÃO desvia: ele senta no meio da zona e o sujeito
                # passa por cima. A colisão é o efeito.
                c["_y"] = int((lay["zona"][0] + lay["zona"][1]) / 2 * altura
                              - lay["h"] * k / 2)
                continue
            # Video sem sujeito (o quadro) nao tem linha de ombro: a busca
            # devolve um numero qualquer e a legenda para onde calhar. Medido no
            # short de webhook, ela acabava em 1270 com 200px de tela livre
            # embaixo. Sem mascara de gente, manda a zona.
            if c["layout"] == "faixa" and not c.get("sobre_rosto") and suj.max() > 0.02:
                # Colocação DIRETA abaixo do ombro, não busca por zona: a caixa
                # de 500px não cabe entre o ombro (~69%) e o teto da UI do
                # Instagram (~88%), então procurar "o mais quieto" ali devolve
                # posição inválida e cai no fallback — que é o rosto de novo.
                ombro = linha_do_ombro(suj, t_suj, c["t0"], c["t1"], altura)
                centro = min(altura * 0.83, ombro + altura * 0.06)
                c["_y"] = int(centro - lay["h"] * k / 2)
                continue
            c["_y"], ocup = melhor_y(suj, t_suj, mov, t_mov, c["t0"], c["t1"],
                                     lay["zona"], int(lay["h"] * k), altura)
            # `faixa` é sobre o corpo por definição — texto no peito é o normal
            # e não merece aviso. Só centro/topo indicam intenção de achar ar.
            if c["layout"] != "faixa" and ocup > 0.55:
                avisos.append(f'  {c["t0"]:5.2f}s {c["layout"]}: {ocup:.0%} em cima do '
                              f'sujeito — use "atras": true ou mande pra faixa')

    # frames dos cards herói precisam do recorte do sujeito em resolução cheia
    alfa_frame: dict[int, np.ndarray] = {}
    alfa_broll: dict[int, np.ndarray] = {}

    # b-roll com `atras`: o painel desce POR TRÁS da pessoa e a cabeça quebra a
    # borda dele. Sem isso o painel corta o quadro numa linha reta e lê como
    # adesivo — o degradê sozinho suaviza a borda mas não cria profundidade.
    br_atras = [b for b in brolls if b.get("atras")]
    if br_atras:
        cache_b = a.video.parent / f".{a.video.stem}_matte_{a.matte}_{a.matte_fps}"
        with tempfile.TemporaryDirectory() as td:
            for j, b in enumerate(br_atras):
                t0, t1 = float(b["t0"]), min(float(b["t1"]), dur)
                sub = Path(td) / f"b{j}"
                sub.mkdir()
                # Matte AMOSTRADO, não quadro a quadro. A silhueta de quem fala
                # muda devagar; a 30fps eu pagava três vezes pelo mesmo recorte.
                # O que o olho pega é a borda, e ela quase não anda em 1/10s.
                ff.run(
                    ["ffmpeg", "-v", "error", "-ss", f"{t0:.3f}",
                     "-t", f"{t1 - t0:.3f}", "-i", str(a.fonte_alpha or a.video),
                     "-vf", f"fps={a.matte_fps}",
                     "-pix_fmt", "rgba" if a.fonte_alpha else "rgb24",
                     f"{sub}/%05d.png"], quiet=True)
                amostras = sorted(sub.glob("*.png"))
                if not amostras:
                    continue
                alfas = [_alfa_cache(f, cache_b / f"br{t0:.2f}", a.matte)
                         for f in amostras]
                ini, fim = int(round(t0 * a.fps)), int(round(t1 * a.fps))
                for idx in range(max(0, ini), min(fim, int(dur * a.fps))):
                    s = int((idx - ini) / a.fps * a.matte_fps)
                    alfa_broll[idx] = alfas[min(s, len(alfas) - 1)]
        print(f"  matte do b-roll: {len(alfa_broll)} frames cobertos por "
              f"{sum(1 for _ in set(id(v) for v in alfa_broll.values()))} recortes "
              f"a {a.matte_fps}fps")
    heróis = [c for c in cards if c.get("atras")]
    if heróis:
        with tempfile.TemporaryDirectory() as td:
            for j, c in enumerate(heróis):
                sub = Path(td) / str(j)
                sub.mkdir()
                ff.run(
                    ["ffmpeg", "-v", "error", "-ss", f'{c["t0"]:.3f}',
                     "-t", f'{c["t1"] - c["t0"]:.3f}',
                     "-i", str(a.fonte_alpha or a.video),
                     "-vf", f"fps={a.fps}",
                     "-pix_fmt", "rgba" if a.fonte_alpha else "rgb24",
                     f"{sub}/%05d.png"], quiet=True)
                base = int(round(c["t0"] * a.fps))
                cache = a.video.parent / f".{a.video.stem}_matte_{a.matte}"
                do_card = []
                for f in sorted(sub.glob("*.png")):
                    idx = base + int(f.stem) - 1
                    if 0 <= idx < int(dur * a.fps):
                        alvo = cache / f"{c['t0']:.2f}"
                        alfa_frame[idx] = _alfa_cache(f, alvo, a.matte)
                        do_card.append(alfa_frame[idx])
                if not do_card:
                    continue
                pior, geral, dy, dx = ajustar_heroi(c, do_card, largura, altura)
                c["_dy"], c["_dx"] = dy, dx
                if pior < 0:
                    c["atras"] = False
                    for i in range(base, base + len(do_card)):
                        alfa_frame.pop(i, None)
                    avisos.append(f'  {c["t0"]:5.2f}s herói: texto largo demais pro '
                                  f'quadro, sem deslocamento possível — FRENTE')
                elif pior < 0.60:
                    c["atras"] = False                    # letra sumindo: vai pra frente
                    for i in range(base, base + len(do_card)):
                        alfa_frame.pop(i, None)
                    avisos.append(f'  {c["t0"]:5.2f}s herói: a pior letra ficava só '
                                  f'{pior:.0%} visível — desenhei na FRENTE')
                else:
                    avisos.append(f'  {c["t0"]:5.2f}s herói: pior letra {pior:.0%}, '
                                  f'geral {geral:.0%} (dy={dy} dx={dx})')
        print(f"  matte: {len(alfa_frame)} frames de {len(heróis)} card(s) herói")

    n = int(dur * a.fps)
    fonte_audio = a.video          # o áudio NUNCA sai daqui, nem passa pela câmera
    tmp = Path(tempfile.mkdtemp(prefix="capviral_"))
    if cenas:
        # move a câmera primeiro: o matte do sujeito precisa ser tirado do
        # quadro JÁ deslocado, senão a silhueta não bate com o que se vê
        fonte_audio = a.video
        a.video = camera_cenas(a.video, cenas, dur, a.fps, largura, altura, tmp)
        print(f"  câmera: {len(cenas)} cena(s) movida(s)")
    reaproveitados = 0
    try:
        overlays = preparar_overlays(cards, a.fps, dur, largura, altura, tmp)
        if overlays:
            print(f"  overlay: {len(overlays)} frames de matte")
        telas = preparar_telas(cards, a.fps, dur, largura, tmp)
        if telas:
            print(f"  tela: {len(telas)} frames de captura")
        brl = preparar_brolls(brolls, a.fps, dur, largura, tmp,
                              a.plan.parent if a.plan else Path("."), a.video, altura)
        if brl:
            # nome próprio: `n` é o total de frames do vídeo. Reusar aqui
            # encurtava o loop pro número de CAMADAS, e o que passasse disso
            # saía congelado no último quadro composto.
            camadas = sum(len(v) for v in brl.values())
            print(f"  b-roll: {len(brolls)} clipes, {len(brl)} frames, "
                  f"{camadas} camadas")
        anterior, arq_anterior = None, None
        for i in range(n):
            t, alvo = i / a.fps, tmp / f"{i:06d}.png"
            chave = estado(t, cards, a.fps)
            if (chave == anterior and arq_anterior is not None
                    and i not in alfa_frame and i not in overlays
                    and i not in telas and i not in brl
                    and i not in alfa_broll):
                os.link(arq_anterior, alvo)
                reaproveitados += 1
                continue
            img = desenhar(t, cards, largura, altura, vol)
            if i in brl:
                fundo = Image.new("RGBA", (largura, altura), (0, 0, 0, 0))
                atras = Image.new("RGBA", (largura, altura), (0, 0, 0, 0))
                for cam, cfg, rel in brl[i]:
                    p = pintar_broll(cam, cfg, rel, largura, altura)
                    (atras if cfg.get("atras") else fundo).alpha_composite(p)
                if i in alfa_broll:
                    # fura a camada de trás com a silhueta: a pessoa fica NA
                    # FRENTE do painel, e o vídeo de baixo já tem a pessoa
                    px = np.array(atras)
                    px[..., 3] = (px[..., 3].astype(np.uint16)
                                  * (255 - alfa_broll[i]) // 255).astype(np.uint8)
                    atras = Image.fromarray(px)
                atras.alpha_composite(fundo)
                atras.alpha_composite(img)
                img = atras
            if i in telas:
                # a tela vai por baixo de tudo: ela é o assunto, a legenda narra
                g = pintar_tela(*telas[i], largura, altura)
                g.alpha_composite(img)
                img = g
            if i in overlays:
                # gráfico entra POR BAIXO do texto: a legenda é que tem que ler
                g = pintar_overlay(*overlays[i], largura, altura)
                g.alpha_composite(img)
                img = g
            if i in alfa_frame:
                # fura o texto com a silhueta: a pessoa passa a estar NA FRENTE.
                # O vídeo de baixo já tem a pessoa — o buraco basta, sem recompor.
                px = np.array(img)
                px[..., 3] = (px[..., 3].astype(np.uint16)
                              * (255 - alfa_frame[i]) // 255).astype(np.uint8)
                img = Image.fromarray(px)
            img.save(alvo, compress_level=1)
            anterior, arq_anterior = chave, alvo

        ff.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-t", f"{dur}", "-i", str(a.video),
             "-framerate", str(a.fps), "-i", str(tmp / "%06d.png"),
             "-t", f"{dur}", "-i", str(fonte_audio),
             "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto[v]",
             "-map", "[v]", "-map", "2:a?", "-t", f"{dur}",
             *ff.args_video("reel", fps=None),
             "-c:a", ff.CODEC_AUDIO, "-b:a", "160k", str(a.out)], quiet=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"{a.out}  ({len(cards)} cards, {n} frames, {reaproveitados} reaproveitados)")
    for av in avisos:
        print(av)
    print("  CONFIRA OS FRAMES: a máscara é do SUJEITO, não dos objetos. "
          "Microfone, luminária e texto na tela são invisíveis pra ela.")


def _autoteste() -> None:
    # mola: sai de 0, passa de 1 (overshoot) e assenta em 1
    assert abs(mola(0.0, 0.3)) < 1e-9 and mola(1.0, 0.3) == 1.0
    assert max(mola(p / 100, 0.5) for p in range(60)) > 1.0, "sem overshoot"
    assert abs(suave(0) ) < 1e-9 and abs(suave(1) - 1) < 1e-9

    c = finalizar([{"t0": 0.0, "t1": 1.0, "anim": "entra",
                    "words": [{"tx": "UM", "t0": 0.0, "t1": 0.4},
                              {"tx": "DOIS", "t0": 0.4, "t1": 0.9, "enf": "punch"}]},
                   {"t0": 1.5, "t1": 2.0, "words": [{"tx": "TRES", "t0": 1.5, "t1": 1.9}]}])
    # o primeiro card tem respiro depois -> saída animada; o último também
    assert c[0]["saida"] and c[1]["saida"]
    # stagger: no t=0 a segunda palavra ainda não entrou
    assert anim(c[0], 1, c[0]["words"][1], 0.0, 0.5)[1] == 0.0
    assert anim(c[0], 1, c[0]["words"][1], 0.30, 0.5)[1] > 0.0
    # entrada mexe nas três propriedades ao mesmo tempo
    e, al, dy = anim(c[0], 0, c[0]["words"][0], 0.05, 0.5)
    assert e < 1.0 and 0.0 < al < 1.0 and dy > 0.0
    # saída é mais rápida que a entrada e chega a alpha 0
    assert SAIDA < ENTRADA
    assert anim(c[0], 0, c[0]["words"][0], 1.0 - 1e-4, 0.5)[1] < 0.02
    # volume alto dá overshoot maior que volume baixo
    pico = lambda v: max(anim(c[0], 0, c[0]["words"][0], x / 200, v)[0] for x in range(60))
    assert pico(1.0) > pico(0.0), "amplitude não segue o volume"
    # punch respira depois de assentar
    r = [anim(c[0], 1, c[0]["words"][1], 0.55 + x / 60, 0.5)[0] for x in range(30)]
    assert max(r) - min(r) > 0.005, "punch não respira"
    # melhor_y foge do sujeito mesmo quando ele está PARADO (o caso do rosto
    # em plano fechado, que o mapa de movimento sozinho não pegava)
    suj = np.zeros((8, 100), dtype=np.float32); suj[:, 20:45] = 1.0
    mov = np.zeros((8, 100), dtype=np.float32); mov[:, 70:90] = 9.0
    y, ocup = melhor_y(suj, 4, mov, 4, 0.0, 2.0, (0.0, 1.0), 192, 1920)
    lin = y / 1920 * 100
    assert not (20 <= lin < 45), f"sentou no sujeito parado (linha {lin:.0f})"
    assert not (70 <= lin < 90), f"sentou no movimento (linha {lin:.0f})"
    assert ocup < 0.2, f"ocupação devolvida errada ({ocup})"
    # alpha da fonte: recorte que já veio pronto não pode ser refeito por modelo
    with tempfile.TemporaryDirectory() as _ta:
        _p = Path(_ta)
        op = Image.new("RGBA", (40, 40), (10, 20, 30, 255))
        op.save(_p / "opaco.png")
        assert alfa_do_arquivo(_p / "opaco.png") is None, \
            "PNG opaco com canal sobrando não é recorte"
        rec = Image.new("RGBA", (40, 40), (10, 20, 30, 0))
        rec.paste(Image.new("RGBA", (18, 18), (255, 0, 0, 255)), (8, 8))
        rec.save(_p / "recorte.png")
        got = alfa_do_arquivo(_p / "recorte.png")
        assert got is not None and got[16, 16] == 255 and got[2, 2] == 0, \
            "recorte de verdade tinha que ser aproveitado"
        Image.new("RGB", (40, 40), (9, 9, 9)).save(_p / "semcanal.png")
        assert alfa_do_arquivo(_p / "semcanal.png") is None, "RGB não tem alpha"

    # câmera: escala constante e zoom montam filtros diferentes, e zoom tem que
    # sair como zoompan — scale+pad varia a dimensão por frame e o codec recusa
    import tempfile as _tc
    with _tc.TemporaryDirectory() as _tcd, ff.seco() as _gravado:
        camera_cenas(Path("x.mp4"), [{"t0": 0.0, "t1": 1.0, "zoom": [1.0, 1.25]},
                                     {"t0": 2.0, "t1": 3.0, "escala": 0.6, "dy": 0.2}],
                     4.0, 30, 1080, 1920, Path(_tcd))
    tudo = " || ".join(" ".join(str(c) for c in cmd) for cmd in _gravado)
    assert "zoompan" in tudo, "cena com zoom não virou zoompan"
    assert "scale=648:1152" in tudo, "cena com escala não virou scale+pad"
    assert tudo.count("zoompan") == 1, "zoompan vazou pras cenas sem zoom"

    # tela dividida: a curva sai de 0, passa de 1 na mola, assenta, e sai
    # monotônica até ~0. A câmera nunca fica à frente da borda do painel.
    assert curva_da_janela({"abre": 0.43}) == (0.6, 0.43)
    assert curva_da_janela({"sobe": 0.3, "entra": 0.5}) == (0.5, 0.3)
    assert curva_tela(0.0, 5.0, 0.6, 0.45) == 0.0
    assert max(curva_tela(k / 300, 5.0, 0.6, 0.45) for k in range(180)) > 1.0
    assert curva_tela(2.0, 5.0, 0.6, 0.45) == 1.0
    saida = [curva_tela(5.0 - 0.45 + k / 100, 5.0, 0.6, 0.45) for k in range(46)]
    assert all(b <= a for a, b in zip(saida, saida[1:])) and saida[-1] < 1e-9
    for k in range(151):
        pk = curva_tela(k / 30, 5.0, 0.6, 0.45) if k < 18 else saida[min(45, k - 105)] if k >= 105 else 1.0
        assert desce_camera(pk, 768, 307, 120) <= 768 * pk + 1e-6, "câmera à frente do painel"

    # e renderiza: 2s com janela têm que COMPOR a câmera. A versão contínua
    # anterior saía com o quadro inteiro preto; quadro preto reprova aqui.
    with tempfile.TemporaryDirectory() as _tl:
        _d = Path(_tl)
        fonte_t = _d / "fonte.mp4"
        ff.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                "testsrc2=s=1080x1920:r=25:d=3", "-pix_fmt", ff.PIX_FMT,
                "-c:v", ff.CODEC_VIDEO, "-preset", "ultrafast", str(fonte_t)],
               check=True)
        cam = camera_cenas(fonte_t, [{"t0": 0.0, "t1": 2.0, "janela": [0.24, 0.6]}],
                           2.0, 30, 1080, 1920, _d)
        luma = ff.run(["ffmpeg", "-v", "error", "-ss", "1.0", "-i", str(cam),
                       "-frames:v", "1", "-vf", "crop=iw:ih/2:0:ih/2",
                       "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                      capture=True, binario=True, quiet=True).stdout
        media = float(np.frombuffer(luma, np.uint8).mean()) if luma else 0.0
        assert media > 30, f"tela dividida saiu preta (luminância {media:.1f})"

    # linha do ombro, no perfil REAL: curva do cabelo subindo, platô da cabeça,
    # depois o ombro. A rampa do cabelo é o que quebrava a medição.
    perfil = np.zeros((6, 100), dtype=np.float32)
    for i, y in enumerate(range(26, 32)):       # cabelo: 0.05 -> 0.35
        perfil[:, y] = 0.05 + i * 0.06
    perfil[:, 32:62] = 0.42                     # platô da cabeça
    perfil[:, 62:70] = 0.62                     # ombro entra
    perfil[:, 70:96] = 0.95                     # tronco
    y_omb = linha_do_ombro(perfil, 4, 0.0, 1.0, 1920) / 1920 * 100
    assert 58 <= y_omb <= 70, f"ombro em {y_omb:.0f}%, esperava entre 58 e 70"
    # sem sujeito reconhecível, não inventa: cai no meio
    assert linha_do_ombro(np.zeros((4, 100), np.float32), 4, 0, 1, 1920) == int(1920 * 0.55)

    # e reporta ocupação alta quando a zona inteira é sujeito
    _, ocup2 = melhor_y(suj, 4, mov, 4, 0.0, 2.0, (0.20, 0.45), 192, 1920)
    assert ocup2 > 0.55, f"não acusou zona tomada ({ocup2})"
    # fonte variável não pode cair na instância fina
    assert fonte("tiktok", 40).get_variation_names(), "tiktok sem eixos"

    # guarda de legibilidade do herói: silhueta cobrindo o meio da tela tem que
    # empurrar o texto pro lado em vez de deixar a palavra ser engolida
    # Resolução real e fonte FIXA: o teste é da lógica do guarda, não da escolha
    # de padrão nem de um quadro de brinquedo. Sem pinar a fonte, trocar
    # FONTE_PADRAO muda a largura do texto e quebra o caso por motivo errado.
    L, A = 1080, 1920
    h = dict(finalizar([{"t0": 0.0, "t1": 1.0, "layout": "centro", "atras": True,
                         "fonte": "black", "corpo": 52,
                         "words": [{"tx": "NENHUM", "t0": 0.0, "t1": 0.9,
                                    "enf": "punch"}]}])[0])
    h["_y"] = int(0.30 * A)
    def _cena(x0f, x1f):
        s = np.zeros((A, L), dtype=np.uint8)
        s[:, int(x0f * L):int(x1f * L)] = 255
        return s

    base, caixas = tinta(h, L, A)
    ys, xs = np.nonzero(base)
    assert len(caixas) == len("NENHUM"), f"caixa por letra errada ({len(caixas)})"

    # cabeça no meio com ar na lateral: empurra e NENHUMA letra pode sumir
    magra = _cena(0.46, 0.54)
    pior0, _ = _visibilidade(base, caixas, (255 - magra) / 255, 0, 0)
    pior, geral, dy, dx = ajustar_heroi(h, [magra], L, A)
    assert pior > pior0, f"não melhorou a pior letra ({pior:.2f} vs {pior0:.2f})"
    assert pior >= 0.60, f"letra sumindo ({pior:.0%})"
    assert geral < 1.0, "sem nenhuma oclusão não vende profundidade"
    # e o empurrão não pode jogar letra pra fora do quadro
    assert 0 <= xs.min() + dx and xs.max() + dx < L, f"saiu pela lateral (dx={dx})"
    assert 0 <= ys.min() + dy and ys.max() + dy < A, f"saiu por cima/baixo (dy={dy})"

    # tinta total mente: com a ÚLTIMA LETRA inteira tapada, o geral continua
    # alto e a palavra já virou outra. Tapa pela caixa da letra, não por um
    # número de pixels — número fixo deixa de cobrir quando o corpo muda.
    tapa = np.zeros((A, L), dtype=np.uint8)
    ux0, uy0, ux1, uy1 = caixas[-1]
    tapa[:, ux0:ux1 + 2] = 255
    p2, g2 = _visibilidade(base, caixas, (255 - tapa) / 255, 0, 0)
    assert g2 > 0.60, f"geral devia seguir alto, deu {g2:.2f}"
    assert p2 < 0.15, f"pior letra devia denunciar, deu {p2:.2f}"

    # duas camadas: gancho parado no topo + legenda rolando embaixo. A saída de
    # cada um se resolve na própria fila, e o frame tem que conter os dois.
    duas = finalizar([
        {"t0": 0.0, "t1": 3.0, "layout": "topo", "camada": "gancho",
         "words": [{"tx": "GANCHO", "t0": 0.0, "t1": 2.9}]},
        {"t0": 0.0, "t1": 1.0, "words": [{"tx": "UM", "t0": 0.0, "t1": 0.9}]},
        {"t0": 1.0, "t1": 2.0, "words": [{"tx": "DOIS", "t0": 1.0, "t1": 1.9}]},
    ])
    g = [c for c in duas if c["camada"] == "gancho"][0]
    l0 = [c for c in duas if c["camada"] == "legenda"][0]
    assert g["saida"], "gancho é o último da fila dele, devia animar saída"
    assert not l0["saida"], "legenda colada na seguinte não pode piscar"
    assert len(estado(0.5, duas, 30)) == 2, "chave do frame perdeu uma camada"
    for c in duas:
        c["_y"] = LAYOUTS[c["layout"]]["zona"][0] * 1920
    v0 = np.zeros(200, dtype=np.float32)
    im2 = desenhar(0.5, duas, 1080, 1920, v0)
    linhas = np.nonzero(np.array(im2)[..., 3].sum(axis=1))[0]
    assert linhas.min() < 900 and linhas.max() > 1000, "os dois não saíram no frame"

    # overlay de matte: colorir o estêncil e aceitar deslocamento NEGATIVO — o
    # gráfico do pack vem posicionado no quadro e quase sempre precisa descer
    # ou subir pra encontrar a faixa da legenda
    import tempfile as _tf
    with _tf.TemporaryDirectory() as _td:
        mt = Image.new("L", (1080, 1920), 0)
        ImageDraw.Draw(mt).rectangle([300, 200, 780, 400], fill=255)
        pth = Path(_td) / "m.png"
        mt.save(pth)
        for desl, esperado in ((0, (200, 400)), (500, (700, 900)), (-150, (50, 250))):
            got = pintar_overlay(pth, {"cor": "#00FF00", "y": desl}, 1080, 1920)
            ys_o = np.nonzero(np.array(got)[..., 3].sum(axis=1))[0]
            assert abs(int(ys_o.min()) - esperado[0]) <= 2, \
                f"deslocamento y={desl} caiu em {ys_o.min()}, esperava {esperado[0]}"
        cor = np.array(pintar_overlay(pth, {"cor": "#12E06A"}, 1080, 1920))
        px = cor[300, 500]
        assert tuple(px[:3]) == (0x12, 0xE0, 0x6A) and px[3] == 255, f"não coloriu ({px})"

            # b-roll: fade nas pontas, entrada deslizando, empilhamento na ordem
        with _tf.TemporaryDirectory() as _tb:
            quadro = Image.new("RGB", (720, 480), (30, 160, 90))
            pb = Path(_tb) / "b.png"
            quadro.save(pb)
            cfg = {"t0": 0.0, "t1": 2.0, "y": 300, "fade": 0.3, "anim": "esquerda"}
            # no meio do clipe está cheio e no lugar
            meio = np.array(pintar_broll(pb, cfg, 1.0, 1080, 1920))
            assert meio[..., 3].max() == 255, "meio do b-roll devia estar opaco"
            xs_m = np.nonzero(meio[..., 3].sum(axis=0))[0]
            assert abs((xs_m.min() + xs_m.max()) / 2 - 540) < 30, "b-roll fora do centro"
            # no começo ainda entrando pela esquerda e transparente
            ini = np.array(pintar_broll(pb, cfg, 0.02, 1080, 1920))
            assert ini[..., 3].max() < 120, "fade de entrada não aplicou"
            xs_i = np.nonzero(ini[..., 3].sum(axis=0))[0]
            if xs_i.size:
                assert xs_i.mean() < xs_m.mean(), "entrada devia vir da esquerda"
            # e no fim, sumindo
            fim = np.array(pintar_broll(pb, cfg, 1.98, 1080, 1920))
            assert fim[..., 3].max() < 120, "fade de saída não aplicou"

            # encaixe no topo: sangra no alto e dissolve no rodapé
            enc = {"t0": 0.0, "t1": 2.0, "encaixe": "topo", "mescla": 150,
                   "larg": 1.0, "fade": 0}
            e = np.array(pintar_broll(pb, enc, 1.0, 1080, 1920))[..., 3]
            linhas = np.nonzero(e.sum(axis=1))[0]
            assert linhas.min() == 0, f"devia sangrar no topo, começa em {linhas.min()}"
            col = e[:, 540]
            cheio = np.nonzero(col == 255)[0]
            assert cheio.size, "nada opaco no painel encaixado"
            pe = int(linhas.max())
            # rodapé tem que ser rampa, não corte seco
            assert 0 < col[pe - 12] < 255, f"rodapé sem degradê (alpha {col[pe - 12]})"
            assert col[int(cheio.max())] == 255 and col[pe] < 70, "rampa invertida"

            # a mescla ESTENDE, não come: o painel tem que seguir opaco até a
            # altura pedida e só dissolver depois dela
            semm = np.array(pintar_broll(pb, dict(enc, mescla=0), 1.0, 1080, 1920))[..., 3]
            comm = np.array(pintar_broll(pb, enc, 1.0, 1080, 1920))[..., 3]
            fim_sem = int(np.nonzero(semm[:, 540])[0].max())
            opaco_com = int(np.nonzero(comm[:, 540] == 255)[0].max())
            assert opaco_com >= fim_sem - 4, \
                f"degradê comeu o painel (opaco até {opaco_com}, devia ir a {fim_sem})"
            fim_com = int(np.nonzero(comm[:, 540])[0].max())
            assert fim_com > fim_sem + 40, "a mescla não estendeu pra baixo"

            # degradê de COR: o painel caminha pra cor do ambiente na descida.
            # Só rampar alpha deixa branco translúcido, que não mescla.
            branco = Image.new("RGB", (720, 480), (250, 250, 250))
            pw = Path(_td) / "w.png"
            branco.save(pw)
            roxo = (40, 30, 200)   # bem saturado: torna a medida decisiva
            com = np.array(pintar_broll(pw, dict(enc, _cor_fundo=roxo), 1.0, 1080, 1920))
            sem = np.array(pintar_broll(pw, enc, 1.0, 1080, 1920))
            # `paste` com máscara sobre fundo transparente PRÉ-MULTIPLICA o RGB,
            # então nas linhas de alpha baixo a cor já vem escurecida e medir
            # valor absoluto não diz nada. A comparação tem que ser relativa.
            alfa = sem[..., 3][:, 540]
            lin = np.nonzero(alfa)[0]
            meio_rampa = int(np.argmin(np.abs(alfa[lin].astype(int) - 128)) + lin.min())
            r_com, r_sem = int(com[meio_rampa, 540, 0]), int(sem[meio_rampa, 540, 0])
            b_com, b_sem = int(com[meio_rampa, 540, 2]), int(sem[meio_rampa, 540, 2])
            assert r_com < r_sem - 10, f"vermelho não caiu rumo ao roxo ({r_com} vs {r_sem})"
            assert (b_com / max(1, r_com)) > (b_sem / max(1, r_sem)) + 0.15, \
                "não puxou pro azul do ambiente"
            # e o topo do painel fica intacto
            topo_y = int(lin.min()) + 20
            assert abs(int(com[topo_y, 540, 0]) - int(sem[topo_y, 540, 0])) < 4, \
                "topo do painel foi contaminado pela cor do fundo"

            # painel atrás do sujeito: a silhueta fura a camada de trás
            painel = np.array(pintar_broll(pb, dict(enc, atras=True), 1.0, 1080, 1920))
            base_lin = np.nonzero(painel[..., 3].sum(axis=1))[0]
            meio = int(base_lin.min() + (base_lin.max() - base_lin.min()) * 0.4)
            silhueta = np.zeros((1920, 1080), dtype=np.uint8)
            silhueta[:, 380:700] = 255                 # coluna central = a pessoa
            furado = painel.copy()
            furado[..., 3] = (furado[..., 3].astype(np.uint16)
                              * (255 - silhueta) // 255).astype(np.uint8)
            dentro = int(furado[meio, 540, 3])
            fora = int(furado[meio, 120, 3])
            assert dentro == 0, f"silhueta não furou o painel (alpha {dentro})"
            assert fora > 200, f"furou fora da silhueta (linha {meio}, alpha {fora})"

    # card de tela: canto arredondado e posicionado, não colado cru
        capt = Image.new("RGB", (900, 500), (40, 90, 200))
        pt = Path(_td) / "t.png"
        capt.save(pt)
        tl = pintar_tela(pt, {"y": 200, "raio": 40, "sombra": False}, 1080, 1920)
        at = np.array(tl)[..., 3]
        assert at[200 + 250, 540] == 255, "meio da tela devia ser opaco"
        assert at[200 + 2, 2] == 0, "canto devia estar arredondado (transparente)"
        ys_t = np.nonzero(at.sum(axis=1))[0]
        assert abs(int(ys_t.min()) - 200) <= 2, f"y da tela errado ({ys_t.min()})"

        # asset COM cor própria entra como está; com `cor:` vira estêncil
        colorido = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        ImageDraw.Draw(colorido).rectangle([300, 200, 780, 400], fill=(255, 90, 30, 255))
        pc = Path(_td) / "c.png"
        colorido.save(pc)
        orig = np.array(pintar_overlay(pc, {"_rgba": True}, 1080, 1920))[300, 500]
        assert tuple(orig[:3]) == (255, 90, 30), f"perdeu a cor original ({orig})"
        forc = np.array(pintar_overlay(pc, {"_rgba": True, "cor": "#0000FF"},
                                       1080, 1920))[300, 500]
        assert tuple(forc[:3]) == (0, 0, 255), f"`cor` não sobrepôs ({forc})"

    # bloco de manchete: fonte e corpo por linha, script em minúscula, e as
    # linhas não podem se atropelar por causa do ascendente do script
    def _bloco(ent):
        b = finalizar([{"t0": 0.0, "t1": 3.0, "layout": "topo", "quebra": "palavra",
                        "entrelinha": ent, "corpo": 70, "words": [
                            {"tx": "UM CRM INTEIRO", "t0": 0.0, "t1": 2.9, "corpo": 62},
                            {"tx": "sem contratar", "t0": 0.1, "t1": 2.9,
                             "corpo": 128, "fonte": "script", "caixa": "original"},
                            {"tx": "NENHUM DEV", "t0": 0.2, "t1": 2.9, "corpo": 58}]}])[0]
        b["_y"] = 200
        perfil = tinta(b, 1080, 1920)[0].sum(axis=1) > 0
        oc = np.nonzero(perfil)[0]
        return b, int(np.sum(np.diff(oc) > 1) + 1)          # blocos de tinta

    # alinhamento e dx por linha: manchete escalona, não centraliza
    esq = finalizar([{"t0": 0.0, "t1": 3.0, "layout": "topo", "quebra": "palavra",
                      "alinhar": "esquerda", "corpo": 70, "words": [
                          {"tx": "UMA", "t0": 0.0, "t1": 2.9},
                          {"tx": "DUAS", "t0": 0.1, "t1": 2.9, "dx": 120}]}])[0]
    esq["_y"] = 300
    diagramar(esq, 1080, 70, "creato", ImageDraw.Draw(Image.new("RGBA", (1080, 1920))),
              esq["_y"], 440)
    x0, x1 = esq["words"][0]["_cx"], esq["words"][1]["_cx"]
    assert x0 < 1080 / 2, "alinhar=esquerda não encostou na margem"
    assert abs((x1 - esq["words"][1]["_larg"] / 2)
               - (x0 - esq["words"][0]["_larg"] / 2) - 120) < 3, "dx da linha não aplicou"

    b, blocos = _bloco(1.20)
    assert b["words"][1]["tx"] == "sem contratar", "script foi pra caixa alta"
    assert b["words"][0]["tx"] == "UM CRM INTEIRO", "linha normal perdeu a caixa alta"
    # com entrelinha > 1 as três linhas ficam separadas mesmo com o script no meio
    assert blocos == 3, f"esperava 3 linhas separadas, achei {blocos}"
    # e entrelinha < 1 tem que ENCOSTAR de propósito — é como se aperta manchete
    assert _bloco(0.85)[1] < 3, "entrelinha apertada devia juntar as linhas"

    # placa não pode vazar pelo quadro, por mais larga que seja a fonte
    pl = finalizar([{"t0": 0.0, "t1": 1.0, "fonte": "basement", "corpo": 84,
                     "placa": {"tipo": "cartao", "cor": "#111318"},
                     "words": [{"tx": "EU RECEBO NOTIFICAÇÃO", "t0": 0.0, "t1": 0.9}]}])[0]
    pl["_y"] = 1150
    imp = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    _desenhar_card(ImageDraw.Draw(imp), pl, 0.9, 1080, 1920, np.zeros(200, np.float32))
    cols = np.nonzero(np.array(imp)[..., 3].sum(axis=0))[0]
    assert cols.min() >= 1 and cols.max() <= 1078, f"placa vazou ({cols.min()}..{cols.max()})"

    # quebra forçada: cartela de gancho vira N linhas, não o que couber na largura
    hk = finalizar([{"t0": 0.0, "t1": 3.0, "layout": "topo", "quebra": "palavra",
                     "corpo": 82, "words": [{"tx": "UM CRM INTEIRO", "t0": 0.0, "t1": 2.9},
                                            {"tx": "SEM CONTRATAR", "t0": 0.1, "t1": 2.9},
                                            {"tx": "NENHUM DEV", "t0": 0.2, "t1": 2.9}]}])[0]
    hk["_y"] = 200
    bh = tinta(hk, 1080, 1920)[0]
    ys_h = np.nonzero(bh.sum(axis=1))[0]
    livres = np.nonzero(bh.sum(axis=1) == 0)[0]
    quebras = np.sum(np.diff(livres[(livres > ys_h.min()) & (livres < ys_h.max())]) > 1) + 1
    assert quebras == 2, f"esperava 3 linhas (2 vãos), achei {quebras + 1}"

    # quebra por LARGURA MEDIDA: card curto em caractere mas largo em pixel
    # (punch numa fonte larga) tem que quebrar/encolher, não vazar pela lateral
    largo = finalizar([{"t0": 0.0, "t1": 1.0, "layout": "centro", "fonte": "slab",
                        "words": [{"tx": "MENOS DE", "t0": 0.0, "t1": 0.4},
                                  {"tx": "UMA HORA", "t0": 0.4, "t1": 0.9,
                                   "enf": "punch"}]}])[0]
    largo["_y"] = 400
    b3 = tinta(largo, 1080, 1920)[0]
    xs3 = np.nonzero(b3)[1]
    assert xs3.min() >= 0 and xs3.max() < 1080, "texto vazou pela lateral"

    # sujeito tomando o quadro: não dá pra salvar, e o chamador tem que saber
    p3, _, _, _ = ajustar_heroi(h, [_cena(0.05, 0.95)], L, A)
    assert p3 < 0.60, f"devia reprovar e cair pra frente, deu {p3:.0%}"

    # cabeça que ANDA durante o card: a posição tem que aguentar o pior instante.
    # Com média das amostras, a esquerda e a direita se anulam e o herói passa
    # num lugar que fica tapado em metade do card.
    anda = [_cena(0.10, 0.45), _cena(0.30, 0.65), _cena(0.55, 0.90)]
    p4, _, dy4, dx4 = ajustar_heroi(h, anda, L, A)
    if p4 >= 0.60:                       # se aprovou, tem que valer frame a frame
        b2, cx2 = tinta(dict(h, _y=h["_y"]), L, A)
        for i, q in enumerate(anda):
            pf, _ = _visibilidade(b2, cx2, (255 - q) / 255, dy4, dx4)
            assert pf >= 0.55, f"aprovou mas some no frame {i} ({pf:.0%})"

    # toda fonte do registro abre (índice de .ttc, instância variável) E desenha
    # acento — fonte de display costuma vir sem Ç, e o buraco só aparece no vídeo
    for n in FONTES:
        assert fonte(n, 40).getbbox("A"), f"fonte {n} não abriu"
        falta = acentos_faltando(n)
        assert not falta, f"fonte {n} não desenha: {falta}"

    # lint: o card que entra e sai sem nunca ficar inteiro na tela, e o que
    # atravessa a virada de tratamento. Os dois passavam batido antes.
    import io
    import contextlib
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "p.json"
        p.write_text(json.dumps({
            "camera": [{"t0": 0.0, "t1": 2.0, "zoom": [1.0, 1.1]},
                       {"t0": 2.0, "t1": 5.0, "janela": [0.3, 0.6]}],
            "brolls": [],
            "cards": [
                {"t0": 0.0, "t1": 0.30, "words": [{"tx": "UM", "t0": 0.0, "t1": 0.15},
                                                  {"tx": "DOIS", "t0": 0.15, "t1": 0.3}]},
                {"t0": 1.60, "t1": 2.60, "words": [{"tx": "TRÊS", "t0": 1.6, "t1": 2.6}]},
            ]}), encoding="utf-8")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _lint(p)
        saida = buf.getvalue()
        assert "terminar de entrar" in saida, saida
        assert "atravessa a virada de 2.00s" in saida, saida
    print("autoteste ok")


def _lint(caminho: Path) -> int:
    """Confere o plano contra as regras da skill. Rode ANTES de renderizar —
    o render leva minutos por causa do matte; isto leva um segundo.

    O teto de palavras conta só palavra CHEIA: filler é encolhido e apagado, não
    custa leitura como as outras.
    """
    plano = json.loads(caminho.read_text(encoding="utf-8"))
    if isinstance(plano, list):
        plano = {"cards": plano}
    aplicar_plano(plano)
    cards = sorted(plano["cards"], key=lambda c: c["t0"])
    erros, avisos = [], []
    punch, herois = [], []

    # Onde o TRATAMENTO do texto muda: a câmera troca de cena (o corpo dele pula
    # de lugar) ou um painel de tela cheia entra e sai (ele deixa de estar
    # exposto). Uma legenda que atravessa esse instante nasce num regime e morre
    # noutro — pisca por cima do gráfico ou fica sem lugar quando a câmera anda.
    cortes = sorted({round(float(v), 3)
                     for c in (plano.get("camera") or [])
                     for v in (c["t0"], c["t1"])}
                    | {round(float(v), 3)
                       for b in (plano.get("brolls") or [])
                       # peça com alpha não tapa ninguém: ela flutua sobre a
                       # imagem e o apresentador continua exposto, então não há
                       # troca de tratamento pra legenda atravessar
                       if float(b.get("alt", 0)) >= 0.9 and not b.get("alfa")
                       for v in (b["t0"], b["t1"])})

    # sobreposição só é erro DENTRO da mesma camada: gancho e legenda convivem
    for cam in {c.get("camada", "legenda") for c in cards}:
        fila = [c for c in cards if c.get("camada", "legenda") == cam]
        for a, b in zip(fila, fila[1:]):
            if a["t1"] > b["t0"] + 1e-6:
                erros.append(f'{a["t0"]:6.2f}s  invade o card seguinte (camada {cam})')

    for c in cards:
        t0, t1 = c["t0"], c["t1"]
        dur = t1 - t0
        # O PISO DEPENDE DE QUANTAS PALAVRAS O CARD TEM.
        #
        # 0,35s e a regua de card com frase: abaixo disso o olho nao termina de
        # varrer e a leitura pisca. Card de UMA palavra e outra coisa -- e
        # karaoke, o olho ja esta no lugar e so troca o que esta escrito, e a
        # velocidade e a da fala. O estilo 7a e todo assim, e com o piso unico
        # ele reprovava 200 cards que estao certos.
        piso = 0.35 if len(c["words"]) > 1 else 0.14
        if dur < piso:
            erros.append(f"{t0:6.2f}s  card de {dur:.2f}s com {len(c['words'])} palavra(s)"
                         f" — ninguém lê abaixo de {piso}")
        # ENTRAR NÃO É ESTAR LEGÍVEL. A última palavra do card só assenta em
        # t0 + ENTRADA + STAGGER*(n-1); o que sobra até t1 é o tempo em que a
        # frase inteira está na tela. Medir o intervalo cru aprova card de meio
        # segundo com quatro palavras — 0,47s entrando e 0,03s legível.
        entrando = ENTRADA + STAGGER * (len(c["words"]) - 1)
        legivel = dur - entrando
        if len(c["words"]) > 1:
            if legivel <= 0:
                erros.append(f"{t0:6.2f}s  acaba antes de terminar de entrar "
                             f"({dur:.2f}s de card, {entrando:.2f}s de entrada)")
            elif legivel < 0.12:
                erros.append(f"{t0:6.2f}s  só {legivel:.2f}s com a frase inteira na tela"
                             f" — entra em {entrando:.2f}s e já sai")
        # a folga é de UM frame: com mais que isso, um card que começa dois
        # frames antes do painel e roda dois segundos embaixo dele passa batido
        cruza = [x for x in cortes if t0 + 1 / 30 < x < t1 - 1 / 30]
        if cruza and c.get("camada", "legenda") == "legenda":
            avisos.append(f"{t0:6.2f}s  atravessa a virada de {cruza[0]:.2f}s — "
                          f"nasce num tratamento e morre noutro")
        cheias = [w for w in c["words"] if w.get("enf") != "filler"]
        if len(cheias) > 4:
            erros.append(f"{t0:6.2f}s  {len(cheias)} palavras cheias (teto 4)")
        if sum(len(w["tx"]) + 1 for w in c["words"]) > 40:
            avisos.append(f"{t0:6.2f}s  card comprido, vai quebrar em 3 linhas")
        for w in c["words"]:
            if w["t0"] < t0 - 0.4 or w["t1"] > t1 + 0.4:
                erros.append(f"{t0:6.2f}s  '{w['tx']}' fora da janela do card")
            if w.get("enf") == "punch":
                punch.append((t0, w["tx"]))
            if w.get("fonte", c.get("fonte")) and w["tx"] != w["tx"].upper():
                pass
        if c.get("atras"):
            herois.append(t0)
            if c.get("layout") != "centro":
                avisos.append(f"{t0:6.2f}s  herói fora do centro — a oclusão pede o meio")

    if len(punch) > 3:
        erros.append(f"        {len(punch)} punches (teto 3): "
                     f"{', '.join(t for _, t in punch)} — quatro punches é zero punch")
    for a, b in zip(herois, herois[1:]):
        if b - a < 5.0:
            erros.append(f"{b:6.2f}s  herói a {b - a:.1f}s do anterior — falta respiro")

    fontes = {}
    for c in cards:
        fontes[c.get("fonte", FONTE_PADRAO)] = fontes.get(c.get("fonte", FONTE_PADRAO), 0) + 1
    if len(fontes) > 6:
        avisos.append(f"        {len(fontes)} fontes — se tudo muda, nada marca virada")

    # uma fonte por grupo do pack: duas da mesma pasta se parecem demais
    porgrupo: dict[str, set[str]] = {}
    for n in fontes:
        g = GRUPO_FONTE.get(n)
        if g:
            porgrupo.setdefault(g, set()).add(n)
    for g, ns in sorted(porgrupo.items()):
        if len(ns) > 1:
            erros.append(f"        {len(ns)} fontes do grupo {g} ({', '.join(sorted(ns))}) "
                         f"— máximo 1 por grupo; as da mesma pasta se parecem")

    # Buraco curto entre duas peças pisca. A de trás sai com fade, a da frente
    # entra com fade, e no vão as duas estão transparentes: aparece o vídeo cru
    # por três frames e lê como falha de edição. Ou as peças se encostam, ou o
    # vão é longo o bastante pra ser respiro.
    peças = sorted((b for b in (plano.get("brolls") or [])
                    if float(b.get("alt", 0)) >= 0.35),
                   key=lambda b: float(b["t0"]))
    for a, b in zip(peças, peças[1:]):
        vao = float(b["t0"]) - float(a["t1"])
        if 0 < vao < 0.5:
            erros.append(f'{a["t1"]:6.2f}s  buraco de {vao:.2f}s até a peça '
                         f'seguinte — encoste as duas ou abra pra 0.5s, senão '
                         f'a imagem pisca no vão')

    cobre = sum(c["t1"] - c["t0"] for c in cards)
    print(f"{len(cards)} cards | {cobre:.1f}s de legenda | {len(punch)} punch | "
          f"{len(herois)} herói | fontes: {', '.join(f'{k}×{v}' for k, v in fontes.items())}")
    for a in avisos:
        print(f"  aviso  {a}")
    for e in erros:
        print(f"  ERRO   {e}")
    if not erros and not avisos:
        print("  plano limpo")
    return 1 if erros else 0


def _auditar(pasta: Path) -> None:
    """Varre um pack de fontes: densidade de tinta, proporção e buraco de glifo.

    Rode isto ANTES de adicionar fonte ao registro. Densidade alta = pesada =
    boa pra legenda queimada; proporção alta = larga = come linha.
    """
    linhas = []
    for f in sorted(pasta.rglob("*")):
        if f.suffix.lower() not in (".otf", ".ttf") or "__MACOSX" in str(f):
            continue
        try:
            ft = ImageFont.truetype(str(f), 64)
            fam, est = ft.getname()
        except Exception:
            print(f"  ABRIU NÃO  {f.name}")
            continue
        FONTES[f"_aud_{f.stem}"] = (str(f), 0, None)
        falta = acentos_faltando(f"_aud_{f.stem}")
        im = Image.new("L", (900, 220), 0)
        ImageDraw.Draw(im).text((450, 110), "NENHUM", font=ft, fill=255, anchor="mm")
        a = np.array(im) > 128
        ys, xs = np.nonzero(a)
        if not len(xs):
            continue
        lg, al = int(xs.max() - xs.min()), int(ys.max() - ys.min())
        linhas.append((round(float(a.sum()) / max(1, lg * al), 3),
                       round(lg / max(1, al), 2), fam, est, falta, str(f)))
    linhas.sort(key=lambda r: -r[0])
    ruins = [r for r in linhas if r[4]]
    print(f"{len(linhas)} fontes | {len(ruins)} com acento faltando\n")
    print(f"{'dens':>5} {'l/a':>5}  {'família':32} {'estilo':18} falta")
    for d, ra, fam, est, falta, _ in linhas:
        print(f"{d:5.2f} {ra:5.2f}  {fam[:32]:32} {est[:18]:18} {falta[:14]}")


if __name__ == "__main__":
    if "--lint" in sys.argv:
        sys.exit(_lint(Path(sys.argv[sys.argv.index("--lint") + 1])))
    elif "--auditar" in sys.argv:
        _auditar(Path(sys.argv[sys.argv.index("--auditar") + 1]))
    elif "--autoteste" in sys.argv:
        _autoteste()
    else:
        main()
