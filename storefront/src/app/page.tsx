import type { Metadata } from 'next'
import { Hero } from '@/components/home/Hero'
import { EffectsStrip } from '@/components/home/EffectsStrip'
import { HomeCategories } from '@/components/home/HomeCategories'
import { BatchGrid } from '@/components/home/BatchGrid'
import { HowItWorks } from '@/components/home/HowItWorks'
import { LabTrust } from '@/components/home/LabTrust'
import { Reviews } from '@/components/home/Reviews'
import { CtaBand } from '@/components/home/CtaBand'
import { DEFAULT_STOREFRONT_NAME } from '@/lib/storefront'
import { getStorefront } from '@/lib/storefront.server'
import { PeptideHome } from '@/verticals/peptides/PeptideHome'

export async function generateMetadata(): Promise<Metadata> {
    const storefront = await getStorefront()
    const peptides = storefront.kind === 'peptides'
    const title = peptides ? 'Research Peptides with Clear Provenance' : 'Lab-Tested Cannabis for Pickup & Delivery'
    const description = peptides
        ? `Browse research-use-only compounds with source documentation from ${storefront.name}.`
        : `Shop lab-tested cannabis flower, edibles, pre-rolls, vapes, concentrates, CBD products, and more from ${DEFAULT_STOREFRONT_NAME}.`
    return {
        title,
        description,
        alternates: { canonical: '/' },
        openGraph: { title: `${storefront.name} | ${title}`, description, type: 'website' },
    }
}

export default async function HomePage() {
    const storefront = await getStorefront()
    if (storefront.kind === 'peptides') return <PeptideHome storefront={storefront} />
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
