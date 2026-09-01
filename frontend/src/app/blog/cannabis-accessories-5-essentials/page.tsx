import type { Metadata } from 'next'
import Link from 'next/link'
import { BlogArticle } from '@/components/blog/BlogArticle'
import { ProductPicks } from '@/components/blog/ProductPicks'
import { Faq } from '@/components/support/Faq'
import { getPost } from '@/lib/blog'

const post = getPost('cannabis-accessories-5-essentials')!

export const metadata: Metadata = {
    title: post.title,
    description: post.description,
    alternates: { canonical: `/blog/${post.slug}` },
}

const TOC = [
    { id: 'what-counts', label: 'What counts as an accessory' },
    { id: 'the-five', label: 'The 5 essentials' },
    { id: 'matching-the-kit', label: 'Matching the kit to how you smoke' },
    { id: 'keeping-clean', label: 'Keeping your accessories clean' },
    { id: 'what-to-skip', label: 'What you can skip' },
    { id: 'faq', label: 'FAQ' },
]

export default function Page() {
    return (
        <BlogArticle
            post={post}
            toc={TOC}
            tldr="Five accessories do almost all the real work: a grinder, a rolling tray, papers with filter tips, a pipe or bong, and proper airtight storage. Everything else is optional or decorative \u2014 spend on the boring essentials, keep them clean, and skip the wall of gimmicks."
        >
            <section id="what-counts">
                <h2>What counts as an accessory</h2>
                <p>
                    An accessory is anything that helps you prepare, consume, or store flower without being the
                    flower itself. That covers a huge range \u2014 from a one-euro pack of papers to a glass piece that
                    costs more than a phone. The useful filter is simple: does it solve a real, repeated annoyance,
                    or does it just look good on a shelf? Most weed-adjacent products fail that test. The handful
                    below pass it.
                </p>
            </section>

            <section id="the-five">
                <h2>The 5 essential accessories</h2>
                <p>
                    These five cover preparation, consumption, and storage between them. Get these right and you
                    genuinely need much less else. The order below is roughly priority order, since which one
                    matters most depends on how you actually smoke.
                </p>

                <h3>1. A grinder</h3>
                <p>
                    A grinder is the one accessory almost everyone underrates and then refuses to give up once
                    they own one. Breaking flower up by hand is slow, sticky, and wasteful, and a ground bud burns
                    far more evenly than a hand-torn one. A decent metal grinder with sharp teeth stays sharp for
                    years and pays for itself in convenience alone.
                </p>
                <p>
                    The other quiet benefit is the kief screen. A four-piece grinder catches the fine, potent dust
                    in a bottom chamber, and over a few weeks that adds up to a bonus you can sprinkle on top of a
                    bowl. Look for: aluminium or steel over cheap plastic, diamond-cut teeth over flat pins, and a
                    two-and-a-half-inch four-piece size for most people.
                </p>

                <h3>2. A rolling tray</h3>
                <p>
                    The least glamorous item on the list and one of the most useful. A rolling tray is just a
                    raised-edge surface, but it turns rolling from a scattered mess into a contained, tidy job, and
                    it catches the loose bits that would otherwise end up in the carpet. Cheap, flat, and quietly
                    essential \u2014 once you roll on one, you stop rolling on books and sofa cushions for good.
                </p>

                <h3>3. Papers and filter tips</h3>
                <p>
                    If you roll, papers are the accessory you consume most, so quality shows up every single time.
                    Thin, slow-burning papers in a natural fibre like hemp or rice beat thick bleached ones that
                    taste of the paper itself. A good pack costs pennies more than a bad one. Filter tips, or
                    crutches, are the small comparison that punches above their price \u2014 they keep the end open,
                    stop scraps reaching your mouth, and make the whole thing easier to hold and pass. If rolling
                    isn&apos;t your thing at all, pre-made rolls skip the step entirely and still get you there.
                </p>

                <h3>4. A pipe or bong</h3>
                <p>
                    For anyone who would rather not roll, a pipe or bong is the core consumption tool, and a
                    simple glass piece does the job better than most expensive ones. A small glass pipe is
                    portable, easy to clean, and genuinely hard to improve on for a quick session. A bong adds
                    water filtration, which cools the smoke and makes a bigger hit feel smoother, and some people
                    much prefer that. Either way, choose glass over plastic or metal \u2014 it tastes cleaner, does
                    not hold odours the same way, and is far easier to keep in good condition.
                </p>

                <h3>5. Airtight storage</h3>
                <p>
                    The accessory that protects everything else you spent money on, and the one most people
                    ignore until it&apos;s too late. Flower kept in a sandwich bag or a loose jar dries out, loses
                    its smell, and turns harsh within weeks. An airtight, opaque container keeps the terpenes in
                    the light out, and that is most of the battle. Glass jars with a proper seal are the simple
                    answer, and a cool, dark cupboard does the rest. The same logic that applies to{' '}
                    <Link href="/learn/what-is-a-cannabis-coa" className="text-hc-amber-dim underline underline-offset-2">
                        storing hash properly
                    </Link>{' '}
                    applies to flower: air, light, and heat are the three things that quietly degrade it. Get
                    storage right and your supply tastes as good on day thirty as it did on day one.
                </p>

                <table>
                    <thead>
                        <tr>
                            <th>Essential</th>
                            <th>Why it earns its place</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Grinder</td>
                            <td>Even grind, better burn, catches kief</td>
                        </tr>
                        <tr>
                            <td>Rolling tray</td>
                            <td>Contains the mess, wastes nothing</td>
                        </tr>
                        <tr>
                            <td>Papers + filter tips</td>
                            <td>What you consume, so quality is tasted</td>
                        </tr>
                        <tr>
                            <td>Pipe or bong</td>
                            <td>Core tool for non-rollers, cleaner than paper</td>
                        </tr>
                        <tr>
                            <td>Airtight storage</td>
                            <td>Protects flavour and potency over time</td>
                        </tr>
                    </tbody>
                </table>
            </section>

            <ProductPicks heading="A few essentials worth starting with" />

            <section id="matching-the-kit">
                <h2>Matching the kit to how you smoke</h2>
                <p>
                    Not everyone needs all five accessories, and the honest answer is that your method decides
                    your shortlist. A dedicated roller leans on the grinder, tray, papers, and tips, and barely
                    touches glass. Someone who prefers a pipe can skip papers entirely and put that money into a
                    better piece and a good jar. Buy for how you actually consume, not the way the shop display
                    assumes you do.
                </p>
            </section>

            <section id="keeping-clean">
                <h2>Keeping your accessories clean</h2>
                <p>
                    The unglamorous half of owning accessories is maintenance, and it matters more than buying
                    the expensive version. A grinder gummed up with resin grinds badly and a dirty pipe tastes
                    of old smoke, so a quick clean is the cheapest upgrade you own. Isopropyl alcohol and a
                    little coarse salt handle glass; a soak loosens the build-up on a metal grinder. Clean gear
                    simply works better, and it lasts years instead of months.
                </p>
            </section>

            <section id="what-to-skip">
                <h2>What you can skip</h2>
                <p>
                    Most of the wall in an accessory shop is solving problems you do not have. None of the below
                    is essential, and some of it is actively a waste of money.
                </p>
                <ul>
                    <li><strong>Novelty grinders</strong> \u2014 the plastic or themed ones that dull within a month.</li>
                    <li><strong>Giant elaborate bongs</strong> \u2014 harder to clean, easy to break, no better than a simple one.</li>
                    <li><strong>Branded &ldquo;stash boxes&rdquo;</strong> \u2014 an opaque jar does the same job for a fraction of the price.</li>
                    <li><strong>Single-use gimmicks</strong> \u2014 the gadget you buy for one trick and never touch again.</li>
                </ul>
            </section>

            <section>
                <h2>The honest checklist</h2>
                <p>
                    No pitch here, just the usual point: knowing what actually earns its place stops you paying
                    for the part that does not. Buy the essentials well, spend on what you consume, choose glass
                    for anything that touches smoke, and ignore the gimmick wall \u2014 novelty rarely survives a
                    month of real use.
                </p>
            </section>

            <section id="faq">
                <Faq
                    title="FAQ"
                    items={[
                        {
                            q: 'What cannabis accessories does a beginner actually need?',
                            a: 'Start with a grinder and papers or a small pipe \u2014 that covers grinding and consuming. Add a rolling tray and an airtight jar once you\u2019re buying flower regularly; everything else can wait.',
                        },
                        {
                            q: 'Is a grinder worth buying?',
                            a: 'Yes \u2014 it\u2019s one of the cheapest upgrades available and pays for itself in a more even burn, less waste, and a kief screen that adds up over time.',
                        },
                        {
                            q: 'Glass or plastic for a pipe or bong?',
                            a: 'Glass. It doesn\u2019t hold odours the way plastic does, tastes cleaner, and is easier to keep in good condition with a simple isopropyl-and-salt clean.',
                        },
                    ]}
                />
            </section>
        </BlogArticle>
    )
}
