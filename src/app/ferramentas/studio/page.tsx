import { ChatApp } from "@/components/chat-app";
import { CrmShell } from "@/components/crm/crm-shell";
import { NexusToolChrome } from "@/components/nexus/nexus-tool-chrome";

export default function FerramentasStudioPage() {
  return (
    <CrmShell hideHeader>
      <NexusToolChrome toolId="studio" flush>
        <div className="nexus-studio-frame flex min-h-[70vh] flex-col overflow-hidden rounded-xl border border-[color:var(--border)] bg-[color:var(--card)]/40">
          <ChatApp variant="studio" />
        </div>
      </NexusToolChrome>
    </CrmShell>
  );
}
