import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { installKitFromZip } from "@/lib/kits/install";
import { KITS_SOURCES } from "@/lib/kits/paths";

export const maxDuration = 300;
export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const form = await req.formData();
  const file = form.get("file");
  const autoInstall = form.get("install") !== "0";

  if (!(file instanceof File)) {
    return Response.json({ error: "Envie um ZIP em 'file'." }, { status: 400 });
  }

  if (!/\.zip$/i.test(file.name)) {
    return Response.json({ error: "Apenas arquivos .zip." }, { status: 400 });
  }

  await mkdir(KITS_SOURCES, { recursive: true });
  const safe = path
    .basename(file.name)
    .replace(/[^a-zA-Z0-9._-]+/g, "-")
    .slice(0, 120);
  const absPath = path.join(KITS_SOURCES, safe);
  const buffer = Buffer.from(await file.arrayBuffer());
  await writeFile(absPath, buffer);

  if (!autoInstall) {
    return Response.json({
      ok: true,
      path: absPath,
      filename: safe,
      size: buffer.byteLength,
      installed: false,
    });
  }

  const result = await installKitFromZip(absPath);
  return Response.json({
    ok: result.ok,
    path: absPath,
    filename: safe,
    size: buffer.byteLength,
    kit: result.kit,
    error: result.error,
  });
}
