"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const STAGES = ["Radar", "Roteiro", "Artes", "Vídeo", "Post"] as const;

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
        <div>
          <p className="font-display text-2xl text-white">Douglas Dev</p>
          <p className="text-[11px] font-semibold tracking-[0.14em] text-white/45">
            @o.douglas.dev · FASE
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/dashboard" className="crm-btn crm-btn-ghost !py-2">
            Entrar
          </Link>
          <Link href="/dashboard" className="crm-btn crm-btn-primary !py-2">
            Salve · CRM
          </Link>
        </div>
      </header>

      <section className="relative z-10 mx-auto flex min-h-[78vh] max-w-6xl flex-col justify-center px-5 pb-16 pt-4 sm:px-8">
        <p
          className="font-display text-[clamp(3.2rem,12vw,7.5rem)] leading-[0.88] text-white animate-fase-rise"
          style={{ animationDelay: "40ms" }}
        >
          Tarefas
          <br />
          no automático
        </p>
        <h1
          className="mt-6 max-w-lg text-lg font-medium leading-snug text-white/75 sm:text-xl animate-fase-rise"
          style={{ animationDelay: "140ms" }}
        >
          CRM de conteúdo com a identidade Douglas Dev — carrosséis realistas,
          agentes e pipeline até o post.
        </h1>
        <p
          className="mt-4 max-w-md text-sm leading-relaxed text-white/45 animate-fase-rise"
          style={{ animationDelay: "240ms" }}
        >
          Preto · laranja #F26522 · tipografia condensada · Antes/Depois
          fotorealista.
        </p>

        <div
          className="mt-8 flex flex-wrap items-center gap-3 animate-fase-rise"
          style={{ animationDelay: "340ms" }}
        >
          <Link href="/dashboard" className="crm-btn crm-btn-primary">
            Abrir Dashboard
          </Link>
          <Link
            href="/studio?mode=arte-realista&q=Planeja%20um%20carrossel%20realista%20Douglas%20Dev%20sobre%205%20automa%C3%A7%C3%B5es%20com%20IA"
            className="crm-btn crm-btn-ghost"
          >
            Carrossel realista
          </Link>
        </div>

        <div
          className="mt-14 flex flex-wrap gap-2 animate-fase-rise"
          style={{ animationDelay: "440ms" }}
        >
          {STAGES.map((label, i) => (
            <span
              key={label}
              className={`rounded-full px-3.5 py-1.5 text-[11px] font-bold uppercase tracking-[0.14em] transition-all duration-500 ${
                i === pulse
                  ? "scale-105 bg-[color:var(--dd-orange)] text-white"
                  : "bg-white/8 text-white/40"
              }`}
            >
              {label}
            </span>
          ))}
        </div>
      </section>

      <section className="relative z-10 border-t border-white/10 bg-black/40 px-5 py-14 sm:px-8">
        <div className="mx-auto grid max-w-6xl gap-8 sm:grid-cols-3">
          {[
            {
              title: "Antes → Depois",
              body: "Carrosséis realistas com problema, seta laranja e solução — no estilo dos seus posts.",
            },
            {
              title: "Agentes FASE",
              body: "Radar, GitHub + Reels 60s, arte realista e criar agente custom.",
            },
            {
              title: "Pipeline CRM",
              body: "Do briefing ao post, com a mesma identidade visual em todo o sistema.",
            },
          ].map((block, i) => (
            <div
              key={block.title}
              className="animate-fase-rise"
              style={{ animationDelay: `${520 + i * 70}ms` }}
            >
              <h2 className="font-display text-2xl text-white">{block.title}</h2>
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
