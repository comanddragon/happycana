import type { Metadata } from "next"
import { ContactForm } from '@/components/support/ContactForm'
import { Faq } from '@/components/support/Faq'

export const metadata: Metadata = {
    title: 'Contact & Help | HappyCana',
    description: 'Get in touch with HappyCana, or find answers to common questions about ordering, shipping, and age verification.',
}

export default function ContactAndFaqPage() {
    return (
        <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
            <p className="font-hc-mono text-xs tracking-wide text-hc-ink-soft">SUPPORT</p>
            <h1 className="mt-2 font-hc-display text-4xl font-medium text-hc-ink">Contact &amp; Help</h1>
            <p className="mt-3 text-hc-ink-soft">
                Have a question about an order, a product, or anything else? Send us a message below, or check the
                FAQ further down first — you might find your answer faster.
            </p>

            <div className="mt-10">
                <ContactForm />
            </div>

            <div className="mt-20">
                <Faq />
            </div>
        </div>
    )
}
