import { AppShell } from "@/components/app-shell";
import { ContentDetail } from "@/components/content-detail";

export default async function ContentItemPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <AppShell>
      <ContentDetail id={id} />
    </AppShell>
  );
}
