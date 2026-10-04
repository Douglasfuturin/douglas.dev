import { generateText, type UIMessage } from "ai";
import {
  chatModel,
  multiAgentModel,
  type AgentMode,
  type ResearchDepth,
} from "./models";
import { GROK_PERSONA, RESEARCH_PERSONA, ROUTER_PROMPT } from "./prompts";
import { grokBotTools, researchTools } from "./tools";

export type OrchestratorInput = {
  mode: AgentMode;
  researchDepth?: ResearchDepth;
  latestUserText: string;
};

export type ResolvedAgent = {
  mode: Exclude<AgentMode, "auto">;
  model: typeof chatModel | typeof multiAgentModel;
  instructions: string;
  tools: ReturnType<typeof grokBotTools> | ReturnType<typeof researchTools>;
  providerOptions?: {
    xai: { reasoningEffort: ResearchDepth };
  };
};

function extractLatestUserText(messages: UIMessage[]): string {
  for (let i = messages.length - 1; i >= 0; i--) {
    const message = messages[i];
    if (message.role !== "user") continue;
    const text = message.parts
      .filter((part): part is { type: "text"; text: string } => part.type === "text")
      .map((part) => part.text)
      .join("\n")
      .trim();
    if (text) return text;
  }
  return "";
}

export async function resolveAgent(
  messages: UIMessage[],
  input: Pick<OrchestratorInput, "mode" | "researchDepth">,
): Promise<ResolvedAgent> {
  const latestUserText = extractLatestUserText(messages);
  const mode =
    input.mode === "auto"
      ? await routeMode(latestUserText)
      : input.mode;

  if (mode === "research") {
    const depth = input.researchDepth ?? "medium";
    return {
      mode,
      model: multiAgentModel,
      instructions: RESEARCH_PERSONA,
      tools: researchTools(),
      providerOptions: {
        xai: { reasoningEffort: depth },
      },
    };
  }

  return {
    mode: "chat",
    model: chatModel,
    instructions: GROK_PERSONA,
    tools: grokBotTools(),
  };
}

async function routeMode(latestUserText: string): Promise<"chat" | "research"> {
  if (!latestUserText) return "chat";

  try {
    const { text } = await generateText({
      model: chatModel,
      instructions: ROUTER_PROMPT,
      prompt: latestUserText,
      temperature: 0,
    });

    const match = text.match(/\{[\s\S]*\}/);
    if (!match) return heuristicRoute(latestUserText);
    const parsed = JSON.parse(match[0]) as { mode?: string };
    return parsed.mode === "research" ? "research" : "chat";
  } catch {
    return heuristicRoute(latestUserText);
  }
}

function heuristicRoute(text: string): "chat" | "research" {
  const researchSignals =
    /\b(pesquisa|pesquise|research|compare|comparar|fontes|cita|deep dive|investiga|o que est[aã]o dizendo|latest|mais recentes|tend[eê]ncias)\b/i;
  return researchSignals.test(text) ? "research" : "chat";
}
