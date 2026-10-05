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

const BOARD_STAGES: ContentStage[] = [...CONTENT_STAGES];

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
    <div className="space-y-6">
      {stats ? (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 animate-fase-rise">
          {[
            { label: "Itens", value: stats.total },
            { label: "Na fila", value: stats.queued },
            { label: "Agendados", value: stats.scheduled },
            { label: "Postados", value: stats.published },
          ].map((s) => (
            <div key={s.label} className="crm-stat">
              <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-[color:var(--fase-muted)]">
                {s.label}
              </p>
              <p className="font-display mt-1 text-2xl font-bold text-[color:var(--fase-ink)]">
                {s.value}
              </p>
            </div>
          ))}
        </div>
      ) : null}

      <form
        onSubmit={createIdea}
        className="crm-panel flex flex-wrap gap-2 animate-fase-rise"
        style={{ animationDelay: "60ms" }}
      >
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Nova ideia de conteúdo…"
          className="field min-w-[220px] flex-1"
        />
        <button
          type="submit"
          disabled={creating || !title.trim()}
          className="crm-btn crm-btn-dark disabled:opacity-50"
        >
          {creating ? "Criando…" : "Adicionar"}
        </button>
      </form>

      {error ? <p className="text-sm text-red-700">{error}</p> : null}

      <section className="animate-fase-rise" style={{ animationDelay: "100ms" }}>
        <h2 className="mb-3 text-xs font-bold uppercase tracking-[0.18em] text-[color:var(--fase-muted)]">
          Kanban
        </h2>
        {loading ? (
          <p className="text-sm text-[color:var(--fase-muted)]">Carregando…</p>
        ) : (
          <div className="crm-kanban">
            {BOARD_STAGES.map((stage) => (
              <div key={stage} className="crm-kanban-col">
                <div className="mb-3 flex items-center justify-between px-0.5">
                  <p className="text-[11px] font-bold uppercase tracking-[0.12em] text-[color:var(--fase-ink)]">
                    {STAGE_LABELS[stage]}
                  </p>
                  <span className="crm-pill">{byStage[stage].length}</span>
                </div>
                <div className="space-y-2">
                  {byStage[stage].map((item) => (
                    <article key={item.id} className="crm-kanban-card">
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
                          <span key={n} className="crm-pill">
                            {NETWORK_LABELS[n]}
                          </span>
                        ))}
                      </div>
                      <div className="mt-2 flex flex-wrap gap-1">
                        {stage !== "published" ? (
                          <button
                            type="button"
                            onClick={() => void advance(item.id)}
                            className="rounded-md bg-[color:var(--fase-ink)] px-2 py-1 text-[10px] font-bold text-white"
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
        <section className="crm-panel">
          <h2 className="text-xs font-bold uppercase tracking-[0.18em] text-[color:var(--fase-muted)]">
            Fila de publicação
          </h2>
          <ul className="mt-3 space-y-2">
            {queue.slice(0, 8).map((job) => (
              <li
                key={job.id}
                className="crm-card-sm flex flex-wrap items-center justify-between gap-2 text-sm"
              >
                <span>
                  <strong>{NETWORK_LABELS[job.network]}</strong> · {job.status}
                </span>
                {job.status === "queued" ? (
                  <button
                    type="button"
                    className="crm-btn crm-btn-primary !py-1 !text-[11px]"
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
    </div>
  );
}
