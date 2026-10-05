import { tool } from "ai";
import { z } from "zod";

export function artDirectorTools(style: "twitter" | "realista") {
  return {
    deliver_art_direction: tool({
      description:
        style === "twitter"
          ? "Entrega briefing visual + prompts de imagem no estilo Twitter/X (capa, carrossel, meme tech)."
          : "Entrega briefing visual + prompts de imagem fotorealista/cinematográfica para Reels ou capa.",
      inputSchema: z.object({
        topic: z.string().describe("Tema / manchete / produto"),
        format: z
          .enum(["capa", "carrossel", "meme", "cena-reels", "thumbnail"])
          .describe("Formato da peça"),
        mood: z.string().optional(),
        textOnImage: z
          .string()
          .optional()
          .describe("Texto curto a aparecer na arte"),
        slides: z
          .number()
          .int()
          .min(1)
          .max(6)
          .optional()
          .describe("Nº de slides se carrossel"),
      }),
      execute: async ({ topic, format, mood, textOnImage, slides = 3 }) => {
        const twitterNotes = {
          aspect: format === "carrossel" || format === "capa" ? "1:1 ou 4:5" : "1:1",
          look: "alto contraste, tipografia bold, fundo escuro ou grid tech, poucas cores",
          platform: "X/Twitter",
        };
        const realistaNotes = {
          aspect: format === "cena-reels" ? "9:16" : "16:9 ou 1:1",
          look: "fotorealista, luz cinematográfica, profundidade de campo, sem cartoon",
          platform: "Reels / capa YouTube / LinkedIn",
        };
        const notes = style === "twitter" ? twitterNotes : realistaNotes;

        const basePrompt =
          style === "twitter"
            ? `Tech editorial graphic for X/Twitter about "${topic}". ${notes.look}. Format: ${format}. ${
                textOnImage ? `Bold on-image text: "${textOnImage}".` : ""
              } Mood: ${mood || "sharp, modern, founder-tech"}. No watermarks.`
            : `Photorealistic cinematic still about "${topic}". ${notes.look}. Format: ${format}. ${
                textOnImage ? `Subtle title treatment: "${textOnImage}".` : "No heavy typography."
              } Mood: ${mood || "premium, documentary, natural light"}. No watermarks, no illustration.`;

        const carousel =
          format === "carrossel"
            ? Array.from({ length: slides }, (_, i) => ({
                slide: i + 1,
                prompt: `${basePrompt} Carousel slide ${i + 1}/${slides}. Clear visual hierarchy.`,
              }))
            : null;

        return {
          ok: true,
          style,
          topic,
          format,
          platformNotes: notes,
          masterPrompt: basePrompt,
          carousel,
          checklist: [
            "Gerar com image_generation usando masterPrompt (ou cada slide)",
            "Revisar legibilidade do texto na arte",
            "Exportar no aspect ratio indicado",
            "Alinhar com o roteiro aprovado",
          ],
          nextStep:
            "Chame image_generation com o masterPrompt (e slides, se houver).",
        };
      },
    }),
  };
}

export function bitCoordinatorTools() {
  return {
    deliver_group_handoff: tool({
      description:
        "Bit fecha um handoff entre membros do grupo: o que foi feito, o que falta e para quem passar a bola.",
      inputSchema: z.object({
        groupName: z.string(),
        fromMember: z.string(),
        toMember: z.string(),
        done: z.array(z.string()).min(1),
        pending: z.array(z.string()).min(1),
        artifactPaths: z.array(z.string()).optional(),
        userDecisionNeeded: z.string().optional(),
      }),
      execute: async (input) => ({
        ok: true,
        ...input,
        message: [
          `Handoff · ${input.groupName}`,
          `${input.fromMember} → ${input.toMember}`,
          "",
          "Feito:",
          ...input.done.map((d) => `✓ ${d}`),
          "",
          "Pendente:",
          ...input.pending.map((p) => `→ ${p}`),
          input.artifactPaths?.length
            ? `\nArtefatos:\n${input.artifactPaths.map((a) => `- ${a}`).join("\n")}`
            : "",
          input.userDecisionNeeded
            ? `\nDecisão do usuário: ${input.userDecisionNeeded}`
            : "",
        ]
          .filter(Boolean)
          .join("\n"),
      }),
    }),
  };
}
