#!/usr/bin/env python3
"""A capa do reel no molde do Nick: a peça g_capa_nick do tools/v2, parada num JPEG 1080×1920.

    from capa import capa_nick
    capa_nick(plano["capa"], pasta_do_video, trabalho / "capa-nick.jpg")

O bloco `capa` do plano traz tudo que é do vídeo; caminho é da pasta do vídeo:
  foto      a foto da pessoa, do peito pra cima. Com fundo ou sem: o rembg tira uma vez, e o tronco
            estica até a borda de baixo da capa. [vídeo, t]: o quadro do vídeo no segundo t (o webm
            do avatar, que já vem sem fundo)
  titulo    "linha 1|linha 2"; `destaque` é o trecho do título que vai na faixa
  topo      o nome da ferramenta, em texto; `logo` é o endereço da marca (`@arquivo` é da pasta do vídeo)
  lados     os dois ícones: mic | onda | claquete | filme | rec | cel, texto curto ou `@arquivo`
  cena      [vídeo, t, y]: um quadro do vídeo, recortado quadrado, entra antes dos `lados`
            (`t` e `y` em fração da duração e da altura)
  larg, ry, iy  o enquadramento: a largura da foto na capa, onde começa o cabelo, a altura dos ícones
Chave que começa com `_` é nota e não vai pra peça.
"""
from __future__ import annotations

import sys
from pathlib import Path

import ff

V2 = Path(__file__).resolve().parents[2] / "v2"
W, H = 1080, 1920


def _v2():
    """Import tardio, como o da fábrica: só a peça parada precisa da biblioteca."""
    if str(V2) not in sys.path:
        sys.path.insert(0, str(V2))
    import v2
    return v2


def quadro(video: Path, t: float, out: Path, alfa: bool = False) -> Path:
    """Um quadro do vídeo em PNG; `alfa` lê o webm com o decodificador que guarda o canal alfa."""
    if not out.exists():
        dec = ["-c:v", "libvpx-vp9"] if alfa else []
        ff.run(["ffmpeg", "-y", "-ss", f"{t:.3f}", *dec, "-i", str(video), "-frames:v", "1", str(out)], quiet=True)
    return out


def recorte(fonte: Path, out: Path, gama: float = .8) -> Path:
    """A foto sem fundo, com o topo da cabeça no topo e o tronco esticado até 2× a largura, pra descer até a
    borda de baixo da capa em qualquer enquadramento. Refaz só se faltar ou se a foto for mais nova.
    Fonte que já vem com alfa não passa pelo rembg de novo."""
    from PIL import Image
    if out.exists() and out.stat().st_mtime >= fonte.stat().st_mtime:
        with Image.open(out) as im:
            if im.height >= 2 * im.width:
                return out
    import numpy as np
    im = Image.open(fonte)
    if im.mode != "RGBA":
        from rembg import remove, new_session
        im = remove(im.convert("RGB"), session=new_session("birefnet-portrait"))
    topo = im.getchannel("A").point(lambda a: 255 if a > 40 else 0).getbbox()[1]
    im = im.crop((0, max(0, topo - 8), im.width, im.height))
    alfa = im.getchannel("A")
    im = im.convert("RGB").point([round(255 * (i / 255) ** gama) for i in range(256)] * 3)   # clareia os médios, a gola segue preta
    im.putalpha(alfa)
    # o vão entre braço e tronco, no quarto de baixo: o rembg deixa ali uma fresta de fundo, e o brilho da peça
    # contorna a fresta como uma linha. Fecha de borda a borda em cada linha, com o fundo da fresta escurecido
    a = np.array(im)
    for y in range(a.shape[0] * 3 // 4, a.shape[0]):
        nz = np.flatnonzero(a[y, :, 3] > 128)
        if len(nz):
            s = a[y, nz[0]:nz[-1] + 1]
            s[:, :3] = (s[:, :3] * (s[:, 3:] / 255)).astype(np.uint8)
            s[:, 3] = 255
            # abaixo do título, o risco de luz na borda do braço vira zigue-zague quando a faixa espelha:
            # teto no brilho da malha preta (99% dela fica abaixo de 27)
            if y >= a.shape[0] * 17 // 20:
                np.minimum(s[:, :3], 28, out=s[:, :3])
    # o tronco: a silhueta da última linha desce reta e a malha vem da faixa de baixo espelhada, escurecendo
    falta, faixa = 2 * im.width - im.height, a[-160:]
    if falta > 0:
        ext = np.concatenate([faixa[::-1] if k % 2 == 0 else faixa for k in range(falta // 160 + 1)])[:falta].astype(np.float32)
        ext[..., :3] *= np.linspace(1, .75, falta)[:, None, None]
        ext[..., 3] = a[-1, :, 3]
        a = np.concatenate([a, ext.astype(np.uint8)])
    Image.fromarray(a, "RGBA").save(out)
    return out


def meio(png: Path) -> float:
    """O meio da cabeça em fração da largura, medido na faixa do cabelo à testa (o `cx` da peça)."""
    from PIL import Image
    a = Image.open(png).getchannel("A")
    x0, _, x1, _ = a.crop((0, a.width // 10, a.width, a.width * 3 // 10)).point(lambda v: 255 if v > 100 else 0).getbbox()
    return (x0 + x1) / 2 / a.width


def cena(video: Path, t: float, yc: float, pasta: Path) -> str:
    """Um quadro do vídeo recortado quadrado (o ícone de app do lado): `t` e `yc` em fração da duração e da altura."""
    from PIL import Image
    out = pasta / f"icone_{video.stem}_{t:.2f}_{yc:.2f}.png"
    if not out.exists():
        im = Image.open(quadro(video, ff.dur(video) * t, pasta / f"cena_{video.stem}_{t:.2f}.png"))
        y = min(max(0, round(im.height * yc - im.width / 2)), im.height - im.width)
        im.crop((0, y, im.width, y + im.width)).save(out)
    return out.as_uri()


def parada(peca: str, pares: list[str], out: Path, tema: str | None = None, t: float = 0.5) -> Path:
    """A peça parada no instante `t` (meio segundo, por padrão), direto num JPEG: o mp4 do `v2.py render` passaria a
    cor por 4:2:0 duas vezes."""
    from playwright.sync_api import sync_playwright
    from html_para_video import carrega_fontes
    v2 = _v2()
    p, qv = v2.acha(peca)
    url = (v2.AQUI / p["arquivo"]).as_uri() + "?" + v2._query(qv, pares, {"ar": f"{W}x{H}", **({"tema": tema} if tema else {})})
    with sync_playwright() as pw:
        nav = pw.chromium.launch(args=["--force-color-profile=srgb", "--disable-lcd-text"])
        pg = nav.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        pg.goto(url)
        pg.wait_for_function("window.__tl && window.__ready === true", timeout=30000)
        carrega_fontes(pg)
        pg.evaluate(f"() => {{ window.__tl.time({t}); }}")   # devolver a timeline trava o playwright
        pg.screenshot(path=str(out), type="jpeg", quality=93)
        nav.close()
    print(f"wrote {out}")
    return out


def capa_nick(bloco: dict, pasta: Path, out: Path, trabalho: Path | None = None, tema: str | None = None) -> Path:
    """O bloco `capa` do plano na g_capa_nick, em `out`. `pasta` é a do vídeo, de onde os caminhos do bloco
    partem; o recorte da foto e o quadro da cena ficam em `trabalho` (padrão: a pasta de `out`)."""
    trabalho = trabalho or out.parent
    trabalho.mkdir(parents=True, exist_ok=True)
    url = lambda v: (pasta / v[1:]).resolve().as_uri() if v.startswith("@") else v
    c = {k: v for k, v in bloco.items() if not k.startswith("_")}
    if "foto" not in c:
        sys.exit("a `capa` precisa de `foto`: o caminho da foto da pessoa, da pasta do vídeo")
    foto = c.pop("foto")
    if isinstance(foto, list):      # [vídeo, t]: um quadro dele; o webm da HeyGen sai com o alfa, sem rembg
        v, t = pasta / foto[0], float(foto[1])
        if not v.exists():
            sys.exit(f"o vídeo da foto da capa não existe: {v}")
        foto = quadro(v, t, trabalho / f"foto_{v.stem}_{v.stat().st_size}_{t:.2f}.png", alfa=v.suffix.lower() == ".webm")
    else:
        foto = pasta / foto
    if not foto.exists():
        sys.exit(f"a foto da capa não existe: {foto}")
    if "logo" in c:
        c["logo"] = url(c["logo"])
    if "lados" in c:
        c["lados"] = ",".join(url(v) for v in c["lados"].split(","))
    if "cena" in c:
        v, t, yc = c.pop("cena")
        c["lados"] = cena(pasta / v, t, yc, trabalho) + "," + c.get("lados", "")
    r = recorte(foto, trabalho / f"recorte-{foto.stem}.png")
    c.update(rosto=r.as_uri(), cx=f"{meio(r):.3f}")
    return parada("g_capa_nick", [f"{k}={v}" for k, v in c.items()], out, tema)
