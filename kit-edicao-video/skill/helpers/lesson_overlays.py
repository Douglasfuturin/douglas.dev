"""Composite HyperFrames explainer overlays onto a finished lesson.

Reads an overlays list (each anchored at a SOURCE time) + the lesson EDL, renders each scene
via hyperframes, and either CORTA (forma de conceito, opaca, toma a tela) ou sobrepõe por
chroma-key (forma de apoio). Reproducible, driven from lessons.json "overlays".

CONTRATO DE DIREÇÃO  (seed a2835cf1 · escolha do dono: "Zine à Mão", invertido pra quadro-negro)
  THESIS       O card é uma página do caderno dele, não um componente de interface. Tudo é
               desenhado à mão e vai aparecendo enquanto ele fala. Recusa a caixa escura de
               canto arredondado com borda accent que todo tutorial de tecnologia entrega —
               e recusa o traço neon vazado sobre preto, que é o oposto previsível dela.
  OWN-WORLD    Quadro negro #0d0a08, giz claro #e9e9e9. Letra de marcador (Excalifont) em TUDO;
               mono só dentro de comando e nome de arquivo. Paleta fechada, herdada do
               video-de-quadro: laranja=tópico, magenta=o nome da coisa, amarelo=a virada
               (é o marca-texto), vermelho=custo/erro/descartado. Nunca mais de três cores na
               mesma tela. Nada de caixa: o que agrupa é oval de duas passadas e fio torto.
  STORY        O aluno ouve o jargão, vê a coisa ser desenhada, e o marca-texto acende a única
               linha que ele tem que levar. Fecha no mudo.
  FIRST VIEWPORT  Quadro vazio. O primeiro elemento entra sozinho e fica; os outros vão
               chegando um por um no ritmo da fala, acumulando na mesma cena — nunca tudo de
               uma vez. Uma coisa por card leva marca-texto amarelo; só uma.
  FORM         "Zine técnico à mão" (desafiante, escolhido pelo dono contra o índice sorteado
               4 = Placa Esmaltada), invertido pra quadro-negro e unificado com o
               video-de-quadro por decisão do dono. Seed a2835cf1.
  FINISH       unreviewed and undocumented is unfinished; this build ends with the finish
               review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

  Coral #da7756 (travado pelo dono, liga card ↔ capa ↔ deck) NÃO entra na paleta de desenho:
  isso quebraria a paleta fechada do video-de-quadro, que já está no ar. Ele vive só na tarja
  de capítulo, no canto — o único elemento que o card tem e o quadro não.

CATÁLOGO DE FORMAS (o `scene`). Escolher a forma pelo que a fala está fazendo:
  term     — o aluno ouviu um jargão            {"term": "MCP", "def": "o jeito padrão ..."}
  hub      — um ponto central liga a muitos      {"cap_ch","from_lb","to_lb","items":[...],"cap"}
  stepper  — ordem importa, N passos             {"steps": [...], "cap", "h"}
  compare  — antes/depois, A vs B                {"h": "...", "left": {...}, "right": {...}, "main"}
  rows     — lista sem ordem (regras, o que faz) {"h": "...", "items": [...], "cap"}
  stat     — um número carrega a frase           {"n": "20 dias", "sub": "..."}
  quote    — a frase dele vale mais que o card   {"q": "...", "by": "..."}

Params comuns: `size` ("1920x1080" padrão, "1080x1920" pra reel), `bg` (só pra forçar), e
`mark` (índice/texto do que leva o marca-texto amarelo — um por card).

CORTE vs CHROMA, decidido pela forma (não pelo item):
  CUT    = hub stepper compare stat quote   → opaco, toma a tela inteira, corte seco
  CHROMA = term rows                        → por cima da gravação, recortado no magenta

Overlay item (em lessons.json, por aula):
  {"at": <source sec>, "dur": 5.0, "scene": "<forma>", ...params}

Usage: python lesson_overlays.py <lesson.mp4> <edl.json> <overlays.json> -o <out.mp4> [--intro 0.4]
       python lesson_overlays.py --selftest   # confere as formas (estrutura), /tmp/overlay_*.html
       python lesson_overlays.py --shots      # PNG de cada forma nos dois canvas -> /tmp/formas/
"""
import argparse, base64, json, math, shutil, subprocess, sys, tempfile
from pathlib import Path

import ff

HELP = Path(__file__).resolve().parent
# Relativo ao helper: caminho absoluto de pasta de trabalho vaza no kit que vai pro
# aluno e quebra na máquina dele.
SCAFFOLD = HELP.parent / "assets" / "scaffold"
FONTS = HELP.parent.parent / "quadro" / "public" / "fonts"

# Paleta fechada do canal. A fonte de verdade é `tools/quadro/mundo.json` — o mesmo arquivo que
# o `src/tipos.ts` do quadro lê. Copiar valor de cor pra cá foi erro; a cópia sobrevive até
# alguém mexer num dos dois lados e ninguém perceber. Não existe verde, e nunca mais de três
# cores na mesma tela (`maxCoresPorTela`).
MUNDO = HELP.parent.parent / "quadro" / "mundo.json"
try:
    _M = json.loads(MUNDO.read_text(encoding="utf-8"))
except (OSError, ValueError) as e:
    sys.exit(f"paleta não encontrada em {MUNDO}: {e}\n"
             "É a fonte de verdade compartilhada com o video-de-quadro; sem ela o card não sai.")
INK, CINZA = _M["ink"], _M["cinza"]
LARANJA, MAGENTA, AMARELO, VERMELHO = _M["laranja"], _M["magenta"], _M["amarelo"], _M["vermelho"]
# O dono aprovou convergir os dois formatos pro preto quente (11/09): `#0d0a08` produz 25,0
# depois do reencode do YouTube, o mesmo valor medido no LABS e no KodeKloud. O quadro vai
# colapsar `fundo` e `fundoQuente` num campo só — ler os dois nesta ordem evita quebrar no
# minuto em que ele fizer isso, seja qual for o nome que sobrar.
QUADRO = _M.get("fundoQuente") or _M["fundo"]
CORAL = _M["coral"]      # só a tarja de capítulo. Fora dela, nunca.
MAX_CORES = _M.get("maxCoresPorTela", 3)

CUT = {"hub", "stepper", "compare", "stat", "quote"}       # opaco, corta a gravação
CHROMA = {"term", "rows"}                                   # recortado, entra por cima


def _font_face():
    """Letra de marcador embutida em base64: o render roda em pasta temporária e offline, então
    caminho relativo não resolve e Google Fonts não é opção.

    A Excalifont vem em SETE subconjuntos por unicode-range e nenhum deles traz o alfabeto
    inteiro. Sem o unicode-range original, declarar os sete com o mesmo family faz o último
    ganhar e os outros sumirem — foi assim que o primeiro render saiu em Apple Chancery.
    Então cada subconjunto vira um family numerado e a cascata do CSS resolve glifo a glifo;
    a Virgil, que é arquivo único e completo, fecha a fila."""
    faces, fams = [], []
    files = sorted(FONTS.glob("Excalifont-Regular-*.woff2"), key=lambda f: -f.stat().st_size)
    for i, f in enumerate(files):
        try:
            b64 = base64.b64encode(f.read_bytes()).decode()
        except OSError:
            continue
        fams.append(f"'Excalifont{i}'")
        faces.append(f"@font-face{{font-family:'Excalifont{i}';font-display:block;"
                     f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    v = FONTS / "Virgil-Regular.woff2"
    if v.exists():
        fams.append("'Virgil'")
        faces.append("@font-face{font-family:'Virgil';font-display:block;src:url(data:font/woff2;"
                     f"base64,{base64.b64encode(v.read_bytes()).decode()}) format('woff2')}}")
    if not fams:
        # Sem a fonte o card ainda renderiza, mas na letra do sistema — o contrário do mundo.
        print("  aviso: letra de marcador não encontrada em tools/quadro/public/fonts/", file=sys.stderr)
        return "", "cursive"
    return "".join(faces), ",".join(fams) + ",cursive"


def _wobble(x1, y1, x2, y2, amp=3.4, seg=7, seed=0):
    """Fio torto: a reta que uma mão desenha. Determinístico (o render tem que repetir)."""
    dx, dy = x2 - x1, y2 - y1
    ln = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / ln, dx / ln
    pts = []
    for i in range(seg + 1):
        t = i / seg
        k = math.sin(t * 5.3 + seed * 2.1) * math.sin(t * 2.7 + seed) * amp * (1 - abs(2 * t - 1) * 0.35)
        pts.append(f"{x1 + dx * t + nx * k:.1f},{y1 + dy * t + ny * k:.1f}")
    return "M" + " L".join(pts)


def rule(w, seed=0, color=None, thick=3):
    """Fio torto horizontal — o que separa no lugar da borda de 1px."""
    c = color or "#3a322c"
    return (f'<svg class="draw rule" width="{w}" height="14" viewBox="0 0 {w} 14" preserveAspectRatio="none">'
            f'<path d="{_wobble(2, 7, w - 2, 7, 2.6, 9, seed)}" pathLength="1" '
            f'style="stroke:{c};stroke-width:{thick}"/></svg>')


def oval(seed=0, color=None):
    """`circula` do vocabulário: oval de DUAS passadas, como quem circula no quadro.
    Uma passada só lê como borda de caixa, que é exatamente o que o mundo recusa.

    A volta é amostrada num círculo com raio irregular e fecha sozinha — a primeira versão
    montava quatro curvas Bézier na mão e não fechava em cima, então saía um par de riscos
    soltos no lugar da oval."""
    c = color or LARANJA
    cx, cy, rx, ry = 151, 50, 146, 46
    paths = []
    for k in range(2):
        # a segunda passada começa deslocada e passa um pouco da volta, como mão que repassa
        a0 = -2.5 + k * 0.9
        pts = []
        n = 34
        for i in range(n + 1):
            a = a0 + (i / n) * (6.35 + k * 0.22)
            j = 1 + math.sin(a * 3.1 + seed + k * 2.3) * 0.028 + math.sin(a * 1.7 + k) * 0.02
            pts.append(f"{cx + math.cos(a) * rx * j:.1f},{cy + math.sin(a) * ry * j:.1f}")
        paths.append(f'<path d="M{" L".join(pts)}" pathLength="1" '
                     f'style="stroke:{c};stroke-width:{3.2 - k * 0.9:.1f};opacity:{0.95 - k * 0.3:.2f}"/>')
    return ('<svg class="draw oval" viewBox="0 0 302 100" preserveAspectRatio="none">'
            + "".join(paths) + "</svg>")


def squiggle(w, seed=0, color=None):
    """`sublinha`: sublinhado ondulado embaixo da palavra."""
    c = color or MAGENTA
    pts = [f"{2 + i * (w - 4) / 12:.1f},{8 + math.sin(i * 1.5 + seed) * 5:.1f}" for i in range(13)]
    return (f'<svg class="draw" width="{w}" height="18" viewBox="0 0 {w} 18" preserveAspectRatio="none">'
            f'<path d="M{" L".join(pts)}" pathLength="1" style="stroke:{c};stroke-width:3.5"/></svg>')


def strike(w, seed=0):
    """`linha` vermelha: o que foi descartado leva risco."""
    return (f'<svg class="draw strike" width="{w}" height="12" viewBox="0 0 {w} 12" preserveAspectRatio="none">'
            f'<path d="{_wobble(1, 6, w - 1, 6, 2.0, 6, seed)}" pathLength="1" '
            f'style="stroke:{VERMELHO};stroke-width:3.5"/></svg>')


def arrow(port, length=130, seed=0, color=None):
    """`aponta`: a seta torta, com farpa. Sempre no sentido da leitura."""
    c = color or CINZA
    st = f"stroke:{c};stroke-width:3.2"
    if port:
        return (f'<svg class="draw" width="46" height="{length}" viewBox="0 0 46 {length}">'
                f'<path d="{_wobble(23, 2, 23, length - 2, 3.0, 6, seed)}" pathLength="1" style="{st}"/>'
                f'<path d="M14,{length - 15} L23,{length - 1} L32,{length - 15}" pathLength="1" style="{st}"/></svg>')
    return (f'<svg class="draw" width="{length}" height="46" viewBox="0 0 {length} 46">'
            f'<path d="{_wobble(2, 23, length - 2, 23, 3.0, 6, seed)}" pathLength="1" style="{st}"/>'
            f'<path d="M{length - 15},14 L{length - 1},23 L{length - 15},32" pathLength="1" style="{st}"/></svg>')


def circled(n, seed=0):
    """Número do passo dentro de um círculo desenhado — não medalha preenchida."""
    p = []
    for k in range(2):
        r = 30 - k * 1.4
        d = (f"M{34 - r:.1f},34 C{34 - r:.1f},{34 - r * 0.75:.1f} {34 - r * 0.72:.1f},{34 - r:.1f} 34,{34 - r:.1f} "
             f"C{34 + r * 0.74:.1f},{34 - r:.1f} {34 + r:.1f},{34 - r * 0.7:.1f} {34 + r:.1f},34 "
             f"C{34 + r:.1f},{34 + r * 0.76:.1f} {34 + r * 0.7:.1f},{34 + r:.1f} 34,{34 + r:.1f} "
             f"C{34 - r * 0.75:.1f},{34 + r:.1f} {34 - r:.1f},{34 + r * 0.72:.1f} {34 - r:.1f},34")
        p.append(f'<path d="{d}" pathLength="1" style="stroke:{LARANJA};stroke-width:{3 - k * 0.7:.1f};'
                 f'opacity:{0.95 - k * 0.3:.2f}"/>')
    return (f'<span class="num"><svg class="draw" width="68" height="68" viewBox="0 0 68 68">'
            f'{"".join(p)}</svg><i>{n}</i></span>')


HEAD = """<!doctype html><html lang="pt-BR"><head><meta charset="UTF-8"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
__FONT__
/* Regras do mundo — o que separa página de caderno de slide:
   1. Nada de caixa. O que agrupa é oval de duas passadas e fio torto.
   2. Letra de marcador em tudo; mono só dentro de comando e nome de arquivo.
   3. Paleta fechada e no máximo três cores por tela. Cor é semântica, nunca decoração.
   4. Um marca-texto amarelo por card — a única linha que o aluno tem que levar.
   5. A cena ACUMULA: um elemento por vez, no ritmo da fala. Nunca tudo junto.
   6. Zero emoji, zero sobrancelha acima do título: o título fala por si. */
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:__W__px;height:__H__px;overflow:hidden;background:#ff00ff;font-family:__FAM__}
#root{position:relative;width:__W__px;height:__H__px;background:__BG__;color:__INK__;
 font-family:__FAM__}
.panel{position:absolute;inset:0;padding:150px 112px 104px;display:flex;flex-direction:column;
 justify-content:center;gap:52px}
/* tarja de capítulo: marcador de página no canto, não sobrancelha colada no título */
.chap{position:absolute;top:54px;left:56px;background:__CORAL__;color:#fff7f2;
 padding:7px 22px 11px;font-size:40px;line-height:1;transform:rotate(-.8deg)}
.title{font-size:132px;line-height:1.04;max-width:94%}
.title .c{color:__MAGENTA__}
.lede{font-size:52px;line-height:1.26;color:__CINZA__;max-width:82%}
code,.mono{font-family:ui-monospace,Menlo,monospace;font-size:.86em;color:__LARANJA__}
/* traço: desenha por dashoffset (pathLength=1 evita medir o path em JS) */
svg.draw path{fill:none;stroke:__CINZA__;stroke-dasharray:1;stroke-dashoffset:1;
 stroke-linecap:round;stroke-linejoin:round;vector-effect:non-scaling-stroke}
svg.rule{display:block}
svg.oval{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;overflow:visible}
svg.strike{position:absolute;left:0;right:0;top:52%}
/* marca-texto: a virada. Rabisco atrás da palavra, nunca retângulo perfeito. */
.mark{position:relative;display:inline;padding:0 .12em;color:#1a1410}
.mark::before{content:"";position:absolute;left:-.06em;right:-.06em;top:.04em;bottom:.02em;
 background:__AMARELO__;z-index:-1;transform:rotate(-.5deg) skewX(-2deg);
 clip-path:polygon(0 6%,100% 0,100% 94%,1% 100%)}
/* hub: origem · nó · leque */
.diagram{display:flex;align-items:center}
.node{position:relative;font-size:64px;line-height:1.1;padding:20px 34px}
.node .sub{font-size:30px;color:__CINZA__;margin-top:10px}
.leaves{display:flex;flex-direction:column;justify-content:space-around}
.leaf{font-size:42px;color:__INK__;white-space:nowrap}
/* passos */
.steps{display:flex;align-items:flex-start}
.step{flex:1;padding-right:30px}
.step .t{font-size:52px;margin-top:18px;line-height:1.2}
.num{position:relative;display:inline-block;width:68px;height:68px}
.num i{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
 font-style:normal;font-size:36px;color:__LARANJA__}
/* comparação: fio torto vertical no lugar de duas caixas */
.cols{display:flex;gap:64px;align-items:stretch}
.col{flex:1;position:relative}
.col h4{font-size:46px;color:__CINZA__;margin-bottom:34px;font-weight:400}
.col.on h4{color:__LARANJA__}
.col li{list-style:none;font-size:52px;line-height:1.26;color:__CINZA__;position:relative;
 padding:6px 0;margin-bottom:20px}
.col.on li{color:__INK__}
.col.off li{color:#6e645c}
.vrule{width:14px;flex:0 0 14px;align-self:stretch}
.vrule svg{width:100%;height:100%;display:block}
/* lista: fio torto separa, caixa não */
.list{display:flex;flex-direction:column}
.item{font-size:58px;line-height:1.18;padding:26px 0 6px}
.plate{position:absolute;left:70px;right:70px;bottom:112px;background:__QUADRO__;padding:40px 54px 46px}
/* número: o dominante do quadro. Folga generosa pra oval caber em volta, não em cima. */
.stat{position:relative;display:inline-block;font-size:280px;line-height:1.05;color:__INK__;
 align-self:flex-start;padding:34px 76px}
/* citação */
.quote{font-size:92px;line-height:1.18;max-width:94%}
.by{font-size:38px;color:__CINZA__}
/* Sublinhado ondulado. Duas armadilhas, as duas já pagas:
   1. com preserveAspectRatio padrão o traço encolhia junto com a largura e virava um fio;
   2. pendurado ABAIXO da caixa ele era cortado pelo clip-path da escrita — agora mora
      dentro da caixa, num respiro reservado, e aparece junto com a palavra. */
.u{position:relative;display:inline-block;padding-bottom:.24em}
.u svg{position:absolute;left:0;bottom:.02em;width:100%;height:.18em}
/* retrato (reel 9:16): 1920px de largura não cabem em 1080 */
@media (max-aspect-ratio:1/1){
 .panel{padding:130px 62px 96px;gap:40px}
 .chap{top:44px;left:40px;font-size:34px}
 .title{font-size:96px;max-width:100%}.lede{font-size:44px;max-width:100%}
 /* `quote` e `stat` são as duas formas de pouco conteúdo: no quadro deitado elas preenchem,
    no quadro em pé sobrava cerca de um terço sem nada. Aqui elas tomam a altura que existe,
    em vez de ficar do tamanho que tinham no 16:9. */
 .stat{font-size:290px;padding:36px 56px}.quote{font-size:104px}.item{font-size:50px}
 .cols{flex-direction:column;gap:34px}.vrule{width:auto;height:14px;flex:0 0 14px}
 .steps{flex-direction:column;gap:22px}.step{padding-right:0}
 .node{font-size:54px}.leaf{font-size:36px}.col li{font-size:46px}.col h4{font-size:40px}
 .step .t{font-size:46px}
 .plate{left:46px;right:46px;bottom:150px;padding:32px 40px 38px}
}
</style></head><body>
"""
FOOT = "\n</body></html>\n"


def comp(inner, tl_js, dur, p=None, scene=None):
    """Monta o HTML da cena. `size` vem do item; o fundo vem da FORMA (corte é opaco)."""
    p = p or {}
    w, h = wh(p)
    bg = p.get("bg") or (QUADRO if scene in CUT else "#ff00ff")
    faces, fams = _font_face()
    head = HEAD
    for k, v in (("__FONT__", faces), ("__FAM__", fams), ("__W__", str(w)), ("__H__", str(h)), ("__BG__", bg),
                 ("__INK__", INK), ("__CINZA__", CINZA), ("__LARANJA__", LARANJA),
                 ("__MAGENTA__", MAGENTA), ("__AMARELO__", AMARELO), ("__CORAL__", CORAL),
                 ("__QUADRO__", QUADRO)):
        head = head.replace(k, v)
    return (head +
            f'<div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="{w}" data-height="{h}">\n'
            + inner +
            '\n</div>\n<script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});\n'
            # Motion do mundo: o traço é DESENHADO e a letra é ESCRITA (revelação por máscara
            # da esquerda pra direita). Um só gesto, repetido — não um efeito por elemento.
            'function escreve(sel,at,d){tl.fromTo(sel,{clipPath:"inset(0 100% 0 0)"},'
            '{clipPath:"inset(0 -4% 0 0)",duration:d||0.42,ease:"power2.out"},at);}\n'
            + tl_js + '\nwindow.__timelines["main"]=tl;</script>' + FOOT)


def wh(p):
    return (int(x) for x in str(p.get("size", "1920x1080")).lower().split("x"))


def _clean(s):
    """Rótulo dos planos antigos vem com emoji na frente ("📸 Instagram") — tira."""
    return "".join(c for c in str(s) if ord(c) < 0x2190).strip(" ·-—").strip()


def _chap(p):
    """`eyebrow`/`header` dos planos já escritos vira TARJA DE CAPÍTULO no canto.
    Não volta como sobrancelha colada no título: o título fala por si."""
    t = p.get("cap_ch") or p.get("eyebrow") or p.get("header")
    return (f'<div class="chap" id="ch">{t}</div>', 'tl.from("#ch",{opacity:0,rotate:-6,duration:0.3},0);') if t else ("", "")


def _title(p, at=0.35):
    if not p.get("h"):
        return "", ""
    return f'<div class="title" id="ti">{p["h"]}</div>', f'escreve("#ti",{at:.2f},0.5);'


def _marca(txt, on):
    """Envolve no marca-texto amarelo se este for O item marcado. Um por card."""
    return f'<span class="mark">{txt}</span>' if on else txt


def _is_mark(p, i, txt):
    m = p.get("mark")
    return m is not None and (m == i or (isinstance(m, str) and m.strip().lower() == str(txt).strip().lower()))


def html_hub(p, dur):
    """Um ponto central liga a muitos. Origem →seta→ nó →leque→ destinos, tudo desenhado.

    {"cap_ch": "...", "h": "...", "from_lb": "Claude Code", "to_lb": "Composio",
     "to_sub": "1 endpoint MCP", "items": ["Instagram", ...], "cap": "...", "mark": 0}
    """
    w, h = wh(p)
    port = h > w
    items = [i if isinstance(i, dict) else {"t": i} for i in p.get("items", [])]
    span = min(880, 210 * len(items)) if port else min(430, 108 * len(items))
    leaves = "".join(f'<div class="leaf">{_clean(i["t"])}</div>' for i in items)
    # O leque: um traço torto do nó até cada destino. Deitado ele sai da esquerda e abre pra
    # direita; em pé sai de cima e abre pra baixo — trocar os eixos joga o traço fora do viewBox.
    reach = 200
    bw, bh = (span, reach) if port else (reach, span)
    fan = []
    for i in range(len(items)):
        t = (i + 0.5) * span / max(1, len(items))
        x1, y1, x2, y2 = (span / 2, 0, t, reach) if port else (0, span / 2, reach, t)
        fan.append(f'<path d="{_wobble(x1, y1, x2, y2, 5.0, 8, i)}" pathLength="1" '
                   f'style="stroke:{CINZA};stroke-width:3"/>')
    fansvg = (f'<svg class="draw" width="{bw:.0f}" height="{bh:.0f}" '
              f'viewBox="0 0 {bw:.0f} {bh:.0f}">{"".join(fan)}</svg>')
    node_o = f'<div class="node" id="n1">{_clean(p.get("from_lb", ""))}</div>'
    sub = f'<div class="sub">{p["to_sub"]}</div>' if p.get("to_sub") else ""
    hub_lb = _clean(p.get("to_lb", ""))
    # O nó central já é destacado pela oval; o marca-texto só entra se o plano pedir, senão
    # todo hub sairia com amarelo e o "um por card" viraria decoração.
    node_h = (f'<div class="node" id="n2">{_marca(hub_lb, _is_mark(p, "hub", hub_lb))}'
              f'{sub}{oval(2, LARANJA)}</div>')
    ch, tl = _chap(p)
    ti, t2 = _title(p); tl += t2
    cap = f'<div class="lede" id="cap">{p["cap"]}</div>' if p.get("cap") else ""
    flow = "column" if port else "row"
    inner = (f'<div class="panel">{ch}{ti}'
             f'<div class="diagram" style="flex-direction:{flow};align-items:center;align-self:flex-start">'
             f'{node_o}{arrow(port, 150, 1)}{node_h}{fansvg}'
             f'<div class="leaves" style="{"height" if not port else "width"}:{span:.0f}px;'
             f'{"flex-direction:row" if port else ""}">{leaves}</div>'
             f'</div>{cap}</div>')
    # acumula: origem → seta → nó → oval → leque → folhas
    tl += ('escreve("#n1",0.9,0.4);'
           'tl.to(".diagram > svg.draw:first-of-type path",{strokeDashoffset:0,duration:0.4,stagger:0.08},1.3);'
           'escreve("#n2",1.7,0.4);'
           'tl.to(".node svg.oval path",{strokeDashoffset:0,duration:0.5,stagger:0.12},2.1);'
           'tl.to(".diagram > svg.draw:last-of-type path",{strokeDashoffset:0,duration:0.5,stagger:0.07},2.6);'
           'tl.from(".leaf",{opacity:0,x:16,duration:0.28,stagger:0.09},3.0);')
    if cap:
        tl += 'escreve("#cap",3.7,0.45);'
    return comp(inner, tl, dur, p, "hub")


def html_term(p, dur):
    """O aluno ouviu um jargão. Entra por cima da gravação (chroma), canto inferior esquerdo,
    livre da câmera. A definição mora no marca-texto: opaco, legível sobre qualquer imagem.

    {"term": "MCP", "def": "o jeito padrão do Claude falar com apps"}
    """
    inner = (f'<div class="plate">'
             f'<div class="title" id="tm" style="font-size:76px">'
             f'<span class="u">{p["term"]}{squiggle(360, 1, MAGENTA)}</span></div>'
             f'<div class="lede" id="df" style="color:{INK};margin-top:26px;max-width:100%">'
             f'<span class="mark">{p["def"]}</span></div></div>')
    tl = ('escreve("#tm",0.05,0.4);'
          'tl.to("#tm svg.draw path",{strokeDashoffset:0,duration:0.4},0.45);'
          'escreve("#df",0.62,0.5);')
    return comp(inner, tl, dur, p, "term")


def html_stepper(p, dur):
    """A ordem importa. Número circulado à mão, seta torta ligando, um passo por vez.

    {"h": "...", "steps": ["instala", "conecta", "usa"], "cap": "...", "mark": 2}
    """
    w, h = wh(p)
    port = h > w
    steps = p["steps"]
    cells = []
    for i, s in enumerate(steps):
        cells.append(f'<div class="step" id="st{i}">{circled(i + 1, i)}'
                     f'<div class="t">{_marca(s, _is_mark(p, i, s))}</div></div>')
        if i < len(steps) - 1:
            cells.append(arrow(port, 100 if port else 130, i + 2))
    ch, tl = _chap(p)
    ti, t2 = _title(p); tl += t2
    cap = f'<div class="lede" id="cap">{p["cap"]}</div>' if p.get("cap") else ""
    inner = (f'<div class="panel">{ch}{ti}'
             f'<div class="steps" style="align-items:{"flex-start" if port else "center"}">'
             f'{"".join(cells)}</div>{cap}</div>')
    for i in range(len(steps)):
        at = 0.95 + i * 0.62
        tl += f'tl.to("#st{i} svg.draw path",{{strokeDashoffset:0,duration:0.4,stagger:0.1}},{at:.2f});'
        tl += f'escreve("#st{i} .t",{at + 0.22:.2f},0.34);'
        if i < len(steps) - 1:
            tl += (f'tl.to(".steps > svg.draw:nth-of-type({i + 1}) path",'
                   f'{{strokeDashoffset:0,duration:0.3,stagger:0.06}},{at + 0.44:.2f});')
    if cap:
        tl += f'escreve("#cap",{0.95 + len(steps) * 0.62 + 0.2:.2f},0.45);'
    return comp(inner, tl, dur, p, "stepper")


def html_compare(p, dur):
    """Antes/depois. Fio torto vertical separa; o lado morto leva risco vermelho.

    {"h": "...", "left": {"h": "ANTES", "items": [...]}, "right": {...}, "main": "right"}
    """
    w, h = wh(p)
    port = h > w
    main = p.get("main", "right")

    def col(c, side):
        dead = side != main
        lis = "".join(
            f'<li id="{side}{i}">{_marca(x, _is_mark(p, f"{side}{i}", x))}'
            f'{strike(560, i) if dead else ""}</li>' for i, x in enumerate(c["items"]))
        return (f'<div class="col {"off" if dead else "on"}" id="c-{side}">'
                f'<h4>{c["h"]}</h4><ul>{lis}</ul></div>')

    ch, tl = _chap(p)
    ti, t2 = _title(p); tl += t2
    cap = f'<div class="lede" id="cap">{p["cap"]}</div>' if p.get("cap") else ""
    vr = (f'<div class="vrule">{rule(900, 5) if port else ""}</div>' if port else
          f'<div class="vrule"><svg class="draw" width="14" height="420" viewBox="0 0 14 420" '
          f'preserveAspectRatio="none"><path d="{_wobble(7, 4, 7, 416, 3.4, 9, 5)}" pathLength="1" '
          f'style="stroke:#3a322c;stroke-width:3"/></svg></div>')
    inner = (f'<div class="panel">{ch}{ti}<div class="cols">'
             f'{col(p["left"], "left")}{vr}{col(p["right"], "right")}</div>{cap}</div>')
    tl += ('escreve("#c-left h4",0.85,0.3);escreve("#c-right h4",1.0,0.3);'
           'tl.to(".vrule path",{strokeDashoffset:0,duration:0.5},1.1);'
           'tl.from(".col li",{opacity:0,x:-14,duration:0.3,stagger:0.14},1.3);'
           # o risco vem por último: primeiro o aluno lê, depois vê que morreu
           'tl.to(".col.off svg.strike path",{strokeDashoffset:0,duration:0.4,stagger:0.14},2.4);')
    if cap:
        tl += 'escreve("#cap",3.1,0.45);'
    return comp(inner, tl, dur, p, "compare")


def html_rows(p, dur):
    """Lista sem ordem — regras, o que faz. Entra por cima da gravação. Fio torto separa.

    {"h": "...", "items": [...], "cap": "...", "mark": 1}
    """
    w, h = wh(p)
    ch, tl = _chap(p)
    ti, t2 = _title(p); tl += t2
    wr = (w if h > w else w) - 224
    items = "".join(
        f'{rule(wr, i) if i else ""}<div class="item" id="rw{i}">'
        f'{_marca(x, _is_mark(p, i, x))}</div>' for i, x in enumerate(p["items"]))
    cap = f'<div class="lede" id="cap">{p["cap"]}</div>' if p.get("cap") else ""
    inner = f'<div class="panel">{ch}{ti}<div class="list">{items}</div>{cap}</div>'
    for i in range(len(p["items"])):
        at = 0.9 + i * 0.5
        if i:
            tl += f'tl.to(".list svg.rule:nth-of-type({i}) path",{{strokeDashoffset:0,duration:0.34}},{at - 0.16:.2f});'
        tl += f'escreve("#rw{i}",{at:.2f},0.36);'
    if cap:
        tl += f'escreve("#cap",{0.9 + len(p["items"]) * 0.5 + 0.2:.2f},0.45);'
    return comp(inner, tl, dur, p, "rows")


def html_stat(p, dur):
    """Um número carrega a frase. Ele domina o quadro e leva a oval de duas passadas.

    {"n": "20 dias", "sub": "esperando a aprovação do Facebook", "cap_ch": "O CUSTO"}
    """
    ch, tl = _chap(p)
    sub = f'<div class="lede" id="sub">{p["sub"]}</div>' if p.get("sub") else ""
    inner = (f'<div class="panel">{ch}'
             f'<div class="stat" id="big">{p["n"]}{oval(1, LARANJA)}</div>{sub}</div>')
    tl += ('escreve("#big",0.3,0.55);'
           'tl.to("#big svg.oval path",{strokeDashoffset:0,duration:0.6,stagger:0.14},0.95);')
    if sub:
        tl += 'escreve("#sub",1.5,0.45);'
    return comp(inner, tl, dur, p, "stat")


def html_quote(p, dur):
    """A frase dele vale mais que o desenho. Sublinhado ondulado no que importa.

    {"q": "...", "by": "...", "mark": "export"}
    """
    ch, tl = _chap(p)
    q = p["q"]
    m = p.get("mark")
    if isinstance(m, str) and m in q:
        q = q.replace(m, f'<span class="mark">{m}</span>', 1)
    by = f'<div class="by" id="by">— {p["by"]}</div>' if p.get("by") else ""
    inner = f'<div class="panel">{ch}<div class="quote" id="q">{q}</div>{by}</div>'
    tl += 'escreve("#q",0.25,0.75);'
    if by:
        tl += 'escreve("#by",1.15,0.35);'
    return comp(inner, tl, dur, p, "quote")


GEN = {"hub": html_hub, "term": html_term, "stepper": html_stepper,
       "compare": html_compare, "rows": html_rows, "stat": html_stat, "quote": html_quote}


def out_time(edl, src_t):
    """Map a SOURCE second to OUTPUT time. If the moment was cut (silence/drop), snap to the
    nearest kept range edge so the overlay still lands next to when it was spoken."""
    cum = 0.0; best = None
    for r in json.loads(Path(edl).read_text(encoding="utf-8"))["ranges"]:
        s, e = float(r["start"]), float(r["end"])
        if s <= src_t <= e:
            return round(cum + (src_t - s), 3)
        d, ot = (s - src_t, cum) if src_t < s else (src_t - e, cum + (e - s))
        if best is None or d < best[0]:
            best = (d, ot)
        cum += e - s
    return round(best[1], 3) if best else None


def render_scene(ov, tmp):
    d = tmp / f"hf_{ov['_i']}"
    d.mkdir()
    shutil.copy(SCAFFOLD / "package.json", d); shutil.copy(SCAFFOLD / "hyperframes.json", d)
    (d / "index.html").write_text(GEN[ov["scene"]](ov, ov.get("dur", 5.0)), encoding="utf-8")
    ff.run(["npm", "run", "render"], cwd=d, quiet=True)
    return max((d / "renders").glob("*.mp4"), key=lambda p: p.stat().st_mtime)


SAMPLES = {
    "term": {"term": "MCP", "def": "o jeito padrão do Claude falar com apps"},
    "hub": {"cap_ch": "Bloco 3", "h": 'um endpoint, <span class="c">~1000 apps</span>',
            "from_lb": "Claude Code", "to_lb": "Composio", "to_sub": "1 endpoint MCP",
            "items": ["Instagram", "Gmail", "YouTube", "Notion"],
            "cap": "zero OAuth na mão"},
    "stepper": {"cap_ch": "Do zero", "h": "três passos, nenhum no navegador", "mark": 2,
                "steps": ["instala a skill", "conecta a conta", "manda postar"]},
    "compare": {"cap_ch": "O que muda", "h": 'antes vs <span class="c">depois</span>', "main": "right",
                "left": {"h": "ANTES", "items": ["app no Facebook Dev", "esperar 20 dias"]},
                "right": {"h": "DEPOIS", "items": ["um endpoint MCP", "postou"]},
                "mark": "right1", "cap": "o trabalho sai do navegador e vai pro terminal"},
    # o `<code>` aqui não é enfeite da amostra: é o que prova que a regra "mono só dentro de
    # comando e nome de arquivo" tem mecanismo. Sem uma forma exercitando, o CSS era letra morta.
    "rows": {"cap_ch": "Skill", "h": "o que ela faz", "cap": "sem preset, sem menu", "mark": 1,
             "items": ["corta silêncio", "tira gaguejada",
                       "grava o corte em <code>edl.json</code>"]},
    "stat": {"cap_ch": "O custo", "n": "20 dias", "sub": "esperando a aprovação do Facebook"},
    "quote": {"q": "ninguém troca de plano por crédito. troca por export.", "by": "matheus",
              "mark": "export"},
}
EMOJI = range(0x1F300, 0x1FAFF)


def _strings(v, skip=("ic", "from_ic", "to_ic", "size", "bg", "main", "mark")):
    """Todo texto que o param carrega, pra conferir se a forma engoliu algum."""
    if isinstance(v, dict):
        return [s for k, x in v.items() if k not in skip for s in _strings(x, skip)]
    if isinstance(v, list):
        return [s for x in v for s in _strings(x, skip)]
    return [v] if isinstance(v, str) else []


def selftest():
    """Cada forma tem que render HTML válido nos dois canvas, com o texto dentro."""
    assert set(SAMPLES) == set(GEN), f"forma sem amostra: {set(GEN) ^ set(SAMPLES)}"
    assert CUT | CHROMA == set(GEN), "forma sem destino (corte ou chroma)"
    assert not (CUT & CHROMA), "forma em corte E chroma"
    for name, p in SAMPLES.items():
        for size in ("1920x1080", "1080x1920"):
            w, h = size.split("x")
            html = GEN[name]({**p, "size": size}, 4.0)
            assert f'data-width="{w}" data-height="{h}"' in html, f"{name}/{size}: canvas errado"
            assert f"width:{w}px;height:{h}px" in html, f"{name}/{size}: css fora do canvas"
            want = QUADRO if name in CUT else "#ff00ff"
            assert f"background:{want}" in html, f"{name}: fundo errado pro destino ({want})"
            assert 'data-duration="4.0"' in html and 'window.__timelines["main"]' in html, f"{name}: sem timeline"
            assert "tl.from" in html or "tl.to" in html or "escreve(" in html, f"{name}: cena sem animação"
            # o marca-texto e o sublinhado embrulham pedaço de frase em <span>; pro teste de
            # "a forma engoliu conteúdo?" o que importa é o texto, não a marcação
            import re
            nospan = lambda t: re.sub(r"</?span[^>]*>", "", t)
            flat = nospan(html)
            for s in _strings(p):
                assert nospan(s) in flat, f"{name}: perdeu '{s}'"
            assert "None" not in html.replace("None-", ""), f"{name}: vazou None no HTML"
            assert "max-aspect-ratio:1/1" in html, f"{name}: sem a regra de retrato (reel)"
            # guardas anti-slop do mundo escolhido
            assert not any(ord(c) in EMOJI for c in html), f"{name}: emoji no card — desenho é SVG"
            assert "border-radius" not in html, f"{name}: canto arredondado — o mundo não tem caixa"
            assert "box-shadow" not in html, f"{name}: sombra — o quadro é chapado"
            assert "text-align:center" not in html, f"{name}: centralizado — o desenho alinha à esquerda"
            # A letra tem que estar EMBUTIDA, não só nomeada: nomear e cair no fallback do
            # sistema foi o primeiro render, que saiu em Apple Chancery.
            assert "data:font/woff2;base64," in html, f"{name}: letra de marcador não embutiu"
            assert html.count("@font-face") >= 2, f"{name}: só um subconjunto — falta alfabeto"
            assert "linear-gradient" not in html, f"{name}: degradê — a paleta é chapada"
            # paleta fechada: fora dos valores do mundo, nenhuma cor nova entra
            allowed = {INK, CINZA, LARANJA, MAGENTA, AMARELO, VERMELHO, QUADRO, CORAL,
                       "#ff00ff", "#3a322c", "#1a1410", "#6e645c", "#fff7f2"}
            import re
            for c in set(re.findall(r"#[0-9A-Fa-f]{6}", html)):
                assert c.lower() in {a.lower() for a in allowed}, f"{name}: cor fora da paleta: {c}"
            # o marca-texto é UM por card (a virada), nunca uma decoração repetida
            assert html.count('class="mark"') <= 1, f"{name}: mais de um marca-texto"
            # Mesma regra pra oval: anotação que acumula tem que cair em lugares diferentes,
            # nunca empilhada. O quadro descobriu isso rendendo cinco `circula` no mesmo bloco —
            # no fim não se lia nenhum. Aqui o card morre em 5 s e o defeito não apareceria
            # sozinho; a guarda entra emprestada, antes de custar um render.
            assert html.count('class="draw oval"') <= 1, f"{name}: mais de uma oval — elas empilham"
        Path(f"/tmp/overlay_{name}.html").write_text(GEN[name](p, 4.0), encoding="utf-8")
    # "mono só dentro de comando e nome de arquivo" (OWN-WORLD) precisa de mecanismo, não só de
    # regra: pelo menos uma forma tem que exercitar o <code>, senão o CSS é letra morta.
    assert any("<code>" in GEN[n](p, 4.0) for n, p in SAMPLES.items()), \
        "nenhuma forma usa <code> — a regra do mono não tem mecanismo"
    print(f"ok — {len(GEN)} formas: {', '.join(sorted(GEN))}"
          f"\n  corte: {', '.join(sorted(CUT))}\n  chroma: {', '.join(sorted(CHROMA))}"
          f"\nprévia em /tmp/overlay_<forma>.html")


CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


class Camera:
    """Um browser vivo para tirar vários PNGs.

    Subir um Chrome por screenshot custa 2,9 s; com ele vivo, 31 ms. É 93×, e a
    diferença não é desenhar — é a partida do processo, a fonte e a biblioteca
    sendo carregadas de novo a cada quadro.

    A prova visual tira 14 PNGs e o auto-teste 28, então isto sai de 41 s e 81 s
    para poucos segundos. É ferramenta que se roda toda vez que se mexe num card.

    Cai de volta para o Chrome avulso se o playwright não estiver instalado: o
    kit do aluno não tem por que arrastar um browser inteiro.
    """

    def __init__(self):
        self._pw = self._browser = None
        try:
            from playwright.sync_api import sync_playwright
            self._pw = sync_playwright().start()
            self._browser = self._pw.chromium.launch()
        except Exception:
            pass

    def tira(self, html: Path, png: Path, largura: int, altura: int) -> None:
        if self._browser is None:
            subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                            f"--window-size={largura},{altura}",
                            f"--screenshot={png}", f"file://{html}"],
                           capture_output=True)
            return
        pg = self._browser.new_page(viewport={"width": largura, "height": altura})
        try:
            pg.goto(f"file://{html}")
            pg.wait_for_timeout(350)      # fonte e biblioteca
            pg.screenshot(path=str(png))
        finally:
            pg.close()

    def fecha(self) -> None:
        if self._browser is not None:
            self._browser.close()
            self._pw.stop()

    def __enter__(self): return self
    def __exit__(self, *_): self.fecha()


def shots(out=Path("/tmp/formas")):
    """Prova visual: um PNG por forma nos dois canvas. Asserção de string não vê layout
    estourado — o card só se confere com o olho. Não substitui o render do hyperframes.
    O chroma sai desenhado sobre o quadro, pra dar pra ver o card (no vídeo ele é recortado)."""
    out.mkdir(parents=True, exist_ok=True)
    with Camera() as cam:
        for name, p in SAMPLES.items():
            for size in ("1920x1080", "1080x1920"):
                w, h = size.split("x")
                html = GEN[name]({**p, "size": size, "bg": QUADRO}, 4.0)
                # o render segura o estado final; 0.99 evita o frame de entrada vazio
                html = html.replace('window.__timelines["main"]=tl;',
                                    'window.__timelines["main"]=tl;tl.progress(0.99);')
                f = out / f"{name}_{size}"
                f.with_suffix(".html").write_text(html, encoding="utf-8")
                cam.tira(f.with_suffix(".html"), Path(f"{f}.png"), int(w), int(h))
    print(f"{2 * len(GEN)} pngs -> {out}")


def _tinta(png):
    """Luma média do PNG. Serve pra comparar duas renderizações do mesmo card."""
    r = ff.run(["ffmpeg", "-v", "error", "-i", str(png), "-vf",
                "signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-",
                "-f", "null", "-"], capture=True, quiet=True, check=False)
    for ln in r.stdout.splitlines() + r.stderr.splitlines():
        if "YAVG=" in ln:
            return float(ln.split("YAVG=")[1].split()[0])
    return 0.0


def oculto(out=Path("/tmp/oculto")):
    """NÃO USE. Fica aqui documentado como beco sem saída, pra ninguém reconstruir igual.

    Objetivo: achar elemento que EXISTE no HTML e não chega em pixel — a classe de defeito que
    asserção de string não pega. A ideia era renderizar o quadro final duas vezes, uma normal e
    outra com recorte e transparência neutralizados, e acusar quando neutralizar acrescenta tinta.

    **Não funciona, e o motivo é aritmético.** A medida é a luma média do quadro inteiro. Um
    sublinhado de ~150x3,5 px num quadro de 1920x1080 acende 0,025% da área e move o YAVG em
    ~0,02 — dez vezes abaixo de qualquer limiar que não dispare com antialiasing. Traço fino
    some no denominador.

    Testado com três defeitos injetados de propósito (sublinhado pendurado fora da caixa;
    `clip-path` no título; `overflow:hidden` cortando o sublinhado): **nenhum disparou.** Um
    quarto teste mostrou que recorte declarado em folha de estilo nem chega a valer, porque o
    GSAP escreve `clip-path` inline e inline ganha.

    O que teria que ser, e é o caminho se alguém voltar aqui: medir POR ELEMENTO, não por
    quadro. Pegar o `getBoundingClientRect` de cada item pelo DOM, recortar o PNG naquela caixa
    e medir ali dentro. É o que o `checa_animacao.mjs` do video-de-quadro faz — ele reproduz a
    câmera e mede a opacidade mínima de cada item durante a janela em que está sendo desenhado.
    """
    print("--oculto está desativado: mede o quadro inteiro e não enxerga traço fino.\n"
          "Veja a docstring para o porquê e para o desenho certo.", file=sys.stderr)
    return
    out.mkdir(parents=True, exist_ok=True)
    ruim = []
    cam = Camera()
    for name, p in SAMPLES.items():
        for size in ("1920x1080", "1080x1920"):
            w, h = size.split("x")
            base = GEN[name]({**p, "size": size, "bg": QUADRO}, 4.0).replace(
                'window.__timelines["main"]=tl;', 'window.__timelines["main"]=tl;tl.progress(0.99);')
            # variante: sem recorte e sem transparência — o teto do que o card poderia mostrar
            livre = base.replace("</style>", "*{clip-path:none!important;opacity:1!important;"
                                             "overflow:visible!important}</style>")
            vals = []
            for tag, html in (("a", base), ("b", livre)):
                f = out / f"{name}_{size}_{tag}"
                f.with_suffix(".html").write_text(html, encoding="utf-8")
                cam.tira(f.with_suffix(".html"), Path(f"{f}.png"), int(w), int(h))
                vals.append(_tinta(f"{f}.png"))
            a, b = vals
            # 0,25 de YAVG é ~0,1% do quadro: menos que isso é antialiasing, não desenho sumido
            if b - a > 0.25:
                ruim.append((name, size, a, b))
    if ruim:
        print("ELEMENTO CORTADO — existe no HTML e não chega em pixel:")
        for n, s, a, b in ruim:
            print(f"  {n} {s}: tinta {a:.2f} -> {b:.2f} sem recorte  (+{b-a:.2f})")
        sys.exit(1)
    print(f"ok — {2 * len(GEN)} quadros, nenhum elemento cortado")


def main():
    if "--selftest" in sys.argv:
        return selftest()
    if "--shots" in sys.argv:
        return shots()
    if "--oculto" in sys.argv:
        return oculto()
    ap = argparse.ArgumentParser()
    ap.add_argument("lesson", type=Path); ap.add_argument("edl", type=Path)
    ap.add_argument("overlays", type=Path); ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--intro", type=float, default=0.4)   # CRT turn-on shifts output time
    args = ap.parse_args()

    _aula = ff.probe(args.lesson)
    W, H = _aula.largura, _aula.altura
    overlays = json.loads(args.overlays.read_text(encoding="utf-8"))
    placed = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for i, ov in enumerate(overlays):
            t = out_time(args.edl, ov["at"])
            if t is None:
                print(f"  skip overlay '{ov.get('scene')}' @src {ov['at']} (moment was cut)"); continue
            ov["_i"] = i
            mp4 = render_scene(ov, tmp)
            placed.append((t + args.intro, ov.get("dur", 5.0), mp4, ov["scene"]))
            print(f"  {'corte ' if ov['scene'] in CUT else 'chroma'} {ov['scene']} -> out {t+args.intro:.2f}s")
        if not placed:
            shutil.copy(args.lesson, args.output); return
        inputs = ["-i", str(args.lesson)]
        for _, _, m, _ in placed:
            inputs += ["-i", str(m)]
        fc = []; last = "0:v"
        for k, (T, dur, _, scene) in enumerate(placed, start=1):
            fo = max(0.1, dur - 0.5)
            if scene in CUT:
                # Corte seco: o card é opaco e TOMA a tela. Sem colorkey e sem fade — o mundo
                # não dissolve, ele vira a página. Fade aqui devolveria o card boiando.
                fc.append(f"[{k}:v]scale={W}:{H},format=yuva420p,setpts=PTS-STARTPTS+{T:.3f}/TB[o{k}]")
            else:
                fc.append(f"[{k}:v]scale={W}:{H},colorkey=0xff00ff:0.30:0.10,format=yuva420p,"
                          f"fade=t=in:st=0:d=0.3:alpha=1,fade=t=out:st={fo:.2f}:d=0.45:alpha=1,"
                          f"setpts=PTS-STARTPTS+{T:.3f}/TB[o{k}]")
            outl = f"v{k}"
            fc.append(f"[{last}][o{k}]overlay=eof_action=pass:enable='between(t,{T:.3f},{T+dur:.3f})'[{outl}]")
            last = outl
        run = ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", f"[{last}]", "-map", "0:a",
               *ff.args_video("reel", fps=None), "-c:a", "copy", str(args.output)]
        r = subprocess.run(run, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            sys.exit("overlay composite failed:\n" + r.stderr[-1000:])
    print(f"done -> {args.output}")


if __name__ == "__main__":
    main()
