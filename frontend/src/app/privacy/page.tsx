import type { Metadata } from "next"

export const metadata: Metadata = {
    title: 'Privacy Policy | HappyCana',
    description: 'How HappyCana collects, uses, and protects your information.',
}

export default function PrivacyPage() {
    return (
        <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
            <p className="font-hc-mono text-xs tracking-wide text-hc-ink-soft">LEGAL</p>
            <h1 className="mt-2 font-hc-display text-4xl font-medium text-hc-ink">Privacy Policy</h1>
            <p className="mt-2 text-sm text-hc-ink-soft">Last updated: August 2026</p>

            <div className="mt-10 space-y-8 text-hc-ink-soft [&_h2]:font-hc-display [&_h2]:text-xl [&_h2]:font-medium [&_h2]:text-hc-ink [&_h2]:mb-2 [&_p]:leading-relaxed">
                <section>
                    <h2>Information we collect</h2>
                    <p>
                        When you create an account, place an order, or contact us, we collect information such as
                        your name, email address, shipping address, phone number, and age verification status.
                        Payment details are processed by our payment provider and are not stored on our servers.
                    </p>
                </section>

                <section>
                    <h2>How we use your information</h2>
                    <p>
                        We use your information to process orders, verify you meet the legal age requirement for
                        cannabis purchases in your state, provide customer support, and send order updates. We do
                        not sell your personal information to third parties.
                    </p>
                </section>

                <section>
                    <h2>Age verification</h2>
                    <p>
                        Because our products are restricted to adults 21 and older, we retain records of age
                        verification as required by applicable state and federal regulations.
                    </p>
                </section>

                <section>
                    <h2>Cookies</h2>
                    <p>
                        We use cookies to keep you signed in, remember items in your cart, and understand how the
                        site is used so we can improve it.
                    </p>
                </section>

                <section>
                    <h2>Your rights</h2>
                    <p>
                        You can request access to, correction of, or deletion of your personal information at any
                        time by contacting us through our <a href="/help/faq" className="text-hc-amber-dim underline underline-offset-2">Help &amp; FAQ</a> page.
                    </p>
                </section>

                <section>
                    <h2>Contact</h2>
                    <p>
                        Questions about this policy? Reach out via our Help &amp; FAQ page and we&rsquo;ll get back
                        to you.
                    </p>
                </section>
            </div>
        </div>
    )
}
