"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { EditorProject } from "@/lib/editor/project-types";
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
import { ProjectHub } from "./project-hub";
import { Timeline } from "./timeline";
import { VideoPreview } from "./video-preview";

function mediaUrl(path: string) {
  return `/api/media?path=${encodeURIComponent(path)}`;
}

type Screen = "hub" | "editor";

export function EditorApp() {
  const searchParams = useSearchParams();
  const initialView = searchParams.get("view");
  const queryProject = searchParams.get("project");

  const [screen, setScreen] = useState<Screen>("hub");
  const [projects, setProjects] = useState<EditorProject[]>([]);
  const [activeProject, setActiveProject] = useState<EditorProject | null>(null);
  const [projectsLoading, setProjectsLoading] = useState(true);

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
  const [outputUrl, setOutputUrl] = useState<string | null>(null);
  const bootstrapped = useRef<string | null>(null);
  const persistTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const activeProjectIdRef = useRef<string | null>(null);

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

  const refreshProjects = useCallback(async () => {
    const res = await fetch("/api/editor/projects");
    const data = (await res.json()) as {
      projects?: EditorProject[];
      activeProjectId?: string | null;
      error?: string;
    };
    if (!res.ok) throw new Error(data.error || "Falha ao listar projetos");
    setProjects(data.projects ?? []);
    return data;
  }, []);

  const persistProject = useCallback(
    async (
      projectId: string,
      patch: Partial<{
        name: string;
        description: string;
        estilo: VideoStyle;
        options: VideoEditOptions;
        mediaPath: string | null;
        mediaFilename: string | null;
        takes: TakeWindow[];
        analysisSummary: EditorProject["analysisSummary"];
        outputUrl: string | null;
      }>,
      opts?: { silent?: boolean },
    ) => {
      const res = await fetch(`/api/editor/projects/${projectId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(patch),
      });
      const data = (await res.json()) as {
        project?: EditorProject;
        error?: string;
      };
      if (!res.ok || !data.project) {
        if (!opts?.silent) {
          pushLog(data.error || "Falha ao salvar projeto");
        }
        return null;
      }
      setActiveProject(data.project);
      setProjects((prev) =>
        prev
          .map((p) => (p.id === data.project!.id ? data.project! : p))
          .sort((a, b) => b.updatedAt.localeCompare(a.updatedAt)),
      );
      return data.project;
    },
    [pushLog],
  );

  const schedulePersist = useCallback(
    (projectId: string, patch: Parameters<typeof persistProject>[1]) => {
      if (persistTimer.current) clearTimeout(persistTimer.current);
      persistTimer.current = setTimeout(() => {
        void persistProject(projectId, patch, { silent: true });
      }, 400);
    },
    [persistProject],
  );

  const applyProjectSession = useCallback(
    (project: EditorProject) => {
      activeProjectIdRef.current = project.id;
      setActiveProject(project);
      setEditOptions({
        ...project.options,
        estilo: project.estilo,
        projeto: project.slug,
      });
      setTakes(project.takes);
      setOutputUrl(project.outputUrl);
      setCurrentTime(0);
      setFilmstrip([]);
      setLogs([]);
      setCommand("");
      setScreen("editor");
      pushLog(`Projeto aberto: ${project.name} (${STYLE_LABELS[project.estilo]})`);
    },
    [pushLog],
  );

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

        const projectId = activeProjectIdRef.current;
        if (projectId) {
          void persistProject(projectId, {
            mediaPath: data.path,
            mediaFilename: data.filename,
            takes: data.takes,
            analysisSummary: {
              duration: data.duration,
              width: data.width,
              height: data.height,
              orientation: data.orientation,
              statusNote: data.statusNote,
            },
          });
        }
      } catch (err) {
        pushLog(err instanceof Error ? err.message : "Erro na análise");
      } finally {
        setBusy(false);
      }
    },
    [persistProject, pushLog],
  );

  const openProject = useCallback(
    async (projectId: string) => {
      setBusy(true);
      try {
        await fetch("/api/editor/projects", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ action: "activate", projectId }),
        });
        const res = await fetch(`/api/editor/projects/${projectId}`);
        const data = (await res.json()) as {
          project?: EditorProject;
          error?: string;
        };
        if (!res.ok || !data.project) {
          throw new Error(data.error || "Projeto não encontrado");
        }
        applyProjectSession(data.project);
        if (data.project.mediaPath) {
          await analyzePath(data.project.mediaPath, false);
          if (data.project.takes.length) {
            setTakes(data.project.takes);
          }
        } else {
          setAnalysis(null);
          setDuration(0);
        }
      } catch (err) {
        pushLog(err instanceof Error ? err.message : "Erro ao abrir projeto");
        setScreen("hub");
      } finally {
        setBusy(false);
      }
    },
    [analyzePath, applyProjectSession, pushLog],
  );

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        await refreshProjects();
        if (cancelled) return;
        if (queryProject) {
          await openProject(queryProject);
        }
      } catch (err) {
        if (!cancelled) {
          pushLog(
            err instanceof Error ? err.message : "Erro ao carregar projetos",
          );
        }
      } finally {
        if (!cancelled) setProjectsLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
    // Bootstrap once on mount / quando ?project= muda
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [queryProject]);

  async function runLocalRender(dryRunOnly = false) {
    if (!analysis || !activeProject) return;
    setBusy(true);
    pushLog(
      dryRunOnly
        ? "Dry-run local (fabrica --seco)…"
        : "Render local sem depender do chat/XAI…",
    );
    try {
      const res = await fetch("/api/editor/render", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          path: analysis.path,
          takes,
          dryRunOnly,
          videoOptions: {
            ...editOptions,
            estilo:
              editOptions.estilo ||
              (analysis.orientation === "vertical" ? "reel-mono" : "aula-ccnp"),
            projeto: activeProject.slug,
            whisperModel: "tiny",
            captions: false,
          },
        }),
      });
      const data = (await res.json()) as {
        ok?: boolean;
        error?: string;
        step?: string;
        publicUrl?: string | null;
        outputPath?: string | null;
        report?: string;
        renderLog?: string;
      };
      if (!res.ok || !data.ok) {
        throw new Error(data.error || data.report || data.renderLog || "Render falhou");
      }
      let nextOutput: string | null = null;
      if (data.publicUrl) {
        nextOutput = data.publicUrl;
        setOutputUrl(data.publicUrl);
        pushLog(`Pronto: ${data.publicUrl}`);
      } else if (data.outputPath) {
        nextOutput = mediaUrl(data.outputPath);
        setOutputUrl(nextOutput);
        pushLog(`Pronto: ${data.outputPath}`);
      } else if (dryRunOnly) {
        pushLog(`Dry-run OK (${data.step})`);
      } else {
        pushLog("Render OK — arquivo gerado (veja logs do servidor).");
      }
      setAnalysis((prev) =>
        prev
          ? {
              ...prev,
              statusNote: dryRunOnly
                ? `${prev.filename.replace(/\.[^.]+$/, "")} — dry-run OK. Aprove o render.`
                : `${prev.filename.replace(/\.[^.]+$/, "")} v2 – corte renderizado.`,
            }
          : prev,
      );
      if (nextOutput) {
        void persistProject(activeProject.id, { outputUrl: nextOutput });
      }
    } catch (err) {
      pushLog(err instanceof Error ? err.message : "Erro no render local");
    } finally {
      setBusy(false);
    }
  }

  function patchEdit<K extends keyof VideoEditOptions>(
    key: K,
    value: VideoEditOptions[K],
  ) {
    setEditOptions((prev) => {
      const next = {
        ...prev,
        [key]: value,
        projeto: activeProject?.slug ?? prev.projeto,
      };
      if (key === "estilo" && typeof value === "string") {
        next.estilo = value as VideoStyle;
      }
      if (activeProject) {
        schedulePersist(activeProject.id, {
          estilo: next.estilo,
          options: next,
        });
      }
      return next;
    });
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

  const queryPath = searchParams.get("path");
  const queryTranscribe = searchParams.get("transcribe") !== "0";

  useEffect(() => {
    if (screen !== "editor" || !activeProject) return;
    const path =
      queryPath || new URLSearchParams(window.location.search).get("path");
    if (!path || bootstrapped.current === path) return;
    bootstrapped.current = path;
    const transcribe =
      new URLSearchParams(window.location.search).get("transcribe") !== "0";
    void analyzePath(path, queryPath ? queryTranscribe : transcribe);
  }, [activeProject, analyzePath, queryPath, queryTranscribe, screen]);

  async function onUpload(file: File | null) {
    if (!file || !activeProject) return;
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
      if (screen !== "editor") return;
      const tag = (e.target as HTMLElement | null)?.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
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
  }, [duration, screen]);

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
        setCommand("");
        await runLocalRender(false);
        return;
      }

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

  async function handleCreateProject(input: {
    name: string;
    estilo: VideoStyle;
  }) {
    setBusy(true);
    try {
      const res = await fetch("/api/editor/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input),
      });
      const data = (await res.json()) as {
        project?: EditorProject;
        error?: string;
      };
      if (!res.ok || !data.project) {
        throw new Error(data.error || "Falha ao criar projeto");
      }
      await refreshProjects();
      await openProject(data.project.id);
    } catch (err) {
      pushLog(err instanceof Error ? err.message : "Erro ao criar projeto");
    } finally {
      setBusy(false);
    }
  }

  async function handleDeleteProject(projectId: string) {
    setBusy(true);
    try {
      const res = await fetch(`/api/editor/projects/${projectId}`, {
        method: "DELETE",
      });
      const data = (await res.json()) as { error?: string };
      if (!res.ok) throw new Error(data.error || "Falha ao excluir");
      if (activeProjectIdRef.current === projectId) {
        activeProjectIdRef.current = null;
        setActiveProject(null);
        setAnalysis(null);
        setScreen("hub");
      }
      await refreshProjects();
    } catch (err) {
      pushLog(err instanceof Error ? err.message : "Erro ao excluir projeto");
    } finally {
      setBusy(false);
    }
  }

  function backToHub() {
    if (persistTimer.current) clearTimeout(persistTimer.current);
    if (activeProject) {
      void persistProject(activeProject.id, {
        estilo: editOptions.estilo,
        options: { ...editOptions, projeto: activeProject.slug },
        takes,
        outputUrl,
        mediaPath: analysis?.path ?? activeProject.mediaPath,
        mediaFilename: analysis?.filename ?? activeProject.mediaFilename,
        analysisSummary: analysis
          ? {
              duration: analysis.duration,
              width: analysis.width,
              height: analysis.height,
              orientation: analysis.orientation,
              statusNote: analysis.statusNote,
            }
          : activeProject.analysisSummary,
      });
    }
    setScreen("hub");
    void refreshProjects();
  }

  if (projectsLoading) {
    return (
      <div className="nexus-editor flex min-h-[50vh] items-center justify-center text-sm text-[color:var(--muted-foreground)]">
        Carregando projetos…
      </div>
    );
  }

  if (screen === "hub") {
    return (
      <div className="nexus-editor flex flex-col">
        <header className="flex items-center justify-between gap-3 border-b border-[color:var(--border)] px-4 py-3">
          <Link href="/dashboard" className="flex items-center gap-2.5">
            <span className="flex size-8 items-center justify-center rounded-md bg-[color:var(--primary)] text-[11px] font-bold text-[color:var(--primary-foreground)]">
              NX
            </span>
            <span className="text-sm font-semibold tracking-tight text-[color:var(--foreground)]">
              Editor{" "}
              <span className="font-mono text-[9px] font-medium uppercase text-[color:var(--muted-foreground)]">
                Nexus
              </span>
            </span>
          </Link>
          <Link
            href="/ferramentas"
            className="text-xs text-[color:var(--muted-foreground)] hover:text-[color:var(--foreground)]"
          >
            ← Ferramentas
          </Link>
        </header>
        <ProjectHub
          projects={projects}
          busy={busy}
          onOpen={(id) => void openProject(id)}
          onCreate={(input) => void handleCreateProject(input)}
          onDelete={(id) => void handleDeleteProject(id)}
        />
      </div>
    );
  }

  return (
    <div className="nexus-editor flex flex-col">
      <header className="flex items-center justify-between gap-3 border-b border-[color:var(--border)] px-4 py-3">
        <div className="flex min-w-0 items-center gap-4">
          <button
            type="button"
            onClick={backToHub}
            className="flex shrink-0 items-center gap-2.5 rounded-lg px-1 py-0.5 hover:bg-[color:var(--muted)]/40"
            title="Voltar aos projetos"
          >
            <span className="flex size-8 items-center justify-center rounded-md bg-[color:var(--primary)] text-[11px] font-bold text-[color:var(--primary-foreground)]">
              NX
            </span>
            <span className="hidden text-left sm:block">
              <span className="block text-sm font-semibold tracking-tight text-[color:var(--foreground)]">
                {activeProject?.name ?? "Editor"}
              </span>
              <span className="block font-mono text-[9px] font-medium uppercase text-[color:var(--muted-foreground)]">
                {activeProject
                  ? `${STYLE_LABELS[activeProject.estilo]} · ${activeProject.slug}`
                  : "Nexus"}
              </span>
            </span>
          </button>

          <div className="flex rounded-lg bg-[color:var(--muted)]/40 p-1">
            <button
              type="button"
              onClick={() => setView("code")}
              className={`rounded-md px-3 py-1.5 text-sm ${
                view === "code"
                  ? "bg-[color:var(--primary)] text-[color:var(--primary-foreground)] font-semibold"
                  : "text-[color:var(--muted-foreground)]"
              }`}
            >
              Code
            </button>
            <button
              type="button"
              onClick={() => setView("visual")}
              className={`rounded-md px-3 py-1.5 text-sm ${
                view === "visual"
                  ? "bg-[color:var(--muted)] text-[color:var(--foreground)] font-semibold"
                  : "text-[color:var(--muted-foreground)]"
              }`}
            >
              Visual
            </button>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={backToHub}
            className="rounded-lg border border-[color:var(--border)] px-3 py-1.5 text-sm text-[color:var(--foreground)]/85 hover:bg-[color:var(--muted)]/40"
          >
            Projetos
          </button>
          <label className="cursor-pointer rounded-lg border border-[color:var(--border)] px-3 py-1.5 text-sm text-[color:var(--foreground)]/85 hover:bg-[color:var(--muted)]/40">
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
            onClick={() => {
              setView("code");
              setCommand("Perguntar: o que cortar neste vídeo?");
            }}
            className="rounded-lg bg-[color:var(--primary)] px-3 py-1.5 text-sm font-semibold text-[color:var(--primary-foreground)]"
          >
            Perguntar
          </button>
        </div>
      </header>

      {analysis?.statusNote ? (
        <div className="border-b border-[color:var(--border)] bg-[color:var(--muted)]/40 px-4 py-2 text-sm text-[color:var(--foreground)]/80">
          {analysis.statusNote}
        </div>
      ) : null}

      <main className="flex flex-1 flex-col gap-4 px-4 py-4">
        {view === "visual" ? (
          <div className="nexus-editor-visual grid gap-4 lg:grid-cols-[minmax(200px,260px)_minmax(0,1fr)] lg:items-start">
            <aside className="rounded-xl border border-[color:var(--border)] bg-[color:var(--background)]/60 p-4">
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
              <div className="mt-3 flex items-center justify-center gap-2">
                <button
                  type="button"
                  onClick={() => setCurrentTime((t) => Math.max(0, t - 1 / 30))}
                  className="rounded-full border border-[color:var(--border)] px-3 py-1.5 text-sm"
                >
                  ‹
                </button>
                <button
                  type="button"
                  onClick={() => setPlaying((p) => !p)}
                  className="rounded-full bg-[color:var(--foreground)] px-4 py-1.5 text-sm font-semibold text-[color:var(--background)]"
                >
                  {playing ? "Pause" : "Play"}
                </button>
                <button
                  type="button"
                  onClick={() =>
                    setCurrentTime((t) => Math.min(duration, t + 1 / 30))
                  }
                  className="rounded-full border border-[color:var(--border)] px-3 py-1.5 text-sm"
                >
                  ›
                </button>
              </div>
            </aside>

            <div className="min-w-0">
              {!analysis ? (
                <div className="flex min-h-[240px] flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-[color:var(--border)] px-6 text-center">
                  <p className="text-sm font-medium text-[color:var(--foreground)]">
                    Projeto pronto: {activeProject?.name}
                  </p>
                  <p className="max-w-sm text-xs text-[color:var(--muted-foreground)]">
                    Preferências deste estilo ficam só neste projeto. Faça upload
                    de um vídeo para começar a editar.
                  </p>
                  <label className="cursor-pointer rounded-lg bg-[color:var(--primary)] px-4 py-2 text-sm font-semibold text-[color:var(--primary-foreground)]">
                    {uploading ? "Enviando…" : "Upload de vídeo"}
                    <input
                      type="file"
                      accept="video/*,.mp4,.mov,.webm"
                      className="hidden"
                      disabled={uploading || busy}
                      onChange={(e) => onUpload(e.target.files?.[0] ?? null)}
                    />
                  </label>
                </div>
              ) : (
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
                    setTakes((prev) => {
                      const next = prev.map((take) =>
                        take.id === id ? { ...take, start, end } : take,
                      );
                      if (activeProject) {
                        schedulePersist(activeProject.id, { takes: next });
                      }
                      return next;
                    });
                  }}
                />
              )}
            </div>
          </div>
        ) : (
          <CodeWorkspace analysis={analysis} logs={logs} busy={busy} />
        )}
      </main>

      <footer className="border-t border-[color:var(--border)] px-4 py-3">
        <div className="flex w-full flex-col gap-2">
          <div className="mb-1 flex items-center justify-between gap-2">
            <p className="text-[10px] uppercase tracking-wider text-[color:var(--muted-foreground)]">
              Preferências do projeto{" "}
              <span className="font-mono text-[color:var(--foreground)]/70">
                {activeProject?.slug}
              </span>
            </p>
          </div>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">
            <label className="flex flex-col gap-1 text-[10px] uppercase tracking-wider text-[color:var(--muted-foreground)]">
              Estilo
              <select
                value={editOptions.estilo}
                onChange={(e) =>
                  patchEdit("estilo", e.target.value as VideoStyle)
                }
                className="rounded-lg border border-[color:var(--border)] bg-[color:var(--background)] px-2 py-1.5 text-xs text-[color:var(--foreground)]"
              >
                {VIDEO_STYLES.map((s) => (
                  <option key={s} value={s}>
                    {STYLE_LABELS[s]}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-[10px] uppercase tracking-wider text-[color:var(--muted-foreground)]">
              Formato
              <select
                value={editOptions.formato}
                onChange={(e) =>
                  patchEdit("formato", e.target.value as VideoFormat)
                }
                className="rounded-lg border border-[color:var(--border)] bg-[color:var(--background)] px-2 py-1.5 text-xs text-[color:var(--foreground)]"
              >
                {VIDEO_FORMATS.map((f) => (
                  <option key={f} value={f}>
                    {f}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-[10px] uppercase tracking-wider text-[color:var(--muted-foreground)]">
              Fonte
              <select
                value={editOptions.fonte}
                onChange={(e) =>
                  patchEdit("fonte", e.target.value as VideoFont)
                }
                className="rounded-lg border border-[color:var(--border)] bg-[color:var(--background)] px-2 py-1.5 text-xs text-[color:var(--foreground)]"
              >
                {VIDEO_FONTS.map((f) => (
                  <option key={f} value={f}>
                    {FONT_LABELS[f]}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-[10px] uppercase tracking-wider text-[color:var(--muted-foreground)]">
              Grade
              <select
                value={editOptions.grade}
                onChange={(e) =>
                  patchEdit("grade", e.target.value as VideoGrade)
                }
                className="rounded-lg border border-[color:var(--border)] bg-[color:var(--background)] px-2 py-1.5 text-xs text-[color:var(--foreground)]"
              >
                {VIDEO_GRADES.map((g) => (
                  <option key={g} value={g}>
                    {g}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-[10px] uppercase tracking-wider text-[color:var(--muted-foreground)]">
              Emenda
              <select
                value={editOptions.efeitoEmenda}
                onChange={(e) =>
                  patchEdit(
                    "efeitoEmenda",
                    e.target.value as VideoEditOptions["efeitoEmenda"],
                  )
                }
                className="rounded-lg border border-[color:var(--border)] bg-[color:var(--background)] px-2 py-1.5 text-xs text-[color:var(--foreground)]"
              >
                <option value="none">Nenhum</option>
                <option value="glitch">Glitch</option>
                <option value="flash">Flash</option>
                <option value="whip">Whip</option>
              </select>
            </label>
            <label className="flex flex-col gap-1 text-[10px] uppercase tracking-wider text-[color:var(--muted-foreground)]">
              Som
              <select
                value={editOptions.som}
                onChange={(e) => patchEdit("som", e.target.value as VideoSound)}
                className="rounded-lg border border-[color:var(--border)] bg-[color:var(--background)] px-2 py-1.5 text-xs text-[color:var(--foreground)]"
              >
                {VIDEO_SOUNDS.map((s) => (
                  <option key={s} value={s}>
                    {SOUND_LABELS[s]}
                  </option>
                ))}
              </select>
            </label>
          </div>
          {outputUrl ? (
            <p className="mb-2 text-xs text-[color:var(--primary)]">
              Saída:{" "}
              <a href={outputUrl} className="underline" target="_blank" rel="noreferrer">
                {outputUrl}
              </a>
            </p>
          ) : null}
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              disabled={busy || !analysis}
              onClick={() => void runLocalRender(true)}
              className="rounded-xl border border-[color:var(--border)] px-3 py-3 text-sm text-[color:var(--foreground)]/85 disabled:opacity-40"
            >
              Dry-run
            </button>
            <button
              type="button"
              disabled={busy || !analysis}
              onClick={() => void runLocalRender(false)}
              className="rounded-xl bg-[color:var(--primary)] px-4 py-3 text-sm font-semibold text-[color:var(--primary-foreground)] disabled:opacity-40"
            >
              {busy ? "Renderizando…" : "Renderizar corte"}
            </button>
            <input
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") void runCommand();
              }}
              placeholder="Comandos — corta gordura · transcreve · edita / render"
              className="min-w-[200px] flex-1 rounded-xl border border-[color:var(--border)] bg-[color:var(--background)] px-3 py-3 text-sm text-[color:var(--foreground)] outline-none ring-[color:var(--primary)] placeholder:text-[color:var(--muted-foreground)] focus:ring-2"
            />
            <label className="flex items-center gap-2 rounded-xl border border-[color:var(--border)] px-3 py-3 text-xs text-[color:var(--muted-foreground)]">
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
              className="rounded-xl border border-[color:var(--border)] px-4 py-3 text-sm font-semibold text-[color:var(--foreground)] disabled:opacity-40"
            >
              Enviar
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}
