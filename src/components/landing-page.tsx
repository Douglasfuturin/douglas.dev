"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const STAGES = [
  "Radar",
  "Roteiro",
  "Artes",
  "Vídeo",
  "Publicar",
] as const;

export function LandingPage() {
  const [pulse, setPulse] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setPulse((p) => (p + 1) % STAGES.length), 2000);
    return () => clearInterval(t);
  }, []);

  return (
    <main className="relative min-h-screen fase-landing">
      <div className="fase-landing-glow" aria-hidden />
      <div className="fase-landing-grain" aria-hidden />

      <header className="relative z-10 mx-auto flex max-w-6xl items-center justify-between px-5 py-6 sm:px-8">
        <p className="font-display text-2xl font-extrabold tracking-tight text-white">
          FASE
        </p>
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard"
            className="text-sm font-semibold text-white/65 transition hover:text-white"
          >
            Entrar no CRM
          </Link>
          <Link
            href="/dashboard"
            className="rounded-lg bg-[color:var(--fase-accent)] px-3.5 py-2 text-sm font-bold text-[color:var(--fase-accent-ink)] transition hover:brightness-105"
          >
            Abrir Dashboard
          </Link>
        </div>
      </header>

      <section className="relative z-10 mx-auto flex min-h-[78vh] max-w-6xl flex-col justify-center px-5 pb-16 pt-4 sm:px-8">
        <p
          className="font-display text-[clamp(4rem,16vw,9rem)] font-extrabold leading-[0.85] tracking-[-0.05em] text-white animate-fase-rise"
          style={{ animationDelay: "40ms" }}
        >
          FASE
        </p>
        <h1
          className="mt-6 max-w-lg text-xl font-medium leading-snug text-white/85 sm:text-2xl animate-fase-rise"
          style={{ animationDelay: "140ms" }}
        >
          CRM de conteúdo com motion — do radar ao post, num só dashboard.
        </h1>
        <p
          className="mt-4 max-w-md text-sm leading-relaxed text-white/45 animate-fase-rise"
          style={{ animationDelay: "240ms" }}
        >
          Inspirado no ritmo de Motionsites, Godly e Spline: agentes, pipeline,
          artes e publicação com interface viva.
        </p>

        <div
          className="mt-8 flex flex-wrap items-center gap-3 animate-fase-rise"
          style={{ animationDelay: "340ms" }}
        >
          <Link
            href="/dashboard"
            className="rounded-lg bg-white px-5 py-3 text-sm font-bold text-[#0a0d12] transition hover:bg-[color:var(--fase-accent)]"
          >
            Entrar no CRM
          </Link>
          <Link
            href="/studio?mode=central"
            className="rounded-lg border border-white/20 px-5 py-3 text-sm font-semibold text-white/90 transition hover:border-white/45"
          >
            Studio IA
          </Link>
        </div>

        <div
          className="mt-14 flex flex-wrap gap-2 animate-fase-rise"
          style={{ animationDelay: "440ms" }}
          aria-label="Etapas"
        >
          {STAGES.map((label, i) => (
            <span
              key={label}
              className={`rounded-md px-3 py-1.5 text-[11px] font-bold uppercase tracking-[0.14em] transition-all duration-500 ${
                i === pulse
                  ? "scale-105 bg-[color:var(--fase-accent)] text-[color:var(--fase-accent-ink)]"
                  : "bg-white/5 text-white/40"
              }`}
            >
              {label}
            </span>
          ))}
        </div>
      </section>

      <section className="relative z-10 border-t border-white/10 bg-black/25 px-5 py-14 sm:px-8">
        <div className="mx-auto grid max-w-6xl gap-10 sm:grid-cols-3">
          {[
            {
              title: "Dashboard CRM",
              body: "Métricas, pipeline, times e todos os módulos num painel.",
            },
            {
              title: "Agentes animados",
              body: "Radar, roteiro, artes, editor e salas Dev / España.",
            },
            {
              title: "Fila de publicação",
              body: "Do ready ao post — Instagram, YouTube, X e Notion.",
            },
          ].map((block, i) => (
            <div
              key={block.title}
              className="animate-fase-rise"
              style={{ animationDelay: `${520 + i * 70}ms` }}
            >
              <h2 className="font-display text-lg font-bold text-white">
                {block.title}
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-white/45">
                {block.body}
              </p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
