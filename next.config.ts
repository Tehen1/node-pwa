// next.config.ts for GitHub Pages static export
import path from 'path';

/** @type {import('next').NextConfig} */
const isGithubPages = process.env.DEPLOY_TARGET === 'github-pages';
const basePath = isGithubPages ? '/studio-fixierun-ai-coach' : '';

const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  basePath,
  assetPrefix: basePath || undefined,
  output: 'export', // force static export; ensure app is exportable (no SSR)
};

export default nextConfig;