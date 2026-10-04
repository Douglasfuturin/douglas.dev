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
    <div className="relative mx-auto flex h-full max-h-[58vh] w-full max-w-[360px] items-center justify-center">
      <div className="relative aspect-[9/16] w-full overflow-hidden rounded-2xl bg-black shadow-[0_0_80px_rgba(255,122,26,0.12)] ring-1 ring-white/10">
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
          <div className="flex h-full items-center justify-center px-6 text-center text-sm text-white/40">
            Envie um vídeo para pré-visualizar em tempo real
          </div>
        )}

        {caption ? (
          <div className="pointer-events-none absolute inset-x-0 bottom-[14%] px-4 text-center">
            <p className="font-display text-3xl font-extrabold uppercase leading-none tracking-tight text-white drop-shadow-[0_2px_10px_rgba(0,0,0,0.85)]">
              {caption}
            </p>
          </div>
        ) : null}
      </div>

      <div className="pointer-events-none absolute -bottom-8 left-1/2 -translate-x-1/2 font-mono text-xs text-white/45">
        {formatClock(currentTime)}
      </div>
    </div>
  );
}
