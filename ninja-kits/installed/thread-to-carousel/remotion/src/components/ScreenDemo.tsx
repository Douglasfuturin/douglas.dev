import React from "react";
import { AbsoluteFill, useVideoConfig } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { ZoomClip, type ZoomConfig } from "./ZoomClip";

export interface ClipDef {
  startMs: number;
  endMs: number;
  zoom: ZoomConfig | null;
}

export interface EditConfig {
  fps: number;
  width: number;
  height: number;
  source: string; // filename in remotion/public/
  clips: ClipDef[];
  transitionDurationMs: number;
}

interface ScreenDemoProps {
  editConfig: EditConfig;
}

/**
 * Main composition — stitches clips together with fade transitions.
 * Each clip can optionally have a zoom effect.
 */
export const ScreenDemo: React.FC<ScreenDemoProps> = ({ editConfig }) => {
  const { fps } = useVideoConfig();
  const transitionFrames = Math.round(
    (editConfig.transitionDurationMs / 1000) * fps
  );

  const msToFrames = (ms: number) => Math.round((ms / 1000) * fps);

  return (
    <AbsoluteFill style={{ background: "black" }}>
      <TransitionSeries>
        {editConfig.clips.map((clip, i) => {
          const clipDurationFrames = msToFrames(clip.endMs - clip.startMs);
          const trimBefore = msToFrames(clip.startMs);
          const trimAfter = msToFrames(clip.endMs);

          return (
            <React.Fragment key={i}>
              {i > 0 && (
                <TransitionSeries.Transition
                  presentation={fade()}
                  timing={linearTiming({
                    durationInFrames: transitionFrames,
                  })}
                />
              )}
              <TransitionSeries.Sequence
                durationInFrames={clipDurationFrames}
              >
                <ZoomClip
                  source={editConfig.source}
                  trimBeforeFrames={trimBefore}
                  trimAfterFrames={trimAfter}
                  zoom={clip.zoom}
                />
              </TransitionSeries.Sequence>
            </React.Fragment>
          );
        })}
      </TransitionSeries>
    </AbsoluteFill>
  );
};
