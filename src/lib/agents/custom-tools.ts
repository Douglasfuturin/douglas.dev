import type { VideoEditOptions } from "@/lib/video/options";
import { grokBotTools, researchTools } from "./tools";
import { githubScoutTools } from "./github-tools";
import { nicheScoutTools } from "./niche-scout-tools";
import { reelsScriptTools } from "./reels-tools";
import { radarTools } from "./radar-tools";
import { artDirectorTools, bitCoordinatorTools } from "./art-tools";
import { videoEditorTools } from "./video-tools";
import { ninjaKitTools } from "./kit-tools";
import { notionRepoTools } from "./notion-tools";
import { pipelineTools } from "./pipeline-tools";
import { spainContentTools } from "./spain-tools";
import { centralContentTools } from "./central-tools";
import type { ToolkitPreset } from "./custom-types";

export function toolsForToolkit(
  toolkit: ToolkitPreset,
  videoOptions: VideoEditOptions,
): Record<string, unknown> {
  switch (toolkit) {
    case "research":
      return researchTools();
    case "github":
      return {
        ...githubScoutTools(),
        ...nicheScoutTools(),
        ...reelsScriptTools(),
        ...centralContentTools(),
        ...grokBotTools(),
      };
    case "radar":
      return { ...radarTools(), ...researchTools(), ...grokBotTools() };
    case "roteiro":
      return {
        ...reelsScriptTools(),
        ...githubScoutTools(),
        ...nicheScoutTools(),
        ...centralContentTools(),
        ...grokBotTools(),
      };
    case "arte":
      return {
        ...artDirectorTools("twitter"),
        ...artDirectorTools("realista"),
        ...spainContentTools(),
        ...grokBotTools(),
      };
    case "video":
      return {
        ...videoEditorTools(videoOptions),
        ...ninjaKitTools(),
        ...grokBotTools(),
      };
    case "notion":
      return {
        ...notionRepoTools(),
        ...githubScoutTools(),
        ...grokBotTools(),
      };
    case "pipeline":
      return {
        ...pipelineTools(),
        ...githubScoutTools(),
        ...nicheScoutTools(),
        ...reelsScriptTools(),
        ...notionRepoTools(),
        ...grokBotTools(),
      };
    case "central":
      return {
        ...centralContentTools(),
        ...radarTools(),
        ...reelsScriptTools(),
        ...nicheScoutTools(),
        ...githubScoutTools(),
        ...bitCoordinatorTools(),
        ...grokBotTools(),
      };
    case "espanha":
      return {
        ...spainContentTools(),
        ...reelsScriptTools(),
        ...ninjaKitTools(),
        ...artDirectorTools("realista"),
        ...grokBotTools(),
      };
    case "full":
      return {
        ...grokBotTools(),
        ...centralContentTools(),
        ...nicheScoutTools(),
        ...githubScoutTools(),
        ...reelsScriptTools(),
        ...radarTools(),
        ...artDirectorTools("twitter"),
        ...artDirectorTools("realista"),
        ...videoEditorTools(videoOptions),
        ...ninjaKitTools(),
        ...notionRepoTools(),
        ...pipelineTools(),
        ...spainContentTools(),
        ...bitCoordinatorTools(),
      };
    case "chat":
    default:
      return { ...grokBotTools(), ...ninjaKitTools() };
  }
}

export function buildCustomAgentInstructions(input: {
  name: string;
  role: string;
  instructions: string;
  toolkit: ToolkitPreset;
}): string {
  return `You are **${input.name}**, a custom FASE agent.

Role: ${input.role}
Toolkit preset: ${input.toolkit}

Custom instructions from the user:
${input.instructions}

Rules:
- Follow the custom instructions above.
- Use available tools when they help; do not invent URLs, stars, or file paths.
- Prefer Portuguese (Brazil) unless the user writes in another language.
- Be concise and actionable.`;
}
