import { NextResponse } from "next/server";
import {
  deleteCustomAgent,
  getCustomAgent,
  updateCustomAgent,
} from "@/lib/agents/custom-store";
import type { ToolkitPreset } from "@/lib/agents/custom-types";

export const runtime = "nodejs";

type Ctx = { params: Promise<{ id: string }> };

export async function GET(_req: Request, ctx: Ctx) {
  const { id } = await ctx.params;
  const agent = await getCustomAgent(id);
  if (!agent) {
    return NextResponse.json({ ok: false, error: "not_found" }, { status: 404 });
  }
  return NextResponse.json({ ok: true, agent });
}

export async function PATCH(req: Request, ctx: Ctx) {
  const { id } = await ctx.params;
  const body = (await req.json()) as {
    name?: string;
    role?: string;
    instructions?: string;
    toolkit?: ToolkitPreset;
    color?: string;
    avatar?: string;
  };
  const agent = await updateCustomAgent(id, body);
  if (!agent) {
    return NextResponse.json({ ok: false, error: "not_found" }, { status: 404 });
  }
  return NextResponse.json({ ok: true, agent });
}

export async function DELETE(_req: Request, ctx: Ctx) {
  const { id } = await ctx.params;
  const ok = await deleteCustomAgent(id);
  if (!ok) {
    return NextResponse.json({ ok: false, error: "not_found" }, { status: 404 });
  }
  return NextResponse.json({ ok: true });
}
