"use client";

import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";
import Link from "next/link";
import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import type { AgentMode, ResearchDepth } from "@/lib/agents/models";
import {
  extractRadarBriefing,
  RadarApprovalCards,
  type RadarCardItem,
} from "@/components/radar-approval-cards";
import {
  DEFAULT_VIDEO_OPTIONS,
  FONT_LABELS,
  SOUND_LABELS,
  STYLE_LABELS,
  VIDEO_FONTS,
  VIDEO_FORMATS,
  VIDEO_GRADES,
  VIDEO_SOUNDS,
  VIDEO_STYLES,
  type VideoEditOptions,
  type VideoFont,
  type VideoFormat,
  type VideoGrade,
  type VideoSound,
  type VideoStyle,
  type WhisperModel,
} from "@/lib/video/options";

const MODE_LABELS: Record<AgentMode, string> = {
  auto: "Automático",
  chat: "Chat + ferramentas",
  research: "Pesquisa multiagente",
  radar: "Radar de Tendências",
  github: "GitHub Scout",
  roteiro: "Roteirista Reels",
  notion: "Notion Guide",
  pipeline: "Pack Scout→Reels→Notion",
  video: "Editor de vídeo",
  kits: "Skills Ninja",
};

function readQueryMode(): AgentMode {
  if (typeof window === "undefined") return "auto";
  const params = new URLSearchParams(window.location.search);
  const m = params.get("mode");
  if (
    m === "kits" ||
    m === "video" ||
    m === "chat" ||
    m === "research" ||
    m === "github" ||
    m === "roteiro" ||
    m === "notion" ||
    m === "pipeline" ||
    m === "radar" ||
    m === "auto"
  ) {
    return m;
  }
  if (params.get("kit")) return "kits";
  return "auto";
}

function readQueryKitId(): string {
  if (typeof window === "undefined") return "";
  return new URLSearchParams(window.location.search).get("kit") || "";
}

function readQueryPrompt(): string {
  if (typeof window === "undefined") return "";
  return new URLSearchParams(window.location.search).get("q") || "";
}

function readQueryAutosend(): boolean {
  if (typeof window === "undefined") return false;
  return new URLSearchParams(window.location.search).get("autosend") === "1";
}

function readHandoff(): {
  kitId?: string;
  prompt?: string;
  autosend?: boolean;
} | null {
  if (typeof window === "undefined") return null;
  const params = new URLSearchParams(window.location.search);
  if (params.get("handoff") !== "1") return null;
  try {
    const raw = sessionStorage.getItem("grokish-skill-handoff");
    if (!raw) return null;
    sessionStorage.removeItem("grokish-skill-handoff");
    return JSON.parse(raw) as {
      kitId?: string;
      prompt?: string;
      autosend?: boolean;
    };
  } catch {
    return null;
  }
}

export function ChatApp() {
  const [handoff] = useState(readHandoff);
  const [input, setInput] = useState(
    () => handoff?.prompt || readQueryPrompt(),
  );
  const [mode, setMode] = useState<AgentMode>(() =>
    handoff?.kitId ? "kits" : readQueryMode(),
  );
  const [researchDepth, setResearchDepth] = useState<ResearchDepth>("medium");
  const [kitId, setKitId] = useState<string>(
    () => handoff?.kitId || readQueryKitId(),
  );
  const [kitOptions, setKitOptions] = useState<Array<{ id: string; name: string }>>(
    [],
  );
  const [videoOptions, setVideoOptions] =
    useState<VideoEditOptions>(DEFAULT_VIDEO_OPTIONS);
  const [uploadedPath, setUploadedPath] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const autosendRef = useRef(Boolean(handoff?.autosend) || readQueryAutosend());

  useEffect(() => {
    let alive = true;
    fetch("/api/kits")
      .then((r) => r.json())
      .then(
        (data: {
          kits?: Array<{ id: string; name: string }>;
          inventory?: Array<{ id: string; name?: string; status: string }>;
        }) => {
          if (!alive) return;
          const fromInventory = (data.inventory || []).map((k) => ({
            id: k.id,
            name: k.name || k.id,
          }));
          const fromInstalled = (data.kits || []).map((k) => ({
            id: k.id,
            name: k.name,
          }));
          const map = new Map<string, { id: string; name: string }>();
          for (const k of [...fromInventory, ...fromInstalled]) {
            map.set(k.id, k);
          }
          setKitOptions(
            [...map.values()].sort((a, b) => a.id.localeCompare(b.id)),
          );
        },
      )
      .catch(() => undefined);
    return () => {
      alive = false;
    };
  }, []);

  const transport = useMemo(
    () =>
      new DefaultChatTransport({
        api: "/api/chat",
        body: {
          mode,
          researchDepth,
          videoOptions,
          kitId: kitId || undefined,
        },
      }),
    [mode, researchDepth, videoOptions, kitId],
  );

  const { messages, sendMessage, status, error, stop } = useChat({
    transport,
  });

  const busy = status === "submitted" || status === "streaming";
  const showVideoPanel = mode === "video" || mode === "auto";

  function approveTrendForRoteirista(item: RadarCardItem) {
    const prompt =
      item.approvePrompt ||
      [
        "Crie um roteiro de Reels de ~60 segundos sobre esta tendência APROVADA do Radar:",
        "",
        `Manchete: ${item.headline}`,
        `Ângulo: ${item.angle}`,
        `Resumo: ${item.summary}`,
        `Por que agora: ${item.whyNow}`,
        "",
        "Use prepare_trend_for_reels e deliver_reels_script.",
      ].join("\n");
    setMode("roteiro");
    void sendMessage(
      { text: prompt },
      {
        body: {
          mode: "roteiro",
          researchDepth,
          videoOptions,
        },
      },
    );
  }

  // Dashboard → agent handoff: autosend once (sessionStorage or ?q=)
  useEffect(() => {
    if (!autosendRef.current) return;
    const prompt = (handoff?.prompt || readQueryPrompt()).trim();
    autosendRef.current = false;
    if (!prompt) return;
    try {
      const url = new URL(window.location.href);
      url.searchParams.delete("autosend");
      url.searchParams.delete("handoff");
      window.history.replaceState({}, "", url.toString());
    } catch {
      /* ignore */
    }
    void sendMessage(
      { text: prompt },
      {
        body: {
          mode: "kits",
          kitId: kitId || undefined,
        },
      },
    );
  }, [handoff, kitId, sendMessage]);

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
            Multi-agente + radar + roteiros + Scout + Notion.
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            <Link
              href="/kits"
              className="inline-flex rounded-lg bg-[var(--ink)] px-3 py-1.5 text-xs font-semibold text-[var(--panel)]"
            >
              Painel de Skills →
            </Link>
            <button
              type="button"
              onClick={() => setMode("radar")}
              className="inline-flex rounded-lg border border-[var(--line)] px-3 py-1.5 text-xs font-semibold text-[var(--ink)]"
            >
              Radar
            </button>
            <button
              type="button"
              onClick={() => setMode("pipeline")}
              className="inline-flex rounded-lg border border-[var(--line)] px-3 py-1.5 text-xs font-semibold text-[var(--ink)]"
            >
              Pack completo
            </button>
            <button
              type="button"
              onClick={() => setMode("github")}
              className="inline-flex rounded-lg border border-[var(--line)] px-3 py-1.5 text-xs font-semibold text-[var(--ink)]"
            >
              GitHub Scout
            </button>
            <button
              type="button"
              onClick={() => setMode("roteiro")}
              className="inline-flex rounded-lg border border-[var(--line)] px-3 py-1.5 text-xs font-semibold text-[var(--ink)]"
            >
              Roteirista
            </button>
            <button
              type="button"
              onClick={() => setMode("notion")}
              className="inline-flex rounded-lg border border-[var(--line)] px-3 py-1.5 text-xs font-semibold text-[var(--ink)]"
            >
              Notion
            </button>
            <Link
              href="/editor"
              className="inline-flex rounded-lg border border-[var(--line)] px-3 py-1.5 text-xs font-semibold text-[var(--ink)]"
            >
              Editor EDVD
            </Link>
          </div>
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
          {mode === "kits" || mode === "auto" ? (
            <label className="text-[11px] uppercase tracking-[0.18em] text-[var(--muted)]">
              Kit ativo
              <select
                className="mt-1 block max-w-[200px] rounded-md border border-[var(--line)] bg-[var(--panel)] px-2 py-1.5 text-sm text-[var(--ink)]"
                value={kitId}
                onChange={(e) => {
                  setKitId(e.target.value);
                  if (e.target.value) setMode("kits");
                }}
              >
                <option value="">Todas as skills</option>
                {kitOptions.map((k) => (
                  <option key={k.id} value={k.id}>
                    {k.name}
                  </option>
                ))}
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

              <Field label="Formato">
                <select
                  value={videoOptions.formato}
                  onChange={(e) =>
                    patchVideo("formato", e.target.value as VideoFormat)
                  }
                >
                  {VIDEO_FORMATS.map((f) => (
                    <option key={f} value={f}>
                      {f}
                    </option>
                  ))}
                </select>
              </Field>

              <Field label="Fonte">
                <select
                  value={videoOptions.fonte}
                  onChange={(e) =>
                    patchVideo("fonte", e.target.value as VideoFont)
                  }
                >
                  {VIDEO_FONTS.map((f) => (
                    <option key={f} value={f}>
                      {FONT_LABELS[f]}
                    </option>
                  ))}
                </select>
              </Field>

              <Field label="Grade de cor">
                <select
                  value={videoOptions.grade}
                  onChange={(e) =>
                    patchVideo("grade", e.target.value as VideoGrade)
                  }
                >
                  {VIDEO_GRADES.map((g) => (
                    <option key={g} value={g}>
                      {g}
                    </option>
                  ))}
                </select>
              </Field>

              <Field label="Efeito emenda">
                <select
                  value={videoOptions.efeitoEmenda}
                  onChange={(e) =>
                    patchVideo(
                      "efeitoEmenda",
                      e.target.value as VideoEditOptions["efeitoEmenda"],
                    )
                  }
                >
                  <option value="none">Nenhum</option>
                  <option value="glitch">Glitch CRT/VHS</option>
                  <option value="flash">Flash branco</option>
                  <option value="whip">Whip pan</option>
                </select>
              </Field>

              <Field label="Intensidade">
                <select
                  value={videoOptions.intensidade}
                  onChange={(e) =>
                    patchVideo(
                      "intensidade",
                      e.target.value as VideoEditOptions["intensidade"],
                    )
                  }
                >
                  <option value="subtle">Subtle</option>
                  <option value="medium">Medium</option>
                  <option value="strong">Strong</option>
                </select>
              </Field>

              <Field label="Som / SFX">
                <select
                  value={videoOptions.som}
                  onChange={(e) =>
                    patchVideo("som", e.target.value as VideoSound)
                  }
                >
                  {VIDEO_SOUNDS.map((s) => (
                    <option key={s} value={s}>
                      {SOUND_LABELS[s]}
                    </option>
                  ))}
                </select>
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
                    const briefing = extractRadarBriefing(part);
                    return (
                      <div key={`${message.id}-${index}`} className="space-y-2">
                        <p className="rounded-md bg-[var(--chip)] px-2 py-1 font-mono text-xs text-[var(--accent-ink)]">
                          tool · {toolName}
                        </p>
                        {briefing ? (
                          <RadarApprovalCards
                            date={briefing.date}
                            items={briefing.items}
                            busy={busy}
                            onApprove={approveTrendForRoteirista}
                          />
                        ) : null}
                      </div>
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
                kitId: kitId || undefined,
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
                : mode === "radar"
                  ? "Ex: Monta o briefing diário de IA, automação e marketing"
                  : "Pergunte algo… ou peça o radar / um roteiro"
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
      : mode === "kits"
        ? [
            "Abra o dashboard em /kits e escolha uma skill para executar",
            "Lista todas as skills Ninja disponíveis e o que cada uma faz",
            "Descreve a skill ativa e entregue um resultado de exemplo",
          ]
        : mode === "github"
          ? [
              "Quais os melhores repositórios de agentes de IA em TypeScript?",
              "Ache libs open-source de edição de vídeo no GitHub e ranqueie",
              "Compare vercel/ai com langchainjs e diga qual usar para um chatbot",
            ]
          : mode === "roteiro"
            ? [
                "Roteiro de Reels 60s sobre vercel/ai",
                "Escreva um roteiro hype de 60 segundos sobre shadcn-ui/ui",
                "Monte o script falado + texto de tela para um Reels do supabase/supabase",
              ]
            : mode === "notion"
              ? [
                  "Publique no Notion o guia de instalação do vercel/ai",
                  "Crie um arquivo/página Notion com link + como usar o repo supabase/supabase",
                  "Exporte o markdown de guia do repositório facebook/react",
                ]
              : mode === "pipeline"
                ? [
                    "Pacote completo: melhores repos de agentes IA em TypeScript + roteiro 60s + guia Notion",
                    "Gera o pack Scout→Reels→Notion sobre edição de vídeo open-source",
                    "Roda o pipeline no repo vercel/ai (roteiro + Notion)",
                  ]
                : mode === "radar"
                  ? [
                      "Monta o briefing diário de automação, IA e marketing",
                      "Quais as melhores notícias de IA de hoje para eu aprovar um Reels?",
                      "Radar de tendências: top histórias + ângulos para conteúdo",
                    ]
                  : [
                      "O que é o modelo grok-4.20-multi-agent e quando usar?",
                      "Pesquise nas últimas notícias o que está rolando sobre agentes de IA",
                      "Lista os kits Ninja disponíveis e o que cada um faz",
                    ];

  return (
    <section className="animate-rise mt-2 space-y-4">
      <p className="text-sm text-[var(--muted)]">
        {mode === "video"
          ? "Upload um MP4, escolha estilo/opções e peça a edição automática."
          : mode === "kits"
            ? "Skill ativa via dashboard /kits — descreva o pedido ou use um atalho."
            : mode === "github"
              ? "Descreva o tema/stack — o scout busca e ranqueia os melhores repos no GitHub."
              : mode === "roteiro"
                ? "Passe o owner/repo ou uma tendência aprovada — Reels de ~60s."
                : mode === "notion"
                  ? "Passe o repo — o agente gera arquivo/página Notion com link, instalação e uso."
                  : mode === "pipeline"
                    ? "Uma tacada: escolhe o melhor repo → roteiro Reels 60s → guia Notion."
                    : mode === "radar"
                      ? "Briefing diário de IA, automação e marketing — aprove um card para o Roteirista."
                      : "Chat, radar, Scout, pack, roteiros, Notion, kits ou editor."}
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
