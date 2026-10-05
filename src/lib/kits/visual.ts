/** Skills com edição visual — abrem o painel de composição no dashboard. */

export type VisualKind =
  | "thumbnail"
  | "carousel"
  | "ad"
  | "image"
  | "diagram"
  | "slide"
  | "video";

export type AspectPreset = {
  id: string;
  label: string;
  /** largura / altura */
  ratio: number;
  hint: string;
};

export type StylePreset = {
  id: string;
  label: string;
  bg: string;
  fg: string;
  accent: string;
  mood: string;
};

export type VisualConfig = {
  kind: VisualKind;
  defaultAspect: string;
  aspects: AspectPreset[];
  styles: StylePreset[];
  defaultSlides?: number;
  maxSlides?: number;
  defaultVariations?: number;
  showSlides?: boolean;
  showVariations?: boolean;
};

const ASPECTS = {
  square: { id: "1:1", label: "1:1", ratio: 1, hint: "Feed" },
  portrait: { id: "4:5", label: "4:5", ratio: 4 / 5, hint: "Feed vertical" },
  story: { id: "9:16", label: "9:16", ratio: 9 / 16, hint: "Stories/Reels" },
  landscape: { id: "16:9", label: "16:9", ratio: 16 / 9, hint: "YouTube" },
  wide: { id: "1.91:1", label: "1.91:1", ratio: 1.91, hint: "Ads link" },
} as const;

const STYLES: StylePreset[] = [
  {
    id: "bold-dark",
    label: "Bold escuro",
    bg: "linear-gradient(160deg,#0f172a 0%,#1e293b 55%,#0f766e 100%)",
    fg: "#f8fafc",
    accent: "#2dd4bf",
    mood: "contraste alto, tipografia pesada",
  },
  {
    id: "clean-light",
    label: "Clean claro",
    bg: "linear-gradient(160deg,#f8fafc 0%,#e2e8f0 100%)",
    fg: "#0f172a",
    accent: "#0f766e",
    mood: "minimalista, respiração, sans moderna",
  },
  {
    id: "warm-editorial",
    label: "Editorial quente",
    bg: "linear-gradient(160deg,#1c1917 0%,#44403c 50%,#b45309 100%)",
    fg: "#fff7ed",
    accent: "#fdba74",
    mood: "editorial, serif display, calor",
  },
  {
    id: "neon-pop",
    label: "Neon pop",
    bg: "linear-gradient(135deg,#18181b 0%,#3b0764 45%,#db2777 100%)",
    fg: "#fdf4ff",
    accent: "#f0abfc",
    mood: "energia, pop, neon controlado",
  },
  {
    id: "handdrawn",
    label: "Hand-drawn",
    bg: "linear-gradient(160deg,#faf7f2 0%,#efe6d6 100%)",
    fg: "#1c1917",
    accent: "#b45309",
    mood: "traço à mão, caderno, informal",
  },
  {
    id: "meme",
    label: "Meme",
    bg: "linear-gradient(160deg,#111827 0%,#374151 100%)",
    fg: "#ffffff",
    accent: "#facc15",
    mood: "impacto imediato, texto Impact-like",
  },
];

function cfg(
  kind: VisualKind,
  opts: Partial<VisualConfig> & { defaultAspect: string; aspects: AspectPreset[] },
): VisualConfig {
  return {
    kind,
    styles: STYLES,
    showSlides: kind === "carousel" || kind === "slide",
    showVariations: kind === "ad" || kind === "image" || kind === "thumbnail",
    defaultSlides: 6,
    maxSlides: 12,
    defaultVariations: 4,
    ...opts,
  };
}

export const VISUAL_KITS: Record<string, VisualConfig> = {
  "youtube-thumbnail": cfg("thumbnail", {
    defaultAspect: "16:9",
    aspects: [ASPECTS.landscape, ASPECTS.square],
    defaultVariations: 4,
  }),
  "youtube-preview": cfg("thumbnail", {
    defaultAspect: "16:9",
    aspects: [ASPECTS.landscape, ASPECTS.story],
  }),
  "youtube-presentation": cfg("slide", {
    defaultAspect: "16:9",
    aspects: [ASPECTS.landscape],
    defaultSlides: 10,
    maxSlides: 24,
  }),
  "instagram-thumbnail": cfg("thumbnail", {
    defaultAspect: "9:16",
    aspects: [ASPECTS.story, ASPECTS.square, ASPECTS.portrait],
  }),
  "instagram-carousel-preview": cfg("carousel", {
    defaultAspect: "4:5",
    aspects: [ASPECTS.portrait, ASPECTS.square],
    defaultSlides: 8,
  }),
  "instagram-thread-carousel": cfg("carousel", {
    defaultAspect: "4:5",
    aspects: [ASPECTS.portrait, ASPECTS.square],
    defaultSlides: 8,
  }),
  "graphic-carousel": cfg("carousel", {
    defaultAspect: "4:5",
    aspects: [ASPECTS.portrait, ASPECTS.square, ASPECTS.story],
    defaultSlides: 8,
  }),
  "handdrawn-carousel": cfg("carousel", {
    defaultAspect: "4:5",
    aspects: [ASPECTS.portrait, ASPECTS.square],
    defaultSlides: 7,
    styles: STYLES.filter((s) =>
      ["handdrawn", "clean-light", "warm-editorial"].includes(s.id),
    ),
  }),
  "graphics-handdrawn-carousel": cfg("carousel", {
    defaultAspect: "4:5",
    aspects: [ASPECTS.portrait, ASPECTS.square],
    defaultSlides: 7,
    styles: STYLES.filter((s) =>
      ["handdrawn", "clean-light", "warm-editorial"].includes(s.id),
    ),
  }),
  "notebook-carousel": cfg("carousel", {
    defaultAspect: "4:5",
    aspects: [ASPECTS.portrait, ASPECTS.square],
    defaultSlides: 6,
    styles: STYLES.filter((s) =>
      ["handdrawn", "clean-light", "warm-editorial"].includes(s.id),
    ),
  }),
  "thread-to-carousel": cfg("carousel", {
    defaultAspect: "4:5",
    aspects: [ASPECTS.portrait, ASPECTS.square],
    defaultSlides: 8,
  }),
  "thread-to-carousel-alt": cfg("carousel", {
    defaultAspect: "4:5",
    aspects: [ASPECTS.portrait, ASPECTS.square, ASPECTS.story],
    defaultSlides: 8,
  }),
  "generate-ads": cfg("ad", {
    defaultAspect: "1:1",
    aspects: [ASPECTS.square, ASPECTS.story, ASPECTS.wide, ASPECTS.portrait],
    defaultVariations: 4,
  }),
  "cartoon-ad-generator": cfg("ad", {
    defaultAspect: "1:1",
    aspects: [ASPECTS.square, ASPECTS.story, ASPECTS.portrait],
    defaultVariations: 4,
    styles: STYLES.filter((s) =>
      ["bold-dark", "neon-pop", "meme"].includes(s.id),
    ),
  }),
  "meme-ad-generator": cfg("ad", {
    defaultAspect: "1:1",
    aspects: [ASPECTS.square, ASPECTS.story],
    defaultVariations: 5,
    styles: STYLES.filter((s) => ["meme", "bold-dark", "neon-pop"].includes(s.id)),
  }),
  "ecommerce-ad-generator": cfg("ad", {
    defaultAspect: "1:1",
    aspects: [ASPECTS.square, ASPECTS.story, ASPECTS.portrait, ASPECTS.wide],
    defaultVariations: 4,
  }),
  "brand-image": cfg("image", {
    defaultAspect: "16:9",
    aspects: [ASPECTS.landscape, ASPECTS.square, ASPECTS.portrait, ASPECTS.story],
    defaultVariations: 4,
  }),
  "photo-generator": cfg("image", {
    defaultAspect: "1:1",
    aspects: [ASPECTS.square, ASPECTS.portrait, ASPECTS.landscape, ASPECTS.story],
    defaultVariations: 4,
  }),
  "nano-banana-diagrams": cfg("diagram", {
    defaultAspect: "16:9",
    aspects: [ASPECTS.landscape, ASPECTS.square],
    defaultVariations: 2,
    styles: STYLES.filter((s) =>
      ["clean-light", "bold-dark", "warm-editorial"].includes(s.id),
    ),
  }),
  "nano-banana-pro-diagram-skill": cfg("diagram", {
    defaultAspect: "16:9",
    aspects: [ASPECTS.landscape, ASPECTS.square],
    defaultVariations: 2,
    styles: STYLES.filter((s) =>
      ["clean-light", "bold-dark", "warm-editorial"].includes(s.id),
    ),
  }),
  "webinar-deck": cfg("slide", {
    defaultAspect: "16:9",
    aspects: [ASPECTS.landscape],
    defaultSlides: 12,
    maxSlides: 30,
  }),
  ugc: cfg("ad", {
    defaultAspect: "9:16",
    aspects: [ASPECTS.story, ASPECTS.portrait, ASPECTS.square],
    defaultVariations: 3,
  }),
  "editar-video": cfg("video", {
    defaultAspect: "9:16",
    aspects: [ASPECTS.story, ASPECTS.landscape, ASPECTS.square],
    showVariations: false,
    showSlides: false,
  }),
  hyperframes: cfg("video", {
    defaultAspect: "16:9",
    aspects: [ASPECTS.landscape, ASPECTS.story, ASPECTS.square],
    showVariations: false,
    showSlides: false,
  }),
};

export const VISUAL_KIND_LABEL: Record<VisualKind, string> = {
  thumbnail: "Thumbnail",
  carousel: "Carrossel",
  ad: "Anúncio",
  image: "Imagem",
  diagram: "Diagrama",
  slide: "Slides",
  video: "Vídeo",
};

export function isVisualKit(id: string): boolean {
  return id in VISUAL_KITS;
}

export function visualConfigFor(id: string): VisualConfig | null {
  return VISUAL_KITS[id] ?? null;
}

export type VisualDraft = {
  aspectId: string;
  styleId: string;
  headline: string;
  subheadline: string;
  topic: string;
  slides: number;
  variations: number;
};

export function defaultVisualDraft(id: string): VisualDraft | null {
  const cfg = visualConfigFor(id);
  if (!cfg) return null;
  return {
    aspectId: cfg.defaultAspect,
    styleId: cfg.styles[0]?.id ?? "bold-dark",
    headline: "",
    subheadline: "",
    topic: "",
    slides: cfg.defaultSlides ?? 6,
    variations: cfg.defaultVariations ?? 4,
  };
}

export function buildVisualPrompt(
  kitId: string,
  kitName: string,
  draft: VisualDraft,
  extraBrief?: string,
): string {
  const cfg = visualConfigFor(kitId);
  if (!cfg) return extraBrief || `Use a skill ${kitName}.`;
  const style = cfg.styles.find((s) => s.id === draft.styleId) ?? cfg.styles[0];
  const aspect =
    cfg.aspects.find((a) => a.id === draft.aspectId) ?? cfg.aspects[0];

  const lines =
    kitId === "hyperframes"
      ? [
          `Use a skill HyperFrames (${kitId}) para criar/editar um vídeo HTML.`,
          "",
          "Especificação do painel visual:",
          `- Framework: HyperFrames (HeyGen)`,
          `- Formato: ${aspect.label} (${aspect.hint})`,
          `- Estilo visual: ${style.label} — ${style.mood}`,
          `- Paleta: ${style.id}, texto ${style.fg}, destaque ${style.accent}`,
        ]
      : [
          `Use a skill "${kitName}" (${kitId}) para produção visual.`,
          "",
          "Especificação do painel visual:",
          `- Tipo: ${VISUAL_KIND_LABEL[cfg.kind]}`,
          `- Formato: ${aspect.label} (${aspect.hint})`,
          `- Estilo: ${style.label} — ${style.mood}`,
          `- Paleta: fundo com caráter ${style.id}, texto ${style.fg}, destaque ${style.accent}`,
        ];

  if (draft.topic.trim()) lines.push(`- Tema/assunto: ${draft.topic.trim()}`);
  if (draft.headline.trim())
    lines.push(`- Título principal na arte: "${draft.headline.trim()}"`);
  if (draft.subheadline.trim())
    lines.push(`- Subtítulo/apoio: "${draft.subheadline.trim()}"`);
  if (cfg.showSlides) lines.push(`- Quantidade de slides: ${draft.slides}`);
  if (cfg.showVariations)
    lines.push(`- Variações a entregar: ${draft.variations}`);

  if (kitId === "hyperframes") {
    lines.push(
      "",
      "Siga skills/hyperframes/SKILL.md e roteie para core/animation/creative/cli conforme o pedido.",
      "Entregue composição HyperFrames + comandos de lint/preview/render.",
      "Responda em português.",
    );
  } else {
    lines.push(
      "",
      "Entregue o resultado pronto para usar (copy por peça + direção de arte + prompts de imagem quando couber).",
      "Responda em português.",
    );
  }

  if (extraBrief?.trim()) {
    lines.push("", "Pedido adicional do usuário:", extraBrief.trim());
  }

  return lines.join("\n");
}
