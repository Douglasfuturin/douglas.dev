import path from "node:path";
import { DEFAULT_VIDEO_OPTIONS } from "../src/lib/video/options";
import {
  dryRunPlan,
  kitPythonReady,
  writePlan,
} from "../src/lib/video/runner";
import { list_delegatable } from "./smoke-orchestrator-lib";

const ROOT = process.cwd();
const demo = path.join(ROOT, "workspace/videos/demo-editor.mp4");

async function main() {
  const ok = await kitPythonReady();
  if (!ok) {
    console.error("✗ kit Python venv missing");
    process.exit(1);
  }
  console.log("✓ kitPythonReady");

  const { planPath } = await writePlan({
    videoPath: demo,
    options: { ...DEFAULT_VIDEO_OPTIONS, autoRender: false },
    slug: `smoke-${Date.now()}`,
  });
  console.log("✓ writePlan", planPath);

  const dry = await dryRunPlan(planPath);
  if (!dry.ok) {
    console.error("✗ dryRunPlan", dry.stderr.slice(-500));
    process.exit(1);
  }
  console.log("✓ dryRunPlan (fabrica --seco)");

  await list_delegatable();
  console.log("\nVideo + orchestrator smoke OK");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
