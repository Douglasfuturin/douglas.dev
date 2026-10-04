"use client";

import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";
import { useMemo, useState, type ReactNode } from "react";
import type { AgentMode, ResearchDepth } from "@/lib/agents/models";
import {
  DEFAULT_VIDEO_OPTIONS,
  STYLE_LABELS,
  VIDEO_STYLES,
  type VideoEditOptions,
  type VideoStyle,
  type WhisperModel,
} from "@/lib/video/options";

const MODE_LABELS: Record<AgentMode, string> = {
  auto: "Auto",
  chat: "Chat + tools",
  research: "Multi-agent research",
  video: "Editor de vídeo",
};

export function ChatApp() {
  const [input, setInput] = useState("");
  const [mode, setMode] = useState<AgentMode>("auto");
  const [researchDepth, setResearchDepth] = useState<ResearchDepth>("medium");
  const [videoOptions, setVideoOptions] =
    useState<VideoEditOptions>(DEFAULT_VIDEO_OPTIONS);
  const [uploadedPath, setUploadedPath] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

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
  const showVideoPanel = mode === "video" || mode === "auto";

  async function onUpload(file: File | null) {
    if (!file) return;
    setUploading(true);
    try {
      const body = new FormData();
      body.append("file", file);
      const res = await fetch("/api/upload", { method: "POST", body });
      const data = (await res.json()) as { path?: string; error?: string };
      if (!res.ok || !data.path) {
        throw new Error(data.error || "Falha no upload");
      }
      setUploadedPath(data.path);
      setMode("video");
      setInput((prev) =>
        prev.trim()
          ? prev
          : `Edita automaticamente este vídeo: ${data.path}`,
      );
    } catch (err) {
      alert(err instanceof Error ? err.message : "Erro no upload");
    } finally {
      setUploading(false);
    }
  }

  function patchVideo<K extends keyof VideoEditOptions>(
    key: K,
    value: VideoEditOptions[K],
  ) {
    setVideoOptions((prev) => ({ ...prev, [key]: value }));
  }

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
            Multi-agente + editor de vídeo automático com o kit de edição.
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
          {mode === "research" ? (
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

      <main className="relative z-10 mx-auto flex w-full max-w-3xl flex-1 flex-col px-5 pb-36">
        {showVideoPanel ? (
          <section className="mb-4 animate-rise rounded-2xl border border-[var(--line)] bg-[var(--panel)]/85 p-4 backdrop-blur">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
              <p className="text-sm font-medium text-[var(--ink)]">
                Editor de vídeo — opções
              </p>
              <label className="cursor-pointer rounded-lg bg-[var(--accent)] px-3 py-1.5 text-xs font-semibold text-[var(--accent-ink)]">
                {uploading ? "Enviando…" : "Upload MP4"}
                <input
                  type="file"
                  accept="video/*,.mp4,.mov,.mkv"
                  className="hidden"
                  disabled={uploading || busy}
                  onChange={(e) => onUpload(e.target.files?.[0] ?? null)}
                />
              </label>
            </div>

            {uploadedPath ? (
              <p className="mb-3 break-all font-mono text-xs text-[var(--muted)]">
                vídeo: {uploadedPath}
              </p>
            ) : null}

            <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
              <Field label="Estilo">
                <select
                  value={videoOptions.estilo}
                  onChange={(e) =>
                    patchVideo("estilo", e.target.value as VideoStyle)
                  }
                >
                  {VIDEO_STYLES.map((style) => (
                    <option key={style} value={style}>
                      {STYLE_LABELS[style]}
                    </option>
                  ))}
                </select>
              </Field>

              <Field label="Resolução">
                <select
                  value={videoOptions.resolution}
                  onChange={(e) =>
                    patchVideo(
                      "resolution",
                      e.target.value as VideoEditOptions["resolution"],
                    )
                  }
                >
                  <option value="1080p">1080p</option>
                  <option value="1440p">1440p</option>
                  <option value="4k">4K</option>
                </select>
              </Field>

              <Field label="Idioma">
                <select
                  value={videoOptions.language}
                  onChange={(e) => patchVideo("language", e.target.value)}
                >
                  <option value="pt">Português</option>
                  <option value="en">English</option>
                  <option value="es">Español</option>
                  <option value="auto">Auto</option>
                </select>
              </Field>

              <Field label="Whisper">
                <select
                  value={videoOptions.whisperModel}
                  onChange={(e) =>
                    patchVideo("whisperModel", e.target.value as WhisperModel)
                  }
                >
                  <option value="tiny">tiny (rápido)</option>
                  <option value="base">base</option>
                  <option value="small">small</option>
                  <option value="medium">medium</option>
                  <option value="large-v3">large-v3 (melhor)</option>
                </select>
              </Field>

              <Field label="Intro/outro">
                <select
                  value={videoOptions.introOutro}
                  onChange={(e) =>
                    patchVideo(
                      "introOutro",
                      e.target.value as VideoEditOptions["introOutro"],
                    )
                  }
                >
                  <option value="crt">CRT</option>
                  <option value="fade">Fade</option>
                  <option value="none">Nenhum</option>
                </select>
              </Field>

              <Field label="pause_keep">
                <input
                  type="number"
                  min={0}
                  step={0.1}
                  value={videoOptions.pauseKeep}
                  onChange={(e) =>
                    patchVideo("pauseKeep", Number(e.target.value))
                  }
                />
              </Field>

              <Field label="sil_cut (s)">
                <input
                  type="number"
                  min={0}
                  step={0.1}
                  value={videoOptions.silCut}
                  onChange={(e) => patchVideo("silCut", Number(e.target.value))}
                />
              </Field>

              <Field label="Crop 9:16">
                <input
                  type="text"
                  placeholder="crop=810:1440:555:0"
                  value={videoOptions.crop ?? ""}
                  onChange={(e) =>
                    patchVideo("crop", e.target.value || undefined)
                  }
                />
              </Field>

              <Field label="Projeto">
                <input
                  type="text"
                  value={videoOptions.projeto}
                  onChange={(e) => patchVideo("projeto", e.target.value)}
                />
              </Field>
            </div>

            <div className="mt-3 flex flex-wrap gap-4 text-sm text-[var(--ink)]">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={videoOptions.captions}
                  onChange={(e) => patchVideo("captions", e.target.checked)}
                />
                Legendas
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={videoOptions.autoConfirm}
                  onChange={(e) => patchVideo("autoConfirm", e.target.checked)}
                />
                Auto-confirmar plano
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={videoOptions.autoRender}
                  onChange={(e) => patchVideo("autoRender", e.target.checked)}
                />
                Render automático
              </label>
            </div>
          </section>
        ) : null}

        <div className="flex flex-1 flex-col gap-4 overflow-y-auto py-2">
          {messages.length === 0 ? (
            <EmptyState
              mode={mode}
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
              {mode === "video"
                ? "Editor trabalhando no pipeline…"
                : "Agentes trabalhando…"}
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
                videoOptions,
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
            placeholder={
              mode === "video"
                ? "Ex: edita automaticamente o vídeo enviado em reel-mono com legendas"
                : "Pergunte algo… ou peça para editar um vídeo"
            }
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

function Field({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <label className="block text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">
      {label}
      <div className="mt-1 [&_input]:w-full [&_input]:rounded-md [&_input]:border [&_input]:border-[var(--line)] [&_input]:bg-white/80 [&_input]:px-2 [&_input]:py-1.5 [&_input]:text-sm [&_input]:normal-case [&_input]:tracking-normal [&_input]:text-[var(--ink)] [&_select]:w-full [&_select]:rounded-md [&_select]:border [&_select]:border-[var(--line)] [&_select]:bg-white/80 [&_select]:px-2 [&_select]:py-1.5 [&_select]:text-sm [&_select]:normal-case [&_select]:tracking-normal [&_select]:text-[var(--ink)]">
        {children}
      </div>
    </label>
  );
}

function EmptyState({
  mode,
  onPick,
}: {
  mode: AgentMode;
  onPick: (prompt: string) => void;
}) {
  const prompts =
    mode === "video"
      ? [
          "Lista os estilos de edição disponíveis no kit",
          "Edita automaticamente o vídeo em workspace/videos — estilo reel-mono com legendas",
          "Monta um plano de aula-ccnp, roda dry-run e só renderiza se eu confirmar",
        ]
      : [
          "O que é o modelo grok-4.20-multi-agent e quando usar?",
          "Pesquise nas últimas notícias o que está rolando sobre agentes de IA",
          "Quero editar um vídeo: corte silêncios, trate a voz e gere um reel",
        ];

  return (
    <section className="animate-rise mt-2 space-y-4">
      <p className="text-sm text-[var(--muted)]">
        {mode === "video"
          ? "Upload um MP4, escolha estilo/opções e peça a edição automática."
          : "Chat, research multi-agente, ou editor de vídeo com o kit."}
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
