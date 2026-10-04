"use client";

import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";
import { useMemo, useState } from "react";
import type { AgentMode, ResearchDepth } from "@/lib/agents/models";

const MODE_LABELS: Record<AgentMode, string> = {
  auto: "Auto",
  chat: "Chat + tools",
  research: "Multi-agent research",
};

export function ChatApp() {
  const [input, setInput] = useState("");
  const [mode, setMode] = useState<AgentMode>("auto");
  const [researchDepth, setResearchDepth] = useState<ResearchDepth>("medium");

  const transport = useMemo(
    () =>
      new DefaultChatTransport({
        api: "/api/chat",
      }),
    [],
  );

  const { messages, sendMessage, status, error, stop } = useChat({
    transport,
  });

  const busy = status === "submitted" || status === "streaming";

  return (
    <div className="relative flex min-h-full flex-1 flex-col overflow-hidden">
      <div className="pointer-events-none absolute inset-0 atmosphere" aria-hidden />
      <div className="pointer-events-none absolute inset-0 grid-fade" aria-hidden />

      <header className="relative z-10 mx-auto flex w-full max-w-3xl items-end justify-between gap-4 px-5 pt-8 pb-4">
        <div>
          <p className="font-display text-4xl tracking-tight text-[var(--ink)] md:text-5xl">
            Grokish
          </p>
          <p className="mt-2 max-w-md text-sm leading-relaxed text-[var(--muted)]">
            Multi-agente com as tools do Grok: web, X, código e imagens.
          </p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <label className="text-[11px] uppercase tracking-[0.18em] text-[var(--muted)]">
            Modo
            <select
              className="mt-1 block rounded-md border border-[var(--line)] bg-[var(--panel)] px-2 py-1.5 text-sm text-[var(--ink)]"
              value={mode}
              onChange={(e) => setMode(e.target.value as AgentMode)}
            >
              {(Object.keys(MODE_LABELS) as AgentMode[]).map((key) => (
                <option key={key} value={key}>
                  {MODE_LABELS[key]}
                </option>
              ))}
            </select>
          </label>
          {mode !== "chat" ? (
            <label className="text-[11px] uppercase tracking-[0.18em] text-[var(--muted)]">
              Agentes
              <select
                className="mt-1 block rounded-md border border-[var(--line)] bg-[var(--panel)] px-2 py-1.5 text-sm text-[var(--ink)]"
                value={researchDepth}
                onChange={(e) =>
                  setResearchDepth(e.target.value as ResearchDepth)
                }
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </label>
          ) : null}
        </div>
      </header>

      <main className="relative z-10 mx-auto flex w-full max-w-3xl flex-1 flex-col px-5 pb-28">
        <div className="flex flex-1 flex-col gap-4 overflow-y-auto py-2">
          {messages.length === 0 ? (
            <EmptyState
              onPick={(prompt) => {
                setInput(prompt);
              }}
            />
          ) : null}

          {messages.map((message) => (
            <article
              key={message.id}
              className={`animate-rise max-w-[92%] rounded-2xl px-4 py-3 text-[15px] leading-relaxed ${
                message.role === "user"
                  ? "ml-auto bg-[var(--ink)] text-[var(--panel)]"
                  : "mr-auto border border-[var(--line)] bg-[var(--panel)]/90 text-[var(--ink)] backdrop-blur"
              }`}
            >
              <p className="mb-1 text-[10px] uppercase tracking-[0.16em] opacity-60">
                {message.role === "user" ? "Você" : "Grokish"}
              </p>
              <div className="space-y-3 whitespace-pre-wrap">
                {message.parts.map((part, index) => {
                  if (part.type === "text") {
                    return <p key={`${message.id}-${index}`}>{part.text}</p>;
                  }

                  if (part.type.startsWith("tool-")) {
                    const toolName = part.type.replace(/^tool-/, "");
                    return (
                      <p
                        key={`${message.id}-${index}`}
                        className="rounded-md bg-[var(--chip)] px-2 py-1 font-mono text-xs text-[var(--accent-ink)]"
                      >
                        tool · {toolName}
                      </p>
                    );
                  }

                  return null;
                })}
              </div>
            </article>
          ))}

          {busy ? (
            <p className="animate-pulse text-sm text-[var(--muted)]">
              Agentes trabalhando…
            </p>
          ) : null}

          {error ? (
            <p className="rounded-xl border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800">
              {error.message}
            </p>
          ) : null}
        </div>
      </main>

      <form
        className="fixed inset-x-0 bottom-0 z-20 border-t border-[var(--line)] bg-[var(--panel)]/85 px-5 py-4 backdrop-blur-xl"
        onSubmit={(e) => {
          e.preventDefault();
          const text = input.trim();
          if (!text || busy) return;
          sendMessage(
            { text },
            {
              body: {
                mode,
                researchDepth,
              },
            },
          );
          setInput("");
        }}
      >
        <div className="mx-auto flex w-full max-w-3xl items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            rows={2}
            placeholder="Pergunte algo… ex: pesquise o estado atual da API multi-agent do Grok"
            className="min-h-[56px] flex-1 resize-none rounded-xl border border-[var(--line)] bg-white/70 px-3 py-3 text-sm text-[var(--ink)] outline-none ring-[var(--accent)] placeholder:text-[var(--muted)] focus:ring-2"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                e.currentTarget.form?.requestSubmit();
              }
            }}
          />
          {busy ? (
            <button
              type="button"
              onClick={() => stop()}
              className="rounded-xl border border-[var(--line)] px-4 py-3 text-sm font-medium text-[var(--ink)]"
            >
              Parar
            </button>
          ) : (
            <button
              type="submit"
              disabled={!input.trim()}
              className="rounded-xl bg-[var(--accent)] px-4 py-3 text-sm font-semibold text-[var(--accent-ink)] transition enabled:hover:brightness-105 disabled:opacity-40"
            >
              Enviar
            </button>
          )}
        </div>
      </form>
    </div>
  );
}

function EmptyState({ onPick }: { onPick: (prompt: string) => void }) {
  const prompts = [
    "O que é o modelo grok-4.20-multi-agent e quando usar?",
    "Pesquise nas últimas notícias o que está rolando sobre agentes de IA",
    "Gere uma imagem de um robô lendo o X à noite, estilo poster vintage",
  ];

  return (
    <section className="animate-rise mt-6 space-y-4">
      <p className="text-sm text-[var(--muted)]">
        Três caminhos: chat com tools, research multi-agente, ou Auto (roteador).
      </p>
      <ul className="space-y-2">
        {prompts.map((prompt) => (
          <li key={prompt}>
            <button
              type="button"
              onClick={() => onPick(prompt)}
              className="w-full rounded-xl border border-[var(--line)] bg-[var(--panel)]/80 px-4 py-3 text-left text-sm text-[var(--ink)] transition hover:border-[var(--accent)] hover:bg-white"
            >
              {prompt}
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
