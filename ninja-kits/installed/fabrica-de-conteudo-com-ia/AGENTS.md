# Fábrica de Conteúdo com IA

Esta pasta é a Fábrica de Conteúdo com IA: reels, criativos de anúncio e capas, feitos
a partir de um plano. Rode tudo da raiz desta pasta.

- Antes de qualquer vídeo, leia a skill `fabrica-de-conteudo`, em
  `.agents/skills/fabrica-de-conteudo/SKILL.md`. Se não existe o arquivo `.fabrica-ok`
  na raiz, comece pela seção "Primeira vez nesta máquina" dela.
- Todo vídeo sai pela cadeia: um plano num estilo, conferido com `fabrica.py --seco` e
  renderizado pelo `fabrica.py`. Não monte vídeo nem a base dele com `ffmpeg` à mão: o que
  falta à cadeia ela recusa e diz o campo.
- O critério de edição está nas outras skills `fabrica-*`, na mesma pasta. O
  `GUIA-DE-PEDIDOS.md` tem um pedido pronto para cada tipo de vídeo.
- Nada pago roda sozinho: voz, avatar e cena param no passo que cobra e esperam o sim
  do usuário.
- Se existe a pasta `marca/` na raiz, ela é a marca do usuário e vale em todo vídeo:
  antes de escrever roteiro, leia `marca/MARCA.md` (quem ele é, o que vende, o tom, o
  que nunca falar); use os estilos dela (`marca/estilos.json`, que o `estilo.py` lista
  junto com os do kit) e os pedidos prontos de `marca/PEDIDOS.md`. Para instalar ou
  conferir uma marca, siga `marca/INSTALAR-MARCA.md`.
- Para criar a marca do usuário a partir de um estilo, das cores e da letra (o pedido do
  `docs/guia-de-estilos.md`), siga a seção "A marca feita aqui" da skill `fabrica-estilo`.
