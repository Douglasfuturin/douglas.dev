# Guia de pedidos

Abra o seu agente de IA dentro da pasta `fabrica-de-conteudo`, copie o pedido e troque o que
está entre `< >`. O agente escreve o plano, confere sem renderizar (o `--seco`), mostra o que
vai custar e só gasta depois do seu sim. O critério que ele segue está nas skills de edição,
em `.agents/skills/`.

## Para começar

```
Esta pasta é a Fábrica de Conteúdo com IA. Siga a seção "Primeira vez nesta
máquina" da skill em .agents/skills/fabrica-de-conteudo/SKILL.md: instale o que
faltar no meu computador, rode a conferência até passar e me diga no fim o que
fez. Se algo pedir senha de administrador, me avise antes.
```

Sai: o computador pronto e o arquivo `.fabrica-ok` na pasta. Mais no `INSTALAR.md`.

```
confere os dois exemplos sem gastar nada
```

Sai: a cadeia do reel editorial e a do criativo (`exemplos/`), paradas no passo que cobra.

## Os cinco tipos de vídeo

### Reel editorial

```
faz um reel editorial de 30 segundos sobre <assunto>, com o meu avatar e a minha voz clonada. A palavra da chamada é <PALAVRA>
```

Sai: `videos/topo/<slug>.mp4`, 1080×1920. Painel em cima, o seu rosto num cartão embaixo,
a fala em duas letras, peças entrando com a fala e trilha. Precisa da voz clonada na
ElevenLabs, de um avatar seu na HeyGen treinado com fundo removível, da placa do seu look
(o fundo atrás do rosto) e de uma trilha. Cobra: a narração (ElevenLabs) e o rosto (HeyGen,
gerado por você no site).

### Reel do vídeo que você já gerou

```
na pasta videos/<pasta> tem a minha voz e o vídeo do meu avatar que eu gerei na HeyGen. Edita esse vídeo pra reel: corta as pausas, põe legenda, arruma a tela e faz a capa
```

Sai: `videos/topo/<slug>.mp4` e a capa ao lado, 1080×1920. O mesmo molde do reel editorial,
com o rosto que você já tem: a fala em duas letras, o fundo atrás de você trocando com o que
a voz diz (as cenas do seu banco de cenas, em `videos/banco-de-cenas/`), o gancho no
primeiro quadro, a chamada no fim e trilha. Serve também o vídeo do celular exportado sem
fundo (webm). Não cobra nada: roda no seu computador.

### Reel com avatar, na voz que você gravou

```
transforma o áudio que eu gravei em <caminho> num reel com o meu avatar, legenda e b-roll
```

Sai: `videos/reels/<slug>.mp4`, com a legenda viral e a trilha. Antes da HeyGen, o áudio
passa pelo portão: as pausas saem, o nível é medido, e nada gera sem você ouvir e aprovar.
Cobra: o rosto (HeyGen).

### Reel do celular

```
corta o vídeo que eu gravei no celular em <caminho> e põe legenda
```

Sai: `videos/reels/<slug>.mp4`, com o silêncio cortado, a legenda viral queimada e, se você
mandar, b-roll por cima. Não leva trilha. Não cobra nada: roda no seu computador.

### Criativo de cinema

```
faz um criativo de câmera escondida sobre <produto>, com cenas geradas na Higgsfield e narração na ElevenLabs
```

Sai: `videos/criativos/<slug>.mp4`. Voz em off sobre cenas do banco de cenas, cada cena no
trecho da fala que ilustra, com o acabamento de filmagem achada: `cctv`, `telejornal`,
`documentario`, `filmadora` ou `celular`. Para o feed, peça "a versão pro Reels". Antes de
gerar, o agente escreve com você o cartão de conceito. Cobra: as cenas (Higgsfield, uns
US$ 0,34 cada, com o preço perguntado antes) e a narração (ElevenLabs).

## As oito técnicas

### Do bruto ao pronto

```
corta o silêncio do vídeo <caminho> e tira as frases que eu errei ou repeti
```

Sai: o vídeo só com a fala. O silêncio sai sozinho; erro e repetição o agente acha no
transcript e tira como drop. No reel com avatar, a voz chega aparada antes de gerar o rosto.

### Motion explicativo

```
quando eu falar <a ideia ou o número>, mostra na tela com uma peça: contador, lista ou passos
```

Sai: uma peça da biblioteca (`tools/v2`) entrando no tempo da fala. No reel editorial.

### Recorte de fundo

```
de <início> a <fim>, tira o fundo de trás de mim e põe <xadrez | o painel | esta imagem: caminho>
```

Sai: o seu rosto recortado sobre outra coisa, só naquele trecho. Pede o avatar gerado com
fundo removível. No reel editorial.

```
põe a palavra <PALAVRA> grande, passando atrás de mim
```

Sai: a palavra-herói atrás de você, recortada no seu computador. Só no reel do celular, que
não troca de fundo.

### Inserção de imagens

```
mostra o print de <endereço da página> quando eu falar <frase>, e o logo da <ferramenta> no começo
```

Sai: a captura da página com grifo e o logo, no instante da frase. Só página pública, sem
login. No reel editorial. No reel do celular, um vídeo seu entra por cima como b-roll: `põe
<vídeo> por cima quando eu falar <frase>`.

### Ícones animados

```
põe um ícone animado em cada ideia do roteiro
```

Sai: sticker, contador, rabisco (seta, x, círculo), carimbo ou passos que viram ✓, entrando
quando a palavra é dita. No reel editorial.

### Legenda

```
põe a legenda de duas letras, uma palavra por vez
```

Sai: a fala em sans, uma ou duas palavras por vez, e o rótulo em serifa itálica. É a
legenda do reel editorial.

```
põe legenda com a palavra <PALAVRA> em destaque
```

Sai: a legenda viral, até quatro palavras por card, quebrada na pausa da fala, com a palavra
acesa. No reel do celular, no reel com avatar e no criativo.

### Cenas geradas por IA

```
gera <n> cenas de <câmera de segurança | plantão | documentário> pro criativo sobre <produto>
```

Sai: o lote. Primeiro o preço, perguntado à API sem gastar; com o seu sim, as cenas baixam
no banco, cada uma com a ficha. Você assiste cada cena e acerta o melhor trecho (a janela).
Cobra na Higgsfield.

### Seu avatar, sua voz

```
grava esse roteiro com o meu avatar e a minha voz clonada: <roteiro>
```

Sai: a narração na sua voz clonada e o áudio pronto para subir na HeyGen. Quando o vídeo do
rosto volta, a montagem segue sozinha. Cobra: a narração (ElevenLabs) e o rosto (HeyGen).

## Etapa por etapa

### Roteiro

```
escreve o roteiro de um reel editorial de 30 segundos sobre <assunto>, com gancho no primeiro quadro e a chamada "comenta <PALAVRA>" só no fim
```

Sai: a `narracao` do plano, escrita como se fala: sem sigla, sem marca de emoção, e só a
palavra da chamada em caixa alta. Não cobra.

```
escreve o cartão de conceito e os trechos de um criativo sobre <produto>
```

Sai: o cartão (a premissa, o quadro-chave, a regra, a mensagem) e os `trechos` do plano,
cada fala com a cena que a cobre. Não cobra.

### Voz

```
gera a narração do reel
```

Sai: `voz.wav` na pasta do vídeo, na sua voz clonada. Cobra na ElevenLabs, por caractere, no
máximo três gerações por vídeo. Clonar a voz você faz uma vez, no site da ElevenLabs.

```
confere o áudio que eu gravei em <caminho> antes de mandar pra HeyGen
```

Sai: o áudio aparado e medido pelo portão, que só libera depois que você ouvir. A conferência
de ouvido por IA é opcional e custa centavos (OpenRouter).

### Rosto

```
prepara o áudio do avatar
```

Sai: `avatar/geracao.wav`. Você sobe esse áudio na HeyGen, gera com fundo removível e salva o
vídeo em `avatar/rosto.webm`. Depois, peça `continua o reel`. Cobra na HeyGen, por minuto
gerado.

```
acha o ID do meu look na HeyGen e põe no .env.local
```

Sai: os seus looks, pelo nome, e o `HEYGEN_LOOK` preenchido com o que você escolher. Precisa
da `HEYGEN_API_KEY` no `.env.local`. Não gera vídeo. A placa do look (o fundo atrás do
rosto) a HeyGen não entrega: o jeito de fazer está no `INSTALAR.md`.

### Montagem

```
confere o plano sem renderizar
```

Sai: a cadeia de comandos e o que cada passo cobra. Nada roda.

```
pode renderizar
```

Sai: o final na pasta do estilo. No reel editorial, também uma folha de quadros
(`folha-1fps.png`) para conferir sem assistir.

```
refaz só a partir do desenho
```

Sai: o render de novo, sem refazer o que já está em disco. As etapas: corte, render,
desenho, composicao, trilha, entrega.

### Capa

```
faz a capa do reel com a minha foto <caminho>, título "<linha 1>|<linha 2>" e "<trecho>" em destaque
```

Sai: `videos/topo/<slug>/capa-nick.jpg`, 1080×1920, ao lado do reel editorial, com a sua foto
sem fundo, o título, o logo e dois ícones. Não cobra.

```
faz só uma capa, sem vídeo, com a minha foto <caminho>: título "<linha 1>|<linha 2>", "<trecho>" em destaque, "<ferramenta>" no topo e os ícones <mic> e <onda> nos lados. Usa a função capa_nick do tools/video-use/helpers/capa.py e salva em <pasta>/capa.jpg
```

Sai: `<pasta>/capa.jpg`, o mesmo JPEG de 1080×1920, para um vídeo que você editou fora da
fábrica. Os ícones: `mic`, `onda`, `claquete`, `filme`, `robo`, `rec` ou `cel`. Não cobra.

### Versão do YouTube

```
faz a versão do YouTube, com a chamada "o link tá na descrição"
```

Sai: `videos/topo/<slug>-yt.mp4`. O mesmo reel, com a última frase trocada e um cartão com
seta para baixo no lugar do "comenta". A frase nova cobra na ElevenLabs. Só no reel
editorial.

### Ajuste

```
no segundo <t>, <o que está errado>. Ajusta e refaz só o que mudou
```

Sai: o plano corrigido e o render refeito a partir da etapa que mudou.

## O que cobra

A transcrição, o corte, as peças, a legenda, a capa e a mixagem rodam no seu computador, de
graça. Cobram a narração (ElevenLabs), o rosto (HeyGen), as cenas (Higgsfield) e, se você
quiser, a conferência de ouvido (OpenRouter). Em todo passo pago a fábrica para, mostra o
comando e espera. A tabela inteira está no `INSTALAR.md`.
