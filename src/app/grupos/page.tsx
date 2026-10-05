import { CrmShell } from "@/components/crm/crm-shell";
import { NexusOrchestrations } from "@/components/nexus/nexus-orchestrations";

export default function GruposPage() {
  return (
    <CrmShell hideHeader>
      <NexusOrchestrations />
    </CrmShell>
  );
}
