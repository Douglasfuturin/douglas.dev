"use client";

import Link from "next/link";
import { useCallback, useEffect, useState, type CSSProperties } from "react";
import type { ContentItem, PublishJob } from "@/lib/content/types";
import { STAGE_LABELS } from "@/lib/content/types";
import {
  OPERATION_BLURBS,
  OPERATION_LABELS,
  type OperationId,
} from "@/lib/agents/group-types";
import { GroupsManager } from "@/components/crm/groups-manager";

type Stats = {
  total: number;
  byStage: Record<string, number>;
  queued: number;
  scheduled: number;
  published: number;
};

type OpFeature = {
  href: string;
  title: string;
  blurb: string;
  glow: string;
  tag: string;
};

const OPS: Record<OperationId, OpFeature[]> = {
  ideacao: [
    {
      href: "/radar",
      title: "Radar",
      blurb: "Briefing diário de IA, automação e marketing",
      glow: "rgba(94, 234, 212, 0.35)",
      tag: "Ideação",
    },
    {
      href: "/studio?mode=github&q=Busca%20os%20melhores%20reposit%C3%B3rios%20do%20GitHub%20em%20diferentes%20nichos%20com%20mais%20stars%20e%20gera%20roteiro%20Reels%2060s%20de%20cada%20vencedor",
      title: "GitHub Scout",
      blurb: "Melhores repos por nicho + roteiro 60s",
      glow: "rgba(94, 234, 212, 0.35)",
      tag: "GitHub",
    },
  ],
  script: [
    {
      href: "/studio?mode=roteiro",
      title: "Roteirista",
      blurb: "Reels 60s, guiones e tom pessoal",
      glow: "rgba(200, 245, 66, 0.35)",
      tag: "Script",
    },
    {
      href: "/studio?mode=roteiro-pessoal",
      title: "Roteirista Pessoal",
      blurb: "1ª pessoa, autoridade e gancho",
      glow: "rgba(167, 139, 250, 0.3)",
      tag: "Script",
    },
  ],
  visual: [
    {
      href: "/studio?mode=arte-realista&q=Planeja%20um%20carrossel%20realista%20Douglas%20Dev%20(Antes%2FDepois)%20sobre%205%20automa%C3%A7%C3%B5es%20com%20IA%20usando%20plan_carrossel_realista_douglas",
      title: "Carrossel realista",
      blurb: "Antes/Depois fotorealista · preto + laranja",
      glow: "rgba(242, 101, 34, 0.4)",
      tag: "Visual",
    },
    {
      href: "/studio?mode=arte-twitter",
      title: "Arte Twitter",
      blurb: "Peças para X no brand kit",
      glow: "rgba(242, 101, 34, 0.28)",
      tag: "Visual",
    },
  ],
  video: [
    {
      href: "/editor",
      title: "Editor de vídeo",
      blurb: "Skills Ninja + EDVD + HyperFrames",
      glow: "rgba(94, 234, 212, 0.3)",
      tag: "Produção",
    },
    {
      href: "/studio?mode=editor-reels",
      title: "Editor Reels",
      blurb: "Corte 9:16, ritmo e legendas",
      glow: "rgba(248, 113, 113, 0.28)",
      tag: "Reels",
    },
  ],
  publicacao: [
    {
      href: "/central",
      title: "Pipeline CRM",
      blurb: "Kanban ideia → postado + fila social",
      glow: "rgba(200, 245, 66, 0.32)",
      tag: "Ops",
    },
    {
      href: "/pipeline",
      title: "Pack Scout",
      blurb: "GitHub → Reels → Notion numa tacada",
      glow: "rgba(94, 234, 212, 0.25)",
      tag: "Pack",
    },
  ],
  times: [],
  sistema: [
    {
      href: "/agentes",
      title: "Criar agente",
      blurb: "Persona + toolkit + instruções",
      glow: "rgba(200, 245, 66, 0.4)",
      tag: "Custom",
    },
    {
      href: "/kits",
      title: "Ninja Kits",
      blurb: "Inventário de skills e runners",
      glow: "rgba(255, 122, 89, 0.22)",
      tag: "Skills",
    },
    {
      href: "/studio?mode=orquestrador&q=Orquestra%20todos%20os%20grupos%20e%20defina%20o%20fluxo%20correto",
      title: "Orquestrador Principal",
      blurb: "Coordena todos os times e operações",
      glow: "rgba(242, 101, 34, 0.45)",
      tag: "Core",
    },
  ],
};

const OP_ORDER: OperationId[] = [
  "sistema",
  "times",
  "ideacao",
  "script",
  "visual",
  "video",
  "publicacao",
];

export function CrmDashboard() {
  const [items, setItems] = useState<ContentItem[]>([]);
  const [queue, setQueue] = useState<PublishJob[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);

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
    <div className="space-y-10">
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
              Operações · @o.douglas.dev
            </p>
            <h2 className="font-display mt-3 text-4xl tracking-tight text-white sm:text-5xl">
              <span className="fase-shimmer-text">Central de Agentes</span>
            </h2>
            <p className="mt-3 text-sm leading-relaxed text-white/55 sm:text-base">
              Dashboard por operação. O Orquestrador Principal coordena os
              grupos; cada time conversa e fecha o fluxo.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Link
              href="/studio?mode=orquestrador&q=Orquestra%20todos%20os%20grupos%20e%20monte%20o%20fluxo%20correto"
              className="crm-btn crm-btn-primary"
            >
              Orquestrador Principal
            </Link>
            <Link href="/grupos" className="crm-btn crm-btn-ghost">
              Criar grupo
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

      {OP_ORDER.map((op, sectionIndex) => {
        if (op === "times") {
          return (
            <section
              key={op}
              className="animate-fase-rise"
              style={{ animationDelay: `${80 + sectionIndex * 40}ms` }}
            >
              <div className="mb-3">
                <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[color:var(--dd-orange)]">
                  Operação
                </p>
                <h3 className="font-display text-2xl font-bold text-white">
                  {OPERATION_LABELS[op]}
                </h3>
                <p className="mt-1 text-sm text-[color:var(--fase-muted)]">
                  {OPERATION_BLURBS[op]}
                </p>
              </div>
              <GroupsManager compact />
            </section>
          );
        }

        const features = OPS[op];
        return (
          <section
            key={op}
            className="animate-fase-rise"
            style={{ animationDelay: `${80 + sectionIndex * 40}ms` }}
          >
            <div className="mb-3 flex flex-wrap items-end justify-between gap-3">
              <div>
                <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[color:var(--dd-orange)]">
                  Operação
                </p>
                <h3 className="font-display text-2xl font-bold text-white">
                  {OPERATION_LABELS[op]}
                </h3>
                <p className="mt-1 text-sm text-[color:var(--fase-muted)]">
                  {OPERATION_BLURBS[op]}
                </p>
              </div>
            </div>
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {features.map((f, i) => (
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
        );
      })}

      <div className="grid gap-4 lg:grid-cols-5">
        <section
          className="crm-panel lg:col-span-3 animate-fase-rise"
          style={{ animationDelay: "160ms" }}
        >
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

        <section className="space-y-4 lg:col-span-2">
          <div
            className="crm-panel animate-fase-rise"
            style={{ animationDelay: "240ms" }}
          >
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
                    <span className="text-[color:var(--fase-muted)]">
                      {j.status}
                    </span>
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
