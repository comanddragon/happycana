import type { Metadata } from "next"

export const metadata: Metadata = {
    title: 'Terms of Service | HappyCana',
    description: 'The terms governing your use of HappyCana.',
}

export default function TermsPage() {
    return (
        <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
            <p className="font-hc-mono text-xs tracking-wide text-hc-ink-soft">LEGAL</p>
            <h1 className="mt-2 font-hc-display text-4xl font-medium text-hc-ink">Terms of Service</h1>
            <p className="mt-2 text-sm text-hc-ink-soft">Last updated: August 2026</p>

            <div className="mt-10 space-y-8 text-hc-ink-soft [&_h2]:font-hc-display [&_h2]:text-xl [&_h2]:font-medium [&_h2]:text-hc-ink [&_h2]:mb-2 [&_p]:leading-relaxed">
                <section>
                    <h2>Age requirement</h2>
                    <p>
                        You must be 21 years of age or older to purchase from HappyCana, and cannabis products may
                        only be shipped to states where such sales are legal. By using this site, you confirm you
                        meet this requirement.
                    </p>
                </section>

                <section>
                    <h2>Account responsibilities</h2>
                    <p>
                        You&rsquo;re responsible for keeping your account credentials secure and for all activity
                        under your account. Notify us immediately if you suspect unauthorized access.
                    </p>
                </section>

                <section>
                    <h2>Orders and pricing</h2>
                    <p>
                        We reserve the right to refuse or cancel any order, including in cases of pricing errors,
                        suspected fraud, or inability to verify age or shipping eligibility. Prices are subject to
                        change without notice.
                    </p>
                </section>

                <section>
                    <h2>Product information</h2>
                    <p>
                        Keep out of reach of children and pets. Our products are intended for use only by adults
                        21+, in states where cannabis is legal, and have not been evaluated by the FDA. They are
                        not intended to diagnose, treat, cure, or prevent any disease.
                    </p>
                </section>

                <section>
                    <h2>Returns</h2>
                    <p>
                        Due to the regulated nature of cannabis products, returns and exchanges are handled on a
                        case-by-case basis. Contact us through our Help &amp; FAQ page if there&rsquo;s an issue
                        with your order.
                    </p>
                </section>

                <section>
                    <h2>Changes to these terms</h2>
                    <p>
                        We may update these terms from time to time. Continued use of the site after changes take
                        effect constitutes acceptance of the updated terms.
                    </p>
                </section>
            </div>
        </div>
    )
}
