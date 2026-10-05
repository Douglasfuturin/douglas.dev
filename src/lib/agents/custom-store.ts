import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import {
  AGENT_COLORS,
  type CustomAgent,
  type CustomAgentStore,
  type ToolkitPreset,
  TOOLKIT_PRESETS,
} from "./custom-types";

const DATA_DIR = path.join(process.cwd(), "data", "agents");
const STORE_PATH = path.join(DATA_DIR, "store.json");

function nowIso() {
  return new Date().toISOString();
}

function id() {
  return `agt_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}

function emptyStore(): CustomAgentStore {
  return { version: 1, agents: [] };
}

async function ensureStore(): Promise<CustomAgentStore> {
  await mkdir(DATA_DIR, { recursive: true });
  try {
    const raw = await readFile(STORE_PATH, "utf8");
    const parsed = JSON.parse(raw) as CustomAgentStore;
    if (!parsed.agents) parsed.agents = [];
    return parsed;
  } catch {
    const store = emptyStore();
    await writeFile(STORE_PATH, JSON.stringify(store, null, 2), "utf8");
    return store;
  }
}

async function saveStore(store: CustomAgentStore) {
  await mkdir(DATA_DIR, { recursive: true });
  await writeFile(STORE_PATH, JSON.stringify(store, null, 2), "utf8");
}

function sanitizeToolkit(value: unknown): ToolkitPreset {
  if (
    typeof value === "string" &&
    (TOOLKIT_PRESETS as readonly string[]).includes(value)
  ) {
    return value as ToolkitPreset;
  }
  return "chat";
}

export async function listCustomAgents(): Promise<CustomAgent[]> {
  const store = await ensureStore();
  return [...store.agents].sort((a, b) =>
    b.updatedAt.localeCompare(a.updatedAt),
  );
}

export async function getCustomAgent(agentId: string): Promise<CustomAgent | null> {
  const store = await ensureStore();
  return store.agents.find((a) => a.id === agentId) ?? null;
}

export async function createCustomAgent(input: {
  name: string;
  role: string;
  instructions: string;
  toolkit?: ToolkitPreset;
  color?: string;
  avatar?: string;
}): Promise<CustomAgent> {
  const store = await ensureStore();
  const ts = nowIso();
  const color =
    input.color ||
    AGENT_COLORS[store.agents.length % AGENT_COLORS.length];
  const agent: CustomAgent = {
    id: id(),
    name: input.name.trim().slice(0, 80),
    role: input.role.trim().slice(0, 160),
    instructions: input.instructions.trim().slice(0, 8000),
    toolkit: sanitizeToolkit(input.toolkit),
    color,
    avatar: (input.avatar || input.name.trim().slice(0, 2)).slice(0, 3).toUpperCase(),
    createdAt: ts,
    updatedAt: ts,
  };
  store.agents.unshift(agent);
  await saveStore(store);
  return agent;
}

export async function updateCustomAgent(
  agentId: string,
  patch: Partial<
    Pick<
      CustomAgent,
      "name" | "role" | "instructions" | "toolkit" | "color" | "avatar"
    >
  >,
): Promise<CustomAgent | null> {
  const store = await ensureStore();
  const idx = store.agents.findIndex((a) => a.id === agentId);
  if (idx < 0) return null;
  const prev = store.agents[idx];
  const next: CustomAgent = {
    ...prev,
    ...patch,
    name: patch.name?.trim().slice(0, 80) || prev.name,
    role: patch.role?.trim().slice(0, 160) || prev.role,
    instructions:
      patch.instructions?.trim().slice(0, 8000) || prev.instructions,
    toolkit: patch.toolkit ? sanitizeToolkit(patch.toolkit) : prev.toolkit,
    avatar: patch.avatar
      ? patch.avatar.slice(0, 3).toUpperCase()
      : prev.avatar,
    id: prev.id,
    createdAt: prev.createdAt,
    updatedAt: nowIso(),
  };
  store.agents[idx] = next;
  await saveStore(store);
  return next;
}

export async function deleteCustomAgent(agentId: string): Promise<boolean> {
  const store = await ensureStore();
  const before = store.agents.length;
  store.agents = store.agents.filter((a) => a.id !== agentId);
  if (store.agents.length === before) return false;
  await saveStore(store);
  return true;
}
