---
name: hyperframes
description: >
  Ponto de entrada HyperFrames (HeyGen) para criar, editar, animar e renderizar
  vídeo/motion a partir de HTML — promo, explainer, legendas, slideshow, port
  Remotion, ou composição HyperFrames. Use quando o usuário pedir vídeo com
  HyperFrames, motion graphics HTML, preview/render hyperframes, ou workflows
  como product launch, talking head, music-to-video e website-to-video.
---

# HyperFrames — Skill Ninja

Kit oficial HeyGen HyperFrames integrado ao hub Grokish. Renderiza vídeo a partir de **composições HTML** com timing `data-*`, animações seekable e CLI (`npx hyperframes`).

## Como operar neste hub

1. Leia primeiro `skills/hyperframes/SKILL.md` (router oficial).
2. Depois carregue a subskill do domínio (core, animation, creative, cli, etc.).
3. Para projeto novo: oriente `npx hyperframes init` (ou scaffold local) e peça brief do vídeo.
4. Entregue composição HTML válida + passos de `lint` / `preview` / `render`.
5. Responda em **português**, mantenha nomes técnicos do framework em inglês quando forem comandos/APIs.

## Mapa de subskills

| Necessidade | Pasta |
| --- | --- |
| Entrada / roteamento | `skills/hyperframes/` |
| Contrato HTML / clips / tracks | `skills/hyperframes-core/` |
| Animação e transições | `skills/hyperframes-animation/` |
| Keyframes / GSAP seek-safe | `skills/hyperframes-keyframes/` |
| Design, paleta, narração | `skills/hyperframes-creative/` |
| Áudio / VO / mix | `skills/hyperframes-audio/` |
| CLI init/lint/preview/render | `skills/hyperframes-cli/` |
| Studio / projeto existente | `skills/hyperframes-studio/` |
| Registry de blocos | `skills/hyperframes-registry/` |
| Mídia (TTS, captions, assets) | `skills/media-use/` |
| Vídeo geral | `skills/general-video/` |
| Motion graphics | `skills/motion-graphics/` |
| Slideshow | `skills/slideshow/` |
| Product launch | `skills/product-launch-video/` |
| Talking head | `skills/talking-head-recut/` |
| Music → vídeo | `skills/music-to-video/` |
| PR → vídeo | `skills/pr-to-video/` |
| Remotion → HyperFrames | `skills/remotion-to-hyperframes/` |
| Faceless explainer | `skills/faceless-explainer/` |
| Legendas embutidas | `skills/embedded-captions/` |
| Figma | `skills/figma/` |

## Pedido típico

- Tema / objetivo do vídeo
- Duração alvo
- Formato (16:9, 9:16, 1:1)
- Tom visual e CTA
- Se há footage, URL, Figma ou só brief

Em seguida siga o workflow em `skills/hyperframes/` e produza a composição.
