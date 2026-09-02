import type { Metadata } from 'next'
import Link from 'next/link'
import { GuideArticle } from '@/components/learn/GuideArticle'
import { getGuide } from '@/lib/guides'

const guide = getGuide('indica-vs-sativa-vs-hybrid')!

export const metadata: Metadata = {
    title: guide.title,
    description: guide.description,
    alternates: { canonical: `/learn/${guide.slug}` },
}

export default function Page() {
    return (
        <GuideArticle guide={guide}>
            <section>
                <h2>The short answer</h2>
                <p>
                    {`Indica, sativa, and hybrid started out as a botanical classification — plant height, leaf shape,
                        flowering time — not a promise about how a product will make you feel. Modern cannabis has been
                        cross-bred for so many generations that a truly "pure" indica or sativa is rare in a retail
                        catalog; almost everything on a shelf today is some kind of hybrid. The labels stuck around as
                        shorthand, but they&apos;re a much weaker predictor of effect than most people assume.`}
                </p>
            </section>

            <section>
                <h2>What the labels originally meant</h2>
                <p>
                    <strong>Indica</strong> plants are traditionally short and bushy with wide leaves, originating
                    from cooler, harsher climates. <strong>Sativa</strong> plants are tall and thin-leafed,
                    originating from equatorial regions with long growing seasons. That&apos;s a description of the
                    plant, not the person smoking it — genetics alone don&apos;t determine whether a strain feels
                    relaxing or energizing.
                </p>
            </section>

            <section>
                <h2>So what actually drives the effect?</h2>
                <p>
                    Three things matter more than the indica/sativa label:
                </p>
                <ul>
                    <li><strong>Cannabinoid content</strong> — THC and CBD ratios, and their overall potency.</li>
                    <li>
                        <strong>Terpene profile</strong> — the aromatic compounds that shape effect alongside
                        cannabinoids (see our{' '}
                        <Link href="/learn/terpenes-101" className="text-hc-amber-dim underline underline-offset-2">
                            terpenes guide
                        </Link>
                        ).
                    </li>
                    <li><strong>Your own tolerance, dose, and setting</strong> — the same product can land differently depending on how much you take and how experienced you are.</li>
                </ul>
                <p>
                    {`This is why two "indica" strains from different growers can feel noticeably different, and why a
                        "sativa" can sometimes feel calming. If you&apos;re shopping by desired effect rather than
                        botanical lineage, it&apos;s usually more reliable to filter by effect (uplift, unwind, rest,
                        focus, social) than by the indica/sativa/hybrid label alone.`}
                </p>
            </section>

            <section>
                <h2>Practical takeaway</h2>
                <p>
                    Use indica/sativa/hybrid as a loose starting point if you like, but check the THC/CBD numbers
                    and, if listed, the terpene profile before you buy — and start with a small amount of anything
                    new regardless of label, since individual reactions vary. You can browse our current menu
                    filtered by how you want to feel on the{' '}
                    <Link href="/shop/products" className="text-hc-amber-dim underline underline-offset-2">
                        shop page
                    </Link>
                    .
                </p>
            </section>
        </GuideArticle>
    )
}
