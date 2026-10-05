import { CrmShell } from "@/components/crm/crm-shell";
import { CrmDashboard } from "@/components/crm/dashboard";
import { NexusOverview } from "@/components/nexus/nexus-overview";

export default function DashboardPage() {
  return (
    <CrmShell hideHeader>
      <NexusOverview />
      <div className="mt-10 border-t border-[color:var(--border)] pt-10">
        <h2 className="mb-2 text-lg font-semibold text-[color:var(--foreground)]">
          Pipelines por grupo
        </h2>
        <p className="mb-6 text-sm text-[color:var(--muted-foreground)]">
          Imagem e Vídeo em sequência de fluxo.
        </p>
        <CrmDashboard />
      </div>
    </CrmShell>
  );
}
