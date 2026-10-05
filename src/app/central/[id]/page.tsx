import Link from "next/link";
import { CrmShell } from "@/components/crm/crm-shell";
import { ContentDetail } from "@/components/content-detail";

export default async function ContentItemPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <CrmShell
      title="Conteúdo"
      subtitle="Detalhe do item no pipeline CRM."
      actions={
        <Link href="/central" className="crm-btn crm-btn-ghost">
          ← Pipeline
        </Link>
      }
    >
      <ContentDetail id={id} />
    </CrmShell>
  );
}
