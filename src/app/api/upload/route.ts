import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { UPLOADS_DIR } from "@/lib/video/paths";

export const maxDuration = 300;

export async function POST(req: Request) {
  const form = await req.formData();
  const file = form.get("file");

  if (!(file instanceof File)) {
    return Response.json({ error: "Envie um arquivo em 'file'." }, { status: 400 });
  }

  const ext = path.extname(file.name) || ".mp4";
  const safeBase = path
    .basename(file.name, ext)
    .replace(/[^a-zA-Z0-9-_]+/g, "-")
    .slice(0, 80);
  const filename = `${Date.now()}-${safeBase || "video"}${ext}`;

  await mkdir(UPLOADS_DIR, { recursive: true });
  const absPath = path.join(UPLOADS_DIR, filename);
  const buffer = Buffer.from(await file.arrayBuffer());
  await writeFile(absPath, buffer);

  return Response.json({
    ok: true,
    path: absPath,
    filename,
    size: buffer.byteLength,
  });
}
