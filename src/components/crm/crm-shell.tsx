"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, type ReactNode } from "react";

type NavItem = {
  href: string;
  label: string;
  ico: string;
  match?: string[];
};

const PRIMARY: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", ico: "DB", match: ["/dashboard"] },
  { href: "/central", label: "Pipeline", ico: "PL", match: ["/central"] },
  { href: "/studio", label: "Studio IA", ico: "AI", match: ["/studio"] },
  { href: "/agentes", label: "Criar agente", ico: "+", match: ["/agentes"] },
  { href: "/grupos", label: "Agentes", ico: "AG", match: ["/grupos"] },
];

const MODULES: NavItem[] = [
  { href: "/github", label: "GitHub + Reels", ico: "GH" },
  { href: "/radar", label: "Radar", ico: "RD" },
  { href: "/roteiro", label: "Roteirista", ico: "RT" },
  { href: "/studio?mode=arte-realista", label: "Artes", ico: "AR" },
  { href: "/editor", label: "Editor vídeo", ico: "ED", match: ["/editor"] },
  { href: "/kits", label: "Ninja Kits", ico: "KT", match: ["/kits"] },
  { href: "/pipeline", label: "Pack Scout", ico: "PK" },
  { href: "/notion", label: "Notion", ico: "NT" },
];

function isActive(pathname: string, item: NavItem) {
  if (item.match) {
    return item.match.some(
      (m) => pathname === m || pathname.startsWith(`${m}/`),
    );
  }
  const base = item.href.split("?")[0];
  return pathname === base || pathname.startsWith(`${base}/`);
}

export function CrmShell({
  children,
  title,
  subtitle,
  actions,
}: {
  children: ReactNode;
  title?: string;
  subtitle?: string;
  actions?: ReactNode;
}) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const sidebar = (
    <>
      <div className="px-2">
        <Link href="/" className="group block">
          <p className="font-display text-2xl font-extrabold tracking-tight text-white">
            FASE
          </p>
          <p className="mt-0.5 text-[10px] font-semibold uppercase tracking-[0.22em] text-white/40">
            Content CRM
          </p>
        </Link>
      </div>

      <div className="px-1">
        <p className="mb-2 px-2 text-[10px] font-bold uppercase tracking-[0.18em] text-white/35">
          Operação
        </p>
        <nav className="space-y-0.5">
          {PRIMARY.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              data-active={isActive(pathname, item)}
              className="crm-nav-link"
              onClick={() => setOpen(false)}
            >
              <span className="crm-nav-ico">{item.ico}</span>
              {item.label}
            </Link>
          ))}
        </nav>
      </div>

      <div className="px-1">
        <p className="mb-2 px-2 text-[10px] font-bold uppercase tracking-[0.18em] text-white/35">
          Módulos
        </p>
        <nav className="space-y-0.5">
          {MODULES.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              data-active={isActive(pathname, item)}
              className="crm-nav-link"
              onClick={() => setOpen(false)}
            >
              <span className="crm-nav-ico">{item.ico}</span>
              {item.label}
            </Link>
          ))}
        </nav>
      </div>

      <div className="mt-auto space-y-3 px-1 pb-2">
        <Link
          href="/studio?mode=central"
          className="crm-btn crm-btn-primary w-full"
          onClick={() => setOpen(false)}
        >
          Operar com IA
        </Link>
        <p className="px-2 text-[10px] leading-relaxed text-white/35">
          Radar → roteiro → artes → vídeo → post. Um CRM só seu.
        </p>
      </div>
    </>
  );

  return (
    <div className="crm-app">
      <aside className="crm-sidebar hidden lg:flex">{sidebar}</aside>

      {/* Mobile drawer */}
      <div className="lg:hidden">
        <div className="sticky top-0 z-40 flex items-center justify-between border-b border-white/10 bg-[color:var(--fase-side)] px-4 py-3 text-white">
          <button
            type="button"
            className="rounded-lg border border-white/15 px-2.5 py-1.5 text-xs font-semibold"
            onClick={() => setOpen(true)}
          >
            Menu
          </button>
          <Link href="/dashboard" className="font-display text-lg font-extrabold">
            FASE
          </Link>
          <Link
            href="/studio?mode=central"
            className="rounded-lg bg-[color:var(--fase-accent)] px-2.5 py-1.5 text-xs font-bold text-[color:var(--fase-accent-ink)]"
          >
            IA
          </Link>
        </div>
        {open ? (
          <div className="fixed inset-0 z-50 flex">
            <button
              type="button"
              className="absolute inset-0 bg-black/55"
              aria-label="Fechar menu"
              onClick={() => setOpen(false)}
            />
            <aside className="crm-sidebar relative z-10 w-[280px] max-w-[85vw]">
              <button
                type="button"
                className="mb-2 self-end rounded-lg border border-white/15 px-2 py-1 text-xs"
                onClick={() => setOpen(false)}
              >
                Fechar
              </button>
              {sidebar}
            </aside>
          </div>
        ) : null}
      </div>

      <div className="crm-main">
        <div className="relative z-10 mx-auto max-w-[1280px] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
          {(title || actions) && (
            <header className="mb-7 flex flex-wrap items-end justify-between gap-4 animate-fase-rise">
              <div>
                <p className="crm-pill">FASE CRM</p>
                {title ? (
                  <h1 className="font-display mt-2 text-3xl font-extrabold tracking-tight text-[color:var(--fase-ink)] sm:text-4xl">
                    {title}
                  </h1>
                ) : null}
                {subtitle ? (
                  <p className="mt-2 max-w-xl text-sm text-[color:var(--fase-muted)]">
                    {subtitle}
                  </p>
                ) : null}
              </div>
              {actions ? <div className="flex flex-wrap gap-2">{actions}</div> : null}
            </header>
          )}
          {children}
        </div>
      </div>
    </div>
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
  if (bare) return <>{children}</>;
  return <CrmShell>{children}</CrmShell>;
}
