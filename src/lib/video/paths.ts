import path from "node:path";

export const ROOT = process.cwd();
// Nomes montados em runtime: o Turbopack não deve seguir o symlink do Python
// nem varrer o skill/.venv no grafo de módulos.
const KIT_FOLDER = ["kit", "edicao", "video"].join("-");
const VENV = `.${"venv"}`;
export const KIT_DIR = path.join(ROOT, KIT_FOLDER, "skill");
export const HELPERS_DIR = path.join(KIT_DIR, "helpers");
export const KIT_PYTHON = path.join(KIT_DIR, VENV, "bin", "python");
export const UPLOADS_DIR = path.join(ROOT, "workspace", "videos");
export const EDITS_DIR = path.join(ROOT, "workspace", "edits");
export const OUTPUTS_DIR = path.join(ROOT, "public", "outputs");
export const PREFERENCES_PATH = path.join(KIT_DIR, "preferences.md");
