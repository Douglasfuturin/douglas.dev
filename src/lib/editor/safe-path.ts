import path from "node:path";
import { EDITS_DIR, OUTPUTS_DIR, ROOT, UPLOADS_DIR } from "@/lib/video/paths";

const ALLOWED_ROOTS = [UPLOADS_DIR, EDITS_DIR, OUTPUTS_DIR, path.join(ROOT, "public")];

export function resolveSafeMediaPath(raw: string): string | null {
  const resolved = path.resolve(raw);
  const ok = ALLOWED_ROOTS.some(
    (root) => resolved === root || resolved.startsWith(root + path.sep),
  );
  return ok ? resolved : null;
}
