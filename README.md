# Central de Agentes — Central de Conteúdo Pessoal

SaaS pessoal (single-user) do **radar ao post**, em cima de Next.js + Vercel AI SDK + xAI Grok.

## O que é

**Central de Agentes** une todas as etapas de operações de conteúdo numa única app:

1. **Ideia / Radar** — briefing diário (IA, automação, marketing) + GitHub Scout  
2. **Aprovação** — cards → Roteirista  
3. **Roteiro** — Reels 60s, guion España, roteiro pessoal  
4. **Artes** — Twitter, realista, capas, carrossel  
5. **Vídeo** — edição automática com skills Ninja + kit EDVD / HyperFrames  
6. **Pacote** — Notion + `outputs/`  
7. **Publicação** — fila local (`/api/publish`) + hook opcional Buffer  

## Rotas do produto

| Rota | Função |
| --- | --- |
| `/` | Landing cinematográfica Central de Agentes |
| `/dashboard` | **CRM Dashboard** — visão geral + todos os módulos |
| `/central` | Kanban do pipeline (ideia → postado) |
| `/central/[id]` | Detalhe do conteúdo |
| `/studio` | Studio de agentes (chat + modos) |
| `/grupos` | Salas Conteúdo Dev / Vídeo / España |
| `/kits` | Hub de skills Ninja |
| `/editor` | Editor visual EDVD |
| `/radar` `/roteiro` `/pipeline` … | Atalhos → Studio |

UI CRM inspirada em Motionsites / Godly / 21st / React Bits / Spline: sidebar escura, accent lime, mesh gradients e motion leve.

## Como rodar

```bash
cp .env.example .env.local
# cole sua XAI_API_KEY de https://console.x.ai

npm install
npm run dev
```

Abra [http://localhost:3000](http://localhost:3000) → **Abrir Central**.

Opcional: `GITHUB_TOKEN`, `NOTION_TOKEN` + `NOTION_PARENT_PAGE_ID`, `BUFFER_ACCESS_TOKEN`.

Para edição de vídeo: `cd kit-edicao-video/skill && uv sync` (ffmpeg no PATH).

## Arquitetura

```
Usuário → /central (kanban + fila)
        → /studio?mode=central|radar|video|grupo…
             → /api/chat → orchestrator
             → tools: central + radar + roteiro + arte + vídeo + notion…
        → /api/content  (CRUD local em data/content/store.json)
        → /api/publish  (fila de posts)
```

### Modo `central`

Agente operador da Central com tools:

- `list_content_pipeline` / `get_content_item`
- `create_content_item` / `update_content_item` / `advance_content_stage`
- `run_central_pipeline` — fecha pacote editorial
- `schedule_content_publish` — enfileira Instagram/YouTube/TikTok/X/LinkedIn/Notion

### Pipeline de estágios

`idea → approved → script → art → video → packaged → ready → scheduled → published`

Dados ficam em `data/content/store.json` (uso pessoal, sem multi-tenant).

## Grupos de agentes

### Conteúdo Dev
Radar → Roteirista → Arte Twitter/Realista → Bit

### Conteúdo Dev Vídeo
Roteiro pessoal → Editor Reels → Editor vídeo (skills) → Bit → Radar GitHub

### Contenidos España
Editor → Carrusel → YouTube → Guionista → Capas → Bit

## Motor multi-agente (Grok)

| Modo | Modelo | Uso |
| --- | --- | --- |
| `central` | `grok-4.7` | SaaS ops — kanban + pacote + fila |
| `chat` / agentes | `grok-4.7` | tools server-side |
| `research` | `grok-4.20-multi-agent` | pesquisa profunda |
| `auto` | roteador | escolhe o modo |

## Hub Ninja Kits

1. Cole `.zip` em `ninja-kits/sources/`  
2. Em `/kits` → **Instalar todos os ZIPs**  
3. Use no Studio (`mode=kits`) ou via Editor de Vídeo  

## Editor de vídeo

- Skills: `auto_edit_with_system_skills`, EDVD, HyperFrames  
- UI visual: `/editor`  
- Chat: `/studio?mode=video` + upload MP4  

## Publicação

1. Avance o item até `ready` / `packaged` na Central  
2. **Fila IG / YouTube / X** ou tool `schedule_content_publish`  
3. **Marcar postado** na fila (ou configure `BUFFER_ACCESS_TOKEN` para stub de envio)  

APIs nativas Meta/YouTube/TikTok podem plugar no mesmo formato de job em `/api/publish`.

## Estrutura

```
src/
  app/
    page.tsx                 # landing Central de Agentes
    central/                 # kanban + detalhe
    studio/                  # chat / agentes
    api/content/             # CRUD pipeline
    api/publish/             # fila de posts
    api/chat/                # streaming agentes
  components/
    landing-page.tsx
    central-board.tsx
    app-shell.tsx
    chat-app.tsx
  lib/
    content/                 # store + types
    agents/                  # orchestrator + tools
```

## Próximos passos (opcional)

- Buffer API real / Meta Graph / YouTube Data API  
- Cron diário do Radar  
- TTS/avatar (HyperFrames) roteiro → MP4 sem gravação  
- Gate PIN local para a Central  
- Deploy Vercel com `XAI_API_KEY`
