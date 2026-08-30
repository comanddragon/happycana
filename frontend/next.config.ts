import BuilderDevTools from "@builder.io/dev-tools/next";
import type { NextConfig } from "next";

const nextConfig: NextConfig = BuilderDevTools()({
    turbopack: {},
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**" },
      { protocol: "http", hostname: "localhost", port: "8000" },
      { protocol: "http", hostname: "192.168.1.182", port: "8000" }
    ],
  },
  allowedDevOrigins: ["192.168.1.182"],
  reactCompiler: true,
  skipTrailingSlashRedirect: true,
  async rewrites() {
    return [
      { source: "/api/:path*/", destination: "http://127.0.0.1:8000/api/:path*/" },
      { source: "/api/:path*", destination: "http://127.0.0.1:8000/api/:path*" },
    ]
  },
});

export default nextConfig;