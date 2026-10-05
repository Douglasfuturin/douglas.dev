import type { RegistryAgent } from "./types";
import { createCustomAgent, getCustomAgent, updateCustomAgent } from "../custom-store";

/** Mantém store.json alinhado para rotas /api/agents e mode=custom legado. */
export async function syncCustomStoreFromRegistry(agent: RegistryAgent) {
  if (agent.runtimeMode && agent.runtimeMode !== "custom" && agent.seedKey) {
    return;
  }
  const existing = await getCustomAgent(agent.id);
  if (existing) {
    await updateCustomAgent(agent.id, {
      name: agent.name,
      role: agent.role,
      instructions: agent.systemPrompt,
      toolkit: agent.toolkit,
      color: agent.color,
      avatar: agent.avatar,
    });
    return;
  }
  await createCustomAgent({
    id: agent.id,
    name: agent.name,
    role: agent.role,
    instructions: agent.systemPrompt,
    toolkit: agent.toolkit,
    color: agent.color,
    avatar: agent.avatar,
  });
}
