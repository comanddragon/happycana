import { JarCard, type JarProduct } from '@/components/home/JarCard'
import { Reveal } from '@/components/home/Reveal'

const BATCH: JarProduct[] = [
    { name: 'Velvet Horizon', kind: 'HYBRID', thc: '24.1%', terpene: 'Myrcene',  effect: 'Unwind', lot: 'HC-0417', testedOn: '04.17', price: '$46 / 3.5g' },
    { name: 'Quiet Static',   kind: 'INDICA', thc: '21.6%', terpene: 'Linalool', effect: 'Rest',   lot: 'HC-0411', testedOn: '04.11', price: '$42 / 3.5g' },
    { name: 'Amber Daylight', kind: 'SATIVA', thc: '19.8%', terpene: 'Limonene', effect: 'Uplift', lot: 'HC-0429', testedOn: '04.29', price: '$44 / 3.5g' },
]

export function BatchGrid() {
    return (
        <section id="batch" className="bg-hc-paper px-7 py-24">
            <div className="mx-auto max-w-[1180px]">
                <Reveal className="mb-11 flex flex-wrap items-end justify-between gap-6">
                    <div>
                        <div className="inline-flex items-center gap-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-sage-dim before:h-px before:w-3.5 before:bg-current before:opacity-50">
                            This week&rsquo;s batch
                        </div>
                        <h2 className="mt-2.5 max-w-[520px] font-hc-display text-[28px] font-normal sm:text-4xl">
                            Harvested April · results posted within 48 hours
                        </h2>
                    </div>
                    <p className="max-w-[320px] text-sm text-hc-ink-soft">
                        Every jar ships with its own lot number — scan it to read the full certificate of analysis.
                    </p>
                </Reveal>

                <div className="grid grid-cols-1 gap-6.5 md:grid-cols-3">
                    {BATCH.map((product, i) => (
                        <Reveal key={product.lot} delay={i * 80}>
                            <JarCard product={product} interactive />
                        </Reveal>
                    ))}
                </div>
            </div>
        </section>
    )
}
