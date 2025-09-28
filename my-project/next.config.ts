import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Match Django's trailing slash to avoid /login <-> /login/ loops
  trailingSlash: true,
  // Don't normalize URL before middleware (keep original path)
  skipMiddlewareUrlNormalize: true,
  // Rewrites handled in middleware to avoid conflicts/loops
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
