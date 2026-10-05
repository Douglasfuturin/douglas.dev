import {
  convertToModelMessages,
  stepCountIs,
  streamText,
  type UIMessage,
} from "ai";
import type { AgentMode, ResearchDepth } from "@/lib/agents/models";
import { resolveAgent } from "@/lib/agents/orchestrator";
import { getXaiApiKeyStatus } from "@/lib/agents/xai-key";
import type { VideoEditOptions } from "@/lib/video/options";

export const maxDuration = 300;

type ChatRequestBody = {
  messages: UIMessage[];
  mode?: AgentMode;
  researchDepth?: ResearchDepth;
  videoOptions?: Partial<VideoEditOptions>;
  kitId?: string;
  groupId?: string;
  memberId?: string;
  customAgentId?: string;
};

export async function POST(req: Request) {
  const keyStatus = getXaiApiKeyStatus();
  if (!keyStatus.ok) {
    return Response.json({ error: keyStatus.error }, { status: 500 });
  }

  const body = (await req.json()) as ChatRequestBody;
  const messages = body.messages ?? [];
  const mode = body.mode ?? "auto";
  const researchDepth = body.researchDepth ?? "medium";
  const videoOptions = body.videoOptions;
  const kitId = body.kitId;
  const groupId = body.groupId;
  const memberId = body.memberId;
  const customAgentId = body.customAgentId;

  try {
    const agent = await resolveAgent(messages, {
      mode,
      researchDepth,
      videoOptions,
      kitId,
      groupId,
      memberId,
      customAgentId,
    });
    const modelMessages = await convertToModelMessages(messages);

    const result = streamText({
      model: agent.model,
      instructions: agent.instructions,
      messages: modelMessages,
      tools: agent.tools as Parameters<typeof streamText>[0]["tools"],
      providerOptions: agent.providerOptions,
      stopWhen:
        agent.mode === "video" ||
        agent.mode === "kits" ||
        agent.mode === "radar" ||
        agent.mode === "pipeline" ||
        agent.mode === "central" ||
        agent.mode === "orquestrador" ||
        agent.mode === "github" ||
        agent.mode === "custom" ||
        agent.mode === "grupo" ||
        agent.mode === "editor-reels"
          ? stepCountIs(12)
          : stepCountIs(8),
    });

    return result.toUIMessageStreamResponse({
      headers: {
        "X-Agent-Mode": agent.mode,
      },
    });
  } catch (err) {
    const message =
      err instanceof Error ? err.message : "Falha ao iniciar o agente";
    return Response.json({ error: message }, { status: 500 });
  }
}
