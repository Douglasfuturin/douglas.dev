import { access, mkdir } from "node:fs/promises";
import { spawn } from "node:child_process";
import path from "node:path";
import { getKitById } from "./discover";

export type KitRunResult = {
  ok: boolean;
  code: number | null;
  stdout: string;
  stderr: string;
};

async function resolvePython(kitInstallPath: string): Promise<string> {
  const venv = `.${"venv"}`;
  const candidates = [
    path.join(kitInstallPath, "skill", venv, "bin", "python"),
    path.join(kitInstallPath, venv, "bin", "python"),
    "python3",
  ];
  for (const c of candidates) {
    if (c === "python3") return c;
    try {
      await access(/* turbopackIgnore: true */ c);
      return c;
    } catch {
      /* next */
    }
  }
  return "python3";
}

export async function runKitHelper(input: {
  kitId: string;
  helper: string;
  args?: string[];
  timeoutMs?: number;
}): Promise<KitRunResult & { helperPath?: string }> {
  const kit = await getKitById(input.kitId);
  if (!kit) {
    return {
      ok: false,
      code: null,
      stdout: "",
      stderr: `Kit '${input.kitId}' não encontrado.`,
    };
  }

  const helper = kit.helpers.find(
    (h) => h.name === input.helper || h.name === `${input.helper}.py`,
  );
  if (!helper) {
    return {
      ok: false,
      code: null,
      stdout: "",
      stderr: `Helper '${input.helper}' não existe neste kit. Disponíveis: ${kit.helpers
        .map((h) => h.name)
        .join(", ")}`,
    };
  }

  const python = await resolvePython(kit.installPath);
  const cwd = path.dirname(helper.path);
  await mkdir(/* turbopackIgnore: true */ cwd, { recursive: true });

  return new Promise((resolve) => {
    const child = spawn(/* turbopackIgnore: true */ python, [
      helper.path,
      ...(input.args || []),
    ], {
      cwd,
      env: process.env,
    });
    let stdout = "";
    let stderr = "";
    const timer =
      input.timeoutMs != null
        ? setTimeout(() => child.kill("SIGTERM"), input.timeoutMs)
        : null;

    child.stdout.on("data", (c: Buffer) => {
      stdout += c.toString();
    });
    child.stderr.on("data", (c: Buffer) => {
      stderr += c.toString();
    });
    child.on("close", (code) => {
      if (timer) clearTimeout(timer);
      resolve({
        ok: code === 0,
        code,
        stdout: stdout.trim(),
        stderr: stderr.trim(),
        helperPath: helper.path,
      });
    });
    child.on("error", (err) => {
      if (timer) clearTimeout(timer);
      resolve({
        ok: false,
        code: null,
        stdout,
        stderr: err.message,
        helperPath: helper.path,
      });
    });
  });
}
