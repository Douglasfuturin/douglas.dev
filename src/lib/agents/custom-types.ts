export const TOOLKIT_PRESETS = [
  "chat",
  "research",
  "github",
  "radar",
  "roteiro",
  "arte",
  "video",
  "notion",
  "pipeline",
  "central",
  "espanha",
  "full",
] as const;

export type ToolkitPreset = (typeof TOOLKIT_PRESETS)[number];

export const TOOLKIT_LABELS: Record<ToolkitPreset, string> = {
  chat: "Chat + web/X/imagem",
  research: "Pesquisa multiagente",
  github: "GitHub Scout + Reels 60s",
  radar: "Radar de tendências",
  roteiro: "Roteirista",
  arte: "Direção de arte",
  video: "Editor de vídeo + skills",
  notion: "Notion Guide",
  pipeline: "Pack Scout→Reels→Notion",
  central: "Central / pipeline CRM",
  espanha: "YouTube / carrusel / capas ES",
  full: "Todas as tools",
};

export type CustomAgent = {
  id: string;
  name: string;
  role: string;
  instructions: string;
  toolkit: ToolkitPreset;
  color: string;
  avatar: string;
  temperature?: number;
  createdAt: string;
  updatedAt: string;
};

export type CustomAgentStore = {
  version: 1;
  agents: CustomAgent[];
};

export const AGENT_COLORS = [
  "#f26522",
  "#ff6a1a",
  "#ffffff",
  "#a8a8a8",
  "#5eead4",
  "#F5C84C",
  "#FB7185",
  "#34D399",
] as const;
