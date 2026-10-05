import type { ToolkitPreset } from "../custom-types";

export type AgentStatus = "active" | "paused" | "archived";

export type AgentModelId = "chat" | "multi";

export type RegistryAgent = {
  id: string;
  name: string;
  avatar: string;
  color: string;
  role: string;
  systemPrompt: string;
  model: AgentModelId;
  toolkit: ToolkitPreset;
  allowedTools: string[];
  inputs: string[];
  outputs: string[];
  status: AgentStatus;
  version: number;
  /** Runtime delegation mode (catalog specialist). */
  runtimeMode?: string;
  seedKey?: string;
  createdAt: string;
  updatedAt: string;
};

export type AgentPromptVersion = {
  version: number;
  systemPrompt: string;
  summary: string;
  changedAt: string;
};

export type AgentProposalKind =
  | "create_agent"
  | "update_agent"
  | "create_room"
  | "update_room";

export type AgentProposal = {
  id: string;
  kind: AgentProposalKind;
  preview: Record<string, unknown>;
  payload: Record<string, unknown>;
  createdAt: string;
  expiresAt?: string;
};

export type OrchestratorActionKind =
  | "create_agent"
  | "update_agent"
  | "archive_agent"
  | "pause_agent"
  | "create_room"
  | "update_room"
  | "add_member"
  | "remove_member"
  | "reorder_pipeline"
  | "undo";

export type OrchestratorAction = {
  id: string;
  kind: OrchestratorActionKind;
  label: string;
  createdAt: string;
  undoable: boolean;
  undoPayload?: Record<string, unknown>;
};

export type RegistryStore = {
  version: 2;
  agents: RegistryAgent[];
  proposals: AgentProposal[];
};

export type AgentVersionStore = {
  version: 1;
  byAgent: Record<string, AgentPromptVersion[]>;
};

export type ActionLogStore = {
  version: 1;
  actions: OrchestratorAction[];
  undoStack: string[];
};

export type AgentExecutionRecord = {
  id: string;
  agentId: string;
  agentName: string;
  inputSummary: string;
  outputSummary: string;
  durationMs: number;
  costEstimateUsd?: number;
  createdAt: string;
};

export type ExecutionStore = {
  version: 1;
  runs: AgentExecutionRecord[];
};
