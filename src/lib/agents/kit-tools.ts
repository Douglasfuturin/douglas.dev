import { tool } from "ai";
import { z } from "zod";
import {
  catalogSummary,
  getKitById,
  listInstalledKits,
  listSourceZips,
} from "@/lib/kits/discover";
import { installAllSourceZips, installKitFromZip } from "@/lib/kits/install";
import { loadManifest } from "@/lib/kits/manifest";
import { KIT_PERSONAS, personaForKit } from "@/lib/kits/skill-personas";
import { runKitHelper } from "@/lib/kits/runner";

export function ninjaKitTools() {
  return {
    list_ninja_kits: tool({
      description:
        "Lista o inventário completo de kits Ninja (manifesto F:\\NINJA CURSOS): instalados, ZIP pronto ou faltando.",
      inputSchema: z.object({}),
      execute: async () => catalogSummary(),
    }),

    describe_ninja_kit: tool({
      description:
        "Mostra detalhes de um kit (instalado ou do manifesto): persona, SKILL.md se houver, helpers.",
      inputSchema: z.object({
        kitId: z.string(),
      }),
      execute: async ({ kitId }) => {
        const kit = await getKitById(kitId);
        const manifest = await loadManifest().catch(() => null);
        const meta = manifest?.kits.find((k) => k.id === kitId);
        if (!kit && !meta && !KIT_PERSONAS[kitId]) {
          const available = [
            ...(await listInstalledKits()).map((k) => k.id),
            ...(manifest?.kits.map((k) => k.id) || []),
          ];
          return { ok: false, error: "Kit não encontrado", available };
        }
        return {
          ok: true,
          kit: {
            id: kitId,
            name: kit?.name || meta?.id || kitId,
            category: meta?.category,
            filename: meta?.filename,
            description: kit?.description || KIT_PERSONAS[kitId] || "",
            kind: kit?.kind || "skill",
            helpers: kit?.helpers.map((h) => h.name) || [],
            installed: Boolean(kit),
            persona: personaForKit(kitId, kit?.name),
            skillPreview: kit?.skillBody?.slice(0, 4000),
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
  const base = personaForKit(kitId, name);
  if (!skillBody) return base;
  return `${base}

--- SKILL.md instalado ---
${skillBody.slice(0, 10000)}
`;
}
