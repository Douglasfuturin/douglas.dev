import { NextResponse } from "next/server";
import { undoLastOrchestratorAction } from "@/lib/agents/registry/actions-log";

export const runtime = "nodejs";

export async function POST() {
  const result = await undoLastOrchestratorAction();
  const status = result.ok ? 200 : 400;
  return NextResponse.json(result, { status });
}
