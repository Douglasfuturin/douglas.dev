import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Uploads de vídeo no /api/upload (local/dev). Em serverless, prefira storage externo.
  experimental: {
    proxyClientMaxBodySize: "512mb",
  },
  // Dev server listens on 0.0.0.0; Next only trusts `localhost` unless listed here.
  allowedDevOrigins: ["127.0.0.1"],
  serverExternalPackages: [],
};

export default nextConfig;
