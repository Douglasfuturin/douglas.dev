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
    name: "Conteúdo Dev — Imagem",
    blurb:
      "Pipeline visual: Radar de Pesquisa → Roteirista → Arte Twitter → Arte Realista.",
    maxMembers: 6,
    members: [
      {
        id: "radar",
        name: "Radar de Pesquisa",
        mode: "radar",
        role: "Pesquisa tendências e briefing de IA, automação e marketing",
        color: "#5B9DFF",
        icon: "cloud",
      },
      {
        id: "roteirista",
        name: "Roteirista",
        mode: "roteiro",
        role: "Transforma o briefing em roteiro / copy do carrossel",
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
        role: "Carrosséis Antes/Depois fotorealistas Douglas Dev",
        color: "#F26522",
        icon: "triangle",
      },
      {
        id: "bit",
        name: "Orquestrador",
        mode: "bit",
        role: "Coordena o fluxo imagem e fecha handoffs",
        color: "#E5E7EB",
        icon: "circle",
      },
    ],
    workflow: [
      "1. Radar de Pesquisa entrega briefing e pede aprovação",
      "2. Roteirista cria o roteiro / copy",
      "3. Diretor de Arte Twitter gera peças para X",
      "4. Diretor de Arte Realista fecha o carrossel Antes/Depois",
    ],
  },
  {
    id: "conteudo-dev-video",
    name: "Conteúdo Dev — Vídeo",
    blurb:
      "Pipeline de vídeo: Radar → Roteirista → Reels animado/realista → Reels pessoal (upload → editado).",
    maxMembers: 6,
    members: [
      {
        id: "radar",
        name: "Radar de Pesquisa",
        mode: "radar",
        role: "Pesquisa tendências e temas fortes para vídeo",
        color: "#5B9DFF",
        icon: "cloud",
      },
      {
        id: "roteirista",
        name: "Roteirista",
        mode: "roteiro",
        role: "Roteiro de Reels ~60s pronto para gravar/editar",
        color: "#4F8CFF",
        icon: "square",
      },
      {
        id: "editor-reels",
        name: "Editor Reels Animação/Realismo",
        mode: "editor-reels",
        role: "Reels com animação e realismo — corte 9:16, ritmo e legendas",
        color: "#F87171",
        icon: "hex",
      },
      {
        id: "editor-video",
        name: "Editor Reels Pessoal",
        mode: "video",
        role: "Você envia o vídeo — ele devolve pronto, já editado (animação/realismo)",
        color: "#34D399",
        icon: "play",
      },
      {
        id: "bit",
        name: "Orquestrador",
        mode: "bit",
        role: "Coordena o fluxo de vídeo e handoffs",
        color: "#E5E7EB",
        icon: "circle",
      },
    ],
    workflow: [
      "1. Radar de Pesquisa escolhe o tema",
      "2. Roteirista escreve o script 60s",
      "3. Editor Reels Animação/Realismo monta o corte",
      "4. Editor Reels Pessoal recebe seu upload e entrega o vídeo editado",
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
