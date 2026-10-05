"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, type ReactNode } from "react";

const NAV = [
  { href: "/app", label: "Chat", match: ["/app"] },
  { href: "/dashboard", label: "Dashboard", match: ["/dashboard"] },
  { href: "/central", label: "Pipeline", match: ["/central"] },
  { href: "/grupos", label: "Grupos", match: ["/grupos"] },
  { href: "/agentes", label: "Agentes", match: ["/agentes"] },
  { href: "/kits", label: "Kits", match: ["/kits"] },
  { href: "/editor", label: "Editor", match: ["/editor"] },
];

function active(pathname: string, href: string, match?: string[]) {
  if (match?.some((m) => pathname === m || pathname.startsWith(`${m}/`))) {
    return true;
  }
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function GrokShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const sidebar = (
    <>
      <div className="px-3 pt-2">
        <Link href="/" className="block">
          <p className="font-display text-xl text-white">Douglas Dev</p>
          <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-white/40">
            Central de Agentes
          </p>
        </Link>
      </div>

      <div className="mt-4 px-2">
        <Link
          href="/app"
          className="grok-new-chat"
          onClick={() => setOpen(false)}
        >
          + Nova conversa
        </Link>
      </div>

      <nav className="mt-4 flex-1 space-y-0.5 overflow-y-auto px-2">
        {NAV.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            data-active={active(pathname, item.href, item.match)}
            className="grok-nav-link"
            onClick={() => setOpen(false)}
          >
            {item.label}
          </Link>
        ))}
      </nav>

      <div className="border-t border-white/10 p-3 text-[10px] text-white/35">
        Orquestrador Principal delega para Radar, Roteirista, Arte, Vídeo e agentes custom.
      </div>
    </>
  );

  return (
    <div className="grok-app">
      <aside className="grok-sidebar hidden md:flex">{sidebar}</aside>

      {open ? (
        <div
          className="fixed inset-0 z-50 bg-black/60 md:hidden"
          onClick={() => setOpen(false)}
          aria-hidden
        />
      ) : null}
      <aside
        className={`grok-sidebar fixed inset-y-0 left-0 z-50 w-[min(280px,88vw)] transition-transform md:hidden ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {sidebar}
      </aside>

      <div className="grok-main flex min-w-0 flex-1 flex-col">
        <header className="grok-topbar flex shrink-0 items-center justify-between gap-3 px-4 py-3 md:px-5">
          <button
            type="button"
            className="rounded-lg border border-white/10 px-2.5 py-1.5 text-xs font-semibold text-white/80 md:hidden"
            onClick={() => setOpen(true)}
          >
            Menu
          </button>
          <div className="min-w-0 flex-1 text-center md:text-left">
            <p className="font-display text-lg text-white">Orquestrador Principal</p>
            <p className="truncate text-[11px] text-white/45">
              Peça qualquer coisa — eu delego para os agentes certos
            </p>
          </div>
          <Link
            href="/app/studio"
            className="hidden shrink-0 rounded-full border border-white/15 px-3 py-1.5 text-[11px] font-semibold text-white/70 hover:border-white/30 sm:inline-flex"
          >
            Modo avançado
          </Link>
        </header>
        <div className="relative min-h-0 flex-1">{children}</div>
      </div>
    </div>
  );
}
