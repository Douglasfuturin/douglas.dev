"""O estilo de edição, como dado.

Antes disto, "o estilo consolidado da aula" não existia em lugar nenhum: era a
sequência de programas que o editor lembrava de rodar, com as flags que lembrava
de passar, sobre constantes que lembrava de não mexer. Por isso não dava para
escolher, listar nem herdar.

    e = estilo("aula-ccnp")                      # o conjunto inteiro, por nome
    e = estilo("reel-mono", imagem={"fps": 24})  # com ajuste de um vídeo só

Um nome resolve os oito eixos: **corte**, **voz**, **imagem**, **graduacao**,
**efeito**, **desenho**, **trilha**, **entrega**.

**A orientação é campo do eixo de imagem, não uma coisa acima do estilo.** O
recorte do rosto não é do formato: dentro do vertical já existem três tratamentos
diferentes, e são três estilos. Um estilo que serve os dois formatos — o vídeo de
quadro — deixa de ser dois.

**Recurso é camada nomeada com posição declarada.** O estilo lista quais quer; o
plano liga e desliga. Ninguém no meio precisa saber o nome de um recurso.

Cada eixo segue o molde que a graduação já usava neste projeto: um dicionário de
nomes, uma função que resolve, e um erro que lista os válidos quando o nome não
existe. Nada aqui é padrão novo — é aquele eixo, oito vezes.
"""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import clean_edl
import ff


# ---- os oito eixos ----------------------------------------------------------
#
# O valor de cada chave é o padrão. Um estilo declara só o que muda.

EIXOS: dict[str, dict[str, Any]] = {
    # O que é cortado — a costura A.
    "corte": {
        "afinacao": "aula",        # aula | tight | silencio
        "ajuste": {},              # sobrescritas da afinação, botão a botão
    },
    # Como a voz é tratada antes de normalizar.
    "voz": {
        "tratamento": "realce",    # realce | cru | isola (serviço, para gravação barulhenta)
        "alvo": ff.LOUDNORM_I,
        # Bloco com a fala dele (não mudo, sem `voz` à parte) passa pelo trata_voz e sai no nível
        # da voz gravada à parte. Para episódio montado de microfones diferentes.
        "por_bloco": False,
        # A voz que nasce do texto, quando nasce: {modelo, stability, similarity_boost,
        # sotaque (a marca que vai na frente do texto), tentativas (o teto de gerações)}.
        "sintese": None,
    },
    # O quadro: proporção, tamanho, taxa e quanto se aperta.
    "imagem": {
        "orientacao": "16:9",      # 16:9 | 9:16
        "altura": ff.ALTURA,
        "fps": ff.FPS,
        "canvas": None,            # "2560x1440" encaixa 16:10 num quadro 16:9
        "qualidade": "final",
        # Como o vertical é montado. Três tratamentos que já existiam, cada um de
        # um estilo — é o que prova que o recorte do rosto é do estilo e não do
        # formato:
        #   pilha        rosto em cima, desenho embaixo (reel de live)
        #   sobreposicao rosto em quadro cheio, desenho por cima (reel com cenas)
        #   cheio        sem montagem (reel de câmera, quadro)
        "composicao": "cheio",
        # Recorte do rosto no quadro da LIVE. A fábrica devolve o vídeo às
        # dimensões da live antes de aplicar — o render pode ter reescalado.
        "recorte": None,           # "crop=810:1440:555:0"
        "banda": [1080, 900],      # o tamanho da faixa do rosto na pilha
        #   editorial    o molde do Nick: painel em cima, rosto num cartão embaixo
        #   cenas        voz em off sobre cenas do banco, cada uma no trecho dela (o criativo)
        # O que vai atrás do rosto gerado (caminho a partir da raiz), na escala e
        # no lugar do avatar. None = o que veio com ele.
        "fundo": None,
        # A tela dividida reta com cena embaixo: [y da costura, altura do degradê].
        "costura": None,
    },
    "graduacao": {
        "preset": "none",          # os nomes vivem no grade.py
    },
    # Abertura, fecho e emenda.
    "efeito": {
        "abertura": None,          # crt | None
        "som": True,
        # Nível dos sons das peças contra a voz, em dB. Medido na VSL em 24/09:
        # com -8 o tick-roll ficava 17 dB debaixo da voz, inaudível.
        "sfx_db": -2.0,
        "emenda": None,            # glitch | flash | whip | None
        "emenda_min": 30.0,        # vão de origem que merece glitch, em s
        "emenda_forca": "subtle",  # subtle | medium | strong
    },
    # O que é desenhado por cima. Cor, letra e movimento NÃO moram aqui: são do
    # núcleo de tools/v2, e o estilo só escolhe entre os dois chãos dele. A
    # direção que vale por padrão é a da VSL — papel claro, nada atrás da pessoa.
    "desenho": {
        # claro | tinta | tinteiro (canal de Lorcana) | marca (a marca/tema.css do aluno) — o ?tema=
        # de toda peça
        "tema": "claro",
        # A letra da legenda viral: um nome do FONTES do captions_viral, ou o caminho de um .ttf/.otf
        # a partir da raiz (`marca/fontes/x.ttf`, `#Black` no fim escolhe a instância da variável).
        # None = a padrão dele.
        "fonte": None,
        # Texto atrás da pessoa (palavra-herói recortada, peça em camadas). A
        # VSL fechou isso: ênfase vem de peso e escala, nunca de profundidade.
        "atras": False,
        # Cadência da legenda viral, [entrada, passo] em s. None = a do captions_viral.
        "ritmo": None,
        # O token do núcleo que acende a palavra em destaque na legenda viral: `ac`, o azul
        # do bloco, ou `mk`, o amarelo do marcador.
        "destaque": "ac",
        # O layout de todo card da legenda viral (`faixa`, `faixa_criativo`…). None = o que o
        # cards_da_fala escolher. Quem lê é o criativo.
        "legenda_layout": None,
        # O y onde começa a faixa da legenda do Instagram: letra nenhuma desce dali.
        "legenda_ig": None,
        # A zona segura do 9:16, [x0, y0, x1, y1]: fora dela a interface da rede cobre a letra. Fundo,
        # cenário e rosto podem sangrar; o que precisa ser lido, não.
        "zona": None,
        # A coluna de botões da rede, [x, y]: de x pra direita e de y pra baixo também não tem letra.
        "botoes": None,
    },
    "trilha": {
        "faixa": None,
        "alvo": ff.LOUDNORM_MUSICA,
        "sob_fala": 0.03,          # volume da trilha enquanto ele fala
        "cama": None,              # LUFS da cama (adaptador cama); None = a do mixa (-31,5)
        # A faixa entra duas vezes e cruza consigo mesma: é o que faz o laço não
        # ter costura audível quando a música é mais curta que o vídeo.
        "cruzamento": 4.0,
        "entrada": 2.2,            # fade de entrada
        "saida": 0.9,              # fade de saída
        # A subida no fecho. A trilha fica embaixo da fala o reel inteiro e só
        # sobe na chamada final — sem isso ela disputa com a voz.
        "subida": 1.2,
        "antes_do_fecho": 0.4,     # começa a subir este tanto antes do outro
        "outro": None,             # vídeo de fecho, se houver
        "outro_dur": 5.0,
        # Pedaços da faixa, [{de, ate, em, entra, sai}]: o trecho dela que entra onde no
        # vídeo. None = a faixa do começo. Quem lê é o reel editorial.
        "pedacos": None,
        "duck": None,              # quanto a voz abaixa a cama (adaptador cama); None = a do mixa (12)
        "fade_fim": None,          # fade da cama no fim, em s; None = o do mixa (2,4)
    },
    "entrega": {
        "pasta": "videos",         # a fábrica completa com o projeto
        "alvo": None,              # LUFS da mistura com cama de trilha; None = o do mixa (-16, web)
    },
}


# ---- recursos ---------------------------------------------------------------
#
# `posicao` é o que faz um recurso ligado entrar no lugar dele em vez de no fim
# da fila. É o mínimo para a lista funcionar — não é ordem declarada genérica,
# que fica de fora até um segundo estilo pedir outra ordem.

# `exige` é o campo do plano sem o qual a camada não tem o que desenhar. Não é
# validação: é o que deixa a fábrica DIZER que o recurso não vai entrar, em vez
# de deixá-lo sumir calado. O estilo `vsl` pedia explicador, o plano nunca trazia
# `overlays`, e o vídeo saía sem — sem uma linha na tela sobre isso.
RECURSOS: dict[str, dict[str, Any]] = {
    "chapa":       {"posicao": 10, "o_que_faz": "moldura do celular por cima da tela (modo 2)",
                    "exige": "celular"},
    "explicador":  {"posicao": 20, "o_que_faz": "cartão gráfico sobre a gravação",
                    "exige": "overlays"},
    # Dois jeitos de entregar a mesma camada, e por isto a costura é real: o
    # `viral` tem direção (cadência, ênfase, palavra-herói) e come um plano de
    # cards; o `liso` queima um .srt e não decide nada. Enquanto havia um só, o
    # nome do recurso bastava — com dois, quem escolhe tem que ser o estilo, e
    # não o programa que por acaso chamou.
    # `exige` aqui é a segunda fonte possível: sem o plano de cards pronto, a
    # legenda nasce da transcrição. Sem nenhuma das duas ela não tem o que dizer.
    "legenda":     {"posicao": 30, "o_que_faz": "legenda queimada",
                    "adaptadores": {"viral": "captions_viral.py", "liso": "legendar.py"},
                    "padrao": "viral", "exige": "transcript"},
    "broll":       {"posicao": 40, "o_que_faz": "corte de apoio por cima da fala",
                    "exige": "broll"},
    "emenda":      {"posicao": 50, "o_que_faz": "glitch nas emendas grandes"},
    "abertura":    {"posicao": 60, "o_que_faz": "CRT de liga e desliga"},
    # Normalizar por último, depois dos passos que mexem no som — hoje o CRT
    # mistura o efeito sonoro DEPOIS da normalização, então ela mede uma coisa e
    # entrega outra.
    #
    # DESLIGADO EM TODOS OS ESTILOS, de propósito. O critério que este spec
    # fixou era: integrado, pico e faixa do final não podem mudar mais que
    # 0,5 LU. Medido em 14/09/2026 no único material que eu tinha — uma onda
    # senoidal — o integrado moveu 0,3 LU (passa) mas o pico moveu 3,4 dB e a
    # faixa 1,3 LU (reprova).
    #
    # Onda senoidal é material péssimo para medir faixa de loudness, e o
    # resultado provavelmente não vale para fala. Mas o critério não abre
    # exceção para material ruim: para ligar, meça numa aula de verdade. Ligar é
    # acrescentar "normalizar" aos recursos do estilo.
    "normalizar":  {"posicao": 65, "o_que_faz": "loudness no alvo das redes (ver nota)"},
    # Dois jeitos: o `fecho` deixa a trilha no piso e sobe na chamada final (o
    # reel); a `cama` fica 13 dB sob a voz o vídeo inteiro, com ducking (a VSL).
    "trilha":      {"posicao": 70, "o_que_faz": "música sob a fala",
                    "adaptadores": {"fecho": "fabrica.py", "cama": "mixa.py"},
                    "padrao": "fecho", "exige": "faixa"},
}


def exige(recurso: str) -> str:
    """O campo do plano sem o qual este recurso não entra. Vazio = não precisa."""
    return RECURSOS.get(recurso, {}).get("exige", "")


@dataclass(frozen=True)
class Estilo:
    nome: str
    bruto: str                      # live | camera | obs+celular | board | avatar | banco
    eixos: dict[str, dict[str, Any]]
    recursos: list[str] = field(default_factory=list)
    # Qual implementação entrega cada recurso. Vazio = a padrão do catálogo.
    adaptadores: dict[str, str] = field(default_factory=dict)

    @property
    def orientacao(self) -> str:
        return self.eixos["imagem"]["orientacao"]

    @property
    def vertical(self) -> bool:
        return self.orientacao == "9:16"

    def afinacao(self) -> clean_edl.Afinacao:
        """A afinação de corte pronta — o elo com a costura A."""
        c = self.eixos["corte"]
        return clean_edl.afinacao(c["afinacao"], **c["ajuste"])

    def tem(self, recurso: str) -> bool:
        return recurso in self.recursos

    def adaptador(self, recurso: str) -> str:
        """Qual implementação entrega este recurso.

        Recurso com um jeito só devolve o próprio nome — quem chama não precisa
        saber se a costura existe ou não, e o dia em que o segundo adaptador
        aparecer, nenhum chamador muda.
        """
        escolhas = RECURSOS.get(recurso, {}).get("adaptadores")
        if not escolhas:
            return recurso
        return self.adaptadores.get(recurso, RECURSOS[recurso]["padrao"])


# ---- o catálogo -------------------------------------------------------------
#
# Os estilos, extraídos do que já era feito. A extração não é hora de
# melhorar o molde: cada um nasce igual ao que já sai hoje.

ESTILOS: dict[str, dict[str, Any]] = {
    "aula-ccnp": {
        "bruto": "live",
        "corte": {"afinacao": "aula"},
        "imagem": {"orientacao": "16:9", "canvas": "2560x1440"},
        "efeito": {"abertura": "crt", "emenda": "glitch"},
        "entrega": {"pasta": "videos"},
        "recursos": ["explicador", "emenda", "abertura"],
    },
    # A aula sem ninguém gravando: a tela de verdade (o agente trabalhando no
    # terminal) com a voz clonada dele por cima, em blocos. Cada bloco é uma
    # janela do bruto com a fala do bloco, e as peças `h_` entram pelo plano
    # dele. A voz chega pronta do Eleven v4; CRT e glitch são do CCnP, não daqui.
    "aula-narrada": {
        "herda": "aula-ccnp",
        "voz": {"tratamento": "cru"},
        "desenho": {"tema": "claro"},
        "recursos": [],
    },
    "reel-mono": {
        "bruto": "live",
        "corte": {"afinacao": "tight"},
        "imagem": {"orientacao": "9:16", "altura": 1920, "qualidade": "reel",
                   "composicao": "pilha", "banda": [1080, 900]},
        # O reel de live ainda desenha no molde escuro do make_reel_v3 (a fase 2
        # do tools/v2 porta as cenas); o chão tinta é o que mais se parece.
        "desenho": {"tema": "tinta", "atras": True},
        "trilha": {"sob_fala": 0.03},
        "entrega": {"pasta": "videos/reels"},
        "recursos": ["explicador", "legenda", "trilha"],
    },
    "reel-camera": {
        "bruto": "camera",
        "corte": {"afinacao": "silencio"},
        "imagem": {"orientacao": "9:16", "altura": 1920, "fps": 24, "qualidade": "reel"},
        "desenho": {"atras": True},
        "entrega": {"pasta": "videos/reels"},
        "recursos": ["broll", "legenda"],
    },
    "quadro": {
        "bruto": "board",
        # O corte do quadro é mais apertado que o da aula e mais solto que o do
        # reel: ele respira entre blocos, mas não guarda pausa de live.
        "corte": {"afinacao": "aula", "ajuste": {"sil_cut": 0.45, "pad_in": 0.06,
                                                 "pad_out": 0.10, "pause_keep": 0.0}},
        "imagem": {"orientacao": "16:9"},
        "desenho": {"tema": "tinta"},
        "entrega": {"pasta": "videos"},
        "recursos": ["trilha"],
    },
    # O quadro vertical. Nove boards já existiam em `tools/quadro/projetos/*/
    # vertical.tsx` e renderizavam — mas a orientação estava no NOME DO ARQUIVO, e
    # aqui ela é campo. Sem esta declaração não havia como pedir um quadro 9:16 à
    # fábrica, e o molde 7a continuava molde. São quatro linhas porque o resto do
    # quadro já está resolvido no pai.
    "quadro-vertical": {
        "herda": "quadro",
        "imagem": {"orientacao": "9:16", "altura": 1920},
        "entrega": {"pasta": "videos/reels"},
    },
    # A VSL de avatar. O apresentador é gerado pelo HeyGen a partir da voz real
    # dele, então a costura A roda no ÁUDIO, antes de existir imagem: não há
    # quadro para cortar quando o corte acontece. É o que o bruto `avatar` declara.
    #
    # Os números não são gosto — saem do take medido: -18,9 LUFS é o nível das
    # aulas gravadas no OBS, e 0,04 de silêncio é o que a narração aguenta sem
    # soar picotada.
    # O que a VSL chama de "cards" é a LEGENDA com direção, não explicador: o
    # `cards_da_fala` gera o plano e o `captions_viral` queima. Declarar
    # `explicador` aqui prometia o cartão de aula, que é outro desenho e exige
    # `overlays` no plano — sem eles o recurso sumia calado.
    "vsl": {
        "bruto": "avatar",
        "corte": {"afinacao": "tight", "ajuste": {"sil_cut": 0.04}},
        "voz": {"tratamento": "realce", "alvo": -18.9},
        "imagem": {"orientacao": "9:16", "altura": 1920, "qualidade": "reel"},
        # A direção que virou padrão nasceu aqui. O ritmo é o de 21 dos 22
        # planos da VSL do Hermes, que o escreviam um por um.
        "desenho": {"tema": "claro", "ritmo": [0.167, 0.033]},
        "entrega": {"pasta": "videos"},
        "recursos": ["legenda", "trilha"],
        "adaptadores": {"legenda": "viral", "trilha": "cama"},
    },
    # O reel de topo de funil: o avatar da VSL com a voz dele clonada no Eleven v4
    # (`tools/quadro/voz.mjs`), rosto só onde a boca tem que aparecer e b-roll no
    # resto. A voz chega pronta — o voz.mjs já normaliza em -18 LUFS — e a cadeia
    # do microfone do OBS por cima dela tiraria ruído que não existe; `cru` pula o
    # trata_voz e deixa o apara, o ouvido e o portão.
    "reel-avatar": {
        "herda": "vsl",
        "voz": {"tratamento": "cru"},
        "entrega": {"pasta": "videos/reels"},
        "recursos": {"+": ["broll"]},
    },
    # O curto do canal de Lorcana: só mãos e cartas, em blocos (abertura, um
    # pacote, encerramento) tirados de JANELAS do bruto — o conteúdo é a carta,
    # e o corte por fala jogaria fora o rasgo e o reveal. Enquanto as cartas
    # passam, o bloco é mudo: trilha e efeito de dinheiro. A fala é a abertura e
    # o encerramento, que ele grava à parte (decisão dele, 29/09).
    "lorcana-curto": {
        "herda": "reel-camera",
        "imagem": {"fps": 30},
        # A marca do canal (direção 12a "Tinteiro noturno"), não a Ninja.
        "desenho": {"tema": "tinteiro", "atras": True},
        # -14: o integrado dos curtos outliers falados com trilha (-13,1 a -15,9).
        "entrega": {"pasta": "videos", "alvo": -14.0},
        # Metade do curto é mão sem fala: a cama de aula (-31,5) deixava a trilha
        # 14 dB abaixo da voz e o bloco mudo soava vazio.
        "trilha": {"cama": -27.0},
        # A trilha é parte do curto (as cartas passam com música e efeito de
        # dinheiro), e é a cama dela que acerta o volume do episódio inteiro — o
        # bloco recortado não se normaliza sozinho. O `normalizar` segue desligado
        # (ver a nota dele em RECURSOS).
        "recursos": ["trilha"],
        "adaptadores": {"trilha": "cama"},
    },
    # O episódio longo do canal de Lorcana, deitado: o mesmo semanal, com o talking head e as
    # mesmas peças (cada uma no `ar` 1920x1080 dela). Ele grava deitado pra servir aos dois
    # formatos; o curto recorta em pé, o longo usa o quadro inteiro.
    "lorcana-longo": {
        "herda": "lorcana-curto",
        "imagem": {"orientacao": "16:9", "altura": 1080, "qualidade": "final"},
        # o episódio junta o talking head de casa, os áudios da loja e o fone: cada bloco no
        # mesmo nível de voz, senão a cama passa por cima do mais baixo (ele, 02/10)
        "voz": {"por_bloco": True},
    },
    # O reel de topo de funil no molde do Nick Saraev (a peça e_editorial): a voz
    # clonada no Eleven v4, o avatar num cartão arredondado embaixo, o painel em cima
    # com a fala, as capturas e as peças. Três monta.py copiados faziam isso, e cada
    # ajuste do dono virava conserto em três lugares. Quem monta é o reel_editorial.py.
    #
    # O que o dono decidiu em 30/09 mora aqui como padrão (tools/v2/LEIA-ME.md, a voz
    # editorial); o que é regra e não número (cartão só com rosto, chamada só no fim,
    # sem selo de IA, gancho no quadro 0) o `confere` do helper cobra no modo seco.
    # A fala na tela quem desenha é a e_editorial, então a legenda não é recurso aqui.
    "reel-editorial": {
        "herda": "reel-avatar",
        "voz": {"alvo": -19.0,
                "sintese": {"modelo": "eleven_v4", "stability": 0.25, "similarity_boost": 0.85,
                            # sem marca de emoção: só o sotaque, na frente do texto
                            "sotaque": "[in a Brazilian Portuguese accent from Rio de Janeiro, carioca]",
                            "tentativas": 3}},
        # O fundo atrás do rosto não tem padrão: é a placa do look de quem grava, e vem do
        # plano (`imagem.fundo`). O confere do helper cobra quando falta.
        "imagem": {"composicao": "editorial", "costura": [768, 120]},
        "desenho": {"legenda_ig": 1450},
        # medidos no teste cego e no Eleven v4: com a razão 12 do mixa a cama sumia
        # sob a narração sem respiro, e o fade de 2,4 s abafava a chamada
        "trilha": {"cama": -21.0, "duck": 3.0, "fade_fim": 0.6},
        "entrega": {"pasta": "videos/topo"},
        "recursos": ["trilha"],
    },
    # O mesmo reel editorial como anúncio de Reels e Stories da Meta. A interface do anúncio cobre o
    # topo (~14%), a base (~35%) e as laterais (~6%), mais a coluna de botões; medido no "Do Zero ao
    # Pronto" V1 em 02/10, o placar, a legenda sobre o rosto, o título da capa e o "Saiba mais"
    # caíam embaixo dela. Vale também pro trial reel e pra página, que cortam do mesmo render.
    "anuncio-editorial": {
        "herda": "reel-editorial",
        "desenho": {"legenda_ig": 1250, "zona": [65, 270, 1015, 1250], "botoes": [960, 1000]},
        "entrega": {"pasta": "videos"},
    },
    # O criativo de anúncio: voz em off sobre cenas do banco (câmera de segurança, plantão,
    # documentário), cada cena no trecho da fala que ilustra. Morou meses fora da fábrica, num
    # monta_criativo.py na pasta dos anúncios; quem monta agora é o criativo.py. Da VSL vem a
    # legenda viral no ritmo dela e a cama sob a voz o vídeo inteiro.
    #
    # O bruto é o banco, não um take: a imagem já existe antes da voz, e a voz nasce do texto.
    # A cama é a de 23 dos 24 roteiros dos ninjas, e o destaque é o amarelo do marcador.
    "criativo": {
        "herda": "vsl",
        "bruto": "banco",
        "voz": {"tratamento": "cru",
                "sintese": {"modelo": "eleven_multilingual_v2", "tentativas": 3}},
        "imagem": {"composicao": "cenas"},
        "desenho": {"destaque": "mk", "legenda_layout": "faixa_criativo"},
        "trilha": {"cama": -20.0, "duck": 1.5, "fade_fim": 0.3},
        "entrega": {"pasta": "videos/criativos"},
    },
    # O mesmo criativo no Reels orgânico: sem o botão do anúncio, a legenda desce pra faixa, e
    # a trilha sai devagar no fim (os seis roteiros -reels repetiam as duas coisas).
    "criativo-reel": {
        "herda": "criativo",
        "desenho": {"legenda_layout": "faixa"},
        "trilha": {"fade_fim": 1.2},
    },
    # Herdar é uma linha. Este existe para provar que o molde não precisa ser
    # copiado quando muda uma coisa só.
    "reel-mono-claro": {
        "herda": "reel-mono",
        "desenho": {"tema": "claro"},
    },

    # ---- novos estilos do kit Grokish ---------------------------------------

    # Podcast/videocast deitado: corte por silêncio, voz realçada, sem CRT.
    "podcast": {
        "bruto": "live",
        "corte": {"afinacao": "silencio", "ajuste": {"sil_cut": 1.2, "pause_keep": 0.45}},
        "voz": {"tratamento": "realce"},
        "imagem": {"orientacao": "16:9", "fps": 30},
        "graduacao": {"preset": "documentary"},
        "efeito": {"abertura": None, "emenda": None},
        "desenho": {"tema": "claro", "fonte": "outfit"},
        "entrega": {"pasta": "videos/podcast"},
        "recursos": ["legenda", "trilha"],
        "adaptadores": {"legenda": "liso", "trilha": "cama"},
    },
    # Shorts rápidos: corte apertado, glitch forte, grade vivida.
    "shorts-rapido": {
        "herda": "reel-camera",
        "corte": {"afinacao": "tight", "ajuste": {"sil_cut": 0.25, "pause_keep": 0.15}},
        "imagem": {"fps": 30},
        "graduacao": {"preset": "vivid_social"},
        "efeito": {"abertura": None, "emenda": "glitch", "emenda_min": 8.0, "emenda_forca": "strong"},
        "desenho": {"tema": "tinta", "fonte": "bebas", "atras": True, "ritmo": [0.12, 0.03]},
        "entrega": {"pasta": "videos/shorts"},
        "recursos": ["legenda", "emenda", "trilha"],
    },
    # Teaser / trailer curto com riser e impacto.
    "teaser": {
        "herda": "reel-mono",
        "corte": {"afinacao": "tight"},
        "graduacao": {"preset": "high_contrast"},
        "efeito": {"abertura": "crt", "emenda": "glitch", "emenda_forca": "strong", "sfx_db": -1.0},
        "desenho": {"fonte": "anton", "tema": "tinta"},
        "trilha": {"sob_fala": 0.06, "subida": 1.8, "antes_do_fecho": 0.6},
        "entrega": {"pasta": "videos/teasers"},
        "recursos": ["legenda", "emenda", "abertura", "trilha"],
    },
    # Story 9:16 ultracurto para Instagram/WhatsApp Status.
    "story-rapido": {
        "herda": "reel-camera",
        "corte": {"afinacao": "tight", "ajuste": {"sil_cut": 0.2}},
        "graduacao": {"preset": "soft_pastel"},
        "desenho": {"fonte": "syne", "legenda_layout": "faixa", "ritmo": [0.1, 0.025]},
        "efeito": {"abertura": None, "emenda": None},
        "entrega": {"pasta": "videos/stories"},
        "recursos": ["legenda"],
    },
    # Webinar / aula ao vivo limpa, 16:9, fade sem glitch.
    "webinar": {
        "herda": "aula-ccnp",
        "corte": {"afinacao": "aula", "ajuste": {"pause_keep": 1.1}},
        "graduacao": {"preset": "neutral_punch"},
        "efeito": {"abertura": None, "emenda": None},
        "desenho": {"tema": "claro", "fonte": "space"},
        "recursos": ["explicador", "legenda"],
        "adaptadores": {"legenda": "liso"},
        "entrega": {"pasta": "videos/webinar"},
    },
    # Entrevista: dois falantes, silêncio mais tolerante, grade documental.
    "entrevista": {
        "bruto": "camera",
        "corte": {"afinacao": "aula", "ajuste": {"sil_cut": 1.6, "pause_keep": 0.7}},
        "voz": {"tratamento": "realce", "por_bloco": True},
        "imagem": {"orientacao": "16:9"},
        "graduacao": {"preset": "documentary"},
        "efeito": {"abertura": None, "emenda": None},
        "desenho": {"fonte": "rubik", "tema": "claro"},
        "entrega": {"pasta": "videos/entrevista"},
        "recursos": ["legenda", "trilha"],
        "adaptadores": {"legenda": "liso", "trilha": "cama"},
    },
    # Documentário vertical: noir suave + legenda discreta.
    "doc-vertical": {
        "herda": "reel-camera",
        "corte": {"afinacao": "silencio"},
        "graduacao": {"preset": "noir"},
        "desenho": {"fonte": "oswald", "tema": "tinta"},
        "efeito": {"abertura": None, "emenda": None, "sfx_db": -4.0},
        "entrega": {"pasta": "videos/doc"},
        "recursos": ["legenda", "broll", "trilha"],
        "adaptadores": {"trilha": "cama"},
    },
    # Feed 1:1 (quadrado) a partir de câmera.
    "feed-quadrado": {
        "bruto": "camera",
        "corte": {"afinacao": "tight"},
        "imagem": {"orientacao": "16:9", "canvas": "1080x1080", "qualidade": "reel"},
        "graduacao": {"preset": "vivid_social"},
        "desenho": {"fonte": "barlow", "tema": "claro"},
        "efeito": {"abertura": None, "emenda": "glitch", "emenda_min": 12.0, "emenda_forca": "subtle"},
        "entrega": {"pasta": "videos/feed"},
        "recursos": ["legenda", "trilha"],
    },
    # Pitch / elevador: 30–60s, punch alto, fonte display.
    "pitch": {
        "herda": "vsl",
        "corte": {"afinacao": "tight", "ajuste": {"sil_cut": 0.05}},
        "graduacao": {"preset": "teal_orange"},
        "desenho": {"fonte": "archivo", "ritmo": [0.14, 0.03]},
        "efeito": {"abertura": None, "emenda": "glitch", "emenda_forca": "medium"},
        "entrega": {"pasta": "videos/pitch"},
        "recursos": ["legenda", "trilha", "emenda"],
        "adaptadores": {"legenda": "viral", "trilha": "cama"},
    },
    # Cold open cinematico 21:9-ish via canvas wide.
    "cold-open": {
        "bruto": "live",
        "corte": {"afinacao": "tight"},
        "imagem": {"orientacao": "16:9", "canvas": "2560x1080", "qualidade": "final"},
        "graduacao": {"preset": "cool_night"},
        "efeito": {"abertura": "crt", "emenda": "glitch", "emenda_forca": "strong"},
        "desenho": {"fonte": "anton", "tema": "tinta"},
        "entrega": {"pasta": "videos/cold-open"},
        "recursos": ["abertura", "emenda", "trilha"],
    },
    # Tutorial vertical passo a passo (how-to).
    "tutorial": {
        "herda": "reel-camera",
        "corte": {"afinacao": "aula", "ajuste": {"pause_keep": 0.55, "sil_cut": 0.8}},
        "graduacao": {"preset": "neutral_punch"},
        "desenho": {"fonte": "rajdhani", "tema": "claro", "legenda_layout": "faixa"},
        "efeito": {"abertura": None, "emenda": "flash", "emenda_min": 10.0, "emenda_forca": "subtle"},
        "entrega": {"pasta": "videos/tutorial"},
        "recursos": ["legenda", "emenda", "explicador"],
        "adaptadores": {"legenda": "liso"},
    },
    # Unboxing / hands-on: close-ups, whip nas trocas.
    "unboxing": {
        "bruto": "camera",
        "corte": {"afinacao": "tight", "ajuste": {"sil_cut": 0.35}},
        "imagem": {"orientacao": "9:16", "qualidade": "reel"},
        "graduacao": {"preset": "vivid_social"},
        "desenho": {"fonte": "kanit", "tema": "tinta", "ritmo": [0.11, 0.03]},
        "efeito": {"abertura": None, "emenda": "whip", "emenda_min": 6.0, "emenda_forca": "medium"},
        "entrega": {"pasta": "videos/unboxing"},
        "recursos": ["legenda", "emenda", "trilha"],
    },
    # Hook de 15s: abertura CRT + glitch forte + riser.
    "hook-15s": {
        "herda": "teaser",
        "corte": {"afinacao": "tight", "ajuste": {"sil_cut": 0.1, "pause_keep": 0.1}},
        "graduacao": {"preset": "high_contrast"},
        "efeito": {"abertura": "crt", "emenda": "flash", "emenda_forca": "strong", "sfx_db": 0.0},
        "desenho": {"fonte": "blackops", "tema": "tinta", "ritmo": [0.08, 0.02]},
        "entrega": {"pasta": "videos/hooks"},
        "recursos": ["legenda", "emenda", "abertura", "trilha"],
    },
    # Destaque de live: corta gordura, mantém energia do ao vivo.
    "live-highlight": {
        "herda": "aula-ccnp",
        "corte": {"afinacao": "tight", "ajuste": {"sil_cut": 0.5, "pause_keep": 0.35}},
        "graduacao": {"preset": "warm_cinematic"},
        "efeito": {"abertura": None, "emenda": "glitch", "emenda_min": 15.0, "emenda_forca": "subtle"},
        "desenho": {"fonte": "teko", "tema": "claro"},
        "entrega": {"pasta": "videos/live"},
        "recursos": ["legenda", "emenda", "trilha"],
    },
    # Carrossel / feed 4:5 Instagram.
    "carrossel": {
        "bruto": "camera",
        "corte": {"afinacao": "tight"},
        "imagem": {"orientacao": "16:9", "canvas": "1080x1350", "qualidade": "reel"},
        "graduacao": {"preset": "soft_pastel"},
        "desenho": {"fonte": "outfit", "tema": "claro", "legenda_layout": "faixa"},
        "efeito": {"abertura": None, "emenda": None},
        "entrega": {"pasta": "videos/carrossel"},
        "recursos": ["legenda", "trilha"],
        "adaptadores": {"legenda": "liso", "trilha": "cama"},
    },
}


# ---- resolver ---------------------------------------------------------------


def _funde(base: dict, novo: dict, onde: str) -> dict:
    """Funde eixo a eixo, recusando botão que não existe."""
    saida = copy.deepcopy(base)
    for eixo, valores in novo.items():
        if eixo not in EIXOS:
            raise KeyError(
                f"eixo '{eixo}' não existe em {onde}. "
                f"Disponíveis: {', '.join(sorted(EIXOS))}"
            )
        if not isinstance(valores, dict):
            raise TypeError(f"o eixo '{eixo}' em {onde} tem que ser um dicionário")
        desconhecidos = set(valores) - set(EIXOS[eixo])
        if desconhecidos:
            raise KeyError(
                f"botão que não existe no eixo '{eixo}' de {onde}: "
                f"{', '.join(sorted(desconhecidos))}. "
                f"Disponíveis: {', '.join(sorted(EIXOS[eixo]))}"
            )
        saida[eixo].update(copy.deepcopy(valores))
    return saida


def _recursos(atuais: list[str], pedido: Any, onde: str) -> list[str]:
    """Aceita a lista inteira, ou {"+": [...], "-": [...]}. Sempre sai em ordem
    de posição — recurso ligado entra no lugar dele, não no fim."""
    if isinstance(pedido, dict):
        saida = list(atuais)
        for r in pedido.get("+", []):
            if r not in saida:
                saida.append(r)
        for r in pedido.get("-", []):
            if r in saida:
                saida.remove(r)
    else:
        saida = list(pedido)

    desconhecidos = [r for r in saida if r not in RECURSOS]
    if desconhecidos:
        raise KeyError(
            f"recurso que não existe em {onde}: {', '.join(desconhecidos)}. "
            f"Disponíveis: {', '.join(sorted(RECURSOS))}"
        )
    return sorted(saida, key=lambda r: RECURSOS[r]["posicao"])


def _adaptadores(base: dict, pedido: Any, onde: str) -> dict[str, str]:
    """Funde a escolha de adaptador, recusando recurso ou adaptador que não existe.

    Errar aqui é escolher um jeito de entregar que ninguém implementou, e
    descobrir isso no meio do render. O erro sai na entrada, listando os válidos.
    """
    saida = dict(base)
    for recurso, escolha in (pedido or {}).items():
        escolhas = RECURSOS.get(recurso, {}).get("adaptadores")
        if not escolhas:
            tem_costura = sorted(r for r, v in RECURSOS.items() if v.get("adaptadores"))
            raise KeyError(
                f"o recurso '{recurso}' em {onde} não tem adaptador para escolher. "
                f"Com escolha: {', '.join(tem_costura) or '(nenhum)'}"
            )
        if escolha not in escolhas:
            raise KeyError(
                f"adaptador '{escolha}' não existe para o recurso '{recurso}' em "
                f"{onde}. Disponíveis: {', '.join(sorted(escolhas))}"
            )
        saida[recurso] = escolha
    return saida


def resolver(declaracao: dict, nome: str = "?", catalogo: dict | None = None,
             _vistos: tuple[str, ...] = ()) -> Estilo:
    """Resolve uma declaração de estilo, seguindo a herança até a raiz."""
    catalogo = ESTILOS if catalogo is None else catalogo

    if nome in _vistos:
        volta = " -> ".join(_vistos + (nome,))
        raise ValueError(f"herança em ciclo: {volta}")

    pai_nome = declaracao.get("herda")
    if pai_nome:
        if pai_nome not in catalogo:
            raise KeyError(
                f"o estilo '{nome}' herda de '{pai_nome}', que não existe. "
                f"Disponíveis: {', '.join(sorted(catalogo))}"
            )
        pai = resolver(catalogo[pai_nome], pai_nome, catalogo, _vistos + (nome,))
        base_eixos, base_recursos, base_bruto = pai.eixos, pai.recursos, pai.bruto
        base_adapt = pai.adaptadores
    else:
        base_eixos = {e: copy.deepcopy(v) for e, v in EIXOS.items()}
        base_recursos, base_bruto, base_adapt = [], "live", {}

    proprios = {k: v for k, v in declaracao.items()
                if k not in ("herda", "bruto", "recursos", "adaptadores")}
    eixos = _funde(base_eixos, proprios, f"o estilo '{nome}'")
    recursos = _recursos(base_recursos, declaracao.get("recursos", base_recursos),
                         f"o estilo '{nome}'")
    adapt = _adaptadores(base_adapt, declaracao.get("adaptadores"),
                         f"o estilo '{nome}'")
    return Estilo(nome=nome, bruto=declaracao.get("bruto", base_bruto),
                  eixos=eixos, recursos=recursos, adaptadores=adapt)


# ---- a marca do aluno -------------------------------------------------------
#
# A pasta `marca/`, na raiz da fábrica, é do aluno e sobrevive à atualização do kit:
# o kit novo troca tools/, a marca fica. Os estilos dela entram no catálogo no mesmo
# molde dos daqui (herda, eixos, recursos) e só acrescentam nome: trocar um que o kit
# traz faria a aula e o vídeo dele divergirem calados.

MARCA = Path(__file__).resolve().parents[3] / "marca"


def da_marca(pasta: Path = MARCA) -> dict[str, dict[str, Any]]:
    """Os estilos de `pasta/estilos.json`, conferidos contra o catálogo. Sem o arquivo, nada.

    O erro sai na importação, com o arquivo no começo: estilo de marca quebrado não
    pode ser descoberto no meio do render. Chave que começa com `_` é nota."""
    arq = pasta / "estilos.json"
    if not arq.is_file():
        return {}
    try:
        lidos = json.loads(arq.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"{arq}: JSON quebrado na linha {e.lineno}, coluna {e.colno}: {e.msg}") from None
    if not isinstance(lidos, dict) or not all(isinstance(d, dict) for n, d in lidos.items()
                                              if not n.startswith("_")):
        raise ValueError(f"{arq}: tem que ser {{\"nome-do-estilo\": {{\"herda\": ..., ...}}}}")
    novos = {n: {k: v for k, v in d.items() if not k.startswith("_")}
             for n, d in lidos.items() if not n.startswith("_")}
    # o que já está no catálogo com a mesma declaração é esta marca, lida na importação: ler de novo vale
    repetidos = sorted(n for n in set(novos) & set(ESTILOS) if ESTILOS[n] != novos[n])
    if repetidos:
        raise ValueError(f"{arq}: '{repetidos[0]}' já existe no kit. Dê outro nome e herde dele "
                         f"(\"herda\": \"{repetidos[0]}\")")
    juntos = {**ESTILOS, **novos}
    for nome, decl in novos.items():
        try:
            resolver(decl, nome, juntos)
        except (KeyError, TypeError, ValueError) as e:
            raise ValueError(f"{arq}: {e.args[0]}") from None
    return novos


ESTILOS.update(da_marca())


def estilo(nome: str, **sobrescritas) -> Estilo:
    """Resolve um estilo por nome, com sobrescritas do plano do vídeo.

    Nome que não existe estoura listando os válidos — o erro não pode ser
    descoberto no meio do render.
    """
    if nome not in ESTILOS:
        raise KeyError(
            f"estilo '{nome}' não existe. Disponíveis: {', '.join(sorted(ESTILOS))}"
        )
    base = resolver(ESTILOS[nome], nome)
    if not sobrescritas:
        return base

    recursos = sobrescritas.pop("recursos", None)
    adapt = sobrescritas.pop("adaptadores", None)
    eixos = _funde(base.eixos, sobrescritas, f"o plano (sobre '{nome}')")
    lista = (_recursos(base.recursos, recursos, f"o plano (sobre '{nome}')")
             if recursos is not None else base.recursos)
    return Estilo(nome=nome, bruto=base.bruto, eixos=eixos, recursos=lista,
                  adaptadores=_adaptadores(base.adaptadores, adapt,
                                           f"o plano (sobre '{nome}')"))


def catalogo() -> list[dict[str, Any]]:
    """O que existe, para um comando listar. A prosa aponta para aqui em vez de
    repetir a lista e envelhecer sozinha."""
    linhas = []
    for nome in sorted(ESTILOS):
        e = estilo(nome)
        linhas.append({
            "nome": nome,
            "orientacao": e.orientacao,
            "bruto": e.bruto,
            "corte": e.eixos["corte"]["afinacao"],
            "recursos": e.recursos,
            "entrega": e.eixos["entrega"]["pasta"],
        })
    return linhas


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description="Os estilos de edição que existem")
    ap.add_argument("nome", nargs="?", help="mostra um estilo inteiro")
    args = ap.parse_args()

    if args.nome:
        e = estilo(args.nome)
        print(f"{e.nome}  ({e.orientacao}, parte de {e.bruto})")
        print(f"  recursos: {', '.join(e.recursos) or '(nenhum)'}")
        for eixo, valores in e.eixos.items():
            print(f"  {eixo}:")
            for k, v in valores.items():
                print(f"    {k} = {v}")
        return

    print(f"{'estilo':<18} {'quadro':<7} {'bruto':<12} {'corte':<9} recursos")
    for l in catalogo():
        print(f"{l['nome']:<18} {l['orientacao']:<7} {l['bruto']:<12} "
              f"{l['corte']:<9} {', '.join(l['recursos'])}")


if __name__ == "__main__":
    main()
