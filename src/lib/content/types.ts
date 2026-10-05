/** Pipeline stages for personal content ops (Central de Agentes). */
export const CONTENT_STAGES = [
  "idea",
  "approved",
  "script",
  "art",
  "video",
  "packaged",
  "ready",
  "scheduled",
  "published",
] as const;

export type ContentStage = (typeof CONTENT_STAGES)[number];

export const STAGE_LABELS: Record<ContentStage, string> = {
  idea: "Ideia",
  approved: "Aprovado",
  script: "Roteiro",
  art: "Artes",
  video: "Vídeo",
  packaged: "Pacote",
  ready: "Pronto",
  scheduled: "Agendado",
  published: "Postado",
};

export const NETWORKS = [
  "youtube",
  "instagram",
  "tiktok",
  "x",
  "linkedin",
  "notion",
] as const;

export type ContentNetwork = (typeof NETWORKS)[number];

export const NETWORK_LABELS: Record<ContentNetwork, string> = {
  youtube: "YouTube",
  instagram: "Instagram",
  tiktok: "TikTok",
  x: "X",
  linkedin: "LinkedIn",
  notion: "Notion",
};

export type ContentMarket = "br" | "es" | "en";

export type ContentSource =
  | "radar"
  | "github"
  | "manual"
  | "pipeline"
  | "grupo"
  | "central";

export type ContentAsset = {
  kind: "script" | "caption" | "thumbnail" | "video" | "carousel" | "notion" | "other";
  label: string;
  path?: string;
  url?: string;
  text?: string;
};

export type PublishJob = {
  id: string;
  contentId: string;
  network: ContentNetwork;
  status: "queued" | "scheduled" | "sent" | "failed";
  scheduledAt?: string;
  sentAt?: string;
  caption?: string;
  mediaPath?: string;
  error?: string;
  externalId?: string;
};

export type ContentItem = {
  id: string;
  title: string;
  summary: string;
  stage: ContentStage;
  market: ContentMarket;
  networks: ContentNetwork[];
  source: ContentSource;
  score?: number;
  tags: string[];
  topic?: string;
  script?: string;
  caption?: string;
  hashtags?: string[];
  artBrief?: string;
  videoPath?: string;
  thumbnailPath?: string;
  notionUrl?: string;
  assets: ContentAsset[];
  groupId?: string;
  notes?: string;
  approvedAt?: string;
  readyAt?: string;
  scheduledAt?: string;
  publishedAt?: string;
  createdAt: string;
  updatedAt: string;
};

export type ContentStore = {
  version: 1;
  items: ContentItem[];
  publishQueue: PublishJob[];
};

export function nextStage(stage: ContentStage): ContentStage | null {
  const i = CONTENT_STAGES.indexOf(stage);
  if (i < 0 || i >= CONTENT_STAGES.length - 1) return null;
  return CONTENT_STAGES[i + 1];
}

export function canAdvance(stage: ContentStage): boolean {
  return nextStage(stage) !== null;
}
