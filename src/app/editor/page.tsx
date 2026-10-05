import { Suspense } from "react";
import { CrmShell } from "@/components/crm/crm-shell";
import { EditorApp } from "@/components/editor/editor-app";

export default function EditorPage() {
  return (
    <CrmShell bare>
      <Suspense
        fallback={
          <div className="flex min-h-[50vh] items-center justify-center text-[color:var(--fase-muted)]">
            Carregando editor…
          </div>
        }
      >
        <div className="overflow-hidden rounded-[1.25rem] border border-[color:var(--fase-line)]">
          <EditorApp />
        </div>
      </Suspense>
    </CrmShell>
  );
}
