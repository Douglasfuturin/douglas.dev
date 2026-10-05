import { tool } from "ai";
import { z } from "zod";

const GH_API = "https://api.github.com";
const UA = "Grokish-GitHub-Scout";

type GhRepo = {
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
};

type RankedRepo = {
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

function authHeaders(): HeadersInit {
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

async function ghGet<T>(path: string, query?: Record<string, string>): Promise<T> {
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

function daysSince(iso: string): number {
  const t = Date.parse(iso);
  if (Number.isNaN(t)) return 9999;
  return Math.max(0, (Date.now() - t) / (1000 * 60 * 60 * 24));
}

/** Score simples: popularidade + atividade recente + saúde básica. */
function scoreRepo(repo: GhRepo): { score: number; why: string[] } {
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

function buildQuery(input: {
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

export function githubScoutTools() {
  return {
    search_best_github_repos: tool({
      description:
        "Busca e ranqueia os melhores repositórios do GitHub para um tema (stars, forks, atividade, licença). Use sempre que o usuário pedir repos, bibliotecas, exemplos open-source ou 'melhores projetos no GitHub'.",
      inputSchema: z.object({
        query: z
          .string()
          .describe("Tema ou palavras-chave, ex.: 'ai agents typescript'"),
        language: z
          .string()
          .optional()
          .describe("Linguagem principal, ex.: TypeScript, Python, Go"),
        topic: z
          .string()
          .optional()
          .describe("Tópico GitHub, ex.: nextjs, llm, rust"),
        minStars: z
          .number()
          .int()
          .nonnegative()
          .optional()
          .describe("Mínimo de stars (default 50)"),
        sort: z
          .enum(["stars", "forks", "updated", "best-match"])
          .optional()
          .describe("Ordenação da API GitHub (default stars)"),
        limit: z
          .number()
          .int()
          .min(3)
          .max(30)
          .optional()
          .describe("Quantos repos retornar (default 10)"),
        includeForks: z.boolean().optional(),
      }),
      execute: async ({
        query,
        language,
        topic,
        minStars = 50,
        sort = "stars",
        limit = 10,
        includeForks = false,
      }) => {
        const q = buildQuery({
          query,
          language,
          topic,
          minStars,
          includeForks,
        });
        const apiSort = sort === "best-match" ? "" : sort;
        try {
          const data = await ghGet<{
            total_count: number;
            incomplete_results: boolean;
            items: GhRepo[];
          }>("/search/repositories", {
            q,
            ...(apiSort ? { sort: apiSort, order: "desc" } : {}),
            per_page: String(Math.min(Math.max(limit * 2, 10), 50)),
          });

          const ranked: RankedRepo[] = data.items
            .map((repo) => {
              const { score, why } = scoreRepo(repo);
              return {
                rank: 0,
                score,
                fullName: repo.full_name,
                url: repo.html_url,
                description: repo.description || "(sem descrição)",
                language: repo.language,
                stars: repo.stargazers_count,
                forks: repo.forks_count,
                openIssues: repo.open_issues_count,
                topics: repo.topics || [],
                license: repo.license?.spdx_id || null,
                archived: repo.archived,
                pushedAt: repo.pushed_at,
                why,
              };
            })
            .sort((a, b) => b.score - a.score)
            .slice(0, limit)
            .map((repo, i) => ({ ...repo, rank: i + 1 }));

          return {
            ok: true,
            query: q,
            totalFound: data.total_count,
            incomplete: data.incomplete_results,
            rateLimitHint:
              "Sem GITHUB_TOKEN o limite é ~10 req/min. Com token, bem maior.",
            repos: ranked,
          };
        } catch (err) {
          return {
            ok: false,
            query: q,
            error: err instanceof Error ? err.message : "Falha na busca GitHub",
          };
        }
      },
    }),

    get_github_repo: tool({
      description:
        "Detalha um repositório GitHub (owner/repo): descrição, stars, tópicos, licença, README resumido se disponível.",
      inputSchema: z.object({
        fullName: z
          .string()
          .describe("Nome completo owner/repo, ex.: vercel/ai"),
      }),
      execute: async ({ fullName }) => {
        const clean = fullName.replace(/^https?:\/\/github\.com\//, "").replace(/\/$/, "");
        try {
          const repo = await ghGet<GhRepo>(`/repos/${clean}`);
          const { score, why } = scoreRepo(repo);
          let readmePreview: string | null = null;
          try {
            const readme = await ghGet<{ content?: string; encoding?: string }>(
              `/repos/${clean}/readme`,
            );
            if (readme.content && readme.encoding === "base64") {
              readmePreview = Buffer.from(readme.content, "base64")
                .toString("utf8")
                .slice(0, 2500);
            }
          } catch {
            readmePreview = null;
          }
          return {
            ok: true,
            repo: {
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
              score,
              why,
              readmePreview,
            },
          };
        } catch (err) {
          return {
            ok: false,
            error: err instanceof Error ? err.message : "Repo não encontrado",
          };
        }
      },
    }),

    compare_github_repos: tool({
      description:
        "Compara 2–5 repositórios GitHub lado a lado (stars, forks, atividade, score) e sugere o melhor para um caso de uso.",
      inputSchema: z.object({
        repos: z
          .array(z.string())
          .min(2)
          .max(5)
          .describe("Lista owner/repo"),
        useCase: z
          .string()
          .optional()
          .describe("Caso de uso do usuário para justificar a recomendação"),
      }),
      execute: async ({ repos, useCase }) => {
        const details = [];
        for (const name of repos) {
          const clean = name
            .replace(/^https?:\/\/github\.com\//, "")
            .replace(/\/$/, "");
          try {
            const repo = await ghGet<GhRepo>(`/repos/${clean}`);
            const { score, why } = scoreRepo(repo);
            details.push({
              fullName: repo.full_name,
              url: repo.html_url,
              description: repo.description,
              language: repo.language,
              stars: repo.stargazers_count,
              forks: repo.forks_count,
              pushedAt: repo.pushed_at,
              score,
              why,
            });
          } catch (err) {
            details.push({
              fullName: clean,
              error: err instanceof Error ? err.message : "falha",
              score: -1,
            });
          }
        }
        const ranked = [...details].sort(
          (a, b) => (b.score ?? -1) - (a.score ?? -1),
        );
        return {
          ok: true,
          useCase: useCase || null,
          winner: ranked[0]?.fullName || null,
          comparison: ranked,
        };
      },
    }),
  };
}
