import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Uploads de vídeo no /api/upload (local/dev). Em serverless, prefira storage externo.
  experimental: {
    proxyClientMaxBodySize: "512mb",
  },
  serverExternalPackages: [],
};

export default nextConfig;
