import { NextResponse } from "next/server";
import {
  advanceContent,
  deleteContent,
  getContent,
  updateContent,
} from "@/lib/content/store";
import type { ContentItem } from "@/lib/content/types";

export const runtime = "nodejs";

type Ctx = { params: Promise<{ id: string }> };

export async function GET(_req: Request, ctx: Ctx) {
  const { id } = await ctx.params;
  const item = await getContent(id);
  if (!item) {
    return NextResponse.json(
      { ok: false, error: "not_found" },
      { status: 404 },
    );
  }
  return NextResponse.json({ ok: true, item });
}

export async function PATCH(req: Request, ctx: Ctx) {
  const { id } = await ctx.params;
  const body = (await req.json()) as Partial<ContentItem> & {
    action?: "advance";
  };

  if (body.action === "advance") {
    const item = await advanceContent(id);
    if (!item) {
      return NextResponse.json(
        { ok: false, error: "not_found" },
        { status: 404 },
      );
    }
    return NextResponse.json({ ok: true, item });
  }

  const {
    action: _a,
    id: _id,
    createdAt: _c,
    updatedAt: _u,
    ...patch
  } = body as Partial<ContentItem> & { action?: string };

  const item = await updateContent(id, patch);
  if (!item) {
    return NextResponse.json(
      { ok: false, error: "not_found" },
      { status: 404 },
    );
  }
  return NextResponse.json({ ok: true, item });
}

export async function DELETE(_req: Request, ctx: Ctx) {
  const { id } = await ctx.params;
  const ok = await deleteContent(id);
  if (!ok) {
    return NextResponse.json(
      { ok: false, error: "not_found" },
      { status: 404 },
    );
  }
  return NextResponse.json({ ok: true });
}
