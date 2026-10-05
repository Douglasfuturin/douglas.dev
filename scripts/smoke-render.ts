import path from "node:path";
import { access } from "node:fs/promises";
import { DEFAULT_VIDEO_OPTIONS } from "../src/lib/video/options";
import { ROOT, UPLOADS_DIR } from "../src/lib/video/paths";
import { dryRunPlan, renderPlan, writePlan } from "../src/lib/video/runner";

async function main() {
  const demo = path.join(ROOT, "workspace/videos/demo-editor.mp4");
  const slug = `e2e-${Date.now()}`;
  const { planPath, plan } = await writePlan({
    videoPath: demo,
    options: {
      ...DEFAULT_VIDEO_OPTIONS,
      estilo: "reel-mono",
      formato: "9:16",
      whisperModel: "tiny",
      autoRender: true,
      captions: false,
    },
    windows: [[0, 2.5]],
    slug,
  });
  console.log("plan", planPath, "saida", plan.saida);

  const dry = await dryRunPlan(planPath);
  console.log("dry", dry.ok);
  if (!dry.ok) {
    console.error((dry.stdout || dry.stderr).slice(-2500));
    process.exit(1);
  }

  console.log("rendering short clip…");
  const r = await renderPlan(planPath);
  console.log("render", r.ok);
  console.log((r.stdout || r.stderr).slice(-2000));
  if (!r.ok) process.exit(1);

  const expected = path.join(UPLOADS_DIR, "reels", `${slug}.mp4`);
  try {
    await access(expected);
    console.log("✓ deliverable", expected);
  } catch {
    console.error("✗ missing", expected);
    process.exit(1);
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
