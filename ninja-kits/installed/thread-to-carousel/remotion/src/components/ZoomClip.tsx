import React from "react";
import {
  AbsoluteFill,
  OffthreadVideo,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";

export interface ZoomConfig {
  scale: number;
  originX: number; // percent (0-100)
  originY: number; // percent (0-100)
}

interface ZoomClipProps {
  source: string;
  trimBeforeFrames: number;
  trimAfterFrames: number;
  zoom: ZoomConfig | null;
}

/**
 * Renders a screen recording clip with an optional animated zoom effect.
 *
 * - No zoom: plays the video flat at 1x scale
 * - With zoom: smoothly zooms in over ~0.5s using spring(), holds, then zooms back out
 */
export const ZoomClip: React.FC<ZoomClipProps> = ({
  source,
  trimBeforeFrames,
  trimAfterFrames,
  zoom,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  let scale = 1;
  let originX = 50;
  let originY = 50;

  if (zoom) {
    originX = zoom.originX;
    originY = zoom.originY;

    const zoomInDuration = Math.round(fps * 0.8); // 0.8s smooth ease in
    const zoomOutStart = Math.max(0, durationInFrames - Math.round(fps * 0.8));

    if (frame <= zoomInDuration) {
      // Smooth zoom in — high damping, no overshoot (Screen Studio feel)
      const springVal = spring({
        frame,
        fps,
        from: 1,
        to: zoom.scale,
        config: { damping: 28, stiffness: 60, mass: 0.8 },
      });
      scale = springVal;
    } else if (frame >= zoomOutStart) {
      // Smooth zoom out — same buttery ease
      const springVal = spring({
        frame: frame - zoomOutStart,
        fps,
        from: zoom.scale,
        to: 1,
        config: { damping: 28, stiffness: 60, mass: 0.8 },
      });
      scale = springVal;
    } else {
      // Hold at zoom level
      scale = zoom.scale;
    }
  }

  const padding = 64;
  const borderRadius = 24;

  return (
    <AbsoluteFill>
      <img
        src={staticFile("gradient.jpg")}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          position: "absolute",
        }}
      />
      <AbsoluteFill
        style={{
          padding,
          transform: `scale(${scale})`,
          transformOrigin: `${originX}% ${originY}%`,
        }}
      >
        <div
          style={{
            width: "100%",
            height: "100%",
            borderRadius,
            overflow: "hidden",
            boxShadow: "0 8px 32px rgba(0, 0, 0, 0.5)",
            border: "2px solid rgba(180, 180, 180, 0.6)",
          }}
        >
          <OffthreadVideo
            src={staticFile(source)}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
            trimBefore={trimBeforeFrames}
            trimAfter={trimAfterFrames}
          />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
