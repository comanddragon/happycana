import { Reveal } from '@/components/home/Reveal'

const REVIEWS = [
    {
        quote: "The lot number actually matches what's printed on my jar. I've never had that from a delivery service before.",
        who: 'MAYA R. · VERIFIED PICKUP',
    },
    {
        quote: 'Ordered at 2, picked up by 3. Staff walked me through terpenes without any of the hard sell.',
        who: 'DEVON T. · VERIFIED PICKUP',
    },
    {
        quote: "Quiet Static is the first thing that's actually let me sleep through the night. I check for it every restock.",
        who: 'PRIYA K. · VERIFIED DELIVERY',
    },
]

export function Reviews() {
    return (
        <section className="bg-hc-paper-2 px-7 py-22">
            <div className="mx-auto max-w-[1180px]">
                <Reveal>
                    <div className="inline-flex items-center gap-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-sage-dim before:h-px before:w-3.5 before:bg-current before:opacity-50">
                        From the pickup counter
                    </div>
                    <h2 className="mt-2.5 font-hc-display text-[24px] font-normal sm:text-[32px]">
                        Regulars talk about the details
                    </h2>
                </Reveal>

                <div className="mt-11 grid grid-cols-1 gap-6 md:grid-cols-3">
                    {REVIEWS.map((review, i) => (
                        <Reveal key={review.who} delay={i * 80} className="rounded-[18px] border border-hc-ink/[0.06] bg-white px-6.5 py-7">
                            <p className="text-[15px] leading-relaxed text-hc-ink">&ldquo;{review.quote}&rdquo;</p>
                            <div className="mt-4.5 font-hc-mono text-xs text-hc-ink-soft">{review.who}</div>
                        </Reveal>
                    ))}
                </div>
            </div>
        </section>
    )
}
