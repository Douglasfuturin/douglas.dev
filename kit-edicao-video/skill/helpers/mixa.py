#!/usr/bin/env python3
"""Fecha o áudio de um corte: cama de trilha, ducking e loudness igual ao resto.

    python mixa.py corte.mp4 --trilha acustico-inspirador -o final.mp4

Três coisas que só fazem sentido juntas, e por isso moram no mesmo passo:

**Nível igual entre os cortes.** Dois blocos com 2dB de diferença lêem como
falha de gravação quando emendados. A voz entra num alvo fixo e a mistura sai
noutro, os dois medidos e não estimados.

**A cama.** Trilha muito mais baixa que a voz — a referência é 13dB abaixo, que
é onde ela sustenta sem disputar. Entra e sai em fade; cortar trilha seco no fim
soa como cabo arrancado. Trilha com final composto (o ta-da cai depois da última
palavra) pede `--fade-fim` curto: o fade de 2,4s abafa justamente o final.

**Ducking.** Mesmo baixa, a trilha some a consoante quando ele fala. O
`sidechaincompress` abaixa a música no ataque da voz e devolve no respiro, então
a cama aparece justamente nos vãos — que é onde ela serve pra alguma coisa.

**Onde há voz.** `--fala a:b,c:d` diz onde ela está; fora dali só há efeito
(o curto de mãos, com uma moeda por carta). A voz é medida só nesses trechos, e
só ali o ducking abaixa a cama — sem isso cada moeda bombeava a trilha, e o
efeito sozinho era levado ao volume de fala. `--fala ""`: não há voz nenhuma.

**O áudio vai até o fim da imagem.** Voz sintética acaba antes do vídeo (a chamada
fica parada meio segundo depois da última palavra), e o `amix` segue a primeira
entrada: a trilha cortava seco no meio do fade (0,34 s antes do fim no Eleven v4).
A voz ganha silêncio até a duração da imagem, e o fade da trilha fecha antes dela.

Sem `--trilha` ele só normaliza, que é o suficiente pra emendar blocos.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import ff

MUSICA = Path(__file__).resolve().parents[1] / "assets" / "musica"
# A raiz da pasta: é dela que o plano escreve `trilha.faixa`, e o comando pode rodar de outra.
RAIZ = Path(__file__).resolve().parents[3]
VOZ = -18.9         # o mesmo alvo do `trata_voz`, medido nas aulas dele
CAMA = -31.5        # 13dB abaixo da voz
SAIDA = -16.0       # mistura final, padrão de web


def lufs(p: Path, onde: str | None = None) -> float:
    so = f"aselect='{onde}'," if onde else ""
    s = ff.run(["ffmpeg", "-hide_banner", "-i", str(p), "-af",
                f"{so}loudnorm=print_format=json", "-f", "null", "-"],
               capture=True, quiet=True).stderr
    m = re.search(r'"input_i"\s*:\s*"?(-?[\d.]+)', s)
    if not m:
        sys.exit(f"não consegui medir {p}")
    return float(m.group(1))


def trechos(fala: str) -> str:
    """`0:2.5,7:9` → a expressão do ffmpeg que vale 1 dentro deles."""
    return "+".join(f"between(t,{a},{b})" for a, b in
                    (x.split(":") for x in fala.split(",") if x))


def duracao(p: Path) -> float:
    """A duração da imagem, que é o que o áudio tem que cobrir. Sem faixa de vídeo
    (ou sem a medida dela), a do arquivo."""
    r = ff.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                "stream=duration", "-of", "csv=p=0", str(p)], capture=True, quiet=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return ff.dur(p)


def resolver(nome: str) -> Path:
    p = Path(nome)
    if p.exists():
        return p
    if not p.is_absolute() and (RAIZ / p).exists():
        return RAIZ / p
    # procura em subpasta também: as do HeyGen moram em musica/heygen/
    for padrao in (p.name, f"{nome}.*", f"{nome}"):
        achados = sorted(MUSICA.rglob(padrao))
        if achados:
            return achados[0]
    sys.exit(f"trilha não achada: {nome} (procurei em {MUSICA})")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=Path)
    ap.add_argument("--trilha", help="nome em assets/musica ou caminho")
    ap.add_argument("--cama", type=float, default=CAMA, help=f"LUFS da trilha ({CAMA})")
    ap.add_argument("--voz", type=float, default=VOZ, help=f"LUFS da voz ({VOZ})")
    ap.add_argument("--alvo", type=float, default=SAIDA, help=f"LUFS da mistura ({SAIDA})")
    ap.add_argument("--sem-duck", action="store_true")
    ap.add_argument("--fade-fim", type=float, default=2.4, help="fade da trilha no fim, em s (2.4)")
    # narração sem respiro (voz sintética de anúncio) com razão 12 deixa a cama 32dB
    # abaixo da voz o tempo todo: medido nos criativos ninjas, ninguém ouvia a trilha
    ap.add_argument("--duck-ratio", type=float, default=12, help="quanto a voz abaixa a trilha (12)")
    ap.add_argument("--fala", help="trechos com voz, 'a:b,c:d' em s; fora deles só há efeito")
    ap.add_argument("-o", "--out", type=Path, required=True)
    a = ap.parse_args()

    dur = duracao(a.video)
    onde = trechos(a.fala) if a.fala is not None else None
    # sem voz nenhuma o efeito fica no nível em que o som.py o pôs, que já é contra a voz
    gv = 0.0 if onde == "" else a.voz - lufs(a.video, onde)
    ate_o_fim = f"apad=whole_dur={dur:.3f}"   # a fala acaba antes da imagem: o resto é silêncio

    if not a.trilha:
        ff.run(["ffmpeg", "-y", "-v", "error", "-i", str(a.video),
                "-af", f"volume={gv:.2f}dB,{ate_o_fim}", "-c:v", "copy",
                "-c:a", ff.CODEC_AUDIO, "-b:a", "192k", str(a.out)], quiet=True)
        print(f"{a.out}  só nível: {lufs(a.out):.1f} LUFS")
        return

    t = resolver(a.trilha)
    gm = a.cama - lufs(t)
    fim = max(0.5, dur - a.fade_fim - 0.1)
    # `aloop` antes do atrim: trilha mais curta que o corte tem que dar a volta,
    # e sem isso a cama simplesmente acaba no meio do vídeo
    cama = (f"[1:a]aloop=loop=-1:size=2000000000,atrim=0:{dur:.3f},"
            f"asetpts=N/SR/TB,volume={gm:.2f}dB,"
            f"afade=t=in:d=1.2,afade=t=out:st={fim:.3f}:d={a.fade_fim}[m]")
    # O teto vale nas duas passadas, e fica bem abaixo de 0: o AAC sobe o pico entre amostras
    # depois do limitador. Em 28/09, com a primeira passada sem limitador e a segunda em 0.97, um
    # criativo saiu com +0,2 dBTP; em 0.91 o mesmo sai com -0,1. Em 29/09, o curto de Lorcana
    # (pancada de efeito no primeiro quadro, +6,9 dB na segunda passada) saiu com +1,0 em 0.91 e
    # -1,3 em 0.85, já com o limitador a 4× (ff.limitador)
    teto = ff.limitador(0.85)
    if a.sem_duck or onde == "":
        graf = (f"[0:a]volume={gv:.2f}dB,{ate_o_fim}[v];{cama};"
                f"[v][m]amix=inputs=2:duration=first:normalize=0,{teto}[a]")
    else:
        # fora da fala a chave cala: o efeito passa por cima da cama sem abaixá-la
        chave = f"[k]volume=0:enable='not({onde})'[k2];" if onde else "[k]anull[k2];"
        graf = (f"[0:a]volume={gv:.2f}dB,{ate_o_fim},asplit=2[v][k];{chave}{cama};"
                f"[m][k2]sidechaincompress=threshold=0.03:ratio={a.duck_ratio}:"
                f"attack=15:release=420:makeup=1[d];"
                f"[v][d]amix=inputs=2:duration=first:normalize=0,{teto}[a]")

    ff.run(["ffmpeg", "-y", "-v", "error", "-i", str(a.video), "-i", str(t),
            "-filter_complex", graf, "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", ff.CODEC_AUDIO, "-b:a", "192k",
            str(a.out)], quiet=True)

    final = lufs(a.out)
    if abs(final - a.alvo) > 0.8:
        # a soma de voz e cama não cai exatamente no alvo: acerta numa segunda
        # passada, com o ganho medido no resultado real
        ff.run(["ffmpeg", "-y", "-v", "error", "-i", str(a.out),
                "-af", f"volume={a.alvo - final:.2f}dB,{teto}",
                "-c:v", "copy", "-c:a", ff.CODEC_AUDIO, "-b:a", "192k",
                str(a.out.with_suffix(".tmp.mp4"))], quiet=True)
        a.out.with_suffix(".tmp.mp4").replace(a.out)
    print(f"{a.out}  voz {gv:+.1f}dB · cama {gm:+.1f}dB ({t.name}) · "
          f"saída {lufs(a.out):.1f} LUFS")


if __name__ == "__main__":
    sys.exit(main())
