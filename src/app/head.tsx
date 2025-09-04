export default function Head() {
  const base = process.env.NEXT_PUBLIC_BASE_PATH || '';
  return (
    <>
      <link rel="manifest" href={`${base}/manifest.json`} />
      <meta name="theme-color" content="#111827" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
    </>
  );
}