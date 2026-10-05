import type { MemberMode } from "./groups";

export const OPERATIONS = [
  "ideacao",
  "script",
  "visual",
  "video",
  "publicacao",
  "times",
  "sistema",
] as const;

export type OperationId = (typeof OPERATIONS)[number];

export const OPERATION_LABELS: Record<OperationId, string> = {
  ideacao: "Ideação",
  script: "Roteiro",
  visual: "Visual",
  video: "Vídeo",
  publicacao: "Publicação",
  times: "Times de agentes",
  sistema: "Sistema",
};

export const OPERATION_BLURBS: Record<OperationId, string> = {
  ideacao: "Radar, GitHub Scout e descoberta de temas",
  script: "Roteiros Reels 60s e guiones",
  visual: "Carrosséis, arte Twitter e capas",
  video: "Edição, skills Ninja e EDVD",
  publicacao: "Pipeline CRM, fila social e packs",
  times: "Grupos que conversam e fecham o fluxo",
  sistema: "Agentes custom, kits e orquestração",
};

export type CatalogAgentId =
  | "orquestrador"
  | "radar"
  | "roteirista"
  | "arte-twitter"
  | "arte-realista"
  | "bit"
  | "roteirista-pessoal"
  | "editor-reels"
  | "editor-video"
  | "radar-github"
  | "youtube-es"
  | "carrossel-es"
  | "capas-es"
  | "roteirista-es";

export type CatalogAgent = {
  id: CatalogAgentId;
  name: string;
  mode: MemberMode | "bit";
  role: string;
  color: string;
  icon: "cloud" | "square" | "triangle" | "circle" | "hex" | "drop" | "play";
  operation: OperationId;
};

export type GroupMemberRef = {
  /** Unique slot id inside the group */
  id: string;
  /** builtin catalog id or custom agent id */
  sourceId: string;
  kind: "builtin" | "custom";
  name: string;
  role: string;
  mode: string;
  color: string;
  icon: CatalogAgent["icon"];
  isOrchestrator: boolean;
  customAgentId?: string;
};

export type UserAgentGroup = {
  id: string;
  name: string;
  blurb: string;
  maxMembers: number;
  operation: OperationId;
  members: GroupMemberRef[];
  workflow: string[];
  orchestratorMemberId: string;
  createdAt: string;
  updatedAt: string;
};

export type AgentGroupStore = {
  version: 1;
  groups: UserAgentGroup[];
};

export type ResolvedGroupMember = {
  id: string;
  name: string;
  mode: string;
  role: string;
  color: string;
  icon: CatalogAgent["icon"];
  isOrchestrator?: boolean;
  customAgentId?: string;
  sourceId?: string;
  kind?: "builtin" | "custom";
};

export type ResolvedAgentGroup = {
  id: string;
  name: string;
  blurb: string;
  maxMembers: number;
  members: ResolvedGroupMember[];
  workflow: string[];
  operation?: OperationId;
  orchestratorMemberId?: string;
  builtin: boolean;
};
