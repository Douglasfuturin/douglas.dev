import { getPersonaForSeedKey } from "./persona-seed";
import type { RegistryAgent } from "./types";

/** Agentes iniciais (editáveis/removíveis como qualquer outro). */
export const SEED_AGENT_DEFS: Array<{
  seedKey: string;
  name: string;
  role: string;
  color: string;
  avatar: string;
  runtimeMode: RegistryAgent["runtimeMode"];
  toolkit: RegistryAgent["toolkit"];
  inputs: string[];
  outputs: string[];
}> = [
  {
    seedKey: "radar",
    name: "Radar de Pesquisa",
    role: "Pesquisa tendências e briefing de IA, automação e marketing",
    color: "#5B9DFF",
    avatar: "RD",
    runtimeMode: "radar",
    toolkit: "radar",
    inputs: ["tema opcional", "mercado", "profundidade"],
    outputs: ["briefing ranqueado", "fontes", "cards para aprovação"],
  },
  {
    seedKey: "roteirista",
    name: "Roteirista",
    role: "Roteiro de Reels ~60s ou copy de carrossel a partir do briefing",
    color: "#4F8CFF",
    avatar: "RT",
    runtimeMode: "roteiro",
    toolkit: "roteiro",
    inputs: ["briefing", "formato", "tom"],
    outputs: ["roteiro", "hooks", "CTA"],
  },
  {
    seedKey: "arte-twitter",
    name: "Diretor de Arte Twitter",
    role: "Peças visuais estilo X/Twitter",
    color: "#3B82F6",
    avatar: "TW",
    runtimeMode: "arte-twitter",
    toolkit: "arte",
    inputs: ["roteiro", "formato", "notas de marca"],
    outputs: ["brief visual", "prompts de imagem"],
  },
  {
    seedKey: "arte-realista",
    name: "Diretor de Arte Realista",
    role: "Carrosséis Antes/Depois fotorealistas",
    color: "#60A5FA",
    avatar: "AR",
    runtimeMode: "arte-realista",
    toolkit: "arte",
    inputs: ["roteiro", "slides", "referências"],
    outputs: ["prompts fotorealistas", "ordem dos slides"],
  },
  {
    seedKey: "editor-reels",
    name: "Editor Reels Animação/Realismo",
    role: "Reels 9:16 — corte, ritmo e legendas",
    color: "#F87171",
    avatar: "ER",
    runtimeMode: "editor-reels",
    toolkit: "video",
    inputs: ["roteiro", "takes", "mídia bruta"],
    outputs: ["timeline", "render", "legendas"],
  },
  {
    seedKey: "editor-video",
    name: "Editor Reels Pessoal",
    role: "Recebe vídeo e devolve editado",
    color: "#34D399",
    avatar: "EV",
    runtimeMode: "video",
    toolkit: "video",
    inputs: ["upload de vídeo", "brief", "estilo"],
    outputs: ["vídeo final", "log de edição"],
  },
  {
    seedKey: "publicador",
    name: "Publicador",
    role: "Agenda e publica conteúdo pronto nas redes",
    color: "#A3E635",
    avatar: "PB",
    runtimeMode: "central",
    toolkit: "central",
    inputs: ["item do pipeline", "rede", "horário"],
    outputs: ["post agendado", "confirmação de publicação"],
  },
];

export function buildSeedAgents(now: string): RegistryAgent[] {
  return SEED_AGENT_DEFS.map((def) => ({
    id: `reg_${def.seedKey}`,
    name: def.name,
    avatar: def.avatar,
    color: def.color,
    role: def.role,
    systemPrompt: getPersonaForSeedKey(def.seedKey),
    model: "multi" as const,
    toolkit: def.toolkit,
    allowedTools: [],
    inputs: def.inputs,
    outputs: def.outputs,
    status: "active" as const,
    version: 1,
    runtimeMode: def.runtimeMode,
    seedKey: def.seedKey,
    createdAt: now,
    updatedAt: now,
  }));
}
