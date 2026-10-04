import { catalogSummary } from "@/lib/kits/discover";

export const dynamic = "force-dynamic";

export async function GET() {
  const catalog = await catalogSummary();
  return Response.json(catalog);
}
