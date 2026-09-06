import { Reveal } from '@/components/home/Reveal'

interface Props {
    heading?: string
    subheading?: string
    href?: string
    label?: string
}

export function CtaBand({
    heading = 'This week\u2019s batch won\u2019t last the week.',
    subheading = 'Same-day pickup, next-day delivery, every lot tested twice.',
    href = '#batch',
    label = 'View today\u2019s menu',
}: Props) {
    return (
        <section className="bg-[linear-gradient(120deg,var(--color-hc-canopy-3),var(--color-hc-canopy)_60%)] px-7 py-18 text-center text-hc-paper">
            <Reveal className="mx-auto max-w-[1180px]">
                <h2 className="font-hc-display text-[26px] font-normal sm:text-4xl">
                    {heading}
                </h2>
                <p className="mt-3 text-[15px] text-hc-sage">
                    {subheading}
                </p>
                <div className="mt-7.5 flex justify-center">
                    <a
                        href={href}
                        className="inline-flex items-center justify-center gap-2 rounded-full px-6.5 py-3.5 text-sm font-semibold text-hc-canopy-2 shadow-[0_6px_18px_rgba(200,121,46,.35)] transition-transform hover:-translate-y-0.5 hover:shadow-[0_10px_24px_rgba(200,121,46,.45)]"
                        style={{ background: 'linear-gradient(180deg, var(--color-hc-amber-light), var(--color-hc-amber))' }}
                    >
                        {label}
                    </a>
                </div>
            </Reveal>
        </section>
    )
}
