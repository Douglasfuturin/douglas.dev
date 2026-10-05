import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import type { AgentGroupStore, GroupMemberRef, UserAgentGroup } from "./group-types";
import { createUserGroup, getUserGroup } from "./group-store";

const DATA_DIR = path.join(process.cwd(), "data", "agents");
const STORE_PATH = path.join(DATA_DIR, "groups.json");

function nowIso() {
  return new Date().toISOString();
}

async function loadStore(): Promise<AgentGroupStore> {
  const raw = await readFile(STORE_PATH, "utf8");
  return JSON.parse(raw) as AgentGroupStore;
}

async function saveStore(store: AgentGroupStore) {
  await mkdir(DATA_DIR, { recursive: true });
  await writeFile(STORE_PATH, JSON.stringify(store, null, 2), "utf8");
}

export async function updateUserGroupMembers(
  groupId: string,
  members: GroupMemberRef[],
): Promise<UserAgentGroup | null> {
  const store = await loadStore();
  const idx = store.groups.findIndex((g) => g.id === groupId);
  if (idx < 0) return null;
  store.groups[idx] = {
    ...store.groups[idx],
    members,
    updatedAt: nowIso(),
  };
  await saveStore(store);
  return store.groups[idx];
}

export async function duplicateUserGroup(
  groupId: string,
  newName?: string,
): Promise<UserAgentGroup | null> {
  const source = await getUserGroup(groupId);
  if (!source) return null;
  const memberSourceIds = source.members
    .filter((m) => !m.isOrchestrator)
    .map((m) => m.customAgentId || m.sourceId);
  return createUserGroup({
    name: newName || `${source.name} (cópia)`,
    blurb: source.blurb,
    operation: source.operation,
    workflow: [...source.workflow],
    memberSourceIds,
  });
}

export async function archiveUserGroup(groupId: string): Promise<boolean> {
  const store = await loadStore();
  const idx = store.groups.findIndex((g) => g.id === groupId);
  if (idx < 0) return false;
  store.groups[idx] = {
    ...store.groups[idx],
    status: "archived",
    updatedAt: nowIso(),
  };
  await saveStore(store);
  return true;
}

export async function insertMemberAfterInGroup(
  groupId: string,
  sourceAgentId: string,
  afterMemberId?: string,
): Promise<UserAgentGroup | null> {
  const { addMemberToGroup } = await import("./group-store");
  let group = await getUserGroup(groupId);
  if (!group) return null;
  try {
    group = await addMemberToGroup(groupId, sourceAgentId);
  } catch (err) {
    if (err instanceof Error && err.message === "already_member") {
      /* ok */
    } else {
      throw err;
    }
    group = await getUserGroup(groupId);
  }
  if (!group || !afterMemberId) return group;

  const ids = group.members.map((m) => m.id);
  const afterIdx = ids.indexOf(afterMemberId);
  const newMember = group.members.find((m) => m.sourceId === sourceAgentId || m.customAgentId === sourceAgentId);
  if (!newMember || afterIdx < 0) return group;

  const without = group.members.filter((m) => m.id !== newMember.id);
  const reordered = [
    ...without.slice(0, afterIdx + 1),
    newMember,
    ...without.slice(afterIdx + 1),
  ];
  return updateUserGroupMembers(groupId, reordered);
}
