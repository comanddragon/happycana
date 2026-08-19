import { Reveal } from '@/components/home/Reveal'

const STATS = [
    { value: '100%', label: 'BATCHES TESTED' },
    { value: '48hr', label: 'AVG. TURNAROUND' },
    { value: '12',   label: 'PANEL SCREEN' },
]

export function LabTrust() {
    return (
        <section id="lab" className="bg-hc-paper px-7 py-24">
            <div className="mx-auto grid max-w-[1180px] grid-cols-1 items-center gap-12 md:grid-cols-2 md:gap-16">
                <Reveal>
                    <div className="inline-flex items-center gap-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-sage-dim before:h-px before:w-3.5 before:bg-current before:opacity-50">
                        Third-party tested
                    </div>
                    <h2 className="mt-2.5 font-hc-display text-[28px] font-normal sm:text-4xl">
                        Nothing reaches the shelf untested.
                    </h2>
                    <p className="mt-4.5 max-w-[460px] text-[15px] leading-relaxed text-hc-ink-soft">
                        Every batch is sent to an independent lab for potency and contaminant screening — pesticides, heavy metals, microbials, and residual solvents. The lot number on your jar links straight to that batch&rsquo;s certificate.
                    </p>
                    <div className="mt-9 flex">
                        {STATS.map((stat, i) => (
                            <div key={stat.label} className={i > 0 ? 'border-l border-hc-ink/10 pl-5.5' : 'pr-5.5'}>
                                <strong className="block font-hc-mono text-[26px] font-medium text-hc-amber-dim">{stat.value}</strong>
                                <span className="text-[11.5px] tracking-wide text-hc-ink-soft">{stat.label}</span>
                            </div>
                        ))}
                    </div>
                </Reveal>

                <Reveal className="order-first justify-self-center md:order-last">
                    <div className="relative flex aspect-square w-[200px] items-center justify-center rounded-full border-2 border-dashed border-hc-ink/25 sm:w-[280px]">
                        <div className="absolute inset-4 rounded-full border border-hc-ink/15" />
                        <div className="text-center">
                            <div className="font-hc-mono text-[34px] font-medium text-hc-canopy">COA</div>
                            <div className="mt-1.5 font-hc-mono text-[10.5px] uppercase tracking-[0.1em] text-hc-ink-soft">
                                Certificate of<br />Analysis · Verified
                            </div>
                        </div>
                    </div>
                </Reveal>
            </div>
        </section>
    )
}
