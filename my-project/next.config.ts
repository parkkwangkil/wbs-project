import type { NextConfig } from "next";

// Forward all routes to the Django backend so the Vercel app serves the real site
// Uses NEXT_PUBLIC_API_BASE set in Vercel envs (falls back to local dev)
const backendBase = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      { source: "/", destination: `${backendBase}/` },
      { source: "/:path*", destination: `${backendBase}/:path*` },
    ];
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "*.trycloudflare.com",
      },
    ],
  },
};

export default nextConfig;
