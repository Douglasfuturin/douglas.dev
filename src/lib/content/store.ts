import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import {
  type ContentItem,
  type ContentMarket,
  type ContentNetwork,
  type ContentSource,
  type ContentStage,
  type ContentStore,
  type PublishJob,
  nextStage,
} from "./types";

const DATA_DIR = path.join(process.cwd(), "data", "content");
const STORE_PATH = path.join(DATA_DIR, "store.json");

function nowIso() {
  return new Date().toISOString();
}

function id(prefix: string) {
  return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}

function emptyStore(): ContentStore {
  return { version: 1, items: [], publishQueue: [] };
}

async function ensureStore(): Promise<ContentStore> {
  await mkdir(DATA_DIR, { recursive: true });
  try {
    const raw = await readFile(STORE_PATH, "utf8");
    const parsed = JSON.parse(raw) as ContentStore;
    if (!parsed.items) parsed.items = [];
    if (!parsed.publishQueue) parsed.publishQueue = [];
    return parsed;
  } catch {
    const store = emptyStore();
    await writeFile(STORE_PATH, JSON.stringify(store, null, 2), "utf8");
    return store;
  }
}

async function saveStore(store: ContentStore) {
  await mkdir(DATA_DIR, { recursive: true });
  await writeFile(STORE_PATH, JSON.stringify(store, null, 2), "utf8");
}

export async function listContent(filters?: {
  stage?: ContentStage;
  market?: ContentMarket;
}): Promise<ContentItem[]> {
  const store = await ensureStore();
  let items = [...store.items].sort(
    (a, b) => b.updatedAt.localeCompare(a.updatedAt),
  );
  if (filters?.stage) items = items.filter((i) => i.stage === filters.stage);
  if (filters?.market) items = items.filter((i) => i.market === filters.market);
  return items;
}

export async function getContent(id: string): Promise<ContentItem | null> {
  const store = await ensureStore();
  return store.items.find((i) => i.id === id) ?? null;
}

export async function createContent(input: {
  title: string;
  summary?: string;
  stage?: ContentStage;
  market?: ContentMarket;
  networks?: ContentNetwork[];
  source?: ContentSource;
  score?: number;
  tags?: string[];
  topic?: string;
  script?: string;
  caption?: string;
  hashtags?: string[];
  artBrief?: string;
  videoPath?: string;
  notes?: string;
  groupId?: string;
}): Promise<ContentItem> {
  const store = await ensureStore();
  const ts = nowIso();
  const item: ContentItem = {
    id: id("cnt"),
    title: input.title.trim(),
    summary: (input.summary || "").trim(),
    stage: input.stage || "idea",
    market: input.market || "br",
    networks: input.networks?.length
      ? input.networks
      : ["instagram", "youtube"],
    source: input.source || "manual",
    score: input.score,
    tags: input.tags || [],
    topic: input.topic,
    script: input.script,
    caption: input.caption,
    hashtags: input.hashtags,
    artBrief: input.artBrief,
    videoPath: input.videoPath,
    assets: [],
    notes: input.notes,
    groupId: input.groupId,
    createdAt: ts,
    updatedAt: ts,
  };
  store.items.unshift(item);
  await saveStore(store);
  return item;
}

export async function updateContent(
  contentId: string,
  patch: Partial<
    Omit<ContentItem, "id" | "createdAt" | "updatedAt">
  >,
): Promise<ContentItem | null> {
  const store = await ensureStore();
  const idx = store.items.findIndex((i) => i.id === contentId);
  if (idx < 0) return null;
  const prev = store.items[idx];
  const next: ContentItem = {
    ...prev,
    ...patch,
    id: prev.id,
    createdAt: prev.createdAt,
    updatedAt: nowIso(),
  };
  if (patch.stage === "approved" && !next.approvedAt) next.approvedAt = nowIso();
  if (patch.stage === "ready" && !next.readyAt) next.readyAt = nowIso();
  if (patch.stage === "scheduled" && !next.scheduledAt) {
    next.scheduledAt = patch.scheduledAt || nowIso();
  }
  if (patch.stage === "published" && !next.publishedAt) {
    next.publishedAt = nowIso();
  }
  store.items[idx] = next;
  await saveStore(store);
  return next;
}

export async function advanceContent(
  contentId: string,
): Promise<ContentItem | null> {
  const item = await getContent(contentId);
  if (!item) return null;
  const nxt = nextStage(item.stage);
  if (!nxt) return item;
  return updateContent(contentId, { stage: nxt });
}

export async function deleteContent(contentId: string): Promise<boolean> {
  const store = await ensureStore();
  const before = store.items.length;
  store.items = store.items.filter((i) => i.id !== contentId);
  store.publishQueue = store.publishQueue.filter(
    (j) => j.contentId !== contentId,
  );
  if (store.items.length === before) return false;
  await saveStore(store);
  return true;
}

export async function getStats() {
  const items = await listContent();
  const byStage: Record<string, number> = {};
  for (const item of items) {
    byStage[item.stage] = (byStage[item.stage] || 0) + 1;
  }
  const store = await ensureStore();
  return {
    total: items.length,
    byStage,
    queued: store.publishQueue.filter((j) => j.status === "queued").length,
    scheduled: store.publishQueue.filter((j) => j.status === "scheduled")
      .length,
    published: items.filter((i) => i.stage === "published").length,
  };
}

export async function queuePublish(input: {
  contentId: string;
  network: ContentNetwork;
  scheduledAt?: string;
  caption?: string;
  mediaPath?: string;
}): Promise<PublishJob | null> {
  const store = await ensureStore();
  const item = store.items.find((i) => i.id === input.contentId);
  if (!item) return null;

  const job: PublishJob = {
    id: id("pub"),
    contentId: input.contentId,
    network: input.network,
    status: input.scheduledAt ? "scheduled" : "queued",
    scheduledAt: input.scheduledAt,
    caption: input.caption || item.caption,
    mediaPath: input.mediaPath || item.videoPath,
  };
  store.publishQueue.unshift(job);

  const idx = store.items.findIndex((i) => i.id === input.contentId);
  if (idx >= 0) {
    store.items[idx] = {
      ...store.items[idx],
      stage: input.scheduledAt ? "scheduled" : "ready",
      scheduledAt: input.scheduledAt || store.items[idx].scheduledAt,
      updatedAt: nowIso(),
    };
  }

  await saveStore(store);
  return job;
}

export async function listPublishQueue(): Promise<PublishJob[]> {
  const store = await ensureStore();
  return [...store.publishQueue];
}

export async function markPublishSent(
  jobId: string,
  result?: { externalId?: string; error?: string },
): Promise<PublishJob | null> {
  const store = await ensureStore();
  const idx = store.publishQueue.findIndex((j) => j.id === jobId);
  if (idx < 0) return null;
  const job = store.publishQueue[idx];
  if (result?.error) {
    store.publishQueue[idx] = {
      ...job,
      status: "failed",
      error: result.error,
    };
  } else {
    store.publishQueue[idx] = {
      ...job,
      status: "sent",
      sentAt: nowIso(),
      externalId: result?.externalId,
      error: undefined,
    };
    const cIdx = store.items.findIndex((i) => i.id === job.contentId);
    if (cIdx >= 0) {
      store.items[cIdx] = {
        ...store.items[cIdx],
        stage: "published",
        publishedAt: nowIso(),
        updatedAt: nowIso(),
      };
    }
  }
  await saveStore(store);
  return store.publishQueue[idx];
}

export async function seedDemoIfEmpty(): Promise<ContentItem[]> {
  const items = await listContent();
  if (items.length > 0) return items;

  const demos = [
    {
      title: "Agentes de IA no Next.js — o stack que está bombando",
      summary:
        "Tendência: frameworks multi-agente + Vercel AI SDK. Bom para Reels 60s + carrusel ES.",
      stage: "idea" as const,
      source: "radar" as const,
      score: 9,
      tags: ["ia", "agentes", "nextjs"],
      topic: "automação",
      market: "br" as const,
      networks: ["instagram", "youtube"] as ContentNetwork[],
    },
    {
      title: "Cómo montar un carrusel de LinkedIn en 24h",
      summary: "Pack España: guion → carrusel → capas → publicación.",
      stage: "script" as const,
      source: "grupo" as const,
      market: "es" as const,
      tags: ["carrusel", "linkedin"],
      networks: ["linkedin", "instagram"] as ContentNetwork[],
      script:
        "Hook: Deja de publicar posts olvidables.\nProblema: El feed premia formato.\nSolución: Plantilla de 7 slides.\nCTA: Guarda y copia el framework.",
      groupId: "conteudos-espanha",
    },
    {
      title: "Repo open-source da semana — pack Scout→Reels→Notion",
      summary: "GitHub Scout escolheu um repo; roteiro e guia Notion prontos.",
      stage: "packaged" as const,
      source: "pipeline" as const,
      tags: ["github", "open-source"],
      networks: ["youtube", "notion", "x"] as ContentNetwork[],
      caption: "Repo da semana no feed — link no Notion.",
    },
  ];

  const created: ContentItem[] = [];
  for (const d of demos) {
    created.push(await createContent(d));
  }
  return created;
}
