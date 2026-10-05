#!/usr/bin/env node
/**
 * Turbopack panics when it resolves kit-edicao-video/skill/.venv/bin/python
 * (symlink → /usr/bin/...). Hide the venv for the duration of `next build`.
 */
import { spawnSync } from "node:child_process";
import { existsSync, renameSync } from "node:fs";
import path from "node:path";

const root = process.cwd();
const venv = path.join(root, "kit-edicao-video", "skill", ".venv");
const hidden = path.join(root, "kit-edicao-video", "skill", ".venv.__build_hidden__");
const args = process.argv.slice(2);

let moved = false;
if (existsSync(venv) && !existsSync(hidden)) {
  renameSync(venv, hidden);
  moved = true;
}

const result = spawnSync("npx", ["next", ...args], {
  stdio: "inherit",
  env: process.env,
  shell: false,
});

if (moved && existsSync(hidden)) {
  renameSync(hidden, venv);
}

process.exit(result.status ?? 1);
