import { tool } from "ai";
import { z } from "zod";
import { fetchRepoBundle } from "./github-client";

const beatSchema = z.object({
  name: z
    .enum(["hook", "problema", "solucao", "demo", "cta"])
    .describe("Bloco do roteiro"),
  startSec: z.number().min(0).max(60),
  endSec: z.number().min(1).max(60),
  onScreen: z.string().describe("Texto na tela (curto)"),
  spoken: z.string().describe("Falado pelo apresentador"),
  visual: z.string().describe("Indicação visual / B-roll"),
});

export function reelsScriptTools() {
  return {
    prepare_repo_for_reels: tool({
      description:
        "Carrega fatos do repositório GitHub para escrever um roteiro de Reels de 60s (descrição, stars, tópicos, README).",
      inputSchema: z.object({
        fullName: z
          .string()
          .describe("owner/repo ou URL do GitHub"),
      }),
      execute: async ({ fullName }) => {
        try {
          const repo = await fetchRepoBundle(fullName);
          return {
            ok: true,
            kind: "repo" as const,
            repo: {
              fullName: repo.fullName,
              url: repo.url,
              description: repo.description,
              language: repo.language,
              stars: repo.stars,
              topics: repo.topics,
              homepage: repo.homepage,
              why: repo.why,
              readmePreview: repo.readmePreview,
            },
            timingGuide: {
              totalSec: 60,
              beats: [
                { name: "hook", range: "0–3s", goal: "Prender atenção" },
                {
                  name: "problema",
                  range: "3–12s",
                  goal: "Dor que o repo resolve",
                },
                {
                  name: "solucao",
                  range: "12–28s",
                  goal: "Apresentar o repo + 1 benefício",
                },
                {
                  name: "demo",
                  range: "28–48s",
                  goal: "Como instalar/usar em 2–3 passos",
                },
                {
                  name: "cta",
                  range: "48–60s",
                  goal: "Link + pedido (salvar/seguir/clonar)",
                },
              ],
            },
          };
        } catch (err) {
          return {
            ok: false,
            error: err instanceof Error ? err.message : "Falha ao carregar repo",
          };
        }
      },
    }),

    prepare_trend_for_reels: tool({
      description:
        "Prepara uma tendência/notícia aprovada do Radar para roteiro de Reels 60s (manchete, ângulo, fontes).",
      inputSchema: z.object({
        headline: z.string(),
        summary: z.string(),
        angle: z.string(),
        category: z
          .enum(["automacao", "ia", "marketing", "cruzado"])
          .optional(),
        whyNow: z.string().optional(),
        sources: z
          .array(
            z.object({
              title: z.string(),
              url: z.string().optional(),
            }),
          )
          .optional(),
      }),
      execute: async ({
        headline,
        summary,
        angle,
        category = "cruzado",
        whyNow,
        sources = [],
      }) => {
        return {
          ok: true,
          kind: "trend" as const,
          trend: {
            headline,
            summary,
            angle,
            category,
            whyNow: whyNow || null,
            sources,
          },
          timingGuide: {
            totalSec: 60,
            beats: [
              { name: "hook", range: "0–3s", goal: "Gancho da notícia" },
              {
                name: "problema",
                range: "3–12s",
                goal: "Contexto / dor do mercado",
              },
              {
                name: "solucao",
                range: "12–28s",
                goal: "O que mudou + insight",
              },
              {
                name: "demo",
                range: "28–48s",
                goal: "Como aplicar / o que fazer com isso",
              },
              {
                name: "cta",
                range: "48–60s",
                goal: "Salvar + opinião / próximo passo",
              },
            ],
          },
        };
      },
    }),

    deliver_reels_script: tool({
      description:
        "Entrega o roteiro final de Reels (~60s) em formato estruturado. Use depois de prepare_repo_for_reels ou prepare_trend_for_reels. A soma dos blocos deve cobrir ~60 segundos.",
      inputSchema: z.object({
        fullName: z
          .string()
          .optional()
          .describe("owner/repo quando for sobre GitHub"),
        topic: z
          .string()
          .optional()
          .describe("Tema/manchete quando for tendência do Radar"),
        title: z.string().describe("Título interno do roteiro"),
        style: z
          .enum(["explicativo", "hype", "tutorial", "opiniao"])
          .optional()
          .describe("Tom do roteiro (default explicativo)"),
        beats: z.array(beatSchema).min(4).max(6),
        hashtags: z.array(z.string()).max(12).optional(),
        caption: z
          .string()
          .optional()
          .describe("Legenda do post (Instagram/TikTok)"),
      }),
      execute: async ({
        fullName,
        topic,
        title,
        style = "explicativo",
        beats,
        hashtags,
        caption,
      }) => {
        const sorted = [...beats].sort((a, b) => a.startSec - b.startSec);
        const totalSec = Math.max(...sorted.map((b) => b.endSec), 0);
        const gaps: string[] = [];
        for (let i = 1; i < sorted.length; i++) {
          if (sorted[i].startSec > sorted[i - 1].endSec + 0.5) {
            gaps.push(
              `buraco entre ${sorted[i - 1].name} e ${sorted[i].name}`,
            );
          }
        }
        const overlaps: string[] = [];
        for (let i = 1; i < sorted.length; i++) {
          if (sorted[i].startSec < sorted[i - 1].endSec - 0.25) {
            overlaps.push(
              `sobreposição ${sorted[i - 1].name}/${sorted[i].name}`,
            );
          }
        }
        const wordCount = sorted
          .map((b) => b.spoken.trim().split(/\s+/).filter(Boolean).length)
          .reduce((a, b) => a + b, 0);
        const paceOk = wordCount >= 90 && wordCount <= 180;

        const scriptText = sorted
          .map(
            (b) =>
              `[${b.startSec.toFixed(0)}–${b.endSec.toFixed(0)}s | ${b.name.toUpperCase()}]\n` +
              `TELA: ${b.onScreen}\n` +
              `FALA: ${b.spoken}\n` +
              `VISUAL: ${b.visual}`,
          )
          .join("\n\n");

        return {
          ok: true,
          fullName: fullName || null,
          topic: topic || null,
          title,
          style,
          durationTargetSec: 60,
          durationCoveredSec: totalSec,
          wordCount,
          paceHint: paceOk
            ? "ritmo ok para ~60s"
            : wordCount < 90
              ? "poucas palavras — pode soar curto; enriqueça a fala"
              : "muitas palavras — risco de corrida; enxugue",
          warnings: [...gaps, ...overlaps],
          hashtags: hashtags || [],
          caption: caption || null,
          beats: sorted,
          scriptText,
        };
      },
    }),
  };
}
