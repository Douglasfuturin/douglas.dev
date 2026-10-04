export type SkillFrontmatter = {
  name?: string;
  description?: string;
  [key: string]: string | undefined;
};

export function parseSkillMarkdown(raw: string): {
  frontmatter: SkillFrontmatter;
  body: string;
} {
  const trimmed = raw.replace(/^\uFEFF/, "");
  if (!trimmed.startsWith("---")) {
    return { frontmatter: {}, body: trimmed };
  }
  const end = trimmed.indexOf("\n---", 3);
  if (end < 0) {
    return { frontmatter: {}, body: trimmed };
  }
  const yaml = trimmed.slice(4, end).trim();
  const body = trimmed.slice(end + 4).replace(/^\s*\n/, "");
  const frontmatter: SkillFrontmatter = {};
  for (const line of yaml.split("\n")) {
    const m = line.match(/^([A-Za-z0-9_-]+)\s*:\s*(.*)$/);
    if (!m) continue;
    let value = m[2].trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    frontmatter[m[1]] = value;
  }
  return { frontmatter, body };
}

export function inferKind(input: {
  id: string;
  name: string;
  description: string;
  helpers: string[];
}): import("./types").KitKind {
  const blob = `${input.id} ${input.name} ${input.description} ${input.helpers.join(" ")}`.toLowerCase();
  if (
    /v[ií]deo|editar-video|fabrica|transcribe|reel|legenda|mp4|ffmpeg/.test(
      blob,
    )
  ) {
    return "video";
  }
  if (/photoshop|design|imagem|manipula|midjourney|flux/.test(blob)) {
    return "design";
  }
  if (/automa[cç]|n8n|workflow|mcp|agent|bot/.test(blob)) {
    return "automation";
  }
  if (/curso|aula|trilha|m[oó]dulo/.test(blob)) {
    return "course";
  }
  if (/skill|claude|grill|prompt/.test(blob)) {
    return "skill";
  }
  return "unknown";
}

export function slugify(input: string): string {
  return input
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80) || "kit";
}
