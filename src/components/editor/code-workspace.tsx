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
      <section className="overflow-auto rounded-2xl border border-white/10 bg-[#12151a] p-4">
        <p className="mb-3 text-xs uppercase tracking-[0.18em] text-white/40">
          Agente · análise
        </p>

        {busy ? (
          <p className="mb-3 animate-pulse text-sm text-[#ff7a1a]">
            Executando comandos do editor…
          </p>
        ) : (
          <p className="mb-3 text-sm text-white/55">
            {logs.length
              ? `Executados ${logs.length} eventos do agente.`
              : "Envie um vídeo ou digite um comando para o agente editar."}
          </p>
        )}

        <div className="mb-4 space-y-2">
          {logs.slice(-8).map((log) => (
            <p key={log.id} className="font-mono text-xs text-white/60">
              <span className="text-white/30">{log.at}</span> {log.text}
            </p>
          ))}
        </div>

        {analysis ? (
          <>
            <h2 className="mb-2 text-sm font-semibold text-white">Material analisado</h2>
            <ul className="mb-4 space-y-1 text-sm text-white/70">
              <li>
                <span className="text-white/40">arquivo:</span> {analysis.filename}
              </li>
              <li>
                <span className="text-white/40">duração:</span>{" "}
                {analysis.duration.toFixed(1)}s
              </li>
              <li>
                <span className="text-white/40">quadro:</span> {analysis.width}x
                {analysis.height} {analysis.orientation}, {analysis.fps}fps
              </li>
              <li>
                <span className="text-white/40">leitura:</span> {analysis.description}
              </li>
            </ul>

            <h3 className="mb-2 text-sm font-semibold text-white">Transcrição</h3>
            <div className="mb-4 overflow-hidden rounded-xl border border-white/10">
              <table className="w-full text-left text-sm">
                <thead className="bg-white/5 text-xs uppercase tracking-wider text-white/40">
                  <tr>
                    <th className="px-3 py-2">#</th>
                    <th className="px-3 py-2">tempo</th>
                    <th className="px-3 py-2">fala</th>
                  </tr>
                </thead>
                <tbody>
                  {analysis.transcript.length ? (
                    analysis.transcript.map((cue) => (
                      <tr key={cue.index} className="border-t border-white/5">
                        <td className="px-3 py-2 text-white/40">{cue.index}</td>
                        <td className="px-3 py-2 font-mono text-xs text-[#f5d76e]">
                          {formatClock(cue.start)} – {formatClock(cue.end)}
                        </td>
                        <td className="px-3 py-2 text-white/80">{cue.text}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={3} className="px-3 py-4 text-white/40">
                        Sem transcript ainda. Peça “transcreve” no comando.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <h3 className="mb-2 text-sm font-semibold text-white">Gordura encontrada</h3>
            <ul className="space-y-2 text-sm text-white/70">
              {analysis.fat.length ? (
                analysis.fat.map((f, i) => (
                  <li key={`${f.start}-${i}`} className="rounded-lg bg-white/5 px-3 py-2">
                    <span className="font-mono text-[#ff7a1a]">
                      {formatClock(f.start)}–{formatClock(f.end)}
                    </span>{" "}
                    · {f.seconds.toFixed(2)}s · {f.reason}
                  </li>
                ))
              ) : (
                <li className="text-white/40">Nenhum trecho óbvio de silêncio.</li>
              )}
            </ul>
          </>
        ) : (
          <p className="text-sm text-white/40">Nenhum material carregado.</p>
        )}
      </section>

      <section className="rounded-2xl border border-white/10 bg-[#12151a] p-4">
        <p className="mb-3 text-xs uppercase tracking-[0.18em] text-white/40">
          Partes do vídeo
        </p>
        <div className="space-y-2">
          {analysis?.takes.map((take) => (
            <div
              key={take.id}
              className="rounded-xl border border-white/10 bg-black/30 px-3 py-3"
            >
              <p className="text-sm font-medium text-white">{take.label}</p>
              <p className="font-mono text-xs text-white/45">
                {formatClock(take.start)} → {formatClock(take.end)}
              </p>
              <div className="mt-2 h-2 overflow-hidden rounded-full bg-white/10">
                <div className="h-full w-2/3 rounded-full bg-gradient-to-r from-[#f5d76e] to-[#ff7a1a]" />
              </div>
            </div>
          )) || (
            <p className="text-sm text-white/40">Takes aparecem após a análise.</p>
          )}
        </div>
      </section>
    </div>
  );
}
