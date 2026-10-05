import { NextResponse } from "next/server";
import {
  cancelProposal,
  confirmProposal,
} from "@/lib/agents/registry/store";

export const runtime = "nodejs";

export async function POST(
  req: Request,
  ctx: { params: Promise<{ id: string }> },
) {
  const { id } = await ctx.params;
  const body = (await req.json()) as { action?: "confirm" | "cancel" };

  if (body.action === "cancel") {
    const ok = await cancelProposal(id);
    return NextResponse.json({ ok });
  }

  const result = await confirmProposal(id);
  const status = result.ok ? 200 : 400;
  return NextResponse.json(result, { status });
}
