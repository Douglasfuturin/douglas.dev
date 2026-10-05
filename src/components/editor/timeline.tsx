"use client";

import { useMemo, useRef } from "react";
import type { TakeWindow } from "@/lib/editor/types";
import { formatClock } from "./format";

type Props = {
  duration: number;
  currentTime: number;
  waveform: number[];
  takes: TakeWindow[];
  zoom: number;
  filmstrip: string[];
  onSeek: (time: number) => void;
  onZoom: (zoom: number) => void;
  onTakeChange: (id: string, start: number, end: number) => void;
};

export function Timeline({
  duration,
  currentTime,
  waveform,
  takes,
  zoom,
  filmstrip,
  onSeek,
  onZoom,
  onTakeChange,
}: Props) {
  const trackRef = useRef<HTMLDivElement>(null);
  const widthPct = Math.max(100, zoom * 100);

  const ticks = useMemo(() => {
    if (duration <= 0) return [];
    const step = duration > 20 ? 2 : 1;
    const out: number[] = [];
    for (let t = 0; t <= duration + 0.001; t += step) out.push(t);
    return out;
  }, [duration]);

  function timeFromClientX(clientX: number) {
    const el = trackRef.current;
    if (!el || duration <= 0) return 0;
    const rect = el.getBoundingClientRect();
    const x = Math.min(Math.max(clientX - rect.left, 0), rect.width);
    return (x / rect.width) * duration;
  }

  return (
    <section className="rounded-2xl border border-[color:var(--border)] bg-[color:var(--background)] p-3">
      <div className="mb-2 flex items-center justify-between gap-3 text-xs text-[color:var(--muted-foreground)]">
        <div className="flex items-center gap-2">
          <span className="font-mono text-[color:var(--foreground)]/85">
            {formatClock(currentTime)} / {formatClock(duration)}
          </span>
        </div>
        <label className="flex items-center gap-2">
          zoom
          <input
            type="range"
            min={1}
            max={4}
            step={0.1}
            value={zoom}
            onChange={(e) => onZoom(Number(e.target.value))}
            className="accent-[color:var(--primary)]"
          />
        </label>
      </div>

      <div className="nexus-editor-timeline-track pb-1">
        <div style={{ width: `${widthPct}%` }} className="min-w-full">
          <div className="relative mb-1 h-4">
            {ticks.map((t) => (
              <span
                key={t}
                className="absolute top-0 -translate-x-1/2 font-mono text-[10px] text-[color:var(--muted-foreground)]"
                style={{ left: `${(t / Math.max(duration, 0.001)) * 100}%` }}
              >
                {formatClock(t)}
              </span>
            ))}
          </div>

          <div
            ref={trackRef}
            className="relative cursor-crosshair select-none"
            onPointerDown={(e) => {
              onSeek(timeFromClientX(e.clientX));
              const move = (ev: PointerEvent) => onSeek(timeFromClientX(ev.clientX));
              const up = () => {
                window.removeEventListener("pointermove", move);
                window.removeEventListener("pointerup", up);
              };
              window.addEventListener("pointermove", move);
              window.addEventListener("pointerup", up);
            }}
          >
            <div className="mb-2 flex h-14 overflow-hidden rounded-lg border border-[color:var(--border)] bg-black/40">
              {filmstrip.length ? (
                filmstrip.map((src, i) => (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    key={`${src}-${i}`}
                    src={src}
                    alt=""
                    className="h-full flex-1 object-cover opacity-90"
                  />
                ))
              ) : (
                <div className="flex w-full items-center justify-center text-xs text-[color:var(--muted-foreground)]">
                  filmstrip
                </div>
              )}
            </div>

            <div className="relative mb-2 h-16 overflow-hidden rounded-lg border border-[color:var(--border)] bg-[color:var(--background)]">
              <div className="absolute left-2 top-1 text-[10px] uppercase tracking-[0.16em] text-[color:var(--primary)]">
                Audio
              </div>
              <div className="flex h-full items-end gap-px px-1 pb-1 pt-5">
                {waveform.map((p, i) => (
                  <div
                    key={i}
                    className="min-w-px flex-1 rounded-sm bg-[color:var(--primary)]"
                    style={{ height: `${Math.max(6, p * 100)}%`, opacity: 0.85 }}
                  />
                ))}
              </div>
            </div>

            <div className="relative h-12 rounded-lg border border-[color:var(--border)] bg-black/30">
              {takes.map((take) => {
                const left = (take.start / Math.max(duration, 0.001)) * 100;
                const width =
                  ((take.end - take.start) / Math.max(duration, 0.001)) * 100;
                return (
                  <div
                    key={take.id}
                    className="absolute top-1 bottom-1 overflow-hidden rounded-md border border-[color:var(--primary)]/60 bg-[color:var(--primary)]/20"
                    style={{ left: `${left}%`, width: `${Math.max(width, 0.8)}%` }}
                    title={take.label}
                  >
                    <span className="px-1 text-[10px] text-[color:var(--foreground)]/85">
                      {take.label}
                    </span>
                    <button
                      type="button"
                      aria-label="ajustar início"
                      className="absolute inset-y-0 left-0 w-2 cursor-ew-resize bg-[color:var(--foreground)]/30"
                      onPointerDown={(e) => {
                        e.stopPropagation();
                        const move = (ev: PointerEvent) => {
                          const t = timeFromClientX(ev.clientX);
                          onTakeChange(take.id, Math.min(t, take.end - 0.1), take.end);
                        };
                        const up = () => {
                          window.removeEventListener("pointermove", move);
                          window.removeEventListener("pointerup", up);
                        };
                        window.addEventListener("pointermove", move);
                        window.addEventListener("pointerup", up);
                      }}
                    />
                    <button
                      type="button"
                      aria-label="ajustar fim"
                      className="absolute inset-y-0 right-0 w-2 cursor-ew-resize bg-[color:var(--foreground)]/30"
                      onPointerDown={(e) => {
                        e.stopPropagation();
                        const move = (ev: PointerEvent) => {
                          const t = timeFromClientX(ev.clientX);
                          onTakeChange(take.id, take.start, Math.max(t, take.start + 0.1));
                        };
                        const up = () => {
                          window.removeEventListener("pointermove", move);
                          window.removeEventListener("pointerup", up);
                        };
                        window.addEventListener("pointermove", move);
                        window.addEventListener("pointerup", up);
                      }}
                    />
                  </div>
                );
              })}
            </div>

            <div
              className="pointer-events-none absolute top-0 bottom-0 z-10 w-[2px] bg-[color:var(--primary)]"
              style={{
                left: `${(currentTime / Math.max(duration, 0.001)) * 100}%`,
              }}
            >
              <div className="absolute -top-1 left-1/2 h-3 w-3 -translate-x-1/2 rounded-full bg-[color:var(--primary)] shadow-[0_0_12px_color-mix(in_oklab,var(--primary)_45%,transparent)]" />
            </div>
          </div>
        </div>
      </div>

      <p className="mt-2 text-[11px] text-[color:var(--muted-foreground)]">
        espaço play/pause · setas frame a frame · shift+setas 1s · arraste as bordas
        de um take · clique na timeline para seek
      </p>
    </section>
  );
}
