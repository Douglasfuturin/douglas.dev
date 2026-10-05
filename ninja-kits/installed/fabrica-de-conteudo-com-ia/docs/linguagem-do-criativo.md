# A linguagem do criativo

O criativo é voz em off sobre cenas geradas, cada cena cobrindo o trecho da fala que ilustra.
Este guia diz o que a cena precisa ter para parar o dedo e como sair um banco de cenas seu. Vem
da mecânica de atenção dos vídeos que viralizam: a forma, nunca o roteiro de ninguém.

Quem rola o feed está no automático. O cérebro prevê o próximo vídeo e só para quando a previsão
falha. Tudo abaixo serve a isso: quebrar a previsão, abrir uma pergunta e puxar a pessoa de
pergunta em pergunta. Retenção é o que a plataforma usa para distribuir.

## O primeiro quadro (1,5 s)

- **Abra pelo conceito e pela imagem mais forte.** Nada de logo, apresentação ou cena comum que só
  fica estranha depois.
- **Reconhecível primeiro, dúvida depois.** O que a pessoa reconhece na hora prende; o elemento
  que não se explica, logo em seguida, cria o conflito que faz pausar, voltar e comentar.
- **O impossível filmado como real.** Um elemento absurdo num registro de coisa verdadeira:
  câmera de segurança, telejornal, documentário, vídeo de celular, fita antiga. Ninguém na cena
  estranha o absurdo, e a narração segue séria.

## Estranheza com função

Bizarrice solta, o cérebro classifica e descarta. O estranho tem que deixar a ideia mais funda,
mais engraçada ou mais lembrada; se não deixa, sai.

- **Contraste:** juntar o que não é do mesmo mundo (luxo e decadência, escritório e selva).
- **Contradição:** sentidos opostos no mesmo quadro. A pessoa não conclui rápido e fica.
- **Estranheza controlada:** o quase real com uma coisa errada. O cérebro tenta decidir se aquilo
  existe.
- **Símbolo emprestado:** o que já está no imaginário de todo mundo explica sem explicação.

## O laço: segurar até o fim

- **Cada cena abre uma pergunta** que o cérebro não responde na hora; a seguinte responde em parte
  e abre outra, até o fecho. Não é esconder informação, é ordenar a história. Os dois furos que
  mais aparecem: revelar o segredo na primeira frase, e a lista (quatro tarefas seguidas não abrem
  pergunta nenhuma).
- **Imagem nova a cada 2,5 a 3 s**, trocando de registro, de escala e de lugar.
- **Toda imagem funciona parada.** Cada quadro vale como print; é o que faz alguém mandar.
- **A palavra forte vira a imagem.** Dá para entender sem som.

## Choque cômico e prova literal (os cinco primeiros segundos)

Cena normal demais não assusta ninguém, e metáfora demais obriga a pessoa a decodificar e ela
nunca vê o produto. A saída tem duas partes, nesta ordem:

1. **Choque (0 a 1,5 s):** susto de surpresa, e cômico. O impossível acontecendo com algo que a
   pessoa reconhece. Nunca violência, medo, nojo ou sofrimento: a Meta barra anúncio chocante ou
   sensacionalista, e conta de anúncio cai por isso.
2. **Prova literal (até 5 s):** a tela real do seu produto fazendo o que você promete, com o verbo
   dito na voz. Captura de verdade, nunca tela montada. Filme a tela com o celular, ponha o vídeo
   na pasta do banco e escreva a ficha à mão, com o acabamento `celular`.

Depois vêm a sua marca (o personagem, o universo que se repete) e o fecho, com a chamada. A piada
fica a serviço do produto: cada absurdo ilustra uma tarefa que o seu público reconhece.

## Os acabamentos

A cena gerada sai limpa demais. O acabamento põe o que o aparelho põe na imagem, igual em todo o
banco, e é o que costura cenas de modelos diferentes. Mora na ficha da cena (`acabamento` no
`cenas.json`), e o trecho do plano pode trocar.

| Acabamento | O que põe | Serve para |
|---|---|---|
| `cctv` | câmera parada, cor lavada, vinheta, `CAM 02` e o relógio | o flagra, a câmera escondida, a madrugada |
| `telejornal` | imagem limpa, selo `AO VIVO` e `PLANTÃO`, relógio | o plantão: a rotina vira notícia; o repórter na rua |
| `documentario` | teleobjetiva que treme pouco, nada escrito | o documentário de natureza: o seu público no habitat dele |
| `celular` | tremor de mão, `REC` piscando, relógio | o vídeo de rua, o flagra de alguém, a prova |
| `filmadora` | cor deslocada nas bordas, data no canto | o arquivo antigo, o comercial de TV velho |

- O texto do aparelho entra aqui, nunca no prompt: o modelo embaralha letra.
- `hora` e `cam` vão na ficha ou no trecho. Câmera escondida numera as câmeras, e o espectador
  olha o rótulo. Cenas seguidas no mesmo telejornal não podem pular de 03:37 para 12:18.
- `data` (AAAA-MM-DD) também: é a que a filmadora escreve no canto. Sem ela, sai a do dia do
  render. O arquivo antigo pede data antiga.
- `cor` no plano (`neutra` ou `technicolor`) vale para todo o vídeo. O modelo não entrega cor
  saturada pelo prompt: ela entra aqui.

## Regras do banco

1. **3 a 4 s gerados por cena**, sem fala, assunto legível em meio segundo. Sobra para cortar em
   2,5 a 3 s.
2. **Nada de texto no prompt.** Placa, quadro, tela ou papel com conteúdo vira letra embaralhada.
   Rótulo, tarja e cartela entram na pós.
3. **A piada que se lê num relance funciona:** o elemento grande, visível, fazendo o impossível
   no meio de gente normal. A que depende de detalhe (um pé no canto, a cadeira girando) some, e
   sobra uma sala vazia.
4. **Muita gente pequena fazendo a mesma coisa não sai.** Ação sincronizada, só com um ou dois
   personagens grandes no quadro.
5. **Registro que tira a cor apaga a sua marca.** O infravermelho é bom de registro e some com a
   cor. Use pouco.
6. **Cada cena guarda o seu melhor trecho.** A ação costuma vir no fim da geração: assista e
   escreva a `janela` (de, até) na ficha. Cortar sempre do começo perde o momento.
7. **Trecho de fala maior que uns 5 s pede duas cenas.** A cena desacelera para cobrir a fala, e
   acima de ~1,25x a câmera lenta aparece.
8. **Proibido:** renda, faturamento, dinheiro ou notificação de venda na tela; corpo deformado;
   pessoa real ou rosto famoso (fora o seu); logo de terceiro, nem de app; política ou religião;
   música conhecida.

## A estética: a sua pele

Com IA, bonito virou padrão, e o feed ignora o genérico. O que fica é a pele que se repete
(paleta, textura, luz) e faz a pessoa reconhecer você antes de ler o nome.

1. **Emoção primeiro:** que sentimento o vídeo deixa ("nostálgico e sujo", "limpo e frio"). Só
   depois a técnica.
2. **Garimpo no Pinterest, em inglês, por autor e obra, nunca por adjetivo.** "Bonito" devolve
   lixo; o nome de um fotógrafo devolve centenas de imagens com a mesma alma. Olhe textura, cor,
   luz e composição, não o personagem. Os três eixos:
   - *textura:* VHS, found footage, Super 8, 16mm grain, halation, light leaks, CRT scanlines;
   - *paleta:* teal and orange, bleach bypass, muted tones, desaturated, technicolor, sepia;
   - *luz:* chiaroscuro, Rembrandt, neon, volumetric, low key, backlit silhouette, golden hour.
3. **Board de 20 a 30 imagens.** O padrão que volta é a identidade; feche com o nome do look em
   três palavras. Nunca copie uma imagem: roube o padrão de trinta.
4. **O código da estética:** o que as imagens têm em comum vira uma entrada do `estetica.json`, com
   um `prompt` em inglês. O lote acrescenta esse prompt no fim de cada cena, e o prompt da cena
   fica só com a cena, a câmera e a composição. O que varia de cena para cena é a câmera e a
   composição, não a estética.
5. **Valide antes de adotar:** gere duas ou três cenas de teste e só fixe o código se elas têm
   personalidade.

Luz escura esconde a piada: peça luz que deixa ler a ação, e escuro só em cena de noite.

## Onde buscar referência

Dois bancos abertos, que se olham sem conta. Deles sai a técnica com o nome certo; o vídeo de
quem fez fica lá.

- **Câmera, luz e lente:** https://melies.co/cinematic-techniques. Centenas de técnicas
  (movimento, ângulo, lente, luz, cor, composição, corte), cada uma com um exemplo curto, quando
  usar, o erro comum e uma linha de prompt, o "Prompt it". Tudo em inglês. O Melies é um gerador
  pago; ler o banco é de graça.
- **Motion feito por agente:** https://skillry.dev/ai-videos/opus-5-5. Centenas de vídeos de
  motion graphics, explicativos e 3D que gente fez com um agente de IA e postou, cada um com o
  que o autor contou do prompt, quase sempre só uma parte. O site vende skills; a fábrica não
  precisa delas.

Do Melies para a cena:

1. Ache a técnica pelo nome e leve a linha do "Prompt it" para o prompt da cena no lote. Luz e
   cor que se repetem no banco inteiro vão para a estética, não para a cena.
2. Limpe a linha antes: troque `[Subject]` pelo assunto da cena e tire nome de filme, diretor,
   ator ou personagem (a do ângulo baixo traz "Citizen Kane"). Nome assim puxa rosto famoso.
3. Um movimento por cena. Já saíram bem no Kling: câmera parada, câmera na mão, teleobjetiva
   com algo desfocado na frente, close e voo de helicóptero em volta. Movimento que pede
   precisão, como o dolly zoom, pode não sair: gere uma cena só antes do lote
   (`lote.py <lote> --gera --so <id>`).

Do Skillry para o reel: abra um vídeo, leia o que o autor contou e anote a mecânica (de quanto
em quanto tempo entra uma ideia, o que vira peça, como o texto se mexe). Peça essa mecânica com
as peças da biblioteca. A cor, a letra e o movimento continuam os do seu estilo.

## Antes de gerar: o cartão de conceito

Cada vídeo, e cada cena forte dele, cabe num cartão:

- **E se…?** a premissa numa frase;
- **o quadro-chave:** um quadro só, descrito: lugar, luz, quem está e o elemento estranho;
- **a regra usada:** contraste, contradição ou símbolo;
- **a mensagem numa linha**, que é o que a pessoa leva.

Passa no filtro de três perguntas: tem carga visual? deixa uma pergunta aberta? tem mensagem?
Falhou uma, é meme: dá view e não constrói marca. Cena sem cartão sai do lote, porque é gasto sem
função.

## Você dentro da cena

A cena `wan` (Wan 3.0 Prime, referência→vídeo) põe o rosto das suas fotos na cena gerada.

- **Duas fotos:** uma de frente e uma neutra, com fundo liso. O modelo copia o fundo: um quadro na
  parede atrás de você vira objeto na cena. Tire o fundo antes.
- **No prompt, um bloco fixo:** que a pessoa é a mesma das imagens ("the SAME person as in both
  reference images (Image 1 and Image 2): same face…"), os traços que o modelo erra (cabelo,
  barba, óculos sem reflexo) e "use the reference images ONLY for the face; do not copy anything
  from their backgrounds". Mais um **figurino fixo**, para você ser reconhecido de relance; o
  figurino fora de lugar (de casaco na praia) vira a piada.
- **Nunca parado:** peça movimento do primeiro ao último quadro (andando, olhando em volta). Parado,
  sai estátua. O olhar para a lente, só no fim.
- Você não fala na cena: a voz é a do locutor.
- Sai em 480p; o acabamento costura com as cenas do `kling`. Confira cada uma antes de usar.

## Do lote ao criativo

1. O cartão de conceito vira o lote: `lote.json` na pasta do banco, com a estética e, em cada
   cena, o prompt e a ficha (`acabamento`, `hora`, `cam`). Formato no topo de
   `tools/video-use/helpers/lote.py`; exemplo em `exemplos/criativo/`.
2. O plano do criativo aponta o banco e o lote. O `--seco` da fábrica mostra o passo `$ cenas`,
   com a estimativa, e o comando. `lote.py <lote>` pergunta o preço à API; com `--gera`, gera e
   baixa, e cada cena entra no `cenas.json`.
3. Assista cada cena e acerte a `janela` na ficha. Cena ruim: mova o arquivo para `descartadas/`,
   dê outro id a ela no lote (`escritorio-3h-b`) e rode de novo, que só gera o que falta. O mesmo
   id não serve: o acabamento fica guardado pelo nome, e a cena velha voltaria.
4. A voz, a montagem, a legenda e a trilha são da fábrica.
