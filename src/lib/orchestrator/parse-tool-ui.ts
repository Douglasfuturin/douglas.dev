/** Extrai eventos de UI a partir do output JSON das tools do orquestrador. */

export type ToolUiEvent =
  | {
      type: "agent_proposal";
      proposalId: string;
      kind: string;
      preview: Record<string, unknown>;
    }
  | { type: "registry_refresh" }
  | { type: "groups_refresh" }
  | { type: "action_log"; actions: unknown[] };

function readOutput(part: unknown): Record<string, unknown> | null {
  if (!part || typeof part !== "object") return null;
  const p = part as Record<string, unknown>;
  if (p.output && typeof p.output === "object") {
    return p.output as Record<string, unknown>;
  }
  if (p.result && typeof p.result === "object") {
    return p.result as Record<string, unknown>;
  }
  if (typeof p.state === "string" && p.state.includes("output") && p.output) {
    return p.output as Record<string, unknown>;
  }
  return null;
}

export function extractOrchestratorUiFromPart(part: unknown): ToolUiEvent | null {
  const out = readOutput(part);
  if (!out?.uiEvent || typeof out.uiEvent !== "object") return null;
  const ev = out.uiEvent as Record<string, unknown>;
  if (ev.type === "agent_proposal" && typeof ev.proposalId === "string") {
    return {
      type: "agent_proposal",
      proposalId: ev.proposalId,
      kind: String(ev.kind || "create_agent"),
      preview: (ev.preview as Record<string, unknown>) || {},
    };
  }
  if (ev.type === "registry_refresh") return { type: "registry_refresh" };
  if (ev.type === "groups_refresh") return { type: "groups_refresh" };
  if (ev.type === "action_log") {
    return { type: "action_log", actions: (ev.actions as unknown[]) || [] };
  }
  return null;
}
