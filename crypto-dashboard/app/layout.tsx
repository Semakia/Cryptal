<<<<<<< HEAD
import type React from "react"
import type { Metadata, Viewport } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import "./globals.css"
import { Providers } from "@/components/providers"
import { Toaster } from "@/components/ui/toaster"

const _geist = Geist({ subsets: ["latin"] })
const _geistMono = Geist_Mono({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Crypto Viz - Analytics Dashboard",
=======
import type React from "react";
import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Analytics } from "@vercel/analytics/next";
import "./globals.css";
import { Providers } from "@/components/providers";
import { Toaster } from "@/components/ui/toaster";

const _geist = Geist({ subsets: ["latin"] });
const _geistMono = Geist_Mono({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "CrypTal - Analytics Dashboard",
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
  description:
    "Real-time cryptocurrency analytics platform with price tracking, risk metrics, and investment simulation tools",
  generator: "v0.app",
  icons: {
    icon: [
      {
        url: "/icon-light-32x32.png",
        media: "(prefers-color-scheme: light)",
      },
      {
        url: "/icon-dark-32x32.png",
        media: "(prefers-color-scheme: dark)",
      },
      {
        url: "/icon.svg",
        type: "image/svg+xml",
      },
    ],
    apple: "/apple-icon.png",
  },
<<<<<<< HEAD
}
=======
};
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f8f8fc" },
    { media: "(prefers-color-scheme: dark)", color: "#1a1a2e" },
  ],
  width: "device-width",
  initialScale: 1,
<<<<<<< HEAD
}
=======
};
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1

export default function RootLayout({
  children,
}: Readonly<{
<<<<<<< HEAD
  children: React.ReactNode
=======
  children: React.ReactNode;
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="font-sans antialiased">
        <Providers>
          {children}
          <Toaster />
        </Providers>
        <Analytics />
      </body>
    </html>
<<<<<<< HEAD
  )
=======
  );
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
}
