export function registerServiceWorker() {
  if (typeof window === 'undefined') return;
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      const base = process.env.NEXT_PUBLIC_BASE_PATH || '';
      // For gh-pages the sw will be at /<repo>/sw.js -> base + /sw.js
      const swUrl = `${base}/sw.js`;
      navigator.serviceWorker.register(swUrl).catch((err) => {
        // eslint-disable-next-line no-console
        console.warn('SW registration failed:', err);
      });
    });
  }
}