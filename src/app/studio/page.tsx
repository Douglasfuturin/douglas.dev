import { CrmShell } from "@/components/crm/crm-shell";
import { ChatApp } from "@/components/chat-app";

export default function StudioPage() {
  return (
    <CrmShell
      title="Studio IA"
      subtitle="Motor de agentes FASE — Central, grupos, radar, roteiro, artes e edição."
    >
      <div className="crm-panel !p-0 overflow-hidden min-h-[70vh]">
        <ChatApp />
      </div>
    </CrmShell>
  );
}
