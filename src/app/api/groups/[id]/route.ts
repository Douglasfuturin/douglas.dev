import { NextResponse } from "next/server";
import {
  addMemberToGroup,
  deleteUserGroup,
  getUserGroup,
  removeMemberFromGroup,
  setGroupOrchestrator,
  updateUserGroup,
} from "@/lib/agents/group-store";
import { resolveAgentGroup } from "@/lib/agents/group-resolve";
import type { OperationId } from "@/lib/agents/group-types";

export const runtime = "nodejs";

type Ctx = { params: Promise<{ id: string }> };

export async function GET(_req: Request, ctx: Ctx) {
  const { id } = await ctx.params;
  const group = await resolveAgentGroup(id);
  if (!group) {
    return NextResponse.json({ ok: false, error: "not_found" }, { status: 404 });
  }
  return NextResponse.json({ ok: true, group });
}

export async function PATCH(req: Request, ctx: Ctx) {
  const { id } = await ctx.params;
  const body = (await req.json()) as {
    action?:
      | "update"
      | "add_member"
      | "remove_member"
      | "set_orchestrator";
    name?: string;
    blurb?: string;
    operation?: OperationId;
    workflow?: string[];
    sourceId?: string;
    memberId?: string;
  };

  const existing = await getUserGroup(id);
  if (!existing) {
    return NextResponse.json(
      { ok: false, error: "builtin_or_missing" },
      { status: 400 },
    );
  }

  try {
    const action = body.action || "update";
    if (action === "add_member") {
      if (!body.sourceId) {
        return NextResponse.json(
          { ok: false, error: "sourceId_required" },
          { status: 400 },
        );
      }
      const group = await addMemberToGroup(id, body.sourceId);
      return NextResponse.json({ ok: true, group });
    }
    if (action === "remove_member") {
      if (!body.memberId) {
        return NextResponse.json(
          { ok: false, error: "memberId_required" },
          { status: 400 },
        );
      }
      const group = await removeMemberFromGroup(id, body.memberId);
      return NextResponse.json({ ok: true, group });
    }
    if (action === "set_orchestrator") {
      if (!body.memberId) {
        return NextResponse.json(
          { ok: false, error: "memberId_required" },
          { status: 400 },
        );
      }
      const group = await setGroupOrchestrator(id, body.memberId);
      return NextResponse.json({ ok: true, group });
    }

    const group = await updateUserGroup(id, {
      name: body.name,
      blurb: body.blurb,
      operation: body.operation,
      workflow: body.workflow,
    });
    return NextResponse.json({ ok: true, group });
  } catch (err) {
    const message = err instanceof Error ? err.message : "error";
    const status =
      message === "group_full" ||
      message === "already_member" ||
      message === "cannot_remove_orchestrator"
        ? 400
        : 404;
    return NextResponse.json({ ok: false, error: message }, { status });
  }
}

export async function DELETE(_req: Request, ctx: Ctx) {
  const { id } = await ctx.params;
  const ok = await deleteUserGroup(id);
  if (!ok) {
    return NextResponse.json(
      { ok: false, error: "builtin_or_missing" },
      { status: 400 },
    );
  }
  return NextResponse.json({ ok: true });
}
