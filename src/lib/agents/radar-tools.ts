import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { tool } from "ai";
import { z } from "zod";

const radarItemSchema = z.object({
  id: z
    .string()
    .describe("ID curto estável, ex.: ai-openai-agents-2026-03-20"),
  category: z.enum(["automacao", "ia", "marketing", "cruzado"]),
  headline: z.string().describe("Manchete curta em português"),
  summary: z
    .string()
    .describe("Resumo de 2–4 frases com o fato principal e o porquê importa"),
  whyNow: z.string().describe("Por que é tendência HOJE / esta semana"),
  angle: z
    .string()
    .describe("Ângulo sugerido para Reels (gancho + dor + insight)"),
  sources: z
    .array(
      z.object({
        title: z.string(),
        url: z.string().optional(),
      }),
    )
    .min(1)
    .max(5),
  score: z
    .number()
    .min(1)
    .max(10)
    .describe("Prioridade editorial 1–10 (10 = cobrir já)"),
  contentFit: z
    .enum(["reels", "carousel", "thread", "any"])
    .optional()
    .describe("Formato ideal (default reels)"),
});

function todayStamp(dateIso?: string): string {
  if (dateIso) return dateIso.slice(0, 10);
  return new Date().toISOString().slice(0, 10);
}

function buildBriefingMarkdown(input: {
  date: string;
  focus: string[];
  executiveSummary: string;
  items: z.infer<typeof radarItemSchema>[];
  watchlist: string[];
}): string {
  const ranked = [...input.items].sort((a, b) => b.score - a.score);
  const lines = [
    `# Radar de Tendências — ${input.date}`,
    "",
    `Foco: ${input.focus.join(" · ")}`,
    "",
    "## Resumo executivo",
    input.executiveSummary,
    "",
    "## Top histórias (aprovar → roteirista)",
    "",
  ];

  for (const [i, item] of ranked.entries()) {
    lines.push(
      `### ${i + 1}. [${item.score}/10] ${item.headline}`,
      `- ID: \`${item.id}\``,
      `- Categoria: ${item.category}`,
      `- Fit: ${item.contentFit || "reels"}`,
      `- Por que agora: ${item.whyNow}`,
      `- Ângulo Reels: ${item.angle}`,
      `- Resumo: ${item.summary}`,
      `- Fontes:`,
      ...item.sources.map(
        (s) => `  - ${s.title}${s.url ? ` — ${s.url}` : ""}`,
      ),
      "",
    );
  }

  if (input.watchlist.length) {
    lines.push("## Watchlist", ...input.watchlist.map((w) => `- ${w}`), "");
  }

  lines.push(
    "---",
    "Gerado pelo Grokish Radar. Aprove um item para o Roteirista criar o Reels.",
  );
  return lines.join("\n");
}

export function radarTools() {
  return {
    deliver_daily_radar_briefing: tool({
      description:
        "Entrega o briefing diário estruturado do Radar (automação, IA, marketing) depois de pesquisar com web_search/x_search. Salva o arquivo do dia e devolve itens aprováveis para o roteirista.",
      inputSchema: z.object({
        date: z
          .string()
          .optional()
          .describe("Data do briefing YYYY-MM-DD (default hoje UTC)"),
        focus: z
          .array(z.enum(["automacao", "ia", "marketing"]))
          .min(1)
          .max(3)
          .optional()
          .describe("Eixos do briefing (default os três)"),
        executiveSummary: z
          .string()
          .describe("Parágrafo curto do dia (o que mudou / o que observar)"),
        items: z
          .array(radarItemSchema)
          .min(4)
          .max(12)
          .describe("Histórias ranqueadas para aprovação"),
        watchlist: z
          .array(z.string())
          .max(8)
          .optional()
          .describe("Sinais fracos / temas para acompanhar"),
      }),
      execute: async ({
        date,
        focus = ["automacao", "ia", "marketing"],
        executiveSummary,
        items,
        watchlist = [],
      }) => {
        const day = todayStamp(date);
        const ranked = [...items].sort((a, b) => b.score - a.score);
        const markdown = buildBriefingMarkdown({
          date: day,
          focus,
          executiveSummary,
          items: ranked,
          watchlist,
        });

        const outDir = path.join(process.cwd(), "outputs", "radar");
        await mkdir(outDir, { recursive: true });
        const localPath = path.join(outDir, `${day}.md`);
        const jsonPath = path.join(outDir, `${day}.json`);
        await writeFile(localPath, markdown, "utf8");
        await writeFile(
          jsonPath,
          JSON.stringify(
            {
              date: day,
              focus,
              executiveSummary,
              items: ranked,
              watchlist,
              generatedAt: new Date().toISOString(),
            },
            null,
            2,
          ),
          "utf8",
        );

        return {
          ok: true,
          date: day,
          focus,
          executiveSummary,
          localPath,
          jsonPath,
          itemCount: ranked.length,
          topIds: ranked.slice(0, 3).map((i) => i.id),
          items: ranked.map((item) => ({
            ...item,
            contentFit: item.contentFit || "reels",
            approvePrompt: [
              `Crie um roteiro de Reels de ~60 segundos sobre esta tendência APROVADA do Radar:`,
              ``,
              `ID: ${item.id}`,
              `Categoria: ${item.category}`,
              `Manchete: ${item.headline}`,
              `Por que agora: ${item.whyNow}`,
              `Ângulo: ${item.angle}`,
              `Resumo: ${item.summary}`,
              `Fontes: ${item.sources.map((s) => (s.url ? `${s.title} (${s.url})` : s.title)).join(" | ")}`,
              ``,
              `Use prepare_trend_for_reels e depois deliver_reels_script. Português do Brasil.`,
            ].join("\n"),
          })),
          watchlist,
          nextStep:
            "Mostre o ranking e peça ao usuário para APROVAR um item (botão na UI ou respondendo com o ID).",
        };
      },
    }),
  };
}

export type RadarBriefingItem = z.infer<typeof radarItemSchema> & {
  contentFit?: string;
  approvePrompt?: string;
};
