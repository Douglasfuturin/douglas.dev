import { getKitById } from "@/lib/kits/discover";

export const dynamic = "force-dynamic";

export async function GET(
  _req: Request,
  ctx: { params: Promise<{ id: string }> },
) {
  const { id } = await ctx.params;
  const kit = await getKitById(id);
  if (!kit) {
    return Response.json({ error: "Kit não encontrado" }, { status: 404 });
  }
  return Response.json({ kit });
}
