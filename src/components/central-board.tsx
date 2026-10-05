"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  CONTENT_STAGES,
  NETWORK_LABELS,
  STAGE_LABELS,
  type ContentItem,
  type ContentStage,
  type PublishJob,
} from "@/lib/content/types";

type Stats = {
  total: number;
  byStage: Record<string, number>;
  queued: number;
  scheduled: number;
  published: number;
};

const BOARD_STAGES: ContentStage[] = [
  "idea",
  "approved",
  "script",
  "art",
  "video",
  "packaged",
  "ready",
  "scheduled",
  "published",
];

const MODULES = [
  {
    href: "/studio?mode=radar",
    title: "Radar",
    blurb: "Briefing diário IA / automação / marketing",
  },
  {
    href: "/studio?mode=roteiro",
    title: "Roteirista",
    blurb: "Reels 60s e guiones",
  },
  {
    href: "/studio?mode=arte-realista",
    title: "Artes",
    blurb: "Twitter + realista + capas",
  },
  {
    href: "/studio?mode=video",
    title: "Editor",
    blurb: "Skills + EDVD automático",
  },
  {
    href: "/grupos",
    title: "Grupos",
    blurb: "Dev, Vídeo e España",
  },
  {
    href: "/studio?mode=central",
    title: "Operar IA",
    blurb: "Modo Central fecha o ciclo",
  },
] as const;

export function CentralBoard() {
  const [items, setItems] = useState<ContentItem[]>([]);
  const [queue, setQueue] = useState<PublishJob[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [title, setTitle] = useState("");
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      const res = await fetch("/api/content?seed=1");
      const data = (await res.json()) as {
        ok: boolean;
        items?: ContentItem[];
        stats?: Stats;
        queue?: PublishJob[];
        error?: string;
      };
      if (!data.ok) throw new Error(data.error || "Falha ao carregar");
      setItems(data.items || []);
      setStats(data.stats || null);
      setQueue(data.queue || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const byStage = useMemo(() => {
    const map = Object.fromEntries(
      BOARD_STAGES.map((s) => [s, [] as ContentItem[]]),
    ) as Record<ContentStage, ContentItem[]>;
    for (const item of items) {
      if (map[item.stage]) map[item.stage].push(item);
    }
    return map;
  }, [items]);

  async function createIdea(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    setCreating(true);
    setError(null);
    try {
      const res = await fetch("/api/content", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: title.trim(),
          source: "manual",
          stage: "idea",
        }),
      });
      const data = await res.json();
      if (!data.ok) throw new Error(data.error || "Falha ao criar");
      setTitle("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro");
    } finally {
      setCreating(false);
    }
  }

  async function advance(id: string) {
    await fetch(`/api/content/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "advance" }),
    });
    await load();
  }

  async function queuePost(id: string, network: "instagram" | "youtube" | "x") {
    await fetch("/api/publish", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contentId: id, network }),
    });
    await load();
  }

  return (
    <main className="mx-auto max-w-[1400px] px-4 py-8 sm:px-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-[color:var(--fase-muted)]">
            SaaS pessoal
          </p>
          <h1 className="font-display mt-1 text-3xl font-extrabold tracking-tight text-[color:var(--fase-ink)] sm:text-4xl">
            Central
          </h1>
          <p className="mt-2 max-w-lg text-sm text-[color:var(--fase-muted)]">
            Pipeline completo: ideia → aprovado → roteiro → artes → vídeo →
            pacote → pronto → agendado → postado.
          </p>
        </div>
        <Link
          href="/studio?mode=central&q=Lista%20o%20pipeline%20e%20me%20diga%20o%20pr%C3%B3ximo%20passo"
          className="rounded-lg bg-[color:var(--fase-accent)] px-4 py-2.5 text-sm font-bold text-[color:var(--fase-accent-ink)]"
        >
          Operar com IA →
        </Link>
      </div>

      {stats ? (
        <div className="mt-6 flex flex-wrap gap-3 text-sm">
          <Stat label="Itens" value={stats.total} />
          <Stat label="Na fila" value={stats.queued} />
          <Stat label="Agendados" value={stats.scheduled} />
          <Stat label="Postados" value={stats.published} />
        </div>
      ) : null}

      <form
        onSubmit={createIdea}
        className="mt-6 flex flex-wrap gap-2 rounded-2xl border border-[color:var(--fase-line)] bg-white/70 p-3"
      >
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Nova ideia de conteúdo…"
          className="min-w-[220px] flex-1 rounded-lg border border-[color:var(--fase-line)] bg-white px-3 py-2 text-sm outline-none focus:border-[color:var(--fase-accent)]"
        />
        <button
          type="submit"
          disabled={creating || !title.trim()}
          className="rounded-lg bg-[color:var(--fase-ink)] px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
        >
          {creating ? "Criando…" : "Adicionar"}
        </button>
      </form>

      {error ? (
        <p className="mt-3 text-sm text-red-700">{error}</p>
      ) : null}

      <section className="mt-8">
        <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-[color:var(--fase-muted)]">
          Módulos
        </h2>
        <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {MODULES.map((m) => (
            <Link
              key={m.href}
              href={m.href}
              className="rounded-2xl border border-[color:var(--fase-line)] bg-white/60 px-4 py-3 transition hover:border-[color:var(--fase-accent)] hover:bg-white"
            >
              <p className="font-display text-base font-bold text-[color:var(--fase-ink)]">
                {m.title}
              </p>
              <p className="mt-1 text-xs text-[color:var(--fase-muted)]">
                {m.blurb}
              </p>
            </Link>
          ))}
        </div>
      </section>

      <section className="mt-10">
        <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-[color:var(--fase-muted)]">
          Pipeline
        </h2>
        {loading ? (
          <p className="mt-4 text-sm text-[color:var(--fase-muted)]">
            Carregando…
          </p>
        ) : (
          <div className="mt-4 flex gap-3 overflow-x-auto pb-4">
            {BOARD_STAGES.map((stage) => (
              <div
                key={stage}
                className="w-[220px] shrink-0 rounded-2xl border border-[color:var(--fase-line)] bg-[color:var(--fase-panel)]/80 p-3"
              >
                <div className="mb-3 flex items-center justify-between">
                  <p className="text-[11px] font-bold uppercase tracking-[0.12em] text-[color:var(--fase-ink)]">
                    {STAGE_LABELS[stage]}
                  </p>
                  <span className="rounded-md bg-black/5 px-1.5 py-0.5 text-[10px] font-semibold text-[color:var(--fase-muted)]">
                    {byStage[stage].length}
                  </span>
                </div>
                <div className="space-y-2">
                  {byStage[stage].map((item) => (
                    <article
                      key={item.id}
                      className="rounded-xl border border-[color:var(--fase-line)] bg-white p-3 shadow-[0_1px_0_rgba(16,32,51,0.04)]"
                    >
                      <Link
                        href={`/central/${item.id}`}
                        className="text-sm font-semibold leading-snug text-[color:var(--fase-ink)] hover:underline"
                      >
                        {item.title}
                      </Link>
                      {item.summary ? (
                        <p className="mt-1 line-clamp-2 text-[11px] text-[color:var(--fase-muted)]">
                          {item.summary}
                        </p>
                      ) : null}
                      <div className="mt-2 flex flex-wrap gap-1">
                        {item.networks.slice(0, 3).map((n) => (
                          <span
                            key={n}
                            className="rounded bg-[color:var(--fase-chip)] px-1.5 py-0.5 text-[10px] font-medium text-[color:var(--fase-accent-ink)]"
                          >
                            {NETWORK_LABELS[n]}
                          </span>
                        ))}
                        {typeof item.score === "number" ? (
                          <span className="rounded bg-black/5 px-1.5 py-0.5 text-[10px] font-medium text-[color:var(--fase-muted)]">
                            ★ {item.score}
                          </span>
                        ) : null}
                      </div>
                      <div className="mt-2 flex flex-wrap gap-1">
                        {stage !== "published" ? (
                          <button
                            type="button"
                            onClick={() => void advance(item.id)}
                            className="rounded-md bg-[color:var(--fase-ink)]/90 px-2 py-1 text-[10px] font-semibold text-white"
                          >
                            Avançar
                          </button>
                        ) : null}
                        {stage === "ready" || stage === "packaged" ? (
                          <button
                            type="button"
                            onClick={() => void queuePost(item.id, "instagram")}
                            className="rounded-md border border-[color:var(--fase-line)] px-2 py-1 text-[10px] font-semibold"
                          >
                            Fila IG
                          </button>
                        ) : null}
                        <Link
                          href={`/studio?mode=central&q=${encodeURIComponent(`Trabalha o item ${item.id}: ${item.title}`)}`}
                          className="rounded-md border border-[color:var(--fase-line)] px-2 py-1 text-[10px] font-semibold"
                        >
                          IA
                        </Link>
                      </div>
                    </article>
                  ))}
                  {byStage[stage].length === 0 ? (
                    <p className="px-1 py-6 text-center text-[11px] text-[color:var(--fase-muted)]">
                      vazio
                    </p>
                  ) : null}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {queue.length > 0 ? (
        <section className="mt-10">
          <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-[color:var(--fase-muted)]">
            Fila de publicação
          </h2>
          <ul className="mt-3 space-y-2">
            {queue.slice(0, 8).map((job) => (
              <li
                key={job.id}
                className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-[color:var(--fase-line)] bg-white/70 px-3 py-2 text-sm"
              >
                <span>
                  <strong>{NETWORK_LABELS[job.network]}</strong> · {job.contentId}{" "}
                  · <span className="text-[color:var(--fase-muted)]">{job.status}</span>
                </span>
                {job.status === "queued" ? (
                  <button
                    type="button"
                    className="rounded-md bg-[color:var(--fase-accent)] px-2 py-1 text-[11px] font-bold text-[color:var(--fase-accent-ink)]"
                    onClick={async () => {
                      await fetch("/api/publish", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                          action: "mark_sent",
                          jobId: job.id,
                        }),
                      });
                      await load();
                    }}
                  >
                    Marcar postado
                  </button>
                ) : null}
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <p className="mt-10 text-[11px] text-[color:var(--fase-muted)]">
        Estágios: {CONTENT_STAGES.map((s) => STAGE_LABELS[s]).join(" → ")}
      </p>
    </main>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-[color:var(--fase-line)] bg-white/70 px-3 py-2">
      <p className="text-[10px] uppercase tracking-[0.14em] text-[color:var(--fase-muted)]">
        {label}
      </p>
      <p className="font-display text-xl font-bold text-[color:var(--fase-ink)]">
        {value}
      </p>
    </div>
  );
}
