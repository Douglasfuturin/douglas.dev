import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import type { ActionLogStore, OrchestratorAction } from "./types";

const DATA_DIR = path.join(process.cwd(), "data", "agents");
const LOG_PATH = path.join(DATA_DIR, "orchestrator-actions.json");

function nowIso() {
  return new Date().toISOString();
}

function newId() {
  return `act_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}

async function ensureLog(): Promise<ActionLogStore> {
  await mkdir(DATA_DIR, { recursive: true });
  try {
    const raw = await readFile(LOG_PATH, "utf8");
    const parsed = JSON.parse(raw) as ActionLogStore;
    if (!parsed.actions) parsed.actions = [];
    if (!parsed.undoStack) parsed.undoStack = [];
    return parsed;
  } catch {
    const store: ActionLogStore = { version: 1, actions: [], undoStack: [] };
    await writeFile(LOG_PATH, JSON.stringify(store, null, 2), "utf8");
    return store;
  }
}

async function saveLog(store: ActionLogStore) {
  await mkdir(DATA_DIR, { recursive: true });
  await writeFile(LOG_PATH, JSON.stringify(store, null, 2), "utf8");
}

export async function logOrchestratorAction(
  input: Omit<OrchestratorAction, "id" | "createdAt">,
): Promise<OrchestratorAction> {
  const store = await ensureLog();
  const action: OrchestratorAction = {
    id: newId(),
    createdAt: nowIso(),
    ...input,
  };
  store.actions.unshift(action);
  store.actions = store.actions.slice(0, 200);
  if (action.undoable && action.undoPayload) {
    store.undoStack.unshift(action.id);
    store.undoStack = store.undoStack.slice(0, 50);
  }
  await saveLog(store);
  return action;
}

export async function listOrchestratorActions(limit = 40) {
  const store = await ensureLog();
  return store.actions.slice(0, limit);
}

export async function undoLastOrchestratorAction(): Promise<{
  ok: boolean;
  error?: string;
  label?: string;
}> {
  const store = await ensureLog();
  const actionId = store.undoStack[0];
  if (!actionId) return { ok: false, error: "nothing_to_undo" };
  const action = store.actions.find((a) => a.id === actionId);
  if (!action?.undoPayload) return { ok: false, error: "undo_payload_missing" };

  const payload = action.undoPayload;

  if (payload.type === "restore_agent" && typeof payload.agentId === "string") {
    const { updateRegistryAgent } = await import("./store");
    const patch = payload.patch as {
      systemPrompt?: string;
      role?: string;
      name?: string;
    };
    await updateRegistryAgent(payload.agentId, patch);
  }

  if (payload.type === "restore_agent_status" && typeof payload.agentId === "string") {
    const { setRegistryAgentStatus } = await import("./store");
    await setRegistryAgentStatus(
      payload.agentId,
      payload.status as "active" | "paused" | "archived",
    );
  }

  store.undoStack = store.undoStack.filter((id) => id !== actionId);
  await saveLog(store);
  await logOrchestratorAction({
    kind: "undo",
    label: `Desfez: ${action.label}`,
    undoable: false,
  });
  return { ok: true, label: action.label };
}
