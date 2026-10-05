"use client";

import Link from "next/link";
import { NexusToolChrome } from "./nexus-tool-chrome";

const PACK_STEPS = [
  {
    title: "Scout GitHub",
    body: "Encontra e ranqueia os melhores repos do nicho.",
  },
  {
    title: "Roteiro Reels 60s",
    body: "Gera script pronto para gravação ou edição.",
  },
  {
    title: "Pack Notion",
    body: "Fecha guia com instalação, uso e links.",
  },
] as const;

export function NexusPackWorkspace() {
  return (
    <NexusToolChrome
      toolId="pack"
      actions={
        <Link
          href="/ferramentas/studio?mode=pipeline"
          className="nexus-btn-primary"
        >
          Iniciar Pack
        </Link>
      }
    >
      <div className="space-y-6">
        <section className="nexus-panel">
          <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[color:var(--primary)]">
            Pipeline · uma tacada
          </p>
          <h2 className="mt-2 text-xl font-semibold text-[color:var(--foreground)]">
            Scout → Roteiro → Notion
          </h2>
          <p className="mt-2 max-w-xl text-sm text-[color:var(--muted-foreground)]">
            O Pack Scout abre o Studio no modo pipeline e orquestra as três etapas
            com as tools certas.
          </p>
          <div className="mt-5 flex flex-wrap gap-2">
            <Link
              href="/ferramentas/studio?mode=pipeline&q=Roda%20o%20pack%20Scout%20para%20um%20nicho%20de%20IA&autosend=1"
              className="nexus-btn-primary"
            >
              Pack com prompt
            </Link>
            <Link href="/ferramentas/studio?mode=github" className="nexus-btn-ghost">
              Só Scout
            </Link>
            <Link href="/ferramentas/studio?mode=notion" className="nexus-btn-ghost">
              Só Notion
            </Link>
          </div>
        </section>

        <ol className="grid gap-3 md:grid-cols-3">
          {PACK_STEPS.map((step, i) => (
            <li key={step.title} className="nexus-pipeline-step">
              <span className="nexus-step-num">{i + 1}</span>
              <p className="mt-2 text-sm font-semibold text-[color:var(--foreground)]">
                {step.title}
              </p>
              <p className="mt-1 text-xs leading-relaxed text-[color:var(--muted-foreground)]">
                {step.body}
              </p>
            </li>
          ))}
        </ol>
      </div>
    </NexusToolChrome>
  );
}
