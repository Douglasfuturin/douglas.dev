import type { CatalogAgent, CatalogAgentId } from "./group-types";

export const AGENT_CATALOG: CatalogAgent[] = [
  {
    id: "orquestrador",
    name: "Orquestrador",
    mode: "bit",
    role: "Agente principal — orquestra o time, define handoffs e fecha o fluxo",
    color: "#F26522",
    icon: "circle",
    operation: "sistema",
  },
  {
    id: "bit",
    name: "Bit",
    mode: "bit",
    role: "Coordena o grupo, resume decisões e puxa o próximo passo",
    color: "#E5E7EB",
    icon: "circle",
    operation: "times",
  },
  {
    id: "radar",
    name: "Radar de Pesquisa",
    mode: "radar",
    role: "Pesquisa tendências e briefing de IA, automação e marketing",
    color: "#5B9DFF",
    icon: "cloud",
    operation: "ideacao",
  },
  {
    id: "radar-github",
    name: "Radar GitHub",
    mode: "github",
    role: "Busca e ranqueia repos + roteiro 60s",
    color: "#FB923C",
    icon: "drop",
    operation: "ideacao",
  },
  {
    id: "roteirista",
    name: "Roteirista",
    mode: "roteiro",
    role: "Roteiro de Reels ~60s sobre tendência ou repo",
    color: "#4F8CFF",
    icon: "square",
    operation: "script",
  },
  {
    id: "roteirista-pessoal",
    name: "Roteirista Pessoal",
    mode: "roteiro-pessoal",
    role: "Roteiro em 1ª pessoa, tom pessoal/autoridade",
    color: "#A78BFA",
    icon: "circle",
    operation: "script",
  },
  {
    id: "roteirista-es",
    name: "Roteirista ES",
    mode: "roteiro",
    role: "Roteiros de Reels/YouTube em espanhol da Espanha",
    color: "#4F8CFF",
    icon: "square",
    operation: "script",
  },
  {
    id: "arte-twitter",
    name: "Diretor de Arte Twitter",
    mode: "arte-twitter",
    role: "Peças visuais estilo X/Twitter",
    color: "#3B82F6",
    icon: "square",
    operation: "visual",
  },
  {
    id: "arte-realista",
    name: "Diretor de Arte Realista",
    mode: "arte-realista",
    role: "Carrosséis Antes/Depois fotorealistas Douglas Dev",
    color: "#60A5FA",
    icon: "triangle",
    operation: "visual",
  },
  {
    id: "carrossel-es",
    name: "Carrossel ES",
    mode: "carrossel",
    role: "Vídeos e peças para carrossel Instagram·LinkedIn",
    color: "#F472B6",
    icon: "square",
    operation: "visual",
  },
  {
    id: "capas-es",
    name: "Capas e Miniaturas",
    mode: "capas",
    role: "Capas YouTube, covers de Reels e thumbnails",
    color: "#FBBF24",
    icon: "triangle",
    operation: "visual",
  },
  {
    id: "editor-reels",
    name: "Editor Reels Animação/Realismo",
    mode: "editor-reels",
    role: "Reels com animação e realismo — corte 9:16, ritmo e legendas",
    color: "#F87171",
    icon: "hex",
    operation: "video",
  },
  {
    id: "editor-video",
    name: "Editor Reels Pessoal",
    mode: "video",
    role: "Você envia o vídeo — ele devolve pronto, já editado",
    color: "#34D399",
    icon: "play",
    operation: "video",
  },
  {
    id: "youtube-es",
    name: "YouTube ES",
    mode: "youtube",
    role: "Pack YouTube: roteiro, títulos, SEO e miniatura",
    color: "#EF4444",
    icon: "play",
    operation: "video",
  },
];

export function getCatalogAgent(id: string): CatalogAgent | null {
  return AGENT_CATALOG.find((a) => a.id === id) ?? null;
}

export function listCatalogAgents(): CatalogAgent[] {
  return AGENT_CATALOG;
}

export function isCatalogAgentId(id: string): id is CatalogAgentId {
  return AGENT_CATALOG.some((a) => a.id === id);
}
