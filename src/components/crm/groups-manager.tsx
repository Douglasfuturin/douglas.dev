"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import type { CatalogAgent } from "@/lib/agents/group-types";
import {
  OPERATION_LABELS,
  OPERATIONS,
  type OperationId,
  type ResolvedAgentGroup,
} from "@/lib/agents/group-types";

type CustomOption = {
  id: string;
  name: string;
  role: string;
  color: string;
};

export function GroupsManager({ compact = false }: { compact?: boolean }) {
  const [groups, setGroups] = useState<ResolvedAgentGroup[]>([]);
  const [catalog, setCatalog] = useState<CatalogAgent[]>([]);
  const [customAgents, setCustomAgents] = useState<CustomOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [creating, setCreating] = useState(false);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: "",
    blurb: "",
    operation: "times" as OperationId,
    memberSourceIds: [] as string[],
  });
  const [addPick, setAddPick] = useState<Record<string, string>>({});

  const load = useCallback(async () => {
    setError(null);
    try {
      const res = await fetch("/api/groups");
      const data = await res.json();
      if (!data.ok) throw new Error(data.error || "Falha");
      setGroups(data.groups || []);
      setCatalog(data.catalog || []);
      setCustomAgents(data.customAgents || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const pickable = useMemo(() => {
    const builtins = catalog.filter((c) => c.id !== "orquestrador");
    const customs = customAgents.map((a) => ({
      id: a.id,
      name: a.name,
      role: a.role,
      color: a.color,
      kind: "custom" as const,
    }));
    return [
      ...builtins.map((b) => ({
        id: b.id,
        name: b.name,
        role: b.role,
        color: b.color,
        kind: "builtin" as const,
      })),
      ...customs,
    ];
  }, [catalog, customAgents]);

  function toggleMember(sourceId: string) {
    setForm((f) => {
      const has = f.memberSourceIds.includes(sourceId);
      return {
        ...f,
        memberSourceIds: has
          ? f.memberSourceIds.filter((id) => id !== sourceId)
          : [...f.memberSourceIds, sourceId].slice(0, 7),
      };
    });
  }

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim()) {
      setError("Nome do grupo é obrigatório.");
      return;
    }
    setCreating(true);
    setError(null);
    try {
      const res = await fetch("/api/groups", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!data.ok) throw new Error(data.error || "Falha ao criar");
      setForm({
        name: "",
        blurb: "",
        operation: "times",
        memberSourceIds: [],
      });
      setShowForm(false);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro");
    } finally {
      setCreating(false);
    }
  }

  async function onAddMember(groupId: string) {
    const sourceId = addPick[groupId];
    if (!sourceId) return;
    setBusyId(groupId);
    setError(null);
    try {
      const res = await fetch(`/api/groups/${groupId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "add_member", sourceId }),
      });
      const data = await res.json();
      if (!data.ok) throw new Error(data.error || "Falha");
      setAddPick((p) => ({ ...p, [groupId]: "" }));
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro");
    } finally {
      setBusyId(null);
    }
  }

  async function onRemoveMember(groupId: string, memberId: string) {
    setBusyId(groupId);
    setError(null);
    try {
      const res = await fetch(`/api/groups/${groupId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "remove_member", memberId }),
      });
      const data = await res.json();
      if (!data.ok) throw new Error(data.error || "Falha");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro");
    } finally {
      setBusyId(null);
    }
  }

  async function onDeleteGroup(groupId: string) {
    if (!confirm("Apagar este grupo?")) return;
    setBusyId(groupId);
    try {
      const res = await fetch(`/api/groups/${groupId}`, { method: "DELETE" });
      const data = await res.json();
      if (!data.ok) throw new Error(data.error || "Falha");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro");
    } finally {
      setBusyId(null);
    }
  }

  const visible = compact
    ? groups.filter((g) => !g.builtin).slice(0, 4)
    : groups;

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="font-display text-lg font-bold text-white">
            {compact ? "Seus grupos" : "Grupos de agentes"}
          </h3>
          <p className="mt-1 text-sm text-[color:var(--fase-muted)]">
            Cada grupo nasce com um Orquestrador. Adicione agentes para
            conversarem e fecharem o fluxo.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {!compact ? (
            <Link
              href="/app?q=Orquestra%20todos%20os%20grupos%20e%20defina%20o%20fluxo%20certo&autosend=1"
              className="crm-btn crm-btn-primary"
            >
              Orquestrador Principal
            </Link>
          ) : (
            <Link href="/grupos" className="crm-btn crm-btn-ghost">
              Gerenciar →
            </Link>
          )}
          <button
            type="button"
            className="crm-btn crm-btn-dark"
            onClick={() => setShowForm((v) => !v)}
          >
            {showForm ? "Fechar" : "+ Criar grupo"}
          </button>
        </div>
      </div>

      {showForm ? (
        <form onSubmit={onCreate} className="crm-panel space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="mb-1 block text-[11px] font-bold uppercase tracking-[0.14em] text-[color:var(--fase-muted)]">
                Nome do grupo
              </span>
              <input
                className="field"
                value={form.name}
                onChange={(e) =>
                  setForm((f) => ({ ...f, name: e.target.value }))
                }
                placeholder="Ex.: Lançamento Reels IA"
                required
              />
            </label>
            <label className="block">
              <span className="mb-1 block text-[11px] font-bold uppercase tracking-[0.14em] text-[color:var(--fase-muted)]">
                Operação
              </span>
              <select
                className="field"
                value={form.operation}
                onChange={(e) =>
                  setForm((f) => ({
                    ...f,
                    operation: e.target.value as OperationId,
                  }))
                }
              >
                {OPERATIONS.map((op) => (
                  <option key={op} value={op}>
                    {OPERATION_LABELS[op]}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <label className="block">
            <span className="mb-1 block text-[11px] font-bold uppercase tracking-[0.14em] text-[color:var(--fase-muted)]">
              Descrição
            </span>
            <input
              className="field"
              value={form.blurb}
              onChange={(e) =>
                setForm((f) => ({ ...f, blurb: e.target.value }))
              }
              placeholder="O que este time resolve juntos"
            />
          </label>
          <div>
            <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.14em] text-[color:var(--fase-muted)]">
              Agentes iniciais (Orquestrador já incluso)
            </p>
            <div className="flex flex-wrap gap-2">
              {pickable.map((a) => {
                const on = form.memberSourceIds.includes(a.id);
                return (
                  <button
                    key={a.id}
                    type="button"
                    onClick={() => toggleMember(a.id)}
                    className={`rounded-lg border px-2.5 py-1.5 text-xs font-semibold transition ${
                      on
                        ? "border-[color:var(--primary)] bg-[color:var(--primary)]/15 text-white"
                        : "border-[color:var(--fase-line)] bg-[color:var(--dd-surface)] text-white/70"
                    }`}
                  >
                    <span
                      className="mr-1.5 inline-block h-2 w-2 rounded-full"
                      style={{ background: a.color }}
                    />
                    {a.name}
                  </button>
                );
              })}
            </div>
          </div>
          <button
            type="submit"
            disabled={creating}
            className="crm-btn crm-btn-primary disabled:opacity-50"
          >
            {creating ? "Criando…" : "Criar grupo com Orquestrador"}
          </button>
        </form>
      ) : null}

      {error ? <p className="text-sm text-red-400">{error}</p> : null}

      {loading ? (
        <p className="text-sm text-[color:var(--fase-muted)]">Carregando…</p>
      ) : visible.length === 0 ? (
        <div className="crm-panel text-sm text-[color:var(--fase-muted)]">
          Nenhum grupo custom ainda. Crie um time e adicione agentes.
        </div>
      ) : (
        <ul className="space-y-4">
          {visible.map((group) => {
            const availableClean = pickable.filter(
              (p) =>
                !group.members.some(
                  (m) =>
                    m.sourceId === p.id ||
                    m.customAgentId === p.id ||
                    m.name === p.name,
                ),
            );
            return (
              <li key={group.id} className="crm-panel">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <h4 className="font-display text-xl font-bold text-white">
                        {group.name}
                      </h4>
                      {group.operation ? (
                        <span className="crm-pill">
                          {OPERATION_LABELS[group.operation]}
                        </span>
                      ) : null}
                      {group.builtin ? (
                        <span className="crm-pill">Preset</span>
                      ) : null}
                    </div>
                    <p className="mt-1 max-w-2xl text-sm text-[color:var(--fase-muted)]">
                      {group.blurb}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Link
                      href={`/studio?mode=grupo&group=${encodeURIComponent(group.id)}`}
                      className="crm-btn crm-btn-primary"
                    >
                      Abrir sala
                    </Link>
                    {!group.builtin ? (
                      <button
                        type="button"
                        className="crm-btn crm-btn-ghost text-red-400"
                        disabled={busyId === group.id}
                        onClick={() => void onDeleteGroup(group.id)}
                      >
                        Apagar
                      </button>
                    ) : null}
                  </div>
                </div>

                <p className="mt-4 text-[11px] font-bold uppercase tracking-[0.16em] text-[color:var(--fase-muted)]">
                  Membros ({group.members.length}/{group.maxMembers})
                </p>
                <ul className="mt-2 grid gap-2 sm:grid-cols-2">
                  {group.members.map((m) => (
                    <li
                      key={m.id}
                      className="crm-card-sm flex items-center justify-between gap-2"
                    >
                      <div className="flex min-w-0 items-center gap-2">
                        <span
                          className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-[10px] font-bold text-[#0b0f14]"
                          style={{ background: m.color }}
                        >
                          {m.name.slice(0, 2).toUpperCase()}
                        </span>
                        <span className="min-w-0">
                          <span className="block truncate text-sm font-semibold text-white">
                            {m.name}
                            {m.isOrchestrator ? " · Orquestrador" : ""}
                          </span>
                          <span className="block truncate text-[11px] text-white/55">
                            {m.role}
                          </span>
                        </span>
                      </div>
                      {!group.builtin && !m.isOrchestrator ? (
                        <button
                          type="button"
                          className="shrink-0 text-[11px] font-semibold text-red-400 hover:underline"
                          disabled={busyId === group.id}
                          onClick={() => void onRemoveMember(group.id, m.id)}
                        >
                          Remover
                        </button>
                      ) : null}
                    </li>
                  ))}
                </ul>

                {!group.builtin && !compact ? (
                  <div className="mt-3 flex flex-wrap items-end gap-2">
                    <label className="min-w-[200px] flex-1">
                      <span className="mb-1 block text-[10px] font-bold uppercase tracking-[0.14em] text-[color:var(--fase-muted)]">
                        Adicionar agente
                      </span>
                      <select
                        className="field"
                        value={addPick[group.id] || ""}
                        onChange={(e) =>
                          setAddPick((p) => ({
                            ...p,
                            [group.id]: e.target.value,
                          }))
                        }
                      >
                        <option value="">Escolher…</option>
                        {availableClean.map((a) => (
                          <option key={a.id} value={a.id}>
                            {a.name} — {a.role}
                          </option>
                        ))}
                      </select>
                    </label>
                    <button
                      type="button"
                      className="crm-btn crm-btn-ghost"
                      disabled={!addPick[group.id] || busyId === group.id}
                      onClick={() => void onAddMember(group.id)}
                    >
                      Adicionar
                    </button>
                  </div>
                ) : null}

                {!compact ? (
                  <ol className="mt-4 list-decimal space-y-1 pl-5 text-xs text-[color:var(--fase-muted)]">
                    {group.workflow.map((step) => (
                      <li key={step}>{step}</li>
                    ))}
                  </ol>
                ) : null}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
