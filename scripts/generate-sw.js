/**
 * Génère out/sw.js après `next export` pour GitHub Pages
 */
const workboxBuild = require('workbox-build');
const path = require('path');

const OUT_DIR = path.join(process.cwd(), 'out');

workboxBuild.generateSW({
  swDest: path.join(OUT_DIR, 'sw.js'),
  globDirectory: OUT_DIR,
  globPatterns: [
    '**/*.{html,js,css,png,jpg,svg,json,ico,webmanifest}'
  ],
  runtimeCaching: [
    {
      urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
      handler: 'CacheFirst',
      options: {
        cacheName: 'images-cache',
        expiration: {
          maxEntries: 60,
          maxAgeSeconds: 30 * 24 * 60 * 60
        },
      },
    },
    {
      urlPattern: /^https?.*/,
      handler: 'NetworkFirst',
      options: {
        cacheName: 'http-responses',
        networkTimeoutSeconds: 10,
      },
    },
  ],
  skipWaiting: true,
  clientsClaim: true,
}).then(({ count, size }) => {
  console.log(`Generated sw.js, precached ${count} files, total ${size} bytes.`);
}).catch(err => {
  console.error('Error generating SW:', err);
  process.exit(1);
});