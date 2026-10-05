"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const STAGES = [
  "Radar",
  "Aprovar",
  "Roteiro",
  "Artes",
  "Editar",
  "Publicar",
] as const;

export function LandingPage() {
  const [pulse, setPulse] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setPulse((p) => (p + 1) % STAGES.length), 2200);
    return () => clearInterval(t);
  }, []);

  return (
    <main className="relative min-h-screen overflow-hidden fase-landing">
      <div className="fase-landing-glow" aria-hidden />
      <div className="fase-landing-grain" aria-hidden />

      <header className="relative z-10 mx-auto flex max-w-6xl items-center justify-between px-5 py-6 sm:px-8">
        <p className="font-display text-2xl font-extrabold tracking-tight text-[color:var(--fase-cream)]">
          FASE
        </p>
        <div className="flex items-center gap-3">
          <Link
            href="/central"
            className="text-sm font-semibold text-[color:var(--fase-cream)]/70 transition hover:text-[color:var(--fase-cream)]"
          >
            Entrar
          </Link>
          <Link
            href="/studio?mode=central"
            className="rounded-lg bg-[color:var(--fase-ember)] px-3.5 py-2 text-sm font-semibold text-[#1a0f08] transition hover:brightness-110"
          >
            Abrir Studio
          </Link>
        </div>
      </header>

      <section className="relative z-10 mx-auto flex min-h-[78vh] max-w-6xl flex-col justify-center px-5 pb-16 pt-6 sm:px-8">
        <p
          className="font-display text-[clamp(3.5rem,14vw,8.5rem)] font-extrabold leading-[0.9] tracking-[-0.04em] text-[color:var(--fase-cream)] animate-fase-rise"
          style={{ animationDelay: "40ms" }}
        >
          FASE
        </p>
        <h1
          className="mt-5 max-w-xl text-xl font-medium leading-snug text-[color:var(--fase-cream)]/90 sm:text-2xl animate-fase-rise"
          style={{ animationDelay: "160ms" }}
        >
          Do radar ao post — sua central pessoal de conteúdo.
        </h1>
        <p
          className="mt-4 max-w-md text-sm leading-relaxed text-[color:var(--fase-cream)]/55 animate-fase-rise"
          style={{ animationDelay: "280ms" }}
        >
          Tendências, roteiros, artes, edição com skills e fila de publicação.
          Um SaaS só seu, rodando no Grok.
        </p>

        <div
          className="mt-8 flex flex-wrap items-center gap-3 animate-fase-rise"
          style={{ animationDelay: "400ms" }}
        >
          <Link
            href="/central"
            className="rounded-lg bg-[color:var(--fase-cream)] px-5 py-3 text-sm font-bold text-[#1c1510] transition hover:bg-white"
          >
            Abrir Central
          </Link>
          <Link
            href="/grupos"
            className="rounded-lg border border-[color:var(--fase-cream)]/25 px-5 py-3 text-sm font-semibold text-[color:var(--fase-cream)]/90 transition hover:border-[color:var(--fase-cream)]/50"
          >
            Ver grupos de agentes
          </Link>
        </div>

        <div
          className="mt-14 flex flex-wrap gap-2 animate-fase-rise"
          style={{ animationDelay: "520ms" }}
          aria-label="Etapas do pipeline"
        >
          {STAGES.map((label, i) => (
            <span
              key={label}
              className={`rounded-md px-3 py-1.5 text-[11px] font-semibold uppercase tracking-[0.14em] transition-all duration-500 ${
                i === pulse
                  ? "bg-[color:var(--fase-ember)] text-[#1a0f08] scale-105"
                  : "bg-white/5 text-[color:var(--fase-cream)]/45"
              }`}
            >
              {label}
            </span>
          ))}
        </div>
      </section>

      <section className="relative z-10 border-t border-white/10 bg-black/20 px-5 py-14 sm:px-8">
        <div className="mx-auto grid max-w-6xl gap-10 sm:grid-cols-3">
          {[
            {
              title: "Pipeline vivo",
              body: "Kanban idea → published com aprovação, roteiro, artes e fila de post.",
            },
            {
              title: "Agentes no Studio",
              body: "Radar, Roteirista, Arte, Editor, YouTube/España e Bit — um modo Central une tudo.",
            },
            {
              title: "Publicação pronta",
              body: "Fila local + hook Buffer/APIs. Notion e packs já saem do mesmo fluxo.",
            },
          ].map((block, i) => (
            <div
              key={block.title}
              className="animate-fase-rise"
              style={{ animationDelay: `${600 + i * 80}ms` }}
            >
              <h2 className="font-display text-lg font-bold text-[color:var(--fase-cream)]">
                {block.title}
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-[color:var(--fase-cream)]/50">
                {block.body}
              </p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
