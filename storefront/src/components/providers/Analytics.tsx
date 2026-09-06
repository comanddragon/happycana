// components/providers/Analytics.tsx
// Google Analytics 4 (gtag.js) loader. Renders nothing unless
// NEXT_PUBLIC_GA_MEASUREMENT_ID is set, so it's a no-op in local/dev
// environments and safe to leave in the tree.
import Script from 'next/script'

export function Analytics() {
    const gaId = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID
    if (!gaId) return null

    return (
        <>
            <Script
                id="ga4-lib"
                strategy="afterInteractive"
                src={`https://www.googletagmanager.com/gtag/js?id=${gaId}`}
            />
            <Script id="ga4-init" strategy="afterInteractive">
                {`
                    window.dataLayer = window.dataLayer || [];
                    function gtag(){dataLayer.push(arguments);}
                    gtag('js', new Date());
                    gtag('config', '${gaId}');
                `}
            </Script>
        </>
    )
}
