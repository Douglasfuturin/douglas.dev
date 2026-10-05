---
name: fabrica-de-conteudo
description: Use quando o usuário pedir um reel (vertical 9:16) — editorial com voz clonada e avatar, com avatar da HeyGen, ou gravado no celular —, pedir para editar um vídeo que já tem (o avatar que gerou na HeyGen, o do celular), um criativo de anúncio com cara de filmagem (câmera de segurança, plantão, documentário), legenda queimada, trilha, capa, ou quando um plano da fábrica der erro. Na primeira vez nesta pasta, confere e adequa a máquina antes de tudo. Roda a Fábrica de Conteúdo com IA desta pasta.
---

# Fábrica de Conteúdo com IA

A **fábrica** recebe **estilo** e **plano** e devolve o **final**. O plano diz o que é
daquele vídeo (a voz, o texto, as peças). O estilo diz o que vale para todo vídeo
daquele tipo (corte, voz, imagem, desenho, trilha, entrega). Rode tudo da raiz
desta pasta, com `uv run python`.

```bash
uv run python tools/video-use/helpers/estilo.py                 # os estilos
uv run python tools/video-use/helpers/estilo.py reel-editorial  # um inteiro, eixo a eixo
uv run python tools/video-use/helpers/fabrica.py plano.json --seco   # confere, não renderiza
uv run python tools/video-use/helpers/fabrica.py plano.json          # renderiza e entrega
uv run python tools/video-use/helpers/fabrica.py plano.json --desde desenho
```

## Primeira vez nesta máquina

Se existe `.fabrica-ok` na raiz, pule esta seção. Se não, faça isto antes de qualquer
vídeo, sem parar a cada passo. Só pare para avisar quando algo pedir a senha de
administrador: quem digita é o usuário, no terminal dele (no Claude Code, `! <comando>`).

Os comandos desta seção são de bash. Num terminal que não é bash (o PowerShell do
Windows), rode o equivalente.

**1. Sistema.** `uname -sm`. No Windows, pelo Git Bash, a resposta começa com `MINGW64`.

**2. O que falta.** Confira `ffmpeg -version`, `ffprobe -version` e `uv --version`, e
instale só o que faltar:

| Sistema | Comandos |
|---|---|
| Mac | `brew install ffmpeg uv`. Sem Homebrew, o usuário roda o instalador de brew.sh, que pede a senha dele |
| Windows | `winget install -e --id Gyan.FFmpeg`, `winget install -e --id astral-sh.uv` e `winget install -e --id Python.Python.3.12`; depois `setx PYTHONUTF8 1` e, nesta sessão, `export PYTHONUTF8=1` |
| Linux | `sudo apt install ffmpeg` (Fedora: `sudo dnf install ffmpeg`) e `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

Depois, na raiz:

```bash
uv sync                               # Python 3.10+ e as dependências do pyproject.toml
uv run playwright install chromium    # no Linux: install --with-deps chromium
[ -f .env.local ] || cp .env.local.exemplo .env.local   # as chaves o usuário preenche depois
```

Se o uv não instalar de jeito nenhum: `python -m venv .venv`, as dependências do
`pyproject.toml` pelo `pip` desse `.venv`, e `.venv/bin/python` (Windows:
`.venv/Scripts/python`) no lugar de `uv run python` daqui em diante.

**3. Conferência.** Não chama ElevenLabs, HeyGen nem Higgsfield, e não lê chave.

```bash
for t in tools/video-use/helpers/test_*.py; do
  uv run python "$t" > /dev/null 2>&1 && echo "ok      $t" || echo "FALHOU  $t"
done
uv run python tools/video-use/helpers/fabrica.py exemplos/reel-editorial/reel.json --seco
uv run python tools/video-use/helpers/fabrica.py exemplos/criativo/plano.json --seco
```

Pronto é: nenhum `FALHOU`, e os dois `--seco` saem sem erro, parados no que cobra. O do
reel editorial tem um passo só, `narração`, marcado `cobra: ElevenLabs`. O do criativo tem
dois: `cenas` (`cobra: Higgsfield`) e `narração`. Para ler a saída de um teste que falhou,
rode só ele.

**4. Se falhar, conserte a máquina e rode a conferência de novo**, até passar:

- `command not found` logo depois de instalar: o PATH desta sessão é velho. Ache o
  programa (`which`; no Windows, `where`) e exporte o caminho, ou peça ao usuário para
  reabrir o agente.
- `ModuleNotFoundError`: `uv sync` de novo.
- `UnicodeDecodeError` ou `cp1252`: falta o `PYTHONUTF8=1`.
- Chromium ou Playwright: o `playwright install` de novo (no Linux, com `--with-deps`).
- Arquivo que não existe, com caminho relativo: rode da raiz desta pasta.

Nunca edite teste ou helper para passar, e nunca apague arquivo do pacote. Se a falha
não é da máquina (um `AssertionError` com tudo instalado, um arquivo do pacote que
falta), ou se a mesma falha sobrevive a três consertos, pare. Diga ao usuário qual
teste falhou e cole a saída exata, para ele mandar ao suporte.

**5. Marcador.** Com tudo passando:

```bash
echo "$(date +%F) $(uname -sm)" > .fabrica-ok
```

Para conferir de novo (pacote novo, computador novo), apague o `.fabrica-ok`.

## Os tipos

Todo vídeo sai pela **cadeia**: um plano num estilo, o `--seco`, o render. Todo plano tem
`estilo`, `slug` (o nome do final) e `fonte`, e mora na pasta do vídeo
(`videos/<slug>/reel.json`, ao lado do material). Escolha o tipo pelo que o usuário já tem:

| Ele tem | Tipo | Estilo |
|---|---|---|
| um assunto, para a voz clonada e o avatar | Reel editorial | `reel-editorial` |
| o webm do avatar gerado na HeyGen com fundo removível, ou o vídeo do celular exportado sem fundo (webm com alfa); com ou sem a voz à parte | Reel do webm pronto | `reel-editorial` |
| a voz gravada, sem rosto ainda | Reel com avatar | `reel-avatar` |
| o vídeo do celular com o fundo dele | Reel do celular | `reel-camera` |
| um produto para anunciar com cenas | Criativo de cinema | `criativo`, `criativo-reel` |

Todo reel sai com **capa** e, menos o do celular, com **trilha** (regras 6 e 7). Com o
**banco de cenas** na pasta, o fundo atrás do rosto vem dele (abaixo).

**Reel editorial** — estilo `reel-editorial`, bruto `avatar`. A narração sai da voz
clonada na ElevenLabs, o rosto da HeyGen entra no cartão ou cheio, e painel e peças
vão por cima. Sai também a capa e a versão do YouTube. O plano pede `narracao` (o
texto como se fala) e `palavra` (a da chamada), `fonte` (a voz, que o passo da
narração gera), `imagem.fundo` (a placa do look dele na HeyGen), `avatar.arquivo` (o
webm sem fundo), `base` (o take, trecho a trecho, de 0 a `dur`), `pecas` e
`trilha.faixa`; `capa` e `youtube` se ele quiser. Formato inteiro no topo de
`reel_editorial.py`; exemplo em `exemplos/reel-editorial/`.

**Reel do webm pronto** — o mesmo estilo `reel-editorial`, sem nada pago: o rosto já
existe. É o pedido "edita esse vídeo pra reel: corta as pausas, põe legenda, arruma a tela e
faz a capa". O plano parte do molde `exemplos/reel-do-webm/reel.json`:

- `fonte` é a voz que foi pra HeyGen; sem ela à parte, o próprio webm. `avatar.alinha`
  (`true`) acha cada pedaço da voz no áudio do webm, e o rosto acompanha a voz. Onde a voz
  fala e o webm não tem rosto, o passo `alinha` recusa a base e diz onde o rosto existe. O
  buraco curto no meio da fala vira um trecho `congela` que começa ainda no rosto: o quadro
  para, como a pose da capa. O fim sem rosto (a chamada gravada depois) vai sobre uma `cena`
  do banco, com a peça da chamada.
- **Corta as pausas:** a voz é o relógio. Transcreva antes do plano (`transcribe.py <voz>
  --model large-v3 --language pt --edit-dir videos/<slug>`). Vão de mais de 0,6 s entre
  palavras é pausa: `apara_pausas.py <voz> --transcript videos/<slug>/transcripts/<voz>.json -o
  <voz>-aparada.wav`, e a aparada vira a `fonte`; o `alinha` leva o rosto junto. Voz sem vão
  assim fica como está.
- **Põe legenda:** a fala em duas letras sai sozinha do transcript da voz.
- **Arruma a tela:** a `base` trecho a trecho, o rosto `cheio` sobre o fundo do banco que
  troca na fala (`fabrica-composicao`), o gancho parado no quadro 0 e a chamada só no fim.
- **Faz a capa:** o bloco `capa`, com `foto` `["<o webm>", <segundo>]`, um quadro do rosto já
  sem fundo.
- Voz que traz várias chamadas no fim vira `fechos`, um final por chamada
  (`reel_editorial.py`, topo). O primeiro da lista é o final que se posta: no reel, o que pede
  para comentar a `palavra`. "Toca em saiba mais" é de anúncio (o botão só existe lá), e "rola
  aí" é da página.

Pronto é: o render até o fim, o final terminando na chamada da `palavra`, e a folha
(`_trabalho/folha-1fps.png`) com o rosto em todo trecho que tem fala dele, o fundo trocando
onde a voz nomeia o lugar e a capa ao lado do final.

**Reel com avatar** — estilo `reel-avatar`, bruto `avatar`. A voz que ele gravou passa
pelo portão (aparada e medida) antes da HeyGen; depois vêm legenda, b-roll e trilha. O
plano pede `fonte` (a voz), `transcript` (o do `transcribe.py`; em `transcripts/<voz>.json`
ele se refaz sozinho quando a voz muda), `gerado` (os vídeos que a HeyGen devolveu;
sem eles a cadeia para no portão), `broll` (beats com `arquivo`, `em` e `dur`) e
`trilha.faixa`. Para gastar menos crédito, o `trechos_de_rosto.py` junta o rosto de
vários reels numa geração só.

**Reel do celular** — estilo `reel-camera`, bruto `camera`. Corta o silêncio do que ele
gravou, põe legenda e b-roll, e a legenda pode passar atrás da pessoa. Não tem trilha.
O plano pede `fonte` (o vídeo), `transcript` (antes, com `transcribe.py <vídeo> --model
large-v3 --language pt`), `drops` (o que sai à mão, se houver) e `broll`.

**Criativo de cinema** — estilos `criativo` (o anúncio) e `criativo-reel` (o mesmo para
o feed: legenda em faixa, trilha que some mais devagar), bruto `banco`. Voz em off
sobre cenas do banco de cenas, cada cena cobrindo o trecho da fala que ilustra, com o
acabamento de filmagem achada (`cctv`, `telejornal`, `documentario`, `filmadora`,
`celular`). O plano pede `banco` (a pasta do banco de cenas), `trechos` (`[fala, cena]`, na ordem),
`locutor` (o `id` da voz na ElevenLabs), `fonte` (a voz, que o passo que cobra gera),
`cor`, `punch` e `trilha.faixa`. Formato inteiro no topo de `criativo.py`; exemplo em
`exemplos/criativo/`.

## O banco de cenas

O **banco de cenas** é a pasta com o `cenas.json`, a ficha de cada cena (`id`, `arquivo`,
`acabamento`, `janela`, `ilustra`); a do usuário fica em `videos/banco-de-cenas/`. Os dois
tipos que usam o banco escolhem a cena pelo `ilustra`, o que ela mostra: o criativo cobre a
fala com ela, e o reel editorial a põe atrás do rosto, no trecho em que a voz fala daquilo
(`"fundo": "@../banco-de-cenas/<arquivo>"`; `fabrica-composicao`, "O fundo atrás do rosto").

O pacote não traz cenas: o banco é dele, e quem gera as cenas é o **lote**. Antes de
escrever qualquer cena, leia `docs/linguagem-do-criativo.md` (primeiro quadro, laço,
choque cômico e prova literal, os acabamentos, as regras do banco) e escreva com ele o
cartão de conceito. O lote é um `lote.json` na pasta do banco: `estetica` (um nome do
`estetica.json`, na pasta do lote ou na de cima, cujo prompt entra no fim de toda
cena), e em `cenas` cada uma com `modelo` (`kling`), `prompt` (em inglês, só a cena, a
câmera e a composição) e a ficha (`acabamento`, e se quiser `hora`, `cam`, `janela` e
`data`, a que a filmadora escreve no canto, em AAAA-MM-DD; sem ela, a do dia do render).
Com `lote` no plano, a fábrica para no passo `$ cenas` enquanto faltar cena no disco,
com a estimativa pela tabela. Quem gera é o `lote.py`:

```bash
uv run python tools/video-use/helpers/lote.py <banco>/lote.json          # pergunta o preço à API, não gasta
uv run python tools/video-use/helpers/lote.py <banco>/lote.json --gera   # gera, baixa no banco e escreve a ficha
```

A chave é `HIGGSFIELD_KEY_ID` e `HIGGSFIELD_KEY_SECRET` no `.env.local` (no site da
Higgsfield, a página de API). A API cobra de uma carteira em dólar, separada do plano.
Depois de baixar, assista cada cena com o usuário e acerte a `janela` no `cenas.json`.
Cena ruim vai para `descartadas/` e volta ao lote com outro id.

**O usuário dentro da cena:** a cena com `modelo` `wan` põe o rosto dele. O lote leva
`rosto` com duas fotos dele (de frente e neutra, fundo liso), e o prompt da cena, o
bloco fixo de identidade e figurino da seção "Você dentro da cena" do guia.

## As skills de edição

Esta skill diz como rodar a fábrica. O critério de edição mora em cinco skills ao lado
desta, na mesma pasta. Antes de escrever ou mexer num plano, leia a que cobre o que
você vai decidir:

| Skill | Decide |
|---|---|
| `fabrica-legendas` | qual legenda, duas letras, palavra marcada, zona segura do Instagram, quebra de linha |
| `fabrica-composicao` | tela dividida, cartão com a cabeça saindo, 40/60 com cena, o fundo atrás do rosto |
| `fabrica-movimento` | o que vira peça, no tempo da fala, uma ênfase por peça, tela nunca vazia |
| `fabrica-ritmo` | corte de silêncio, cortes e zoom, gancho no primeiro quadro, chamada só no fim |
| `fabrica-estilo` | tema claro ou tinta, trilha até o fim, capa, versão do YouTube, entrega |

O `GUIA-DE-PEDIDOS.md`, na raiz, traz o pedido pronto para cada tipo de vídeo, técnica e
etapa. Quando o usuário colar um deles, faça o que ele promete, nem mais nem menos.

## Regras

1. **Sempre `--seco` primeiro.** Mostre ao usuário a cadeia e o que custa. Só renderize
   depois que ele confirmar.
2. **Nada pago roda sozinho.** Voz, avatar e cena nova viram passo que **cobra**: a
   fábrica para e imprime o comando. Quem decide gastar é o usuário: mostre o custo e
   espere o sim antes de rodar o `--gera` do lote ou a narração. O teto de gerações de
   voz está no estilo (`voz.sintese.tentativas`); não contorne.
3. **Chave só no `.env.local`**, na raiz. Nunca imprima o valor de uma chave.
4. **O fundo atrás do rosto é do usuário:** a placa do look dele na HeyGen (`imagem.fundo`)
   ou as cenas do banco dele, trecho a trecho (`fundo`). Sem placa, `imagem.fundo` fica com a
   do exemplo (`exemplos/reel-editorial/fundo.png`, neutra) e todo trecho de rosto leva o seu
   `fundo` do banco. A HeyGen não entrega a
   placa, e o `INSTALAR.md` ("O look e a placa da HeyGen") diz como fazer e como achar o ID
   do look. A chave da HeyGen só lista looks; o rosto se gera no site (regra 5).
5. **O avatar é gerado à mão, no site da HeyGen.** O passo `heygen` deixa pronto o
   `avatar/geracao.wav`. O usuário sobe esse áudio, gera com fundo removível, baixa o
   webm em `avatar/rosto.webm` e roda a fábrica de novo.
6. **Trilha sempre.** A do usuário (a da ElevenLabs Music, ou outra com licença) vai em
   `trilha.faixa`, com o caminho do arquivo. Sem a dele, uma das três de `exemplos/trilhas/`,
   pelo tom da fala: `lofi-calma`, `groove-leve` ou `animada` (CC0; a licença no `LEIA-ME.md`
   de lá). `"nenhuma"` só quando ele disser que põe a música pelo app do Instagram.
7. **Capa sempre.** No reel editorial, o bloco `capa` do plano; sem foto dele, um quadro do
   webm (`"foto": ["<o webm>", <segundo>]`). Nos outros, a capa avulsa (`fabrica-estilo`,
   "Capa").
8. Tipo de vídeo novo é **estilo novo** herdando de um que chega perto (`herda` no
   `ESTILOS` do `estilo.py`, ou no `marca/estilos.json` se for da marca do usuário),
   não script novo.

## Peças

O que vai por cima do vídeo (gancho, chip, painel, chamada) é **peça** de `tools/v2`.
Liste com `uv run python tools/v2/v2.py lista`. Peça nova entra em `tools/v2/pecas/`
e no catálogo (`v2.py catalogo`), nunca como HTML solto na pasta do vídeo.

## Quando dá erro

Leia a mensagem: a fábrica recusa antes do primeiro comando e diz o campo que falta.
Corrija o plano e rode `--seco` de novo. Depois de um passo que já rodou, use
`--desde <etapa>` (`corte`, `render`, `desenho`, `composicao`, `trilha`, `entrega`)
para não refazer o que está em disco. Para conferir que a fábrica segue inteira:

```bash
uv run python tools/video-use/helpers/test_fabrica.py
```

Os finais saem em `videos/`, na pasta que o estilo manda (`estilo.py`, eixo `entrega`).
