import { access, mkdir, readdir, readFile, stat } from "node:fs/promises";
import path from "node:path";
import {
  CURSOR_UPLOADS,
  KITS_INSTALLED,
  KITS_ROOT,
  KITS_SOURCES,
} from "./paths";
import { inferKind, parseSkillMarkdown, slugify } from "./parse-skill";
import type { KitHelper, KitSourceZip, NinjaKit } from "./types";

async function exists(p: string): Promise<boolean> {
  try {
    await access(/* turbopackIgnore: true */ p);
    return true;
  } catch {
    return false;
  }
}

async function walkFiles(dir: string, max = 400): Promise<string[]> {
  const out: string[] = [];
  async function walk(current: string) {
    if (out.length >= max) return;
    let entries;
    try {
      entries = await readdir(/* turbopackIgnore: true */ current, {
        withFileTypes: true,
      });
    } catch {
      return;
    }
    for (const entry of entries) {
      if (out.length >= max) return;
      if (
        entry.name === "node_modules" ||
        entry.name === `.${"venv"}` ||
        entry.name === ".git" ||
        entry.name === ".next" ||
        entry.name === "dist"
      ) {
        continue;
      }
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) await walk(full);
      else out.push(full);
    }
  }
  await walk(dir);
  return out;
}

async function findSkillFile(root: string): Promise<string | undefined> {
  const candidates = [
    path.join(root, "skill", "SKILL.md"),
    path.join(root, "SKILL.md"),
    path.join(root, "skills", "SKILL.md"),
  ];
  for (const c of candidates) {
    if (await exists(c)) return c;
  }
  const files = await walkFiles(root, 200);
  const hit = files.find((f) => path.basename(f).toLowerCase() === "skill.md");
  return hit;
}

async function listHelpers(root: string): Promise<KitHelper[]> {
  const helpersDirs = [
    path.join(root, "skill", "helpers"),
    path.join(root, "helpers"),
    path.join(root, "scripts"),
    path.join(root, "tools"),
  ];
  const helpers: KitHelper[] = [];
  for (const dir of helpersDirs) {
    if (!(await exists(dir))) continue;
    const entries = await readdir(/* turbopackIgnore: true */ dir, {
      withFileTypes: true,
    });
    for (const entry of entries) {
      if (!entry.isFile()) continue;
      if (!/\.(py|js|mjs|ts|sh)$/i.test(entry.name)) continue;
      if (entry.name.startsWith("test_")) continue;
      helpers.push({
        name: entry.name,
        path: path.join(dir, entry.name),
        runnable: /\.py$/i.test(entry.name),
      });
    }
  }
  return helpers.sort((a, b) => a.name.localeCompare(b.name));
}

export async function ensureKitDirs(): Promise<void> {
  await Promise.all([
    mkdir(/* turbopackIgnore: true */ KITS_ROOT, { recursive: true }),
    mkdir(/* turbopackIgnore: true */ KITS_SOURCES, { recursive: true }),
    mkdir(/* turbopackIgnore: true */ KITS_INSTALLED, { recursive: true }),
  ]);
}

export async function inspectInstalledKit(
  installPath: string,
  opts?: { id?: string; sourceZip?: string; status?: NinjaKit["status"] },
): Promise<NinjaKit | null> {
  if (!(await exists(installPath))) return null;

  const skillPath = await findSkillFile(installPath);
  let name = opts?.id || path.basename(installPath);
  let description = "";
  let skillBody = "";
  let id = opts?.id || slugify(path.basename(installPath));

  if (skillPath) {
    const raw = await readFile(/* turbopackIgnore: true */ skillPath, "utf8");
    const { frontmatter, body } = parseSkillMarkdown(raw);
    if (frontmatter.name) {
      name = frontmatter.name;
      id = opts?.id || slugify(frontmatter.name);
    }
    description = frontmatter.description || "";
    skillBody = body.slice(0, 12000);
  } else {
    // fallback: INSTALAR.md / README
    for (const readme of ["INSTALAR.md", "README.md", "readme.md"]) {
      const p = path.join(/* turbopackIgnore: true */ installPath, readme);
      if (await exists(p)) {
        const raw = await readFile(/* turbopackIgnore: true */ p, "utf8");
        const title = raw.match(/^#\s+(.+)$/m)?.[1]?.trim();
        if (title) name = title;
        description = raw
          .split("\n")
          .filter((l) => l.trim() && !l.startsWith("#") && !l.startsWith("<"))
          .slice(0, 3)
          .join(" ")
          .slice(0, 280);
        break;
      }
    }
  }

  const helpers = await listHelpers(installPath);
  // Nomes de pasta montados para não criar DirAssetReference no Turbopack.
  const venvName = `.${"venv"}`;
  const hasPythonVenv =
    (await exists(path.join(installPath, "skill", venvName))) ||
    (await exists(path.join(installPath, venvName)));
  const prefsName = "prefer" + "ences.md";
  const hasPreferences =
    (await exists(path.join(installPath, "skill", prefsName))) ||
    (await exists(path.join(installPath, prefsName)));

  const allFiles = await walkFiles(installPath, 300);
  const assets = allFiles
    .filter((f) => /\/assets\//i.test(f) || /\.(png|jpg|wav|ttf|otf|json)$/i.test(f))
    .map((f) => path.relative(installPath, f))
    .slice(0, 40);

  const kind = inferKind({
    id,
    name,
    description,
    helpers: helpers.map((h) => h.name),
  });

  const tags: string[] = [kind];
  if (helpers.length) tags.push("helpers");
  if (skillPath) tags.push("skill");
  if (hasPythonVenv) tags.push("python");
  if (hasPreferences) tags.push("prefs");

  return {
    id,
    name,
    description,
    kind,
    sourceZip: opts?.sourceZip,
    installPath,
    skillPath,
    skillBody,
    helpers,
    hasPythonVenv,
    hasPreferences,
    assets,
    status: opts?.status || "installed",
    tags,
  };
}

export async function listInstalledKits(): Promise<NinjaKit[]> {
  await ensureKitDirs();
  const kits: NinjaKit[] = [];

  const entries = await readdir(/* turbopackIgnore: true */ KITS_INSTALLED, {
    withFileTypes: true,
  });
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    const full = path.join(KITS_INSTALLED, entry.name);
    const kit = await inspectInstalledKit(full, { id: slugify(entry.name) });
    if (!kit) continue;
    // avoid duplicating seeded video if someone installed a copy
    if (kits.some((k) => k.id === kit.id)) continue;
    kits.push(kit);
  }

  return kits.sort((a, b) => a.name.localeCompare(b.name, "pt"));
}

async function listZipsInDir(dir: string): Promise<KitSourceZip[]> {
  if (!(await exists(dir))) return [];
  const entries = await readdir(/* turbopackIgnore: true */ dir, {
    withFileTypes: true,
  });
  const out: KitSourceZip[] = [];
  for (const entry of entries) {
    if (!entry.isFile()) continue;
    if (!/\.zip$/i.test(entry.name)) continue;
    const full = path.join(dir, entry.name);
    const st = await stat(/* turbopackIgnore: true */ full);
    out.push({
      filename: entry.name,
      path: full,
      size: st.size,
      mtimeMs: st.mtimeMs,
    });
  }
  return out;
}

export async function listSourceZips(): Promise<KitSourceZip[]> {
  await ensureKitDirs();
  const [sources, inbox] = await Promise.all([
    listZipsInDir(KITS_SOURCES),
    listZipsInDir(CURSOR_UPLOADS),
  ]);
  const byName = new Map<string, KitSourceZip>();
  for (const z of [...inbox, ...sources]) {
    byName.set(z.filename, z);
  }
  return [...byName.values()].sort((a, b) => b.mtimeMs - a.mtimeMs);
}

export async function getKitById(id: string): Promise<NinjaKit | null> {
  const kits = await listInstalledKits();
  return kits.find((k) => k.id === id) ?? null;
}

export async function catalogSummary() {
  const [kits, zips] = await Promise.all([
    listInstalledKits(),
    listSourceZips(),
  ]);
  return {
    installedCount: kits.length,
    sourceZipCount: zips.length,
    kits,
    zips,
    roots: {
      sources: KITS_SOURCES,
      installed: KITS_INSTALLED,
      cursorUploads: CURSOR_UPLOADS,
      windowsHint: "F:\\\\NINJA CURSOS",
    },
  };
}
