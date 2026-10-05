#!/usr/bin/env python3
"""Biblioteca v2 — o ÚNICO ponto de entrada de motion do repo.

Tudo que desenha mora em tools/v2/pecas/ (HTML + GSAP, timeline buscável) e
herda cor, fonte e movimento de tools/v2/nucleo/. Este script lista, renderiza
e compõe. Os scripts antigos (make_reel_v3, lesson_overlays, tools/mg) viram
TRADUTORES: leem a config deles e chamam isto — não desenham mais nada.

    v2.py lista   [--familia ve] [--formato 1920x1080] [--camadas]
    v2.py info    <peca>
    v2.py catalogo                                   ← regenera o catalogo.json dos cabeçalhos
    v2.py qa      [peca ...] [--familia g] [--json rel.json] [--notas]
                                                     ← inspeciona as peças (mesma regra do Estúdio);
                                                       sai com código 1 se houver falha
    v2.py render  <peca> [k=v ...] [--out x.mov] [--ar 1080x1920] [--tema claro|tinta]
                          [--camada tras|frente] [--fps 30] [--opaco]
    v2.py camadas <peca> [k=v ...] --out base      → base.tras.mov, base.frente.mov, base.json
    v2.py compor  --take take.mp4 --peca base.json --em 12.4 --out saida.mp4
                  [--pessoa pessoa.mov] [--folga 1.25] [--seco]

  <peca> é o id do catalogo.json (ou um id de variante, ex.: ve_titulo_capa).
  k=v entra na query da peça, exatamente como no comentário do topo dela.

Saídas de render: ProRes 4444 com alfa (padrão) e, ao lado, <saida>.json com
duração, cues de som (window.__cues), onde a peça quer a pessoa
(window.__pessoa) e os efeitos que ela pede ao take (window.__video).

Requer o venv do pipeline: ~/obs-optimize/tools/video-use/.venv/bin/python
"""
from __future__ import annotations

import argparse, json, shutil, sys, tempfile, time
from pathlib import Path
from urllib.parse import urlencode, parse_qsl

AQUI = Path(__file__).resolve().parent
CATALOGO = AQUI / "catalogo.json"
# A marca do aluno, na raiz da fábrica (ao lado de tools/): ?tema=marca carrega esta folha por cima
# do núcleo (direcao-v2.js). Ela sobrevive à atualização do kit, que só troca tools/.
MARCA_CSS = AQUI.parents[1] / "marca" / "tema.css"
HELPERS = AQUI.parent / "video-use" / "helpers"
sys.path.insert(0, str(HELPERS))
import ff  # noqa: E402 — a costura B: todo ffmpeg daqui passa por ela


# ───────────────────────── núcleo ─────────────────────────
def token(nome: str, tema: str | None = None) -> str:
    """O valor de um token do núcleo (`ac` → "#0640fb"). Quem roda fora do
    navegador — a legenda, a fábrica — lê daqui em vez de copiar o hex. Com o
    tema `marca`, o que a marca/tema.css redeclara ganha do núcleo."""
    import re
    css = (AQUI / "nucleo" / "direcao-v2.css").read_text(encoding="utf-8")
    if tema == "marca" and MARCA_CSS.is_file():
        css = MARCA_CSS.read_text(encoding="utf-8") + css
    m = re.search(rf"--{re.escape(nome)}:\s*([^;}}]+)[;}}]", css)
    if not m:
        sys.exit(f"token que o núcleo não tem: --{nome}")
    return m.group(1).strip()


# ───────────────────────── catálogo ─────────────────────────
def catalogo() -> dict:
    return json.loads(CATALOGO.read_text(encoding="utf-8"))


def acha(peca: str) -> tuple[dict, str]:
    """Devolve (entrada do catálogo, query da variante). Aceita alias."""
    cat = catalogo()
    al, qa = cat.get("aliases", {}).get(peca), ""
    if al:   # nome antigo (make_reel_v3, lesson_overlays) → peça nova + query fixa
        peca, qa = (al["peca"], al.get("query", "")) if isinstance(al, dict) else (al, "")
    for p in cat["pecas"]:
        if p["id"] == peca:
            return p, qa
        for v in p.get("variantes", []):
            if v["id"] == peca:   # variante pode trocar o formato (ex.: x_corte_16x9)
                return {**p, "formato": v.get("formato", p["formato"])}, v["query"]
    sys.exit(f"peça desconhecida: {peca}  (v2.py lista)")


def cmd_lista(a):
    for p in catalogo()["pecas"]:
        if a.familia and p["familia"] != a.familia:
            continue
        if a.formato and p["formato"] != a.formato:
            continue
        if a.camadas and not p["camadas"]:
            continue
        marca = ("alfa " if p["alfa"] else "     ") + ("camadas " if p["camadas"] else "        ")
        print(f"{p['id']:<22} {p['formato']:<10} {marca} {p.get('nome') or ''}")
        for v in p.get("variantes", []):
            print(f"  └ {v['id']:<18} ?{v['query']}")


def cmd_info(a):
    p, q = acha(a.peca)
    print(json.dumps({**p, "query_variante": q}, ensure_ascii=False, indent=1))


def cmd_catalogo(a):
    """Regenera o catalogo.json a partir do comentário do topo de cada peça.
    Nome, grupo, variantes e aliases já escritos à mão são preservados."""
    cat = gera_catalogo()
    CATALOGO.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {CATALOGO}  ({len(cat['pecas'])} peças)")


def gera_catalogo() -> dict:
    """O catálogo que os cabeçalhos das peças descrevem hoje, sem gravar."""
    import re
    velho = catalogo() if CATALOGO.exists() else {"pecas": []}
    por_id = {p["id"]: p for p in velho["pecas"]}
    novas = []
    for f in sorted((AQUI / "pecas").glob("*.html")):
        s = f.read_text(encoding="utf-8")
        c = (re.search(r"<!--([\s\S]*?)-->", s) or [None, ""])[1]
        ls = [l.strip() for l in c.splitlines() if l.strip()]
        v = por_id.get(f.stem, {})
        dims = re.search(r"(\d{3,4})x(\d{3,4})", c)
        # `?a=1` ou `rótulo: ?a=1` — peça com mais de um modo nomeia cada exemplo
        ex = next((l[l.index("?"):] for l in ls if re.match(r"(\w+:\s*)?\?", l)), "")
        novas.append({"id": f.stem, "arquivo": f"pecas/{f.name}", "familia": f.stem.split("_")[0],
                      "grupo": v.get("grupo"), "nome": v.get("nome"),
                      "formato": dims.group(0) if dims else v.get("formato", "1080x1920"),
                      "alfa": "--alpha" in c or bool(re.search(r'class="[^"]*\balfa\b', s)),
                      "camadas": 'data-c="' in s, "descricao": re.sub(r"\s+", " ", ls[0] if ls else "")[:220],
                      "exemplo": ex, **({"variantes": v["variantes"]} if v.get("variantes") else {})})
    velho.update({"pecas": novas, "gerado": time.strftime("%Y-%m-%d")})
    return velho


# ───────────────────────── qa ─────────────────────────
def cmd_qa(a):
    """Inspeciona as peças no Chromium com a MESMA regra do Estúdio (nucleo/qa.js):
    fica pronta, duração × timeline, cues com arquivo, texto que vaza ou é cortado
    pela caixa, texto fora do quadro ou na zona do rosto (16:9), peça alfa que
    aparece sem entrar ou não sai, contrato da timeline, cor e fonte fora do
    núcleo. Código 1 se houver falha: dá pra pôr antes de todo render."""
    from playwright.sync_api import sync_playwright
    cat = catalogo()
    sons = json.loads((AQUI / "sfx" / "sfx.json").read_text(encoding="utf-8"))["sons"]
    qa_js = (AQUI / "nucleo" / "qa.js").read_text(encoding="utf-8")
    alvo = []
    for p in cat["pecas"]:
        if a.familia and p["familia"] != a.familia:
            continue
        alvo.append((p["id"], p, ""))
        alvo += [(v["id"], {**p, "formato": v.get("formato", p["formato"])}, v["query"]) for v in p.get("variantes", [])]
    if a.pecas:
        alvo = [x for x in alvo if x[0] in a.pecas]
    rel, marca = [], {"ok": "✓", "aviso": "!", "falha": "✕"}
    with sync_playwright() as pw:
        nav = pw.chromium.launch(args=["--force-color-profile=srgb"])
        aux = nav.new_page()
        aux.set_content("<html><body></body></html>")
        aux.add_script_tag(content=qa_js)
        for pid, p, qv in alvo:
            W, H = (int(x) for x in p["formato"].split("x"))
            pg = nav.new_page(viewport={"width": W, "height": H})
            erros: list[str] = []
            pg.on("pageerror", lambda e, erros=erros: erros.append(str(e)))
            q = "&".join(x for x in (qv, f"ar={p['formato']}") if x)
            r = {"id": pid, "achados": []}
            t0 = time.time()
            try:
                pg.goto((AQUI / p["arquivo"]).as_uri() + "?" + q)
                pg.wait_for_function("window.__tl && window.__ready === true", timeout=15000)
                pg.evaluate("document.fonts.ready.then(() => true)")
                r["pronta_ms"] = int((time.time() - t0) * 1000)
                pg.add_script_tag(content=qa_js)
                opc = {"alfa": p["alfa"], "sai": True,
                       "rosto": [1440, 760, 1880, 1040] if p["familia"] == "h" and p["alfa"] else None}
                d = pg.evaluate("([s, o]) => V2QA.dinamico(window, s, o)", [sons, opc])
                r["achados"] += d.pop("achados")
                r.update(d)
            except Exception as e:
                r["achados"].append({"nivel": "falha", "tipo": "pronta", "msg": "não ficou pronta: " + str(e).splitlines()[0][:160]})
            r["achados"] += [{"nivel": "falha", "tipo": "erro", "msg": m[:200]} for m in erros]
            r["achados"] += aux.evaluate("s => V2QA.estatico(s)", (AQUI / p["arquivo"]).read_text(encoding="utf-8"))
            pg.close()
            nv = {x["nivel"] for x in r["achados"]}
            r["nivel"] = "falha" if "falha" in nv else "aviso" if "aviso" in nv else "ok"
            rel.append(r)
            print(f"{marca[r['nivel']]} {pid:<24} {r.get('dur', 0):5.2f}s {r.get('ncues', 0):3d} cues")
            for x in r["achados"]:
                if x["nivel"] != "nota" or a.notas:
                    print(f"      {x['nivel']:<5} {x['tipo']:<8} {x['msg']}")
        nav.close()
    if a.json:
        Path(a.json).write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
    n = {k: sum(r["nivel"] == k for r in rel) for k in ("ok", "aviso", "falha")}
    print(f"\n{len(rel)} peças · {n['ok']} ok · {n['aviso']} com aviso · {n['falha']} com falha")
    sys.exit(1 if n["falha"] else 0)


# ───────────────────────── render ─────────────────────────
def _query(base_q: str, pares: list[str], extra: dict) -> str:
    q = dict(parse_qsl(base_q, keep_blank_values=True))
    for kv in pares:
        k, _, v = kv.partition("=")
        q[k] = v
    q.update({k: v for k, v in extra.items() if v is not None})
    return urlencode(q)


# Rastro (motion blur): cada quadro é a média de 4 de 8 subquadros (obturador de 180°), com o
# alfa pré-multiplicado — sem isso a borda que anda mistura cor com o preto do transparente e
# vira franja escura. A 120 qps o rastro sai em cópias separadas; a 240, corre (AN2, 03/10).
SUBQUADROS = 8


def render(peca: str, pares: list[str], out: Path, ar: str | None = None, tema: str | None = None,
           camada: str | None = None, fps: int = 30, alfa: bool = True, rastro: bool = False) -> dict:
    from playwright.sync_api import sync_playwright
    from html_para_video import carrega_fontes

    p, qv = acha(peca)
    ar = ar or p["formato"]
    W, H = (int(x) for x in ar.lower().split("x"))
    q = _query(qv, pares, {"ar": ar, "tema": tema, "camada": camada})
    if dict(parse_qsl(q)).get("tema") == "marca" and not MARCA_CSS.is_file():
        sys.exit(f"o tema marca pede {MARCA_CSS}, que não existe: instale o pacote de marca ou troque o tema")
    url = (AQUI / p["arquivo"]).as_uri() + "?" + q
    quadros = Path(tempfile.mkdtemp(prefix="v2_"))
    try:
        with sync_playwright() as pw:
            nav = pw.chromium.launch(args=["--force-color-profile=srgb", "--disable-lcd-text"])
            pg = nav.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
            pg.goto(url)
            pg.wait_for_function("window.__tl && window.__ready === true", timeout=30000)
            pg.wait_for_timeout(300)
            carrega_fontes(pg)
            meta = pg.evaluate("({duracao: window.__duration, cues: window.__cues || [],"
                               " pessoa: window.__pessoa || null, video: window.__video || []})")
            k = SUBQUADROS if rastro else 1
            n = int(meta["duracao"] * fps) * k
            t0 = time.time()
            for i in range(n + 1):
                pg.evaluate("(t)=>{window.__tl.time(t);}", i / (fps * k))
                pg.screenshot(path=str(quadros / f"f_{i:05d}.png"), omit_background=alfa)
                if i % 60 == 0:
                    print(f"  {peca}{'·' + camada if camada else ''}  {i}/{n}  {time.time() - t0:.1f}s")
            nav.close()
        cod = (["-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le"] if alfa else
               ["-c:v", ff.CODEC_VIDEO, "-pix_fmt", ff.PIX_FMT, "-crf", "17", "-movflags", "+faststart"])
        mistura = []
        if rastro:
            m = f"tmix=frames={SUBQUADROS // 2},framestep={SUBQUADROS}"
            mistura = ["-vf", f"premultiply=inplace=1,{m},unpremultiply=inplace=1" if alfa else m, "-r", str(fps)]
        ff.run(["ffmpeg", "-y", "-framerate", str(fps * k), "-i", str(quadros / "f_%05d.png"), *mistura, *cod, str(out)],
               quiet=True)
    finally:
        shutil.rmtree(quadros, ignore_errors=True)
    meta.update({"peca": peca, "query": q, "fps": fps, "formato": ar})
    out.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {out}  ({meta['duracao']:.2f}s, {len(meta['cues'])} cues)")
    return meta


def cmd_render(a):
    out = Path(a.out or (a.peca + ".mov"))
    render(a.peca, a.pares, out, a.ar, a.tema, a.camada, a.fps, alfa=not a.opaco, rastro=a.rastro)


def cmd_camadas(a):
    """As duas camadas de uma peça de ensaio + um JSON só, que o `compor` lê."""
    p, _ = acha(a.peca)
    if not p["camadas"]:
        sys.exit(f"{a.peca} não é em camadas — use `render`")
    base = Path(a.out)
    meta = None
    for c in ("tras", "frente"):
        meta = render(a.peca, a.pares, base.with_suffix(f".{c}.mov"), a.ar, a.tema, c, a.fps)
        base.with_suffix(f".{c}.json").unlink(missing_ok=True)
    meta["camadas"] = {c: str(base.with_suffix(f".{c}.mov")) for c in ("tras", "frente")}
    base.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {base.with_suffix('.json')}")


# ───────────────────────── compor ─────────────────────────
# Pilha, tudo no mesmo t:  take (reenquadrado + efeitos) → tras → pessoa → frente.
# `pessoa` é o recorte ALFA do próprio take (HeyGen sem fundo, rembg…): recebe a
# mesma geometria e os mesmos efeitos de cor do take, menos o desfoque — é o
# que faz "desfocar só o fundo" funcionar.
CENTRO_X = 610          # x da pessoa centralizada, no quadro da peça (ensaio.js)
SOBE = .5               # quanto o `empurra` leva pra chegar (s)
IO = "(if(lt({k},.5),4*pow({k},3),1-pow(-2*{k}+2,3)/2))"   # ease-in-out cúbico


def _k_janela(a: float, b: float, dur: float = .6, t: str = "it") -> str:
    """0→1 em `dur` a partir de a, 1→0 em `dur` antes de b."""
    ki = f"clip(({t}-{a:.3f})/{dur},0,1)"
    ko = f"clip(({b:.3f}-{t})/{dur},0,1)"
    return f"min({IO.format(k=ki)},{IO.format(k=ko)})"


def _cartao(meta: dict) -> dict | None:
    """O enquadramento do cartão (e_editorial), se a peça pediu. Um só por peça."""
    cs = [e for e in meta.get("video", []) if e["efeito"] == "cartao"]
    if not cs:
        return None
    geo = lambda e: tuple(e[k] for k in ("x", "y", "w", "h", "raio", "escala", "topo"))
    if any(geo(e) != geo(cs[0]) for e in cs):
        sys.exit("cartões com enquadramento diferente na mesma peça: o compor só sabe um")
    return {**cs[0], "trechos": [(e["t0"], e["t1"]) for e in cs]}


def mascara_cartao(c: dict, destino: Path) -> Path:
    """Branco no cartão, preto fora. Só os cantos de cima arredondam: o de baixo
    sangra pra fora do quadro. Desenhado 4× e reduzido, pra borda não serrilhar."""
    from PIL import Image, ImageDraw
    k, w, h, r = 4, int(c["w"]), int(c["h"]), int(c["raio"])
    im = Image.new("L", (w * k, h * k), 0)
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w * k - 1, (h + r) * k), radius=r * k, fill=255)
    im.resize((w, h), Image.LANCZOS).save(destino)
    return destino


def grafo(meta: dict, em: float, W: int, H: int, folga: float, com_pessoa: bool,
          i_mascara: int | None = None, fontes: tuple[int, int] | None = None) -> tuple[str, str]:
    """`fontes`: os qps do take e da pessoa, que a ff.taxa leva aos da peça."""
    dur = meta["duracao"]
    fps = meta.get("fps", 30)
    fontes = fontes or (fps, fps)
    ef = [{**e, "t0": e["t0"] + em, "t1": e["t1"] + em} for e in meta.get("video", [])]
    um = lambda n: next((e for e in ef if e["efeito"] == n), None)

    # Geometria num filtro só, com saída de tamanho FIXO (perspective + scale W×H):
    # mudar o tamanho do quadro no meio do vídeo é o que fazia a escada do crop no
    # captions_viral. O take aberto é ampliado `folga` vezes e a janela desliza
    # até a pessoa cair onde a peça quer. A folga cresce sozinha se o deslize
    # pedir mais margem do que ela dá.
    pes = meta.get("pessoa") or {}
    dx = (pes.get("x", CENTRO_X) - CENTRO_X) if pes.get("lado") not in (None, "centro") else 0
    folga = max(folga, 1 + 2 * abs(dx) / W) if dx else folga
    # zoom: um trecho ou vários (o rosto cheio do e_editorial pede um por cena, em
    # corte seco: entra 0). Fora de todos, 1.
    # O tempo é o quadro de entrada (`in`): o perspective não tem `t`, e antes dele o take já
    # está na taxa da peça (cadeia).
    t = f"(in/{fps})"
    z = "1"
    for zm in reversed([e for e in ef if e["efeito"] == "zoom"]):
        k = f"clip(({t}-{zm['t0']:.3f})/{max(zm.get('entra', .5), .001)},0,1)"
        # `reta` é a deriva entre dois cortes: o corte esconde a partida e a parada
        anda = k if zm.get("curva") == "reta" else f"(1-pow(1-{k},3))"
        z = (f"if(between({t},{zm['t0']:.3f},{zm['t1']:.3f}),"
             f"{zm['de']}+({zm['para']}-{zm['de']})*{anda},{z})")
    # empurra: a câmera chega junto com a peça que entra por cima — sobe `valor` em SOBE s
    # (ease-out cúbico) e volta até t1 (cosseno). Multiplica o zoom: vale dentro de qualquer cena.
    emp = "".join(
        f"+{e['valor']}*(1-pow(1-clip(({t}-{e['t0']:.3f})/{SOBE},0,1),3))"
        f"*(1+cos(PI*clip(({t}-{e['t0'] + SOBE:.3f})/{max(e['t1'] - e['t0'] - SOBE, .001):.3f},0,1)))/2"
        for e in ef if e["efeito"] == "empurra")
    Z = f"({folga}*{z}*(1{emp}))"
    # perspective, não zoompan: o zoompan arredonda a janela pro pixel, e mesmo com o scale 2× de
    # antes o passo do zoom lento oscilava 0,48 px; o perspective amostra em ponto flutuante
    # (0,06 px, medido em 03/10) e sai um pouco mais barato que o scale 2× + zoompan.
    hw, hh = f"(W/2/{Z})", f"(H/2/{Z})"
    centro = f"clip(W/2-({dx})*{_k_janela(em, em + dur, t=t)}*W/({Z}*{W}),{hw},W-{hw})"
    geo = (f"perspective=x0='{centro}-{hw}':y0='H/2-{hh}':x1='{centro}+{hw}':y1='H/2-{hh}':"
           f"x2='{centro}-{hw}':y2='H/2+{hh}':x3='{centro}+{hw}':y3='H/2+{hh}':interpolation=cubic:eval=frame,"
           f"scale={W}:{H}:flags=lanczos")

    cor = []
    pb, ds = um("pb"), um("dessatura")
    if pb:
        cor.append(f"hue=s=0:enable='between(t,{pb['t0']:.3f},{pb['t1']:.3f})'")
    if ds:
        k = f"clip((t-{ds['t0']:.3f})/{ds.get('entra', .5)},0,1)"
        cor.append(f"hue=s='if(between(t,{ds['t0']:.3f},{ds['t1']:.3f}),1-{ds['valor']}*{k},1)'")
    cg = um("congela")
    cong = (f"[{{i}}a][{{i}}b]freezeframes=first={int(cg['t0'] * fps)}:last={int(cg['t1'] * fps)}:replace={int(cg['t0'] * fps)}"
            if cg else None)

    def cadeia(entrada: str, nome: str, alfa: bool) -> list[str]:
        # Congela ANTES da geometria: congelar depois prende o deslize no meio —
        # a pessoa parava a 1/4 do caminho (medido: 612px de 1033). A taxa vem
        # primeiro porque o freezeframes conta quadro, e o take pode vir a 25.
        fonte = fontes[1] if alfa else fontes[0]
        pre = f"[{entrada}]{'format=yuva444p,' if alfa else ''}{ff.taxa(fonte, fps, alfa=nome if alfa else '')}"
        if cong:
            f = [f"{pre},split[{nome}a][{nome}b]", cong.format(i=nome) + f"[{nome}c]"]
        else:
            f = [f"{pre}[{nome}c]"]
        return f + [f"[{nome}c]{geo}{(',' + ','.join(cor)) if cor else ''}[{nome}]"]

    fs = cadeia("0:v", "base", False)
    df = um("desfoca")
    if df:
        k = (f"min(clip((T-{df['t0']:.3f})/{df.get('entra', .5)},0,1),"
             f"clip(({df['t1']:.3f}-T)/{df.get('sai', .5) or .001},0,1))")
        fs += [f"[base]split[bs][bb]", f"[bb]gblur=sigma={df['px'] / 2:.2f}[bz]",
               f"[bs][bz]blend=all_expr='A+(B-A)*{k}'[base]"]
    atraso = f"setpts=PTS-STARTPTS+{em:.3f}/TB"
    janela = f"enable='between(t,{em:.3f},{em + dur:.3f})'"
    fs += [f"[1:v]{atraso}[tras]", f"[base][tras]overlay=0:0:{janela}:eof_action=pass[v1]"]
    ult = "v1"
    c = _cartao(meta)
    if c:
        # Tela dividida: o take reduzido cai no cartão de cantos redondos, por cima
        # do painel (tras). A pessoa, se veio, só entra ACIMA do cartão: é a cabeça
        # que passa da borda. Dentro dele o recorte seria o mesmo pixel do take.
        # [a, b): no quadro do corte o cartão já saiu (between() fecha nos dois lados).
        # O 1 ms é o t do quadro, que chega como 13.79999 e deixava o cartão um quadro a mais.
        on = "+".join(f"gte(t,{a + em - .001:.3f})*lt(t,{b + em - .001:.3f})" for a, b in c["trechos"])
        s, cx = c["escala"], f"(iw-{W})/2+{int(c['x'])}"
        red = f"scale=trunc(iw*{s}/2)*2:trunc(ih*{s}/2)*2:flags=lanczos"
        fs += [f"[0:v]{ff.taxa(fontes[0], fps)},{red},crop={int(c['w'])}:{int(c['h'])}:{cx}:{int(c['y'] - c['topo'])},format=yuva444p[ct0]",
               f"[{i_mascara}:v]format=gray[cm]", "[ct0][cm]alphamerge[ct]",
               f"[v1][ct]overlay={int(c['x'])}:{int(c['y'])}:enable='{on}'[v2]"]
        ult = "v2"
        if com_pessoa:
            alto = int(c["y"] - max(c["topo"], 0)) + 6
            fs += [f"[3:v]format=yuva444p,{ff.taxa(fontes[1], fps, alfa='pp')},{red},crop={int(c['w'])}:{alto}:{cx}:{int(max(-c['topo'], 0))}[pp]",
                   f"[v2][pp]overlay={int(c['x'])}:{int(max(c['topo'], 0))}:enable='{on}'[v3]"]
            ult = "v3"
    elif com_pessoa:
        fs += cadeia("3:v", "pes", True)
        fs += [f"[v1][pes]overlay=0:0:format=auto[v2]"]
        ult = "v2"
    fs += [f"[2:v]{atraso}[fr]", f"[{ult}][fr]overlay=0:0:{janela}:eof_action=pass,format={ff.PIX_FMT}[vout]"]
    return ";".join(fs), "vout"


def cmd_compor(a):
    meta = json.loads(Path(a.peca).read_text(encoding="utf-8"))
    cam = meta.get("camadas") or sys.exit("o JSON não tem camadas — gere com `v2.py camadas`")
    W, H = (int(x) for x in meta["formato"].split("x"))
    cmd = ["ffmpeg", "-y", "-i", a.take, "-i", cam["tras"], "-i", cam["frente"]]
    if a.pessoa:
        cmd += ["-i", a.pessoa]
    c, i_masc = _cartao(meta), None
    if c:
        i_masc = 4 if a.pessoa else 3
        masc = mascara_cartao(c, Path(tempfile.mkdtemp(prefix="v2_cartao_")) / "cartao.png")
        # a máscara em laço não acaba sozinha: sem o -t, o overlay seguia depois do take
        cmd += ["-loop", "1", "-framerate", str(meta.get("fps", 30)), "-t", f"{ff.dur(a.take):.3f}", "-i", str(masc)]
    fontes = (ff.probe(a.take).fps, ff.probe(a.pessoa).fps if a.pessoa else 0)
    g, saida = grafo(meta, a.em, W, H, a.folga, bool(a.pessoa), i_masc, fontes)
    # crf 17: o composto é fonte de outro passo (legenda, junta), não o final
    cmd += ["-filter_complex", g, "-map", f"[{saida}]", "-map", "0:a?", "-c:a", "copy",
            "-c:v", ff.CODEC_VIDEO, "-crf", "17", "-pix_fmt", ff.PIX_FMT, a.out]
    if a.seco:
        with ff.seco() as cmds:
            ff.run(cmd)
        print(" \\\n  ".join(cmds[0]))
        return
    ff.run(cmd)
    cues = [{**c, "t": round(c["t"] + a.em, 3)} for c in meta.get("cues", [])]
    Path(a.out).with_suffix(".cues.json").write_text(json.dumps({"cues": cues}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {a.out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("lista"); s.add_argument("--familia"); s.add_argument("--formato"); s.add_argument("--camadas", action="store_true"); s.set_defaults(f=cmd_lista)
    s = sub.add_parser("info"); s.add_argument("peca"); s.set_defaults(f=cmd_info)
    s = sub.add_parser("catalogo"); s.set_defaults(f=cmd_catalogo)
    s = sub.add_parser("qa"); s.add_argument("pecas", nargs="*"); s.add_argument("--familia"); s.add_argument("--json")
    s.add_argument("--notas", action="store_true", help="mostra também as notas (não contam como problema)"); s.set_defaults(f=cmd_qa)
    for nome, fn in (("render", cmd_render), ("camadas", cmd_camadas)):
        s = sub.add_parser(nome); s.add_argument("peca"); s.add_argument("pares", nargs="*")
        s.add_argument("--out", required=nome == "camadas"); s.add_argument("--ar"); s.add_argument("--tema", choices=["claro", "tinta", "tinteiro", "marca"])
        s.add_argument("--fps", type=int, default=30)
        if nome == "render":
            s.add_argument("--camada", choices=["tras", "frente"]); s.add_argument("--opaco", action="store_true")
            s.add_argument("--rastro", action="store_true", help="motion blur nas entradas rápidas (~5× o tempo)")
        s.set_defaults(f=fn)
    s = sub.add_parser("compor"); s.add_argument("--take", required=True); s.add_argument("--peca", required=True)
    s.add_argument("--em", type=float, required=True); s.add_argument("--out", required=True); s.add_argument("--pessoa")
    s.add_argument("--folga", type=float, default=1.25, help="quanto o take aberto é ampliado pra ter onde deslizar")
    s.add_argument("--seco", action="store_true", help="só imprime o comando do ffmpeg"); s.set_defaults(f=cmd_compor)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
