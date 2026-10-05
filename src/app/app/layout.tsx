import type { ReactNode } from "react";
import { GrokShell } from "@/components/grok/grok-shell";

export default function AppHubLayout({ children }: { children: ReactNode }) {
  return <GrokShell>{children}</GrokShell>;
}
