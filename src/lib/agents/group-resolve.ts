import { AGENT_GROUPS, getAgentGroup as getBuiltinGroup } from "./groups";
import { getUserGroup, listUserGroups } from "./group-store";
import type {
  OperationId,
  ResolvedAgentGroup,
  ResolvedGroupMember,
} from "./group-types";

function builtinToResolved(id: string): ResolvedAgentGroup | null {
  const g = getBuiltinGroup(id);
  if (!g) return null;
  const operation: OperationId =
    g.id === "conteudo-dev-video"
      ? "video"
      : g.id === "conteudos-espanha"
        ? "visual"
        : "ideacao";
  const members: ResolvedGroupMember[] = g.members.map((m) => ({
    id: m.id,
    name: m.name,
    mode: m.mode,
    role: m.role,
    color: m.color,
    icon: m.icon,
    isOrchestrator: m.id === "bit" || m.mode === "bit",
    kind: "builtin" as const,
    sourceId: m.id,
  }));
  const orch = members.find((m) => m.isOrchestrator);
  return {
    id: g.id,
    name: g.name,
    blurb: g.blurb,
    maxMembers: g.maxMembers,
    members,
    workflow: g.workflow,
    operation,
    orchestratorMemberId: orch?.id,
    builtin: true,
  };
}

export async function resolveAgentGroup(
  groupId: string | undefined | null,
): Promise<ResolvedAgentGroup | null> {
  if (!groupId) return null;
  const builtin = builtinToResolved(groupId);
  if (builtin) return builtin;
  const user = await getUserGroup(groupId);
  if (!user) return null;
  return {
    id: user.id,
    name: user.name,
    blurb: user.blurb,
    maxMembers: user.maxMembers,
    members: user.members.map((m) => ({
      id: m.id,
      name: m.name,
      mode: m.mode,
      role: m.role,
      color: m.color,
      icon: m.icon,
      isOrchestrator: m.isOrchestrator,
      customAgentId: m.customAgentId,
      sourceId: m.sourceId,
      kind: m.kind,
    })),
    workflow: user.workflow,
    operation: user.operation,
    orchestratorMemberId: user.orchestratorMemberId,
    builtin: false,
  };
}

export async function resolveGroupMember(
  groupId: string | undefined | null,
  memberId: string | undefined | null,
) {
  const group = await resolveAgentGroup(groupId);
  if (!group || !memberId) return null;
  return group.members.find((m) => m.id === memberId) ?? null;
}

export async function listAllResolvedGroups(): Promise<ResolvedAgentGroup[]> {
  const builtins = AGENT_GROUPS.map((g) => builtinToResolved(g.id)!);
  const users = await listUserGroups();
  const custom = users.map(
    (user): ResolvedAgentGroup => ({
      id: user.id,
      name: user.name,
      blurb: user.blurb,
      maxMembers: user.maxMembers,
      members: user.members.map((m) => ({
        id: m.id,
        name: m.name,
        mode: m.mode,
        role: m.role,
        color: m.color,
        icon: m.icon,
        isOrchestrator: m.isOrchestrator,
        customAgentId: m.customAgentId,
        sourceId: m.sourceId,
        kind: m.kind,
      })),
      workflow: user.workflow,
      operation: user.operation,
      orchestratorMemberId: user.orchestratorMemberId,
      builtin: false,
    }),
  );
  return [...custom, ...builtins];
}
