import { NextResponse } from "next/server";
import {
  getRegistryAgent,
  updateRegistryAgent,
} from "@/lib/agents/registry/store";
import { listAgentVersions } from "@/lib/agents/registry/versions";
import type { ToolkitPreset } from "@/lib/agents/custom-types";

export const runtime = "nodejs";

export async function GET(
  _req: Request,
  ctx: { params: Promise<{ id: string }> },
) {
  const { id } = await ctx.params;
  const agent = await getRegistryAgent(id);
  if (!agent) {
    return NextResponse.json({ ok: false, error: "not_found" }, { status: 404 });
  }
  const versions = await listAgentVersions(id);
  return NextResponse.json({ ok: true, agent, versions });
}

export async function PATCH(
  req: Request,
  ctx: { params: Promise<{ id: string }> },
) {
  const { id } = await ctx.params;
  const body = (await req.json()) as Partial<{
    name: string;
    role: string;
    systemPrompt: string;
    toolkit: ToolkitPreset;
    model: "chat" | "multi";
    status: "active" | "paused" | "archived";
  }>;

  const result = await updateRegistryAgent(id, body);
  if (!result) {
    return NextResponse.json({ ok: false, error: "not_found" }, { status: 404 });
  }

  const { syncCustomStoreFromRegistry } = await import(
    "@/lib/agents/registry/sync-custom"
  );
  await syncCustomStoreFromRegistry(result.agent);

  return NextResponse.json({ ok: true, agent: result.agent, diff: result.diff });
}
