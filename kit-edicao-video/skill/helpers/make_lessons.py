"""Roda a fábrica em lote: um plano com várias aulas.

A live vira várias aulas, e cada uma é um plano. Este arquivo é só o laço — e é
por isso que ele encolheu de 95 linhas para trinta e poucas: cortar, renderizar,
desenhar, compor e entregar é da fábrica.

    python helpers/make_lessons.py <lessons.json>
    python helpers/make_lessons.py <lessons.json> --seco
    python helpers/make_lessons.py <lessons.json> --so 08

O `lessons.json` é um plano com uma lista `lessons`; o que está no topo vale para
todas e o que está em cada item vale para uma. Campo repetido no item ganha.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import fabrica


def main() -> None:
    ap = argparse.ArgumentParser(description="Roda a fábrica para cada aula do plano")
    ap.add_argument("plano", type=Path)
    ap.add_argument("--seco", action="store_true", help="não renderiza, só imprime")
    ap.add_argument("--so", metavar="PREFIXO", help="uma aula só, pelo começo do slug")
    ap.add_argument("--desde", default="corte", choices=fabrica.ETAPAS)
    args = ap.parse_args()

    doc = json.loads(args.plano.read_text(encoding="utf-8"))
    aulas = doc.get("lessons") or doc.get("aulas") or []
    if not aulas:
        sys.exit("o plano não tem nenhuma aula em `lessons`")
    comum = {k: v for k, v in doc.items() if k not in ("lessons", "aulas")}
    if args.so:
        aulas = [a for a in aulas if str(a.get("slug", "")).startswith(args.so)]

    falhas = []
    for i, aula in enumerate(aulas, 1):
        slug = aula.get("slug", f"aula-{i}")
        print(f"\n=== [{i}/{len(aulas)}] {slug} — {aula.get('title', '')} ===", flush=True)
        try:
            r = fabrica.fabrica({**comum, **aula}, seco=args.seco, desde=args.desde)
            if args.seco:
                r.imprime()
        except Exception as e:
            falhas.append(slug)
            print(f"  !! FALHOU: {e}", flush=True)

    print(f"\n{len(aulas) - len(falhas)}/{len(aulas)} aulas"
          + (f" — falharam: {', '.join(falhas)}" if falhas else ", nenhuma falha"))
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
