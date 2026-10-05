import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { getCatalogAgent } from "./agent-catalog";
import { listCustomAgents } from "./custom-store";
import { getRegistryAgent } from "./registry/store";
import type {
  AgentGroupStore,
  GroupMemberRef,
  OperationId,
  UserAgentGroup,
} from "./group-types";
import { OPERATIONS } from "./group-types";

const DATA_DIR = path.join(process.cwd(), "data", "agents");
const STORE_PATH = path.join(DATA_DIR, "groups.json");

const MAX_MEMBERS = 8;

function nowIso() {
  return new Date().toISOString();
}

function id(prefix: string) {
  return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}

function emptyStore(): AgentGroupStore {
  return { version: 1, groups: [] };
}

async function ensureStore(): Promise<AgentGroupStore> {
  await mkdir(DATA_DIR, { recursive: true });
  try {
    const raw = await readFile(STORE_PATH, "utf8");
    const parsed = JSON.parse(raw) as AgentGroupStore;
    if (!parsed.groups) parsed.groups = [];
    return parsed;
  } catch {
    const store = emptyStore();
    await writeFile(STORE_PATH, JSON.stringify(store, null, 2), "utf8");
    return store;
  }
}

async function saveStore(store: AgentGroupStore) {
  await mkdir(DATA_DIR, { recursive: true });
  await writeFile(STORE_PATH, JSON.stringify(store, null, 2), "utf8");
}

function sanitizeOperation(value: unknown): OperationId {
  if (
    typeof value === "string" &&
    (OPERATIONS as readonly string[]).includes(value)
  ) {
    return value as OperationId;
  }
  return "times";
}

function makeOrchestratorMember(): GroupMemberRef {
  const cat = getCatalogAgent("orquestrador")!;
  return {
    id: id("mem"),
    sourceId: cat.id,
    kind: "builtin",
    name: cat.name,
    role: cat.role,
    mode: cat.mode,
    color: cat.color,
    icon: cat.icon,
    isOrchestrator: true,
  };
}

function defaultWorkflow(name: string): string[] {
  return [
    `Orquestrador entende o briefing e escolhe o próximo agente do grupo "${name}"`,
    "Agente especializado executa a etapa e devolve o artefato",
    "Orquestrador faz o handoff para o próximo membro",
    "Time fecha o pacote e lista o próximo passo no pipeline",
  ];
}

export async function listUserGroups(): Promise<UserAgentGroup[]> {
  const store = await ensureStore();
  return [...store.groups]
    .filter((g) => g.status !== "archived")
    .sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
}

export async function getUserGroup(
  groupId: string,
): Promise<UserAgentGroup | null> {
  const store = await ensureStore();
  return store.groups.find((g) => g.id === groupId) ?? null;
}

export async function createUserGroup(input: {
  name: string;
  blurb?: string;
  operation?: OperationId;
  workflow?: string[];
  memberSourceIds?: string[];
}): Promise<UserAgentGroup> {
  const store = await ensureStore();
  const ts = nowIso();
  const orchestrator = makeOrchestratorMember();
  const members: GroupMemberRef[] = [orchestrator];

  const customAgents = await listCustomAgents();
  for (const sourceId of input.memberSourceIds ?? []) {
    if (sourceId === "orquestrador" || sourceId === "bit") continue;
    if (members.length >= MAX_MEMBERS) break;
    const builtin = getCatalogAgent(sourceId);
    if (builtin) {
      members.push({
        id: id("mem"),
        sourceId: builtin.id,
        kind: "builtin",
        name: builtin.name,
        role: builtin.role,
        mode: builtin.mode,
        color: builtin.color,
        icon: builtin.icon,
        isOrchestrator: false,
      });
      continue;
    }
    const custom = customAgents.find((a) => a.id === sourceId);
    if (custom) {
      members.push({
        id: id("mem"),
        sourceId: custom.id,
        kind: "custom",
        name: custom.name,
        role: custom.role,
        mode: "custom",
        color: custom.color,
        icon: "circle",
        isOrchestrator: false,
        customAgentId: custom.id,
      });
    }
  }

  const group: UserAgentGroup = {
    id: id("grp"),
    name: input.name.trim().slice(0, 80),
    blurb:
      (input.blurb?.trim() ||
        "Grupo de agentes que conversam e fecham o fluxo sob o Orquestrador.")
        .slice(0, 280),
    maxMembers: MAX_MEMBERS,
    operation: sanitizeOperation(input.operation),
    members,
    workflow:
      input.workflow?.filter(Boolean).slice(0, 8) ||
      defaultWorkflow(input.name.trim()),
    orchestratorMemberId: orchestrator.id,
    createdAt: ts,
    updatedAt: ts,
  };

  store.groups.unshift(group);
  await saveStore(store);
  return group;
}

export async function updateUserGroup(
  groupId: string,
  patch: Partial<
    Pick<UserAgentGroup, "name" | "blurb" | "operation" | "workflow">
  >,
): Promise<UserAgentGroup | null> {
  const store = await ensureStore();
  const idx = store.groups.findIndex((g) => g.id === groupId);
  if (idx < 0) return null;
  const prev = store.groups[idx];
  const next: UserAgentGroup = {
    ...prev,
    name: patch.name?.trim().slice(0, 80) || prev.name,
    blurb: patch.blurb?.trim().slice(0, 280) || prev.blurb,
    operation: patch.operation
      ? sanitizeOperation(patch.operation)
      : prev.operation,
    workflow: patch.workflow?.length
      ? patch.workflow.filter(Boolean).slice(0, 8)
      : prev.workflow,
    updatedAt: nowIso(),
  };
  store.groups[idx] = next;
  await saveStore(store);
  return next;
}

export async function deleteUserGroup(groupId: string): Promise<boolean> {
  const store = await ensureStore();
  const before = store.groups.length;
  store.groups = store.groups.filter((g) => g.id !== groupId);
  if (store.groups.length === before) return false;
  await saveStore(store);
  return true;
}

export async function addMemberToGroup(
  groupId: string,
  sourceId: string,
): Promise<UserAgentGroup | null> {
  const store = await ensureStore();
  const idx = store.groups.findIndex((g) => g.id === groupId);
  if (idx < 0) return null;
  const group = store.groups[idx];
  if (group.members.length >= group.maxMembers) {
    throw new Error("group_full");
  }
  if (group.members.some((m) => m.sourceId === sourceId)) {
    throw new Error("already_member");
  }

  const builtin = getCatalogAgent(sourceId);
  let member: GroupMemberRef | null = null;
  if (builtin) {
    member = {
      id: id("mem"),
      sourceId: builtin.id,
      kind: "builtin",
      name: builtin.name,
      role: builtin.role,
      mode: builtin.mode,
      color: builtin.color,
      icon: builtin.icon,
      isOrchestrator: false,
    };
  } else {
    const reg = await getRegistryAgent(sourceId);
    if (reg?.seedKey) {
      const seeded = getCatalogAgent(reg.seedKey);
      if (seeded) {
        member = {
          id: id("mem"),
          sourceId: seeded.id,
          kind: "builtin",
          name: reg.name,
          role: reg.role,
          mode: seeded.mode,
          color: reg.color,
          icon: seeded.icon,
          isOrchestrator: false,
        };
      }
    }
    if (!member) {
      const custom =
        (await listCustomAgents()).find((a) => a.id === sourceId) ||
        (reg
          ? {
              id: reg.id,
              name: reg.name,
              role: reg.role,
              color: reg.color,
            }
          : null);
      if (!custom) throw new Error("agent_not_found");
      member = {
        id: id("mem"),
        sourceId: custom.id,
        kind: "custom",
        name: custom.name,
        role: custom.role,
        mode: "custom",
        color: custom.color,
        icon: "circle",
        isOrchestrator: false,
        customAgentId: custom.id,
      };
    }
  }

  group.members.push(member);
  group.updatedAt = nowIso();
  store.groups[idx] = group;
  await saveStore(store);
  return group;
}

export async function removeMemberFromGroup(
  groupId: string,
  memberId: string,
): Promise<UserAgentGroup | null> {
  const store = await ensureStore();
  const idx = store.groups.findIndex((g) => g.id === groupId);
  if (idx < 0) return null;
  const group = store.groups[idx];
  const target = group.members.find((m) => m.id === memberId);
  if (!target) throw new Error("member_not_found");
  if (target.isOrchestrator || target.id === group.orchestratorMemberId) {
    throw new Error("cannot_remove_orchestrator");
  }
  group.members = group.members.filter((m) => m.id !== memberId);
  group.updatedAt = nowIso();
  store.groups[idx] = group;
  await saveStore(store);
  return group;
}

export async function setGroupOrchestrator(
  groupId: string,
  memberId: string,
): Promise<UserAgentGroup | null> {
  const store = await ensureStore();
  const idx = store.groups.findIndex((g) => g.id === groupId);
  if (idx < 0) return null;
  const group = store.groups[idx];
  if (!group.members.some((m) => m.id === memberId)) {
    throw new Error("member_not_found");
  }
  group.members = group.members.map((m) => ({
    ...m,
    isOrchestrator: m.id === memberId,
  }));
  group.orchestratorMemberId = memberId;
  group.updatedAt = nowIso();
  store.groups[idx] = group;
  await saveStore(store);
  return group;
}
