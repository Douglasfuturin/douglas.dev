import { tool } from "ai";
import { z } from "zod";
import { listCatalogAgents } from "./agent-catalog";
import { createCustomAgent, listCustomAgents } from "./custom-store";
import { TOOLKIT_LABELS, TOOLKIT_PRESETS, type ToolkitPreset } from "./custom-types";
import { listAllResolvedGroups } from "./group-resolve";

export function orchestratorTools() {
  return {
    list_delegatable_agents: tool({
      description:
        "Lista agentes que o Orquestrador pode delegar: catálogo (Radar, Roteirista, Arte…) + agentes custom do usuário.",
      inputSchema: z.object({
        operation: z
          .enum(["all", "ideacao", "script", "visual", "video", "times", "sistema"])
          .optional(),
      }),
      execute: async ({ operation = "all" }) => {
        const catalog = listCatalogAgents().filter((a) => a.id !== "orquestrador");
        const custom = await listCustomAgents();
        const filtered =
          operation === "all"
            ? catalog
            : catalog.filter((a) => a.operation === operation);
        return {
          ok: true,
          catalog: filtered.map((a) => ({
            id: a.id,
            name: a.name,
            mode: a.mode,
            role: a.role,
            operation: a.operation,
          })),
          customAgents: custom.map((a) => ({
            id: a.id,
            name: a.name,
            role: a.role,
            toolkit: a.toolkit,
            toolkitLabel: TOOLKIT_LABELS[a.toolkit],
          })),
        };
      },
    }),

    list_agent_groups: tool({
      description:
        "Lista grupos de agentes (Imagem, Vídeo, Espanha + grupos custom) com membros e fluxo.",
      inputSchema: z.object({}),
      execute: async () => {
        const groups = await listAllResolvedGroups();
        return {
          ok: true,
          groups: groups.map((g) => ({
            id: g.id,
            name: g.name,
            blurb: g.blurb,
            builtin: g.builtin,
            members: g.members.map((m) => ({
              id: m.id,
              name: m.name,
              mode: m.mode,
              role: m.role,
              isOrchestrator: m.isOrchestrator,
              customAgentId: m.customAgentId,
            })),
            workflow: g.workflow,
          })),
        };
      },
    }),

    create_custom_agent: tool({
      description:
        "Cria um novo agente custom e registra no sistema. Use quando o usuário pedir um agente novo ou nenhum existente servir.",
      inputSchema: z.object({
        name: z.string().min(2),
        role: z.string().min(3),
        instructions: z.string().min(10),
        toolkit: z.enum(TOOLKIT_PRESETS).optional(),
      }),
      execute: async (input) => {
        const agent = await createCustomAgent({
          name: input.name,
          role: input.role,
          instructions: input.instructions,
          toolkit: input.toolkit as ToolkitPreset | undefined,
        });
        return {
          ok: true,
          agent: {
            id: agent.id,
            name: agent.name,
            role: agent.role,
            toolkit: agent.toolkit,
            studioUrl: `/app?mode=custom&agent=${encodeURIComponent(agent.id)}`,
          },
          message:
            "Agente criado. Você pode delegar tarefas a ele nas próximas mensagens (mode=custom + agent id) ou continuar executando você mesmo com as tools do toolkit.",
        };
      },
    }),

    delegate_to_specialist: tool({
      description:
        "Registra delegação formal para um agente (catálogo, custom ou membro de grupo). Depois execute o trabalho com as tools adequadas e rotule a resposta (**Nome do agente:** …).",
      inputSchema: z.object({
        specialistName: z.string(),
        specialistMode: z.string().optional(),
        customAgentId: z.string().optional(),
        groupId: z.string().optional(),
        memberId: z.string().optional(),
        task: z.string(),
        expectedArtifact: z.string().optional(),
      }),
      execute: async (input) => ({
        ok: true,
        delegation: input,
        nextSteps: [
          `Executar como **${input.specialistName}** usando tools de ${input.specialistMode || "especialista"}`,
          "Entregar artefato ao usuário",
          "Resumir handoff para o Orquestrador / próximo passo do pipeline",
        ],
      }),
    }),
  };
}
