"use client";

import { useState } from "react";

type Preview = {
  name?: string;
  avatar?: string;
  color?: string;
  role?: string;
  systemPromptPreview?: string;
  toolkit?: string;
  model?: string;
  inputs?: string[];
  outputs?: string[];
  before?: string;
  after?: string;
};

export function OrchestratorProposalCard({
  proposalId,
  kind,
  preview,
  onDone,
}: {
  proposalId: string;
  kind: string;
  preview: Preview;
  onDone?: () => void;
}) {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function act(action: "confirm" | "cancel") {
    setBusy(true);
    setMessage(null);
    try {
      const res = await fetch(`/api/orchestrator/proposals/${proposalId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action }),
      });
      const data = await res.json();
      if (!data.ok && action === "confirm") {
        setMessage(data.error || "Falha ao confirmar");
        return;
      }
      setMessage(action === "confirm" ? "Salvo." : "Cancelado.");
      window.dispatchEvent(new CustomEvent("nexus-registry-refresh"));
      onDone?.();
    } catch {
      setMessage("Erro de rede");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="nexus-panel space-y-3 !p-4 text-sm">
      <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[color:var(--primary)]">
        Pré-visualização · {kind === "update_agent" ? "Editar agente" : "Novo agente"}
      </p>
      {preview.name ? (
        <div className="flex items-center gap-3">
          <span
            className="flex size-10 items-center justify-center rounded-lg text-xs font-bold text-[#0b0f14]"
            style={{ background: preview.color || "var(--primary)" }}
          >
            {preview.avatar || "AI"}
          </span>
          <div>
            <p className="font-semibold text-[color:var(--foreground)]">{preview.name}</p>
            <p className="text-xs text-[color:var(--muted-foreground)]">{preview.role}</p>
          </div>
        </div>
      ) : null}
      {preview.systemPromptPreview ? (
        <p className="rounded-md border border-[color:var(--border)] bg-[color:var(--background)]/60 p-2 text-xs leading-relaxed text-[color:var(--muted-foreground)]">
          {preview.systemPromptPreview}
        </p>
      ) : null}
      {preview.before && preview.after ? (
        <div className="grid gap-2 text-xs md:grid-cols-2">
          <div className="rounded border border-[color:var(--border)] p-2">
            <p className="mb-1 font-semibold">Antes</p>
            <p className="whitespace-pre-wrap text-[color:var(--muted-foreground)]">
              {preview.before}
            </p>
          </div>
          <div className="rounded border border-[color:var(--primary)]/40 p-2">
            <p className="mb-1 font-semibold text-[color:var(--primary)]">Depois</p>
            <p className="whitespace-pre-wrap text-[color:var(--muted-foreground)]">
              {preview.after}
            </p>
          </div>
        </div>
      ) : null}
      {(preview.inputs?.length || preview.outputs?.length) ? (
        <div className="flex flex-wrap gap-2 text-[11px]">
          {preview.inputs?.map((i) => (
            <span key={`in-${i}`} className="nexus-tag-muted nexus-tag">
              in: {i}
            </span>
          ))}
          {preview.outputs?.map((o) => (
            <span key={`out-${o}`} className="nexus-tag">
              out: {o}
            </span>
          ))}
        </div>
      ) : null}
      <div className="flex flex-wrap gap-2 pt-1">
        <button
          type="button"
          disabled={busy}
          className="nexus-btn-primary !py-1.5 text-xs"
          onClick={() => void act("confirm")}
        >
          Confirmar
        </button>
        <button
          type="button"
          disabled={busy}
          className="nexus-btn-ghost !py-1.5 text-xs"
          onClick={() => void act("cancel")}
        >
          Cancelar
        </button>
      </div>
      {message ? <p className="text-xs text-[color:var(--muted-foreground)]">{message}</p> : null}
    </div>
  );
}
