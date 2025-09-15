import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  eslint: {
    // Skip ESLint during production builds to avoid blocking on stylistic issues
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
