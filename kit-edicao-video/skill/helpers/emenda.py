"""Trocar um pedaço do vídeo sem recodificar o resto.

Medido antes disto: o glitch gastava 16,5 s para trocar 0,4 s, e a abertura CRT
10,1 s para trocar 0,8 s. **1,4% do trabalho era útil.** Os dois montavam o vídeo
com uma junção de FILTRO, e filtro obriga a decodificar e recodificar tudo que
passa por ele — inclusive o miolo, que não muda em nada.

Aqui a junção é pelo **demultiplexador**, que copia os bits. Codifica só os
pedaços que mudam; o resto atravessa intocado.

    plano = planeja(fonte, [Trecho(4.0, 4.4, "glitch")], saida)
    executa(plano, {"glitch": caminho_do_pedaco_pronto})

Duas coisas que não são detalhe:

**O corte cai num quadro-chave.** Cortar no meio de um grupo de quadros faz o
vídeo piscar ou travar na junção, porque o decodificador não tem de onde partir.

**A cópia exige fluxos compatíveis.** É por isso que as constantes de saída moram
todas na costura B: o pedaço codificado tem que sair com os mesmos parâmetros da
fonte. Quando não dá, este módulo recodifica e **diz que recodificou** — degradar
calado transforma regressão de desempenho em mistério.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import ff

# Quantos quadros de deslocamento ainda contam como o mesmo vídeo. A junção mexe
# no relógio em centésimos; dois quadros é folga de sobra e ainda pega troca de
# conteúdo, que desloca muito mais que isso.
TOLERANCIA = 2


@dataclass(frozen=True)
class Trecho:
    """Um pedaço da fonte que vai ser substituído."""
    inicio: float
    fim: float
    nome: str           # qual pedaço pronto entra aqui

    @property
    def dur(self) -> float:
        return self.fim - self.inicio


@dataclass(frozen=True)
class Pedaco:
    """Um pedaço do resultado: copiado da fonte, ou substituído."""
    inicio: float
    fim: float
    copia: bool
    nome: str = ""

    @property
    def dur(self) -> float:
        return self.fim - self.inicio


@dataclass
class Plano:
    fonte: Path
    saida: Path
    pedacos: list[Pedaco]
    comandos: list[list[str]] = field(default_factory=list)
    motivo_recodificou: str = ""

    @property
    def total(self) -> float:
        return sum(p.dur for p in self.pedacos)

    @property
    def copiado(self) -> float:
        return sum(p.dur for p in self.pedacos if p.copia)

    @property
    def recodificado(self) -> float:
        return sum(p.dur for p in self.pedacos if not p.copia)


def quadros_chave(fonte: Path | str) -> list[float]:
    """Onde o decodificador consegue começar. O corte tem que cair num destes."""
    r = ff.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                "-skip_frame", "nokey", "-show_entries", "frame=pts_time",
                "-of", "csv=p=0", str(fonte)], capture=True, quiet=True, check=False)
    return sorted(float(x) for x in re.findall(r"[\d.]+", r.stdout or "") if x)


def _antes(chaves: list[float], t: float) -> float:
    """O quadro-chave em t ou antes dele."""
    anteriores = [k for k in chaves if k <= t + 0.001]
    return max(anteriores) if anteriores else 0.0


def _depois(chaves: list[float], t: float, dur: float) -> float:
    """O quadro-chave em t ou depois dele."""
    seguintes = [k for k in chaves if k >= t - 0.001]
    return min(seguintes) if seguintes else dur


def planeja(fonte: Path | str, trechos: list[Trecho], saida: Path | str,
            forca_recodificar: bool = False) -> Plano:
    """Monta a lista de pedaços e os comandos que os juntam. Não executa nada."""
    fonte, saida = Path(fonte), Path(saida)
    dur = ff.dur(fonte)

    ordenados = sorted(trechos, key=lambda t: t.inicio)
    for t in ordenados:
        if t.inicio < 0 or t.fim > dur + 0.01:
            raise ValueError(
                f"o trecho {t.inicio:.1f}→{t.fim:.1f} cai fora do vídeo, que tem {dur:.1f}s"
            )
    for a, b in zip(ordenados, ordenados[1:]):
        if b.inicio < a.fim - 0.001:
            raise ValueError(
                f"os trechos {a.inicio:.1f}→{a.fim:.1f} e {b.inicio:.1f}→{b.fim:.1f} "
                f"se sobrepõem"
            )

    chaves = quadros_chave(fonte)

    # Dois trechos perto um do outro caem no MESMO grupo de quadros depois de
    # ancorar, e aí os dois viram o mesmo pedaço — a junção montava o vídeo com o
    # trecho repetido. Quem está no mesmo grupo vira UM trecho só; quem produz o
    # substituto recebe o vão inteiro e desenha os dois efeitos dentro dele.
    juntos: list[Trecho] = []
    for t in ordenados:
        if juntos and _antes(chaves, t.inicio) < _depois(chaves, juntos[-1].fim, dur) - 0.001:
            anterior = juntos[-1]
            juntos[-1] = Trecho(anterior.inicio, max(anterior.fim, t.fim),
                                f"{anterior.nome}+{t.nome}")
        else:
            juntos.append(t)
    ordenados = juntos

    pedacos: list[Pedaco] = []
    cursor = 0.0
    for t in ordenados:
        # AS DUAS bordas do pedaço substituído caem em quadro-chave, e não só a
        # de entrada: quem começa torto é o pedaço COPIADO que vem depois, e um
        # pedaço copiado que não começa num quadro-chave pisca ou trava.
        #
        # O preço é o substituído crescer até a chave seguinte. Ele diz de quanto
        # precisa em `pedacos`, e quem produz o substituto cobre esse tempo.
        ini = _antes(chaves, t.inicio)
        fim = _depois(chaves, t.fim, dur)
        if ini > cursor + 0.01:
            pedacos.append(Pedaco(cursor, ini, copia=True))
        pedacos.append(Pedaco(ini, fim, copia=False, nome=t.nome))
        cursor = fim
    if dur > cursor + 0.01:
        pedacos.append(Pedaco(cursor, dur, copia=True))
    if not pedacos:
        pedacos = [Pedaco(0.0, dur, copia=True)]

    plano = Plano(fonte=fonte, saida=saida, pedacos=pedacos)
    if forca_recodificar:
        plano.motivo_recodificou = "pedido explicitamente"
    plano.comandos = _comandos(plano)
    return plano


def _comandos(plano: Plano) -> list[list[str]]:
    trab = plano.saida.parent / f"_emenda_{plano.saida.stem}"
    cmds: list[list[str]] = []
    partes: list[Path] = []

    for i, p in enumerate(plano.pedacos):
        alvo = trab / f"{i:03d}.mp4"
        partes.append(alvo)
        if p.copia and not plano.motivo_recodificou:
            # O único jeito de não pagar o encoder: recortar copiando o fluxo.
            cmds.append(["ffmpeg", "-y", "-v", "error",
                         "-ss", f"{p.inicio:.3f}", "-to", f"{p.fim:.3f}",
                         "-i", str(plano.fonte), "-c", "copy",
                         "-avoid_negative_ts", "make_zero", str(alvo)])
        elif p.copia:
            cmds.append(["ffmpeg", "-y", "-v", "error",
                         "-ss", f"{p.inicio:.3f}", "-to", f"{p.fim:.3f}",
                         "-i", str(plano.fonte),
                         *ff.args_video("composicao"), *ff.args_audio(), str(alvo)])
        # pedaço substituído: o arquivo vem pronto de fora, em `executa`

    lista = trab / "partes.txt"
    cmds.append(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                 "-i", str(lista), "-c", "copy",
                 "-movflags", "+faststart", str(plano.saida)])
    return cmds


def lista_de_partes(partes: list[Path], onde: Path) -> Path:
    """O arquivo que o demultiplexador lê para juntar os pedaços.

    Existe como função porque a abertura CRT também junta pedaços — ela
    acrescenta pontas em vez de trocar miolo, então não usa `planeja`, mas a
    junção é a mesma. Escrever esta lista em dois lugares é como nascem as duas
    implementações que divergem.
    """
    onde.mkdir(parents=True, exist_ok=True)
    lista = onde / "partes.txt"
    lista.write_text("".join(f"file '{Path(p).resolve()}'\n" for p in partes), encoding="utf-8")
    return lista


def executa(plano: Plano, substitutos: dict[str, Path]) -> Path:
    """Roda o plano. `substitutos` traz o arquivo pronto de cada trecho."""
    trab = plano.saida.parent / f"_emenda_{plano.saida.stem}"
    trab.mkdir(parents=True, exist_ok=True)

    partes: list[Path] = []
    for i, p in enumerate(plano.pedacos):
        alvo = trab / f"{i:03d}.mp4"
        if p.copia:
            partes.append(alvo)
        else:
            pronto = substitutos.get(p.nome)
            if pronto is None:
                raise KeyError(f"falta o pedaço pronto para '{p.nome}'")
            partes.append(Path(pronto))

    for cmd in plano.comandos[:-1]:
        ff.run(cmd, quiet=True)

    lista_de_partes(partes, trab)
    ff.run(plano.comandos[-1], quiet=True)
    return plano.saida


def iguais(a: Path | str, b: Path | str, inicio: float, dur: float) -> bool:
    """Os quadros deste trecho são os mesmos nos dois arquivos?

    Compara o resumo de cada quadro DECODIFICADO, ignorando o instante. É a prova
    de que o miolo copiado continua idêntico à FONTE — ele deixou de ser
    recodificado, então agora é obrigação ser igual ao original.

    Não usa PSNR por instante: a junção desloca o relógio em alguns centésimos, e
    comparar dois arquivos com relógios diferentes mede desalinhamento, não
    degradação. Isso me custou uma hora achando que tinha estragado o vídeo —
    PSNR 40 dB com os quadros bit a bit idênticos.
    """
    def resumo(v: Path | str) -> list[str]:
        r = ff.run(["ffmpeg", "-v", "error", "-ss", f"{inicio:.3f}", "-t", f"{dur:.3f}",
                    "-i", str(v), "-map", "0:v", "-f", "framemd5", "-"],
                   capture=True, quiet=True, check=False)
        return [l.split(",")[-1].strip() for l in (r.stdout or "").splitlines()
                if l and not l.startswith("#")]

    x, y = resumo(a), resumo(b)
    if not x or not y:
        return False
    if x == y:
        return True
    # A junção desloca o relógio em alguns centésimos, e `-ss` nos dois arquivos
    # pega janelas levemente diferentes. Deslocar até TOLERANCIA quadros separa
    # desalinhamento de degradação — foi isso que me fez achar duas vezes que
    # tinha estragado o vídeo quando os quadros eram os mesmos.
    for k in range(-TOLERANCIA, TOLERANCIA + 1):
        se, ate = max(0, k), len(x) + min(0, k)
        corte_x, corte_y = x[se:ate], y[max(0, -k):len(y) + min(0, -k)]
        if corte_x and corte_x == corte_y:
            return True
    return False


def compara(a: Path | str, b: Path | str, inicio: float, dur: float) -> float:
    """PSNR entre dois vídeos num trecho. Infinito vira 99.

    Serve para o trecho que MUDOU — comparar o efeito novo com o antigo. Para o
    miolo copiado use `iguais`, que não se confunde com deslocamento de relógio.
    """
    # Sem `-v error`: o filtro psnr imprime o resumo em nível info, e silenciar o
    # ffmpeg silencia justamente a medida que se foi buscar.
    r = ff.run(["ffmpeg", "-hide_banner", "-nostats",
                "-ss", f"{inicio:.3f}", "-t", f"{dur:.3f}", "-i", str(a),
                "-ss", f"{inicio:.3f}", "-t", f"{dur:.3f}", "-i", str(b),
                "-lavfi", "[0:v][1:v]psnr", "-f", "null", "-"],
               capture=True, quiet=True, check=False)
    m = re.search(r"average:([\d.]+|inf)", (r.stderr or "") + (r.stdout or ""))
    if not m:
        return 0.0
    return 99.0 if m.group(1) == "inf" else float(m.group(1))
