import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "EDVD — Editor visual Grokish",
  description: "Editor de vídeo em tempo real com timeline, waveform e agente.",
};

export default function EditorLayout({ children }: LayoutProps<"/editor">) {
  return (
    <div className="editor-root min-h-screen bg-[#0b0d10] text-[#f3f5f7]">
      {children}
    </div>
  );
}
