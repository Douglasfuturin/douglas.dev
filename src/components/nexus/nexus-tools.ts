import type { NexusIconName } from "./nexus-config";

export type NexusToolId = "studio" | "editor" | "skills" | "pack";

export type NexusToolDef = {
  id: NexusToolId;
  href: string;
  label: string;
  short: string;
  blurb: string;
  icon: NexusIconName;
  match: string[];
  cta: string;
  accent: string;
};

/** Quatro módulos do workspace de ferramentas. */
export const NEXUS_TOOLS: NexusToolDef[] = [
  {
    id: "studio",
    href: "/ferramentas/studio",
    label: "Studio",
    short: "Agentes",
    blurb:
      "Sala avançada de agentes — radar, roteiro, artes, grupos e modos especializados.",
    icon: "studio",
    match: ["/ferramentas/studio", "/app/studio", "/studio"],
    cta: "Abrir Studio",
    accent: "from-[color-mix(in_oklab,var(--primary)_22%,transparent)]",
  },
  {
    id: "editor",
    href: "/ferramentas/editor",
    label: "Editor de vídeo",
    short: "Reels",
    blurb:
      "Timeline local 9:16, takes, legendas e render sem depender do chat.",
    icon: "editor",
    match: ["/ferramentas/editor", "/editor"],
    cta: "Abrir Editor",
    accent: "from-[color-mix(in_oklab,var(--primary)_18%,transparent)]",
  },
  {
    id: "skills",
    href: "/ferramentas/skills",
    label: "Skills",
    short: "Kits",
    blurb:
      "Biblioteca de Ninja Kits — instale, rode e entregue skills no workspace.",
    icon: "kits",
    match: ["/ferramentas/skills", "/kits"],
    cta: "Abrir Skills",
    accent: "from-[color-mix(in_oklab,var(--primary)_16%,transparent)]",
  },
  {
    id: "pack",
    href: "/ferramentas/pack",
    label: "Pack Scout",
    short: "Pack",
    blurb:
      "Pipeline Scout → Roteiro Reels 60s → Notion em uma tacada.",
    icon: "pipeline",
    match: ["/ferramentas/pack", "/pipeline"],
    cta: "Rodar Pack",
    accent: "from-[color-mix(in_oklab,var(--primary)_20%,transparent)]",
  },
];

export function getNexusTool(id: NexusToolId) {
  return NEXUS_TOOLS.find((t) => t.id === id)!;
}

export function matchNexusTool(pathname: string): NexusToolId | null {
  for (const tool of NEXUS_TOOLS) {
    if (tool.match.some((m) => pathname === m || pathname.startsWith(`${m}/`))) {
      return tool.id;
    }
  }
  return null;
}
