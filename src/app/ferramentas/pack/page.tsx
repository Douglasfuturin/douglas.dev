import { CrmShell } from "@/components/crm/crm-shell";
import { NexusPackWorkspace } from "@/components/nexus/nexus-pack-workspace";

export default function FerramentasPackPage() {
  return (
    <CrmShell hideHeader>
      <NexusPackWorkspace />
    </CrmShell>
  );
}
