import { Hero } from '@/components/home/Hero'
import { EffectsStrip } from '@/components/home/EffectsStrip'
import { BatchGrid } from '@/components/home/BatchGrid'
import { HowItWorks } from '@/components/home/HowItWorks'
import { LabTrust } from '@/components/home/LabTrust'
import { Reviews } from '@/components/home/Reviews'
import { CtaBand } from '@/components/home/CtaBand'

export default function HomePage() {
    return (
        <>
            <Hero />
            <EffectsStrip />
            <BatchGrid />
            <HowItWorks />
            <LabTrust />
            <Reviews />
            <CtaBand />
        </>
    )
}
