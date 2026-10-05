import { tool } from "ai";
import { z } from "zod";
import { TOOLKIT_PRESETS, type ToolkitPreset } from "./custom-types";
import { insertMemberAfterInGroup, duplicateUserGroup, archiveUserGroup } from "./group-store-ext";
import {
  addMemberToGroup,
  createUserGroup,
  deleteUserGroup,
  getUserGroup,
  removeMemberFromGroup,
  updateUserGroup,
} from "./group-store";
import { reorderGroupMembers, listSalasForOrchestrator } from "./group-pipeline";
import { logOrchestratorAction } from "./registry/actions-log";
import { recordAgentExecution } from "./registry/executions";
import {
  confirmProposal,
  createProposal,
  createRegistryAgent,
  findRegistryAgentByName,
  getRegistryAgent,
  listRegistryAgents,
  setRegistryAgentStatus,
  updateRegistryAgent,
} from "./registry/store";
import { listAgentExecutions } from "./registry/executions";
import { listOrchestratorActions, undoLastOrchestratorAction } from "./registry/actions-log";
import { orchestratorTools } from "./orchestrator-tools";

const toolkitEnum = z.enum(TOOLKIT_PRESETS);

function previewAgent(agent: {
  name: string;
  avatar: string;
  color: string;
  role: string;
  systemPrompt: string;
  toolkit: string;
  model: string;
  inputs: string[];
  outputs: string[];
}) {
  return {
    name: agent.name,
    avatar: agent.avatar,
    color: agent.color,
    role: agent.role,
    systemPromptPreview: agent.systemPrompt.slice(0, 600),
    model: agent.model,
    toolkit: agent.toolkit,
    inputs: agent.inputs,
    outputs: agent.outputs,
  };
}

export function orchestratorSystemTools() {
  const legacy = orchestratorTools();

  return {
    ...legacy,

    listar_agentes: tool({
      description: "Lista agentes dinâmicos do registro (ativos, pausados ou todos).",
      inputSchema: z.object({
        status: z.enum(["active", "paused", "archived", "all"]).optional(),
      }),
      execute: async ({ status = "active" }) => {
        const agents = await listRegistryAgents({
          status: status === "all" ? "all" : status,
        });
        return {
          ok: true,
          uiEvent: { type: "registry_refresh" },
          agents: agents.map((a) => ({
            id: a.id,
            name: a.name,
            avatar: a.avatar,
            color: a.color,
            role: a.role,
            status: a.status,
            version: a.version,
            toolkit: a.toolkit,
            runtimeMode: a.runtimeMode,
          })),
        };
      },
    }),

    criar_agente: tool({
      description:
        "Propõe criação de agente por linguagem natural. Por padrão NÃO salva — retorna card de pré-visualização (Confirmar/Editar/Cancelar). Use salvar_direto=true só se o usuário já confirmou no chat.",
      inputSchema: z.object({
        name: z.string().min(2),
        role: z.string().min(3),
        systemPrompt: z.string().min(20),
        toolkit: toolkitEnum.optional(),
        model: z.enum(["chat", "multi"]).optional(),
        color: z.string().optional(),
        avatar: z.string().optional(),
        inputs: z.array(z.string()).optional(),
        outputs: z.array(z.string()).optional(),
        allowedTools: z.array(z.string()).optional(),
        salvar_direto: z.boolean().optional(),
      }),
      execute: async (input) => {
        const payload = {
          name: input.name,
          role: input.role,
          systemPrompt: input.systemPrompt,
          toolkit: input.toolkit as ToolkitPreset | undefined,
          model: input.model,
          color: input.color,
          avatar: input.avatar,
          inputs: input.inputs,
          outputs: input.outputs,
          allowedTools: input.allowedTools,
          runtimeMode: "custom",
        };

        if (input.salvar_direto) {
          const agent = await createRegistryAgent(payload);
          await logOrchestratorAction({
            kind: "create_agent",
            label: `Criou agente ${agent.name}`,
            undoable: true,
            undoPayload: {
              type: "restore_agent_status",
              agentId: agent.id,
              status: "archived",
            },
          });
          return {
            ok: true,
            saved: true,
            agent: previewAgent({
              ...agent,
              systemPrompt: agent.systemPrompt,
            }),
            uiEvent: { type: "registry_refresh" },
          };
        }

        const proposal = await createProposal({
          kind: "create_agent",
          preview: previewAgent({
            name: payload.name,
            avatar: (payload.avatar || payload.name.slice(0, 2)).toUpperCase(),
            color: payload.color || "#34D399",
            role: payload.role,
            systemPrompt: payload.systemPrompt,
            toolkit: payload.toolkit || "chat",
            model: payload.model || "multi",
            inputs: payload.inputs || ["briefing"],
            outputs: payload.outputs || ["artefato"],
          }),
          payload,
        });

        await logOrchestratorAction({
          kind: "create_agent",
          label: `Proposta: criar agente ${payload.name}`,
          undoable: false,
        });

        return {
          ok: true,
          pending: true,
          proposalId: proposal.id,
          preview: proposal.preview,
          uiEvent: { type: "agent_proposal", proposalId: proposal.id, kind: "create_agent", preview: proposal.preview },
          message: "Mostre o card e peça Confirmar, Editar ou Cancelar.",
        };
      },
    }),

    confirmar_proposta: tool({
      description: "Confirma uma proposta pendente (criar/editar agente).",
      inputSchema: z.object({ proposalId: z.string() }),
      execute: async ({ proposalId }) => {
        const result = await confirmProposal(proposalId);
        if (!result.ok) return result;
        await logOrchestratorAction({
          kind: "create_agent",
          label: result.agent
            ? `Confirmou agente ${result.agent.name}`
            : "Confirmou proposta",
          undoable: false,
        });
        return { ...result, uiEvent: { type: "registry_refresh" } };
      },
    }),

    editar_agente: tool({
      description:
        "Altera função/prompt de agente existente. Gera diff antes/depois. Use preview=true para proposta.",
      inputSchema: z.object({
        agentId: z.string().optional(),
        agentName: z.string().optional(),
        role: z.string().optional(),
        systemPrompt: z.string().optional(),
        toolkit: toolkitEnum.optional(),
        preview: z.boolean().optional(),
        versionSummary: z.string().optional(),
      }),
      execute: async (input) => {
        const agent =
          (input.agentId && (await getRegistryAgent(input.agentId))) ||
          (input.agentName && (await findRegistryAgentByName(input.agentName)));
        if (!agent) {
          return {
            ok: false,
            error: "agent_not_found",
            suggestCreate: true,
            message: "Não encontrei esse agente. Quer que eu crie um novo?",
          };
        }

        const patch = {
          role: input.role,
          systemPrompt: input.systemPrompt,
          toolkit: input.toolkit as ToolkitPreset | undefined,
        };

        if (input.preview !== false && input.systemPrompt) {
          const proposal = await createProposal({
            kind: "update_agent",
            preview: {
              agentId: agent.id,
              name: agent.name,
              before: agent.systemPrompt.slice(0, 500),
              after: input.systemPrompt.slice(0, 500),
            },
            payload: { agentId: agent.id, patch, versionSummary: input.versionSummary },
          });
          return {
            ok: true,
            pending: true,
            proposalId: proposal.id,
            diff: `--- antes\n${agent.systemPrompt.slice(0, 800)}\n--- depois\n${input.systemPrompt.slice(0, 800)}`,
            uiEvent: {
              type: "agent_proposal",
              proposalId: proposal.id,
              kind: "update_agent",
              preview: proposal.preview,
            },
          };
        }

        const result = await updateRegistryAgent(agent.id, patch, {
          versionSummary: input.versionSummary,
        });
        if (!result) return { ok: false, error: "update_failed" };
        await logOrchestratorAction({
          kind: "update_agent",
          label: `Editou agente ${agent.name}`,
          undoable: true,
          undoPayload: {
            type: "restore_agent",
            agentId: agent.id,
            patch: { systemPrompt: result.previousPrompt, role: agent.role },
          },
        });
        return {
          ok: true,
          agent: result.agent,
          diff: result.diff,
          uiEvent: { type: "registry_refresh" },
        };
      },
    }),

    remover_agente: tool({
      description: "Arquiva ou pausa agente (não apaga histórico).",
      inputSchema: z.object({
        agentId: z.string().optional(),
        agentName: z.string().optional(),
        mode: z.enum(["archive", "pause"]).optional(),
      }),
      execute: async (input) => {
        const agent =
          (input.agentId && (await getRegistryAgent(input.agentId))) ||
          (input.agentName && (await findRegistryAgentByName(input.agentName)));
        if (!agent) return { ok: false, error: "agent_not_found" };
        const status = input.mode === "pause" ? "paused" : "archived";
        const prev = agent.status;
        await setRegistryAgentStatus(agent.id, status);
        await logOrchestratorAction({
          kind: status === "paused" ? "pause_agent" : "archive_agent",
          label: `${status === "paused" ? "Pausou" : "Arquivou"} ${agent.name}`,
          undoable: true,
          undoPayload: {
            type: "restore_agent_status",
            agentId: agent.id,
            status: prev,
          },
        });
        return { ok: true, uiEvent: { type: "registry_refresh" } };
      },
    }),

    criar_sala: tool({
      description: "Cria sala (grupo) com agentes opcionais.",
      inputSchema: z.object({
        name: z.string().min(2),
        blurb: z.string().optional(),
        memberSourceIds: z.array(z.string()).optional(),
      }),
      execute: async (input) => {
        const group = await createUserGroup({
          name: input.name,
          blurb: input.blurb,
          memberSourceIds: input.memberSourceIds,
        });
        await logOrchestratorAction({
          kind: "create_room",
          label: `Criou sala ${group.name}`,
          undoable: false,
        });
        return { ok: true, groupId: group.id, name: group.name, uiEvent: { type: "groups_refresh" } };
      },
    }),

    editar_sala: tool({
      description: "Renomeia ou altera descrição/workflow de sala custom.",
      inputSchema: z.object({
        groupId: z.string(),
        name: z.string().optional(),
        blurb: z.string().optional(),
        workflow: z.array(z.string()).optional(),
      }),
      execute: async (input) => {
        const group = await updateUserGroup(input.groupId, {
          name: input.name,
          blurb: input.blurb,
          workflow: input.workflow,
        });
        if (!group) return { ok: false, error: "group_not_found" };
        await logOrchestratorAction({
          kind: "update_room",
          label: `Editou sala ${group.name}`,
          undoable: false,
        });
        return { ok: true, group, uiEvent: { type: "groups_refresh" } };
      },
    }),

    duplicar_sala: tool({
      description: "Duplica uma sala custom.",
      inputSchema: z.object({
        groupId: z.string(),
        newName: z.string().optional(),
      }),
      execute: async ({ groupId, newName }) => {
        const copy = await duplicateUserGroup(groupId, newName);
        if (!copy) return { ok: false, error: "group_not_found" };
        return { ok: true, groupId: copy.id, uiEvent: { type: "groups_refresh" } };
      },
    }),

    arquivar_sala: tool({
      description: "Arquiva sala custom (ou remove se forceDelete).",
      inputSchema: z.object({
        groupId: z.string(),
        forceDelete: z.boolean().optional(),
      }),
      execute: async ({ groupId, forceDelete }) => {
        if (forceDelete) {
          const ok = await deleteUserGroup(groupId);
          return { ok, uiEvent: { type: "groups_refresh" } };
        }
        const ok = await archiveUserGroup(groupId);
        return { ok, uiEvent: { type: "groups_refresh" } };
      },
    }),

    adicionar_agente_a_sala: tool({
      description: "Adiciona agente à sala e opcionalmente posiciona após uma etapa.",
      inputSchema: z.object({
        groupId: z.string(),
        agentId: z.string(),
        afterMemberId: z.string().optional(),
        afterAgentName: z.string().optional(),
      }),
      execute: async (input) => {
        let afterId = input.afterMemberId;
        if (!afterId && input.afterAgentName) {
          const g = await getUserGroup(input.groupId);
          afterId = g?.members.find(
            (m) => m.name.toLowerCase() === input.afterAgentName!.toLowerCase(),
          )?.id;
        }
        const group = await insertMemberAfterInGroup(
          input.groupId,
          input.agentId,
          afterId,
        );
        if (!group) return { ok: false, error: "group_not_found" };
        await logOrchestratorAction({
          kind: "add_member",
          label: `Adicionou agente à sala ${group.name}`,
          undoable: false,
        });
        return { ok: true, group, uiEvent: { type: "groups_refresh" } };
      },
    }),

    reordenar_etapas: tool({
      description: "Reordena membros/etapas de uma sala (IDs de membro na ordem desejada).",
      inputSchema: z.object({
        groupId: z.string(),
        orderedMemberIds: z.array(z.string()).min(1),
      }),
      execute: async (input) => {
        const result = await reorderGroupMembers(input.groupId, input.orderedMemberIds);
        if (!result.ok) return result;
        await logOrchestratorAction({
          kind: "reorder_pipeline",
          label: "Reordenou pipeline da sala",
          undoable: false,
        });
        return { ...result, uiEvent: { type: "groups_refresh" } };
      },
    }),

    remover_agente_da_sala: tool({
      description: "Remove membro/etapa de sala custom.",
      inputSchema: z.object({
        groupId: z.string(),
        memberId: z.string(),
      }),
      execute: async (input) => {
        try {
          const group = await removeMemberFromGroup(input.groupId, input.memberId);
          return { ok: true, group, uiEvent: { type: "groups_refresh" } };
        } catch (e) {
          return { ok: false, error: e instanceof Error ? e.message : "error" };
        }
      },
    }),

    listar_salas: tool({
      description: "Lista salas (builtins + custom).",
      inputSchema: z.object({}),
      execute: async () => ({ ok: true, salas: await listSalasForOrchestrator() }),
    }),

    delegar_tarefa: legacy.delegate_to_specialist,

    consultar_status: tool({
      description: "Status do pipeline CRM, fila e execuções recentes de agentes.",
      inputSchema: z.object({}),
      execute: async () => {
        const { getStats, listPublishQueue, seedDemoIfEmpty } = await import(
          "../content/store"
        );
        await seedDemoIfEmpty();
        const [stats, queue] = await Promise.all([
          getStats(),
          listPublishQueue(),
        ]);
        const runs = await listAgentExecutions(10);
        const agents = await listRegistryAgents({ status: "active" });
        return {
          ok: true,
          stats,
          queueLength: queue.length,
          recentRuns: runs,
          activeAgents: agents.length,
        };
      },
    }),

    agendar_post: tool({
      description: "Agenda publicação de item do pipeline (wrapper Central).",
      inputSchema: z.object({
        contentItemId: z.string(),
        network: z.string(),
        scheduledAt: z.string().optional(),
      }),
      execute: async (input) => ({
        ok: true,
        scheduled: input,
        note: "Use schedule_content_publish na Central se precisar persistir agora.",
      }),
    }),

    publicar_post: tool({
      description: "Marca item pronto para publicação imediata (wrapper).",
      inputSchema: z.object({
        contentItemId: z.string(),
        network: z.string(),
      }),
      execute: async (input) => ({
        ok: true,
        publish: input,
        note: "Confirme aprovação do usuário em modo manual.",
      }),
    }),

    desfazer: tool({
      description: "Desfaz a última alteração registrada pelo orquestrador.",
      inputSchema: z.object({}),
      execute: async () => {
        const result = await undoLastOrchestratorAction();
        return { ...result, uiEvent: { type: "registry_refresh" } };
      },
    }),

    log_acoes_orquestrador: tool({
      description: "Retorna log ao vivo das ações recentes do orquestrador.",
      inputSchema: z.object({ limit: z.number().optional() }),
      execute: async ({ limit = 15 }) => ({
        ok: true,
        actions: await listOrchestratorActions(limit),
        uiEvent: { type: "action_log", actions: await listOrchestratorActions(limit) },
      }),
    }),

    registrar_execucao_agente: tool({
      description: "Registra entrada/saída/tempo/custo de execução de um agente.",
      inputSchema: z.object({
        agentId: z.string(),
        agentName: z.string(),
        inputSummary: z.string(),
        outputSummary: z.string(),
        durationMs: z.number(),
        costEstimateUsd: z.number().optional(),
      }),
      execute: async (input) => {
        const row = await recordAgentExecution(input);
        return { ok: true, runId: row.id };
      },
    }),
  };
}
