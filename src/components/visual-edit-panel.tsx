"use client";

import { useMemo, useState, type ReactNode } from "react";
import {
  buildVisualPrompt,
  defaultVisualDraft,
  visualConfigFor,
  VISUAL_KIND_LABEL,
  type VisualDraft,
} from "@/lib/kits/visual";

type Props = {
  kitId: string;
  kitName: string;
  extraBrief: string;
  onExtraBriefChange: (value: string) => void;
  /** inDashboard=true executa no painel; false abre o agente completo */
  onRun: (prompt: string, inDashboard: boolean) => void;
};

const inputClass =
  "w-full rounded-xl border border-[var(--line)] bg-white/80 px-3 py-2 text-sm text-[var(--ink)] outline-none focus:ring-2 focus:ring-[var(--accent)]";

export function VisualEditPanel({
  kitId,
  kitName,
  extraBrief,
  onExtraBriefChange,
  onRun,
}: Props) {
  const config = visualConfigFor(kitId);
  const [draft, setDraft] = useState<VisualDraft>(
    () =>
      defaultVisualDraft(kitId) ?? {
        aspectId: "1:1",
        styleId: "bold-dark",
        headline: "",
        subheadline: "",
        topic: "",
        slides: 6,
        variations: 4,
      },
  );

  const style = useMemo(
    () =>
      config?.styles.find((s) => s.id === draft.styleId) ?? config?.styles[0],
    [config, draft.styleId],
  );
  const aspect = useMemo(
    () =>
      config?.aspects.find((a) => a.id === draft.aspectId) ?? config?.aspects[0],
    [config, draft.aspectId],
  );

  if (!config || !style || !aspect) return null;

  const previewPrompt = buildVisualPrompt(kitId, kitName, draft, extraBrief);

  function patch<K extends keyof VisualDraft>(key: K, value: VisualDraft[K]) {
    setDraft((prev) => ({ ...prev, [key]: value }));
  }

  const previewMaxW = aspect.ratio >= 1 ? 280 : 180;
  const previewH = Math.max(120, Math.min(previewMaxW / aspect.ratio, 320));

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">
          Painel visual · {VISUAL_KIND_LABEL[config.kind]}
        </p>
        <span className="rounded-md bg-[var(--chip)] px-2 py-0.5 text-[11px] text-[var(--accent-ink)]">
          Edição visual
        </span>
      </div>

      <div className="flex justify-center rounded-xl border border-[var(--line)] bg-slate-900/5 p-4">
        <div
          className="relative overflow-hidden rounded-lg shadow-lg transition-all duration-300"
          style={{
            width: previewMaxW,
            height: previewH,
            background: style.bg,
            color: style.fg,
          }}
        >
          <div
            className="pointer-events-none absolute inset-0 opacity-30"
            style={{
              backgroundImage:
                "radial-gradient(circle at 20% 15%, rgba(255,255,255,0.25), transparent 45%)",
            }}
          />
          <div className="relative flex h-full flex-col justify-between p-3">
            <p
              className="text-[10px] uppercase tracking-[0.16em]"
              style={{ color: style.accent }}
            >
              {aspect.label} · {style.label}
            </p>
            <div>
              <p
                className="font-display leading-tight"
                style={{
                  fontSize: draft.headline.length > 28 ? 14 : 18,
                  wordBreak: "break-word",
                }}
              >
                {draft.headline.trim() || "Seu título aqui"}
              </p>
              {draft.subheadline.trim() || draft.topic.trim() ? (
                <p className="mt-1 text-xs leading-snug opacity-85">
                  {draft.subheadline.trim() || draft.topic.trim()}
                </p>
              ) : (
                <p className="mt-1 text-xs opacity-60">Subtítulo / apoio</p>
              )}
            </div>
            <div
              className="h-1 w-10 rounded-sm"
              style={{ background: style.accent }}
            />
          </div>
          {config.showSlides ? (
            <div className="absolute bottom-2 right-2 rounded bg-black/35 px-1.5 py-0.5 text-[10px] text-white">
              {draft.slides} slides
            </div>
          ) : null}
        </div>
      </div>

      <div className="grid gap-2">
        <Field label="Tema / assunto">
          <input
            value={draft.topic}
            onChange={(e) => patch("topic", e.target.value)}
            placeholder="Ex.: como vender no Instagram"
            className={inputClass}
          />
        </Field>
        <Field label="Título na arte">
          <input
            value={draft.headline}
            onChange={(e) => patch("headline", e.target.value)}
            placeholder="Texto principal (curto)"
            className={inputClass}
            maxLength={60}
          />
        </Field>
        <Field label="Subtítulo">
          <input
            value={draft.subheadline}
            onChange={(e) => patch("subheadline", e.target.value)}
            placeholder="Apoio opcional"
            className={inputClass}
            maxLength={80}
          />
        </Field>
      </div>

      <div>
        <p className="mb-1.5 text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">
          Formato
        </p>
        <div className="flex flex-wrap gap-1.5">
          {config.aspects.map((a) => (
            <button
              key={a.id}
              type="button"
              onClick={() => patch("aspectId", a.id)}
              className={`rounded-lg px-2.5 py-1 text-xs ${
                draft.aspectId === a.id
                  ? "bg-[var(--ink)] font-semibold text-[var(--panel)]"
                  : "border border-[var(--line)] bg-white/70 text-[var(--ink)]"
              }`}
            >
              {a.label}
              <span className="ml-1 opacity-60">{a.hint}</span>
            </button>
          ))}
        </div>
      </div>

      <div>
        <p className="mb-1.5 text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">
          Estilo visual
        </p>
        <div className="grid grid-cols-2 gap-1.5 sm:grid-cols-3">
          {config.styles.map((s) => (
            <button
              key={s.id}
              type="button"
              onClick={() => patch("styleId", s.id)}
              className={`overflow-hidden rounded-lg border text-left ${
                draft.styleId === s.id
                  ? "border-[var(--accent)] ring-1 ring-[var(--accent)]"
                  : "border-[var(--line)]"
              }`}
            >
              <div className="h-8" style={{ background: s.bg }} />
              <p className="px-2 py-1 text-[11px] font-medium text-[var(--ink)]">
                {s.label}
              </p>
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2">
        {config.showSlides ? (
          <Field label={`Slides (${draft.slides})`}>
            <input
              type="range"
              min={3}
              max={config.maxSlides ?? 12}
              value={draft.slides}
              onChange={(e) => patch("slides", Number(e.target.value))}
              className="w-full accent-[var(--accent)]"
            />
          </Field>
        ) : null}
        {config.showVariations ? (
          <Field label={`Variações (${draft.variations})`}>
            <input
              type="range"
              min={2}
              max={8}
              value={draft.variations}
              onChange={(e) => patch("variations", Number(e.target.value))}
              className="w-full accent-[var(--accent)]"
            />
          </Field>
        ) : null}
      </div>

      <Field label="Pedido extra (opcional)">
        <textarea
          value={extraBrief}
          onChange={(e) => onExtraBriefChange(e.target.value)}
          rows={3}
          className={`${inputClass} min-h-[72px] resize-none`}
          placeholder="Detalhes extras: tom, público, proibições…"
        />
      </Field>

      <div className="sticky bottom-0 flex flex-col gap-2 bg-[var(--panel)]/95 pt-1 backdrop-blur">
        <button
          type="button"
          onClick={() => onRun(previewPrompt, true)}
          className="rounded-xl bg-[var(--ink)] px-4 py-3 text-sm font-semibold text-[var(--panel)] transition hover:brightness-110"
        >
          Gerar no painel →
        </button>
        <button
          type="button"
          onClick={() => onRun(previewPrompt, false)}
          className="rounded-xl border border-[var(--line)] px-4 py-2.5 text-sm text-[var(--ink)]"
        >
          Abrir no agente completo
        </button>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">
      {label}
      <div className="mt-1 normal-case tracking-normal">{children}</div>
    </label>
  );
}
