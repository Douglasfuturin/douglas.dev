import { xai } from "@ai-sdk/xai";

/** Chat agentic: tools server-side do Grok (search, code, image). */
export const chatModel = xai.responses("grok-4.7");

/**
 * Multi-agent nativo da xAI: vários agentes em paralelo para deep research.
 * Em grok-4.20-multi-agent, reasoningEffort controla a *quantidade* de agentes
 * (low/medium/high), não só a profundidade de thinking.
 */
export const multiAgentModel = xai.responses("grok-4.20-multi-agent");

export type AgentMode = "chat" | "research" | "video" | "kits" | "auto";

export type ResearchDepth = "low" | "medium" | "high";
