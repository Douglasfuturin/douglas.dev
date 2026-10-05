import Link from "next/link";
import { CrmShell } from "@/components/crm/crm-shell";
import { AgentsManager } from "@/components/crm/agents-manager";

export default function AgentesPage() {
  return (
    <CrmShell
      title="Criar agente"
      subtitle="Monte agentes personalizados com toolkit, persona e instruções."
      actions={
        <>
          <Link href="/studio?mode=custom" className="crm-btn crm-btn-primary">
            Abrir Studio
          </Link>
          <Link href="/grupos" className="crm-btn crm-btn-ghost">
            Salas prontas
          </Link>
        </>
      }
    >
      <AgentsManager />
    </CrmShell>
  );
}
