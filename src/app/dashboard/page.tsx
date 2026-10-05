import { CrmShell } from "@/components/crm/crm-shell";
import { CrmDashboard } from "@/components/crm/dashboard";

export default function DashboardPage() {
  return (
    <CrmShell
      title="Dashboard"
      subtitle="Visão geral do CRM FASE — pipeline, agentes e módulos."
      actions={
        <>
          <a href="/studio?mode=central" className="crm-btn crm-btn-primary">
            Operar com IA
          </a>
          <a href="/central" className="crm-btn crm-btn-dark">
            Pipeline
          </a>
        </>
      }
    >
      <CrmDashboard />
    </CrmShell>
  );
}
