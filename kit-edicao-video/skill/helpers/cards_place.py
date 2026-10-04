"""Encosta cada card numa pausa da fala e mostra o que está sendo dito por baixo dele.

Um card que entra no meio de uma frase compete com o áudio: o aluno lê uma coisa e ouve
outra, e a tradução que o card carrega se perde. Esta ferramenta pega os tempos de SAÍDA
(work/cards_t.json) e encosta cada um na borda de frase mais próxima, além de imprimir a
fala que roda durante os segundos do card — que é como se enxerga a colisão.

Não mexe em vídeo. Roda antes do burn_cards.py.

Uso:
    python helpers/cards_place.py --words work/obs_words.json --edl work/clean.json \
        --cards work/cards_t.json [--dur 5.0] [--write]
    python helpers/cards_place.py --words A.json B.json --edl c1.json c2.json --cards t.json

    --write reescreve cards_t.json com os tempos encostados (guarda os antigos em _antes).
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

PAUSE_MIN = 0.35    # silêncio que conta como borda de frase
SEARCH = 2.5        # o quanto o card pode andar pra achar uma borda (s)


def out_words(words_files: list[Path], edl_files: list[Path]) -> list[dict]:
    """Linha do tempo de SAÍDA: palavras do corte final com o tempo que elas têm no vídeo."""
    out, t = [], 0.0
    for wf, ef in zip(words_files, edl_files):
        W = [w for w in json.loads(wf.read_text(encoding="utf-8"))["words"] if w.get("type") == "word"]
        for r in json.loads(ef.read_text(encoding="utf-8"))["ranges"]:
            s, e = float(r["start"]), float(r["end"])
            for w in W:
                if float(w["start"]) >= s - 0.01 and float(w["end"]) <= e + 0.01:
                    out.append({"s": round(t + float(w["start"]) - s, 3),
                                "e": round(t + float(w["end"]) - s, 3), "x": w["text"]})
            t += e - s
    return out


def edges(ow: list[dict]) -> list[float]:
    """Instantes onde a fala respira: começo do vídeo e toda retomada depois de PAUSE_MIN."""
    e = [0.0]
    for i in range(1, len(ow)):
        if ow[i]["s"] - ow[i-1]["e"] >= PAUSE_MIN:
            e.append(ow[i]["s"])
        # ponto final também é borda, mesmo sem pausa medível
        elif ow[i-1]["x"].rstrip().endswith((".", "?", "!")):
            e.append(ow[i]["s"])
    return e


def snap(t: float, eds: list[float], search: float = SEARCH) -> float:
    near = [x for x in eds if abs(x - t) <= search]
    return min(near, key=lambda x: abs(x - t)) if near else t


def said(ow: list[dict], a: float, b: float) -> str:
    return " ".join(w["x"] for w in ow if a <= w["s"] < b) or "(silêncio)"


def mmss(t): return f"{int(t//60)}:{int(t % 60):02d}"


def main():
    ap = argparse.ArgumentParser(description="Encosta os cards numa pausa da fala")
    ap.add_argument("--words", type=Path, nargs="+", required=True)
    ap.add_argument("--edl", type=Path, nargs="+", required=True)
    ap.add_argument("--cards", type=Path, required=True)
    ap.add_argument("--dur", type=float, default=5.0)
    ap.add_argument("--search", type=float, default=SEARCH)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    if len(args.words) != len(args.edl):
        raise SystemExit("passe um --edl por --words, na mesma ordem")

    ow = out_words(args.words, args.edl)
    eds = edges(ow)
    T = json.loads(args.cards.read_text(encoding="utf-8"))
    novos = {}
    for k, v in sorted(T.items(), key=lambda kv: (isinstance(kv[1], str), kv[1])):
        if k.startswith("_") or isinstance(v, str):
            novos[k] = v; continue
        n = round(snap(float(v), eds, args.search), 2)
        novos[k] = n
        marca = "encostado" if abs(n - v) > 0.01 else "já na borda"
        print(f"[{k}] {mmss(v)} ({v:.2f}s) -> {mmss(n)} ({n:.2f}s)  {marca} {n-v:+.2f}s")
        print(f"     fala sob o card: {said(ow, n, n + args.dur)[:150]}")

    if args.write:
        novos["_antes"] = {k: v for k, v in T.items() if not k.startswith("_")}
        args.cards.write_text(json.dumps(novos, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n-> {args.cards} reescrito (tempos antigos em _antes)")
    else:
        print("\n(dry-run; use --write pra gravar)")


def _selftest():
    ow = [{"s": 0.0, "e": 0.4, "x": "um"}, {"s": 0.4, "e": 0.8, "x": "dois."},
          {"s": 2.0, "e": 2.4, "x": "tres"}, {"s": 2.4, "e": 2.8, "x": "quatro"}]
    eds = edges(ow)
    assert eds == [0.0, 2.0], eds                     # a pausa de 1.2s é a única borda
    assert snap(1.7, eds) == 2.0                      # anda pra frente pra borda
    assert snap(0.2, eds) == 0.0                      # anda pra tras
    assert snap(9.0, eds) == 9.0                      # nada perto: nao mexe
    assert said(ow, 2.0, 5.0) == "tres quatro"
    assert said(ow, 1.0, 1.5) == "(silêncio)"
    # pausa curta nao vira borda, mas ponto final vira
    ow2 = [{"s": 0.0, "e": 0.4, "x": "um."}, {"s": 0.5, "e": 0.9, "x": "dois"}]
    assert edges(ow2) == [0.0, 0.5], edges(ow2)
    print("cards_place selftest ok")


if __name__ == "__main__":
    import sys
    _selftest() if "--selftest" in sys.argv else main()
