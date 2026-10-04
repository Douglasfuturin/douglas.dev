export type KitKind =
  | "video"
  | "skill"
  | "automation"
  | "design"
  | "course"
  | "unknown";

export type KitHelper = {
  name: string;
  path: string;
  /** true se parece CLI python com --help */
  runnable: boolean;
};

export type NinjaKit = {
  id: string;
  name: string;
  description: string;
  kind: KitKind;
  sourceZip?: string;
  installPath: string;
  skillPath?: string;
  skillBody?: string;
  helpers: KitHelper[];
  hasPythonVenv: boolean;
  hasPreferences: boolean;
  assets: string[];
  status: "installed" | "source-only" | "seeded";
  tags: string[]; // kind + flags livres (helpers, skill, python…)
};

export type KitSourceZip = {
  filename: string;
  path: string;
  size: number;
  mtimeMs: number;
  installedId?: string;
};
