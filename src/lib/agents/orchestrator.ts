import { generateText, type UIMessage } from "ai";
import {
  chatModel,
  multiAgentModel,
  type AgentMode,
  type ResearchDepth,
} from "./models";
import {
  GROK_PERSONA,
  KITS_PERSONA,
  RESEARCH_PERSONA,
  ROUTER_PROMPT,
  VIDEO_EDITOR_PERSONA,
} from "./prompts";
import { grokBotTools, researchTools } from "./tools";
import { videoEditorTools } from "./video-tools";
import { kitPersona, ninjaKitTools } from "./kit-tools";
import { getKitById } from "@/lib/kits/discover";
import {
  DEFAULT_VIDEO_OPTIONS,
  type VideoEditOptions,
} from "@/lib/video/options";

export type OrchestratorInput = {
  mode: AgentMode;
  researchDepth?: ResearchDepth;
  videoOptions?: Partial<VideoEditOptions>;
  kitId?: string;
  latestUserText: string;
};

export type ResolvedAgent = {
  mode: Exclude<AgentMode, "auto">;
  model: typeof chatModel | typeof multiAgentModel;
  instructions: string;
  tools: Record<string, unknown>;
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
  input: Pick<
    OrchestratorInput,
    "mode" | "researchDepth" | "videoOptions" | "kitId"
  >,
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

  if (mode === "video") {
    const videoOptions = {
      ...DEFAULT_VIDEO_OPTIONS,
      ...input.videoOptions,
    };
    return {
      mode,
      model: chatModel,
      instructions: `${VIDEO_EDITOR_PERSONA}

Current UI editor options (JSON):
${JSON.stringify(videoOptions, null, 2)}
`,
      tools: {
        ...videoEditorTools(videoOptions),
        ...ninjaKitTools(),
      },
    };
  }

  if (mode === "kits") {
    const kit = input.kitId ? await getKitById(input.kitId) : null;
    const instructions = kit
      ? kitPersona(kit.id, kit.skillBody, kit.name)
      : KITS_PERSONA;

    const tools: Record<string, unknown> = {
      ...ninjaKitTools(),
      ...grokBotTools(),
    };

    if (kit?.kind === "video") {
      Object.assign(
        tools,
        videoEditorTools({
          ...DEFAULT_VIDEO_OPTIONS,
          ...input.videoOptions,
        }),
      );
    }

    return {
      mode,
      model: chatModel,
      instructions: `${instructions}

Active kitId: ${kit?.id || "(none — list/install first)"}
`,
      tools,
    };
  }

  return {
    mode: "chat",
    model: chatModel,
    instructions: `${GROK_PERSONA}

You can also inventory Ninja kits with list_ninja_kits when the user mentions kits/ZIPs/cursos.`,
    tools: {
      ...grokBotTools(),
      ...ninjaKitTools(),
    },
  };
}

async function routeMode(
  latestUserText: string,
): Promise<"chat" | "research" | "video" | "kits"> {
  if (!latestUserText) return "chat";
  if (heuristicKits(latestUserText)) return "kits";
  if (heuristicVideo(latestUserText)) return "video";

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
    if (parsed.mode === "research") return "research";
    if (parsed.mode === "video") return "video";
    if (parsed.mode === "kits") return "kits";
    return "chat";
  } catch {
    return heuristicRoute(latestUserText);
  }
}

function heuristicKits(text: string): boolean {
  return /\b(ninja\s*kits?|ninja\s*cursos|instala(r)?\s*kit|list(a|ar)\s*kits?|skill\.md|f:\\\\ninja|\.zip\b.*kit|kits?\s*ninja)\b/i.test(
    text,
  );
}

function heuristicVideo(text: string): boolean {
  return /\b(edita|editar|edi[cç][aã]o|v[ií]deo|reel|legenda|legendas|fabrica|transcreve|transcrever|aula-ccnp|sil[eê]ncio|mp4|b-?roll|vsl)\b/i.test(
    text,
  );
}

function heuristicRoute(text: string): "chat" | "research" | "video" | "kits" {
  if (heuristicKits(text)) return "kits";
  if (heuristicVideo(text)) return "video";
  const researchSignals =
    /\b(pesquisa|pesquise|research|compare|comparar|fontes|cita|deep dive|investiga|o que est[aã]o dizendo|latest|mais recentes|tend[eê]ncias)\b/i;
  return researchSignals.test(text) ? "research" : "chat";
}
