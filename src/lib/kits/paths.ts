import path from "node:path";

/** Escopo estático sob ninja-kits/ para o Turbopack não rastrear o repo inteiro. */
export const KITS_ROOT = path.join(process.cwd(), "ninja-kits");
export const KITS_SOURCES = path.join(process.cwd(), "ninja-kits", "sources");
export const KITS_INSTALLED = path.join(
  process.cwd(),
  "ninja-kits",
  "installed",
);

/** Inbox de uploads do Cursor (ZIPs anexados na conversa). */
export const CURSOR_UPLOADS = path.join(
  process.env.HOME || "/home/ubuntu",
  ".cursor",
  "projects",
  "workspace",
  "uploads",
);
