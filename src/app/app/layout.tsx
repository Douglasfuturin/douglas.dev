import type { ReactNode } from "react";
import { NexusShell } from "@/components/nexus/nexus-shell";

export default function AppHubLayout({ children }: { children: ReactNode }) {
  return <NexusShell variant="chat">{children}</NexusShell>;
}
