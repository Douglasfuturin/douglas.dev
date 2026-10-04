"""A fábrica: estilo, bruto e plano entram, o final sai.

Uma só, para aula e para reel. A orientação é campo do estilo, não nome de
módulo — o recorte do rosto não é do formato, e o vídeo de quadro, que tem molde
horizontal e nove verticais, deixa de nascer partido em dois.

    fabrica(plano)                     # renderiza e entrega
    fabrica(plano, seco=True)          # monta a cadeia e imprime, sem executar
    fabrica(plano, desde="desenho")    # reaproveita o que já está em disco

O plano diz o que é **daquele vídeo**: bruto, transcrição, janelas, drops,
conteúdo. O estilo diz o que vale para **todo vídeo daquele tipo**. Sobrescrita
de eixo no plano é o ajuste de um vídeo só; quando ela se repete, vira estilo
novo herdando.

**O modo seco é o ponto.** Ele monta a cadeia inteira e devolve os comandos, o
EDL calculado, o estilo resolvido e a pilha de recursos — sem esperar render. É
a única superfície de teste barata que um pipeline de vídeo tem.

Uso pela linha de comando:
    python helpers/fabrica.py <plano.json>
    python helpers/fabrica.py <plano.json> --seco
    python helpers/fabrica.py <plano.json> --desde desenho
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

import clean_edl
import estilo as es
import ff
import impressao
import regua

AQUI = Path(__file__).resolve().parent
PY = sys.executable
# A biblioteca de peças: núcleo (cor, letra, movimento), catálogo e render.
V2 = AQUI.parents[1] / "v2"


def _v2():
    """Import tardio: o kit do aluno não leva a biblioteca, e só o bloco da VSL
    e a legenda precisam dela."""
    if str(V2) not in sys.path:
        sys.path.insert(0, str(V2))
    import v2
    return v2

# As etapas, em ordem. `desde` escolhe onde começar — é o que absorve o programa
# separado que refazia só o layout de um reel.
ETAPAS = ["corte", "render", "desenho", "composicao", "trilha", "entrega"]

OBRIGATORIOS = ("estilo", "fonte", "slug")

# De que bruto cada estilo parte. Mandar uma live para um estilo de câmera é erro
# de entrada, não coisa para descobrir vinte minutos depois.
#
# `avatar` é o único que não parte de imagem: a fonte é a voz gravada, e o quadro
# só nasce depois que o HeyGen gera. Por isso a costura A dele roda no áudio.
#
# `banco` é o do criativo: as cenas já existem no banco, e a voz nasce do texto.
BRUTOS = {"live", "camera", "obs+celular", "board", "avatar", "banco"}

# Quanto custa, mais ou menos, processar um segundo de vídeo nesta máquina.
# Medido em 14/09/2026: 1440p30 num laptop de doze núcleos. Serve para comparar
# passos entre si; não é promessa de relógio.
SEGUNDOS_POR_SEGUNDO = 0.28

# Abaixo disto, o passo custa o vídeo inteiro e muda quase nada.
PISO_APROVEITAMENTO = 0.10


@dataclass(frozen=True)
class Passo:
    """Um passo da cadeia: o que ele roda, o que produz, e quanto do vídeo muda.

    `toca` é o que separa um passo caro e honesto de um passo caro e bobo. O
    render toca tudo e custa tudo; o glitch tocava 0,4 s e custava 16,5 s. Com o
    número declarado, o segundo se denuncia no modo seco em vez de virar uma
    sensação de que "o pipeline está lento".
    """
    nome: str
    cmd: list[str]
    saida: Path
    entradas: list[Path] = field(default_factory=list)
    # Segundos do vídeo que este passo muda. None = muda tudo, e aí custar o
    # vídeo inteiro é o preço certo.
    toca: float | None = None
    # O que a fábrica calculou em memória e este passo consome — o EDL, por
    # exemplo. TEM que entrar na impressão: ler de volta do disco devolve o
    # arquivo da corrida anterior, e mudar a janela passava despercebido.
    extra: str = ""
    # Arquivo que a fábrica calcula em memória e o comando lê do disco — o plano
    # de um bloco, o de uma receita. Escrito na execução, antes do comando, e
    # só se mudou: reescrever igual dá instante novo e invalida o cache.
    arquivo: tuple[Path, str] | None = None
    # Preenchido pela fábrica: o cache já tem este trabalho?
    pulavel: bool = False
    # Passo cujo custo não vem do tamanho do vídeo: um portão mede e sai, e mede
    # o mesmo tanto num vídeo de 30s ou de 30min. Sem isto ele entra na conta
    # como se processasse o vídeo inteiro, e ainda é marcado de suspeito por não
    # mudar nada — que é exatamente o trabalho dele.
    custo_fixo: float | None = None
    # Quanto vídeo este passo processa, quando não é o vídeo inteiro: um passo
    # de bloco da VSL custa o bloco, e é contra o bloco que ele é suspeito.
    sobre: float | None = None
    # Quem cobra por este passo (a ElevenLabs, a HeyGen). A fábrica não gasta:
    # passo que cobra sai impresso com o comando, e ninguém o executa sozinho.
    cobra: str = ""

    def custo(self, duracao: float) -> float:
        """Estimativa grosseira, em segundos. É conta de guardanapo e está dita
        assim — serve para comparar passos entre si, não para prometer relógio."""
        if self.custo_fixo is not None:
            return self.custo_fixo
        return max(0.1, (self.sobre or duracao) * SEGUNDOS_POR_SEGUNDO)

    def suspeito(self, duracao: float) -> bool:
        """Custa o vídeo inteiro e muda quase nada?

        É a regra que encontrou os dois passos caros deste projeto — o glitch
        gastava 16,5 s para trocar 0,4 s. Fica no código para encontrar o
        próximo, em vez de depender de alguém desconfiar de novo.
        """
        duracao = self.sobre or duracao
        if self.custo_fixo is not None or self.toca is None or duracao <= 0:
            return False
        return (self.toca / duracao) < PISO_APROVEITAMENTO


@dataclass
class Seco:
    """O que a fábrica devolve quando não executa."""
    estilo: es.Estilo
    edl: list[dict]
    passos: list[Passo] = field(default_factory=list)
    final: Path = Path()
    duracao: float = 0.0
    pulados: list[str] = field(default_factory=list)
    # Recurso que o estilo pediu e que não vai entrar, porque o plano não trouxe
    # o dado dele. Some calado é o defeito; dizer na tela é o conserto.
    mudos: list[tuple[str, str]] = field(default_factory=list)
    # Os finais que já existem e não foram feitos pela fábrica.
    alheio: list[Path] = field(default_factory=list)

    @property
    def comandos(self) -> list[list[str]]:
        return [p.cmd for p in self.passos]

    def custo_total(self) -> float:
        return sum(p.custo(self.duracao) for p in self.passos if not p.pulavel and not p.cobra)

    def imprime(self) -> None:
        e = self.estilo
        print(f"estilo   {e.nome}  ({e.orientacao}, parte de {e.bruto})")
        print(f"recursos {', '.join(e.recursos) or '(nenhum)'}")
        print(f"corte    {e.eixos['corte']['afinacao']} -> {len(self.edl)} trechos, "
              f"{sum(t['end'] - t['start'] for t in self.edl):.1f}s")
        print(f"final    {self.final}")
        for alheio in self.alheio:
            print(f"PERIGO   {alheio.name} já existe e não foi a fábrica que fez — "
                  f"a execução recusa; mude o slug ou tire o arquivo de lá")
        for recurso, campo in self.mudos:
            print(f"MUDO     {recurso}: o estilo pede e o plano não trouxe '{campo}' "
                  f"— esta camada não vai entrar")
        if self.pulados:
            print(f"cache    {len(self.pulados)} de {len(self.passos)} já feitos: "
                  f"{', '.join(self.pulados)}")

        print(f"\n{len(self.passos)} passos:")
        for p in self.passos:
            if p.pulavel:
                marca = "="
                custo = "já feito"
            elif p.cobra:
                marca = "$"
                custo = f"cobra: {p.cobra}"
            else:
                marca = "!" if p.suspeito(self.duracao) else " "
                custo = f"~{p.custo(self.duracao):.0f}s"
            muda = ("muda tudo" if p.toca is None
                    else f"muda {p.toca:.1f}s de {p.sobre or self.duracao:.0f}s")
            print(f" {marca} {p.nome:<24} {custo:>10}   {muda}")
            print(f"     {' '.join(p.cmd)}")

        falta = self.custo_total()
        suspeitos = [p.nome for p in self.passos
                     if p.suspeito(self.duracao) and not p.pulavel and not p.cobra]
        print(f"\n~{falta / 60:.1f} min estimados (conta de guardanapo)"
              + (f", {len(suspeitos)} passo(s) suspeito(s): {', '.join(suspeitos)}"
                 if suspeitos else ""))


def _rel(plano: dict, caminho: str | Path) -> Path:
    """Caminho do plano: relativo à pasta dele, não a de quem chamou."""
    p = Path(caminho)
    return p if p.is_absolute() else Path(plano.get("_dir", ".")) / p


def _lista(x) -> list:
    return [] if not x else (x if isinstance(x, list) else [x])


def _caminhos(plano: dict) -> dict:
    """Os arquivos que a cadeia lê do plano, a partir da pasta dele: a regra do editorial e do
    criativo. Antes eles iam crus para o Path() e valia a pasta de quem rodou o comando. O
    `_confere` achava a fonte (procura nas duas) e o corte caía em FileNotFoundError."""
    def acha(c):
        p = _rel(plano, c)
        # ponytail: plano antigo, escrito a partir da raiz do repositório (videos/troco), ainda roda de lá
        return str(p if p.exists() or not Path(c).exists() else Path(c))
    novo = {**plano}
    for k in ("fonte", "transcript", "legenda", "camada"):
        if novo.get(k):
            novo[k] = acha(novo[k])
    if novo.get("gerado"):
        novo["gerado"] = [acha(g) for g in _lista(novo["gerado"])]
    if novo.get("broll"):
        novo["broll"] = [{**b, "arquivo": acha(b["arquivo"])} if b.get("arquivo") else b
                         for b in novo["broll"]]
    return novo


def _confere(plano: dict) -> None:
    """Tudo o que dá para recusar antes do primeiro comando, recusado aqui."""
    obrig = ("estilo", "slug", "blocos") if plano.get("blocos") else OBRIGATORIOS
    faltando = [c for c in obrig if not plano.get(c)]
    if faltando:
        raise KeyError(
            f"o plano não tem: {', '.join(faltando)}. "
            f"Obrigatórios: {', '.join(obrig)}"
        )
    if plano.get("blocos"):
        for i, b in enumerate(plano["blocos"], 1):
            nome = b.get("nome") or f"#{i}"
            if not b.get("nome"):
                raise KeyError(f"o bloco #{i} não tem nome")
            if isinstance(b.get("pronto"), list):
                raise TypeError(f"bloco {nome}: `pronto` é o corte de um arquivo só")
            if b.get("janelas"):
                if not plano.get("fonte"):
                    raise KeyError(f"o bloco {nome} recorta janelas e o plano não tem "
                                   f"`fonte` — o bruto de onde elas saem")
                # o bloco pode recortar de outro bruto: o dia gravado em vários clipes
                fontes = _lista(b.get("fonte")) or [plano["fonte"]]
            else:
                fontes = (_lista(b.get("pronto")) or _lista(b.get("gerado"))
                          or _lista(b.get("fonte")))
            if not fontes:
                raise KeyError(f"o bloco {nome} não tem pronto, gerado nem fonte — "
                               f"não há de onde partir")
            for f in fontes + _lista(b.get("plano")) + _lista(b.get("voz")):
                if not _rel(plano, f).exists():
                    raise FileNotFoundError(f"bloco {nome}: não existe {_rel(plano, f)}")
    elif not plano.get("narracao") and not plano.get("trechos"):
        # Plano com `narracao` (ou os `trechos` do criativo) parte do texto: a voz,
        # que é a fonte, nasce no portão da ElevenLabs, e a cadeia para lá enquanto
        # ela não existir.
        fonte = Path(plano["fonte"])
        # relativa à pasta do plano também: é assim que o reel editorial lê todo caminho
        if not fonte.exists() and not _rel(plano, fonte).exists():
            raise FileNotFoundError(f"a fonte não existe: {fonte}")

    # A régua de desenho: uma aula que virou slide de texto é defeito, e ele
    # aparece aqui em vez de aparecer no gate de alunos depois do render.
    if plano.get("overlays"):
        v = regua.confere(plano["overlays"])
        if not v.passou:
            raise ValueError(f"a régua de desenho reprovou:\n  {v}")


def _dura(j) -> float:
    """Uma janela `[de, até]`, `[de, até, congela]` ou `[de, até, congela, velocidade]`.
    O terceiro número são os segundos de quadro parado no fim dela (carta que passou
    rápido demais pra ler); o quarto acelera o trecho (a demora com uma carta na mão)."""
    congela = float(j[2]) if len(j) > 2 else 0.0
    vel = float(j[3]) if len(j) > 3 else 1.0
    return (float(j[1]) - float(j[0])) / vel + congela


def _edl(plano: dict, e: es.Estilo) -> list[dict]:
    """A costura A, com a afinação que o estilo mandou."""
    if e.eixos["imagem"]["composicao"] == "editorial":
        # A voz sintética já sai sem ar morto, e o relógio do reel é o dela.
        return [{"source": plano["slug"], "start": 0.0, "end": float(plano.get("dur") or 0)}]
    if e.eixos["imagem"]["composicao"] == "cenas":
        # O criativo também: a voz inteira e a cauda. Sem a voz ainda, não há relógio.
        voz = _rel(plano, plano["fonte"])
        return [{"source": plano["slug"], "start": 0.0,
                 "end": ff.dur(voz) + _cr().CAUDA if voz.exists() else 0.0}]
    if plano.get("blocos"):
        # Na VSL em blocos o corte já aconteceu no áudio de cada take; cada
        # bloco entra inteiro, na ordem do plano.
        return [{"source": b["nome"], "start": 0.0,
                 "end": (ff.dur(_rel(plano, b["voz"])) + FOLGA_VOZ if b.get("voz") else
                         sum(_dura(j) for j in b["janelas"]) if b.get("janelas") else
                         sum(ff.dur(_rel(plano, f)) for f in
                             _lista(b.get("pronto")) or _lista(b.get("gerado"))
                             or _lista(b.get("fonte"))))}
                for b in plano["blocos"]]
    transcript = plano.get("transcript")
    fonte = Path(plano["fonte"])
    if not transcript:
        # Sem transcrição não há corte por palavra: o vídeo entra inteiro, e quem
        # corta por energia é uma afinação, não outro caminho.
        return [{"source": fonte.stem, "start": 0.0, "end": ff.dur(fonte)}]

    palavras = json.loads(Path(transcript).read_text(encoding="utf-8"))["words"]
    return clean_edl.cortar(
        palavras,
        drops=[tuple(d) for d in plano.get("drops", [])],
        janelas=[tuple(j) for j in plano.get("janelas", [])] or None,
        afinacao=e.afinacao(),
        fonte=fonte.stem,
    )


def _fonte_isolada(trabalho: Path) -> Path:
    """Onde mora o bruto com a voz isolada (`voz.tratamento = isola`)."""
    return trabalho / "fonte_isolada.mp4"


def _transcricao(voz: Path, fala: Path) -> Passo | None:
    """A transcrição da voz, sempre na cadeia, guardada pela impressão, que olha a voz: voz
    refeita refaz a transcrição, voz igual pula. Antes ela entrava só quando o arquivo faltava,
    e a voz nova saía cortada e legendada no tempo da velha.

    Só a de `transcripts/<voz>.json`, que é onde o transcribe.py escreve. Transcrição em outro
    caminho é do usuário, e ninguém escreve por cima dela. A correção à mão na de `transcripts/`
    também fica: o transcribe.py só refaz quando a voz é mais nova que ela."""
    if (fala.parent.name, fala.name) != ("transcripts", f"{voz.stem}.json"):
        return None
    return Passo(f"transcreve {voz.name}",
                 [PY, str(AQUI / "transcribe.py"), str(voz), "--model", "large-v3",
                  "--language", "pt", "--edit-dir", str(fala.parent.parent)],
                 fala, [voz], custo_fixo=60.0)


def _fala_no_corte(transcript: Path, trechos: list[dict]) -> str:
    """A transcrição no tempo do vídeo cortado. Palavra cujo meio o corte tirou sai."""
    doc = json.loads(transcript.read_text(encoding="utf-8"))
    palavras = [{**w, "start": tempo_de_saida(trechos, float(w["start"])),
                 "end": tempo_de_saida(trechos, float(w["end"]))}
                for w in doc["words"]
                if any(float(t["start"]) <= (float(w["start"]) + float(w["end"])) / 2
                       <= float(t["end"]) for t in trechos)]
    return json.dumps({**doc, "words": palavras}, ensure_ascii=False)


def tempo_de_saida(trechos: list[dict], t: float) -> float:
    """Converte tempo da FONTE para tempo do vídeo cortado.

    As âncoras de card são medidas assistindo a live, mas o card pousa no clipe
    já cortado. Sem esta conversão o card entra deslocado exatamente pelo
    silêncio que o corte tirou. Fora de qualquer trecho mantido, cai na emenda
    mais próxima — é onde o card faria menos estrago.
    """
    acumulado = 0.0
    for tr in trechos:
        ini, fim = float(tr["start"]), float(tr["end"])
        if ini - 0.05 <= t <= fim + 0.05:
            return round(acumulado + (t - ini), 3)
        acumulado += fim - ini
    if not trechos:
        return 0.0
    perto = min(range(len(trechos)),
                key=lambda i: min(abs(t - float(trechos[i]["start"])),
                                  abs(t - float(trechos[i]["end"]))))
    antes = sum(float(x["end"]) - float(x["start"]) for x in trechos[:perto])
    # Depois do fim do trecho vizinho, o card entra NA emenda. Mandá-lo para o
    # começo do trecho o joga segundos para trás, em cima de outra frase.
    if t > float(trechos[perto]["end"]):
        antes += float(trechos[perto]["end"]) - float(trechos[perto]["start"])
    return round(antes, 3)


def _composicao(plano: dict, e: es.Estilo, corrente: Path, trabalho: Path,
                desenho: Path | None = None) -> tuple[list[list[str]], Path]:
    """Monta o quadro vertical: recorte do rosto mais o desenho.

    O recorte é medido no quadro da LIVE, e o render pode ter reescalado a fonte
    — então o vídeo volta às dimensões da live antes de recortar. Pular isso tira
    o rosto do lugar, e foi o defeito que custou mais retrabalho no reel.
    """
    img = e.eixos["imagem"]
    modo = img["composicao"]
    if modo == "cheio" or not img["recorte"]:
        return [], corrente

    fonte = Path(plano["fonte"])
    sonda = ff.probe(fonte)
    lw, lh = sonda.largura, sonda.altura
    bw, bh = img["banda"]
    topo = trabalho / "rosto.mp4"
    brutos = [["ffmpeg", "-y", "-i", str(corrente), "-vf",
             f"scale={lw}:{lh},{img['recorte']},"
             f"scale={bw}:{bh}:force_original_aspect_ratio=increase,"
             f"crop={bw}:{bh},setsar=1,fps={img['fps']}",
             "-an", *ff.args_video("efeito", fps=None), str(topo)]]
    cmds = [Passo("recorte do rosto", brutos[0], topo, [corrente])]

    if desenho is None:
        return cmds, topo

    saida = trabalho / "composto.mp4"
    largura, altura = (1080, 1920)
    if modo == "pilha":
        fc = "[0:v][1:v]vstack=inputs=2[v]"
    else:   # sobreposicao — o desenho vem com chroma magenta por cima do rosto
        fc = (f"[0:v]pad={largura}:{altura}:0:0:color=0x1a1614[b];"
              f"[1:v]colorkey=0xff00ff:0.30:0.12[k];[b][k]overlay=0:0[v]")
    cmds.append(Passo("montagem do quadro",
                      ["ffmpeg", "-y", "-i", str(topo), "-i", str(desenho),
                       "-i", str(corrente), "-filter_complex", fc,
                       "-map", "[v]", "-map", "2:a",
                       *ff.args_video(img["qualidade"]), *ff.args_audio(),
                       "-shortest", str(saida)],
                      saida, [topo, desenho, corrente]))
    return cmds, saida


# A forma de um beat de b-roll. Obrigatório é o que o `broll_cmd` lê sem `get`;
# opcional é o que ele lê com padrão. `fonte` não é desenho: é a procedência do
# clipe, e viaja junto para o final poder dizer de onde cada quadro veio.
# `nota` é documental e ninguém a lê — é o lugar de escrever por que aquele clipe
# está ali, que é a única coisa que um plano não consegue dizer sozinho.
BEAT_OBRIGATORIOS = ("arquivo", "em", "dur")
BEAT_OPCIONAIS = ("anim", "largura", "altura", "x", "y", "fonte", "nota")

# O vocabulário de antes da fábrica, que sobreviveu num plano. Recusar sem
# ensinar a tradução manda quem escreveu adivinhar.
BEAT_VELHO = {"file": "arquivo", "start": "em", "scale_w": "largura",
              "x_off": "x", "y_off": "y", "note": "nota",
              # `sfx` não tem para onde ir: nenhum passo da cadeia lia esse
              # campo, então o som que ele pedia nunca tocou. Quem tem efeito
              # sonoro para colocar usa o `som.py`, depois da emenda.
              "sfx": "(nada lia este campo; use o som.py)"}


def confere_beats(lista: list[dict]) -> list[dict]:
    """Confere a forma de cada beat de b-roll, e devolve a lista intacta.

    Antes disto o erro aparecia como `KeyError: 'arquivo'` no meio da montagem do
    filtro, sem dizer qual beat nem o que era esperado.
    """
    validos = set(BEAT_OBRIGATORIOS) | set(BEAT_OPCIONAIS)
    for i, b in enumerate(lista, 1):
        velhas = {k: BEAT_VELHO[k] for k in b if k in BEAT_VELHO}
        if velhas:
            traducao = ", ".join(f"{v} -> {n}" for v, n in sorted(velhas.items()))
            raise KeyError(
                f"o beat #{i} usa o vocabulário antigo: {traducao}. "
                f"Campos de hoje: {', '.join(sorted(validos))}"
            )
        faltando = [c for c in BEAT_OBRIGATORIOS if c not in b]
        if faltando:
            raise KeyError(
                f"o beat #{i} não tem: {', '.join(faltando)}. "
                f"Obrigatórios: {', '.join(BEAT_OBRIGATORIOS)}"
            )
        sobrando = sorted(set(b) - validos)
        if sobrando:
            raise KeyError(
                f"o beat #{i} tem campo que não existe: {', '.join(sobrando)}. "
                f"Disponíveis: {', '.join(sorted(validos))}"
            )
    return lista


def procedencia(plano: dict) -> list[dict]:
    """O que entrou no final e não é seu.

    Só o que declara `fonte`: material próprio não precisa de licença, e listá-lo
    junto transformaria a declaração num inventário onde ninguém acha nada.
    """
    return [{"arquivo": b["arquivo"], "fonte": b["fonte"]}
            for b in (plano.get("broll") or []) if b.get("fonte")]


def broll_cmd(e: es.Estilo, corrente: Path, beats: list[dict], saida: Path) -> list[str]:
    """B-roll por cima da fala, entrando e saindo por deslize.

    Cada corte de apoio é um clipe com alpha que desliza para dentro e para fora.
    O deslocamento é escrito como expressão do tempo, e não como fade de posição,
    porque o overlay só aceita uma posição por quadro — a rampa TEM que estar na
    coordenada.
    """
    d = e.eixos["desenho"].get("broll_fade", 0.28)
    largura, altura = 1080, 674

    entradas = ["-i", str(corrente)]
    for b in beats:
        entradas += ["-i", str(b["arquivo"])]

    partes, anterior = [], "[0:v]"
    for i, b in enumerate(beats, 1):
        em, dur = float(b["em"]), float(b["dur"])
        fim, larg = em + dur, int(b.get("largura", largura))
        partes.append(
            f"[{i}:v]trim=0:{dur},setpts=PTS-STARTPTS,scale={larg}:-2,format=yuva420p,"
            f"fade=t=in:st=0:d={d}:alpha=1,fade=t=out:st={dur - d}:d={d}:alpha=1,"
            f"setpts=PTS-STARTPTS+{em}/TB[b{i}]"
        )

    for i, b in enumerate(beats, 1):
        em, dur = float(b["em"]), float(b["dur"])
        fim, anim = em + dur, b.get("anim", "top")
        x0, y0 = int(b.get("x", 0)), int(b.get("y", 0))
        larg = int(b.get("largura", largura))
        dentro = f"clip((t-{em})/{d}\\,0\\,1)"
        fora = f"clip((t-{fim}+{d})/{d}\\,0\\,1)"
        if anim == "top":
            alt = int(b.get("altura", altura))
            x, y = str(x0), f"{y0}+{-alt}*(1-{dentro})+{-alt}*{fora}"
        elif anim == "left":
            x, y = f"{x0}+{-larg}*(1-{dentro})+{-larg}*{fora}", str(y0)
        elif anim == "static":
            x, y = str(x0), str(y0)
        else:                                           # right
            x, y = f"{x0}+{largura}*(1-{dentro})+{largura}*{fora}", str(y0)
        alvo = f"[v{i}]" if i < len(beats) else "[v]"
        partes.append(f"{anterior}[b{i}]overlay=x='{x}':y='{y}':"
                      f"enable='between(t,{em - d},{fim + d})'{alvo}")
        anterior = f"[v{i}]"

    return ["ffmpeg", "-y", *entradas, "-filter_complex", ";".join(partes),
            "-map", "[v]", "-map", "0:a?",
            *ff.args_video(e.eixos["imagem"]["qualidade"], fps=None),
            "-c:a", "copy", str(saida)]


def ja_feito(passo: Passo) -> bool:
    """O cache já tem o trabalho deste passo?"""
    return impressao.pronto(passo.saida, _digital(passo))


def _digital(passo: Passo) -> str:
    return impressao.de(passo.cmd + ([passo.extra] if passo.extra else []),
                        _entradas(passo), helpers=_helpers(passo))


def _entradas(passo: Passo) -> list[Path]:
    """Todo arquivo que o comando lê entra na impressão.

    Curar essa lista à mão era o erro: três dos cinco passos que recebem arquivo
    por argumento — o explicador, o b-roll e a legenda — ficaram de fora, e o
    efeito é o pior que existe. O comando não muda, a impressão não muda, e o
    cache entrega o vídeo com o card velho sem avisar ninguém.

    A saída do próprio passo fica de fora: ela existe da corrida anterior, e o
    instante dela mudaria a impressão a cada corrida.
    """
    achados = list(passo.entradas)
    for arg in passo.cmd:
        if not isinstance(arg, str) or arg.startswith("-"):
            continue
        p = Path(arg)
        try:
            # Perguntar a um `filter_complex` de b-roll se ele é arquivo estoura
            # `File name too long` — são milhares de caracteres, e o sistema
            # recusa antes de responder que não existe. O que não dá para
            # perguntar não é entrada.
            if p == passo.saida or not p.exists() or p.is_dir():
                continue
        except OSError:
            continue
        if p not in achados:
            achados.append(p)
    return achados


def _helpers(passo: Passo) -> list[Path]:
    """Os arquivos de código que produzem esta saída.

    É isto que faz corrigir uma heurística refazer o que ela produziu, sem
    ninguém lembrar de subir um número de versão. Um passo que chama ffmpeg
    direto não tem helper: o comando já está na impressão inteiro.
    """
    return [Path(c) for c in passo.cmd
            if isinstance(c, str) and c.endswith(".py") and Path(c).exists()]


def _final(plano: dict, e: es.Estilo) -> Path:
    """Onde o final limpo mora. Não é campo livre: quem manda é o estilo."""
    pasta = e.eixos["entrega"]["pasta"]
    # As pastas de reel são planas: o final mora nelas direto, sem pasta de projeto.
    # videos/topo guarda os reels de topo de funil, e a pasta de cada um é a de trabalho.
    reel = pasta.endswith(("reels", "topo"))
    projeto = plano.get("projeto", "sem-projeto")
    if plano.get("saida"):
        # `saida` é a pasta dos projetos, no lugar de videos/
        raiz = _rel(plano, plano["saida"]).resolve()
        destino = raiz / Path(pasta).name if reel else raiz / projeto
    else:
        # Sem `saida`, a pasta do estilo manda. Antes ela só servia para testar
        # se terminava em "reels", e todo final caía em obs-optimize/<projeto>/,
        # fora de videos/ — nenhum plano real passava `saida`, os testes sim.
        destino = AQUI.parents[2] / pasta / ("" if reel else projeto)
    return destino / f"{plano['slug']}.mp4"


def _marca_final(final: Path) -> Path:
    return final.with_name(final.name + ".fabrica")


def _final_alheio(final: Path) -> bool:
    """Já existe um final com este nome, e não foi a fábrica que fez?

    Os finais publicados moram em videos/ e ficam fora do git. Em 26/09 o slug
    de um plano novo da VSL era o nome do vídeo que estava no ar, e o copy do
    fim da cadeia o apagaria sem aviso.
    """
    return final.exists() and not _marca_final(final).exists()


def _preparo_avatar(plano: dict, e: es.Estilo, trabalho: Path) -> tuple[list[Passo], Path]:
    """A costura A do bruto `avatar`: ela roda no ÁUDIO, antes de existir imagem.

    O apresentador da VSL é gerado pelo HeyGen a partir da voz real dele, então
    não há quadro para cortar na hora do corte. Trata a voz, apara as pausas com
    a mesma afinação que o estilo declara, e para no portão.

    **O portão não é burocracia: é o passo mais barato da cadeia.** 83% dos
    créditos de uma sessão foram embora no mesmo padrão, quatro vezes — gerar,
    descobrir que o áudio estava errado, gerar de novo. Medir antes custa um
    segundo; gerar custa crédito e cinco minutos.
    """
    fonte = Path(plano["fonte"])
    voz = trabalho / "voz.wav"
    limpo = trabalho / "voz_limpa.wav"
    t_limpo = trabalho / "transcript_limpo.json"
    c = e.eixos["corte"]

    passos = [p for p in [_transcricao(fonte, Path(plano["transcript"]))] if p]
    if e.eixos["voz"]["tratamento"] == "cru":
        # Voz sintética já sai limpa e no nível; o portão ainda mede o loudness.
        voz = fonte
    else:
        passos.append(Passo("voz tratada",
                            [PY, str(AQUI / "trata_voz.py"), str(fonte), "-o", str(voz),
                             "--alvo", str(e.eixos["voz"]["alvo"])],
                            voz, [fonte]))

    apara = [PY, str(AQUI / "apara_pausas.py"), str(voz),
             "--transcript", str(plano["transcript"]),
             "-o", str(limpo), "--out-transcript", str(t_limpo),
             "--afinacao", c["afinacao"]]
    # A afinação do estilo manda aqui também. Sem isto o corte da VSL e o corte
    # que a fábrica calcula seriam dois números diferentes com o mesmo nome.
    for botao, flag in (("sil_cut", "--sil-cut"), ("pause_keep", "--pause-keep"),
                        ("pad_out", "--pad-out")):
        if botao in c["ajuste"]:
            apara += [flag, str(c["ajuste"][botao])]
    for d in plano.get("drops", []):
        apara += ["--drop", str(d[0]), str(d[1])]
    # Emenda de dois takes no meio da frase ("Funciona" de um, "assim, se você decidir" do outro):
    # a borda cai em voz de propósito, e o plano diz isso em vez de a trava do apara barrar.
    if plano.get("drop_em_voz"):
        apara.append("--drop-em-voz")
    passos.append(Passo("apara pausas", apara, limpo, [voz]))

    # O whisper escreve a frase como devia ser e apaga o falso começo; o
    # clean_edl lê esse texto e não enxerga o tropeço. Um modelo que OUVE
    # reprova antes do portão — o V1 da VSL saiu com quatro gaguejadas e os
    # centavos do preço cortados. Sem chave da OpenRouter ele avisa e passa.
    ouvido = trabalho / "ouvido.json"
    passos.append(Passo("ouvido confere",
                        [PY, str(AQUI / "ouvido.py"), "confere", str(limpo), "--json", str(ouvido)],
                        ouvido, [limpo], toca=0.0, custo_fixo=30.0))

    portao = [PY, str(AQUI / "pre_voo.py"), str(limpo), "--transcript", str(t_limpo)]
    if plano.get("creditos"):
        portao += ["--creditos", str(plano["creditos"])]
    # O look é de quem gera: o plano escolhe; sem ele, o pre_voo lê o HEYGEN_LOOK.
    if plano.get("look"):
        portao += ["--look", str(plano["look"])]
    # Não produz arquivo: é portão, e sair 0 é o produto. A saída é um nome que
    # nunca existe, então ele roda toda vez — custa um segundo. Apontar para o
    # áudio limpo fazia o portão e o apara apagarem a marca de cache um do
    # outro: o apara refazia sempre, e o ouvido, que é pago, vinha atrás.
    passos.append(Passo("portão do HeyGen", portao, trabalho / "portão", [limpo],
                        toca=0.0, custo_fixo=1.0))
    return passos, limpo


# ---- a VSL em blocos ---------------------------------------------------------
#
# Um bloco é um take: voz própria, geração própria no HeyGen e um plano próprio
# (cards, peças, câmera, sons) com o tempo contado do zero dele. Era o que o
# monta.sh da VSL do Hermes fazia à mão, com a direção copiada em cada plano.

# O que um item de receita diz à fábrica, e não à receita.
RECEITA_ORQUESTRA = {"id", "de", "ate", "tira", "sem_legenda", "rosto"}


def _direcao(doc: dict, base: Path, e: es.Estilo, nome: str) -> dict:
    """O plano de um bloco com o que é do ESTILO preenchido, e os caminhos
    absolutos — ele vai ser lido de outra pasta, a de trabalho."""
    d = json.loads(json.dumps(doc))
    des = e.eixos["desenho"]
    d.setdefault("acento", _v2().token("ac", des["tema"]))
    for c in d.get("cards") or [] if des["fonte"] else []:
        c.setdefault("fonte", des["fonte"])
    if des["ritmo"] and "ritmo" not in d:
        d["ritmo"] = {"entrada": des["ritmo"][0], "stagger": des["ritmo"][1]}
    if not des["atras"]:
        atras = [c.get("t0") for c in d.get("cards") or [] if c.get("atras")]
        if atras:
            raise ValueError(
                f"bloco {nome}: card com texto atrás da pessoa em {atras} — o estilo "
                f"'{e.nome}' não põe nada atrás do sujeito. Ênfase é peso e escala."
            )
    for chave in ("brolls", "sons"):
        for item in d.get(chave) or []:
            if "arquivo" in item and (base / item["arquivo"]).exists():
                item["arquivo"] = str((base / item["arquivo"]).resolve())
    return d


def _peca(item: dict, e: es.Estilo, pasta: Path) -> Passo:
    """Uma peça pedida pelo nome do catálogo, renderizada no tema do estilo.

    O arquivo leva o hash do pedido no nome: a mesma peça com o mesmo texto não
    é renderizada duas vezes, e texto novo nunca cai em cima do velho.
    """
    import hashlib
    from urllib.parse import parse_qsl
    v2 = _v2()
    peca = item.pop("peca")
    q = item.pop("q", {})
    pares = [f"{k}={v}" for k, v in (q.items() if isinstance(q, dict)
                                     else parse_qsl(q.lstrip("?"), keep_blank_values=True))]
    ar = item.pop("ar", None)
    tema = item.pop("tema", None) or e.eixos["desenho"]["tema"]
    if v2.acha(peca)[0]["camadas"] and not e.eixos["desenho"]["atras"]:
        raise ValueError(f"a peça {peca} põe texto atrás da pessoa, e o estilo "
                         f"'{e.nome}' não põe nada atrás do sujeito")
    chave = hashlib.blake2b(json.dumps([peca, pares, ar, tema]).encode(),
                            digest_size=4).hexdigest()
    saida = pasta / f"{peca}-{chave}.mov"
    cmd = [PY, str(V2 / "v2.py"), "render", peca, *pares, "--tema", tema, "--out", str(saida)]
    if ar:
        cmd += ["--ar", ar]
    item["arquivo"] = str(saida)
    item["_peca"] = peca                    # o `tira` da receita acha pelo nome
    # Sem `alfa` o captions_viral perde o alpha e a peça transparente cobre o
    # vídeo com um retângulo preto. Quem sabe se ela é transparente é o catálogo.
    item.setdefault("alfa", bool(v2.acha(peca)[0]["alfa"]))
    # O nome do arquivo guarda o pedido; o desenho está no HTML e no núcleo, e
    # é por eles que mexer numa peça refaz o render.
    desenho = [V2 / v2.acha(peca)[0]["arquivo"], *sorted((V2 / "nucleo").glob("direcao-v2.*"))]
    return Passo(f"peça {peca}", cmd, saida, desenho, custo_fixo=10.0)


def _camera_parada(cams: list[dict], janelas: list[tuple[float, float]]) -> list[dict]:
    """Corta a câmera nas bordas das janelas; dentro delas, quadro parado — zoom
    por cima de receita corta o texto dela."""
    out = []
    for c in cams:
        a, z = float(c["t0"]), float(c["t1"])
        cortes = sorted({a, z, *[x for j in janelas for x in j if a < x < z]})
        for x, y in zip(cortes, cortes[1:]):
            dentro = any(j0 <= x and y <= j1 for j0, j1 in janelas)
            out.append({"t0": x, "t1": y, "zoom": [1.0, 1.0], "ease": "reta"} if dentro
                       else {**c, "t0": x, "t1": y})
    return out


def _receitas(plano: dict, b: dict, base: Path, doc: dict, e: es.Estilo,
              pasta: Path) -> tuple[list[Passo], Path]:
    """Janelas do bloco em que o rosto sem fundo volta sobre a placa, com a
    receita desenhada em volta dele. A boca da receita foi gerada com o mesmo
    trecho de áudio, então só a IMAGEM é trocada; o som fica o da base."""
    img = e.eixos["imagem"]
    placa = _rel(plano, b.get("placa") or plano["placa"])
    passos, janelas, partes = [], [], []
    for m in sorted(b["receitas"], key=lambda m: m["de"]):
        dur = round(m["ate"] - m["de"], 3)
        r = {k: v for k, v in m.items() if k not in RECEITA_ORQUESTRA}
        # O plano da receita é lido da pasta de trabalho: todo caminho que ele
        # cita (captura, take_b) tem que sair absoluto daqui.
        for k, v in list(r.items()):
            if isinstance(v, str) and ("/" in v or "." in v) and _rel(plano, v).exists():
                r[k] = str(_rel(plano, v).resolve())
        rosto = _rel(plano, m["rosto"]).resolve()
        rp = {"fonte": str(rosto), "placa": str(placa.resolve()),
              "receitas": [{**r, "de": 0.0, "ate": dur}]}
        texto = json.dumps(rp, ensure_ascii=False, indent=1)
        pj, mp4 = pasta / f"{m['id']}.plano.json", pasta / f"{m['id']}.mp4"
        citados = [Path(v) for v in r.values() if isinstance(v, str) and Path(v).is_absolute()]
        desenho = [V2 / "nucleo" / n for n in ("receita.html", "receitas-core.js", "legendas-core.js")]
        passos.append(Passo(f"receita {m['id']}",
                            [PY, str(AQUI / "receita_para_video.py"), str(pj), str(mp4)],
                            mp4, [rosto, placa, *citados, *desenho,
                                  AQUI / "receitas_prep.py", AQUI / "som.py"],
                            extra=texto, arquivo=(pj, texto)))
        janelas.append((m["de"], m["ate"]))
        partes.append((m, mp4))
        # os sons da receita: o som.py lê os cues dela quando o arquivo existir
        doc.setdefault("cues_de", []).append({"arquivo": str(mp4), "t0": m["de"], "t1": m["ate"]})

    for (a, z), (a2, _) in zip(janelas, janelas[1:]):
        if a2 < z:
            raise ValueError(f"bloco {b['nome']}: receitas sobrepostas em {a2:.2f}s — "
                             f"a emenda pularia a base e o vídeo sairia maior que o áudio")
    # Peça pedida pelo nome ainda não tem arquivo: o `tira` acha pelo nome dela.
    nome_de = lambda x: x.get("peca") or Path(x["arquivo"]).name
    tira = {n for m in b["receitas"] for n in m.get("tira", [])}
    doc["brolls"] = [x for x in doc.get("brolls") or [] if nome_de(x) not in tira]
    for x in doc["brolls"]:
        a, z = float(x["t0"]), float(x["t1"])
        if any(a < j1 and j0 < z for j0, j1 in janelas):
            raise ValueError(f"bloco {b['nome']}: b-roll {nome_de(x)} "
                             f"em cima de receita — tire com `tira`")
    doc["camera"] = _camera_parada(doc.get("camera") or [], janelas)
    mudas = [(m["de"], m["ate"]) for m in b["receitas"] if m.get("sem_legenda")]
    doc["cards"] = [c for c in doc.get("cards") or []
                    if not any(float(c["t0"]) < z and a < float(c["t1"]) for a, z in mudas)]

    # A base com cada janela trocada pelo vídeo da receita. A cauda vai até o
    # fim sem precisar saber a duração, que no modo seco ainda não existe.
    w, h = (1080, img["altura"]) if e.vertical else (img["altura"] * 16 // 9, img["altura"])
    ins, fc, t = ["-i", str(base)], [], 0.0
    for k, (m, mp4) in enumerate(partes, 1):
        ins += ["-i", str(mp4)]
        if m["de"] > t:
            fc.append(f"[0:v]trim={t:.3f}:{m['de']:.3f},setpts=PTS-STARTPTS[p{len(fc)}]")
        # a receita pode sair um quadro mais longa: corta na duração da janela
        fc.append(f"[{k}:v]fps={img['fps']},scale={w}:{h},setsar=1,"
                  f"trim=0:{m['ate'] - m['de']:.3f},setpts=PTS-STARTPTS[p{len(fc)}]")
        t = m["ate"]
    fc.append(f"[0:v]trim=start={t:.3f},setpts=PTS-STARTPTS[p{len(fc)}]")
    grafo = ";".join(fc) + ";" + "".join(f"[p{i}]" for i in range(len(fc))) \
        + f"concat=n={len(fc)}:v=1:a=0[v]"
    saida = pasta / "base.mp4"
    passos.append(Passo("receitas na base",
                        ["ffmpeg", "-y", *ins, "-filter_complex", grafo, "-map", "[v]",
                         "-map", "0:a", *ff.args_video(fps=img["fps"]), "-c:a", "copy", str(saida)],
                        saida, [base] + [mp4 for _, mp4 in partes],
                        toca=sum(m["ate"] - m["de"] for m, _ in partes)))
    return passos, saida


# Silêncio depois da última palavra de um bloco de voz gravada, antes do corte.
FOLGA_VOZ = 0.3


def _recorte(plano: dict, e: es.Estilo, b: dict, tb: Path, trabalho: Path,
             feitas: set) -> tuple[list[Passo], Path, float]:
    """O bloco que sai de janelas do bruto: um EDL só dele, pelo mesmo render.

    A voz é isolada uma vez para o bruto inteiro (`feitas` guarda), e todo
    recorte lê a fonte limpa — isolar janela por janela pagaria o serviço de novo.
    """
    img, passos = e.eixos["imagem"], []
    fonte = _rel(plano, b.get("fonte") or plano["fonte"])
    janelas = b["janelas"]
    if b.get("fonte") and e.eixos["voz"]["tratamento"] == "isola":
        raise ValueError(f"bloco {b['nome']}: a voz isolada é a do bruto do plano; "
                         f"bloco com `fonte` própria não isola")
    voz = _rel(plano, b["voz"]) if b.get("voz") else None
    if voz:
        # Bloco de voz gravada à parte: a imagem dura o que a fala dura, a
        # partir do início da primeira janela.
        a0 = float(janelas[0][0])
        janelas = [[a0, round(a0 + ff.dur(voz) + FOLGA_VOZ, 3)]]
    if e.eixos["voz"]["tratamento"] == "isola":
        isolada = _fonte_isolada(trabalho)
        if isolada not in feitas:
            feitas.add(isolada)
            passos.append(Passo("isola a voz", [PY, str(AQUI / "isola_voz.py"), str(fonte),
                                                "-o", str(isolada)], isolada, [fonte]))
        fonte = isolada
    doc = {"version": 1, "sources": {"bruto": str(fonte)},
           "ranges": [{"source": "bruto", "start": j[0], "end": j[1],
                       **({"congela": j[2]} if len(j) > 2 and j[2] else {}),
                       **({"velocidade": j[3]} if len(j) > 3 and j[3] != 1 else {}),
                       **({"recorte": b["recorte"]} if b.get("recorte") else {})} for j in janelas],
           "grade": e.eixos["graduacao"]["preset"], "overlays": [],
           "total_duration_s": round(sum(_dura(j) for j in janelas), 2)}
    texto = json.dumps(doc, ensure_ascii=False, indent=2)
    base, edl = tb / "trecho.mp4", tb / "edl.json"
    # O volume é do vídeo inteiro, não do bloco: normalizado sozinho, um bloco
    # sem fala subia o resto de conversa 26 dB e virava ruído. Quem acerta o
    # episódio é o `normalizar` (ou a cama de trilha) depois da emenda.
    cmd = [PY, str(AQUI / "render.py"), str(edl), "-o", str(base),
           "--height", str(img["altura"]), "--fps", str(img["fps"]), "--no-loudnorm"]
    # `voz.por_bloco`: a fala do próprio bloco passa pela mesma cadeia da voz gravada à parte
    # (trata_voz) e sai no mesmo nível. No longo do semanal cada bloco vinha de um microfone
    # (casa, loja, fone) e a cama da trilha passava por cima dos mais baixos.
    nivela = not (b.get("mudo") or voz) and e.eixos["voz"].get("por_bloco")
    if b.get("mudo") or voz:
        cmd.append("--mudo")
    elif e.eixos["voz"]["tratamento"] == "realce" and not nivela:
        cmd.append("--voice-enhance")
    dur = doc["total_duration_s"]
    if voz and e.eixos["voz"]["tratamento"] == "cru":
        # Voz sintética já chega limpa e no nível, como no `_preparo_avatar`: a
        # cadeia do microfone por cima trataria o que não tem ruído.
        tratada = voz
    elif voz:
        tratada = tb / "voz.wav"
        passos.append(Passo(f"{b['nome']}: trata a voz",
                            [PY, str(AQUI / "trata_voz.py"), str(voz), "-o", str(tratada)],
                            tratada, [voz]))
    passos.append(Passo(f"{b['nome']}: recorte", cmd, base, [fonte], extra=texto,
                        arquivo=(edl, texto), sobre=dur))
    if nivela:
        tratada = tb / "voz.wav"
        passos.append(Passo(f"{b['nome']}: trata a voz",
                            [PY, str(AQUI / "trata_voz.py"), str(base), "-o", str(tratada)],
                            tratada, [base]))
    if voz or nivela:
        com_voz = tb / "trecho_voz.mp4"
        passos.append(Passo(f"{b['nome']}: voz do bloco",
                            [PY, str(AQUI / "poe_voz.py"), str(base), str(tratada),
                             "-o", str(com_voz)], com_voz, [base, tratada], sobre=dur))
        base = com_voz
    return passos, base, dur


def _blocos(plano: dict, e: es.Estilo, trabalho: Path,
            inicio: int) -> tuple[list[Passo], Path, bool]:
    """Cada bloco até o corte pronto dele, e os cortes emendados.

    Devolve (passos, corrente, completo). Incompleto = algum bloco ainda não foi
    gerado: a cadeia desse bloco para no portão e a emenda não entra.
    """
    img = e.eixos["imagem"]
    passos: list[Passo] = []
    cortes, falta, feitas = [], [], set()
    for b in plano["blocos"]:
        nome, tb = b["nome"], trabalho / b["nome"]
        if b.get("pronto"):
            cortes.append(_rel(plano, b["pronto"]))
            continue
        if b.get("janelas"):
            rec, base, dur = _recorte(plano, e, b, tb, trabalho, feitas)
            passos += rec
        elif not b.get("gerado"):
            if inicio <= ETAPAS.index("render"):
                preparo, _ = _preparo_avatar(
                    {**b, "fonte": str(_rel(plano, b["fonte"])),
                     "transcript": str(_rel(plano, b["transcript"])),
                     "creditos": plano.get("creditos"),
                     "look": b.get("look") or plano.get("look")}, e, tb)
                passos += [replace(p, nome=f"{nome}: {p.nome}") for p in preparo]
            falta.append(nome)
            continue
        else:
            gerado = [_rel(plano, g) for g in _lista(b["gerado"])]
            dur = sum(ff.dur(g) for g in gerado)
            base = gerado[0]
            if len(gerado) > 1:
                base = tb / "gerado.mp4"
                passos.append(Passo(f"{nome}: emenda do gerado",
                                    [PY, str(AQUI / "junta.py"), *map(str, gerado),
                                     "-o", str(base), "--fps", str(img["fps"])], base,
                                    gerado, sobre=dur))

        bp = _rel(plano, b["plano"]) if b.get("plano") else None
        doc = _direcao(json.loads(bp.read_text(encoding="utf-8")) if bp else {"cards": []},
                       bp.parent if bp else tb, e, nome)
        if b.get("vinheta"):
            # o jingle cantado abre o bloco; quem abaixa a cama embaixo dele é o _fala
            doc.setdefault("sons", []).append(
                {"arquivo": str(_rel(plano, b["vinheta"])), "t": 0.0, "ganho": 1.0})
        if b.get("receitas"):
            rec, base = _receitas(plano, b, base, doc, e, tb)
            passos += [replace(p, nome=f"{nome}: {p.nome}", sobre=dur) for p in rec]
        for item in doc.get("brolls") or []:
            if "peca" in item:
                passo = _peca(item, e, trabalho / "pecas")
                if passo.saida not in feitas:
                    feitas.add(passo.saida)
                    passos.append(passo)

        texto = json.dumps(doc, ensure_ascii=False, indent=1)
        pj, leg, corte = tb / "plano.json", tb / "legenda.mp4", tb / "corte.mp4"
        # O texto do plano entra na impressão, mas os arquivos que ele CITA não:
        # uma peça refeita no mesmo caminho passaria batida e o bloco sairia com
        # o painel velho.
        citados = [Path(x["arquivo"]) for x in doc.get("brolls") or []]
        sons = [*citados, *[Path(x["arquivo"]) for x in doc.get("cues_de") or []]]
        sons += [q.with_suffix(suf) for q in list(sons) for suf in (".json", ".cues.json")]
        sons += [Path(x["arquivo"]) for x in doc.get("sons") or [] if "arquivo" in x]
        sons.append(V2 / "sfx" / "sfx.json")
        passos.append(Passo(f"{nome}: legenda, peças e câmera",
                            [PY, str(AQUI / "captions_viral.py"), str(base), "--plan", str(pj),
                             "-o", str(leg)], leg, [base, *citados], extra=texto,
                            arquivo=(pj, texto), sobre=dur))
        som = [PY, str(AQUI / "som.py"), str(leg), "--plan", str(pj), "-o", str(corte),
               "--mestre", str(e.eixos["efeito"]["sfx_db"])]
        if b.get("corta"):
            som += ["--corta", str(b["corta"])]
        passos.append(Passo(f"{nome}: som", som, corte, [leg, *sons], extra=texto, sobre=dur))
        cortes.append(corte)

    if falta:
        return passos, trabalho, False
    if len(cortes) == 1:
        return passos, cortes[0], True
    corrente = trabalho / "juntado.mp4"
    # junta.py e não `ffmpeg -f concat`: o HeyGen entrega a 25 fps, o projeto
    # roda a 30, e o concat mantém a taxa do primeiro arquivo.
    passos.append(Passo("emenda dos blocos",
                        [PY, str(AQUI / "junta.py"), *map(str, cortes), "-o", str(corrente),
                         "--fps", str(img["fps"])], corrente, cortes))
    return passos, corrente, True


def _reel():
    """Import tardio, como o `_v2`: o reel editorial desenha com tools/v2, que o kit não leva."""
    import reel_editorial
    return reel_editorial


def _args_cama(e: es.Estilo) -> list[str]:
    """Os botões da cama que o estilo mudou, em flags do mixa. O que é None fica no padrão dele."""
    t, args = e.eixos["trilha"], []
    for botao, flag in (("cama", "--cama"), ("duck", "--duck-ratio"), ("fade_fim", "--fade-fim")):
        if t[botao] is not None:
            args += [flag, str(t[botao])]
    return args


# Em que etapa cada passo do reel editorial mora: é o que faz o `--desde` valer aqui também.
ETAPA_EDITORIAL = {"take": "render", "pessoa": "render", "camadas": "desenho", "pecas": "desenho",
                   "compor": "composicao", "junta": "composicao", "degraus": "composicao", "som": "trilha",
                   "yt": "trilha",
                   "capa": "entrega", "folha": "entrega"}


def _editorial(plano: dict, e: es.Estilo, trabalho: Path,
               inicio: int) -> tuple[list[Passo], Path | None]:
    """O reel editorial (o molde do Nick, a peça e_editorial): voz sintética, avatar no cartão ou
    cheio sobre o escritório, painel e peças por cima. Quem monta é o `reel_editorial.py`; aqui
    entra o que é do estilo, a conferência das regras e a ordem dos passos.

    O que custa dinheiro não roda: a voz e o avatar faltando viram passo que cobra, impresso
    com o comando, e a cadeia para ali."""
    re_ = _reel()
    img, tr = e.eixos["imagem"], e.eixos["trilha"]
    raiz = AQUI.parents[2]
    doc = {**plano, "_dir": str(Path(plano.get("_dir", ".")).resolve()),
           "trilha": {"faixa": tr["faixa"], "pedacos": tr["pedacos"]},
           "_estilo": {"nome": e.nome, "fundo": img["fundo"] and str(raiz / img["fundo"]), "costura": img["costura"],
                       "legenda_ig": e.eixos["desenho"]["legenda_ig"], "sintese": e.eixos["voz"]["sintese"],
                       # só quem declara zona (ou tema que não é o claro) leva: a impressão dos outros reels não muda
                       **{k: e.eixos["desenho"][k] for k in ("zona", "botoes") if e.eixos["desenho"][k]},
                       **({"tema": e.eixos["desenho"]["tema"]} if e.eixos["desenho"]["tema"] != "claro" else {}),
                       "alvo": e.eixos["voz"]["alvo"], "sfx_db": e.eixos["efeito"]["sfx_db"],
                       "mixa": _args_cama(e)}}
    erros = re_.confere(doc)
    if erros:
        raise ValueError("o reel editorial reprovou antes do render:\n  " + "\n  ".join(erros))

    pj = trabalho / "reel.json"
    texto = json.dumps(doc, ensure_ascii=False, indent=1)
    helper = str(AQUI / "reel_editorial.py")
    rel = lambda c: _rel(plano, c)
    voz = rel(plano["fonte"])
    fala = Path(doc["_dir"]) / "transcripts" / f"{voz.stem}.json"
    webm = rel(plano["avatar"]["arquivo"])
    mapa = [rel(plano["avatar"]["mapa"])] if plano["avatar"].get("mapa") else []
    fim_yt = Path(doc["_dir"]) / "vozes" / "fim-yt.wav"

    def passo(nome: str, saida: Path, entradas=(), chaves=(), **kw) -> Passo:
        # Cada passo leva na impressão só o pedaço do plano que ele lê: trocar um
        # som não refaz o take. O reel.json inteiro chega pelo `arquivo`.
        extra = json.dumps({k: doc.get(k) for k in (*chaves, "_estilo")}, ensure_ascii=False, sort_keys=True)
        return Passo(nome, [PY, helper, nome, str(trabalho)], saida, [*entradas], extra=extra,
                     arquivo=(pj, texto), **kw)

    def cobra(nome: str, quem: str, cmd: list[str], saida: Path) -> Passo:
        return Passo(nome, cmd, saida, arquivo=(pj, texto), cobra=quem, custo_fixo=0.0, toca=0.0)

    # O material é da pasta do vídeo, não do trabalho. A captura e o avatar saem quando faltam;
    # a transcrição segue a voz.
    passos: list[Passo] = []
    if not voz.exists():
        return [cobra("narração", "ElevenLabs", [PY, helper, "voz", str(trabalho)], voz)], None
    falta = [c for c in re_.capturas(doc) if not c.exists()]
    if falta:
        passos.append(passo("captura", falta[0], custo_fixo=30.0))
    passos.append(_transcricao(voz, fala))
    if not webm.exists():
        geracao = Path(doc["_dir"]) / "avatar" / "geracao.wav"
        passos.append(passo("heygen", geracao, [voz], ("base", "dur"), custo_fixo=2.0))
        passos.append(cobra("avatar", "HeyGen", ["heygen:", str(geracao), "->", str(webm)], webm))
        return passos, None
    yt = plano.get("youtube")
    if yt and not fim_yt.exists():
        passos.append(cobra("frase do YouTube", "ElevenLabs", [PY, helper, "yt_voz", str(trabalho)], fim_yt))
    elif yt:
        passos.append(_transcricao(fim_yt, fala.parent / f"{fim_yt.stem}.json"))

    t = trabalho
    cenas = [rel(s.get("cena") or s["divide"]) for s in plano["base"] if "cena" in s or "divide" in s]
    # o cenário gerado atrás do rosto (`fundo` que é arquivo): trocar o arquivo refaz o take
    cenas += [rel(s["fundo"][1:]) for s in plano["base"] if str(s.get("fundo", "")).startswith("@")]
    faixa = [re_.faixa_de(tr["faixa"])]
    # o que as peças e as imagens citam: recapturar uma página refaz a peça que a mostra
    citados = [rel(v[1:]) for x in plano.get("pecas", []) for v in (x.get("q") or {}).values()
               if isinstance(v, str) and v.startswith("@") and not v.startswith("@foco:")]
    citados += [rel(x["arquivo"]) for x in plano.get("imagens", [])]
    citados += [Path(doc["_dir"]) / "_trabalho" / "cap" / "focos.json"] if "@foco:" in json.dumps(plano.get("pecas")) else []
    capa = []
    if plano.get("capa"):
        # A foto, o logo e os lados que são arquivo: trocar a foto mantendo o nome refaz a capa.
        # `@x` é da pasta do vídeo; o resto, se for arquivo, é da pasta da peça.
        c = plano["capa"]
        arqs = [rel(c["foto"])] if c.get("foto") else []
        arqs += [rel(c["cena"][0])] if c.get("cena") else []
        for v in [c.get("logo", ""), *c.get("lados", "").split(",")]:
            arqs += [rel(v[1:])] if v.startswith("@") else [V2 / "pecas" / v] if v and (V2 / "pecas" / v).is_file() else []
        capa = [passo("capa", t / "capa-nick.jpg", arqs, chaves=("capa",), custo_fixo=15.0)]
    render = [
        passo("take", t / "take.mp4", [webm, *mapa, Path(doc["_estilo"]["fundo"]), *cenas], ("base", "avatar", "dur")),
        passo("pessoa", t / "pessoa.mov", [webm, *mapa], ("base", "avatar", "dur")),
        passo("camadas", t / "ed.json", [voz, fala], ("r", "css", "junta", "dur")),
        # a capa antes das peças: a que mostra a capa no vídeo (o r_capa) cita o arquivo dela
        *capa,
        passo("pecas", t / "pecas.json", [voz, *citados], ("pecas",), custo_fixo=10.0 * len(plano.get("pecas", []))),
        passo("compor", t / "composto.mp4", [t / "take.mp4", t / "pessoa.mov", t / "ed.json"]),
        passo("junta", t / "imagem_voz.mp4", [t / "composto.mp4", t / "pecas.json", voz, *citados],
              ("imagens", "pecas", "dur")),
    ]
    imagem = t / "imagem_voz.mp4"
    if plano.get("degraus"):
        # o mesmo take com 0, 1… N skills, montado nas trocas: refaz se o take, a voz ou as peças mudaram
        imagem = t / "imagem_degraus.mp4"
        render.append(passo("degraus", imagem, [t / "imagem_voz.mp4", t / "pecas.json", webm, *mapa, voz, fala],
                            ("degraus", "base", "avatar", "r", "pecas", "imagens", "dur", "junta", "css")))
    render.append(passo("som", t / "final.mp4", [imagem, voz, *faixa], ("sons", "trilha", "dur", "fechos")))
    if yt and fim_yt.exists():
        render.append(passo("yt", t / "final-yt.mp4", [t / "imagem_voz.mp4", voz, fim_yt, fala, *faixa],
                            ("youtube", "sons", "trilha", "dur", "junta")))
    render.append(passo("folha", t / "folha-1fps.png", [t / "final.mp4"], custo_fixo=5.0))
    passos += [p for p in render if ETAPAS.index(ETAPA_EDITORIAL[p.nome]) >= inicio]
    return passos, t / "final.mp4"


def _cr():
    """Import tardio, como o `_reel`: só o criativo precisa do acabamento de filmagem achada."""
    import criativo
    return criativo


# Em que etapa cada passo do criativo mora: é o que faz o `--desde` valer aqui também.
ETAPA_CRIATIVO = {"base": "render", "cards": "desenho", "legenda": "desenho"}


def _cenas_do_lote(plano: dict) -> Passo | None:
    """As cenas do `lote` do plano que ainda não estão no disco: saem da Higgsfield, custam, e viram
    passo que cobra, com a estimativa pela tabela. Quem gera é o `lote.py`, que pergunta o preço à
    API antes de gastar e põe a ficha de cada cena no cenas.json da pasta do lote."""
    if not plano.get("lote"):
        return None
    import lote
    arq = _rel(plano, plano["lote"]).resolve()
    lo = lote.ler(arq)
    erros = lote.confere(lo)
    if erros:
        raise ValueError("o lote reprovou antes de gerar:\n  " + "\n  ".join(erros))
    falta = lote.faltam(lo)
    if not falta:
        return None
    return Passo("cenas", [PY, str(AQUI / "lote.py"), str(arq), "--gera"], lo["_pasta"] / f"{falta[0]}.mp4",
                 cobra=f"Higgsfield, {len(lote.a_gerar(lo))} cenas, ~US$ {lote.estimativa(lo):.2f}",
                 custo_fixo=0.0, toca=0.0)


def _criativo(plano: dict, e: es.Estilo, trabalho: Path,
              inicio: int) -> tuple[list[Passo], Path | None]:
    """O criativo: voz em off sobre cenas do banco, cada cena no trecho da fala que ilustra. Quem
    monta é o `criativo.py`; aqui entra o que é do estilo e a ordem dos passos. A trilha é a cama
    da fábrica, depois da legenda.

    A voz e as cenas do `lote` custam dinheiro e não rodam: faltando, viram passo que cobra,
    impresso com o comando, e a cadeia para ali."""
    cr = _cr()
    des = e.eixos["desenho"]
    doc = {**plano, "_dir": str(Path(plano.get("_dir", ".")).resolve()),
           "_estilo": {"nome": e.nome, "fps": e.eixos["imagem"]["fps"], "sintese": e.eixos["voz"]["sintese"],
                       "ritmo": des["ritmo"], "layout": des["legenda_layout"],
                       **({"fonte": des["fonte"]} if des["fonte"] else {}),
                       # o kit sem a biblioteca fica com a cor padrão do captions_viral
                       "acento": _v2().token(des["destaque"], des["tema"]) if V2.exists() else None}}
    pj = trabalho / "criativo.json"
    texto = json.dumps(doc, ensure_ascii=False, indent=1)
    helper = str(AQUI / "criativo.py")
    voz, fala, t = cr.fonte(doc), cr.transcript(doc), trabalho
    narracao = Passo("narração", [PY, helper, "voz", str(t)], voz, arquivo=(pj, texto),
                     cobra="ElevenLabs", custo_fixo=0.0, toca=0.0)

    # A cena nova é a primeira coisa que custa: sem ela o banco não tem o que conferir. O seco
    # mostra também a voz, se faltar, pra o custo inteiro aparecer de uma vez.
    cenas = _cenas_do_lote(plano)
    if cenas:
        return [cenas, *([] if voz.exists() else [narracao])], None
    erros = cr.confere(doc)
    if erros:
        raise ValueError("o criativo reprovou antes do render:\n  " + "\n  ".join(erros))

    def passo(nome: str, saida: Path, entradas=(), chaves=()) -> Passo:
        # Cada passo leva na impressão só o pedaço do plano que ele lê: trocar a palavra do
        # "comenta" não refaz as cenas. O criativo.json inteiro chega pelo `arquivo`.
        extra = json.dumps({k: doc.get(k) for k in (*chaves, "_estilo")}, ensure_ascii=False, sort_keys=True)
        return Passo(nome, [PY, helper, nome, str(t)], saida, [*entradas], extra=extra, arquivo=(pj, texto))

    if not voz.exists():
        return [narracao], None
    # A transcrição de outro caminho é do usuário; o confere já cobrou que ela exista.
    passos = [p for p in [_transcricao(voz, fala)] if p]
    # O acabamento de cada cena mora na base: ele é guardado no banco, por nome, e só roda na
    # cena que ainda não tem. Num passo à parte, a lista dele ficava abaixo do piso da impressão.
    render = [passo("base", t / "base.mp4", [voz, fala, *cr.brutas(doc), AQUI / "filmagem_achada.py"],
                    ("banco", "trechos", "cor", "zona"))]
    if e.tem("legenda"):
        render += [
            passo("cards", t / "legenda.json", [fala, AQUI / "cards_da_fala.py"], ("trechos", "punch", "funde")),
            Passo("legenda", [PY, str(AQUI / "captions_viral.py"), str(t / "base.mp4"),
                              "--plan", str(t / "legenda.json"), "-o", str(t / "legendado.mp4")],
                  t / "legendado.mp4", [t / "base.mp4", t / "legenda.json"]),
        ]
    passos += [p for p in render if ETAPAS.index(ETAPA_CRIATIVO[p.nome]) >= inicio]
    return passos, render[-1].saida


def _entregas(plano: dict, e: es.Estilo, final: Path, trabalho: Path) -> list[tuple[Path | None, Path]]:
    """O que sai da área de trabalho, e para onde. O `None` é o que a cadeia produziu por último.

    O reel editorial entrega o final, um final por fecho (`-<nome>`), a versão do YouTube ao lado
    dele e a capa na pasta do vídeo, onde a agenda do YouTube e a do Instagram vão buscar."""
    saidas: list[tuple[Path | None, Path]] = [(None, final)]
    if e.eixos["imagem"]["composicao"] == "editorial":
        # um final por fecho, ao lado do principal (que é o primeiro deles)
        for nome in plano.get("fechos") or {}:
            saidas.append((trabalho / f"final-{nome}.mp4", final.with_name(f"{final.stem}-{nome}.mp4")))
        if plano.get("youtube"):
            saidas.append((trabalho / "final-yt.mp4", final.with_name(f"{final.stem}-yt.mp4")))
        if plano.get("capa"):
            saidas.append((trabalho / "capa-nick.jpg", final.parent / plano["slug"] / "capa-nick.jpg"))
    return saidas


def _cadeia(plano: dict, e: es.Estilo, edl_path: Path, trabalho: Path,
            desde: str, edl_texto: str = "") -> tuple[list[Passo], Path]:
    """Monta a sequência de comandos. Nada executa aqui — é isso que deixa o modo
    seco existir sem um `if` espalhado por cada passo."""
    cmds: list[list[str]] = []
    img = e.eixos["imagem"]
    corrente = trabalho / "render.mp4"
    inicio = ETAPAS.index(desde)

    if img["composicao"] == "editorial":
        return _editorial(plano, e, trabalho, inicio)
    if img["composicao"] == "cenas":
        return _criativo(plano, e, trabalho, inicio)

    legenda_feita = False
    if plano.get("blocos"):
        blocos, corrente, completo = _blocos(plano, e, trabalho, inicio)
        cmds += blocos
        if not completo:
            return cmds, None
        legenda_feita = True          # entrou bloco a bloco, com o plano de cada um
    elif e.bruto == "avatar":
        # O adaptador de avatar substitui o render: o que produz imagem aqui é a
        # geração no HeyGen, que custa crédito e por isso não roda sozinha.
        limpo = trabalho / "voz_limpa.wav"
        if inicio <= ETAPAS.index("render"):
            preparo, limpo = _preparo_avatar(plano, e, trabalho)
            cmds += preparo
        gerado = [Path(p) for p in plano.get("gerado", [])]
        if gerado:
            corrente = trabalho / "juntado.mp4"
            # junta.py e não `ffmpeg -f concat`: o HeyGen entrega a 25 fps, o
            # projeto roda a 30, e o demultiplexador mantém a taxa do primeiro
            # arquivo sem reescrever o relógio. Em 19/09 um corte de 78s saiu
            # com 94s de imagem em cima de 70s de áudio.
            cmds.append(Passo("emenda dos blocos",
                              [PY, str(AQUI / "junta.py"), *[str(p) for p in gerado],
                               "-o", str(corrente), "--fps", str(img["fps"])],
                              corrente, gerado))
        else:
            # Sem os blocos gerados a cadeia para no portão, de propósito. A
            # fábrica não gera: ela prepara, mede e diz o que pedir.
            return cmds, None

    elif inicio <= ETAPAS.index("render"):
        fonte = Path(plano["fonte"])
        if e.eixos["voz"]["tratamento"] == "isola":
            # O EDL já aponta para a fonte isolada (ver `fabrica`); aqui ela nasce.
            isolada = _fonte_isolada(trabalho)
            cmds.append(Passo("isola a voz", [PY, str(AQUI / "isola_voz.py"), str(fonte),
                                              "-o", str(isolada)], isolada, [fonte]))
            fonte = isolada
        render = [PY, str(AQUI / "render.py"), str(edl_path), "-o", str(corrente),
                  "--height", str(img["altura"]), "--fps", str(img["fps"])]
        if img["canvas"]:
            render += ["--canvas", img["canvas"]]
        # Voz isolada NÃO passa pelo realce: o afftdn dele (piso -25 dB) toma a
        # voz limpa por ruído e come o agudo (ver test_voz_isolada_entra_antes_do_render).
        if e.eixos["voz"]["tratamento"] == "realce":
            render.append("--voice-enhance")
        if e.tem("normalizar"):
            # A normalização sai daqui e vai para o fim da cadeia: os passos
            # seguintes mexem no som, e normalizar antes deles é medir uma coisa
            # e entregar outra.
            render.append("--no-loudnorm")
        cmds.append(Passo("render", render, corrente, [fonte],
                          extra=edl_texto))

    # A camada de desenho do vertical: cenas animadas ou cards fixos viram uma
    # composição HTML, que o hyperframes renderiza a vídeo. O plano pode trazer a
    # camada pronta em vez disso — é o que deixa refazer só o layout ser barato.
    camada = Path(plano["camada"]) if plano.get("camada") else None
    if (inicio <= ETAPAS.index("desenho") and camada is None
            and (plano.get("cenas") or plano.get("cards"))):
        dirdesenho = Path(plano.get("dir_desenho") or (trabalho / "desenho"))
        gerador = "make_reel_v3.py" if plano.get("cenas") else "make_reel_v2.py"
        cfg = trabalho / "camada.json"
        cmds.append(Passo("composição do desenho",
                          [PY, str(AQUI / gerador), str(plano.get("transcript", "")),
                           str(edl_path), str(dirdesenho / "index.html"), str(cfg)],
                          dirdesenho / "index.html", [edl_path], extra=edl_texto))
        cmds.append(Passo("render do desenho", ["npm", "run", "render"],
                          dirdesenho / "renders" / "camada.mp4",
                          [dirdesenho / "index.html"]))
        camada = dirdesenho / "renders" / "camada.mp4"

    if inicio <= ETAPAS.index("desenho") and e.tem("explicador") and plano.get("overlays"):
        ov = trabalho / "overlays.json"
        saida = trabalho / "com_explicador.mp4"
        explica = [PY, str(AQUI / "lesson_overlays.py"), str(corrente),
                   str(edl_path), str(ov), "-o", str(saida)]
        # O explicador do tronco desenha com a biblioteca, no tema do estilo; o do
        # kit é o quadro-negro antigo, que não conhece a opção.
        if V2.exists():
            explica += ["--tema", e.eixos["desenho"]["tema"]]
        cmds.append(Passo("explicador", explica,
                          saida, [corrente, edl_path],
                          # O conteúdo dos cards é calculado em memória e só vira
                          # arquivo na hora de executar. Ler de volta do disco
                          # devolveria o da corrida anterior — o mesmo defeito
                          # que o EDL teve.
                          extra=edl_texto + json.dumps(plano["overlays"],
                                                       ensure_ascii=False,
                                                       sort_keys=True)))
        corrente = saida

    if inicio <= ETAPAS.index("composicao"):
        montagem, corrente = _composicao(plano, e, corrente, trabalho, camada)
        cmds += montagem

    if inicio <= ETAPAS.index("composicao") and e.tem("emenda"):
        ef = e.eixos["efeito"]
        saida = trabalho / "com_emenda.mp4"
        modo = ef.get("emenda") or "glitch"
        if modo not in ("glitch", "flash", "whip"):
            modo = "glitch"
        # O efeito toca poucos quadros por emenda. O número declarado é o que
        # faz o modo seco marcar este passo quando ele custa o vídeo inteiro.
        cmds.append(Passo(f"{modo} de emenda",
                          [PY, str(AQUI / "glitch_cuts.py"), str(corrente), str(edl_path),
                           "-o", str(saida), "--min-gap", str(ef["emenda_min"]),
                           "--intensity", ef["emenda_forca"], "--mode", modo],
                          saida, [corrente, edl_path], toca=0.4, extra=edl_texto))
        corrente = saida

    # A abertura vem DEPOIS da emenda: o glitch é posicionado pelo tempo do EDL, e
    # o CRT muda a duração do vídeo. Invertendo, a emenda cai no lugar errado.
    if inicio <= ETAPAS.index("composicao") and e.tem("abertura"):
        saida = trabalho / "com_abertura.mp4"
        crt = [PY, str(AQUI / "tv_effect.py"), str(corrente), "-o", str(saida)]
        if not e.eixos["efeito"]["som"]:
            crt.append("--no-sound")
        cmds.append(Passo("abertura CRT", crt, saida, [corrente],
                          toca=2 * e.eixos["efeito"].get("dur", 0.4)))
        corrente = saida

    if inicio <= ETAPAS.index("composicao") and e.tem("broll") and plano.get("broll"):
        lista = confere_beats(plano["broll"])
        saida = trabalho / "com_broll.mp4"
        cmds.append(Passo("b-roll", broll_cmd(e, corrente, lista, saida),
                          saida, [corrente],
                          toca=sum(float(b["dur"]) for b in lista)))
        corrente = saida

    if inicio <= ETAPAS.index("trilha") and e.tem("normalizar"):
        saida = trabalho / "normalizado.mp4"
        cmds.append(Passo("loudness",
                          [PY, str(AQUI / "normaliza.py"), str(corrente), "-o", str(saida)],
                          saida, [corrente]))
        corrente = saida

    if inicio <= ETAPAS.index("trilha") and e.tem("legenda") and not legenda_feita:
        como = e.adaptador("legenda")
        saida = trabalho / "com_legenda.mp4"
        if como == "liso":
            # O .srt sai do próprio render, pelos offsets do EDL.
            srt = plano.get("legenda") or (trabalho / "master.srt")
            cmds.append(Passo("legenda", [PY, str(AQUI / "legendar.py"), str(corrente),
                                          str(srt), "-o", str(saida)],
                              saida, [corrente]))
            corrente = saida
        else:
            plan = plano.get("legenda")
            if not plan and plano.get("transcript"):
                # O estilo pediu legenda e o plano não trouxe o plano de cards.
                # Antes disto o recurso sumia calado: `e.tem("legenda")` dava
                # verdadeiro e nenhum comando entrava na cadeia.
                plan = trabalho / "cards.json"
                fala, cortada = Path(plano["transcript"]), None
                if edl_texto and e.bruto != "avatar":
                    # A transcrição está no tempo do bruto e a legenda queima no
                    # vídeo cortado: sem isto, cada silêncio tirado atrasa a legenda.
                    fala = trabalho / "fala_cortada.json"
                    cortada = (fala, _fala_no_corte(Path(plano["transcript"]),
                                                    json.loads(edl_texto)["ranges"]))
                cards = [PY, str(AQUI / "cards_da_fala.py"), str(fala), "-o", str(plan)]
                # O kit do aluno não leva a biblioteca: lá a legenda fica com a
                # cor padrão do captions_viral, em vez de quebrar.
                if V2.exists():
                    cards += ["--acento", _v2().token(e.eixos["desenho"]["destaque"], e.eixos["desenho"]["tema"])]
                if e.eixos["desenho"]["fonte"]:
                    cards += ["--fonte", e.eixos["desenho"]["fonte"]]
                ritmo = e.eixos["desenho"]["ritmo"]
                if ritmo:
                    cards += ["--ritmo", f"{ritmo[0]},{ritmo[1]}"]
                cmds.append(Passo("cards da fala", cards, Path(plan),
                                  [Path(plano["transcript"])],
                                  extra=cortada[1] if cortada else "", arquivo=cortada))
            if plan:
                cmds.append(Passo("legenda",
                                  [PY, str(AQUI / "captions_viral.py"), str(corrente),
                                   "--plan", str(plan), "-o", str(saida)],
                                  saida, [corrente, Path(plan)]))
                corrente = saida

    return cmds, corrente


def _fala(plano: dict, trechos: list[dict]) -> str | None:
    """Onde há voz no vídeo emendado, `a:b,c:d`. None = em todo lugar.

    Bloco `mudo` sem `voz` só tem efeito: medir a voz ali, ou deixar o efeito
    abaixar a trilha, é tratar moeda como fala."""
    blocos = plano.get("blocos") or []
    fala = [bool(b.get("voz") or not b.get("mudo")) for b in blocos]
    if all(fala):
        return None
    t, out = 0.0, []
    for b, f, tr in zip(blocos, fala, trechos):
        d = tr["end"] - tr["start"]
        # a vinheta cantada também tira a cama da frente, enquanto dura
        fim = t + d if f else t + min(d, ff.dur(_rel(plano, b["vinheta"]))) if b.get("vinheta") else None
        if fim is not None:
            out.append(f"{t:.2f}:{fim:.2f}")
        t += d
    return ",".join(out)


def _trilha(e: es.Estilo, corrente: Path, duracao: float, trabalho: Path,
            faixa: str, outro: str | None, fala: str | None = None) -> Passo:
    """O passo da trilha, pelo adaptador do estilo: `fecho` sobe na chamada
    final (reel), `cama` fica sob a voz o vídeo inteiro com ducking (VSL)."""
    saida = trabalho / "com_trilha.mp4"
    if e.adaptador("trilha") == "cama":
        cmd = [PY, str(AQUI / "mixa.py"), str(corrente), "--trilha", str(faixa),
               "-o", str(saida)]
        if fala is not None:
            cmd += ["--fala", fala]
        if e.eixos["entrega"]["alvo"] is not None:
            cmd += ["--alvo", str(e.eixos["entrega"]["alvo"])]
        cmd += _args_cama(e)
    else:
        cmd = trilha_cmd(e, corrente, duracao, saida, faixa, outro)
    return Passo("fecho com trilha", cmd, saida,
                 [corrente] + ([Path(faixa)] if Path(faixa).exists() else []))


def trilha_cmd(e: es.Estilo, corrente: Path, duracao: float, saida: Path,
               faixa: str, outro: str | None = None) -> list[str]:
    """O fecho: trilha por baixo da fala o vídeo inteiro, subindo na chamada final.

    A faixa entra DUAS vezes e cruza consigo mesma — é o que faz o laço não ter
    costura audível quando a música é mais curta que o vídeo. O volume fica no
    piso até `antes_do_fecho` e sobe em rampa; sem isso a trilha disputa com a
    voz, e com ela o fecho não tem energia nenhuma.

    `amix` com `normalize=0` e `dropout_transition` alto: normalizar faria a
    trilha subir sozinha toda vez que a fala desse uma pausa.
    """
    t = e.eixos["trilha"]
    piso, cruz = t["sob_fala"], t["cruzamento"]
    total = duracao + (t["outro_dur"] if outro else 0.0)
    sobe = round(duracao - t["antes_do_fecho"], 2)
    fim_fade = round(total - t["saida"], 2)

    # Com fecho, o vídeo e o som são concatenados antes; o outro entra mudo, e a
    # trilha é a única coisa que se ouve ali.
    volume = (f"volume='clip({piso}+{1 - piso:.2f}*(t-{sobe})/{t['subida']},"
              f"{piso},1.0)':eval=frame" if outro else f"volume={piso}")
    musica = (f"acrossfade=d={cruz}:c1=tri:c2=tri[loop];"
              f"[loop]atrim=0:{round(total, 2)},loudnorm=I={t['alvo']},{volume},"
              f"afade=t=in:st=0:d={t['entrada']},"
              f"afade=t=out:st={fim_fade}:d={t['saida']}[mus]")
    mix = ("amix=inputs=2:normalize=0:dropout_transition=99999,"
           f"{ff.limitador(0.95)}[a]")

    if outro:
        fc = (f"[0:v][0:a][1:v][2:a]concat=n=2:v=1:a=1[v][voz];"
              f"[3:a][4:a]{musica};[voz][mus]{mix}")
        entradas = ["-i", str(corrente), "-i", outro,
                    "-f", "lavfi", "-t", str(t["outro_dur"]),
                    "-i", "anullsrc=r=48000:cl=stereo", "-i", faixa, "-i", faixa]
        mapa = ["-map", "[v]", "-map", "[a]"]
    else:
        fc = f"[1:a][2:a]{musica};[0:a][mus]{mix}"
        entradas = ["-i", str(corrente), "-i", faixa, "-i", faixa]
        mapa = ["-map", "0:v", "-map", "[a]"]

    return (["ffmpeg", "-y", *entradas, "-filter_complex", fc, *mapa,
             *ff.args_video(e.eixos["imagem"]["qualidade"]), *ff.args_audio(),
             "-movflags", "+faststart", str(saida)])


def fabrica(plano: dict, seco: bool = False, desde: str = "corte",
            sem_cache: bool = False) -> Path | Seco:
    """Recebe estilo, bruto e plano; devolve o final. Em modo seco, devolve a
    cadeia montada sem executar nada."""
    if desde not in ETAPAS:
        raise KeyError(f"etapa '{desde}' não existe. Disponíveis: {', '.join(ETAPAS)}")

    _confere(plano)

    sobrescritas = {k: v for k, v in plano.items()
                    if k in es.EIXOS or k in ("recursos", "adaptadores")}
    e = es.estilo(plano["estilo"], **sobrescritas)
    # O editorial e o criativo resolvem os deles pela pasta do plano e só por ela: lá a voz pode
    # ainda não existir, e procurar na pasta de quem rodou acharia a voz de outro vídeo.
    if e.eixos["imagem"]["composicao"] not in ("editorial", "cenas"):
        plano = _caminhos(plano)

    bruto = plano.get("bruto", e.bruto)
    if bruto != e.bruto:
        raise ValueError(
            f"o estilo '{e.nome}' parte de {e.bruto}, e o plano trouxe {bruto}. "
            f"Brutos: {', '.join(sorted(BRUTOS))}"
        )

    trechos = _edl(plano, e)
    if not trechos:
        raise ValueError("o corte não deixou nenhum trecho — confira janelas e drops")

    # A legenda aceita duas fontes: o plano de cards pronto, ou a transcrição de
    # onde gerá-lo. Por isso ela é a única em que o próprio nome do recurso no
    # plano também satisfaz a exigência. Na VSL em blocos ela vem no plano de
    # cada bloco, e no criativo ela sai do texto dos trechos.
    atendidos = {"legenda"} if plano.get("blocos") or plano.get("trechos") else set()
    mudos = [(r, es.exige(r)) for r in e.recursos
             if es.exige(r) and not plano.get(es.exige(r)) and not plano.get(r)
             and r not in atendidos]
    # No modo seco quem mostra é o `Seco.imprime`, com o resto da conferência.
    # Imprimir aqui também faria a mesma frase sair duas vezes, em duas redações.
    if not seco:
        for recurso, campo in mudos:
            print(f"aviso: o estilo pede '{recurso}' e o plano não trouxe '{campo}' — "
                  f"esta camada não vai entrar")

    final = _final(plano, e)
    trabalho = (_rel(plano, plano["trabalho"]) if plano.get("trabalho")
                else final.parent / "_trabalho" / plano["slug"]).resolve()
    entregas = _entregas(plano, e, final, trabalho)
    alheios = [d for _, d in entregas if _final_alheio(d)]
    if not seco and alheios:
        raise FileExistsError(
            f"{alheios[0]} já existe e não foi a fábrica que fez. Mude o `slug` ou tire o "
            f"arquivo de lá — o final é copiado por cima, e fora do git não há volta."
        )

    edl_path = trabalho / "edl.json"
    fonte_render = (str(_fonte_isolada(trabalho)) if e.eixos["voz"]["tratamento"] == "isola"
                    else plano.get("fonte"))
    edl_doc = {"version": 1, "sources": ({Path(plano["fonte"]).stem: fonte_render}
                                         if plano.get("fonte") else {}),
               "ranges": trechos, "grade": e.eixos["graduacao"]["preset"],
               "overlays": [], "total_duration_s": round(
                   sum(t["end"] - t["start"] for t in trechos), 2)}

    edl_texto = json.dumps(edl_doc, ensure_ascii=False, indent=2)
    cmds, corrente = _cadeia(plano, e, edl_path, trabalho, desde, edl_texto)
    # None = a cadeia parou no portão: ainda não existe imagem, e sem ela não há
    # trilha nem final. Seguir mandava uma PASTA para o ffmpeg e para o copy.
    parou = corrente is None

    duracao = sum(t["end"] - t["start"] for t in trechos)
    faixa = plano.get("faixa") or e.eixos["trilha"]["faixa"]
    outro = plano.get("outro") or e.eixos["trilha"]["outro"]
    # O editorial mistura a trilha no passo de som dele, em pedaços e com o ducking na fala
    # medida: a cama da fábrica por cima seria a segunda trilha.
    quer_trilha = (ETAPAS.index(desde) <= ETAPAS.index("trilha")
                   and e.tem("trilha") and faixa and not parou
                   and e.eixos["imagem"]["composicao"] != "editorial")

    if seco:
        # A trilha precisa da duração do vídeo, que só existe depois de render.
        # No seco ela sai do EDL: aproximada, e é o bastante para conferir a
        # cadeia. Na execução o valor é medido no arquivo.
        if quer_trilha:
            cmds = cmds + [_trilha(e, corrente, duracao, trabalho, faixa, outro,
                                   _fala(plano, trechos))]
        if not sem_cache:
            cmds = [replace(p, pulavel=ja_feito(p)) for p in cmds]
        return Seco(estilo=e, edl=trechos, passos=cmds, final=final,
                    duracao=duracao, mudos=mudos, alheio=alheios,
                    pulados=[p.nome for p in cmds if p.pulavel])

    trabalho.mkdir(parents=True, exist_ok=True)
    # O EDL em disco é entrada de passo; no bruto `avatar` nenhum passo o lê,
    # porque quem corta é o `apara_pausas`, no áudio. Gravar assim mesmo deixava
    # em disco um segundo cálculo do mesmo corte, pronto para divergir do
    # primeiro no dia em que alguém mexesse num lado só.
    if e.bruto != "avatar":
        # Só reescreve se mudou. Reescrever igual dá instante novo ao arquivo, e o
        # instante entra na impressão — um EDL idêntico invalidava a cadeia inteira.
        if not edl_path.exists() or edl_path.read_text(encoding="utf-8") != edl_texto:
            edl_path.write_text(edl_texto, encoding="utf-8")
    if plano.get("overlays"):
        (trabalho / "overlays.json").write_text(
            json.dumps(plano["overlays"], ensure_ascii=False), encoding="utf-8")

    pulados = []
    for passo in cmds:
        passo.saida.parent.mkdir(parents=True, exist_ok=True)
        if passo.arquivo:
            caminho, texto = passo.arquivo
            caminho.parent.mkdir(parents=True, exist_ok=True)
            if not caminho.exists() or caminho.read_text(encoding="utf-8") != texto:
                caminho.write_text(texto, encoding="utf-8")
        if passo.cobra:
            print(f"  $ {passo.nome}: cobra na {passo.cobra}, e a fábrica não gasta. Quando quiser, "
                  f"rode à mão:\n      {' '.join(passo.cmd)}")
            continue
        digital = _digital(passo)
        if not sem_cache and impressao.pronto(passo.saida, digital):
            pulados.append(passo.nome)
            print(f"  = {passo.nome} (já feito)")
            continue
        ff.run(passo.cmd)
        if passo.saida.exists():
            impressao.marca(passo.saida, digital)

    if quer_trilha:
        passo = _trilha(e, corrente, ff.dur(corrente), trabalho, faixa, outro,
                        _fala(plano, trechos))
        digital = _digital(passo)
        if not sem_cache and impressao.pronto(passo.saida, digital):
            pulados.append("fecho com trilha")
            print("  = fecho com trilha (já feito)")
        else:
            ff.run(passo.cmd)
            impressao.marca(passo.saida, digital)
        corrente = passo.saida

    if pulados:
        print(f"pulados por já existirem: {', '.join(pulados)}")

    if parou:
        print("parou no portão: gere o que ele pediu acima (no HeyGen, o arquivo vai em "
              "`gerado`, ou no lugar que o passo `$` mostrou) e rode de novo")
        return trabalho

    # Copia, não move. Mover leva embora o último intermediário, e sem ele a
    # corrida seguinte refaz o passo que o produziu — disco é mais barato que
    # uma geração de encode.
    for origem, destino in entregas:
        origem = origem or corrente
        if not origem.exists():
            print(f"não entregue: {destino.name} (falta {origem.name})")
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(origem), str(destino))
        _marca_final(destino).write_text(plano["slug"] + "\n", encoding="utf-8")

    # A procedência viaja com o final, não com a área de trabalho: é lá que ela
    # vai ser procurada, meses depois, por quem precisa responder de onde veio
    # um quadro.
    fontes = procedencia(plano)
    if fontes:
        lado = final.with_suffix(".fontes.json")
        lado.write_text(json.dumps(fontes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"procedência: {len(fontes)} clipe(s) de terceiro -> {lado.name}")

    print(f"pronto: {final}")
    return final


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description="A fábrica: estilo, bruto e plano -> o final")
    ap.add_argument("plano", type=Path)
    ap.add_argument("--seco", action="store_true",
                    help="monta a cadeia e imprime, sem renderizar")
    ap.add_argument("--desde", default="corte", choices=ETAPAS,
                    help="etapa em que começa (reaproveita o que já está em disco)")
    args = ap.parse_args()

    plano = json.loads(args.plano.read_text(encoding="utf-8"))
    plano.setdefault("_dir", str(args.plano.resolve().parent))
    r = fabrica(plano, seco=args.seco, desde=args.desde)
    if isinstance(r, Seco):
        r.imprime()


if __name__ == "__main__":
    main()
