import { NextResponse } from "next/server";
import {
  createCustomAgent,
  listCustomAgents,
} from "@/lib/agents/custom-store";
import {
  TOOLKIT_LABELS,
  TOOLKIT_PRESETS,
  type ToolkitPreset,
} from "@/lib/agents/custom-types";

export const runtime = "nodejs";

export async function GET() {
  const agents = await listCustomAgents();
  return NextResponse.json({
    ok: true,
    agents,
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
