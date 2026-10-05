import { listCatalogAgents } from "../src/lib/agents/agent-catalog";
import { listAllResolvedGroups } from "../src/lib/agents/group-resolve";

export async function list_delegatable() {
  const catalog = listCatalogAgents().filter((a) => a.id !== "orquestrador");
  if (!catalog.length) {
    throw new Error("catalog empty");
  }
  console.log(`✓ list_delegatable_agents (${catalog.length} catalog)`);

  const groups = await listAllResolvedGroups();
  if (!groups.some((g) => g.id === "conteudo-dev")) {
    throw new Error("list_agent_groups missing conteudo-dev");
  }
  console.log(`✓ list_agent_groups (${groups.length} groups)`);
}
