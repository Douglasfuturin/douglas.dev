"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { GROUP_TEMPLATES, type GroupTemplate } from "@/lib/agents/group-templates";
import {
  OPERATION_LABELS,
  type OperationId,
  type ResolvedAgentGroup,
} from "@/lib/agents/group-types";
import { useAgentGroups } from "@/hooks/use-agent-groups";

function pipelineMembers(group: ResolvedAgentGroup) {
  return group.members.filter((m) => !m.isOrchestrator && m.mode !== "bit");
}

function groupProgress(group: ResolvedAgentGroup) {
  const steps = Math.max(group.workflow.length, 1);
  const filled = Math.min(pipelineMembers(group).length, steps);
  return Math.round((filled / steps) * 100);
}

function agentsLabel(group: ResolvedAgentGroup) {
  const names = pipelineMembers(group)
    .slice(0, 4)
    .map((m) => m.name.split(" ")[0]);
  const orch = group.members.find((m) => m.isOrchestrator)?.name || "Orquestrador";
  if (!names.length) return orch;
  return `${names.join(" + ")} + ${orch.split(" ")[0]}`;
}

function GroupCard({
  group,
  busy,
  addPick,
  onAddPick,
  onAddMember,
  onRemoveMember,
  onDelete,
  pickable,
}: {
  group: ResolvedAgentGroup;
  busy: boolean;
  addPick: string;
  onAddPick: (v: string) => void;
  onAddMember: () => void;
  onRemoveMember: (memberId: string) => void;
  onDelete: () => void;
  pickable: ReturnType<typeof useAgentGroups>["pickable"];
}) {
  const progress = groupProgress(group);
  const steps = pipelineMembers(group);

  const available = pickable.filter(
    (p) =>
      !group.members.some(
        (m) =>
          m.sourceId === p.id || m.customAgentId === p.id || m.name === p.name,
      ),
  );

  return (
    <article className="nexus-orch-card">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-lg font-semibold text-[color:var(--foreground)]">
              {group.name}
            </h3>
            {group.builtin ? (
              <span className="nexus-tag">Preset</span>
            ) : group.operation ? (
              <span className="nexus-tag nexus-tag-muted">
                {OPERATION_LABELS[group.operation]}
              </span>
            ) : null}
          </div>
          <p className="mt-1 text-sm text-[color:var(--muted-foreground)]">
            {group.blurb}
          </p>
          <p className="mt-2 text-xs font-medium text-[color:var(--primary)]">
            {agentsLabel(group)}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link
            href={`/app/studio?mode=grupo&group=${encodeURIComponent(group.id)}`}
            className="nexus-btn-primary !py-2 !text-xs"
          >
            Abrir sala
          </Link>
          <Link
            href={`/app?q=${encodeURIComponent(`Orquestra o grupo ${group.name} no fluxo correto`)}&autosend=1`}
            className="nexus-btn-ghost !text-xs"
          >
            Orquestrar
          </Link>
          {!group.builtin ? (
            <button
              type="button"
              className="nexus-btn-ghost !text-xs text-red-400"
              disabled={busy}
              onClick={onDelete}
            >
              Apagar
            </button>
          ) : null}
        </div>
      </div>

      <div className="mt-4">
        <div className="mb-1 flex justify-between text-[11px] text-[color:var(--muted-foreground)]">
          <span>Estrutura do fluxo</span>
          <span>{progress}%</span>
        </div>
        <div className="h-1.5 overflow-hidden rounded-full bg-[color:var(--muted)]">
          <div
            className="h-full rounded-full bg-[color:var(--primary)] transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <ol className="mt-5 flex flex-col gap-0 sm:flex-row sm:flex-wrap sm:items-stretch">
        {steps.map((member, index) => (
          <li key={member.id} className="nexus-pipeline-step flex min-w-0 flex-1 basis-[140px]">
            <div className="flex w-full flex-col">
              <div className="flex items-center gap-2">
                <span className="nexus-step-num">{index + 1}</span>
                <span
                  className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-[10px] font-bold text-[#0a0a0a]"
                  style={{ background: member.color }}
                >
                  {member.name.slice(0, 2).toUpperCase()}
                </span>
              </div>
              <p className="mt-2 text-sm font-medium text-[color:var(--foreground)]">
                {member.name}
              </p>
              <p className="mt-0.5 line-clamp-2 text-[11px] leading-snug text-[color:var(--muted-foreground)]">
                {member.role}
              </p>
              {!group.builtin && !member.isOrchestrator ? (
                <button
                  type="button"
                  className="mt-2 self-start text-[10px] font-semibold text-red-400 hover:underline"
                  disabled={busy}
                  onClick={() => onRemoveMember(member.id)}
                >
                  Remover
                </button>
              ) : null}
            </div>
          </li>
        ))}
        {group.members
          .filter((m) => m.isOrchestrator)
          .map((m) => (
            <li key={m.id} className="nexus-pipeline-step nexus-pipeline-orch flex min-w-0 flex-1 basis-[140px]">
              <div className="flex w-full flex-col">
                <div className="flex items-center gap-2">
                  <span className="nexus-step-num">◎</span>
                  <span
                    className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-[10px] font-bold text-[#0a0a0a]"
                    style={{ background: m.color }}
                  >
                    OR
                  </span>
                </div>
                <p className="mt-2 text-sm font-medium text-[color:var(--foreground)]">
                  {m.name}
                </p>
                <p className="mt-0.5 text-[11px] text-[color:var(--muted-foreground)]">
                  {m.role}
                </p>
              </div>
            </li>
          ))}
      </ol>

      <details className="mt-4 rounded-lg border border-[color:var(--border)] bg-[color:var(--background)]/40 px-3 py-2">
        <summary className="cursor-pointer text-xs font-semibold text-[color:var(--muted-foreground)]">
          Workflow documentado ({group.workflow.length} passos)
        </summary>
        <ol className="mt-2 list-decimal space-y-1 pl-5 text-xs text-[color:var(--muted-foreground)]">
          {group.workflow.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      </details>

      {!group.builtin ? (
        <div className="mt-4 flex flex-wrap items-end gap-2 border-t border-[color:var(--border)] pt-4">
          <label className="min-w-[200px] flex-1">
            <span className="mb-1 block text-[10px] font-semibold uppercase tracking-[0.12em] text-[color:var(--muted-foreground)]">
              Adicionar agente ao fluxo
            </span>
            <select
              className="nexus-field"
              value={addPick}
              onChange={(e) => onAddPick(e.target.value)}
            >
              <option value="">Escolher do catálogo…</option>
              {available.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            className="nexus-btn-ghost"
            disabled={!addPick || busy}
            onClick={onAddMember}
          >
            Adicionar
          </button>
        </div>
      ) : null}
    </article>
  );
}

export function NexusOrchestrations() {
  const {
    groups,
    pickable,
    loading,
    error,
    setError,
    createGroup,
    addMember,
    removeMember,
    deleteGroup,
    operationLabels,
    operations,
  } = useAgentGroups();

  const [showForm, setShowForm] = useState(false);
  const [creating, setCreating] = useState(false);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [addPick, setAddPick] = useState<Record<string, string>>({});
  const [form, setForm] = useState({
    name: "",
    blurb: "",
    operation: "times" as OperationId,
    memberSourceIds: [] as string[],
    workflow: [] as string[],
    templateId: "",
  });

  const builtins = useMemo(() => groups.filter((g) => g.builtin), [groups]);
  const customs = useMemo(() => groups.filter((g) => !g.builtin), [groups]);

  function applyTemplate(t: GroupTemplate) {
    setForm({
      name: t.name,
      blurb: t.blurb,
      operation: t.operation,
      memberSourceIds: [...t.memberSourceIds],
      workflow: [...t.workflow],
      templateId: t.id,
    });
    setShowForm(true);
  }

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
      await createGroup({
        name: form.name,
        blurb: form.blurb,
        operation: form.operation,
        memberSourceIds: form.memberSourceIds,
        workflow: form.workflow.length ? form.workflow : undefined,
      });
      setForm({
        name: "",
        blurb: "",
        operation: "times",
        memberSourceIds: [],
        workflow: [],
        templateId: "",
      });
      setShowForm(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro");
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="space-y-8 animate-nexus-rise">
      <section className="relative overflow-hidden rounded-2xl border border-[color:var(--border)] bg-[color:var(--card)] p-6 md:p-8">
        <div className="nexus-hero-glow pointer-events-none absolute inset-0" aria-hidden />
        <div className="relative z-10 flex flex-wrap items-end justify-between gap-4">
          <div className="max-w-2xl">
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--muted-foreground)]">
              Orquestrações · Times de agentes
            </p>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight text-[color:var(--foreground)] md:text-3xl">
              Estrutura completa de grupos
            </h2>
            <p className="mt-2 text-sm text-[color:var(--muted-foreground)]">
              Presets Imagem, Vídeo e Espanha já vêm montados. Crie times custom a
              partir de templates — cada grupo inclui Orquestrador, pipeline visual
              e workflow documentado.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Link href="/app" className="nexus-btn-primary">
              Nova conversa
            </Link>
            <button
              type="button"
              className="nexus-btn-ghost"
              onClick={() => setShowForm((v) => !v)}
            >
              {showForm ? "Fechar" : "+ Criar grupo"}
            </button>
          </div>
        </div>
      </section>

      <section>
        <h3 className="text-sm font-semibold text-[color:var(--foreground)]">
          Templates (estrutura pronta)
        </h3>
        <p className="mt-1 text-sm text-[color:var(--muted-foreground)]">
          Um clique preenche membros + workflow — você só ajusta o nome.
        </p>
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          {GROUP_TEMPLATES.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => applyTemplate(t)}
              className="nexus-template-card text-left"
            >
              <p className="text-sm font-semibold text-[color:var(--foreground)]">
                {t.name}
              </p>
              <p className="mt-1 text-xs text-[color:var(--muted-foreground)]">
                {t.blurb}
              </p>
              <p className="mt-2 text-[10px] font-medium text-[color:var(--primary)]">
                {t.memberSourceIds.length} agentes + Orquestrador ·{" "}
                {t.workflow.length} passos
              </p>
            </button>
          ))}
        </div>
      </section>

      {showForm ? (
        <form onSubmit={onCreate} className="nexus-panel space-y-4">
          <h3 className="text-base font-semibold text-[color:var(--foreground)]">
            Novo grupo
            {form.templateId ? (
              <span className="ml-2 text-xs font-normal text-[color:var(--muted-foreground)]">
                (template: {form.templateId})
              </span>
            ) : null}
          </h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="nexus-label">Nome do grupo</span>
              <input
                className="nexus-field"
                value={form.name}
                onChange={(e) =>
                  setForm((f) => ({ ...f, name: e.target.value }))
                }
                required
              />
            </label>
            <label className="block">
              <span className="nexus-label">Operação</span>
              <select
                className="nexus-field"
                value={form.operation}
                onChange={(e) =>
                  setForm((f) => ({
                    ...f,
                    operation: e.target.value as OperationId,
                  }))
                }
              >
                {operations.map((op) => (
                  <option key={op} value={op}>
                    {operationLabels[op]}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <label className="block">
            <span className="nexus-label">Descrição</span>
            <input
              className="nexus-field"
              value={form.blurb}
              onChange={(e) =>
                setForm((f) => ({ ...f, blurb: e.target.value }))
              }
            />
          </label>
          <div>
            <span className="nexus-label">Agentes (Orquestrador incluso automaticamente)</span>
            <div className="mt-2 flex flex-wrap gap-2">
              {pickable.map((a) => {
                const on = form.memberSourceIds.includes(a.id);
                return (
                  <button
                    key={a.id}
                    type="button"
                    onClick={() => toggleMember(a.id)}
                    className={`nexus-chip ${on ? "nexus-chip-on" : ""}`}
                  >
                    <span
                      className="inline-block h-2 w-2 rounded-full"
                      style={{ background: a.color }}
                    />
                    {a.name}
                  </button>
                );
              })}
            </div>
          </div>
          {form.workflow.length > 0 ? (
            <div>
              <span className="nexus-label">Workflow</span>
              <ol className="mt-2 list-decimal space-y-1 pl-5 text-xs text-[color:var(--muted-foreground)]">
                {form.workflow.map((step) => (
                  <li key={step}>{step}</li>
                ))}
              </ol>
            </div>
          ) : null}
          <button
            type="submit"
            disabled={creating}
            className="nexus-btn-primary disabled:opacity-50"
          >
            {creating ? "Criando…" : "Criar grupo com estrutura"}
          </button>
        </form>
      ) : null}

      {error ? (
        <p className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-300">
          {error}
        </p>
      ) : null}

      {loading ? (
        <p className="text-sm text-[color:var(--muted-foreground)]">Carregando grupos…</p>
      ) : (
        <>
          <section className="space-y-4">
            <h3 className="text-lg font-semibold text-[color:var(--foreground)]">
              Grupos preset (sistema)
            </h3>
            <div className="space-y-4">
              {builtins.map((group) => (
                <GroupCard
                  key={group.id}
                  group={group}
                  busy={busyId === group.id}
                  addPick={addPick[group.id] || ""}
                  onAddPick={(v) =>
                    setAddPick((p) => ({ ...p, [group.id]: v }))
                  }
                  onAddMember={async () => {
                    const sid = addPick[group.id];
                    if (!sid) return;
                    setBusyId(group.id);
                    try {
                      await addMember(group.id, sid);
                      setAddPick((p) => ({ ...p, [group.id]: "" }));
                    } catch (err) {
                      setError(err instanceof Error ? err.message : "Erro");
                    } finally {
                      setBusyId(null);
                    }
                  }}
                  onRemoveMember={() => undefined}
                  onDelete={() => undefined}
                  pickable={pickable}
                />
              ))}
            </div>
          </section>

          <section className="space-y-4">
            <h3 className="text-lg font-semibold text-[color:var(--foreground)]">
              Seus grupos custom
            </h3>
            {customs.length === 0 ? (
              <p className="nexus-panel text-sm text-[color:var(--muted-foreground)]">
                Nenhum grupo custom ainda. Use um template acima ou crie do zero.
              </p>
            ) : (
              <div className="space-y-4">
                {customs.map((group) => (
                  <GroupCard
                    key={group.id}
                    group={{
                      ...group,
                      operation: group.operation,
                    }}
                    busy={busyId === group.id}
                    addPick={addPick[group.id] || ""}
                    onAddPick={(v) =>
                      setAddPick((p) => ({ ...p, [group.id]: v }))
                    }
                    onAddMember={async () => {
                      const sid = addPick[group.id];
                      if (!sid) return;
                      setBusyId(group.id);
                      try {
                        await addMember(group.id, sid);
                        setAddPick((p) => ({ ...p, [group.id]: "" }));
                      } catch (err) {
                        setError(err instanceof Error ? err.message : "Erro");
                      } finally {
                        setBusyId(null);
                      }
                    }}
                    onRemoveMember={async (memberId) => {
                      setBusyId(group.id);
                      try {
                        await removeMember(group.id, memberId);
                      } catch (err) {
                        setError(err instanceof Error ? err.message : "Erro");
                      } finally {
                        setBusyId(null);
                      }
                    }}
                    onDelete={async () => {
                      if (!confirm("Apagar este grupo?")) return;
                      setBusyId(group.id);
                      try {
                        await deleteGroup(group.id);
                      } catch (err) {
                        setError(err instanceof Error ? err.message : "Erro");
                      } finally {
                        setBusyId(null);
                      }
                    }}
                    pickable={pickable}
                  />
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}
