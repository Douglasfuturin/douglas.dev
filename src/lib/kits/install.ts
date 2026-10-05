import { copyFile, mkdir, readdir, rename, rm, stat } from "node:fs/promises";
import { spawn } from "node:child_process";
import path from "node:path";
import { ensureKitDirs, inspectInstalledKit } from "./discover";
import { KITS_INSTALLED, KITS_SOURCES } from "./paths";
import { slugify } from "./parse-skill";
import type { NinjaKit } from "./types";

function run(cmd: string, args: string[]): Promise<{ ok: boolean; stderr: string }> {
  return new Promise((resolve) => {
    const child = spawn(/* turbopackIgnore: true */ cmd, args, {
      env: process.env,
    });
    let stderr = "";
    child.stderr.on("data", (c: Buffer) => {
      stderr += c.toString();
    });
    child.on("error", (err) =>
      resolve({ ok: false, stderr: err.message }),
    );
    child.on("close", (code) =>
      resolve({ ok: code === 0, stderr: stderr.trim() }),
    );
  });
}

async function uniqueDir(base: string): Promise<string> {
  let dir = base;
  let i = 2;
  while (true) {
    try {
      await stat(/* turbopackIgnore: true */ dir);
      dir = `${base}-${i++}`;
    } catch {
      return dir;
    }
  }
}

/** Acha a pasta raiz útil dentro do unzip (onde tem SKILL.md / skill/). */
async function resolveKitRoot(extractDir: string): Promise<string> {
  const entries = await readdir(extractDir, { withFileTypes: true });
  const files = entries.filter((e) => e.isFile()).map((e) => e.name.toLowerCase());
  if (files.includes("skill.md") || files.includes("instalar.md") || files.includes("readme.md")) {
    return extractDir;
  }
  if (entries.some((e) => e.isDirectory() && e.name === "skill")) {
    return extractDir;
  }
  const dirs = entries.filter((e) => e.isDirectory() && !e.name.startsWith("."));
  if (dirs.length === 1) {
    return path.join(extractDir, dirs[0].name);
  }
  for (const d of dirs) {
    const nested = path.join(extractDir, d.name);
    const nestedEntries = await readdir(nested, { withFileTypes: true });
    const names = nestedEntries.map((e) => e.name.toLowerCase());
    if (
      names.includes("skill.md") ||
      names.includes("skill") ||
      names.includes("instalar.md")
    ) {
      return nested;
    }
  }
  return extractDir;
}

export async function importZipToSources(zipPath: string): Promise<string> {
  await ensureKitDirs();
  const filename = path.basename(zipPath);
  const dest = path.join(KITS_SOURCES, filename);
  if (path.resolve(zipPath) !== path.resolve(dest)) {
    await copyFile(zipPath, dest);
  }
  return dest;
}

export async function installKitFromZip(
  zipPath: string,
  opts?: { id?: string },
): Promise<{ ok: boolean; kit?: NinjaKit; error?: string }> {
  await ensureKitDirs();
  const st = await stat(zipPath).catch(() => null);
  if (!st) {
    return { ok: false, error: `ZIP não encontrado: ${zipPath}` };
  }

  const baseName = path.basename(zipPath, path.extname(zipPath));
  const id = slugify(opts?.id || baseName.replace(/_?[a-f0-9]{4,}$/i, ""));
  const staging = path.join(KITS_INSTALLED, `.staging-${id}-${Date.now()}`);
  await mkdir(staging, { recursive: true });

  const unzip = await run("unzip", ["-q", "-o", zipPath, "-d", staging]);
  if (!unzip.ok) {
    await rm(staging, { recursive: true, force: true });
    return {
      ok: false,
      error: `Falha ao descompactar: ${unzip.stderr || "unzip error"}`,
    };
  }

  const kitRoot = await resolveKitRoot(staging);
  const finalDir = await uniqueDir(path.join(KITS_INSTALLED, id));
  await mkdir(path.dirname(finalDir), { recursive: true });

  if (path.resolve(kitRoot) === path.resolve(staging)) {
    await rename(staging, finalDir);
  } else {
    await rename(kitRoot, finalDir);
    await rm(staging, { recursive: true, force: true });
  }

  // keep a copy in sources
  await importZipToSources(zipPath).catch(() => undefined);

  const kit = await inspectInstalledKit(finalDir, {
    id,
    sourceZip: path.basename(zipPath),
    status: "installed",
  });

  if (!kit) {
    return { ok: false, error: "Kit instalado mas não foi possível inspecionar." };
  }

  return { ok: true, kit };
}

export async function installAllSourceZips(paths: string[]): Promise<{
  installed: NinjaKit[];
  errors: Array<{ path: string; error: string }>;
}> {
  const installed: NinjaKit[] = [];
  const errors: Array<{ path: string; error: string }> = [];
  for (const zipPath of paths) {
    const result = await installKitFromZip(zipPath);
    if (result.ok && result.kit) installed.push(result.kit);
    else errors.push({ path: zipPath, error: result.error || "erro" });
  }
  return { installed, errors };
}
