import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import type { AgentExecutionRecord, ExecutionStore } from "./types";

const DATA_DIR = path.join(process.cwd(), "data", "agents");
const EXEC_PATH = path.join(DATA_DIR, "executions.json");

function nowIso() {
  return new Date().toISOString();
}

function newId() {
  return `run_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}

async function ensureExecutions(): Promise<ExecutionStore> {
  await mkdir(DATA_DIR, { recursive: true });
  try {
    const raw = await readFile(EXEC_PATH, "utf8");
    return JSON.parse(raw) as ExecutionStore;
  } catch {
    const store: ExecutionStore = { version: 1, runs: [] };
    await writeFile(EXEC_PATH, JSON.stringify(store, null, 2), "utf8");
    return store;
  }
}

async function saveExecutions(store: ExecutionStore) {
  await writeFile(EXEC_PATH, JSON.stringify(store, null, 2), "utf8");
}

export async function recordAgentExecution(input: {
  agentId: string;
  agentName: string;
  inputSummary: string;
  outputSummary: string;
  durationMs: number;
  costEstimateUsd?: number;
}) {
  const store = await ensureExecutions();
  const row: AgentExecutionRecord = {
    id: newId(),
    createdAt: nowIso(),
    ...input,
  };
  store.runs.unshift(row);
  store.runs = store.runs.slice(0, 500);
  await saveExecutions(store);
  return row;
}

export async function listAgentExecutions(limit = 30) {
  const store = await ensureExecutions();
  return store.runs.slice(0, limit);
}
