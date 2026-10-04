#!/usr/bin/env python3
"""O som por cima da voz: os cues das peças, os do plano, e mais nenhum mixador.

    python som.py bloco.mp4 --plan plano.json -o bloco_som.mp4 [--mestre -2] [--corta 74.2]
    python som.py --cues peca.json -o trilha.wav [--em 12.4] [--ganho -6]

No plano, um som é um CUE ou um ARQUIVO:

    "sons": [{"tipo": "pop", "t": 3.2},                                  ← ganho do sfx.json
             {"arquivo": "heygen/notif_b.mp3", "t": 23.74, "ganho": 0.5}]  ← ganho linear

E toda peça do plano (`brolls[]`) que publicou cues — o render grava duração e
cues em <peça>.json — soa sozinha, a partir do instante em que entra. O `sons`
do plano é só o extra: o whoosh na saída de uma peça renderizada com `sai=0`,
a notificação do print. Converter cue em som era o que três scripts da VSL
faziam à mão, cada um com seu MESTRE_DB.

O banco é um só, tools/v2/sfx/: um arquivo por nome de cue, o sfx.json com o
ganho de cada um, e as subpastas com o que não é cue (heygen/, avulsos/).
`arquivo` relativo procura ao lado do plano e depois no banco.

Depois do render e não antes: o áudio que vai pro HeyGen é o que ele usa pra
sincronizar a boca. Um bipe no meio dele confunde o lipsync e volta no vídeo
gerado, onde não dá mais pra tirar.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import ff

SFX = Path(__file__).resolve().parents[2] / "v2" / "sfx"
MAPA = json.loads((SFX / "sfx.json").read_text(encoding="utf-8"))["sons"]

# Nível dos cues contra a voz. Medido em 24/09 na VSL: com -8 o tick-roll
# ficava 17 dB debaixo da voz, inaudível. É do estilo; este é o padrão.
MESTRE_DB = -2.0

# Os de cinema pesam: no máximo três por vídeo (tools/v2/CUES.md).
CINEMA = {"riser", "boom", "sub-drop", "hit", "swell", "tom", "shimmer", "tape-stop", "glitch"}
DOSE_CINEMA = 3


def eventos(cues):
    """Cue → (t, arquivo no banco, ganho em dB). Cue com `dur` vira sequência."""
    for c in cues:
        s = MAPA.get(c["tipo"])
        if not s:
            print(f"  cue sem som: {c['tipo']}", file=sys.stderr)
            continue
        dur = c.get("dur")
        if dur and c["tipo"] == "tick-roll":
            for i in range(18):
                yield c["t"] + dur * .92 * (1 - (1 - i / 18) ** .35), s["unidade"], s["ganho_db"]
        elif dur and c["tipo"] == "type":
            for i in range(max(1, round(dur / .075))):
                yield c["t"] + i * .075, s["unidade"], s["ganho_db"]
        elif s.get("ancora") == "fim":
            # riser/swell: o som TERMINA no cue — começa `dur` antes
            yield c["t"] - s["dur"], s["arquivo"], s["ganho_db"]
        else:
            yield c["t"], s["arquivo"], s["ganho_db"]


def resolver(nome: str, base: Path) -> Path:
    p = Path(nome)
    for cand in (p if p.is_absolute() else base / p, SFX / p):
        if cand.exists():
            return cand
    achados = sorted(SFX.rglob(p.name))
    if achados:
        return achados[0]
    sys.exit(f"efeito não achado: {nome} (procurei ao lado do plano e em {SFX})")


def _cues_da_peca(arquivo: Path) -> list | None:
    for meta in (arquivo.with_suffix(".json"), arquivo.with_suffix(".cues.json")):
        if meta.exists():
            d = json.loads(meta.read_text(encoding="utf-8"))
            if isinstance(d, dict) and "cues" in d:
                return d["cues"]
    return None


def do_plano(plano: dict, base: Path, mestre: float = MESTRE_DB) -> list[tuple[float, Path, float]]:
    """Todos os sons de um plano como (t, arquivo, ganho em dB), em ordem."""
    saida, tipos = [], []
    # `cues_de`: mídia que soa e não é b-roll do plano — a receita de talking
    # head, que troca a imagem da base e publica os cues ao lado do .mp4.
    for b in (plano.get("brolls") or []) + (plano.get("cues_de") or []):
        arq = Path(b["arquivo"]) if Path(b["arquivo"]).is_absolute() else base / b["arquivo"]
        cues = _cues_da_peca(arq)
        # `mudo`: a peça entra calada — quem soa ali é o plano (a moeda de cada carta,
        # não o stamp e o whoosh de doze etiquetas seguidas)
        if cues is None or b.get("mudo"):
            continue
        t0, t1 = float(b["t0"]), float(b["t1"])
        # `inicio`: o captions_viral busca o clipe a partir dali, então o cue
        # que cai antes nunca aparece, e os outros andam junto.
        ini = float(b.get("inicio") or 0)
        tocam = [c for c in cues if ini <= c["t"] < ini + (t1 - t0)]
        tipos += [c["tipo"] for c in tocam]
        saida += [(t0 + t - ini, SFX / nome, db + mestre) for t, nome, db in eventos(tocam)]
    for s in plano.get("sons") or []:
        t = float(s["t"])
        if "tipo" in s:
            tipos.append(s["tipo"])
            saida += [(tt, SFX / nome, db + mestre) for tt, nome, db in eventos([s])]
        else:
            ganho = float(s.get("ganho", 0.5))
            saida.append((t, resolver(s["arquivo"], base), 20 * math.log10(max(ganho, 1e-6))))
    n = sum(1 for t in tipos if t in CINEMA)
    if n > DOSE_CINEMA:
        sys.exit(f"{n} sons de cinema neste plano; o teto é {DOSE_CINEMA} por vídeo (tools/v2/CUES.md)")
    return sorted(saida, key=lambda e: e[0])


def _grafo(evs, primeiro: int) -> tuple[list[str], list[str], list[str]]:
    """Uma entrada por ARQUIVO, não por evento: 216 ticks são um -i e um asplit."""
    usos = defaultdict(list)
    for i, (_, arq, _) in enumerate(evs):
        usos[arq].append(i)
    entradas, filtros, rotulos = [], [], []
    for k, (arq, idx) in enumerate(usos.items()):
        entradas += ["-i", str(arq)]
        n = primeiro + k
        if len(idx) == 1:
            filtros.append(f"[{n}:a]anull[r{idx[0]}]")
        else:
            filtros.append(f"[{n}:a]asplit={len(idx)}" + "".join(f"[r{i}]" for i in idx))
    for i, (t, _, db) in enumerate(evs):
        # Som que começaria antes do zero (o riser de um cue no primeiro
        # segundo) perde a cabeça, não o fim: ele tem que terminar no cue.
        cabeca = f"atrim=start={-t:.3f},asetpts=PTS-STARTPTS," if t < 0 else ""
        filtros.append(f"[r{i}]{cabeca}adelay={max(0, round(t * 1000))}:all=1,"
                       f"volume={db:.2f}dB[s{i}]")
        rotulos.append(f"[s{i}]")
    return entradas, filtros, rotulos


def mixa(cues, saida, em=0.0, ganho=0.0):
    """A trilha dos cues de uma peça, sozinha, em `saida` (a receita chama direto)."""
    evs = [(t + em, SFX / nome, db + ganho) for t, nome, db in eventos(cues)]
    if not evs:
        sys.exit("nenhum cue")
    entradas, filtros, rotulos = _grafo(evs, 0)
    filtros.append("".join(rotulos) + f"amix=inputs={len(evs)}:normalize=0[out]")
    ff.run(["ffmpeg", "-y", "-loglevel", "error", *entradas,
            "-filter_complex", ";".join(filtros), "-map", "[out]",
            "-ar", ff.AUDIO_RATE, str(saida)])
    print(f"wrote {saida}  ({len(evs)} eventos)")


def no_video(video: Path, evs, saida: Path, corta: float | None = None) -> None:
    if evs:
        entradas, filtros, rotulos = _grafo(evs, 1)
        # `duration=first` prende a saída ao vídeo: sem isso um efeito perto do
        # fim estica a trilha e o arquivo sai mais longo que a imagem
        filtros.append("[0:a]" + "".join(rotulos)
                       + f"amix=inputs={len(evs) + 1}:duration=first:normalize=0[a]")
        mapas = ["-filter_complex", ";".join(filtros), "-map", "0:v", "-map", "[a]"]
    else:
        entradas, mapas = [], ["-map", "0:v", "-map", "0:a"]
    corte = ["-t", f"{corta:.3f}"] if corta else []
    ff.run(["ffmpeg", "-y", "-v", "error", "-i", str(video), *entradas, *mapas, *corte,
            "-c:v", "copy", "-c:a", ff.CODEC_AUDIO, "-b:a", ff.AUDIO_BITRATE, str(saida)],
           quiet=True)
    print(f"{saida}  {len(evs)} efeito(s)  {ff.dur(saida):.2f}s")


def _autoteste() -> None:
    """Cue de peça + cue do plano + arquivo avulso, a dose de cinema, e o vídeo
    que sai com a mesma duração que entrou."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "peca.json").write_text(json.dumps({"cues": [{"tipo": "pop", "t": .5},
                                                         {"tipo": "stamp", "t": 9}]}), encoding="utf-8")
        plano = {"brolls": [{"arquivo": "peca.mov", "t0": 1.0, "t1": 3.0}],
                 "sons": [{"tipo": "riser", "t": 2.0}, {"arquivo": "heygen/notif_b.mp3", "t": .2}]}
        evs = do_plano(plano, d, mestre=-2)
        nomes = [(round(t, 2), a.name) for t, a, _ in evs]
        assert (1.5, "pop.wav") in nomes, "cue da peça cai em t0 + t"
        assert not any(a == "stamp.wav" for _, a in nomes), "cue depois do t1 da peça não toca"
        assert (round(2.0 - MAPA["riser"]["dur"], 2), "riser.wav") in nomes, "riser termina no cue"
        pop = next(db for t, a, db in evs if a.name == "pop.wav")
        assert abs(pop - (MAPA["pop"]["ganho_db"] - 2)) < 1e-9, "ganho do sfx.json mais o mestre"
        notif = next(db for t, a, db in evs if a.name == "notif_b.mp3")
        assert abs(notif - 20 * math.log10(.5)) < 1e-9, "arquivo sem ganho = 0,5 linear"
        buscada = {"brolls": [{"arquivo": "peca.mov", "t0": 1.0, "t1": 3.0, "inicio": .4}]}
        assert [(round(t, 2), a.name) for t, a, _ in do_plano(buscada, d)] == [(1.1, "pop.wav")], (
            "clipe buscado a partir de `inicio`: o cue anda junto")
        calada = {"brolls": [{"arquivo": "peca.mov", "t0": 1.0, "t1": 3.0, "mudo": True}]}
        assert do_plano(calada, d) == [], "peça muda não soa"
        cedo = do_plano({"sons": [{"tipo": "riser", "t": .5}]}, d)
        assert cedo[0][0] < 0, "riser no começo começa antes do zero"
        filtro = ";".join(_grafo(cedo, 0)[1])
        assert "atrim=start=" in filtro and "adelay=0" in filtro, "a cabeça tem que ser cortada"
        muitos = {"sons": [{"tipo": "boom", "t": float(i)} for i in range(DOSE_CINEMA + 1)]}
        try:
            do_plano(muitos, d)
            raise AssertionError("passou do teto de cinema sem recusar")
        except SystemExit:
            pass
        ff.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc=size=320x568:rate=30:duration=4",
                "-f", "lavfi", "-i", "sine=frequency=440:duration=4", "-shortest",
                *ff.args_video(), *ff.args_audio(), str(d / "v.mp4")], quiet=True)
        no_video(d / "v.mp4", evs, d / "s.mp4")
        assert abs(ff.dur(d / "s.mp4") - ff.dur(d / "v.mp4")) < .05, "o som esticou o vídeo"
    print("autoteste ok")


def main() -> None:
    if "--autoteste" in sys.argv:
        return _autoteste()
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=Path, nargs="?")
    ap.add_argument("--plan", type=Path)
    ap.add_argument("--cues", type=Path, help="só a trilha de uma peça, sem vídeo")
    ap.add_argument("--mestre", type=float, default=MESTRE_DB, help="nível dos cues contra a voz, dB")
    ap.add_argument("--corta", type=float, default=None,
                    help="duração final, pra aparar respiro do fim")
    ap.add_argument("--em", type=float, default=0.0, help="com --cues: onde a peça entra")
    ap.add_argument("--ganho", type=float, default=0.0, help="com --cues: ganho da trilha, dB")
    ap.add_argument("-o", "--out", type=Path, required=True)
    a = ap.parse_args()

    if a.cues:
        return mixa(json.loads(a.cues.read_text(encoding="utf-8"))["cues"], a.out, a.em, a.ganho)
    if not (a.video and a.plan):
        ap.error("som de vídeo pede o vídeo e --plan; trilha de peça pede --cues")
    evs = do_plano(json.loads(a.plan.read_text(encoding="utf-8")), a.plan.parent, a.mestre)
    if not evs and a.corta is None:
        # Bloco sem som nenhum passa direto: a fábrica chama o som em todo bloco.
        print("nenhum som neste plano; o vídeo passa como está")
    no_video(a.video, evs, a.out, a.corta)


if __name__ == "__main__":
    sys.exit(main())
