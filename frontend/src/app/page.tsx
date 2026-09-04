import type { Metadata } from 'next'
import { Hero } from '@/components/home/Hero'
import { EffectsStrip } from '@/components/home/EffectsStrip'
import { HomeCategories } from '@/components/home/HomeCategories'
import { BatchGrid } from '@/components/home/BatchGrid'
import { HowItWorks } from '@/components/home/HowItWorks'
import { LabTrust } from '@/components/home/LabTrust'
import { Reviews } from '@/components/home/Reviews'
import { CtaBand } from '@/components/home/CtaBand'

export const metadata: Metadata = {
    title: 'Lab-Tested Cannabis for Pickup & Delivery',
    description: 'Shop lab-tested cannabis flower, edibles, pre-rolls, vapes, concentrates, CBD products, and more from HappyCana.',
    alternates: { canonical: '/' },
    openGraph: {
        title: 'HappyCana | Lab-Tested Cannabis for Pickup & Delivery',
        description: 'Explore trusted cannabis products by category, effect, and format with transparent potency and lab information.',
        type: 'website',
    },
}

export default function HomePage() {
    return (
        <>
            <Hero />
            <EffectsStrip />
            <HomeCategories />
            <BatchGrid />
            <HowItWorks />
            <LabTrust />
            <Reviews />
            <CtaBand />
        </>
    )
}
