'use client'

import Link from 'next/link'
import { Reveal } from '@/components/home/Reveal'
import { useEffects } from '@/hooks/useApi'

// The Effect model only carries name/slug — no description field — so we
// keep a small copy map for the handful of effects we have nice blurbs
// for, and fall back to no subtitle for anything else (new effects added
// on the backend still render correctly, just without custom copy).
const EFFECT_COPY: Record<string, string> = {
    uplift: 'Energizing, creative, daytime',
    unwind: 'Light body ease, evening',
    rest: 'Heavy calm, sleep support',
    focus: 'Clear-headed, low-key',
    social: 'Easy, talkative, shared',
}

export function EffectsStrip() {
    const { data: effects, isLoading } = useEffects()

    if (!isLoading && (!effects || effects.length === 0)) return null

    return (
        <section id="effects" className="border-b border-hc-ink/[0.08] bg-hc-paper px-7 py-14">
            <div className="mx-auto max-w-[1180px]">
                <Reveal className="mb-8 text-center">
                    <div className="inline-flex items-center gap-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-sage-dim before:h-px before:w-3.5 before:bg-current before:opacity-50">
                        Shop the menu
                    </div>
                    <h2 className="mt-2.5 font-hc-display text-[26px] font-normal sm:text-3xl">
                        Choose by how you want to feel
                    </h2>
                </Reveal>

                <Reveal className="grid grid-cols-2 gap-3.5 sm:grid-cols-5">
                    {isLoading
                        ? Array.from({ length: 5 }).map((_, i) => (
                            <div
                                key={i}
                                className="animate-pulse rounded-2xl border border-hc-ink/[0.08] bg-white px-4 py-5 text-center"
                            >
                                <div className="mx-auto mb-3 h-8.5 w-8.5 rounded-full bg-hc-ink/[0.06]" />
                                <div className="mx-auto h-3.5 w-16 rounded bg-hc-ink/[0.06]" />
                                <div className="mx-auto mt-2 h-3 w-24 rounded bg-hc-ink/[0.06]" />
                            </div>
                        ))
                        : effects!.map(effect => (
                            <Link
                                key={effect.id}
                                href={`/shop/products?effect=${effect.slug}`}
                                className="rounded-2xl border border-hc-ink/[0.08] bg-white px-4 py-5 text-center transition-all duration-200 hover:-translate-y-1 hover:border-hc-amber hover:shadow-[0_16px_30px_-14px_rgba(23,20,15,0.25)]"
                            >
                                <div className="mx-auto mb-3 flex h-8.5 w-8.5 items-center justify-center rounded-full bg-hc-canopy">
                                    <span className="h-2 w-2 rounded-full bg-hc-amber-light" />
                                </div>
                                <h3 className="text-[15px] font-semibold text-hc-ink capitalize">{effect.name}</h3>
                                {EFFECT_COPY[effect.slug] && (
                                    <p className="mt-1 text-xs leading-tight text-hc-ink-soft">
                                        {EFFECT_COPY[effect.slug]}
                                    </p>
                                )}
                            </Link>
                        ))}
                </Reveal>
            </div>
        </section>
    )
}