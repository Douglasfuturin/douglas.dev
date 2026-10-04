# Grokish — multi-agente com funcionalidades do Grok Bot

Starter em Next.js + Vercel AI SDK + xAI Grok para um sistema multi-agente com as mesmas capabilities do Grok Bot:

- chat agentic com tools server-side
- research multi-agente paralelo (`grok-4.20-multi-agent`)
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
| `auto` | roteador + um dos acima | decide pelo conteúdo da mensagem |

```
Usuário → /api/chat → orchestrator (auto|chat|research)
                         ├─ chat: grok-4.7 + web/X/code/image tools
                         └─ research: grok-4.20-multi-agent + web/X
```

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

## Editor de vídeo (kit integrado)

O modo **Editor de vídeo** usa o kit em `kit-edicao-video/`:

1. Uma vez: `cd kit-edicao-video/skill && uv sync`
2. Na UI: escolha o modo **Editor de vídeo**, faça upload do MP4 e ajuste opções
3. Peça: `Edita automaticamente este vídeo…`

### Opções na UI

- Estilos: `aula-ccnp`, `reel-mono`, `reel-camera`, `quadro`, `vsl`, etc.
- Resolução, idioma, modelo Whisper
- Legendas, intro/outro, crop 9:16, `pause_keep`, `sil_cut`
- Auto-confirmar plano + render automático

### Tools do agente

`list_video_styles`, `describe_video_style`, `transcribe_video`, `create_edit_plan`, `dry_run_edit`, `render_edit`, `burn_captions`, `measure_breathing`, `auto_edit_video`

Pipeline automático: **transcreve → plano → dry-run → render**.

## Próximos passos

- Persistência de sessão (DB / Redis)
- Memória de longo prazo por usuário
- Canal Slack / Discord
- Evals para qualidade das respostas research
- Deploy na Vercel com `XAI_API_KEY` nas env vars
- Fila de jobs para renders longos
