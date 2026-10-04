#!/usr/bin/env python3
"""Um lote de cenas novas para o banco, gerado na Higgsfield. Estima antes de gastar.

    python lote.py <pasta>/lote.json          # só estima: diz o custo e para
    python lote.py <pasta>/lote.json --gera   # gera o que falta e baixa na pasta do lote
    python lote.py <pasta>/lote.json --gera --so t3-fundo   # só estas cenas (o teste antes do resto)

Pelo plano, quem chama é a fábrica: o criativo com `lote` para no passo que cobra enquanto
faltar cena do lote no disco, e mostra este comando com a estimativa. Quem decide gastar é você.

O lote (`lote.json`):
  estetica   o nome de uma estética do estetica.json (na pasta do lote ou na de cima). O prompt
             dela entra no fim de toda cena: o da cena fica só com a cena, a câmera e a
             composição. Lote sem estética usa o prompt como está
  rosto      as fotos do rosto que entra na cena, a partir da pasta do lote: duas (de frente e
             neutra), com fundo liso, senão o modelo copia o fundo pra cena. Só a cena `wan` usa
  duracao    segundos por cena (padrão: 4 no kling, 5 no wan)
  proporcao  "9:16" (padrão), "16:9", "1:1"…
  cenas      {"<id>": {"modelo": "kling" | "wan", "prompt": "…"}}. Para o criativo usar a cena
             assim que ela baixa, ela leva também a ficha do banco: `acabamento` (cctv,
             telejornal, documentario, filmadora, celular) e, se quiser, `janela`, `hora`, `cam`,
             `data` (a que a filmadora escreve, AAAA-MM-DD; sem ela, a do dia do render) e `ilustra`.
             A cena pode trocar a duração (`duracao`) e a resolução (`resolucao`) do lote

Kling 3.0 std, texto→vídeo, é a cena sem rosto conhecido. Wan 3.0 Prime, referência→vídeo, é a
cena com o rosto das fotos: o prompt dela diz que a pessoa é a das imagens e que delas só vale o
rosto. Os parâmetros são os que passaram na calibração do banco; a linguagem da cena está em
docs/linguagem-do-criativo.md.

Wan 2.7 imagem→vídeo com voz (`fala`) é a pessoa falando a voz que vai junto: a imagem inicial
(`imagem`) e o trecho da voz (`audio`, que o avatar_lote.py corta do `voz` [t0, t1] da cena) movem a
boca e o tempo da ação. A cena dura o trecho. É o avatar feito na Higgsfield (avatar_lote.py monta).
A `acao` é o mesmo modelo sem a voz: o gesto de boca fechada, com a voz por cima na montagem. Cena
`fala` ou `acao` cuja imagem ainda não existe espera: ela costuma sair de outra cena do mesmo lote.

Idempotente: cada pedido vai para `pedidos.json` assim que sai, e cena já baixada não é pedida de
novo. Pedido que falha sai da lista e volta na rodada seguinte; a API estorna geração que falha.
A chave: HIGGSFIELD_KEY_ID e HIGGSFIELD_KEY_SECRET no .env.local da raiz.

Só biblioteca padrão: roda com qualquer python3, sem o ambiente da fábrica.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
API = "https://api.higgsfield.ai"
MODELOS = {
    "kling": ("kling-video/v3.0/std/text-to-video", {"duration": 4, "aspect_ratio": "9:16", "sound": "off"}),
    "wan": ("alibaba/wan-3.0-prime/reference-to-video",
            {"duration": 5, "resolution": "480p", "aspect_ratio": "9:16", "generate_audio": False}),
    # a proporção é a da imagem inicial; o áudio que volta é o que foi, e não é usado
    "fala": ("wan/v2.7/image-to-video", {"duration": 5, "resolution": "720p"}),
    # o mesmo, sem voz: o gesto de boca fechada, que a montagem encaixa na palavra
    "acao": ("wan/v2.7/image-to-video", {"duration": 3, "resolution": "720p"}),
}
# US$ por segundo, da estimativa da API em 01/10/2026 (kling 4 s US$ 0,336; wan 5 s US$ 0,34) e
# 02/10 (fala 720p, US$ 0,10/s). É o que o modo seco usa, sem chave e sem rede. Antes de gerar,
# quem diz o preço é a API.
USD_S = {"kling": 0.084, "wan": 0.068, "fala": 0.10, "acao": 0.10}
UA = "obs-optimize/1.0"          # sem User-Agent, o Cloudflare barra (1010)
FICHA = ("acabamento", "janela", "hora", "cam", "data", "ilustra")


def ler(arq: Path) -> dict:
    """O lote, com a pasta dele em `_pasta`."""
    arq = Path(arq)
    return {**json.loads(arq.read_text(encoding="utf-8")), "_pasta": arq.resolve().parent}


def _estetica(lo: dict) -> Path | None:
    return next((p / "estetica.json" for p in (lo["_pasta"], lo["_pasta"].parent)
                 if (p / "estetica.json").exists()), None)


def pele(lo: dict) -> str:
    """O prompt da estética do lote, que entra no fim de toda cena."""
    if not lo.get("estetica"):
        return ""
    return " " + json.loads(_estetica(lo).read_text(encoding="utf-8"))[lo["estetica"]]["prompt"]


def params(lo: dict, modelo: str) -> tuple[str, dict]:
    """O endpoint do modelo e o que vai no pedido, com a duração e a proporção do lote."""
    ep, base = MODELOS[modelo]
    return ep, {**base, **({"duration": lo["duracao"]} if lo.get("duracao") else {}),
                **({"aspect_ratio": lo["proporcao"]} if lo.get("proporcao") else {})}


def corpo(lo: dict, c: str) -> tuple[str, dict]:
    """O `params` de uma cena: a duração e a resolução dela valem sobre as do lote. A `fala` dura o
    trecho de voz dela."""
    cena = lo["cenas"][c]
    ep, base = params(lo, cena["modelo"])
    dur = cena.get("duracao") or (round(cena["voz"][1] - cena["voz"][0]) if "voz" in cena else None)
    return ep, {**base, **({"duration": dur} if dur else {}),
                **({"resolution": cena["resolucao"]} if cena.get("resolucao") else {})}


def fotos(lo: dict, rosto=()) -> list[Path]:
    """As fotos do rosto: as do lote ou, sem elas, as de quem chamou."""
    return [lo["_pasta"] / f for f in lo["rosto"]] if lo.get("rosto") else [Path(f) for f in rosto]


def confere(lo: dict, rosto=()) -> list[str]:
    """Tudo o que dá para recusar antes de gastar, com o motivo."""
    erros = []
    if lo.get("estetica"):
        arq = _estetica(lo)
        if not arq:
            erros.append(f"a estética '{lo['estetica']}' pede um estetica.json na pasta do lote ou na de cima")
        elif lo["estetica"] not in json.loads(arq.read_text(encoding="utf-8")):
            erros.append(f"a estética '{lo['estetica']}' não está em {arq}")
    cenas = lo.get("cenas") or {}
    if not cenas:
        erros.append("o lote não tem `cenas`")
    for c, cena in cenas.items():
        if cena.get("modelo") not in MODELOS:
            erros.append(f"a cena {c} pede o modelo '{cena.get('modelo')}'. Disponíveis: {', '.join(MODELOS)}")
        if not cena.get("prompt"):
            erros.append(f"a cena {c} não tem `prompt`")
        if cena.get("modelo") in ("fala", "acao") and not cena.get("imagem"):
            erros.append(f"a cena {c} é `{cena['modelo']}`: pede a `imagem` inicial")
        if cena.get("modelo") == "fala" and not cena.get("audio"):
            erros.append(f"a cena {c} é `fala`: pede o `audio` (o trecho da voz)")
    if any(c.get("modelo") == "wan" for c in cenas.values()):
        fs = fotos(lo, rosto)
        if not fs:
            erros.append("a cena `wan` pede `rosto` no lote: as fotos do rosto que entra na cena")
        erros += [f"a foto do rosto não existe: {f}" for f in fs if not f.exists()]
    return erros


def _pedidos(lo: dict) -> dict:
    arq = lo["_pasta"] / "pedidos.json"
    return json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}


def faltam(lo: dict) -> list[str]:
    """As cenas do lote que ainda não estão no disco, pedidas ou não."""
    return [c for c in lo["cenas"] if not (lo["_pasta"] / f"{c}.mp4").exists()]


def a_gerar(lo: dict) -> list[str]:
    """As que faltam e ninguém pediu ainda: é por elas que se paga."""
    pedidos = _pedidos(lo)
    return [c for c in faltam(lo) if c not in pedidos]


def tabela(lo: dict) -> dict[str, float]:
    """US$ por cena de cada modelo, pela tabela, na duração do lote."""
    return {m: USD_S[m] * params(lo, m)[1]["duration"] for m in MODELOS}


def estimativa(lo: dict, preco: dict | None = None) -> float:
    """US$ das cenas a gerar: pelo preço por cena da API, se veio, senão pela tabela. A cena que dura
    outra coisa que o lote paga na proporção."""
    preco = preco or tabela(lo)
    m = lambda c: lo["cenas"][c]["modelo"]
    return sum(preco[m(c)] * corpo(lo, c)[1]["duration"] / params(lo, m(c))[1]["duration"] for c in a_gerar(lo))


def registra(lo: dict) -> list[str]:
    """A cena baixada com `acabamento` no lote ganha ficha no cenas.json da pasta, que é o banco que
    o criativo lê. Ficha que já existe não é tocada: a janela que você acertou depois de assistir
    fica. Cena sem acabamento (os lotes antigos) quem registra é você, depois de revisar."""
    pasta, arq = lo["_pasta"], lo["_pasta"] / "cenas.json"
    banco = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else []
    tem = {f["id"] for f in banco}
    novas = [{"id": c, "arquivo": f"{c}.mp4", **{k: cena[k] for k in FICHA if k in cena},
              "prompt": cena["prompt"] + pele(lo)}
             for c, cena in lo["cenas"].items()
             if cena.get("acabamento") and c not in tem and (pasta / f"{c}.mp4").exists()]
    if novas:
        arq.write_text(json.dumps(banco + novas, ensure_ascii=False, indent=1), encoding="utf-8")
    return [f["id"] for f in novas]


# ---- a API -------------------------------------------------------------------


def _chave(env: Path | None) -> dict:
    """HIGGSFIELD_KEY_ID e HIGGSFIELD_KEY_SECRET, do .env.local da raiz ou do `env` de quem chamou.
    O valor nunca é impresso."""
    arq = Path(env) if env else RAIZ / ".env.local"
    if not arq.is_file():
        return {}
    d = dict(l.strip().split("=", 1) for l in arq.read_text(encoding="utf-8").splitlines()
             if "=" in l and not l.startswith("#"))
    return d if d.get("HIGGSFIELD_KEY_ID") and d.get("HIGGSFIELD_KEY_SECRET") else {}


def _req(url: str, h: dict, corpo=None) -> dict:
    r = urllib.request.Request(url if url.startswith("http") else f"{API}/{url}", headers=h,
                               data=json.dumps(corpo).encode() if corpo is not None else None)
    try:
        return json.load(urllib.request.urlopen(r, timeout=60))
    except urllib.error.HTTPError as e:
        return {"erro": e.code, "corpo": e.read().decode()[:300]}


def _sobe(foto: Path, h: dict) -> str:
    up = _req("files/generate-upload-url", h, {"content_type": mimetypes.guess_type(foto.name)[0] or "image/jpeg"})
    urllib.request.urlopen(urllib.request.Request(up["upload_url"], data=foto.read_bytes(), method="PUT",
                                                  headers={**up["upload_headers"], "User-Agent": UA}))
    return up["public_url"]


def main(argv=None, rosto=(), env: Path | None = None) -> None:
    """`rosto` e `env` são de quem embrulha: o banco do dono passa as fotos e a chave dele."""
    ap = argparse.ArgumentParser(description="Gera um lote de cenas na Higgsfield. Sem --gera, só estima.")
    ap.add_argument("lote", type=Path, help="o lote.json; as cenas baixam na pasta dele")
    ap.add_argument("--gera", action="store_true", help="gera o que falta: cobra na Higgsfield")
    ap.add_argument("--so", nargs="+", metavar="CENA", help="só estas cenas (o teste antes do resto)")
    a = ap.parse_args(argv)
    lo = ler(a.lote)
    erros = confere(lo, rosto)
    if erros:
        sys.exit("o lote reprovou antes de gastar:\n  " + "\n  ".join(erros))
    pasta, cenas, skin = lo["_pasta"], lo["cenas"], pele(lo)
    if lo.get("estetica"):
        print("estética:", lo["estetica"])
    chave = _chave(env)
    h = {"Authorization": f"Key {chave.get('HIGGSFIELD_KEY_ID')}:{chave.get('HIGGSFIELD_KEY_SECRET')}",
         "Content-Type": "application/json", "User-Agent": UA}
    faltando = [c for c in a_gerar(lo) if not a.so or c in a.so]
    # o que cada modelo pede de mídia, pra estimativa (ela não olha a mídia, mas recusa sem)
    midia = {"wan": {"image_urls": ["https://x.co/a.jpg"] * 2},
             "fala": {"image_url": "https://x.co/a.jpg", "audio_url": "https://x.co/a.wav"},
             "acao": {"image_url": "https://x.co/a.jpg"}}

    if chave:
        preco, de_onde = {}, ""
        for m in MODELOS:
            ep, base = params(lo, m)
            e = _req(f"estimate/{ep}", h, {"prompt": "x", **base, **midia.get(m, {})})
            preco[m] = float(e.get("usd", "nan"))
    else:
        preco, de_onde = tabela(lo), "  pela tabela: sem a chave da Higgsfield no .env.local"
    if any(lo["cenas"][c].get("duracao") or lo["cenas"][c].get("resolucao") or "voz" in lo["cenas"][c]
           for c in faltando) and chave:
        # cena com duração ou resolução própria: a API diz o preço de cada uma
        custo = {c: float(_req(f"estimate/{corpo(lo, c)[0]}", h, {"prompt": "x", **corpo(lo, c)[1],
                                                                   **midia.get(cenas[c]["modelo"], {})}).get("usd", "nan"))
                 for c in faltando}
        print(f"{len(faltando)} cenas a gerar, US$ {sum(custo.values()):.2f}  (" +
              ", ".join(f"{c} {u:.2f}" for c, u in custo.items()) + ")")
    else:
        print(f"{len(faltando)} cenas a gerar, US$ {estimativa({**lo, 'cenas': {c: cenas[c] for c in faltando}}, preco):.2f}  ("
              + ", ".join(f"{m} US$ {p:.3f}" for m, p in preco.items()) + " por cena)" + de_onde)
    if not a.gera:
        return
    if not chave:
        sys.exit("sem a chave: HIGGSFIELD_KEY_ID e HIGGSFIELD_KEY_SECRET no .env.local da raiz")

    arq_pedidos, pedidos = pasta / "pedidos.json", _pedidos(lo)
    refs = [_sobe(f, h) for f in fotos(lo, rosto)] if any(cenas[c]["modelo"] == "wan" for c in faltando) else []
    for c in faltando:
        ep, base = corpo(lo, c)
        extra = {"image_urls": refs} if cenas[c]["modelo"] == "wan" else {}
        if cenas[c]["modelo"] in ("fala", "acao"):
            fs = [pasta / cenas[c]["imagem"], *([pasta / cenas[c]["audio"]] if cenas[c]["modelo"] == "fala" else [])]
            if not all(f.exists() for f in fs):
                print(c, "espera:", ", ".join(str(f) for f in fs if not f.exists()))
                continue
            extra = dict(zip(("image_url", "audio_url"), (_sobe(f, h) for f in fs)))
        r = _req(ep, h, {"prompt": cenas[c]["prompt"] + skin, **base, **extra})
        if "status_url" not in r:
            print(c, "RECUSADO:", r)
            continue
        pedidos[c] = r["status_url"]
        arq_pedidos.write_text(json.dumps(pedidos, indent=1), encoding="utf-8")

    for _ in range(120):                          # até 20 min
        for c, url in list(pedidos.items()):
            s = _req(url, h)
            if s.get("status") in ("queued", "in_progress", "processing"):
                continue
            if s.get("video"):
                urllib.request.urlretrieve(s["video"]["url"], pasta / f"{c}.mp4")
            print(c, s.get("status"), "" if s.get("video") else s)
            pedidos.pop(c)
            arq_pedidos.write_text(json.dumps(pedidos, indent=1), encoding="utf-8")
        if not pedidos:
            break
        time.sleep(10)
    fichas = registra(lo)
    if fichas:
        print("no banco (cenas.json):", ", ".join(fichas))
    print("baixadas:", sorted(p.stem for p in pasta.glob("*.mp4")), "| pendentes:", list(pedidos))


if __name__ == "__main__":
    main()
