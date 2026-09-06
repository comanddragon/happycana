import { JarCard } from '@/components/home/JarCard'
import { getProducts } from '@/lib/catalog.server'
import { toJarProduct } from '@/lib/jarProduct'

const STATS = [
    { value: '48hr',    label: 'LAB TURNAROUND' },
    { value: '12-panel', label: 'CONTAMINANT SCREEN' },
    { value: '20min',   label: 'AVG. PICKUP TIME' },
]

export async function Hero() {
    const { results } = await getProducts(
        { ordering: '-created_at', page_size: 1, min_thc: 0.01 },
        { revalidate: false },
    )
    const heroJar = results[0] ? toJarProduct(results[0]) : null

    return (
        <section
            id="top"
            className="relative overflow-hidden bg-[radial-gradient(120%_90%_at_50%_0%,var(--color-hc-canopy-3),var(--color-hc-canopy)_55%,var(--color-hc-canopy-2))] px-7 py-24 text-hc-paper sm:py-28"
        >
            <div
                aria-hidden
                className="pointer-events-none absolute left-1/2 top-[-10%] h-[900px] w-[900px] -translate-x-1/2 animate-[hc-pulse_7s_ease-in-out_infinite] rounded-full blur-[10px] motion-reduce:animate-none"
                style={{ background: 'radial-gradient(circle, rgba(200,121,46,.35), transparent 62%)' }}
            />

            <div className="relative mx-auto grid max-w-[1180px] grid-cols-1 items-center gap-14 md:grid-cols-[1.1fr_0.9fr] md:gap-16">
                <div>
                    <div className="mb-5 inline-flex items-center gap-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-amber-light before:h-px before:w-3.5 before:bg-current before:opacity-50">
                        Same-day pickup &amp; delivery
                    </div>
                    <h1 className="font-hc-display text-[38px] font-normal leading-[1.06] tracking-tight sm:text-5xl lg:text-[64px]">
                        Grown slow.<br />
                        Tested twice.<br />
                        <em className="font-medium not-italic italic text-hc-amber-light">Felt once you exhale.</em>
                    </h1>
                    <p className="mt-6 max-w-[480px] text-[16.5px] leading-relaxed text-hc-sage">
                        Flower, edibles, and concentrates from small-batch growers — every lot third-party tested for potency and purity before it ever reaches your door.
                    </p>
                    <div className="mt-9 flex flex-wrap gap-3.5">
                        <a
                            href="#effects"
                            className="inline-flex items-center justify-center gap-2 rounded-full px-6.5 py-3.5 text-sm font-semibold text-hc-canopy-2 shadow-[0_6px_18px_rgba(200,121,46,.35)] transition-transform hover:-translate-y-0.5 hover:shadow-[0_10px_24px_rgba(200,121,46,.45)]"
                            style={{ background: 'linear-gradient(180deg, var(--color-hc-amber-light), var(--color-hc-amber))' }}
                        >
                            Shop by effect
                        </a>
                        <a
                            href="#batch"
                            className="inline-flex items-center justify-center gap-2 rounded-full border border-hc-paper/35 bg-hc-paper/[0.04] px-6.5 py-3.5 text-sm font-semibold text-hc-paper transition-transform hover:-translate-y-0.5 hover:bg-hc-paper/10"
                        >
                            View today&rsquo;s menu
                        </a>
                    </div>
                    <div className="mt-13 flex flex-wrap gap-7 font-hc-mono">
                        {STATS.map(stat => (
                            <div key={stat.label}>
                                <strong className="block text-[22px] font-normal text-hc-paper">{stat.value}</strong>
                                <span className="text-[11.5px] tracking-wide text-hc-sage-dim">{stat.label}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {heroJar && (
                    <div className="relative mx-auto max-w-[340px] md:max-w-none">
                        <JarCard
                            className="rotate-[-3deg] animate-[hc-float_6s_ease-in-out_infinite] motion-reduce:animate-none"
                            interactive
                            product={heroJar}
                        />
                        <div className="absolute -bottom-6.5 -left-6.5 flex items-center gap-2.5 rounded-[22px] border border-hc-paper/[0.14] bg-hc-canopy-2 px-4.5 py-3.5 font-hc-mono text-[11.5px] text-hc-paper shadow-[0_20px_40px_-12px_rgba(0,0,0,0.5)]">
                            <span className="h-2 w-2 rounded-full bg-hc-amber-light shadow-[0_0_10px_var(--color-hc-amber-light)]" />
                            Batch cleared · third-party lab
                        </div>
                    </div>
                )}
            </div>
        </section>
    )
}
