import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/",
        destination: "/app",
      },
      {
        source: "/home",
        destination: "/web/pages/home",
      },
      {
        source: "/login",
        destination: "/web/pages/login",
      },
      {
        source: "/signup",
        destination: "/web/pages/signup",
      },
      {
        source: "/settings",
        destination: "/web/pages/settings",
      },
      {
        source: "/profile",
        destination: "/web/pages/profile/[username]",
      },
      {
        source: "/messages",
        destination: "/web/pages/messages",
      },
      {
        source: "/communities",
        destination: "/web/pages/communities",
      },
      {
        source: "/administration",
        destination: "/web/pages/administration",
      },
      {
        source: "/administration/:id",
        destination: "/web/pages/administration/:id",
      },
      {
        source: "/notifications",
        destination: "/web/pages/notifications",
      },
    ];
  },
  images: {
    domains: ["res.cloudinary.com"],
  },  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  devIndicators: false,
};

export default nextConfig;
