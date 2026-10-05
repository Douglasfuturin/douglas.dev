import { tool } from "ai";
import { z } from "zod";
import { VIDEO_STYLES, type VideoEditOptions } from "@/lib/video/options";
import {
  burnCaptions,
  describeStyle,
  dryRunPlan,
  kitPythonReady,
  listStyles,
  measureBreathing,
  renderPlan,
  runHelper,
  transcribeVideo,
  writePlan,
} from "@/lib/video/runner";
import { getKitById, listInstalledKits } from "@/lib/kits/discover";
import { runKitHelper } from "@/lib/kits/runner";
import { VISUAL_KITS } from "@/lib/kits/visual";

const styleSchema = z.enum(VIDEO_STYLES);

function mergeOptions(
  defaults: VideoEditOptions,
  patch?: Partial<VideoEditOptions>,
): VideoEditOptions {
  return { ...defaults, ...patch };
}

export function videoEditorTools(defaults: VideoEditOptions) {
  return {
    list_video_styles: tool({
      description:
        "Lista os estilos de edição disponíveis no kit (aula, reel, quadro, VSL, etc.).",
      inputSchema: z.object({}),
      execute: async () => {
        if (!(await kitPythonReady())) {
          return {
            error:
              "Kit Python não instalado. Rode uv sync em kit/skill do editor EDVD.",
          };
        }
        const result = await listStyles();
        return {
          ok: result.ok,
          styles: result.stdout,
          stderr: result.stderr || undefined,
        };
      },
    }),

    list_edit_catalog: tool({
      description:
        "Lista formatos, fontes do kit, sons/SFX, efeitos e grades de cor disponíveis.",
      inputSchema: z.object({
        parte: z
          .enum(["tudo", "formatos", "fontes", "sons", "efeitos", "grades"])
          .optional(),
      }),
      execute: async ({ parte }) => {
        const result = await runHelper("catalogo.py", [parte || "tudo"]);
        return {
          ok: result.ok,
          catalog: result.stdout || result.stderr,
        };
      },
    }),

    describe_video_style: tool({
      description: "Mostra a configuração completa de um estilo (eixos e recursos).",
      inputSchema: z.object({
        estilo: styleSchema,
      }),
      execute: async ({ estilo }) => {
        const result = await describeStyle(estilo);
        return {
          ok: result.ok,
          detail: result.stdout || result.stderr,
        };
      },
    }),

    transcribe_video: tool({
      description:
        "Transcreve um vídeo local com faster-whisper. Retorna caminho do transcript JSON.",
      inputSchema: z.object({
        videoPath: z.string().describe("Caminho absoluto do vídeo"),
        language: z.string().optional(),
        model: z
          .enum(["tiny", "base", "small", "medium", "large-v3"])
          .optional(),
      }),
      execute: async ({ videoPath, language, model }) => {
        const opts = mergeOptions(defaults, {
          language: language ?? defaults.language,
          whisperModel: model ?? defaults.whisperModel,
        });
        const result = await transcribeVideo({
          videoPath,
          language: opts.language,
          model: opts.whisperModel,
        });
        return {
          ok: result.ok,
          transcriptPath: result.transcriptPath,
          stdout: result.stdout.slice(-4000),
          stderr: result.stderr.slice(-2000) || undefined,
        };
      },
    }),

    create_edit_plan: tool({
      description:
        "Cria o plano.json do kit (estilo, janelas, drops, opções). Use após transcrever ou com janelas manuais.",
      inputSchema: z.object({
        videoPath: z.string(),
        transcriptPath: z.string().optional(),
        estilo: styleSchema.optional(),
        slug: z.string().optional(),
        windows: z
          .array(z.tuple([z.number(), z.number()]))
          .optional()
          .describe("Trechos [inicio_s, fim_s] a manter"),
        drops: z
          .array(z.tuple([z.number(), z.number()]))
          .optional()
          .describe("Trechos [inicio_s, fim_s] a remover"),
        crop: z.string().optional().describe('Filtro ffmpeg crop=w:h:x:y'),
      }),
      execute: async (input) => {
        const opts = mergeOptions(defaults, {
          estilo: input.estilo ?? defaults.estilo,
          crop: input.crop ?? defaults.crop,
        });
        const { planPath, plan } = await writePlan({
          videoPath: input.videoPath,
          transcriptPath: input.transcriptPath,
          options: opts,
          windows: input.windows,
          drops: input.drops,
          slug: input.slug,
        });
        return { ok: true, planPath, plan };
      },
    }),

    dry_run_edit: tool({
      description:
        "Roda a fábrica em modo --seco: monta a cadeia, EDL e custo sem renderizar. Sempre rode antes do render.",
      inputSchema: z.object({
        planPath: z.string(),
      }),
      execute: async ({ planPath }) => {
        const result = await dryRunPlan(planPath);
        return {
          ok: result.ok,
          report: (result.stdout || result.stderr).slice(-8000),
        };
      },
    }),

    render_edit: tool({
      description:
        "Renderiza o plano com fabrica.py (corte, voz, legendas/recursos do estilo, entrega).",
      inputSchema: z.object({
        planPath: z.string(),
      }),
      execute: async ({ planPath }) => {
        const result = await renderPlan(planPath);
        return {
          ok: result.ok,
          log: (result.stdout || result.stderr).slice(-8000),
        };
      },
    }),

    burn_captions: tool({
      description: "Queima um arquivo .srt em um vídeo pronto (legendar.py).",
      inputSchema: z.object({
        videoPath: z.string(),
        srtPath: z.string(),
        outputPath: z.string().optional(),
      }),
      execute: async (input) => {
        const result = await burnCaptions(input);
        return {
          ok: result.ok,
          outputPath: result.outputPath,
          log: (result.stdout || result.stderr).slice(-3000),
        };
      },
    }),

    measure_breathing: tool({
      description:
        "Mede o fôlego da aula (folego.py) — se o corte ficou sufocado após remover pausas.",
      inputSchema: z.object({
        wordsPath: z.string(),
        edlPath: z.string(),
      }),
      execute: async (input) => {
        const result = await measureBreathing(input);
        return {
          ok: result.ok,
          report: (result.stdout || result.stderr).slice(-4000),
        };
      },
    }),

    list_video_skills: tool({
      description:
        "Lista skills/kits de vídeo do sistema (editar-video, hyperframes, fabrica, etc.) prontos para edição automática.",
      inputSchema: z.object({}),
      execute: async () => {
        const installed = await listInstalledKits();
        const videoKits = installed.filter(
          (k) =>
            k.kind === "video" ||
            k.id === "editar-video" ||
            k.id === "hyperframes" ||
            k.id.includes("video") ||
            k.id.includes("fabrica") ||
            Boolean(VISUAL_KITS[k.id] && VISUAL_KITS[k.id].kind === "video"),
        );
        const seeded = [
          {
            id: "editar-video",
            name: "Editor EDVD (kit de edição)",
            path: ["kit", "edicao", "video"].join("-") + "/",
            pipeline: "auto_edit_video / fabrica.py",
          },
          {
            id: "hyperframes",
            name: "HyperFrames",
            path: "ninja-kits/installed/hyperframes/",
            pipeline: "skill HyperFrames + helpers",
          },
        ];
        return {
          ok: true,
          pythonReady: await kitPythonReady(),
          seeded,
          installedVideoSkills: videoKits.map((k) => ({
            id: k.id,
            name: k.name,
            helpers: k.helpers.map((h) => h.name),
            hasSkillMd: Boolean(k.skillBody),
          })),
          tip: "Para edição automática de MP4 use auto_edit_with_system_skills ou auto_edit_video.",
        };
      },
    }),

    auto_edit_video: tool({
      description:
        "Pipeline automático: transcreve → cria plano → dry-run → (se autoRender) renderiza. Ideal para edição sem microgestão.",
      inputSchema: z.object({
        videoPath: z.string(),
        estilo: styleSchema.optional(),
        windows: z.array(z.tuple([z.number(), z.number()])).optional(),
        drops: z.array(z.tuple([z.number(), z.number()])).optional(),
        skipTranscribe: z.boolean().optional(),
        transcriptPath: z.string().optional(),
        forceRender: z.boolean().optional(),
      }),
      execute: async (input) => {
        if (!(await kitPythonReady())) {
          return {
            ok: false,
            error:
              "Kit Python não instalado. Rode uv sync em kit/skill do editor EDVD.",
          };
        }

        const opts = mergeOptions(defaults, {
          estilo: input.estilo ?? defaults.estilo,
        });

        let transcriptPath = input.transcriptPath;
        let transcriptLog: string | undefined;

        if (!input.skipTranscribe && !transcriptPath) {
          const tr = await transcribeVideo({
            videoPath: input.videoPath,
            language: opts.language,
            model: opts.whisperModel,
          });
          transcriptLog = tr.stderr.slice(-1500) || tr.stdout.slice(-1500);
          if (!tr.ok) {
            return {
              ok: false,
              step: "transcribe",
              error: transcriptLog,
            };
          }
          transcriptPath = tr.transcriptPath;
        }

        const { planPath, plan } = await writePlan({
          videoPath: input.videoPath,
          transcriptPath,
          options: opts,
          windows: input.windows,
          drops: input.drops,
        });

        const dry = await dryRunPlan(planPath);
        if (!dry.ok) {
          return {
            ok: false,
            step: "dry_run",
            planPath,
            plan,
            report: (dry.stdout || dry.stderr).slice(-6000),
          };
        }

        const shouldRender = input.forceRender ?? (opts.autoRender && opts.autoConfirm);
        if (!shouldRender) {
          return {
            ok: true,
            step: "awaiting_confirm",
            planPath,
            plan,
            dryRun: dry.stdout.slice(-6000),
            message:
              "Dry-run OK. Peça render_edit com este planPath para gerar o MP4, ou ligue autoRender/autoConfirm.",
          };
        }

        const rendered = await renderPlan(planPath);
        return {
          ok: rendered.ok,
          step: "render",
          planPath,
          plan,
          dryRun: dry.stdout.slice(-3000),
          renderLog: (rendered.stdout || rendered.stderr).slice(-6000),
          transcriptPath,
          transcriptLog,
        };
      },
    }),

    auto_edit_with_system_skills: tool({
      description:
        "Edita vídeo automaticamente usando as skills do sistema: inventaria kits de vídeo (editar-video/hyperframes), aplica a skill escolhida e roda o pipeline EDVD (transcribe→plano→dry-run→render).",
      inputSchema: z.object({
        videoPath: z.string().describe("Caminho absoluto do MP4"),
        skillId: z
          .enum(["editar-video", "hyperframes", "auto"])
          .optional()
          .describe("Skill preferida (default auto → editar-video)"),
        estilo: styleSchema.optional(),
        forceRender: z.boolean().optional(),
        helper: z
          .string()
          .optional()
          .describe("Helper opcional da skill (ex.: estilo.py) antes do edit"),
        helperArgs: z.array(z.string()).optional(),
      }),
      execute: async ({
        videoPath,
        skillId = "auto",
        estilo,
        forceRender,
        helper,
        helperArgs,
      }) => {
        const chosen =
          skillId === "auto"
            ? ((await getKitById("editar-video")) ? "editar-video" : "editar-video")
            : skillId;

        const skill = await getKitById(chosen);
        let helperRun: Record<string, unknown> | null = null;
        if (skill && helper) {
          const result = await runKitHelper({
            kitId: chosen,
            helper,
            args: helperArgs,
            timeoutMs: 5 * 60 * 1000,
          });
          helperRun = {
            ok: result.ok,
            helper,
            stdout: result.stdout.slice(-3000),
            stderr: result.stderr.slice(-1500) || undefined,
          };
        }

        if (!(await kitPythonReady())) {
          return {
            ok: false,
            skillId: chosen,
            skillInstalled: Boolean(skill),
            skillPreview: skill?.skillBody?.slice(0, 1200) || null,
            helperRun,
            error:
              "Kit Python (EDVD) não instalado. Rode uv sync no skill do editor.",
          };
        }

        const opts = mergeOptions(defaults, {
          estilo: estilo ?? defaults.estilo,
        });

        let transcriptPath: string | undefined;
        const tr = await transcribeVideo({
          videoPath,
          language: opts.language,
          model: opts.whisperModel,
        });
        if (!tr.ok) {
          return {
            ok: false,
            skillId: chosen,
            step: "transcribe",
            skillInstalled: Boolean(skill),
            error: (tr.stderr || tr.stdout).slice(-2000),
          };
        }
        transcriptPath = tr.transcriptPath;

        const { planPath, plan } = await writePlan({
          videoPath,
          transcriptPath,
          options: opts,
        });
        const dry = await dryRunPlan(planPath);
        if (!dry.ok) {
          return {
            ok: false,
            skillId: chosen,
            step: "dry_run",
            planPath,
            skillInstalled: Boolean(skill),
            helperRun,
            report: (dry.stdout || dry.stderr).slice(-6000),
          };
        }

        const shouldRender =
          forceRender ?? (opts.autoRender && opts.autoConfirm);
        if (!shouldRender) {
          return {
            ok: true,
            skillId: chosen,
            skillInstalled: Boolean(skill),
            skillName: skill?.name || chosen,
            skillPreview: skill?.skillBody?.slice(0, 1500) || null,
            helperRun,
            step: "awaiting_confirm",
            planPath,
            plan,
            dryRun: dry.stdout.slice(-6000),
            message:
              "Skills do sistema aplicadas (EDVD). Dry-run OK — confirme para render_edit ou forceRender=true.",
          };
        }

        const rendered = await renderPlan(planPath);
        return {
          ok: rendered.ok,
          skillId: chosen,
          skillInstalled: Boolean(skill),
          skillName: skill?.name || chosen,
          helperRun,
          step: "render",
          planPath,
          plan,
          dryRun: dry.stdout.slice(-3000),
          renderLog: (rendered.stdout || rendered.stderr).slice(-6000),
          transcriptPath,
        };
      },
    }),
  };
}

export type VideoEditorTools = ReturnType<typeof videoEditorTools>;
