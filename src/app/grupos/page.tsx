"use client";

import Link from "next/link";
import { CrmShell } from "@/components/crm/crm-shell";
import { listAgentGroups, type AgentMember } from "@/lib/agents/groups";

function MemberIcon({ member }: { member: AgentMember }) {
  return (
    <span
      className="inline-flex h-10 w-10 items-center justify-center rounded-xl text-sm font-bold text-[#0b0f14]"
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
    <CrmShell
      title="Agentes"
      subtitle="Salas FASE — Conteúdo Dev, Dev Vídeo e Contenidos España."
      actions={
        <Link href="/dashboard" className="crm-btn crm-btn-ghost">
          Dashboard
        </Link>
      }
    >
      <div className="space-y-5">
        {groups.map((group, i) => (
          <section
            key={group.id}
            className="crm-panel animate-fase-rise"
            style={{ animationDelay: `${i * 80}ms` }}
          >
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 className="font-display text-2xl font-bold tracking-tight text-[color:var(--fase-ink)]">
                  {group.name}
                </h2>
                <p className="mt-1 max-w-xl text-sm text-[color:var(--fase-muted)]">
                  {group.blurb}
                </p>
              </div>
              <Link
                href={`/studio?mode=grupo&group=${group.id}`}
                className="crm-btn crm-btn-primary"
              >
                Abrir sala →
              </Link>
            </div>

            <p className="mt-5 text-[11px] font-bold uppercase tracking-[0.18em] text-[color:var(--fase-muted)]">
              Membros ({group.members.length}/{group.maxMembers})
            </p>
            <ul className="mt-3 grid gap-2 sm:grid-cols-2">
              {group.members.map((member) => (
                <li key={member.id}>
                  <Link
                    href={`/studio?mode=${member.mode}&group=${group.id}&member=${member.id}`}
                    className="flex items-center gap-3 rounded-xl border border-[color:var(--fase-line)] bg-white/70 px-3 py-2.5 transition hover:border-[color:var(--fase-ink)]/25"
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
    </CrmShell>
  );
}
