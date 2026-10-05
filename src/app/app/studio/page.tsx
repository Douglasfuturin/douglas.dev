import { redirect } from "next/navigation";

type PageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function AppStudioPage({ searchParams }: PageProps) {
  const sp = await searchParams;
  const qs = new URLSearchParams();
  for (const [key, value] of Object.entries(sp)) {
    if (typeof value === "string") qs.set(key, value);
    else if (Array.isArray(value) && value[0]) qs.set(key, value[0]);
  }
  const tail = qs.toString();
  redirect(tail ? `/ferramentas/studio?${tail}` : "/ferramentas/studio");
}
