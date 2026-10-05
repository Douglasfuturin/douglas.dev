import { generateText, type UIMessage } from "ai";
import {
  chatModel,
  multiAgentModel,
  type AgentMode,
  type ResearchDepth,
} from "./models";
import {
  GROK_PERSONA,
  GITHUB_SCOUT_PERSONA,
  KITS_PERSONA,
  NOTION_AGENT_PERSONA,
  PIPELINE_PERSONA,
  RESEARCH_PERSONA,
  ROTEIRISTA_PERSONA,
  ROUTER_PROMPT,
  VIDEO_EDITOR_PERSONA,
} from "./prompts";
import { grokBotTools, researchTools } from "./tools";
import { githubScoutTools } from "./github-tools";
import { reelsScriptTools } from "./reels-tools";
import { notionRepoTools } from "./notion-tools";
import { pipelineTools } from "./pipeline-tools";
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

type ConcreteMode = Exclude<AgentMode, "auto">;

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
    const installed = input.kitId ? await getKitById(input.kitId) : null;
    const instructions = input.kitId
      ? kitPersona(input.kitId, installed?.skillBody, installed?.name)
      : KITS_PERSONA;

    const tools: Record<string, unknown> = {
      ...ninjaKitTools(),
      ...grokBotTools(),
    };

    if (installed?.kind === "video" || input.kitId === "editar-video") {
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

Active kitId: ${input.kitId || "(none — list/install first)"}
Installed ZIP/SKILL: ${installed ? "yes" : "no — still deliver the kit's job with tools"}
`,
      tools,
    };
  }

  if (mode === "github") {
    return {
      mode,
      model: chatModel,
      instructions: GITHUB_SCOUT_PERSONA,
      tools: {
        ...githubScoutTools(),
        ...grokBotTools(),
      },
    };
  }

  if (mode === "roteiro") {
    return {
      mode,
      model: chatModel,
      instructions: ROTEIRISTA_PERSONA,
      tools: {
        ...reelsScriptTools(),
        ...githubScoutTools(),
        ...grokBotTools(),
      },
    };
  }

  if (mode === "notion") {
    return {
      mode,
      model: chatModel,
      instructions: NOTION_AGENT_PERSONA,
      tools: {
        ...notionRepoTools(),
        ...githubScoutTools(),
        ...grokBotTools(),
      },
    };
  }

  if (mode === "pipeline") {
    return {
      mode,
      model: chatModel,
      instructions: PIPELINE_PERSONA,
      tools: {
        ...pipelineTools(),
        ...githubScoutTools(),
        ...reelsScriptTools(),
        ...notionRepoTools(),
        ...grokBotTools(),
      },
    };
  }

  return {
    mode: "chat",
    model: chatModel,
    instructions: `${GROK_PERSONA}

You can also inventory Ninja kits with list_ninja_kits when the user mentions kits/ZIPs/cursos.
For GitHub repo discovery, prefer mode github / search_best_github_repos.
For Reels scripts about a repo, prefer mode roteiro.
For Notion repo guides, prefer mode notion.
For the full Scout → Roteiro → Notion pack, prefer mode pipeline / run_repo_content_pack.`,
    tools: {
      ...grokBotTools(),
      ...ninjaKitTools(),
      ...githubScoutTools(),
      ...reelsScriptTools(),
      ...notionRepoTools(),
      ...pipelineTools(),
    },
  };
}

async function routeMode(latestUserText: string): Promise<ConcreteMode> {
  if (!latestUserText) return "chat";
  if (heuristicKits(latestUserText)) return "kits";
  if (heuristicPipeline(latestUserText)) return "pipeline";
  if (heuristicRoteiro(latestUserText)) return "roteiro";
  if (heuristicNotion(latestUserText)) return "notion";
  if (heuristicGithub(latestUserText)) return "github";
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
    if (parsed.mode === "github") return "github";
    if (parsed.mode === "roteiro") return "roteiro";
    if (parsed.mode === "notion") return "notion";
    if (parsed.mode === "pipeline") return "pipeline";
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

function heuristicPipeline(text: string): boolean {
  return /\b(pipeline|content\s*pack|pacote\s+completo|scout\s*\+\s*roteiro|roteiro\s+e\s+notion|tudo\s+(junto|de\s+uma\s+vez)|gera(r)?\s+(o\s+)?pack|encade(ia|ar))\b/i.test(
    text,
  );
}

function heuristicRoteiro(text: string): boolean {
  return /\b(roteirista|roteiro|script\s+(de\s+)?(reels?|shorts?)|reels?\s+de\s+60|60\s*segundos?\s+(sobre|falando)|gancho\s+do\s+reels?)\b/i.test(
    text,
  );
}

function heuristicNotion(text: string): boolean {
  return /\b(notion|publique?\s+no\s+notion|guia\s+no\s+notion|p[aá]gina\s+no\s+notion|disponibiliz(a|ar)\s+(no\s+)?notion)\b/i.test(
    text,
  );
}

function heuristicGithub(text: string): boolean {
  return /\b(github|reposit[oó]rios?|repos?\b|open[\s-]?source|melhor(es)?\s+(libs?|bibliotecas?|projetos?)|trending|stars?\b)\b/i.test(
    text,
  );
}

function heuristicVideo(text: string): boolean {
  return /\b(edita|editar|edi[cç][aã]o|v[ií]deo|legenda|legendas|fabrica|transcreve|transcrever|aula-ccnp|sil[eê]ncio|mp4|b-?roll|vsl|render(izar)?\s+(o\s+)?(v[ií]deo|mp4))\b/i.test(
    text,
  );
}

function heuristicRoute(text: string): ConcreteMode {
  if (heuristicKits(text)) return "kits";
  if (heuristicPipeline(text)) return "pipeline";
  if (heuristicRoteiro(text)) return "roteiro";
  if (heuristicNotion(text)) return "notion";
  if (heuristicGithub(text)) return "github";
  if (heuristicVideo(text)) return "video";
  const researchSignals =
    /\b(pesquisa|pesquise|research|compare|comparar|fontes|cita|deep dive|investiga|o que est[aã]o dizendo|latest|mais recentes|tend[eê]ncias)\b/i;
  return researchSignals.test(text) ? "research" : "chat";
}
