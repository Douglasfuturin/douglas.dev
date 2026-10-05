import { NextResponse } from "next/server";
import { listOrchestratorActions } from "@/lib/agents/registry/actions-log";

export const runtime = "nodejs";

export async function GET(req: Request) {
  const url = new URL(req.url);
  const limit = Number(url.searchParams.get("limit") || "30");
  const actions = await listOrchestratorActions(
    Number.isFinite(limit) ? limit : 30,
  );
  return NextResponse.json({ ok: true, actions });
}
