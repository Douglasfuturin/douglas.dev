#!/usr/bin/env node
/**
 * Smoke tests for Central de Agentes APIs (run with dev server on :3000).
 * Usage: node scripts/smoke-api.mjs [baseUrl]
 */
const BASE = process.argv[2] || "http://localhost:3000";

const results = [];

function pass(name, detail = "") {
  results.push({ name, ok: true, detail });
  console.log(`✓ ${name}${detail ? ` — ${detail}` : ""}`);
}

function fail(name, detail = "") {
  results.push({ name, ok: false, detail });
  console.error(`✗ ${name}${detail ? ` — ${detail}` : ""}`);
}

async function getJson(path, opts = {}) {
  const res = await fetch(`${BASE}${path}`, opts);
  const text = await res.text();
  let json;
  try {
    json = JSON.parse(text);
  } catch {
    json = { _raw: text.slice(0, 200) };
  }
  return { status: res.status, json, text };
}

async function main() {
  console.log(`Smoke tests → ${BASE}\n`);

  // Pages
  for (const route of [
    "/",
    "/app",
    "/app/studio",
    "/dashboard",
    "/editor",
    "/central",
    "/grupos",
    "/agentes",
    "/kits",
  ]) {
    const res = await fetch(`${BASE}${route}`);
    if (res.status === 200) pass(`GET ${route}`, String(res.status));
    else fail(`GET ${route}`, `status ${res.status}`);
  }

  // Redirects
  const studio = await fetch(`${BASE}/studio`, { redirect: "manual" });
  const loc = studio.headers.get("location") || "";
  if (studio.status >= 300 && studio.status < 400 && loc.includes("/app/studio")) {
    pass("GET /studio redirect", loc);
  } else {
    fail("GET /studio redirect", `status ${studio.status} loc=${loc}`);
  }

  // APIs GET
  const apis = [
    "/api/groups",
    "/api/agents",
    "/api/content",
    "/api/kits",
    "/api/publish",
  ];
  for (const path of apis) {
    const { status, json } = await getJson(path);
    if (status === 200) pass(`GET ${path}`, `keys: ${Object.keys(json).join(",")}`);
    else fail(`GET ${path}`, `status ${status}`);
  }

  // Groups structure
  const { json: groupsJson } = await getJson("/api/groups");
  const groups = groupsJson.groups || [];
  const builtin = ["conteudo-dev", "conteudo-dev-video", "conteudos-espanha"];
  for (const id of builtin) {
    if (groups.some((g) => g.id === id)) pass(`group ${id} present`);
    else fail(`group ${id} present`, "missing");
  }

  // Media + editor analyze (demo video)
  const demoPath = `${process.cwd()}/workspace/videos/demo-editor.mp4`;
  const { status: mediaStatus } = await getJson(
    `/api/media?path=${encodeURIComponent(demoPath)}`,
  );
  if (mediaStatus === 200) pass("GET /api/media demo-editor.mp4");
  else fail("GET /api/media", `status ${mediaStatus}`);

  const analyzeStart = Date.now();
  const { status: analyzeStatus, json: analysis } = await getJson(
    "/api/editor/analyze",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: demoPath, transcribe: false }),
    },
  );
  const analyzeMs = Date.now() - analyzeStart;
  if (analyzeStatus === 200 && analysis.duration > 0 && Array.isArray(analysis.waveform)) {
    pass(
      "POST /api/editor/analyze",
      `${analysis.duration}s ${analysis.width}x${analysis.height} waveform=${analysis.waveform.length} (${analyzeMs}ms)`,
    );
  } else {
    fail("POST /api/editor/analyze", `status ${analyzeStatus} ${JSON.stringify(analysis).slice(0, 120)}`);
  }

  // Upload small file
  const demoBuf = await fetch(`${BASE}/api/media?path=${encodeURIComponent(demoPath)}`).then(
    (r) => r.arrayBuffer(),
  );
  const form = new FormData();
  form.append("file", new Blob([demoBuf], { type: "video/mp4" }), "smoke-upload.mp4");
  const uploadRes = await fetch(`${BASE}/api/upload`, { method: "POST", body: form });
  const uploadJson = await uploadRes.json();
  if (uploadRes.ok && uploadJson.path) {
    pass("POST /api/upload", uploadJson.filename);
    const { status: a2 } = await getJson("/api/editor/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: uploadJson.path, transcribe: false }),
    });
    if (a2 === 200) pass("POST /api/editor/analyze (uploaded file)");
    else fail("POST /api/editor/analyze (uploaded file)", `status ${a2}`);
  } else {
    fail("POST /api/upload", JSON.stringify(uploadJson));
  }

  // Chat (expects 500 without key or 200 stream with key)
  const chatRes = await fetch(`${BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      mode: "orquestrador",
      messages: [{ id: "1", role: "user", parts: [{ type: "text", text: "ping" }] }],
    }),
  });
  if (chatRes.status === 500) {
    const err = await chatRes.json();
    if (err.error?.includes("XAI_API_KEY")) {
      pass("POST /api/chat", "missing XAI_API_KEY (expected in CI)");
    } else {
      fail("POST /api/chat", JSON.stringify(err));
    }
  } else if (chatRes.ok) {
    pass("POST /api/chat", `status ${chatRes.status} (stream)`);
  } else {
    fail("POST /api/chat", `status ${chatRes.status}`);
  }

  const failed = results.filter((r) => !r.ok);
  console.log(`\n${results.length - failed.length}/${results.length} passed`);
  process.exit(failed.length ? 1 : 0);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
