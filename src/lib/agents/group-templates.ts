import type { OperationId } from "./group-types";

export type GroupTemplate = {
  id: string;
  name: string;
  blurb: string;
  operation: OperationId;
  memberSourceIds: string[];
  workflow: string[];
};

/** Modelos com pipeline + membros (Orquestrador é adicionado automaticamente na criação). */
export const GROUP_TEMPLATES: GroupTemplate[] = [
  {
    id: "pipeline-imagem",
    name: "Pipeline Imagem (Radar → Arte)",
    blurb:
      "Briefing diário, roteiro de carrossel, artes Twitter e carrossel realista Douglas Dev.",
    operation: "visual",
    memberSourceIds: [
      "radar",
      "roteirista",
      "arte-twitter",
      "arte-realista",
    ],
    workflow: [
      "1. Radar entrega briefing e pede aprovação de tendências",
      "2. Roteirista escreve copy do carrossel / Reels",
      "3. Diretor de Arte Twitter gera peças para X",
      "4. Diretor de Arte Realista fecha Antes/Depois fotorealista",
      "5. Orquestrador revisa handoffs e salva na Central",
    ],
  },
  {
    id: "pipeline-video",
    name: "Pipeline Vídeo (Radar → Editor)",
    blurb:
      "Temas fortes, script Reels 60s, edição animada/realista e upload pessoal editado.",
    operation: "video",
    memberSourceIds: [
      "radar",
      "roteirista",
      "editor-reels",
      "editor-video",
    ],
    workflow: [
      "1. Radar seleciona temas fortes para vídeo",
      "2. Roteirista entrega script Reels ~60s",
      "3. Editor Reels corta 9:16 com ritmo e legendas",
      "4. Editor Pessoal recebe upload e devolve MP4 pronto",
      "5. Orquestrador coordena fila e publicação",
    ],
  },
  {
    id: "pipeline-espanha",
    name: "Conteúdo Espanha (ES)",
    blurb:
      "Mercado espanhol: roteiro ES, carrossel, YouTube, capas e editor de vídeo ES.",
    operation: "publicacao",
    memberSourceIds: [
      "roteirista-es",
      "carrossel-es",
      "youtube-es",
      "capas-es",
      "editor-video",
    ],
    workflow: [
      "1. Roteirista ES adapta tema para mercado da Espanha",
      "2. Carrossel ES monta sequência visual",
      "3. YouTube ES prepara longo/shorts",
      "4. Capas e miniaturas para redes",
      "5. Editor de vídeo ES finaliza entrega",
    ],
  },
  {
    id: "scout-pack",
    name: "Scout → Reels → Notion",
    blurb: "GitHub Scout, roteiro hype 60s e guia Notion do melhor repo.",
    operation: "ideacao",
    memberSourceIds: ["radar-github", "roteirista"],
    workflow: [
      "1. Radar GitHub ranqueia repos open-source",
      "2. Roteirista gera Reels 60s sobre o vencedor",
      "3. Orquestrador dispara pack Notion (modo pipeline)",
    ],
  },
];

export function getGroupTemplate(id: string): GroupTemplate | undefined {
  return GROUP_TEMPLATES.find((t) => t.id === id);
}
