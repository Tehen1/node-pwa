'use client';
import { useEffect } from 'react';
import { registerServiceWorker } from '../utils/registerSW';

export default function RegisterSWClient() {
  useEffect(() => {
    if (process.env.NODE_ENV === 'production') {
      registerServiceWorker();
    }
  }, []);
  return null;
}