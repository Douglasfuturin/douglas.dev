import { Suspense } from "react";
import { EditorApp } from "@/components/editor/editor-app";

export default function EditorPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center text-white/50">
          Carregando editor…
        </div>
      }
    >
      <EditorApp />
    </Suspense>
  );
}
