import { CrmShell } from "@/components/crm/crm-shell";
import { CrmDashboard } from "@/components/crm/dashboard";
import { NexusOverview } from "@/components/nexus/nexus-overview";

export default function DashboardPage() {
  return (
    <CrmShell hideHeader>
      <NexusOverview />
      <div className="mt-10">
        <CrmDashboard />
      </div>
    </CrmShell>
  );
}
