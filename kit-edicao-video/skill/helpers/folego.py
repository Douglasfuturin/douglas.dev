"""Mede o fôlego de um corte: ritmo da fala e pausa que sobrou.

Um corte apertado demais passa em toda checagem de conteúdo — nenhuma palavra se perde — e
mesmo assim entrega uma aula que o aluno não consegue acompanhar, porque some o tempo de
processar a virada de tópico. Isso não aparece num diff de transcrição. Aparece aqui.

Limites, medidos nas quatro aulas do módulo de skills (a que respira contra as três que não):
    ritmo médio      <= 165 palavras/min      (a boa deu 162; a pior, 184)
    pico em 30s      <= 210 palavras/min      (as quatro deram 228 a 256)
    maior pausa      >= 1.2 s                 (a boa deu 1.92; as três, 0.78)
    pausas >=0.35s   >= 8 por minuto          (a boa deu 9.8; as três, 3.7 a 4.6)

Uso:
    python helpers/folego.py --words work/obs_words.json --edl work/clean.json
    python helpers/folego.py --words A.json B.json --edl c1.json c2.json
Sai com código 1 se algum limite estourar.
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path

from cards_place import out_words

WPM_MED, WPM_PICO, PAUSA_MAX, PAUSAS_MIN = 165, 210, 1.2, 8.0
PAUSA = 0.35        # o que conta como pausa
JANELA = 30.0       # janela do pico, em s


def medir(ow: list[dict]) -> dict:
    if len(ow) < 2:
        raise SystemExit("poucas palavras pra medir")
    dur = ow[-1]["e"]
    pausas = [ow[i]["s"] - ow[i-1]["e"] for i in range(1, len(ow))
              if ow[i]["s"] - ow[i-1]["e"] >= PAUSA]
    pico, j = 0, 0
    for i in range(len(ow)):                       # janela deslizante de JANELA segundos
        while j < len(ow) and ow[j]["s"] < ow[i]["s"] + JANELA:
            j += 1
        if ow[j-1]["s"] - ow[i]["s"] >= JANELA * 0.9:
            pico = max(pico, (j - i) * 60.0 / JANELA)
    return {"dur": dur, "wpm": len(ow) * 60.0 / dur, "pico": pico,
            "pausa_max": max(pausas, default=0.0), "pausas_min": len(pausas) * 60.0 / dur}


def main():
    ap = argparse.ArgumentParser(description="Mede ritmo e pausa de um corte")
    ap.add_argument("--words", type=Path, nargs="+", required=True)
    ap.add_argument("--edl", type=Path, nargs="+", required=True)
    args = ap.parse_args()
    if len(args.words) != len(args.edl):
        raise SystemExit("passe um --edl por --words, na mesma ordem")

    m = medir(out_words(args.words, args.edl))
    checks = [
        ("ritmo médio", m["wpm"], "<=", WPM_MED, "palavras/min"),
        ("pico em 30s", m["pico"], "<=", WPM_PICO, "palavras/min"),
        ("maior pausa", m["pausa_max"], ">=", PAUSA_MAX, "s"),
        ("pausas/min", m["pausas_min"], ">=", PAUSAS_MIN, f"pausas >={PAUSA}s por min"),
    ]
    print(f"corte de {m['dur']/60:.1f}min")
    ruim = 0
    for nome, val, op, lim, un in checks:
        ok = val <= lim if op == "<=" else val >= lim
        ruim += not ok
        print(f"  {'ok  ' if ok else 'FORA'} {nome:<12} {val:6.1f}  (limite {op} {lim}) {un}")
    if ruim:
        print(f"\n{ruim} fora do limite. Pausa curta: suba o --pause-keep ou o --sil-cut no "
              f"clean_edl. Ritmo alto: é a fala, anote pro próximo take.")
    sys.exit(1 if ruim else 0)


def _selftest():
    # fala corrida, sem pausa: ritmo alto e fôlego zero (0.24s por palavra = 250 wpm)
    corrido = [{"s": i * 0.24, "e": i * 0.24 + 0.23, "x": "x"} for i in range(200)]
    m = medir(corrido)
    assert m["wpm"] > WPM_MED and m["pausa_max"] == 0.0, m
    assert m["pico"] > WPM_PICO, m
    # uma palavra a cada 0.6s com pausa de 1.5s a cada 5 palavras: passa
    t, folgado = 0.0, []
    for i in range(200):
        folgado.append({"s": t, "e": t + 0.3, "x": "x"})
        t += 1.5 if i % 4 == 3 else 0.45
    m2 = medir(folgado)
    assert m2["wpm"] <= WPM_MED, m2
    assert m2["pausa_max"] >= PAUSA_MAX, m2
    assert m2["pausas_min"] >= PAUSAS_MIN, m2
    print("folego selftest ok")


if __name__ == "__main__":
    _selftest() if "--selftest" in sys.argv else main()
