"use client";

import type { ReactNode } from "react";
import { NexusShell } from "@/components/nexus/nexus-shell";

export function CrmShell({
  children,
  title,
  subtitle,
  actions,
  hideHeader,
  bare,
}: {
  children: ReactNode;
  title?: string;
  subtitle?: string;
  actions?: ReactNode;
  hideHeader?: boolean;
  bare?: boolean;
}) {
  return (
    <NexusShell
      variant={bare ? "bare" : "app"}
      title={title}
      subtitle={subtitle}
      actions={actions}
      hideHeader={hideHeader}
    >
      {children}
    </NexusShell>
  );
}

/** Back-compat wrapper used by older pages */
export function AppShell({
  children,
  bare = false,
}: {
  children: ReactNode;
  bare?: boolean;
}) {
  return (
    <NexusShell variant={bare ? "bare" : "app"}>
      {children}
    </NexusShell>
  );
}
