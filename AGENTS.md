<!-- BEGIN:nextjs-agent-rules -->

# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->

## Cursor Cloud specific instructions

- Next.js app at the repo root. Install with `npm ci`, then `npx next typegen` so route helpers such as `LayoutProps` exist for `tsc`. Dev server: `npm run dev -- --hostname 0.0.0.0 --port 3000`. Pages: `/` (chat) and `/editor` (visual editor). Lint: `npm run lint`. Typecheck: `npx tsc --noEmit` after typegen. Production build: `npm run build`.
- Video kit lives in `kit-edicao-video/skill`. Install with `uv sync --frozen` from that directory. The app invokes `kit-edicao-video/skill/.venv/bin/python`. `uv` must be on the default PATH (`/usr/local/bin`), because login shells do not load `~/.bashrc`. `ffmpeg` and `ffprobe` must be on PATH for `/api/editor/analyze`.
- `XAI_API_KEY` (see `.env.example`) is required only for `/api/chat`. The UI, `/api/upload`, and `/api/editor/analyze` run without it. Analyze with `transcribe: true` downloads a Whisper model on first use; pass `transcribe: false` for a local probe of duration, waveform, and silence.
