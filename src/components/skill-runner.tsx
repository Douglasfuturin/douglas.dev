"use client";

import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";
import { useEffect, useMemo, useRef, useState } from "react";

type Props = {
  runId: number;
  kitId: string;
  kitName: string;
  prompt: string;
  onClose: () => void;
};

/** Ensures each dashboard run starts exactly once (survives Strict Mode remounts). */
const startedRuns = new Set<number>();

function formatRunError(raw: string): string {
  let msg = raw;
  try {
    const parsed = JSON.parse(raw) as { error?: string };
    if (parsed.error) msg = parsed.error;
  } catch {
    const match = raw.match(/"error"\s*:\s*"([^"]+)"/);
    if (match?.[1]) msg = match[1];
  }
  if (/xai_api_key/i.test(msg)) {
    return `${msg} Configure XAI_API_KEY no .env.local para executar de verdade.`;
  }
  return msg;
}

export function SkillRunner({
  runId,
  kitId,
  kitName,
  prompt,
  onClose,
}: Props) {
  const [followUp, setFollowUp] = useState("");
  const [localError, setLocalError] = useState<string | null>(null);
  const scrollerRef = useRef<HTMLDivElement | null>(null);
  const sendRef = useRef<typeof sendMessage | null>(null);

  const transport = useMemo(
    () =>
      new DefaultChatTransport({
        api: "/api/chat",
        body: {
          mode: "kits" as const,
          kitId,
        },
      }),
    [kitId],
  );

  const { messages, sendMessage, status, error, stop } = useChat({
    transport,
  });

  sendRef.current = sendMessage;
  const busy = status === "submitted" || status === "streaming";

  async function startRun(text: string) {
    const trimmed = text.trim();
    if (!trimmed) {
      setLocalError("Pedido vazio — volte e preencha o brief.");
      return;
    }
    setLocalError(null);
    const send = sendRef.current;
    if (!send) {
      setLocalError("Chat ainda não pronto — clique em Reenviar pedido.");
      return;
    }
    try {
      await send(
        { text: trimmed },
        {
          body: {
            mode: "kits",
            kitId,
          },
        },
      );
    } catch (err) {
      setLocalError(
        err instanceof Error ? err.message : "Falha ao iniciar a skill",
      );
    }
  }

  useEffect(() => {
    // Defer start so Strict Mode cleanup doesn't cancel a mid-flight request,
    // and so useChat transport is ready. Mark runId only when actually starting.
    const timer = window.setTimeout(() => {
      if (startedRuns.has(runId)) return;
      startedRuns.add(runId);
      void startRun(prompt);
    }, 120);
    return () => window.clearTimeout(timer);
    // run once per runId
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [runId]);

  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [messages, busy, localError]);

  function sendFollowUp() {
    const text = followUp.trim();
    if (!text || busy) return;
    void startRun(text);
    setFollowUp("");
  }

  return (
    <section className="flex min-h-0 flex-1 flex-col rounded-2xl border border-[var(--line)] bg-[var(--panel)]/95 animate-rise shadow-sm backdrop-blur">
      <header className="flex items-start justify-between gap-3 border-b border-[var(--line)] px-4 py-3">
        <div className="min-w-0">
          <p className="text-[10px] uppercase tracking-[0.16em] text-[var(--muted)]">
            Executando skill
          </p>
          <h2 className="truncate font-display text-xl text-[var(--ink)]">
            {kitName}
          </h2>
          <p className="mt-0.5 font-mono text-[11px] text-[var(--muted)]">
            {kitId}
          </p>
        </div>
        <div className="flex shrink-0 gap-2">
          {busy ? (
            <button
              type="button"
              onClick={() => stop()}
              className="rounded-lg border border-[var(--line)] px-3 py-1.5 text-xs text-[var(--ink)]"
            >
              Parar
            </button>
          ) : null}
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg bg-[var(--ink)] px-3 py-1.5 text-xs font-semibold text-[var(--panel)]"
          >
            Fechar
          </button>
        </div>
      </header>

      <div
        ref={scrollerRef}
        className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto px-4 py-3"
      >
        <article className="ml-auto max-w-[95%] rounded-2xl bg-[var(--ink)] px-3 py-2.5 text-sm leading-relaxed text-[var(--panel)]">
          <p className="mb-1 text-[10px] uppercase tracking-[0.14em] opacity-60">
            Você
          </p>
          <p className="whitespace-pre-wrap">{prompt || "(sem pedido)"}</p>
        </article>

        {messages.map((message) => {
          // Skip duplicate of the seed user prompt if the SDK echoes it
          if (
            message.role === "user" &&
            message.parts.some(
              (p) => p.type === "text" && p.text.trim() === prompt.trim(),
            )
          ) {
            return null;
          }
          return (
            <article
              key={message.id}
              className={`max-w-[95%] rounded-2xl px-3 py-2.5 text-sm leading-relaxed ${
                message.role === "user"
                  ? "ml-auto bg-[var(--ink)] text-[var(--panel)]"
                  : "mr-auto border border-[var(--line)] bg-[var(--panel)] text-[var(--ink)]"
              }`}
            >
              <p className="mb-1 text-[10px] uppercase tracking-[0.14em] opacity-60">
                {message.role === "user" ? "Você" : kitName}
              </p>
              <div className="space-y-2 whitespace-pre-wrap">
                {message.parts.map((part, index) => {
                  if (part.type === "text") {
                    return <p key={`${message.id}-${index}`}>{part.text}</p>;
                  }
                  if (part.type.startsWith("tool-")) {
                    const toolName = part.type.replace(/^tool-/, "");
                    return (
                      <p
                        key={`${message.id}-${index}`}
                        className="rounded-md bg-[var(--chip)] px-2 py-1 font-mono text-[11px] text-[var(--accent-ink)]"
                      >
                        ferramenta · {toolName}
                      </p>
                    );
                  }
                  return null;
                })}
              </div>
            </article>
          );
        })}

        {busy ? (
          <p className="animate-pulse text-sm text-[var(--muted)]">
            Skill trabalhando…
          </p>
        ) : null}

        {!busy && messages.length === 0 ? (
          <div className="space-y-2">
            <p className="text-sm text-[var(--muted)]">
              Aguardando resposta da skill…
            </p>
            <button
              type="button"
              onClick={() => void startRun(prompt)}
              className="rounded-lg border border-[var(--line)] px-3 py-1.5 text-xs text-[var(--ink)]"
            >
              Reenviar pedido
            </button>
          </div>
        ) : null}

        {localError || error ? (
          <p className="rounded-xl border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800">
            {formatRunError(localError || error?.message || "Erro desconhecido")}
          </p>
        ) : null}
      </div>

      <form
        className="border-t border-[var(--line)] px-3 py-3"
        onSubmit={(e) => {
          e.preventDefault();
          sendFollowUp();
        }}
      >
        <div className="flex items-end gap-2">
          <textarea
            value={followUp}
            onChange={(e) => setFollowUp(e.target.value)}
            rows={2}
            placeholder="Ajuste o pedido ou peça outra variação…"
            className="min-h-[52px] flex-1 resize-none rounded-xl border border-[var(--line)] bg-[var(--panel)] px-3 py-2 text-sm text-[var(--ink)] outline-none focus:ring-2 focus:ring-[var(--accent)]"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                e.currentTarget.form?.requestSubmit();
              }
            }}
          />
          <button
            type="submit"
            disabled={busy || !followUp.trim()}
            className="rounded-xl bg-[var(--accent)] px-4 py-3 text-sm font-semibold text-[var(--accent-ink)] disabled:opacity-40"
          >
            Enviar
          </button>
        </div>
      </form>
    </section>
  );
}
