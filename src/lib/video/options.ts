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
] as const;

export type VideoStyle = (typeof VIDEO_STYLES)[number];

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
};
