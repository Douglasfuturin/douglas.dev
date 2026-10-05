import { listSourceZips } from "@/lib/kits/discover";
import { installAllSourceZips, installKitFromZip } from "@/lib/kits/install";

export const maxDuration = 300;
export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const body = (await req.json().catch(() => ({}))) as {
    zipPath?: string;
    all?: boolean;
  };

  if (body.all || !body.zipPath) {
    const zips = await listSourceZips();
    if (!zips.length) {
      return Response.json(
        {
          ok: false,
          error:
            "Nenhum ZIP em ninja-kits/sources nem na inbox de uploads. Envie os ZIPs de F:\\NINJA CURSOS.",
        },
        { status: 404 },
      );
    }
    const result = await installAllSourceZips(zips.map((z) => z.path));
    return Response.json({ ok: true, scanned: zips.length, ...result });
  }

  const result = await installKitFromZip(body.zipPath);
  return Response.json(result, { status: result.ok ? 200 : 400 });
}
