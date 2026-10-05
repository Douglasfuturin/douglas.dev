"use client";

import type { AgentLogEntry, MediaAnalysis } from "@/lib/editor/types";
import { formatClock } from "./format";

type Props = {
  analysis: MediaAnalysis | null;
  logs: AgentLogEntry[];
  busy: boolean;
};

export function CodeWorkspace({ analysis, logs, busy }: Props) {
  return (
    <div className="grid h-full gap-4 lg:grid-cols-[1.4fr_0.9fr]">
      <section className="rounded-2xl border border-[color:var(--border)] bg-[color:var(--background)] p-4">
        <p className="mb-3 text-xs uppercase tracking-[0.18em] text-[color:var(--muted-foreground)]">
          Agente · análise
        </p>

        {busy ? (
          <p className="mb-3 animate-pulse text-sm text-[color:var(--primary)]">
            Executando comandos do editor…
          </p>
        ) : (
          <p className="mb-3 text-sm text-[color:var(--muted-foreground)]">
            {logs.length
              ? `Executados ${logs.length} eventos do agente.`
              : "Envie um vídeo ou digite um comando para o agente editar."}
          </p>
        )}

        <div className="mb-4 space-y-2">
          {logs.slice(-8).map((log) => (
            <p key={log.id} className="font-mono text-xs text-[color:var(--muted-foreground)]">
              <span className="text-[color:var(--muted-foreground)]">{log.at}</span> {log.text}
            </p>
          ))}
        </div>

        {analysis ? (
          <>
            <h2 className="mb-2 text-sm font-semibold text-[color:var(--foreground)]">Material analisado</h2>
            <ul className="mb-4 space-y-1 text-sm text-[color:var(--muted-foreground)]">
              <li>
                <span className="text-[color:var(--muted-foreground)]">arquivo:</span> {analysis.filename}
              </li>
              <li>
                <span className="text-[color:var(--muted-foreground)]">duração:</span>{" "}
                {analysis.duration.toFixed(1)}s
              </li>
              <li>
                <span className="text-[color:var(--muted-foreground)]">quadro:</span> {analysis.width}x
                {analysis.height} {analysis.orientation}, {analysis.fps}fps
              </li>
              <li>
                <span className="text-[color:var(--muted-foreground)]">leitura:</span> {analysis.description}
              </li>
            </ul>

            <h3 className="mb-2 text-sm font-semibold text-[color:var(--foreground)]">Transcrição</h3>
            <div className="mb-4 overflow-hidden rounded-xl border border-[color:var(--border)]">
              <table className="w-full text-left text-sm">
                <thead className="bg-[color:var(--muted)]/40 text-xs uppercase tracking-wider text-[color:var(--muted-foreground)]">
                  <tr>
                    <th className="px-3 py-2">#</th>
                    <th className="px-3 py-2">tempo</th>
                    <th className="px-3 py-2">fala</th>
                  </tr>
                </thead>
                <tbody>
                  {analysis.transcript.length ? (
                    analysis.transcript.map((cue) => (
                      <tr key={cue.index} className="border-t border-[color:var(--border)]">
                        <td className="px-3 py-2 text-[color:var(--muted-foreground)]">{cue.index}</td>
                        <td className="px-3 py-2 font-mono text-xs text-[color:var(--primary)]">
                          {formatClock(cue.start)} – {formatClock(cue.end)}
                        </td>
                        <td className="px-3 py-2 text-[color:var(--foreground)]/85">{cue.text}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={3} className="px-3 py-4 text-[color:var(--muted-foreground)]">
                        Sem transcript ainda. Peça “transcreve” no comando.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <h3 className="mb-2 text-sm font-semibold text-[color:var(--foreground)]">Gordura encontrada</h3>
            <ul className="space-y-2 text-sm text-[color:var(--muted-foreground)]">
              {analysis.fat.length ? (
                analysis.fat.map((f, i) => (
                  <li key={`${f.start}-${i}`} className="rounded-lg bg-[color:var(--muted)]/40 px-3 py-2">
                    <span className="font-mono text-[color:var(--primary)]">
                      {formatClock(f.start)}–{formatClock(f.end)}
                    </span>{" "}
                    · {f.seconds.toFixed(2)}s · {f.reason}
                  </li>
                ))
              ) : (
                <li className="text-[color:var(--muted-foreground)]">Nenhum trecho óbvio de silêncio.</li>
              )}
            </ul>
          </>
        ) : (
          <p className="text-sm text-[color:var(--muted-foreground)]">Nenhum material carregado.</p>
        )}
      </section>

      <section className="rounded-2xl border border-[color:var(--border)] bg-[color:var(--background)] p-4">
        <p className="mb-3 text-xs uppercase tracking-[0.18em] text-[color:var(--muted-foreground)]">
          Partes do vídeo
        </p>
        <div className="space-y-2">
          {analysis?.takes.map((take) => (
            <div
              key={take.id}
              className="rounded-xl border border-[color:var(--border)] bg-black/30 px-3 py-3"
            >
              <p className="text-sm font-medium text-[color:var(--foreground)]">{take.label}</p>
              <p className="font-mono text-xs text-[color:var(--muted-foreground)]">
                {formatClock(take.start)} → {formatClock(take.end)}
              </p>
              <div className="mt-2 h-2 overflow-hidden rounded-full bg-[color:var(--muted)]/50">
                <div className="h-full w-2/3 rounded-full bg-gradient-to-r from-[color:var(--primary)] to-[color:var(--primary)]" />
              </div>
            </div>
          )) || (
            <p className="text-sm text-[color:var(--muted-foreground)]">Takes aparecem após a análise.</p>
          )}
        </div>
      </section>
    </div>
  );
}
