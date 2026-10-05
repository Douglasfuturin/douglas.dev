import type { MediaAnalysis, TakeWindow } from "@/lib/editor/types";
import type { VideoEditOptions, VideoStyle } from "@/lib/video/options";

export type EditorProject = {
  id: string;
  name: string;
  /** Pasta de saída do kit (`workspace/videos/<slug>/`). */
  slug: string;
  /** Estilo principal deste projeto — preferências de edição ficam isoladas. */
  estilo: VideoStyle;
  description: string;
  options: VideoEditOptions;
  mediaPath: string | null;
  mediaFilename: string | null;
  takes: TakeWindow[];
  /** Snapshot leve da última análise (sem waveform/transcript pesados). */
  analysisSummary: Pick<
    MediaAnalysis,
    "duration" | "width" | "height" | "orientation" | "statusNote"
  > | null;
  outputUrl: string | null;
  createdAt: string;
  updatedAt: string;
};

export type EditorProjectStore = {
  version: 1;
  activeProjectId: string | null;
  projects: EditorProject[];
};

export type EditorProjectInput = {
  name: string;
  estilo: VideoStyle;
  description?: string;
  options?: Partial<VideoEditOptions>;
};

export type EditorProjectPatch = Partial<
  Pick<
    EditorProject,
    | "name"
    | "description"
    | "estilo"
    | "options"
    | "mediaPath"
    | "mediaFilename"
    | "takes"
    | "analysisSummary"
    | "outputUrl"
  >
>;
