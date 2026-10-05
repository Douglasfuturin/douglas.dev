import { NextResponse } from "next/server";
import {
  listPublishQueue,
  markPublishSent,
  queuePublish,
} from "@/lib/content/store";
import type { ContentNetwork } from "@/lib/content/types";

export const runtime = "nodejs";

/**
 * Personal publish queue.
 * With BUFFER_ACCESS_TOKEN (optional) we mark jobs as sent after a stub handoff.
 * Without it, jobs stay queued/scheduled in data/content/store.json for manual post.
 */
export async function GET() {
  const queue = await listPublishQueue();
  return NextResponse.json({
    ok: true,
    queue,
    bufferConfigured: Boolean(process.env.BUFFER_ACCESS_TOKEN),
  });
}

export async function POST(req: Request) {
  const body = (await req.json()) as {
    contentId?: string;
    network?: ContentNetwork;
    scheduledAt?: string;
    caption?: string;
    mediaPath?: string;
    jobId?: string;
    action?: "queue" | "mark_sent" | "mark_failed";
    externalId?: string;
    error?: string;
  };

  if (body.action === "mark_sent" || body.action === "mark_failed") {
    if (!body.jobId) {
      return NextResponse.json(
        { ok: false, error: "jobId_required" },
        { status: 400 },
      );
    }
    const job = await markPublishSent(body.jobId, {
      externalId: body.externalId,
      error: body.action === "mark_failed" ? body.error || "failed" : undefined,
    });
    if (!job) {
      return NextResponse.json(
        { ok: false, error: "job_not_found" },
        { status: 404 },
      );
    }
    return NextResponse.json({ ok: true, job });
  }

  if (!body.contentId || !body.network) {
    return NextResponse.json(
      { ok: false, error: "contentId_and_network_required" },
      { status: 400 },
    );
  }

  const job = await queuePublish({
    contentId: body.contentId,
    network: body.network,
    scheduledAt: body.scheduledAt,
    caption: body.caption,
    mediaPath: body.mediaPath,
  });

  if (!job) {
    return NextResponse.json(
      { ok: false, error: "content_not_found" },
      { status: 404 },
    );
  }

  // Optional: if Buffer token exists, auto-mark as sent (personal stub —
  // real Buffer API posting can be wired later without changing this shape).
  if (process.env.BUFFER_ACCESS_TOKEN && !body.scheduledAt) {
    const sent = await markPublishSent(job.id, {
      externalId: `local-buffer-${Date.now()}`,
    });
    return NextResponse.json({
      ok: true,
      job: sent,
      note: "BUFFER_ACCESS_TOKEN presente — marcado como enviado (stub local). Conecte a API Buffer real se quiser post automático.",
    });
  }

  return NextResponse.json({
    ok: true,
    job,
    note: "Na fila local. Publique manualmente ou configure BUFFER_ACCESS_TOKEN / APIs sociais.",
  });
}
