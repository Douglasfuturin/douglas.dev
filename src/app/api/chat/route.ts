import {
  convertToModelMessages,
  streamText,
  type UIMessage,
} from "ai";
import type { AgentMode, ResearchDepth } from "@/lib/agents/models";
import { resolveAgent } from "@/lib/agents/orchestrator";

export const maxDuration = 300;

type ChatRequestBody = {
  messages: UIMessage[];
  mode?: AgentMode;
  researchDepth?: ResearchDepth;
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

  const agent = await resolveAgent(messages, { mode, researchDepth });
  const modelMessages = await convertToModelMessages(messages);

  const result = streamText({
    model: agent.model,
    instructions: agent.instructions,
    messages: modelMessages,
    tools: agent.tools,
    providerOptions: agent.providerOptions,
  });

  return result.toUIMessageStreamResponse({
    headers: {
      "X-Agent-Mode": agent.mode,
    },
  });
}
