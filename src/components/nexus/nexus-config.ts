import type { ReactNode } from "react";
import { NEXUS_TOOLS } from "./nexus-tools";

export type NexusNavItem = {
  href: string;
  label: string;
  icon: NexusIconName;
  match?: string[];
  soon?: boolean;
};

export type NexusIconName =
  | "overview"
  | "agents"
  | "orchestrations"
  | "activity"
  | "studio"
  | "editor"
  | "kits"
  | "pipeline"
  | "plus"
  | "tools";

export const NEXUS_MAIN_NAV: NexusNavItem[] = [
  { href: "/dashboard", label: "Visão geral", icon: "overview", match: ["/dashboard"] },
  { href: "/agentes", label: "Agentes", icon: "agents", match: ["/agentes"] },
  { href: "/grupos", label: "Orquestrações", icon: "orchestrations", match: ["/grupos"] },
  { href: "/central", label: "Atividade", icon: "activity", match: ["/central"] },
];

/** Ferramentas: hub + 4 módulos + orquestrador. */
export const NEXUS_TOOLS_NAV: NexusNavItem[] = [
  {
    href: "/ferramentas",
    label: "Todas",
    icon: "tools",
    match: ["/ferramentas"],
  },
  ...NEXUS_TOOLS.map((t) => ({
    href: t.href,
    label: t.label,
    icon: t.icon,
    match: t.match,
  })),
  { href: "/app", label: "Orquestrador", icon: "plus", match: ["/app"] },
];

export const NEXUS_RECENT_CHATS = [
  {
    href: "/app?q=Orquestra%20campanha%20Q4",
    title: "Estratégia de campanha Q4",
    agent: "Orquestrador",
    when: "Agora",
  },
  {
    href: "/app?mode=radar",
    title: "Briefing do dia",
    agent: "Radar",
    when: "18 min",
  },
  {
    href: "/ferramentas/studio?mode=roteiro",
    title: "Roteiro Reels 60s",
    agent: "Roteirista",
    when: "2 h",
  },
] as const;

export function isNexusActive(pathname: string, item: NexusNavItem) {
  // Hub /ferramentas: active only on exact path (not child modules)
  if (item.href === "/ferramentas") {
    return pathname === "/ferramentas";
  }
  if (item.match) {
    return item.match.some(
      (m) => pathname === m || pathname.startsWith(`${m}/`),
    );
  }
  const base = item.href.split("?")[0];
  return pathname === base || pathname.startsWith(`${base}/`);
}

export type NexusShellProps = {
  children: ReactNode;
  variant?: "app" | "chat" | "bare";
  title?: string;
  subtitle?: string;
  actions?: ReactNode;
  hideHeader?: boolean;
};
