"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import type { ContentItem, PublishJob } from "@/lib/content/types";
import { STAGE_LABELS } from "@/lib/content/types";
import { AGENT_GROUPS, type AgentGroup, type AgentMember } from "@/lib/agents/groups";
import { GroupsManager } from "@/components/crm/groups-manager";

/** Pipeline steps shown on dashboard (excludes orchestrator from the numbered flow). */
function pipelineMembers(group: AgentGroup): AgentMember[] {
  return group.members.filter((m) => m.mode !== "bit" && m.id !== "bit");
}

const PIPELINE_GROUPS = AGENT_GROUPS.filter(
  (g) => g.id === "conteudo-dev" || g.id === "conteudo-dev-video",
);

function PipelineGroupCard({
  group,
  accent,
}: {
  group: AgentGroup;
  accent: string;
}) {
  const steps = pipelineMembers(group);

  return (
    <section className="crm-panel !p-0 overflow-hidden animate-fase-rise">
      <div
        className="border-b border-white/10 px-5 py-4 sm:px-6"
        style={{
          background: `linear-gradient(135deg, ${accent}22 0%, transparent 55%)`,
        }}
      >
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[color:var(--primary)]">
              Pipeline · {steps.length} etapas
            </p>
            <h3 className="font-display mt-1 text-2xl font-bold text-white">
              {group.name}
            </h3>
            <p className="mt-1 max-w-xl text-sm text-white/50">{group.blurb}</p>
          </div>
          <Link
            href={`/app/studio?mode=grupo&group=${group.id}`}
            className="crm-btn crm-btn-primary"
          >
            Abrir sala
          </Link>
        </div>
      </div>

      <ol className="relative space-y-0 px-5 py-5 sm:px-6">
        {steps.map((member, index) => {
          const step = index + 1;
          const isLast = index === steps.length - 1;
          return (
            <li key={member.id} className="relative flex gap-4 pb-5 last:pb-0">
              {!isLast ? (
                <span
                  className="absolute left-[18px] top-10 bottom-0 w-px bg-white/10"
                  aria-hidden
                />
              ) : null}
              <div className="relative z-10 flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-white/15 bg-[#0a0a0a] font-display text-sm font-bold text-[color:var(--primary)]">
                {step}
              </div>
              <Link
                href={`/app/studio?mode=${member.mode}&group=${group.id}&member=${member.id}`}
                className="crm-card-sm group flex min-w-0 flex-1 items-center gap-3 !py-3 transition hover:border-[color:var(--primary)]/45"
              >
                <span
                  className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-xs font-bold text-[#0b0f14]"
                  style={{ background: member.color }}
                >
                  {member.name
                    .split(" ")
                    .slice(0, 2)
                    .map((w) => w[0])
                    .join("")}
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block text-sm font-semibold text-white group-hover:text-[color:var(--primary)]">
                    {member.name}
                  </span>
                  <span className="mt-0.5 block text-[12px] leading-snug text-white/50">
                    {member.role}
                  </span>
                </span>
                <span className="hidden shrink-0 text-[10px] font-bold uppercase tracking-[0.14em] text-white/30 sm:block">
                  Etapa {step}
                </span>
              </Link>
            </li>
          );
        })}
      </ol>

      <div className="border-t border-white/10 px-5 py-3 sm:px-6">
        <p className="text-[11px] text-white/40">
          Fluxo: {steps.map((m) => m.name).join(" → ")}
        </p>
      </div>
    </section>
  );
}

export function CrmDashboard() {
  const [items, setItems] = useState<ContentItem[]>([]);
  const [queue, setQueue] = useState<PublishJob[]>([]);

  const load = useCallback(async () => {
    try {
      const res = await fetch("/api/content?seed=1");
      const data = await res.json();
      if (!data.ok) return;
      setItems(data.items || []);
      setQueue(data.queue || []);
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const recent = items.slice(0, 5);

  return (
    <div className="space-y-10">
      <section className="space-y-6">
        <div>
          <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[color:var(--primary)]">
            Distribuição
          </p>
          <h3 className="font-display text-2xl font-bold text-white">
            Pipelines por grupo
          </h3>
          <p className="mt-1 text-sm text-white/50">
            Ordem do fluxo — clique no agente para abrir a etapa no Studio.
          </p>
        </div>

        <div className="grid gap-6 xl:grid-cols-2">
          {PIPELINE_GROUPS.map((group) => (
            <PipelineGroupCard
              key={group.id}
              group={group}
              accent={
                group.id === "conteudo-dev-video" ? "#34D399" : "#F26522"
              }
            />
          ))}
        </div>
      </section>

      <section className="animate-fase-rise" style={{ animationDelay: "120ms" }}>
        <div className="mb-3">
          <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[color:var(--primary)]">
            Operação
          </p>
          <h3 className="font-display text-2xl font-bold text-white">
            Seus grupos custom
          </h3>
          <p className="mt-1 text-sm text-white/50">
            Crie times extras, adicione ou remova agentes.
          </p>
        </div>
        <GroupsManager compact />
      </section>

      <div className="grid gap-4 lg:grid-cols-5">
        <section className="crm-panel lg:col-span-3 animate-fase-rise">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-display text-lg font-bold">Pipeline recente</h3>
            <Link
              href="/central"
              className="text-xs font-semibold text-white/45 hover:text-white"
            >
              Abrir kanban →
            </Link>
          </div>
          <ul className="space-y-2">
            {recent.length === 0 ? (
              <li className="text-sm text-white/45">
                Nenhum item ainda. Rode o Radar ou adicione na Central.
              </li>
            ) : (
              recent.map((item) => (
                <li key={item.id}>
                  <Link
                    href={`/central/${item.id}`}
                    className="crm-card-sm flex items-start justify-between gap-3"
                  >
                    <div>
                      <p className="text-sm font-semibold text-white">
                        {item.title}
                      </p>
                      <p className="mt-0.5 text-[11px] text-white/45">
                        {STAGE_LABELS[item.stage]} · {item.source} ·{" "}
                        {item.market.toUpperCase()}
                      </p>
                    </div>
                    {typeof item.score === "number" ? (
                      <span className="crm-pill">★ {item.score}</span>
                    ) : null}
                  </Link>
                </li>
              ))
            )}
          </ul>
        </section>

        <section className="space-y-4 lg:col-span-2">
          <div className="crm-panel animate-fase-rise">
            <h3 className="font-display text-lg font-bold">Atalhos</h3>
            <div className="mt-3 flex flex-col gap-2">
              <Link href="/central" className="crm-btn crm-btn-ghost w-full">
                Pipeline CRM
              </Link>
              <Link href="/agentes" className="crm-btn crm-btn-ghost w-full">
                Criar agente
              </Link>
              <Link href="/kits" className="crm-btn crm-btn-ghost w-full">
                Ninja Kits
              </Link>
            </div>
          </div>
          <div className="crm-panel animate-fase-rise">
            <h3 className="font-display text-lg font-bold">Fila de posts</h3>
            {queue.length === 0 ? (
              <p className="mt-2 text-sm text-white/45">
                Vazia — avance itens até ready e enfileire.
              </p>
            ) : (
              <ul className="mt-3 space-y-2">
                {queue.slice(0, 4).map((j) => (
                  <li
                    key={j.id}
                    className="crm-card-sm flex items-center justify-between text-xs"
                  >
                    <span className="font-semibold uppercase">{j.network}</span>
                    <span className="text-white/45">{j.status}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
