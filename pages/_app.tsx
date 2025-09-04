import type { AppProps } from 'next/app';
import Head from 'next/head';
import { useEffect } from 'react';
import { registerServiceWorker } from '../utils/registerSW';
import '../styles/globals.css';

function MyApp({ Component, pageProps }: AppProps) {
  useEffect(() => {
    if (process.env.NODE_ENV === 'production') {
      registerServiceWorker();
    }
  }, []);

  return (
    <>
      <Head>
        <link rel="manifest" href={`${process.env.NEXT_PUBLIC_BASE_PATH || ''}/manifest.json`} />
        <meta name="theme-color" content="#111827" />
      </Head>
      <Component {...pageProps} />
    </>
  );
}

export default MyApp;