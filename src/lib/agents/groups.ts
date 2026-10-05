/**
 * Estruturas de grupos de agentes (espelha chats em grupo do Grok).
 * Máx. 6 membros por grupo.
 */

export type AgentMemberId =
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

export type AgentGroupId =
  | "conteudo-dev"
  | "conteudo-dev-video"
  | "conteudos-espanha";

/** Modo do orquestrador associado ao membro. */
export type MemberMode =
  | "radar"
  | "roteiro"
  | "roteiro-pessoal"
  | "arte-twitter"
  | "arte-realista"
  | "bit"
  | "editor-reels"
  | "video"
  | "github"
  | "youtube"
  | "carrossel"
  | "capas";

export type AgentMember = {
  id: AgentMemberId;
  name: string;
  mode: MemberMode;
  role: string;
  color: string;
  icon: "cloud" | "square" | "triangle" | "circle" | "hex" | "drop" | "play";
};

export type AgentGroup = {
  id: AgentGroupId;
  name: string;
  blurb: string;
  maxMembers: number;
  members: AgentMember[];
  workflow: string[];
};

export const AGENT_GROUPS: AgentGroup[] = [
  {
    id: "conteudo-dev",
    name: "Conteúdo Dev",
    blurb:
      "Radar → roteiro → direção de arte (Twitter + realista). Bit coordena; Roteirista Pessoal refina o tom.",
    maxMembers: 6,
    members: [
      {
        id: "radar",
        name: "Radar de Tendências",
        mode: "radar",
        role: "Briefing diário de IA, automação e marketing",
        color: "#5B9DFF",
        icon: "cloud",
      },
      {
        id: "roteirista",
        name: "Roteirista",
        mode: "roteiro",
        role: "Roteiro de Reels ~60s sobre tendência ou repo",
        color: "#4F8CFF",
        icon: "square",
      },
      {
        id: "arte-twitter",
        name: "Diretor de Arte Twitter",
        mode: "arte-twitter",
        role: "Peças visuais estilo X/Twitter (carrossel, capa, meme tech)",
        color: "#3B82F6",
        icon: "square",
      },
      {
        id: "arte-realista",
        name: "Diretor de Arte Realista",
        mode: "arte-realista",
        role: "Direção visual fotorealista / cinematográfica",
        color: "#60A5FA",
        icon: "triangle",
      },
      {
        id: "bit",
        name: "Bit",
        mode: "bit",
        role: "Coordena o grupo, resume decisões e puxa o próximo passo",
        color: "#E5E7EB",
        icon: "circle",
      },
      {
        id: "roteirista-pessoal",
        name: "Roteirista Pessoal",
        mode: "roteiro-pessoal",
        role: "Roteiro em 1ª pessoa, tom pessoal/autoridade",
        color: "#A78BFA",
        icon: "circle",
      },
    ],
    workflow: [
      "Radar entrega briefing e pede aprovação",
      "Roteirista (ou Pessoal) cria o script 60s",
      "Diretor de Arte Twitter gera peças para X",
      "Diretor de Arte Realista gera capa/cenas realistas",
      "Bit fecha o pacote e lista próximos passos",
    ],
  },
  {
    id: "conteudo-dev-video",
    name: "Conteúdo Dev Vídeo",
    blurb:
      "Do roteiro à edição: Reels realista + editor pessoal + Radar GitHub. Bit coordena.",
    maxMembers: 6,
    members: [
      {
        id: "roteirista-pessoal",
        name: "Roteirista Pessoal",
        mode: "roteiro-pessoal",
        role: "Roteiro pessoal para vídeo/Reels",
        color: "#A78BFA",
        icon: "circle",
      },
      {
        id: "editor-reels",
        name: "Editor Reels Realista",
        mode: "editor-reels",
        role: "Edição vertical 9:16, corte, legenda, ritmo de Reels",
        color: "#F87171",
        icon: "hex",
      },
      {
        id: "editor-video",
        name: "Editor Vídeo Pessoal",
        mode: "video",
        role: "Pipeline EDVD + skills do sistema (auto edit)",
        color: "#34D399",
        icon: "circle",
      },
      {
        id: "bit",
        name: "Bit",
        mode: "bit",
        role: "Coordena o grupo de vídeo e handoffs",
        color: "#E5E7EB",
        icon: "circle",
      },
      {
        id: "radar-github",
        name: "Radar GitHub",
        mode: "github",
        role: "Busca e ranqueia repos para conteúdo",
        color: "#FB923C",
        icon: "drop",
      },
    ],
    workflow: [
      "Radar GitHub escolhe o repo/tema",
      "Roteirista Pessoal escreve o script",
      "Editor Reels Realista monta o corte 9:16",
      "Editor Vídeo Pessoal renderiza com skills do sistema (EDVD/HyperFrames)",
      "Bit entrega checklist final",
    ],
  },
  {
    id: "conteudos-espanha",
    name: "Contenidos España",
    blurb:
      "Sala en español (España): editor de vídeo, carrusel, YouTube, guionista y portadas/thumbnails.",
    maxMembers: 6,
    members: [
      {
        id: "editor-video",
        name: "Editor de Vídeo",
        mode: "video",
        role: "Edición automática con skills del sistema (EDVD / HyperFrames)",
        color: "#34D399",
        icon: "play",
      },
      {
        id: "carrossel-es",
        name: "Carrusel",
        mode: "carrossel",
        role: "Vídeos/piezas para carrusel Instagram·LinkedIn",
        color: "#F472B6",
        icon: "square",
      },
      {
        id: "youtube-es",
        name: "YouTube",
        mode: "youtube",
        role: "Pack YouTube: guion, títulos, SEO, miniatura",
        color: "#EF4444",
        icon: "play",
      },
      {
        id: "roteirista-es",
        name: "Guionista",
        mode: "roteiro",
        role: "Guiones Reels/YouTube en español de España",
        color: "#4F8CFF",
        icon: "square",
      },
      {
        id: "capas-es",
        name: "Capas y Thumbnails",
        mode: "capas",
        role: "Portadas YouTube, covers Reels y thumbnails",
        color: "#FBBF24",
        icon: "triangle",
      },
      {
        id: "bit",
        name: "Bit",
        mode: "bit",
        role: "Coordina el grupo y los handoffs",
        color: "#E5E7EB",
        icon: "circle",
      },
    ],
    workflow: [
      "Guionista define el ángulo en español",
      "YouTube o Carrusel monta el formato",
      "Capas y Thumbnails genera portadas",
      "Editor de Vídeo edita/renderiza con skills del sistema",
      "Bit cierra el paquete",
    ],
  },
];

export function getAgentGroup(id: string | undefined | null): AgentGroup | null {
  if (!id) return null;
  return AGENT_GROUPS.find((g) => g.id === id) || null;
}

export function getGroupMember(
  groupId: string | undefined | null,
  memberId: string | undefined | null,
): AgentMember | null {
  const group = getAgentGroup(groupId);
  if (!group || !memberId) return null;
  return group.members.find((m) => m.id === memberId) || null;
}

export function listAgentGroups(): AgentGroup[] {
  return AGENT_GROUPS;
}
