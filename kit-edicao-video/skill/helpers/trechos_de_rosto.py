#!/usr/bin/env python3
"""Só o rosto vai pro HeyGen: os trechos de rosto de vários blocos numa geração só.

    python helpers/trechos_de_rosto.py monta seg/plano.json qua/plano.json sex/plano.json -o semana/
    python helpers/trechos_de_rosto.py devolve semana/geracao.json semana/gerado.mp4

Onde a peça é tela cheia a boca não aparece, e o avatar não precisa existir ali.
Cada bloco de avatar declara no plano as janelas de tela cheia (`tela_cheia`, em
segundos do áudio limpo, com fronteira entre frases). O `monta` junta os trechos de
rosto de todos os blocos ainda não gerados — os três reels da semana — num áudio
só, com VAO de silêncio entre eles e SOBRA pra dentro da peça dos dois lados: o
avatar entra e sai com a boca certa, e a sobra fica debaixo da peça. O
`geracao.json` diz de que reel, de que bloco e de que trecho veio cada pedaço.

O `devolve` faz o caminho de volta: recorta o gerado no tempo do áudio limpo de
cada bloco, preto onde a peça cobre, com o áudio limpo inteiro por baixo. O
arquivo que sai vai no `gerado` do bloco, e a fábrica segue dali.

O áudio limpo é o que a fábrica deixou no portão (`fabrica.py <plano>` para lá
quando o bloco não tem `gerado`). Nasceu no upsell de uma VSL: as duas versões de preço saíram de uma geração de 94
créditos, contra 145 por versão gerando o áudio inteiro.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import fabrica as fb
import ff

SOBRA, VAO = 0.25, 0.3   # vão acima de ~0,35 s estoura o teto de pausa do pre_voo (0,6 s)


def trechos(dur: float, tela_cheia: list) -> list[tuple[float, float]]:
    """O que a tela cheia não cobre, com a sobra pra dentro da peça."""
    janelas = sorted((float(a), float(b)) for a, b in tela_cheia)
    for (a, b), (prox, _) in zip(janelas, janelas[1:] + [(dur, dur)]):
        if not 0 <= a < b <= prox:
            raise ValueError(f"tela cheia [{a}, {b}] fora do áudio ({dur:.2f}s) "
                             f"ou em cima da seguinte")
    bordas = [0.0, *[t for j in janelas for t in j], dur]
    # Tela cheia colada no começo ou no fim não deixa rosto nenhum daquele lado.
    return [(max(0.0, a - SOBRA), min(dur, b + SOBRA))
            for a, b in zip(bordas[::2], bordas[1::2]) if b > a]


def blocos_do_plano(caminho: Path) -> list[dict]:
    """Os blocos de avatar ainda não gerados de um plano, com o áudio limpo de cada um.

    Quem sabe onde o áudio limpo mora é a fábrica: no modo seco, a saída do passo
    do apara_pausas de cada bloco pendente é o áudio. Repetir o caminho aqui era
    ter dois lugares para ele divergir.
    """
    plano = json.loads(caminho.read_text(encoding="utf-8"))
    plano.setdefault("_dir", str(caminho.resolve().parent))
    seco = fb.fabrica(plano, seco=True, sem_cache=True)
    por_nome = {b["nome"]: b for b in plano.get("blocos") or []}
    out = []
    for p in seco.passos:
        if Path(p.cmd[1]).name != "apara_pausas.py":
            continue
        nome = p.nome.rpartition(": ")[0] or None
        if not p.saida.exists():
            raise FileNotFoundError(
                f"{caminho}: o áudio limpo de {nome or plano['slug']} ainda não existe. "
                f"Rode `fabrica.py {caminho}` antes: ela para no portão com ele pronto")
        out.append({"plano": str(caminho.resolve()), "reel": plano["slug"], "bloco": nome,
                    "voz": str(p.saida), "fps": seco.estilo.eixos["imagem"]["fps"],
                    "tela_cheia": por_nome.get(nome, plano).get("tela_cheia") or []})
    return out


def monta(blocos: list[dict], pasta: Path) -> dict:
    """Um geracao.wav com os trechos de rosto de todos os blocos, e o mapa dele."""
    doc = {"sobra": SOBRA, "vao": VAO, "blocos": [], "trechos": []}
    ins, partes, t = [], [], 0.0
    for k, b in enumerate(blocos):
        dur = ff.dur(b["voz"])
        ins += ["-i", str(b["voz"])]
        doc["blocos"].append({**b, "voz": str(b["voz"]), "dur": round(dur, 3)})
        for a, z in trechos(dur, b.get("tela_cheia") or []):
            doc["trechos"].append({"reel": b["reel"], "bloco": b.get("bloco"),
                                   "fonte": [round(a, 3), round(z, 3)],
                                   "gerado": [round(t, 3), round(t + z - a, 3)]})
            partes.append(f"[{k}:a]atrim={a:.3f}:{z:.3f},asetpts=N/SR/TB,"
                          f"aformat=sample_rates=48000:channel_layouts=mono")
            t += z - a + VAO
    if not partes:
        raise ValueError("nenhum trecho de rosto: a tela cheia cobre tudo")
    n = len(partes)
    grafo = ";".join(f"{p},apad=pad_dur={VAO}[s{i}]" if i < n - 1 else f"{p}[s{i}]"
                     for i, p in enumerate(partes))
    grafo += ";" + "".join(f"[s{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[o]"
    pasta.mkdir(parents=True, exist_ok=True)
    ff.run(["ffmpeg", "-y", *ins, "-filter_complex", grafo, "-map", "[o]",
            "-ar", "48000", str(pasta / "geracao.wav")], quiet=True)
    (pasta / "geracao.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    return doc


def devolve(geracao: Path, gerado: Path, pasta: Path | None = None) -> list[tuple[dict, Path]]:
    """Cada bloco de volta ao tempo do áudio limpo dele: o rosto onde ele fala,
    preto onde a peça cobre."""
    doc = json.loads(geracao.read_text(encoding="utf-8"))
    pasta = pasta or geracao.parent
    sonda = ff.probe(gerado)
    w, h = sonda.largura, sonda.altura
    saidas = []
    for b in doc["blocos"]:
        meus = [t for t in doc["trechos"]
                if (t["reel"], t["bloco"]) == (b["reel"], b.get("bloco"))]
        fps, dur = b.get("fps", ff.FPS), b["dur"]
        fc = f"color=black:s={w}x{h}:r={fps}:d={dur:.3f}[f0];"
        for i, t in enumerate(meus):
            (a, z), (g0, g1) = t["fonte"], t["gerado"]
            fc += (f"[0:v]trim={g0:.3f}:{g1:.3f},setpts=PTS-STARTPTS+{a:.3f}/TB,fps={fps}[r{i}];"
                   f"[f{i}][r{i}]overlay=eof_action=pass:"
                   f"enable='between(t,{a:.3f},{z:.3f})'[f{i + 1}];")
        fc += f"[f{len(meus)}]format=yuv420p[v]"
        saida = pasta / (".".join(x for x in (b["reel"], b.get("bloco")) if x) + ".mp4")
        ff.run(["ffmpeg", "-y", "-i", str(gerado), "-i", b["voz"], "-filter_complex", fc,
                "-map", "[v]", "-map", "1:a", "-t", f"{dur:.3f}",
                *ff.args_video(fps=fps), *ff.args_audio(), str(saida)], quiet=True)
        saidas.append((b, saida))
    return saidas


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("monta", help="junta os trechos de rosto dos planos num geracao.wav")
    m.add_argument("planos", nargs="+", type=Path)
    m.add_argument("-o", "--pasta", type=Path, required=True)
    d = sub.add_parser("devolve", help="recorta o gerado de volta no tempo de cada bloco")
    d.add_argument("geracao", type=Path)
    d.add_argument("gerado", type=Path)
    d.add_argument("-o", "--pasta", type=Path)
    a = ap.parse_args()

    if a.cmd == "monta":
        blocos = [b for p in a.planos for b in blocos_do_plano(p)]
        if not blocos:
            sys.exit("nenhum bloco de avatar sem `gerado` nesses planos")
        doc = monta(blocos, a.pasta)
        wav = a.pasta / "geracao.wav"
        total = sum(b["dur"] for b in doc["blocos"])
        print(f"{wav}  {ff.dur(wav):.1f}s de {total:.1f}s  "
              f"({len(doc['trechos'])} trechos de rosto, {len(blocos)} blocos)")
        return
    for b, saida in devolve(a.geracao, a.gerado, a.pasta):
        onde = f"do bloco {b['bloco']} " if b.get("bloco") else ""
        print(f"{saida}\n  -> `gerado` {onde}em {b['plano']}")


if __name__ == "__main__":
    main()
