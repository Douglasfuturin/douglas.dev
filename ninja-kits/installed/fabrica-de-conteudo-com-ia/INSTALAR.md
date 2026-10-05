# Fábrica de Conteúdo com IA — Instalação

Descompacte o ZIP onde quiser (por exemplo, na sua pasta pessoal). Abra o seu
agente de IA **dentro** da pasta `fabrica-de-conteudo` e cole este pedido:

```
Esta pasta é a Fábrica de Conteúdo com IA. Siga a seção "Primeira vez nesta
máquina" da skill em .agents/skills/fabrica-de-conteudo/SKILL.md: instale o que
faltar no meu computador, rode a conferência até passar e me diga no fim o que
fez. Se algo pedir senha de administrador, me avise antes.
```

O agente descobre o seu sistema (Mac, Windows ou Linux) e instala o que falta.
Leva uns 10 minutos. Se a conferência acusar um defeito do pacote, ele para e
mostra a mensagem exata; mande essa mensagem para o suporte.

## Qual agente

Qualquer agente de IA que rode comandos no seu computador e leia skills. As
skills moram em `.agents/skills/`, a pasta do padrão aberto de skills, que o Codex
lê; o Claude Code acha a cópia delas em `.claude/skills/`. As instruções da pasta
estão no `AGENTS.md`, e o `CLAUDE.md` e o `GEMINI.md` apontam para ele.

Testado em 01/10/2026 num Mac, com o Claude Code e com o Codex: os dois acharam
as skills, rodaram a conferência inteira e pararam nos passos que cobram. O
Claude Code pede o Claude Pro ou acima; o Codex, no terminal, o ChatGPT Plus ou
acima. Outro agente que leia `.agents/skills/` deve achar o pacote do mesmo
jeito, mas não foi testado.

O modelo de transcrição (~3 GB) só baixa no primeiro vídeo, não agora.

## As chaves

Toda chave mora num arquivo só: o `.env.local`, na raiz da pasta. Ele é seu e
não vai para ninguém. O `.env.local.exemplo` diz o que preencher.

## O look e a placa da HeyGen

O reel editorial e o reel com avatar usam o seu avatar da HeyGen. Dois dados dele a
fábrica não descobre sozinha.

**O ID do look** (`HEYGEN_LOOK`, opcional). O look é cada versão do seu avatar: roupa,
lugar, enquadramento. Gerando pelo site, você escolhe o look lá e deixa a linha vazia.
Para preencher, crie uma chave em app.heygen.com/developers/api, ponha em
`HEYGEN_API_KEY` no `.env.local` e peça o ID ao agente. Ele lista os seus looks, sem
gerar vídeo:

```bash
set -a; . ./.env.local; set +a
curl -s "https://api.heygen.com/v3/avatars/looks?ownership=private" -H "X-Api-Key: $HEYGEN_API_KEY"
```

Cada look vem com `name`, `id` e `preview_image_url`. O `id` é o `HEYGEN_LOOK`. Não
confunda com o `group_id`, que é o avatar inteiro: a geração pede o do look.

**A placa** (`imagem.fundo`, no plano do reel editorial). É o lugar atrás de você, sem
você: a fábrica põe o rosto recortado (o webm sem fundo) em cima dela. A HeyGen não
entrega a placa pronta. A única imagem do look que a API dá é a `preview_image_url`, com
você na frente. Faça a placa de um destes jeitos:

1. Grave uns segundos do cenário vazio, com a mesma câmera, no mesmo lugar e no mesmo
   enquadramento do vídeo que treinou o avatar, e tire um quadro.
2. Pegue a imagem do look (a `preview_image_url`) e apague você dela num editor de
   imagem com IA.

A placa tem o tamanho do vídeo que a HeyGen gera (1080×1920 no vertical). A fábrica a
põe na mesma escala e na mesma posição do rosto, e é assim que a cadeira e o microfone
caem no lugar. Placa que não cobre o quadro, ela recusa.

## O que cobra, e onde

A transcrição, o corte, as peças, a legenda e a mixagem rodam na sua máquina,
de graça. Pagam-se as ferramentas abaixo, e a fábrica nunca gasta sozinha: quando
chega num passo pago, ela para, mostra o comando e espera você.

| Passo | Serviço | Como cobra | Chave |
|---|---|---|---|
| Narração (reel editorial e criativo) | ElevenLabs | por caractere; no máximo 3 gerações por vídeo | `ELEVENLABS_API_KEY` no `.env.local` e, no reel editorial, `VOZ_ID` |
| Clonar a sua voz | ElevenLabs | o clone profissional pede o plano Creator | — |
| Trilha (opcional) | ElevenLabs Music | uso comercial só no plano pago. Sem a sua, a fábrica usa uma das três faixas CC0 de `exemplos/trilhas/`, de graça | — |
| Rosto (avatar) | HeyGen, no site | créditos por minuto gerado; para o rosto sair sem fundo, o avatar tem que ser treinado com fundo removível | `HEYGEN_LOOK` e `HEYGEN_API_KEY`, opcionais (acima) |
| Cenas do criativo | Higgsfield, pela API | uns US$ 0,34 por cena, de uma carteira em dólar separada do plano (recarga mínima de US$ 5); o pacote não traz cenas | `HIGGSFIELD_KEY_ID` e `HIGGSFIELD_KEY_SECRET` no `.env.local` |
| Conferir a voz de ouvido (opcional) | OpenRouter | centavos; sem chave, o passo avisa e segue | `OPENROUTER_API_KEY` no `.env.local` |

## Depois

Com a conferência passando, é pedir:

```
faz um reel editorial sobre <assunto>, com a minha voz
```

```
corta o vídeo que eu gravei no celular em ~/Downloads/gravacao.mp4 e põe legenda
```

O agente escreve o plano, confere sem renderizar e mostra o que vai custar antes
de qualquer passo pago. O `GUIA-DE-PEDIDOS.md` tem um pedido pronto para cada tipo
de vídeo, técnica e etapa.
