"use client";

import { useCallback, useEffect, useState } from "react";

type Action = {
  id: string;
  label: string;
  kind: string;
  createdAt: string;
};

export function OrchestratorActionLog({ compact }: { compact?: boolean }) {
  const [actions, setActions] = useState<Action[]>([]);
  const [undoBusy, setUndoBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const res = await fetch("/api/orchestrator/log?limit=20");
      const data = await res.json();
      if (data.ok) setActions(data.actions || []);
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    void load();
    const onRefresh = () => void load();
    window.addEventListener("nexus-registry-refresh", onRefresh);
    const t = setInterval(load, 8000);
    return () => {
      window.removeEventListener("nexus-registry-refresh", onRefresh);
      clearInterval(t);
    };
  }, [load]);

  async function undo() {
    setUndoBusy(true);
    try {
      await fetch("/api/orchestrator/undo", { method: "POST" });
      window.dispatchEvent(new CustomEvent("nexus-registry-refresh"));
      await load();
    } finally {
      setUndoBusy(false);
    }
  }

  if (!actions.length && compact) return null;

  return (
    <aside
      className={
        compact
          ? "rounded-xl border border-[color:var(--border)] bg-[color:var(--card)]/80 p-3"
          : "nexus-panel"
      }
    >
      <div className="mb-2 flex items-center justify-between gap-2">
        <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[color:var(--muted-foreground)]">
          Log do orquestrador
        </p>
        <button
          type="button"
          className="nexus-btn-ghost !px-2 !py-1 text-[10px]"
          disabled={undoBusy}
          onClick={() => void undo()}
        >
          Desfazer
        </button>
      </div>
      <ul className="max-h-40 space-y-1.5 overflow-y-auto text-xs">
        {actions.length === 0 ? (
          <li className="text-[color:var(--muted-foreground)]">Nenhuma ação ainda.</li>
        ) : (
          actions.map((a) => (
            <li key={a.id} className="flex gap-2 text-[color:var(--foreground)]">
              <span className="shrink-0 text-[color:var(--primary)]">•</span>
              <span>{a.label}</span>
            </li>
          ))
        )}
      </ul>
    </aside>
  );
}
