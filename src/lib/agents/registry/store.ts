import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import {
  AGENT_COLORS,
  TOOLKIT_PRESETS,
  type ToolkitPreset,
} from "../custom-types";
import { buildSeedAgents } from "./seed";
import type {
  AgentProposal,
  AgentProposalKind,
  RegistryAgent,
  RegistryStore,
} from "./types";

const DATA_DIR = path.join(process.cwd(), "data", "agents");
const REGISTRY_PATH = path.join(DATA_DIR, "registry.json");

function nowIso() {
  return new Date().toISOString();
}

function newId(prefix: string) {
  return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}

function emptyStore(): RegistryStore {
  return { version: 2, agents: [], proposals: [] };
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

async function ensureRegistry(): Promise<RegistryStore> {
  await mkdir(DATA_DIR, { recursive: true });
  try {
    const raw = await readFile(REGISTRY_PATH, "utf8");
    const parsed = JSON.parse(raw) as RegistryStore;
    if (!parsed.agents) parsed.agents = [];
    if (!parsed.proposals) parsed.proposals = [];
    if (parsed.agents.length === 0) {
      const ts = nowIso();
      parsed.agents = buildSeedAgents(ts);
      await writeFile(REGISTRY_PATH, JSON.stringify(parsed, null, 2), "utf8");
    }
    return parsed;
  } catch {
    const ts = nowIso();
    const store: RegistryStore = {
      version: 2,
      agents: buildSeedAgents(ts),
      proposals: [],
    };
    await writeFile(REGISTRY_PATH, JSON.stringify(store, null, 2), "utf8");
    return store;
  }
}

async function saveRegistry(store: RegistryStore) {
  await mkdir(DATA_DIR, { recursive: true });
  await writeFile(REGISTRY_PATH, JSON.stringify(store, null, 2), "utf8");
}

export async function listRegistryAgents(options?: {
  status?: RegistryAgent["status"] | "all";
}): Promise<RegistryAgent[]> {
  const store = await ensureRegistry();
  const status = options?.status ?? "active";
  return store.agents
    .filter((a) => status === "all" || a.status === status)
    .sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
}

export async function getRegistryAgent(
  agentId: string,
): Promise<RegistryAgent | null> {
  const store = await ensureRegistry();
  return store.agents.find((a) => a.id === agentId) ?? null;
}

export async function findRegistryAgentByName(
  name: string,
): Promise<RegistryAgent | null> {
  const store = await ensureRegistry();
  const q = name.trim().toLowerCase();
  return (
    store.agents.find((a) => a.name.toLowerCase() === q && a.status !== "archived") ??
    null
  );
}

export type CreateAgentInput = {
  name: string;
  role: string;
  systemPrompt: string;
  toolkit?: ToolkitPreset;
  model?: RegistryAgent["model"];
  color?: string;
  avatar?: string;
  inputs?: string[];
  outputs?: string[];
  allowedTools?: string[];
  runtimeMode?: string;
};

function buildAgentFromInput(input: CreateAgentInput): RegistryAgent {
  const ts = nowIso();
  const color = input.color || AGENT_COLORS[Math.floor(Math.random() * AGENT_COLORS.length)];
  return {
    id: newId("reg"),
    name: input.name.trim().slice(0, 80),
    avatar: (input.avatar || input.name.trim().slice(0, 2)).slice(0, 3).toUpperCase(),
    color,
    role: input.role.trim().slice(0, 200),
    systemPrompt: input.systemPrompt.trim().slice(0, 12000),
    model: input.model ?? "multi",
    toolkit: sanitizeToolkit(input.toolkit),
    allowedTools: input.allowedTools?.slice(0, 40) ?? [],
    inputs: input.inputs?.slice(0, 12) ?? ["briefing do usuário"],
    outputs: input.outputs?.slice(0, 12) ?? ["artefato principal"],
    status: "active",
    version: 1,
    runtimeMode: input.runtimeMode ?? "custom",
    createdAt: ts,
    updatedAt: ts,
  };
}

export async function createRegistryAgent(
  input: CreateAgentInput,
): Promise<RegistryAgent> {
  const store = await ensureRegistry();
  const agent = buildAgentFromInput(input);
  store.agents.unshift(agent);
  await saveRegistry(store);
  return agent;
}

export async function updateRegistryAgent(
  agentId: string,
  patch: Partial<
    Pick<
      RegistryAgent,
      | "name"
      | "role"
      | "systemPrompt"
      | "toolkit"
      | "model"
      | "color"
      | "avatar"
      | "inputs"
      | "outputs"
      | "allowedTools"
      | "status"
      | "runtimeMode"
    >
  >,
  meta?: { versionSummary?: string },
): Promise<{ agent: RegistryAgent; previousPrompt?: string; diff?: string } | null> {
  const store = await ensureRegistry();
  const idx = store.agents.findIndex((a) => a.id === agentId);
  if (idx < 0) return null;
  const prev = store.agents[idx];
  const previousPrompt = prev.systemPrompt;
  const nextPrompt = patch.systemPrompt?.trim() ?? prev.systemPrompt;
  const next: RegistryAgent = {
    ...prev,
    ...patch,
    name: patch.name?.trim().slice(0, 80) ?? prev.name,
    role: patch.role?.trim().slice(0, 200) ?? prev.role,
    systemPrompt: nextPrompt.slice(0, 12000),
    toolkit: patch.toolkit ? sanitizeToolkit(patch.toolkit) : prev.toolkit,
    avatar: patch.avatar?.slice(0, 3).toUpperCase() ?? prev.avatar,
    version: patch.systemPrompt && patch.systemPrompt !== prev.systemPrompt ? prev.version + 1 : prev.version,
    updatedAt: nowIso(),
  };
  store.agents[idx] = next;
  await saveRegistry(store);

  const { appendAgentVersion } = await import("./versions");
  if (patch.systemPrompt && patch.systemPrompt !== previousPrompt) {
    await appendAgentVersion(agentId, {
      version: next.version,
      systemPrompt: next.systemPrompt,
      summary: meta?.versionSummary || "Atualização via orquestrador",
      changedAt: next.updatedAt,
    });
  }

  return {
    agent: next,
    previousPrompt,
    diff:
      patch.systemPrompt && patch.systemPrompt !== previousPrompt
        ? `--- antes\n${previousPrompt.slice(0, 1200)}\n--- depois\n${next.systemPrompt.slice(0, 1200)}`
        : undefined,
  };
}

export async function setRegistryAgentStatus(
  agentId: string,
  status: RegistryAgent["status"],
): Promise<RegistryAgent | null> {
  return (await updateRegistryAgent(agentId, { status }))?.agent ?? null;
}

export async function createProposal(input: {
  kind: AgentProposalKind;
  preview: Record<string, unknown>;
  payload: Record<string, unknown>;
}): Promise<AgentProposal> {
  const store = await ensureRegistry();
  const proposal: AgentProposal = {
    id: newId("prop"),
    kind: input.kind,
    preview: input.preview,
    payload: input.payload,
    createdAt: nowIso(),
  };
  store.proposals.unshift(proposal);
  store.proposals = store.proposals.slice(0, 30);
  await saveRegistry(store);
  return proposal;
}

export async function getProposal(
  proposalId: string,
): Promise<AgentProposal | null> {
  const store = await ensureRegistry();
  return store.proposals.find((p) => p.id === proposalId) ?? null;
}

export async function cancelProposal(proposalId: string): Promise<boolean> {
  const store = await ensureRegistry();
  const before = store.proposals.length;
  store.proposals = store.proposals.filter((p) => p.id !== proposalId);
  if (store.proposals.length === before) return false;
  await saveRegistry(store);
  return true;
}

export async function confirmProposal(proposalId: string): Promise<{
  ok: boolean;
  error?: string;
  agent?: RegistryAgent;
  groupId?: string;
}> {
  const store = await ensureRegistry();
  const proposal = store.proposals.find((p) => p.id === proposalId);
  if (!proposal) return { ok: false, error: "proposal_not_found" };

  if (proposal.kind === "create_agent") {
    const payload = proposal.payload as CreateAgentInput;
    const agent = buildAgentFromInput(payload);
    store.agents.unshift(agent);
    store.proposals = store.proposals.filter((p) => p.id !== proposalId);
    await saveRegistry(store);
    const { syncCustomStoreFromRegistry } = await import("./sync-custom");
    await syncCustomStoreFromRegistry(agent);
    return { ok: true, agent };
  }

  if (proposal.kind === "update_agent") {
    const { agentId, patch, versionSummary } = proposal.payload as {
      agentId: string;
      patch: Partial<RegistryAgent>;
      versionSummary?: string;
    };
    store.proposals = store.proposals.filter((p) => p.id !== proposalId);
    await saveRegistry(store);
    const result = await updateRegistryAgent(agentId, patch, { versionSummary });
    if (!result) return { ok: false, error: "agent_not_found" };
    const { syncCustomStoreFromRegistry } = await import("./sync-custom");
    await syncCustomStoreFromRegistry(result.agent);
    return { ok: true, agent: result.agent };
  }

  return { ok: false, error: "unsupported_proposal" };
}

/** Map registry agent to legacy custom agent shape for chat resolution. */
export function registryToCustomShape(agent: RegistryAgent) {
  return {
    id: agent.id,
    name: agent.name,
    role: agent.role,
    instructions: agent.systemPrompt,
    toolkit: agent.toolkit,
    color: agent.color,
    avatar: agent.avatar,
    createdAt: agent.createdAt,
    updatedAt: agent.updatedAt,
  };
}
