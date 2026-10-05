"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  AGENT_COLORS,
  TOOLKIT_LABELS,
  TOOLKIT_PRESETS,
  type CustomAgent,
  type ToolkitPreset,
} from "@/lib/agents/custom-types";

type ToolkitOption = { id: ToolkitPreset; label: string };

const TEMPLATES: Array<{
  name: string;
  role: string;
  toolkit: ToolkitPreset;
  instructions: string;
}> = [
  {
    name: "Caçador GitHub",
    role: "Encontra repos top e escreve Reels 60s",
    toolkit: "github",
    instructions:
      "Sempre busque por nichos com mais stars. Entregue ranking + roteiro 60s completo. Salve na Central quando fizer sentido.",
  },
  {
    name: "Editor Editorial",
    role: "Fecha pacotes na Central FASE",
    toolkit: "central",
    instructions:
      "Liste o pipeline, avance estágios e monte packs (roteiro + caption + art brief). Peça aprovação antes de publicar.",
  },
  {
    name: "Radar Diário",
    role: "Briefing de IA, automação e marketing",
    toolkit: "radar",
    instructions:
      "Monte briefing ranqueado do dia e peça aprovação para o roteirista. Português claro e fontes reais.",
  },
];

export function AgentsManager() {
  const [agents, setAgents] = useState<CustomAgent[]>([]);
  const [toolkits, setToolkits] = useState<ToolkitOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    name: "",
    role: "",
    instructions: "",
    toolkit: "chat" as ToolkitPreset,
    color: AGENT_COLORS[0] as string,
  });

  const load = useCallback(async () => {
    setError(null);
    try {
      const res = await fetch("/api/agents");
      const data = await res.json();
      if (!data.ok) throw new Error(data.error || "Falha");
      setAgents(data.agents || []);
      setToolkits(data.toolkits || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  function applyTemplate(t: (typeof TEMPLATES)[number]) {
    setForm({
      name: t.name,
      role: t.role,
      instructions: t.instructions,
      toolkit: t.toolkit,
      color: AGENT_COLORS[Math.floor(Math.random() * AGENT_COLORS.length)],
    });
    setShowForm(true);
  }

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim() || !form.role.trim() || !form.instructions.trim()) {
      setError("Preencha nome, papel e instruções.");
      return;
    }
    setCreating(true);
    setError(null);
    try {
      const res = await fetch("/api/agents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!data.ok) throw new Error(data.error || "Falha ao criar");
      setForm({
        name: "",
        role: "",
        instructions: "",
        toolkit: "chat",
        color: AGENT_COLORS[0],
      });
      setShowForm(false);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro");
    } finally {
      setCreating(false);
    }
  }

  async function onDelete(id: string) {
    if (!confirm("Apagar este agente?")) return;
    await fetch(`/api/agents/${id}`, { method: "DELETE" });
    await load();
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3 animate-fase-rise">
        <p className="text-sm text-[color:var(--fase-muted)]">
          Crie agentes com persona, toolkit e instruções próprias.
        </p>
        <button
          type="button"
          className="crm-btn crm-btn-primary"
          onClick={() => setShowForm((v) => !v)}
        >
          {showForm ? "Fechar formulário" : "+ Criar agente"}
        </button>
      </div>

      <section className="animate-fase-rise" style={{ animationDelay: "40ms" }}>
        <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.16em] text-[color:var(--fase-muted)]">
          Templates rápidos
        </p>
        <div className="flex flex-wrap gap-2">
          {TEMPLATES.map((t) => (
            <button
              key={t.name}
              type="button"
              className="crm-btn crm-btn-ghost"
              onClick={() => applyTemplate(t)}
            >
              {t.name}
            </button>
          ))}
        </div>
      </section>

      {showForm ? (
        <form
          onSubmit={onCreate}
          className="crm-panel space-y-4 animate-fase-rise"
        >
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="mb-1 block text-[11px] font-bold uppercase tracking-[0.14em] text-[color:var(--fase-muted)]">
                Nome
              </span>
              <input
                className="field"
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="Ex.: Caçador GitHub"
                required
              />
            </label>
            <label className="block">
              <span className="mb-1 block text-[11px] font-bold uppercase tracking-[0.14em] text-[color:var(--fase-muted)]">
                Papel
              </span>
              <input
                className="field"
                value={form.role}
                onChange={(e) => setForm((f) => ({ ...f, role: e.target.value }))}
                placeholder="O que este agente faz"
                required
              />
            </label>
          </div>

          <label className="block">
            <span className="mb-1 block text-[11px] font-bold uppercase tracking-[0.14em] text-[color:var(--fase-muted)]">
              Toolkit
            </span>
            <select
              className="field"
              value={form.toolkit}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  toolkit: e.target.value as ToolkitPreset,
                }))
              }
            >
              {(toolkits.length
                ? toolkits
                : TOOLKIT_PRESETS.map((id) => ({
                    id,
                    label: TOOLKIT_LABELS[id],
                  }))
              ).map((t) => (
                <option key={t.id} value={t.id}>
                  {t.label}
                </option>
              ))}
            </select>
          </label>

          <label className="block">
            <span className="mb-1 block text-[11px] font-bold uppercase tracking-[0.14em] text-[color:var(--fase-muted)]">
              Instruções do sistema
            </span>
            <textarea
              className="field min-h-[140px]"
              value={form.instructions}
              onChange={(e) =>
                setForm((f) => ({ ...f, instructions: e.target.value }))
              }
              placeholder="Como o agente deve se comportar, tom, formato de entrega…"
              required
            />
          </label>

          <div>
            <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.14em] text-[color:var(--fase-muted)]">
              Cor
            </p>
            <div className="flex flex-wrap gap-2">
              {AGENT_COLORS.map((c) => (
                <button
                  key={c}
                  type="button"
                  aria-label={`Cor ${c}`}
                  onClick={() => setForm((f) => ({ ...f, color: c }))}
                  className={`h-8 w-8 rounded-lg border-2 transition ${
                    form.color === c
                      ? "border-[color:var(--fase-ink)] scale-110"
                      : "border-transparent"
                  }`}
                  style={{ background: c }}
                />
              ))}
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              type="submit"
              disabled={creating}
              className="crm-btn crm-btn-primary disabled:opacity-50"
            >
              {creating ? "Criando…" : "Criar agente"}
            </button>
            <button
              type="button"
              className="crm-btn crm-btn-ghost"
              onClick={() => setShowForm(false)}
            >
              Cancelar
            </button>
          </div>
        </form>
      ) : null}

      {error ? <p className="text-sm text-red-700">{error}</p> : null}

      <section>
        <h2 className="mb-3 font-display text-lg font-bold text-[color:var(--fase-ink)]">
          Seus agentes
        </h2>
        {loading ? (
          <p className="text-sm text-[color:var(--fase-muted)]">Carregando…</p>
        ) : agents.length === 0 ? (
          <div className="crm-panel text-sm text-[color:var(--fase-muted)]">
            Nenhum agente ainda. Clique em <strong>+ Criar agente</strong> ou use
            um template.
          </div>
        ) : (
          <ul className="grid gap-3 sm:grid-cols-2">
            {agents.map((agent, i) => (
              <li
                key={agent.id}
                className="crm-panel animate-fase-rise"
                style={{ animationDelay: `${i * 50}ms` }}
              >
                <div className="flex items-start gap-3">
                  <span
                    className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-sm font-bold text-[#0b0f14]"
                    style={{ background: agent.color }}
                  >
                    {agent.avatar}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="font-display text-lg font-bold text-[color:var(--fase-ink)]">
                      {agent.name}
                    </p>
                    <p className="text-xs text-[color:var(--fase-muted)]">
                      {agent.role}
                    </p>
                    <p className="mt-2 line-clamp-2 text-xs text-[color:var(--fase-muted)]">
                      {agent.instructions}
                    </p>
                    <span className="crm-pill mt-2">
                      {TOOLKIT_LABELS[agent.toolkit]}
                    </span>
                  </div>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  <Link
                    href={`/studio?mode=custom&agent=${encodeURIComponent(agent.id)}`}
                    className="crm-btn crm-btn-primary"
                  >
                    Abrir no Studio
                  </Link>
                  <button
                    type="button"
                    className="crm-btn crm-btn-ghost text-red-700"
                    onClick={() => void onDelete(agent.id)}
                  >
                    Apagar
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
