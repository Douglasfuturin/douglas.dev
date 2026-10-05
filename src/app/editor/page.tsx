import { Suspense } from "react";
import { AppShell } from "@/components/app-shell";
import { EditorApp } from "@/components/editor/editor-app";

export default function EditorPage() {
  return (
    <AppShell>
      <Suspense
        fallback={
          <div className="flex min-h-[60vh] items-center justify-center text-[color:var(--fase-muted)]">
            Carregando editor…
          </div>
        }
      >
        <EditorApp />
      </Suspense>
    </AppShell>
  );
}
