/** Identidade visual Douglas Dev — carrosséis realistas + brand kit. */

export const DOUGLAS_DEV_BRAND = {
  name: "Douglas Dev",
  handle: "@o.douglas.dev",
  colors: {
    black: "#0A0A0A",
    charcoal: "#161616",
    surface: "#1C1C1C",
    orange: "#F26522",
    orangeHot: "#FF6A1A",
    white: "#FFFFFF",
    muted: "#A8A8A8",
  },
  typography: {
    display: "Tall condensed bold sans (Anton / Bebas-like), ALL CAPS",
    body: "Clean geometric sans (Plus Jakarta / Montserrat-like)",
  },
  ui: {
    radius: "24–32px cards, pill buttons",
    ctaPrimary: "Orange pill 'Salve'",
    ctaSecondary: "Dark pill 'Siga' / 'Arraste →'",
    accentArrow: "Hand-drawn style orange arrow connecting problem → solution",
    slideBadge: "Dark circle with slide number on divider",
  },
  photoStyle:
    "Photorealistic lifestyle tech photography, cinematic warm/cool contrast, shallow DOF, Antes/Depois scenes (messy vs clean desk, cluttered phone vs calm UI)",
} as const;

export function douglasCarouselMasterPrompt(input: {
  topic: string;
  slideTitle: string;
  problem: string;
  solution: string;
  slideNumber: number;
  totalSlides: number;
  scene: "cover" | "antes-depois" | "fluxo" | "cta";
}) {
  const brand = DOUGLAS_DEV_BRAND;
  const base = `Instagram carousel slide in Douglas Dev brand identity.
Brand: ${brand.name} ${brand.handle}.
Colors: deep black/charcoal backgrounds, vibrant orange #F26522 accents, white typography.
Display type: tall condensed bold ALL CAPS headline.
UI: large rounded corners (~28px), pill buttons (Salve orange, Siga dark), orange arrow motif.
Photography: ${brand.photoStyle}.
No watermarks, no purple neon, no cartoon illustration.`;

  if (input.scene === "cover") {
    return `${base}
Cover slide ${input.slideNumber}/${input.totalSlides}.
Huge condensed headline "${input.slideTitle}".
Subline about AI automations / productivity: "${input.topic}".
Dark grid background, premium 3D or cinematic object with orange glow particles.
Glass UI overlays optional.`;
  }

  if (input.scene === "fluxo") {
    return `${base}
Slide ${input.slideNumber}/${input.totalSlides} titled "${input.slideTitle}".
White rounded workflow card on black: nodes Trigger → IA (orange border) → Action.
Mono label like fluxo_com_ia. Toggle Ativo. Topic: ${input.topic}.`;
  }

  if (input.scene === "cta") {
    return `${base}
Final CTA slide ${input.slideNumber}/${input.totalSlides}.
Headline "${input.slideTitle}".
Orange Salve + dark Siga pills, handle ${brand.handle}, Arraste →.
Dramatic portrait silhouette with orange-red halo lighting behind subject (Douglas Dev vibe).`;
  }

  return `${base}
Antes/Depois carousel slide ${input.slideNumber}/${input.totalSlides}.
Huge ALL CAPS title "${input.slideTitle}".
Left dark rounded problem card: "${input.problem}".
Orange arrow pointing to solution text: "${input.solution}".
Bottom: two photorealistic panels labeled ANTES and DEPOIS (pill badges), related to "${input.topic}".
Slide number badge "${String(input.slideNumber).padStart(2, "0")}" on center divider.
Header chrome: Douglas Dev avatar + Salve/Siga pills. Footer: ${brand.handle} + Arraste →.`;
}
