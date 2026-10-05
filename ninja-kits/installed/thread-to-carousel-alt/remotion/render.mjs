#!/usr/bin/env node
/**
 * Remotion Render Bridge
 *
 * Takes an edit config JSON + source recording and renders a polished
 * demo video using Remotion's programmatic API.
 *
 * Usage:
 *   node remotion/render.mjs <edit-config.json> <source-video.mp4> <output.mp4>
 *
 * The edit config defines clips, zoom keyframes, and transitions.
 * The source video is copied into remotion/public/ for Remotion to access.
 */

import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import { existsSync, copyFileSync, readFileSync, mkdirSync } from "fs";
import { resolve, dirname, basename } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const REMOTION_DIR = __dirname;

async function main() {
  const args = process.argv.slice(2);

  if (args.length < 3) {
    console.error(
      "Usage: node remotion/render.mjs <edit-config.json> <source-video.mp4> <output.mp4>"
    );
    process.exit(1);
  }

  const [configPath, sourcePath, outputPath] = args;

  // Validate inputs
  if (!existsSync(configPath)) {
    console.error(`Error: Config not found: ${configPath}`);
    process.exit(1);
  }
  if (!existsSync(sourcePath)) {
    console.error(`Error: Source video not found: ${sourcePath}`);
    process.exit(1);
  }

  // Load edit config
  const editConfig = JSON.parse(readFileSync(configPath, "utf-8"));
  console.log(
    `Loaded config: ${editConfig.clips.length} clips, ${editConfig.fps}fps, ${editConfig.width}x${editConfig.height}`
  );

  // Copy source video to remotion/public/
  const publicDir = resolve(REMOTION_DIR, "public");
  mkdirSync(publicDir, { recursive: true });
  const sourceFilename = editConfig.source || "recording.mp4";
  const destPath = resolve(publicDir, sourceFilename);
  console.log(`Copying source video to ${destPath}...`);
  copyFileSync(resolve(sourcePath), destPath);

  // Bundle the Remotion project
  console.log("Bundling Remotion project...");
  const entryPoint = resolve(REMOTION_DIR, "src", "index.ts");
  const bundleLocation = await bundle({
    entryPoint,
    publicDir,
  });
  console.log("Bundle complete.");

  // Select the composition with our config as inputProps
  const inputProps = { editConfig };
  console.log("Selecting composition...");
  const composition = await selectComposition({
    serveUrl: bundleLocation,
    id: "ScreenDemo",
    inputProps,
  });
  console.log(
    `Composition: ${composition.durationInFrames} frames @ ${composition.fps}fps (${(composition.durationInFrames / composition.fps).toFixed(1)}s)`
  );

  // Render
  const resolvedOutput = resolve(outputPath);
  console.log(`Rendering to ${resolvedOutput}...`);

  await renderMedia({
    composition,
    serveUrl: bundleLocation,
    codec: "h264",
    outputLocation: resolvedOutput,
    inputProps,
    chromiumOptions: {
      enableMultiProcessOnLinux: true,
    },
    onProgress: ({ progress }) => {
      const pct = Math.round(progress * 100);
      if (pct % 10 === 0) {
        process.stderr.write(`\r  Rendering: ${pct}%`);
      }
    },
  });

  console.log(`\nDone — saved to ${resolvedOutput}`);
}

main().catch((err) => {
  console.error("Render failed:", err.message);
  process.exit(1);
});
