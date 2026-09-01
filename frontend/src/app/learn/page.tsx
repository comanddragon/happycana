// app/learn/page.tsx
import type { Metadata } from 'next'
import Link from 'next/link'
import { GUIDES } from '@/lib/guides'

export const metadata: Metadata = {
    title: 'Cannabis Guides & FAQs',
    description: 'Plain-language guides on indica vs. sativa, edible onset time, terpenes, lab testing, and dosing — everything to know before you shop.',
    alternates: { canonical: '/learn' },
}

export default function LearnIndexPage() {
    return (
        <div className="mx-auto max-w-4xl px-4 py-16 sm:px-6">
            <p className="font-hc-mono text-xs tracking-wide text-hc-ink-soft">LEARN</p>
            <h1 className="mt-2 font-hc-display text-4xl font-medium text-hc-ink">Cannabis Guides</h1>
            <p className="mt-3 max-w-2xl text-hc-ink-soft leading-relaxed">
                Straightforward answers to the questions we hear most before someone places their first order —
                what the strain types actually mean, how long edibles take, how to read a COA, and how to dose
                sensibly. No fluff, no medical claims.
            </p>

            <div className="mt-12 grid gap-4 sm:grid-cols-2">
                {GUIDES.map(guide => (
                    <Link
                        key={guide.slug}
                        href={`/learn/${guide.slug}`}
                        className="group rounded-2xl border border-hc-ink/[0.08] bg-white p-6 transition-all duration-200 hover:-translate-y-1 hover:border-hc-amber hover:shadow-[0_16px_30px_-14px_rgba(23,20,15,0.25)]"
                    >
                        <p className="font-hc-mono text-[11px] uppercase tracking-[0.1em] text-hc-sage-dim">
                            {guide.kicker}
                        </p>
                        <h2 className="mt-2 font-hc-display text-lg font-medium text-hc-ink">
                            {guide.title}
                        </h2>
                        <p className="mt-2 text-sm leading-relaxed text-hc-ink-soft">{guide.description}</p>
                        <span className="mt-4 inline-block text-xs font-medium text-hc-amber-dim group-hover:underline">
                            Read guide &rarr;
                        </span>
                    </Link>
                ))}
            </div>

            <div className="mt-14 rounded-2xl border border-hc-ink/[0.08] bg-hc-paper-2 p-6">
                <p className="text-sm text-hc-ink-soft">
                    Have an order or shipping question instead? Check our{' '}
                    <Link href="/help/faq" className="text-hc-amber-dim underline underline-offset-2">
                        Help &amp; FAQ
                    </Link>{' '}
                    page.
                </p>
            </div>
        </div>
    )
}
