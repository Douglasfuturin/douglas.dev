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
import {
  exportRepoGuideBundle,
  publishRepoGuideBundle,
} from "./notion-tools";

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

function draftReelsScript(input: {
  fullName: string;
  url: string;
  description: string | null;
  language: string | null;
  stars: number;
  topics: string[];
  installCmd: string;
  style: "explicativo" | "hype" | "tutorial" | "opiniao";
}) {
  const shortName = input.fullName.split("/")[1] || input.fullName;
  const desc =
    (input.description || "um projeto open-source poderoso").replace(
      /\s+/g,
      " ",
    ).slice(0, 120);
  const lang = input.language || "várias linguagens";
  const starsLabel =
    input.stars >= 1000
      ? `${Math.round(input.stars / 1000)}k stars`
      : `${input.stars} stars`;

  const beats: Beat[] =
    input.style === "hype"
      ? [
          {
            name: "hook",
            startSec: 0,
            endSec: 3,
            onScreen: "Isso muda o jogo",
            spoken: `Para: se você mexe com ${lang}, precisa conhecer ${shortName} agora.`,
            visual: "zoom no rosto + texto punch",
          },
          {
            name: "problema",
            startSec: 3,
            endSec: 12,
            onScreen: "Todo mundo sofre com isso",
            spoken:
              "A gente perde tempo reinventando a roda, misturando libs e quebrando o fluxo.",
            visual: "tela de erro / código bagunçado",
          },
          {
            name: "solucao",
            startSec: 12,
            endSec: 28,
            onScreen: `${input.fullName}`,
            spoken: `${shortName} resolve isso. ${desc}. Já tem ${starsLabel} no GitHub e comunidade ativa.`,
            visual: "card do repo + contador de stars",
          },
          {
            name: "demo",
            startSec: 28,
            endSec: 48,
            onScreen: input.installCmd,
            spoken: `Começa simples: ${input.installCmd}. Em minutos você já está rodando o fluxo principal do projeto.`,
            visual: "terminal digitando o comando",
          },
          {
            name: "cta",
            startSec: 48,
            endSec: 60,
            onScreen: "Salva + clona",
            spoken: `Link na bio: ${input.url}. Salva esse Reels e testa hoje.`,
            visual: "CTA com URL",
          },
        ]
      : [
          {
            name: "hook",
            startSec: 0,
            endSec: 3,
            onScreen: `Conhece ${shortName}?`,
            spoken: `Em 60 segundos eu te mostro o repositório ${shortName} e como começar.`,
            visual: "apresentador + logo do projeto",
          },
          {
            name: "problema",
            startSec: 3,
            endSec: 12,
            onScreen: "O problema",
            spoken:
              "Quando a stack cresce, fica difícil achar uma base open-source confiável, documentada e ativa.",
            visual: "lista de opções confusas",
          },
          {
            name: "solucao",
            startSec: 12,
            endSec: 28,
            onScreen: input.fullName,
            spoken: `${input.fullName} é ${desc}. Feito em ${lang}, com ${starsLabel}. Por isso vale a pena olhar.`,
            visual: "README / página do GitHub",
          },
          {
            name: "demo",
            startSec: 28,
            endSec: 48,
            onScreen: "Instalar e usar",
            spoken: `Instalação rápida: ${input.installCmd}. Depois siga o README para o primeiro exemplo de uso.`,
            visual: "terminal + snippet",
          },
          {
            name: "cta",
            startSec: 48,
            endSec: 60,
            onScreen: "Link no guia",
            spoken: `Salva este Reels, clona o repo e me conta no comentário o que você vai construir. Link: ${input.url}`,
            visual: "QR/URL + pedido para salvar",
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

  const topicTags = input.topics.slice(0, 4).map((t) => t.replace(/\s+/g, ""));
  const hashtags = [
    "opensource",
    "github",
    "dev",
    shortName.replace(/[^\w]/g, ""),
    ...topicTags,
  ].filter(Boolean);

  return {
    title: `Reels 60s — ${shortName}`,
    style: input.style,
    beats,
    scriptText,
    wordCount,
    hashtags,
    caption: `${shortName}: ${desc}\n${input.url}`,
  };
}

async function pickBestRepo(input: {
  query: string;
  language?: string;
  topic?: string;
  minStars?: number;
}) {
  const q = buildSearchQuery({
    query: input.query,
    language: input.language,
    topic: input.topic,
    minStars: input.minStars ?? 50,
    includeForks: false,
  });
  const data = await ghGet<{
    total_count: number;
    items: GhRepo[];
  }>("/search/repositories", {
    q,
    sort: "stars",
    order: "desc",
    per_page: "12",
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
        score,
        why,
      };
    })
    .sort((a, b) => b.score - a.score);

  return {
    query: q,
    totalFound: data.total_count,
    candidates: ranked.slice(0, 5),
    winner: ranked[0] || null,
  };
}

export function pipelineTools() {
  return {
    run_repo_content_pack: tool({
      description:
        "Pipeline completo: escolhe o melhor repo (Scout) → gera roteiro de Reels 60s → publica guia no Notion (ou exporta .md). Use quando o usuário quiser o pacote inteiro numa tacada.",
      inputSchema: z.object({
        topic: z
          .string()
          .describe(
            "Tema para buscar o melhor repo, ex.: 'ai agents typescript'",
          ),
        fullName: z
          .string()
          .optional()
          .describe("Se já souber o repo, pule a busca (owner/repo)"),
        language: z.string().optional(),
        topicTag: z.string().optional().describe("topic: do GitHub"),
        minStars: z.number().int().nonnegative().optional(),
        style: z
          .enum(["explicativo", "hype", "tutorial", "opiniao"])
          .optional(),
        publishToNotion: z
          .boolean()
          .optional()
          .describe("Tentar publicar no Notion (default true)"),
        parentPageId: z.string().optional(),
        extraNotes: z.string().optional(),
      }),
      execute: async ({
        topic,
        fullName,
        language,
        topicTag,
        minStars = 50,
        style = "explicativo",
        publishToNotion = true,
        parentPageId,
        extraNotes,
      }) => {
        try {
          let scout: Awaited<ReturnType<typeof pickBestRepo>> | null = null;
          let chosenName = fullName?.trim() || "";

          if (!chosenName) {
            scout = await pickBestRepo({
              query: topic,
              language,
              topic: topicTag,
              minStars,
            });
            if (!scout.winner) {
              return {
                ok: false,
                step: "scout",
                error: `Nenhum repositório encontrado para: ${topic}`,
              };
            }
            chosenName = scout.winner.fullName;
          }

          const repo = await fetchRepoBundle(chosenName);
          const hints = extractInstallUsageHints(repo.readmePreview);
          const installCmd = firstInstallCommand(hints.install);
          const script = draftReelsScript({
            fullName: repo.fullName,
            url: repo.url,
            description: repo.description,
            language: repo.language,
            stars: repo.stars,
            topics: repo.topics,
            installCmd,
            style,
          });

          const notes = [
            extraNotes,
            `Pipeline Grokish — tema: ${topic}`,
            `Roteiro: ${script.title}`,
          ]
            .filter(Boolean)
            .join("\n");

          const guide = publishToNotion
            ? await publishRepoGuideBundle({
                fullName: repo.fullName,
                parentPageId,
                title: `Guia + Reels: ${repo.fullName}`,
                extraNotes: notes,
              })
            : await exportRepoGuideBundle({
                fullName: repo.fullName,
                extraNotes: notes,
              });

          const packDir = path.join(process.cwd(), "outputs", "packs");
          await mkdir(packDir, { recursive: true });
          const safe = repo.fullName.replace(/[^\w.-]+/g, "_");
          const packPath = path.join(packDir, `${safe}-pack.md`);
          const packMarkdown = `# Pack: ${repo.fullName}

## 1) Repo escolhido
- URL: ${repo.url}
- Stars: ${repo.stars}
- Score: ${repo.score}
- Por quê: ${(repo.why || []).join("; ")}

## 2) Roteiro Reels 60s
${script.scriptText}

Legenda: ${script.caption}
Hashtags: ${script.hashtags.map((h) => `#${h}`).join(" ")}

## 3) Guia (install/uso)
Arquivo: ${guide.localPath || "(não gerado)"}
Notion: ${guide.notionUrl || "(não publicado — exporte local ou configure NOTION_TOKEN)"}
${guide.error ? `\nAviso Notion: ${guide.error}\n` : ""}
`;

          await writeFile(packPath, packMarkdown, "utf8");
          await writeFile(
            path.join(packDir, `${safe}-roteiro.md`),
            `# ${script.title}\n\n${script.scriptText}\n`,
            "utf8",
          );

          return {
            ok: true,
            steps: {
              scout: scout
                ? {
                    query: scout.query,
                    totalFound: scout.totalFound,
                    candidates: scout.candidates,
                    winner: scout.winner,
                  }
                : { skipped: true, fullName: chosenName },
              roteiro: {
                ...script,
                durationTargetSec: 60,
              },
              notion: {
                ok: guide.ok,
                notionUrl: guide.notionUrl || null,
                localPath: guide.localPath || null,
                error: guide.error || null,
              },
            },
            packPath,
            summary: {
              repo: repo.fullName,
              url: repo.url,
              stars: repo.stars,
              roteiroTitle: script.title,
              notionUrl: guide.notionUrl || null,
              localGuide: guide.localPath || null,
              packPath,
            },
          };
        } catch (err) {
          return {
            ok: false,
            error: err instanceof Error ? err.message : "Falha no pipeline",
          };
        }
      },
    }),
  };
}
