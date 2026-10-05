import Link from "next/link";
import { CrmShell } from "@/components/crm/crm-shell";
import { CentralBoard } from "@/components/central-board";

export default function CentralPage() {
  return (
    <CrmShell
      title="Pipeline"
      subtitle="Kanban editorial — ideia até postado, com fila social."
      actions={
        <>
          <Link href="/studio?mode=central" className="crm-btn crm-btn-primary">
            Operar com IA
          </Link>
          <Link href="/dashboard" className="crm-btn crm-btn-ghost">
            Dashboard
          </Link>
        </>
      }
    >
      <CentralBoard />
    </CrmShell>
  );
}
