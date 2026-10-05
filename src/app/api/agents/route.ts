import { NextResponse } from "next/server";
import {
  createCustomAgent,
  listCustomAgents,
} from "@/lib/agents/custom-store";
import {
  listRegistryAgents,
  registryToCustomShape,
} from "@/lib/agents/registry/store";
import {
  TOOLKIT_LABELS,
  TOOLKIT_PRESETS,
  type ToolkitPreset,
} from "@/lib/agents/custom-types";

export const runtime = "nodejs";

export async function GET() {
  const registry = await listRegistryAgents({ status: "all" });
  const legacy = await listCustomAgents();
  const byId = new Map<string, ReturnType<typeof registryToCustomShape>>();
  for (const r of registry) {
    byId.set(r.id, registryToCustomShape(r));
  }
  for (const c of legacy) {
    if (!byId.has(c.id)) byId.set(c.id, c);
  }
  const agents = [...byId.values()];
  return NextResponse.json({
    ok: true,
    agents,
    registry: registry.map((a) => ({
      id: a.id,
      name: a.name,
      status: a.status,
      version: a.version,
      seedKey: a.seedKey,
    })),
    toolkits: TOOLKIT_PRESETS.map((id) => ({
      id,
      label: TOOLKIT_LABELS[id],
    })),
  });
}

export async function POST(req: Request) {
  const body = (await req.json()) as {
    name?: string;
    role?: string;
    instructions?: string;
    toolkit?: ToolkitPreset;
    color?: string;
    avatar?: string;
  };

  if (!body.name?.trim() || !body.role?.trim() || !body.instructions?.trim()) {
    return NextResponse.json(
      { ok: false, error: "name_role_instructions_required" },
      { status: 400 },
    );
  }

  const agent = await createCustomAgent({
    name: body.name,
    role: body.role,
    instructions: body.instructions,
    toolkit: body.toolkit,
    color: body.color,
    avatar: body.avatar,
  });

  return NextResponse.json({ ok: true, agent });
}
