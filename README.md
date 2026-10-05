# Central de Agentes

SaaS pessoal de **operações de conteúdo** — do radar ao post — com identidade **Douglas Dev** (preto + laranja `#F26522`).

Stack: **Next.js 16** · **Vercel AI SDK** · **xAI Grok** (`grok-4.7` / `grok-4.20-multi-agent`).

Uso single-user: dados em JSON local (`data/`), sem multi-tenant.

---

## O que o sistema faz

A Central de Agentes transforma ideias em conteúdo pronto para publicar, com **agentes especializados** que trabalham em **pipeline** (sequência) dentro de **grupos**.

| Etapa | O que acontece |
| --- | --- |
| **1. Ideação** | Radar de Pesquisa e GitHub Scout encontram temas/repos |
| **2. Roteiro** | Roteirista escreve Reels ~60s / copy de carrossel |
| **3. Visual** | Diretores de arte (Twitter + realista Antes/Depois) |
| **4. Vídeo** | Editores de Reels (animação/realismo) e Reels pessoal (você envia → recebe editado) |
| **5. Pacote** | Notion + artefatos em `outputs/` |
| **6. Publicação** | Kanban CRM + fila local (`/api/publish`) |

Há um **Orquestrador Principal** que coordena todos os grupos e um **Orquestrador por grupo** que conduz o fluxo entre os membros.

---

## Como funciona (visão geral)

```
Você
 ├─ /dashboard     → pipelines por grupo + stats
 ├─ /grupos        → criar/editar times, add/remove agentes
 ├─ /studio        → conversa com agentes (modos)
 ├─ /central       → kanban ideia → postado
 ├─ /agentes       → criar agentes custom
 ├─ /kits          → instalar skills Ninja
 └─ /editor        → edição visual de vídeo

Studio / Chat
 └─ POST /api/chat
      └─ orchestrator.resolveAgent(mode, group, member…)
           ├─ persona (prompts)
           ├─ modelo (grok-4.7 ou multi-agent)
           └─ tools (radar, arte, vídeo, central, github…)
```

1. Você escolhe um **grupo** ou **modo** no Studio (ou deixa `auto` rotear).
2. O **orquestrador** resolve persona + tools.
3. O agente usa tools (pesquisa, pipeline CRM, edição, etc.).
4. Itens persistem em `data/content/store.json` e avançam no kanban.
5. Quando `ready`, entram na fila de publicação.

---

## Pipelines de agentes (grupos padrão)

### Conteúdo Dev — Imagem

| # | Agente | Função |
| --- | --- | --- |
| 1 | Radar de Pesquisa | Briefing de IA, automação e marketing |
| 2 | Roteirista | Roteiro / copy do carrossel |
| 3 | Diretor de Arte Twitter | Peças estilo X/Twitter |
| 4 | Diretor de Arte Realista | Carrossel Antes/Depois fotorealista Douglas Dev |

Orquestrador do grupo coordena handoffs.

### Conteúdo Dev — Vídeo

| # | Agente | Função |
| --- | --- | --- |
| 1 | Radar de Pesquisa | Temas fortes para vídeo |
| 2 | Roteirista | Script Reels ~60s |
| 3 | Editor Reels Animação/Realismo | Corte 9:16, ritmo, legendas |
| 4 | Editor Reels Pessoal | Você envia o vídeo → devolve pronto, editado |

### Conteúdo Espanha

Mercado ES (labels em português; conteúdo publicado em espanhol da Espanha):

Roteirista ES → Carrossel ES → YouTube ES → Capas e Miniaturas → Editor de Vídeo ES → Orquestrador.

### Grupos custom

Em `/grupos` ou no dashboard você pode:

- **Criar grupo** (já nasce com Orquestrador)
- **Adicionar / remover agentes** (catálogo + agents custom)
- Abrir a **sala** no Studio (`mode=grupo`)

---

## Rotas do produto

| Rota | Função |
| --- | --- |
| `/` | Landing Douglas Dev / Central de Agentes |
| `/dashboard` | CRM: pipelines Imagem/Vídeo + grupos custom + fila |
| `/central` | Kanban do pipeline editorial |
| `/central/[id]` | Detalhe do item (avançar estágio, publicar) |
| `/studio` | Chat multi-agente (todos os modos) |
| `/grupos` | Gerenciar grupos e membros |
| `/agentes` | Criar agentes custom (persona + toolkit) |
| `/kits` | Hub Ninja Kits (ZIP → instalar → usar) |
| `/editor` | Editor visual EDVD |
| `/radar` `/roteiro` `/github` `/pipeline` `/notion` | Atalhos → Studio |

---

## Modos do Studio

| Modo | Modelo | Uso |
| --- | --- | --- |
| `orquestrador` | multi-agent | Coordena todos os grupos/operações |
| `grupo` | grok-4.7 | Sala do grupo (orquestra membros) |
| `central` | grok-4.7 | Opera o kanban CRM + fila |
| `radar` | grok-4.7 | Briefing diário |
| `github` | grok-4.7 | Scout de repos + roteiro 60s |
| `roteiro` / `roteiro-pessoal` | grok-4.7 | Scripts |
| `arte-twitter` / `arte-realista` | grok-4.7 | Direção de arte |
| `editor-reels` / `video` | grok-4.7 | Edição de vídeo |
| `youtube` / `carrossel` / `capas` | grok-4.7 | Mercado Espanha |
| `custom` | conforme toolkit | Agente criado por você |
| `kits` / `pipeline` / `notion` / `research` | — | Skills, pack Scout→Reels→Notion, Notion, pesquisa profunda |
| `auto` | roteador | Classifica a mensagem e escolhe o modo |

Query params úteis:

```
/studio?mode=grupo&group=conteudo-dev
/studio?mode=arte-realista&group=conteudo-dev&member=arte-realista
/studio?mode=orquestrador
/studio?mode=custom&agent=<id>
```

---

## Pipeline CRM (conteúdo)

Estágios:

```
idea → approved → script → art → video → packaged → ready → scheduled → published
```

- **Store:** `data/content/store.json`
- **API:** `GET/POST /api/content`, `PATCH/DELETE /api/content/[id]`
- **Publicação:** `POST /api/publish` (fila local; Buffer opcional via `BUFFER_ACCESS_TOKEN`)

---

## Dados locais

```
data/
  content/store.json     # itens do pipeline + fila
  agents/store.json      # agentes custom
  agents/groups.json     # grupos criados por você
```

(`data/` está no `.gitignore` — criado em runtime.)

---

## Estrutura do repositório

```
src/
  app/
    page.tsx                 # landing
    dashboard/               # CRM + pipelines
    central/                 # kanban + detalhe
    studio/                  # chat de agentes
    grupos/                  # CRUD de grupos
    agentes/                 # CRUD de agentes custom
    kits/ editor/ …          # módulos
    api/
      chat/                  # streaming (AI SDK)
      content/ publish/      # pipeline + fila
      agents/ groups/        # agents e grupos
      kits/ editor/ upload/  # skills e mídia

  components/
    crm/
      dashboard.tsx          # pipelines por grupo
      groups-manager.tsx     # criar/add/remove
      agents-manager.tsx
      crm-shell.tsx          # shell lateral
    chat-app.tsx             # Studio
    central-board.tsx
    landing-page.tsx
    …

  lib/
    agents/
      orchestrator.ts        # resolve mode → persona + tools
      groups.ts              # grupos padrão (Imagem / Vídeo / Espanha)
      group-store.ts         # grupos custom
      agent-catalog.ts       # agentes disponíveis para times
      prompts.ts             # personas
      *-tools.ts             # tools por domínio
    content/                 # types + store do CRM
    kits/                    # descoberta/instalação de skills
    video/                   # opções e runner de edição
    brand/douglas-dev.ts     # identidade visual
```

---

## Identidade visual

- **Marca:** Douglas Dev · Central de Agentes  
- **Cores:** preto `#0a0a0a` · superfície `#121212` · laranja `#F26522`  
- **UI:** cards dark (borda sutil, texto branco)  
- **Carrosséis realistas:** Antes → Depois fotorealista no estilo da marca  

---

## Como rodar

```bash
cp .env.example .env.local
# XAI_API_KEY=…   (obrigatório — https://console.x.ai)

npm install
npm run dev
```

Abra [http://localhost:3000](http://localhost:3000) → **Dashboard** ou **Studio**.

### Variáveis opcionais

| Variável | Uso |
| --- | --- |
| `GITHUB_TOKEN` | Scout com mais rate limit |
| `NOTION_TOKEN` + `NOTION_PARENT_PAGE_ID` | Guias Notion |
| `BUFFER_ACCESS_TOKEN` | Stub de envio social |

### Vídeo / ffmpeg

Para edição automática:

```bash
cd kit-edicao-video/skill && uv sync   # ffmpeg no PATH
```

Skills Ninja: coloque `.zip` em `ninja-kits/sources/` → `/kits` → **Instalar**.

---

## APIs principais

| Endpoint | Função |
| --- | --- |
| `POST /api/chat` | Stream do agente (mode, groupId, memberId, customAgentId…) |
| `GET/POST /api/content` | Listar / criar itens do pipeline |
| `PATCH /api/content/[id]` | Atualizar / avançar estágio |
| `GET/POST /api/publish` | Fila de posts |
| `GET/POST /api/agents` | Agentes custom |
| `GET/POST /api/groups` | Grupos (builtin + custom) |
| `PATCH /api/groups/[id]` | update / add_member / remove_member / set_orchestrator |
| `GET/POST /api/kits` | Inventário e instalação de skills |

---

## Fluxo típico (exemplo)

1. **Dashboard** → abrir **Conteúdo Dev — Imagem**
2. Etapa 1: **Radar de Pesquisa** gera briefing e pede aprovação  
3. Etapa 2: **Roteirista** fecha o copy  
4. Etapas 3–4: **Arte Twitter** + **Arte Realista**  
5. Item aparece no **kanban** (`/central`)  
6. Avança até `ready` → **fila de posts**  

Para vídeo: mesmo radar/roteiro, depois editores; no **Reels Pessoal**, faça upload do MP4 no Studio.

---

## Deploy

- **Web (Studio/CRM):** Vercel com `XAI_API_KEY`  
- **Vídeo/ffmpeg:** precisa de máquina com binários (VPS) — o FS da Vercel é efêmero; para produção use Blob/DB no lugar de `data/*.json`

---

## Próximos passos (opcional)

- APIs reais Meta / YouTube / TikTok / Buffer  
- Cron diário do Radar  
- Persistência em Postgres/Blob  
- TTS/avatar (HyperFrames) roteiro → MP4  
- Gate PIN local
