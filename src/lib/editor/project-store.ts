import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import {
  DEFAULT_VIDEO_OPTIONS,
  STYLE_LABELS,
  VIDEO_STYLES,
  type VideoEditOptions,
  type VideoFormat,
  type VideoStyle,
} from "@/lib/video/options";
import type {
  EditorProject,
  EditorProjectInput,
  EditorProjectPatch,
  EditorProjectStore,
} from "./project-types";

const DATA_DIR = path.join(process.cwd(), "data", "editor");
const STORE_PATH = path.join(DATA_DIR, "projects.json");

function nowIso() {
  return new Date().toISOString();
}

function id() {
  return `edp_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}

function slugify(name: string): string {
  return name
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 48) || "projeto";
}

/** Formato padrão derivado do nome do estilo. */
export function defaultFormatForStyle(estilo: VideoStyle): VideoFormat {
  if (
    estilo.includes("reel") ||
    estilo.includes("vertical") ||
    estilo.includes("shorts") ||
    estilo.includes("story") ||
    estilo.includes("hook") ||
    estilo.includes("teaser") ||
    estilo.includes("vsl") ||
    estilo.includes("criativo") ||
    estilo.includes("unboxing") ||
    estilo.includes("tutorial") ||
    estilo.includes("pitch") ||
    estilo.includes("lorcana-curto") ||
    estilo.includes("anuncio") ||
    estilo.includes("doc-vertical") ||
    estilo.includes("avatar")
  ) {
    return "9:16";
  }
  if (estilo === "feed-quadrado") return "1:1";
  if (estilo === "carrossel") return "4:5";
  if (estilo === "cold-open") return "21:9";
  return "16:9";
}

export function optionsForStyle(
  estilo: VideoStyle,
  overrides?: Partial<VideoEditOptions>,
): VideoEditOptions {
  const formato = overrides?.formato ?? defaultFormatForStyle(estilo);
  return {
    ...DEFAULT_VIDEO_OPTIONS,
    ...overrides,
    estilo,
    formato,
    projeto: overrides?.projeto ?? slugify(estilo),
  };
}

const SEED_STYLES: VideoStyle[] = [
  "aula-ccnp",
  "reel-mono",
  "reel-editorial",
  "shorts-rapido",
  "podcast",
  "vsl",
  "tutorial",
  "webinar",
  "hook-15s",
  "entrevista",
];

function seedProjects(): EditorProject[] {
  const ts = nowIso();
  return SEED_STYLES.map((estilo, index) => {
    const name = STYLE_LABELS[estilo];
    const slug = slugify(estilo);
    return {
      id: `edp_seed_${estilo}`,
      name,
      slug,
      estilo,
      description: `Preferências isoladas para o estilo ${name}.`,
      options: optionsForStyle(estilo, { projeto: slug }),
      mediaPath: null,
      mediaFilename: null,
      takes: [],
      analysisSummary: null,
      outputUrl: null,
      createdAt: ts,
      updatedAt: new Date(Date.parse(ts) + index).toISOString(),
    };
  });
}

function emptyStore(): EditorProjectStore {
  const projects = seedProjects();
  return {
    version: 1,
    activeProjectId: projects[0]?.id ?? null,
    projects,
  };
}

function isVideoStyle(value: unknown): value is VideoStyle {
  return (
    typeof value === "string" &&
    (VIDEO_STYLES as readonly string[]).includes(value)
  );
}

function sanitizeOptions(
  estilo: VideoStyle,
  options: Partial<VideoEditOptions> | undefined,
  projetoSlug: string,
): VideoEditOptions {
  return optionsForStyle(estilo, {
    ...options,
    estilo,
    projeto: projetoSlug,
  });
}

async function ensureStore(): Promise<EditorProjectStore> {
  await mkdir(DATA_DIR, { recursive: true });
  try {
    const raw = await readFile(STORE_PATH, "utf8");
    const parsed = JSON.parse(raw) as EditorProjectStore;
    if (!Array.isArray(parsed.projects)) parsed.projects = [];
    if (parsed.version !== 1) parsed.version = 1;
    if (parsed.projects.length === 0) {
      const seeded = emptyStore();
      await saveStore(seeded);
      return seeded;
    }
    return parsed;
  } catch {
    const store = emptyStore();
    await saveStore(store);
    return store;
  }
}

async function saveStore(store: EditorProjectStore) {
  await mkdir(DATA_DIR, { recursive: true });
  await writeFile(STORE_PATH, JSON.stringify(store, null, 2), "utf8");
}

function uniqueSlug(base: string, existing: string[]): string {
  let slug = slugify(base);
  if (!existing.includes(slug)) return slug;
  let n = 2;
  while (existing.includes(`${slug}-${n}`)) n += 1;
  return `${slug}-${n}`;
}

export async function listEditorProjects(): Promise<EditorProject[]> {
  const store = await ensureStore();
  return [...store.projects].sort((a, b) =>
    b.updatedAt.localeCompare(a.updatedAt),
  );
}

export async function getActiveProjectId(): Promise<string | null> {
  const store = await ensureStore();
  return store.activeProjectId;
}

export async function getEditorProject(
  projectId: string,
): Promise<EditorProject | null> {
  const store = await ensureStore();
  return store.projects.find((p) => p.id === projectId) ?? null;
}

export async function setActiveEditorProject(
  projectId: string | null,
): Promise<EditorProject | null> {
  const store = await ensureStore();
  if (projectId && !store.projects.some((p) => p.id === projectId)) {
    return null;
  }
  store.activeProjectId = projectId;
  await saveStore(store);
  return projectId
    ? (store.projects.find((p) => p.id === projectId) ?? null)
    : null;
}

export async function createEditorProject(
  input: EditorProjectInput,
): Promise<EditorProject> {
  const store = await ensureStore();
  const estilo = isVideoStyle(input.estilo) ? input.estilo : "aula-ccnp";
  const name = input.name.trim() || STYLE_LABELS[estilo];
  const slug = uniqueSlug(
    input.options?.projeto || name || estilo,
    store.projects.map((p) => p.slug),
  );
  const ts = nowIso();
  const project: EditorProject = {
    id: id(),
    name,
    slug,
    estilo,
    description:
      input.description?.trim() ||
      `Preferências isoladas para o estilo ${STYLE_LABELS[estilo]}.`,
    options: sanitizeOptions(estilo, input.options, slug),
    mediaPath: null,
    mediaFilename: null,
    takes: [],
    analysisSummary: null,
    outputUrl: null,
    createdAt: ts,
    updatedAt: ts,
  };
  store.projects.unshift(project);
  store.activeProjectId = project.id;
  await saveStore(store);
  return project;
}

export async function updateEditorProject(
  projectId: string,
  patch: EditorProjectPatch,
): Promise<EditorProject | null> {
  const store = await ensureStore();
  const index = store.projects.findIndex((p) => p.id === projectId);
  if (index < 0) return null;

  const current = store.projects[index];
  const nextEstilo = isVideoStyle(patch.estilo) ? patch.estilo : current.estilo;
  const nextOptions = patch.options
    ? sanitizeOptions(nextEstilo, { ...current.options, ...patch.options }, current.slug)
    : nextEstilo !== current.estilo
      ? sanitizeOptions(nextEstilo, current.options, current.slug)
      : current.options;

  const updated: EditorProject = {
    ...current,
    name: patch.name?.trim() || current.name,
    description:
      typeof patch.description === "string"
        ? patch.description
        : current.description,
    estilo: nextEstilo,
    options: nextOptions,
    mediaPath:
      patch.mediaPath !== undefined ? patch.mediaPath : current.mediaPath,
    mediaFilename:
      patch.mediaFilename !== undefined
        ? patch.mediaFilename
        : current.mediaFilename,
    takes: patch.takes !== undefined ? patch.takes : current.takes,
    analysisSummary:
      patch.analysisSummary !== undefined
        ? patch.analysisSummary
        : current.analysisSummary,
    outputUrl:
      patch.outputUrl !== undefined ? patch.outputUrl : current.outputUrl,
    updatedAt: nowIso(),
  };

  store.projects[index] = updated;
  store.activeProjectId = updated.id;
  await saveStore(store);
  return updated;
}

export async function deleteEditorProject(
  projectId: string,
): Promise<boolean> {
  const store = await ensureStore();
  const before = store.projects.length;
  store.projects = store.projects.filter((p) => p.id !== projectId);
  if (store.projects.length === before) return false;
  if (store.activeProjectId === projectId) {
    store.activeProjectId = store.projects[0]?.id ?? null;
  }
  await saveStore(store);
  return true;
}
