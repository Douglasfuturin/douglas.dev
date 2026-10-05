"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AGENT_GROUPS } from "@/lib/agents/groups";

type Stats = {
  total: number;
  queued: number;
  byStage: Record<string, number>;
};

const FIELD_AGENTS = [
  {
    name: "Orquestrador",
    role: "Coordenador",
    status: "Ativo",
    detail: "Delega pipelines Imagem e Vídeo",
    tone: "active" as const,
    href: "/app",
  },
  {
    name: "Radar",
    role: "Pesquisa",
    status: "Executando",
    detail: "Briefing diário de tendências",
    tone: "running" as const,
    href: "/app?mode=radar",
  },
  {
    name: "Roteirista",
    role: "Script",
    status: "Disponível",
    detail: "Reels ~60s e copy",
    tone: "idle" as const,
    href: "/app?mode=roteiro",
  },
  {
    name: "Editor Reels",
    role: "Vídeo",
    status: "Disponível",
    detail: "Corte 9:16 e render local",
    tone: "idle" as const,
    href: "/editor",
  },
];

function greeting() {
  const h = new Date().getHours();
  if (h < 12) return "Bom dia";
  if (h < 18) return "Boa tarde";
  return "Boa noite";
}

export function NexusOverview() {
  const [stats, setStats] = useState<Stats | null>(null);
  const groupCount = AGENT_GROUPS.length;

  useEffect(() => {
    fetch("/api/content")
      .then((r) => r.json())
      .then((data: { stats?: Stats }) => setStats(data.stats ?? null))
      .catch(() => undefined);
  }, []);

  const tasksDone = stats?.total ?? 0;
  const inQueue = stats?.queued ?? 0;
  const inProgress =
    (stats?.byStage?.script ?? 0) +
    (stats?.byStage?.visual ?? 0) +
    (stats?.byStage?.editing ?? 0);

  return (
    <div className="space-y-8 animate-nexus-rise">
      <section className="relative overflow-hidden rounded-2xl border border-[color:var(--border)] bg-[color:var(--card)] p-6 md:p-8">
        <div className="nexus-hero-glow pointer-events-none absolute inset-0" aria-hidden />
        <div className="relative z-10 max-w-2xl">
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--primary)]">
            Nexus OS · Central de comando
          </p>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight text-[color:var(--foreground)] md:text-4xl">
            {greeting()}, Douglas.
          </h2>
          <p className="mt-3 text-base text-[color:var(--muted-foreground)]">
            Sua equipe de agentes está pronta — orquestre conteúdo, vídeo e publicação
            em um só lugar.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/app" className="nexus-btn-primary">
              Iniciar missão
            </Link>
            <Link href="/central" className="nexus-btn-ghost">
              Ver atividade
            </Link>
          </div>
        </div>
      </section>

      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {[
          {
            label: "Agentes ativos",
            value: `${groupCount + 4}`,
            hint: "+2 hoje",
          },
          {
            label: "Itens no CRM",
            value: String(tasksDone),
            hint: "pipeline",
          },
          {
            label: "Em execução",
            value: String(inProgress || inQueue || 0),
            hint: "prioritárias",
          },
          {
            label: "Grupos",
            value: String(groupCount),
            hint: "orquestrações",
          },
        ].map((card) => (
          <article key={card.label} className="nexus-stat-card">
            <p className="text-[11px] font-medium uppercase tracking-[0.12em] text-[color:var(--muted-foreground)]">
              {card.label}
            </p>
            <p className="mt-2 text-3xl font-semibold tabular-nums text-[color:var(--foreground)]">
              {card.value}
            </p>
            <p className="mt-1 text-xs text-[color:var(--primary)]">{card.hint}</p>
          </article>
        ))}
      </section>

      <section className="space-y-4">
        <div className="flex items-end justify-between gap-3">
          <div>
            <h3 className="text-lg font-semibold text-[color:var(--foreground)]">
              Agentes em campo
            </h3>
            <p className="text-sm text-[color:var(--muted-foreground)]">
              Status da sua força de trabalho digital
            </p>
          </div>
          <Link href="/agentes" className="nexus-link text-sm">
            Ver todos
          </Link>
        </div>
        <div className="grid gap-3 md:grid-cols-2">
          {FIELD_AGENTS.map((agent) => (
            <Link key={agent.name} href={agent.href} className="nexus-agent-card group">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-[color:var(--foreground)] group-hover:text-[color:var(--primary)]">
                    {agent.name}
                  </p>
                  <p className="text-xs text-[color:var(--muted-foreground)]">{agent.role}</p>
                </div>
                <span className={`nexus-status nexus-status-${agent.tone}`}>
                  {agent.status}
                </span>
              </div>
              <p className="mt-3 text-sm text-[color:var(--muted-foreground)]">{agent.detail}</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
