"use client";

import Link from "next/link";
import { useCallback, useEffect, useState, startTransition } from "react";
import type { KitSourceZip, NinjaKit } from "@/lib/kits/types";

type Catalog = {
  installedCount: number;
  sourceZipCount: number;
  kits: NinjaKit[];
  zips: KitSourceZip[];
  roots: {
    sources: string;
    installed: string;
    cursorUploads: string;
    windowsHint: string;
  };
};

const KIND_LABEL: Record<string, string> = {
  video: "Vídeo",
  skill: "Skill",
  automation: "Automação",
  design: "Design",
  course: "Curso",
  unknown: "Kit",
};

export function KitsHub() {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

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
        startTransition(() => setCatalog(data));
      })
      .catch(() => undefined);
    return () => {
      alive = false;
    };
  }, []);

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
      if (!res.ok || !data.ok) {
        throw new Error(data.error || "Falha no upload");
      }
      setMessage(
        data.kit
          ? `Instalado: ${data.kit.name} (${data.kit.id})`
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
        `Instalados ${data.installed?.length ?? 0} de ${data.scanned ?? 0} ZIPs` +
          (data.errors?.length ? ` · ${data.errors.length} erro(s)` : ""),
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

      <div className="relative z-10 mx-auto w-full max-w-4xl px-5 py-8">
        <header className="mb-8 flex flex-wrap items-end justify-between gap-4">
          <div>
            <Link
              href="/"
              className="text-xs uppercase tracking-[0.18em] text-[var(--muted)]"
            >
              ← Grokish
            </Link>
            <h1 className="mt-2 font-display text-4xl tracking-tight text-[var(--ink)] md:text-5xl">
              Ninja Kits
            </h1>
            <p className="mt-2 max-w-xl text-sm leading-relaxed text-[var(--muted)]">
              Importe cada ZIP de <code className="text-[var(--ink)]">F:\NINJA CURSOS</code>{" "}
              e o sistema registra skill, helpers e agente dedicado.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <label className="cursor-pointer rounded-lg bg-[var(--ink)] px-3 py-2 text-sm font-semibold text-[var(--panel)]">
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
                    for (const f of Array.from(files)) {
                      await onUpload(f);
                    }
                  })();
                }}
              />
            </label>
            <button
              type="button"
              disabled={busy}
              onClick={() => void installAll()}
              className="rounded-lg border border-[var(--line)] bg-[var(--panel)] px-3 py-2 text-sm text-[var(--ink)] disabled:opacity-40"
            >
              Instalar todos os ZIPs
            </button>
            <button
              type="button"
              disabled={busy}
              onClick={() => void refresh()}
              className="rounded-lg border border-[var(--line)] px-3 py-2 text-sm text-[var(--muted)]"
            >
              Atualizar
            </button>
          </div>
        </header>

        {message ? (
          <p className="mb-4 rounded-xl border border-[var(--line)] bg-[var(--chip)] px-3 py-2 text-sm text-[var(--accent-ink)]">
            {message}
          </p>
        ) : null}
        {error ? (
          <p className="mb-4 rounded-xl border border-red-300/40 bg-red-50 px-3 py-2 text-sm text-red-800">
            {error}
          </p>
        ) : null}

        <section className="mb-8 grid gap-3 sm:grid-cols-3">
          <Stat
            label="Kits instalados"
            value={String(catalog?.installedCount ?? "—")}
          />
          <Stat
            label="ZIPs na fila"
            value={String(catalog?.sourceZipCount ?? "—")}
          />
          <Stat
            label="Pasta Windows"
            value={catalog?.roots.windowsHint ?? "F:\\NINJA CURSOS"}
            small
          />
        </section>

        <section className="mb-10">
          <h2 className="mb-3 text-xs uppercase tracking-[0.18em] text-[var(--muted)]">
            Instalados
          </h2>
          {!catalog?.kits.length ? (
            <Empty
              title="Nenhum kit ainda"
              body="Envie os ZIPs de F:\NINJA CURSOS. O kit de edição de vídeo do repo já deve aparecer como seeded."
            />
          ) : (
            <div className="grid gap-3 md:grid-cols-2">
              {catalog.kits.map((kit) => (
                <article
                  key={kit.id}
                  className="rounded-2xl border border-[var(--line)] bg-[var(--panel)]/90 p-4"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="text-[10px] uppercase tracking-[0.16em] text-[var(--muted)]">
                        {KIND_LABEL[kit.kind] || kit.kind} · {kit.status}
                      </p>
                      <h3 className="mt-1 font-display text-xl text-[var(--ink)]">
                        {kit.name}
                      </h3>
                    </div>
                    <span className="rounded-md bg-[var(--chip)] px-2 py-1 font-mono text-[10px] text-[var(--accent-ink)]">
                      {kit.id}
                    </span>
                  </div>
                  <p className="mt-2 line-clamp-3 text-sm text-[var(--muted)]">
                    {kit.description || "Sem descrição no SKILL.md"}
                  </p>
                  <p className="mt-3 text-xs text-[var(--muted)]">
                    {kit.helpers.length} helpers
                    {kit.hasPythonVenv ? " · venv" : ""}
                    {kit.skillPath ? " · SKILL.md" : ""}
                  </p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    <Link
                      href={`/?mode=kits&kit=${encodeURIComponent(kit.id)}`}
                      className="rounded-lg bg-[var(--ink)] px-3 py-1.5 text-xs font-semibold text-[var(--panel)]"
                    >
                      Abrir no agente
                    </Link>
                    {kit.kind === "video" ? (
                      <Link
                        href="/editor"
                        className="rounded-lg border border-[var(--line)] px-3 py-1.5 text-xs text-[var(--ink)]"
                      >
                        Editor EDVD
                      </Link>
                    ) : null}
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        <section>
          <h2 className="mb-3 text-xs uppercase tracking-[0.18em] text-[var(--muted)]">
            ZIPs detectados (sources + uploads)
          </h2>
          {!catalog?.zips.length ? (
            <Empty
              title="Fila vazia"
              body="Copie os .zip de F:\NINJA CURSOS para ninja-kits/sources/ ou faça upload aqui / anexe na conversa do agente."
            />
          ) : (
            <ul className="space-y-2">
              {catalog.zips.map((z) => (
                <li
                  key={z.path}
                  className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-[var(--line)] bg-[var(--panel)]/70 px-3 py-2 text-sm"
                >
                  <div>
                    <p className="font-medium text-[var(--ink)]">{z.filename}</p>
                    <p className="font-mono text-[11px] text-[var(--muted)]">
                      {(z.size / (1024 * 1024)).toFixed(2)} MB · {z.path}
                    </p>
                  </div>
                  <button
                    type="button"
                    disabled={busy}
                    onClick={() => {
                      void (async () => {
                        setBusy(true);
                        setError(null);
                        try {
                          const res = await fetch("/api/kits/install", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ zipPath: z.path }),
                          });
                          const data = (await res.json()) as {
                            ok?: boolean;
                            error?: string;
                            kit?: NinjaKit;
                          };
                          if (!res.ok || !data.ok) {
                            throw new Error(data.error || "Falha");
                          }
                          setMessage(`Instalado: ${data.kit?.name}`);
                          await refresh();
                        } catch (err) {
                          setError(
                            err instanceof Error ? err.message : "Erro",
                          );
                        } finally {
                          setBusy(false);
                        }
                      })();
                    }}
                    className="rounded-lg border border-[var(--line)] px-3 py-1.5 text-xs text-[var(--ink)]"
                  >
                    Instalar
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}

function Stat({
  label,
  value,
  small,
}: {
  label: string;
  value: string;
  small?: boolean;
}) {
  return (
    <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)]/80 px-4 py-3">
      <p className="text-[10px] uppercase tracking-[0.16em] text-[var(--muted)]">
        {label}
      </p>
      <p
        className={`mt-1 font-display text-[var(--ink)] ${
          small ? "text-base break-all" : "text-3xl"
        }`}
      >
        {value}
      </p>
    </div>
  );
}

function Empty({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-2xl border border-dashed border-[var(--line)] px-4 py-8 text-center">
      <p className="font-medium text-[var(--ink)]">{title}</p>
      <p className="mx-auto mt-2 max-w-md text-sm text-[var(--muted)]">{body}</p>
    </div>
  );
}
