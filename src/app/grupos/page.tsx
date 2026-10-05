"use client";

import Link from "next/link";
import { AppShell } from "@/components/app-shell";
import { listAgentGroups, type AgentMember } from "@/lib/agents/groups";

function MemberIcon({ member }: { member: AgentMember }) {
  const shape =
    member.icon === "cloud"
      ? "rounded-[40%]"
      : member.icon === "triangle"
        ? "rounded-md rotate-0"
        : member.icon === "hex"
          ? "rounded-lg"
          : member.icon === "drop"
            ? "rounded-[40%_40%_45%_45%]"
            : member.icon === "play"
              ? "rounded-2xl"
              : member.icon === "square"
                ? "rounded-xl"
                : "rounded-full";

  return (
    <span
      className={`inline-flex h-10 w-10 items-center justify-center ${shape} text-sm font-bold text-[#0b0f14]`}
      style={{ background: member.color }}
      aria-hidden
    >
      {member.name
        .split(" ")
        .slice(0, 2)
        .map((w) => w[0])
        .join("")}
    </span>
  );
}

export default function GruposPage() {
  const groups = listAgentGroups();

  return (
    <AppShell>
      <main className="mx-auto max-w-3xl px-5 py-10">
        <div className="mb-8 flex items-end justify-between gap-4">
          <div>
            <p className="font-display text-4xl tracking-tight text-[color:var(--fase-ink)]">
              Grupos
            </p>
            <p className="mt-2 max-w-lg text-sm text-[color:var(--fase-muted)]">
              Salas FASE — Conteúdo Dev, Dev Vídeo e Contenidos España.
            </p>
          </div>
          <Link
            href="/central"
            className="rounded-lg border border-[color:var(--fase-line)] bg-white/70 px-3 py-1.5 text-xs font-semibold"
          >
            ← Central
          </Link>
        </div>

        <div className="space-y-8">
          {groups.map((group) => (
            <section
              key={group.id}
              className="rounded-3xl border border-[color:var(--fase-line)] bg-white/70 p-5"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h2 className="text-2xl font-semibold tracking-tight text-[color:var(--fase-ink)]">
                    {group.name}
                  </h2>
                  <p className="mt-1 text-sm text-[color:var(--fase-muted)]">
                    {group.blurb}
                  </p>
                </div>
                <Link
                  href={`/studio?mode=grupo&group=${group.id}`}
                  className="rounded-lg bg-[color:var(--fase-accent)] px-3 py-1.5 text-xs font-semibold text-[color:var(--fase-accent-ink)]"
                >
                  Abrir sala →
                </Link>
              </div>

              <p className="mt-5 text-[11px] uppercase tracking-[0.18em] text-[color:var(--fase-muted)]">
                Membros ({group.members.length}/{group.maxMembers})
              </p>
              <ul className="mt-3 grid gap-2 sm:grid-cols-2">
                {group.members.map((member) => (
                  <li key={member.id}>
                    <Link
                      href={`/studio?mode=${member.mode}&group=${group.id}&member=${member.id}`}
                      className="flex items-center gap-3 rounded-2xl border border-[color:var(--fase-line)] bg-[color:var(--fase-panel)]/80 px-3 py-2.5 transition hover:border-[color:var(--fase-accent)]"
                    >
                      <MemberIcon member={member} />
                      <span>
                        <span className="block text-sm font-semibold text-[color:var(--fase-ink)]">
                          {member.name}
                        </span>
                        <span className="block text-[11px] text-[color:var(--fase-muted)]">
                          {member.role}
                        </span>
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>

              <ol className="mt-5 list-decimal space-y-1 pl-5 text-xs text-[color:var(--fase-muted)]">
                {group.workflow.map((step) => (
                  <li key={step}>{step}</li>
                ))}
              </ol>
            </section>
          ))}
        </div>
      </main>
    </AppShell>
  );
}
