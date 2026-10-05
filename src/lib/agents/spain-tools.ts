import { tool } from "ai";
import { z } from "zod";
import { getKitById, listInstalledKits } from "@/lib/kits/discover";
import { VISUAL_KITS } from "@/lib/kits/visual";

const CAROUSEL_KITS = [
  "graphic-carousel",
  "instagram-carousel-preview",
  "instagram-thread-carousel",
  "handdrawn-carousel",
  "graphics-handdrawn-carousel",
  "notebook-carousel",
  "thread-to-carousel",
  "thread-to-carousel-alt",
];

const YOUTUBE_KITS = [
  "youtube-pack",
  "youtube-script",
  "youtube-title",
  "youtube-description",
  "youtube-thumbnail",
  "youtube-research",
  "youtube-preview",
];

const THUMB_KITS = [
  "youtube-thumbnail",
  "instagram-thumbnail",
  "youtube-preview",
  "brand-image",
  "photo-generator",
];

async function skillStatus(ids: string[]) {
  const installed = await listInstalledKits();
  const map = new Map(installed.map((k) => [k.id, k]));
  return ids.map((id) => ({
    id,
    installed: map.has(id),
    name: map.get(id)?.name || id,
    visual: VISUAL_KITS[id]?.kind || null,
  }));
}

export function spainContentTools() {
  return {
    plan_youtube_es: tool({
      description:
        "Monta un pack YouTube en español (España): títulos, guion, descripción, timestamps y brief de thumbnail. Usa skills youtube-* del sistema.",
      inputSchema: z.object({
        tema: z.string(),
        duracionMin: z.number().optional(),
        tono: z
          .enum(["educativo", "opinión", "tutorial", "noticias", "entretenimiento"])
          .optional(),
        audiencia: z.string().optional(),
      }),
      execute: async ({
        tema,
        duracionMin = 10,
        tono = "educativo",
        audiencia = "audiencia en España / LATAM hispanohablante",
      }) => {
        const skills = await skillStatus(YOUTUBE_KITS);
        const yt = await getKitById("youtube-pack");
        return {
          ok: true,
          locale: "es-ES",
          skills,
          skillPreview: yt?.skillBody?.slice(0, 2000) || null,
          pack: {
            tema,
            duracionMin,
            tono,
            audiencia,
            titulos: [
              `${tema}: lo que nadie te cuenta`,
              `Cómo ${tema} está cambiando 2026`,
              `${tema} en España — guía práctica`,
            ],
            estructuraGuion: [
              { min: "0:00", bloque: "Hook (promesa + tensión)" },
              { min: "0:30", bloque: "Contexto rápido" },
              { min: "2:00", bloque: "Punto 1 con ejemplo" },
              { min: "5:00", bloque: "Punto 2 + demo/caso" },
              { min: "8:00", bloque: "Errores comunes" },
              { min: `${Math.max(duracionMin - 1, 9)}:00`, bloque: "CTA + resumen" },
            ],
            descripcionOutline:
              "Intro SEO + timestamps + enlaces + CTA a newsletter/Discord",
            thumbnailBrief: {
              textoCorto: tema.slice(0, 28),
              emocion: "curiosidad + urgencia",
              contraste: "alto",
              aspect: "16:9",
            },
          },
          nextStep:
            "Escribe el guion completo, luego llama a plan_thumbnails_es y/o image_generation para la miniatura.",
        };
      },
    }),

    plan_carousel_es: tool({
      description:
        "Planifica un carrusel (Instagram/LinkedIn) en español: slides, copy y dirección visual. Usa skills de carousel del sistema.",
      inputSchema: z.object({
        tema: z.string(),
        slides: z.number().int().min(4).max(12).optional(),
        plataforma: z.enum(["instagram", "linkedin", "tiktok"]).optional(),
        estilo: z
          .enum(["grafico", "handdrawn", "notebook", "thread"])
          .optional(),
      }),
      execute: async ({
        tema,
        slides = 8,
        plataforma = "instagram",
        estilo = "grafico",
      }) => {
        const preferred =
          estilo === "handdrawn"
            ? "handdrawn-carousel"
            : estilo === "notebook"
              ? "notebook-carousel"
              : estilo === "thread"
                ? "thread-to-carousel"
                : "graphic-carousel";
        const skills = await skillStatus(CAROUSEL_KITS);
        const kit = await getKitById(preferred);
        const slidePlan = Array.from({ length: slides }, (_, i) => ({
          slide: i + 1,
          rol:
            i === 0
              ? "portada / gancho"
              : i === slides - 1
                ? "CTA final"
                : `punto ${i}`,
          headline: i === 0 ? tema : `Idea ${i}`,
          body:
            i === 0
              ? "Promesa clara en 1 línea"
              : i === slides - 1
                ? "Guarda + sígueme + comentario"
                : "Beneficio o tip accionable",
        }));
        return {
          ok: true,
          locale: "es-ES",
          plataforma,
          skillId: preferred,
          skillInstalled: Boolean(kit),
          skills,
          aspect: VISUAL_KITS[preferred]?.defaultAspect || "4:5",
          slides: slidePlan,
          nextStep:
            "Refina copy por slide y genera artes con image_generation (o skill visual del kit).",
        };
      },
    }),

    plan_thumbnails_es: tool({
      description:
        "Genera briefs y prompts de portadas/thumbnails (YouTube 16:9, Reels 9:16, carrusel) en español. Usa skills youtube-thumbnail / instagram-thumbnail.",
      inputSchema: z.object({
        tema: z.string(),
        formato: z
          .enum(["youtube", "reels", "carrusel", "ambos"])
          .optional(),
        textoEnImagen: z.string().optional(),
        variaciones: z.number().int().min(2).max(6).optional(),
      }),
      execute: async ({
        tema,
        formato = "ambos",
        textoEnImagen,
        variaciones = 4,
      }) => {
        const skills = await skillStatus(THUMB_KITS);
        const text = textoEnImagen || tema.slice(0, 32);
        const formats = [];
        if (formato === "youtube" || formato === "ambos") {
          formats.push({
            kind: "youtube-thumbnail",
            aspect: "16:9",
            prompt: `YouTube thumbnail, Spanish audience Spain, bold short text "${text}", high contrast face or product, cinematic light, no clutter, CTR-optimized composition about ${tema}`,
          });
        }
        if (formato === "reels" || formato === "ambos" || formato === "carrusel") {
          formats.push({
            kind: "instagram-cover",
            aspect: formato === "carrusel" ? "4:5" : "9:16",
            prompt: `Vertical cover for Reels/carousel, Spanish, bold typography "${text}", clean modern tech aesthetic, topic: ${tema}`,
          });
        }
        return {
          ok: true,
          locale: "es-ES",
          skills,
          variaciones,
          formats,
          checklist: [
            "Texto ≤ 4 palabras en la imagen",
            "Contraste alto legible en móvil",
            "Una emoción clara",
            "Probar 3–4 variaciones con image_generation",
          ],
          nextStep: "Llama image_generation con cada prompt.",
        };
      },
    }),
  };
}
