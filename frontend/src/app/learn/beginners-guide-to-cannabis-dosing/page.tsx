import type { Metadata } from 'next'
import Link from 'next/link'
import { GuideArticle } from '@/components/learn/GuideArticle'
import { getGuide } from '@/lib/guides'

const guide = getGuide('beginners-guide-to-cannabis-dosing')!

export const metadata: Metadata = {
    title: guide.title,
    description: guide.description,
    alternates: { canonical: `/learn/${guide.slug}` },
}

export default function Page() {
    return (
        <GuideArticle guide={guide}>
            <section>
                <h2>Why &quot;start low, go slow&quot; is the rule</h2>
                <p>
                    Potency varies a lot between products, and everyone&apos;s tolerance and body chemistry are
                    different — the same dose that does nothing for one person can feel intense for another. The
                    safest way to figure out what works for you is to start with a small amount, wait to see how it
                    affects you, and increase gradually on a later occasion rather than taking more right away.
                </p>
            </section>

            <section>
                <h2>What &quot;starting low&quot; looks like by product type</h2>
                <ul>
                    <li>
                        <strong>Edibles</strong> — many state-legal packages list a standard single serving in the
                        low single-digit milligrams of THC. If you&apos;re new to edibles, taking less than a full
                        package serving and waiting a few hours before considering more is the more cautious
                        approach — see our{' '}
                        <Link href="/learn/how-long-do-edibles-take-to-kick-in" className="text-hc-amber-dim underline underline-offset-2">
                            edibles onset guide
                        </Link>{' '}
                        for why the wait matters so much here.
                    </li>
                    <li>
                        <strong>Flower</strong> — a single small inhalation, waiting several minutes before taking
                        another, gives you time to gauge the effect before it fully sets in.
                    </li>
                    <li>
                        <strong>Vapes and concentrates</strong> — generally higher potency per use than flower, so
                        the "one small amount, then wait" approach matters even more here.
                    </li>
                    <li>
                        <strong>Tinctures</strong> — dosed by the drop or milliliter, making it easier to take a
                        precise small amount and adjust gradually.
                    </li>
                </ul>
            </section>

            <section>
                <h2>Set and setting matter too</h2>
                <p>
                    Where and with whom you consume affects the experience as much as the dose does. First-time or
                    higher doses are best tried somewhere comfortable and familiar, with something to eat and drink
                    on hand, and without needing to drive or operate machinery for the rest of the day.
                </p>
            </section>

            <section>
                <h2>If you take too much</h2>
                <p>
                    Cannabis overconsumption is uncomfortable — rapid heartbeat, anxiety, nausea — but is not
                    considered life-threatening on its own. It passes with time. Sit or lie down somewhere calm,
                    stay hydrated, and remind yourself it will wear off. If you have chest pain, difficulty
                    breathing, or any other severe symptom, treat it as a medical emergency and seek care right
                    away.
                </p>
            </section>

            <section>
                <h2>One more thing</h2>
                <p>
                    This is general information, not medical advice — talk to a doctor if you&apos;re using cannabis
                    for a medical condition, are pregnant or breastfeeding, or are taking other medications. Products
                    are for adults 21+ only, and you should never drive or operate machinery after use.
                </p>
            </section>
        </GuideArticle>
    )
}
