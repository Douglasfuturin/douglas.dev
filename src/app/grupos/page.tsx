"use client";

import Link from "next/link";
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
    <main className="min-h-screen bg-[radial-gradient(1200px_600px_at_20%_-10%,#1a2740,transparent),linear-gradient(180deg,#0b0f14,#121820)] px-5 py-10 text-[#e8eef7]">
      <div className="mx-auto max-w-3xl">
        <div className="mb-8 flex items-end justify-between gap-4">
          <div>
            <p className="font-display text-4xl tracking-tight">Grupos</p>
            <p className="mt-2 max-w-lg text-sm text-[#9aa8bc]">
              Duas salas de agentes no estilo Grok — até 6 membros cada.
            </p>
          </div>
          <Link
            href="/"
            className="rounded-lg border border-white/15 px-3 py-1.5 text-xs font-semibold"
          >
            ← Chat
          </Link>
        </div>

        <div className="space-y-8">
          {groups.map((group) => (
            <section
              key={group.id}
              className="rounded-3xl border border-white/10 bg-white/[0.03] p-5 backdrop-blur"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h2 className="text-2xl font-semibold tracking-tight">
                    {group.name}
                  </h2>
                  <p className="mt-1 text-sm text-[#9aa8bc]">{group.blurb}</p>
                </div>
                <Link
                  href={`/?mode=grupo&group=${group.id}`}
                  className="rounded-lg bg-[#5B9DFF] px-3 py-1.5 text-xs font-semibold text-[#0b0f14]"
                >
                  Abrir sala →
                </Link>
              </div>

              <p className="mt-5 text-[11px] uppercase tracking-[0.18em] text-[#7f8ea3]">
                Membros ({group.members.length}/{group.maxMembers})
              </p>
              <ul className="mt-3 divide-y divide-white/8">
                {group.members.map((member) => (
                  <li key={member.id}>
                    <Link
                      href={`/?mode=${member.mode}&group=${group.id}&member=${member.id}`}
                      className="flex items-center gap-3 py-3 transition hover:bg-white/[0.03]"
                    >
                      <MemberIcon member={member} />
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium">
                          {member.name}
                        </p>
                        <p className="truncate text-xs text-[#9aa8bc]">
                          {member.role}
                        </p>
                      </div>
                      <span className="text-xs text-[#5B9DFF]">Conversar</span>
                    </Link>
                  </li>
                ))}
              </ul>

              {group.members.length >= group.maxMembers ? (
                <p className="mt-2 text-xs text-[#7f8ea3]">
                  Os chats em grupo podem ter até {group.maxMembers} membros.
                </p>
              ) : null}

              <div className="mt-5">
                <p className="text-[11px] uppercase tracking-[0.18em] text-[#7f8ea3]">
                  Fluxo
                </p>
                <ol className="mt-2 list-decimal space-y-1 pl-5 text-sm text-[#c5d0e0]">
                  {group.workflow.map((step) => (
                    <li key={step}>{step}</li>
                  ))}
                </ol>
              </div>

              <p className="mt-5 text-[11px] uppercase tracking-[0.18em] text-[#7f8ea3]">
                Rotinas
              </p>
              <p className="mt-1 text-sm text-[#7f8ea3]">Nenhuma rotina ainda</p>
            </section>
          ))}
        </div>
      </div>
    </main>
  );
}
