import type { Metadata } from 'next'
import Link from 'next/link'
import { GuideArticle } from '@/components/learn/GuideArticle'
import { getGuide } from '@/lib/guides'

const guide = getGuide('what-is-a-cannabis-coa')!

export const metadata: Metadata = {
    title: guide.title,
    description: guide.description,
    alternates: { canonical: `/learn/${guide.slug}` },
}

export default function Page() {
    return (
        <GuideArticle guide={guide}>
            <section>
                <h2>What a COA is</h2>
                <p>
                    A Certificate of Analysis (COA) is a lab report for a specific batch of cannabis product. An
                    independent, third-party lab tests a sample of that batch and documents exactly what&apos;s in
                    it — cannabinoid content, and screening for contaminants that shouldn&apos;t be there. In legal
                    markets, licensed retailers are generally required to have COAs on file for the batches they
                    sell; a retailer voluntarily publishing them is a good sign of transparency.
                </p>
            </section>

            <section>
                <h2>The sections worth actually reading</h2>
                <ul>
                    <li>
                        <strong>Cannabinoid potency</strong> — THC, CBD, and often minor cannabinoids, usually shown
                        as a percentage by weight. This is what determines actual strength, and it can vary batch to
                        batch even under the same product name.
                    </li>
                    <li>
                        <strong>Pesticide screening</strong> — a panel testing for pesticide residues above
                        regulatory limits.
                    </li>
                    <li>
                        <strong>Microbial screening</strong> — testing for mold, yeast, and harmful bacteria,
                        particularly important for anything inhaled.
                    </li>
                    <li>
                        <strong>Heavy metals</strong> — cannabis plants absorb metals from soil, so this panel checks
                        for lead, arsenic, cadmium, and mercury.
                    </li>
                    <li>
                        <strong>Residual solvents</strong> — relevant for concentrates and vapes made with
                        solvent-based extraction; confirms no unsafe solvent residue remains.
                    </li>
                    <li>
                        <strong>Batch/lot number</strong> — ties the report to the exact batch you&apos;re holding,
                        not just the product line in general. If a COA doesn&apos;t reference a batch number that
                        matches your packaging, it isn&apos;t telling you much about what&apos;s actually in your
                        hand.
                    </li>
                </ul>
            </section>

            <section>
                <h2>Questions worth asking before you trust a claim</h2>
                <ul>
                    <li>Is the lab independent from the grower/processor, and is it accredited?</li>
                    <li>Does the COA&apos;s batch number match the packaging in front of you?</li>
                    <li>Is the report recent, and does it cover the full contaminant panel — not potency alone?</li>
                </ul>
                <p>
                    A badge or logo that says &quot;lab tested&quot; without a linked, batch-matched report isn&apos;t
                    verifiable — it&apos;s a claim. A real COA is what turns that claim into something you can check
                    yourself.
                </p>
            </section>

            <section>
                <h2>Where to see ours</h2>
                <p>
                    Every batch we sell is tested at an independent lab before it reaches the menu. If you can&apos;t
                    find the COA for a specific product you&apos;ve purchased,{' '}
                    <Link href="/help/faq" className="text-hc-amber-dim underline underline-offset-2">
                        reach out
                    </Link>{' '}
                    and we&apos;ll get you the batch-specific report.
                </p>
            </section>
        </GuideArticle>
    )
}
