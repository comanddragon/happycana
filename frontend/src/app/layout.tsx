// app/layout.tsx
import type { Metadata } from 'next'
import { Fraunces, Space_Grotesk, IBM_Plex_Mono } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/providers/providers'
import {AgeGate} from "@/components/home/AgeGate";
import {CartDrawer} from "@/components/shop/CartDrawer";
import React from "react";
import {SiteShell} from "@/components/layout/SiteShell";

// next/font/google self-hosts these at build time (no runtime request to
// fonts.googleapis.com, no render-blocking <link>, no layout shift) and
// exposes each family as a CSS variable we wire into Tailwind below.
const fraunces = Fraunces({
    subsets: ['latin'],
    weight: ['300', '400', '500', '600', '700'],
    style: ['normal', 'italic'],
    variable: '--font-fraunces',
    display: 'swap',
})

const spaceGrotesk = Space_Grotesk({
    subsets: ['latin'],
    weight: ['400', '500', '600', '700'],
    variable: '--font-space-grotesk',
    display: 'swap',
})

const ibmPlexMono = IBM_Plex_Mono({
    subsets: ['latin'],
    weight: ['400', '500'],
    variable: '--font-ibm-plex-mono',
    display: 'swap',
})

export const metadata: Metadata = {
    metadataBase: new URL('https://yourstore.com'),
    title: {
        default: 'HappyCana — Modern Dispensary',
        template: '%s | HappyCana',
    },
    description: 'Flower, edibles, and concentrates from small-batch growers, third-party tested and delivered same-day.',
    openGraph: {
        type: 'website',
        siteName: 'HappyCana',
    },
    robots: { index: true, follow: true },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
        <html
            lang="en"
            suppressHydrationWarning
            className={`${fraunces.variable} ${spaceGrotesk.variable} ${ibmPlexMono.variable}`}
        >
        <body className="font-hc-body bg-hc-paper">
        <Providers>
            <AgeGate />
            <CartDrawer />
            <SiteShell>{children}</SiteShell>
        </Providers>
        </body>
        </html>
    )
}