import type { Metadata } from 'next'
import Link from 'next/link'
import { BlogArticle } from '@/components/blog/BlogArticle'
import { Faq } from '@/components/support/Faq'
import { getPost } from '@/lib/blog'

const post = getPost('joint-filter-comparison-carbon-vs-paper')!

export const metadata: Metadata = {
    title: post.title,
    description: post.description,
    alternates: { canonical: `/blog/${post.slug}` },
}

const TOC = [
    { id: 'why-filter', label: 'Why filter at all' },
    { id: 'paper', label: 'Paper crutches' },
    { id: 'carbon', label: 'Activated carbon tips' },
    { id: 'comparison', label: 'Side by side' },
    { id: 'faq', label: 'FAQ' },
]

export default function Page() {
    return (
        <BlogArticle
            post={post}
            toc={TOC}
            tldr="Paper crutches are cheap, structural, and reusable-in-spirit \u2014 they just hold the joint's shape. Activated carbon tips add real filtration and a noticeably smoother draw, for a bit more cost and a fractionally tighter pull. Neither is wrong; it's a trade between price and smoothness."
        >
            <section id="why-filter">
                <h2>Why filter at all</h2>
                <p>
                    A filter tip \u2014 or crutch, if you want the rolling-community term \u2014 sits at the mouth end of
                    a joint. Its baseline job has nothing to do with taste: it keeps the paper from collapsing as
                    you draw, stops loose flower and roach material reaching your mouth, and gives you something
                    firm to hold onto once the joint gets short. Everything past that is where paper and carbon
                    diverge.
                </p>
            </section>

            <section id="paper">
                <h2>Paper crutches</h2>
                <p>
                    The standard option: a strip of thin card, rolled into a small cylinder and tucked into one
                    end before you fill and roll. It does the structural job well and costs almost nothing \u2014 most
                    packs of papers include crutch material, or you can tear a strip from any business card. What
                    it does not do is filter anything meaningfully. Smoke passes through a paper crutch largely
                    unchanged, so if flavour and airflow are your priority, this is the simpler choice.
                </p>
            </section>

            <section id="carbon">
                <h2>Activated carbon tips</h2>
                <p>
                    Pre-made filter tips with an activated carbon core work the same way a carbon water filter
                    does: the porous carbon structure traps some of the tar and particulate in the smoke as it
                    passes through, before it reaches you. The result is a visibly smoother, cooler draw \u2014
                    people who switch to carbon tips consistently describe less throat irritation on a big hit.
                    The trade-offs are a slightly firmer pull, since the carbon adds resistance, and a marginally
                    higher cost per joint, since you&apos;re buying a manufactured tip instead of tearing paper.
                </p>
            </section>

            <section id="comparison">
                <h2>Side by side</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Attribute</th>
                            <th>Paper crutch</th>
                            <th>Carbon tip</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Filtration</td>
                            <td>Structural only</td>
                            <td>Traps tar &amp; particulate</td>
                        </tr>
                        <tr>
                            <td>Draw</td>
                            <td>Open, unrestricted</td>
                            <td>Slightly firmer</td>
                        </tr>
                        <tr>
                            <td>Cost</td>
                            <td>Free with most papers</td>
                            <td>A few cents more per joint</td>
                        </tr>
                        <tr>
                            <td>Best for</td>
                            <td>Flavour-first rollers</td>
                            <td>Big hitters, sensitive throats</td>
                        </tr>
                    </tbody>
                </table>
                <p>
                    If you&apos;re just getting into rolling, a paper crutch is the sensible default \u2014 see the{' '}
                    <Link href="/blog/joint-rolling-for-beginners" className="text-hc-amber-dim underline underline-offset-2">
                        beginner&rsquo;s rolling walkthrough
                    </Link>{' '}
                    for the full process. Once you know your habits, a box of carbon tips is a cheap experiment
                    worth running.
                </p>
            </section>

            <section id="faq">
                <Faq
                    title="FAQ"
                    items={[
                        {
                            q: 'Do carbon filter tips remove THC?',
                            a: 'No \u2014 they trap some tar and particulate, not the cannabinoids themselves, so potency isn\u2019t meaningfully affected.',
                        },
                        {
                            q: 'Can I reuse a filter tip?',
                            a: 'Not recommended for either type. Both are inexpensive enough that a fresh one per joint is the simplest, cleanest habit.',
                        },
                        {
                            q: 'Do I need a filter tip if I use a pipe or bong instead?',
                            a: 'No \u2014 filter tips are specific to rolled joints. See the accessories guide for what actually matters if you\u2019d rather not roll.',
                        },
                    ]}
                />
            </section>
        </BlogArticle>
    )
}
