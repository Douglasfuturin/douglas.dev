#!/usr/bin/env python3
"""Emenda vários cortes num vídeo só, e confere que a soma bateu.

    python junta.py r3.mp4 s2e3.mp4 s4e5.mp4 -o vsl.mp4

Parece trabalho pra `ffmpeg -f concat`, e é justamente aí que mora a armadilha.

**O demultiplexador não reescreve o relógio.** Ele cola os quadros e mantém a
taxa declarada do PRIMEIRO arquivo. Emendar um trecho de 25 fps com outro de 30
fps faz o segundo tocar a 25: a imagem estica 20%, o áudio não estica junto, e o
vídeo inteiro sai fora de sincronia depois da junção. Recodificar na saída não
salva — a essa altura os carimbos de tempo já estão errados.

Aqui a junção é por FILTRO, com `fps=` em cada entrada antes de concatenar. Custa
uma recodificação e entrega o relógio certo.

A conferência não é enfeite: mede a duração de cada entrada, soma, e compara com
o que saiu. Mais de um quadro de diferença é erro, não aviso — foi exatamente
assim que um corte de 78s virou um de 94s sem ninguém perceber.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import ff


def _quadros(p: Path) -> int:
    """Quantos quadros a imagem tem. Contados, não calculados."""
    r = ff.run(["ffprobe", "-v", "error", "-select_streams", "v", "-count_frames",
                "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(p)],
               capture=True, quiet=True).stdout.strip()
    # um trecho com dado lateral (o perfil ICC de uma foto) sai "424," no csv
    return int(r.splitlines()[0].split(",")[0])


def juntar(partes: list[Path], saida: Path, *, fps: int = ff.FPS,
           largura: int = 0, altura: int = 0, quiet: bool = False) -> float:
    if len(partes) < 2:
        sys.exit("junta precisa de pelo menos dois arquivos")

    sondas = [ff.probe(p) for p in partes]
    largura = largura or sondas[0].largura
    altura = altura or sondas[0].altura
    if not all(s.tem_audio for s in sondas):
        mudas = [p.name for p, s in zip(partes, sondas) if not s.tem_audio]
        sys.exit(f"sem faixa de áudio: {', '.join(mudas)}")

    if not quiet:
        for p, s in zip(partes, sondas):
            marca = "" if s.fps == fps else f"  <- {s.fps} fps, vai pra {fps}"
            print(f"  {p.name:34} {s.duracao:7.2f}s  {s.largura}x{s.altura}{marca}")

    # Quantos quadros cada parte tem DE VERDADE. Não dá pra confiar na duração
    # do contêiner: ela é o maior entre imagem e som, e o som sempre passa uns
    # centésimos do último quadro. O `fps=` então completa a diferença inventando
    # quadro, uma vez por emenda — treze partes viraram 38 quadros a mais.
    # O corte acontece DEPOIS do `fps=`, então a conta é na taxa de saída: um
    # clipe de 25fps com 50 quadros vira 60 a 30fps, e aparar em 50 o encurtaria
    # em um terço. Contar na fonte e cortar no destino foi exatamente esse erro.
    contados = [_quadros(p) for p in partes]
    quadros = [max(1, round(c * fps / (s.fps or fps))) for c, s in zip(contados, sondas)]
    # O esperado é a duração da IMAGEM de cada parte, na taxa dela. A do contêiner
    # é o maior entre imagem e som, e o som de cada bloco passa uns centésimos do
    # último quadro: num episódio de 19 blocos isso somou 0,67 s e reprovou um
    # vídeo certo. Contra a imagem na própria taxa, o defeito que a conferência
    # existe pra pegar (25fps tocando a 30) continua aparecendo inteiro.
    esperado = sum(c / (s.fps or fps) for c, s in zip(contados, sondas))

    entradas: list[str] = []
    graf: list[str] = []
    rotulos: list[str] = []
    for i, (p, n, s) in enumerate(zip(partes, quadros, sondas)):
        entradas += ["-i", str(p)]
        # A taxa ANTES do concat, em cada entrada. É o passo que o demultiplexador
        # não tem como fazer, e sem ele a emenda desanda. O `trim` logo depois
        # fecha a parte num número inteiro de quadros, e aí a soma é exata. A
        # parte do HeyGen (25) mistura em vez de repetir quadro (ff.taxa).
        graf.append(f"[{i}:v]{ff.taxa(s.fps or fps, fps)},trim=end_frame={n},setpts=N/FRAME_RATE/TB,"
                    f"scale={largura}:{altura},setsar=1,format={ff.PIX_FMT}[v{i}];")
        graf.append(f"[{i}:a]aresample={ff.AUDIO_RATE},atrim=0:{n / fps:.5f},"
                    f"apad=whole_dur={n / fps:.5f},asetpts=N/SR/TB[a{i}];")
        rotulos.append(f"[v{i}][a{i}]")
    graf.append("".join(rotulos) + f"concat=n={len(partes)}:v=1:a=1[v][a]")

    ff.run(["ffmpeg", "-y", "-v", "error", *entradas,
            "-filter_complex", "".join(graf), "-map", "[v]", "-map", "[a]",
            *ff.args_video(fps=fps), *ff.args_audio(), str(saida)], quiet=True)

    saiu = _quadros(saida) / fps
    # Um quadro por parte, mais um pro contêiner. Tentei fechar no quadro exato
    # aparando cada entrada e não fecha: treze partes recodificadas acumulam
    # meio segundo em 387, e perseguir isso é precisão que o formato não dá.
    #
    # A folga continua três ordens de grandeza abaixo do defeito que isto existe
    # pra pegar — 25fps tocando a 30 estica 20%, o que num minuto dá 12s.
    folga = (len(partes) + 1) / fps
    if abs(saiu - esperado) > folga:
        sys.exit(f"a soma não bateu: esperava {esperado:.2f}s, saiu {saiu:.2f}s "
                 f"({abs(saiu - esperado):.2f}s de diferença, folga é {folga:.2f}s). "
                 f"Alguma entrada tem relógio quebrado.")
    if not quiet:
        print(f"{saida}  {saiu:.2f}s  ({len(partes)} partes, "
              f"deriva {abs(saiu - esperado) * 1000:.0f} ms)")
    return saiu


def _autoteste() -> None:
    """Emenda 25 fps com 30 fps e confere que a soma bate — que é o caso que o
    demultiplexador erra."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        for nome, taxa, dur in (("a.mp4", 25, 2.0), ("b.mp4", 30, 3.0)):
            ff.run(["ffmpeg", "-y", "-v", "error",
                    "-f", "lavfi", "-i", f"testsrc=size=320x568:rate={taxa}:duration={dur}",
                    "-f", "lavfi", "-i", f"sine=frequency=440:duration={dur}",
                    "-shortest", *ff.args_video(fps=taxa), *ff.args_audio(),
                    str(d / nome)], quiet=True)
        saiu = juntar([d / "a.mp4", d / "b.mp4"], d / "j.mp4", quiet=True)
        assert abs(saiu - 5.0) < 0.1, f"esperava ~5.0s, saiu {saiu:.2f}s"
        assert ff.probe(d / "j.mp4").fps == ff.FPS
        # doze blocos com o som 60 ms mais comprido que a imagem: a soma do contêiner
        # passava da folga e reprovava uma emenda certa
        for i in range(12):
            ff.run(["ffmpeg", "-y", "-v", "error",
                    "-f", "lavfi", "-i", f"testsrc=size=320x568:rate={ff.FPS}:duration=1",
                    "-f", "lavfi", "-i", "sine=frequency=440:duration=1.06",
                    *ff.args_video(fps=ff.FPS), *ff.args_audio(), str(d / f"s{i}.mp4")], quiet=True)
        saiu = juntar([d / f"s{i}.mp4" for i in range(12)], d / "s.mp4", quiet=True)
        assert abs(saiu - 12.0) < 0.1, f"esperava ~12.0s, saiu {saiu:.2f}s"
    print("autoteste ok: 25fps + 30fps -> 5.00s na taxa do projeto; som passando da imagem não reprova")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("partes", nargs="*", type=Path)
    ap.add_argument("-o", "--out", type=Path)
    ap.add_argument("--fps", type=int, default=ff.FPS)
    ap.add_argument("--autoteste", action="store_true")
    a = ap.parse_args()
    if a.autoteste:
        return _autoteste()
    if not a.partes or not a.out:
        ap.error("precisa dos arquivos e de -o")
    for p in a.partes:
        if not p.exists():
            sys.exit(f"não achei {p}")
    juntar(a.partes, a.out, fps=a.fps)


if __name__ == "__main__":
    sys.exit(main())
