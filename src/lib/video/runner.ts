import { spawn } from "node:child_process";
import { mkdir, writeFile, access } from "node:fs/promises";
import path from "node:path";
import {
  EDITS_DIR,
  HELPERS_DIR,
  KIT_PYTHON,
  OUTPUTS_DIR,
  UPLOADS_DIR,
} from "./paths";
import type { VideoEditOptions } from "./options";

export type RunResult = {
  ok: boolean;
  code: number | null;
  stdout: string;
  stderr: string;
};

async function ensureDirs() {
  await Promise.all([
    mkdir(UPLOADS_DIR, { recursive: true }),
    mkdir(EDITS_DIR, { recursive: true }),
    mkdir(OUTPUTS_DIR, { recursive: true }),
  ]);
}

export async function kitPythonReady(): Promise<boolean> {
  try {
    await access(KIT_PYTHON);
    return true;
  } catch {
    return false;
  }
}

export function runHelper(
  script: string,
  args: string[],
  options?: { timeoutMs?: number },
): Promise<RunResult> {
  return new Promise((resolve) => {
    const child = spawn(KIT_PYTHON, [path.join(HELPERS_DIR, script), ...args], {
      cwd: HELPERS_DIR,
      env: process.env,
    });

    let stdout = "";
    let stderr = "";
    const timer =
      options?.timeoutMs != null
        ? setTimeout(() => {
            child.kill("SIGTERM");
          }, options.timeoutMs)
        : null;

    child.stdout.on("data", (chunk: Buffer) => {
      stdout += chunk.toString();
    });
    child.stderr.on("data", (chunk: Buffer) => {
      stderr += chunk.toString();
    });
    child.on("close", (code) => {
      if (timer) clearTimeout(timer);
      resolve({
        ok: code === 0,
        code,
        stdout: stdout.trim(),
        stderr: stderr.trim(),
      });
    });
    child.on("error", (err) => {
      if (timer) clearTimeout(timer);
      resolve({
        ok: false,
        code: null,
        stdout,
        stderr: err.message,
      });
    });
  });
}

export async function listStyles(): Promise<RunResult> {
  await ensureDirs();
  return runHelper("estilo.py", []);
}

export async function describeStyle(nome: string): Promise<RunResult> {
  return runHelper("estilo.py", [nome]);
}

export async function transcribeVideo(input: {
  videoPath: string;
  language: string;
  model: string;
}): Promise<RunResult & { transcriptPath?: string }> {
  await ensureDirs();
  const videoPath = path.resolve(input.videoPath);
  const slug = path.parse(videoPath).name;
  const editDir = path.join(EDITS_DIR, slug);

  const result = await runHelper(
    "transcribe.py",
    [
      videoPath,
      "--edit-dir",
      editDir,
      "--language",
      input.language,
      "--model",
      input.model,
    ],
    { timeoutMs: 60 * 60 * 1000 },
  );

  const transcriptPath = path.join(
    editDir,
    "transcripts",
    `${slug}.json`,
  );
  // fallback common path used by the kit
  const alt = path.join(editDir, "transcript.json");

  return {
    ...result,
    transcriptPath: result.ok ? transcriptPath : undefined,
    stdout:
      result.stdout +
      (result.ok
        ? `\ntranscript candidates:\n- ${transcriptPath}\n- ${alt}`
        : ""),
  };
}

export async function probeDurationSeconds(
  videoPath: string,
): Promise<number | null> {
  return new Promise((resolve) => {
    const child = spawn(
      "ffprobe",
      [
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        videoPath,
      ],
      { env: process.env },
    );
    let out = "";
    child.stdout.on("data", (c: Buffer) => {
      out += c.toString();
    });
    child.on("close", () => {
      const n = Number.parseFloat(out.trim());
      resolve(Number.isFinite(n) ? n : null);
    });
    child.on("error", () => resolve(null));
  });
}

export async function writePlan(input: {
  videoPath: string;
  transcriptPath?: string;
  options: VideoEditOptions;
  windows?: Array<[number, number]>;
  drops?: Array<[number, number]>;
  slug?: string;
}): Promise<{ planPath: string; plan: Record<string, unknown> }> {
  await ensureDirs();
  const videoPath = path.resolve(input.videoPath);
  const slug =
    input.slug ??
    `${path.parse(videoPath).name}-${input.options.estilo}`.replace(
      /[^a-zA-Z0-9-_]+/g,
      "-",
    );

  let windows = input.windows;
  if (!windows?.length) {
    const duration = await probeDurationSeconds(videoPath);
    windows = [[0, duration && duration > 1 ? duration : 60]];
  }

  const plan: Record<string, unknown> = {
    estilo: input.options.estilo,
    fonte: videoPath,
    slug,
    projeto: input.options.projeto,
    janelas: windows,
    drops: input.drops ?? [],
    pause_keep: input.options.pauseKeep,
    sil_cut: input.options.silCut,
  };

  if (input.transcriptPath) {
    plan.transcript = path.resolve(input.transcriptPath);
  }
  if (input.options.crop) {
    plan.crop = input.options.crop;
  }
  if (input.options.captions) {
    // many styles already enable caption resource; keep explicit flag for reel helpers
    plan.captions = true;
  }

  // resolution / intro overrides as axis patches when useful
  const imagem: Record<string, unknown> = {};
  if (input.options.resolution === "1080p") imagem.altura =
    input.options.estilo.includes("reel") ||
    input.options.estilo.includes("vertical") ||
    input.options.estilo === "vsl" ||
    input.options.estilo.startsWith("criativo") ||
    input.options.estilo.startsWith("lorcana-curto") ||
    input.options.estilo.startsWith("anuncio")
      ? 1920
      : 1080;
  if (input.options.resolution === "1440p") imagem.canvas = "2560x1440";
  if (input.options.resolution === "4k") imagem.altura = 2160;
  if (Object.keys(imagem).length) plan.imagem = imagem;

  if (input.options.introOutro === "crt") {
    plan.efeito = { abertura: "crt" };
  } else if (input.options.introOutro === "none") {
    plan.efeito = { abertura: null, emenda: null };
  }

  const planPath = path.join(EDITS_DIR, `${slug}.plan.json`);
  await writeFile(planPath, JSON.stringify(plan, null, 2), "utf8");
  return { planPath, plan };
}

export async function dryRunPlan(planPath: string): Promise<RunResult> {
  return runHelper("fabrica.py", [planPath, "--seco"], {
    timeoutMs: 10 * 60 * 1000,
  });
}

export async function renderPlan(planPath: string): Promise<RunResult> {
  return runHelper("fabrica.py", [planPath], {
    timeoutMs: 3 * 60 * 60 * 1000,
  });
}

export async function burnCaptions(input: {
  videoPath: string;
  srtPath: string;
  outputPath?: string;
}): Promise<RunResult & { outputPath?: string }> {
  const out =
    input.outputPath ??
    path.join(
      OUTPUTS_DIR,
      `${path.parse(input.videoPath).name}-legendado.mp4`,
    );
  const result = await runHelper("legendar.py", [
    input.videoPath,
    input.srtPath,
    "-o",
    out,
  ]);
  return { ...result, outputPath: result.ok ? out : undefined };
}

export async function measureBreathing(input: {
  wordsPath: string;
  edlPath: string;
}): Promise<RunResult> {
  return runHelper("folego.py", [
    "--words",
    input.wordsPath,
    "--edl",
    input.edlPath,
  ]);
}
