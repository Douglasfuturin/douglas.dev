import React from "react";
import { Composition } from "remotion";
import { ScreenDemo, type EditConfig } from "./components/ScreenDemo";

/**
 * Remotion entry — registers the ScreenDemo composition.
 *
 * inputProps.editConfig is provided at render time by render-demo.mjs
 * and contains the clip definitions, zoom keyframes, and source path.
 */

const defaultConfig: EditConfig = {
  fps: 30,
  width: 1920,
  height: 1080,
  source: "recording.mp4",
  clips: [{ startMs: 0, endMs: 5000, zoom: null }],
  transitionDurationMs: 500,
};

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="ScreenDemo"
      component={ScreenDemo}
      durationInFrames={300}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{ editConfig: defaultConfig }}
      calculateMetadata={({ props }) => {
        const { editConfig } = props;
        const fps = editConfig.fps;

        // Total duration = sum of all clip durations minus overlapping transitions
        const clipDurations = editConfig.clips.map(
          (c) => Math.round(((c.endMs - c.startMs) / 1000) * fps)
        );
        const totalClipFrames = clipDurations.reduce((a, b) => a + b, 0);
        const transitionFrames = Math.round(
          (editConfig.transitionDurationMs / 1000) * fps
        );
        const transitionOverlap =
          Math.max(0, editConfig.clips.length - 1) * transitionFrames;
        const durationInFrames = Math.max(
          1,
          totalClipFrames - transitionOverlap
        );

        return {
          durationInFrames,
          fps,
          width: editConfig.width,
          height: editConfig.height,
        };
      }}
    />
  );
};
