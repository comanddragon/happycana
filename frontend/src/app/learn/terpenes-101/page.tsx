import type { Metadata } from 'next'
import Link from 'next/link'
import { GuideArticle } from '@/components/learn/GuideArticle'
import { getGuide } from '@/lib/guides'

const guide = getGuide('terpenes-101')!

export const metadata: Metadata = {
    title: guide.title,
    description: guide.description,
    alternates: { canonical: `/learn/${guide.slug}` },
}

export default function Page() {
    return (
        <GuideArticle guide={guide}>
            <section>
                <h2>What terpenes are</h2>
                <p>
                    Terpenes are aromatic compounds produced by the same plant structures (trichomes) that make
                    cannabinoids like THC and CBD. They&apos;re not unique to cannabis — the same or similar
                    compounds give pine trees their scent, citrus peel its zing, and lavender its smell. In cannabis,
                    terpenes are what give different strains their distinct aroma, and researchers believe they
                    interact with cannabinoids to shape the overall effect, not just the smell.
                </p>
            </section>

            <section>
                <h2>Common terpenes and what they smell like</h2>
                <ul>
                    <li><strong>Myrcene</strong> — earthy, musky, sometimes described as clove-like; one of the most common terpenes in cannabis overall.</li>
                    <li><strong>Limonene</strong> — bright citrus smell, found in lemon and orange peel too.</li>
                    <li><strong>Pinene</strong> — sharp pine scent, the same compound found in pine needles.</li>
                    <li><strong>Linalool</strong> — floral, similar to lavender.</li>
                    <li><strong>Caryophyllene</strong> — peppery, spicy; also found in black pepper and cloves.</li>
                    <li><strong>Terpinolene</strong> — a lighter, herbal-floral note often found alongside citrus terpenes.</li>
                </ul>
            </section>

            <section>
                <h2>Why terpenes matter more than the strain name</h2>
                <p>
                    The idea that terpenes and cannabinoids work together to shape effect is often called the
                    &quot;entourage effect.&quot; The research is still developing, but in practice this means two
                    strains with the same THC percentage can feel noticeably different depending on their terpene
                    profile — which is a big part of why{' '}
                    <Link href="/learn/indica-vs-sativa-vs-hybrid" className="text-hc-amber-dim underline underline-offset-2">
                        the indica/sativa label alone
                    </Link>{' '}
                    {`is a weaker predictor of effect than people assume. If a product's lab report lists a terpene
                        breakdown, that's often more informative than the strain category.`}
                </p>
            </section>

            <section>
                <h2>How to use this when shopping</h2>
                <p>
                    If a strain worked well for you, it&apos;s worth checking its terpene profile (when listed) and
                    looking for other products that share the dominant terpenes, rather than relying only on the
                    strain name or indica/sativa/hybrid label — those can vary between growers even when the name is
                    the same.
                </p>
            </section>
        </GuideArticle>
    )
}
