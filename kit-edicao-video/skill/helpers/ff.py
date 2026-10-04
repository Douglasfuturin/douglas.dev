"""Costura B — o único lugar onde este projeto chama ffmpeg.

Antes disto, `run` estava escrito de novo em cinco arquivos, `dur`/`probe` em
quatro, e as constantes de saída em cada um que renderiza. "A saída do canal é
1440p30" era convenção lembrada, não linha escrita.

Quatro verbos e um bloco de constantes:

    run       executa (ou grava, no modo seco)
    probe     largura, altura, fps, duração, tem áudio
    dur       duração em segundos
    loudness  a medida de loudnorm, com os cinco valores da 2ª passagem

**Modo seco.** `run` dentro de `seco()` não executa: grava o comando e devolve
uma resposta com cara de sucesso. O chamador não muda de caminho — é o que
permite conferir uma cadeia de filtros sem esperar um render.

    with ff.seco() as cmds:
        monta_a_aula(plano)
    for c in cmds:
        print(" ".join(c))

`probe`, `dur` e `loudness` continuam medindo dentro do `seco()`. Elas só leem, e
sem elas a cadeia não monta — quem precisa do tamanho do quadro para escrever o
filtro precisa dele também no modo seco.

**Fora do escopo, de propósito:** abstração sobre filtergraph. As cadeias de
filtros continuam escritas à mão em cada helper. Elas são a parte artística,
mudam por vídeo, e uma camada por cima delas teria interface tão complicada
quanto a implementação.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Iterator

# ---- Windows ------------------------------------------------------------------
#
# No Windows, o Python que escreve num cano (e o Claude Code lê tudo por cano)
# escreve em cp1252, e o primeiro "→" de um print estoura. Os filhos herdam o
# modo utf-8 pela variável; este processo, que já começou, troca a saída aqui.
# No Mac e no Linux já é utf-8 e nada muda.
os.environ.setdefault("PYTHONUTF8", "1")
for _fluxo in (sys.stdout, sys.stderr):
    if (hasattr(_fluxo, "reconfigure")
            and (_fluxo.encoding or "").lower().replace("-", "") != "utf8"):
        _fluxo.reconfigure(encoding="utf-8", errors="replace")


def caminho_no_filtro(p: Path | str) -> str:
    """O caminho de um arquivo pronto para entrar numa cadeia de filtros, sem aspas.

    `arnndn=m=`, `metadata=print:file=`, `subtitles=`: dentro do filtro, `:`
    separa opção e `\\` escapa. O caminho do Windows é `C:\\Users\\…`, e o ffmpeg
    lia `C` como o arquivo e o resto como outra opção. A barra vira `/`, que o
    ffmpeg aceita no Windows, e o resto escapa nos dois níveis do filtergraph: o
    da opção (`\\` `'` `:`) e o da cadeia (`\\` `'` `[` `]` `,` `;`). Caminho comum
    do Mac sai como entrou.
    """
    s = (p if isinstance(p, PurePath) else Path(p)).as_posix()
    for c in "\\':":
        s = s.replace(c, "\\" + c)
    for c in "\\'[],;":
        s = s.replace(c, "\\" + c)
    return s


# ---- saída padrão do canal --------------------------------------------------
#
# Trocar o encoder é editar aqui. Em nenhum outro lugar.

ALTURA = 1440                 # 1440p — a fonte é 16:10, o canvas 16:9 vem do plano
FPS = 30
PIX_FMT = "yuv420p"
CODEC_VIDEO = "libx264"
CODEC_AUDIO = "aac"
AUDIO_BITRATE = "192k"
AUDIO_RATE = "48000"

# Distância máxima entre quadros-chave, em quadros.
#
# O padrão do x264 é 250 — oito segundos a 30fps —, e quem paga por isso é a
# emenda: para trocar 0,4 s de vídeo ela precisa recodificar o grupo inteiro.
# Com grupo de 8 s, um efeito custa 8 s de encode; o ganho de copiar o resto
# quase evapora.
#
# O preço de encurtar é arquivo maior. Medido em 14/09/2026, 20 s a 1440p:
#
#   grupo 250 (8,3 s)  ..... referência
#   grupo 120 (4,0 s)  ..... +3,6%
#   grupo  60 (2,0 s)  ..... +12,0%
#   grupo  30 (1,0 s)  ..... +30,0%
#
# Dois segundos é o joelho da curva: recodifica quatro vezes menos que o padrão
# por 12% de tamanho. Trocar este número é uma linha, e a conta está aqui para
# quem quiser trocar.
GOP = 2 * FPS

# A escada de qualidade: final é o que vai pro ar, prévia dá pra avaliar,
# rascunho serve só pra conferir ponto de corte.
QUALIDADES: dict[str, tuple[str, str]] = {
    "final":    ("fast", "20"),
    "previa":   ("medium", "22"),
    "rascunho": ("ultrafast", "28"),
    # A composição roda uma geração depois do corte, então ela aperta menos:
    # o que ela comprime já passou por um encode.
    "composicao": ("fast", "18"),
    # Efeito (CRT, glitch) reencoda o vídeo inteiro por causa de poucos quadros:
    # mesmo alvo da composição, preset mais lento porque o arquivo sai maior.
    "efeito": ("medium", "18"),
    # Reel: o destino é o feed, que reencoda tudo de novo do outro lado. Aperta
    # um pouco mais que a composição de aula porque o ganho não sobrevive à
    # viagem.
    "reel": ("medium", "19"),
}
PRESET, CRF = QUALIDADES["final"]

# Padrão das redes: -14 LUFS integrado, -1 dBTP de pico, 11 LU de faixa.
# Bate com a normalização do YouTube, Instagram, TikTok e X.
LOUDNORM_I = -14.0
LOUDNORM_TP = -1.0
LOUDNORM_LRA = 11.0

# A trilha não disputa com a fala: ela entra 3 LU abaixo do alvo da voz e ainda
# é abaixada por volume no filtro. Alvo diferente porque a função é diferente,
# não porque alguém esqueceu de alinhar.
LOUDNORM_MUSICA = -17.0

def limitador(teto: float) -> str:
    """O alimiter que fica no teto. O padrão do ffmpeg liga `level`, que depois
    de limitar sobe tudo de volta até 0 dBFS: baixar o teto não baixava o pico,
    e uma aula publicada saiu com -0,6 dBTP. `latency` compensa o atraso de
    leitura adiantada do limitador, que senão desloca o som da imagem.

    Limita a 4× a taxa: o pico que importa é o ENTRE amostras (dBTP), e a 48 kHz o
    limitador não o vê. Em 29/09 um curto saiu com +1,0 dBTP com teto 0.91; a 192 kHz,
    o mesmo teto dava -0,6."""
    return (f"aresample={4 * int(AUDIO_RATE)},alimiter=limit={teto}:level=disabled:latency=true,"
            f"aresample={AUDIO_RATE}")


# Preparo do áudio para a transcrição: teto mais baixo e nivelamento dinâmico
# atrás. Não é som que alguém vá ouvir — é entrada de modelo, e o que importa é
# a consoante fraca não sumir.
TRANSCRICAO_AF = f"loudnorm=I={LOUDNORM_I}:TP=-1.5:LRA={LOUDNORM_LRA},dynaudnorm=f=150:g=15"


# ---- modo seco --------------------------------------------------------------

_gravando: list[list[str]] | None = None


@contextmanager
def seco() -> Iterator[list[list[str]]]:
    """Dentro do bloco, `run` grava em vez de executar. Devolve a lista gravada.

    Aninhar é erro: duas listas abertas ao mesmo tempo é o estado global que a
    costura A existe pra matar, entrando por outra porta.
    """
    global _gravando
    if _gravando is not None:
        raise RuntimeError("seco() aninhado — já existe um bloco gravando comandos")
    _gravando = []
    try:
        yield _gravando
    finally:
        _gravando = None


def _resposta_seca(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")


# ---- verbos -----------------------------------------------------------------


def run(cmd: list[str], *, quiet: bool = False, check: bool = True,
        capture: bool = False, binario: bool = False,
        cwd: Path | str | None = None) -> subprocess.CompletedProcess:
    """Executa um comando. Dentro de `seco()`, grava e devolve sucesso.

    `check=True` estoura com o comando na mensagem — um passo que falha diz qual
    passo foi, sem exigir a leitura do log inteiro.

    `binario=True` quando a saída NÃO é texto: rawvideo, PCM, qualquer pipe de
    mídia. Sem isso o decode em utf-8 estoura no primeiro byte alto — e estoura
    longe, no meio do subprocess, sem dizer que o problema era o modo de leitura.
    """
    cmd = [str(c) for c in cmd]
    if _gravando is not None:
        _gravando.append(cmd)
        return _resposta_seca(cmd)

    if not quiet:
        cabeca = " ".join(cmd[:6])
        print(f"  $ {cabeca}{' …' if len(cmd) > 6 else ''}")

    # O ffmpeg escreve progresso no stderr. Se ele está indo pra tela, deixa ir —
    # quem está olhando já viu o erro, e engolir o stderr mata a barra de progresso
    # de um render de vinte minutos. No modo calado ninguém viu nada, então a
    # mensagem de falha tem que carregar a ponta do log.
    pega_stderr = capture or quiet
    r = subprocess.run(
        cmd,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if pega_stderr else None,
        text=not binario,
        # a saída do ffmpeg é utf-8 em todo sistema; o padrão do Windows é cp1252
        encoding=None if binario else "utf-8",
        errors=None if binario else "replace",
        cwd=str(cwd) if cwd else None,
    )
    if check and r.returncode != 0:
        err = r.stderr
        if isinstance(err, bytes):
            err = err.decode("utf-8", "replace")
        detalhe = (err or "").strip().splitlines()[-3:]
        raise RuntimeError(
            f"passo falhou (código {r.returncode}): {' '.join(cmd[:8])}"
            + ("\n  " + "\n  ".join(detalhe) if detalhe else "")
        )
    return r


@dataclass(frozen=True)
class Sonda:
    largura: int
    altura: int
    fps: int
    duracao: float
    tem_audio: bool
    transferencia: str = ""     # a curva de transferência: pq/hlg = HDR

    @property
    def retrato(self) -> bool:
        return self.altura > self.largura

    @property
    def hdr(self) -> bool:
        return self.transferencia in ("smpte2084", "arib-std-b67")


def probe(path: Path | str) -> Sonda:
    """Mede o arquivo. Um vídeo sem faixa de áudio responde `tem_audio=False`,
    não estoura — o chamador decide o que fazer com isso."""
    path = Path(path)
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,width,height,r_frame_rate,color_transfer",
         "-show_entries", "format=duration",
         "-of", "json", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if r.returncode != 0:
        detalhe = (r.stderr or "").strip().splitlines()[-1:] or ["sem detalhe"]
        raise RuntimeError(f"ffprobe falhou em {path}: {detalhe[0]}")

    dados = json.loads(r.stdout or "{}")
    fluxos = dados.get("streams", [])
    video = next((s for s in fluxos if s.get("codec_type") == "video"), None)
    if video is None:
        raise RuntimeError(f"{path} não tem faixa de vídeo")

    num, den = (video.get("r_frame_rate") or "0/1").split("/")
    fps = round(float(num) / float(den)) if float(den) else 0
    duracao = float(dados.get("format", {}).get("duration") or 0.0)
    tem_audio = any(s.get("codec_type") == "audio" for s in fluxos)
    return Sonda(int(video["width"]), int(video["height"]), fps, duracao, tem_audio,
                 video.get("color_transfer") or "")


_LIBASS: bool | None = None


def tem_libass() -> bool:
    """Este ffmpeg sabe queimar legenda?

    O `brew install ffmpeg` do homebrew-core vem sem libass, e sem libass o filtro
    `subtitles` não existe. A mensagem que o ffmpeg devolve nesse caso fala em
    sintaxe ("No option name near ..."), o que manda quem lê consertar a linha de
    comando — o que falta é a biblioteca. Por isso a checagem é pelo nome do filtro,
    e não pelo erro.
    """
    global _LIBASS
    if _LIBASS is None:
        saida = subprocess.run(["ffmpeg", "-hide_banner", "-filters"],
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace").stdout
        _LIBASS = any(l.split()[1:2] == ["subtitles"] for l in saida.splitlines() if l.strip())
    return _LIBASS


def dur(path: Path | str) -> float:
    """Duração em segundos — de vídeo ou de som.

    Não passa pelo `probe`: duração é do formato, não da faixa de vídeo. Um wav
    de efeito sonoro tem duração e não tem imagem, e exigir imagem para responder
    quanto ele dura foi um erro que travou o CRT da aula.
    """
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    saida = (r.stdout or "").strip()
    if r.returncode != 0 or not saida:
        detalhe = (r.stderr or "").strip().splitlines()[-1:] or ["sem detalhe"]
        raise RuntimeError(f"não deu para medir a duração de {path}: {detalhe[0]}")
    return float(saida)


def legivel(path: Path | str) -> bool:
    """O ffprobe consegue abrir este arquivo?

    Existe para quem lida com arquivo quebrado de propósito — a recuperação do
    cache do CapCut desofusca bytes e precisa perguntar "já deu?" a cada tentativa,
    sem que a resposta "não" seja um erro.
    """
    try:
        probe(path)
        return True
    except Exception:
        return False


def loudness(path: Path | str) -> dict[str, str] | None:
    """Primeira passagem do loudnorm: mede e devolve os cinco valores que a
    segunda passagem precisa. `None` quando a medida não sai.

    Uma implementação só, de propósito. O `ebur128` que o vídeo de quadro usa dá
    só o LRA; quem quiser só o LRA lê o campo daqui, e aí as duas medidas não
    podem discordar.
    """
    filtro = f"loudnorm=I={LOUDNORM_I}:TP={LOUDNORM_TP}:LRA={LOUDNORM_LRA}:print_format=json"
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-nostats", "-i", str(path),
         "-af", filtro, "-vn", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    # o loudnorm imprime o JSON no stderr, no fim da corrida
    stderr = r.stderr or ""
    ini, fim = stderr.rfind("{"), stderr.rfind("}")
    if ini == -1 or fim <= ini:
        return None
    try:
        dados = json.loads(stderr[ini:fim + 1])
    except json.JSONDecodeError:
        return None
    preciso = {"input_i", "input_tp", "input_lra", "input_thresh", "target_offset"}
    return dados if preciso.issubset(dados) else None


# ---- montadores de argumento ------------------------------------------------


def loudnorm_filter(medida: dict[str, str] | None = None) -> str:
    """O filtro de loudnorm. Com medida, é a 2ª passagem — e ela carrega os cinco
    valores, senão é uma 1ª passagem cara que não normaliza direito."""
    base = f"loudnorm=I={LOUDNORM_I}:TP={LOUDNORM_TP}:LRA={LOUDNORM_LRA}"
    if not medida:
        return base
    return (f"{base}"
            f":measured_I={medida['input_i']}"
            f":measured_TP={medida['input_tp']}"
            f":measured_LRA={medida['input_lra']}"
            f":measured_thresh={medida['input_thresh']}"
            f":offset={medida['target_offset']}"
            f":linear=true")


def args_video(qualidade: str = "final", fps: int | None = FPS) -> list[str]:
    """Os argumentos de vídeo da saída. Trocar encoder é mexer nas constantes.

    `fps=None` não fixa a taxa: a saída herda a da entrada. Serve para o passo de
    composição, onde forçar a taxa remendaria um render de 24 para 30.
    """
    if qualidade not in QUALIDADES:
        raise KeyError(
            f"qualidade '{qualidade}' não existe. Disponíveis: {', '.join(QUALIDADES)}"
        )
    preset, crf = QUALIDADES[qualidade]
    args = ["-c:v", CODEC_VIDEO, "-preset", preset, "-crf", crf, "-pix_fmt", PIX_FMT,
            # `-g` aqui, e não em cada chamador: é o que deixa a emenda cortar
            # fino em vez de recodificar um grupo inteiro para trocar meio
            # segundo.
            "-g", str(GOP)]
    return args + (["-r", str(fps)] if fps else [])


def args_audio() -> list[str]:
    """Os argumentos de áudio da saída."""
    return ["-c:a", CODEC_AUDIO, "-b:a", AUDIO_BITRATE, "-ar", AUDIO_RATE]
