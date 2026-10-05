"use client";

import { useMemo, useState } from "react";
import type { EditorProject } from "@/lib/editor/project-types";
import {
  STYLE_LABELS,
  VIDEO_STYLES,
  type VideoStyle,
} from "@/lib/video/options";

type Props = {
  projects: EditorProject[];
  busy?: boolean;
  onOpen: (projectId: string) => void;
  onCreate: (input: { name: string; estilo: VideoStyle }) => void;
  onDelete: (projectId: string) => void;
};

export function ProjectHub({
  projects,
  busy,
  onOpen,
  onCreate,
  onDelete,
}: Props) {
  const [name, setName] = useState("");
  const [estilo, setEstilo] = useState<VideoStyle>("reel-mono");
  const [filter, setFilter] = useState("");

  const filtered = useMemo(() => {
    const q = filter.trim().toLowerCase();
    if (!q) return projects;
    return projects.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.estilo.toLowerCase().includes(q) ||
        STYLE_LABELS[p.estilo].toLowerCase().includes(q) ||
        p.slug.toLowerCase().includes(q),
    );
  }, [filter, projects]);

  return (
    <div className="flex flex-1 flex-col gap-6 px-4 py-6">
      <div className="max-w-3xl">
        <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-[color:var(--muted-foreground)]">
          Editor Nexus
        </p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight text-[color:var(--foreground)]">
          Projetos de edição
        </h1>
        <p className="mt-2 text-sm text-[color:var(--muted-foreground)]">
          Cada projeto guarda o estilo e as preferências de edição (formato,
          fonte, grade, som, takes). Abra um para editar sem misturar com os
          outros.
        </p>
      </div>

      <form
        className="grid gap-3 rounded-xl border border-[color:var(--border)] bg-[color:var(--background)]/50 p-4 sm:grid-cols-[1fr_220px_auto]"
        onSubmit={(e) => {
          e.preventDefault();
          onCreate({
            name: name.trim() || STYLE_LABELS[estilo],
            estilo,
          });
          setName("");
        }}
      >
        <label className="flex flex-col gap-1 text-[10px] uppercase tracking-wider text-[color:var(--muted-foreground)]">
          Novo projeto
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Ex.: Reels da semana"
            className="rounded-lg border border-[color:var(--border)] bg-[color:var(--card)] px-3 py-2 text-sm text-[color:var(--foreground)] outline-none ring-[color:var(--primary)] focus:ring-2"
          />
        </label>
        <label className="flex flex-col gap-1 text-[10px] uppercase tracking-wider text-[color:var(--muted-foreground)]">
          Estilo de edição
          <select
            value={estilo}
            onChange={(e) => setEstilo(e.target.value as VideoStyle)}
            className="rounded-lg border border-[color:var(--border)] bg-[color:var(--card)] px-3 py-2 text-sm text-[color:var(--foreground)]"
          >
            {VIDEO_STYLES.map((s) => (
              <option key={s} value={s}>
                {STYLE_LABELS[s]}
              </option>
            ))}
          </select>
        </label>
        <div className="flex items-end">
          <button
            type="submit"
            disabled={busy}
            className="w-full rounded-lg bg-[color:var(--primary)] px-4 py-2 text-sm font-semibold text-[color:var(--primary-foreground)] disabled:opacity-40 sm:w-auto"
          >
            Criar projeto
          </button>
        </div>
      </form>

      <div className="flex items-center gap-3">
        <input
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Filtrar por nome ou estilo…"
          className="min-w-0 flex-1 rounded-lg border border-[color:var(--border)] bg-[color:var(--background)] px-3 py-2 text-sm text-[color:var(--foreground)] outline-none ring-[color:var(--primary)] placeholder:text-[color:var(--muted-foreground)] focus:ring-2"
        />
        <span className="shrink-0 text-xs text-[color:var(--muted-foreground)]">
          {filtered.length} projeto{filtered.length === 1 ? "" : "s"}
        </span>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {filtered.map((project) => (
          <article
            key={project.id}
            className="flex flex-col gap-3 rounded-xl border border-[color:var(--border)] bg-[color:var(--card)] p-4 transition-colors hover:border-[color:var(--primary)]/40"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <h2 className="truncate text-base font-semibold text-[color:var(--foreground)]">
                  {project.name}
                </h2>
                <p className="mt-1 text-xs text-[color:var(--muted-foreground)]">
                  {STYLE_LABELS[project.estilo]} · {project.options.formato}
                </p>
              </div>
              <span className="shrink-0 rounded-md bg-[color:var(--muted)]/50 px-2 py-1 font-mono text-[10px] uppercase text-[color:var(--muted-foreground)]">
                {project.slug}
              </span>
            </div>

            <dl className="grid grid-cols-2 gap-x-3 gap-y-1 text-[11px] text-[color:var(--muted-foreground)]">
              <div>
                <dt className="uppercase tracking-wider opacity-70">Fonte</dt>
                <dd className="text-[color:var(--foreground)]/85">
                  {project.options.fonte}
                </dd>
              </div>
              <div>
                <dt className="uppercase tracking-wider opacity-70">Grade</dt>
                <dd className="text-[color:var(--foreground)]/85">
                  {project.options.grade}
                </dd>
              </div>
              <div>
                <dt className="uppercase tracking-wider opacity-70">Mídia</dt>
                <dd className="truncate text-[color:var(--foreground)]/85">
                  {project.mediaFilename || "Sem arquivo"}
                </dd>
              </div>
              <div>
                <dt className="uppercase tracking-wider opacity-70">Takes</dt>
                <dd className="text-[color:var(--foreground)]/85">
                  {project.takes.length}
                </dd>
              </div>
            </dl>

            <div className="mt-auto flex items-center gap-2 pt-1">
              <button
                type="button"
                disabled={busy}
                onClick={() => onOpen(project.id)}
                className="flex-1 rounded-lg bg-[color:var(--primary)] px-3 py-2 text-sm font-semibold text-[color:var(--primary-foreground)] disabled:opacity-40"
              >
                Abrir edição
              </button>
              <button
                type="button"
                disabled={busy}
                title="Excluir projeto"
                onClick={() => onDelete(project.id)}
                className="rounded-lg border border-[color:var(--border)] px-3 py-2 text-sm text-[color:var(--muted-foreground)] disabled:opacity-40"
              >
                Excluir
              </button>
            </div>
          </article>
        ))}
      </div>

      {filtered.length === 0 ? (
        <p className="text-sm text-[color:var(--muted-foreground)]">
          Nenhum projeto com esse filtro. Crie um novo acima.
        </p>
      ) : null}
    </div>
  );
}
