import { createReadStream, existsSync, statSync } from "node:fs";
import { Readable } from "node:stream";
import { resolveSafeMediaPath } from "@/lib/editor/safe-path";

export const runtime = "nodejs";

export async function GET(req: Request) {
  const url = new URL(req.url);
  const raw = url.searchParams.get("path");
  if (!raw) {
    return Response.json({ error: "path obrigatório" }, { status: 400 });
  }

  const filePath = resolveSafeMediaPath(raw);
  if (!filePath || !existsSync(filePath)) {
    return Response.json({ error: "arquivo não encontrado" }, { status: 404 });
  }

  const stat = statSync(filePath);
  const range = req.headers.get("range");
  const contentType = filePath.endsWith(".webm")
    ? "video/webm"
    : filePath.endsWith(".mov")
      ? "video/quicktime"
      : "video/mp4";

  if (range) {
    const match = /bytes=(\d+)-(\d*)/.exec(range);
    if (!match) {
      return new Response("Invalid range", { status: 416 });
    }
    const start = Number(match[1]);
    const end = match[2] ? Number(match[2]) : Math.min(start + 1024 * 1024, stat.size - 1);
    const stream = createReadStream(filePath, { start, end });
    return new Response(Readable.toWeb(stream) as ReadableStream, {
      status: 206,
      headers: {
        "Content-Type": contentType,
        "Content-Length": String(end - start + 1),
        "Content-Range": `bytes ${start}-${end}/${stat.size}`,
        "Accept-Ranges": "bytes",
        "Cache-Control": "no-store",
      },
    });
  }

  const stream = createReadStream(filePath);
  return new Response(Readable.toWeb(stream) as ReadableStream, {
    headers: {
      "Content-Type": contentType,
      "Content-Length": String(stat.size),
      "Accept-Ranges": "bytes",
      "Cache-Control": "no-store",
    },
  });
}
