"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  NETWORK_LABELS,
  STAGE_LABELS,
  type ContentItem,
  type ContentNetwork,
  type ContentStage,
} from "@/lib/content/types";

export function ContentDetail({ id }: { id: string }) {
  const [item, setItem] = useState<ContentItem | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [draft, setDraft] = useState({
    title: "",
    summary: "",
    script: "",
    caption: "",
    artBrief: "",
    notes: "",
    stage: "idea" as ContentStage,
  });

  const load = useCallback(async () => {
    setError(null);
    const res = await fetch(`/api/content/${id}`);
    const data = await res.json();
    if (!data.ok) {
      setError(data.error || "not_found");
      return;
    }
    const it = data.item as ContentItem;
    setItem(it);
    setDraft({
      title: it.title,
      summary: it.summary || "",
      script: it.script || "",
      caption: it.caption || "",
      artBrief: it.artBrief || "",
      notes: it.notes || "",
      stage: it.stage,
    });
  }, [id]);

  useEffect(() => {
    void load();
  }, [load]);

  async function save() {
    setSaving(true);
    try {
      const res = await fetch(`/api/content/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(draft),
      });
      const data = await res.json();
      if (!data.ok) throw new Error(data.error);
      setItem(data.item);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro");
    } finally {
      setSaving(false);
    }
  }

  async function advance() {
    await fetch(`/api/content/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "advance" }),
    });
    await load();
  }

  async function queue(network: ContentNetwork) {
    await fetch("/api/publish", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contentId: id,
        network,
        caption: draft.caption || undefined,
      }),
    });
    await load();
  }

  async function remove() {
    if (!confirm("Apagar este item?")) return;
    await fetch(`/api/content/${id}`, { method: "DELETE" });
    window.location.href = "/central";
  }

  if (error && !item) {
    return (
      <div className="py-8">
        <p className="text-sm text-red-700">{error}</p>
        <Link href="/central" className="mt-4 inline-block text-sm underline">
          ← Pipeline
        </Link>
      </div>
    );
  }

  if (!item) {
    return (
      <div className="py-8 text-sm text-[color:var(--fase-muted)]">
        Carregando…
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2">
          <Link
            href={`/studio?mode=central&q=${encodeURIComponent(`Atualiza e avança o item ${item.id}: ${item.title}`)}`}
            className="crm-btn crm-btn-primary"
          >
            Operar com IA
          </Link>
          <button
            type="button"
            onClick={() => void advance()}
            className="crm-btn crm-btn-dark"
          >
            Avançar estágio
          </button>
        </div>
      </div>

      <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[color:var(--fase-muted)]">
        {STAGE_LABELS[item.stage]} · {item.market.toUpperCase()} · {item.source}
      </p>
      <h2 className="font-display text-2xl font-extrabold tracking-tight text-[color:var(--fase-ink)]">
        {item.title}
      </h2>

      <div className="mt-3 flex flex-wrap gap-1">
        {item.networks.map((n) => (
          <span
            key={n}
            className="rounded-md bg-[color:var(--fase-chip)] px-2 py-0.5 text-[11px] font-medium"
          >
            {NETWORK_LABELS[n]}
          </span>
        ))}
      </div>

      <div className="mt-8 space-y-4">
        <Field label="Título">
          <input
            className="field"
            value={draft.title}
            onChange={(e) => setDraft((d) => ({ ...d, title: e.target.value }))}
          />
        </Field>
        <Field label="Resumo">
          <textarea
            className="field min-h-[72px]"
            value={draft.summary}
            onChange={(e) =>
              setDraft((d) => ({ ...d, summary: e.target.value }))
            }
          />
        </Field>
        <Field label="Roteiro">
          <textarea
            className="field min-h-[140px] font-mono text-xs"
            value={draft.script}
            onChange={(e) =>
              setDraft((d) => ({ ...d, script: e.target.value }))
            }
          />
        </Field>
        <Field label="Caption / legenda">
          <textarea
            className="field min-h-[80px]"
            value={draft.caption}
            onChange={(e) =>
              setDraft((d) => ({ ...d, caption: e.target.value }))
            }
          />
        </Field>
        <Field label="Brief de arte">
          <textarea
            className="field min-h-[80px]"
            value={draft.artBrief}
            onChange={(e) =>
              setDraft((d) => ({ ...d, artBrief: e.target.value }))
            }
          />
        </Field>
        <Field label="Notas">
          <textarea
            className="field min-h-[60px]"
            value={draft.notes}
            onChange={(e) => setDraft((d) => ({ ...d, notes: e.target.value }))}
          />
        </Field>
      </div>

      <div className="mt-6 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => void save()}
          disabled={saving}
          className="rounded-lg bg-[color:var(--fase-ink)] px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
        >
          {saving ? "Salvando…" : "Salvar"}
        </button>
        <button
          type="button"
          onClick={() => void queue("instagram")}
          className="rounded-lg border border-[color:var(--fase-line)] px-4 py-2 text-sm font-semibold"
        >
          Fila Instagram
        </button>
        <button
          type="button"
          onClick={() => void queue("youtube")}
          className="rounded-lg border border-[color:var(--fase-line)] px-4 py-2 text-sm font-semibold"
        >
          Fila YouTube
        </button>
        <button
          type="button"
          onClick={() => void queue("x")}
          className="rounded-lg border border-[color:var(--fase-line)] px-4 py-2 text-sm font-semibold"
        >
          Fila X
        </button>
        <button
          type="button"
          onClick={() => void remove()}
          className="ml-auto rounded-lg px-4 py-2 text-sm font-semibold text-red-700"
        >
          Apagar
        </button>
      </div>

      {item.videoPath ? (
        <p className="mt-6 text-xs text-[color:var(--fase-muted)]">
          Vídeo: <code>{item.videoPath}</code>
        </p>
      ) : null}
    </div>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--fase-muted)]">
        {label}
      </span>
      {children}
    </label>
  );
}
