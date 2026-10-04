"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type {
  AgentLogEntry,
  EditorView,
  MediaAnalysis,
  TakeWindow,
} from "@/lib/editor/types";
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
} from "@/lib/video/options";
import { CodeWorkspace } from "./code-workspace";
import { Timeline } from "./timeline";
import { VideoPreview } from "./video-preview";

function mediaUrl(path: string) {
  return `/api/media?path=${encodeURIComponent(path)}`;
}

export function EditorApp() {
  const searchParams = useSearchParams();
  const initialView = searchParams.get("view");
  const [view, setView] = useState<EditorView>(
    initialView === "code" ? "code" : "visual",
  );
  const [analysis, setAnalysis] = useState<MediaAnalysis | null>(null);
  const [takes, setTakes] = useState<TakeWindow[]>([]);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [zoom, setZoom] = useState(1.2);
  const [filmstrip, setFilmstrip] = useState<string[]>([]);
  const [command, setCommand] = useState("");
  const [automation, setAutomation] = useState(true);
  const [busy, setBusy] = useState(false);
  const [logs, setLogs] = useState<AgentLogEntry[]>([]);
  const [uploading, setUploading] = useState(false);
  const [editOptions, setEditOptions] = useState<VideoEditOptions>(
    DEFAULT_VIDEO_OPTIONS,
  );
  const bootstrapped = useRef<string | null>(null);

  function patchEdit<K extends keyof VideoEditOptions>(
    key: K,
    value: VideoEditOptions[K],
  ) {
    setEditOptions((prev) => ({ ...prev, [key]: value }));
  }

  const src = analysis ? mediaUrl(analysis.path) : null;

  const caption = useMemo(() => {
    if (!analysis?.transcript.length) return undefined;
    const cue = analysis.transcript.find(
      (c) => currentTime >= c.start && currentTime <= c.end,
    );
    if (!cue) return undefined;
    const words = cue.text.split(/\s+/).filter(Boolean);
    return words.slice(0, 3).join(" ").toUpperCase();
  }, [analysis, currentTime]);

  const pushLog = useCallback((text: string) => {
    setLogs((prev) => [
      ...prev,
      {
        id: `${Date.now()}-${Math.random()}`,
        at: new Date().toLocaleTimeString("pt-BR", { hour12: false }),
        text,
      },
    ]);
  }, []);

  const analyzePath = useCallback(
    async (path: string, transcribe = true) => {
      setBusy(true);
      pushLog(`Analisando ${path.split("/").pop()}…`);
      try {
        const res = await fetch("/api/editor/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ path, transcribe }),
        });
        const data = (await res.json()) as MediaAnalysis & { error?: string };
        if (!res.ok) throw new Error(data.error || "Falha na análise");
        setAnalysis(data);
        setTakes(data.takes);
        setDuration(data.duration);
        setCurrentTime(0);
        pushLog(
          `Material lido: ${data.duration}s · ${data.width}x${data.height} · ${data.fat.length} trechos de gordura`,
        );
        if (data.transcript.length) {
          pushLog(`Transcript com ${data.transcript.length} falas`);
        }
      } catch (err) {
        pushLog(err instanceof Error ? err.message : "Erro na análise");
      } finally {
        setBusy(false);
      }
    },
    [pushLog],
  );

  const queryPath = searchParams.get("path");
  const queryTranscribe = searchParams.get("transcribe") !== "0";

  useEffect(() => {
    const path =
      queryPath || new URLSearchParams(window.location.search).get("path");
    if (!path || bootstrapped.current === path) return;
    bootstrapped.current = path;
    const transcribe =
      new URLSearchParams(window.location.search).get("transcribe") !== "0";
    void analyzePath(path, queryPath ? queryTranscribe : transcribe);
  }, [analyzePath, queryPath, queryTranscribe]);

  async function onUpload(file: File | null) {
    if (!file) return;
    setUploading(true);
    try {
      const body = new FormData();
      body.append("file", file);
      const res = await fetch("/api/upload", { method: "POST", body });
      const data = (await res.json()) as { path?: string; error?: string };
      if (!res.ok || !data.path) throw new Error(data.error || "Upload falhou");
      pushLog(`Upload ok: ${data.path}`);
      await analyzePath(data.path, true);
      setView("visual");
    } catch (err) {
      pushLog(err instanceof Error ? err.message : "Erro no upload");
    } finally {
      setUploading(false);
    }
  }

  // Build filmstrip from video element once loaded
  useEffect(() => {
    if (!src || !duration) return;
    let cancelled = false;
    const video = document.createElement("video");
    video.src = src;
    video.muted = true;
    video.playsInline = true;
    video.preload = "auto";

    const capture = async () => {
      await new Promise<void>((resolve, reject) => {
        video.onloadeddata = () => resolve();
        video.onerror = () => reject(new Error("preview load failed"));
      });
      const canvas = document.createElement("canvas");
      canvas.width = 120;
      canvas.height = 214;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      const frames = 12;
      const shots: string[] = [];
      for (let i = 0; i < frames; i++) {
        const t = (duration * i) / Math.max(frames - 1, 1);
        await new Promise<void>((resolve) => {
          video.onseeked = () => resolve();
          video.currentTime = Math.min(t, Math.max(duration - 0.05, 0));
        });
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        shots.push(canvas.toDataURL("image/jpeg", 0.7));
      }
      if (!cancelled) setFilmstrip(shots);
    };

    void capture().catch(() => undefined);

    return () => {
      cancelled = true;
      video.src = "";
    };
  }, [src, duration]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      const tag = (e.target as HTMLElement | null)?.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA") return;
      if (e.code === "Space") {
        e.preventDefault();
        setPlaying((p) => !p);
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        setCurrentTime((t) =>
          Math.min(duration, t + (e.shiftKey ? 1 : 1 / 30)),
        );
        setPlaying(false);
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        setCurrentTime((t) => Math.max(0, t - (e.shiftKey ? 1 : 1 / 30)));
        setPlaying(false);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [duration]);

  async function runCommand() {
    const text = command.trim();
    if (!text || !analysis) return;
    setBusy(true);
    pushLog(`Comando: ${text}`);

    try {
      if (/transcrev/i.test(text)) {
        await analyzePath(analysis.path, true);
        setCommand("");
        return;
      }

      if (/aplic(a|ar)?\s*corte|aprova|render|edita/i.test(text) && automation) {
        const res = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            mode: "video",
            videoOptions: {
              ...editOptions,
              autoConfirm: true,
              autoRender: true,
              estilo:
                editOptions.estilo ||
                (analysis.orientation === "vertical" ? "reel-mono" : "aula-ccnp"),
            },
            messages: [
              {
                id: "cmd-1",
                role: "user",
                parts: [
                  {
                    type: "text",
                    text: `${text}. Vídeo: ${analysis.path}. Takes: ${JSON.stringify(takes)}. Use auto_edit_video ou create_edit_plan + dry_run_edit + render_edit.`,
                  },
                ],
              },
            ],
          }),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(
            (err as { error?: string }).error ||
              `Falha no agente (${res.status}). Configure XAI_API_KEY.`,
          );
        }
        pushLog("Agente de vídeo acionado — acompanhe o pipeline nas tools.");
        setAnalysis((prev) =>
          prev
            ? {
                ...prev,
                statusNote: `${prev.filename.replace(/\.[^.]+$/, "")} v2 – corte pelos takes aprovados. Revise o render.`,
              }
            : prev,
        );
        setCommand("");
        return;
      }

      // local visual ops
      if (/remove.*sil[eê]ncio|corta gordura|aperta/i.test(text)) {
        setTakes((prev) => prev);
        setAnalysis((prev) =>
          prev
            ? {
                ...prev,
                statusNote: `${prev.filename.replace(/\.[^.]+$/, "")} v2 – silêncios marcados removidos na timeline. ${takes
                  .reduce((a, t) => a + (t.end - t.start), 0)
                  .toFixed(2)
                  .replace(".", ",")}s. Revise e aprove.`,
              }
            : prev,
        );
        pushLog("Timeline atualizada com takes sem a gordura marcada.");
        setView("visual");
        setCommand("");
        return;
      }

      pushLog("Comando registrado. Use Visual para revisar takes e playhead.");
      setCommand("");
    } catch (err) {
      pushLog(err instanceof Error ? err.message : "Erro no comando");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex items-center justify-between gap-3 border-b border-white/10 px-4 py-3">
        <div className="flex items-center gap-4">
          <Link href="/" className="flex items-center gap-2">
            <span className="flex flex-col gap-[3px]">
              <i className="block h-[3px] w-7 rounded-full bg-[#ff7a1a]" />
              <i className="block h-[3px] w-7 rounded-full bg-[#f5d76e]" />
              <i className="block h-[3px] w-7 rounded-full bg-[#6dd3a7]" />
              <i className="block h-[3px] w-7 rounded-full bg-[#5aa7ff]" />
            </span>
            <span className="font-display text-lg font-bold tracking-[0.2em]">
              EDVD
            </span>
          </Link>

          <div className="flex rounded-lg bg-white/5 p-1">
            <button
              type="button"
              onClick={() => setView("code")}
              className={`rounded-md px-3 py-1.5 text-sm ${
                view === "code"
                  ? "bg-[#ff7a1a] text-black font-semibold"
                  : "text-white/60"
              }`}
            >
              Code
            </button>
            <button
              type="button"
              onClick={() => setView("visual")}
              className={`rounded-md px-3 py-1.5 text-sm ${
                view === "visual"
                  ? "bg-white/15 text-white font-semibold"
                  : "text-white/60"
              }`}
            >
              Visual
            </button>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <label className="cursor-pointer rounded-lg border border-white/15 px-3 py-1.5 text-sm text-white/80 hover:bg-white/5">
            {uploading ? "Enviando…" : "Upload"}
            <input
              type="file"
              accept="video/*,.mp4,.mov,.webm"
              className="hidden"
              disabled={uploading || busy}
              onChange={(e) => onUpload(e.target.files?.[0] ?? null)}
            />
          </label>
          <button
            type="button"
            className="rounded-lg border border-white/15 px-3 py-1.5 text-sm text-white/70"
            title="feedback"
          >
            👍
          </button>
          <button
            type="button"
            className="rounded-lg border border-white/15 px-3 py-1.5 text-sm text-white/70"
            title="feedback"
          >
            👎
          </button>
          <button
            type="button"
            onClick={() => {
              setView("code");
              setCommand("Perguntar: o que cortar neste vídeo?");
            }}
            className="rounded-lg bg-[#ff7a1a] px-3 py-1.5 text-sm font-semibold text-black"
          >
            Perguntar
          </button>
        </div>
      </header>

      {analysis?.statusNote ? (
        <div className="border-b border-white/10 bg-[#151922] px-4 py-2 text-sm text-white/75">
          {analysis.statusNote}
        </div>
      ) : null}

      <main className="flex flex-1 flex-col gap-4 px-4 py-4">
        {view === "visual" ? (
          <>
            <div className="flex flex-1 flex-col items-center justify-center py-2">
              <VideoPreview
                src={src}
                currentTime={currentTime}
                playing={playing}
                caption={caption}
                onTime={setCurrentTime}
                onDuration={(d) => {
                  if (d > 0) setDuration(d);
                }}
                onPlayingChange={setPlaying}
              />
            </div>

            <div className="mx-auto flex w-full max-w-5xl items-center justify-center gap-3">
              <button
                type="button"
                onClick={() => setCurrentTime((t) => Math.max(0, t - 1 / 30))}
                className="rounded-full border border-white/15 px-3 py-2 text-sm"
              >
                ‹
              </button>
              <button
                type="button"
                onClick={() => setPlaying((p) => !p)}
                className="rounded-full bg-white px-5 py-2 text-sm font-semibold text-black"
              >
                {playing ? "Pause" : "Play"}
              </button>
              <button
                type="button"
                onClick={() =>
                  setCurrentTime((t) => Math.min(duration, t + 1 / 30))
                }
                className="rounded-full border border-white/15 px-3 py-2 text-sm"
              >
                ›
              </button>
            </div>

            <div className="mx-auto w-full max-w-5xl">
              <Timeline
                duration={duration || analysis?.duration || 0}
                currentTime={currentTime}
                waveform={analysis?.waveform ?? []}
                takes={takes}
                zoom={zoom}
                filmstrip={filmstrip}
                onSeek={(t) => {
                  setCurrentTime(t);
                  setPlaying(false);
                }}
                onZoom={setZoom}
                onTakeChange={(id, start, end) => {
                  setTakes((prev) =>
                    prev.map((take) =>
                      take.id === id ? { ...take, start, end } : take,
                    ),
                  );
                }}
              />
            </div>
          </>
        ) : (
          <CodeWorkspace analysis={analysis} logs={logs} busy={busy} />
        )}
      </main>

      <footer className="border-t border-white/10 px-4 py-3">
        <div className="mx-auto flex w-full max-w-5xl flex-col gap-2">
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">
            <label className="flex flex-col gap-1 text-[10px] uppercase tracking-wider text-white/40">
              Estilo
              <select
                value={editOptions.estilo}
                onChange={(e) =>
                  patchEdit("estilo", e.target.value as VideoStyle)
                }
                className="rounded-lg border border-white/10 bg-[#12151a] px-2 py-1.5 text-xs text-white"
              >
                {VIDEO_STYLES.map((s) => (
                  <option key={s} value={s}>
                    {STYLE_LABELS[s]}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-[10px] uppercase tracking-wider text-white/40">
              Formato
              <select
                value={editOptions.formato}
                onChange={(e) =>
                  patchEdit("formato", e.target.value as VideoFormat)
                }
                className="rounded-lg border border-white/10 bg-[#12151a] px-2 py-1.5 text-xs text-white"
              >
                {VIDEO_FORMATS.map((f) => (
                  <option key={f} value={f}>
                    {f}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-[10px] uppercase tracking-wider text-white/40">
              Fonte
              <select
                value={editOptions.fonte}
                onChange={(e) =>
                  patchEdit("fonte", e.target.value as VideoFont)
                }
                className="rounded-lg border border-white/10 bg-[#12151a] px-2 py-1.5 text-xs text-white"
              >
                {VIDEO_FONTS.map((f) => (
                  <option key={f} value={f}>
                    {FONT_LABELS[f]}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-[10px] uppercase tracking-wider text-white/40">
              Grade
              <select
                value={editOptions.grade}
                onChange={(e) =>
                  patchEdit("grade", e.target.value as VideoGrade)
                }
                className="rounded-lg border border-white/10 bg-[#12151a] px-2 py-1.5 text-xs text-white"
              >
                {VIDEO_GRADES.map((g) => (
                  <option key={g} value={g}>
                    {g}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-[10px] uppercase tracking-wider text-white/40">
              Emenda
              <select
                value={editOptions.efeitoEmenda}
                onChange={(e) =>
                  patchEdit(
                    "efeitoEmenda",
                    e.target.value as VideoEditOptions["efeitoEmenda"],
                  )
                }
                className="rounded-lg border border-white/10 bg-[#12151a] px-2 py-1.5 text-xs text-white"
              >
                <option value="none">Nenhum</option>
                <option value="glitch">Glitch</option>
                <option value="flash">Flash</option>
                <option value="whip">Whip</option>
              </select>
            </label>
            <label className="flex flex-col gap-1 text-[10px] uppercase tracking-wider text-white/40">
              Som
              <select
                value={editOptions.som}
                onChange={(e) => patchEdit("som", e.target.value as VideoSound)}
                className="rounded-lg border border-white/10 bg-[#12151a] px-2 py-1.5 text-xs text-white"
              >
                {VIDEO_SOUNDS.map((s) => (
                  <option key={s} value={s}>
                    {SOUND_LABELS[s]}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="flex items-center gap-2">
            <input
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") void runCommand();
              }}
              placeholder="Digite para comandos — ex: corta gordura · transcreve · edita automaticamente"
              className="flex-1 rounded-xl border border-white/10 bg-[#12151a] px-3 py-3 text-sm text-white outline-none ring-[#ff7a1a] placeholder:text-white/30 focus:ring-2"
            />
            <label className="flex items-center gap-2 rounded-xl border border-white/10 px-3 py-3 text-xs text-white/60">
              <input
                type="checkbox"
                checked={automation}
                onChange={(e) => setAutomation(e.target.checked)}
              />
              Automação
            </label>
            <button
              type="button"
              disabled={!command.trim() || busy || !analysis}
              onClick={() => void runCommand()}
              className="rounded-xl bg-[#ff7a1a] px-4 py-3 text-sm font-semibold text-black disabled:opacity-40"
            >
              Enviar
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}
