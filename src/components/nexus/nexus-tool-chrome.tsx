"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { NexusIcon } from "./nexus-icons";
import {
  getNexusTool,
  matchNexusTool,
  NEXUS_TOOLS,
  type NexusToolId,
} from "./nexus-tools";

export function NexusToolChrome({
  toolId,
  children,
  actions,
  flush,
}: {
  toolId: NexusToolId;
  children: ReactNode;
  actions?: ReactNode;
  /** Full-bleed content (editor) without max-width padding. */
  flush?: boolean;
}) {
  const pathname = usePathname();
  const tool = getNexusTool(toolId);
  const activeId = matchNexusTool(pathname) ?? toolId;

  return (
    <div className="nexus-tool-workspace animate-nexus-rise">
      <div className="nexus-tool-switcher">
        <div className="min-w-0 flex-1">
          <p className="nexus-tool-kicker">Ferramentas · Nexus OS</p>
          <h1 className="text-xl font-semibold tracking-tight text-[color:var(--foreground)] md:text-2xl">
            {tool.label}
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-[color:var(--muted-foreground)]">
            {tool.blurb}
          </p>
        </div>
        {actions ? <div className="flex flex-wrap gap-2">{actions}</div> : null}
      </div>

      <nav className="nexus-tool-tabs" aria-label="Módulos de ferramentas">
        {NEXUS_TOOLS.map((t) => {
          const active = t.id === activeId;
          return (
            <Link
              key={t.id}
              href={t.href}
              data-active={active}
              className="nexus-tool-tab"
            >
              <NexusIcon name={t.icon} className="size-3.5 shrink-0" />
              <span className="hidden sm:inline">{t.label}</span>
              <span className="sm:hidden">{t.short}</span>
            </Link>
          );
        })}
      </nav>

      <div className={flush ? "nexus-tool-body-flush" : "nexus-tool-body"}>
        {children}
      </div>
    </div>
  );
}
