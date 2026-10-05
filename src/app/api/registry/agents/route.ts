import { NextResponse } from "next/server";
import { listRegistryAgents } from "@/lib/agents/registry/store";

export const runtime = "nodejs";

export async function GET(req: Request) {
  const url = new URL(req.url);
  const status = url.searchParams.get("status") as
    | "active"
    | "paused"
    | "archived"
    | "all"
    | null;

  const agents = await listRegistryAgents({
    status: status || "active",
  });

  return NextResponse.json({ ok: true, agents });
}
