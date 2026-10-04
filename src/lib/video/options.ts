export const VIDEO_STYLES = [
  "aula-ccnp",
  "aula-narrada",
  "reel-mono",
  "reel-mono-claro",
  "reel-camera",
  "reel-avatar",
  "reel-editorial",
  "quadro",
  "quadro-vertical",
  "vsl",
  "criativo",
  "criativo-reel",
  "lorcana-curto",
  "lorcana-longo",
  "anuncio-editorial",
  "podcast",
  "shorts-rapido",
  "teaser",
  "story-rapido",
  "webinar",
  "entrevista",
  "doc-vertical",
  "feed-quadrado",
  "pitch",
  "cold-open",
  "tutorial",
  "unboxing",
  "hook-15s",
  "live-highlight",
  "carrossel",
] as const;

export type VideoStyle = (typeof VIDEO_STYLES)[number];

export const VIDEO_FONTS = [
  "montserrat",
  "ibm",
  "bebas",
  "oswald",
  "space",
  "outfit",
  "archivo",
  "rubik",
  "barlow",
  "anton",
  "bangers",
  "syne",
  "rajdhani",
  "teko",
  "blackops",
  "kanit",
] as const;

export type VideoFont = (typeof VIDEO_FONTS)[number];

export const VIDEO_GRADES = [
  "none",
  "subtle",
  "neutral_punch",
  "warm_cinematic",
  "cool_night",
  "teal_orange",
  "high_contrast",
  "soft_pastel",
  "noir",
  "vivid_social",
  "documentary",
] as const;

export type VideoGrade = (typeof VIDEO_GRADES)[number];

export const VIDEO_FORMATS = ["16:9", "9:16", "1:1", "4:5", "21:9"] as const;
export type VideoFormat = (typeof VIDEO_FORMATS)[number];

export const VIDEO_SOUNDS = [
  "none",
  "tick",
  "click",
  "impacto",
  "whoosh",
  "transicao",
  "riser",
  "pop",
  "bass",
  "swoosh",
  "glitch",
] as const;
export type VideoSound = (typeof VIDEO_SOUNDS)[number];

export const VIDEO_EFFECTS = [
  "none",
  "crt",
  "fade",
  "glitch",
  "flash",
  "whip",
] as const;
export type VideoEffect = (typeof VIDEO_EFFECTS)[number];

export type WhisperModel =
  | "tiny"
  | "base"
  | "small"
  | "medium"
  | "large-v3";

export type VideoEditOptions = {
  estilo: VideoStyle;
  language: string;
  whisperModel: WhisperModel;
  captions: boolean;
  autoRender: boolean;
  /** Confirma o plano automaticamente após o dry-run. */
  autoConfirm: boolean;
  resolution: "1080p" | "1440p" | "4k";
  pauseKeep: number;
  silCut: number;
  introOutro: "none" | "fade" | "crt";
  crop?: string;
  projeto: string;
  fonte: VideoFont;
  grade: VideoGrade;
  formato: VideoFormat;
  som: VideoSound;
  efeitoEmenda: "none" | "glitch" | "flash" | "whip";
  intensidade: "subtle" | "medium" | "strong";
};

export const DEFAULT_VIDEO_OPTIONS: VideoEditOptions = {
  estilo: "aula-ccnp",
  language: "pt",
  whisperModel: "medium",
  captions: true,
  autoRender: true,
  autoConfirm: true,
  resolution: "1080p",
  pauseKeep: 0.9,
  silCut: 2.0,
  introOutro: "crt",
  projeto: "grokish",
  fonte: "montserrat",
  grade: "neutral_punch",
  formato: "16:9",
  som: "none",
  efeitoEmenda: "glitch",
  intensidade: "subtle",
};

export const STYLE_LABELS: Record<VideoStyle, string> = {
  "aula-ccnp": "Aula 16:9 (live)",
  "aula-narrada": "Aula narrada 16:9",
  "reel-mono": "Reel live 9:16",
  "reel-mono-claro": "Reel live claro 9:16",
  "reel-camera": "Reel câmera 9:16",
  "reel-avatar": "Reel avatar 9:16",
  "reel-editorial": "Reel editorial 9:16",
  quadro: "Quadro 16:9",
  "quadro-vertical": "Quadro vertical 9:16",
  vsl: "VSL avatar 9:16",
  criativo: "Criativo 9:16",
  "criativo-reel": "Criativo reel 9:16",
  "lorcana-curto": "Lorcana curto 9:16",
  "lorcana-longo": "Lorcana longo 16:9",
  "anuncio-editorial": "Anúncio editorial 9:16",
  podcast: "Podcast 16:9",
  "shorts-rapido": "Shorts rápido 9:16",
  teaser: "Teaser 9:16",
  "story-rapido": "Story rápido 9:16",
  webinar: "Webinar 16:9",
  entrevista: "Entrevista 16:9",
  "doc-vertical": "Doc vertical 9:16",
  "feed-quadrado": "Feed 1:1",
  pitch: "Pitch / elevador 9:16",
  "cold-open": "Cold open 21:9",
  tutorial: "Tutorial / how-to 9:16",
  unboxing: "Unboxing 9:16",
  "hook-15s": "Hook 15s 9:16",
  "live-highlight": "Live highlight 16:9",
  carrossel: "Carrossel 4:5",
};

export const FONT_LABELS: Record<VideoFont, string> = {
  montserrat: "Montserrat Black",
  ibm: "IBM Plex Mono",
  bebas: "Bebas Neue",
  oswald: "Oswald Bold",
  space: "Space Grotesk",
  outfit: "Outfit Bold",
  archivo: "Archivo Black",
  rubik: "Rubik Black",
  barlow: "Barlow Condensed",
  anton: "Anton",
  bangers: "Bangers",
  syne: "Syne Bold",
  rajdhani: "Rajdhani Bold",
  teko: "Teko Bold",
  blackops: "Black Ops One",
  kanit: "Kanit Bold",
};

export const SOUND_LABELS: Record<VideoSound, string> = {
  none: "Nenhum",
  tick: "Tick",
  click: "Click",
  impacto: "Impacto",
  whoosh: "Whoosh",
  transicao: "Transição",
  riser: "Riser",
  pop: "Pop",
  bass: "Bass",
  swoosh: "Swoosh",
  glitch: "Glitch SFX",
};

export const FORMAT_CANVAS: Record<VideoFormat, string | undefined> = {
  "16:9": undefined,
  "9:16": undefined,
  "1:1": "1080x1080",
  "4:5": "1080x1350",
  "21:9": "2560x1080",
};
