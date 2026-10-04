import { catalogSummary, listInstalledKits, listSourceZips } from "@/lib/kits/discover";
import { installKitFromZip } from "@/lib/kits/install";

export const dynamic = "force-dynamic";

export async function GET() {
  // Auto-seed: se não há kits instalados mas há ZIPs na fila, instala o primeiro.
  const installed = await listInstalledKits();
  if (!installed.length) {
    const zips = await listSourceZips();
    if (zips[0]) {
      await installKitFromZip(zips[0].path).catch(() => undefined);
    }
  }
  const catalog = await catalogSummary();
  return Response.json(catalog);
}
