import type { Metadata } from 'next'
import Link from 'next/link'
import { GuideArticle } from '@/components/learn/GuideArticle'
import { getGuide } from '@/lib/guides'

const guide = getGuide('how-long-do-edibles-take-to-kick-in')!

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
                    Most people feel the effects of an edible within <strong>30 to 90 minutes</strong>, with the peak
                    usually landing somewhere between 2 and 3 hours after eating it. That&apos;s a much wider — and
                    slower — window than smoking or vaping, where effects are typically felt within minutes.
                </p>
            </section>

            <section>
                <h2>Why edibles take so much longer</h2>
                <p>
                    When you smoke or vape, cannabinoids enter your bloodstream through your lungs almost
                    immediately. An edible has to be digested first: it passes through your stomach and gets
                    processed by your liver, which converts THC into a different, often more potent compound before
                    it reaches your bloodstream. That extra step is why onset is slower and why the effects of
                    edibles tend to feel different — often described as heavier or more body-focused — than
                    inhaled cannabis.
                </p>
            </section>

            <section>
                <h2>What changes the timing</h2>
                <ul>
                    <li><strong>Stomach contents</strong> — taking an edible on an empty stomach tends to speed up onset; eating a meal first slows it down.</li>
                    <li><strong>Metabolism</strong> — this varies person to person and can&apos;t really be predicted in advance.</li>
                    <li><strong>Product type</strong> — fast-acting formats (some dissolvables, drinks) are formulated to skip part of the digestive process and can kick in closer to 15–30 minutes.</li>
                    <li><strong>Dose</strong> — a higher dose doesn&apos;t arrive faster, it just hits harder once it does.</li>
                </ul>
            </section>

            <section>
                <h2>The single most important thing to know</h2>
                <p>
                    <strong>&quot;It&apos;s not working yet&quot; is the most common — and most avoidable — edible
                    mistake.</strong> Because onset can take well over an hour, it&apos;s easy to assume a first
                    edible did nothing and take a second one, only to have both hit at once. If you&apos;ve taken an
                    edible, give it at least 2 full hours before deciding whether you need more. See our{' '}
                    <Link href="/learn/beginners-guide-to-cannabis-dosing" className="text-hc-amber-dim underline underline-offset-2">
                        beginner&apos;s dosing guide
                    </Link>{' '}
                    for how much to start with in the first place.
                </p>
            </section>

            <section>
                <h2>How long do the effects last?</h2>
                <p>
                    Edible effects typically last <strong>4 to 8 hours</strong>, longer than most inhaled formats,
                    with a gradual comedown rather than a sharp cutoff. Plan accordingly — an edible taken in the
                    evening can still have residual effects the following morning for some people.
                </p>
            </section>
        </GuideArticle>
    )
}
