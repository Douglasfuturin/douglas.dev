"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { NEXUS_PRODUCT } from "@/lib/brand/nexus";

const STAGES = ["Radar", "Roteiro", "Artes", "Vídeo", "Post"] as const;

export function LandingPage() {
  const [pulse, setPulse] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setPulse((p) => (p + 1) % STAGES.length), 2000);
    return () => clearInterval(t);
  }, []);

  return (
    <main className="relative min-h-screen nexus-landing">
      <div className="nexus-landing-glow" aria-hidden />
      <div className="nexus-landing-grid" aria-hidden />

      <header className="relative z-10 mx-auto flex max-w-6xl items-center justify-between px-5 py-6 sm:px-8">
        <div className="flex items-center gap-3">
          <span className="flex size-10 items-center justify-center rounded-lg bg-[color:var(--primary)] text-sm font-bold text-[color:var(--primary-foreground)]">
            NX
          </span>
          <div>
            <p className="text-lg font-semibold tracking-tight text-[color:var(--foreground)]">
              {NEXUS_PRODUCT.name}{" "}
              <span className="font-mono text-[10px] font-medium uppercase tracking-wider text-[color:var(--muted-foreground)]">
                {NEXUS_PRODUCT.badge}
              </span>
            </p>
            <p className="text-[11px] font-medium tracking-[0.12em] text-[color:var(--muted-foreground)]">
              {NEXUS_PRODUCT.tagline}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/app" className="nexus-btn-ghost !py-2 text-sm">
            Chat
          </Link>
          <Link href="/dashboard" className="nexus-btn-primary !py-2 text-sm">
            Entrar
          </Link>
        </div>
      </header>

      <section className="relative z-10 mx-auto flex min-h-[78vh] max-w-6xl flex-col justify-center px-5 pb-16 pt-4 sm:px-8">
        <p
          className="text-[11px] font-semibold uppercase tracking-[0.2em] text-[color:var(--primary)] animate-nexus-rise"
          style={{ animationDelay: "20ms" }}
        >
          Sistema operacional para agentes
        </p>
        <h1
          className="mt-4 max-w-3xl text-[clamp(2.4rem,8vw,5rem)] font-semibold leading-[1.05] tracking-tight text-[color:var(--foreground)] animate-nexus-rise"
          style={{ animationDelay: "80ms" }}
        >
          {NEXUS_PRODUCT.tagline}
        </h1>
        <p
          className="mt-6 max-w-xl text-lg leading-relaxed text-[color:var(--muted-foreground)] animate-nexus-rise"
          style={{ animationDelay: "160ms" }}
        >
          {NEXUS_PRODUCT.description}
        </p>

        <div
          className="mt-8 flex flex-wrap items-center gap-3 animate-nexus-rise"
          style={{ animationDelay: "240ms" }}
        >
          <Link href="/dashboard" className="nexus-btn-primary">
            Abrir central
          </Link>
          <Link href="/app" className="nexus-btn-ghost">
            Nova conversa
          </Link>
          <Link href="/grupos" className="nexus-btn-ghost">
            Orquestrações
          </Link>
        </div>

        <div
          className="mt-14 flex flex-wrap gap-2 animate-nexus-rise"
          style={{ animationDelay: "320ms" }}
        >
          {STAGES.map((label, i) => (
            <span
              key={label}
              className={`rounded-full px-3.5 py-1.5 text-[11px] font-semibold uppercase tracking-[0.12em] transition-all duration-500 ${
                i === pulse
                  ? "scale-105 bg-[color:var(--primary)] text-[color:var(--primary-foreground)]"
                  : "border border-[color:var(--border)] bg-[color:var(--card)] text-[color:var(--muted-foreground)]"
              }`}
            >
              {label}
            </span>
          ))}
        </div>
      </section>

      <section className="relative z-10 border-t border-[color:var(--border)] px-5 py-14 sm:px-8">
        <div className="mx-auto grid max-w-6xl gap-8 sm:grid-cols-3">
          {[
            {
              title: "Orquestrador",
              body: "Delega missões para Radar, Roteiro, Arte, Vídeo e agentes custom em sequência.",
            },
            {
              title: "Grupos & pipelines",
              body: "Templates prontos, fluxo visual e CRUD de orquestrações com API persistente.",
            },
            {
              title: "Ferramentas Nexus",
              body: "Studio, editor de reels local, Ninja Kits e Pack Scout no mesmo shell.",
            },
          ].map((block, i) => (
            <article
              key={block.title}
              className="nexus-panel animate-nexus-rise"
              style={{ animationDelay: `${400 + i * 70}ms` }}
            >
              <h2 className="text-lg font-semibold text-[color:var(--foreground)]">
                {block.title}
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-[color:var(--muted-foreground)]">
                {block.body}
              </p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
