import type { Metadata } from 'next'
import Link from 'next/link'
import { BlogArticle } from '@/components/blog/BlogArticle'
import { Faq } from '@/components/support/Faq'
import { getPost } from '@/lib/blog'

const post = getPost('joint-rolling-for-beginners')!

export const metadata: Metadata = {
    title: post.title,
    description: post.description,
    alternates: { canonical: `/blog/${post.slug}` },
}

const TOC = [
    { id: 'gather', label: 'What you need' },
    { id: 'grind', label: 'Step 1: Grind' },
    { id: 'crutch', label: 'Step 2: Set the crutch' },
    { id: 'fill', label: 'Step 3: Fill and shape' },
    { id: 'roll', label: 'Step 4: Roll and twist' },
    { id: 'mistakes', label: 'Common mistakes' },
    { id: 'faq', label: 'FAQ' },
]

export default function Page() {
    return (
        <BlogArticle
            post={post}
            toc={TOC}
            tldr="Four steps, in order: grind evenly, set a crutch, fill and shape a cone, then roll and twist the end shut. Most bad joints trace back to one thing \u2014 flower that isn\u2019t ground fine and even enough to pack a consistent cone."
        >
            <section id="gather">
                <h2>What you need</h2>
                <p>
                    Rolling papers, a filter tip (or a strip of card to make your own crutch), ground flower, and
                    somewhere flat to work \u2014 a{' '}
                    <Link href="/blog/cannabis-accessories-5-essentials" className="text-hc-amber-dim underline underline-offset-2">
                        rolling tray
                    </Link>{' '}
                    makes this dramatically less messy, but a clean plate works in a pinch. A grinder isn&apos;t
                    strictly required, but hand-broken flower rolls noticeably worse \u2014 it&apos;s uneven, which is
                    the single most common cause of an uneven burn.
                </p>
            </section>

            <section id="grind">
                <h2>Step 1: Grind</h2>
                <p>
                    Break the flower down to a fine, even consistency \u2014 not powder, but no chunks either. Even
                    grind size is what lets the joint burn at a consistent rate along its whole length; a mix of
                    big and small pieces burns unevenly and tends to canoe, where one side burns faster than the
                    other and the joint goes out lopsided.
                </p>
            </section>

            <section id="crutch">
                <h2>Step 2: Set the crutch</h2>
                <p>
                    Fold a strip of card into a small accordion at one end, then roll it into a tight cylinder
                    slightly narrower than the paper. Place it at one end of the paper, on the inside. This gives
                    the joint a firm mouthpiece and stops the end collapsing once you&apos;re a few draws in \u2014
                    see the{' '}
                    <Link href="/blog/joint-filter-comparison-carbon-vs-paper" className="text-hc-amber-dim underline underline-offset-2">
                        filter comparison
                    </Link>{' '}
                    if you&apos;d rather use a pre-made carbon tip instead.
                </p>
            </section>

            <section id="fill">
                <h2>Step 3: Fill and shape</h2>
                <p>
                    Lay the ground flower along the paper next to the crutch, tapering it thinner toward the far
                    end so you end up with a cone rather than a straight tube \u2014 a cone burns more evenly and is
                    easier to draw on. Use your fingertips to shape it into a loose log before you start rolling;
                    don&apos;t pack it tight yet.
                </p>
            </section>

            <section id="roll">
                <h2>Step 4: Roll and twist</h2>
                <p>
                    Pinch the paper between your fingertips and thumbs on both sides, and roll it back and forth
                    to pack the flower into an even, firm cylinder before you start sealing. Once it feels evenly
                    packed, tuck the unglued edge under and roll it up, licking the gummed strip to seal as you
                    go. Finish by twisting the open end shut \u2014 this keeps flower from spilling out and gives you
                    a clean edge to light.
                </p>
            </section>

            <section id="mistakes">
                <h2>Common mistakes</h2>
                <ul>
                    <li><strong>Uneven grind</strong> \u2014 the top cause of canoeing; fix it before anything else.</li>
                    <li><strong>Packing too tight</strong> \u2014 restricts airflow and makes the joint hard to draw on and prone to going out.</li>
                    <li><strong>Packing too loose</strong> \u2014 burns too fast and can fall apart mid-smoke.</li>
                    <li><strong>Skipping the taper</strong> \u2014 a straight cylinder burns less predictably than a cone.</li>
                </ul>
            </section>

            <section id="faq">
                <Faq
                    title="FAQ"
                    items={[
                        {
                            q: 'Why does my joint keep canoeing?',
                            a: 'Almost always an uneven grind or uneven packing \u2014 one side is denser than the other, so it burns slower. Grind finer and pack the log evenly before rolling.',
                        },
                        {
                            q: 'Do I need a filter tip to roll a joint?',
                            a: 'Not strictly, but it makes a real difference \u2014 it keeps the end from collapsing and gives you something to hold once it gets short.',
                        },
                        {
                            q: 'What size paper should a beginner start with?',
                            a: 'Standard 1\u00bc size is the easiest to learn on \u2014 large enough to work with comfortably, small enough that mistakes are cheap.',
                        },
                    ]}
                />
            </section>
        </BlogArticle>
    )
}
