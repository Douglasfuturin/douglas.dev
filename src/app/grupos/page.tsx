"use client";

import Link from "next/link";
import { CrmShell } from "@/components/crm/crm-shell";
import { GroupsManager } from "@/components/crm/groups-manager";

export default function GruposPage() {
  return (
    <CrmShell
      title="Grupos de agentes"
      subtitle="Crie times, adicione ou remova agentes. O Orquestrador conduz o fluxo."
      actions={
        <div className="flex flex-wrap gap-2">
          <Link
            href="/studio?mode=orquestrador&q=Orquestra%20todos%20os%20grupos"
            className="crm-btn crm-btn-primary"
          >
            Orquestrador Principal
          </Link>
          <Link href="/dashboard" className="crm-btn crm-btn-ghost">
            Dashboard
          </Link>
        </div>
      }
    >
      <GroupsManager />
    </CrmShell>
  );
}
