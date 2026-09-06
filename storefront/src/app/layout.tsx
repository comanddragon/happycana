// app/layout.tsx
import type { Metadata } from 'next'
import { Fraunces, Space_Grotesk, IBM_Plex_Mono } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/providers/providers'
import {AgeGate} from "@/verticals/cannabis/AgeGate";
import {CartDrawer} from "@/components/shop/CartDrawer";
import React from "react";
import {SiteShell} from "@/components/layout/SiteShell";
import Script from 'next/script'
import { Analytics } from '@/components/providers/Analytics'
import '@/components/blog/BlogContent.css'
import { DEFAULT_STOREFRONT_NAME, safeJsonLd, storefrontUrl } from '@/lib/storefront'
import { getStorefront } from '@/lib/storefront.server'
import { brandingString } from '@/storefront/config'
import { StorefrontProvider } from '@/storefront/StorefrontProvider'
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

export async function generateMetadata(): Promise<Metadata> {
    const storefront = await getStorefront()
    const name = storefront.name || DEFAULT_STOREFRONT_NAME
    const url = storefrontUrl(storefront)
    const description = brandingString(storefront, 'description')
        || process.env.NEXT_PUBLIC_STOREFRONT_DESCRIPTION
        || `Shop ${name}.`
    const ogImage = brandingString(storefront, 'og_image') || storefront.logo_url || '/og-default.png'
    return {
    metadataBase: new URL(url),
    applicationName: name,
    title: {
        default: brandingString(storefront, 'meta_title') || name,
        template: `%s | ${name}`,
    },
    description,
    creator: name,
    publisher: name,
    alternates: { canonical: '/' },
    openGraph: {
        type: 'website',
        siteName: name,
        images: [{ url: ogImage, alt: name }],
    },
    twitter: {
        card: 'summary_large_image',
        title: name,
        description,
        images: [ogImage],
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
}

export default async function RootLayout({ children }: { children: React.ReactNode }) {
    const storefront = await getStorefront()
    const name = storefront.name || DEFAULT_STOREFRONT_NAME
    const siteUrl = storefrontUrl(storefront)
    const logo = storefront.logo_url || `${siteUrl}/brand/logo-lockup-light-bg.png`
    const organizationLd = {
        '@context': 'https://schema.org',
        '@type': 'Organization',
        '@id': `${siteUrl}/#organization`,
        name,
        url: siteUrl,
        logo,
    }
    const websiteLd = {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        '@id': `${siteUrl}/#website`,
        name,
        url: siteUrl,
        publisher: { '@id': `${siteUrl}/#organization` },
        potentialAction: {
            '@type': 'SearchAction',
            target: `${siteUrl}/shop/products?search={search_term_string}`,
            'query-input': 'required name=search_term_string',
        },
    }
    return (
        <html
            lang="en"
            suppressHydrationWarning
            data-storefront={storefront.slug}
            data-vertical={storefront.kind}
            className={`${fraunces.variable} ${spaceGrotesk.variable} ${ibmPlexMono.variable}`}
        >
        <body className="font-hc-body bg-hc-paper">
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: safeJsonLd(organizationLd) }} />
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: safeJsonLd(websiteLd) }} />
        <Analytics />
        <StorefrontProvider storefront={storefront}>
            <Providers>
                <AgeGate />
                <CartDrawer />
                {/*<FloatingChatButton />*/}
                <SiteShell>{children}</SiteShell>
            </Providers>
        </StorefrontProvider>
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
