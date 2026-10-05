"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import {
  isNexusActive,
  NEXUS_MAIN_NAV,
  NEXUS_RECENT_CHATS,
  NEXUS_TOOLS_NAV,
  type NexusShellProps,
} from "./nexus-config";
import { NexusIcon } from "./nexus-icons";

function SidebarNav({
  pathname,
  onNavigate,
}: {
  pathname: string;
  onNavigate?: () => void;
}) {
  return (
    <>
      <nav className="space-y-1 px-3">
        {NEXUS_MAIN_NAV.map((item) => {
          const active = isNexusActive(pathname, item);
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              data-active={active}
              className="nexus-nav-link"
            >
              <NexusIcon name={item.icon} />
              <span className="flex-1">{item.label}</span>
              {item.soon ? (
                <span className="nexus-badge-soon">Em breve</span>
              ) : null}
            </Link>
          );
        })}
      </nav>

      <div className="mt-5 px-3">
        <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-[0.16em] text-[color:var(--muted-foreground)]">
          Conversas
        </p>
        <ul className="space-y-0.5">
          {NEXUS_RECENT_CHATS.map((chat) => (
            <li key={chat.href}>
              <Link
                href={chat.href}
                onClick={onNavigate}
                className="nexus-convo-link"
              >
                <span className="block truncate text-sm font-medium text-[color:var(--foreground)]">
                  {chat.title}
                </span>
                <span className="mt-0.5 flex items-center gap-2 text-[11px] text-[color:var(--muted-foreground)]">
                  <span>{chat.agent}</span>
                  <span aria-hidden>·</span>
                  <span>{chat.when}</span>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </div>

      <div className="mt-5 px-3">
        <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-[0.16em] text-[color:var(--muted-foreground)]">
          Ferramentas
        </p>
        <nav className="space-y-0.5">
          {NEXUS_TOOLS_NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              data-active={isNexusActive(pathname, item)}
              className="nexus-nav-link nexus-nav-link-subtle"
            >
              <NexusIcon name={item.icon} />
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>
      </div>
    </>
  );
}

export function NexusShell({
  children,
  variant = "app",
  title,
  subtitle,
  actions,
  hideHeader = false,
}: NexusShellProps) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [xaiError, setXaiError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    fetch("/api/health")
      .then((r) => r.json())
      .then((data: { xai?: { ok?: boolean; error?: string | null } }) => {
        if (!alive) return;
        setXaiError(data.xai?.ok ? null : data.xai?.error || null);
      })
      .catch(() => undefined);
    return () => {
      alive = false;
    };
  }, []);

  if (variant === "bare") {
    return <>{children}</>;
  }

  const sidebar = (
    <>
      <div className="flex items-center justify-between gap-2 px-4 pt-4">
        <Link href="/dashboard" className="flex items-center gap-2.5" onClick={() => setOpen(false)}>
          <span className="flex size-8 items-center justify-center rounded-md bg-[color:var(--primary)] text-[color:var(--primary-foreground)]">
            <NexusIcon name="orchestrations" className="size-4" />
          </span>
          <span className="text-base font-semibold tracking-tight text-[color:var(--foreground)]">
            CENTRAL
          </span>
          <span className="rounded border border-[color:var(--border)] px-1.5 py-0.5 font-mono text-[9px] text-[color:var(--muted-foreground)]">
            Agentes
          </span>
        </Link>
        <button
          type="button"
          className="nexus-icon-btn lg:hidden"
          onClick={() => setOpen(false)}
          aria-label="Fechar menu"
        >
          ✕
        </button>
      </div>

      <div className="p-3">
        <Link
          href="/app"
          className="nexus-btn-primary w-full justify-start gap-2"
          onClick={() => setOpen(false)}
        >
          <NexusIcon name="plus" />
          Nova conversa
        </Link>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto pb-3">
        <SidebarNav pathname={pathname} onNavigate={() => setOpen(false)} />
      </div>

      <div className="border-t border-[color:var(--sidebar-border)] p-3">
        <div className="flex items-center gap-3 rounded-lg px-2 py-2">
          <span className="flex size-9 items-center justify-center rounded-full bg-[color:var(--sidebar-accent)] text-xs font-bold text-[color:var(--sidebar-accent-foreground)]">
            DD
          </span>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-semibold text-[color:var(--foreground)]">
              Douglas Dev
            </p>
            <p className="truncate text-[11px] text-[color:var(--muted-foreground)]">
              Workspace Pro
            </p>
          </div>
        </div>
      </div>
    </>
  );

  const isChat = variant === "chat";

  return (
    <div className={`nexus-app ${isChat ? "nexus-app-chat" : ""}`}>
      <aside className="nexus-sidebar hidden lg:flex">{sidebar}</aside>

      {open ? (
        <div
          className="fixed inset-0 z-50 bg-black/60 lg:hidden"
          onClick={() => setOpen(false)}
          aria-hidden
        />
      ) : null}
      <aside
        className={`nexus-sidebar fixed inset-y-0 left-0 z-50 w-[min(288px,88vw)] transition-transform lg:hidden ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {sidebar}
      </aside>

      <div className="nexus-main flex min-w-0 flex-1 flex-col">
        <header className="nexus-topbar">
          <button
            type="button"
            className="nexus-icon-btn lg:hidden"
            onClick={() => setOpen(true)}
            aria-label="Abrir menu"
          >
            ☰
          </button>

          <div className="hidden min-w-0 flex-1 items-center gap-3 md:flex">
            <label className="nexus-search flex-1">
              <span className="sr-only">Buscar</span>
              <input
                type="search"
                placeholder="Buscar agentes ou conversas"
                className="nexus-search-input"
              />
              <kbd className="nexus-kbd">⌘ K</kbd>
            </label>
          </div>

          {isChat ? (
            <div className="min-w-0 flex-1 text-center md:text-left lg:flex-none">
              <p className="text-sm font-semibold text-[color:var(--foreground)]">
                Orquestrador Principal
              </p>
              <p className="truncate text-[11px] text-[color:var(--muted-foreground)]">
                Delega para Radar, Roteiro, Arte, Vídeo e agentes custom
              </p>
            </div>
          ) : (
            <p className="flex-1 text-center text-[11px] font-medium uppercase tracking-[0.14em] text-[color:var(--muted-foreground)] md:text-left lg:hidden">
              Central de Agentes
            </p>
          )}

          <div className="flex shrink-0 items-center gap-2">
            {isChat ? (
              <Link href="/app/studio" className="nexus-btn-ghost hidden sm:inline-flex">
                Modo avançado
              </Link>
            ) : (
              <Link href="/app" className="nexus-btn-ghost hidden sm:inline-flex">
                Chat
              </Link>
            )}
          </div>
        </header>

        {xaiError ? (
          <div className="nexus-banner-warn px-4 py-2 text-xs md:px-6">
            Chat IA: {xaiError}{" "}
            <Link href="/editor" className="underline">
              Editor local
            </Link>{" "}
            funciona sem chave.
          </div>
        ) : null}

        <div
          className={`relative min-h-0 flex-1 ${isChat ? "flex flex-col" : "overflow-y-auto"}`}
        >
          {!isChat && !hideHeader && (title || actions) ? (
            <div className="mx-auto w-full max-w-6xl px-4 pb-2 pt-6 md:px-6">
              <header className="flex flex-wrap items-end justify-between gap-4">
                <div>
                  {title ? (
                    <h1 className="text-2xl font-semibold tracking-tight text-[color:var(--foreground)] md:text-3xl">
                      {title}
                    </h1>
                  ) : null}
                  {subtitle ? (
                    <p className="mt-2 max-w-2xl text-sm text-[color:var(--muted-foreground)]">
                      {subtitle}
                    </p>
                  ) : null}
                </div>
                {actions ? <div className="flex flex-wrap gap-2">{actions}</div> : null}
              </header>
            </div>
          ) : null}

          <div
            className={
              isChat
                ? "flex min-h-0 flex-1 flex-col"
                : "mx-auto w-full max-w-6xl px-4 pb-10 pt-2 md:px-6 md:pb-12"
            }
          >
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
