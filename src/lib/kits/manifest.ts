import { readFile } from "node:fs/promises";
import path from "node:path";

export type ManifestKit = {
  id: string;
  filename: string;
  category: string;
};

export type NinjaManifest = {
  source: string;
  updatedAt: string;
  kits: ManifestKit[];
};

const MANIFEST_PATH = path.join(process.cwd(), "ninja-kits", "manifest.json");

export const CATEGORY_LABELS: Record<string, string> = {
  youtube: "YouTube",
  instagram: "Instagram",
  ads: "Ads / Meta",
  email: "E-mail",
  web: "Web / Landing",
  design: "Design / Imagem",
  content: "Conteúdo",
  research: "Pesquisa / News",
  business: "Negócios",
  audit: "Auditoria",
  productivity: "Produtividade",
  video: "Vídeo",
  unknown: "Outros",
};

export async function loadManifest(): Promise<NinjaManifest> {
  const raw = await readFile(
    /* turbopackIgnore: true */ MANIFEST_PATH,
    "utf8",
  );
  return JSON.parse(raw) as NinjaManifest;
}

export function categoryForFilename(filename: string): string {
  const n = filename.toLowerCase();
  if (n.includes("youtube")) return "youtube";
  if (n.includes("instagram") || n.includes("carousel") || n.includes("thread"))
    return "instagram";
  if (n.includes("ad") || n.includes("ugc") || n.includes("meta-")) return "ads";
  if (n.includes("email")) return "email";
  if (n.includes("website") || n.includes("landing")) return "web";
  if (
    n.includes("photo") ||
    n.includes("brand-image") ||
    n.includes("diagram") ||
    n.includes("nano-banana")
  )
    return "design";
  if (n.includes("vsl") || n.includes("webinar") || n.includes("conteudo"))
    return "content";
  if (n.includes("hyperframe") || n.includes("editar-video") || n.includes("video"))
    return "video";
  if (n.includes("news") || n.includes("research")) return "research";
  if (n.includes("invoice") || n.includes("contract")) return "business";
  if (n.includes("audit") || n.includes("security") || n.includes("accessib"))
    return "audit";
  if (
    n.includes("goal") ||
    n.includes("morning") ||
    n.includes("team") ||
    n.includes("learning") ||
    n.includes("think")
  )
    return "productivity";
  return "unknown";
}
