import type { NextConfig } from "next";

const nextConfig = {
  output: 'export', // <-- CRUCIAL: Enables static HTML generation
  trailingSlash: true, // Recommended for clean Nginx sub-page routing paths
  images: {
    unoptimized: true, // Mandatory since static exports don't run an image server
  },
};

export default nextConfig;
