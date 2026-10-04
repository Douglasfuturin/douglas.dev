import path from "node:path";

export const ROOT = process.cwd();
export const KIT_DIR = path.join(ROOT, "kit-edicao-video", "skill");
export const HELPERS_DIR = path.join(KIT_DIR, "helpers");
export const KIT_PYTHON = path.join(KIT_DIR, ".venv", "bin", "python");
export const UPLOADS_DIR = path.join(ROOT, "workspace", "videos");
export const EDITS_DIR = path.join(ROOT, "workspace", "edits");
export const OUTPUTS_DIR = path.join(ROOT, "public", "outputs");
export const PREFERENCES_PATH = path.join(KIT_DIR, "preferences.md");
