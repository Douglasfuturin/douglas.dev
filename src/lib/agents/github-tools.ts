import { tool } from "ai";
import { z } from "zod";
import {
  buildSearchQuery,
  cleanRepoFullName,
  fetchRepoBundle,
  ghGet,
  scoreRepo,
  type GhRepo,
  type RankedRepo,
} from "./github-client";

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
        const q = buildSearchQuery({
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
        try {
          const repo = await fetchRepoBundle(fullName);
          return { ok: true, repo };
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
          const clean = cleanRepoFullName(name);
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
