"use client";

import Link from "next/link";
import { useCallback, useEffect, useState, type CSSProperties } from "react";
import type { ContentItem, PublishJob } from "@/lib/content/types";
import { STAGE_LABELS } from "@/lib/content/types";
import { listAgentGroups } from "@/lib/agents/groups";

type Stats = {
  total: number;
  byStage: Record<string, number>;
  queued: number;
  scheduled: number;
  published: number;
};

const FEATURES = [
  {
    href: "/agentes",
    title: "Criar agente",
    blurb: "Persona + toolkit + instruções — agentes só seus",
    glow: "rgba(200, 245, 66, 0.4)",
    tag: "Custom",
  },
  {
    href: "/studio?mode=github&q=Busca%20os%20melhores%20reposit%C3%B3rios%20do%20GitHub%20em%20diferentes%20nichos%20com%20mais%20stars%20e%20gera%20roteiro%20Reels%2060s%20de%20cada%20vencedor",
    title: "GitHub Scout",
    blurb: "Melhores repos por nicho + roteiro de vídeo 60s",
    glow: "rgba(94, 234, 212, 0.35)",
    tag: "GitHub",
  },
  {
    href: "/radar",
    title: "Radar",
    blurb: "Briefing diário de IA, automação e marketing",
    glow: "rgba(94, 234, 212, 0.35)",
    tag: "Ideação",
  },
  {
    href: "/studio?mode=roteiro",
    title: "Roteirista",
    blurb: "Reels 60s, guiones e tom pessoal",
    glow: "rgba(200, 245, 66, 0.35)",
    tag: "Script",
  },
  {
    href: "/studio?mode=arte-realista&q=Planeja%20um%20carrossel%20realista%20Douglas%20Dev%20(Antes%2FDepois)%20sobre%205%20automa%C3%A7%C3%B5es%20com%20IA%20usando%20plan_carrossel_realista_douglas",
    title: "Carrossel realista",
    blurb: "Antes/Depois fotorealista · preto + laranja Douglas Dev",
    glow: "rgba(242, 101, 34, 0.4)",
    tag: "Visual",
  },
  {
    href: "/studio?mode=arte-realista",
    title: "Direção de arte",
    blurb: "Twitter + realista + capas no brand kit",
    glow: "rgba(242, 101, 34, 0.28)",
    tag: "Visual",
  },
  {
    href: "/editor",
    title: "Editor de vídeo",
    blurb: "Skills Ninja + EDVD + HyperFrames",
    glow: "rgba(94, 234, 212, 0.3)",
    tag: "Produção",
  },
  {
    href: "/grupos",
    title: "Salas de agentes",
    blurb: "Dev, Dev Vídeo e Contenidos España",
    glow: "rgba(200, 245, 66, 0.28)",
    tag: "Times",
  },
  {
    href: "/kits",
    title: "Ninja Kits",
    blurb: "Inventário de skills e runners",
    glow: "rgba(255, 122, 89, 0.22)",
    tag: "Skills",
  },
  {
    href: "/pipeline",
    title: "Pack Scout",
    blurb: "GitHub → Reels → Notion numa tacada",
    glow: "rgba(94, 234, 212, 0.25)",
    tag: "Pack",
  },
  {
    href: "/central",
    title: "Pipeline CRM",
    blurb: "Kanban ideia → postado + fila social",
    glow: "rgba(200, 245, 66, 0.32)",
    tag: "Ops",
  },
] as const;

const QUICK = [
  {
    href: "/agentes",
    label: "Criar agente",
  },
  {
    href: "/studio?mode=github&q=Busca%20os%20melhores%20reposit%C3%B3rios%20do%20GitHub%20em%20diferentes%20nichos%20(mais%20stars)%20e%20me%20entrega%20um%20roteiro%20de%20v%C3%ADdeo%20de%20at%C3%A9%2060s%20explicando%20o%20que%20cada%20vencedor%20faz",
    label: "GitHub + Reels 60s",
  },
  {
    href: "/studio?mode=central&q=Lista%20o%20pipeline%20e%20sugira%20o%20próximo%20passo",
    label: "Operar Central",
  },
  {
    href: "/studio?mode=radar&q=Monta%20o%20briefing%20diário%20de%20IA%2C%20automação%20e%20marketing",
    label: "Rodar Radar",
  },
  {
    href: "/studio?mode=grupo&group=conteudo-dev",
    label: "Sala Conteúdo Dev",
  },
  {
    href: "/studio?mode=grupo&group=conteudos-espanha",
    label: "Contenidos España",
  },
] as const;

export function CrmDashboard() {
  const [items, setItems] = useState<ContentItem[]>([]);
  const [queue, setQueue] = useState<PublishJob[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const groups = listAgentGroups();

  const load = useCallback(async () => {
    try {
      const res = await fetch("/api/content?seed=1");
      const data = await res.json();
      if (!data.ok) return;
      setItems(data.items || []);
      setStats(data.stats || null);
      setQueue(data.queue || []);
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const recent = items.slice(0, 5);
  const inMotion = items.filter(
    (i) => !["published", "idea"].includes(i.stage),
  ).length;

  return (
    <div className="space-y-8">
      {/* Hero composition */}
      <section className="relative overflow-hidden rounded-[1.75rem] border border-white/10 bg-[#141414] px-6 py-8 text-white sm:px-8 sm:py-10 animate-fase-rise">
        <div
          className="pointer-events-none absolute inset-0"
          style={{
            background:
              "radial-gradient(600px 320px at 15% 20%, rgba(242,101,34,0.35), transparent 55%), radial-gradient(500px 280px at 90% 10%, rgba(120,30,10,0.25), transparent 50%)",
          }}
          aria-hidden
        />
        <div className="relative z-10 flex flex-wrap items-end justify-between gap-6">
          <div className="max-w-xl">
            <p className="text-[11px] font-bold uppercase tracking-[0.22em] text-[color:var(--dd-orange)]">
              Content operations · @o.douglas.dev
            </p>
            <h2 className="font-display mt-3 text-4xl tracking-tight text-white sm:text-5xl">
              <span className="fase-shimmer-text">FASE</span>
            </h2>
            <p className="mt-3 text-sm leading-relaxed text-white/55 sm:text-base">
              Identidade Douglas Dev — preto, laranja e carrosséis realistas.
              Dashboard único para agentes, pipeline e publicação.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Link href="/studio?mode=central" className="crm-btn crm-btn-primary">
              Abrir Studio IA
            </Link>
            <Link
              href="/central"
              className="crm-btn border border-white/20 bg-white/5 text-white hover:bg-white/10"
            >
              Ver pipeline
            </Link>
          </div>
        </div>

        <div className="relative z-10 mt-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
          {[
            { label: "Itens", value: stats?.total ?? "—" },
            { label: "Em fluxo", value: inMotion },
            { label: "Fila", value: stats?.queued ?? 0 },
            { label: "Postados", value: stats?.published ?? 0 },
          ].map((s, i) => (
            <div
              key={s.label}
              className="rounded-xl border border-white/10 bg-white/5 px-3 py-3 backdrop-blur-sm animate-fase-rise"
              style={{ animationDelay: `${120 + i * 60}ms` }}
            >
              <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-white/45">
                {s.label}
              </p>
              <p className="font-display mt-1 text-2xl font-bold">{s.value}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Quick actions */}
      <section className="animate-fase-rise" style={{ animationDelay: "80ms" }}>
        <div className="mb-3 flex items-center justify-between">
          <h3 className="font-display text-lg font-bold text-white">
            Ações rápidas
          </h3>
        </div>
        <div className="flex flex-wrap gap-2">
          {QUICK.map((q) => (
            <Link key={q.href} href={q.href} className="crm-btn crm-btn-ghost">
              {q.label}
            </Link>
          ))}
        </div>
      </section>

      {/* Feature grid — all SaaS functions */}
      <section>
        <div className="mb-3 flex items-end justify-between gap-3">
          <h3 className="font-display text-lg font-bold text-white">
            Todas as funcionalidades
          </h3>
          <p className="text-xs text-[color:var(--fase-muted)]">
            Clique para abrir o módulo
          </p>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {FEATURES.map((f, i) => (
            <Link
              key={f.href}
              href={f.href}
              className="crm-tile animate-fase-rise"
              style={
                {
                  "--tile-glow": f.glow,
                  animationDelay: `${100 + i * 40}ms`,
                } as CSSProperties
              }
            >
              <span className="crm-pill">{f.tag}</span>
              <p className="font-display relative z-10 text-xl font-bold text-white">
                {f.title}
              </p>
              <p className="relative z-10 text-xs leading-relaxed text-[color:var(--fase-muted)]">
                {f.blurb}
              </p>
            </Link>
          ))}
        </div>
      </section>

      <div className="grid gap-4 lg:grid-cols-5">
        {/* Recent pipeline */}
        <section className="crm-panel lg:col-span-3 animate-fase-rise" style={{ animationDelay: "160ms" }}>
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-display text-lg font-bold">Pipeline recente</h3>
            <Link
              href="/central"
              className="text-xs font-semibold text-[color:var(--fase-muted)] hover:text-white"
            >
              Abrir kanban →
            </Link>
          </div>
          <ul className="space-y-2">
            {recent.length === 0 ? (
              <li className="text-sm text-[color:var(--fase-muted)]">
                Nenhum item ainda. Rode o Radar ou adicione na Central.
              </li>
            ) : (
              recent.map((item) => (
                <li key={item.id}>
                  <Link
                    href={`/central/${item.id}`}
                    className="flex items-start justify-between gap-3 rounded-xl border border-[color:var(--fase-line)] bg-white/80 px-3 py-2.5 transition hover:border-[color:var(--fase-ink)]/20"
                  >
                    <div>
                      <p className="text-sm font-semibold text-white">
                        {item.title}
                      </p>
                      <p className="mt-0.5 text-[11px] text-[color:var(--fase-muted)]">
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

        {/* Groups + queue */}
        <section className="space-y-4 lg:col-span-2">
          <div className="crm-panel animate-fase-rise" style={{ animationDelay: "200ms" }}>
            <h3 className="font-display text-lg font-bold">Times de agentes</h3>
            <ul className="mt-3 space-y-2">
              {groups.map((g) => (
                <li key={g.id}>
                  <Link
                    href={`/studio?mode=grupo&group=${g.id}`}
                    className="block rounded-xl border border-[color:var(--fase-line)] bg-white/70 px-3 py-2.5 transition hover:border-[color:var(--fase-ink)]/20"
                  >
                    <p className="text-sm font-semibold">{g.name}</p>
                    <p className="mt-0.5 line-clamp-2 text-[11px] text-[color:var(--fase-muted)]">
                      {g.blurb}
                    </p>
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div className="crm-panel animate-fase-rise" style={{ animationDelay: "240ms" }}>
            <h3 className="font-display text-lg font-bold">Fila de posts</h3>
            {queue.length === 0 ? (
              <p className="mt-2 text-sm text-[color:var(--fase-muted)]">
                Vazia — avance itens até ready e enfileire.
              </p>
            ) : (
              <ul className="mt-3 space-y-2">
                {queue.slice(0, 4).map((j) => (
                  <li
                    key={j.id}
                    className="flex items-center justify-between rounded-lg bg-white/70 px-2.5 py-2 text-xs"
                  >
                    <span className="font-semibold uppercase">{j.network}</span>
                    <span className="text-[color:var(--fase-muted)]">{j.status}</span>
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
