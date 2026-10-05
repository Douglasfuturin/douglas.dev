import { Suspense } from "react";
import { CrmShell } from "@/components/crm/crm-shell";
import { EditorApp } from "@/components/editor/editor-app";
import { NexusToolChrome } from "@/components/nexus/nexus-tool-chrome";

export default function FerramentasEditorPage() {
  return (
    <CrmShell hideHeader>
      <NexusToolChrome toolId="editor" flush>
        <Suspense
          fallback={
            <div className="flex min-h-[50vh] items-center justify-center text-sm text-[color:var(--muted-foreground)]">
              Carregando editor…
            </div>
          }
        >
          <div className="overflow-hidden rounded-xl border border-[color:var(--border)] bg-[color:var(--card)]">
            <EditorApp />
          </div>
        </Suspense>
      </NexusToolChrome>
    </CrmShell>
  );
}
