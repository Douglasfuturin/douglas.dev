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

export function SkillsDashboard({ embedded = false }: { embedded?: boolean }) {
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
          setSelectedId((prev) => {
            if (prev) return prev;
            const first = data.inventory?.[0];
            if (first) {
              setBrief(first.starters[0]?.prompt ?? "");
              return first.id;
            }
            return prev;
          });
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
      `/ferramentas/studio?mode=kits&kit=${encodeURIComponent(selected.id)}&handoff=1`,
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
    <div className="nexus-skills-workspace relative w-full">
      {!embedded ? (
        <header className="mb-6 flex flex-wrap items-end justify-between gap-3">
          <div>
            <Link
              href="/ferramentas"
              className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[color:var(--muted-foreground)]"
            >
              ← Ferramentas
            </Link>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-[color:var(--foreground)]">
              Skills
            </h1>
            <p className="mt-1 text-sm text-[color:var(--muted-foreground)]">
              {catalog?.manifestCount ?? "…"} skills · escolha, ajuste o brief e execute
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setShowManage((v) => !v)}
              className="nexus-btn-ghost !py-2 text-sm"
            >
              {showManage ? "Fechar gestão" : "Gestão de ZIPs"}
            </button>
            <Link href="/ferramentas/editor" className="nexus-btn-ghost !py-2 text-sm">
              Editor
            </Link>
          </div>
        </header>
      ) : (
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-[color:var(--muted-foreground)]">
            {filtered.length} de {catalog?.manifestCount ?? "…"} skills
          </p>
          <button
            type="button"
            onClick={() => setShowManage((v) => !v)}
            className="nexus-btn-ghost !py-1.5 text-xs"
          >
            {showManage ? "Fechar gestão" : "Gestão de ZIPs"}
          </button>
        </div>
      )}

      {message ? (
        <p className="mb-3 rounded-lg border border-[color:var(--border)] bg-[color:var(--chip)] px-3 py-2 text-sm">
          {message}
        </p>
      ) : null}
      {error ? (
        <p className="mb-3 rounded-lg border border-red-400/30 bg-red-500/10 px-3 py-2 text-sm text-red-200">
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

      <section className="nexus-panel mb-6 space-y-4">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[color:var(--muted-foreground)]">
              {selected?.categoryLabel || "Skill"}
            </p>
            <h2 className="mt-1 text-xl font-semibold text-[color:var(--foreground)]">
              {selected?.name || "Escolha uma skill"}
            </h2>
            {selected ? (
              <p className="mt-2 text-sm leading-relaxed text-[color:var(--muted-foreground)]">
                {selected.description}
              </p>
            ) : null}
            {selected ? (
              <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
                <StatusDot status={selected.status} withLabel />
                {selected.hasSkill ? (
                  <span className="nexus-tag">Skill instalada</span>
                ) : null}
                {selected.visual ? (
                  <span className="nexus-tag">Painel visual</span>
                ) : null}
              </div>
            ) : null}
          </div>
          <label className="block min-w-[200px] shrink-0">
            <span className="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.12em] text-[color:var(--muted-foreground)]">
              Escolher skill
            </span>
            <select
              className="nexus-field w-full min-w-[220px]"
              value={selected?.id || ""}
              onChange={(e) => {
                const item = inventory.find((i) => i.id === e.target.value);
                if (item) selectSkill(item);
              }}
            >
              {!inventory.length ? (
                <option value="">Carregando…</option>
              ) : (
                inventory.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.categoryLabel} · {item.name}
                  </option>
                ))
              )}
            </select>
          </label>
        </div>

        {selected?.visual ? (
          <VisualEditPanel
            key={selected.id}
            kitId={selected.id}
            kitName={selected.name}
            extraBrief={brief}
            onExtraBriefChange={setBrief}
            onRun={(prompt, inDashboard) => runSkill(prompt, !inDashboard)}
          />
        ) : (
          <>
            {selected?.starters?.length ? (
              <div>
                <p className="mb-1.5 text-[11px] font-semibold uppercase tracking-[0.12em] text-[color:var(--muted-foreground)]">
                  Atalhos
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {selected.starters.map((s) => (
                    <button
                      key={s.label}
                      type="button"
                      onClick={() => setBrief(s.prompt)}
                      className="nexus-chip"
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
              </div>
            ) : null}

            <label className="block">
              <span className="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.12em] text-[color:var(--muted-foreground)]">
                Pedido
              </span>
              <textarea
                value={activeBrief}
                onChange={(e) => setBrief(e.target.value)}
                rows={4}
                className="nexus-field w-full resize-y !rounded-xl"
                placeholder="Escreva o comando. Troque os [placeholders] pelos seus dados."
              />
            </label>

            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={!selected}
                onClick={() => runSkill(activeBrief, false)}
                className="nexus-btn-primary disabled:opacity-40"
              >
                Executar no painel →
              </button>
              <button
                type="button"
                disabled={!selected}
                onClick={() => runSkill(activeBrief, true)}
                className="nexus-btn-ghost disabled:opacity-40"
              >
                Abrir no Studio
              </button>
              {selected?.id.includes("video") || selected?.kind === "video" ? (
                <Link href="/ferramentas/editor" className="nexus-btn-ghost">
                  Editor de vídeo
                </Link>
              ) : null}
            </div>
          </>
        )}
      </section>

      {activeRun ? (
        <div className="nexus-panel mb-6 !p-0">
          <SkillRunner
            key={activeRun.key}
            runId={activeRun.key}
            kitId={activeRun.kitId}
            kitName={activeRun.kitName}
            prompt={activeRun.prompt}
            onClose={() => setActiveRun(null)}
          />
        </div>
      ) : null}

      <div className="space-y-4">
        <div className="flex flex-col gap-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--muted-foreground)]">
              Biblioteca
            </p>
            <p className="text-xs text-[color:var(--muted-foreground)]">
              {filtered.length} skill{filtered.length === 1 ? "" : "s"}
            </p>
          </div>
          <label className="relative block">
            <span className="sr-only">Buscar skills</span>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Buscar por nome, categoria ou objetivo…"
              className="nexus-field w-full !py-2.5"
            />
          </label>
          <div className="flex flex-wrap gap-1.5">
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
        </div>

        <ul className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {filtered.map((item) => {
            const active = selected?.id === item.id;
            return (
              <li key={item.id}>
                <button
                  type="button"
                  onClick={() => selectSkill(item)}
                  className={`nexus-skill-tile w-full text-left ${active ? "nexus-skill-tile-on" : ""}`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-[color:var(--foreground)]">
                        {item.name}
                      </p>
                      <p className="mt-1 line-clamp-2 text-xs leading-relaxed text-[color:var(--muted-foreground)]">
                        {item.description}
                      </p>
                    </div>
                    <StatusDot status={item.status} />
                  </div>
                  <div className="mt-3 flex flex-wrap items-center gap-1.5">
                    <span className="nexus-tag-muted nexus-tag">
                      {item.categoryLabel}
                    </span>
                    {item.visual ? <span className="nexus-tag">Visual</span> : null}
                  </div>
                </button>
              </li>
            );
          })}
          {!filtered.length ? (
            <li className="col-span-full rounded-xl border border-dashed border-[color:var(--border)] px-4 py-12 text-center text-sm text-[color:var(--muted-foreground)]">
              Nenhuma skill encontrada para “{query}”.
            </li>
          ) : null}
        </ul>
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
      className={`nexus-chip ${active ? "nexus-chip-on" : ""}`}
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
        <ul className="space-y-1 text-xs text-[color:var(--muted-foreground)]">
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
