"use client";

type RadarSource = { title: string; url?: string };

export type RadarCardItem = {
  id: string;
  category: string;
  headline: string;
  summary: string;
  whyNow: string;
  angle: string;
  score: number;
  contentFit?: string;
  sources?: RadarSource[];
  approvePrompt?: string;
};

function categoryLabel(category: string): string {
  switch (category) {
    case "automacao":
      return "Automação";
    case "ia":
      return "IA";
    case "marketing":
      return "Marketing";
    default:
      return "Cruzado";
  }
}

export function RadarApprovalCards({
  date,
  items,
  onApprove,
  busy,
}: {
  date?: string;
  items: RadarCardItem[];
  onApprove: (item: RadarCardItem) => void;
  busy?: boolean;
}) {
  if (!items.length) return null;

  return (
    <div className="mt-2 space-y-3">
      <p className="text-[11px] uppercase tracking-[0.16em] text-[var(--muted)]">
        Radar {date || "hoje"} — aprove para o Roteirista
      </p>
      <ul className="space-y-2">
        {items.map((item) => (
          <li
            key={item.id}
            className="rounded-xl border border-[var(--line)] bg-white/70 px-3 py-3"
          >
            <div className="flex flex-wrap items-center gap-2 text-[11px] text-[var(--muted)]">
              <span className="rounded bg-[var(--chip)] px-1.5 py-0.5 font-semibold text-[var(--accent-ink)]">
                {item.score}/10
              </span>
              <span>{categoryLabel(item.category)}</span>
              <span className="font-mono opacity-70">{item.id}</span>
            </div>
            <p className="mt-1 text-sm font-semibold text-[var(--ink)]">
              {item.headline}
            </p>
            <p className="mt-1 text-xs leading-relaxed text-[var(--muted)]">
              {item.angle}
            </p>
            <button
              type="button"
              disabled={busy}
              onClick={() => onApprove(item)}
              className="mt-2 inline-flex rounded-lg bg-[var(--ink)] px-3 py-1.5 text-xs font-semibold text-[var(--panel)] disabled:opacity-50"
            >
              Aprovar → Roteirista
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function extractRadarBriefing(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  part: any,
): { date?: string; items: RadarCardItem[] } | null {
  if (!part || typeof part !== "object") return null;
  const type = String(part.type || "");
  if (
    type !== "tool-deliver_daily_radar_briefing" &&
    !type.includes("deliver_daily_radar_briefing")
  ) {
    return null;
  }
  const output =
    part.output ??
    part.result ??
    (part.state === "output-available" ? part.output : null);
  if (!output || typeof output !== "object" || !Array.isArray(output.items)) {
    return null;
  }
  return {
    date: typeof output.date === "string" ? output.date : undefined,
    items: output.items as RadarCardItem[],
  };
}
