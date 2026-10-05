import { generateText, type UIMessage } from "ai";
import {
  chatModel,
  multiAgentModel,
  type AgentMode,
  type ResearchDepth,
} from "./models";
import {
  ARTE_REALISTA_PERSONA,
  ARTE_TWITTER_PERSONA,
  BIT_PERSONA,
  CAPAS_ES_PERSONA,
  CARROSSEL_ES_PERSONA,
  CENTRAL_PERSONA,
  EDITOR_REELS_PERSONA,
  GROK_PERSONA,
  GITHUB_SCOUT_PERSONA,
  groupConductorPersona,
  KITS_PERSONA,
  NOTION_AGENT_PERSONA,
  PIPELINE_PERSONA,
  RADAR_PERSONA,
  RESEARCH_PERSONA,
  ROTEIRISTA_PERSONA,
  ROTEIRISTA_PESSOAL_PERSONA,
  ROUTER_PROMPT,
  VIDEO_EDITOR_PERSONA,
  YOUTUBE_ES_PERSONA,
} from "./prompts";
import { grokBotTools, researchTools } from "./tools";
import { githubScoutTools } from "./github-tools";
import { reelsScriptTools } from "./reels-tools";
import { notionRepoTools } from "./notion-tools";
import { pipelineTools } from "./pipeline-tools";
import { radarTools } from "./radar-tools";
import { artDirectorTools, bitCoordinatorTools } from "./art-tools";
import { spainContentTools } from "./spain-tools";
import { videoEditorTools } from "./video-tools";
import { centralContentTools } from "./central-tools";
import { kitPersona, ninjaKitTools } from "./kit-tools";
import { getKitById } from "@/lib/kits/discover";
import {
  getAgentGroup,
  getGroupMember,
  type AgentGroupId,
  type MemberMode,
} from "./groups";
import {
  DEFAULT_VIDEO_OPTIONS,
  type VideoEditOptions,
} from "@/lib/video/options";

export type OrchestratorInput = {
  mode: AgentMode;
  researchDepth?: ResearchDepth;
  videoOptions?: Partial<VideoEditOptions>;
  kitId?: string;
  groupId?: string;
  memberId?: string;
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

function memberModeToAgentMode(mode: MemberMode): ConcreteMode {
  if (mode === "video") return "video";
  return mode;
}

function toolsForMemberMode(
  mode: MemberMode,
  videoOptions: VideoEditOptions,
): Record<string, unknown> {
  switch (mode) {
    case "radar":
      return { ...radarTools(), ...researchTools(), ...grokBotTools() };
    case "roteiro":
    case "roteiro-pessoal":
      return {
        ...reelsScriptTools(),
        ...centralContentTools(),
        ...githubScoutTools(),
        ...grokBotTools(),
      };
    case "arte-twitter":
      return {
        ...artDirectorTools("twitter"),
        ...grokBotTools(),
      };
    case "arte-realista":
      return {
        ...artDirectorTools("realista"),
        ...grokBotTools(),
      };
    case "bit":
      return {
        ...bitCoordinatorTools(),
        ...radarTools(),
        ...reelsScriptTools(),
        ...githubScoutTools(),
        ...grokBotTools(),
      };
    case "editor-reels":
      return {
        ...videoEditorTools({
          ...videoOptions,
          estilo: "reel-camera",
          formato: "9:16",
        }),
        ...ninjaKitTools(),
      };
    case "video":
      return {
        ...videoEditorTools(videoOptions),
        ...ninjaKitTools(),
        ...grokBotTools(),
      };
    case "github":
      return { ...githubScoutTools(), ...grokBotTools() };
    case "youtube":
      return {
        ...spainContentTools(),
        ...ninjaKitTools(),
        ...reelsScriptTools(),
        ...grokBotTools(),
      };
    case "carrossel":
      return {
        ...spainContentTools(),
        ...ninjaKitTools(),
        ...artDirectorTools("twitter"),
        ...grokBotTools(),
      };
    case "capas":
      return {
        ...spainContentTools(),
        ...ninjaKitTools(),
        ...artDirectorTools("realista"),
        ...grokBotTools(),
      };
    default:
      return { ...grokBotTools() };
  }
}

function personaForMemberMode(mode: MemberMode, videoOptions: VideoEditOptions): string {
  switch (mode) {
    case "radar":
      return RADAR_PERSONA;
    case "roteiro":
      return ROTEIRISTA_PERSONA;
    case "roteiro-pessoal":
      return ROTEIRISTA_PESSOAL_PERSONA;
    case "arte-twitter":
      return ARTE_TWITTER_PERSONA;
    case "arte-realista":
      return ARTE_REALISTA_PERSONA;
    case "bit":
      return BIT_PERSONA;
    case "editor-reels":
      return EDITOR_REELS_PERSONA;
    case "video":
      return `${VIDEO_EDITOR_PERSONA}

Current UI editor options (JSON):
${JSON.stringify(videoOptions, null, 2)}
`;
    case "github":
      return `${GITHUB_SCOUT_PERSONA}

Você também atua como Radar GitHub no grupo Conteúdo Dev Vídeo.`;
    case "youtube":
      return YOUTUBE_ES_PERSONA;
    case "carrossel":
      return CARROSSEL_ES_PERSONA;
    case "capas":
      return CAPAS_ES_PERSONA;
    default:
      return GROK_PERSONA;
  }
}

function toolsForGroup(groupId: AgentGroupId, videoOptions: VideoEditOptions) {
  const group = getAgentGroup(groupId);
  const tools: Record<string, unknown> = { ...bitCoordinatorTools() };
  if (!group) return tools;
  for (const member of group.members) {
    Object.assign(tools, toolsForMemberMode(member.mode, videoOptions));
  }
  return tools;
}

export async function resolveAgent(
  messages: UIMessage[],
  input: Pick<
    OrchestratorInput,
    "mode" | "researchDepth" | "videoOptions" | "kitId" | "groupId" | "memberId"
  >,
): Promise<ResolvedAgent> {
  const latestUserText = extractLatestUserText(messages);
  const videoOptions = {
    ...DEFAULT_VIDEO_OPTIONS,
    ...input.videoOptions,
  };

  // Grupo explícito: membro específico ou sala inteira
  if (input.groupId) {
    const group = getAgentGroup(input.groupId);
    const member = getGroupMember(input.groupId, input.memberId);
    if (group && member) {
      const mode = memberModeToAgentMode(member.mode);
      const spain = group.id === "conteudos-espanha";
      const base = personaForMemberMode(member.mode, videoOptions);
      return {
        mode,
        model: chatModel,
        instructions: `${base}

${spain ? "Trabajas en el grupo Contenidos España. Responde en español de España." : `Você está no grupo "${group.name}" como **${member.name}**.`}
Papel / Rol: ${member.role}
Miembro: ${member.name}
`,
        tools: toolsForMemberMode(member.mode, videoOptions),
      };
    }
    if (group) {
      return {
        mode: "grupo",
        model: chatModel,
        instructions: groupConductorPersona(
          group.name,
          group.members.map((m) => `${m.name} — ${m.role}`),
          group.workflow,
        ),
        tools: toolsForGroup(group.id, videoOptions),
      };
    }
  }

  let mode: ConcreteMode =
    input.mode === "auto"
      ? await routeMode(latestUserText)
      : input.mode === "grupo"
        ? "grupo"
        : input.mode;

  if (mode === "grupo") {
    const guessed = /\b(españa|espanha|spain|carrusel|youtube|thumbnail|miniatura)\b/i.test(
      latestUserText,
    )
      ? "conteudos-espanha"
      : /\b(v[ií]deo|reels?|editor|github)\b/i.test(latestUserText)
        ? "conteudo-dev-video"
        : "conteudo-dev";
    const group = getAgentGroup(guessed)!;
    return {
      mode: "grupo",
      model: chatModel,
      instructions: groupConductorPersona(
        group.name,
        group.members.map((m) => `${m.name} — ${m.role}`),
        group.workflow,
      ),
      tools: toolsForGroup(group.id, videoOptions),
    };
  }

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
    return {
      mode,
      model: chatModel,
      instructions: personaForMemberMode("video", videoOptions),
      tools: toolsForMemberMode("video", videoOptions),
    };
  }

  if (mode === "editor-reels") {
    return {
      mode,
      model: chatModel,
      instructions: EDITOR_REELS_PERSONA,
      tools: toolsForMemberMode("editor-reels", videoOptions),
    };
  }

  if (mode === "youtube") {
    return {
      mode,
      model: chatModel,
      instructions: YOUTUBE_ES_PERSONA,
      tools: toolsForMemberMode("youtube", videoOptions),
    };
  }

  if (mode === "carrossel") {
    return {
      mode,
      model: chatModel,
      instructions: CARROSSEL_ES_PERSONA,
      tools: toolsForMemberMode("carrossel", videoOptions),
    };
  }

  if (mode === "capas") {
    return {
      mode,
      model: chatModel,
      instructions: CAPAS_ES_PERSONA,
      tools: toolsForMemberMode("capas", videoOptions),
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
      Object.assign(tools, videoEditorTools(videoOptions));
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
      instructions: personaForMemberMode("github", videoOptions),
      tools: toolsForMemberMode("github", videoOptions),
    };
  }

  if (mode === "roteiro") {
    return {
      mode,
      model: chatModel,
      instructions: ROTEIRISTA_PERSONA,
      tools: toolsForMemberMode("roteiro", videoOptions),
    };
  }

  if (mode === "roteiro-pessoal") {
    return {
      mode,
      model: chatModel,
      instructions: ROTEIRISTA_PESSOAL_PERSONA,
      tools: toolsForMemberMode("roteiro-pessoal", videoOptions),
    };
  }

  if (mode === "arte-twitter") {
    return {
      mode,
      model: chatModel,
      instructions: ARTE_TWITTER_PERSONA,
      tools: toolsForMemberMode("arte-twitter", videoOptions),
    };
  }

  if (mode === "arte-realista") {
    return {
      mode,
      model: chatModel,
      instructions: ARTE_REALISTA_PERSONA,
      tools: toolsForMemberMode("arte-realista", videoOptions),
    };
  }

  if (mode === "bit") {
    return {
      mode,
      model: chatModel,
      instructions: BIT_PERSONA,
      tools: toolsForMemberMode("bit", videoOptions),
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

  if (mode === "radar") {
    return {
      mode,
      model: chatModel,
      instructions: RADAR_PERSONA,
      tools: toolsForMemberMode("radar", videoOptions),
    };
  }

  if (mode === "central") {
    return {
      mode,
      model: chatModel,
      instructions: CENTRAL_PERSONA,
      tools: {
        ...centralContentTools(),
        ...radarTools(),
        ...reelsScriptTools(),
        ...artDirectorTools("twitter"),
        ...artDirectorTools("realista"),
        ...pipelineTools(),
        ...notionRepoTools(),
        ...githubScoutTools(),
        ...spainContentTools(),
        ...videoEditorTools(videoOptions),
        ...ninjaKitTools(),
        ...bitCoordinatorTools(),
        ...grokBotTools(),
      },
    };
  }

  return {
    mode: "chat",
    model: chatModel,
    instructions: `${GROK_PERSONA}

Central FASE: /central — SaaS pessoal do radar ao post.
Grupos: /grupos. Studio: /studio.
Modos: central, radar, roteiro, arte-twitter, arte-realista, bit, editor-reels, youtube, carrossel, capas, github, pipeline, notion, kits, video.`,
    tools: {
      ...grokBotTools(),
      ...centralContentTools(),
      ...ninjaKitTools(),
      ...githubScoutTools(),
      ...reelsScriptTools(),
      ...notionRepoTools(),
      ...pipelineTools(),
      ...radarTools(),
      ...artDirectorTools("twitter"),
      ...bitCoordinatorTools(),
    },
  };
}

async function routeMode(latestUserText: string): Promise<ConcreteMode> {
  if (!latestUserText) return "chat";
  if (heuristicCentral(latestUserText)) return "central";
  if (heuristicKits(latestUserText)) return "kits";
  if (heuristicGrupo(latestUserText)) return "grupo";
  if (heuristicRadar(latestUserText)) return "radar";
  if (heuristicArte(latestUserText)) {
    return /realista|foto|cinem/i.test(latestUserText)
      ? "arte-realista"
      : "arte-twitter";
  }
  if (heuristicEditorReels(latestUserText)) return "editor-reels";
  if (heuristicPipeline(latestUserText)) return "pipeline";
  if (heuristicRoteiroPessoal(latestUserText)) return "roteiro-pessoal";
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
    const allowed: ConcreteMode[] = [
      "research",
      "video",
      "kits",
      "github",
      "roteiro",
      "roteiro-pessoal",
      "notion",
      "pipeline",
      "radar",
      "arte-twitter",
      "arte-realista",
      "bit",
      "editor-reels",
      "youtube",
      "carrossel",
      "capas",
      "central",
      "grupo",
      "chat",
    ];
    if (parsed.mode && allowed.includes(parsed.mode as ConcreteMode)) {
      return parsed.mode as ConcreteMode;
    }
    return "chat";
  } catch {
    return heuristicRoute(latestUserText);
  }
}

function heuristicCentral(text: string): boolean {
  return /\b(central(\s+de)?\s+conte[uú]do|fase\b|kanban|pipeline\s+(editorial|de\s+conte[uú]do)|agenda(r)?\s+(o\s+)?post|fila\s+de\s+publica[cç][aã]o|schedule\s+post|do\s+zero\s+ao\s+post|opera[cç][oõ]es\s+de\s+conte[uú]do)\b/i.test(
    text,
  );
}

function heuristicKits(text: string): boolean {
  return /\b(ninja\s*kits?|ninja\s*cursos|instala(r)?\s*kit|list(a|ar)\s*kits?|skill\.md|f:\\\\ninja|\.zip\b.*kit|kits?\s*ninja)\b/i.test(
    text,
  );
}

function heuristicGrupo(text: string): boolean {
  return /\b(grupo\s+conte[uú]do|conte[uú]do\s+dev(\s+v[ií]deo)?|contenidos?\s+españa|conte[uú]dos?\s+espanha|sala\s+de\s+agentes|time\s+de\s+conte[uú]do)\b/i.test(
    text,
  );
}

function heuristicRadar(text: string): boolean {
  return /\b(radar(\s+de)?\s+tend[eê]ncias?|briefing\s+di[aá]rio|not[ií]cias?\s+(de\s+)?(ia|automa[cç][aã]o|marketing)|tend[eê]ncias?\s+(de\s+)?(ia|automa[cç][aã]o|marketing)|o\s+que\s+est[aá]\s+bombando)\b/i.test(
    text,
  );
}

function heuristicArte(text: string): boolean {
  return /\b(diretor\s+de\s+arte|arte\s+(twitter|realista)|capa\s+pro\s+twitter|carrossel\s+(pro\s+)?(x|twitter)|dire[cç][aã]o\s+de\s+arte)\b/i.test(
    text,
  );
}

function heuristicEditorReels(text: string): boolean {
  return /\b(editor\s+reels|reels\s+realista|edita(r)?\s+(o\s+)?reels)\b/i.test(
    text,
  );
}

function heuristicPipeline(text: string): boolean {
  return /\b(pipeline|content\s*pack|pacote\s+completo|scout\s*\+\s*roteiro|roteiro\s+e\s+notion|tudo\s+(junto|de\s+uma\s+vez)|gera(r)?\s+(o\s+)?pack|encade(ia|ar))\b/i.test(
    text,
  );
}

function heuristicRoteiroPessoal(text: string): boolean {
  return /\b(roteirista\s+pessoal|roteiro\s+pessoal|em\s+primeira\s+pessoa|tom\s+pessoal)\b/i.test(
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
  return /\b(radar\s+github|github|reposit[oó]rios?|repos?\b|open[\s-]?source|melhor(es)?\s+(libs?|bibliotecas?|projetos?)|stars?\b)\b/i.test(
    text,
  );
}

function heuristicVideo(text: string): boolean {
  return /\b(edita|editar|edi[cç][aã]o|v[ií]deo|legenda|legendas|fabrica|transcreve|transcrever|aula-ccnp|sil[eê]ncio|mp4|b-?roll|vsl|render(izar)?\s+(o\s+)?(v[ií]deo|mp4))\b/i.test(
    text,
  );
}

function heuristicRoute(text: string): ConcreteMode {
  if (heuristicCentral(text)) return "central";
  if (heuristicKits(text)) return "kits";
  if (heuristicGrupo(text)) return "grupo";
  if (heuristicRadar(text)) return "radar";
  if (heuristicArte(text)) {
    return /realista|foto|cinem/i.test(text) ? "arte-realista" : "arte-twitter";
  }
  if (heuristicEditorReels(text)) return "editor-reels";
  if (heuristicPipeline(text)) return "pipeline";
  if (heuristicRoteiroPessoal(text)) return "roteiro-pessoal";
  if (heuristicRoteiro(text)) return "roteiro";
  if (heuristicNotion(text)) return "notion";
  if (heuristicGithub(text)) return "github";
  if (heuristicVideo(text)) return "video";
  const researchSignals =
    /\b(pesquisa|pesquise|research|compare|comparar|fontes|cita|deep dive|investiga|o que est[aã]o dizendo|latest|mais recentes)\b/i;
  return researchSignals.test(text) ? "research" : "chat";
}
