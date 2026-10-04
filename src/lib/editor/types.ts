export type EditorView = "visual" | "code";

export type TranscriptCue = {
  index: number;
  start: number;
  end: number;
  text: string;
};

export type FatSegment = {
  start: number;
  end: number;
  reason: string;
  seconds: number;
};

export type TakeWindow = {
  id: string;
  start: number;
  end: number;
  label?: string;
};

export type MediaAnalysis = {
  path: string;
  filename: string;
  duration: number;
  width: number;
  height: number;
  fps: number;
  orientation: "vertical" | "horizontal" | "square";
  description: string;
  waveform: number[];
  transcript: TranscriptCue[];
  fat: FatSegment[];
  takes: TakeWindow[];
  statusNote: string;
};

export type AgentLogEntry = {
  id: string;
  at: string;
  text: string;
};
