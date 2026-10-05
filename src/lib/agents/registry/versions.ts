import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import type { AgentPromptVersion, AgentVersionStore } from "./types";

const DATA_DIR = path.join(process.cwd(), "data", "agents");
const VERSIONS_PATH = path.join(DATA_DIR, "agent-versions.json");

async function ensureVersions(): Promise<AgentVersionStore> {
  await mkdir(DATA_DIR, { recursive: true });
  try {
    const raw = await readFile(VERSIONS_PATH, "utf8");
    const parsed = JSON.parse(raw) as AgentVersionStore;
    if (!parsed.byAgent) parsed.byAgent = {};
    return parsed;
  } catch {
    const store: AgentVersionStore = { version: 1, byAgent: {} };
    await writeFile(VERSIONS_PATH, JSON.stringify(store, null, 2), "utf8");
    return store;
  }
}

async function saveVersions(store: AgentVersionStore) {
  await mkdir(DATA_DIR, { recursive: true });
  await writeFile(VERSIONS_PATH, JSON.stringify(store, null, 2), "utf8");
}

export async function appendAgentVersion(
  agentId: string,
  entry: AgentPromptVersion,
) {
  const store = await ensureVersions();
  const list = store.byAgent[agentId] ?? [];
  list.unshift(entry);
  store.byAgent[agentId] = list.slice(0, 20);
  await saveVersions(store);
}

export async function listAgentVersions(agentId: string) {
  const store = await ensureVersions();
  return store.byAgent[agentId] ?? [];
}
