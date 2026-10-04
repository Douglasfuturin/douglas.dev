---
name: editar-video
description: Use when the user wants to edit a video — cut silences, remove filler words and stammers, enhance voice, burn captions, export mp4. Covers long-form lessons in 16:9 and vertical reels in 9:16. Also when they ask to update their editing preferences.
---

# Editor de Vídeo com Claude Code

Pipeline de edição guiado pela transcrição. Corta silêncio, tira vício de fala
e gaguejo, trata a voz, normaliza loudness. Dois formatos: aula (16:9) e reel
(9:16).

Nada renderiza sem o usuário confirmar o plano de corte. Render é caro em tempo
e a decisão de o que cortar é dele, não sua.

## Caminhos

A skill vive em `~/.claude/skills/editar-video/`, que é o `SKILL_DIR`.

- **Python**: `<SKILL_DIR>/.venv/bin/python`
- **Helpers**: `<SKILL_DIR>/helpers/`
- **Preferências**: `<SKILL_DIR>/preferences.md`

Os helpers se importam entre si, então rode-os **de dentro de `helpers/`** e
chame o Python por `../.venv/bin/python`. Chamar de outro lugar quebra em
`import clean_edl`.

## Preferências

Leia `preferences.md` antes de qualquer edição.

**Se o arquivo não existir**, esta é a primeira vez. Chame a skill `grill-me`,
que vem instalada junto com este kit, e passe a ela o que descobrir abaixo. O
grill pergunta em rodadas, com uma recomendação por pergunta — é o que separa
uma entrevista de um formulário.

- Formato principal: aula 16:9, reel 9:16, ou os dois
- Resolução de saída: 1080p, 1440p ou 4K
- Idioma falado nos vídeos
- Legendas queimadas: quer? em que estilo
- Intro e outro: corte seco, fade, ou nenhum
- B-roll: costuma ter arquivo para sobrepor
- Referência visual ou paleta que os vídeos seguem

Escreva o arquivo antes de seguir para a transcrição.

```markdown
# Preferências de Edição

## Perfil
- Formato principal:
- Resolução:
- Idioma:

## Visual
- Intro/outro:
- Legendas:
- B-roll:
- Referência visual:

## Notas
```

Quando o usuário pedir para atualizar preferências, pergunte de novo e
reescreva o arquivo. Não passe pela transcrição.

## Passo 1 — Transcrever

```bash
cd <SKILL_DIR>
.venv/bin/python helpers/transcribe.py <video> --model large-v3 --language pt
```

Troque `--language` pelo idioma de `preferences.md`.

Sai em `<pasta_do_video>/edit/<slug>/transcript.json`. Mostre o caminho.

Na primeira vez o modelo large-v3 (~1,5 GB) é baixado e fica em cache. Avise
antes, senão o usuário acha que travou.

## Passo 2 — Propor o plano de corte

Leia o transcript e proponha.

Para aula:

- Divida por tópico, não por relógio
- Cada aula no tamanho que `preferences.md` pedir (padrão: 5–10 min de conteúdo real)
- Abra em frase confiante: corte o rodeio do início
- Tire Q&A sem resposta, meta-comentário e volta de troubleshooting

Para reel:

- Hook nos primeiros 3s, a frase de maior impacto do material
- Duração dentro do que o usuário pediu
- Marque tempo de b-roll se `preferences.md` disser que ele usa

**Espere a confirmação.** Só depois dela escreva o JSON e renderize.

## Passo 3 — Renderizar

Um comando, para todo tipo de vídeo. O que muda é o **estilo**.

```bash
cd <SKILL_DIR>/helpers
../.venv/bin/python fabrica.py <plano.json> --seco   # confere sem renderizar
../.venv/bin/python fabrica.py <plano.json>          # renderiza e entrega
```

**Rode `--seco` primeiro, sempre.** Ele monta a cadeia inteira e imprime os
comandos, o corte calculado e o custo estimado, sem esperar render. É a diferença
entre descobrir um erro em dois segundos ou em vinte minutos.

Os estilos que existem, e quem lista é o código:

```bash
../.venv/bin/python estilo.py            # todos
../.venv/bin/python estilo.py aula-ccnp  # um inteiro, eixo a eixo
```

| Estilo | Quadro | Parte de | Para |
|---|---|---|---|
| `aula-ccnp` | 16:9 | live | aula longa de um módulo |
| `reel-mono` | 9:16 | live | corte vertical de live, rosto em cima |
| `reel-camera` | 9:16 | camera | reel gravado na câmera, com b-roll |
| `quadro` | 16:9 | board | vídeo de quadro deitado |
| `quadro-vertical` | 9:16 | board | vídeo de quadro em pé |
| `vsl` | 9:16 | avatar | VSL com apresentador gerado |

### plano.json

```json
{
  "estilo": "aula-ccnp",
  "fonte": "/abs/path/live.mp4",
  "transcript": "/abs/path/edit/<slug>/transcripts/<stem>.json",
  "slug": "nome-da-aula",
  "projeto": "curso",
  "janelas": [[120.0, 640.0]],
  "drops": []
}
```

O **plano** é o que é daquele vídeo: fonte, janelas, drops, conteúdo. O **estilo**
é o que vale para todo vídeo daquele tipo. Ajuste de um vídeo só entra como
sobrescrita de eixo no plano; quando ele se repete, vira estilo novo herdando.

O caminho antigo, um programa por formato, ainda está no kit:

```bash
../.venv/bin/python make_lessons.py <lessons.json>   # aulas em lote
../.venv/bin/python build_reel.py <reel.json>        # reel 9:16 só com ffmpeg
```

- `--build-only` → só os EDLs, para revisar corte sem renderizar
- `--only <slug>` → uma aula só
- `--no-final-transcript` → não transcreve o mp4 pronto (o padrão transcreve e
  guarda em `transcripts-finais/<slug>.json`, para buscar dentro da aula depois)

## VSL com apresentador gerado

O estilo `vsl` parte do bruto `avatar`: o apresentador é gerado pelo HeyGen a
partir da voz real do usuário. Isso muda uma coisa que manda no resto — **não há
imagem na hora do corte**. Quem corta a VSL corta o áudio, e o quadro só nasce
depois da geração.

A `fonte` do plano é o take de voz, não um vídeo. A fábrica trata a voz, apara as
pausas e **para no portão**:

```bash
../.venv/bin/python fabrica.py vsl.json --seco
```

O portão (`pre_voo.py`) recusa enquanto faltar o áudio tratado, aparado e ouvido.
A aprovação por ouvido é um arquivo `<audio>.ok` criado à mão, depois de escutar.

Não contorne o portão. Ele existe porque 83% dos créditos de uma sessão foram
embora no mesmo padrão, repetido quatro vezes: gerar, descobrir que o áudio
estava errado, gerar de novo. Medir antes custa um segundo.

Passado o portão, gere no HeyGen com os parâmetros que o `pre_voo` imprime, ponha
os blocos gerados em `"gerado": [...]` e rode de novo. A emenda é pelo `junta.py`,
nunca por `ffmpeg -f concat`: o HeyGen entrega a 25 fps, o projeto roda a 30, e o
demultiplexador mantém a taxa do primeiro arquivo sem reescrever o relógio — um
corte de 78s já saiu com 94s de imagem em cima de 70s de áudio.

### lessons.json

```json
{
  "video": "/abs/path/video.mp4",
  "transcript": "/abs/path/edit/<slug>/transcript.json",
  "canvas": "1920x1080",
  "pause_keep": 0.9,
  "lessons": [
    {
      "slug": "nome-da-aula",
      "title": "Título",
      "windows": [[inicio_s, fim_s]],
      "drops": []
    }
  ]
}
```

`canvas` segue a resolução de `preferences.md`. Deixe `glitch` e `overlays`
fora: efeito que o usuário não pediu é efeito que ele vai mandar refazer.

`pause_keep` é o fôlego devolvido em cada emenda de ar morto, em segundos.
Padrão 0.9. Suba se o corte ficar sufocado, baixe se arrastar. `sil_cut`
(padrão 2.0) é a pausa a partir da qual o corte acontece.

### reel.json

```json
{
  "video": "/abs/path/video.mp4",
  "transcript": "/abs/path/edit/<slug>/transcripts/<stem>.json",
  "output": "/abs/path/reel.mp4",
  "windows": [[162.5, 187.5]],
  "crop": "crop=810:1440:555:0",
  "captions": true
}
```

`windows` são os trechos da live, em segundos, na ordem. Dentro deles o
silêncio some sozinho — `silence_edl` corta pelo áudio real, não pelo
timestamp da palavra.

`crop` é a moldura 9:16, **medida no quadro da live**, no formato do filtro
`crop` do ffmpeg (`crop=largura:altura:x:y`). Sem ele o corte é a faixa
central: serve para rosto, estraga gravação de tela — o texto fica cortado
dos dois lados. Em screencast, aponte o `crop` para a região que importa.

`captions` queima a legenda a partir do `transcript`, sem instalar nada.

## Passo 4 — Medir o fôlego da aula

Um corte apertado passa em qualquer conferência de conteúdo — nenhuma palavra
se perde — e mesmo assim entrega uma aula que o aluno não acompanha, porque
sumiu o tempo de processar a virada de tópico. Isso não aparece na transcrição.
Aparece aqui.

```bash
cd <SKILL_DIR>/helpers
../.venv/bin/python folego.py --words <transcript.json> --edl edl_<slug>.json
```

Passe um `--edl` por `--words`, na mesma ordem, para medir várias aulas juntas.
Reprovou? Suba o `pause_keep` do `lessons.json` e renderize de novo. Não é
gosto: é o que separa a aula que respira da que corre.

## O que sai pronto, sem pedir

- Corte de silêncio
- Vício de fala fora: "é", "tipo", "então", "uh", "um"
- Gaguejo e repetição imediata fora
- Voz tratada: denoise, EQ de presença, compressão leve
- Loudness em −14 LUFS

Intro, outro, glitch, overlay e legenda só entram se `preferences.md` pedir ou
se o usuário pedir no prompt.

## Legenda

Funciona sem instalar nada. O ffmpeg do homebrew-core vem sem libass, então o
filtro `subtitles` não existe na maioria das máquinas — o kit não usa ele.
`legendar.py` desenha os cues com Pillow e sobrepõe. Quando existe libass, o
`render.py` usa o caminho nativo; quando não, cai no desenho, na mesma altura
do quadro.

Não mande o usuário instalar outro ffmpeg por causa de legenda.

Para queimar um `.srt` em um vídeo pronto, avulso:

```bash
cd <SKILL_DIR>/helpers
../.venv/bin/python legendar.py <video.mp4> <legenda.srt> -o <saida.mp4>
```

## Overlays animados precisam de Node

`lesson_overlays.py` renderiza os cards via `npx hyperframes`, então quer
Node 20+. Os dois arquivos de config viajam no kit
(`<SKILL_DIR>/assets/scaffold/`); o resto vem por npx na hora. Sem Node, deixe
`overlays` fora do `lessons.json` — que já é o padrão recomendado acima.

## Saída

- Aula: `<pasta_do_lessons.json>/<slug>.mp4`
- Reel: o campo `output` do reel.json

Mostre o caminho e pergunte antes de mover para `~/videos/<projeto>/`.
