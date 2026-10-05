"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import type { CatalogAgent } from "@/lib/agents/group-types";
import {
  OPERATION_LABELS,
  OPERATIONS,
  type OperationId,
  type ResolvedAgentGroup,
} from "@/lib/agents/group-types";

export type CustomAgentOption = {
  id: string;
  name: string;
  role: string;
  color: string;
};

export type PickableAgent = {
  id: string;
  name: string;
  role: string;
  color: string;
  kind: "builtin" | "custom";
};

export function useAgentGroups() {
  const [groups, setGroups] = useState<ResolvedAgentGroup[]>([]);
  const [catalog, setCatalog] = useState<CatalogAgent[]>([]);
  const [customAgents, setCustomAgents] = useState<CustomAgentOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      const res = await fetch("/api/groups");
      const data = await res.json();
      if (!data.ok) throw new Error(data.error || "Falha ao carregar grupos");
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

  const pickable = useMemo((): PickableAgent[] => {
    const builtins = catalog.filter((c) => c.id !== "orquestrador");
    return [
      ...builtins.map((b) => ({
        id: b.id,
        name: b.name,
        role: b.role,
        color: b.color,
        kind: "builtin" as const,
      })),
      ...customAgents.map((a) => ({
        id: a.id,
        name: a.name,
        role: a.role,
        color: a.color,
        kind: "custom" as const,
      })),
    ];
  }, [catalog, customAgents]);

  async function createGroup(input: {
    name: string;
    blurb: string;
    operation: OperationId;
    memberSourceIds: string[];
    workflow?: string[];
  }) {
    const res = await fetch("/api/groups", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || "Falha ao criar grupo");
    await load();
    return data.group;
  }

  async function addMember(groupId: string, sourceId: string) {
    const res = await fetch(`/api/groups/${groupId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "add_member", sourceId }),
    });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || "Falha ao adicionar");
    await load();
  }

  async function removeMember(groupId: string, memberId: string) {
    const res = await fetch(`/api/groups/${groupId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "remove_member", memberId }),
    });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || "Falha ao remover");
    await load();
  }

  async function deleteGroup(groupId: string) {
    const res = await fetch(`/api/groups/${groupId}`, { method: "DELETE" });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || "Falha ao apagar");
    await load();
  }

  return {
    groups,
    catalog,
    customAgents,
    pickable,
    loading,
    error,
    setError,
    load,
    createGroup,
    addMember,
    removeMember,
    deleteGroup,
    operationLabels: OPERATION_LABELS,
    operations: OPERATIONS,
  };
}
