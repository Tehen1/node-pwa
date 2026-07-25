// next.config.ts for GitHub Pages static export
import path from 'path';

/** @type {import('next').NextConfig} */
const isGithubPages = process.env.DEPLOY_TARGET === 'github-pages';
const basePath = isGithubPages ? '/studio-fixierun-ai-coach' : '';

const nextConfig = {
  reactStrictMode: true,
  basePath,
  assetPrefix: basePath || undefined,
  output: 'export',
  distDir: 'dist',
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;