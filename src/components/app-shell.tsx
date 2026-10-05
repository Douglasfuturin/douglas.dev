"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

const NAV = [
  { href: "/central", label: "Central" },
  { href: "/studio", label: "Studio" },
  { href: "/grupos", label: "Grupos" },
  { href: "/radar", label: "Radar" },
  { href: "/editor", label: "Editor" },
  { href: "/kits", label: "Kits" },
] as const;

export function AppShell({
  children,
  bare = false,
}: {
  children: ReactNode;
  bare?: boolean;
}) {
  const pathname = usePathname();

  if (bare) return <>{children}</>;

  return (
    <div className="flex min-h-screen flex-col fase-shell">
      <header className="sticky top-0 z-40 border-b border-[color:var(--fase-line)] bg-[color:var(--fase-panel)]/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
          <Link href="/" className="group flex items-baseline gap-2">
            <span className="font-display text-xl font-extrabold tracking-tight text-[color:var(--fase-ink)]">
              FASE
            </span>
            <span className="hidden text-[11px] uppercase tracking-[0.2em] text-[color:var(--fase-muted)] sm:inline">
              conteúdo
            </span>
          </Link>

          <nav className="flex flex-wrap items-center gap-1 sm:gap-2">
            {NAV.map((item) => {
              const active =
                pathname === item.href ||
                pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`rounded-lg px-2.5 py-1.5 text-xs font-semibold transition sm:text-sm ${
                    active
                      ? "bg-[color:var(--fase-accent)] text-[color:var(--fase-accent-ink)]"
                      : "text-[color:var(--fase-muted)] hover:bg-black/5 hover:text-[color:var(--fase-ink)]"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <Link
            href="/studio?mode=central"
            className="hidden rounded-lg border border-[color:var(--fase-ink)]/15 bg-[color:var(--fase-ink)] px-3 py-1.5 text-xs font-semibold text-white sm:inline-flex"
          >
            Operar com IA
          </Link>
        </div>
      </header>
      <div className="flex min-h-0 flex-1 flex-col">{children}</div>
    </div>
  );
}
