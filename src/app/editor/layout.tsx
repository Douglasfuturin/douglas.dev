import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Editor vídeo — Nexus OS",
  description: "Editor de reels com timeline, waveform e render local.",
};

export default function EditorLayout({ children }: LayoutProps<"/editor">) {
  return (
    <div className="editor-root min-h-screen bg-[color:var(--background)] text-[color:var(--foreground)]">
      {children}
    </div>
  );
}
