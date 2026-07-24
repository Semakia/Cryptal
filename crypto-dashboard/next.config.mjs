/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  // `standalone` sert au build Docker auto-hébergé (le Dockerfile copie
  // .next/standalone). Sur Vercel, ce mode casse le routage et provoque un
  // 404 NOT_FOUND : la variable VERCEL=1 est injectée par la plateforme, on
  // retombe alors sur la sortie par défaut qu'elle attend.
  output: process.env.VERCEL ? undefined : "standalone",
};

export default nextConfig;
