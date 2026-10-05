import {
  convertToModelMessages,
  stepCountIs,
  streamText,
  type UIMessage,
} from "ai";
import type { AgentMode, ResearchDepth } from "@/lib/agents/models";
import { resolveAgent } from "@/lib/agents/orchestrator";
import type { VideoEditOptions } from "@/lib/video/options";

export const maxDuration = 300;

type ChatRequestBody = {
  messages: UIMessage[];
  mode?: AgentMode;
  researchDepth?: ResearchDepth;
  videoOptions?: Partial<VideoEditOptions>;
  kitId?: string;
};

export async function POST(req: Request) {
  if (!process.env.XAI_API_KEY) {
    return Response.json(
      {
        error:
          "Missing XAI_API_KEY. Create a key at https://console.x.ai and add it to .env.local",
      },
      { status: 500 },
    );
  }

  const body = (await req.json()) as ChatRequestBody;
  const messages = body.messages ?? [];
  const mode = body.mode ?? "auto";
  const researchDepth = body.researchDepth ?? "medium";
  const videoOptions = body.videoOptions;
  const kitId = body.kitId;

  const agent = await resolveAgent(messages, {
    mode,
    researchDepth,
    videoOptions,
    kitId,
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
      agent.mode === "pipeline"
        ? stepCountIs(12)
        : stepCountIs(8),
  });

  return result.toUIMessageStreamResponse({
    headers: {
      "X-Agent-Mode": agent.mode,
    },
  });
}
