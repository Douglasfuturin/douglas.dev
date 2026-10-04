import { xai } from "@ai-sdk/xai";

/**
 * Tools server-side do Grok Bot via Responses API.
 * O modelo orquestra as chamadas no servidor da xAI — você não implementa
 * o loop de search/browse/código.
 */
export function grokBotTools() {
  return {
    web_search: xai.tools.webSearch({
      enableImageUnderstanding: true,
      enableImageSearch: true,
    }),
    x_search: xai.tools.xSearch({
      enableImageUnderstanding: true,
      enableVideoUnderstanding: true,
    }),
    code_execution: xai.tools.codeExecution(),
    image_generation: xai.tools.imageGeneration({
      action: "auto",
    }),
    view_image: xai.tools.viewImage(),
  };
}

/** Deep research: foco em evidência pública (web + X). */
export function researchTools() {
  return {
    web_search: xai.tools.webSearch({
      enableImageUnderstanding: true,
    }),
    x_search: xai.tools.xSearch({
      enableImageUnderstanding: true,
      enableVideoUnderstanding: true,
    }),
  };
}
