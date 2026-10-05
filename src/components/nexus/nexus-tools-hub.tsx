"use client";

import Link from "next/link";
import { NexusIcon } from "./nexus-icons";
import { NEXUS_TOOLS } from "./nexus-tools";

const FLOW = [
  { step: "01", title: "Studio", body: "Defina modo e agente" },
  { step: "02", title: "Skills", body: "Rode kits especializados" },
  { step: "03", title: "Editor", body: "Corte e renderize o reel" },
  { step: "04", title: "Pack", body: "Feche Scout → Notion" },
] as const;

export function NexusToolsHub() {
  return (
    <div className="space-y-10 animate-nexus-rise">
      <section className="relative overflow-hidden rounded-2xl border border-[color:var(--border)] bg-[color:var(--card)] px-6 py-8 md:px-8 md:py-10">
        <div className="nexus-hero-glow pointer-events-none absolute inset-0" aria-hidden />
        <div className="relative z-10 max-w-2xl">
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--primary)]">
            Workspace · Ferramentas
          </p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight text-[color:var(--foreground)] md:text-4xl">
            Studio, Skills, Editor e Pack
          </h1>
          <p className="mt-3 text-base text-[color:var(--muted-foreground)]">
            Quatro módulos no mesmo sistema operacional — identidade Nexus, um fluxo
            contínuo do briefing ao vídeo e ao pack Notion.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/ferramentas/studio" className="nexus-btn-primary">
              Abrir Studio
            </Link>
            <Link href="/app" className="nexus-btn-ghost">
              Orquestrador
            </Link>
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2">
        {NEXUS_TOOLS.map((tool) => (
          <Link
            key={tool.id}
            href={tool.href}
            className="nexus-tool-card group"
          >
            <div className="flex items-start justify-between gap-3">
              <span className="flex size-11 items-center justify-center rounded-xl bg-[color:var(--primary)]/15 text-[color:var(--primary)]">
                <NexusIcon name={tool.icon} className="size-5" />
              </span>
              <span className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[color:var(--muted-foreground)]">
                {tool.short}
              </span>
            </div>
            <h2 className="mt-4 text-lg font-semibold text-[color:var(--foreground)] group-hover:text-[color:var(--primary)]">
              {tool.label}
            </h2>
            <p className="mt-2 text-sm leading-relaxed text-[color:var(--muted-foreground)]">
              {tool.blurb}
            </p>
            <span className="mt-4 inline-flex text-sm font-semibold text-[color:var(--primary)]">
              {tool.cta} →
            </span>
          </Link>
        ))}
      </section>

      <section className="nexus-panel">
        <h2 className="text-lg font-semibold text-[color:var(--foreground)]">
          Fluxo sugerido
        </h2>
        <p className="mt-1 text-sm text-[color:var(--muted-foreground)]">
          Use na ordem ou pule direto para o módulo que precisa.
        </p>
        <ol className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {FLOW.map((item) => (
            <li
              key={item.step}
              className="rounded-xl border border-[color:var(--border)] bg-[color:var(--background)]/50 px-4 py-3"
            >
              <p className="font-mono text-[10px] text-[color:var(--primary)]">
                {item.step}
              </p>
              <p className="mt-1 text-sm font-semibold text-[color:var(--foreground)]">
                {item.title}
              </p>
              <p className="mt-0.5 text-xs text-[color:var(--muted-foreground)]">
                {item.body}
              </p>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}
