import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Uploads de vídeo no /api/upload (local/dev). Em serverless, prefira storage externo.
  experimental: {
    proxyClientMaxBodySize: "512mb",
  },
  // Evita pânico do Turbopack com symlinks do .venv do kit (python -> /usr/bin/...).
  outputFileTracingRoot: path.join(__dirname),
  serverExternalPackages: [],
};

export default nextConfig;
