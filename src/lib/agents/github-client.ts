const GH_API = "https://api.github.com";
const UA = "Grokish-GitHub-Scout";

export type GhRepo = {
  id: number;
  full_name: string;
  html_url: string;
  description: string | null;
  language: string | null;
  stargazers_count: number;
  forks_count: number;
  watchers_count: number;
  open_issues_count: number;
  topics?: string[];
  license?: { spdx_id?: string | null } | null;
  archived: boolean;
  fork: boolean;
  created_at: string;
  updated_at: string;
  pushed_at: string;
  homepage?: string | null;
  owner?: { login: string; html_url: string };
  default_branch?: string;
};

export type RankedRepo = {
  rank: number;
  score: number;
  fullName: string;
  url: string;
  description: string;
  language: string | null;
  stars: number;
  forks: number;
  openIssues: number;
  topics: string[];
  license: string | null;
  archived: boolean;
  pushedAt: string;
  why: string[];
};

export function authHeaders(): HeadersInit {
  const headers: Record<string, string> = {
    Accept: "application/vnd.github+json",
    "User-Agent": UA,
    "X-GitHub-Api-Version": "2022-11-28",
  };
  const token =
    process.env.GITHUB_TOKEN ||
    process.env.GH_TOKEN ||
    process.env.GITHUB_PAT ||
    "";
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

export async function ghGet<T>(
  path: string,
  query?: Record<string, string>,
): Promise<T> {
  const url = new URL(path.startsWith("http") ? path : `${GH_API}${path}`);
  if (query) {
    for (const [k, v] of Object.entries(query)) {
      if (v) url.searchParams.set(k, v);
    }
  }
  const res = await fetch(url, {
    headers: authHeaders(),
    cache: "no-store",
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(
      `GitHub API ${res.status}: ${body.slice(0, 300) || res.statusText}`,
    );
  }
  return (await res.json()) as T;
}

export function cleanRepoFullName(fullName: string): string {
  return fullName
    .replace(/^https?:\/\/github\.com\//, "")
    .replace(/\.git$/, "")
    .replace(/\/$/, "")
    .trim();
}

export function daysSince(iso: string): number {
  const t = Date.parse(iso);
  if (Number.isNaN(t)) return 9999;
  return Math.max(0, (Date.now() - t) / (1000 * 60 * 60 * 24));
}

/** Score simples: popularidade + atividade recente + saúde básica. */
export function scoreRepo(repo: GhRepo): { score: number; why: string[] } {
  const why: string[] = [];
  const stars = repo.stargazers_count || 0;
  const forks = repo.forks_count || 0;
  const ageDays = daysSince(repo.pushed_at || repo.updated_at);
  const starScore = Math.log10(stars + 1) * 28;
  const forkScore = Math.log10(forks + 1) * 10;
  let activity = 18;
  if (ageDays <= 30) {
    activity = 22;
    why.push("atualizado no último mês");
  } else if (ageDays <= 90) {
    activity = 18;
    why.push("atividade recente (≤90 dias)");
  } else if (ageDays <= 365) {
    activity = 10;
    why.push("push no último ano");
  } else {
    activity = 2;
    why.push("pouca atividade recente");
  }

  let health = 8;
  if (repo.archived) {
    health -= 20;
    why.push("arquivado");
  }
  if (repo.fork) {
    health -= 8;
    why.push("é um fork");
  }
  if ((repo.open_issues_count || 0) > stars * 0.2 && stars > 200) {
    health -= 4;
    why.push("muitas issues abertas vs. stars");
  } else if (stars > 500) {
    why.push("comunidade forte (stars)");
  }
  if (repo.license?.spdx_id) {
    health += 3;
    why.push(`licença ${repo.license.spdx_id}`);
  }
  if (repo.language) why.push(`linguagem ${repo.language}`);

  const score = Math.round(starScore + forkScore + activity + health);
  return { score: Math.max(0, score), why: why.slice(0, 5) };
}

export function buildSearchQuery(input: {
  query: string;
  language?: string;
  minStars?: number;
  topic?: string;
  includeForks?: boolean;
}): string {
  const parts = [input.query.trim()];
  if (input.language) parts.push(`language:${input.language}`);
  if (input.topic) parts.push(`topic:${input.topic}`);
  if (typeof input.minStars === "number" && input.minStars > 0) {
    parts.push(`stars:>=${input.minStars}`);
  }
  if (!input.includeForks) parts.push("fork:false");
  parts.push("archived:false");
  return parts.filter(Boolean).join(" ");
}

export async function fetchRepoReadmePreview(
  fullName: string,
  maxChars = 4000,
): Promise<string | null> {
  const clean = cleanRepoFullName(fullName);
  try {
    const readme = await ghGet<{ content?: string; encoding?: string }>(
      `/repos/${clean}/readme`,
    );
    if (readme.content && readme.encoding === "base64") {
      return Buffer.from(readme.content, "base64")
        .toString("utf8")
        .slice(0, maxChars);
    }
  } catch {
    return null;
  }
  return null;
}

export async function fetchRepoBundle(fullName: string) {
  const clean = cleanRepoFullName(fullName);
  const repo = await ghGet<GhRepo>(`/repos/${clean}`);
  const { score, why } = scoreRepo(repo);
  const readmePreview = await fetchRepoReadmePreview(clean);
  return {
    fullName: repo.full_name,
    url: repo.html_url,
    description: repo.description,
    language: repo.language,
    stars: repo.stargazers_count,
    forks: repo.forks_count,
    openIssues: repo.open_issues_count,
    topics: repo.topics || [],
    license: repo.license?.spdx_id || null,
    homepage: repo.homepage || null,
    pushedAt: repo.pushed_at,
    createdAt: repo.created_at,
    defaultBranch: repo.default_branch || "main",
    score,
    why,
    readmePreview,
  };
}

/** Extrai blocos de instalação/uso comuns do README. */
export function extractInstallUsageHints(readme: string | null): {
  install: string[];
  usage: string[];
} {
  if (!readme) return { install: [], usage: [] };
  const lines = readme.split(/\r?\n/);
  const install: string[] = [];
  const usage: string[] = [];
  let section: "none" | "install" | "usage" = "none";

  for (const raw of lines) {
    const line = raw.trim();
    const heading = /^#{1,3}\s+(.+)/.exec(line);
    if (heading) {
      const h = heading[1].toLowerCase();
      if (/(install|getting started|quick ?start|setup|início|instal)/i.test(h)) {
        section = "install";
        continue;
      }
      if (/(usage|how to use|example|uso|exemplos?|getting started)/i.test(h)) {
        section = "usage";
        continue;
      }
      section = "none";
      continue;
    }
    if (!line) continue;
    if (section === "install" && install.length < 12) install.push(line);
    if (section === "usage" && usage.length < 12) usage.push(line);
  }

  // Fallback: comandos npm/pnpm/yarn/pip/cargo no texto
  if (install.length === 0) {
    for (const line of lines) {
      if (
        /^\s*(npm|pnpm|yarn|bun|pip|uv|cargo|go get|brew)\b/i.test(line) ||
        /```/.test(line)
      ) {
        const cleaned = line.replace(/```\w*/g, "").trim();
        if (cleaned) install.push(cleaned);
        if (install.length >= 8) break;
      }
    }
  }

  return { install, usage };
}
