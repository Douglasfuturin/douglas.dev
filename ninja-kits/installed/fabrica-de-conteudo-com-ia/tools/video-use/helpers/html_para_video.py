#!/usr/bin/env python3
"""A espera de fonte que todo render de página faz antes de fotografar.

O render de peça mora em tools/v2/v2.py. Aqui ficou o que ele e a receita
importam (`carrega_fontes`), mais a linha de comando antiga como atalho:

    python html_para_video.py "t_frase.html?l1=Oi&l2=tudo" saida.mov 1080x1920 [--alpha]
    = python tools/v2/v2.py render t_frase l1=Oi l2=tudo --ar 1080x1920 --out saida.mov

Antes este arquivo tinha o próprio laço de captura: gravava os quadros dentro
de helpers/ e nunca apagava (95 pastas, 1,1 GB), resolvia a saída contra a
pasta dele e não contra quem chamava, e fixava 30 fps. Dois laços iguais
divergem; ficou um.
"""
import sys
from pathlib import Path
from urllib.parse import parse_qsl


def carrega_fontes(page):
    # Puxa TODA face declarada antes de começar a saltar no tempo.
    #
    # O Google só busca a face quando um glifo precisa dela, e no t=0 os
    # elementos estão com opacity:0 — ninguém pinta, nada é pedido. Ao saltar
    # pra 4,6s e fotografar na hora, o pedido sai e a foto acontece antes da
    # fonte chegar: o Chromium mede a caixa certa e desenha os glifos
    # empilhados. O PNG sai com a palavra amassada e o layout parecendo
    # correto, então o defeito só aparece olhando o vídeo pronto.
    page.evaluate("() => Promise.all([...document.fonts]"
                  "        .map(f => f.load().catch(() => null)))")
    page.wait_for_function(
        "() => [...document.fonts].every(f => f.status !== 'loading')",
        timeout=30000)
    ruins = page.evaluate(
        "() => [...document.fonts].filter(f => f.status === 'error')"
        "        .map(f => `${f.family} ${f.weight}`)")
    if ruins:
        sys.exit("fonte falhou: " + ", ".join(ruins))


def main(argv: list[str]) -> None:
    alfa = "--alpha" in argv
    args = [a for a in argv if a != "--alpha"]
    if not args:
        sys.exit(__doc__)
    src, _, query = args[0].partition("?")
    peca = Path(src).stem                 # a peça é o nome do arquivo no catálogo
    out = Path(args[1]) if len(args) > 1 else Path(peca + ".mov")
    ar = args[2] if len(args) > 2 else None
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "v2"))
    import v2
    pares = [f"{k}={v}" for k, v in parse_qsl(query, keep_blank_values=True)]
    v2.render(peca, pares, out, ar=ar, alfa=alfa)


if __name__ == "__main__":
    main(sys.argv[1:])
