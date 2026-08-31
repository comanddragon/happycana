import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {},
  images: {
    loader: "custom",
    loaderFile: "./src/lib/imgix-loader.ts",
    remotePatterns: [
      { protocol: "https", hostname: "**" },
      { protocol: "http", hostname: "localhost", port: "8000" },
      { protocol: "http", hostname: "192.168.1.182", port: "8000" }
    ],
    qualities: [40, 65, 75, 85],
  },
  allowedDevOrigins: ["192.168.1.182"],
  reactCompiler: true,
  skipTrailingSlashRedirect: true,
  async rewrites() {
    const backend =
      process.env.BACKEND_ORIGIN || "http://127.0.0.1:8000";

    return [
      { source: "/api/:path*/", destination: `${backend}/api/:path*/` },
      { source: "/api/:path*", destination: `${backend}/api/:path*` },
      { source: "/media/:path*", destination: `${backend}/media/:path*` },
    ];
  },
};

export default nextConfig;