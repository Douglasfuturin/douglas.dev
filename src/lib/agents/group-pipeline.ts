import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { AGENT_GROUPS } from "./groups";
import { getUserGroup, listUserGroups } from "./group-store";
import type { GroupMemberRef, UserAgentGroup } from "./group-types";

const DATA_DIR = path.join(process.cwd(), "data", "agents");
const OVERRIDES_PATH = path.join(DATA_DIR, "group-overrides.json");

type BuiltinOverride = {
  memberOrder?: string[];
  removedMemberIds?: string[];
};

type OverrideStore = {
  version: 1;
  builtin: Record<string, BuiltinOverride>;
};

async function ensureOverrides(): Promise<OverrideStore> {
  await mkdir(DATA_DIR, { recursive: true });
  try {
    const raw = await readFile(OVERRIDES_PATH, "utf8");
    return JSON.parse(raw) as OverrideStore;
  } catch {
    const store: OverrideStore = { version: 1, builtin: {} };
    await writeFile(OVERRIDES_PATH, JSON.stringify(store, null, 2), "utf8");
    return store;
  }
}

async function saveOverrides(store: OverrideStore) {
  await writeFile(OVERRIDES_PATH, JSON.stringify(store, null, 2), "utf8");
}

export async function reorderGroupMembers(
  groupId: string,
  orderedMemberIds: string[],
): Promise<{ ok: boolean; error?: string }> {
  const user = await getUserGroup(groupId);
  if (user) {
    const map = new Map(user.members.map((m) => [m.id, m]));
    const reordered: GroupMemberRef[] = [];
    for (const id of orderedMemberIds) {
      const m = map.get(id);
      if (m) reordered.push(m);
    }
    for (const m of user.members) {
      if (!reordered.some((r) => r.id === m.id)) reordered.push(m);
    }
    const { updateUserGroupMembers } = await import("./group-store-ext");
    await updateUserGroupMembers(groupId, reordered);
    return { ok: true };
  }

  const builtin = AGENT_GROUPS.find((g) => g.id === groupId);
  if (!builtin) return { ok: false, error: "group_not_found" };

  const store = await ensureOverrides();
  store.builtin[groupId] = {
    ...store.builtin[groupId],
    memberOrder: orderedMemberIds,
  };
  await saveOverrides(store);
  return { ok: true };
}

export async function applyBuiltinMemberOrder<T extends { id: string }>(
  groupId: string,
  members: T[],
): Promise<T[]> {
  const store = await ensureOverrides();
  const ov = store.builtin[groupId];
  if (!ov?.memberOrder?.length) {
    if (ov?.removedMemberIds?.length) {
      return members.filter((m) => !ov.removedMemberIds!.includes(m.id));
    }
    return members;
  }
  const map = new Map(members.map((m) => [m.id, m]));
  const ordered: T[] = [];
  for (const id of ov.memberOrder) {
    const m = map.get(id);
    if (m) ordered.push(m);
  }
  for (const m of members) {
    if (!ordered.some((o) => o.id === m.id)) ordered.push(m);
  }
  const removed = new Set(ov.removedMemberIds ?? []);
  return ordered.filter((m) => !removed.has(m.id));
}

export async function listSalasForOrchestrator() {
  const builtins = AGENT_GROUPS.map((g) => ({
    id: g.id,
    name: g.name,
    blurb: g.blurb,
    builtin: true,
    members: g.members.map((m) => ({ id: m.id, name: m.name, mode: m.mode })),
  }));
  const users = await listUserGroups();
  const custom = users
    .filter((g) => g.status !== "archived")
    .map((g) => ({
      id: g.id,
      name: g.name,
      blurb: g.blurb,
      builtin: false,
      members: g.members.map((m) => ({
        id: m.id,
        name: m.name,
        mode: m.mode,
        sourceId: m.sourceId,
      })),
    }));
  return [...custom, ...builtins];
}
