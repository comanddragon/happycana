// app/layout.tsx
import type { Metadata } from 'next'
import { Fraunces, Space_Grotesk, IBM_Plex_Mono } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/providers/providers'
import {AgeGate} from "@/components/home/AgeGate";
import {CartDrawer} from "@/components/shop/CartDrawer";
import React from "react";
import {SiteShell} from "@/components/layout/SiteShell";
import Script from 'next/script'
import { Analytics } from '@/components/providers/Analytics'
import '@/components/blog/BlogContent.css'
// import {FloatingChatButton} from '@/components/chat/FloatingChatButton'


const fraunces = Fraunces({
    subsets: ['latin'],
    weight: ['400', '500', '600'],
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
    metadataBase: new URL(`${process.env.NEXT_PUBLIC_FRONTEND_URL}`),
    title: {
        default: 'HappyCana — Modern Dispensary',
        template: '%s | HappyCana',
    },
    description: 'Flower, edibles, and concentrates from small-batch growers, third-party tested and delivered same-day.',
    openGraph: {
        type: 'website',
        siteName: 'HappyCana',
        images: [{ url: '/og-default.png', width: 1200, height: 630, alt: 'HappyCana — Modern Dispensary' }],
    },
    twitter: {
        card: 'summary_large_image',
        title: 'HappyCana — Modern Dispensary',
        description: 'Flower, edibles, and concentrates from small-batch growers, third-party tested and delivered same-day.',
        images: ['/og-default.png'],
    },
    robots: { index: true, follow: true },
    icons: {
        icon: '/favicon.ico',
        apple: '/apple-touch-icon.png',
    },
    // Search Console (and other engine) ownership verification. Values are
    // read from env so nothing is committed here; unset keys are simply
    // omitted from the rendered <meta> tags by Next.
    verification: {
        google: process.env.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION,
        other: {
            ...(process.env.NEXT_PUBLIC_BING_SITE_VERIFICATION && {
                'msvalidate.01': process.env.NEXT_PUBLIC_BING_SITE_VERIFICATION,
            }),
        },
    },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
        <html
            lang="en"
            suppressHydrationWarning
            className={`${fraunces.variable} ${spaceGrotesk.variable} ${ibmPlexMono.variable}`}
        >
        <body className="font-hc-body bg-hc-paper">
        <Analytics />
        <Providers>
            <AgeGate />
            <CartDrawer />
            {/*<FloatingChatButton />*/}
            <SiteShell>{children}</SiteShell>
        </Providers>
        <Script id="smartsupp-widget" strategy="lazyOnload">
            {`
            var _smartsupp = _smartsupp || {};
            _smartsupp.key = '${process.env.NEXT_PUBLIC_SMARTSUPP_KEY}';
            window.smartsupp || (function (d) {
              var s, c, o = smartsupp = function () { o._.push(arguments) };
              o._ = [];
              s = d.getElementsByTagName('script')[0];
              c = d.createElement('script');
              c.type = 'text/javascript';
              c.charset = 'utf-8';
              c.async = true;
              c.src = 'https://www.smartsuppchat.com/loader.js?';
              s.parentNode.insertBefore(c, s);
            })(document);
          `}
        </Script>
        <noscript>Powered by <a href="https://www.smartsupp.com" target="_blank">Smartsupp</a></noscript>
        </body>
        </html>
    )
}