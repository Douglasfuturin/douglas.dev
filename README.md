# Grokish — multi-agente com funcionalidades do Grok Bot

Starter em Next.js + Vercel AI SDK + xAI Grok para um sistema multi-agente com as mesmas capabilities do Grok Bot:

- chat agentic com tools server-side
- research multi-agente paralelo (`grok-4.20-multi-agent`)
- GitHub Scout — busca e ranqueia os melhores repositórios open-source
- Roteirista — roteiro de Reels ~60s sobre um repositório
- Notion Guide — página/arquivo com link + instalação + uso
- Pipeline — Scout → Roteiro → Notion numa tacada
- Radar de Tendências — briefing diário (IA, automação, marketing) com aprovação → Roteirista
- web search, X search, code execution, image generation

## Arquitetura (duas camadas)

### 1) Multi-agente nativo da xAI (recomendado para research)

Use o modelo `grok-4.20-multi-agent` via Responses API. A xAI sobe vários agentes em paralelo. Em `providerOptions.xai.reasoningEffort`, `low` / `medium` / `high` controlam a **quantidade de agentes**.

Tools típicas: `web_search`, `x_search`.

### 2) Orquestrador próprio + Grok agentic (`grok-4.7`)

Um roteador escolhe o modo:

| Modo | Modelo | Quando usar |
| --- | --- | --- |
| `chat` | `grok-4.7` | conversa, código, imagens, fatos rápidos |
| `research` | `grok-4.20-multi-agent` | investigação profunda com fontes |
| `github` | `grok-4.7` | melhores repos GitHub, libs open-source, comparação |
| `roteiro` | `grok-4.7` | roteiro de Reels ~60s sobre um repo |
| `notion` | `grok-4.7` | guia no Notion (link + instalar + usar) |
| `pipeline` | `grok-4.7` | pack completo Scout → Reels → Notion |
| `radar` | `grok-4.7` | briefing diário IA / automação / marketing |
| `kits` | `grok-4.7` | skills Ninja / ZIPs instalados |
| `video` | `grok-4.7` | edição automática de vídeo |
| `auto` | roteador + um dos acima | decide pelo conteúdo da mensagem |

```
Usuário → /api/chat → orchestrator (...|pipeline|radar|kits|video)
                         ├─ radar: briefing diário → aprovar → Roteirista
                         ├─ pipeline: Scout → Roteiro → Notion
                         ├─ github / roteiro / notion
                         ├─ kits / video
                         └─ research: grok-4.20-multi-agent + web/X
```

## GitHub Scout

Modo dedicado (UI: **GitHub Scout**, atalho `/github` ou `/?mode=github`) que usa a Search API do GitHub:

- `search_best_github_repos` — busca + score (stars, forks, atividade, licença)
- `get_github_repo` — detalhe + preview do README
- `compare_github_repos` — comparativo lado a lado

Opcional: defina `GITHUB_TOKEN` (ou `GH_TOKEN` / `GITHUB_PAT`) em `.env.local` para limites de rate maiores.

## Roteirista (Reels 60s)

Atalho `/roteiro` ou `/?mode=roteiro`:

- `prepare_repo_for_reels` — fatos do repo + guia de timing
- `deliver_reels_script` — roteiro estruturado (hook → CTA) com fala, texto de tela e visual

## Notion Guide

Atalho `/notion` ou `/?mode=notion`:

- `publish_repo_guide_to_notion` — cria página Notion + arquivo `.md` local (e tenta anexar o arquivo)
- `export_repo_guide_markdown` — só gera/salva o markdown em `outputs/repo-guides/`

Configure no `.env.local`:

```bash
NOTION_TOKEN=ntn_...
NOTION_PARENT_PAGE_ID=...   # página pai compartilhada com a integração
```

## Pipeline (Scout → Reels → Notion)

Atalho `/pipeline` ou `/?mode=pipeline`:

- `run_repo_content_pack` — escolhe o melhor repo, gera roteiro 60s e publica/exporta o guia
- Salva o pack em `outputs/packs/`

Exemplo: “Pacote completo sobre agentes de IA em TypeScript”.

## Radar de Tendências

Atalho `/radar` ou `/?mode=radar`:

1. O agente pesquisa (web + X) notícias de **automação**, **IA** e **marketing**
2. Entrega briefing ranqueado via `deliver_daily_radar_briefing` (salva em `outputs/radar/`)
3. Você **aprova** um card → handoff automático para o **Roteirista** (`prepare_trend_for_reels`)

Exemplo: “Monta o briefing diário de automação, IA e marketing”.

## Como rodar

```bash
cp .env.example .env.local
# cole sua XAI_API_KEY de https://console.x.ai

npm install
npm run dev
```

Abra [http://localhost:3000](http://localhost:3000).

## Estrutura

```
src/
  app/api/chat/route.ts     # endpoint streaming
  components/chat-app.tsx   # UI
  lib/agents/
    models.ts               # chat + multi-agent models
    tools.ts                # tools do Grok Bot
    prompts.ts              # persona + router
    orchestrator.ts         # roteamento de modos
```

## Exemplo mínimo (só API)

```ts
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

const { text, sources } = await generateText({
  model: xai.responses('grok-4.20-multi-agent'),
  prompt: 'Pesquise o estado atual de MCP em agentes de IA',
  tools: {
    web_search: xai.tools.webSearch(),
    x_search: xai.tools.xSearch(),
  },
  providerOptions: {
    xai: { reasoningEffort: 'medium' }, // nº de agentes
  },
});
```

## Hub Ninja Kits

Abra [http://localhost:3000/kits](http://localhost:3000/kits) para importar cada ZIP de `F:\NINJA CURSOS`:

1. Cole os `.zip` em `ninja-kits/sources/` (ou upload na UI / anexe na conversa do Cloud Agent)
2. Clique em **Instalar todos os ZIPs**
3. Cada kit vira agente + helpers (`list_ninja_kits`, `describe_ninja_kit`, `run_ninja_kit_helper`)
4. Modo **Ninja Kits** no chat, com kit ativo selecionável

O Cloud Agent **não acessa** o disco `F:\` do Windows — os ZIPs precisam ser enviados/copiados.

## Editor de vídeo (kit integrado)

O modo **Editor de vídeo** usa o kit em `kit-edicao-video/`:

1. Uma vez: `cd kit-edicao-video/skill && uv sync`
2. Na UI: escolha o modo **Editor de vídeo**, faça upload do MP4 e ajuste opções
3. Peça: `Edita automaticamente este vídeo…`

### Editor visual em tempo real (EDVD)

Abra [http://localhost:3000/editor](http://localhost:3000/editor):

- Abas **Code** / **Visual** (como na referência)
- Preview 9:16 com legendas ao vivo
- Timeline com filmstrip, waveform e playhead
- Takes arrastáveis + atalhos (espaço, setas)
- Painel do agente: material analisado, transcript, gordura
- Comandos + automação no rodapé

### Opções na UI do chat e do editor EDVD

- **30 estilos**: aula, reel, quadro, VSL, podcast, shorts, teaser, story, webinar, entrevista, doc, feed, pitch, cold-open, tutorial, unboxing, hook-15s, live-highlight, carrossel, etc.
- **16 fontes OFL** no kit (Montserrat, Bebas, Anton, Rajdhani, Teko, …)
- **5 formatos**: 16:9, 9:16, 1:1, 4:5, 21:9
- **11 grades** de cor + **10 SFX** sintéticos + emendas `glitch` / `flash` / `whip`
- Resolução, idioma, Whisper, legendas, intro/outro, crop, `pause_keep`, `sil_cut`
- Auto-confirmar plano + render automático

### Tools do agente

`list_video_styles`, `list_edit_catalog`, `describe_video_style`, `transcribe_video`, `create_edit_plan`, `dry_run_edit`, `render_edit`, `burn_captions`, `measure_breathing`, `auto_edit_video`

Pipeline automático: **transcreve → plano → dry-run → render**.

## Próximos passos

- Persistência de sessão (DB / Redis)
- Memória de longo prazo por usuário
- Canal Slack / Discord
- Evals para qualidade das respostas research
- Deploy na Vercel com `XAI_API_KEY` nas env vars
- Fila de jobs para renders longos
