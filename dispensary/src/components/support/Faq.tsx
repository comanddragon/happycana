export interface FaqItem {
    q: string
    a: string
}

export const DEFAULT_FAQS: FaqItem[] = [
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
        a: 'Because our products are regulated, returns are handled case-by-case. Contact us with your order number and we\u2019ll help sort it out.',
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
        a: 'Use the chat widget in the bottom corner of the site for the fastest response, or the contact form on this page for anything else.',
    },
]

interface Props {
    items?: FaqItem[]
    title?: string
    className?: string
}

/**
 * Drop-in FAQ accordion. Reuse the site-wide defaults or pass a page-specific
 * `items` list (e.g. shipping questions on a product page).
 */
export function Faq({ items = DEFAULT_FAQS, title = 'Frequently asked questions', className }: Props) {
    return (
        <div className={className}>
            <div className="mb-7 inline-flex items-center gap-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-sage-dim before:h-px before:w-3.5 before:bg-current before:opacity-50">
                FAQ
            </div>
            <h2 className="font-hc-display text-2xl font-medium text-hc-ink mb-6">{title}</h2>
            <div className="divide-y divide-hc-ink/[0.08] border-y border-hc-ink/[0.08]">
                {items.map(({ q, a }) => (
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
