import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "product-images.del1.vultrobjects.com", // Allows all Unsplash subdomains
      },
    ],
  },
};

export default nextConfig;
