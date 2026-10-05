"use client";

import { useEffect, useRef } from "react";
import { formatClock } from "./format";

type Props = {
  src: string | null;
  currentTime: number;
  playing: boolean;
  caption?: string;
  onTime: (t: number) => void;
  onDuration: (d: number) => void;
  onPlayingChange: (playing: boolean) => void;
};

export function VideoPreview({
  src,
  currentTime,
  playing,
  caption,
  onTime,
  onDuration,
  onPlayingChange,
}: Props) {
  const ref = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (Math.abs(el.currentTime - currentTime) > 0.12) {
      el.currentTime = currentTime;
    }
  }, [currentTime]);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (playing) {
      void el.play().catch(() => onPlayingChange(false));
    } else {
      el.pause();
    }
  }, [playing, onPlayingChange]);

  return (
    <div className="nexus-editor-preview flex w-full flex-col gap-3">
      <div className="relative mx-auto aspect-[9/16] w-full max-w-[220px] overflow-hidden rounded-xl bg-black ring-1 ring-[color:var(--border)] lg:max-w-[240px]">
        {src ? (
          <video
            ref={ref}
            src={src}
            className="h-full w-full object-cover"
            playsInline
            preload="auto"
            onLoadedMetadata={(e) => onDuration(e.currentTarget.duration || 0)}
            onTimeUpdate={(e) => onTime(e.currentTarget.currentTime)}
            onPlay={() => onPlayingChange(true)}
            onPause={() => onPlayingChange(false)}
            onEnded={() => onPlayingChange(false)}
          />
        ) : (
          <div className="flex h-full items-center justify-center px-4 text-center text-xs leading-relaxed text-[color:var(--muted-foreground)]">
            Envie um vídeo para pré-visualizar
          </div>
        )}

        {caption ? (
          <div className="pointer-events-none absolute inset-x-0 bottom-[12%] px-3 text-center">
            <p className="text-lg font-extrabold uppercase leading-none tracking-tight text-white drop-shadow-[0_2px_8px_rgba(0,0,0,0.85)]">
              {caption}
            </p>
          </div>
        ) : null}
      </div>

      <p className="text-center font-mono text-xs text-[color:var(--muted-foreground)]">
        {formatClock(currentTime)}
      </p>
    </div>
  );
}
