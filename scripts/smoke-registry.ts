import { listRegistryAgents } from "../src/lib/agents/registry/store";
import { listOrchestratorActions } from "../src/lib/agents/registry/actions-log";

async function main() {
  const agents = await listRegistryAgents({ status: "active" });
  if (agents.length < 7) {
    throw new Error(`expected seeded agents, got ${agents.length}`);
  }
  console.log(`✓ registry agents (${agents.length})`);
  const log = await listOrchestratorActions(5);
  console.log(`✓ orchestrator log (${log.length} entries)`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
