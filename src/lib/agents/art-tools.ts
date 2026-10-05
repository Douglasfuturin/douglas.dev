import { tool } from "ai";
import { z } from "zod";
import {
  DOUGLAS_DEV_BRAND,
  douglasCarouselMasterPrompt,
} from "@/lib/brand/douglas-dev";

export function artDirectorTools(style: "twitter" | "realista") {
  return {
    deliver_art_direction: tool({
      description:
        style === "twitter"
          ? "Entrega briefing visual + prompts no estilo Twitter/X (capa, carrossel, meme tech) com identidade Douglas Dev (preto + laranja)."
          : "Entrega briefing + prompts de carrossel REALISTA Douglas Dev (Antes/Depois fotorealista, tipografia condensada, accent laranja #F26522).",
      inputSchema: z.object({
        topic: z.string().describe("Tema / manchete / produto"),
        format: z
          .enum(["capa", "carrossel", "meme", "cena-reels", "thumbnail"])
          .describe("Formato da peça"),
        mood: z.string().optional(),
        textOnImage: z
          .string()
          .optional()
          .describe("Texto curto / título condensado ALL CAPS"),
        problem: z
          .string()
          .optional()
          .describe("Frase do card de problema (carrossel realista)"),
        solution: z
          .string()
          .optional()
          .describe("Frase da solução após a seta laranja"),
        slides: z
          .number()
          .int()
          .min(1)
          .max(8)
          .optional()
          .describe("Nº de slides se carrossel"),
      }),
      execute: async ({
        topic,
        format,
        mood,
        textOnImage,
        problem,
        solution,
        slides = 5,
      }) => {
        const brand = DOUGLAS_DEV_BRAND;
        const title = (textOnImage || topic).toUpperCase();

        if (style === "realista" && format === "carrossel") {
          const slidePlan = [
            {
              slide: 1,
              scene: "cover" as const,
              title: title.slice(0, 28),
              problem: "",
              solution: "",
            },
            ...Array.from({ length: Math.max(slides - 2, 1) }, (_, i) => ({
              slide: i + 2,
              scene: "antes-depois" as const,
              title: title.slice(0, 22),
              problem:
                problem ||
                `Você ainda perde tempo com ${topic.toLowerCase()} no automático?`,
              solution:
                solution ||
                `Com IA: ${topic} fica no automático e você só revisa o que importa.`,
            })),
            {
              slide: slides,
              scene: "cta" as const,
              title: "SALVE ISSO",
              problem: "",
              solution: "",
            },
          ].slice(0, slides);

          const carousel = slidePlan.map((s) => ({
            slide: s.slide,
            scene: s.scene,
            prompt: douglasCarouselMasterPrompt({
              topic,
              slideTitle: s.title,
              problem: s.problem,
              solution: s.solution,
              slideNumber: s.slide,
              totalSlides: slides,
              scene: s.scene,
            }),
          }));

          return {
            ok: true,
            style: "douglas-realista",
            brand,
            topic,
            format,
            platformNotes: {
              aspect: "4:5 ou 1:1 Instagram",
              look: "preto + laranja #F26522, tipografia condensada ALL CAPS, pills, Antes/Depois fotorealista",
              platform: "Instagram carousel · Douglas Dev",
            },
            masterPrompt: carousel[1]?.prompt || carousel[0]?.prompt,
            carousel,
            checklist: [
              "Gerar cada slide com image_generation (prompts do carousel[])",
              "Manter tipografia condensada e accent laranja",
              "ANTES/DEPOIS com fotos realistas (não ilustração)",
              "Incluir Salve / Siga / Arraste → / @o.douglas.dev quando couber",
            ],
            nextStep:
              "Chame image_generation para cada slide.prompt do carrossel realista.",
          };
        }

        const twitterNotes = {
          aspect: format === "carrossel" || format === "capa" ? "1:1 ou 4:5" : "1:1",
          look: `Douglas Dev: fundo preto, accent ${brand.colors.orange}, tipografia bold condensada, poucas cores`,
          platform: "X/Twitter",
        };
        const realistaNotes = {
          aspect: format === "cena-reels" ? "9:16" : "16:9 ou 1:1",
          look: `Fotorealista cinematográfico + brand Douglas Dev (laranja ${brand.colors.orange} em UI), sem cartoon`,
          platform: "Reels / capa / LinkedIn",
        };
        const notes = style === "twitter" ? twitterNotes : realistaNotes;

        const basePrompt =
          style === "twitter"
            ? `Tech editorial graphic for X/Twitter about "${topic}" in Douglas Dev brand (black + orange #F26522, condensed bold type). ${notes.look}. Format: ${format}. ${
                textOnImage ? `Bold on-image text: "${textOnImage}".` : ""
              } Mood: ${mood || "sharp, modern, founder-tech"}. No watermarks.`
            : `Photorealistic cinematic still about "${topic}" with Douglas Dev orange accents. ${notes.look}. Format: ${format}. ${
                textOnImage ? `Subtle condensed title: "${textOnImage}".` : "No heavy typography."
              } Mood: ${mood || "premium, documentary, warm contrast"}. No watermarks, no illustration.`;

        const carousel =
          format === "carrossel"
            ? Array.from({ length: slides }, (_, i) => ({
                slide: i + 1,
                prompt: `${basePrompt} Carousel slide ${i + 1}/${slides}. Clear visual hierarchy.`,
              }))
            : null;

        return {
          ok: true,
          style: style === "realista" ? "douglas-realista" : "douglas-twitter",
          brand,
          topic,
          format,
          platformNotes: notes,
          masterPrompt: basePrompt,
          carousel,
          checklist: [
            "Gerar com image_generation usando masterPrompt (ou cada slide)",
            "Respeitar preto + laranja #F26522",
            "Exportar no aspect ratio indicado",
            "Alinhar com o roteiro aprovado",
          ],
          nextStep:
            "Chame image_generation com o masterPrompt (e slides, se houver).",
        };
      },
    }),

    plan_carrossel_realista_douglas: tool({
      description:
        "Planeja carrossel Instagram REALISTA no estilo Douglas Dev (@o.douglas.dev): capa, slides Antes/Depois, fluxo IA e CTA — com prompts prontos para image_generation.",
      inputSchema: z.object({
        tema: z.string(),
        tituloPrincipal: z
          .string()
          .optional()
          .describe("Headline condensada ALL CAPS, ex.: CORTAR VÍDEOS"),
        automacoes: z
          .array(
            z.object({
              titulo: z.string(),
              problema: z.string(),
              solucao: z.string(),
            }),
          )
          .min(1)
          .max(6)
          .optional(),
      }),
      execute: async ({ tema, tituloPrincipal, automacoes }) => {
        const title = (tituloPrincipal || tema).toUpperCase();
        const items =
          automacoes && automacoes.length
            ? automacoes
            : [
                {
                  titulo: title,
                  problema: `Ainda faz ${tema.toLowerCase()} na mão e perde horas?`,
                  solucao: `Um agente com IA resolve o básico e te devolve só o que importa.`,
                },
                {
                  titulo: "RESPONDER CLIENTES",
                  problema:
                    "Clientes mandam as mesmas perguntas no WhatsApp o dia inteiro?",
                  solucao:
                    "Um agente com IA responde o básico e te passa só os casos difíceis.",
                },
                {
                  titulo: "RESUMIR REUNIÕES",
                  problema:
                    "Saiu da reunião com a página rabiscada e ninguém lembra quem faz o quê?",
                  solucao:
                    "A IA lê a transcrição e devolve decisões e tarefas com responsável.",
                },
              ];

        const slides = [
          {
            slide: 1,
            tipo: "capa",
            prompt: douglasCarouselMasterPrompt({
              topic: tema,
              slideTitle: "TAREFAS NO AUTOMÁTICO",
              problem: "",
              solution: "",
              slideNumber: 1,
              totalSlides: items.length + 2,
              scene: "cover",
            }),
          },
          ...items.map((item, i) => ({
            slide: i + 2,
            tipo: "antes-depois",
            titulo: item.titulo.toUpperCase(),
            problema: item.problema,
            solucao: item.solucao,
            prompt: douglasCarouselMasterPrompt({
              topic: tema,
              slideTitle: item.titulo.toUpperCase(),
              problem: item.problema,
              solution: item.solucao,
              slideNumber: i + 2,
              totalSlides: items.length + 2,
              scene: "antes-depois",
            }),
          })),
          {
            slide: items.length + 2,
            tipo: "cta",
            prompt: douglasCarouselMasterPrompt({
              topic: tema,
              slideTitle: "SALVE E SIGA",
              problem: "",
              solution: "",
              slideNumber: items.length + 2,
              totalSlides: items.length + 2,
              scene: "cta",
            }),
          },
        ];

        return {
          ok: true,
          brand: DOUGLAS_DEV_BRAND,
          tema,
          slides,
          copyHints: {
            header: "Douglas Dev · verificado",
            buttons: ["Salve", "Siga", "Arraste →"],
            handle: DOUGLAS_DEV_BRAND.handle,
          },
          nextStep:
            "Gere cada slide.prompt com image_generation. Mantenha identidade preto + laranja.",
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
