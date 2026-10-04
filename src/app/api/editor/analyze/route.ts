import { spawn } from "node:child_process";
import { access } from "node:fs/promises";
import path from "node:path";
import { resolveSafeMediaPath } from "@/lib/editor/safe-path";
import type {
  FatSegment,
  MediaAnalysis,
  TakeWindow,
  TranscriptCue,
} from "@/lib/editor/types";
import { EDITS_DIR, HELPERS_DIR, KIT_PYTHON } from "@/lib/video/paths";

export const maxDuration = 300;

function run(cmd: string, args: string[]): Promise<{ code: number; out: string; err: string }> {
  return new Promise((resolve) => {
    const child = spawn(cmd, args);
    let out = "";
    let err = "";
    child.stdout.on("data", (c: Buffer) => {
      out += c.toString();
    });
    child.stderr.on("data", (c: Buffer) => {
      err += c.toString();
    });
    child.on("close", (code) => resolve({ code: code ?? 1, out, err }));
    child.on("error", (e) => resolve({ code: 1, out: "", err: e.message }));
  });
}

async function probe(filePath: string) {
  const { out } = await run("ffprobe", [
    "-v",
    "error",
    "-select_streams",
    "v:0",
    "-show_entries",
    "stream=width,height,r_frame_rate,duration:format=duration",
    "-of",
    "json",
    filePath,
  ]);
  const json = JSON.parse(out || "{}") as {
    streams?: Array<{
      width?: number;
      height?: number;
      r_frame_rate?: string;
      duration?: string;
    }>;
    format?: { duration?: string };
  };
  const stream = json.streams?.[0] ?? {};
  const [num, den] = (stream.r_frame_rate || "30/1").split("/").map(Number);
  const fps = den ? num / den : 30;
  const duration = Number(stream.duration || json.format?.duration || 0);
  const width = stream.width || 1080;
  const height = stream.height || 1920;
  return { duration, width, height, fps };
}

async function waveformPeaks(filePath: string, samples = 240): Promise<number[]> {
  const { mkdir, readFile, unlink } = await import("node:fs/promises");
  await mkdir(EDITS_DIR, { recursive: true });
  const tmp = path.join(EDITS_DIR, `wf-${Date.now()}.pcm`);
  const { code } = await run("ffmpeg", [
    "-y",
    "-i",
    filePath,
    "-ac",
    "1",
    "-ar",
    "8000",
    "-f",
    "f32le",
    tmp,
  ]);

  if (code !== 0) {
    return Array.from({ length: samples }, () => 0.15);
  }

  try {
    const buf = await readFile(tmp);
    const floats = new Float32Array(
      buf.buffer,
      buf.byteOffset,
      Math.floor(buf.byteLength / 4),
    );
    if (!floats.length) return Array.from({ length: samples }, () => 0.12);
    const block = Math.max(1, Math.floor(floats.length / samples));
    const peaks: number[] = [];
    for (let i = 0; i < samples; i++) {
      let max = 0;
      const start = i * block;
      for (let j = start; j < start + block && j < floats.length; j++) {
        max = Math.max(max, Math.abs(floats[j]));
      }
      peaks.push(Math.min(1, max));
    }
    const peak = Math.max(...peaks, 0.0001);
    return peaks.map((p) => p / peak);
  } catch {
    return Array.from({ length: samples }, () => 0.12);
  } finally {
    await unlink(tmp).catch(() => undefined);
  }
}

function detectFat(peaks: number[], duration: number): FatSegment[] {
  if (!peaks.length || duration <= 0) return [];
  const fat: FatSegment[] = [];
  const threshold = 0.08;
  let silentStart: number | null = null;
  for (let i = 0; i < peaks.length; i++) {
    const t = (i / peaks.length) * duration;
    const quiet = peaks[i] < threshold;
    if (quiet && silentStart == null) silentStart = t;
    if ((!quiet || i === peaks.length - 1) && silentStart != null) {
      const end = quiet && i === peaks.length - 1 ? duration : t;
      const seconds = end - silentStart;
      if (seconds >= 0.45) {
        fat.push({
          start: Number(silentStart.toFixed(2)),
          end: Number(end.toFixed(2)),
          seconds: Number(seconds.toFixed(2)),
          reason:
            silentStart < 0.8
              ? "cabeça morta no início"
              : "silêncio / ar morto",
        });
      }
      silentStart = null;
    }
  }
  return fat;
}

function takesFromFat(duration: number, fat: FatSegment[]): TakeWindow[] {
  const cuts = fat
    .filter((f) => f.seconds >= 0.45)
    .map((f) => [f.start, f.end] as const);
  if (!cuts.length) {
    return [{ id: "take-1", start: 0, end: duration, label: "Take 1" }];
  }

  const takes: TakeWindow[] = [];
  let cursor = 0;
  let idx = 1;
  for (const [s, e] of cuts) {
    if (s - cursor >= 0.35) {
      takes.push({
        id: `take-${idx}`,
        start: Number(cursor.toFixed(2)),
        end: Number(s.toFixed(2)),
        label: `Take ${idx}`,
      });
      idx += 1;
    }
    cursor = e;
  }
  if (duration - cursor >= 0.35) {
    takes.push({
      id: `take-${idx}`,
      start: Number(cursor.toFixed(2)),
      end: Number(duration.toFixed(2)),
      label: `Take ${idx}`,
    });
  }
  return takes.length
    ? takes
    : [{ id: "take-1", start: 0, end: duration, label: "Take 1" }];
}

async function loadTranscript(videoPath: string): Promise<TranscriptCue[]> {
  const slug = path.parse(videoPath).name;
  const candidates = [
    path.join(EDITS_DIR, slug, "transcript.json"),
    path.join(EDITS_DIR, slug, "transcripts", `${slug}.json`),
  ];

  for (const candidate of candidates) {
    try {
      await access(candidate);
      const { readFile } = await import("node:fs/promises");
      const raw = JSON.parse(
        await readFile(/*turbopackIgnore: true*/ candidate, "utf8"),
      ) as {
        words?: Array<{ word?: string; text?: string; start: number; end: number }>;
        segments?: Array<{ text: string; start: number; end: number }>;
      };
      if (raw.segments?.length) {
        return raw.segments.map((s, i) => ({
          index: i + 1,
          start: s.start,
          end: s.end,
          text: s.text.trim(),
        }));
      }
      if (raw.words?.length) {
        const cues: TranscriptCue[] = [];
        let buf: string[] = [];
        let start = raw.words[0].start;
        let end = raw.words[0].end;
        for (const w of raw.words) {
          const token = (w.word || w.text || "").trim();
          if (!token) continue;
          if (!buf.length) start = w.start;
          buf.push(token);
          end = w.end;
          if (buf.length >= 8 || /[.!?]$/.test(token)) {
            cues.push({
              index: cues.length + 1,
              start,
              end,
              text: buf.join(" "),
            });
            buf = [];
          }
        }
        if (buf.length) {
          cues.push({
            index: cues.length + 1,
            start,
            end,
            text: buf.join(" "),
          });
        }
        return cues;
      }
    } catch {
      // continue
    }
  }

  // optional quick transcribe if kit python exists (may be slow; skip if missing)
  try {
    await access(KIT_PYTHON);
    const editDir = path.join(EDITS_DIR, slug);
    await run(KIT_PYTHON, [
      path.join(HELPERS_DIR, "transcribe.py"),
      videoPath,
      "--edit-dir",
      editDir,
      "--language",
      "pt",
      "--model",
      "tiny",
    ]);
    return loadTranscript(videoPath);
  } catch {
    return [];
  }
}

export async function POST(req: Request) {
  const body = (await req.json()) as { path?: string; transcribe?: boolean };
  if (!body.path) {
    return Response.json({ error: "path obrigatório" }, { status: 400 });
  }
  const filePath = resolveSafeMediaPath(body.path);
  if (!filePath) {
    return Response.json({ error: "caminho não permitido" }, { status: 400 });
  }

  try {
    await access(filePath);
  } catch {
    return Response.json({ error: "arquivo não encontrado" }, { status: 404 });
  }

  const meta = await probe(filePath);
  const waveform = await waveformPeaks(filePath, 280);
  const fat = detectFat(waveform, meta.duration);
  const takes = takesFromFat(meta.duration, fat);
  const transcript =
    body.transcribe === false ? [] : await loadTranscript(filePath);

  const kept = takes.reduce((acc, t) => acc + (t.end - t.start), 0);
  const removed = Math.max(0, meta.duration - kept);
  const orientation =
    meta.height > meta.width
      ? "vertical"
      : meta.width > meta.height
        ? "horizontal"
        : "square";

  const analysis: MediaAnalysis = {
    path: filePath,
    filename: path.basename(filePath),
    duration: Number(meta.duration.toFixed(2)),
    width: meta.width,
    height: meta.height,
    fps: Number(meta.fps.toFixed(2)),
    orientation,
    description:
      orientation === "vertical"
        ? "talking head / formato vertical para stories e reels"
        : "gravação horizontal — considere crop 9:16 no estilo reel",
    waveform,
    transcript,
    fat,
    takes,
    statusNote: `${path.parse(filePath).name} v1 – ${removed.toFixed(2).replace(".", ",")}s de gordura marcada. ${kept.toFixed(2).replace(".", ",")}s úteis. Revise e aprove.`,
  };

  return Response.json(analysis);
}
