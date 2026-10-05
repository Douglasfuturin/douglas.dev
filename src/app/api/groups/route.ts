import { NextResponse } from "next/server";
import { listCatalogAgents } from "@/lib/agents/agent-catalog";
import { listAllResolvedGroups } from "@/lib/agents/group-resolve";
import { createUserGroup } from "@/lib/agents/group-store";
import { listCustomAgents } from "@/lib/agents/custom-store";
import {
  OPERATION_LABELS,
  OPERATIONS,
  type OperationId,
} from "@/lib/agents/group-types";

export const runtime = "nodejs";

export async function GET() {
  const [groups, customAgents] = await Promise.all([
    listAllResolvedGroups(),
    listCustomAgents(),
  ]);
  return NextResponse.json({
    ok: true,
    groups,
    catalog: listCatalogAgents(),
    customAgents: customAgents.map((a) => ({
      id: a.id,
      name: a.name,
      role: a.role,
      color: a.color,
      toolkit: a.toolkit,
    })),
    operations: OPERATIONS.map((id) => ({
      id,
      label: OPERATION_LABELS[id],
    })),
  });
}

export async function POST(req: Request) {
  const body = (await req.json()) as {
    name?: string;
    blurb?: string;
    operation?: OperationId;
    workflow?: string[];
    memberSourceIds?: string[];
  };

  if (!body.name?.trim()) {
    return NextResponse.json(
      { ok: false, error: "name_required" },
      { status: 400 },
    );
  }

  const group = await createUserGroup({
    name: body.name,
    blurb: body.blurb,
    operation: body.operation,
    workflow: body.workflow,
    memberSourceIds: body.memberSourceIds,
  });

  return NextResponse.json({ ok: true, group });
}
