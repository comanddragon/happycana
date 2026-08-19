import { Reveal } from '@/components/home/Reveal'

const STEPS = [
    {
        num: '01 / BROWSE',
        title: 'Filter by feeling',
        body: "Sort the menu by effect, potency, or your favorite terpene instead of scrolling strain names you don't recognize.",
    },
    {
        num: '02 / VERIFY',
        title: "Confirm you're 21+",
        body: 'Upload your ID once at checkout. We verify in under a minute and remember you for next time.',
    },
    {
        num: '03 / RECEIVE',
        title: 'Pick up or get it delivered',
        body: 'Ready in store in about 20 minutes, or delivered same-day within our service area.',
    },
]

export function HowItWorks() {
    return (
        <section className="bg-hc-canopy-2 px-7 py-22 text-hc-paper">
            <div className="mx-auto max-w-[1180px]">
                <Reveal>
                    <div className="inline-flex items-center gap-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-amber-light before:h-px before:w-3.5 before:bg-current before:opacity-50">
                        Ordering, start to finish
                    </div>
                    <h2 className="mt-2.5 max-w-[560px] font-hc-display text-[28px] font-normal sm:text-4xl">
                        Three steps, no waiting around
                    </h2>
                </Reveal>

                <div className="mt-13 grid grid-cols-1 gap-9 md:grid-cols-3 md:gap-0">
                    {STEPS.map((step, i) => (
                        <Reveal
                            key={step.num}
                            delay={i * 100}
                            className={
                                i > 0
                                    ? 'border-t border-hc-paper/[0.12] pt-8 md:border-t-0 md:border-l md:pt-0 md:pl-7.5'
                                    : 'md:pr-7.5'
                            }
                        >
                            <div className="font-hc-mono text-[13px] tracking-wide text-hc-amber-light">{step.num}</div>
                            <h3 className="mb-2.5 mt-3.5 font-hc-display text-[22px] font-medium">{step.title}</h3>
                            <p className="text-[14.5px] leading-relaxed text-hc-sage">{step.body}</p>
                        </Reveal>
                    ))}
                </div>
            </div>
        </section>
    )
}
