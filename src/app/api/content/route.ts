import { NextResponse } from "next/server";
import {
  createContent,
  getStats,
  listContent,
  listPublishQueue,
  seedDemoIfEmpty,
} from "@/lib/content/store";
import type {
  ContentMarket,
  ContentNetwork,
  ContentSource,
  ContentStage,
} from "@/lib/content/types";

export const runtime = "nodejs";

export async function GET(req: Request) {
  const url = new URL(req.url);
  const stage = url.searchParams.get("stage") as ContentStage | null;
  const market = url.searchParams.get("market") as ContentMarket | null;
  const seed = url.searchParams.get("seed") === "1";

  if (seed) await seedDemoIfEmpty();

  const [items, stats, queue] = await Promise.all([
    listContent({
      stage: stage || undefined,
      market: market || undefined,
    }),
    getStats(),
    listPublishQueue(),
  ]);

  return NextResponse.json({ ok: true, items, stats, queue });
}

export async function POST(req: Request) {
  const body = (await req.json()) as {
    title?: string;
    summary?: string;
    stage?: ContentStage;
    market?: ContentMarket;
    networks?: ContentNetwork[];
    source?: ContentSource;
    score?: number;
    tags?: string[];
    topic?: string;
    script?: string;
    caption?: string;
    notes?: string;
    groupId?: string;
  };

  if (!body.title?.trim()) {
    return NextResponse.json(
      { ok: false, error: "title_required" },
      { status: 400 },
    );
  }

  const item = await createContent({
    title: body.title,
    summary: body.summary,
    stage: body.stage,
    market: body.market,
    networks: body.networks,
    source: body.source || "manual",
    score: body.score,
    tags: body.tags,
    topic: body.topic,
    script: body.script,
    caption: body.caption,
    notes: body.notes,
    groupId: body.groupId,
  });

  return NextResponse.json({ ok: true, item });
}
