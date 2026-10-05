import { getXaiApiKeyStatus } from "@/lib/agents/xai-key";
import { kitPythonReady } from "@/lib/video/runner";

export async function GET() {
  const xai = getXaiApiKeyStatus();
  const videoKit = await kitPythonReady();
  return Response.json({
    ok: xai.ok && videoKit,
    xai: { ok: xai.ok, error: xai.error ?? null },
    videoKit: { ok: videoKit },
  });
}
