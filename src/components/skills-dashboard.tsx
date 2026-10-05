"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState, startTransition } from "react";
import { SkillRunner } from "@/components/skill-runner";
import { VisualEditPanel } from "@/components/visual-edit-panel";
import type { KitSourceZip, NinjaKit } from "@/lib/kits/types";

type ActiveRun = {
  kitId: string;
  kitName: string;
  prompt: string;
  key: number;
};

type Starter = { label: string; prompt: string };

type InventoryItem = {
  id: string;
  name: string;
  description: string;
  filename: string;
  category: string;
  categoryLabel: string;
  status: "installed" | "zip-ready" | "missing";
  helpers: number;
  hasSkill?: boolean;
  kind?: string;
  visual?: boolean;
  starters: Starter[];
};

type Catalog = {
  installedCount: number;
  sourceZipCount: number;
  manifestCount?: number;
  missingCount?: number;
  zipReadyCount?: number;
  kits: NinjaKit[];
  zips: KitSourceZip[];
  inventory?: InventoryItem[];
  byCategory?: Record<string, InventoryItem[]>;
  roots: {
    sources: string;
    installed: string;
    cursorUploads: string;
    windowsHint: string;
  };
};

export function SkillsDashboard() {
  const router = useRouter();
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<string>("all");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [brief, setBrief] = useState("");
  const [showManage, setShowManage] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeRun, setActiveRun] = useState<ActiveRun | null>(null);

  const refresh = useCallback(async () => {
    const res = await fetch("/api/kits");
    const data = (await res.json()) as Catalog;
    startTransition(() => setCatalog(data));
  }, []);

  useEffect(() => {
    let alive = true;
    fetch("/api/kits")
      .then((r) => r.json())
      .then((data: Catalog) => {
        if (!alive) return;
        startTransition(() => {
          setCatalog(data);
        });
      })
      .catch(() => undefined);
    return () => {
      alive = false;
    };
  }, []);

  const inventory = useMemo(() => catalog?.inventory ?? [], [catalog?.inventory]);

  const categories = useMemo(() => {
    const map = new Map<string, string>();
    for (const item of inventory) {
      map.set(item.category, item.categoryLabel);
    }
    return [...map.entries()].sort((a, b) => a[1].localeCompare(b[1]));
  }, [inventory]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return inventory.filter((item) => {
      if (category !== "all" && item.category !== category) return false;
      if (!q) return true;
      return (
        item.id.includes(q) ||
        item.name.toLowerCase().includes(q) ||
        item.description.toLowerCase().includes(q) ||
        item.categoryLabel.toLowerCase().includes(q)
      );
    });
  }, [inventory, query, category]);

  const selected =
    filtered.find((i) => i.id === selectedId) ||
    inventory.find((i) => i.id === selectedId) ||
    filtered[0] ||
    null;

  const activeBrief =
    brief || selected?.starters[0]?.prompt || "";

  function selectSkill(item: InventoryItem) {
    setSelectedId(item.id);
    setBrief(item.starters[0]?.prompt ?? "");
  }

  function runSkill(prompt: string, openInAgent = false) {
    if (!selected) return;
    const text =
      prompt.trim() ||
      selected.starters[0]?.prompt ||
      `Use a skill ${selected.name} (${selected.id}). Responda em português.`;

    // Default: run visually inside the dashboard
    if (!openInAgent) {
      setActiveRun({
        kitId: selected.id,
        kitName: selected.name,
        prompt: text,
        key: Date.now(),
      });
      return;
    }

    // Optional: open standalone agent with prompt in sessionStorage (avoids URL truncation)
    try {
      sessionStorage.setItem(
        "grokish-skill-handoff",
        JSON.stringify({
          kitId: selected.id,
          prompt: text,
          autosend: true,
        }),
      );
    } catch {
      /* ignore */
    }
    router.push(
      `/studio?mode=kits&kit=${encodeURIComponent(selected.id)}&handoff=1`,
    );
  }

  async function onUpload(file: File | null) {
    if (!file) return;
    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      const body = new FormData();
      body.append("file", file);
      const res = await fetch("/api/kits/upload", { method: "POST", body });
      const data = (await res.json()) as {
        ok?: boolean;
        error?: string;
        kit?: NinjaKit;
        filename?: string;
      };
      if (!res.ok || !data.ok) throw new Error(data.error || "Falha no upload");
      setMessage(
        data.kit
          ? `Instalado: ${data.kit.name}`
          : `ZIP salvo: ${data.filename}`,
      );
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro no upload");
    } finally {
      setBusy(false);
    }
  }

  async function installAll() {
    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      const res = await fetch("/api/kits/install", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ all: true }),
      });
      const data = (await res.json()) as {
        ok?: boolean;
        error?: string;
        installed?: NinjaKit[];
        errors?: Array<{ path: string; error: string }>;
        scanned?: number;
      };
      if (!res.ok || data.ok === false) {
        throw new Error(data.error || "Falha na instalação");
      }
      setMessage(
        `Instalados ${data.installed?.length ?? 0} de ${data.scanned ?? 0} ZIPs`,
      );
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao instalar");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="relative min-h-full flex-1 overflow-hidden">
      <div className="pointer-events-none absolute inset-0 atmosphere" aria-hidden />
      <div className="pointer-events-none absolute inset-0 grid-fade" aria-hidden />

      <div className="relative z-10 mx-auto flex h-[100dvh] w-full max-w-7xl flex-col px-4 py-5 md:px-6">
        <header className="mb-4 flex flex-wrap items-end justify-between gap-3 animate-rise">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <Link
                href="/"
                className="text-xs uppercase tracking-[0.18em] text-[var(--muted)]"
              >
                ← Grokish
              </Link>
              <span className="text-xs text-[var(--muted)]">/</span>
              <p className="text-xs uppercase tracking-[0.18em] text-[var(--accent-ink)]">
                Painel de Skills
              </p>
            </div>
            <h1 className="mt-2 font-display text-3xl tracking-tight text-[var(--ink)] md:text-4xl">
              Skills Ninja
            </h1>
            <p className="mt-1 max-w-xl text-sm text-[var(--muted)]">
              Escolha a skill, ajuste o brief (ou o painel visual) e execute —{" "}
              {catalog?.manifestCount ?? "…"} skills disponíveis.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setShowManage((v) => !v)}
              className="rounded-lg border border-[var(--line)] bg-[var(--panel)]/80 px-3 py-2 text-sm text-[var(--ink)]"
            >
              {showManage ? "Fechar gestão" : "Gestão de ZIPs"}
            </button>
            <Link
              href="/editor"
              className="rounded-lg border border-[var(--line)] px-3 py-2 text-sm text-[var(--ink)]"
            >
              Editor EDVD
            </Link>
          </div>
        </header>

        {message ? (
          <p className="mb-3 rounded-lg border border-[var(--line)] bg-[var(--chip)] px-3 py-2 text-sm text-[var(--accent-ink)]">
            {message}
          </p>
        ) : null}
        {error ? (
          <p className="mb-3 rounded-lg border border-red-300/40 bg-red-50 px-3 py-2 text-sm text-red-800">
            {error}
          </p>
        ) : null}

        {showManage ? (
          <ManagePanel
            catalog={catalog}
            busy={busy}
            onUpload={onUpload}
            onInstallAll={installAll}
            onRefresh={() => void refresh()}
          />
        ) : null}

        <div
          className={`grid min-h-0 flex-1 gap-4 ${
            activeRun
              ? "lg:grid-cols-[minmax(240px,320px)_minmax(0,1fr)]"
              : selected?.visual
                ? "lg:grid-cols-[minmax(0,0.9fr)_minmax(360px,460px)]"
                : "lg:grid-cols-[minmax(0,1fr)_minmax(320px,400px)]"
          }`}
        >
          <section
            className={`flex min-h-0 flex-col animate-rise ${
              activeRun ? "hidden md:flex" : ""
            }`}
          >
            <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-center">
              <label className="relative min-w-0 flex-1">
                <span className="sr-only">Buscar skills</span>
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Buscar por nome, categoria ou objetivo…"
                  className="w-full rounded-xl border border-[var(--line)] bg-[var(--panel)]/90 px-3 py-2.5 text-sm text-[var(--ink)] outline-none ring-[var(--accent)] focus:ring-2"
                />
              </label>
              <p className="shrink-0 text-xs text-[var(--muted)]">
                {filtered.length} skill{filtered.length === 1 ? "" : "s"}
              </p>
            </div>

            <div className="mb-3 flex gap-1.5 overflow-x-auto pb-1">
              <CategoryChip
                active={category === "all"}
                onClick={() => setCategory("all")}
                label="Todas"
              />
              {categories.map(([id, label]) => (
                <CategoryChip
                  key={id}
                  active={category === id}
                  onClick={() => setCategory(id)}
                  label={label}
                />
              ))}
            </div>

            <ul className="min-h-0 flex-1 space-y-1.5 overflow-y-auto pr-1">
              {filtered.map((item, index) => {
                const active = selected?.id === item.id;
                return (
                  <li key={item.id}>
                    <button
                      type="button"
                      onClick={() => selectSkill(item)}
                      style={{ animationDelay: `${Math.min(index, 12) * 30}ms` }}
                      className={`animate-rise w-full rounded-xl border px-3 py-2.5 text-left transition ${
                        active
                          ? "border-[var(--accent)] bg-[var(--panel)] shadow-[0_0_0_1px_var(--accent)]"
                          : "border-[var(--line)] bg-[var(--panel)] hover:border-[var(--accent)]/50 hover:bg-[color:var(--dd-elevated)]"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0">
                          <p className="truncate text-sm font-semibold text-[var(--ink)]">
                            {item.name}
                          </p>
                          <p className="mt-0.5 line-clamp-1 text-xs text-[var(--muted)]">
                            {item.description}
                          </p>
                        </div>
                        <div className="flex shrink-0 flex-col items-end gap-1">
                          <span className="text-[10px] uppercase tracking-[0.12em] text-[var(--muted)]">
                            {item.categoryLabel}
                          </span>
                          <div className="flex items-center gap-1">
                            {item.visual ? (
                              <span className="rounded bg-[var(--chip)] px-1 py-0.5 text-[9px] text-[var(--accent-ink)]">
                                Visual
                              </span>
                            ) : null}
                            <StatusDot status={item.status} />
                          </div>
                        </div>
                      </div>
                    </button>
                  </li>
                );
              })}
              {!filtered.length ? (
                <li className="rounded-xl border border-dashed border-[var(--line)] px-4 py-10 text-center text-sm text-[var(--muted)]">
                  Nenhuma skill encontrada para “{query}”.
                </li>
              ) : null}
            </ul>
          </section>

          {activeRun ? (
            <SkillRunner
              key={activeRun.key}
              runId={activeRun.key}
              kitId={activeRun.kitId}
              kitName={activeRun.kitName}
              prompt={activeRun.prompt}
              onClose={() => setActiveRun(null)}
            />
          ) : (
            <aside className="flex min-h-0 flex-col rounded-2xl border border-[var(--line)] bg-[var(--panel)]/90 p-4 animate-rise backdrop-blur md:p-5">
              {selected ? (
                <>
                  <div className="mb-3 shrink-0">
                    <p className="text-[10px] uppercase tracking-[0.16em] text-[var(--muted)]">
                      {selected.categoryLabel}
                    </p>
                    <h2 className="mt-1 font-display text-2xl text-[var(--ink)]">
                      {selected.name}
                    </h2>
                    <p className="mt-2 text-sm leading-relaxed text-[var(--muted)]">
                      {selected.description}
                    </p>
                    <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
                      <StatusDot status={selected.status} withLabel />
                      {selected.visual ? (
                        <span className="rounded-md bg-[var(--chip)] px-2 py-0.5 text-[var(--accent-ink)]">
                          Painel visual
                        </span>
                      ) : null}
                      {selected.hasSkill ? (
                        <span className="rounded-md bg-[var(--chip)] px-2 py-0.5 text-[var(--accent-ink)]">
                          Skill instalada
                        </span>
                      ) : null}
                      {selected.helpers > 0 ? (
                        <span className="rounded-md bg-[var(--chip)] px-2 py-0.5 text-[var(--accent-ink)]">
                          {selected.helpers} auxiliares
                        </span>
                      ) : null}
                    </div>
                  </div>

                  {selected.visual ? (
                    <VisualEditPanel
                      key={selected.id}
                      kitId={selected.id}
                      kitName={selected.name}
                      extraBrief={brief}
                      onExtraBriefChange={setBrief}
                      onRun={(prompt, inDashboard) =>
                        runSkill(prompt, !inDashboard)
                      }
                    />
                  ) : (
                    <>
                      <div className="mb-3">
                        <p className="mb-1.5 text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">
                          Atalhos
                        </p>
                        <div className="flex flex-wrap gap-1.5">
                          {selected.starters.map((s) => (
                            <button
                              key={s.label}
                              type="button"
                              onClick={() => setBrief(s.prompt)}
                              className="rounded-lg border border-[var(--line)] bg-[var(--panel)] px-2.5 py-1 text-xs text-[var(--ink)] hover:border-[var(--accent)]"
                            >
                              {s.label}
                            </button>
                          ))}
                        </div>
                      </div>

                      <label className="flex min-h-0 flex-1 flex-col">
                        <span className="mb-1.5 text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">
                          Pedido
                        </span>
                        <textarea
                          value={activeBrief}
                          onChange={(e) => setBrief(e.target.value)}
                          rows={8}
                          className="min-h-[140px] flex-1 resize-none rounded-xl border border-[var(--line)] bg-[var(--panel)] px-3 py-2.5 text-sm leading-relaxed text-[var(--ink)] outline-none ring-[var(--accent)] focus:ring-2"
                          placeholder="Descreva o que precisa. Troque os [placeholders] pelos seus dados."
                        />
                      </label>

                      <div className="mt-3 flex flex-col gap-2">
                        <button
                          type="button"
                          onClick={() => runSkill(activeBrief, false)}
                          className="rounded-xl bg-[var(--ink)] px-4 py-3 text-sm font-semibold text-[var(--panel)] transition hover:brightness-110"
                        >
                          Executar no painel →
                        </button>
                        <button
                          type="button"
                          onClick={() => runSkill(activeBrief, true)}
                          className="rounded-xl border border-[var(--line)] px-4 py-2.5 text-sm text-[var(--ink)]"
                        >
                          Abrir no agente completo
                        </button>
                      </div>
                    </>
                  )}

                  {selected.id.includes("video") || selected.kind === "video" ? (
                    <Link
                      href="/editor"
                      className="mt-2 rounded-xl border border-[var(--line)] px-4 py-2.5 text-center text-sm text-[var(--ink)]"
                    >
                      Abrir Editor EDVD
                    </Link>
                  ) : null}
                </>
              ) : (
                <div className="flex flex-1 items-center justify-center text-sm text-[var(--muted)]">
                  Selecione uma skill à esquerda.
                </div>
              )}
            </aside>
          )}
        </div>
      </div>
    </div>
  );
}

function CategoryChip({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`shrink-0 rounded-lg px-2.5 py-1 text-xs transition ${
        active
          ? "bg-[var(--ink)] font-semibold text-[var(--panel)]"
          : "border border-[var(--line)] bg-[var(--panel)]/70 text-[var(--muted)] hover:text-[var(--ink)]"
      }`}
    >
      {label}
    </button>
  );
}

function StatusDot({
  status,
  withLabel,
}: {
  status: InventoryItem["status"];
  withLabel?: boolean;
}) {
  const map = {
    installed: { cls: "bg-emerald-500", label: "Pronta" },
    "zip-ready": { cls: "bg-amber-500", label: "ZIP pronto" },
    missing: { cls: "bg-slate-400", label: "Modo persona" },
  } as const;
  const item = map[status];
  if (withLabel) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-md bg-[var(--panel)] px-2 py-0.5 text-[var(--ink)]">
        <span className={`h-1.5 w-1.5 rounded-sm ${item.cls}`} />
        {item.label}
      </span>
    );
  }
  return (
    <span
      title={item.label}
      className={`mt-1 h-1.5 w-1.5 rounded-sm ${item.cls}`}
    />
  );
}

function ManagePanel({
  catalog,
  busy,
  onUpload,
  onInstallAll,
  onRefresh,
}: {
  catalog: Catalog | null;
  busy: boolean;
  onUpload: (file: File | null) => Promise<void>;
  onInstallAll: () => Promise<void>;
  onRefresh: () => void;
}) {
  return (
    <section className="mb-4 rounded-2xl border border-[var(--line)] bg-[var(--panel)]/85 p-4 animate-rise">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div>
          <h2 className="text-sm font-semibold text-[var(--ink)]">Gestão de ZIPs</h2>
          <p className="text-xs text-[var(--muted)]">
            Instalados {catalog?.installedCount ?? 0} · ZIP pronto{" "}
            {catalog?.zipReadyCount ?? 0} · faltando {catalog?.missingCount ?? 0}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <label className="cursor-pointer rounded-lg bg-[var(--ink)] px-3 py-1.5 text-xs font-semibold text-[var(--panel)]">
            {busy ? "Processando…" : "Upload ZIP"}
            <input
              type="file"
              accept=".zip,application/zip"
              className="hidden"
              disabled={busy}
              multiple
              onChange={(e) => {
                const files = e.target.files;
                if (!files?.length) return;
                void (async () => {
                  for (const f of Array.from(files)) await onUpload(f);
                })();
              }}
            />
          </label>
          <button
            type="button"
            disabled={busy}
            onClick={() => void onInstallAll()}
            className="rounded-lg border border-[var(--line)] px-3 py-1.5 text-xs text-[var(--ink)]"
          >
            Instalar todos
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={onRefresh}
            className="rounded-lg border border-[var(--line)] px-3 py-1.5 text-xs text-[var(--muted)]"
          >
            Atualizar
          </button>
        </div>
      </div>
      {catalog?.zips?.length ? (
        <ul className="max-h-40 space-y-1 overflow-y-auto text-xs text-[var(--muted)]">
          {catalog.zips.map((z) => (
            <li key={z.path} className="truncate font-mono">
              {z.filename} · {(z.size / (1024 * 1024)).toFixed(2)} MB
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-xs text-[var(--muted)]">Nenhum ZIP na fila de sources/uploads.</p>
      )}
    </section>
  );
}
