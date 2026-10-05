import { tool } from "ai";
import { z } from "zod";
import {
  advanceContent,
  createContent,
  getContent,
  getStats,
  listContent,
  queuePublish,
  updateContent,
} from "@/lib/content/store";
import { CONTENT_STAGES, NETWORKS } from "@/lib/content/types";

export function centralContentTools() {
  return {
    list_content_pipeline: tool({
      description:
        "Lista itens da Central FASE (kanban pessoal: ideia → postado). Filtra por stage ou market.",
      inputSchema: z.object({
        stage: z.enum(CONTENT_STAGES).optional(),
        market: z.enum(["br", "es", "en"]).optional(),
      }),
      execute: async ({ stage, market }) => {
        const items = await listContent({ stage, market });
        const stats = await getStats();
        return {
          ok: true,
          stats,
          count: items.length,
          items: items.map((i) => ({
            id: i.id,
            title: i.title,
            stage: i.stage,
            market: i.market,
            networks: i.networks,
            score: i.score,
            source: i.source,
            updatedAt: i.updatedAt,
          })),
        };
      },
    }),

    create_content_item: tool({
      description:
        "Cria um item na Central FASE (ideia, tendência aprovada, tema de vídeo, etc.).",
      inputSchema: z.object({
        title: z.string().min(3),
        summary: z.string().optional(),
        stage: z.enum(CONTENT_STAGES).optional(),
        market: z.enum(["br", "es", "en"]).optional(),
        networks: z.array(z.enum(NETWORKS)).optional(),
        source: z
          .enum(["radar", "github", "manual", "pipeline", "grupo", "central"])
          .optional(),
        score: z.number().min(0).max(10).optional(),
        tags: z.array(z.string()).optional(),
        topic: z.string().optional(),
        script: z.string().optional(),
        caption: z.string().optional(),
        notes: z.string().optional(),
        groupId: z.string().optional(),
      }),
      execute: async (input) => {
        const item = await createContent(input);
        return { ok: true, item };
      },
    }),

    update_content_item: tool({
      description:
        "Atualiza campos de um item (roteiro, caption, artBrief, videoPath, stage, etc.).",
      inputSchema: z.object({
        contentId: z.string(),
        title: z.string().optional(),
        summary: z.string().optional(),
        stage: z.enum(CONTENT_STAGES).optional(),
        script: z.string().optional(),
        caption: z.string().optional(),
        hashtags: z.array(z.string()).optional(),
        artBrief: z.string().optional(),
        videoPath: z.string().optional(),
        thumbnailPath: z.string().optional(),
        notionUrl: z.string().optional(),
        notes: z.string().optional(),
        score: z.number().min(0).max(10).optional(),
        networks: z.array(z.enum(NETWORKS)).optional(),
      }),
      execute: async ({ contentId, ...patch }) => {
        const item = await updateContent(contentId, patch);
        if (!item) return { ok: false, error: "content_not_found" };
        return { ok: true, item };
      },
    }),

    advance_content_stage: tool({
      description:
        "Avança o item uma etapa no pipeline (idea→approved→script→art→video→packaged→ready→scheduled→published).",
      inputSchema: z.object({
        contentId: z.string(),
      }),
      execute: async ({ contentId }) => {
        const item = await advanceContent(contentId);
        if (!item) return { ok: false, error: "content_not_found" };
        return { ok: true, item };
      },
    }),

    get_content_item: tool({
      description: "Detalhe completo de um item da Central.",
      inputSchema: z.object({ contentId: z.string() }),
      execute: async ({ contentId }) => {
        const item = await getContent(contentId);
        if (!item) return { ok: false, error: "content_not_found" };
        return { ok: true, item };
      },
    }),

    schedule_content_publish: tool({
      description:
        "Enfileira publicação do conteúdo (Instagram/YouTube/TikTok/X/LinkedIn/Notion). Marca como ready/scheduled. Sem API externa configurada, fica na fila local data/content/store.json.",
      inputSchema: z.object({
        contentId: z.string(),
        network: z.enum(NETWORKS),
        scheduledAt: z
          .string()
          .optional()
          .describe("ISO datetime futuro; omitir = fila imediata (queued)"),
        caption: z.string().optional(),
        mediaPath: z.string().optional(),
      }),
      execute: async (input) => {
        const job = await queuePublish(input);
        if (!job) return { ok: false, error: "content_not_found" };
        return {
          ok: true,
          job,
          hint: "Fila local pronta. Conecte BUFFER_ACCESS_TOKEN ou APIs Meta/YouTube/TikTok para envio automático.",
        };
      },
    }),

    run_central_pipeline: tool({
      description:
        "Cria ou atualiza um item e registra o pacote editorial completo (título, resumo, roteiro, caption, art brief, redes). Use após Radar/Roteirista/Arte para fechar a etapa na Central.",
      inputSchema: z.object({
        contentId: z.string().optional(),
        title: z.string().min(3),
        summary: z.string().optional(),
        market: z.enum(["br", "es", "en"]).optional(),
        networks: z.array(z.enum(NETWORKS)).optional(),
        source: z
          .enum(["radar", "github", "manual", "pipeline", "grupo", "central"])
          .optional(),
        score: z.number().min(0).max(10).optional(),
        tags: z.array(z.string()).optional(),
        topic: z.string().optional(),
        script: z.string().optional(),
        caption: z.string().optional(),
        hashtags: z.array(z.string()).optional(),
        artBrief: z.string().optional(),
        videoPath: z.string().optional(),
        stage: z.enum(CONTENT_STAGES).optional(),
        notes: z.string().optional(),
        groupId: z.string().optional(),
        autoAdvance: z
          .boolean()
          .optional()
          .describe("Se true, avança uma etapa após salvar"),
      }),
      execute: async (input) => {
        let item;
        if (input.contentId) {
          item = await updateContent(input.contentId, {
            title: input.title,
            summary: input.summary,
            market: input.market,
            networks: input.networks,
            source: input.source,
            score: input.score,
            tags: input.tags,
            topic: input.topic,
            script: input.script,
            caption: input.caption,
            hashtags: input.hashtags,
            artBrief: input.artBrief,
            videoPath: input.videoPath,
            stage: input.stage,
            notes: input.notes,
            groupId: input.groupId,
          });
          if (!item) return { ok: false, error: "content_not_found" };
        } else {
          item = await createContent({
            title: input.title,
            summary: input.summary,
            market: input.market,
            networks: input.networks,
            source: input.source || "central",
            score: input.score,
            tags: input.tags,
            topic: input.topic,
            script: input.script,
            caption: input.caption,
            hashtags: input.hashtags,
            artBrief: input.artBrief,
            videoPath: input.videoPath,
            stage: input.stage || (input.script ? "script" : "idea"),
            notes: input.notes,
            groupId: input.groupId,
          });
        }

        if (input.autoAdvance) {
          item = (await advanceContent(item.id)) || item;
        }

        const stats = await getStats();
        return {
          ok: true,
          item,
          stats,
          nextHint:
            item.stage === "script"
              ? "Próximo: artes/capas ou edição de vídeo"
              : item.stage === "ready"
                ? "Próximo: schedule_content_publish"
                : `Estágio atual: ${item.stage}`,
        };
      },
    }),
  };
}
