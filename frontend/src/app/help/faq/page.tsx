import type { Metadata } from "next"

export const metadata: Metadata = {
    title: 'Help & FAQ | HappyCana',
    description: 'Answers to common questions about ordering, shipping, and age verification at HappyCana.',
}

const FAQS = [
    {
        q: 'Do I need to verify my age to order?',
        a: 'Yes. You must be 21 or older to purchase, and we verify age at checkout. Cannabis products can only be shipped to states where such sales are legal.',
    },
    {
        q: 'How long does shipping take?',
        a: 'Most orders ship within 1-2 business days and arrive within 3-7 business days, depending on your location.',
    },
    {
        q: 'Can I return a product?',
        a: 'Because our products are regulated, returns are handled case-by-case. Contact us below with your order number and we\u2019ll help sort it out.',
    },
    {
        q: 'How do I track my order?',
        a: 'Once your order ships, you\u2019ll get a tracking link by email. You can also check order status anytime from your account under Orders.',
    },
    {
        q: 'Which states can you ship to?',
        a: 'We ship only to states where cannabis sales are legal. If your state isn\u2019t supported, it won\u2019t be available at checkout.',
    },
    {
        q: 'How do I contact support?',
        a: 'Use the chat widget in the bottom corner of the site for the fastest response, or reach out through your account for order-specific questions.',
    },
]

export default function FaqPage() {
    return (
        <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
            <p className="font-hc-mono text-xs tracking-wide text-hc-ink-soft">SUPPORT</p>
            <h1 className="mt-2 font-hc-display text-4xl font-medium text-hc-ink">Help &amp; FAQ</h1>
            <p className="mt-3 text-hc-ink-soft">
                Can&rsquo;t find what you&rsquo;re looking for? Use the chat widget in the corner of the screen and
                we&rsquo;ll help you out.
            </p>

            <div className="mt-10 divide-y divide-hc-ink/[0.08] border-y border-hc-ink/[0.08]">
                {FAQS.map(({ q, a }) => (
                    <details key={q} className="group py-5">
                        <summary className="flex cursor-pointer list-none items-center justify-between font-hc-display text-lg font-medium text-hc-ink">
                            {q}
                            <span className="ml-4 shrink-0 text-hc-ink-soft transition-transform group-open:rotate-45">+</span>
                        </summary>
                        <p className="mt-3 leading-relaxed text-hc-ink-soft">{a}</p>
                    </details>
                ))}
            </div>
        </div>
    )
}
