import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { tool } from "ai";
import { z } from "zod";
import {
  buildSearchQuery,
  extractInstallUsageHints,
  fetchRepoBundle,
  ghGet,
  scoreRepo,
  type GhRepo,
} from "./github-client";
import { createContent } from "@/lib/content/store";

export const GITHUB_NICHES = [
  {
    id: "ai-agents",
    label: "Agentes de IA",
    query: "ai agent framework",
    topic: "ai-agents",
    language: undefined as string | undefined,
    minStars: 500,
  },
  {
    id: "llm",
    label: "LLM / RAG",
    query: "llm rag",
    topic: "llm",
    language: undefined,
    minStars: 1000,
  },
  {
    id: "nextjs",
    label: "Next.js",
    query: "next.js starter",
    topic: "nextjs",
    language: "TypeScript",
    minStars: 500,
  },
  {
    id: "react",
    label: "React UI",
    query: "react component library",
    topic: "react",
    language: "TypeScript",
    minStars: 2000,
  },
  {
    id: "devops",
    label: "DevOps / K8s",
    query: "kubernetes",
    topic: "kubernetes",
    language: "Go",
    minStars: 5000,
  },
  {
    id: "automation",
    label: "Automação",
    query: "workflow automation",
    topic: "automation",
    language: undefined,
    minStars: 1000,
  },
  {
    id: "python-data",
    label: "Python / Data",
    query: "data science",
    topic: "machine-learning",
    language: "Python",
    minStars: 5000,
  },
  {
    id: "mobile",
    label: "Mobile",
    query: "react native",
    topic: "react-native",
    language: "TypeScript",
    minStars: 1000,
  },
  {
    id: "security",
    label: "Security",
    query: "security scanning",
    topic: "security",
    language: undefined,
    minStars: 1000,
  },
  {
    id: "devtools",
    label: "DevTools",
    query: "developer tools cli",
    topic: "cli",
    language: undefined,
    minStars: 2000,
  },
] as const;

type NicheId = (typeof GITHUB_NICHES)[number]["id"];

type Beat = {
  name: "hook" | "problema" | "solucao" | "demo" | "cta";
  startSec: number;
  endSec: number;
  onScreen: string;
  spoken: string;
  visual: string;
};

function firstInstallCommand(install: string[]): string {
  for (const line of install) {
    const cleaned = line.replace(/^[`$\s]+/, "").replace(/`$/, "").trim();
    if (
      /^(npm|pnpm|yarn|bun|pip|uv|cargo|go get|brew|git clone)\b/i.test(cleaned)
    ) {
      return cleaned.slice(0, 80);
    }
  }
  return "git clone + README";
}

function draftReels60(input: {
  fullName: string;
  url: string;
  description: string | null;
  language: string | null;
  stars: number;
  nicheLabel: string;
  installCmd: string;
  style: "explicativo" | "hype" | "tutorial" | "opiniao";
}) {
  const shortName = input.fullName.split("/")[1] || input.fullName;
  const desc = (input.description || "um projeto open-source poderoso")
    .replace(/\s+/g, " ")
    .slice(0, 110);
  const lang = input.language || "várias linguagens";
  const starsLabel =
    input.stars >= 1000
      ? `${(input.stars / 1000).toFixed(input.stars >= 10000 ? 0 : 1)}k stars`
      : `${input.stars} stars`;

  const beats: Beat[] =
    input.style === "hype"
      ? [
          {
            name: "hook",
            startSec: 0,
            endSec: 3,
            onScreen: "Repo top do nicho",
            spoken: `Para: o melhor do nicho ${input.nicheLabel} agora é ${shortName}.`,
            visual: "texto punch + contador de stars",
          },
          {
            name: "problema",
            startSec: 3,
            endSec: 12,
            onScreen: "Muita opção, pouco sinal",
            spoken:
              "O GitHub tem milhares de repos. A gente perde tempo testando o que não vale.",
            visual: "scroll infinito no GitHub",
          },
          {
            name: "solucao",
            startSec: 12,
            endSec: 28,
            onScreen: input.fullName,
            spoken: `${shortName} resolve isso: ${desc}. Já tem ${starsLabel} e stack em ${lang}.`,
            visual: "card do repo",
          },
          {
            name: "demo",
            startSec: 28,
            endSec: 48,
            onScreen: input.installCmd,
            spoken: `Começa assim: ${input.installCmd}. Em minutos você vê o fluxo principal.`,
            visual: "terminal digitando",
          },
          {
            name: "cta",
            startSec: 48,
            endSec: 60,
            onScreen: "Salva e clona",
            spoken: `Link: ${input.url}. Salva esse Reels e testa hoje.`,
            visual: "URL + CTA",
          },
        ]
      : [
          {
            name: "hook",
            startSec: 0,
            endSec: 3,
            onScreen: `Nicho: ${input.nicheLabel}`,
            spoken: `Em 60 segundos: o que o ${shortName} faz e por que ele é top no GitHub.`,
            visual: "apresentador + badge do nicho",
          },
          {
            name: "problema",
            startSec: 3,
            endSec: 12,
            onScreen: "A dor",
            spoken: `No nicho ${input.nicheLabel}, é fácil se perder entre libs sem manutenção e hype sem uso real.`,
            visual: "opções confusas na tela",
          },
          {
            name: "solucao",
            startSec: 12,
            endSec: 28,
            onScreen: input.fullName,
            spoken: `${input.fullName} faz isto: ${desc}. Linguagem ${lang}, com ${starsLabel} — sinal de adoção real.`,
            visual: "README / GitHub",
          },
          {
            name: "demo",
            startSec: 28,
            endSec: 48,
            onScreen: "Como começar",
            spoken: `Para rodar: ${input.installCmd}. Depois abra o README e siga o primeiro exemplo.`,
            visual: "terminal + snippet",
          },
          {
            name: "cta",
            startSec: 48,
            endSec: 60,
            onScreen: "Clona agora",
            spoken: `Salva o vídeo, clona ${shortName} e me diz nos comentários o que você vai construir. ${input.url}`,
            visual: "CTA salvar + URL",
          },
        ];

  const scriptText = beats
    .map(
      (b) =>
        `[${b.startSec}–${b.endSec}s | ${b.name.toUpperCase()}]\n` +
        `TELA: ${b.onScreen}\n` +
        `FALA: ${b.spoken}\n` +
        `VISUAL: ${b.visual}`,
    )
    .join("\n\n");

  const wordCount = beats
    .map((b) => b.spoken.trim().split(/\s+/).filter(Boolean).length)
    .reduce((a, b) => a + b, 0);

  return {
    title: `Reels 60s — ${shortName} (${input.nicheLabel})`,
    style: input.style,
    beats,
    scriptText,
    wordCount,
    hashtags: [
      "github",
      "opensource",
      "dev",
      shortName.replace(/[^\w]/g, ""),
      input.nicheLabel.replace(/\s+/g, ""),
    ],
    caption: `${shortName} (${input.nicheLabel}): ${desc}\n⭐ ${starsLabel}\n${input.url}`,
  };
}

async function searchTopForNiche(input: {
  query: string;
  language?: string;
  topic?: string;
  minStars: number;
  perPage?: number;
}) {
  const q = buildSearchQuery({
    query: input.query,
    language: input.language,
    topic: input.topic,
    minStars: input.minStars,
    includeForks: false,
  });
  const data = await ghGet<{
    total_count: number;
    items: GhRepo[];
  }>("/search/repositories", {
    q,
    sort: "stars",
    order: "desc",
    per_page: String(input.perPage ?? 8),
  });

  const ranked = data.items
    .map((repo) => {
      const { score, why } = scoreRepo(repo);
      return {
        fullName: repo.full_name,
        url: repo.html_url,
        description: repo.description,
        language: repo.language,
        stars: repo.stargazers_count,
        forks: repo.forks_count,
        score,
        why,
        topics: repo.topics || [],
      };
    })
    .sort((a, b) => b.stars - a.stars || b.score - a.score);

  return {
    query: q,
    totalFound: data.total_count,
    top: ranked.slice(0, 5),
    winner: ranked[0] || null,
  };
}

function resolveNiches(nicheIds?: string[]) {
  if (!nicheIds?.length) return [...GITHUB_NICHES];
  const set = new Set(nicheIds);
  const picked = GITHUB_NICHES.filter((n) => set.has(n.id));
  return picked.length ? picked : [...GITHUB_NICHES];
}

export function nicheScoutTools() {
  return {
    list_github_niches: tool({
      description:
        "Lista os nichos pré-definidos para caçar os melhores repositórios do GitHub (IA, Next.js, DevOps, etc.).",
      inputSchema: z.object({}),
      execute: async () => ({
        ok: true,
        niches: GITHUB_NICHES.map((n) => ({
          id: n.id,
          label: n.label,
          query: n.query,
          topic: n.topic,
          language: n.language || null,
          minStars: n.minStars,
        })),
      }),
    }),

    scout_best_repos_by_niches: tool({
      description:
        "Busca os melhores repositórios do GitHub em vários nichos, ordenados por mais stars/avaliações. Use quando o usuário pedir 'melhores repos', 'nichos', 'top GitHub'.",
      inputSchema: z.object({
        nicheIds: z
          .array(z.string())
          .optional()
          .describe("IDs de nicho; omitir = todos os nichos padrão"),
        minStarsOverride: z.number().int().nonnegative().optional(),
        perNiche: z
          .number()
          .int()
          .min(1)
          .max(5)
          .optional()
          .describe("Quantos top repos listar por nicho (default 3)"),
      }),
      execute: async ({ nicheIds, minStarsOverride, perNiche = 3 }) => {
        const niches = resolveNiches(nicheIds);
        const results = [];
        for (const niche of niches) {
          try {
            const scout = await searchTopForNiche({
              query: niche.query,
              language: niche.language,
              topic: niche.topic,
              minStars: minStarsOverride ?? niche.minStars,
              perPage: Math.max(perNiche * 2, 6),
            });
            results.push({
              nicheId: niche.id,
              nicheLabel: niche.label,
              ok: true,
              query: scout.query,
              totalFound: scout.totalFound,
              repos: scout.top.slice(0, perNiche),
              winner: scout.winner,
            });
          } catch (err) {
            results.push({
              nicheId: niche.id,
              nicheLabel: niche.label,
              ok: false,
              error: err instanceof Error ? err.message : "Falha na busca",
            });
          }
          // small delay to respect unauthenticated rate limits
          await new Promise((r) => setTimeout(r, 250));
        }

        const winners = results
          .filter((r) => r.ok && "winner" in r && r.winner)
          .map((r) => ({
            nicheId: (r as { nicheId: string }).nicheId,
            nicheLabel: (r as { nicheLabel: string }).nicheLabel,
            repo: (r as { winner: NonNullable<Awaited<ReturnType<typeof searchTopForNiche>>["winner"]> }).winner,
          }))
          .sort((a, b) => (b.repo?.stars || 0) - (a.repo?.stars || 0));

        return {
          ok: true,
          nichesScanned: niches.length,
          winners,
          byNiche: results,
          hint: "Próximo passo: scout_repo_reels_60s com fullName do vencedor, ou scout_niches_with_reels_scripts para gerar roteiros de todos.",
        };
      },
    }),

    scout_repo_reels_60s: tool({
      description:
        "Gera roteiro de vídeo Reels de até 60 segundos explicando o que um repositório GitHub faz (hook → CTA).",
      inputSchema: z.object({
        fullName: z.string().describe("owner/repo ou URL"),
        nicheLabel: z.string().optional(),
        style: z.enum(["explicativo", "hype", "tutorial", "opiniao"]).optional(),
        saveToCentral: z.boolean().optional(),
      }),
      execute: async ({
        fullName,
        nicheLabel = "Open Source",
        style = "explicativo",
        saveToCentral = true,
      }) => {
        try {
          const repo = await fetchRepoBundle(fullName);
          const hints = extractInstallUsageHints(repo.readmePreview);
          const installCmd = firstInstallCommand(hints.install);
          const script = draftReels60({
            fullName: repo.fullName,
            url: repo.url,
            description: repo.description,
            language: repo.language,
            stars: repo.stars,
            nicheLabel,
            installCmd,
            style,
          });

          const outDir = path.join(process.cwd(), "outputs", "reels");
          await mkdir(outDir, { recursive: true });
          const safe = repo.fullName.replace(/[^\w.-]+/g, "_");
          const filePath = path.join(outDir, `${safe}-60s.md`);
          await writeFile(
            filePath,
            `# ${script.title}\n\n⭐ ${repo.stars} · ${repo.url}\n\n${script.scriptText}\n\n---\nLegenda: ${script.caption}\nHashtags: ${script.hashtags.map((h) => `#${h}`).join(" ")}\n`,
            "utf8",
          );

          let contentId: string | null = null;
          if (saveToCentral) {
            const item = await createContent({
              title: script.title,
              summary: repo.description || undefined,
              stage: "script",
              source: "github",
              score: Math.min(10, Math.round(Math.log10(repo.stars + 1) * 3)),
              tags: ["github", "reels", nicheLabel.toLowerCase()],
              topic: nicheLabel,
              script: script.scriptText,
              caption: script.caption,
              networks: ["instagram", "youtube", "tiktok"],
              notes: `Repo: ${repo.url} · ${repo.stars} stars`,
            });
            contentId = item.id;
          }

          return {
            ok: true,
            repo: {
              fullName: repo.fullName,
              url: repo.url,
              stars: repo.stars,
              description: repo.description,
              language: repo.language,
              score: repo.score,
              why: repo.why,
            },
            roteiro: {
              ...script,
              durationTargetSec: 60,
              filePath,
            },
            contentId,
          };
        } catch (err) {
          return {
            ok: false,
            error: err instanceof Error ? err.message : "Falha no roteiro",
          };
        }
      },
    }),

    scout_niches_with_reels_scripts: tool({
      description:
        "Caça os melhores repos (mais stars) em vários nichos e gera roteiro de vídeo de até 60s explicando o que cada vencedor faz. Use para pedido completo: 'melhores repos + roteiro'.",
      inputSchema: z.object({
        nicheIds: z
          .array(z.string())
          .optional()
          .describe("IDs; default = seleção enxuta de 5 nichos quentes"),
        style: z.enum(["explicativo", "hype", "tutorial", "opiniao"]).optional(),
        maxNiches: z.number().int().min(1).max(8).optional(),
        saveToCentral: z.boolean().optional(),
      }),
      execute: async ({
        nicheIds,
        style = "explicativo",
        maxNiches = 5,
        saveToCentral = true,
      }) => {
        const defaultHot: NicheId[] = [
          "ai-agents",
          "llm",
          "nextjs",
          "automation",
          "devtools",
        ];
        const niches = resolveNiches(
          nicheIds?.length ? nicheIds : defaultHot,
        ).slice(0, maxNiches);

        const packs = [];
        for (const niche of niches) {
          try {
            const scout = await searchTopForNiche({
              query: niche.query,
              language: niche.language,
              topic: niche.topic,
              minStars: niche.minStars,
            });
            if (!scout.winner) {
              packs.push({
                nicheId: niche.id,
                nicheLabel: niche.label,
                ok: false,
                error: "Nenhum repo encontrado",
              });
              continue;
            }

            const repo = await fetchRepoBundle(scout.winner.fullName);
            const hints = extractInstallUsageHints(repo.readmePreview);
            const installCmd = firstInstallCommand(hints.install);
            const script = draftReels60({
              fullName: repo.fullName,
              url: repo.url,
              description: repo.description,
              language: repo.language,
              stars: repo.stars,
              nicheLabel: niche.label,
              installCmd,
              style,
            });

            let contentId: string | null = null;
            if (saveToCentral) {
              const item = await createContent({
                title: script.title,
                summary: `${niche.label}: ${repo.description || repo.fullName}`,
                stage: "script",
                source: "github",
                score: Math.min(10, Math.round(Math.log10(repo.stars + 1) * 3)),
                tags: ["github", "reels", niche.id],
                topic: niche.label,
                script: script.scriptText,
                caption: script.caption,
                networks: ["instagram", "youtube", "tiktok"],
                notes: `Nicho ${niche.label} · ${repo.stars} stars · ${repo.url}`,
              });
              contentId = item.id;
            }

            packs.push({
              nicheId: niche.id,
              nicheLabel: niche.label,
              ok: true,
              candidates: scout.top.slice(0, 3),
              winner: {
                fullName: repo.fullName,
                url: repo.url,
                stars: repo.stars,
                description: repo.description,
                language: repo.language,
                score: repo.score,
                why: repo.why,
              },
              roteiro: {
                title: script.title,
                scriptText: script.scriptText,
                caption: script.caption,
                hashtags: script.hashtags,
                wordCount: script.wordCount,
                durationTargetSec: 60,
                beats: script.beats,
              },
              contentId,
            });
          } catch (err) {
            packs.push({
              nicheId: niche.id,
              nicheLabel: niche.label,
              ok: false,
              error: err instanceof Error ? err.message : "Falha",
            });
          }
          await new Promise((r) => setTimeout(r, 300));
        }

        const outDir = path.join(process.cwd(), "outputs", "reels");
        await mkdir(outDir, { recursive: true });
        const stamp = new Date().toISOString().slice(0, 10);
        const digestPath = path.join(outDir, `nichos-${stamp}.md`);
        const md = packs
          .map((p) => {
            if (!p.ok || !("roteiro" in p) || !p.roteiro) {
              return `## ${p.nicheLabel}\nFalha: ${"error" in p ? p.error : "?"}\n`;
            }
            const w = p.winner!;
            return `## ${p.nicheLabel} — ${w.fullName} (⭐ ${w.stars})\n${w.url}\n\n${p.roteiro.scriptText}\n\nLegenda: ${p.roteiro.caption}\n`;
          })
          .join("\n---\n\n");
        await writeFile(digestPath, `# Melhores repos + Reels 60s — ${stamp}\n\n${md}`, "utf8");

        return {
          ok: true,
          count: packs.filter((p) => p.ok).length,
          digestPath,
          packs,
          summary: packs
            .filter((p) => p.ok && p.winner)
            .map((p) => ({
              niche: p.nicheLabel,
              repo: p.winner!.fullName,
              stars: p.winner!.stars,
              url: p.winner!.url,
              contentId: p.contentId,
            })),
        };
      },
    }),
  };
}
