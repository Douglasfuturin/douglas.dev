import { tool } from "ai";
import { z } from "zod";
import {
  catalogSummary,
  getKitById,
  listInstalledKits,
  listSourceZips,
} from "@/lib/kits/discover";
import { installAllSourceZips, installKitFromZip } from "@/lib/kits/install";
import { runKitHelper } from "@/lib/kits/runner";

export function ninjaKitTools() {
  return {
    list_ninja_kits: tool({
      description:
        "Lista kits Ninja instalados e ZIPs disponíveis (sources/uploads). Use para inventariar F:\\NINJA CURSOS após upload.",
      inputSchema: z.object({}),
      execute: async () => catalogSummary(),
    }),

    describe_ninja_kit: tool({
      description:
        "Mostra detalhes de um kit instalado: descrição, helpers, assets, trecho do SKILL.md.",
      inputSchema: z.object({
        kitId: z.string(),
      }),
      execute: async ({ kitId }) => {
        const kit = await getKitById(kitId);
        if (!kit) {
          const available = (await listInstalledKits()).map((k) => k.id);
          return { ok: false, error: "Kit não encontrado", available };
        }
        return {
          ok: true,
          kit: {
            id: kit.id,
            name: kit.name,
            description: kit.description,
            kind: kit.kind,
            helpers: kit.helpers.map((h) => h.name),
            hasPythonVenv: kit.hasPythonVenv,
            hasPreferences: kit.hasPreferences,
            assets: kit.assets.slice(0, 20),
            tags: kit.tags,
            skillPreview: kit.skillBody?.slice(0, 4000),
          },
        };
      },
    }),

    install_ninja_kit_zip: tool({
      description:
        "Instala um ZIP de kit Ninja (caminho absoluto ou nome do arquivo em sources/uploads).",
      inputSchema: z.object({
        zipPathOrName: z.string(),
      }),
      execute: async ({ zipPathOrName }) => {
        const zips = await listSourceZips();
        const hit =
          zips.find((z) => z.path === zipPathOrName) ||
          zips.find((z) => z.filename === zipPathOrName) ||
          zips.find((z) =>
            z.filename.toLowerCase().includes(zipPathOrName.toLowerCase()),
          );
        const target = hit?.path || zipPathOrName;
        return installKitFromZip(target);
      },
    }),

    install_all_ninja_zips: tool({
      description:
        "Instala todos os ZIPs encontrados em ninja-kits/sources e na inbox de uploads do Cursor.",
      inputSchema: z.object({}),
      execute: async () => {
        const zips = await listSourceZips();
        if (!zips.length) {
          return {
            ok: false,
            error:
              "Nenhum ZIP encontrado. Envie os arquivos de F:\\NINJA CURSOS para a conversa ou copie para ninja-kits/sources/.",
            roots: (await catalogSummary()).roots,
          };
        }
        const result = await installAllSourceZips(zips.map((z) => z.path));
        return { ok: true, ...result, scanned: zips.length };
      },
    }),

    run_ninja_kit_helper: tool({
      description:
        "Executa um helper de um kit instalado (ex: estilo.py, catalogo.py). Prefira --help antes de runs longos.",
      inputSchema: z.object({
        kitId: z.string(),
        helper: z.string(),
        args: z.array(z.string()).optional(),
      }),
      execute: async ({ kitId, helper, args }) => {
        const result = await runKitHelper({
          kitId,
          helper,
          args,
          timeoutMs: 10 * 60 * 1000,
        });
        return {
          ok: result.ok,
          helperPath: result.helperPath,
          stdout: result.stdout.slice(-8000),
          stderr: result.stderr.slice(-4000) || undefined,
        };
      },
    }),
  };
}

export function kitPersona(kitId: string, skillBody?: string, name?: string) {
  return `You are the Grokish specialist for the Ninja kit "${name || kitId}".

You operate the installed kit tools via list_ninja_kits / describe_ninja_kit / run_ninja_kit_helper.
Follow the skill instructions below. Prefer Portuguese answers. Never invent file paths.

--- SKILL ---
${(skillBody || "Sem SKILL.md — inspecione helpers e guie o usuário.").slice(0, 10000)}
`;
}
