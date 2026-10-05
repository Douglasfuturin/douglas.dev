import { mkdir, copyFile, access } from "node:fs/promises";
import path from "node:path";
import { resolveSafeMediaPath } from "@/lib/editor/safe-path";
import {
  DEFAULT_VIDEO_OPTIONS,
  type VideoEditOptions,
} from "@/lib/video/options";
import { EDITS_DIR, OUTPUTS_DIR, ROOT, UPLOADS_DIR } from "@/lib/video/paths";
import {
  dryRunPlan,
  kitPythonReady,
  renderPlan,
  writePlan,
} from "@/lib/video/runner";

export const maxDuration = 300;

type RenderBody = {
  path?: string;
  takes?: Array<{ start: number; end: number }>;
  dryRunOnly?: boolean;
  videoOptions?: Partial<VideoEditOptions>;
  slug?: string;
};

export async function POST(req: Request) {
  if (!(await kitPythonReady())) {
    return Response.json(
      {
        error:
          "Kit Python do editor não está pronto. Rode uv sync no skill do editor EDVD.",
      },
      { status: 503 },
    );
  }

  const body = (await req.json()) as RenderBody;
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

  const options: VideoEditOptions = {
    ...DEFAULT_VIDEO_OPTIONS,
    ...body.videoOptions,
    autoConfirm: true,
    autoRender: !body.dryRunOnly,
    whisperModel: body.videoOptions?.whisperModel ?? "tiny",
  };

  const windows =
    body.takes && body.takes.length > 0
      ? (body.takes.map((t) => [t.start, t.end] as [number, number]) as Array<
          [number, number]
        >)
      : undefined;

  const slug =
    body.slug ||
    `edvd-${path.parse(filePath).name}-${Date.now()}`.replace(
      /[^a-zA-Z0-9-_]+/g,
      "-",
    );

  try {
    const { planPath, plan } = await writePlan({
      videoPath: filePath,
      options,
      windows,
      slug,
    });

    const dry = await dryRunPlan(planPath);
    if (!dry.ok) {
      return Response.json(
        {
          ok: false,
          step: "dry_run",
          planPath,
          plan,
          report: (dry.stdout || dry.stderr).slice(-8000),
          error: "Dry-run falhou",
        },
        { status: 500 },
      );
    }

    if (body.dryRunOnly) {
      return Response.json({
        ok: true,
        step: "dry_run",
        planPath,
        plan,
        report: dry.stdout.slice(-6000),
      });
    }

    const rendered = await renderPlan(planPath);
    if (!rendered.ok) {
      return Response.json(
        {
          ok: false,
          step: "render",
          planPath,
          plan,
          dryRun: dry.stdout.slice(-3000),
          renderLog: (rendered.stdout || rendered.stderr).slice(-8000),
          error: "Render falhou",
        },
        { status: 500 },
      );
    }

    await mkdir(OUTPUTS_DIR, { recursive: true });
    const estilo = String(plan.estilo || "aula-ccnp");
    const projeto = String(plan.projeto || "grokish");
    const candidates = [
      // saida=workspace/videos + estilos reel → videos/reels/<slug>.mp4
      path.join(UPLOADS_DIR, "reels", `${slug}.mp4`),
      path.join(UPLOADS_DIR, "topo", `${slug}.mp4`),
      path.join(UPLOADS_DIR, projeto, `${slug}.mp4`),
      path.join(UPLOADS_DIR, `${slug}.mp4`),
      // fallback kit-local (planos antigos sem saida)
      path.join(ROOT, ["kit", "edicao", "video"].join("-"), "videos", "reels", `${slug}.mp4`),
      path.join(ROOT, ["kit", "edicao", "video"].join("-"), "videos", projeto, `${slug}.mp4`),
      path.join(ROOT, ["kit", "edicao", "video"].join("-"), "videos", `${slug}.mp4`),
      path.join(EDITS_DIR, slug, "final.mp4"),
      path.join(EDITS_DIR, slug, "entrega.mp4"),
    ];
    void estilo;

    let outputPath: string | null = null;
    for (const c of candidates) {
      try {
        await access(c);
        outputPath = c;
        break;
      } catch {
        /* next */
      }
    }

    let publicUrl: string | null = null;
    if (outputPath) {
      const publicName = `${slug}.mp4`;
      const dest = path.join(OUTPUTS_DIR, publicName);
      await copyFile(outputPath, dest);
      publicUrl = `/outputs/${publicName}`;
    }

    return Response.json({
      ok: true,
      step: "render",
      planPath,
      plan,
      dryRun: dry.stdout.slice(-2000),
      renderLog: (rendered.stdout || rendered.stderr).slice(-4000),
      outputPath,
      publicUrl,
    });
  } catch (err) {
    return Response.json(
      {
        ok: false,
        error: err instanceof Error ? err.message : "Erro no render",
      },
      { status: 500 },
    );
  }
}
